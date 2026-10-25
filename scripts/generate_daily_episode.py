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
import re
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

# Add repository root and scripts directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from google import genai
from PIL import Image
import imageio_ffmpeg
from youtube_uploader import upload_video
from production_studio.animation_engine import AnimationEngine
from production_studio.art_director import ArtDirectorAgent

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

# Rich pedagogical curriculum for 3 to 10 years across 4 core pillars (32+ Topics)
CURRICULUM_TOPICS = [
    # ==========================================
    # ==========================================
    # المحور 1: الأخلاق والآداب والتربية الحسنة (Manners & Values)
    # ==========================================
    {
        "topic_key": "polite-words-magic",
        "pillar": "الآداب والأخلاق (Manners)",
        "scene_name": "scene_peace_garden.jpg",
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
        "scene_name": "scene_dining_bismillah.jpg",
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
        "scene_name": "scene_sharing_playground.jpg",
        "title_ar": "مُشَارَكَةُ الأَلْعَاب: فَرَحَةُ العَطَاءِ 🧸🎁",
        "script": (
            "مَرْحَبًا يَا صِغَارِي! اللَّعِبُ لَذِيذ، لَكِنَّ اللَّعِبَ مَعَ الأَصْدِقَاءِ أَجْمَلُ بِكَثِير! "
            "عِنْدَمَا نُشَارِكُ أَلْعَابَنَا وَأَلْوَانَنَا مَعَ إِخْوَانِنَا، تَكْبُرُ الفَرْحَةُ فِي قُلُوبِنَا! "
            "المُشَارَكَةُ تَبْنِي صَدَاقَاتٍ رَائِعَة، وَتَجْعَلُنَا مَحْبُوبِينَ فِي كُلِّ مَكَان!"
        ),
        "lesson": "مشاركة الألعاب تعزز الصداقة وتزرع روح العطاء والمحبة بين الأطفال.",
        "tags": ["#shorts", "#مشاركة_الألعاب", "#أخلاق_الأطفال", "#تربية_الأطفال", "#talesofwonder"]
    },
    {
        "topic_key": "spreading-peace-salam",
        "pillar": "الآداب والأخلاق (Manners)",
        "scene_name": "scene_peace_garden.jpg",
        "title_ar": "تَحِيَّةُ الإِسْلَام: السَّلَامُ عَلَيْكُمْ 🕊️",
        "script": (
            "أَهْلًا يَا أَبْطَال! مَا هِيَ أَجْمَلُ تَحِيَّةٍ نَبْدَأُ بِهَا يَوْمَنَا؟ "
            "عِنْدَمَا نَدْخُلُ البَيْتَ أَوِ الفَصْل، نَبْتَسِمُ وَنَقُول: السَّلَامُ عَلَيْكُمْ وَرَحْمَةُ الله! "
            "هَذِهِ الكَلِمَةُ تَنْشُرُ السَّلَامَ وَالأَمَانَ فِي قُلُوبِ الجَمِيع.. رَدِّدُوهَا دَائِمًا!"
        ),
        "lesson": "إفشاء السلام يزرع الطمأنينة والمحبة بين الناس.",
        "tags": ["#shorts", "#إفشاء_السلام", "#أخلاق_إسلامية", "#تعليم_الأطفال", "#talesofwonder"]
    },
    {
        "topic_key": "helping-the-elderly",
        "pillar": "الآداب والأخلاق (Manners)",
        "scene_name": "routine_tidying_toys.jpg",
        "title_ar": "مُسَاعَدَةُ الكِبَارِ وَالعَطْفُ عَلَيْهِم 👵👴",
        "script": (
            "مَرْحَبًا يَا أَصْدِقَائِي! الجَدُّ وَالجَدَّةُ بَرَكَةُ بَيْتِنَا! "
            "عِنْدَمَا نَرَاهُمْ يَحْتَاجُونَ مُسَاعَدَةً فِي حَمْلِ شَيْء، نُسْرِعُ لِمُسَاعَدَتِهِمْ بِكُلِّ أَدَب! "
            "احْتِرَامُ الكِبَارِ خُلُقٌ عَظِيمٌ يَفْخَرُ بِهِ كُلُّ بَطَلٍ صَغِير!"
        ),
        "lesson": "احترام ومساعدة كبار السن واجب يغرس الرحمة في نفوس الصغار.",
        "tags": ["#shorts", "#احترام_الكبير", "#تربية_الأطفال", "#أخلاق_حميدة", "#talesofwonder"]
    },
    {
        "topic_key": "kindness-to-animals",
        "pillar": "الآداب والأخلاق (Manners)",
        "scene_name": "scene_animal_kindness.jpg",
        "title_ar": "الرِّفْقُ بِالحَيَوَان: صَدِيقُنَا الأَلِيف 🐱🐦",
        "script": (
            "أَهْلًا يَا صِغَار! الحَيَوَانَاتُ وَالطُّيُورُ مَخْلُوقَاتٌ لَطِيفَةٌ تُحِبُّ الرِّعَايَة! "
            "نُقَدِّمُ لَهَا المَاءَ وَالطَّعَام، وَلَا نُؤْذِيهَا أَبَدًا! "
            "مَنْ يَرْحَمُ الحَيَوَانَ يَرْحَمُهُ الله، وَيَكُونُ قَلْبُهُ مَلِيئًا بِالطَّيِّبَةِ وَالنُّور!"
        ),
        "lesson": "الرفق بالحيوان وتقديم الطعام والماء له فضيلة إنسانية عظيمة.",
        "tags": ["#shorts", "#الرفق_بالحيوان", "#أخلاق_الطفل", "#تعليم_الأطفال", "#talesofwonder"]
    },
    {
        "topic_key": "patience-and-calm",
        "pillar": "الآداب والأخلاق (Manners)",
        "scene_name": "nature_rain_forest.jpg",
        "title_ar": "الصَّبْرُ الجَمِيلُ وَالتَّحَكُّمُ فِي الغَضَب 🧘‍♂️🌟",
        "script": (
            "مَرْحَبًا يَا أَبْطَال! عِنْدَمَا لَا تَسِيرُ الأُمُورُ كَمَا نُرِيد، مَاذَا نَفْعَل؟ "
            "لَا نَصْرُخُ وَلَا نَغْضَب، بَلْ نَأْخُذُ نَفَسًا عَمِيقًا: شَهِيق.. وَزَفِير! "
            "البَطَلُ القَوِيُّ هُوَ الَّذِي يَتَحَكَّمُ فِي نَفْسِهِ عِنْدَ الغَضَبِ وَيَبْتَسِم!"
        ),
        "lesson": "التحكم في الغضب والتنفس بهدوء يعلم الطفل التوازن العاطفي والصبر.",
        "tags": ["#shorts", "#التحكم_في_الغضب", "#الذكاء_العاطفي", "#تربية_الطفل", "#talesofwonder"]
    },

    # ==========================================
    # المحور 2: برنامج الروض واللغة العربية (Alphabet & Literacy)
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
        "scene_name": "scene_art_colors.jpg",
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
        "scene_name": "nature_rain_forest.jpg",
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
    {
        "topic_key": "arabic-letters-dal-dhal",
        "pillar": "اللغة العربية والروض (Alphabet)",
        "scene_name": "scene_letters_dal_dhal.jpg",
        "title_ar": "قِطَارُ الحُرُوف: حَرْفُ الدَّالِ وَالذَّال 🐻🐺",
        "script": (
            "أَهْلًا يَا صِغَار! رِحْلَتُنَا مُسْتَمِرَّةٌ مَعَ حَرْفِ الدَّال: دَ.. دُبٌّ طَيِّبٌ يُحِبُّ العَسَل! وَدَرَّاجَةٌ سَرِيعَة! "
            "وَأَخُوهُ حَرْفُ الذَّالِ ذُو النُّقْطَة: ذَ.. ذِئْبٌ فِي الغَابَة! وَذُرَةٌ حُلْوَةٌ وَشَهِيَّة! "
            "مَا أَسْهَلَ حُرُوفَنَا العَرَبِيَّة!"
        ),
        "lesson": "التعرف على حرفي الدال والذال والفرق بينهما بالنطق والنقطة.",
        "tags": ["#shorts", "#حرف_الدال", "#حرف_الذال", "#تعليم_الحروف", "#talesofwonder"]
    },
    {
        "topic_key": "arabic-letters-raa-zay",
        "pillar": "اللغة العربية والروض (Alphabet)",
        "scene_name": "scene_fruits_kitchen.jpg",
        "title_ar": "قِطَارُ الحُرُوف: حَرْفُ الرَّاءِ وَالزَّاي 🍇🦒",
        "script": (
            "مَرْحَبًا يَا عَبَاقِرَة! حَرْفُ الرَّاءِ كَالزُّحْلُوقَة: رَ.. رُمَّانٌ يَاقُوتِيٌّ لَذِيذ! وَرِيشَةٌ نَاعِمَة! "
            "وَحَرْفُ الزَّايِ مَعَ نُقْطَتِهِ الجَمِيلَة: زَ.. زَرَافَةٌ طَوِيلَةُ العُنُق! وَزَهْرَةٌ فَوَّاحَة! "
            "أَنْتُمْ رَائِعُونَ جِدًّا فِي التَّعَلُّم!"
        ),
        "lesson": "تعليم نطق حرفي الراء والزاي بكلمات ممتعة للأطفال.",
        "tags": ["#shorts", "#حرف_الراء", "#حرف_الزاي", "#روضة_الأطفال", "#talesofwonder"]
    },
    {
        "topic_key": "arabic-letters-seen-sheen",
        "pillar": "اللغة العربية والروض (Alphabet)",
        "scene_name": "scene_peace_garden.jpg",
        "title_ar": "قِطَارُ الحُرُوف: حَرْفُ السِّينِ وَالشِّين 🐟☀️",
        "script": (
            "أَهْلًا بِأَصْدِقَائِي! حَرْفُ السِّينِ لَهُ ثَلَاثَةُ أَسْنَان: سَ.. سَمَكَةٌ تَسْبَحُ فِي البَحْر! وَسَيَّارَةٌ لَامِعَة! "
            "وَحَرْفُ الشِّينِ بِثَلَاثِ نِقَاط: شَـ.. شَمْسٌ سَاطِعَةٌ تُدْفِئُنَا! وَشَجَرَةٌ خَضْرَاءُ مُثْمِرَة! "
            "رَدِّدُوا: سِين.. شِين!"
        ),
        "lesson": "تعليم حرفي السين والشين مع ربطهما بمظاهر الطبيعة المحيطة بالطفل.",
        "tags": ["#shorts", "#حرف_السين", "#حرف_الشين", "#لغتي_الجميلة", "#talesofwonder"]
    },
    {
        "topic_key": "arabic-letters-saad-daad",
        "pillar": "اللغة العربية والروض (Alphabet)",
        "scene_name": "scene_sharing_playground.jpg",
        "title_ar": "قِطَارُ الحُرُوف: حَرْفُ الصَّادِ وَالضَّاد 🦅🐸",
        "script": (
            "مَرْحَبًا يَا أَبْطَالَ اللُّغَة! حَرْفُ الصَّادِ القَوِيّ: صَـ.. صَقْرٌ يُحَلِّقُ عَالِيًا فِي السَّمَاء! وَصُنْدُوقُ أَلْعَاب! "
            "وَحَرْفُ الضَّاد: ضَـ.. ضِفْدَعٌ يَقْفِزُ بِمَرَح! وَضَوْءٌ يُنِيرُ غُرْفَتَنَا! "
            "لُغَتُنَا العَرَبِيَّةُ هِيَ لُغَةُ الضَّادِ الخَالِدَة!"
        ),
        "lesson": "إتقان نطق حرفي الصاد والضاد والتفريق بينهما بدقة.",
        "tags": ["#shorts", "#لغة_الضاد", "#حرف_الصاد", "#حرف_الضاد", "#talesofwonder"]
    },
    {
        "topic_key": "arabic-letters-taa-zaa",
        "pillar": "اللغة العربية والروض (Alphabet)",
        "scene_name": "alphabet_nursery.jpg",
        "title_ar": "قِطَارُ الحُرُوف: حَرْفُ الطَّاءِ وَالظَّاء ✈️🦌",
        "script": (
            "تُووت تُووت! وَصَلْنَا إِلَى حَرْفِ الطَّاء: طَـ.. طَيَّارَةٌ تُسَافِرُ بَيْنَ الغُيُوم! وَطَبْلٌ يَعْزِفُ أَنْغَامًا! "
            "وَحَرْفُ الظَّاءِ مَعَ النُّقْطَة: ظَـ.. ظَبْيٌ سَرِيعٌ فِي البَرِّيَّة! وَظِلٌّ نَسْتَرِيحُ تَحْتَه! "
            "مَا أَجْمَلَ هَذِهِ الحُرُوفَ المُمَيَّزَة!"
        ),
        "lesson": "التعرف على حرفي الطاء والظاء مع أمثلة بصرية شيقة.",
        "tags": ["#shorts", "#حرف_الطاء", "#حرف_الظاء", "#تعليم_الحروف", "#talesofwonder"]
    },

    # ==========================================
    # المحور 3: الأرقام والحساب الممتع والأشكال (Numbers & Math)
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
        "scene_name": "scene_bedtime_stars.jpg",
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
        "scene_name": "scene_art_colors.jpg",
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
    {
        "topic_key": "fun-addition-fruits",
        "pillar": "الأرقام والحساب (Numbers & Math)",
        "scene_name": "scene_fruits_kitchen.jpg",
        "title_ar": "الجَمْعُ المُمْتِعُ مَعَ الفَوَاكِهِ اللَّذِيذَة 🍌🍓",
        "script": (
            "تَعَالَوْا نَلْعَبْ لُعْبَةَ الجَمْعِ السِّحْرِيَّة! "
            "إِذَا كَانَ مَعَنَا مَوْزَةٌ وَاحِدَة، وَأَعْطَتْنَا مَامَا مَوْزَةً أُخْرَى.. كَمْ مَوْزَةً مَعَنَا الآن؟ "
            "وَاحِد زَائِد وَاحِد يُسَاوِي: اِثْنَان! "
            "أَنْتُمْ عَبَاقِرَةٌ فِي الرِّيَاضِيَّاتِ يَا شُطَّار!"
        ),
        "lesson": "مقدمة مبسطة لعملية الجمع بالاعتماد على الفواكه الملموسة.",
        "tags": ["#shorts", "#الجمع_للأطفال", "#رياضيات_ممتعة", "#تعليم_الحساب", "#talesofwonder"]
    },
    {
        "topic_key": "big-and-small-sizes",
        "pillar": "الأشكال والألوان (Shapes & Colors)",
        "scene_name": "scene_animal_kindness.jpg",
        "title_ar": "عَالَمُ الأَحْجَام: كَبِيرٌ وَصَغِير 🐘🐁",
        "script": (
            "انْظُرُوا مَعِي يَا أَصْدِقَائِي! "
            "الفِيلُ فِي الغَابَةِ حَجْمُهُ كَبِيرٌ جِدًّا! "
            "وَالفَأْرُ اللَّطِيفُ حَجْمُهُ صَغِير! "
            "البِطِّيخَةُ كَبِيرَة، وَالفَرَاوْلَةُ صَغِيرَة! تَعَلُّمُ الأَحْجَامِ لُعْبَةٌ سَهْلَةٌ وَمُمْتِعَة!"
        ),
        "lesson": "التمييز بين مفهومي الكبير والصغير من خلال مقارنة الحيوانات والفواكه.",
        "tags": ["#shorts", "#المفاهيم_الأساسية", "#كبير_وصغير", "#تعليم_الروضة", "#talesofwonder"]
    },
    {
        "topic_key": "counting-numbers-11-to-15",
        "pillar": "الأرقام والحساب (Numbers & Math)",
        "scene_name": "counting_numbers.jpg",
        "title_ar": "مُغَامَرَةُ الأَرْقَام: نَعُدُّ مِنْ 11 إِلَى 15 🚀✨",
        "script": (
            "رِحْلَتُنَا الحِسَابِيَّةُ تَصْعَدُ إِلَى الفَضَاءِ! "
            "بَعْدَ العَشَرَة: أَحَدَ عَشَر.. اِثْنَا عَشَر.. ثَلَاثَةَ عَشَر.. أَرْبَعَةَ عَشَر.. خَمْسَةَ عَشَر! "
            "خَمْسَةَ عَشَرَ نَجْمًا يَلْمَعُ فِي السَّمَاءِ بِمَعْلُومَاتِكُمْ الرَّائِعَة!"
        ),
        "lesson": "تطوير مهارات العد المتقدم للأطفال من 11 إلى 15 بطريقة مشجعة.",
        "tags": ["#shorts", "#أرقام_11_15", "#حساب_الأطفال", "#رياضيات_الروضة", "#talesofwonder"]
    },
    {
        "topic_key": "primary-colors-magic",
        "pillar": "الأشكال والألوان (Shapes & Colors)",
        "scene_name": "scene_art_colors.jpg",
        "title_ar": "سِحْرُ الأَلْوَانِ الأَسَاسِيَّةِ فِي حَيَاتِنَا 🎨🌈",
        "script": (
            "عَالَمُنَا مَلِيءٌ بِالأَلْوَانِ البَهِيَّة! "
            "الأَحْمَرُ مِثْلَ الفَرَاوْلَة! "
            "وَالأَزْرَقُ مِثْلَ مِيَاهِ البَحْرِ الهَادِئ! "
            "وَالأَصْفَرُ مِثْلَ نُورِ الشَّمْسِ الدَّافِئ! "
            "مَا هُوَ لَوْنُكُمْ المُفَضَّلُ يَا أَبْطَالَ الأَلْوَان؟"
        ),
        "lesson": "التعرف على الألوان الأساسية وتثبيتها من خلال ربطها بالطبيعة.",
        "tags": ["#shorts", "#الألوان_للأطفال", "#تعليم_الألوان", "#أنشطة_الروضة", "#talesofwonder"]
    },
    {
        "topic_key": "shapes-in-our-house",
        "pillar": "الأشكال والألوان (Shapes & Colors)",
        "scene_name": "routine_tidying_toys.jpg",
        "title_ar": "نَكْتَشِفُ الأَشْكَالَ دَاخِلَ بَيْتِنَا الجَمِيل 🏠🪟",
        "script": (
            "تَعَالَوْا نَسْتَكْشِفْ مَعًا غُرْفَتَنَا! "
            "السَّاعَةُ عَلَى الجِدَارِ دَائِرِيَّة! "
            "وَالطَّاوِلَةُ مُرَبَّعَة! "
            "وَالتِّلْفَازُ مُسْتَطِيلٌ لَامِع! "
            "كُلُّ شَيْءٍ حَوْلَنَا لَهُ شَكْلٌ هَنْدَسِيٌّ جَمِيل.. هَيَّا ابْحَثُوا عَنْ دَائِرَةٍ فِي غُرْفَتِكُمْ!"
        ),
        "lesson": "تطبيق مفاهيم الأشكال الهندسية في البيئة المنزلية للطفل.",
        "tags": ["#shorts", "#أشكال_المنزل", "#هندسة_مبسطة", "#تعليم_مبكر", "#talesofwonder"]
    },

    # ==========================================
    # المحور 4: العادات الصحية والنظام (Healthy Habits)
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
    },
    {
        "topic_key": "healthy-eating-vegetables",
        "pillar": "العادات الصحية والنظام (Healthy Habits)",
        "scene_name": "scene_fruits_kitchen.jpg",
        "title_ar": "طَبَقُ الصِّحَّة: الخُضَارُ وَالفَوَاكِهُ الطَّازَجَة 🥦🥕",
        "script": (
            "مَرْحَبًا يَا أَبْطَالَ القُوَّة! كَيْفَ نَصِيرُ أَقْوِيَاءَ وَنَشِيطِين؟ "
            "بِأَكْلِ الخُضَارِ اللَّذِيذَة كَالجَزَرِ وَالطَّمَاطِم، وَالفَوَاكِهِ الطَّازَجَة كَالتُّفَّاحِ وَالمَوْز! "
            "الطَّعَامُ الصِّحِّيُّ يَمْنَحُنَا طَاقَةً هَائِلَةً لِلَّعِبِ وَالتَّفَوُّقِ فِي الدِّرَاسَة!"
        ),
        "lesson": "تشجيع الطفل على تناول الخضار والفواكه لنمو صحي وسليم.",
        "tags": ["#shorts", "#الغذاء_الصحي", "#تغذية_الطفل", "#صحة_الأطفال", "#talesofwonder"]
    },
    {
        "topic_key": "early-sleep-energy",
        "pillar": "العادات الصحية والنظام (Healthy Habits)",
        "scene_name": "scene_bedtime_stars.jpg",
        "title_ar": "النَّوْمُ المُبَكِّرُ يَصْنَعُ أَبْطَالَ النَّشَاط 🌙⭐",
        "script": (
            "أَهْلًا يَا صِغَارِي! عِنْدَمَا تَغْرُبُ الشَّمْسُ وَيَأْتِي اللَّيْل، يَحِينُ وَقْتُ الرَّاحَة! "
            "نَنَامُ مُبَكِّرًا لِتَرْتَاحَ عُيُونُنَا وَتَنْمُو أَجْسَامُنَا بِصِحَّةٍ وَعَافِيَة! "
            "النَّوْمُ المُبَكِّرُ يَجْعَلُنَا نَسْتَيْقِظُ كَالنُّجُومِ المُشْرِقَةِ نَشَاطًا وَفَرَحًا!"
        ),
        "lesson": "أهمية النوم المبكر لنمو الدماغ والجسم بنشاط وحيوية.",
        "tags": ["#shorts", "#النوم_المبكر", "#عادات_صحية", "#أطفالنا", "#talesofwonder"]
    },
    {
        "topic_key": "drinking-water-vitality",
        "pillar": "العادات الصحية والنظام (Healthy Habits)",
        "scene_name": "scene_dining_bismillah.jpg",
        "title_ar": "المَاءُ سِرُّ الحَيَاةِ وَالانْتِعَاش 💧🥤",
        "script": (
            "مَرْحَبًا يَا أَبْطَال! جِسْمُنَا الذَّكِيُّ يَحْتَاجُ إِلَى المَاءِ لِيَبْقَى قَوِيًّا وَمُنْتَعِشًا! "
            "نَشْرَبُ المَاءَ النَّقِيَّ عِنْدَ العَطَش، وَخِلَالَ اللَّعِبِ وَالحَرَكَة! "
            "المَاءُ يَغْسِلُ أَجْسَامَنَا مِنَ التَّعَبِ وَيَجْعَلُ عُقُولَنَا حَادَّةً وَذَكِيَّة!"
        ),
        "lesson": "ترسيخ عادة شرب الماء بانتظام لطاقة وانتعاش دائم للطفل.",
        "tags": ["#shorts", "#شرب_الماء", "#صحة_الطفل", "#عادات_يومية", "#talesofwonder"]
    },
    {
        "topic_key": "morning-kids-exercise",
        "pillar": "العادات الصحية والنظام (Healthy Habits)",
        "scene_name": "scene_morning_exercise.jpg",
        "title_ar": "الرِّيَاضَةُ الصَّبَاحِيَّةُ لِأَجْسَامٍ قَوِيَّة 🏃‍♂️🤸‍♀️",
        "script": (
            "صَبَاحُ النَّشَاطِ يَا أَبْطَال! هَيَّا نَتَحَرَّكْ مَعًا! "
            "نَرْفَعُ أَيْدِيَنَا عَالِيًا نَحْوَ السَّمَاء، ثُمَّ نَلْمِسُ أَقْدَامَنَا، وَنَقْفِزُ ثَلَاثَ قَفَزَاتٍ مَرِحَة! "
            "الرِّيَاضَةُ كُلَّ صَبَاحٍ تَمْلأُ قُلُوبَنَا بِالفَرَحِ وَتَجْعَلُنَا أَقْوِيَاءَ كَالأَبْطَالِ الخَارِقِين!"
        ),
        "lesson": "الحركات الرياضية الصباحية الخفيفة تنشط الدورة الدموية وتعزز الحيوية.",
        "tags": ["#shorts", "#رياضة_الأطفال", "#نشاط_صباحي", "#صحة_ورشاقة", "#talesofwonder"]
    },
    {
        "topic_key": "hair-and-neatness",
        "pillar": "العادات الصحية والنظام (Healthy Habits)",
        "scene_name": "hygiene_brushing_teeth.jpg",
        "title_ar": "التَّمْشِيطُ وَالأَنَاقَةُ كُلَّ صَبَاح 💇‍♂️👕",
        "script": (
            "أَهْلًا يَا جَمِيلِينَ! بَعْدَ غَسْلِ الوَجْهِ بِالمَاءِ المُنْعِش، نَأْخُذُ المِشْطَ الجَمِيل! "
            "نُمَشِّطُ شُعُورَنَا بِلُطْف، وَنَرْتَدِي مَلَابِسَنَا النَّظِيفَةَ المُرَتَّبَة! "
            "النَّظَافَةُ وَالأَنَاقَةُ سِرُّ الجَمَالِ وَالبَهْجَة.. أَنْتُمْ دَوْمًا أَجْمَلُ أَبْطَال!"
        ),
        "lesson": "تعويد الطفل على العناية بمظهره وهندامه ونظافته الشخصية.",
        "tags": ["#shorts", "#النظافة_الشخصية", "#أناقة_الطفل", "#تربية_الروضة", "#talesofwonder"]
    }
]

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

