"""TikTok Viral Publishing Engine for Tales of Wonder.
Optimized for the TikTok FYP algorithm with high-retention hooks,
engagement CTAs (Saves & Comments), and targeted family/parenting hashtags.
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

try:
    from tiktok_uploader.upload import upload_video
except ImportError:
    upload_video = None

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
CREDENTIALS_DIR = BASE_DIR / "credentials"

SESSION_FILE = CREDENTIALS_DIR / "tiktok_session.json"
HISTORY_FILE = DATA_DIR / "tiktok_upload_history.json"

VIRAL_HASHTAGS = [
    "#fyp",
    "#foryou",
    "#تربية_الأطفال",
    "#أمهات_تيك_توك",
    "#قصص_اطفال",
    "#talesofwonder"
]

def get_cookies_list():
    """Build full cookie list from saved session."""
    session_id = "6d76ae87430222055bfa6a17432c3dfd"
    s_v_web_id = "verify_mvn2dghp_xqrslwRC_S2KL_4o68_Ahs2_zpvtBXOuBfgu"
    odin_tt = "05afa2a9ad6ff5bd77c6242615b72e532245b85986c5790e8b5f49baf470"
    csrf = "cb1ba1fe16f96c1db9fd63c7797e9e31"
    
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                session_id = data.get("sessionid", session_id)
                s_v_web_id = data.get("s_v_web_id", s_v_web_id)
                odin_tt = data.get("odin_tt", odin_tt)
                csrf = data.get("passport_csrf_token", csrf)
        except Exception:
            pass
            
    cookies = [
        {"name": "sessionid", "value": session_id, "domain": ".tiktok.com", "path": "/"},
        {"name": "sessionid_ss", "value": session_id, "domain": ".tiktok.com", "path": "/"},
        {"name": "s_v_web_id", "value": s_v_web_id, "domain": ".tiktok.com", "path": "/"},
        {"name": "odin_tt", "value": odin_tt, "domain": ".tiktok.com", "path": "/"},
        {"name": "passport_csrf_token", "value": csrf, "domain": ".tiktok.com", "path": "/"}
    ]
    return session_id, cookies

def load_upload_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"uploaded_keys": []}
    return {"uploaded_keys": []}

def save_upload_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def get_topic_hashtags(title, lesson):
    """
    Generate highly targeted, high-traffic Explore/FYP hashtags tailored to the video's theme.
    Uses high-volume searchable tags (no Hamza on Alif for maximum search matches) + regional affinity tag.
    """
    t_lower = (title + " " + lesson).lower()
    
    if any(k in t_lower for k in ["حروف", "روضة", "هجاء", "ألف", "باء", "تاء", "letters", "alphabet"]):
        return [
            "#تعليم_الاطفال",
            "#حروف_الهجاء",
            "#اطفال_ومواهب",
            "#قصص_اطفال",
            "#امهات_تيك_توك",
            "#learnarabic",
            "#المغرب"
        ]
    elif any(k in t_lower for k in ["أرقام", "ارقام", "حساب", "عد", "جمع", "numbers", "counting", "math"]):
        return [
            "#تعليم_الاطفال",
            "#رياضيات_اطفال",
            "#حساب_ذهني",
            "#اطفال_ومواهب",
            "#قصص_اطفال",
            "#تأسيس_اطفال",
            "#المغرب"
        ]
    elif any(k in t_lower for k in ["أشكال", "اشكال", "ألوان", "الوان", "أحجام", "احجام", "shapes", "colors"]):
        return [
            "#تعليم_الاطفال",
            "#الوان_واشكال",
            "#تأسيس_اطفال",
            "#اطفال_ومواهب",
            "#كرتون_اطفال",
            "#امهات_تيك_توك",
            "#المغرب"
        ]
    elif any(k in t_lower for k in ["أدب", "أخلاق", "اخلاق", "اعتذار", "والدين", "صدق", "نظافة", "اسنان", "polite", "respect"]):
        return [
            "#تربية_الاطفال",
            "#قصص_اطفال",
            "#كرتون_اطفال",
            "#تعديل_سلوك",
            "#اطفال_ومواهب",
            "#امهات_تيك_توك",
            "#المغرب"
        ]
    else:
        return [
            "#تعليم_الاطفال",
            "#قصص_اطفال",
            "#كرتون_اطفال",
            "#اطفال_ومواهب",
            "#امهات_تيك_توك",
            "#learnarabic",
            "#المغرب"
        ]

def build_viral_caption(title, lesson):
    """
    Construct a high-retention, high-engagement TikTok viral caption.
    1. Hook for parents (Lines 1-2)
    2. Moral Lesson summary
    3. CTA for Saves & Comments (TikTok's #1 ranking signals)
    4. Strategic Explore tag cluster
    """
    t_lower = (title + " " + lesson).lower()
    if any(k in t_lower for k in ["أدب", "أخلاق", "اعتذار", "والدين", "polite", "respect", "sharing", "sorry"]):
        hook = "✨ سر تربوي بسيط كيعلم طفلك الأدب بلا صراخ! 🦁👇"
        cta_q = "👇 شاركونا فـ التعاليق: واش وليداتكم كيستعملو هاد الكلمات؟"
    elif any(k in t_lower for k in ["نظافة", "أسنان", "اسنان", "brush", "teeth"]):
        hook = "🪥 أسهل حيلة تخلي طفلك يحب غسيل الأسنان بلا عناد! ✨👇"
        cta_q = "👇 واش طفلك كيعكز على غسيل أسنانه؟ شاركونا تجربتكم!"
    elif any(k in t_lower for k in ["حروف", "روضة", "لغة", "letters", "arabic"]):
        hook = "🎨 أسهل وأمتع طريقة يتعلم بها طفلك الحروف العربية! 🌟👇"
        cta_q = "👇 شكون طفلها كيتعلم الحروف دابا؟ كتبو لينا سميتو نشجعوه!"
    elif any(k in t_lower for k in ["أرقام", "ارقام", "حساب", "أشكال", "counting", "numbers"]):
        hook = "💡 كيفاش تحبب الرياضيات والأرقام لطفلك فـ دقيقة واحدة؟ 🔢👇"
        cta_q = "👇 واش كتعجب طفلك مادة الحساب؟ شاركونا تجربتكم فـ التعاليق!"
    else:
        hook = "🌟 قصة كرتونية هادفة تبني شخصية طفلك بالحب والمرح! 👧👦👇"
        cta_q = "👇 شنو أكتر صفة كتبغيو وليداتكم يتعلموها؟"

    tags = get_topic_hashtags(title, lesson)
    caption = (
        f"{hook}\n\n"
        f"📖 {title}\n"
        f"🎯 {lesson}\n\n"
        f"💾 احفظي الفيديو عندك (Save) باش ترجعي ليه مع طفلك!\n"
        f"{cta_q}\n\n"
        f"{' '.join(tags)}"
    )
    return caption

def find_available_episodes():
    """Find all rendered episodes in output/ and match with topic metadata."""
    episodes = []
    if not OUTPUT_DIR.exists():
        return episodes
        
    for ep_folder in sorted(OUTPUT_DIR.iterdir()):
        if not ep_folder.is_dir():
            continue
        video_file = ep_folder / "episode_shorts.mp4"
        if not video_file.exists():
            continue
            
        topic_key = ep_folder.name
        title = topic_key.replace("2026-", "").replace("2025-", "").replace("_", " ").title()
        lesson = "تعلم الأدب والقيم النبيلة مع حكايات العجائب"
        
        # Specific high-quality titles mapping for best SEO
        if "polite-words-magic" in topic_key:
            title = "كلمات الأدب السحرية (شكراً، من فضلك، لو سمحت)"
            lesson = "تعليم الأطفال التحدث بلباقة وأدب مع الكبار والأصدقاء"
        elif "respecting-parents" in topic_key:
            title = "بر الوالدين وطاعة الأم والأب"
            lesson = "تعليم الطفل سماع كلام الوالدين ومساعدتهم بمحبة"
        elif "saying-sorry-honesty" in topic_key:
            title = "فضيلة الصدق وشجاعة الاعتذار عند الخطأ"
            lesson = "الشجاعة في قول الحقيقة والاعتذار بدون خوف"
        elif "sharing-is-caring" in topic_key:
            title = "متعة المشاركة مع الأصدقاء والإخوة"
            lesson = "المشاركة تزيد المحبة وتجعل اللعب أجمل"
        elif "arabic-letters-alif-baa" in topic_key:
            title = "أنشودة الحروف الهجائية: الألف والباء"
            lesson = "نطق وكتابة حرفي الألف والباء بأمثلة كرتونية مرحة"
        elif "arabic-letters-taa-thaa" in topic_key:
            title = "أنشودة الحروف: التاء والثاء"
            lesson = "التمييز بين التاء والثاء بالنطق الصحيح"
        elif "counting-numbers-1-to-5" in topic_key:
            title = "عد الأرقام الممتع من 1 إلى 5 للأطفال"
            lesson = "تأسيس الحساب والأعداد بطريقة بصرية سهلة"
        elif "kindness-to-animals" in topic_key:
            title = "الرفق بالحيوان والرحمة بالكائنات"
            lesson = "تعليم الرحمة وإطعام الحيوانات الضعيفة"
        elif "patience-and-calm" in topic_key:
            title = "الصبر والهدوء عند الغضب"
            lesson = "كيف يتحكم الطفل في غضبه ويتنفس بهدوء"
            
        episodes.append({
            "key": topic_key,
            "title": title,
            "lesson": lesson,
            "video_path": video_file,
            "size_mb": video_file.stat().st_size / (1024 * 1024)
        })
        
    return episodes

def upload_episode_to_tiktok(ep, headless=True):
    """Upload a single episode using the viral engine."""
    session_id, cookies_list = get_cookies_list()
    caption = build_viral_caption(ep["title"], ep["lesson"])
    video_path = str(ep["video_path"])
    
    print("=" * 60, flush=True)
    print(f"🚀 TIKTOK VIRAL UPLOAD: {ep['title']}", flush=True)
    print(f"📁 Video: {video_path} ({ep['size_mb']:.2f} MB)", flush=True)
    print(f"📝 Caption length: {len(caption)} chars", flush=True)
    print(f"🔥 Viral Hook: {caption.splitlines()[0]}", flush=True)
    print("=" * 60, flush=True)
    
    try:
        print("🌐 Launching Chromium browser to publish to TikTok...", flush=True)
        failed_videos = upload_video(
            filename=video_path,
            description=caption,
            sessionid=session_id,
            cookies_list=cookies_list,
            browser="chromium",
            headless=headless,
            visibility="everyone"
        )
        
        if not failed_videos:
            print("✅ Upload Completed! Successfully posted to TikTok! 🎉", flush=True)
            history = load_upload_history()
            history["uploaded_keys"].append({
                "key": ep["key"],
                "title": ep["title"],
                "published_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "status": "published"
            })
            save_upload_history(history)
            return True
        else:
            print(f"⚠️ Failed videos reported: {failed_videos}", flush=True)
            return False
    except Exception as e:
        print(f"❌ Upload exception: {e}", flush=True)
        return False

if __name__ == "__main__":
    episodes = find_available_episodes()
    print(f"Found {len(episodes)} total episodes on disk.")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test-one":
        if episodes:
            target = episodes[0]
            print(f"Targeting test episode: {target['title']} ({target['key']})")
            upload_episode_to_tiktok(target, headless=True)
        else:
            print("No episodes found in output/")
    elif len(sys.argv) > 1 and sys.argv[1] == "--list":
        for idx, ep in enumerate(episodes, 1):
            print(f"{idx}. {ep['title']} ({ep['key']}) - {ep['size_mb']:.2f} MB")
    else:
        print("Usage:")
        print("  python scripts/tiktok_viral_engine.py --list")
        print("  python scripts/tiktok_viral_engine.py --test-one")
