"""Batch Publisher for the Last 10 Shorts on TikTok.
Uploads sequentially with safe pacing and viral algorithm captions.
"""

import os
import sys
import json
import time
import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "tiktok_upload_history.json"

sys.path.insert(0, str(BASE_DIR / "scripts"))
from custom_tiktok_uploader import upload_to_tiktok

LAST_10_KEYS = [
    "2026-10-17_arabic-letters-raa-zay",
    "2026-10-17_arabic-letters-saad-daad",
    "2026-10-17_arabic-letters-seen-sheen",
    "2026-10-17_arabic-letters-taa-zaa",
    "2026-10-17_counting-numbers-1-to-5",
    "2026-10-17_counting-numbers-6-to-10",
    "2026-10-17_fun-addition-fruits",
    "2026-10-17_geometric-shapes-colors",
    "2026-10-18_big-and-small-sizes",
    "2026-10-25_counting-numbers-11-to-15"
]

TITLES_MAP = {
    "2026-10-17_arabic-letters-raa-zay": ("أنشودة الحروف: الراء والزاي 🌟", "نطق وتمييز حرفي الراء والزاي بطريقة كرتونية مرحة"),
    "2026-10-17_arabic-letters-saad-daad": ("أنشودة الحروف: الصاد والضاد 🌟", "تعليم الطفل مخارج الحروف الفخمة بطريقة سهلة وممتعة"),
    "2026-10-17_arabic-letters-seen-sheen": ("أنشودة الحروف: السين والشين 🌟", "التمييز بين السين والشين مع أصوات الحيوانات والكلمات"),
    "2026-10-17_arabic-letters-taa-zaa": ("أنشودة الحروف: الطاء والظاء 🌟", "تدريب لغوي وتأسيسي ممتع للأطفال فـ مرحلة الروضة"),
    "2026-10-17_counting-numbers-1-to-5": ("عد الأرقام الممتع من 1 إلى 5 🔢", "تأسيس الحساب البصري للأطفال بالعد المرح مع ليو"),
    "2026-10-17_counting-numbers-6-to-10": ("عد الأرقام الذكي من 6 إلى 10 🔢", "تكملة سلسلة الأعداد وتنمية مهارات التفكير السريع"),
    "2026-10-17_fun-addition-fruits": ("الجمع الممتع بالفواكه اللذيذة 🍎🍌", "أسهل طريقة لتعليم الطفل الجمع البسيط بالمجسمات"),
    "2026-10-17_geometric-shapes-colors": ("الأشكال الهندسية والألوان الزاهية 🎨", "التعرف على الدائرة، المربع، والمثلث مع ألوان مبهجة"),
    "2026-10-18_big-and-small-sizes": ("الأحجام: الكبير والصغير 🐘🐭", "مقارنة الأحجام والأبعاد بطريقة كرتونية مسلية"),
    "2026-10-25_counting-numbers-11-to-15": ("عد الأرقام الكبيرة من 11 إلى 15 🚀", "خطوة متقدمة وممتعة فـ تعلم الأرقام للأطفال الصغار")
}

VIRAL_TAGS = "#fyp #foryou #تربية_الأطفال #أمهات_تيك_توك #قصص_اطفال #تعليم_مبكر #talesofwonder"

def build_caption(key):
    title, lesson = TITLES_MAP.get(key, ("حكايات العجائب", "محتوى تربوي هادف"))
    
    if "الحروف" in title or "letters" in key:
        hook = "🎨 أسهل وأمتع طريقة يتعلم بها طفلك الحروف العربية! 🌟👇"
        cta_q = "👇 شكون طفلها كيتعلم الحروف دابا؟ كتبو لينا سميتو نشجعوه!"
    elif "الأرقام" in title or "الجمع" in title or "الأشكال" in title or "الأحجام" in title:
        hook = "💡 كيفاش تحبب الرياضيات والحساب لطفلك فـ دقيقة واحدة؟ 🔢👇"
        cta_q = "👇 واش كتعجب طفلك مادة الحساب؟ شاركونا تجربتكم فـ التعاليق!"
    else:
        hook = "✨ سر تربوي بسيط كيبني شخصية طفلك بالحب والمرح! 🦁👇"
        cta_q = "👇 شنو أكتر مهارة كتبغيو وليداتكم يتعلموها؟"

    caption = (
        f"{hook}\n\n"
        f"📖 {title}\n"
        f"🎯 {lesson}\n\n"
        f"💾 احفظي الفيديو عندك (Save) باش ترجعي ليه مع طفلك!\n"
        f"{cta_q}\n\n"
        f"{VIRAL_TAGS}"
    )
    return caption

def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"uploaded_keys": []}
    return {"uploaded_keys": []}

def save_history(hist):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=2, ensure_ascii=False)

def run_batch_upload(delay_seconds=60):
    hist = load_history()
    uploaded = set(item.get("key") for item in hist.get("uploaded_keys", []))
    
    pending = [k for k in LAST_10_KEYS if k not in uploaded]
    print(f"📊 Total in Last 10: {len(LAST_10_KEYS)} | Already uploaded: {len(uploaded)} | Pending: {len(pending)}")
    
    for idx, key in enumerate(pending, 1):
        video_path = OUTPUT_DIR / key / "episode_shorts.mp4"
        if not video_path.exists():
            print(f"⚠️ Video not found for {key}, skipping.")
            continue
            
        title, _ = TITLES_MAP.get(key, (key, ""))
        print("\n" + "=" * 60)
        print(f"[{idx}/{len(pending)}] 🚀 Uploading: {title} ({key})")
        print("=" * 60)
        
        caption = build_caption(key)
        
        try:
            success = upload_to_tiktok(str(video_path), caption, headless=True)
            if success:
                print(f"🎉 SUCCESS! Published {title} to TikTok.")
                hist["uploaded_keys"].append({
                    "key": key,
                    "title": title,
                    "published_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                })
                save_history(hist)
            else:
                print(f"❌ Failed to publish {title}.")
        except Exception as e:
            print(f"❌ Error uploading {key}: {e}")
            
        if idx < len(pending):
            print(f"⏳ Waiting {delay_seconds} seconds before uploading next video to stay safe with TikTok algorithm...", flush=True)
            time.sleep(delay_seconds)
            
    print("\n🏁 All requested shorts processed!")

if __name__ == "__main__":
    delay = 60
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        delay = int(sys.argv[1])
    run_batch_upload(delay_seconds=delay)
