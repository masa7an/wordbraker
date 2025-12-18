"""
当たり判定システム
"""
import pygame
from entities.ball import Ball
from entities.paddle import Paddle
from entities.block import Block
from entities.door import Door


def check_ball_wall_collision(ball, screen_width, screen_height):
    """
    ボールと壁の当たり判定
    Args:
        ball: Ballオブジェクト
        screen_width: 画面幅
        screen_height: 画面高さ
    Returns:
        tuple: (左右の壁に当たった, 上の壁に当たった, 下に落ちた)
    """
    hit_left_right = False
    hit_top = False
    fell_bottom = False
    
    # 左右の壁
    if ball.x - ball.radius <= 0:
        ball.x = ball.radius
        ball.reflect_x()
        hit_left_right = True
    elif ball.x + ball.radius >= screen_width:
        ball.x = screen_width - ball.radius
        ball.reflect_x()
        hit_left_right = True
    
    # 上の壁
    if ball.y - ball.radius <= 0:
        ball.y = ball.radius
        ball.reflect_y()
        hit_top = True
    
    # 下に落ちた（画面外）
    if ball.y > screen_height + ball.radius:
        fell_bottom = True
    
    return (hit_left_right, hit_top, fell_bottom)


def check_ball_paddle_collision(ball, paddle):
    """
    ボールとパドルの当たり判定
    Args:
        ball: Ballオブジェクト
        paddle: Paddleオブジェクト
    Returns:
        bool: 当たったかどうか
    """
    ball_rect = ball.get_rect()
    paddle_rect = paddle.get_rect()
    
    if ball_rect.colliderect(paddle_rect):
        # ボールがパドルの上側に当たった場合のみ反射
        if ball.vy > 0:  # ボールが下向きの場合
            # パドル中央からの距離で反射角度を調整（移動方向も考慮）
            paddle_move_dir = paddle.get_move_direction()
            ball.reflect_paddle(paddle.x, paddle.width, paddle_move_dir)
            
            # ボールをパドルの上に配置（重なりを解消）
            ball.y = paddle.y - ball.radius
            return True
    
    return False


def check_ball_block_collision(ball, block, door_unlocked=False):
    """
    ボールとブロックの当たり判定
    Args:
        ball: Ballオブジェクト
        block: Blockオブジェクト
        door_unlocked: 扉がアンロックされているか（Trueの場合、不正解ブロックの当たり判定を無効化）
    Returns:
        bool: 当たったかどうか（破壊されたかどうかは別途確認）
    """
    # 装飾ブロックは当たり判定なし
    if not block.has_collision():
        return False
    
    # 破壊済みブロックは当たり判定なし
    if block.is_destroyed():
        return False
    
    # 扉がアンロックされている場合、不正解ブロックの当たり判定を無効化
    if door_unlocked and block.is_incorrect():
        return False
    
    ball_rect = ball.get_rect()
    block_rect = block.get_rect()
    
    if ball_rect.colliderect(block_rect):
        # より正確な当たり方向の判定
        # ボールの前フレーム位置を推定（速度から逆算）
        prev_x = ball.x - ball.vx
        prev_y = ball.y - ball.vy
        
        # ブロックの各辺の座標
        block_left = block.x
        block_right = block.x + block.width
        block_top = block.y
        block_bottom = block.y + block.height
        block_center_x = block.x + block.width / 2
        block_center_y = block.y + block.height / 2
        
        # 前フレームでどの辺に近かったかで判定
        dist_to_left = abs(prev_x - block_left)
        dist_to_right = abs(prev_x - block_right)
        dist_to_top = abs(prev_y - block_top)
        dist_to_bottom = abs(prev_y - block_bottom)
        
        # 最小距離の辺を特定
        min_dist = min(dist_to_left, dist_to_right, dist_to_top, dist_to_bottom)
        
        # 横方向の当たり（左右から）
        if min_dist == dist_to_left or min_dist == dist_to_right:
            ball.reflect_x()
            # 位置補正（ブロックの外側に確実に配置）
            if prev_x < block_center_x:
                ball.x = block_left - ball.radius - 1  # 少し余裕を持たせる
            else:
                ball.x = block_right + ball.radius + 1
        else:
            # 縦方向の当たり（上下から）
            ball.reflect_y()
            # 位置補正（ブロックの外側に確実に配置）
            if prev_y < block_center_y:
                ball.y = block_top - ball.radius - 1  # 少し余裕を持たせる
            else:
                ball.y = block_bottom + ball.radius + 1
        
        return True
    
    return False


def check_ball_door_collision(ball, door):
    """
    ボールと扉の当たり判定
    Args:
        ball: Ballオブジェクト
        door: Doorオブジェクト
    Returns:
        bool: 当たったかどうか（アンロック状態の場合のみ）
    """
    if door.is_locked():
        return False
    
    ball_rect = ball.get_rect()
    door_rect = door.get_rect()
    
    if ball_rect.colliderect(door_rect):
        return True
    
    return False


def check_ball_blocks_collision(ball, blocks, door_unlocked=False):
    """
    ボールと複数のブロックの当たり判定
    Args:
        ball: Ballオブジェクト
        blocks: Blockオブジェクトのリスト
        door_unlocked: 扉がアンロックされているか（Trueの場合、不正解ブロックの当たり判定を無効化）
    Returns:
        tuple: (当たったブロック, 破壊されたかどうか)
    """
    for block in blocks:
        if check_ball_block_collision(ball, block, door_unlocked):
            destroyed = block.hit()
            return (block, destroyed)
    
    return (None, False)

