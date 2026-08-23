@echo off
cd /d "%~dp0"

REM Use the venv python directly. Do not use activate.bat: it only checks
REM that the folder exists, so it reports success even when the base
REM interpreter is gone.
if not exist "venv\Scripts\python.exe" (
    echo [エラー] venv が見つかりません。先に作成してください:
    echo     py -3.12 -m venv venv
    echo     venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

REM Read the browser tab title from config.py (single source of truth for
REM the version string). config.py holds constants only, so importing it
REM does not pull in pygame.
set "WEB_TITLE=Word Breaker"
for /f "delims=" %%v in ('"venv\Scripts\python.exe" -c "from config import WINDOW_TITLE; print(WINDOW_TITLE)"') do set "WEB_TITLE=%%v"
echo タイトル: %WEB_TITLE%
echo.

echo ========================================
echo Word Breaker (Web版) を起動しています...
echo ========================================
echo.
echo ブラウザで自動的に開きます。Ctrl+C で終了できます。
echo.
"venv\Scripts\python.exe" -m pygbag --title "%WEB_TITLE%" main.py

echo.
echo Server stopped.
pause
