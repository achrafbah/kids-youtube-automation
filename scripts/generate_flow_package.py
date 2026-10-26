"""Google Flow Multi-Scene Storyboard & Prompt Architect.
Generates complete ready-to-paste production packages for Google Flow (labs.google/fx/tools/flow):
- Master Character Anchor (Leo Consistency Prompt)
- High-fidelity 16:9 Video Prompts per Scene (Camera Motion, Character Action, Environment, Lighting)
- Synchronized Arabic Voiceover Scripts with full Tashkeel
- Ready-to-publish YouTube Metadata (Title, Chapters, Tags)
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "flow_storyboards"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Master Character Anchor for Google Flow
LEO_FLOW_CHARACTER_ANCHOR = (
    "Consistent Character: Leo, an adorable 6-year-old cartoon boy, Disney Pixar 3D animated movie style, "
    "messy curly brown hair, large expressive warm brown eyes, friendly cheerful smile, highly animated facial expressions."
)

PILOT_STORY_SPACE_ADVENTURE = {
    "story_title_ar": "مُغَامَرَةُ لِيُو فِي الفَضَاءِ: إِنْقَاذُ الكَوْكَبِ الصَّغِير 🚀🪐",
    "theme": "الفضاء والاستكشاف والتعاون (Space & Teamwork)",
    "target_aspect_ratio": "16:9 Widescreen (1920x1080)",
    "scenes": [
        {
            "scene_number": 1,
            "scene_title_ar": "المشهد 1: نداء الاستكشاف في مرصد ليو",
            "flow_prompt": (
                "Cinematic slow zoom-in shot, 16:9 widescreen, 3D Disney Pixar animation style. "
                "Leo, a 6-year-old boy with curly brown hair wearing a cute futuristic explorer jacket, "
                "looks excitedly through a brass telescope on his cozy bedroom terrace under a breathtaking starry night sky. "
                "His eyes sparkle with curiosity as a glowing golden star shoots across the cosmos. "
                "Soft magical moonlight, warm volumetric lighting, rich textures, 4k cinematic render."
            ),
            "camera_motion": "Slow Zoom-In (توجيه الكاميرا ببطء نحو ليو وهو ينظر في التلسكوب)",
            "voiceover_ar": "فِي لَيْلَةٍ صَافِيَةٍ مَلِيئَةٍ بِالنُّجُوم، كَانَ صَدِيقُنَا لِيُو يَتَأَمَّلُ السَّمَاءَ بِمِرْصَدِهِ الصَّغِير. فَجْأَةً.. لَمَعَ نَجْمٌ ذَهَبِيٌّ وَأَرْسَلَ إِشَارَةً غَامِضَة! يَا تُرَى، مَا هُوَ السِّرُّ الَّذِي يَنْتَظِرُنَا فِي الفَضَاء؟",
            "sfx_cue": "Sparkling chime sound ✨ + gentle cosmic wind",
            "duration_sec": 7
        },
        {
            "scene_number": 2,
            "scene_title_ar": "المشهد 2: الانطلاق بالسفينة الفضائية الكرتونية",
            "flow_prompt": (
                "Dynamic tracking follow shot, 16:9 widescreen, 3D Disney Pixar animation style. "
                "Leo wearing a pearl-white and sapphire-blue astronaut suit with cute mission patches, "
                "sitting happily in the cockpit of a colorful retro-futuristic spaceship. "
                "He cheerfully pulls the launch lever as colorful buttons blink playfully on the dashboard. "
                "Outside the curved cockpit glass, stars and miniature cartoon planets streak by in vibrant pastel streaks. "
                "Energetic joyful cinematic lighting, Octane 3D render."
            ),
            "camera_motion": "Dynamic Tracking / Orbit (الكاميرا تتحرك بجانب مقصورة القيادة وسرعة النجوم)",
            "voiceover_ar": "ارْتَدَى لِيُو بَدْلَتَهُ الفَضَائِيَّةَ اللَّامِعَة، وَانْطَلَقَ بِسَفِينَتِهِ الشُّجَاعَة نَحْوَ المَجَرَّات! رَبَطَ حِزَامَ الأَمَان، وَضَغَطَ الزِّرَّ الأَخْضَر: ثَلَاثَة.. اِثْنَان.. وَاحِد.. اِنْطِلَاق!",
            "sfx_cue": "Rocket launch whoosh 🚀 + bubbly spaceship beeps",
            "duration_sec": 6
        },
        {
            "scene_number": 3,
            "scene_title_ar": "المشهد 3: اكتشاف الكوكب الكريستالي اللطيف",
            "flow_prompt": (
                "Wide panoramic establishing shot, 16:9 widescreen, 3D Disney Pixar animation style. "
                "Leo in his astronaut suit gently steps out onto the soft floating surface of a magical miniature candy-crystal planet. "
                "Surrounding him are adorable miniature alien creatures with glowing gentle eyes welcoming him cheerfully. "
                "Gentle floating crystal rocks and glowing pink and turquoise nebula clouds in the sky. "
                "Dreamy atmospheric studio lighting, whimsical colorful palette, 8k render."
            ),
            "camera_motion": "Panoramic Dolly Glide (مسح بانورامي واسع لسطح الكوكب العجيب)",
            "voiceover_ar": "وَصَلَ لِيُو إِلَى كَوْكَبِ البِلَّوْرِ السِّحْرِيّ! كَانَ المَكَانُ يَتَلَأْلَأُ بِأَلْوَانٍ بَدِيعَة، وَاسْتَقْبَلَتْهُ كَائِنَاتٌ فَضَائِيَّةٌ لَطِيفَةٌ تَبْتَسِمُ وَتُرَحِّبُ بِصَدِيقِهَا الجَدِيد!",
            "sfx_cue": "Magical crystal resonance 💎 + cute alien squeaks",
            "duration_sec": 7
        },
        {
            "scene_number": 4,
            "scene_title_ar": "المشهد 4: التعاون وإعادة تشغيل النجمة الذهبية",
            "flow_prompt": (
                "Medium close-up shot, 16:9 widescreen, 3D Disney Pixar animation style. "
                "Leo smiles warmly, kneeling alongside two cute furry alien friends as they gently lift and place a glowing golden star together onto a crystalline pedestal. "
                "As the star touches the pedestal, a brilliant wave of warm golden light blooms across the screen, illuminating their joyful faces. "
                "Emotional warm cinematic lighting, soft lens flare, Pixar feature film aesthetic."
            ),
            "camera_motion": "Slow Push-In on Action (تقريب بطيء نحو ليو وأصدقائه وهم يضعون النجمة)",
            "voiceover_ar": "كَانَتْ شَمْسُ الكَوْكَبِ الصَّغِيرِ تَحْتَاجُ إِلَى مُسَاعَدَة! بِيَدٍ وَاحِدَةٍ وَتَعَاوُنٍ كَبِير، اجْتَمَعَ لِيُو مَعَ أَصْدِقَائِهِ لِيُعِيدُوا النَّجْمَةَ المُنِيرَةَ إِلَى مَكَانِهَا، فَعَادَ النُّورُ يَمْلأُ المَكَانَ بِالدِّفْءِ وَالفَرَح!",
            "sfx_cue": "Power surge resonance 🌟 + joyful chime crescendo",
            "duration_sec": 8
        },
        {
            "scene_number": 5,
            "scene_title_ar": "المشهد 5: العودة إلى البيت والرسالة التربوية",
            "flow_prompt": (
                "Cozy warm wide shot, 16:9 widescreen, 3D Disney Pixar animation style. "
                "Leo back in his warm cozy pajamas, tucked into his soft bed at home, looking out his bedroom window with a serene happy smile. "
                "Outside the window, the golden star winks playfully in the night sky. "
                "Cozy bedroom with soft amber lamp lighting, star-patterned blanket, bedtime tranquility, 4k render."
            ),
            "camera_motion": "Slow Reveal Pull-Back (تراجع بطيء للكاميرا داخل الغرفة لوداع ليو)",
            "voiceover_ar": "عَادَ لِيُو إِلَى سَرِيرِهِ الدَّافِئ، وَقَلْبُهُ يَمْلَؤُهُ الأَمَل. تَعَلَّمَ أَنَّ الصَّدَاقَةَ وَالتَّعَاوُنَ يَصْنَعَانِ المُعْجِزَات! نَامُوا أَنْتُمْ أَيْضًا يَا أَبْطَال، فَغَدًا مَوْعِدُنَا مَعَ مُغَامَرَةٍ جَدِيدَة. تَصْبَحُونَ عَلَى خَيْر!",
            "sfx_cue": "Gentle music box lullaby 🎵 + soft bedtime hush",
            "duration_sec": 7
        }
    ],
    "youtube_metadata": {
        "title": "مغامرة ليو في الفضاء: إنقاذ الكوكب الصغير 🚀🪐 | قصة كرتونية هادفة للأطفال بدقة 4K",
        "chapters": [
            "00:00 - نداء الاستكشاف في مرصد ليو",
            "00:45 - الانطلاق بالسفينة الفضائية",
            "01:30 - اكتشاف الكوكب الكريستالي اللطيف",
            "02:15 - سر التعاون وإعادة النور للكوكب",
            "03:00 - العودة إلى البيت وحكاية النوم"
        ],
        "tags": [
            "قصص اطفال", "كرتون اطفال", "افلام كرتون اطفال", "قصص الفضاء للاطفال",
            "حكايات قبل النوم", "قصة ليو", "حكايات العجائب", "كرتون 3D", "تعليم اطفال"
        ]
    }
}

def export_storyboard_to_markdown(data: Dict[str, Any], filepath: Path):
    """Export formatted, copy-paste ready package to Markdown."""
    lines = []
    lines.append(f"# 🎬 Google Flow Production Package: {data['story_title_ar']}")
    lines.append(f"**المحور والهدف:** {data['theme']} | **صيغة العرض:** `{data['target_aspect_ratio']}`\n")
    lines.append("---")
    lines.append("## 🧑‍🎨 1. Character Anchor Prompt (خاصية تثبيت الشخصية فـ Flow)")
    lines.append("> هاد الـ Prompt كيتكتب فـ خانة الـ Agent أو الشخصية الأساسية باش يعقل على ملامح Leo فكاع المشاهد:\n")
    lines.append("```text")
    lines.append(LEO_FLOW_CHARACTER_ANCHOR)
    lines.append("```\n")
    lines.append("---")
    lines.append("## 🎞️ 2. المشاهد بالتفصيل (Scene-by-Scene Copy-Paste Prompts)\n")

    for sc in data["scenes"]:
        lines.append(f"### {sc['scene_title_ar']} (⏱️ ~{sc['duration_sec']} ثواني)")
        lines.append(f"* **حركة الكاميرا الموصى بها:** `{sc['camera_motion']}`")
        lines.append(f"* **المؤثر الصوتي:** `{sc['sfx_cue']}`\n")
        lines.append("#### 📋 البرومبت المباشر لـ Google Flow (كوبيه كما هو):")
        lines.append("```text")
        lines.append(sc["flow_prompt"])
        lines.append("```\n")
        lines.append("#### 🎙️ النص الصوتي بالتشكيل (Voiceover Script):")
        lines.append(f"> \"{sc['voiceover_ar']}\"\n")
        lines.append("-" * 50 + "\n")

    lines.append("## 🏷️ 3. بيانات النشر لـ YouTube (SEO & Chapters)")
    lines.append(f"**العنوان:** `{data['youtube_metadata']['title']}`\n")
    lines.append("**الفصول في الوصف (Chapters):**")
    lines.append("```text")
    for ch in data["youtube_metadata"]["chapters"]:
        lines.append(ch)
    lines.append("```\n")
    lines.append(f"**الوسوم (Tags):** `{' , '.join(data['youtube_metadata']['tags'])}`")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ Storyboard exported: {filepath}")

def main():
    out_file = OUTPUT_DIR / "pilot_space_adventure_flow_package.md"
    export_storyboard_to_markdown(PILOT_STORY_SPACE_ADVENTURE, out_file)

if __name__ == "__main__":
    main()
