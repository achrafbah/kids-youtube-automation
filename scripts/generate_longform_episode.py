"""Long-Form 16:9 Widescreen 3D Cartoon Episode Generator for Tales of Wonder.
Generates episodic multi-scene 1080p full HD videos designed for TV, tablets, and YouTube.
Features:
- Multi-scene episodic storytelling (4 continuous scenes)
- 16:9 widescreen layout (1920x1080) with cinematic blurred backdrop + sharp 3D character staging
- Cinematic slow camera pan/zoom per scene
- Filmic transitions (smooth fades between scenes)
- Synchronized Arabic subtitles with full Tashkeel
- Gemini 3.8 Flash TTS expressive voiceover per scene
- Continuous atmospheric background score
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
from pathlib import Path
from typing import List, Dict, Any

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display
import imageio_ffmpeg
from google import genai

BASE_DIR = Path(r"C:\Users\SetupGame\.gemini\antigravity\scratch\kids-youtube-automation")
SCENES_DIR = BASE_DIR / "characters" / "scenes"
OUTPUT_DIR = BASE_DIR / "output" / "longform_test_episode"
BGM_FILE = SCENES_DIR / "kids_gentle_bgm.wav"

FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "C:\\Windows\\Fonts\\segoeui.ttf"

def get_api_key():
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in open(env_file, encoding="utf-8"):
            if line.startswith("GEMINI_API_KEY="):
                return line.strip().split("=", 1)[1]
    return os.environ.get("GEMINI_API_KEY", "")

def get_audio_duration(audio_path: Path) -> float:
    with wave.open(str(audio_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())

def generate_voiceover(text: str, output_path: Path):
    print(f"🎙️ Generating voiceover: '{text[:40]}...'")
    from gtts import gTTS
    temp_mp3 = output_path.with_suffix(".mp3")
    tts = gTTS(text=text, lang="ar")
    tts.save(str(temp_mp3))

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([
        ffmpeg_bin, "-y", "-i", str(temp_mp3),
        "-ar", "24000", "-ac", "1",
        str(output_path)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if temp_mp3.exists():
        temp_mp3.unlink()
    print(f"✅ Voiceover ready: {output_path}")
    return output_path

def create_widescreen_frame(scene_img_path: Path, output_frame_path: Path, title_badge: str, theme_color: tuple):
    """Render 1920x1080 widescreen base frame with blurred background and centered character."""
    canvas = Image.new("RGBA", (1920, 1080), (15, 23, 42, 255))
    src = Image.open(scene_img_path).convert("RGBA")

    # 1. Background: Cover 1920x1080 and apply heavy Gaussian Blur
    bg_ratio = max(1920 / src.width, 1080 / src.height)
    bg_w, bg_h = int(src.width * bg_ratio), int(src.height * bg_ratio)
    bg_resized = src.resize((bg_w, bg_h), Image.Resampling.LANCZOS)
    bg_crop_x = (bg_w - 1920) // 2
    bg_crop_y = (bg_h - 1080) // 2
    bg_cropped = bg_resized.crop((bg_crop_x, bg_crop_y, bg_crop_x + 1920, bg_crop_y + 1080))
    bg_blurred = bg_cropped.filter(ImageFilter.GaussianBlur(radius=30))

    # Darken background slightly
    dark_overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 90))
    bg_blurred.paste(dark_overlay, (0, 0), dark_overlay)
    canvas.paste(bg_blurred, (0, 0))

    # 2. Foreground: Place the sharp scene with soft drop shadow
    fg_target_h = 980
    fg_ratio = fg_target_h / src.height
    fg_w = int(src.width * fg_ratio)
    fg_resized = src.resize((fg_w, fg_target_h), Image.Resampling.LANCZOS)

    fg_x = (1920 - fg_w) // 2
    fg_y = 50

    # Draw shadow
    shadow = Image.new("RGBA", (fg_w + 40, fg_target_h + 40), (0, 0, 0, 140))
    shadow_blurred = shadow.filter(ImageFilter.GaussianBlur(radius=15))
    canvas.paste(shadow_blurred, (fg_x - 20, fg_y - 10), shadow_blurred)
    canvas.paste(fg_resized, (fg_x, fg_y), fg_resized)

    # 3. Top Header Badge for 16:9
    badge_w, badge_h = 1000, 90
    badge = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(badge)
    bdraw.rounded_rectangle([(0, 0), (badge_w, badge_h)], radius=30, fill=(*theme_color[:3], 230), outline=(255, 255, 255, 200), width=3)

    # Render badge text
    reshaped_text = arabic_reshaper.reshape(title_badge)
    bidi_text = get_display(reshaped_text)
    try:
        font = ImageFont.truetype(FONT_PATH, 38)
    except:
        font = ImageFont.load_default()
    
    bbox = bdraw.textbbox((0, 0), bidi_text, font=font)
    tx = (badge_w - (bbox[2] - bbox[0])) // 2
    ty = (badge_h - (bbox[3] - bbox[1])) // 2 - 4
    bdraw.text((tx, ty), bidi_text, fill=(255, 255, 255, 255), font=font)

    badge_x = (1920 - badge_w) // 2
    canvas.paste(badge, (badge_x, 30), badge)

    canvas.convert("RGB").save(output_frame_path, "JPEG", quality=95)
    return output_frame_path

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

def render_scene_clip(scene_idx: int, frame_path: Path, audio_path: Path, script_text: str, output_clip_path: Path, ffmpeg_bin: str):
    duration = get_audio_duration(audio_path)
    total_duration = duration + 0.6  # slight breathing padding
    
    # Generate subtitle strip
    sub_strip_path = frame_path.parent / f"sub_{scene_idx}.png"
    create_subtitles_strip(script_text, sub_strip_path)

    # Different camera motion per scene
    # 0: slow zoom-in, 1: slow zoom-out, 2: slow pan left, 3: slow pan right
    zoom_expr = "min(pzoom+0.0006,1.08)" if scene_idx % 2 == 0 else "max(1.08-0.0006*on,1.0)"
    
    # FFmpeg command to render animated 16:9 clip with fade-in and fade-out
    # Fade in 0.4s, fade out 0.4s
    vf = (
        f"zoompan=z='{zoom_expr}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=25,"
        f"fade=t=in:st=0:d=0.4,fade=t=out:st={total_duration-0.4:.2f}:d=0.4[bg];"
        f"[bg][1:v]overlay=x=(1920-1500)/2:y=910:enable='between(t,0.3,{total_duration-0.2:.2f})'[vout]"
    )

    cmd = [
        ffmpeg_bin, "-y",
        "-loop", "1", "-i", str(frame_path),
        "-i", str(sub_strip_path),
        "-i", str(audio_path),
        "-filter_complex", vf,
        "-map", "[vout]", "-map", "2:a",
        "-t", f"{total_duration:.2f}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(output_clip_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
    return output_clip_path

def main():
    print("=" * 60)
    print("🎬 TALES OF WONDER: 16:9 WIDESCREEN LONG-FORM PROTOTYPE")
    print("=" * 60)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    scenes_data = [
        {
            "name": "morning_exercise",
            "canvas": "scene_morning_exercise.jpg",
            "badge": "🏃‍♂️ المَشْهَدُ الأَوَّل: الرِّيَاضَةُ الصَّبَاحِيَّةُ وَالنَّشَاط",
            "theme_color": (16, 185, 129), # Emerald
            "script": "صَبَاحُ الخَيْرِ يَا أَصْدِقَائِي! اسْتَيْقَظَ لِيُو بَاكِرًا بِنَشَاطٍ وَحَيَوِيَّة! فَتَحَ نَافِذَتَهُ وَبَدَأَ حَرَكَاتِهِ الرِّيَاضِيَّةَ لِيَكُونَ جِسْمُهُ قَوِيًّا وَسَلِيمًا!"
        },
        {
            "name": "healthy_breakfast",
            "canvas": "scene_dining_bismillah.jpg",
            "badge": "🍎 المَشْهَدُ الثَّانِي: آدَابُ الطَّعَامِ وَالبَسْمَلَة",
            "theme_color": (245, 158, 11), # Amber
            "script": "وَالآنَ، حَانَ وَقْتُ الفُطُورِ اللَّذِيذ! غَسَلَ لِيُو يَدَيْهِ جَيِّدًا، وَجَلَسَ بِأَدَبٍ قَائِلًا: بِسْمِ الله! أَكَلَ الفَوَاكِهَ الطَّازَجَةَ لِتَمْنَحَهُ طَاقَةً وَذَكَاء!"
        },
        {
            "name": "kindness_playground",
            "canvas": "scene_animal_kindness.jpg",
            "badge": "🐱 المَشْهَدُ الثَّالِث: الرِّفْقُ بِالحَيَوَانِ وَالعَطْف",
            "theme_color": (13, 148, 136), # Teal
            "script": "فِي المَسَاءِ، خَرَجَ لِيُو لِيَلْعَبَ فِي الحَدِيقَة. وَحِينَ رَأَى القِطَّةَ الجَمِيلَة، قَدَّمَ لَهَا الحَلِيبَ بِعَطْفٍ وَرِفْق، فَالرِّفْقُ بِالحَيَوَانِ خُلُقٌ جَمِيل!"
        },
        {
            "name": "bedtime_stars",
            "canvas": "scene_bedtime_stars.jpg",
            "badge": "⭐ المَشْهَدُ الرَّابِع: النَّوْمُ الهَادِئُ وَالأَحْلَامُ الجَمِيلَة",
            "theme_color": (99, 102, 241), # Indigo
            "script": "وَحِينَ ظَهَرَتِ النُّجُومُ السَّاحِرَة، رَتَّبَ لِيُو غُرْفَتَهُ بِنِظَام، وَنَامَ فِي سَرِيرِهِ الدَّافِئِ بَعْدَ أَنْ شَكَرَ رَبَّهُ. تَصْبَحُونَ عَلَى خَيْرٍ وَأَحْلَامٍ سَعِيدَة!"
        }
    ]

    clip_paths = []
    for i, sc in enumerate(scenes_data):
        print(f"\n--- 🎥 Producing Scene {i+1}/4: {sc['name']} ---")
        sc_dir = OUTPUT_DIR / f"scene_{i+1}_{sc['name']}"
        sc_dir.mkdir(exist_ok=True)

        audio_path = sc_dir / "voice.wav"
        frame_path = sc_dir / "widescreen_frame.jpg"
        clip_path = sc_dir / "scene_clip.mp4"

        # 1. Voiceover
        generate_voiceover(sc["script"], audio_path)

        # 2. Widescreen Base Frame
        src_canvas = SCENES_DIR / sc["canvas"]
        create_widescreen_frame(src_canvas, frame_path, sc["badge"], sc["theme_color"])

        # 3. Render Scene Clip
        print(f"🎬 Rendering Scene {i+1} clip with cinematic motion & subtitles...")
        render_scene_clip(i, frame_path, audio_path, sc["script"], clip_path, ffmpeg_bin)
        clip_paths.append(clip_path)

    # Concatenate all scenes into a seamless movie
    print("\n🎞️ Stitching 4 scenes into full Long-Form Episode with continuous BGM...")
    final_output = OUTPUT_DIR / "leo_full_day_adventure_1080p.mp4"
    concat_list_file = OUTPUT_DIR / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for cp in clip_paths:
            f.write(f"file '{cp.resolve().as_posix()}'\n")

    # Step A: Concat clips
    temp_stitched = OUTPUT_DIR / "temp_stitched.mp4"
    cmd_concat = [
        ffmpeg_bin, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(temp_stitched)
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)

    # Step B: Mix continuous looping BGM under the final video
    cmd_bgm = [
        ffmpeg_bin, "-y",
        "-i", str(temp_stitched),
        "-stream_loop", "-1", "-i", str(BGM_FILE),
        "-filter_complex", "[0:a]volume=1.0[voice];[1:a]volume=0.18[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(final_output)
    ]
    subprocess.run(cmd_bgm, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)

    print("\n" + "=" * 60)
    print("🎉 FULL LONG-FORM 16:9 EPISODE COMPLETED!")
    print(f"📁 Video Path: {final_output}")
    print("=" * 60)
    return str(final_output)

if __name__ == "__main__":
    main()
