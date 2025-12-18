"""
ボールエンティティ
"""
import pygame
import random
import math
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BALL_RADIUS,
    BALL_SPEED_X, BALL_SPEED_Y, BALL_MAX_VX,
    COLOR_BALL, WALL_BLOCK_BOUNCE_DAMPING,
    PADDLE_ANGLE_TAN, PADDLE_BOUNCE_SPEED_BOOST
)


class Ball:
    """ボールクラス"""
    
    def __init__(self, x, y):
        """
        ボールを初期化
        Args:
            x: 初期X座標
            y: 初期Y座標
        """
        self.radius = BALL_RADIUS
        self.x = float(x)
        self.y = float(y)
        
        # 初期速度（x方向はランダム符号）
        self.vx = BALL_SPEED_X * random.choice([-1, 1])
        self.vy = -BALL_SPEED_Y  # 上向き
        
        # 発射待ち状態
        self.launched = False
        
        # 色
        self.color = COLOR_BALL
        
        # パフォーマンス用：定数キャッシュ（WASM環境での関数内import回避）
        self._wall_damping = WALL_BLOCK_BOUNCE_DAMPING
        self._max_vx = BALL_MAX_VX
        self._angle_tan = PADDLE_ANGLE_TAN
        self._bounce_boost = PADDLE_BOUNCE_SPEED_BOOST
        
        # Rectキャッシュ（毎フレーム生成を避ける）
        self._rect = pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2
        )
    
    def launch(self):
        """ボールを発射（クリック時）"""
        if not self.launched:
            # x方向の速度をランダム符号で設定
            self.vx = BALL_SPEED_X * random.choice([-1, 1])
            self.vy = -BALL_SPEED_Y
            self.launched = True
    
    def update(self, dt=1.0):
        """
        ボールを更新
        Args:
            dt: デルタタイム（フレームレート補正用、デフォルト1.0）
        """
        if not self.launched:
            return
        
        # 位置更新
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Rectキャッシュを更新
        self._rect.x = int(self.x - self.radius)
        self._rect.y = int(self.y - self.radius)
    
    def reflect_x(self):
        """X方向の速度を反転（左右の壁やブロックに当たった時、速度を20%減らす）"""
        self.vx = -self.vx * self._wall_damping
    
    def reflect_y(self):
        """Y方向の速度を反転（上下の壁やブロックに当たった時、速度を20%減らす）"""
        self.vy = -self.vy * self._wall_damping
    
    def reflect_paddle(self, paddle_x, paddle_width, paddle_move_direction=0):
        """
        パドルに当たった時の反射
        Args:
            paddle_x: パドルのX座標
            paddle_width: パドルの幅
            paddle_move_direction: パドルの移動方向（-1: 左, 0: 停止, 1: 右）
        """
        # パドル中央からの距離（-1.0 ～ 1.0）
        paddle_center = paddle_x + paddle_width / 2
        hit_pos = (self.x - paddle_center) / (paddle_width / 2)
        hit_pos = max(-1.0, min(1.0, hit_pos))  # クランプ
        
        # x方向の速度をパドル位置に応じて調整（係数を0.3倍に減らして予測しやすく）
        base_vx = hit_pos * self._max_vx * 0.3
        
        # パドルの移動方向に応じて角度を追加（主な角度制御）
        if paddle_move_direction != 0:
            # 30度の角度を速度に変換（tan(30°) ≈ 0.577）
            angle_effect = abs(self.vy) * self._angle_tan * paddle_move_direction
            self.vx = base_vx + angle_effect
        else:
            self.vx = base_vx
        
        # y方向は常に反転（上向き）
        self.vy = -abs(self.vy)  # 常に上向きにする
        
        # パドル反射時に速度を+1増やす（ラケットで打ち返すイメージ）
        current_speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        new_speed = current_speed + self._bounce_boost
        
        # 速度の方向を保ったまま、速度の大きさを増やす
        if current_speed > 0:
            speed_ratio = new_speed / current_speed
            self.vx *= speed_ratio
            self.vy *= speed_ratio
    
    def reset(self, x, y):
        """
        ボールをリセット（落下時など）
        Args:
            x: 新しいX座標
            y: 新しいY座標
        """
        self.x = float(x)
        self.y = float(y)
        self.vx = 0
        self.vy = 0
        self.launched = False
    
    def is_out_of_bounds(self):
        """
        ボールが画面外（下）に落ちたかチェック
        Returns:
            bool: 画面外ならTrue
        """
        return self.y > SCREEN_HEIGHT + self.radius
    
    def get_rect(self):
        """
        ボールの当たり判定用Rectを取得（キャッシュ使用）
        Returns:
            pygame.Rect: ボールのRect
        """
        return self._rect
    
    def draw(self, screen):
        """
        ボールを描画
        Args:
            screen: pygame.Surface
        """
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
    
    def get_pos(self):
        """
        ボールの位置を取得
        Returns:
            tuple: (x, y)
        """
        return (self.x, self.y)

