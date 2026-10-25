# 🌟 Tales of Wonder — Kids YouTube Automation Engine

> 📖 **المرجع المركزي الموحد للمشروع:** راجع الملف الشامل [MASTER_PROJECT_CENTRAL.md](MASTER_PROJECT_CENTRAL.md) للاطلاع على كل التفاصيل، الإعدادات، وطريقة العمل الموحدة.

Automated educational animated Shorts in Modern Standard Arabic for preschool & primary kids (ages 3–10) on YouTube channel **Tales of Wonder**.

Runs 100% in the cloud via **GitHub Actions** on a daily schedule without needing your computer powered on.

---

## 🚀 Key Features

* **🎙️ Voice Synthesis**: Gemini 3.8 Flash TTS (`gemini-3.8-flash-tts`) with expressive cartoon storytelling voice (`Kore`).
* **🎬 Real Animation & Kinetic Flow (Option 2)**:
  - Veo 3.1 Fast AI video generation with seamless auto-fallback.
  - Multi-shot kinetic camera motion & floating animated golden stars (`sinusoidal floating physics`).
* **✨ Arabic Subtitles & Badges (Option 3)**:
  - Synchronized sentence-by-sentence subtitle cards with full Arabic Tashkeel (diacritics).
  - Glowing pedagogical header badge at the top.
* **🛡️ Anti-Duplication Engine**:
  - Automatically picks non-repeated curriculum topics from `data/topics_history.json`.
  - Automatically commits & pushes updated history back to the repo after each run.
* **📺 YouTube Deployment**:
  - Automatically uploads to YouTube channel 'Tales of Wonder' as **Private / Draft** with custom high-res thumbnail.
  - Marked as *Made for Kids* (COPPA compliant).

---

## ⚙️ Cloud Automation Setup (GitHub Actions)

### 1. Push to GitHub
Create a new private or public repository on GitHub (e.g. `kids-youtube-automation`) and run:
```bash
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git branch -M main
git push -u origin main
```

### 2. Configure GitHub Repository Secrets
Go to your GitHub repository:
**Settings** ➔ **Secrets and variables** ➔ **Actions** ➔ **New repository secret**

Add these 3 secrets:

| Secret Name | Description | Value |
|---|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API Key | `AQ.Ab8RN6Ly...` |
| `YOUTUBE_CLIENT_SECRET_JSON` | Content of `credentials/client_secret.json` | `{"installed":{"client_id":...` |
| `YOUTUBE_TOKEN_JSON` | Content of `credentials/token.json` | `{"token":"ya29...","refresh_token":...` |

### 3. Automatic Daily Schedule
The GitHub Actions workflow [`.github/workflows/daily_automation.yml`](.github/workflows/daily_automation.yml) is scheduled to run every day at **08:00 AM UTC** (`cron: '0 8 * * *'`).

You can also trigger it manually at any time by going to:
**Actions tab** ➔ **Daily Kids Episode Automation** ➔ **Run workflow**.

---

## 📂 Project Structure

```text
kids-youtube-automation/
├── .github/
│   └── workflows/
│       └── daily_automation.yml     # Cloud CI/CD daily automation schedule
├── assets/
│   └── fonts/
│       └── Arial.ttf                # Bundled cross-platform Arabic font
├── characters/
│   ├── scenes/                      # 3D Pixar scene canvases & BGM
│   └── character_bible.json         # Character traits & visual specs
├── data/
│   └── topics_history.json          # Anti-duplication curriculum database
├── production_studio/
│   ├── animation_engine.py          # Option 2 & 3 kinetic engine & subtitles
│   ├── motion_animator.py           # Video motion director
│   ├── orchestrator.py              # Studio multi-agent coordinator
│   └── ...
├── scripts/
│   ├── generate_daily_episode.py    # Main daily execution script
│   └── youtube_uploader.py          # YouTube Data API v3 uploader
├── requirements.txt                 # Python dependencies
└── README.md
```
