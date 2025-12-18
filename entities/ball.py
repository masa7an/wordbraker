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
        
        # パフォーマンス用：描画用Surfaceを事前作成（WASM環境でのdraw.circleコスト削減）
        surface_size = self.radius * 2
        self._surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
        pygame.draw.circle(
            self._surface,
            self.color,
            (self.radius, self.radius),  # Surface内の中心座標
            self.radius
        )
    
    def launch(self, mouse_x=None, direction=None, screen_width=1280):
        """
        ボールを発射（クリック時）
        Args:
            mouse_x: マウスのX座標（Noneの場合は使用しない）
            direction: 発射方向（-1: 左, 0: 中央/ランダム, 1: 右、Noneの場合はマウス位置を使用）
            screen_width: 画面幅（マウス位置の判定用）
        """
        if not self.launched:
            # 方向指定が優先（キーボード入力）
            if direction is not None:
                if direction == -1:
                    # 左向きの角度範囲（-45度～-15度）でランダム
                    angle_degrees = random.uniform(-45, -15)
                    angle_rad = math.radians(angle_degrees)
                    speed = math.sqrt(BALL_SPEED_X ** 2 + BALL_SPEED_Y ** 2)
                    self.vx = speed * math.sin(angle_rad)
                    self.vy = -speed * math.cos(angle_rad)  # 上向きなので負
                elif direction == 1:
                    # 右向きの角度範囲（15度～45度）でランダム
                    angle_degrees = random.uniform(15, 45)
                    angle_rad = math.radians(angle_degrees)
                    speed = math.sqrt(BALL_SPEED_X ** 2 + BALL_SPEED_Y ** 2)
                    self.vx = speed * math.sin(angle_rad)
                    self.vy = -speed * math.cos(angle_rad)  # 上向きなので負
                else:
                    # direction == 0: 中央/ランダム
                    self.vx = BALL_SPEED_X * random.choice([-1, 1])
                    self.vy = -BALL_SPEED_Y
            elif mouse_x is not None:
                # マウス位置に応じた発射角度を計算
                screen_center = screen_width / 2
                relative_x = mouse_x - screen_center  # 中央からの相対位置
                
                # 中央からの距離で判定（画面幅の20%以内は中央扱い）
                center_threshold = screen_width * 0.2
                
                if abs(relative_x) < center_threshold:
                    # 中央付近：従来通りランダム（左右どちらか）
                    self.vx = BALL_SPEED_X * random.choice([-1, 1])
                    self.vy = -BALL_SPEED_Y
                elif relative_x < 0:
                    # 左側：左向きの角度範囲（-45度～-15度）でランダム
                    angle_degrees = random.uniform(-45, -15)
                    angle_rad = math.radians(angle_degrees)
                    speed = math.sqrt(BALL_SPEED_X ** 2 + BALL_SPEED_Y ** 2)
                    self.vx = speed * math.sin(angle_rad)
                    self.vy = -speed * math.cos(angle_rad)  # 上向きなので負
                else:
                    # 右側：右向きの角度範囲（15度～45度）でランダム
                    angle_degrees = random.uniform(15, 45)
                    angle_rad = math.radians(angle_degrees)
                    speed = math.sqrt(BALL_SPEED_X ** 2 + BALL_SPEED_Y ** 2)
                    self.vx = speed * math.sin(angle_rad)
                    self.vy = -speed * math.cos(angle_rad)  # 上向きなので負
            else:
                # マウス位置も方向指定もない場合：従来通りランダム
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
        ボールを描画（事前作成したSurfaceをblit）
        Args:
            screen: pygame.Surface
        """
        screen.blit(
            self._surface,
            (int(self.x - self.radius), int(self.y - self.radius))
        )
    
    def get_pos(self):
        """
        ボールの位置を取得
        Returns:
            tuple: (x, y)
        """
        return (self.x, self.y)

