"""TikTok OAuth2 v2 Authentication Helper.
Handles URL generation, authorization code exchange, and token refresh.
"""

import os
import sys
import json
import urllib.parse
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
CREDENTIALS_DIR = BASE_DIR / "credentials"
CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)

CLIENT_FILE = CREDENTIALS_DIR / "tiktok_client.json"
TOKEN_FILE = CREDENTIALS_DIR / "tiktok_token.json"

AUTH_BASE_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_ENDPOINT = "https://open.tiktokapis.com/v2/oauth/token/"

DEFAULT_SCOPES = ["user.info.basic", "video.upload", "video.publish"]

def get_client_credentials():
    """Load client_key, client_secret, and redirect_uri from file or env."""
    client_key = os.environ.get("TIKTOK_CLIENT_KEY")
    client_secret = os.environ.get("TIKTOK_CLIENT_SECRET")
    redirect_uri = os.environ.get("TIKTOK_REDIRECT_URI", "https://achrafbah.github.io/kids-youtube-automation/")

    if CLIENT_FILE.exists():
        try:
            with open(CLIENT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                client_key = client_key or data.get("client_key")
                client_secret = client_secret or data.get("client_secret")
                redirect_uri = redirect_uri or data.get("redirect_uri")
        except Exception as e:
            print(f"Warning reading tiktok_client.json: {e}")

    if not client_key or not client_secret:
        raise ValueError("Missing TIKTOK_CLIENT_KEY or TIKTOK_CLIENT_SECRET")

    return client_key, client_secret, redirect_uri

def generate_authorization_url(state="tales_auth"):
    """Generate TikTok user authorization URL."""
    client_key, _, redirect_uri = get_client_credentials()
    params = {
        "client_key": client_key,
        "scope": ",".join(DEFAULT_SCOPES),
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "state": state
    }
    url = f"{AUTH_BASE_URL}?{urllib.parse.urlencode(params)}"
    return url

def exchange_code_for_token(code):
    """Exchange authorization code for access and refresh tokens."""
    client_key, client_secret, redirect_uri = get_client_credentials()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }
    payload = {
        "client_key": client_key,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }
    
    print(f"Exchanging code for token with TikTok API...", flush=True)
    res = requests.post(TOKEN_ENDPOINT, data=payload, headers=headers)
    data = res.json()
    
    if res.status_code == 200 and "data" in data and "access_token" in data["data"]:
        token_info = data["data"]
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(token_info, f, indent=2)
        print(" Successfully retrieved and saved TikTok tokens to credentials/tiktok_token.json")
        return token_info
    else:
        print(f" Failed to exchange code. Response: {data}")
        return None

def refresh_access_token():
    """Refresh the access token using the stored refresh_token."""
    client_key, client_secret, _ = get_client_credentials()
    
    # Restore token from env if missing
    if not TOKEN_FILE.exists() and os.environ.get("TIKTOK_TOKEN_JSON"):
        try:
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(os.environ["TIKTOK_TOKEN_JSON"])
        except Exception:
            pass
            
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(f"Missing {TOKEN_FILE} and TIKTOK_TOKEN_JSON not set.")
        
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        token_data = json.load(f)
        
    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        raise ValueError("No refresh_token found in token file.")
        
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }
    payload = {
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    res = requests.post(TOKEN_ENDPOINT, data=payload, headers=headers)
    data = res.json()
    
    if res.status_code == 200 and "data" in data and "access_token" in data["data"]:
        new_token = data["data"]
        token_data.update(new_token)
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)
        return token_data["access_token"]
    else:
        print(f"Token refresh failed: {data}")
        # Return existing access_token as fallback if still valid
        return token_data.get("access_token")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--url":
        print(generate_authorization_url())
    elif len(sys.argv) > 2 and sys.argv[1] == "--code":
        exchange_code_for_token(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == "--refresh":
        print(refresh_access_token())
    else:
        print("Usage:")
        print("  python scripts/tiktok_auth.py --url")
        print("  python scripts/tiktok_auth.py --code <code>")
        print("  python scripts/tiktok_auth.py --refresh")
