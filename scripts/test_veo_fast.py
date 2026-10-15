import os
import sys
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
SCENES_DIR = BASE_DIR / "characters" / "scenes"
OUTPUT_DIR = BASE_DIR / "output" / "veo_test"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ENV_FILE = BASE_DIR / ".env"
api_key = "AQ.Ab8RN6Ly6CghBsKIp9KFboAoEWe_N7hlrKwYhzBosimjI_JVrA"
if ENV_FILE.exists():
    for line in open(ENV_FILE, encoding="utf-8"):
        if line.startswith("GEMINI_API_KEY="):
            api_key = line.strip().split("=", 1)[1]

client = genai.Client(api_key=api_key)

scene_img_path = SCENES_DIR / "manners_classroom.jpg"
print(f"Reading image: {scene_img_path}")
with open(scene_img_path, "rb") as f:
    img_bytes = f.read()

image = types.Image(image_bytes=img_bytes, mime_type="image/jpeg")

prompt = (
    "The 3D animated cartoon boy Leo smiles warmly, blinks with big expressive eyes, "
    "and waves his hand happily to preschool children in the classroom. "
    "Pixar 3D animated character style, smooth motion."
)

print("Starting Veo 3.1 fast video generation with types.GenerateVideosSource...")
try:
    operation = client.models.generate_videos(
        model="veo-3.1-fast-generate-preview",
        source=types.GenerateVideosSource(
            prompt=prompt,
            image=image
        ),
        config=types.GenerateVideosConfig(
            aspect_ratio="9:16",
            duration_seconds=5,
        )
    )
    print(f"Operation started: {getattr(operation, 'name', 'done')}")
    poll_count = 0
    while not operation.done:
        time.sleep(10)
        poll_count += 1
        operation = client.operations.get(operation)
        print(f"Polling ({poll_count * 10}s)... Done: {operation.done}")

    print("Veo generation completed!")
    if hasattr(operation, "response") and operation.response and getattr(operation.response, "generated_videos", None):
        video_obj = operation.response.generated_videos[0].video
        out_path = OUTPUT_DIR / "veo_test_output.mp4"
        client.files.download(file=video_obj, destination=str(out_path))
        print(f"SUCCESS: Video saved to {out_path}")
    else:
        print(f"Response error or empty: {operation.error or operation.response}")
except Exception as e:
    print(f"Veo Error: {e}")
