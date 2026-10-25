"""TikTok Video Uploader via Content Posting API v2.
Handles chunked video upload, publishing status checks, and token management.
"""

import os
import sys
import math
import time
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from tiktok_auth import refresh_access_token

INIT_ENDPOINT = "https://open.tiktokapis.com/v2/post/publish/video/init/"
STATUS_ENDPOINT = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"

# Default chunk size: 10MB (TikTok requires minimum 5MB and maximum 64MB for chunks)
CHUNK_SIZE = 10 * 1024 * 1024

def upload_video_to_tiktok(video_path, caption, privacy_level="PUBLIC_TO_EVERYONE"):
    """
    Upload a local video file to TikTok using Content Posting API v2.
    
    Args:
        video_path: Path to MP4 file.
        caption: Caption text including hashtags (max 2200 characters).
        privacy_level: 'PUBLIC_TO_EVERYONE', 'MUTUAL_FOLLOW_FRIENDS', or 'SELF_ONLY'.
        
    Returns:
        dict with status, publish_id, or error.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found at: {video_path}")
        
    video_size = os.path.getsize(video_path)
    
    # Calculate chunk parameters
    if video_size <= CHUNK_SIZE:
        chunk_size = video_size
        total_chunks = 1
    else:
        chunk_size = CHUNK_SIZE
        total_chunks = math.ceil(video_size / chunk_size)
        
    print(f"🎬 Preparing TikTok upload: {video_path.name} ({video_size / (1024*1024):.2f} MB, {total_chunks} chunk(s))...", flush=True)
    
    # 1. Obtain valid access token
    try:
        access_token = refresh_access_token()
    except Exception as e:
        print(f"⚠️ Could not obtain TikTok access token: {e}", flush=True)
        return {"status": "auth_failed", "error": str(e)}
        
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    init_payload = {
        "post_info": {
            "title": caption[:2200],
            "privacy_level": privacy_level,
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            "video_cover_timestamp_ms": 1000
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": chunk_size,
            "total_chunk_count": total_chunks
        }
    }
    
    # 2. Initialize video upload
    print("Initiating TikTok direct post upload...", flush=True)
    init_res = requests.post(INIT_ENDPOINT, json=init_payload, headers=headers)
    init_data = init_res.json()
    
    if init_res.status_code != 200 or "data" not in init_data or "upload_url" not in init_data["data"]:
        print(f"❌ TikTok Init Failed: {init_data}", flush=True)
        return {"status": "init_failed", "error": init_data}
        
    upload_url = init_data["data"]["upload_url"]
    publish_id = init_data["data"]["publish_id"]
    print(f"✅ Initialized successfully. Publish ID: {publish_id}")
    
    # 3. Stream binary chunks to upload_url
    with open(video_path, "rb") as f:
        for chunk_idx in range(total_chunks):
            chunk_data = f.read(chunk_size)
            start_byte = chunk_idx * chunk_size
            end_byte = start_byte + len(chunk_data) - 1
            
            chunk_headers = {
                "Content-Range": f"bytes {start_byte}-{end_byte}/{video_size}",
                "Content-Type": "video/mp4"
            }
            
            print(f"Uploading chunk {chunk_idx + 1}/{total_chunks} ({len(chunk_data)} bytes)...", flush=True)
            put_res = requests.put(upload_url, data=chunk_data, headers=chunk_headers)
            
            if put_res.status_code not in [200, 201, 206]:
                print(f"❌ Chunk upload failed with status {put_res.status_code}: {put_res.text}")
                return {"status": "chunk_failed", "publish_id": publish_id, "chunk": chunk_idx}
                
    print("🎉 All video chunks uploaded to TikTok servers!")
    
    # 4. Check publish status
    for check_attempt in range(6):
        time.sleep(3)
        status_res = requests.post(STATUS_ENDPOINT, json={"publish_id": publish_id}, headers=headers)
        status_data = status_res.json()
        
        if status_res.status_code == 200 and "data" in status_data:
            pub_status = status_data["data"].get("status")
            print(f"📡 TikTok Processing Status [{check_attempt+1}/6]: {pub_status}", flush=True)
            if pub_status in ["SUCCESS", "PUBLISH_COMPLETE"]:
                print("🌟 Video is officially PUBLISHED on TikTok!")
                return {"status": "published", "publish_id": publish_id}
            elif pub_status in ["FAILED"]:
                print(f"❌ TikTok publishing failed: {status_data['data'].get('fail_reason')}")
                return {"status": "failed", "publish_id": publish_id, "reason": status_data["data"]}
                
    return {"status": "uploaded_processing", "publish_id": publish_id}

if __name__ == "__main__":
    if len(sys.argv) > 2:
        res = upload_video_to_tiktok(sys.argv[1], sys.argv[2])
        print("Result:", res)
    else:
        print("Usage: python scripts/tiktok_uploader.py <video_path> <caption>")
