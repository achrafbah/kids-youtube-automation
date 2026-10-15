@echo off
REM ========================================================
REM Tales of Wonder - Daily YouTube Automation (10:00 AM)
REM Executes the full multi-agent animation and upload pipeline
REM ========================================================

cd /d "C:\Users\SetupGame\.gemini\antigravity\scratch\kids-youtube-automation"

echo [%date% %time%] Starting Daily Kids Episode Automation... >> "output\daily_scheduler.log"

"C:\Users\SetupGame\.gemini\antigravity\scratch\kids-youtube-automation\.venv\Scripts\python.exe" "scripts\generate_daily_episode.py" >> "output\daily_scheduler.log" 2>&1

echo [%date% %time%] Daily Run Finished with exit code %ERRORLEVEL% >> "output\daily_scheduler.log"
