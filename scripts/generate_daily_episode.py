"""Daily Educational Episode Automation Engine for Preschool & Primary Kids (3-10 Years).
Channel: Tales of Wonder.

Curriculum Pillars:
1. الآداب والأخلاق والتربية الحسنة (Manners, Respect & Values)
2. برنامج الروض واللغة العربية (Preschool Arabic Letters & Words)
3. الأرقام والحساب الممتع والأشكال (Numbers, Counting & Shapes)
4. العادات الصحية والنظام (Healthy Habits & Daily Routines)

Audio & Visual Pipeline:
- Gemini 3.8 Flash TTS expressive voice synthesis (warm, energetic cartoon storyteller)
- 3D Pixar character Leo & themed educational scenes
- Gentle music box nursery background music (BGM) mixed softly under narration
- Smooth 30fps 1080x1920 (9:16) Ken Burns dynamic 2.5D camera animation
- Anti-duplication database tracking in data/topics_history.json
- Automated Private / Draft YouTube upload to Tales of Wonder
"""

import os
import sys
import json
import base64
import datetime
import subprocess
from pathlib import Path

# Fix Windows console encoding for Arabic characters
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google import genai
from PIL import Image
import imageio_ffmpeg
from youtube_uploader import upload_video

# Add parent directory to path for production_studio imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from production_studio.animation_engine import AnimationEngine

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHARACTERS_DIR = BASE_DIR / "characters"
SCENES_DIR = CHARACTERS_DIR / "scenes"
OUTPUT_DIR = BASE_DIR / "output"
ENV_FILE = BASE_DIR / ".env"

TOPICS_FILE = DATA_DIR / "topics_history.json"
CHARACTERS_FILE = CHARACTERS_DIR / "character_bible.json"
BGM_FILE = SCENES_DIR / "kids_gentle_bgm.wav"

def get_gemini_api_key():
    if ENV_FILE.exists():
        for line in open(ENV_FILE, encoding="utf-8"):
            if line.startswith("GEMINI_API_KEY="):
                return line.strip().split("=", 1)[1]
    return os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6Ly6CghBsKIp9KFboAoEWe_N7hlrKwYhzBosimjI_JVrA")

