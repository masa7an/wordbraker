"""
スコア管理システム
"""
from config import (
    SCORE_BLOCK_DESTROY, COMBO_THRESHOLD, COMBO_MULTIPLIER,
    PERFECT_BONUS_MULTIPLIER, INITIAL_LIFES
)


class ScoreManager:
    """スコア管理クラス"""
    
    def __init__(self):
        """スコアマネージャーを初期化"""
        self.score = 0
        self.combo_count = 0  # 連続正解カウント
        self.combo_multiplier = 1.0  # 現在のコンボ倍率
        self.initial_lifes = INITIAL_LIFES
        self.current_lifes = INITIAL_LIFES
        self.miss_count = 0  # ミス回数（ライフ減少回数）
        self.perfect = True  # ノーミスかどうか
    
    def add_block_score(self):
        """
        正解ブロック破壊時のスコア加算
        Returns:
            int: 加算されたスコア
        """
        # コンボカウント増加
        self.combo_count += 1
        
        # コンボ倍率計算（3回ごとに×1.2）
        combo_level = self.combo_count // COMBO_THRESHOLD
        self.combo_multiplier = 1.0 + (combo_level * (COMBO_MULTIPLIER - 1.0))
        
        # スコア計算
        base_score = SCORE_BLOCK_DESTROY
        added_score = int(base_score * self.combo_multiplier)
        self.score += added_score
        
        return added_score
    
    def reset_combo(self):
        """コンボをリセット（不正解ブロック命中 or ミス時）"""
        self.combo_count = 0
        self.combo_multiplier = 1.0
    
    def lose_life(self):
        """
        ライフを減らす（ボール落下時）
        Returns:
            bool: ゲームオーバーかどうか
        """
        self.current_lifes -= 1
        self.miss_count += 1
        self.perfect = False
        self.reset_combo()
        
        return self.current_lifes <= 0
    
    def is_game_over(self):
        """
        ゲームオーバーかどうか
        Returns:
            bool: ゲームオーバーならTrue
        """
        return self.current_lifes <= 0
    
    def get_final_score(self):
        """
        最終スコアを取得（ノーミスボーナス適用）
        Returns:
            int: 最終スコア
        """
        if self.perfect:
            return int(self.score * PERFECT_BONUS_MULTIPLIER)
        return self.score
    
    def is_perfect(self):
        """
        ノーミスかどうか
        Returns:
            bool: ノーミスならTrue
        """
        return self.perfect
    
    def reset(self):
        """スコアをリセット（ゲーム開始時）"""
        self.score = 0
        self.combo_count = 0
        self.combo_multiplier = 1.0
        self.current_lifes = self.initial_lifes
        self.miss_count = 0
        self.perfect = True
    
    def continue_game(self):
        """コンティニュー処理（ライフ全回復、スコア保持）"""
        self.current_lifes = self.initial_lifes
        # スコアは保持（リセットしない）
    
    def get_score(self):
        """
        現在のスコアを取得
        Returns:
            int: 現在のスコア
        """
        return self.score
    
    def get_combo_count(self):
        """
        現在のコンボカウントを取得
        Returns:
            int: コンボカウント
        """
        return self.combo_count
    
    def get_combo_multiplier(self):
        """
        現在のコンボ倍率を取得
        Returns:
            float: コンボ倍率
        """
        return self.combo_multiplier
    
    def get_lifes(self):
        """
        現在のライフを取得
        Returns:
            int: 現在のライフ
        """
        return self.current_lifes

