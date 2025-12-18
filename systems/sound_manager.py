"""
音声管理システム
"""
import pygame
import os
from config import SOUND_DIR


class SoundManager:
    """音声管理クラス"""
    
    def __init__(self):
        """音声ファイルを読み込む"""
        self.sounds = {}
        # パフォーマンステスト用: 音声を無効化（Trueで無効、Falseで有効）
        # TODO: テスト完了後は False に戻す
        self.muted = True  # テスト用: 音声を無効化
        
        # 音声ファイルのパス
        sound_files = {
            'bounce': os.path.join(SOUND_DIR, 'Bounce_sound.wav'),
            'correct': os.path.join(SOUND_DIR, 'Correct_sound.wav'),
            'clear': os.path.join(SOUND_DIR, 'CLEAR.wav'),
        }
        
        # 音声ファイルを読み込む（ファイルが存在しない場合はスキップ）
        for name, path in sound_files.items():
            try:
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                else:
                    print(f"警告: 音声ファイルが見つかりません: {path}")
            except Exception as e:
                print(f"警告: 音声ファイルの読み込みに失敗しました ({name}): {e}")
    
    def play(self, sound_name):
        """
        音声を再生
        Args:
            sound_name: 音声名 ('bounce', 'correct', 'clear')
        """
        if self.muted:
            return
        
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"警告: 音声の再生に失敗しました ({sound_name}): {e}")
    
    def set_muted(self, muted):
        """
        ミュート状態を設定
        Args:
            muted: Trueでミュート、Falseでミュート解除
        """
        self.muted = muted

