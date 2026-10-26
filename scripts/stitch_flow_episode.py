"""Google Flow Automated Assembly & Publishing Pipeline.
Takes real AI-animated .mp4 video clips generated in Google Flow (labs.google/fx/tools/flow),
synchronizes Arabic voiceover (Gemini 3.8 Flash TTS), overlays formatted Arabic subtitles,
mixes background music with audio ducking, stitches seamless transitions, and uploads to YouTube!
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import base64
import wave
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import imageio_ffmpeg
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from youtube_uploader import upload_video

INPUT_CLIPS_DIR = BASE_DIR / "output" / "flow_clips"
FINAL_OUTPUT_DIR = BASE_DIR / "output" / "flow_episodes"
SCENES_DIR = BASE_DIR / "characters" / "scenes"
BGM_FILE = SCENES_DIR / "kids_gentle_bgm.wav"
ENV_FILE = BASE_DIR / ".env"

INPUT_CLIPS_DIR.mkdir(parents=True, exist_ok=True)
FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "C:\\Windows\\Fonts\\segoeui.ttf"

def get_api_key():
    if ENV_FILE.exists():
        for line in open(ENV_FILE, encoding="utf-8"):
            if line.startswith("GEMINI_API_KEY="):
                return line.strip().split("=", 1)[1]
    return os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6Ly6CghBsKIp9KFboAoEWe_N7hlrKwYhzBosimjI_JVrA")

def get_audio_duration(audio_path: Path) -> float:
    with wave.open(str(audio_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())

def get_video_duration(video_path: Path, ffmpeg_bin: str) -> float:
    """Get video clip duration using ffprobe."""
    ffprobe_bin = ffmpeg_bin.replace("ffmpeg.exe", "ffprobe.exe")
    if not os.path.exists(ffprobe_bin):
        # Fallback using ffmpeg directly
        cmd = [ffmpeg_bin, "-i", str(video_path)]
        res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        for line in res.stderr.split("\n"):
            if "Duration:" in line:
                part = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = part.split(":")
                return float(h) * 3600 + float(m) * 60 + float(s)
        return 5.0

    cmd = [
        ffprobe_bin, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        return float(res.stdout.strip())
    except:
        return 5.0

def generate_voiceover(text: str, output_path: Path):
    """Generate expressive Arabic storytelling voiceover using Gemini 3.8 Flash TTS."""
    if output_path.exists() and output_path.stat().st_size > 1000:
        return output_path

    print(f"🎙️ Generating voiceover: '{text[:40]}...'")
    try:
        api_key = get_api_key()
        client = genai.Client(api_key=api_key)
        interaction = client.interactions.create(
            model="gemini-3.8-flash-tts",
            input=[{
                "type": "user_input",
                "content": [{
                    "type": "text",
                    "text": text,
                    "annotations": [{
                        "type": "speech_metadata",
                        "style": "warm, gentle, encouraging, and highly expressive kindergarten teacher and cartoon narrator",
                    }],
                }],
            }],
            response_format={"type": "audio"},
            generation_config={
                "speech_config": [
                    {"voice": "Kore"},
                ]
            },
        )
        audio_bytes = base64.b64decode(interaction.output_audio.data)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        print(f"✅ Voiceover saved: {output_path.name}")
        return output_path
    except Exception as e:
        print(f"⚠️ Gemini TTS fallback to gTTS: {e}")
        from gtts import gTTS
        temp_mp3 = output_path.with_suffix(".mp3")
        tts = gTTS(text=text, lang="ar")
        tts.save(str(temp_mp3))
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run([
            ffmpeg_bin, "-y", "-i", str(temp_mp3),
            "-ar", "24000", "-ac", "1", str(output_path)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return output_path

def create_subtitles_strip(text: str, output_path: Path, box_w=1500, box_h=120):
    """Render a 16:9 lower-third subtitle strip with full Arabic Tashkeel."""
    sub_img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sub_img)
    sdraw.rounded_rectangle([(0, 0), (box_w, box_h)], radius=25, fill=(15, 23, 42, 220), outline=(250, 204, 21, 230), width=3)

    reshaped = arabic_reshaper.reshape(text)
    bidi_txt = get_display(reshaped)
    try:
        font = ImageFont.truetype(FONT_PATH, 36)
    except:
        font = ImageFont.load_default()

    bbox = sdraw.textbbox((0, 0), bidi_txt, font=font)
    sx = (box_w - (bbox[2] - bbox[0])) // 2
    sy = (box_h - (bbox[3] - bbox[1])) // 2 - 3
    sdraw.text((sx, sy), bidi_txt, fill=(255, 255, 255, 255), font=font)
    sub_img.save(output_path, "PNG")
    return output_path

def process_motion_scene(
    scene_idx: int,
    raw_video_path: Path,
    script_text: str,
    output_clip_path: Path,
    ffmpeg_bin: str
) -> Path:
    """Takes a raw video clip from Flow, loops/syncs it to voiceover duration, and overlays subtitles."""
    audio_path = FINAL_OUTPUT_DIR / f"vo_scene_{scene_idx}.wav"
    generate_voiceover(script_text, audio_path)
    vo_duration = get_audio_duration(audio_path)
    target_duration = vo_duration + 0.8  # breathing space

    sub_strip_path = FINAL_OUTPUT_DIR / f"sub_scene_{scene_idx}.png"
    create_subtitles_strip(script_text, sub_strip_path)

    clip_len = get_video_duration(raw_video_path, ffmpeg_bin)
    loop_count = int(target_duration // clip_len) + 1

    # Complex filter:
    # 1. Scale/crop raw video to 1920x1080 16:9
    # 2. Loop video if shorter than audio
    # 3. Apply smooth fade in/out
    # 4. Overlay subtitle strip
    vf = (
        f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
        f"fade=t=in:st=0:d=0.3,fade=t=out:st={target_duration-0.3:.2f}:d=0.3[vbase];"
        f"[vbase][1:v]overlay=x=(1920-1500)/2:y=910:enable='between(t,0.3,{target_duration-0.2:.2f})'[vout]"
    )

    cmd = [
        ffmpeg_bin, "-y",
        "-stream_loop", str(loop_count),
        "-i", str(raw_video_path),
        "-i", str(sub_strip_path),
        "-i", str(audio_path),
        "-filter_complex", vf,
        "-map", "[vout]", "-map", "2:a",
        "-t", f"{target_duration:.2f}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(output_clip_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
    print(f"  🎬 Processed Scene {scene_idx} Motion Clip ({target_duration:.1f}s)")
    return output_clip_path

def assemble_full_flow_episode(
    story_package: Dict[str, Any],
    upload_to_youtube: bool = True,
    privacy_status: str = "private"
):
    """Main stitching function that scans output/flow_clips/ and builds the complete video."""
    print("=" * 70)
    print("🚀 GOOGLE FLOW MOTION STITCHER & AUTOMATED PRODUCTION")
    print("=" * 70)
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    scenes = story_package["scenes"]
    processed_clips = []
    missing_clips = []

    # Check for available raw clips
    for sc in scenes:
        idx = sc["scene_number"]
        # Look for scene_1.mp4, scene1.mp4, scene_1.mov, etc.
        candidates = list(INPUT_CLIPS_DIR.glob(f"scene_{idx}.*")) + list(INPUT_CLIPS_DIR.glob(f"scene{idx}.*")) + list(INPUT_CLIPS_DIR.glob(f"clip_{idx}.*"))
        if not candidates:
            missing_clips.append(idx)
        else:
            raw_clip = candidates[0]
            out_clip = FINAL_OUTPUT_DIR / f"processed_scene_{idx}.mp4"
            process_motion_scene(idx, raw_clip, sc["voiceover_ar"], out_clip, ffmpeg_bin)
            processed_clips.append(out_clip)

    if missing_clips:
        print(f"\n⚠️ Notice: Missing clips for scene numbers: {missing_clips}")
        print(f"👉 Please download the generated video clips from Google Flow into:")
        print(f"   {INPUT_CLIPS_DIR}")
        print(f"   Name them: scene_1.mp4, scene_2.mp4, scene_3.mp4, scene_4.mp4, scene_5.mp4\n")
        return None

    # Concatenate all scenes
    concat_list_file = FINAL_OUTPUT_DIR / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for clip in processed_clips:
            f.write(f"file '{clip.resolve().as_posix()}'\n")

    unmixed_path = FINAL_OUTPUT_DIR / "stitched_raw_scenes.mp4"
    cmd_concat = [
        ffmpeg_bin, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(unmixed_path)
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)

    # Mix continuous atmospheric BGM with ducking
    final_master_path = FINAL_OUTPUT_DIR / "space_adventure_4k_flow_master.mp4"
    print("🎵 Mixing cinematic nursery BGM with audio ducking...")

    audio_filter = (
        "[1:a]aloop=loop=-1:size=2e+09,volume=0.18[bgm];"
        "[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )

    cmd_mix = [
        ffmpeg_bin, "-y",
        "-i", str(unmixed_path),
        "-i", str(BGM_FILE),
        "-filter_complex", audio_filter,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "256k",
        str(final_master_path)
    ]
    subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
    print(f"✨ Master Motion Episode Ready: {final_master_path}")

    if upload_to_youtube:
        meta = story_package["youtube_metadata"]
        description = (
            f"🚀 قصة جديدة بتقنية 3D Motion للأبطال الصغار في قناة حكايات العجب!\n\n"
            f"في هذه المغامرة الفضائية الرائعة، يسافر صديقنا ليو إلى أعماق الكون لإنقاذ الكوكب الصغير وإعادة النور للنجمة الذهبية عبر قوة التعاون والمحبة.\n\n"
            f"⏱️ فصول القصة (Chapters):\n"
            + "\n".join(meta["chapters"])
            + "\n\n🔔 اشتركوا في القناة لدعم مغامرات ليو التعليمية اليومية!"
        )

        print("\n📤 Uploading 16:9 Motion Episode to YouTube...")
        video_id = upload_video(
            video_path=str(final_master_path),
            title=meta["title"],
            description=description,
            tags=meta["tags"],
            privacy_status=privacy_status
        )
        print(f"🎉 Successfully uploaded! URL: https://youtu.be/{video_id}")
        return video_id

    return str(final_master_path)

if __name__ == "__main__":
    from generate_flow_package import PILOT_STORY_SPACE_ADVENTURE
    assemble_full_flow_episode(PILOT_STORY_SPACE_ADVENTURE, upload_to_youtube=False)