def get_next_unique_curriculum_topic():
    """Retrieve next uncompleted curriculum topic with strict zero-repetition visual diversity guard."""
    history_data = load_json(TOPICS_FILE)
    existing_keys = {t.get("topic_key", t.get("title", "")).lower() for t in history_data.get("topics", [])}

    # Identify last used scene from history
    last_used_scene = None
    if history_data.get("topics"):
        for t in reversed(history_data["topics"]):
            if "scene_name" in t:
                last_used_scene = t["scene_name"]
                break

    selected_item = None
    for item in CURRICULUM_TOPICS:
        if item["topic_key"].lower() not in existing_keys:
            selected_item = dict(item)
            break

    # If all curated topics exhausted, dynamic AI-driven endless curriculum generator
    if not selected_item:
        print("🤖 Curated curriculum covered! Sourcing brand-new pedagogical topic via Gemini AI...", flush=True)
        api_key = get_gemini_api_key()
        pillars = [
            "الآداب والأخلاق الإسلامية والتربية الحسنة",
            "برنامج الروض واللغة العربية وحروف الهجاء",
            "الأرقام والحساب الممتع والرياضيات المبسطة",
            "الأشكال والألوان والذكاء البصري للأطفال",
            "العادات الصحية والنظام اليومي للأطفال"
        ]
        chosen_pillar = pillars[len(existing_keys) % len(pillars)]
        rot_idx = len(history_data.get("topics", [])) % len(ALL_AVAILABLE_SCENES)
        chosen_scene = ALL_AVAILABLE_SCENES[rot_idx]
        if chosen_scene == last_used_scene:
            chosen_scene = ALL_AVAILABLE_SCENES[(rot_idx + 1) % len(ALL_AVAILABLE_SCENES)]

        prompt = (
            f"أنت خبير تربوي ومؤلف محتوى أطفال لمرحلة الروضة والتعليم المبكر (3-10 سنوات) لقناة كرتون 3D هادفة.\n"
            f"المحور المطلوب: {chosen_pillar}\n"
            f"اكتب موضوع حلقة شورتس كرتونية جديدة ومبتكرة تماماً لا تشبه الحلقات السابقة.\n\n"
            f"المعايير:\n"
            f"1. العنوان: جذاب، مشوق للأطفال، يحتوي إيموجي، وبدون تشكيل معقد، أقل من 50 حرف.\n"
            f"2. النص الكرتوني (Script): قصة أو حوار مرح ومشجع يلقيه الراوي للطفل، بين 40 و 65 كلمة باللغة العربية الفصحى السلسة والمحببة للأطفال.\n"
            f"3. الدرس المستفاد (Lesson): جملة واحدة تلخص الفائدة التربوية أو الأخلاقية.\n"
            f"4. الكلمات الدلالية: 5 وسوم متعلقة بالموضوع.\n\n"
            f"أعد الإجابة بصيغة JSON حصراً:\n"
            f"{{\n"
            f'  "topic_key": "unique-slug-en",\n'
            f'  "title_ar": "العنوان المشوق باللغة العربية 🌟",\n'
            f'  "script": "النص الكرتوني الكامل هنا...",\n'
            f'  "lesson": "الدرس المستفاد هنا...",\n'
            f'  "tags": ["#shorts", "#تعليم_اطفال", "#كرتون", "#talesofwonder"]\n'
            f"}}"
        )

        candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        for model_name in candidate_models:
            try:
                client = genai.Client(api_key=api_key)
                resp = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                if resp and resp.text:
                    data = json.loads(resp.text)
                    if data.get("title_ar") and data.get("script"):
                        slug = data.get("topic_key", f"ai-topic-{int(datetime.datetime.now().timestamp())}")
                        selected_item = {
                            "topic_key": slug,
                            "pillar": chosen_pillar,
                            "scene_name": chosen_scene,
                            "title_ar": data["title_ar"],
                            "script": data["script"],
                            "lesson": data.get("lesson", "التعلم المستمر والأخلاق الحميدة ينيران عقول أبطالنا الصغار."),
                            "tags": data.get("tags", ["#shorts", "#أطفال", "#كرتون_تعليمي", "#talesofwonder"])
                        }
                        break
            except Exception as e:
                print(f"Gemini topic generation warning ({model_name}): {e}", flush=True)

        # Dynamic fail-safe curated cycle if offline/quota
        if not selected_item:
            cycle_idx = len(existing_keys) % len(CURRICULUM_TOPICS)
            base_item = dict(CURRICULUM_TOPICS[cycle_idx])
            cycle_num = (len(existing_keys) // len(CURRICULUM_TOPICS)) + 1
            base_item["topic_key"] = f"{base_item['topic_key']}-cycle-{cycle_num}"
            base_item["scene_name"] = chosen_scene
            selected_item = base_item

    # Strict Diversity Guard: if selected scene equals the previous video's scene, swap to alternate
    if last_used_scene and selected_item.get("scene_name") == last_used_scene:
        current_idx = ALL_AVAILABLE_SCENES.index(last_used_scene) if last_used_scene in ALL_AVAILABLE_SCENES else 0
        selected_item["scene_name"] = ALL_AVAILABLE_SCENES[(current_idx + 1) % len(ALL_AVAILABLE_SCENES)]
        print(f"🛡️ Diversity Guard: Swapped scene to {selected_item['scene_name']} to guarantee zero consecutive visual repetition!", flush=True)

    return selected_item, history_data

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

def assemble_video(
    image_path,
    audio_path,
    bgm_path,
    output_video_path,
    topic_title="حِكَايَاتُ العَجَائِب",
    script_text="",
    theme_palette=None,
    particles=None,
    camera_profile=None
):
    print(f"🎬 Rendering dynamic animated Shorts with script-driven cinematography & theme...", flush=True)
    engine = AnimationEngine(base_dir=BASE_DIR)
    return engine.render_animated_episode(
        scene_image_path=image_path,
        audio_path=audio_path,
        bgm_path=bgm_path,
        topic_title=topic_title,
        script_text=script_text,
        output_video_path=output_video_path,
        theme_palette=theme_palette,
        particles=particles,
        camera_profile=camera_profile
    )

def clean_arabic_text(text: str) -> str:
    """Removes excessive Arabic diacritics (tashkeel) and tatweel for search indexing."""
    if not text:
        return ""
    tashkeel_regex = re.compile(r'[\u0617-\u061A\u064B-\u0652]')
    cleaned = tashkeel_regex.sub('', text)
    cleaned = cleaned.replace('ـ', '')  # Remove tatweel
    return re.sub(r'\s+', ' ', cleaned).strip()

def build_optimized_seo_package(topic: dict) -> dict:
    """
    Builds maximum-CTR and high-ranking YouTube Shorts metadata:
    1. Short, Hook-focused Title ending with #shorts (strictly under 60-70 chars for mobile feed display)
    2. Rich keyword-dense Description starting with high-intent keywords + educational CTA + targeted hashtags
    3. 500-Character Master Tag Pool (Clean keywords without '#', mixing universal kids queries, pillar-specific Arabic queries, and English queries).
    """
    raw_title = topic.get("title_ar", "")
    clean_title = clean_arabic_text(raw_title)
    pillar = topic.get("pillar", "")
    lesson = topic.get("lesson", "")

    # 1. OPTIMIZED TITLE (Mobile Shorts Hook)
    base_title = clean_title.split("|")[0].strip()
    if "#shorts" not in base_title.lower():
        if len(base_title) > 52:
            base_title = base_title[:52].rstrip()
        optimized_title = f"{base_title} #shorts"
    else:
        optimized_title = base_title[:65]

    # 2. PILLAR MAPPING & TARGETED HASHTAGS
    pillar_lower = pillar.lower()
    key_lower = topic.get("topic_key", "").lower()

    pillar_tags = []
    pillar_hashtags = []

    if "أرقام" in pillar or "حساب" in pillar or "number" in key_lower or "count" in key_lower:
        pillar_tags = [
            "تعليم الارقام للاطفال", "تعلم العد للاطفال", "حساب الروضة",
            "ارقام الروضة", "رياضيات مبسطة للاطفال", "الارقام العربية",
            "learn numbers arabic", "arabic numbers for kids", "counting for toddlers"
        ]
        pillar_hashtags = ["#تعليم_الارقام", "#حساب_الاطفال", "#ارقام_الروضة", "#رياضيات_مبسطة"]
    elif "أشكال" in pillar or "ألوان" in pillar or "color" in key_lower or "shape" in key_lower:
        pillar_tags = [
            "تعليم الاشكال للاطفال", "تعلم الالوان للاطفال", "الاشكال الهندسية للاطفال",
            "الالوان الاساسية", "رسم وتلوين للاطفال", "الوان و اشكال الروضة",
            "learn shapes and colors", "arabic colors for kids", "shapes in arabic"
        ]
        pillar_hashtags = ["#تعليم_الالوان", "#الاشكال_للاطفال", "#رسم_وتلوين", "#اشكال_الروضة"]
    elif "حروف" in pillar or "عربية" in pillar or "alphabet" in key_lower or "letter" in key_lower:
        pillar_tags = [
            "تعليم الحروف للاطفال", "حروف الهجاء", "الحروف العربية للاطفال",
            "الف باء تاء", "لغتي الجميلة", "تعلم القراءة للاطفال",
            "انشودة الحروف", "arabic alphabet for kids", "learn arabic letters"
        ]
        pillar_hashtags = ["#حروف_الهجاء", "#تعليم_الحروف", "#لغتي_العربية", "#الحروف_الابجدية"]
    else:  # Manners / Morals / Healthy Habits
        pillar_tags = [
            "تربية الطفل", "اخلاق الطفل", "تعديل سلوك الاطفال",
            "اداب اسلامية للاطفال", "بر الوالدين للاطفال", "قصص هادفة للاطفال",
            "اخلاق حميدة", "احترام الكبير", "moral stories for kids", "good manners kids"
        ]
        pillar_hashtags = ["#تربية_الطفل", "#اخلاق_الاطفال", "#قصص_هادفة", "#آداب_الطفل"]

    # 3. MASTER BASE TAGS (Universal 500-Character Pool, NO '#')
    universal_tags = [
        "تعليم اطفال", "اطفال", "كرتون اطفال", "قصص اطفال", "حكايات اطفال",
        "رسوم متحركة", "تعليم الروضة", "اناشيد اطفال", "طيور الجنة", "سبيستون",
        "حكايات العجائب", "tales of wonder", "arabic for kids", "kids animation",
        "preschool learning", "arabic cartoon", "براعم"
    ]

    # Topic specific tags (clean from '#')
    topic_clean_tags = []
    for t in topic.get("tags", []):
        ct = clean_arabic_text(t).lstrip("#").strip()
        if ct and ct not in topic_clean_tags:
            topic_clean_tags.append(ct)

    # Combine & deduplicate tags up to 480 characters (YouTube allows max 500)
    final_tags = []
    total_tag_chars = 0
    all_candidates = pillar_tags + universal_tags + topic_clean_tags
    for tag in all_candidates:
        clean_tag = tag.strip()
        if clean_tag and clean_tag not in final_tags:
            if total_tag_chars + len(clean_tag) + 1 <= 480:
                final_tags.append(clean_tag)
                total_tag_chars += len(clean_tag) + 1

    # 4. RICH SEO DESCRIPTION
    universal_hashtags = ["#shorts", "#اطفال", "#كرتون_اطفال", "#رسوم_متحركة", "#حكايات_العجائب", "#kids", "#talesofwonder"]
    combined_hashtags = " ".join(universal_hashtags + pillar_hashtags[:3])

    description = (
        f"🌟 {base_title} | حكايات العجائب للأطفال\n\n"
        f"💡 موضوع اليوم: {base_title}\n"
        f"🎯 الهدف والدرس المستفاد: {lesson}\n\n"
        f"محتوى كرتوني وتربوي هادف للأطفال من 3 إلى 10 سنوات (الروضة والمستوى الأولي) لغرس القيم النبيلة وتعليم المهارات الأساسية بأسلوب كرتوني 3D ممتع وشيق.\n\n"
        f"🔔 اشتركوا في قناة حكايات العجائب (Tales of Wonder) ليصلكم كل يوم فيديو تعليمي وتربوي جديد ومفيد لأطفالكم!\n\n"
        f"{combined_hashtags}"
    )

    return {
        "title": optimized_title,
        "description": description,
        "tags": final_tags,
        "hashtags": combined_hashtags
    }


def check_algorithm_pacing_window(history_data, min_hours=5.0):
    """YouTube Shorts Algorithm Pacing Guard:
    1. Spacing: Wait 4 to 6 hours (default 5.0h) between uploads to avoid cannibalizing the Shorts shelf.
    2. Active Hours: Avoid publishing between 22:00 and 06:00 UTC (dead-of-night in the Arab world).
    3. Manual Override: Bypass guard if GITHUB_EVENT_NAME == 'workflow_dispatch' or --force is passed.
    """
    if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch" or "--force" in sys.argv or not os.environ.get("GITHUB_ACTIONS"):
        print("⚡ Manual trigger detected: Bypassing algorithm pacing guard.", flush=True)
        return True

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    current_hour_utc = now_utc.hour

    # Sleep hours in MENA region (22:00 UTC = 23:00 Morocco / 01:00 KSA to 06:00 UTC = 07:00 Morocco / 09:00 KSA)
    if current_hour_utc >= 22 or current_hour_utc < 6:
        print(f"🌙 [ALGORITHM GUARD] Night hours in target Arab audience (Current UTC: {now_utc.strftime('%H:%M')}).", flush=True)
        print("   Uploading during low-traffic night hours harms the initial 2-hour velocity in the Shorts shelf.", flush=True)
        print("   Skipping this cycle until morning preschool hours (07:00+ UTC).", flush=True)
        return False

    topics = history_data.get("topics", [])
    if not topics:
        return True

    # Find the most recent published topic with a valid video_url
    last_published = None
    for entry in reversed(topics):
        if entry.get("status") == "public_published" and entry.get("video_url"):
            last_published = entry
            break

    if not last_published:
        return True

    last_ts_str = last_published.get("published_at")
    if last_ts_str:
        try:
            last_dt = datetime.datetime.fromisoformat(last_ts_str)
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=datetime.timezone.utc)
            elapsed_hours = (now_utc - last_dt).total_seconds() / 3600.0
            if elapsed_hours < min_hours:
                print(f"⏳ [ALGORITHM GUARD] YouTube Shorts Spacing Window Active:", flush=True)
                print(f"   Last video '{last_published.get('title')}' was published {elapsed_hours:.1f} hours ago.", flush=True)
                print(f"   YouTube Shorts algorithm requires 4 to 6 hours between uploads to allow seed audience testing.", flush=True)
                print(f"   Next optimal upload window in ~{min_hours - elapsed_hours:.1f} hours. Skipping this cycle safely.", flush=True)
                return False
        except Exception as e:
            print(f"Notice parsing published_at: {e}", flush=True)
    else:
        # Fallback to date comparison if published_at is not present
        today_date = now_utc.date().isoformat()
        today_count = sum(1 for e in topics if e.get("date") == today_date and e.get("status") == "public_published")
        if today_count >= 3:
            print(f"🛑 [ALGORITHM GUARD] Already published {today_count} videos today ({today_date}).", flush=True)
            print("   Max 3-4 daily Shorts recommended for optimal channel authority. Skipping.", flush=True)
            return False

    return True

