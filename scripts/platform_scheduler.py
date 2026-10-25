"""Platform-Optimized Algorithmic Pacing Engine for Tales of Wonder.
Decouples YouTube Shorts and TikTok scheduling rules to maximize channel authority
and prevent algorithmic cannibalization.

YOUTUBE SHORTS RULES:
- Strict Daily Cap: 2 videos / day MAX.
- Strict Spacing: Minimum 5.5 hours between uploads.
- Peak Windows (Morocco GMT+1):
    Slot 1: 13:00 - 15:30 (Lunch / school exit)
    Slot 2: 19:00 - 21:30 (Evening family / bedtime routine)

TIKTOK RULES:
- Strict Daily Cap: 3 videos / day MAX.
- Strict Spacing: Minimum 3.5 hours between uploads.
- Peak Windows (Morocco GMT+1):
    Slot 1: 08:30 - 10:30 (Morning routine)
    Slot 2: 13:30 - 15:30 (Lunch / afternoon rest)
    Slot 3: 20:00 - 22:30 (Prime evening)
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

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

# Strict Platform Limits
YT_MAX_DAILY = 2
YT_MIN_SPACING_HOURS = 5.5
YT_PEAK_WINDOWS_MOROCCO = [(13, 0, 15, 30), (19, 0, 21, 30)]

TT_MAX_DAILY = 3
TT_MIN_SPACING_HOURS = 3.5
TT_PEAK_WINDOWS_MOROCCO = [(8, 30, 10, 30), (13, 30, 15, 30), (20, 0, 22, 30)]

def load_json(path: Path) -> dict:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def is_in_time_window(hour: int, minute: int, windows: list) -> bool:
    cur_m = hour * 60 + minute
    for start_h, start_m, end_h, end_m in windows:
        if (start_h * 60 + start_m) <= cur_m <= (end_h * 60 + end_m):
            return True
    return False

def check_youtube_pacing(now_utc: Optional[datetime.datetime] = None, force: bool = False) -> Tuple[bool, str]:
    """Strict YouTube Shorts algorithm pacing check."""
    if force or "--force" in sys.argv or os.environ.get("FORCE_RUN") == "1":
        return True, "⚡ Force override active (bypassing YouTube pacing check)."

    if now_utc is None:
        now_utc = datetime.datetime.now(datetime.timezone.utc)

    morocco_time = now_utc + datetime.timedelta(hours=1)
    topics_data = load_json(TOPICS_FILE)
    topics = topics_data.get("topics", [])

    # 1. Count YouTube videos published today
    today_str = now_utc.date().isoformat()
    yt_today_count = 0
    latest_yt_time = None

    for entry in topics:
        if entry.get("status") == "public_published" and entry.get("video_url"):
            pub_at = entry.get("published_at")
            if pub_at:
                try:
                    dt = datetime.datetime.fromisoformat(pub_at)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=datetime.timezone.utc)
                    if latest_yt_time is None or dt > latest_yt_time:
                        latest_yt_time = dt
                    if dt.date() == now_utc.date():
                        yt_today_count += 1
                except Exception:
                    pass

    # Rule A: Strict Daily Cap (2 videos/day max)
    if yt_today_count >= YT_MAX_DAILY:
        return False, f"🛑 YouTube daily cap reached: {yt_today_count}/{YT_MAX_DAILY} published today. Paused to protect channel authority."

    # Rule B: Strict Spacing (minimum 5.5 hours)
    if latest_yt_time:
        elapsed_hours = (now_utc - latest_yt_time).total_seconds() / 3600.0
        if elapsed_hours < YT_MIN_SPACING_HOURS:
            remaining = YT_MIN_SPACING_HOURS - elapsed_hours
            return False, f"⏳ YouTube spacing lock: Latest video was {elapsed_hours:.1f}h ago. Need {remaining:.1f}h more breathing room (minimum {YT_MIN_SPACING_HOURS}h spacing)."

    # Rule C: Optimal Peak Time Window (Morocco GMT+1)
    in_peak = is_in_time_window(morocco_time.hour, morocco_time.minute, YT_PEAK_WINDOWS_MOROCCO)
    if not in_peak:
        return False, f"⏰ YouTube off-peak: Current time is {morocco_time.strftime('%H:%M')} (Morocco). Peak slots are 13:00-15:30 and 19:00-21:30."

    return True, f"🚀 YouTube greenlit: Slot is active ({morocco_time.strftime('%H:%M')} Morocco) and {yt_today_count}/{YT_MAX_DAILY} published today."

def check_tiktok_pacing(now_utc: Optional[datetime.datetime] = None, force: bool = False) -> Tuple[bool, str]:
    """Strict TikTok FYP algorithm pacing check."""
    if force or "--force" in sys.argv or os.environ.get("FORCE_RUN") == "1":
        return True, "⚡ Force override active (bypassing TikTok pacing check)."

    if now_utc is None:
        now_utc = datetime.datetime.now(datetime.timezone.utc)

    morocco_time = now_utc + datetime.timedelta(hours=1)
    tt_data = load_json(TIKTOK_HISTORY_FILE)
    uploads = tt_data.get("uploaded_keys", [])

    tt_today_count = 0
    latest_tt_time = None

    for entry in uploads:
        pub_at = entry.get("published_at")
        if pub_at:
            try:
                dt = datetime.datetime.fromisoformat(pub_at)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
                if latest_tt_time is None or dt > latest_tt_time:
                    latest_tt_time = dt
                if dt.date() == now_utc.date():
                    tt_today_count += 1
            except Exception:
                pass

    # Rule A: Strict Daily Cap (3 videos/day max)
    if tt_today_count >= TT_MAX_DAILY:
        return False, f"🛑 TikTok daily cap reached: {tt_today_count}/{TT_MAX_DAILY} published today. Paused to prevent spam flags."

    # Rule B: Strict Spacing (minimum 3.5 hours)
    if latest_tt_time:
        elapsed_hours = (now_utc - latest_tt_time).total_seconds() / 3600.0
        if elapsed_hours < TT_MIN_SPACING_HOURS:
            remaining = TT_MIN_SPACING_HOURS - elapsed_hours
            return False, f"⏳ TikTok spacing lock: Latest post was {elapsed_hours:.1f}h ago. Need {remaining:.1f}h more spacing (minimum {TT_MIN_SPACING_HOURS}h)."

    # Rule C: Peak Time Window (Morocco GMT+1)
    in_peak = is_in_time_window(morocco_time.hour, morocco_time.minute, TT_PEAK_WINDOWS_MOROCCO)
    if not in_peak:
        return False, f"⏰ TikTok off-peak: Current time is {morocco_time.strftime('%H:%M')} (Morocco). Peak slots are 08:30-10:30, 13:30-15:30, and 20:00-22:30."

    return True, f"🚀 TikTok greenlit: Slot is active ({morocco_time.strftime('%H:%M')} Morocco) and {tt_today_count}/{TT_MAX_DAILY} published today."

def get_schedule_overview():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    yt_ready, yt_reason = check_youtube_pacing(now_utc)
    tt_ready, tt_reason = check_tiktok_pacing(now_utc)

    return {
        "current_time_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "current_time_morocco": (now_utc + datetime.timedelta(hours=1)).strftime("%H:%M (GMT+1)"),
        "youtube": {
            "daily_cap": f"{YT_MAX_DAILY} videos / day max",
            "min_spacing": f"{YT_MIN_SPACING_HOURS} hours",
            "ready_to_publish": yt_ready,
            "status_reason": yt_reason
        },
        "tiktok": {
            "daily_cap": f"{TT_MAX_DAILY} videos / day max",
            "min_spacing": f"{TT_MIN_SPACING_HOURS} hours",
            "ready_to_publish": tt_ready,
            "status_reason": tt_reason
        }
    }

if __name__ == "__main__":
    overview = get_schedule_overview()
    print(json.dumps(overview, indent=2, ensure_ascii=False))
