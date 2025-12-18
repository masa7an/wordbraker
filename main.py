"""
Word Breaker - エントリーポイント
"""
import pygame
import sys
import asyncio
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from game import Game

# pygame初期化
pygame.init()

# 音声システム初期化（Web環境でエラーになる場合はスキップ）
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
except Exception as e:
    pass  # Web環境では音声初期化が失敗しても続行

# 画面設定
# Web環境ではフルスクリーン非対応のため、通常ウィンドウモードに変更
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Word Breaker")

async def main():
    """メイン関数（Web対応のためasync）"""
    game = Game(screen)
    await game.run()
    sys.exit()

# pygbag対応: asyncio.run()を使用
asyncio.run(main())

