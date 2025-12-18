"""
Word Breaker - 定数管理ファイル
すべてのゲーム定数をここで管理します。
"""

# ==================== 画面設定 ====================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
# フルスクリーンフラグは main.py で pygame.SCALED | pygame.FULLSCREEN として設定

# ==================== ゲーム要素サイズ ====================
BLOCK_WIDTH = 300  # 文字がはみ出ないように3倍に拡大（100 → 300）
BLOCK_HEIGHT = 40
PADDLE_WIDTH = 168  # 20%UP（140 → 168、難易度調整）
PADDLE_HEIGHT = 20
BALL_RADIUS = 8
DOOR_WIDTH = 360  # 文字がはみ出ないように3倍に拡大（120 → 360）
DOOR_HEIGHT = 40

# ==================== 速度設定 ====================
BALL_SPEED_X = 2.88  # ±2.88（ランダム符号、元の72%：20%UP）
BALL_SPEED_Y = 3.6  # -3.6（初期は上向き、元の72%：20%UP）
PADDLE_SPEED = 8
BALL_MAX_VX = 4.32  # パドル端での最大x速度（元の72%：20%UP）

# パドル角度設定
PADDLE_ANGLE_DEGREES = 30  # パドル移動時の反射角度（度）
PADDLE_ANGLE_TAN = 0.577  # tan(30°) ≈ 0.577

# パドル反射時の速度増加（難易度調整）
PADDLE_BOUNCE_SPEED_BOOST = 1.0  # パドル反射時に速度を+1増やす

# 壁・ブロック反射時の速度減衰（難易度調整）
WALL_BLOCK_BOUNCE_DAMPING = 0.8  # 画面上端・ブロック反射時に速度を20%減らす（0.8倍）

# ==================== ブロック配置 ====================
BLOCK_COLUMNS = 3
BLOCK_SPACING_X = 30  # ブロック間の横間隔（ボールが通れるように30pxに拡大）
BLOCK_SPACING_Y = 30  # ブロック間の縦間隔（ボールが通れるように30pxに拡大）

# ==================== 扉位置 ====================
DOOR_X = (SCREEN_WIDTH - DOOR_WIDTH) // 2  # 580
DOOR_Y = 20

# ==================== スコア設定 ====================
SCORE_BLOCK_DESTROY = 100
COMBO_THRESHOLD = 3  # 3回連続でコンボ
COMBO_MULTIPLIER = 1.2
PERFECT_BONUS_MULTIPLIER = 1.2

# ==================== ライフ設定 ====================
INITIAL_LIFES = 10

# ==================== ステージ設定 ====================
STAGE_CLEAR_DELAY = 1.5  # 秒
WORDS_PER_STAGE_MIN = 3
WORDS_PER_STAGE_MAX = 5
NEW_WORDS_PER_STAGE_MAX = 5
TOTAL_STAGES = 10

# ==================== フォント設定 ====================
FONT_SIZE_SCORE = 24
FONT_SIZE_TITLE = 48
FONT_SIZE_NORMAL = 32

# 日本語フォント（優先順位順、Windows標準フォント）
# 利用可能なフォントから自動選択されます
JAPANESE_FONTS = [
    "Meiryo",           # メイリオ（推奨）
    "MS PGothic",       # MS Pゴシック
    "MS Gothic",        # MSゴシック
    "Yu Gothic",        # 游ゴシック
    "MS UI Gothic",     # MS UIゴシック
]

# ==================== 色設定（ダークモード + 柔らかめ） ====================
# 背景色
COLOR_BG = (20, 20, 30)  # ダークブルーグレー

# テキスト色
COLOR_TEXT = (240, 240, 250)  # オフホワイト
COLOR_TEXT_DIM = (180, 180, 200)  # 薄いグレー

# ブロック色
COLOR_BLOCK_CORRECT = (100, 200, 150)  # 柔らかいグリーン（HP: 2）
COLOR_BLOCK_CORRECT_HIT = (150, 250, 200)  # 明るいグリーン（HP: 1、1回ヒット後）
COLOR_BLOCK_INCORRECT = (200, 120, 120)  # 柔らかいレッド
COLOR_BLOCK_DECORATIVE = (80, 80, 100)  # グレー（装飾用）

# ブロックHP設定
BLOCK_CORRECT_HP = 2  # 正解ブロックの初期HP

# パドル色
COLOR_PADDLE = (150, 180, 220)  # 柔らかいブルー

# ボール色
COLOR_BALL = (250, 200, 100)  # 柔らかいオレンジ

# 扉色
COLOR_DOOR_LOCKED = (100, 100, 120)  # グレー（ロック状態）
COLOR_DOOR_UNLOCKED = (150, 200, 150)  # グリーン（アンロック状態）

# UI色
COLOR_UI_ACCENT = (200, 150, 250)  # 柔らかいパープル
COLOR_UI_WARNING = (250, 180, 100)  # 柔らかいオレンジ

# ==================== ファイルパス ====================
DATA_DIR = "data"
WORDS_JSON_PATH = f"{DATA_DIR}/words.json"
SOUND_DIR = "asset/sound"
FONT_DIR = "asset/fonts"
FONT_FILE = f"{FONT_DIR}/NotoSansJP-Regular.ttf"  # Web対応フォント

# ==================== ゲーム状態 ====================
class GameState:
    TITLE = "TITLE"
    STAGE_START = "STAGE_START"
    PLAYING = "PLAYING"
    STAGE_CLEAR = "STAGE_CLEAR"
    RESULT = "RESULT"
    GAME_OVER = "GAME_OVER"

# ==================== 単語状態 ====================
class WordState:
    UNSEEN = "UNSEEN"  # 未出題
    CORRECT = "CORRECT"  # 正解済
    MISSED = "MISSED"  # ミスあり（再出題対象）

