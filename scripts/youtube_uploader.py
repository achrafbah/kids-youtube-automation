"""YouTube Automated Video Uploader via YouTube Data API v3.
Compliant with COPPA (Made for Kids) and handles OAuth2 token caching.
"""

import os
import sys
import json
from pathlib import Path

# Fix Windows console encoding for Arabic characters
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_DIR = BASE_DIR / "credentials"
CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)

CLIENT_SECRET_FILE = CREDENTIALS_DIR / "client_secret.json"
TOKEN_FILE = CREDENTIALS_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

def ensure_credentials_from_env():
    """Populate credentials from GitHub Secrets / environment variables if missing on disk."""
    if not TOKEN_FILE.exists() and os.environ.get("YOUTUBE_TOKEN_JSON"):
        print("Restoring YouTube token from environment secret...")
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(os.environ["YOUTUBE_TOKEN_JSON"])

    if not CLIENT_SECRET_FILE.exists() and os.environ.get("YOUTUBE_CLIENT_SECRET_JSON"):
        print("Restoring YouTube client secret from environment secret...")
        with open(CLIENT_SECRET_FILE, "w", encoding="utf-8") as f:
            f.write(os.environ["YOUTUBE_CLIENT_SECRET_JSON"])

def get_authenticated_service():
    """Authenticate with YouTube Data API v3 and return YouTube service."""
    ensure_credentials_from_env()
    creds = None
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as e:
            print(f"Warning: Could not read token.json: {e}")
            creds = None

    if not creds or not creds.valid:
        refreshed = False
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired YouTube OAuth token...")
            try:
                creds.refresh(Request())
                refreshed = True
            except Exception as e:
                print(f"⚠️ Failed to refresh token ({e}). Re-authorizing...")
                creds = None

        if not refreshed:
            if not CLIENT_SECRET_FILE.exists():
                print("=" * 60)
                print("❌ Fichier `client_secret.json` introuvable !")
                print(f"Emplacement requis : {CLIENT_SECRET_FILE}")
                print("=" * 60)
                print("Étapes rapides pour l'obtenir :")
                print("1. Rendez-vous sur https://console.cloud.google.com/")
                print("2. Activez 'YouTube Data API v3'")
                print("3. Créez un 'Identifiant OAuth 2.0' (Application de bureau / Desktop)")
                print("4. Téléchargez le fichier JSON et renommez-le `client_secret.json`")
                print(f"5. Placez-le dans : {CREDENTIALS_DIR}")
                print("=" * 60)
                return None

            print("Opening browser for YouTube authorization...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
                creds = flow.run_local_server(
                    port=8080,
                    open_browser=True,
                    access_type="offline",
                    prompt="consent",
                    timeout_seconds=60
                )
            except Exception as auth_err:
                print(f"⚠️ YouTube authorization could not complete: {auth_err}")
                return None

        # Save credentials for future unattended runs
        if creds:
            with open(TOKEN_FILE, "w", encoding="utf-8") as token_f:
                token_f.write(creds.to_json())
            print(f"✅ Authorization token saved successfully to {TOKEN_FILE}")

    if not creds or not creds.valid:
        return None

    return build("youtube", "v3", credentials=creds)

def upload_video(
    video_path,
    title,
    description,
    tags,
    category_id="27",  # 27 = Education
    privacy_status="public",  # Direct public publishing
    made_for_kids=False,
    thumbnail_path=None
):
    """Upload a video file to YouTube with metadata and kid-safety flags."""
    youtube = get_authenticated_service()
    if not youtube:
        return None

    if not os.path.exists(video_path):
        print(f"❌ Video file does not exist: {video_path}")
        return None

    # Sanitize and deduplicate tags: YouTube expects clean keywords without '#' (max 500 chars)
    clean_tags = []
    char_count = 0
    for t in (tags or []):
        c = str(t).lstrip("#").strip()
        if c and c not in clean_tags:
            if char_count + len(c) + 1 <= 480:
                clean_tags.append(c)
                char_count += len(c) + 1

    body = {
        "snippet": {
            "title": title[:100],  # YouTube max title length is 100
            "description": description[:5000],
            "tags": clean_tags,
            "categoryId": category_id,
            "defaultLanguage": "ar",
            "defaultAudioLanguage": "ar"
        },
        "status": {
            "privacyStatus": privacy_status,  # public, unlisted, private
            "selfDeclaredMadeForKids": made_for_kids
        }
    }

    media = MediaFileUpload(
        str(video_path),
        chunksize=-1,
        resumable=True
    )

    print(f"Uploading video '{title}' to YouTube...")
    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    try:
        response = insert_request.execute()
        video_id = response.get("id")
        video_url = f"https://youtu.be/{video_id}"
        print(f"🎉 Upload Complete! Video URL: {video_url}")

        # Set custom thumbnail if provided
        if thumbnail_path and os.path.exists(thumbnail_path) and video_id:
            try:
                print("Uploading custom thumbnail...")
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(str(thumbnail_path))
                ).execute()
                print("✅ Custom thumbnail uploaded.")
            except Exception as thumb_err:
                print(f"Thumbnail upload notice: {thumb_err}")

        return {
            "video_id": video_id,
            "video_url": video_url,
            "title": title,
            "status": privacy_status
        }
    except Exception as upload_err:
        err_msg = str(upload_err)
        print(f"\n⚠️ YouTube Upload Exception: {err_msg}")
        if "uploadLimitExceeded" in err_msg:
            print("🛑 YouTube Daily Upload Limit Reached: Channel 'Tales of Wonder' has hit YouTube's rolling 24-hour upload quota.")
            print("The episode video and assets are completely generated, saved locally, and ready to publish once quota resets.")
            status_val = "upload_limit_exceeded"
        else:
            status_val = "upload_failed"

        return {
            "video_id": None,
            "video_url": None,
            "title": title,
            "status": status_val,
            "error": err_msg
        }

if __name__ == "__main__":
    youtube = get_authenticated_service()
    if youtube:
        print("YouTube service is connected and ready to upload!")
    else:
        sys.exit(1)
