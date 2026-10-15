"""Interactive OAuth Authorization Helper for YouTube API.
Generates the authorization URL, opens the default browser directly via Windows,
and listens on a local server to capture the token.
"""

import os
import sys
import json
from pathlib import Path

# Unbuffered stdout
sys.stdout.reconfigure(line_buffering=True)

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

    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true"
    )

    print(f"\nAUTH_URL_START\n{auth_url}\nAUTH_URL_END\n", flush=True)

    with open(AUTH_URL_FILE, "w", encoding="utf-8") as f:
        f.write(auth_url)

    # Force open browser on Windows
    try:
        os.startfile(auth_url)
        print("Browser launch attempted via os.startfile.", flush=True)
    except Exception as e:
        print(f"Could not auto-open browser: {e}", flush=True)

    print("Waiting for callback on http://localhost:8080/ ...", flush=True)
    try:
        creds = flow.run_local_server(port=8080, open_browser=False)
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print("AUTH_SUCCESS: Token saved successfully!", flush=True)
    except Exception as e:
        print(f"AUTH_ERROR: {e}", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
