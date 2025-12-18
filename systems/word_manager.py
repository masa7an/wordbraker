"""
単語管理システム（学習制御ロジック）
"""
import json
import random
from config import WORDS_JSON_PATH, WordState, WORDS_PER_STAGE_MIN, WORDS_PER_STAGE_MAX, NEW_WORDS_PER_STAGE_MAX


class WordManager:
    """単語管理クラス"""
    
    def __init__(self):
        """単語マネージャーを初期化"""
        self.words = []  # 全単語データ
        self.word_states = {}  # {word_id: WordState}
        self.missed_words = {}  # {word_id: miss_count} 不正解選択肢に当てた回数
        self.load_words()
    
    def load_words(self):
        """英単語データをJSONから読み込み"""
        try:
            with open(WORDS_JSON_PATH, 'r', encoding='utf-8') as f:
                self.words = json.load(f)
            
            # 初期状態を設定
            for word in self.words:
                word_id = word['id']
                self.word_states[word_id] = WordState.UNSEEN
                self.missed_words[word_id] = 0
            
        except FileNotFoundError:
            print(f"エラー: {WORDS_JSON_PATH} が見つかりません")
            self.words = []
        except json.JSONDecodeError:
            print(f"エラー: {WORDS_JSON_PATH} のJSON形式が不正です")
            self.words = []
    
    def get_stage_words(self, stage_num):
        """
        ステージ用の単語を選択
        Args:
            stage_num: ステージ番号（1始まり）
        Returns:
            list: 選択された単語データのリスト
        """
        # ミスした単語（再出題対象）
        review_words = [
            word for word in self.words
            if self.word_states.get(word['id']) == WordState.MISSED
        ]
        
        # 未出題の単語
        unseen_words = [
            word for word in self.words
            if self.word_states.get(word['id']) == WordState.UNSEEN
        ]
        
        # ステージに必要な単語数
        num_words = random.randint(WORDS_PER_STAGE_MIN, WORDS_PER_STAGE_MAX)
        
        selected_words = []
        
        # 1. まず復習語を追加（最大5語まで新出語、残りは復習語）
        max_new_words = min(NEW_WORDS_PER_STAGE_MAX, len(unseen_words))
        num_new_words = min(max_new_words, num_words)
        num_review_words = num_words - num_new_words
        
        # 復習語を選択（重み付き：ミス回数が多いほど優先）
        if review_words and num_review_words > 0:
            review_weights = [
                self.missed_words.get(word['id'], 0) + 1
                for word in review_words
            ]
            selected_review = random.choices(
                review_words,
                weights=review_weights,
                k=min(num_review_words, len(review_words))
            )
            selected_words.extend(selected_review)
        
        # 2. 新出語を追加
        if unseen_words and num_new_words > 0:
            selected_new = random.sample(
                unseen_words,
                min(num_new_words, len(unseen_words))
            )
            selected_words.extend(selected_new)
        
        # 3. 足りない場合は既出の単語から追加
        if len(selected_words) < num_words:
            all_words = [w for w in self.words if w not in selected_words]
            needed = num_words - len(selected_words)
            if all_words:
                additional = random.sample(all_words, min(needed, len(all_words)))
                selected_words.extend(additional)
        
        return selected_words[:num_words]
    
    def mark_correct(self, word_id):
        """
        単語を正解済みとしてマーク
        Args:
            word_id: 単語ID
        """
        self.word_states[word_id] = WordState.CORRECT
        # ミス回数はリセットしない（学習履歴として保持）
    
    def mark_miss(self, word_id):
        """
        単語をミスとしてマーク（不正解ブロックに当てた時）
        Args:
            word_id: 単語ID
        """
        if self.word_states.get(word_id) != WordState.CORRECT:
            self.word_states[word_id] = WordState.MISSED
        self.missed_words[word_id] = self.missed_words.get(word_id, 0) + 1
    
    def get_word_by_id(self, word_id):
        """
        IDから単語データを取得
        Args:
            word_id: 単語ID
        Returns:
            dict: 単語データ、見つからない場合はNone
        """
        for word in self.words:
            if word['id'] == word_id:
                return word
        return None
    
    def get_all_words(self):
        """
        全単語データを取得
        Returns:
            list: 全単語データ
        """
        return self.words
    
    def reset_stage(self):
        """ステージリセット（必要に応じて）"""
        # 現在は何もしない（状態は保持）
        pass