def load_json(path):
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Rich pedagogical curriculum for 3 to 10 years across 4 core pillars
CURRICULUM_TOPICS = [
    # ==========================================
    # المحور 1: الأخلاق والآداب والتربية الحسنة
    # ==========================================
    {
        "topic_key": "polite-words-magic",
        "pillar": "الآداب والأخلاق (Manners)",
        "scene_name": "manners_classroom.jpg",
        "title_ar": "سِحْرُ الكَلِمَاتِ الطَّيِّبَة: مِنْ فَضْلِكَ وَشُكْرًا ✨",
        "script": (
            "أَهْلًا يَا أَبْطَالَ حِكَايَاتِ العَجَائِب! "
            "هَلْ تَعْلَمُونَ أَنَّ لَدَيْنَا كَلِمَاتٍ سِحْرِيَّةً تَجْعَلُ كُلَّ النَّاسِ يُحِبُّونَنَا؟ "
            "عِنْدَمَا نَطْلُبُ شَيْئًا مِنْ مَامَا أَوْ صَدِيقِنَا، نَقُولُ بِأَدَب: مِنْ فَضْلِك! "
            "وَعِنْدَمَا يُقَدِّمُ لَنَا أَحَدٌ شَيْئًا جَمِيلًا، نَبْتَسِمُ وَنَقُول: شُكْرًا لَك! "
            "الكَلِمَةُ الطَّيِّبَةُ تَصْنَعُ الفَرَحَ وَالمَحَبَّة.. كُونُوا دَوْمًا أَبْطَالَ الأَدَبِ وَالأَخْلَاق!"
        ),
        "lesson": "طلب الأشياء بأدب وتقديم الشكر يزرع المحبة بين الجميع.",
        "tags": ["#shorts", "#أطفال", "#تربية_الطفل", "#آداب_الأطفال", "#تعليم_الروضة", "#talesofwonder"]
    },
    {
        "topic_key": "respecting-parents",
        "pillar": "الآداب والأخلاق (Manners)",
        "scene_name": "manners_classroom.jpg",
        "title_ar": "بِرُّ الوَالِدَيْن: أُمِّي وَأَبِي تَاجُ رَأْسِي ❤️",
        "script": (
            "مَرْحَبًا يَا أَصْدِقَائِي الأَعِزَّاء! "
            "أُمُّنَا وَأَبُونَا يَبْذُلاَنِ كُلَّ جُهْدِهِمَا لِنَكُونَ سُعَدَاءَ وَآمِنِين! "
            "كَيْفَ نُسْعِدُهُمَا؟ بِسَمَاعِ كَلَامِهِمَا، وَتَقْبِيلِ أَيْدِيهِمَا، وَمُسَاعَدَتِهِمَا فِي تَرْتِيبِ المَنْزِل! "
            "ابْتِسَامَةُ أُمِّكَ وَأَبِيكَ هِيَ أَجْمَلُ جَائِزَةٍ فِي العَالَم! قُولُوا لَهُمَا اليَوْم: أُحِبُّكُمَا كَثِيرًا!"
        ),
        "lesson": "طاعة الوالدين وإسعادهما واجب وأجمل عمل يقوم به الطفل الصالح.",
        "tags": ["#shorts", "#بر_الوالدين", "#أخلاق_الأطفال", "#تربية_إسلامية_للأطفال", "#talesofwonder"]
    },
    {
        "topic_key": "saying-sorry-honesty",
        "pillar": "الآداب والأخلاق (Manners)",
        "scene_name": "manners_classroom.jpg",
        "title_ar": "شَجَاعَةُ الاِعْتِذَارِ وَقَوْلُ الصِّدْق 🤝",
        "script": (
            "أَهْلًا يَا أَبْطَال! هَلْ تَعْلَمُونَ مَنْ هُوَ البَطَلُ الحَقِيقِيّ؟ "
            "البَطَلُ هُوَ الَّذِي يَقُولُ الصِّدْقَ دَائِمًا وَلَا يَكْذِب! "
            "وَإِذَا أَخْطَأْنَا دُونَ قَصْد، نَتَحَلَّى بِالشَّجَاعَةِ وَنَقُول: أَنَا آسِف، لَنْ أُعِيدَهَا ثَانِيَة! "
            "الصِّدْقُ يُنَجِّينَا وَيَجْعَلُ الجَمِيعَ يَثِقُونَ بِنَا وَيَحْتَرِمُونَنَا!"
        ),
        "lesson": "الصدق فضيلة وشجاعة، والاعتذار عند الخطأ خلق رفيع.",
        "tags": ["#shorts", "#الصدق", "#الاعتذار", "#تربية_الطفل", "#أخلاق_حميدة", "#talesofwonder"]
    },
    {
        "topic_key": "sharing-is-caring",
        "pillar": "الآداب والأخلاق (Manners)",
        "scene_name": "manners_classroom.jpg",
        "title_ar": "مُشَارَكَةُ الأَلْعَاب: فَرَحَةُ العَطَاءِ 🧸🎁",
        "script": (
            "مَرْحَبًا يَا صِغَارِي! اللَّعِبُ لَذِيذ، لَكِنَّ اللَّعِبَ مَعَ الأَصْدِقَاءِ أَجْمَلُ بِكَثِير! "
            "عِنْدَمَا نُشَارِكُ أَلْعَابَنَا وَأَلْوَانَنَا مَعَ إِخْوَانِنَا، تَكْبُرُ الفَرْحَةُ فِي قُلُوبِنَا! "
            "المُشَارَكَةُ تَبْنِي صَدَاقَاتٍ رَائِعَة، وَتَجْعَلُنَا مَحْبُوبِينَ فِي كُلِّ مَكَان!"
        ),
        "lesson": "مشاركة الألعاب تعزز الصداقة وتزرع روح العطاء والمحبة بين الأطفال.",
        "tags": ["#shorts", "#مشاركة_الألعاب", "#أخلاق_الأطفال", "#تربية_الأطفال", "#talesofwonder"]
    },

    # ==========================================
    # المحور 2: برنامج الروض واللغة العربية
    # ==========================================
    {
        "topic_key": "arabic-letters-alif-baa",
        "pillar": "اللغة العربية والروض (Alphabet)",
        "scene_name": "alphabet_nursery.jpg",
        "title_ar": "قِطَارُ الحُرُوف: حَرْفُ الأَلِفِ وَالبَاء 🚂🔤",
        "script": (
            "تُووت تُووت! قِطَارُ الحُرُوفِ العَرَبِيَّةِ وَصَل! "
            "أَوَّلُ حَرْفٍ هُوَ الأَلِف: أ.. أَرْنَبٌ يَأْكُلُ الجَزَر! وَأَسَدٌ مَلِكُ الغَابَة! "
            "وَالحَرْفُ الثَّانِي هُوَ البَاء: ب.. بَطَّةٌ تَسْبَحُ فِي المَاء! وَبَيْتٌ دَافِئٌ جَمِيل! "
            "مَا أَجْمَلَ لُغَتَنَا العَرَبِيَّة! رَدِّدُوا مَعِي: أَلِف.. بَاء!"
        ),
        "lesson": "التعرف على حرفي الألف والباء بنطق سليم وكلمات مصورة للأطفال.",
        "tags": ["#shorts", "#حروف_الهجاء", "#اللغة_العربية_للأطفال", "#تعليم_الروضة", "#talesofwonder"]
    },
    {
        "topic_key": "arabic-letters-taa-thaa",
        "pillar": "اللغة العربية والروض (Alphabet)",
        "scene_name": "alphabet_nursery.jpg",
        "title_ar": "قِطَارُ الحُرُوف: حَرْفُ التَّاءِ وَالثَّاء 🍎🦊",
        "script": (
            "أَهْلًا يَا أَبْطَالَ اللُّغَةِ العَرَبِيَّة! "
            "مَحَطَّتُنَا اليَوْمَ مَعَ حَرْفِ التَّاء: تَـ.. تُفَّاحَةٌ لَذِيذَةٌ وَحَمْرَاء! وَتَاجٌ ذَهَبِيٌّ لِلأَمِير! "
            "ثُمَّ حَرْفُ الثَّاء: ثَـ.. ثَعْلَبٌ ذَكِيٌّ وَسَرِيع! وَثَلْجٌ أَبْيَضُ نَاصِع! "
            "رَدِّدُوا بِصَوْتٍ عَالٍ: تَاء.. ثَاء.. أَحْسَنْتُمْ يَا شُطَّار!"
        ),
        "lesson": "تعليم نطق حرفي التاء والثاء مع أمثلة بصرية ممتعة.",
        "tags": ["#shorts", "#حرف_التاء", "#حرف_الثاء", "#لغتي_العربية", "#تعليم_الأطفال", "#talesofwonder"]
    },
    {
        "topic_key": "arabic-letters-jeem-haa-khaa",
        "pillar": "اللغة العربية والروض (Alphabet)",
        "scene_name": "alphabet_nursery.jpg",
        "title_ar": "قِطَارُ الحُرُوف: الإِخْوَةُ الثَّلَاثَة (ج، ح، خ) 🐪🐴",
        "script": (
            "مَرْحَبًا يَا أَصْدِقَائِي! مَعَنَا اليَوْمَ ثَلَاثَةُ إِخْوَةٍ مُتَشَابِهِين! "
            "الجِيم: فِي بَطْنِهِ نُقْطَة.. ج.. جَمَلٌ صَبُورٌ فِي الصَّحْرَاء! "
            "الحَاء: بِلَا نُقْطَة.. ح.. حِصَانٌ سَرِيعٌ وَرَشِيق! "
            "وَالخَاء: فَوْقَ رَأْسِهِ نُقْطَة.. خ.. خَرُوفٌ جَمِيلٌ ذُو صُوفٍ دَافِئ! "
            "يَا لَهَا مِنْ حُرُوفٍ رَائِعَة!"
        ),
        "lesson": "التمييز بين الحروف المتشابهة (ج، ح، خ) ومواضع النقطة بطريقة مبتكرة.",
        "tags": ["#shorts", "#حروف_الهجاء", "#جيم_حاء_خاء", "#تعليم_مبكر", "#talesofwonder"]
    },

    # ==========================================
    # المحور 3: الأرقام والحساب الممتع والأشكال
    # ==========================================
    {
        "topic_key": "counting-numbers-1-to-5",
        "pillar": "الأرقام والحساب (Numbers & Math)",
        "scene_name": "counting_numbers.jpg",
        "title_ar": "مُغَامَرَةُ الأَرْقَام: نَتَعَلَّمُ العَدَّ مِنْ 1 إِلَى 5 🍎🔢",
        "script": (
            "تَعَالَوْا يَا صِغَار لِنَعُدَّ مَعًا التُّفَّاحَاتِ اللَّذِيذَة! "
            "وَاحِد: تُفَّاحَةٌ حَمْرَاء! "
            "اِثْنَان: تُفَّاحَتَان! "
            "ثَلَاثَة.. أَرْبَعَة.. خَمْسَة! "
            "لَدَيْنَا خَمْسُ تُفَّاحَاتٍ كَأَصَابِعِ يَدِنَا الوَاحِدَة! "
            "أَحْسَنْتُمْ يَا عَبَاقِرَةَ الحِسَاب!"
        ),
        "lesson": "تعليم الطفل العد من 1 إلى 5 باستخدام الأصابع والأشياء الملموسة.",
        "tags": ["#shorts", "#أرقام_للأطفال", "#حساب_الروضة", "#تعليم_الأرقام", "#رياضيات_مبسطة", "#talesofwonder"]
    },
    {
        "topic_key": "counting-numbers-6-to-10",
        "pillar": "الأرقام والحساب (Numbers & Math)",
        "scene_name": "counting_numbers.jpg",
        "title_ar": "مُغَامَرَةُ الأَرْقَام: نُكْمِلُ العَدَّ مِنْ 6 إِلَى 10 ⭐🔟",
        "script": (
            "أَهْلًا بِعَبَاقِرَةِ الرِّيَاضِيَّات! نُوَاصِلُ رِحْلَةَ العَدِّ المُمْتِعَة! "
            "بَعْدَ الخَمْسَة.. سِتَّة.. سَبْعَة.. ثَمَانِيَة.. تِسْعَة.. عَشَرَة! "
            "عَشَرَةُ أَرْقَامٍ مُمَيَّزَةٍ كَأَصَابِعِ يَدَيْنَا الاثْنَتَيْن! "
            "صَفِّقُوا مَعِي عَشْرَ مَرَّاتٍ احْتِفَالًا بِإِنْجَازِكُمْ الرَّائِع!"
        ),
        "lesson": "إتقان العد من 6 إلى 10 وتطوير المهارات الحسابية الأساسية للطفل.",
        "tags": ["#shorts", "#أرقام_1_10", "#حساب_أطفال", "#تعليم_الحساب", "#talesofwonder"]
    },
    {
        "topic_key": "geometric-shapes-colors",
        "pillar": "الأشكال والألوان (Shapes & Colors)",
        "scene_name": "counting_numbers.jpg",
        "title_ar": "عَالَمُ الأَشْكَالِ الهَنْدَسِيَّةِ وَالأَلْوَان 🟡🔺🟦",
        "script": (
            "انْظُرُوا حَوْلَكُمْ فِي الغُرْفَة! "
            "الشَّمْسُ فِي السَّمَاءِ دَائِرَةٌ صَفْرَاء! "
            "وَالبَابُ مُسْتَطِيلٌ كَبِير! "
            "وَقِطْعَةُ البِيتْزَا مُثَلَّثٌ لَذِيذ! "
            "الأَشْكَالُ الهَنْدَسِيَّةُ تَمْلأُ عَالَمَنَا فِي كُلِّ مَكَان.. مَا هُوَ شَكْلُ لُعْبَتِكَ المُفَضَّلَة؟"
        ),
        "lesson": "التمييز بين الدائرة والمثلث والمربع والمستطيل في الحياة اليومية.",
        "tags": ["#shorts", "#أشكال_هندسية", "#ألوان_للأطفال", "#تعليم_مبكر", "#talesofwonder"]
    },

    # ==========================================
    # المحور 4: العادات الصحية والنظام
    # ==========================================
    {
        "topic_key": "dental-hygiene-superhero",
        "pillar": "العادات الصحية والنظام (Healthy Habits)",
        "scene_name": "hygiene_brushing_teeth.jpg",
        "title_ar": "بَطَلُ الأَسْنَانِ السِّحْرِيَّة: نَبْتَسِمُ بِبَيَاضٍ نَاصِع 🪥✨",
        "script": (
            "مَرْحَبًا يَا أَبْطَالَ النَّظَافَة! "
            "أَسْنَانُنَا الجَمِيلَةُ تُحِبُّ الانْتِعَاش! "
            "فِي الصَّبَاحِ بَعْدَ الإِفْطَار، وَفِي اللَّيْلِ قَبْلَ النَّوْم، نَأْخُذُ الفُرْشَاةَ وَالمَعْجُون! "
            "نُنَظِّفُ أَعْلَى وَأَسْفَل، يَمِينًا وَيَسَارًا، لِتَطِيرَ سُوسَةُ الأَسْنَانِ بَعِيدًا! "
            "ابْتِسَامَتُكُمْ البَيْضَاءُ تُضِيءُ العَالَم!"
        ),
        "lesson": "تنظيف الأسنان مرتين يومياً بالفرشاة والمعجون يحافظ على صحتها ونظافتها.",
        "tags": ["#shorts", "#تنظيف_الأسنان", "#صحة_الطفل", "#عادات_صحية", "#talesofwonder"]
    },
    {
        "topic_key": "tidy-room-routine",
        "pillar": "العادات الصحية والنظام (Healthy Habits)",
        "scene_name": "routine_tidying_toys.jpg",
        "title_ar": "بَطَلُ التَّرْتِيب: نُعِيدُ الأَلْعَابَ إِلَى مَكَانِهَا 🧸📦",
        "script": (
            "اللَّعِبُ مُمْتِعٌ جِدًّا، لَكِنَّ البَطَلَ الحَقِيقِيَّ لَا يَتْرُكُ غُرْفَتَهُ فَوْضَوِيَّة! "
            "عِنْدَمَا نَنْتَهِي مِنَ اللَّعِب، نَجْمَعُ السِّيَّارَاتِ وَالمُكَعَّبَاتِ وَنَضَعُهَا فِي الصُّنْدُوق! "
            "الغُرْفَةُ المُرَتَّبَةُ تَجْعَلُنَا نَجِدُ أَلْعَابَنَا بِسُرْعَة، وَتُفْرِحُ مَامَا كَثِيرًا! "
            "هَيَّا يَا أَبْطَالَ النِّظَام، رَتِّبُوا غُرَفَكُمْ مَعِي!"
        ),
        "lesson": "تعويد الطفل على تحمل المسؤولية وترتيب غرفته وألعابه بعد اللعب.",
        "tags": ["#shorts", "#ترتيب_الغرفة", "#عادات_صحية_للأطفال", "#النظام", "#talesofwonder"]
    },
    {
        "topic_key": "washing-hands-habit",
        "pillar": "العادات الصحية والنظام (Healthy Habits)",
        "scene_name": "hygiene_brushing_teeth.jpg",
        "title_ar": "فَقَاقِيعُ الصَّابُون: غَسْلُ اليَدَيْنِ بِذَكَاء 🧼💦",
        "script": (
            "أَهْلًا يَا صِغَار! قَبْلَ تَنَاوُلِ الطَّعَام، وَبَعْدَ العَوْدَةِ مِنَ اللَّعِب، مَاذَا نَفْعَل؟ "
            "نَفْتَحُ الصَّنْبُور، نَضَعُ الصَّابُونَ الجَمِيل، وَنَفْرُكُ كُفُوفَنَا وَأَصَابِعَنَا لِمُدَّةِ عِشْرِينَ ثَانِيَة! "
            "المَاءُ وَالصَّابُونُ يَطْرُدَانِ الجَرَاثِيمَ فَوْرًا وَيَجْعَلَانِ أَيْدِيَنَا نَظِيفَةً وَعَطِرَة!"
        ),
        "lesson": "غسل اليدين بالماء والصابون يقي من الأمراض ويحمي صحة الطفل.",
        "tags": ["#shorts", "#غسل_اليدين", "#نظافة_شخصية", "#عادات_يومية", "#talesofwonder"]
    }
]

