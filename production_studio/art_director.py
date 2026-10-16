"""Art Director & Visual Designer Agent (قسم الفنون والتصميم البصري).
Maintains Pixar 3D character consistency (Leo) and dynamically crafts 
scene art prompts, generates images, and determines animation choreography directly from the script.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image
from google.genai import types
from .base import BaseAgent

ALL_AVAILABLE_SCENES = [
    "scene_animal_kindness.jpg",
    "scene_letters_dal_dhal.jpg",
    "scene_art_colors.jpg",
    "scene_fruits_kitchen.jpg",
    "scene_morning_exercise.jpg",
    "scene_bedtime_stars.jpg",
    "scene_sharing_playground.jpg",
    "scene_dining_bismillah.jpg",
    "scene_peace_garden.jpg",
    "counting_numbers.jpg",
    "hygiene_brushing_teeth.jpg",
    "routine_tidying_toys.jpg",
    "nature_rain_forest.jpg",
    "alphabet_nursery.jpg",
    "manners_classroom.jpg"
]

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

    def analyze_script_and_design_visuals(self, script_text: str, title: str = "", pillar: str = "") -> Dict[str, Any]:
        """Analyze Arabic script with Gemini AI to generate custom 3D image prompt and animation styling."""
        self.log(f"🎨 Analyzing script to design tailored 3D Pixar scene and cinematography: '{title}'...")

        prompt = f"""
You are the Lead 3D Art Director for a Disney/Pixar animated preschool series starring 6-year-old cartoon boy Leo (curly brown hair, expressive warm eyes, charming child outfit).
Analyze this Arabic educational script:
Title: {title}
Pillar: {pillar}
Script: "{script_text}"

Return ONLY a valid JSON object (no markdown, no backticks) with:
1. "scene_description": A vivid 1-2 sentence English summary of what Leo is doing and the environment.
2. "image_prompt": Ultra-detailed 3D Disney/Pixar animation prompt in vertical 9:16 aspect ratio (character pose, clothes, facial expression, background props, soft lighting, 8k render).
3. "theme_palette": One of ["emerald", "sapphire", "amber", "teal", "ruby", "twilight"].
4. "particle1": Primary emoji symbol matching the theme (e.g. 🫧, 🔤, 🔢, 🌙, ⚡, 🦋, 🍎, ⭐, 🕊️, 🎨).
5. "particle2": Secondary complementary emoji symbol (e.g. 💧, ✨, ⭐, 🌸, 🌟, ❤️, 🌈).
6. "camera_style": Integer 0 to 4 (0=push_in_sway, 1=panoramic_dolly, 2=rhythmic_bounce, 3=reveal_glide, 4=upward_tilt).
7. "best_matching_scene": Best fitting scene file from this list: {ALL_AVAILABLE_SCENES}.
"""
        try:
            resp = self.client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )
            raw_text = resp.text.strip()
            # Clean markdown code block if model wrapped it
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?", "", raw_text)
                raw_text = re.sub(r"```$", "", raw_text).strip()

            data = json.loads(raw_text)
            self.log(f"✨ Visual Concept: {data.get('scene_description')}")
            return data
        except Exception as e:
            self.log(f"⚠️ Visual prompt extraction notice: {e}. Using deterministic fallback.")
            return {
                "scene_description": f"Leo engaging in educational preschool activity for {title}",
                "image_prompt": (
                    f"Ultra-detailed 3D Disney Pixar animation style, vertical 9:16 aspect ratio. "
                    f"Leo, a 6-year-old cartoon boy with curly brown hair and warm brown eyes, smiling cheerfully in a colorful preschool setting interacting with {title}. "
                    f"Soft volumetric daylight, 8k render."
                ),
                "theme_palette": "sapphire" if "حرف" in script_text else "emerald",
                "particle1": "🔤" if "حرف" in script_text else "🌟",
                "particle2": "✨",
                "camera_style": 0,
                "best_matching_scene": "alphabet_nursery.jpg" if "حرف" in script_text else "scene_peace_garden.jpg"
            }

    def generate_or_resolve_scene_image(
        self,
        visual_spec: Dict[str, Any],
        output_path: Path,
        last_used_scene: Optional[str] = None
    ) -> Path:
        """Attempt AI image generation, with seamless intelligent fallback to matching scene library."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image_prompt = visual_spec.get("image_prompt", "")
        
        # Step 1: Probe direct AI image generation if quota is active
        self.log("🎨 Probing AI image generator for custom scene rendering...")
        try:
            for model_name in ["gemini-3.1-flash-image", "gemini-2.5-flash-image", "nano-banana-pro-preview"]:
                try:
                    resp = self.client.models.generate_content(
                        model=model_name,
                        contents=image_prompt,
                        config=types.GenerateContentConfig(response_modalities=["IMAGE"])
                    )
                    if hasattr(resp, "parts"):
                        for part in resp.parts:
                            if part.inline_data and part.inline_data.data:
                                with open(output_path, "wb") as f:
                                    f.write(part.inline_data.data)
                                self.log(f"🎉 Direct AI image generation SUCCESS with {model_name}: {output_path}")
                                return output_path
                except Exception:
                    continue
        except Exception as e:
            self.log(f"ℹ️ AI image generation note: {e}")

        # Step 2: Fallback to best matching scene with Strict Diversity Guard
        chosen_scene_name = visual_spec.get("best_matching_scene", "manners_classroom.jpg")
        scene_file = self.scenes_dir / chosen_scene_name
        if not scene_file.exists():
            scene_file = self.scenes_dir / "scene_peace_garden.jpg"
            chosen_scene_name = "scene_peace_garden.jpg"

        # Diversity Guard: ensure zero consecutive repetition
        if last_used_scene and chosen_scene_name == last_used_scene:
            cur_idx = ALL_AVAILABLE_SCENES.index(last_used_scene) if last_used_scene in ALL_AVAILABLE_SCENES else 0
            alt_scene = ALL_AVAILABLE_SCENES[(cur_idx + 1) % len(ALL_AVAILABLE_SCENES)]
            scene_file = self.scenes_dir / alt_scene
            self.log(f"🛡️ Diversity Guard: Swapped from '{last_used_scene}' to '{alt_scene}'")

        # Format and save to 1080x1920
        img = Image.open(scene_file)
        resized_img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
        resized_img.save(output_path, quality=95)
        self.log(f"✅ Scene canvas ready at: {output_path} (source: {scene_file.name})")
        return output_path

    def run(
        self,
        script_text: str,
        title: str = "",
        pillar: str = "",
        output_path: Optional[Path] = None,
        last_used_scene: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute complete script-to-visual art workflow."""
        visual_spec = self.analyze_script_and_design_visuals(script_text, title, pillar)
        if output_path:
            canvas = self.generate_or_resolve_scene_image(visual_spec, output_path, last_used_scene)
            visual_spec["canvas_path"] = str(canvas)
        return visual_spec
