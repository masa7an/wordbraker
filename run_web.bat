@echo off
REM Word Breaker - Web版実行用バッチファイル（仮想環境用）
REM pygbagでローカルサーバーを起動します

echo ========================================
echo Word Breaker (Web版) を起動しています...
echo ========================================
echo.

REM 仮想環境をアクティベート
call venv\Scripts\activate

REM pygbagでゲームを起動
echo pygbagでローカルサーバーを起動します...
echo ブラウザで自動的に開きます。
echo Ctrl+C で終了できます。
echo.
pygbag main.py

REM 正常終了
echo.
echo サーバーを終了しました。
pause

