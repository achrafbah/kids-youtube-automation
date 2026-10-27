"""Art Director & Visual Designer Agent (قسم الفنون والتصميم البصري).
Maintains 100% consistent Disney/Pixar 3D character identity (Leo) and cinematography:
1. Dynamically constructs tailored 3D Pixar scene prompts for every episode based on its specific script and theme.
2. Character Consistency: Strictly locks Leo's visual identity (6yo boy, messy curly brown hair, warm brown eyes, joyful smile).
3. Zero-Reuse History Guard: NEVER reuses an image that was used in any prior episode.
4. Native AI Image Generation: Supports Gemini / Imagen API generation with automatic fallback to unique unused scenes.
5. Produces pixel-perfect 1080x1920 (9:16) canvases for high-retention YouTube Shorts.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from PIL import Image
from .base import BaseAgent

ALL_AVAILABLE_SCENES = [
    "leo_brushing_teeth_custom.jpg",
    "leo_washing_hands_custom.jpg",
    "leo_tidying_toys_custom.jpg",
    "leo_healthy_food_custom.jpg",
    "leo_drinking_water_custom.jpg",
    "leo_morning_exercise_custom.jpg",
    "leo_bedtime_story_custom.jpg",
    "leo_helping_family_custom.jpg",
    "leo_arabic_alphabet_custom.jpg",
    "leo_counting_numbers_custom.jpg",
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

    def get_all_used_scenes_from_history(self) -> Set[str]:
        """Collect all scene names and image files previously used across all published episodes."""
        history_file = self.data_dir / "topics_history.json"
        used = set()
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for entry in data.get("topics", []):
                    scene = entry.get("scene_name")
                    if scene:
                        used.add(Path(scene).name.lower())
            except Exception as e:
                self.log(f"Notice reading history: {e}")
        return used

    def build_dynamic_leo_scene_prompt(self, script_text: str, title: str = "", pillar: str = "") -> str:
        """Constructs a custom 3D Disney/Pixar scene prompt tailored to the episode's topic and Leo's consistent appearance."""
        clean_title = re.sub(r"[#🌟✨🪥🧸📦🧼💦🥦🥕🏃‍♂️💧]", "", title).strip()
        clean_script = script_text[:160].replace("\n", " ").strip()
        
        prompt = (
            f"3D Disney Pixar animated film style, ultra-detailed CGI render of Leo: "
            f"a cute 6-year-old cartoon boy with messy curly brown hair, big warm expressive brown eyes, and a joyful energetic smile. "
            f"Vertical 9:16 portrait composition. "
            f"Episode Theme: '{clean_title}'. Activity: {clean_script}. "
            f"Leo is happily engaged in the action with colorful props matching the theme. "
            f"Cinematic soft volumetric studio lighting, rich Pixar color palette, highly detailed textures, masterpiece 3D render, no text, no watermark, vertical framing."
        )
        return prompt

    def analyze_script_and_design_visuals(self, script_text: str, title: str = "", pillar: str = "") -> Dict[str, Any]:
        """Analyze Arabic script with Gemini AI to design tailored visual concept, image generation prompt, and cinematography."""
        self.log(f"🎨 Analyzing script to design tailored 3D Pixar scene and cinematography: '{title}'...")

        # Build dynamic 3D prompt ensuring Leo's consistent character
        image_prompt = self.build_dynamic_leo_scene_prompt(script_text, title, pillar)

        prompt = f"""
You are the Lead 3D Art Director for the award-winning Disney/Pixar animated preschool series starring Leo (a cute 6-year-old cartoon boy with curly brown hair, expressive warm eyes, and a joyful animated face).

Analyze this educational Arabic episode:
Title: {title}
Pillar: {pillar}
Script: "{script_text}"

