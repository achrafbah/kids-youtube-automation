"""Google Flow Production Package: Leo & The Lost Kitten in the Rain (Animal Kindness & Empathy).
Official Tales of Wonder Educational Long-Form Episode.
7 Sequential Scenes with Cause-and-Effect Storytelling, Nano Banana Pro 16:9 Image Prompts,
Google Flow Image-to-Video Motion Prompts, and Synchronized Arabic Tashkeel Voiceover.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "flow_storyboards"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LEO_LOST_KITTEN_STORY = {
    "story_title_ar": "لِيُو وَإِنْقَاذُ القِطَّةِ التَّائِهَةِ فِي المَطَر 🐱🌧️💛",
    "theme": "الرِّفْقُ بِالحَيَوَانِ، العَطْفُ، وَمُسَاعَدَةُ الضَّعِيف (Animal Kindness & Empathy)",
    "target_aspect_ratio": "16:9 Widescreen (1920x1080)",
    "scenes": [
        {
            "scene_number": 1,
            "scene_title_ar": "المشهد 1: ليو يلعب في الحديقة قبل المطر",
            "narrative_function": "الوضعية الابتدائية - ليو يستمتع بوقته في حديقة المنزل الخضراء",
            "nanobanana_prompt": (
                "An adorable 6-year-old cartoon boy named Leo, messy curly brown hair, warm brown eyes, "
                "wearing a bright yellow sweater and blue denim overalls, smiling cheerfully while playing with a colorful red ball "
                "in a lush green family backyard garden with blooming roses, soft overcast afternoon lighting, "
                "Disney Pixar 3D animated movie style, Octane 3D render, ultra cute, highly detailed, cinematic, --ar 16:9"
            ),
            "flow_motion_prompt": (
                "Camera slowly glides left to right. Leo happily bounces the red ball on the green grass, "
                "running forward two steps with a cheerful playful laugh, brushing his curly hair with his hand, "
                "then stops and looks up as soft raindrops begin to fall. Fluid 3D character animation, natural running physics, 16:9 widescreen."
            ),
            "flow_settings": {"camera_motion": "Slow Pan Right", "motion_slider": "Level 6 (Dynamic)"},
            "voiceover_ar": "فِي مَسَاءِ يَوْمٍ لَطِيف، كَانَ صَدِيقُنَا لِيُو يَلْعَبُ بِكُرَتِهِ الحَمْرَاءِ فِي حَدِيقَةِ المَنْزِل. كَانَ كُلُّ شَيْءٍ يَمْلَؤُهُ المَرَح.. حَتَّى بَدَأَتْ قَطَرَاتُ المَطَرِ تَهْطِلُ بِلُطْف!",
            "sfx_cue": "Playful children xylophone + gentle rain drops on leaves",
            "duration_sec": 7
        },
        {
            "scene_number": 2,
            "scene_title_ar": "المشهد 2: بداية المطر وسماع مواء حزين",
            "narrative_function": "الحدث المحرك - ليو يحتمي من المطر ويسمع استغاثة القطة",
            "nanobanana_prompt": (
                "Leo standing under the wooden roof of his garden patio, holding his red ball, "
                "listening carefully with a curious surprised expression, looking toward a wet wooden garden bench in the rain, "
                "soft rain falling outside creating ripples in puddles, warm cozy porch lighting contrasting with cool rain, "
                "Disney Pixar 3D animated style, highly detailed, emotional, --ar 16:9"
            ),
            "flow_motion_prompt": (
                "Camera pushes in toward Leo. Leo turns his head and puts his hand to his ear, listening intently. "
                "His eyes widen with concern as he hears a soft crying sound. He takes two cautious steps forward, "
                "looking through the falling raindrops towards the wet bench. Realistic rain animation, expressive facial acting, 16:9 widescreen."
            ),
            "flow_settings": {"camera_motion": "Slow Push In", "motion_slider": "Level 6 (Dynamic)"},
            "voiceover_ar": "أَسْرَعَ لِيُو يَحْتَمِي تَحْتَ مَظَلَّةِ المَنْزِل. وَفَجْأَةً.. سَمِعَ صَوْتًا ضَعِيفًا يَبْكِي بَيْنَ الأَمْطَار: 'مِيَاوْ.. مِيَاوْ..' يَا تُرَى، مَنْ يَكُونُ هَذَا الصَّغِيرُ الخَائِف؟",
            "sfx_cue": "Rainfall ambiance 🌧️ + faint sad kitten meow 🐱 + gentle cello notes",
            "duration_sec": 8
        },
        {
            "scene_number": 3,
            "scene_title_ar": "المشهد 3: اكتشاف القطة الصغيرة المبللة تحت المقعد",
            "narrative_function": "الاكتشاف والشفقة - ليو يجد القطة ترتجف من البرد",
            "nanobanana_prompt": (
                "Leo kneeling down gently on the wet grass near a wooden garden bench, "
                "looking with immense tenderness and compassion at an adorable tiny ginger and white kitten shivering under the bench, "
                "the kitten has huge watery blue eyes and soaked fur, Leo extending his hand slowly to comfort it, "
                "Pixar 3D emotional scene, glowing rain particles, cinematic lighting, --ar 16:9"
            ),
            "flow_motion_prompt": (
                "Low angle close-up shot. The tiny ginger kitten shivers in the cold, tucking its wet paws and meowing softly. "
                "Leo kneels down gently, slowly stretching his warm hand forward, smiling with deep tenderness, "
                "and gently stroking the kitten's head with his finger to reassure it. Heartwarming emotional character acting, 16:9 widescreen."
            ),
            "flow_settings": {"camera_motion": "Low Angle Dolly", "motion_slider": "Level 5 (Gentle Emotion)"},
            "voiceover_ar": "اِقْتَرَبَ لِيُو بِهُدُوء، فَوَجَدَ قِطَّةً صَغِيرَةً لَطِيفَةً مُبَلَّلَةً بِالمَطَر، تَرْتَجِفُ مِنَ البَرْدِ وَتَبْحَثُ عَنْ أَمَان! لَمْ يَتَرَدَّدْ لِيُو لَحْظَةً وَاحِدَةً فِي مُسَاعَدَتِهَا!",
            "sfx_cue": "Soft kitten purr starting + emotional warm piano melody",
            "duration_sec": 8
        },
        {
            "scene_number": 4,
            "scene_title_ar": "المشهد 4: تدفئة القطة وإطعامها الحليب في البيت",
            "narrative_function": "العناية والرحمة - ليو ينشف القطة ويطعمها الحليب الدافئ",
            "nanobanana_prompt": (
                "Inside a cozy warm living room with a glowing fireplace in background, "
                "Leo sitting cross-legged on a soft carpet, wrapping the tiny fluffy dry kitten in a warm yellow towel, "
                "the kitten is happily licking a small blue ceramic saucer filled with warm white milk, "
                "Leo smiling with pure joy watching the kitten, Disney Pixar 3D style, warm amber lighting, ultra cozy, --ar 16:9"
            ),
            "flow_motion_prompt": (
                "Warm medium shot. Leo gently pats the fluffy kitten with the soft towel, smiling proudly. "
                "The kitten happily drinks from the milk saucer, its tiny tail wagging with delight. "
                "The kitten then raises its head, licking Leo's finger affectionately, making Leo giggle happily. "
                "Fluid cozy character animation, lively kitten physics, 16:9 widescreen."
            ),
            "flow_settings": {"camera_motion": "Gentle Arc", "motion_slider": "Level 6 (Dynamic)"},
            "voiceover_ar": "حَمَلَهَا لِيُو بِحَنَانٍ إِلَى دَاخِلِ المَنْزِل. جَفَّفَ فَرْوَهَا بِمِنْشَفَةٍ دَافِئَة، وَقَدَّمَ لَهَا طَبَقًا مِنَ الحَلِيبِ اللَّذِيذ! شَرِبَتِ القِطَّةُ حَتَّى شَبِعَتْ، وَبَدَأَتْ تَمْسَحُ رَأْسَهَا بِيَدِ لِيُو عِرْفَانًا بِالجَمِيل!",
            "sfx_cue": "Milk lapping sound + joyful children giggle + warm fireplace crackle",
            "duration_sec": 8
        },
        {
            "scene_number": 5,
            "scene_title_ar": "المشهد 5: توقف المطر وظهور قوس قزح والبحث عن الأم",
            "narrative_function": "انطلاق رحلة البحث - خروج ليو والقطة للبحث عن صاحبها",
            "nanobanana_prompt": (
                "Sunlight bursting through parting storm clouds creating a magnificent vibrant rainbow in the sky, "
                "Leo standing proudly by the open garden wooden gate, holding the happy ginger kitten safely in his arms, "
                "sparkling raindrops on lush green leaves, wet asphalt reflecting golden sunlight, "
                "Pixar 3D feature movie lighting, vibrant hopeful colors, --ar 16:9"
            ),
            "flow_motion_prompt": (
                "Camera tracks forward beside Leo. Leo walks briskly and joyfully through the garden gate, "
                "holding the kitten securely in his left arm while pointing happily toward the brilliant rainbow with his right hand. "
                "The kitten looks around with perked ears and lively eyes. Golden sunlight glinting, natural walking locomotion, 16:9 widescreen."
            ),
            "flow_settings": {"camera_motion": "Tracking Forward", "motion_slider": "Level 6 (Dynamic)"},
            "voiceover_ar": "تَوَقَّفَ المَطَرُ وَأَشْرَقَتِ الشَّمْسُ بِقَوْسِ قُزَحٍ بَدِيع! حَمَلَ لِيُو صَدِيقَتَهُ الصَّغِيرَةَ وَخَرَجَا لِيَبْحَثَا عَنْ عَائِلَتِهَا.. فَمَنْ يُنْقِذُ ضَعِيفًا يُتِمُّ مَعْرُوفَهُ إِلَى النِّهَايَة!",
            "sfx_cue": "Chirping birds returning 🐦 + uplifting orchestral strings + gentle breeze",
            "duration_sec": 7
        },
        {
            "scene_number": 6,
            "scene_title_ar": "المشهد 6: لقاء القطة مع الطفلة الصغيرة وفرحة اللقاء",
            "narrative_function": "ذروة الأحداث - إعادة الأمانة وفرحة العائلة",
            "nanobanana_prompt": (
                "A heartwarming emotional scene in a colorful suburban neighborhood street, "
                "an adorable 5-year-old girl with pigtails crying tears of joy as she hugs the ginger kitten that Leo is handing to her with a proud smile, "
                "the girl's mother in background smiling warmly with gratitude at Leo, golden hour sunlight, "
                "Disney Pixar 3D animated movie masterpiece, emotional depth, --ar 16:9"
            ),
            "flow_motion_prompt": (
                "Dynamic emotional shot. Leo gently hands the kitten over to the little girl. "
                "The little girl gasps with immense joy, hugging the kitten tightly to her cheek as the kitten purrs and cuddles her. "
                "Leo stands tall with hands on his hips, smiling with glowing pride and happiness. Emotional Pixar animation, 16:9 widescreen."
            ),
            "flow_settings": {"camera_motion": "Dynamic Medium Orbit", "motion_slider": "Level 7 (High Motion)"},
            "voiceover_ar": "وَفِي نِهَايَةِ الشَّارِع، كَانَتْ طِفْلَةٌ صَغِيرَةٌ تَبْحَثُ عَنْ قِطَّتِهَا الضَّائِعَة! عِنْدَمَا رَأَتْهَا.. طَارَتْ مِنَ الفَرَحِ وَاحْتَضَنَتْهَا، وَشَكَرَتْ لِيُو بِكُلِّ امْتِنَان: 'شُكْرًا لَكَ يَا أَعَزَّ بَطَل!'" ,
            "sfx_cue": "Joyful gasp + happy laughter + triumphant emotional brass and strings",
            "duration_sec": 8
        },
        {
            "scene_number": 7,
            "scene_title_ar": "المشهد 7: العودة وفرحة الإنجاز والعبرة التربوية",
            "narrative_function": "النهاية السعيدة والرسالة البيداغوجية لقناة حكايات العجب",
            "nanobanana_prompt": (
                "Leo walking back home along the garden path at sunset, hands in his overall pockets, "
                "turning toward camera with a radiant heartwarming smile, golden evening glow, colorful blooming flowers around him, "
                "a tiny butterfly fluttering near his shoulder, Disney Pixar 3D ending scene, full of warmth and inspiration, --ar 16:9"
            ),
            "flow_motion_prompt": (
                "Camera slowly pulls back. Leo walks leisurely toward the camera with a joyful bounce in his step, "
                "stops, waves both hands warmly to the viewer, smiling brightly with twinkling eyes, "
                "giving a gentle nod of encouragement as the screen softly fades to golden twilight. 24fps Pixar character motion, 16:9 widescreen."
            ),
            "flow_settings": {"camera_motion": "Slow Pull Back", "motion_slider": "Level 5 (Gentle Emotion)"},
            "voiceover_ar": "عَادَ لِيُو إِلَى بَيْتِهِ وَقَلْبُهُ يَمْلَؤُهُ السُّرُور. تَعَلَّمَ أَنَّ الرِّفْقَ بِالحَيَوَانِ وَالعَطْفَ عَلَى مَنْ هُوَ أَضْعَفُ مِنَّا، هُوَ أَجْمَلُ عَمَلٍ يَجْعَلُنَا أَبْطَالًا حَقِيقِيِّين! نَلْتَقِي فِي مُغَامَرَةٍ جَدِيدَةٍ يَا أَصْدِقَائِي، مَعَ السَّلَامَة!",
            "sfx_cue": "Gentle acoustic guitar outro + heartwarming lullaby finish",
            "duration_sec": 8
        }
    ],
    "youtube_metadata": {
        "title": "مغامرة ليو وإنقاذ القطة التائهة في المطر 🐱🌧️ | قصة كرتونية هادفة للأطفال بدقة 4K",
        "chapters": [
            "00:00 - ليو يلعب في الحديقة قبل المطر",
            "00:45 - مفاجأة وصوت استغاثة",
            "01:30 - العثور على القطة الصغيرة المبللة",
            "02:20 - العناية والتدفئة وطبق الحليب",
            "03:15 - ظهور قوس قزح وبداية البحث",
            "04:05 - لقاء مؤثر وإعادة الأمانة",
            "04:55 - سر السعادة والعبرة التربوية"
        ],
        "tags": [
            "قصص اطفال", "كرتون اطفال", "الرفق بالحيوان للاطفال", "حكايات العجب",
            "قصة ليو", "كرتون 3D", "قصص قبل النوم", "افلام كرتون هادفة",
            "تعليم الاطفال الرحمة", "قصص اطفال جديدة"
        ]
    }
}

def export_storyboard_to_markdown(data: Dict[str, Any], filepath: Path):
    """Export complete production package to Markdown."""
    lines = []
    lines.append(f"# 🎬 Google Flow Production Package: {data['story_title_ar']}")
    lines.append(f"**المحور التربوي الرسمي للقناة:** {data['theme']} | **صيغة العرض:** `{data['target_aspect_ratio']}`\n")
    lines.append("---")
    lines.append("## 🎞️ المشاهد الـ 7 بالتفصيل (Nano Banana Pro Prompts + Google Flow Motion Prompts)\n")

    for sc in data["scenes"]:
        lines.append(f"### {sc['scene_title_ar']} (⏱️ ~{sc['duration_sec']} ثواني)")
        lines.append(f"* **الوظيفة الدرامية:** `{sc['narrative_function']}`")
        lines.append(f"* **إعدادات Flow الموصى بها:** Camera: `{sc['flow_settings']['camera_motion']}` | Motion: `{sc['flow_settings']['motion_slider']}`\n")
        lines.append("#### 🖼️ برومبت Nano Banana Pro (توليد الصورة 16:9):")
        lines.append("```text")
        lines.append(sc["nanobanana_prompt"])
        lines.append("```\n")
        lines.append("#### 🎬 برومبت Google Flow (تحريك الصورة Image-to-Video):")
        lines.append("```text")
        lines.append(sc["flow_motion_prompt"])
        lines.append("```\n")
        lines.append("#### 🎙️ التعليق الصوتي المشكول:")
        lines.append(f"> \"{sc['voiceover_ar']}\"\n")
        lines.append("-" * 55 + "\n")

    lines.append("## 🏷️ بيانات النشر لـ YouTube")
    lines.append(f"**العنوان:** `{data['youtube_metadata']['title']}`\n")
    lines.append("**الفصول:**")
    lines.append("```text")
    for ch in data["youtube_metadata"]["chapters"]:
        lines.append(ch)
    lines.append("```\n")
    lines.append(f"**الوسوم:** `{', '.join(data['youtube_metadata']['tags'])}`")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ Package exported to: {filepath}")

def main():
    target_file = OUTPUT_DIR / "leo_lost_kitten_flow_package.md"
    export_storyboard_to_markdown(LEO_LOST_KITTEN_STORY, target_file)

if __name__ == "__main__":
    main()
