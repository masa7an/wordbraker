"""
扉（ゴール）エンティティ
"""
import pygame
from config import (
    DOOR_WIDTH, DOOR_HEIGHT, DOOR_X, DOOR_Y,
    COLOR_DOOR_LOCKED, COLOR_DOOR_UNLOCKED
)


class Door:
    """扉クラス"""
    
    def __init__(self):
        """扉を初期化"""
        self.width = DOOR_WIDTH
        self.height = DOOR_HEIGHT
        self.x = DOOR_X
        self.y = DOOR_Y
        self.locked = True  # 初期状態はロック
        self.color = COLOR_DOOR_LOCKED
        
        # Rectキャッシュ（毎フレーム生成を避ける）
        self._rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        
        # 描画用Surfaceキャッシュ（WASM環境でのdraw.rectコスト削減）
        self._surface = None  # 状態が変わった時だけ再作成
        self._cached_locked = None
    
    def unlock(self):
        """扉をアンロック（全正解ブロック破壊時）"""
        self.locked = False
        self.color = COLOR_DOOR_UNLOCKED
    
    def is_locked(self):
        """
        扉がロックされているか
        Returns:
            bool: ロックされていればTrue
        """
        return self.locked
    
    def is_unlocked(self):
        """
        扉がアンロックされているか
        Returns:
            bool: アンロックされていればTrue
        """
        return not self.locked
    
    def get_rect(self):
        """
        扉の当たり判定用Rectを取得（キャッシュ使用）
        Returns:
            pygame.Rect: 扉のRect
        """
        return self._rect
    
    def _create_surface(self):
        """
        扉の描画用Surfaceを作成（状態が変わった時だけ呼ばれる）
        Returns:
            pygame.Surface: 扉の描画用Surface
        """
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # 扉本体を描画
        pygame.draw.rect(surface, self.color, (0, 0, self.width, self.height))
        
        # 枠線を描画
        border_color = (200, 200, 200) if self.locked else (100, 255, 100)
        pygame.draw.rect(surface, border_color, (0, 0, self.width, self.height), 3)
        
        return surface
    
    def draw(self, screen, font=None):
        """
        扉を描画（Surface blitを使用、WASM環境対応）
        Args:
            screen: pygame.Surface
            font: テキスト表示用フォント（Noneの場合はテキスト非表示）
        """
        # 状態が変わった時だけSurfaceを再作成
        if self._surface is None or self._cached_locked != self.locked:
            self._surface = self._create_surface()
            self._cached_locked = self.locked
        
        # Surfaceをblit（毎フレームのdraw.rectを避ける）
        screen.blit(self._surface, (self._rect.x, self._rect.y))
        
        # テキスト表示（フォントが指定されている場合）
        if font:
            if self.locked:
                text = "LOCKED"
            else:
                text = "GOAL"
            
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.get_rect().center)
            screen.blit(text_surface, text_rect)
    
    def reset(self):
        """扉をリセット（ステージ開始時）"""
        self.locked = True
        self.color = COLOR_DOOR_LOCKED
        # Surfaceキャッシュをクリア（状態が変わったので再作成が必要）
        self._surface = None
        self._cached_locked = None

