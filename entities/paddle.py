"""
パドルエンティティ
"""
import pygame
import math
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT,
    PADDLE_SPEED, COLOR_PADDLE, PADDLE_ANGLE_DEGREES
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
        self.move_direction = 0  # -1: 左移動, 0: 停止, 1: 右移動
        self.angle = 0  # パドルの傾き角度（度）
        
        # Rectキャッシュ（毎フレーム生成を避ける）
        self._rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        
        # 描画用Surfaceキャッシュ（WASM環境でのdraw.rectコスト削減）
        self._surface = None  # 通常描画用（角度0の時）
        self._rotated_surface = None  # 回転描画用（角度が0以外の時）
        self._cached_angle = None
    
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
        
        # 移動方向を判定
        dx = self.x - self.prev_x
        if abs(dx) < 0.1:  # ほぼ停止
            self.move_direction = 0
            self.angle = 0
        elif dx > 0:  # 右移動
            self.move_direction = 1
            self.angle = PADDLE_ANGLE_DEGREES
        else:  # 左移動
            self.move_direction = -1
            self.angle = -PADDLE_ANGLE_DEGREES
    
    def get_rect(self):
        """
        パドルの当たり判定用Rectを取得（キャッシュ使用）
        Returns:
            pygame.Rect: パドルのRect
        """
        return self._rect
    
    def _create_surface(self):
        """
        パドルの描画用Surfaceを作成（角度0の時）
        Returns:
            pygame.Surface: パドルの描画用Surface
        """
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.color, (0, 0, self.width, self.height))
        return surface
    
    def _create_rotated_surface(self):
        """
        パドルの回転描画用Surfaceを作成（角度が0以外の時）
        Returns:
            tuple: (rotated_surface, rotated_rect)
        """
        # 基本Surfaceを作成（キャッシュがあれば再利用）
        if self._surface is None:
            self._surface = self._create_surface()
        
        # 回転
        rotated_surface = pygame.transform.rotate(self._surface, -self.angle)
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        rotated_rect = rotated_surface.get_rect(center=(center_x, center_y))
        
        return (rotated_surface, rotated_rect)
    
    def draw(self, screen):
        """
        パドルを描画（移動方向に応じて傾きを表示、Surface blitを使用）
        Args:
            screen: pygame.Surface
        """
        # 角度が変わった時だけSurfaceを再作成
        if abs(self.angle) > 0.1:
            # 回転描画
            if self._cached_angle != self.angle:
                # 角度が変わった時、回転Surfaceを再作成
                self._rotated_surface, self._rotated_rect = self._create_rotated_surface()
                self._cached_angle = self.angle
            else:
                # 角度は同じだが、位置が変わった可能性があるので位置を更新
                center_x = self.x + self.width / 2
                center_y = self.y + self.height / 2
                if self._rotated_surface is not None:
                    self._rotated_rect = self._rotated_surface.get_rect(center=(center_x, center_y))
            
            if self._rotated_surface is not None:
                screen.blit(self._rotated_surface, self._rotated_rect)
        else:
            # 通常描画（角度0の時）
            if self._cached_angle != 0:
                # 角度が0に戻った時、通常Surfaceを作成
                self._surface = self._create_surface()
                self._cached_angle = 0
                self._rotated_surface = None
            
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

