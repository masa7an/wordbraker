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

echo ========================================
echo Word Breaker を起動しています...
echo ========================================
echo.
echo ESCキーで終了できます。
echo.
"venv\Scripts\python.exe" main.py

if errorlevel 1 (
    echo.
    echo [エラー] ゲームの実行中にエラーが発生しました。
    echo.
    pause
    exit /b 1
)

echo.
echo Game finished.
pause
