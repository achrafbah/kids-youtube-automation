"""Interactive OAuth Authorization Helper for YouTube API.
"""

import sys
from pathlib import Path

# Fix Windows console encoding
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

class PromptMessage(str):
    def format(self, *args, **kwargs):
        url = kwargs.get("url", "")
        if url:
            with open(AUTH_URL_FILE, "w", encoding="utf-8") as f:
                f.write(url)
        msg = (
            "\n" + "=" * 60 + "\n"
            f"YOUTUBE OAUTH AUTHORIZATION URL:\n{url}\n"
            + "=" * 60 + "\n\nWaiting for authorization on http://localhost:8080/ ...\n"
        )
        print(msg, flush=True)
        return msg

def main():
    print("Initializing Clean OAuth Flow...", flush=True)
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRET_FILE),
        scopes=SCOPES
    )

    try:
        creds = flow.run_local_server(
            port=8080,
            open_browser=True,
            prompt="consent",
            access_type="offline",
            timeout_seconds=1800,
            authorization_prompt_message=PromptMessage("Please visit: {url}")
        )
        with open(TOKEN_FILE, "w", encoding="utf-8") as token_f:
            token_f.write(creds.to_json())
        print("AUTH_SUCCESS: Token saved successfully!", flush=True)
    except Exception as e:
        print(f"AUTH_ERROR: {e}", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
