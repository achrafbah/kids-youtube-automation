import subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "test_effects"
SCENES_DIR = BASE_DIR / "characters" / "scenes"

ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

scene_img = SCENES_DIR / "manners_classroom.jpg"
audio_path = BASE_DIR / "output" / "2026-10-15_sharing-is-caring" / "voiceover.wav"
bgm_path = SCENES_DIR / "kids_gentle_bgm.wav"

header_p = OUTPUT_DIR / "header_badge.png"
sub_p = OUTPUT_DIR / "sub_test.png"
star_p = OUTPUT_DIR / "star.png"
out_video = OUTPUT_DIR / "test_animated_short.mp4"

# Base 1080x1920
img = Image.open(scene_img).resize((1080, 1920), Image.Resampling.LANCZOS)
temp_base = OUTPUT_DIR / "temp_base.jpg"
img.save(temp_base, quality=95)

filter_complex = (
    # 1. Base scene camera zoom and pan (dynamic Ken Burns)
    "[0:v]zoompan=z='min(zoom+0.0008,1.15)':d=800:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)*0.85':s=1080x1920:fps=30,format=yuv420p[base];"
    # 2. Header badge at top
    "[base][3:v]overlay=x=(W-w)/2:y=120[v1];"
    # 3. Subtitle card at bottom
    "[v1][4:v]overlay=x=(W-w)/2:y=H-h-200[v2];"
    # 4. Floating animated star left
    "[v2][5:v]overlay=x='100+30*sin(t*2.5)':y='320+25*cos(t*2)':eval=frame[v3];"
    # 5. Floating animated star right
    "[v3][5:v]overlay=x='W-w-100+30*cos(t*2.5)':y='350+25*sin(t*2)':eval=frame[v];"
    # Audio mix
    "[1:a]volume=1.0[voice];"
    "[2:a]volume=0.12[bgm];"
    "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
)

cmd = [
    ffmpeg_bin,
    "-y",
    "-loop", "1", "-i", str(temp_base),
    "-i", str(audio_path),
    "-stream_loop", "-1", "-i", str(bgm_path),
    "-i", str(header_p),
    "-i", str(sub_p),
    "-i", str(star_p),
    "-filter_complex", filter_complex,
    "-map", "[v]",
    "-map", "[a]",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "20",
    "-c:a", "aac",
    "-b:a", "192k",
    "-t", "5",  # 5-second test
    str(out_video)
]

print("Rendering 5s test video with graphic overlays...")
subprocess.run(cmd, check=True)
print(f"SUCCESS! Rendered to {out_video}")
