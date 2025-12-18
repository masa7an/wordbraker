"""
パドルエンティティ
"""
import pygame
import math
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT,
    PADDLE_SPEED, COLOR_PADDLE
)


class Paddle:
    """パドルクラス"""
    
    def __init__(self, x, y):
        """
        パドルを初期化
        Args:
            x: 初期X座標
            y: 初期Y座標
        """
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = float(x)
        self.y = float(y)
        self.speed = PADDLE_SPEED
        self.color = COLOR_PADDLE
        self.prev_x = float(x)  # 前フレームのX座標（移動方向判定用）
        self.move_direction = 0  # -1: 左移動, 0: 停止, 1: 右移動（反射の角度計算用、描画には使用しない）
        
        # Rectキャッシュ（毎フレーム生成を避ける）
        self._rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        
        # 描画用Surfaceキャッシュ（WASM環境でのdraw.rectコスト削減）
        self._surface = None  # 通常描画用（傾き表示なし、常に水平）
    
    def update(self, mouse_x):
        """
        マウス位置に追従
        Args:
            mouse_x: マウスのX座標
        """
        # 前フレームの位置を保存
        self.prev_x = self.x
        
        # パドル中央をマウス位置に合わせる
        target_x = mouse_x - self.width / 2
        
        # 画面外に出ないように制限
        target_x = max(0, min(target_x, SCREEN_WIDTH - self.width))
        
        self.x = target_x
        
        # Rectキャッシュを更新
        self._rect.x = int(self.x)
        
        # 移動方向を判定（反射の角度計算用、描画には使用しない）
        dx = self.x - self.prev_x
        if abs(dx) < 0.1:  # ほぼ停止
            self.move_direction = 0
        elif dx > 0:  # 右移動
            self.move_direction = 1
        else:  # 左移動
            self.move_direction = -1
    
    def get_rect(self):
        """
        パドルの当たり判定用Rectを取得（キャッシュ使用）
        Returns:
            pygame.Rect: パドルのRect
        """
        return self._rect
    
    def _create_surface(self):
        """
        パドルの描画用Surfaceを作成（常に水平）
        Returns:
            pygame.Surface: パドルの描画用Surface
        """
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.color, (0, 0, self.width, self.height))
        return surface
    
    def draw(self, screen):
        """
        パドルを描画（傾き表示なし、常に水平、Surface blitを使用）
        Args:
            screen: pygame.Surface
        """
        # 常に通常描画（傾き表示なし）
        if self._surface is None:
            self._surface = self._create_surface()
        
        screen.blit(self._surface, (self._rect.x, self._rect.y))
    
    def get_pos(self):
        """
        パドルの位置を取得
        Returns:
            tuple: (x, y)
        """
        return (self.x, self.y)
    
    def get_center_x(self):
        """
        パドルの中央X座標を取得
        Returns:
            float: 中央X座標
        """
        return self.x + self.width / 2
    
    def get_move_direction(self):
        """
        パドルの移動方向を取得
        Returns:
            int: -1（左移動）, 0（停止）, 1（右移動）
        """
        return self.move_direction

