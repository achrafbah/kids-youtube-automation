import sys
from pathlib import Path
from google import genai
from google.genai import types

api_key = "AQ.Ab8RN6Ly6CghBsKIp9KFboAoEWe_N7hlrKwYhzBosimjI_JVrA"
client = genai.Client(api_key=api_key)

BASE_DIR = Path(__file__).resolve().parent.parent
scene_img_path = BASE_DIR / "characters" / "scenes" / "manners_classroom.jpg"
with open(scene_img_path, "rb") as f:
    img_bytes = f.read()

image = types.Image(image_bytes=img_bytes, mime_type="image/jpeg")
prompt = "The 3D cartoon boy Leo smiles and waves his hand in the classroom."

for dur in [None, 4, 5, 6, 7, 8]:
    print(f"Testing duration_seconds = {dur}...")
    try:
        config_args = {"aspect_ratio": "9:16"}
        if dur is not None:
            config_args["duration_seconds"] = dur
        operation = client.models.generate_videos(
            model="veo-3.1-fast-generate-preview",
            source=types.GenerateVideosSource(
                prompt=prompt,
                image=image
            ),
            config=types.GenerateVideosConfig(**config_args)
        )
        print(f"SUCCESS with duration_seconds={dur}! Operation: {operation.name}")
        break
    except Exception as e:
        print(f"Failed with {dur}: {e}")
