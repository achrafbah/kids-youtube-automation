"""Art Director & Visual Designer Agent (قسم الفنون والتصميم البصري).
Maintains Pixar 3D character consistency (Leo & Mia) and crafts scene art prompts.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
from .base import BaseAgent

class ArtDirectorAgent(BaseAgent):
    """Specialist agent responsible for character visual identity, scene design, and composition."""

    def __init__(self):
        super().__init__(
            name="Marc Dupuis",
            role="Lead 3D Art Director & Character Supervisor"
        )
        self.bible_path = self.characters_dir / "character_bible.json"
        self.character_bible = self._load_bible()

    def _load_bible(self) -> Dict[str, Any]:
        if self.bible_path.exists():
            with open(self.bible_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def craft_scene_prompt(self, theme: str, environment_desc: str, character: str = "leo") -> Dict[str, str]:
        """Craft a studio-grade Pixar 3D prompt for image generation."""
        self.log(f"🎨 Designing 3D Pixar visual prompt for '{theme}' with character '{character}'...")
        
        leo_traits = (
            "6-year-old cute animated boy Leo, Pixar and Disney 3D style, messy curly brown hair, "
            "big warm expressive brown eyes, cheerful contagious smile, round friendly cheeks. "
        )
        
        prompt = (
            f"Ultra-detailed 3D character animation still in modern Pixar/Disney animation studio style. "
            f"Character: {leo_traits} "
            f"Action/Mood: Happy, curious, and welcoming pose, interacting with {theme}. "
            f"Environment: {environment_desc}. Soft vibrant pastel colors, clean playroom lighting, volumetric sunlight rays, "
            f"subsurface skin scattering, 8k render, Unreal Engine 5 aesthetic, 9:16 vertical portrait composition."
        )
        
        negative_prompt = (
            "photorealistic, real human, distorted anatomy, creepy eyes, 2D anime, flat illustration, "
            "gloomy dark lighting, dull colors, low quality, blurry, text, watermark"
        )

        return {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio": "9:16",
            "resolution": "1080x1920"
        }

    def prepare_scene_image(self, target_scene_name: str, output_path: Path) -> Path:
        """Fetch, format, and ensure 1080x1920 vertical format for the animation pipeline."""
        scene_file = self.scenes_dir / target_scene_name
        if not scene_file.exists():
            # Fallback to existing default scene
            self.log(f"⚠️ Requested scene '{target_scene_name}' not found, falling back to 'manners_classroom.jpg'")
            scene_file = self.scenes_dir / "manners_classroom.jpg"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img = Image.open(scene_file)
        resized_img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
        resized_img.save(output_path, quality=95)
        self.log(f"✅ Scene canvas prepared at 1080x1920: {output_path}")
        return output_path

    def run(self, theme: str, scene_hint: Optional[str] = None, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Execute Art Direction workflow."""
        prompt_data = self.craft_scene_prompt(
            theme=theme,
            environment_desc=scene_hint or "Charming colorful kindergarten classroom with wooden toys and educational alphabet charts"
        )
        
        if output_path:
            # Map theme to best matching existing scene
            scene_map = {
                "teeth": "hygiene_brushing_teeth.jpg",
                "hygiene": "hygiene_brushing_teeth.jpg",
                "clean": "hygiene_brushing_teeth.jpg",
                "alphabet": "alphabet_nursery.jpg",
                "letters": "alphabet_nursery.jpg",
                "numbers": "counting_numbers.jpg",
                "math": "counting_numbers.jpg",
                "tidy": "routine_tidying_toys.jpg",
                "toys": "routine_tidying_toys.jpg",
                "manners": "manners_classroom.jpg",
            }
            matched_scene = "manners_classroom.jpg"
            for k, v in scene_map.items():
                if k in theme.lower():
                    matched_scene = v
                    break

            prepared_canvas = self.prepare_scene_image(matched_scene, output_path)
            prompt_data["canvas_path"] = str(prepared_canvas)

        return prompt_data
