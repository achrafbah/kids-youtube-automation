import sys
from google import genai
from google.genai import types

api_key = "AQ.Ab8RN6Ly6CghBsKIp9KFboAoEWe_N7hlrKwYhzBosimjI_JVrA"
client = genai.Client(api_key=api_key)

print("1. Testing image generation (gemini-3.1-flash-image)...")
try:
    img_resp = client.models.generate_content(
        model="gemini-3.1-flash-image",
        contents="Cute 3D Pixar character smiling in kindergarten classroom, vibrant colors, 9:16 vertical",
        config={"response_modalities": ["IMAGE"]}
    )
    print("SUCCESS: Image generation works!")
except Exception as e:
    print(f"Image gen error: {e}")

print("\n2. Testing gemini-omni-1.1-flash...")
try:
    omni_resp = client.models.generate_content(
        model="gemini-omni-1.1-flash",
        contents="Cute animated boy smiling and waving hand",
    )
    print("SUCCESS: gemini-omni-1.1-flash works!")
except Exception as e:
    print(f"Omni error: {e}")