def execute_daily_run():

    topic, history_data = get_next_unique_curriculum_topic()

    # YouTube Shorts Algorithm Pacing Guard (Interval 4 to 6 hours, peak hours only)
    if not check_algorithm_pacing_window(history_data, min_hours=5.0):
        print("✅ Cycle gracefully finished without uploading. Channel momentum protected.")
        sys.exit(0)
    today_str = datetime.date.today().isoformat()
    ep_dir = OUTPUT_DIR / f"{today_str}_{topic['topic_key']}"
    ep_dir.mkdir(parents=True, exist_ok=True)

    audio_path = ep_dir / "voiceover.wav"
    video_path = ep_dir / "episode_shorts.mp4"
    scene_file = ep_dir / "scene_canvas.jpg"

    # Identify last used scene from history for strict diversity guard
    last_used_scene = None
    if history_data.get("topics"):
        for t in reversed(history_data["topics"]):
            if "scene_name" in t:
                last_used_scene = t["scene_name"]
                break

    # Step 1: Script Analysis & Visual/Animation Design (Intila9an men script -> image & animation)
    prompt_json = ep_dir / "scene_prompt.json"
    if prompt_json.exists():
        visual_spec = load_json(prompt_json)
        print("🎨 Loaded existing visual spec from cache.", flush=True)
    else:
        print("🎨 Art Director AI analyzing script to design custom 3D visual & animation...", flush=True)
        art_director = ArtDirectorAgent()
        visual_spec = art_director.analyze_script_and_design_visuals(
            script_text=topic["script"],
            title=topic["title_ar"],
            pillar=topic["pillar"]
        )
        print(f"🎬 Visual Description: {visual_spec.get('scene_description')}", flush=True)
        print(f"🎨 Theme: {visual_spec.get('theme_palette')} | Particles: {visual_spec.get('particle1')} {visual_spec.get('particle2')} | Cam Profile: #{visual_spec.get('camera_style')}", flush=True)

        # Save visual prompt and specification for full transparency & tracking
        with open(ep_dir / "scene_prompt.json", "w", encoding="utf-8") as pf:
            json.dump(visual_spec, pf, ensure_ascii=False, indent=2)
        with open(ep_dir / "scene_prompt.txt", "w", encoding="utf-8") as pf:
            pf.write(visual_spec.get("image_prompt", ""))

    # Step 2: Generate or Resolve Scene Image from script spec
    if not scene_file.exists():
        art_director = ArtDirectorAgent()
        scene_file = art_director.generate_or_resolve_scene_image(
            visual_spec=visual_spec,
            output_path=scene_file,
            last_used_scene=last_used_scene
        )
    else:
        print(f"🖼️ Scene canvas already generated: {scene_file}", flush=True)

    # Step 3: Storytelling Voiceover via Gemini 3.8 Flash TTS
    if not audio_path.exists():
        generate_voiceover(topic["script"], audio_path)
    else:
        print(f"🎙️ Voiceover already generated: {audio_path}", flush=True)

    # Step 4: Video Assembly with Dynamic Script-Driven Animation & Cinematography
    if not video_path.exists():
        assemble_video(
            image_path=scene_file,
            audio_path=audio_path,
            bgm_path=BGM_FILE,
            output_video_path=video_path,
            topic_title=topic["title_ar"],
            script_text=topic["script"],
            theme_palette=visual_spec.get("theme_palette"),
            particles=(visual_spec.get("particle1", "⭐"), visual_spec.get("particle2", "✨")),
            camera_profile=visual_spec.get("camera_style")
        )
    else:
        print(f"🎬 Video already assembled: {video_path}", flush=True)

    # Step 5: Upload to YouTube as PUBLIC with Advanced SEO
    seo_package = build_optimized_seo_package(topic)
    title = seo_package["title"]
    description = seo_package["description"]
    tags = seo_package["tags"]

    print(f"🎯 SEO Optimized Title: {title}", flush=True)
    print(f"🏷️ SEO Tags ({len(tags)} tags, {sum(len(t) for t in tags)} chars): {tags[:6]}...", flush=True)
    print(f"📝 Hashtags: {seo_package['hashtags']}", flush=True)

    upload_result = upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        privacy_status="public",  # Direct Public Publishing
        made_for_kids=False,
        thumbnail_path=str(scene_file)
    )

    # Step 5b: Multi-Platform Upload to TikTok
    tiktok_published = False
    try:
        from custom_tiktok_uploader import upload_episode_to_tiktok
        print("📱 [TIKTOK AUTOMATION] Publishing daily short episode to TikTok with viral algorithm captions...", flush=True)
        tiktok_published = upload_episode_to_tiktok(
            video_path=video_path,
            title=topic["title_ar"],
            lesson=topic["lesson"],
            topic_key=topic["topic_key"],
            headless=True
        )
        if tiktok_published:
            print(f"🎉 [TIKTOK AUTOMATION] Successfully published '{topic['title_ar']}' to TikTok!", flush=True)
        else:
            print(f"⚠️ [TIKTOK AUTOMATION] TikTok publish returned non-success flag.", flush=True)
    except Exception as tiktok_err:
        print(f"⚠️ [TIKTOK AUTOMATION] TikTok upload notice: {tiktok_err}", flush=True)

    # Step 6: Record history to prevent duplicates
    status_str = "public_published" if (upload_result and upload_result.get("video_url")) else (upload_result.get("status", "upload_pending") if upload_result else "upload_pending")
    new_entry = {
        "topic_key": topic["topic_key"],
        "date": today_str,
        "published_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "pillar": topic["pillar"],
        "title": topic["title_ar"],
        "seo_title": title,
        "lesson": topic["lesson"],
        "scene_name": visual_spec.get("best_matching_scene", topic.get("scene_name")),
        "scene_description": visual_spec.get("scene_description", ""),
        "video_url": upload_result.get("video_url") if upload_result else None,
        "tiktok_published": tiktok_published,
        "status": status_str
    }
    history_data.setdefault("topics", []).append(new_entry)
    save_json(TOPICS_FILE, history_data)

    print("\n" + "=" * 50)
    print("🎉 DAILY RUN FINISHED!")
    print(f"Pillar: {topic['pillar']}")
    print(f"Title: {topic['title_ar']}")
    if upload_result and upload_result.get("video_url"):
        print(f"Public URL: {upload_result['video_url']}")
    else:
        print(f"Status: {status_str} (Local video saved: {video_path})")
    print("=" * 50)
    return new_entry

