"""Platform-Optimized Algorithm Scheduler for Tales of Wonder.
Defines peak engagement windows, spacing intervals, and daily volume
custom-tailored for YouTube Shorts and TikTok algorithms in the MENA/Arab world.
"""

import os
import sys
import json
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
DATA_DIR = BASE_DIR / "data"
TOPICS_FILE = DATA_DIR / "topics_history.json"
TIKTOK_HISTORY_FILE = DATA_DIR / "tiktok_upload_history.json"

# =====================================================================
# YOUTUBE SHORTS ALGORITHM CONFIGURATION
# Rule: Seed Audience Test takes 3-5h. Never flood the Shorts shelf.
# Daily Limit: 2 videos / day
# Minimum Spacing: 5.0 hours
# Peak Audience Slots (UTC):
#   Slot 1: 12:00 - 15:30 UTC  (13:00 - 16:30 Morocco / 15:00 - 18:30 Gulf)
#   Slot 2: 17:30 - 21:00 UTC  (18:30 - 22:00 Morocco / 20:30 - 00:00 Gulf)
# =====================================================================
YT_MAX_DAILY = 2
YT_MIN_SPACING_HOURS = 5.0
YT_PEAK_WINDOWS_UTC = [
    (12, 0, 15, 30),  # Slot 1
    (17, 30, 21, 0)   # Slot 2
]

# =====================================================================
# TIKTOK ALGORITHM CONFIGURATION
# Rule: High-velocity FYP feed. Freshness & consistency wins.
# Daily Limit: 3 videos / day
# Minimum Spacing: 3.0 hours
# Peak Audience Slots (UTC):
#   Slot 1: 07:00 - 09:30 UTC  (08:00 - 10:30 Morocco / 10:00 - 12:30 Gulf)
#   Slot 2: 12:00 - 14:30 UTC  (13:00 - 15:30 Morocco / 15:00 - 17:30 Gulf)
#   Slot 3: 19:00 - 22:00 UTC  (20:00 - 23:00 Morocco / 22:00 - 01:00 Gulf)
# =====================================================================
TIKTOK_MAX_DAILY = 3
TIKTOK_MIN_SPACING_HOURS = 3.0
TIKTOK_PEAK_WINDOWS_UTC = [
    (7, 0, 9, 30),    # Slot 1
    (12, 0, 14, 30),  # Slot 2
    (19, 0, 22, 0)    # Slot 3
]

def is_time_in_windows(dt_utc, windows):
    """Check if current UTC time falls into any of the configured peak windows."""
    cur_mins = dt_utc.hour * 60 + dt_utc.minute
    for (sh, sm, eh, em) in windows:
        start_mins = sh * 60 + sm
        end_mins = eh * 60 + em
        if start_mins <= cur_mins <= end_mins:
            return True, f"{sh:02d}:{sm:02d}-{eh:02d}:{em:02d} UTC"
    return False, None

def check_youtube_pacing(now_utc=None, force=False):
    """Evaluates whether YouTube Shorts should publish right now."""
    if force or "--force" in sys.argv or "--force-youtube" in sys.argv:
        return True, "Force flag active (bypassing YouTube schedule guard)."
    if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
        return True, "Manual workflow dispatch trigger."

    if now_utc is None:
        now_utc = datetime.datetime.now(datetime.timezone.utc)

    # 1. Check Peak Window
    in_window, window_label = is_time_in_windows(now_utc, YT_PEAK_WINDOWS_UTC)
    if not in_window:
        return False, f"Outside YouTube peak hours (Current: {now_utc.strftime('%H:%M')} UTC). Next slots: 12:00-15:30 & 17:30-21:00 UTC."

    # 2. Check Daily Limit & Spacing from History
    if not TOPICS_FILE.exists():
        return True, "No prior YouTube history found."

    try:
        with open(TOPICS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return True, "Could not read YouTube history."

    topics = data.get("topics", [])
    today_date = now_utc.date().isoformat()
    today_count = sum(1 for e in topics if e.get("date") == today_date and e.get("status") == "public_published" and e.get("video_url"))

    if today_count >= YT_MAX_DAILY:
        return False, f"YouTube daily cap reached ({today_count}/{YT_MAX_DAILY} published today on YouTube)."

    # Find last published YouTube video
    last_published = None
    for entry in reversed(topics):
        if entry.get("status") == "public_published" and entry.get("video_url"):
            last_published = entry
            break

    if last_published and last_published.get("published_at"):
        try:
            last_dt = datetime.datetime.fromisoformat(last_published["published_at"])
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=datetime.timezone.utc)
            elapsed = (now_utc - last_dt).total_seconds() / 3600.0
            if elapsed < YT_MIN_SPACING_HOURS:
                return False, f"YouTube spacing active: Last published {elapsed:.1f}h ago (Need {YT_MIN_SPACING_HOURS:.1f}h minimum)."
        except Exception:
            pass

    return True, f"YouTube ready in peak window {window_label} (Published today: {today_count}/{YT_MAX_DAILY})."

