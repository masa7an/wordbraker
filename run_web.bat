@echo off
REM Word Breaker - Web版実行用バッチファイル（仮想環境用）
REM pygbagでローカルサーバーを起動します

echo ========================================
echo Word Breaker (Web版) を起動しています...
echo ========================================
echo.

REM ブラウザのタブに出すタイトルを config.py から取得する
REM （バージョン表記の単一の情報源。config.py の VERSION を変えればここも追従する）
REM ※ venvのアクティベート前に実行する。config.py は定数のみでpygame等に依存しないため。
set "WEB_TITLE=Word Breaker"
for /f "delims=" %%v in ('python -c "from config import WINDOW_TITLE; print(WINDOW_TITLE)"') do set "WEB_TITLE=%%v"
echo タイトル: %WEB_TITLE%
echo.

REM 仮想環境をアクティベート
call venv\Scripts\activate

REM pygbagでゲームを起動
echo pygbagでローカルサーバーを起動します...
echo ブラウザで自動的に開きます。
echo Ctrl+C で終了できます。
echo.
pygbag --title "%WEB_TITLE%" main.py

REM 正常終了
echo.
echo サーバーを終了しました。
pause