def retry_pending_uploads():
    history_data = load_json(TOPICS_FILE)
    topics = history_data.get("topics", [])
    updated = False
    for entry in topics:
        if entry.get("status") in ["upload_limit_exceeded", "upload_pending", "upload_failed"]:
            print(f"🔄 Retrying upload for: {entry['title']} ({entry['topic_key']})...", flush=True)
            ep_dir = OUTPUT_DIR / f"{entry['date']}_{entry['topic_key']}"
            video_path = ep_dir / "episode_shorts.mp4"
            scene_file = ep_dir / "scene_canvas.jpg"
            if not video_path.exists():
                print(f"Video file missing at {video_path}, skipping.", flush=True)
                continue

            title = f"{entry['title']} | برنامج الروضة والأخلاق 🌟"
            description = (
                f"مرحباً بكم في حكايات العجائب (Tales of Wonder)! 🌟\n\n"
                f"المحور: {entry['pillar']}\n"
                f"💡 موضوع اليوم: {entry['title']}\n"
                f"🎯 الدرس المستفاد: {entry['lesson']}\n\n"
                f"محتوى تربوي وتأسيسي هادف للأطفال من 3 إلى 10 سنوات (الروضة والمستوى الأولي).\n\n"
                f"اشتركوا معنا ليتعلم أطفالكم كل يوم خلقاً جديداً ومعلومة مفيدة!\n\n"
                f"#shorts #تربية_الطفل #تعليم_مبكر #talesofwonder"
            )
            upload_result = upload_video(
                video_path=video_path,
                title=title,
                description=description,
                tags=["#shorts", "#أطفال", "#تعليم_الروضة", "#talesofwonder"],
                privacy_status="public",
                made_for_kids=True,
                thumbnail_path=str(scene_file) if scene_file.exists() else None
            )
            if upload_result and upload_result.get("video_url"):
                entry["video_url"] = upload_result["video_url"]
                entry["status"] = "public_published"
                updated = True
                print(f"🎉 Successfully published {entry['title']}: {upload_result['video_url']}")
            else:
                print(f"Upload could not complete: {upload_result.get('status') if upload_result else 'unknown'}")
                break

            if not entry.get("tiktok_published"):
                try:
                    from custom_tiktok_uploader import upload_episode_to_tiktok
                    print(f"📱 Uploading pending episode to TikTok: {entry['title']}...", flush=True)
                    if upload_episode_to_tiktok(video_path, entry["title"], entry.get("lesson", ""), entry["topic_key"], headless=True):
                        entry["tiktok_published"] = True
                        updated = True
                        print(f"🎉 Successfully published {entry['title']} to TikTok!")
                except Exception as t_err:
                    print(f"Notice on TikTok retry: {t_err}")
    if updated:
        save_json(TOPICS_FILE, history_data)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--retry-pending":
        retry_pending_uploads()
    else:
        execute_daily_run()

