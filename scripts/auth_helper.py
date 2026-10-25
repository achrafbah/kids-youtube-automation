"""Interactive OAuth Authorization Helper for YouTube API.
Opens default browser with matching OAuth state and listens on local server to capture token.
"""

import os
import sys
import json
import secrets
from pathlib import Path

# Fix Windows console encoding for characters & emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_DIR = BASE_DIR / "credentials"
CLIENT_SECRET_FILE = CREDENTIALS_DIR / "client_secret.json"
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
AUTH_URL_FILE = CREDENTIALS_DIR / "auth_url.txt"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

def main():
    print("Initializing OAuth Flow...", flush=True)
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRET_FILE),
        scopes=SCOPES,
        redirect_uri="http://localhost:8080/"
    )

    state = secrets.token_urlsafe(32)
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        state=state
    )

    with open(AUTH_URL_FILE, "w", encoding="utf-8") as f:
        f.write(auth_url)

    print("\n" + "=" * 60)
    print("YOUTUBE OAUTH AUTHORIZATION URL:")
    print(auth_url)
    print("=" * 60 + "\n", flush=True)

    print("Waiting for authorization on http://localhost:8080/ ...", flush=True)
    try:
        creds = flow.run_local_server(
            port=8080,
            open_browser=True,
            prompt="consent",
            access_type="offline",
            state=state,
            timeout_seconds=300
        )
        with open(TOKEN_FILE, "w", encoding="utf-8") as token_f:
            token_f.write(creds.to_json())
        print("AUTH_SUCCESS: Token saved successfully!", flush=True)
    except Exception as e:
        print(f"AUTH_ERROR: {e}", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
