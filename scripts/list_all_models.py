import os
from google import genai

api_key = "AQ.Ab8RN6Ly6CghBsKIp9KFboAoEWe_N7hlrKwYhzBosimjI_JVrA"
client = genai.Client(api_key=api_key)

models = list(client.models.list())
print(f"TOTAL MODELS AVAILABLE: {len(models)}\n")

categories = {
    "Video Generation (Veo / Omni)": [],
    "Image Generation (Imagen / Nano Banana)": [],
    "Speech & Audio (TTS / Live Audio)": [],
    "Core Reasoning & Multimodal (Gemini 2.5 / 3.x)": [],
    "Other / Specialized": []
}

for m in sorted(models, key=lambda x: x.name):
    name = m.name
    display = getattr(m, "display_name", "")
    entry = f"{name} ({display})" if display else name
    
    if any(k in name for k in ["veo", "omni", "video"]):
        categories["Video Generation (Veo / Omni)"].append(entry)
    elif any(k in name for k in ["image", "imagen", "banana"]):
        categories["Image Generation (Imagen / Nano Banana)"].append(entry)
    elif any(k in name for k in ["tts", "audio", "voice", "speech"]):
        categories["Speech & Audio (TTS / Live Audio)"].append(entry)
    elif any(k in name for k in ["gemini-2.5", "gemini-3", "pro", "flash"]):
        categories["Core Reasoning & Multimodal (Gemini 2.5 / 3.x)"].append(entry)
    else:
        categories["Other / Specialized"].append(entry)

for cat, items in categories.items():
    print(f"=== {cat} ({len(items)}) ===")
    for item in items:
        print(f"  • {item}")
    print()