Return ONLY a valid JSON object (no markdown, no backticks) with:
1. "scene_description": A vivid 1-2 sentence English summary of Leo's educational activity.
2. "image_prompt": Detailed 3D Pixar animation prompt describing Leo's pose, clothes, props, and environment for 9:16 vertical render.
3. "theme_palette": One of ["emerald", "sapphire", "amber", "teal", "ruby", "twilight", "coral", "amethyst"].
4. "particle1": Primary emoji directly matching the lesson theme (e.g. 🍎, 🥦, 🔤, 🔢, 🪥, 🌙, 🎨, ⭐, 🚀).
5. "particle2": Secondary complementary emoji symbol (e.g. ✨, 🌟, 💧, 🫧, 🌸, ❤️).
6. "camera_style": Integer 0 to 4 (0=push_in_sway, 1=panoramic_dolly, 2=rhythmic_bounce, 3=reveal_glide, 4=upward_tilt).
"""
        candidate_models = ["gemini-3.8-flash", "gemini-flash-latest"]
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
                if not data.get("image_prompt"):
                    data["image_prompt"] = image_prompt
                self.log(f"✨ Master Concept Designed: '{data.get('scene_description')}' (Theme: {data.get('theme_palette')})")
                return data
            except Exception as e:
                self.log(f"Notice with {model_name}: {e}")
                continue

        # Deterministic rich fallback
        self.log("⚠️ Using deterministic tailored visual spec.")
        is_num = "رقم" in script_text or "عد" in script_text or "1" in title
        is_color = "ألوان" in script_text or "لون" in script_text or "أحمر" in script_text or "أزرق" in script_text
        is_art = "رسم" in script_text or "لوحة" in script_text

        return {
            "scene_description": f"Leo engaging in high-retention preschool activity for {title}",
            "image_prompt": image_prompt,
            "theme_palette": "amber" if (is_color or is_art) else ("sapphire" if is_num else "emerald"),
            "particle1": "🎨" if (is_color or is_art) else ("🔢" if is_num else "🌟"),
            "particle2": "✨",
            "camera_style": 0
        }

    def generate_image_via_gemini_api(self, prompt: str, output_path: Path) -> bool:
        """Attempt to generate new image via Gemini / Imagen API with GEMINI_API_KEY."""
        try:
            from google.genai import types
            candidate_models = ["gemini-2.5-flash-image", "gemini-3.1-flash-image", "imagen-3.0-generate-002"]
            for model_name in candidate_models:
                try:
                    self.log(f"🎨 Generating dynamic scene via {model_name}...")
                    resp = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_modalities=["IMAGE"]
                        )
                    )
                    if resp and resp.parts:
                        for p in resp.parts:
                            if p.inline_data:
                                img = p.as_image()
                                resized = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                                resized.save(output_path, "JPEG", quality=95)
                                self.log(f"🎉 Successfully generated new AI scene: {output_path} ({model_name})")
                                return True
                except Exception as model_err:
                    self.log(f"Notice with {model_name}: {model_err}")
                    continue
        except Exception as e:
            self.log(f"Notice: Gemini image generation not available: {e}")
        return False

    def generate_or_resolve_scene_image(
        self,
        visual_spec: Dict[str, Any],
        output_path: Path,
        last_used_scene: Optional[str] = None,
        topic: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Generate a brand-new, topic-specific 3D scene canvas for Leo, with strict ZERO-REUSE of old photos.
        Guarantee: Never reuse an image that was used in ANY previous episode.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        title = (topic.get("title_ar") or topic.get("title", "")) if topic else (visual_spec.get("title_ar") or visual_spec.get("title", ""))
        script = topic.get("script", "") if topic else visual_spec.get("script", "")
        pillar = topic.get("pillar", "") if topic else visual_spec.get("pillar", "")

        # 1. Build prompt for Leo's 3D Pixar character specific to this episode
        dynamic_prompt = visual_spec.get("image_prompt") or self.build_dynamic_leo_scene_prompt(script, title, pillar)
        visual_spec["image_prompt"] = dynamic_prompt

        # 2. Try generating a brand-new image via Gemini / Imagen AI API
        if self.generate_image_via_gemini_api(dynamic_prompt, output_path):
            visual_spec["generated_dynamically"] = True
            visual_spec["best_matching_scene"] = output_path.name
            return output_path

        # 3. STRICT ZERO-REUSE GUARD:
        # Check all scenes ever used in history. Never reuse an old photo!
        used_scenes = self.get_all_used_scenes_from_history()
        self.log(f"🛡️ Zero-Reuse Guard: Checking against {len(used_scenes)} previously used scenes in channel history.")

        # Check for any unused images in scenes_dir
        available_scenes = []
        if self.scenes_dir.exists():
            for f in self.scenes_dir.glob("*.jpg"):
                if f.name.lower() not in used_scenes:
                    available_scenes.append(f)

        if available_scenes:
            # Topic-aware matching among strictly UNUSED scenes
            text_context = (title + " " + script + " " + pillar).lower()
            selected_scene = None
            keyword_mappings = [
                (["أسنان", "اسنان", "فرشاة", "معجون", "teeth", "brush"], "leo_brushing_teeth_custom.jpg"),
                (["يدين", "صابون", "نظافة اليدين", "جراثيم", "wash", "soap"], "leo_washing_hands_custom.jpg"),
                (["ترتيب", "ألعاب", "العاب", "صندوق", "غرفة", "tidy", "toys"], "leo_tidying_toys_custom.jpg"),
                (["طعام", "غذاء", "خضار", "فواكه", "تفاح", "صحة", "food", "fruit"], "leo_healthy_food_custom.jpg"),
                (["ماء", "شرب", "انتعاش", "عطش", "water", "drink"], "leo_drinking_water_custom.jpg"),
                (["رياضة", "صباح", "نشاط", "قفز", "طاقة", "sport", "exercise"], "leo_morning_exercise_custom.jpg"),
                (["نوم", "سرير", "أحلام", "ليل", "نجوم", "sleep", "bedtime"], "leo_bedtime_story_custom.jpg"),
                (["مساعدة", "والدين", "أخلاق", "تعاون", "شكر", "help", "family"], "leo_helping_family_custom.jpg"),
                (["حروف", "هجاء", "لغة", "عربية", "قراءة", "alphabet", "letters"], "leo_arabic_alphabet_custom.jpg"),
                (["أرقام", "ارقام", "حساب", "عد", "رياضيات", "numbers", "counting"], "leo_counting_numbers_custom.jpg"),
            ]
            for keywords, target_filename in keyword_mappings:
                if any(kw in text_context for kw in keywords):
                    for cand in available_scenes:
                        if cand.name.lower() == target_filename.lower():
                            selected_scene = cand
                            self.log(f"🎯 Perfectly matched topic '{target_filename}' to episode theme!")
                            break
                    if selected_scene:
                        break

            if not selected_scene:
                selected_scene = available_scenes[0]

            self.log(f"✨ Selected unique never-before-used scene: {selected_scene.name}")
            img = Image.open(selected_scene)
            resized = img.resize((1080, 1920), Image.Resampling.LANCZOS)
            resized.save(output_path, quality=95)
            visual_spec["best_matching_scene"] = selected_scene.name
            return output_path

        # 4. If all images have been used and AI generation is unavailable:
        error_msg = (
            "🛑 [ZERO-REUSE GUARD] All existing scene images have already been used in previous episodes! "
            "To guarantee channel quality and avoid reusing old photos, a new image must be generated via AI. "
            "Please ensure Pay-as-you-go billing is active for GEMINI_API_KEY on Google AI Studio."
        )
        self.log(error_msg)
        raise RuntimeError(error_msg)

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