def get_next_unique_curriculum_topic():
    history_data = load_json(TOPICS_FILE)
    existing_keys = {t.get("topic_key", t.get("title", "")).lower() for t in history_data.get("topics", [])}

    for item in CURRICULUM_TOPICS:
        if item["topic_key"].lower() not in existing_keys:
            return item, history_data

    # Dynamic fallback rotation
    today_str = datetime.date.today().isoformat()
    fallback = {
        "topic_key": f"preschool-learning-{today_str}",
        "pillar": "التربية والتعليم الشامل (Preschool)",
        "scene_name": "manners_classroom.jpg",
        "title_ar": f"مُغَامَرَةُ التَّعَلُّمِ وَالأَخْلَاق ({today_str}) 🌟",
        "script": (
            "مَرْحَبًا يَا أَصْدِقَائِي! كُلَّ يَوْمٍ نَتَعَلَّمُ شَيْئًا جَدِيدًا يُنِيرُ عُقُولَنَا وَيُهَذِّبُ أَخْلَاقَنَا! "
            "احْتَرِمُوا كِبَارَكُمْ، وَسَاعِدُوا إِخْوَانَكُمْ، وَكُونُوا دَوْمًا نُجُومًا مُشْرِقَةً بِالعِلْمِ وَالأَدَب!"
        ),
        "lesson": "التعلم المستمر والتحلي بالأخلاق يرفعان شأن الطفل الصالح.",
        "tags": ["#shorts", "#تربية_الطفل", "#أخلاق_الأطفال", "#تعليم_الروضة", "#talesofwonder"]
    }
    return fallback, history_data

