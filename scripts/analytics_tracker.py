"""Algorithmic Analytics Pacing Engine for Tales of Wonder.
Monitors the view velocity of the latest published video on YouTube/TikTok:
1. If the latest video is actively surging in views, delay the next drop to avoid cannibalizing viral momentum.
2. If the video has stagnated/plateaued, initiate a 1-hour grace period, then GREENLIGHT the next drop.
3. Enforces a strict daily limit of MAXIMUM 3 VIDEOS PER DAY throughout the day.
"""

import os
import sys
import json
import re
import datetime
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

# Ensure UTF-8 console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TOPICS_FILE = DATA_DIR / "topics_history.json"
TIKTOK_HISTORY_FILE = DATA_DIR / "tiktok_upload_history.json"
ANALYTICS_CACHE_FILE = DATA_DIR / "video_analytics_cache.json"

MAX_DAILY_VIDEOS = 3          # Maximum 3 videos / day
MIN_SEED_HOURS = 1.5          # Minimum breathing time for initial seed audience test
POST_STAGNATION_WAIT_HOURS = 1.0  # Wait ~1h after stagnation before dropping next video
MAX_CEILING_HOURS = 6.0       # If video has been live for >6h and daily cap not reached, allow next drop

def load_json(path: Path) -> dict:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_youtube_video_id(url: str) -> Optional[str]:
    if not url:
        return None
    # Support https://youtu.be/ID and https://www.youtube.com/watch?v=ID and https://youtube.com/shorts/ID
    m = re.search(r"(?:youtu\.be/|v=|shorts/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None

def get_latest_published_video(topics_data: dict) -> Optional[dict]:
    """Find the most recent publicly published video entry."""
    topics = topics_data.get("topics", [])
    for entry in reversed(topics):
        if entry.get("status") == "public_published" and entry.get("video_url"):
            return entry
    return None

def get_daily_published_count(topics_data: dict, now_utc: datetime.datetime) -> int:
    """Count how many videos were successfully published in the current 24-hour day."""
    today_str = now_utc.date().isoformat()
    count = 0
    for entry in topics_data.get("topics", []):
        if entry.get("status") == "public_published" and entry.get("video_url"):
            pub_at = entry.get("published_at")
            if pub_at:
                try:
                    dt = datetime.datetime.fromisoformat(pub_at)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=datetime.timezone.utc)
                    if dt.date() == now_utc.date():
                        count += 1
                        continue
                except Exception:
                    pass
            if entry.get("date") == today_str:
                count += 1
    return count

