"""
メインゲームループ
"""
import pygame
import random
import time

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GameState,
    BLOCK_COLUMNS, BLOCK_SPACING_X, BLOCK_SPACING_Y,
    BLOCK_WIDTH, BLOCK_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT,
    BALL_RADIUS, INITIAL_LIFES, STAGE_CLEAR_DELAY,
    COLOR_BG, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_UI_WARNING,
    FONT_SIZE_SCORE, FONT_SIZE_TITLE, FONT_SIZE_NORMAL, JAPANESE_FONTS, FONT_FILE
)
from entities.ball import Ball
from entities.paddle import Paddle
from entities.block import Block, BlockType
from entities.door import Door
from systems.collision import (
    check_ball_wall_collision, check_ball_paddle_collision,
    check_ball_blocks_collision, check_ball_door_collision
)
from systems.score_manager import ScoreManager
from systems.word_manager import WordManager
from systems.sound_manager import SoundManager


def get_japanese_font(size):
    """日本語対応フォントを取得（Web対応フォントを優先）"""
    import os
    
    # 1. まずWeb対応フォントファイルを試す（asset/fonts/NotoSansJP-Regular.ttf）
    if os.path.exists(FONT_FILE):
        try:
            font = pygame.font.Font(FONT_FILE, size)
            # フォントが正しく読み込めたかテスト
            test_surface = font.render("あ", True, (255, 255, 255))
            if test_surface.get_width() > 0:
                return font
        except Exception:
            pass  # フォントファイルの読み込みに失敗した場合は次へ
    
    # 2. システムフォントを試す（ローカル環境用）
    for font_name in JAPANESE_FONTS:
        try:
            font = pygame.font.SysFont(font_name, size)
            test_surface = font.render("あ", True, (255, 255, 255))
            if test_surface.get_width() > 0:
                return font
        except:
            continue
    
    # 3. フォールバック: デフォルトフォント
    return pygame.font.Font(None, size)