def generate_voiceover(text, output_audio_path):
    print("🎙️ Generating Gemini 3.8 Flash TTS storytelling voiceover...", flush=True)
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
                    "style": "warm, gentle, encouraging, and highly expressive kindergarten teacher and cartoon narrator",
                }],
            }],
        }],
        response_format={"type": "audio"},
        generation_config={
            "speech_config": [
                {"voice": "Kore"},
            ]
        },
    )

    audio_bytes = base64.b64decode(interaction.output_audio.data)
    with open(output_audio_path, "wb") as f:
        f.write(audio_bytes)
    print(f"✅ Voiceover saved: {output_audio_path}", flush=True)
    return output_audio_path

def assemble_video(image_path, audio_path, bgm_path, output_video_path, topic_title="حِكَايَاتُ العَجَائِب", script_text=""):
    print(f"🎬 Rendering dynamic animated Shorts with Option 2 (motion flow) and Option 3 (subtitles & overlays)...", flush=True)
    engine = AnimationEngine(base_dir=BASE_DIR)
    return engine.render_animated_episode(
        scene_image_path=image_path,
        audio_path=audio_path,
        bgm_path=bgm_path,
        topic_title=topic_title,
        script_text=script_text,
        output_video_path=output_video_path
    )

def execute_daily_run():
    topic, history_data = get_next_unique_curriculum_topic()
    today_str = datetime.date.today().isoformat()
    ep_dir = OUTPUT_DIR / f"{today_str}_{topic['topic_key']}"
    ep_dir.mkdir(parents=True, exist_ok=True)

    audio_path = ep_dir / "voiceover.wav"
    video_path = ep_dir / "episode_shorts.mp4"

    # Select scene image matching topic
    scene_file = SCENES_DIR / topic.get("scene_name", "manners_classroom.jpg")
    if not scene_file.exists():
        scene_file = SCENES_DIR / "manners_classroom.jpg"

    # Step 1: TTS
    generate_voiceover(topic["script"], audio_path)

    # Step 2: Video Assemble with Options 2 & 3 (Kinetic camera, floating animated stars, and synchronized Arabic subtitles)
    assemble_video(
        image_path=scene_file,
        audio_path=audio_path,
        bgm_path=BGM_FILE,
        output_video_path=video_path,
        topic_title=topic["title_ar"],
        script_text=topic["script"]
    )

    # Step 3: Upload to YouTube as DRAFT / PRIVATE
    title = f"{topic['title_ar']} | برنامج الروضة والأخلاق 🌟"
    description = (
        f"مرحباً بكم في حكايات العجائب (Tales of Wonder)! 🌟\n\n"
        f"المحور: {topic['pillar']}\n"
        f"💡 موضوع اليوم: {topic['title_ar']}\n"
        f"🎯 الدرس المستفاد: {topic['lesson']}\n\n"
        f"محتوى تربوي وتأسيسي هادف للأطفال من 3 إلى 10 سنوات (الروضة والمستوى الأولي).\n\n"
        f"اشتركوا معنا ليتعلم أطفالكم كل يوم خلقاً جديداً ومعلومة مفيدة!\n\n"
        f"{' '.join(topic['tags'])}"
    )

    upload_result = upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=topic["tags"],
        privacy_status="private",  # Strictly DRAFT / PRIVATE
        made_for_kids=True,
        thumbnail_path=str(scene_file)
    )

    # Step 4: Record history to prevent duplicates
    new_entry = {
        "topic_key": topic["topic_key"],
        "date": today_str,
        "pillar": topic["pillar"],
        "title": topic["title_ar"],
        "lesson": topic["lesson"],
        "video_url": upload_result.get("video_url") if upload_result else None,
        "status": "private_draft"
    }
    history_data.setdefault("topics", []).append(new_entry)
    save_json(TOPICS_FILE, history_data)

    print("\n" + "=" * 50)
    print("🎉 DAILY RUN COMPLETE!")
    print(f"Pillar: {topic['pillar']}")
    print(f"Title: {topic['title_ar']}")
    if upload_result:
        print(f"Draft URL: {upload_result['video_url']}")
    print("=" * 50)
    return new_entry

if __name__ == "__main__":
    execute_daily_run()
