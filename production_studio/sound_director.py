"""Sound & Voice Director Agent (قسم الصوت والدوبلاج).
Directs Gemini 3.8 Flash TTS expressive speech synthesis and audio post-mastering.
"""

import base64
from pathlib import Path
from typing import Dict, Any, Optional
from .base import BaseAgent

class SoundDirectorAgent(BaseAgent):
    """Specialist agent responsible for voice acting direction, TTS synthesis, and sound design."""

    def __init__(self):
        super().__init__(
            name="Amir Bencherif",
            role="Lead Sound & Voice Director"
        )
        self.default_voice = "Kore"
        self.default_style = (
            "warm, gentle, encouraging, and highly expressive kindergarten teacher and cartoon narrator"
        )

    def synthesize_expressive_speech(
        self,
        text: str,
        output_audio_path: Path,
        voice: Optional[str] = None,
        style: Optional[str] = None
    ) -> Path:
        """Synthesize Arabic speech with emotional nuance using Gemini 3.8 Flash TTS."""
        voice = voice or self.default_voice
        style = style or self.default_style
        
        self.log(f"🎙️ Synthesizing expressive Arabic voiceover (Voice: {voice}, Model: gemini-3.8-flash-tts)...")
        output_audio_path.parent.mkdir(parents=True, exist_ok=True)

        interaction = self.client.interactions.create(
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

        self.log(f"✅ Voiceover mastered and saved: {output_audio_path}")
        return output_audio_path

    def run(
        self,
        script_text: str,
        output_audio_path: Optional[Path] = None,
        voice: Optional[str] = None,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute sound direction workflow."""
        if not output_audio_path:
            output_audio_path = self.output_dir / "studio_renders" / "voiceover_master.wav"

        audio_file = self.synthesize_expressive_speech(
            text=script_text,
            output_audio_path=output_audio_path,
            voice=voice,
            style=style
        )

        return {
            "status": "success",
            "audio_path": str(audio_file),
            "voice": voice or self.default_voice,
            "engine": "gemini-3.8-flash-tts"
        }
