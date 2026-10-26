"""Google Flow Multi-Scene Storyboard & High-Motion Prompt Architect.
Generates complete ready-to-paste production packages for Google Flow (labs.google/fx/tools/flow):
- Master Character Anchor (Leo Consistency Prompt)
- High-Motion 16:9 Video Prompts per Scene (Active Character Physical Actions, Walking, Gestures, Facial Expressions)
- Flow UI Settings: Motion Intensity, Camera Movement, Aspect Ratio
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
    "messy curly brown hair, large expressive warm brown eyes, friendly cheerful smile, highly animated facial expressions, "
    "smooth 24fps fluid character physics."
)

PILOT_STORY_SPACE_ADVENTURE = {
    "story_title_ar": "مُغَامَرَةُ لِيُو فِي الفَضَاءِ: إِنْقَاذُ الكَوْكَبِ الصَّغِير 🚀🪐",
    "theme": "الفضاء والاستكشاف والتعاون (Space & Teamwork)",
    "target_aspect_ratio": "16:9 Widescreen (1920x1080)",
    "scenes": [
        {
            "scene_number": 1,
            "scene_title_ar": "المشهد 1: نداء الاستكشاف في مرصد ليو",
            "motion_type": "حركة شخصية نشطة (Physical Character Motion) + دوران كاميرا خفيف",
            "flow_settings": {
                "aspect_ratio": "16:9 Landscape",
                "camera_motion": "Slow Orbit / Push In",
                "motion_slider": "Level 6 (Dynamic)"
            },
            "flow_prompt": (
                "Dynamic character animation, 16:9 widescreen, Disney Pixar 3D movie style. "
                "Leo, a cute 6-year-old cartoon boy with curly brown hair wearing an explorer jacket, "
                "actively walks across his wooden balcony, excitedly grabs the brass telescope with both hands, "
                "peers through the eyepiece, then joyfully spins around to face the camera with wide sparkling eyes and a huge gasp of wonder. "
                "Fluid animated body movement, expressive facial expressions, blinking eyes, hair blowing softly, starry night sky background, 4k cinematic render."
            ),
            "voiceover_ar": "فِي لَيْلَةٍ صَافِيَةٍ مَلِيئَةٍ بِالنُّجُوم، كَانَ صَدِيقُنَا لِيُو يَتَأَمَّلُ السَّمَاءَ بِمِرْصَدِهِ الصَّغِير. فَجْأَةً.. لَمَعَ نَجْمٌ ذَهَبِيٌّ وَأَرْسَلَ إِشَارَةً غَامِضَة! يَا تُرَى، مَا هُوَ السِّرُّ الَّذِي يَنْتَظِرُنَا فِي الفَضَاء؟",
            "sfx_cue": "Sparkling chime sound ✨ + gentle cosmic wind",
            "duration_sec": 7
        },
        {
            "scene_number": 2,
            "scene_title_ar": "المشهد 2: الانطلاق بالسفينة الفضائية الكرتونية",
            "motion_type": "حركة سريعة واهتزاز سفينة (Cockpit Action & Speed)",
            "flow_settings": {
                "aspect_ratio": "16:9 Landscape",
                "camera_motion": "Dynamic Tracking / Cockpit Follow",
                "motion_slider": "Level 7 (High Motion)"
            },
            "flow_prompt": (
                "High dynamic animation, 16:9 widescreen, Disney Pixar 3D cartoon style. "
                "Leo wearing a pearl-white astronaut helmet and space suit, energetically steers the retro-futuristic steering wheel inside a glowing cockpit. "
                "He cheerfully pulls down a large glowing red launch lever with his right hand, cheering and laughing with lively mouth movements. "
                "Outside the curved cockpit window, colorful cosmic nebulae and bright stars streak by in rapid motion blur. "
                "Lively character physics, glowing button lights reflecting on his helmet visor, Octane 3D render."
            ),
            "voiceover_ar": "ارْتَدَى لِيُو بَدْلَتَهُ الفَضَائِيَّةَ اللَّامِعَة، وَانْطَلَقَ بِسَفِينَتِهِ الشُّجَاعَة نَحْوَ المَجَرَّات! رَبَطَ حِزَامَ الأَمَان، وَضَغَطَ الزِّرَّ الأَخْضَر: ثَلَاثَة.. اِثْنَان.. وَاحِد.. اِنْطِلَاق!",
            "sfx_cue": "Rocket launch whoosh 🚀 + bubbly spaceship beeps",
            "duration_sec": 6
        },
        {
            "scene_number": 3,
            "scene_title_ar": "المشهد 3: المشي والتفاعل في كوكب الكريستال اللطيف",
            "motion_type": "مشي كامل للشخصية في انعدام الجاذبية (Low-Gravity Bouncy Walk & Hand Waving)",
            "flow_settings": {
                "aspect_ratio": "16:9 Landscape",
                "camera_motion": "Smooth Dolly Tracking",
                "motion_slider": "Level 6 (Dynamic)"
            },
            "flow_prompt": (
                "Full-body character walking animation, 16:9 widescreen, 3D Disney Pixar aesthetic. "
                "Leo in his cute astronaut suit gently bounces and walks forward across the pastel candy-crystal ground in low gravity. "
                "He smiles warmly and waves enthusiastically with both hands at two fluffy, adorable glowing baby alien creatures that hop joyfully around his feet. "
                "Floating floating crystal rocks, gentle floating glowing dust particles, rich 3D cartoon lighting, fluid character locomotion."
            ),
            "voiceover_ar": "وَصَلَ لِيُو إِلَى كَوْكَبِ البِلَّوْرِ السِّحْرِيّ! كَانَ المَكَانُ يَتَلَأْلَأُ بِأَلْوَانٍ بَدِيعَة، وَاسْتَقْبَلَتْهُ كَائِنَاتٌ فَضَائِيَّةٌ لَطِيفَةٌ تَبْتَسِمُ وَتُرَحِّبُ بِصَدِيقِهَا الجَدِيد!",
            "sfx_cue": "Magical crystal resonance 💎 + cute alien squeaks",
            "duration_sec": 7
        },
        {
            "scene_number": 4,
            "scene_title_ar": "المشهد 4: التعاون والاحتفال بالقفز والفرح",
            "motion_type": "حركة جماعية واحتفال بالقفز (Interactive Teamwork & Jumping Celebration)",
            "flow_settings": {
                "aspect_ratio": "16:9 Landscape",
                "camera_motion": "Dynamic Push-In to Celebration",
                "motion_slider": "Level 7 (High Motion)"
            },
            "flow_prompt": (
                "Lively interactive character animation, 16:9 widescreen, Disney Pixar feature film style. "
                "Leo and two cute fluffy alien friends together lift a glowing pulsing golden star with both hands, placing it on top of a crystal pedestal. "
                "Instantly, a warm golden blast of light bursts outwards illuminating their happy faces. "
                "Leo jumps up excitedly into the air, pumping his fists in triumph with a huge joyful cheer, smiling at his alien buddies. "
                "Dynamic fluid character physics, volumetric golden sparkles, Pixar lighting."
            ),
            "voiceover_ar": "كَانَتْ شَمْسُ الكَوْكَبِ الصَّغِيرِ تَحْتَاجُ إِلَى مُسَاعَدَة! بِيَدٍ وَاحِدَةٍ وَتَعَاوُنٍ كَبِير، اجْتَمَعَ لِيُو مَعَ أَصْدِقَائِهِ لِيُعِيدُوا النَّجْمَةَ المُنِيرَةَ إِلَى مَكَانِهَا، فَعَادَ النُّورُ يَمْلأُ المَكَانَ بِالدِّفْءِ وَالفَرَح!",
            "sfx_cue": "Power surge resonance 🌟 + joyful chime crescendo",
            "duration_sec": 8
        },
        {
            "scene_number": 5,
            "scene_title_ar": "المشهد 5: العودة إلى البيت والوداع الهادئ",
            "motion_type": "حركات تمطط وتثاؤب ثم التلويح باليد (Stretching, Yawning, Waving Goodbye)",
            "flow_settings": {
                "aspect_ratio": "16:9 Landscape",
                "camera_motion": "Gentle Pull Back",
                "motion_slider": "Level 4 (Gentle Motion)"
            },
            "flow_prompt": (
                "Gentle character bedtime animation, 16:9 widescreen, Disney Pixar 3D animated style. "
                "Leo, back in his cozy star-patterned pajamas, sits up on his soft bed, stretches his arms while yawning cutely, "
                "then pulls a warm blanket over his chest. He turns his head toward the camera, waves goodbye with a sweet gentle hand motion, "
                "smiles softly, and closes his eyes peacefully to sleep. Outside the window, a golden star twinkles softly. "
                "Warm soothing amber lamp lighting, cozy bedroom, cinematic 4k render."
            ),
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
    lines.append("> هاد الـ Prompt كيتكتب فـ خانة الـ Agent أو الـ Character Anchor باش تضمن باللي Leo كيبقا نفس الوجه 3D Pixar فكاع المشاهد:\n")
    lines.append("```text")
    lines.append(LEO_FLOW_CHARACTER_ANCHOR)
    lines.append("```\n")
    lines.append("---")
    lines.append("## ⚙️ 2. أسرار الحركة الحقيقية (Real Motion Settings فـ Google Flow)")
    lines.append("باش ما يخرجش ليك المشهد صورة جامدة وفيها ghir zoom، هادو هما الإعدادات لي دارو فـ الفيديو ديال Moad Sarmani:\n")
    lines.append("1. **Mode**: ختار **Text-to-Video** أو **Image-to-Video** (وحط صورة ليو كـ Start Frame).")
    lines.append("2. **Aspect Ratio**: ضروري تختار **16:9 Landscape**.")
    lines.append("3. **Motion Intensity**: دير السلايدر فـ **Level 6 أو 7** (باش ليو يتحرك بيديه ورجليه ووجهو).")
    lines.append("4. **Camera Controls**: تبع حركة الكاميرا المحددة فـ كل مشهد لتحت.\n")
    lines.append("---")
    lines.append("## 🎞️ 3. المشاهد بالتفصيل (Prompts مع حركات Motion حقيقية)\n")

    for sc in data["scenes"]:
        lines.append(f"### {sc['scene_title_ar']} (⏱️ ~{sc['duration_sec']} ثواني)")
        lines.append(f"* **نوع الحركة المطلوبة:** `{sc['motion_type']}`")
        lines.append(f"* **إعدادات Flow:** Camera: `{sc['flow_settings']['camera_motion']}` | Motion Slider: `{sc['flow_settings']['motion_slider']}`")
        lines.append(f"* **المؤثر الصوتي المرافق:** `{sc['sfx_cue']}`\n")
        lines.append("#### 📋 البرومبت المباشر لـ Google Flow (كوبيه كما هو فـ Flow):")
        lines.append("```text")
        lines.append(sc["flow_prompt"])
        lines.append("```\n")
        lines.append("#### 🎙️ النص الصوتي بالتشكيل (Voiceover Script):")
        lines.append(f"> \"{sc['voiceover_ar']}\"\n")
        lines.append("-" * 50 + "\n")

    lines.append("## ⚡ 4. كيفاش كيرجع هادشي فيديو واجد لـ YouTube فـ دقيقة واحدة؟")
    lines.append("1. نزل الـ 5 فيديوهات من Google Flow (كل مشهد كـ mp4).")
    lines.append("2. سميهم: `scene_1.mp4`, `scene_2.mp4`, `scene_3.mp4`, `scene_4.mp4`, `scene_5.mp4`.")
    lines.append(f"3. حطهم فـ هاد المجلد مباشرة: `output/flow_clips/`.")
    lines.append("4. طلق هاد الكوماند الوحيدة فـ Terminal:")
    lines.append("   ```powershell")
    lines.append("   python scripts/stitch_flow_episode.py")
    lines.append("   ```")
    lines.append("5. السكريبت كيتكلف بـ: الصوت العربي، الترجمة المتحركة التحتية، الموسيقى الخلفية، المونتاج التلقائي، والنشر المباشر فـ YouTube كـ Draft!\n")
    lines.append("---")
    lines.append("## 🏷️ 5. بيانات النشر لـ YouTube (SEO & Chapters)")
    lines.append(f"**العنوان:** `{data['youtube_metadata']['title']}`\n")
    lines.append("**الفصول في الوصف (Chapters):**")
    lines.append("```text")
    for ch in data["youtube_metadata"]["chapters"]:
        lines.append(ch)
    lines.append("```\n")
    lines.append(f"**الوسوم (Tags):** `{', '.join(data['youtube_metadata']['tags'])}`")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ Package exported to: {filepath}")

def main():
    target_file = OUTPUT_DIR / "pilot_space_adventure_flow_package.md"
    export_storyboard_to_markdown(PILOT_STORY_SPACE_ADVENTURE, target_file)

if __name__ == "__main__":
    main()
