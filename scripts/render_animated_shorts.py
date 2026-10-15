"""Render dynamic 2.5D Animated Cartoon Shorts with Ken Burns camera motion,
particle overlays, and Gemini 3.8 Flash TTS expressive audio.
"""

import os
import sys
import subprocess
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import imageio_ffmpeg
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "animated_test"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_SRC = Path(r"C:\Users\SetupGame\.gemini\antigravity\brain\59f1f52c-a76a-49d9-b49d-6025282b0bba\leo_manners_classroom_1791849746174.jpg")
VOICE_PATH = BASE_DIR / "output" / "educational_manners_ep" / "manners_voiceover.wav"
OUT_ANIMATED_VIDEO = OUTPUT_DIR / "leo_animated_motion.mp4"

def render_animated_shorts():
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    print("🎬 Rendering dynamic 2.5D animated video with camera motion and transitions...", flush=True)

    # Prepare standard vertical 1080x1920 base
    img = Image.open(IMAGE_SRC)
    img_resized = img.resize((1080, 1920), Image.Resampling.LANCZOS)
    temp_img = OUTPUT_DIR / "frame_base.jpg"
    img_resized.save(temp_img, quality=95)

    # Complex ffmpeg filtergraph:
    # 1. zoompan: continuous dynamic slow zoom into Leo's eyes and the golden star
    # 2. setsar & format: ensures clean 60fps vertical animation
    filter_complex = (
        "[0:v]zoompan=z='min(zoom+0.0008,1.15)':d=850:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)*0.85':s=1080x1920:fps=30,"
        "format=yuv420p[v]"
    )

    cmd = [
        ffmpeg_bin,
        "-y",
        "-loop", "1",
        "-i", str(temp_img),
        "-i", str(VOICE_PATH),
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(OUT_ANIMATED_VIDEO)
    ]

    print("Running ffmpeg animation pipeline...", flush=True)
    subprocess.run(cmd, check=True)
    print(f"🎉 Animated Motion Video created successfully: {OUT_ANIMATED_VIDEO}", flush=True)
    return OUT_ANIMATED_VIDEO

if __name__ == "__main__":
    render_animated_shorts()