class Game:
    """メインゲームクラス"""
    
    def __init__(self, screen):
        """
        ゲームを初期化
        Args:
            screen: pygame.Surface
        """
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        # フォント（初期化時にキャッシュ - 毎フレーム呼び出すと重い）
        self.font_score = get_japanese_font(FONT_SIZE_SCORE)
        self.font_normal = get_japanese_font(FONT_SIZE_NORMAL)
        self.font_title = get_japanese_font(FONT_SIZE_TITLE)
        self.font_id = get_japanese_font(FONT_SIZE_TITLE // 2)  # ID表示用（半分のサイズ）
        
        # ゲーム状態
        self.state = GameState.TITLE
        self.current_stage = 1
        
        # マネージャー
        self.score_manager = ScoreManager()
        self.word_manager = WordManager()
        self.sound_manager = SoundManager()
        
        # エンティティ
        self.ball = None
        self.paddle = None
        self.blocks = []
        self.door = None
        
        # 正解ブロック残り数（毎フレームのlist comprehensionを避けるためカウンタ管理）
        self.remaining_correct_blocks = 0
        
        # ステージ情報
        self.current_words = []
        self.current_question = None  # 現在の問題
        self.stage_start_time = 0
        self.stage_clear_time = 0
        
        # タイマー表示の間引き用（パフォーマンス改善）
        self.last_timer_update = 0  # 最後にタイマーを更新した時刻
        self.displayed_time = 0.0  # 表示中の時間（秒）
        self.timer_update_interval = 0.1  # タイマー更新間隔（秒）
        
        # ハードモードフラグ
        self.hard_mode = False
        
        # テキスト描画キャッシュ（値が変わった時だけ再レンダリング）
        self._cached_texts = {}  # {key: (surface, value)} の辞書
        
        # ゲームパッド初期化（Web環境でもエラーが出ないようにtry-exceptで囲む）
        self.joystick = None
        try:
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
        except Exception:
            # Web環境などでゲームパッドが使えない場合は無視
            self.joystick = None
        
        # ゲームパッドのボタン状態（前フレーム）
        self.prev_button_a = False
        
        # 仮想パドル位置（マウスとゲームパッドの両方から更新）
        self.virtual_paddle_x = None  # 初期化時に設定
        
        # 前フレームのマウス位置（マウス移動検出用）
        self.prev_mouse_x = None
        
        # 初期化
        self.init_title()
    
    def init_title(self):
        """タイトル画面の初期化"""
        self.state = GameState.TITLE
    
    def init_stage(self, stage_num):
        """
        ステージの初期化
        Args:
            stage_num: ステージ番号
        """
        self.current_stage = stage_num
        self.state = GameState.STAGE_START
        
        # ステージ用の単語を取得
        self.current_words = self.word_manager.get_stage_words(stage_num)
        
        # 問題を設定（最初の単語）- arrange_blocks()の前に設定する必要がある
        if self.current_words:
            self.current_question = self.current_words[0]
        
        # エンティティの初期化
        self.init_entities()
        
        # タイマーリセット
        self.stage_start_time = time.time()
        self.stage_clear_time = 0
        self.last_timer_update = time.time()  # タイマー表示の間引き用もリセット
        self.displayed_time = 0.0
        
        # テキストキャッシュをクリア（ステージが変わったため）
        self._cached_texts.clear()
    
    def init_entities(self):
        """エンティティを初期化"""
        # パドル（画面下部中央）
        paddle_x = (SCREEN_WIDTH - PADDLE_WIDTH) // 2
        paddle_y = SCREEN_HEIGHT - PADDLE_HEIGHT - 20
        self.paddle = Paddle(paddle_x, paddle_y)
        # 仮想パドル位置を初期化
        self.virtual_paddle_x = paddle_x + PADDLE_WIDTH / 2  # パドル中央のX座標
        
        # ボール（パドルの上）
        ball_x = paddle_x + PADDLE_WIDTH // 2
        ball_y = paddle_y - BALL_RADIUS - 5
        self.ball = Ball(ball_x, ball_y)
        # 仮想パドル位置を初期化（ボールの位置に合わせる）
        if self.virtual_paddle_x is None:
            self.virtual_paddle_x = ball_x
        
        # 扉
        self.door = Door()
        
        # ブロック配置
        self.blocks = []
        self.remaining_correct_blocks = 0  # カウンタをリセット
        self.arrange_blocks()
    
    def arrange_blocks(self):
        """ブロックを配置（現在の問題に対応するブロックのみ）"""
        if not self.current_question:
            return
        
        # 現在の問題に対応するブロックのみを配置
        word = self.current_question
        
        # 3列固定、中央揃え
        total_width = (BLOCK_COLUMNS * BLOCK_WIDTH) + ((BLOCK_COLUMNS - 1) * BLOCK_SPACING_X)
        start_x = (SCREEN_WIDTH - total_width) // 2
        block_y = 150  # 上部から150px
        
        # 3択の選択肢を生成
        choices = [word['ja']] + random.sample(
            [w['ja'] for w in self.word_manager.get_all_words() if w['id'] != word['id']],
            2
        )
        random.shuffle(choices)
        
        # 3列に配置
        for col in range(BLOCK_COLUMNS):
            block_x = start_x + col * (BLOCK_WIDTH + BLOCK_SPACING_X)
            
            choice = choices[col]
            is_correct = (choice == word['ja'])
            
            if is_correct:
                # 正解ブロック（word_idを設定）
                block = Block(block_x, block_y, BlockType.CORRECT, word['id'], choice)
                self.remaining_correct_blocks += 1  # カウンタを増やす
            else:
                # 不正解ブロック（word_idは正解ブロックのIDを設定して、ミス判定に使用）
                block = Block(block_x, block_y, BlockType.INCORRECT, word['id'], choice)
            
            self.blocks.append(block)
    
    def update(self, dt):
        """
        ゲームを更新
        Args:
            dt: デルタタイム
        """
        if self.state == GameState.PLAYING:
            self.update_playing(dt)
        elif self.state == GameState.STAGE_CLEAR:
            self.update_stage_clear()
    
    def update_playing(self, dt):
        """プレイ中の更新"""
        # ゲームパッドのAボタン状態をチェック（連続押し検出用）
        if self.joystick:
            button_a = self.joystick.get_button(0)  # Aボタン
            if button_a and not self.prev_button_a:
                # ボタンが押された瞬間
                self._handle_action()
            self.prev_button_a = button_a
        
        # 仮想パドル位置の更新（マウスまたはゲームパッド）
        if self.virtual_paddle_x is None:
            # 初期化されていない場合は現在のパドル位置を使用
            self.virtual_paddle_x = self.paddle.x + self.paddle.width / 2
        
        # マウス入力の処理
        mouse_x, _ = pygame.mouse.get_pos()
        
        # 前フレームのマウス位置を初期化
        if self.prev_mouse_x is None:
            self.prev_mouse_x = mouse_x
        
        # マウスが実際に動いたかどうかを判定
        mouse_moved = abs(mouse_x - self.prev_mouse_x) > 3  # 3px以上動いたら移動とみなす
        
        # ゲームパッド入力の処理
        if self.joystick:
            # アナログスティックの取得（左スティックのX軸）
            axis_x = self.joystick.get_axis(0)  # -1.0 ～ 1.0
            
            # デッドゾーン処理（中心付近の微小な値は無視）
            DEAD_ZONE = 0.1
            stick_active = abs(axis_x) > DEAD_ZONE
            
            if stick_active:
                # アナログスティックで移動（相対移動、感度調整）
                from config import PADDLE_SPEED
                # スティックの倒し具合に応じて速度を調整
                delta_x = axis_x * PADDLE_SPEED * dt
                self.virtual_paddle_x += delta_x
            else:
                # スティックがデッドゾーン内の場合、十字キーをチェック
                hat = self.joystick.get_hat(0)  # 十字キーの状態 (x, y)
                hat_x = hat[0]  # -1: 左, 0: 中央, 1: 右
                
                if hat_x != 0:
                    # ゲームパッドの十字キーで移動（相対移動）
                    from config import PADDLE_SPEED
                    delta_x = hat_x * PADDLE_SPEED * dt
                    self.virtual_paddle_x += delta_x
                else:
                    # 十字キーも押されていない場合
                    # マウスが実際に動いた場合のみマウス位置を使用
                    if mouse_moved:
                        self.virtual_paddle_x = mouse_x
        else:
            # ゲームパッドが接続されていない場合はマウス位置を使用（絶対位置）
            self.virtual_paddle_x = mouse_x
        
        # 前フレームのマウス位置を更新
        self.prev_mouse_x = mouse_x
        
        # 仮想パドル位置を画面範囲内に制限
        min_x = self.paddle.width / 2
        max_x = SCREEN_WIDTH - self.paddle.width / 2
        self.virtual_paddle_x = max(min_x, min(self.virtual_paddle_x, max_x))
        
        # 仮想パドル位置でパドルを更新
        self.paddle.update(self.virtual_paddle_x)
        
        # ボール更新
        if self.ball.launched:
            self.ball.update(dt)
            
            # 壁との当たり判定
            hit_left_right, hit_top, fell_bottom = check_ball_wall_collision(
                self.ball, SCREEN_WIDTH, SCREEN_HEIGHT
            )
            
            # 壁に当たった時の音声
            if hit_left_right or hit_top:
                self.sound_manager.play('bounce')
            
            if fell_bottom:
                # ボール落下
                if self.score_manager.lose_life():
                    self.state = GameState.GAME_OVER
                else:
                    # リスポーン
                    # 仮想パドル位置を使用
                    if self.virtual_paddle_x is None:
                        paddle_center_x = self.paddle.x + PADDLE_WIDTH / 2
                    else:
                        paddle_center_x = self.virtual_paddle_x
                    self.ball.reset(
                        paddle_center_x,
                        self.paddle.y - BALL_RADIUS - 5
                    )
            else:
                # パドルとの当たり判定
                if check_ball_paddle_collision(self.ball, self.paddle):
                    self.sound_manager.play('bounce')  # パドル反射音
                
                # ブロックとの当たり判定（扉がアンロックされている場合、不正解ブロックの当たり判定を無効化）
                door_unlocked = self.door.is_unlocked()
                hit_block, destroyed = check_ball_blocks_collision(self.ball, self.blocks, door_unlocked)
                if hit_block:
                    if destroyed and hit_block.is_correct():
                        # 正解ブロック破壊
                        self.sound_manager.play('correct')  # 正解ブロック破壊音
                        self.score_manager.add_block_score()
                        self.word_manager.mark_correct(hit_block.word_id)
                        self.remaining_correct_blocks -= 1  # カウンタを減らす
                    elif hit_block.is_incorrect():
                        # 不正解ブロック命中
                        self.sound_manager.play('bounce')  # 不正解ブロック反射音
                        self.score_manager.reset_combo()
                        if hit_block.word_id:
                            self.word_manager.mark_miss(hit_block.word_id)
                    else:
                        # 正解ブロックに当たったが破壊されなかった（HP残り）
                        self.sound_manager.play('bounce')  # ブロック反射音
                
                # 扉との当たり判定
                if check_ball_door_collision(self.ball, self.door):
                    # ステージクリア
                    self.sound_manager.play('clear')  # ステージクリア音
                    self.stage_clear_time = time.time()
                    self.state = GameState.STAGE_CLEAR
        
        # 全正解ブロック破壊チェック（カウンタ使用で毎フレームのlist生成を回避）
        if self.remaining_correct_blocks <= 0:
            self.door.unlock()
    
    def update_stage_clear(self):
        """ステージクリア待機"""
        elapsed = time.time() - self.stage_clear_time
        if elapsed >= STAGE_CLEAR_DELAY:
            # 次のステージへ
            if self.current_stage < 10:
                self.current_stage += 1
                self.init_stage(self.current_stage)
            else:
                # 全ステージクリア
                self.state = GameState.RESULT
    
    def _handle_action(self):
        """アクション処理（クリックやAボタン）"""
        if self.state == GameState.TITLE:
            # ゲーム開始
            self.score_manager.reset()
            self.init_stage(1)
        elif self.state == GameState.STAGE_START:
            # ボール発射
            self.ball.launch()
            self.state = GameState.PLAYING
        elif self.state == GameState.PLAYING:
            # プレイ中でも、ボールが未発射の場合は発射可能（リスポーン後など）
            if self.ball and not self.ball.launched:
                self.ball.launch()
        elif self.state == GameState.GAME_OVER:
            # コンティニュー
            self.score_manager.continue_game()
            self.init_stage(self.current_stage)
        elif self.state == GameState.RESULT:
            # リザルト画面から通常モードで最初から
            self.hard_mode = False
            self.score_manager.reset()
            self.word_manager.reset()
            self.init_stage(1)
    
    def handle_event(self, event):
        """
        イベント処理
        Args:
            event: pygame.Event
        """
        if event.type == pygame.QUIT:
            return False
        
        elif event.type == pygame.KEYDOWN:
            # Web環境でのキーコード問題を診断するため、unicode属性も確認
            key_unicode = event.unicode if hasattr(event, 'unicode') else None
            
            if event.key == pygame.K_ESCAPE:
                if self.state == GameState.RESULT:
                    # リザルト画面でESCキーで終了
                    return False
                return False
            elif event.key == pygame.K_h or (key_unicode and key_unicode.lower() == 'h'):
                # Hキーでハードモードをトグル（いつでも切り替え可能）
                if self.state == GameState.RESULT:
                    # リザルト画面でHキーを押した場合、ハードモードで再挑戦
                    self.hard_mode = True
                    self.score_manager.reset()
                    self.word_manager.reset()
                    self.init_stage(1)
                else:
                    # 通常のステージ中はトグル
                    self.hard_mode = not self.hard_mode
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                self._handle_action()
        
        # ゲームパッドのボタンイベント
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # Aボタン（通常はボタン0）
                self._handle_action()
        
        return True
    
    def draw(self):
        """描画処理"""
        # 背景クリア
        self.screen.fill(COLOR_BG)
        
        if self.state == GameState.TITLE:
            self.draw_title()
        elif self.state == GameState.STAGE_START:
            self.draw_stage_start()
        elif self.state == GameState.PLAYING:
            self.draw_playing()
        elif self.state == GameState.STAGE_CLEAR:
            self.draw_stage_clear()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.RESULT:
            self.draw_result()
    
    def draw_title(self):
        """タイトル画面を描画"""
        title_text = self.font_title.render("Word Breaker", True, COLOR_TEXT)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(title_text, title_rect)
        
        start_text = self.font_normal.render("クリックでスタート", True, COLOR_TEXT_DIM)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(start_text, start_rect)
    
    def draw_stage_start(self):
        """ステージ開始画面を描画"""
        # 問題表示
        if self.current_question:
            # お題（単語）を中央に表示（キャッシュ化、draw_playing()と同じキーを使用）
            question_text = self.current_question['word']
            cache_key = f"question_{question_text}"
            if cache_key not in self._cached_texts or self._cached_texts[cache_key][1] != question_text:
                word_surface = self.font_title.render(question_text, True, COLOR_TEXT)
                self._cached_texts[cache_key] = (word_surface, question_text)
            word_surface, _ = self._cached_texts[cache_key]
            word_rect = word_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(word_surface, word_rect)
            
            # IDナンバーを表示（グレー、小さい文字、お題の左側、キャッシュ化）
            word_id = self.current_question.get('id', 0)
            id_text_str = f"ID={word_id}"
            cache_key = f"id_{word_id}"
            if cache_key not in self._cached_texts or self._cached_texts[cache_key][1] != id_text_str:
                id_surface = self.font_id.render(id_text_str, True, COLOR_TEXT_DIM)
                self._cached_texts[cache_key] = (id_surface, id_text_str)
            id_surface, _ = self._cached_texts[cache_key]
            id_rect = id_surface.get_rect()
            id_rect.centery = word_rect.centery  # お題と同じ高さ
            id_rect.right = word_rect.left - 20  # お題の左から20px左側
            self.screen.blit(id_surface, id_rect)
            
            # ヒントテキスト（キャッシュ化）
            cache_key = "hint_launch"
            if cache_key not in self._cached_texts:
                hint_surface = self.font_normal.render("クリックでボール発射", True, COLOR_TEXT_DIM)
                self._cached_texts[cache_key] = (hint_surface, "クリックでボール発射")
            hint_surface, _ = self._cached_texts[cache_key]
            hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            self.screen.blit(hint_surface, hint_rect)
        
        # ブロックとパドルを表示（プレビュー）
        door_unlocked = self.door.is_unlocked()
        correct_text = self.current_question['ja'] if self.current_question else None
        for block in self.blocks:
            block.draw(self.screen, self.font_normal, door_unlocked, correct_text, self.hard_mode)
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        self.door.draw(self.screen, self.font_normal)
    
    def draw_playing(self):
        """プレイ中画面を描画"""
        # 問題表示（中央上部、最初の位置のまま）
        if self.current_question:
            # お題（単語）を中央に表示（キャッシュ化）
            question_text = self.current_question['word']
            cache_key = f"question_{question_text}"
            if cache_key not in self._cached_texts or self._cached_texts[cache_key][1] != question_text:
                word_surface = self.font_title.render(question_text, True, COLOR_TEXT)
                self._cached_texts[cache_key] = (word_surface, question_text)
            word_surface, _ = self._cached_texts[cache_key]
            word_rect = word_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(word_surface, word_rect)
            
            # IDナンバーを表示（グレー、小さい文字、お題の左側、キャッシュ化）
            word_id = self.current_question.get('id', 0)
            id_text_str = f"ID={word_id}"
            cache_key = f"id_{word_id}"
            if cache_key not in self._cached_texts or self._cached_texts[cache_key][1] != id_text_str:
                id_surface = self.font_id.render(id_text_str, True, COLOR_TEXT_DIM)
                self._cached_texts[cache_key] = (id_surface, id_text_str)
            id_surface, _ = self._cached_texts[cache_key]
            id_rect = id_surface.get_rect()
            id_rect.centery = word_rect.centery  # お題と同じ高さ
            id_rect.right = word_rect.left - 20  # お題の左から20px左側
            self.screen.blit(id_surface, id_rect)
        
        # スコア表示（左上、キャッシュ化）
        current_score = self.score_manager.get_score()
        cache_key = "score"
        if cache_key not in self._cached_texts or self._cached_texts[cache_key][1] != current_score:
            score_surface = self.font_score.render(f"スコア: {current_score}", True, COLOR_TEXT)
            self._cached_texts[cache_key] = (score_surface, current_score)
        score_surface, _ = self._cached_texts[cache_key]
        self.screen.blit(score_surface, (20, 60))
        
        # ライフ表示（キャッシュ化）
        current_lifes = self.score_manager.get_lifes()
        cache_key = "life"
        if cache_key not in self._cached_texts or self._cached_texts[cache_key][1] != current_lifes:
            life_surface = self.font_score.render(f"ライフ: {current_lifes}", True, COLOR_TEXT)
            self._cached_texts[cache_key] = (life_surface, current_lifes)
        life_surface, _ = self._cached_texts[cache_key]
        self.screen.blit(life_surface, (20, 90))
        
        # コンボ表示（キャッシュ化）
        combo_count = self.score_manager.get_combo_count()
        if combo_count > 0:
            cache_key = "combo"
            if cache_key not in self._cached_texts or self._cached_texts[cache_key][1] != combo_count:
                combo_surface = self.font_score.render(f"コンボ: {combo_count}", True, COLOR_TEXT)
                self._cached_texts[cache_key] = (combo_surface, combo_count)
            combo_surface, _ = self._cached_texts[cache_key]
            self.screen.blit(combo_surface, (20, 120))
        elif "combo" in self._cached_texts:
            # コンボが0になったらキャッシュを削除
            del self._cached_texts["combo"]
        
        # タイマー表示（右上）- 間引き表示でパフォーマンス改善（キャッシュ化）
        current_time = time.time()
        elapsed = current_time - self.stage_start_time
        
        # 一定間隔（0.1秒）ごとにタイマー表示を更新
        if current_time - self.last_timer_update >= self.timer_update_interval:
            self.displayed_time = elapsed
            self.last_timer_update = current_time
        
        # タイマーのキャッシュ（表示値が変わった時だけ再レンダリング）
        timer_value = int(self.displayed_time * 10) / 10  # 0.1秒単位で丸める
        cache_key = "timer"
        if cache_key not in self._cached_texts or self._cached_texts[cache_key][1] != timer_value:
            timer_surface = self.font_score.render(f"時間: {timer_value:.1f}秒", True, COLOR_TEXT)
            self._cached_texts[cache_key] = (timer_surface, timer_value)
        timer_surface, _ = self._cached_texts[cache_key]
        timer_rect = timer_surface.get_rect()
        timer_rect.topright = (SCREEN_WIDTH - 20, 20)
        self.screen.blit(timer_surface, timer_rect)
        
        # エンティティ描画
        door_unlocked = self.door.is_unlocked()
        correct_text = self.current_question['ja'] if self.current_question else None
        for block in self.blocks:
            block.draw(self.screen, self.font_normal, door_unlocked, correct_text, self.hard_mode)
        
        # ハードモード表示（右上、キャッシュ化）
        if self.hard_mode:
            cache_key = "hard_mode"
            if cache_key not in self._cached_texts:
                hard_surface = self.font_score.render("HARD MODE", True, COLOR_UI_WARNING)
                self._cached_texts[cache_key] = (hard_surface, True)
            hard_surface, _ = self._cached_texts[cache_key]
            hard_rect = hard_surface.get_rect()
            hard_rect.topright = (SCREEN_WIDTH - 20, 50)
            self.screen.blit(hard_surface, hard_rect)
        elif "hard_mode" in self._cached_texts:
            # ハードモードがオフになったらキャッシュを削除
            del self._cached_texts["hard_mode"]
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        self.door.draw(self.screen, self.font_normal)
    
    def draw_stage_clear(self):
        """ステージクリア画面を描画"""
        clear_text = self.font_title.render("STAGE CLEAR!", True, COLOR_TEXT)
        clear_rect = clear_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(clear_text, clear_rect)
    
    def draw_game_over(self):
        """ゲームオーバー画面を描画"""
        gameover_text = self.font_title.render("GAME OVER", True, COLOR_TEXT)
        gameover_rect = gameover_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(gameover_text, gameover_rect)
        
        score_text = self.font_normal.render(
            f"スコア: {self.score_manager.get_score()}", True, COLOR_TEXT_DIM
        )
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)
        
        continue_text = self.font_normal.render("クリックでコンティニュー", True, COLOR_TEXT_DIM)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(continue_text, continue_rect)
    
    def draw_result(self):
        """リザルト画面を描画"""
        result_text = self.font_title.render("全ステージクリア!", True, COLOR_TEXT)
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(result_text, result_rect)
        
        final_score = self.score_manager.get_final_score()
        score_text = self.font_normal.render(
            f"最終スコア: {final_score}", True, COLOR_TEXT_DIM
        )
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(score_text, score_rect)
        
        if self.score_manager.is_perfect():
            perfect_text = self.font_normal.render("PERFECT!!", True, COLOR_TEXT)
            perfect_rect = perfect_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(perfect_text, perfect_rect)
        
        # 選択肢表示
        hard_text = self.font_normal.render("[H キー] ハードモードで再挑戦", True, COLOR_TEXT)
        hard_rect = hard_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(hard_text, hard_rect)
        
        restart_text = self.font_normal.render("[クリック] 通常モードで最初から", True, COLOR_TEXT)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
        self.screen.blit(restart_text, restart_rect)
        
        exit_text = self.font_normal.render("[Esc] 終了", True, COLOR_TEXT_DIM)
        exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130))
        self.screen.blit(exit_text, exit_rect)
    
    async def run(self):
        """
        メインループ（Web対応のためasync、協調型ループ）
        
        pygbag環境での注意点（Geminiのアドバイスに基づく）:
        - await asyncio.sleep(0) をループの最後に1回だけ呼ぶ（VSync同期）
        - 時間指定（sleep(0.016)など）はNG（ブラウザのタイミングとズレる）
        - clock.tick() との二重待機を避ける（asyncio.sleep(0)がVSyncを強制するため）
        - 重い処理はフレーム外で実行（init_stage()など）
        """
        import asyncio
        running = True
        
        while running:
            dt = 1.0  # フレーム単位（元の設計に合わせる）
            
            # イベント処理
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
            
            # 更新
            self.update(dt)
            
            # 描画
            self.draw()
            
            # 画面更新
            pygame.display.flip()
            
            # ブラウザへの制御返却（Geminiのアドバイスに基づく）
            # await asyncio.sleep(0) は「即座にブラウザへ制御を戻し、次の描画フレーム（VSync）を待つ」
            # 必ずループの最後で0秒待機（時間指定はNG、ブラウザのタイミングとズレる）
            await asyncio.sleep(0)
        
        pygame.quit()
    

