"""Art Director & Visual Designer Agent (قسم الفنون والتصميم البصري).
Maintains 100% consistent Disney/Pixar 3D character identity (Leo) and cinematography:
1. Analyzes Arabic educational scripts with Gemini AI to determine scene themes and cinematography.
2. Selects matching high-definition 3D studio environments from the curated Master Library.
3. Strict zero-repetition Diversity Guard prevents consecutive identical scenes.
4. Produces pixel-perfect 1080x1920 (9:16) canvases for high-retention YouTube Shorts.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image
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
        """Analyze Arabic script with Gemini AI to design tailored visual concept and cinematography."""
        self.log(f"🎨 Analyzing script to design tailored 3D Pixar scene and cinematography: '{title}'...")

        prompt = f"""
You are the Lead 3D Art Director for the award-winning Disney/Pixar animated preschool series starring Leo (a cute 6-year-old cartoon boy with curly brown hair, expressive warm eyes, and a joyful animated face).

Analyze this educational Arabic episode:
Title: {title}
Pillar: {pillar}
Script: "{script_text}"

Available High-Definition Master Studio Scenes:
{ALL_AVAILABLE_SCENES}

Return ONLY a valid JSON object (no markdown, no backticks) with:
1. "scene_description": A vivid 1-2 sentence English summary of Leo's educational activity.
2. "best_matching_scene": The most fitting scene filename from the list above.
3. "theme_palette": One of ["emerald", "sapphire", "amber", "teal", "ruby", "twilight", "coral", "amethyst"].
4. "particle1": Primary emoji directly matching the lesson theme (e.g. 🍎, 🥦, 🔤, 🔢, 🪥, 🌙, 🎨, ⭐, 🚀).
5. "particle2": Secondary complementary emoji symbol (e.g. ✨, 🌟, 💧, 🫧, 🌸, ❤️).
6. "camera_style": Integer 0 to 4 (0=push_in_sway, 1=panoramic_dolly, 2=rhythmic_bounce, 3=reveal_glide, 4=upward_tilt).
"""
        candidate_models = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-flash-latest"]
        for model_name in candidate_models:
            try:
                resp = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if not resp or not resp.text:
                    continue
                raw_text = resp.text.strip()
                if raw_text.startswith("```"):
                    raw_text = re.sub(r"^```(?:json)?", "", raw_text)
                    raw_text = re.sub(r"```$", "", raw_text).strip()

                data = json.loads(raw_text)
                self.log(f"✨ Master Concept Designed: '{data.get('scene_description')}' (Theme: {data.get('theme_palette')}, Scene: {data.get('best_matching_scene')})")
                return data
            except Exception as e:
                self.log(f"Notice with {model_name}: {e}")
                continue

        # Deterministic rich fallback
        self.log("⚠️ Using deterministic tailored visual spec.")
        is_num = "رقم" in script_text or "عد" in script_text or "1" in title
        is_color = "ألوان" in script_text or "لون" in script_text or "أحمر" in script_text or "أزرق" in script_text
        is_art = "رسم" in script_text or "لوحة" in script_text

        best_scene = "counting_numbers.jpg" if is_num else ("scene_art_colors.jpg" if (is_color or is_art) else "scene_peace_garden.jpg")

        return {
            "scene_description": f"Leo engaging in high-retention preschool activity for {title}",
            "best_matching_scene": best_scene,
            "theme_palette": "amber" if (is_color or is_art) else ("sapphire" if is_num else "emerald"),
            "particle1": "🎨" if (is_color or is_art) else ("🔢" if is_num else "🌟"),
            "particle2": "✨",
            "camera_style": 0
        }

    def generate_or_resolve_scene_image(
        self,
        visual_spec: Dict[str, Any],
        output_path: Path,
        last_used_scene: Optional[str] = None
    ) -> Path:
        """Resolve highest-quality 3D Disney/Pixar scene canvas from Master Library with Diversity Guard."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        chosen_scene_name = visual_spec.get("best_matching_scene", "manners_classroom.jpg")
        scene_file = self.scenes_dir / chosen_scene_name
        if not scene_file.exists():
            scene_file = self.scenes_dir / "scene_peace_garden.jpg"
            chosen_scene_name = "scene_peace_garden.jpg"

        # Diversity Guard: ensure zero consecutive repetition of scenes across episodes
        if last_used_scene and chosen_scene_name == last_used_scene:
            cur_idx = ALL_AVAILABLE_SCENES.index(last_used_scene) if last_used_scene in ALL_AVAILABLE_SCENES else 0
            alt_scene = ALL_AVAILABLE_SCENES[(cur_idx + 1) % len(ALL_AVAILABLE_SCENES)]
            scene_file = self.scenes_dir / alt_scene
            self.log(f"🛡️ Diversity Guard: Swapped from '{last_used_scene}' to '{alt_scene}'")

        # Standardize to 1080x1920 (9:16) with high-fidelity LANCZOS resampling
        img = Image.open(scene_file)
        resized_img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
        resized_img.save(output_path, quality=95)
        self.log(f"✅ Studio-grade 3D Pixar canvas ready: {output_path} (Master Asset: {scene_file.name})")
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
