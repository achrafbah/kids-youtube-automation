"""Render YouTube Shorts educational video using Gemini 3.8 Flash TTS for expressive, natural voiceover,
and upload directly as Private / Draft to the YouTube channel Tales of Wonder.
"""

import os
import sys
import base64
import subprocess
from pathlib import Path

# Fix Windows console encoding for Arabic characters
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google import genai
from PIL import Image
import imageio_ffmpeg
from youtube_uploader import upload_video

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "live_test"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load GEMINI_API_KEY from .env
ENV_FILE = BASE_DIR / ".env"
GEMINI_API_KEY = "AQ.Ab8RN6Ly6CghBsKIp9KFboAoEWe_N7hlrKwYhzBosimjI_JVrA"
if ENV_FILE.exists():
    for line in open(ENV_FILE, encoding="utf-8"):
        if line.startswith("GEMINI_API_KEY="):
            GEMINI_API_KEY = line.strip().split("=", 1)[1]

IMAGE_SRC = Path(r"C:\Users\SetupGame\.gemini\antigravity\brain\59f1f52c-a76a-49d9-b49d-6025282b0bba\leo_rain_adventure_1791846781665.jpg")

ARABIC_TEXT = (
    "مَرْحَبًا يَا أَصْدِقَائِي الصِّغَار فِي قَنَاة حِكَايَاتِ العَجَائِب! "
    "أَنَا لَيْث، وَأُحِبُّ اسْتِكْشَافَ الطَّبِيعَةِ مَعَكُمْ! "
    "انْظُرُوا إِلَى المَطَرِ البَدِيع! المَطَرُ يَسْقِي الأَشْجَارَ وَالأَزْهَارَ وَيَمْلأُ الأَرْضَ حَيَاةً وَجَمَالاً! "
    "نَلْتَقِي كُلَّ يَوْمٍ فِي مُغَامَرَةٍ جَدِيدَةٍ وَمُمْتِعَة!"
)

def generate_gemini_speech(text, output_audio_path):
    print("🎙️ Generating expressive Arabic voiceover with Gemini 3.8 Flash TTS...", flush=True)
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    interaction = client.interactions.create(
        model="gemini-3.8-flash-tts",
        input=[{
            "type": "user_input",
            "content": [{
                "type": "text",
                "text": text,
                "annotations": [{
                    "type": "speech_metadata",
                    "style": "cheerful, warm, and highly expressive kids cartoon storyteller",
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
    with open(output_audio_path, "wb") as f:
        f.write(audio_bytes)
    print(f"✅ High-fidelity audio saved ({len(audio_bytes)} bytes) at: {output_audio_path}", flush=True)

def assemble_video(image_path, audio_path, output_video_path):
    print("Preparing 9:16 frame for YouTube Shorts...", flush=True)
    img = Image.open(image_path)
    w, h = img.size
    if w % 2 != 0: w -= 1
    if h % 2 != 0: h -= 1
    img = img.resize((w, h), Image.Resampling.LANCZOS)
    temp_img = OUTPUT_DIR / "prepared_frame.jpg"
    img.save(temp_img, quality=95)

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    print("Rendering video with ffmpeg...", flush=True)
    
    cmd = [
        ffmpeg_bin,
        "-y",
        "-loop", "1",
        "-i", str(temp_img),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_video_path)
    ]
    
    subprocess.run(cmd, check=True)
    print(f"✅ Video rendered successfully: {output_video_path}", flush=True)

def main():
    audio_path = OUTPUT_DIR / "gemini_voiceover.wav"
    video_path = OUTPUT_DIR / "gemini_draft_story.mp4"

    # Step 1: Gemini 3.8 Flash TTS Voiceover
    generate_gemini_speech(ARABIC_TEXT, audio_path)

    # Step 2: Assemble Video
    assemble_video(IMAGE_SRC, audio_path, video_path)

    # Step 3: Upload to YouTube as DRAFT / PRIVATE
    print("\n🚀 Uploading video as PRIVATE / DRAFT to YouTube channel 'Tales of Wonder'...", flush=True)
    title = "سِرُّ المَطَرِ البَدِيع 🌧️ | مغامرات ليث للأطفال (نسخة الصوت الاحترافي) 🌟"
    description = (
        "مرحباً بكم يا أبطال في قناة Tales of Wonder!\n"
        "مغامرة اليوم التعليمية مع ليث بصوت Gemini 3.8 الطبيعي والمعبر للأطفال!\n"
        "من أين يأتي المطر ولماذا تحبه الأشجار والأزهار؟ 🌸🌧️\n\n"
        "اشتركوا معنا لتتعلموا كل يوم قصة جديدة ومفيدة!\n\n"
        "#shorts #أطفال #كرتون_تعليمي #العربية_للأطفال #قصص_أطفال #talesofwonder"
    )
    tags = ["#shorts", "#أطفال", "#كرتون_تعليمي", "#العربية_للأطفال", "#المطر", "#talesofwonder"]

    result = upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        privacy_status="private",  # Always DRAFT / PRIVATE so user reviews and publishes manually
        made_for_kids=True,
        thumbnail_path=str(IMAGE_SRC)
    )

    if result:
        print("\n" + "=" * 50, flush=True)
        print("🎉 SUCCESSFUL DRAFT UPLOAD WITH GEMINI TTS!", flush=True)
        print(f"Video URL: {result['video_url']}", flush=True)
        print(f"Status: {result['status']} (DRAFT / PRIVATE)", flush=True)
        print("=" * 50, flush=True)
    else:
        print("❌ Upload failed. Please check logs.", flush=True)

if __name__ == "__main__":
    main()
