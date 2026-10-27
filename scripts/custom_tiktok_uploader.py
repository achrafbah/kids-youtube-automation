"""Direct Playwright TikTok Studio Uploader for Tales of Wonder.
Handles modern TikTok Studio (/tiktokstudio/upload):
- Injects authenticated session cookies.
- Uploads vertical MP4 short.
- Cleans Joyride onboarding tooltips & overlays.
- Inserts viral Arabic caption, hook, and tags.
- Targets real publish button (button[data-e2e='post_video_button']).
- Confirms "Continue to post?" dialog by clicking "Post now".
- Verifies post completion and redirection to /tiktokstudio/content.
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

from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_DIR = BASE_DIR / "credentials"
SESSION_FILE = CREDENTIALS_DIR / "tiktok_session.json"

def get_session_cookies():
    session_id = "6d76ae87430222055bfa6a17432c3dfd"
    s_v_web_id = "verify_mvn2dghp_xqrslwRC_S2KL_4o68_Ahs2_zpvtBXOuBfgu"
    odin_tt = "05afa2a9ad6ff5bd77c6242615b72e532245b85986c5790e8b5f49baf470"
    csrf = "cb1ba1fe16f96c1db9fd63c7797e9e31"
    
    # 1. Check environment variable first (e.g. in GitHub Actions)
    env_session = os.environ.get("TIKTOK_SESSION_JSON")
    if env_session:
        try:
            data = json.loads(env_session)
            session_id = data.get("sessionid", session_id)
            s_v_web_id = data.get("s_v_web_id", s_v_web_id)
            odin_tt = data.get("odin_tt", odin_tt)
            csrf = data.get("passport_csrf_token", csrf)
        except Exception:
            pass
    elif SESSION_FILE.exists():
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
    return cookies

def upload_to_tiktok(video_path, caption, headless=True):
    video_path = os.path.abspath(video_path)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
        
    print(f"\n🎬 Starting TikTok upload: {os.path.basename(video_path)}")
    print(f"👁️ Browser Mode: {'Headless' if headless else 'Visible'}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        context.add_cookies(get_session_cookies())
        
        page = context.new_page()
        
        print("🌐 Navigating to TikTok Studio upload page...", flush=True)
        page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        
        def clean_overlays():
            # Dismiss Got it / Turn on / info modals
            for sel in ["button:has-text('Got it')", "div[role='dialog'] button:has-text('Turn on')", "button:has-text('Dismiss')", "button:has-text('Not now')"]:
                try:
                    elem = page.locator(sel).first
                    if elem.count() > 0 and elem.is_visible():
                        elem.click()
                        time.sleep(0.3)
                except Exception:
                    pass
            # Remove joyride walkthrough overlay
            try:
                page.evaluate("""
                    const joyride = document.getElementById('react-joyride-portal');
                    if (joyride) joyride.remove();
                    document.querySelectorAll('.react-joyride__overlay, .react-joyride__spotlight, [data-test-id="overlay"]').forEach(e => e.remove());
                """)
            except Exception:
                pass

        clean_overlays()
        
        print("📁 Selecting video file for upload...", flush=True)
        file_input = page.locator("input[type='file']").first
        file_input.set_input_files(video_path)
        print("⏳ Video file selected, waiting for form ready...", flush=True)
        
        # Wait until caption editor appears
        editor = page.locator("div[contenteditable='true']").first
        for _ in range(20):
            clean_overlays()
            time.sleep(1)
            if editor.count() > 0 and editor.is_visible():
                break
                
        print("✍️ Setting caption and hashtags...", flush=True)
        clean_overlays()
        editor.click(force=True)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.3)
        
        # 1. Native synthetic paste event for Draft.js / Lexical
        page.evaluate("""(text) => {
            const el = document.querySelector("div[contenteditable='true']");
            if (!el) return;
            el.focus();
            const dt = new DataTransfer();
            dt.setData('text/plain', text);
            const evt = new ClipboardEvent('paste', { bubbles: true, cancelable: true, clipboardData: dt });
            el.dispatchEvent(evt);
        }""", caption)
        time.sleep(1)

        # 2. Verify text inside editor, fallback to page.keyboard.insert_text if empty
        val = editor.inner_text().strip()
        if len(val) < 5:
            editor.click(force=True)
            page.keyboard.insert_text(caption)
            time.sleep(1)
            
        print("✅ Caption entered!", flush=True)
        clean_overlays()
        time.sleep(2)
        
        # Locate real post button
        post_btn = page.locator("button[data-e2e='post_video_button']")
        post_btn.wait_for(state="visible", timeout=30000)
        
        # Wait for button to be ready (enabled & not loading)
        print("⏳ Waiting for Post button to be active...", flush=True)
        for i in range(30):
            clean_overlays()
            aria_disabled = post_btn.get_attribute("aria-disabled")
            data_loading = post_btn.get_attribute("data-loading")
            if post_btn.is_enabled() and aria_disabled != "true" and data_loading != "true":
                break
            time.sleep(1)
            
        clean_overlays()
        post_btn.scroll_into_view_if_needed()
        time.sleep(1)
        print("🚀 Clicking initial Post button...", flush=True)
        post_btn.click()
        time.sleep(2)
        
        # Check for "Continue to post?" modal (Content check in progress dialog)
        try:
            post_now_btn = page.locator("button:has-text('Post now')").first
            if post_now_btn.is_visible(timeout=5000):
                print("🎯 Confirmation modal detected! Clicking 'Post now'...", flush=True)
                post_now_btn.click()
                print("✅ Clicked 'Post now'!", flush=True)
        except Exception:
            pass
            
        # Wait for publication confirmation / redirect to content list
        print("⏳ Waiting for publication to finalize...", flush=True)
        published = False
        for _ in range(30):
            time.sleep(1)
            if "tiktokstudio/content" in page.url:
                print("🎉 Page redirected to TikTok Studio Content list!")
                published = True
                break
            body_text = page.locator("body").inner_text()
            if any(s.lower() in body_text.lower() for s in ["manage your posts", "your video has been uploaded", "your video is being uploaded"]):
                print("🎉 Success signal detected in page content!")
                published = True
                break
                
        if not published:
            # Check if modal closed or content page reached
            if "tiktokstudio/upload" not in page.url:
                published = True
                
        time.sleep(2)
        browser.close()
        return published

from tiktok_viral_engine import get_topic_hashtags

def build_tiktok_viral_caption(title, lesson, topic_key=""):
    """Build high-retention viral caption adapted to the TikTok FYP algorithm with targeted explore tags."""
    combined = (title + " " + lesson + " " + topic_key).lower()
    
    if any(k in combined for k in ["أدب", "أخلاق", "اعتذار", "polite", "respect", "sharing", "sorry", "والدين", "صدق"]):
        hook = "✨ سر تربوي بسيط كيعلم طفلك الأدب بلا صراخ! 🦁👇"
        cta_q = "👇 شاركونا فـ التعاليق: واش وليداتكم كيستعملو هاد الكلمات؟"
    elif any(k in combined for k in ["نظافة", "أسنان", "اسنان", "brush", "teeth"]):
        hook = "🪥 أسهل حيلة تخلي طفلك يحب غسيل الأسنان بلا عناد! ✨👇"
        cta_q = "👇 واش طفلك كيعكز على غسيل أسنانه؟ شاركونا تجربتكم!"
    elif any(k in combined for k in ["حروف", "روضة", "لغة", "letters", "arabic", "نطق", "هجائية"]):
        hook = "🎨 أسهل وأمتع طريقة يتعلم بها طفلك الحروف العربية! 🌟👇"
        cta_q = "👇 شكون طفلها كيتعلم الحروف دابا؟ كتبو لينا سميتو نشجعوه!"
    elif any(k in combined for k in ["أرقام", "ارقام", "حساب", "أشكال", "counting", "numbers", "جمع", "أحجام", "رياضيات"]):
        hook = "💡 كيفاش تحبب الرياضيات والحساب لطفلك فـ دقيقة واحدة؟ 🔢👇"
        cta_q = "👇 واش كتعجب طفلك مادة الحساب؟ شاركونا تجربتكم فـ التعاليق!"
    else:
        hook = "🌟 قصة كرتونية هادفة تبني شخصية طفلك بالحب والمرح! 👧👦👇"
        cta_q = "👇 شنو أكتر مهارة كتبغيو وليداتكم يتعلموها؟"

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

def upload_episode_to_tiktok(video_path, title, lesson, topic_key="", headless=True):
    """Publish a daily episode to TikTok with viral captions and history tracking."""
    caption = build_tiktok_viral_caption(title, lesson, topic_key)
    success = upload_to_tiktok(video_path, caption, headless=headless)
    
    if success:
        try:
            hist_file = BASE_DIR / "data" / "tiktok_upload_history.json"
            hist = {"uploaded_keys": []}
            if hist_file.exists():
                with open(hist_file, "r", encoding="utf-8") as f:
                    hist = json.load(f)
            
            clean_key = topic_key or Path(video_path).parent.name
            # Check if not already in history
            existing_keys = {item.get("key") for item in hist.get("uploaded_keys", [])}
            if clean_key not in existing_keys:
                hist.setdefault("uploaded_keys", []).append({
                    "key": clean_key,
                    "title": title,
                    "published_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "status": "published"
                })
                with open(hist_file, "w", encoding="utf-8") as f:
                    json.dump(hist, f, indent=2, ensure_ascii=False)
                print(f"📝 Recorded {clean_key} to tiktok_upload_history.json", flush=True)
        except Exception as e:
            print(f"Notice saving tiktok history: {e}", flush=True)
            
    return success

if __name__ == "__main__":
    video_arg = r"C:\Users\SetupGame\.gemini\antigravity\scratch\kids-youtube-automation\output\2026-10-17_arabic-letters-saad-daad\episode_shorts.mp4"
    sample_caption = (
        "🎨 أسهل وأمتع طريقة يتعلم بها طفلك الحروف العربية! 🌟👇\n\n"
        "📖 أنشودة الحروف: الصاد والضاد 🌟\n"
        "🎯 تعليم الطفل مخارج الحروف الفخمة بطريقة سهلة وممتعة\n\n"
        "💾 احفظي الفيديو عندك (Save) باش ترجعي ليه مع طفلك!\n"
        "👇 شكون طفلها كيتعلم الحروف دابا؟ كتبو لينا سميتو نشجعوه!\n\n"
        "#fyp #foryou #تربية_الأطفال #أمهات_تيك_توك #قصص_اطفال #تعليم_مبكر #talesofwonder"
    )
    res = upload_to_tiktok(video_arg, sample_caption, headless=True)
    print("Upload result:", res)
