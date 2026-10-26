"""Art Director & Visual Designer Agent (قسم الفنون والتصميم البصري).
Omni-Powered 3D Visual Pipeline:
1. Analyzes Arabic educational scripts with Gemini AI / Gemini Omni.
2. Dynamically customizes Leo's outfit, expression, interactive props, and environment.
3. Generates 100% unique 3D Disney/Pixar 9:16 vertical images via Omni / AI Generation.
4. Intelligent fallback hierarchy with Diversity Guard ensures zero pipeline downtime.
"""

import json
import re
import urllib.request
import urllib.parse
import hashlib
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
You are the Lead 3D Art Director for an award-winning Disney/Pixar animated preschool series starring Leo (a cute 6-year-old cartoon boy with curly brown hair, large expressive warm eyes, and a joyful animated face).

Analyze this educational Arabic episode:
Title: {title}
Pillar: {pillar}
Script: "{script_text}"

Design a 100% UNIQUE 3D scene where every visual asset strictly matches the topic.
Return ONLY a valid JSON object (no markdown, no backticks) with:
1. "leo_outfit": Leo's custom clothing matching this lesson (e.g. astronaut suit, chef apron & mini hat, cozy pajamas, doctor coat, gardener overalls, school uniform).
2. "leo_expression": Detailed facial expression and pose (e.g. beaming with wonder, pointing excitedly at a floating prop, gentle warm smile).
3. "custom_props": Specific 3D pedagogical objects visible in the scene (e.g. glowing number 12, smiling cartoon carrot and apple, magical glowing Arabic letter, toy spaceship).
4. "environment_setting": Detailed 3D background world (e.g. colorful starry galaxy, sunny preschool kitchen, blossom garden with gentle animals, cozy bedroom under moonlight).
5. "scene_description": A vivid 2-sentence English summary of what Leo is doing and the custom setting.
6. "image_prompt": Ultra-detailed 3D Disney/Pixar animation prompt in vertical 9:16 aspect ratio describing Leo with the specific outfit, expression, custom props, and setting. Include: "3D Disney Pixar movie style, 9:16 vertical aspect ratio, cute 6-year-old cartoon boy Leo, soft volumetric daylight, cinematic studio lighting, rich vibrant colors, Octane render 8k".
7. "theme_palette": One of ["emerald", "sapphire", "amber", "teal", "ruby", "twilight", "coral", "amethyst"].
8. "particle1": Primary emoji directly matching the lesson theme (e.g. 🚀, 🥦, 🔤, 🔢, 🪥, 🍎, 🌙, 🦋, 🎨, ⭐).
9. "particle2": Secondary complementary emoji symbol (e.g. ✨, 🌟, 💧, 🫧, 🌸, ❤️, 🪐).
10. "camera_style": Integer 0 to 4 (0=push_in_sway, 1=panoramic_dolly, 2=rhythmic_bounce, 3=reveal_glide, 4=upward_tilt).
11. "best_matching_scene": Best fitting fallback scene from this list: {ALL_AVAILABLE_SCENES}.
"""
        # Try primary Gemini models for visual concept analysis
        candidate_models = ["gemini-omni-1.1-flash", "gemini-3.8-flash", "gemini-2.5-flash"]
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
                self.log(f"✨ Custom Concept Designed: Leo as '{data.get('leo_outfit')}' in '{data.get('environment_setting')}'")
                return data
            except Exception as e:
                self.log(f"Notice with {model_name}: {e}")
                continue

        # Deterministic rich fallback if AI extraction is unavailable
        self.log("⚠️ Using deterministic tailored visual spec.")
        is_num = "رقم" in script_text or "عد" in script_text or "1" in title
        is_hygiene = "أسنان" in script_text or "نظاف" in script_text or "فرشاة" in script_text
        is_food = "خضار" in script_text or "فواكه" in script_text or "طعام" in script_text

        return {
            "leo_outfit": "astronaut suit" if is_num else ("chef apron" if is_food else "colorful preschool overalls"),
            "leo_expression": "excited and pointing enthusiastically",
            "custom_props": "glowing 3D numbers" if is_num else ("friendly 3D fruits" if is_food else "sparkling magical stars"),
            "environment_setting": "a vibrant educational 3D world",
            "scene_description": f"Leo playfully engaging with educational elements for {title}",
            "image_prompt": (
                f"3D Disney Pixar animation style, vertical 9:16 aspect ratio. "
                f"Leo, a cute 6-year-old cartoon boy with curly brown hair and expressive warm eyes, "
                f"interacting with {title}. Soft volumetric studio lighting, rich textures, 8k render."
            ),
            "theme_palette": "sapphire" if is_num else ("amber" if is_food else "emerald"),
            "particle1": "🔢" if is_num else ("🪥" if is_hygiene else ("🍎" if is_food else "🌟")),
            "particle2": "✨",
            "camera_style": 0,
            "best_matching_scene": "counting_numbers.jpg" if is_num else "scene_peace_garden.jpg"
        }

    def _generate_via_gemini_omni(self, prompt: str, output_path: Path) -> bool:
        """Attempt image generation via Gemini Omni / Imagen models."""
        for model_name in ["gemini-omni-1.1-flash", "gemini-3.1-flash-image", "gemini-2.5-flash-image"]:
            try:
                resp = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_modalities=["IMAGE"])
                )
                if hasattr(resp, "parts"):
                    for part in resp.parts:
                        if part.inline_data and part.inline_data.data:
                            with open(output_path, "wb") as f:
                                f.write(part.inline_data.data)
                            self.log(f"🎉 Direct Gemini Omni generation SUCCESS ({model_name})!")
                            return True
            except Exception:
                continue
        return False

    def _generate_via_ai_visual_engine(self, prompt: str, output_path: Path, seed: Optional[int] = None) -> bool:
        """Generate high-fidelity 3D Pixar vertical image via AI visual engine (Flux / SDXL 3D)."""
        try:
            self.log("🚀 Generating tailored 3D Pixar scene via Dedicated AI Visual Engine...")
            clean_prompt = prompt.replace("\n", " ").strip()
            encoded_prompt = urllib.parse.quote(clean_prompt)
            
            # Deterministic or randomized seed
            if seed is None:
                seed_str = hashlib.md5(prompt.encode("utf-8")).hexdigest()
                seed = int(seed_str[:8], 16) % 1000000

            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&model=flux&seed={seed}&nologo=true"
            
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "TalesOfWonder-Studio/2.0 (ArtDirectorEngine)"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                if content and len(content) > 10000:
                    with open(output_path, "wb") as f:
                        f.write(content)
                    
                    # Verify and standardize to exact 1080x1920 dimensions
                    img = Image.open(output_path)
                    if img.size != (1080, 1920):
                        resized = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                        resized.save(output_path, quality=95)
                    self.log(f"🎉 Dedicated AI Visual Engine SUCCESS: {output_path} (1080x1920 3D Pixar)")
                    return True
        except Exception as e:
            self.log(f"⚠️ AI visual engine notice: {e}")
        return False

    def generate_or_resolve_scene_image(
        self,
        visual_spec: Dict[str, Any],
        output_path: Path,
        last_used_scene: Optional[str] = None
    ) -> Path:
        """Complete 3-Tier Multi-Engine Generation:
        Tier 1: Gemini Omni / Imagen multimodal generation.
        Tier 2: High-fidelity AI Visual Engine (Flux 3D Pixar custom render).
        Tier 3: Local Curated 3D Scene Library with strict zero-repetition Diversity Guard.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image_prompt = visual_spec.get("image_prompt", "")

        # Tier 1: Try Gemini Omni directly
        if image_prompt:
            omni_ok = self._generate_via_gemini_omni(image_prompt, output_path)
            if omni_ok:
                return output_path

        # Tier 2: Try High-Fidelity 3D Visual Engine
        if image_prompt:
            ai_ok = self._generate_via_ai_visual_engine(image_prompt, output_path)
            if ai_ok:
                return output_path

        # Tier 3: Resilient Fallback to Curated Library with Diversity Guard
        self.log("🛡️ Engaging Curated 3D Scene Library Fallback with Diversity Guard...")
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

        img = Image.open(scene_file)
        resized_img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
        resized_img.save(output_path, quality=95)
        self.log(f"✅ Scene canvas ready from library: {output_path} (source: {scene_file.name})")
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
