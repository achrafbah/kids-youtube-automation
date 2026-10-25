"""Platform-Optimized Algorithmic Pacing Engine for Tales of Wonder.
Monitors the real-time view velocity of the latest published video on YouTube and TikTok:
1. Target: Exactly 3 videos per day.
2. If the latest video is actively surging in views, delay the next drop to avoid cannibalizing viral momentum.
3. If the video has stagnated/plateaued, initiate a strict 1-hour grace period.
4. Only after the full 1-hour grace period has elapsed after stagnation, GREENLIGHT the next video drop.
5. Strict daily limit of MAXIMUM 3 VIDEOS PER DAY.
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
SCRIPTS_DIR = BASE_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from analytics_tracker import check_algorithmic_readiness, MAX_DAILY_VIDEOS

def check_youtube_pacing(now_utc: Optional[datetime.datetime] = None, force: bool = False) -> Tuple[bool, str]:
    """Strict YouTube Shorts algorithm pacing check: Stagnation + 1h Grace Period, Max 3/day."""
    ready, reason, data = check_algorithmic_readiness(now_utc=now_utc, force=force)
    return ready, reason

def check_tiktok_pacing(now_utc: Optional[datetime.datetime] = None, force: bool = False) -> Tuple[bool, str]:
    """Strict TikTok FYP algorithm pacing check: Stagnation + 1h Grace Period, Max 3/day."""
    ready, reason, data = check_algorithmic_readiness(now_utc=now_utc, force=force)
    return ready, reason

def get_schedule_overview():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    yt_ready, yt_reason = check_youtube_pacing(now_utc)
    tt_ready, tt_reason = check_tiktok_pacing(now_utc)

    return {
        "current_time_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "current_time_morocco": (now_utc + datetime.timedelta(hours=1)).strftime("%H:%M (GMT+1)"),
        "algorithm": "Stagnation Tracker + Strict 1-Hour Grace Period",
        "daily_target": f"{MAX_DAILY_VIDEOS} videos / day max",
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
