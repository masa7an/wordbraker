@echo off
REM Word Breaker - 実行用バッチファイル
REM 直接Pythonでゲームを起動します

echo ========================================
echo Word Breaker を起動しています...
echo ========================================
echo.

REM Pythonがインストールされているか確認
REM pygameがインストールされているか確認


REM ゲームを起動
echo ゲームを起動します...
echo ESCキーで終了できます。
echo.
python main.py

REM エラーが発生した場合
if errorlevel 1 (
    echo.
    echo [エラー] ゲームの実行中にエラーが発生しました。
    echo.
    pause
    exit /b 1
)

REM 正常終了
echo.
echo ゲームを終了しました。
pause

