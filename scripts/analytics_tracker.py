"""Algorithmic Analytics Pacing Engine for Tales of Wonder.
Monitors the view velocity of the latest published video on YouTube/TikTok:
1. Target: Exactly 3 videos per day.
2. If the latest video is actively surging in views, delay the next drop to avoid cannibalizing viral momentum.
3. If the video has stagnated/plateaued, initiate a strict 1-hour grace period.
4. Only after the full 1-hour grace period has elapsed after stagnation, GREENLIGHT the next video drop.
5. Enforces a strict daily limit of MAXIMUM 3 VIDEOS PER DAY.
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

MAX_DAILY_VIDEOS = 3              # Exactly 3 videos / day
MIN_SEED_HOURS = 1.5              # Minimum breathing time right after upload
POST_STAGNATION_WAIT_MINS = 60.0  # Exactly 1 hour grace period after stagnation
SURGE_VELOCITY_THRESHOLD = 15     # Views gained over recent window to consider surging

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

    # 0. Enforce Daytime Waking Hours Window (08:00 - 22:00 Morocco / 07:00 - 21:00 UTC)
    morocco_time = now_utc + datetime.timedelta(hours=1)
    morocco_hour = morocco_time.hour
    if morocco_hour < 8 or morocco_hour >= 22:
        reason = (
            f"🌙 Night rest active: Current time in Morocco is {morocco_time.strftime('%H:%M')} (Night). "
            f"Kids content publishes strictly during active waking daytime hours (08:00 - 22:00 Morocco)."
        )
        return False, reason, {
            "morocco_time": morocco_time.strftime("%H:%M"),
            "active_window": "08:00 - 22:00 (GMT+1 Morocco)",
            "status": "night_paused"
        }

    topics_data = load_json(TOPICS_FILE)
    today_count = get_daily_published_count(topics_data, now_utc)

    # 1. Enforce strict daily cap: Exactly 3 videos / day max
    if today_count >= MAX_DAILY_VIDEOS:
        reason = f"🛑 Daily cap reached: {today_count}/{MAX_DAILY_VIDEOS} videos already published today. System rests until tomorrow."
        return False, reason, {"daily_count": today_count, "cap": MAX_DAILY_VIDEOS}

    # 2. If no video published today yet -> Greenlight first video
    if today_count == 0:
        reason = f"🚀 First video of the day (1/{MAX_DAILY_VIDEOS}) greenlit for publication."
        return True, reason, {"daily_count": 0, "cap": MAX_DAILY_VIDEOS}

    # 3. Find latest published video to analyze its growth
    latest_video = get_latest_published_video(topics_data)
    if not latest_video:
        return True, f"🚀 No prior published video found. Greenlit for publication (video {today_count + 1}/{MAX_DAILY_VIDEOS}).", {}

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
            elapsed_hours = 2.0

    # 4. Minimum seed testing window: give the video at least 1.5h to breathe
    if elapsed_hours < MIN_SEED_HOURS:
        remaining_seed = int((MIN_SEED_HOURS - elapsed_hours) * 60)
        reason = f"⏳ Seed audience test active: Latest video '{title}' was published {elapsed_hours:.1f}h ago. Letting it breathe ({remaining_seed} mins left of {MIN_SEED_HOURS}h seed window)."
        return False, reason, {"video_id": video_id, "elapsed_hours": elapsed_hours}

    # 5. Fetch live analytics from YouTube Data API
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

    # Calculate recent delta over snapshots taken in the last 60 minutes
    views_surging = False
    recent_delta = 0
    if len(history) >= 2 and current_views is not None:
        # Find oldest snapshot within the last 60 minutes
        cutoff_dt = now_utc - datetime.timedelta(minutes=60)
        baseline_views = None
        for h in history:
            try:
                h_dt = datetime.datetime.fromisoformat(h["timestamp"])
                if h_dt.tzinfo is None:
                    h_dt = h_dt.replace(tzinfo=datetime.timezone.utc)
                if h_dt <= cutoff_dt or baseline_views is None:
                    baseline_views = h["views"]
            except Exception:
                pass

        if baseline_views is not None:
            recent_delta = current_views - baseline_views

        if recent_delta >= SURGE_VELOCITY_THRESHOLD:
            views_surging = True

    if views_surging:
        # Video is active and gaining views -> Reset stagnation timer and HOLD
        v_cache["stagnation_detected_at"] = None
        cache[video_id] = v_cache
        save_json(ANALYTICS_CACHE_FILE, cache)
        reason = f"🔥 Latest video '{title}' is actively surging (+{recent_delta} views recently, now at {current_views}). Holding next drop to maximize algorithmic reach."
        return False, reason, {"video_id": video_id, "views": current_views, "recent_delta": recent_delta, "status": "surging"}

    # Views have flattened out / stagnated
    if stagnation_detected_at is None:
        # First time detecting stagnation! Start the strict 1-hour grace timer
        v_cache["stagnation_detected_at"] = now_iso
        cache[video_id] = v_cache
        save_json(ANALYTICS_CACHE_FILE, cache)
        reason = f"📉 Stagnation detected on '{title}' ({current_views or 0} views). Starting strict 1-hour grace timer before next video drop."
        return False, reason, {"video_id": video_id, "views": current_views, "status": "stagnation_initiated"}

    # Stagnation timer is already running: Check elapsed time since stagnation
    try:
        stag_dt = datetime.datetime.fromisoformat(stagnation_detected_at)
        if stag_dt.tzinfo is None:
            stag_dt = stag_dt.replace(tzinfo=datetime.timezone.utc)
        stag_elapsed_mins = (now_utc - stag_dt).total_seconds() / 60.0
    except Exception:
        stag_elapsed_mins = 0.0

    if stag_elapsed_mins < POST_STAGNATION_WAIT_MINS:
        remaining_mins = int(POST_STAGNATION_WAIT_MINS - stag_elapsed_mins)
        reason = f"⏳ 1-Hour grace period active: Video stagnated {int(stag_elapsed_mins)} mins ago. Waiting {remaining_mins} more minutes before dropping next video."
        return False, reason, {"video_id": video_id, "stag_elapsed_mins": stag_elapsed_mins, "remaining_mins": remaining_mins}

    # Stagnation confirmed + full 1 hour grace period elapsed + daily count < 3 -> GREENLIGHT!
    cache[video_id] = v_cache
    save_json(ANALYTICS_CACHE_FILE, cache)
    reason = f"✅ Algorithmic greenlight: Latest video stagnated for {stag_elapsed_mins / 60.0:.1f}h. Ready to launch episode {today_count + 1}/{MAX_DAILY_VIDEOS} today!"
    return True, reason, {"daily_count": today_count, "cap": MAX_DAILY_VIDEOS, "video_id": video_id}

if __name__ == "__main__":
    ready, reason, data = check_algorithmic_readiness()
    print("=" * 60)
    print("📊 ALGORITHMIC PACING STATUS")
    print(f"Action: {'🟢 PUBLISH NEW EPISODE' if ready else '🔴 PAUSE / WAIT'}")
    print(f"Reason: {reason}")
    print(f"Data:   {data}")
    print("=" * 60)
