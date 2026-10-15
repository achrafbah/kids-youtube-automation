"""Gemini 3.8 Flash TTS Voiceover Engine.
Generates natural, expressive Arabic voiceovers for children's educational cartoons.
"""

import os
import sys
import base64
from pathlib import Path
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

def get_gemini_api_key():
    if ENV_FILE.exists():
        for line in open(ENV_FILE, encoding="utf-8"):
            if line.startswith("GEMINI_API_KEY="):
                return line.strip().split("=", 1)[1]
    return os.environ.get("GEMINI_API_KEY", "")

def generate_arabic_voiceover(text, output_audio_path, style="cheerful, warm, and highly expressive kids cartoon storyteller", voice="Kore"):
    api_key = get_gemini_api_key()
    client = genai.Client(api_key=api_key)

    interaction = client.interactions.create(
        model="gemini-3.8-flash-tts",
        input=[{
            "type": "user_input",
            "content": [{
                "type": "text",
                "text": text,
                "annotations": [{
                    "type": "speech_metadata",
                    "style": style,
                }],
            }],
        }],
        response_format={"type": "audio"},
        generation_config={
            "speech_config": [
                {"voice": voice},
            ]
        },
    )

    audio_bytes = base64.b64decode(interaction.output_audio.data)
    with open(output_audio_path, "wb") as f:
        f.write(audio_bytes)
    return output_audio_path

if __name__ == "__main__":
    test_out = BASE_DIR / "output" / "test_gemini_tts.wav"
    generate_arabic_voiceover("مرحباً بكم يا أصدقائي الصغار!", test_out)
    print(f"Gemini TTS Test Success: {test_out}")
