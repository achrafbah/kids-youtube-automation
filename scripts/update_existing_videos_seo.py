"""
Bulk SEO Overhaul for Already-Published Videos on Tales of Wonder.
Reads data/topics_history.json, builds optimized SEO packages (Shorts hook title, rich keyword description, 500-char tags),
and calls YouTube Data API v3 (videos().update) to update all live videos.
"""
import os
import sys
import json
import time
from pathlib import Path

# Add project root and scripts directory
BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from youtube_uploader import get_authenticated_service
from generate_daily_episode import build_optimized_seo_package, load_json, TOPICS_FILE

def bulk_update_all_videos():
    history_data = load_json(TOPICS_FILE)
    topics = history_data.get("topics", [])
    if not topics:
        print("No topics found in history.")
        return

    youtube = get_authenticated_service()
    if not youtube:
        print("Could not authenticate YouTube service.")
        return

    print(f"🚀 Found {len(topics)} topics in history. Beginning SEO overhaul on YouTube...")
    updated_count = 0

    for idx, item in enumerate(topics, 1):
        video_url = item.get("video_url")
        if not video_url or "youtu.be/" not in video_url:
            continue
        video_id = video_url.split("youtu.be/")[1].split("?")[0].strip()

        # Build SEO package
        topic_dummy = {
            "title_ar": item.get("title", ""),
            "pillar": item.get("pillar", item.get("category", "تعليم الأطفال")),
            "lesson": item.get("lesson", item.get("summary", "")),
            "topic_key": item.get("topic_key", item.get("id", "")),
            "tags": item.get("tags", [])
        }
        seo_pkg = build_optimized_seo_package(topic_dummy)

        print(f"\n[{idx}/{len(topics)}] Updating Video: {video_id}", flush=True)
        print(f"   🎯 New Title: {seo_pkg['title']}", flush=True)
        print(f"   🏷️ Tags: {len(seo_pkg['tags'])} tags", flush=True)

        try:
            # 1. Fetch current snippet
            get_req = youtube.videos().list(part="snippet,status", id=video_id)
            resp = get_req.execute()
            items = resp.get("items", [])
            if not items:
                print(f"   ⚠️ Video {video_id} not found on YouTube.", flush=True)
                continue

            snippet = items[0]["snippet"]
            snippet["title"] = seo_pkg["title"][:100]
            snippet["description"] = seo_pkg["description"][:5000]
            snippet["tags"] = seo_pkg["tags"]
            snippet["categoryId"] = "27"
            snippet["defaultLanguage"] = "ar"
            snippet["defaultAudioLanguage"] = "ar"

            # 2. Push update
            update_req = youtube.videos().update(
                part="snippet",
                body={
                    "id": video_id,
                    "snippet": snippet
                }
            )
            update_req.execute()
            print(f"   ✅ Successfully updated SEO for video {video_id}!", flush=True)
            updated_count += 1
            time.sleep(1)  # respectful API rate limit pause
        except Exception as err:
            print(f"   ❌ Error updating video {video_id}: {err}", flush=True)

    print("\n" + "=" * 50, flush=True)
    print(f"🎉 Bulk SEO Update Complete! Successfully updated {updated_count} videos.", flush=True)
    print("=" * 50, flush=True)

if __name__ == "__main__":
    bulk_update_all_videos()