def check_tiktok_pacing(now_utc=None, force=False):
    """Evaluates whether TikTok should publish right now."""
    if force or "--force" in sys.argv or "--force-tiktok" in sys.argv:
        return True, "Force flag active (bypassing TikTok schedule guard)."
    if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
        return True, "Manual workflow dispatch trigger."

    if now_utc is None:
        now_utc = datetime.datetime.now(datetime.timezone.utc)

    # 1. Check Peak Window
    in_window, window_label = is_time_in_windows(now_utc, TIKTOK_PEAK_WINDOWS_UTC)
    if not in_window:
        return False, f"Outside TikTok peak hours (Current: {now_utc.strftime('%H:%M')} UTC). Next slots: 07:00-09:30, 12:00-14:30, 19:00-22:00 UTC."

    # 2. Check Daily Limit & Spacing from History
    if not TIKTOK_HISTORY_FILE.exists():
        return True, "No prior TikTok history found."

    try:
        with open(TIKTOK_HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return True, "Could not read TikTok history."

    uploaded_keys = data.get("uploaded_keys", [])
    today_date = now_utc.date().isoformat()
    today_count = sum(1 for e in uploaded_keys if e.get("published_at", "").startswith(today_date))

    if today_count >= TIKTOK_MAX_DAILY:
        return False, f"TikTok daily cap reached ({today_count}/{TIKTOK_MAX_DAILY} published today on TikTok)."

    if uploaded_keys:
        last_entry = uploaded_keys[-1]
        last_ts = last_entry.get("published_at")
        if last_ts:
            try:
                last_dt = datetime.datetime.fromisoformat(last_ts)
                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(tzinfo=datetime.timezone.utc)
                elapsed = (now_utc - last_dt).total_seconds() / 3600.0
                if elapsed < TIKTOK_MIN_SPACING_HOURS:
                    return False, f"TikTok spacing active: Last published {elapsed:.1f}h ago (Need {TIKTOK_MIN_SPACING_HOURS:.1f}h minimum)."
            except Exception:
                pass

    return True, f"TikTok ready in peak window {window_label} (Published today: {today_count}/{TIKTOK_MAX_DAILY})."

def get_schedule_overview():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    yt_ready, yt_reason = check_youtube_pacing(now_utc)
    tt_ready, tt_reason = check_tiktok_pacing(now_utc)
    
    return {
        "current_time_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "current_time_morocco": (now_utc + datetime.timedelta(hours=1)).strftime("%H:%M (GMT+1)"),
        "current_time_gulf": (now_utc + datetime.timedelta(hours=3)).strftime("%H:%M (GMT+3)"),
        "youtube": {
            "ready_to_publish": yt_ready,
            "status_reason": yt_reason,
            "daily_target": "2 videos / day",
            "spacing": "5.0h minimum",
            "peak_slots_local_morocco": ["13:00 - 16:30", "18:30 - 22:00"]
        },
        "tiktok": {
            "ready_to_publish": tt_ready,
            "status_reason": tt_reason,
            "daily_target": "3 videos / day",
            "spacing": "3.0h minimum",
            "peak_slots_local_morocco": ["08:00 - 10:30", "13:00 - 15:30", "20:00 - 23:00"]
        }
    }

if __name__ == "__main__":
    overview = get_schedule_overview()
    print(json.dumps(overview, indent=2, ensure_ascii=False))
