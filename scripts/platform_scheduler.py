"""Platform-Optimized Algorithmic Pacing Engine for Tales of Wonder.
Monitors the analytics of the latest published video and triggers publication on YouTube and TikTok:
1. Active throughout the 24 hours of the day.
2. Max daily volume: Exactly 3 videos / day.
3. If latest video is surging in views: Pause next upload to avoid cannibalizing organic momentum.
4. If latest video stagnates: Wait 1 hour grace period, then trigger the next upload!
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
SCRIPTS_DIR = BASE_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from analytics_tracker import check_algorithmic_readiness, MAX_DAILY_VIDEOS

def check_youtube_pacing(now_utc=None, force=False):
    """Evaluates whether YouTube Shorts should publish right now based on live analytics."""
    ready, reason, data = check_algorithmic_readiness(now_utc=now_utc, force=force)
    return ready, reason

def check_tiktok_pacing(now_utc=None, force=False):
    """Evaluates whether TikTok should publish right now (synchronized with YouTube pipeline)."""
    ready, reason, data = check_algorithmic_readiness(now_utc=now_utc, force=force)
    return ready, reason

def get_schedule_overview():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    yt_ready, yt_reason = check_youtube_pacing(now_utc)
    tt_ready, tt_reason = check_tiktok_pacing(now_utc)

    return {
        "current_time_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "current_time_morocco": (now_utc + datetime.timedelta(hours=1)).strftime("%H:%M (GMT+1)"),
        "pacing_mode": "Dynamic Analytics-Driven (Views Velocity & Stagnation Tracker)",
        "daily_cap": f"{MAX_DAILY_VIDEOS} videos / day max",
        "youtube": {
            "ready_to_publish": yt_ready,
            "status_reason": yt_reason
        },
        "tiktok": {
            "ready_to_publish": tt_ready,
            "status_reason": tt_reason
        }
    }

if __name__ == "__main__":
    overview = get_schedule_overview()
    print(json.dumps(overview, indent=2, ensure_ascii=False))
