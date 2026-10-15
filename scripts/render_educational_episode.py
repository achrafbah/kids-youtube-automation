"""Educational Manners & Early Learning Episode Generator (Ages 3-10).
Theme: Polite Words & Respect (Manners, Preschool & Kindergarten).
Uploads to YouTube as Private / Draft.
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
OUTPUT_DIR = BASE_DIR / "output" / "educational_manners_ep"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load GEMINI_API_KEY from .env
ENV_FILE = BASE_DIR / ".env"
GEMINI_API_KEY = "AQ.Ab8RN6Ly6CghBsKIp9KFboAoEWe_N7hlrKwYhzBosimjI_JVrA"
if ENV_FILE.exists():
    for line in open(ENV_FILE, encoding="utf-8"):
        if line.startswith("GEMINI_API_KEY="):
            GEMINI_API_KEY = line.strip().split("=", 1)[1]

IMAGE_SRC = Path(r"C:\Users\SetupGame\.gemini\antigravity\brain\59f1f52c-a76a-49d9-b49d-6025282b0bba\leo_manners_classroom_1791849746174.jpg")

ARABIC_EDUCATIONAL_SCRIPT = (
    "أَهْلًا يَا أَبْطَالَ حِكَايَاتِ العَجَائِب! "
    "هَلْ تَعْلَمُونَ أَنَّ لَدَيْنَا كَلِمَاتٍ سِحْرِيَّةً تَجْعَلُ كُلَّ النَّاسِ يُحِبُّونَنَا؟ "
    "عِنْدَمَا نَطْلُبُ لُعْبَةً أَوْ مُسَاعَدَةً مِنْ مَامَا أَوْ صَدِيقِنَا، نَقُولُ بِأَدَب: مِنْ فَضْلِك! "
    "وَعِنْدَمَا يُقَدِّمُ لَنَا أَحَدٌ شَيْئًا جَمِيلًا، نَبْتَسِمُ وَنَقُول: شُكْرًا لَك! "
    "الكَلِمَةُ الطَّيِّبَةُ تَصْنَعُ الفَرَحَ وَالمَحَبَّة.. كُونُوا دَوْمًا أَبْطَالَ الأَدَبِ وَالأَخْلَاق!"
)

def generate_gemini_speech(text, output_audio_path):
    print("🎙️ Generating educational storytelling voiceover with Gemini 3.8 Flash TTS...", flush=True)
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
                    "style": "warm, encouraging, gentle, and highly expressive kindergarten teacher and cartoon narrator",
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
    print(f"✅ Voiceover saved ({len(audio_bytes)} bytes) at: {output_audio_path}", flush=True)

def assemble_video(image_path, audio_path, output_video_path):
    print("Preparing 9:16 frame for YouTube Shorts...", flush=True)
    img = Image.open(image_path)
    w, h = img.size
    if w % 2 != 0: w -= 1
    if h % 2 != 0: h -= 1
    img = img.resize((w, h), Image.Resampling.LANCZOS)
    temp_img = OUTPUT_DIR / "classroom_frame.jpg"
    img.save(temp_img, quality=95)

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    print("Rendering educational video with ffmpeg...", flush=True)
    
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
    print(f"✅ Educational Video rendered successfully: {output_video_path}", flush=True)

def main():
    audio_path = OUTPUT_DIR / "manners_voiceover.wav"
    video_path = OUTPUT_DIR / "polite_words_episode.mp4"

    # Step 1: Voiceover
    generate_gemini_speech(ARABIC_EDUCATIONAL_SCRIPT, audio_path)

    # Step 2: Assemble Video
    assemble_video(IMAGE_SRC, audio_path, video_path)

    # Step 3: Upload to YouTube as Private / Draft
    print("\n🚀 Uploading educational episode as PRIVATE / DRAFT to 'Tales of Wonder'...", flush=True)
    title = "سِحْرُ الكَلِمَاتِ الطَّيِّبَة: مِنْ فَضْلِكَ وَشُكْرًا ✨ | آداب وأخلاق للأطفال 🌟"
    description = (
        "مرحباً بكم في حكايات العجائب (Tales of Wonder)! 🌟\n\n"
        "حلقة تربوية وتعليمية هادفة للأطفال (3 إلى 10 سنوات):\n"
        "💡 موضوع اليوم: آداب الكلام والتربية الحسنة (الكلمات السحرية: من فضلك وشكراً).\n"
        "🎯 الهدف التربوي: تعليم الطفل أسلوب الطلب بأدب، وشكر الوالدين والأصدقاء والمعلمين.\n\n"
        "برنامج تعليمي متكامل للروضة والمستوى التأسيسي الأول.\n\n"
        "اشتركوا في القناة لدعم المحتوى الهادف والمفيد لأطفالنا!\n\n"
        "#shorts #أطفال #تربية_الطفل #آداب_الأطفال #تعليم_الروضة #قصص_تعليمية #talesofwonder"
    )
    tags = ["#shorts", "#أطفال", "#تربية_الطفل", "#آداب_الأطفال", "#تعليم_الروضة", "#أخلاق_حميدة", "#talesofwonder"]

    result = upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        privacy_status="private",  # Strictly DRAFT / PRIVATE
        made_for_kids=True,
        thumbnail_path=str(IMAGE_SRC)
    )

    if result:
        print("\n" + "=" * 50, flush=True)
        print("🎉 SUCCESSFUL EDUCATIONAL DRAFT EPISODE UPLOAD!", flush=True)
        print(f"Video URL: {result['video_url']}", flush=True)
        print(f"Status: {result['status']} (DRAFT / PRIVATE)", flush=True)
        print("=" * 50, flush=True)
    else:
        print("❌ Upload failed. Please check logs.", flush=True)

if __name__ == "__main__":
    main()