def check_algorithmic_readiness(now_utc: Optional[datetime.datetime] = None, force: bool = False) -> Tuple[bool, str, Dict[str, Any]]:
    """Evaluates real-time video analytics to decide if a new video should be published."""
    if force or "--force" in sys.argv or os.environ.get("FORCE_RUN") == "1":
        return True, "⚡ Force override active (bypassing pacing check).", {}
    if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
        return True, "🔘 Manual workflow dispatch trigger.", {}

    if now_utc is None:
        now_utc = datetime.datetime.now(datetime.timezone.utc)

    topics_data = load_json(TOPICS_FILE)
    today_count = get_daily_published_count(topics_data, now_utc)

    # 1. Enforce strict daily cap (Max 3 videos/day)
    if today_count >= MAX_DAILY_VIDEOS:
        reason = f"🛑 Daily cap reached: {today_count}/{MAX_DAILY_VIDEOS} videos already published today. System rests until tomorrow."
        return False, reason, {"daily_count": today_count, "cap": MAX_DAILY_VIDEOS}

    # 2. If no video published today yet -> Greenlight first video
    if today_count == 0:
        reason = f"🚀 First video of the day greenlit for publication (0/{MAX_DAILY_VIDEOS} published today)."
        return True, reason, {"daily_count": 0, "cap": MAX_DAILY_VIDEOS}

    # 3. Find latest published video to analyze its growth
    latest_video = get_latest_published_video(topics_data)
    if not latest_video:
        return True, "🚀 No prior published video found. Greenlit for publication.", {}

    video_url = latest_video.get("video_url", "")
    video_id = extract_youtube_video_id(video_url)
    title = latest_video.get("title", "")

    # Calculate elapsed time since latest video upload
    pub_ts = latest_video.get("published_at")
    elapsed_hours = 0.0
    if pub_ts:
        try:
            pub_dt = datetime.datetime.fromisoformat(pub_ts)
            if pub_dt.tzinfo is None:
                pub_dt = pub_dt.replace(tzinfo=datetime.timezone.utc)
            elapsed_hours = (now_utc - pub_dt).total_seconds() / 3600.0
        except Exception:
            elapsed_hours = 2.0  # safe assumption if timestamp parsing fails

    # 4. Minimum seed testing window: give the video at least 1.5h to breathe
    if elapsed_hours < MIN_SEED_HOURS:
        reason = f"⏳ Seed audience test active: Latest video '{title}' was published {elapsed_hours:.1f}h ago. Letting it breathe (minimum {MIN_SEED_HOURS}h)."
        return False, reason, {"video_id": video_id, "elapsed_hours": elapsed_hours}

    # 5. Fetch live analytics from YouTube
    stats = None
    if video_id:
        try:
            from youtube_uploader import get_video_statistics
            stats = get_video_statistics(video_id)
        except Exception as e:
            print(f"Notice: Could not reach YouTube Data API for live stats: {e}")

    current_views = stats.get("view_count", 0) if stats else None

    # Load / update analytics cache
    cache = load_json(ANALYTICS_CACHE_FILE)
    v_cache = cache.get(video_id, {
        "title": title,
        "first_seen": now_utc.isoformat(),
        "history": [],
        "stagnation_detected_at": None
    })

    now_iso = now_utc.isoformat()
    if current_views is not None:
        v_cache["history"].append({"timestamp": now_iso, "views": current_views})
        # Keep last 20 snapshots
        v_cache["history"] = v_cache["history"][-20:]

    # 6. Analyze View Velocity & Stagnation
    history = v_cache.get("history", [])
    stagnation_detected_at = v_cache.get("stagnation_detected_at")

    # Check growth velocity across previous snapshots
    views_surging = False
    if len(history) >= 2:
        prev_views = history[-2]["views"]
        recent_delta = current_views - prev_views if (current_views is not None and prev_views is not None) else 0
        if recent_delta >= 10:  # Gaining steady views
            views_surging = True

    if views_surging:
        # Reset stagnation flag because video is active
        v_cache["stagnation_detected_at"] = None
        cache[video_id] = v_cache
        save_json(ANALYTICS_CACHE_FILE, cache)
        reason = f"🔥 Latest video '{title}' is actively surging in views (+{recent_delta} views). Holding next drop to maximize algorithm reach."
        return False, reason, {"video_id": video_id, "views": current_views, "status": "surging"}

    # If views are flat/stagnated
    if stagnation_detected_at is None:
        # First time detecting stagnation! Start the 1-hour grace timer
        v_cache["stagnation_detected_at"] = now_iso
        cache[video_id] = v_cache
        save_json(ANALYTICS_CACHE_FILE, cache)
        reason = f"📉 Stagnation detected on '{title}' ({current_views or 0} views). Starting 1-hour grace timer before next video drop."
        return False, reason, {"video_id": video_id, "views": current_views, "status": "stagnation_initiated"}

    # Stagnation timer already running: Check elapsed time since stagnation
    try:
        stag_dt = datetime.datetime.fromisoformat(stagnation_detected_at)
        if stag_dt.tzinfo is None:
            stag_dt = stag_dt.replace(tzinfo=datetime.timezone.utc)
        stag_elapsed_hours = (now_utc - stag_dt).total_seconds() / 3600.0
    except Exception:
        stag_elapsed_hours = 1.0

    if stag_elapsed_hours < POST_STAGNATION_WAIT_HOURS and elapsed_hours < MAX_CEILING_HOURS:
        remaining_mins = int((POST_STAGNATION_WAIT_HOURS - stag_elapsed_hours) * 60)
        reason = f"⏳ 1-Hour grace period active: Video stagnated {stag_elapsed_hours:.1f}h ago. Waiting {remaining_mins} more minutes before dropping next video."
        return False, reason, {"video_id": video_id, "stag_elapsed_hours": stag_elapsed_hours}

    # Stagnation confirmed + 1 hour grace period elapsed + daily count < 3 -> GREENLIGHT!
    cache[video_id] = v_cache
    save_json(ANALYTICS_CACHE_FILE, cache)
    reason = f"✅ Algorithmic greenlight: Latest video stagnated for {stag_elapsed_hours:.1f}h. Ready to launch episode {today_count + 1}/{MAX_DAILY_VIDEOS} today!"
    return True, reason, {"daily_count": today_count, "cap": MAX_DAILY_VIDEOS, "video_id": video_id}

if __name__ == "__main__":
    ready, reason, data = check_algorithmic_readiness()
    print("=" * 60)
    print("📊 ALGORITHMIC PACING STATUS")
    print(f"Action: {'🟢 PUBLISH NEW EPISODE' if ready else '🔴 PAUSE / WAIT'}")
    print(f"Reason: {reason}")
    print(f"Data:   {data}")
    print("=" * 60)
