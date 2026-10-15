"""Test Veo 3.1 Fast Image-to-Video Generation with Google GenAI SDK.
Animates the Pixar 3D character Leo into real motion video.
"""

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
OUTPUT_DIR = BASE_DIR / "output" / "veo_test"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_PATH = Path(r"C:\Users\SetupGame\.gemini\antigravity\brain\59f1f52c-a76a-49d9-b49d-6025282b0bba\leo_manners_classroom_1791849746174.jpg")
API_KEY = "AQ.Ab8RN6Ly6CghBsKIp9KFboAoEWe_N7hlrKwYhzBosimjI_JVrA"

def test_veo():
    print("🎬 Initializing Veo 3.1 Fast Image-to-Video...", flush=True)
    client = genai.Client(api_key=API_KEY)
    
    print(f"Loading reference frame from {IMAGE_PATH}...", flush=True)
    image = types.Image.from_file(location=str(IMAGE_PATH))

    prompt = (
        "The 3D cartoon boy Leo smiles warmly, blinks with big expressive eyes, "
        "and happily waves his hand as the magical golden star in his hands twinkles with soft sparkles. "
        "Smooth, cinematic 3D Pixar character animation."
    )

    print("Submitting video generation request to model 'veo-3.1-fast-generate-preview'...", flush=True)
    try:
        operation = client.models.generate_videos(
            model="veo-3.1-fast-generate-preview",
            source=types.GenerateVideosSource(
                prompt=prompt,
                image=image
            ),
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                duration_seconds=5,
                aspect_ratio="9:16",
            )
        )
        print(f"Operation created: {getattr(operation, 'name', 'unnamed')}. Polling status...", flush=True)
    except Exception as e:
        print(f"Error submitting Veo request: {e}", flush=True)
        return None

    poll_count = 0
    while not operation.done:
        time.sleep(10)
        poll_count += 1
        operation = client.operations.get(operation)
        print(f"Polling ({poll_count * 10}s)... Done: {operation.done}", flush=True)

    print("Operation finished! Processing output video...", flush=True)
    if hasattr(operation, "response") and operation.response and getattr(operation.response, "generated_videos", None):
        video_obj = operation.response.generated_videos[0].video
        out_video_path = OUTPUT_DIR / "veo_leo_animated.mp4"
        
        # Save or download video
        if hasattr(video_obj, "video_bytes") and video_obj.video_bytes:
            with open(out_video_path, "wb") as f:
                f.write(video_obj.video_bytes)
        else:
            client.files.download(file=video_obj, destination=str(out_video_path))
            
        print(f"🎉 VEO ANIMATION SUCCESS: Saved to {out_video_path}", flush=True)
        return out_video_path
    else:
        print(f"Operation completed without generated_videos: {operation.error or operation.response}", flush=True)
        return None

if __name__ == "__main__":
    test_veo()
