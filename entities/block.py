"""
ブロックエンティティ
"""
import pygame
from config import (
    BLOCK_WIDTH, BLOCK_HEIGHT,
    COLOR_BLOCK_CORRECT, COLOR_BLOCK_CORRECT_HIT,
    COLOR_BLOCK_INCORRECT, COLOR_BLOCK_DECORATIVE,
    BLOCK_CORRECT_HP
)


class BlockType:
    """ブロックタイプ定数"""
    CORRECT = "CORRECT"      # 正解ブロック（破壊可能）
    INCORRECT = "INCORRECT"  # 不正解ブロック（無敵）
    DECORATIVE = "DECORATIVE"  # 装飾ブロック（当たり判定なし）


class Block:
    """ブロッククラス"""
    
    def __init__(self, x, y, block_type, word_id=None, text=""):
        """
        ブロックを初期化
        Args:
            x: X座標
            y: Y座標
            block_type: ブロックタイプ（BlockType.CORRECT, INCORRECT, DECORATIVE）
            word_id: 単語ID（正解ブロックの場合）
            text: 表示テキスト（日本語の意味など）
        """
        self.width = BLOCK_WIDTH
        self.height = BLOCK_HEIGHT
        self.x = float(x)
        self.y = float(y)
        self.type = block_type
        self.word_id = word_id
        self.text = text
        self.destroyed = False
        
        # HP設定（正解ブロックのみ）
        if block_type == BlockType.CORRECT:
            self.hp = BLOCK_CORRECT_HP
        else:
            self.hp = 1  # 不正解・装飾ブロックは実質無敵
        
        # 色設定
        if block_type == BlockType.CORRECT:
            self.color = COLOR_BLOCK_CORRECT
        elif block_type == BlockType.INCORRECT:
            self.color = COLOR_BLOCK_INCORRECT
        else:  # DECORATIVE
            self.color = COLOR_BLOCK_DECORATIVE
        
        # Rectキャッシュ（毎フレーム生成を避ける）
        self._rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def hit(self):
        """
        ブロックに当たった時の処理
        Returns:
            bool: 破壊されたか（正解ブロックのみ、HPが0になった時True）
        """
        if self.type == BlockType.CORRECT and not self.destroyed:
            # HPを減らす
            self.hp -= 1
            
            # HPが0になったら破壊
            if self.hp <= 0:
                self.destroyed = True
                return True
            else:
                # 1回ヒット時（HP: 1）の視覚的フィードバック
                # 色を変更して単語を強調表示
                self.color = COLOR_BLOCK_CORRECT_HIT
                return False  # まだ破壊されていない
        elif self.type == BlockType.INCORRECT:
            # 不正解ブロックは音・エフェクトのみ（破壊されない）
            return False
        else:  # DECORATIVE
            # 装飾ブロックは当たり判定なし
            return False
    
    def is_destroyed(self):
        """
        ブロックが破壊されているか
        Returns:
            bool: 破壊されていればTrue
        """
        return self.destroyed
    
    def is_correct(self):
        """
        正解ブロックかどうか
        Returns:
            bool: 正解ブロックならTrue
        """
        return self.type == BlockType.CORRECT
    
    def is_incorrect(self):
        """
        不正解ブロックかどうか
        Returns:
            bool: 不正解ブロックならTrue
        """
        return self.type == BlockType.INCORRECT
    
    def has_collision(self):
        """
        当たり判定があるか
        Returns:
            bool: 当たり判定があればTrue（装飾ブロックはFalse）
        """
        return self.type != BlockType.DECORATIVE
    
    def get_rect(self):
        """
        ブロックの当たり判定用Rectを取得（キャッシュ使用）
        Returns:
            pygame.Rect: ブロックのRect
        """
        return self._rect
    
    def draw(self, screen, font=None, door_unlocked=False, correct_text=None, hard_mode=False):
        """
        ブロックを描画
        Args:
            screen: pygame.Surface
            font: テキスト表示用フォント（Noneの場合はテキスト非表示）
            door_unlocked: 扉がアンロックされているか
            correct_text: 正解テキスト（扉がアンロックされている場合、不正解ブロックに表示）
            hard_mode: ハードモードかどうか（Trueの場合、正解ブロックも赤色で表示）
        """
        if self.destroyed:
            return
        
        # ブロック本体を描画
        rect = self.get_rect()
        # ハードモード時、正解ブロックも赤色で表示
        draw_color = self.color
        if hard_mode and self.type == BlockType.CORRECT:
            draw_color = COLOR_BLOCK_INCORRECT  # 不正解ブロックと同じ色
        pygame.draw.rect(screen, draw_color, rect)
        
        # 枠線を描画（視認性向上）
        # 1回ヒット時（HP: 1）は太い枠線で強調表示
        if self.type == BlockType.CORRECT and self.hp == 1:
            # 強調表示：太い黄色の枠線
            pygame.draw.rect(screen, (255, 255, 100), rect, 4)
        else:
            # 通常表示：細い白の枠線
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)
        
        # テキスト表示（フォントが指定されている場合）
        if font:
            # 表示するテキストを決定
            display_text = self.text
            if door_unlocked and self.type == BlockType.INCORRECT and correct_text:
                # 扉がアンロックされている場合、不正解ブロックには正解テキストを表示
                display_text = correct_text
            
            if display_text:
                # 1回ヒット時（HP: 1）は太字で強調表示
                if self.type == BlockType.CORRECT and self.hp == 1:
                    # 強調表示：太字風に2回描画（オフセット）
                    text_color = (255, 255, 200)  # 明るい色
                    text_surface = font.render(display_text, True, text_color)
                    text_rect = text_surface.get_rect(center=rect.center)
                    # 太字効果：少しずらして2回描画
                    screen.blit(text_surface, (text_rect.x - 1, text_rect.y))
                    screen.blit(text_surface, (text_rect.x + 1, text_rect.y))
                    screen.blit(text_surface, (text_rect.x, text_rect.y - 1))
                    screen.blit(text_surface, (text_rect.x, text_rect.y + 1))
                    screen.blit(text_surface, text_rect)
                else:
                    # 通常表示
                    text_surface = font.render(display_text, True, (255, 255, 255))
                    text_rect = text_surface.get_rect(center=rect.center)
                    screen.blit(text_surface, text_rect)
    
    def get_pos(self):
        """
        ブロックの位置を取得
        Returns:
            tuple: (x, y)
        """
        return (self.x, self.y)

