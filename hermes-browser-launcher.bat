@echo off
REM Hermes Browser Launcher -- starts headless Chrome on 9222 then Hermes
REM The cdp_url in config.yaml points browser tool to this Chrome instance
REM This avoids the "Chrome exited early" crash when your normal Chrome profile is locked
REM
REM Usage: double-click this file, or run from terminal

echo Starting headless Chrome on port 9222...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --remote-debugging-port=9222 --user-data-dir="C:\tmp\chrome-hermes" --no-first-run --no-default-browser-check --disable-gpu --no-sandbox

echo Waiting for Chrome to start...
timeout /t 3 /nobreak >nul

echo Chrome is running on http://127.0.0.1:9222
echo Starting Hermes...
hermes