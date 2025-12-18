# Word Breaker（英単語ブロック崩し）
## Word Breaker (English Vocabulary Block Breaker)

英単語学習とブロック崩しを組み合わせた教育ゲーム
A puzzle game that combines English vocabulary learning with block breaking

---

## ゲームについて / About the Game

英単語の意味を3択から選び、正解ブロックを破壊してステージをクリアするブロック崩しゲームです。
A block-breaking game where you choose the correct meaning from 3 options and break the correct blocks to clear stages.

**特徴 / Features:**
- 正解ブロックだけが破壊可能 / Only correct blocks can be destroyed
- 不正解ブロックは壊れない（思考を促す仕組み） / Incorrect blocks are indestructible (encourages thinking)
- 10ステージのチャレンジ / 10 stages to challenge
- スコアとクリアタイムで再挑戦を誘導 / Score and clear time encourage replay

---

## ゲームルール / Game Rules

1. **目的 / Objective**: 英単語の意味を3択から選び、正解ブロックを破壊してステージをクリア
   Choose the correct meaning from 3 options and break all correct blocks to clear the stage

2. **正解ブロック / Correct Blocks**: 1ヒットで破壊可能
   Can be destroyed with 1 hit

3. **不正解ブロック / Incorrect Blocks**: 完全無敵（壊れない）
   Completely indestructible (cannot be broken)

4. **扉（ゴール）/ Door (Goal)**: 全正解ブロック破壊でアンロック、ボールが当たるとクリア
   Unlocks when all correct blocks are destroyed; hitting it with the ball clears the stage

5. **ライフ / Lives**: 初期10、ボール落下で-1
   Starts with 10; decreases by 1 when the ball falls

6. **スコア / Score**: 正解ブロック破壊で+100、コンボ・ノーミスボーナスあり
   +100 for each correct block destroyed; combo and no-miss bonuses available

---

## 操作方法 / Controls

### マウス操作 / Mouse Controls
- **パドル移動 / Move Paddle**: マウスで移動
  Move with mouse
- **ボール発射 / Launch Ball**: クリック（ステージ開始時、リスポーン後）
  Click (at stage start, after respawn)
- **発射角度調整 / Adjust Launch Angle**: マウス位置で自動調整（左側で左向き、右側で右向き）
  Automatically adjusted by mouse position (left side = leftward, right side = rightward)

### キーボード操作 / Keyboard Controls
- **←→キー / Left/Right Keys**: ボール発射角度を調整（左キーで左向き、右キーで右向き）
  Adjust launch angle (left key = leftward, right key = rightward)
- **Hキー / H Key**: ハードモード切り替え（いつでも）
  Toggle hard mode (anytime)
- **Escキー / Esc Key**: 終了（リザルト画面で）
  Exit (on result screen)

### ゲームパッド操作 / Gamepad Controls
- **パドル移動 / Move Paddle**: 十字キー（左右）または左アナログスティック
  D-pad (left/right) or left analog stick
- **ボール発射 / Launch Ball**: Aボタン（ステージ開始時、リスポーン後、各種アクション）
  A button (at stage start, after respawn, various actions)

**注意 / Note**: Web版ではゲームパッドの動作が不安定な場合があります
Gamepad may not work reliably in the web version

---

## ハードモード / Hard Mode

**Hキー**でいつでも切り替え可能
Press **H key** to toggle anytime

- 正解ブロックも赤色で表示されるため、見分けがつかない
  Correct blocks are also displayed in red, making them indistinguishable
- リザルト画面でHキーを押すとハードモードで再挑戦
  Press H key on the result screen to retry in hard mode
- スコア倍率が適用される
  Score multiplier is applied

---

## スコアシステム / Scoring System

- **基本スコア / Base Score**: 正解ブロック破壊で+100
  +100 for each correct block destroyed
- **コンボ / Combo**: 3回連続で破壊すると×1.2倍
  ×1.2 multiplier for 3 consecutive destructions
- **ノーミスボーナス / No-Miss Bonus**: ミスなしでクリアすると×1.2倍 + "PERFECT!!"表示
  ×1.2 multiplier + "PERFECT!!" display for clearing without missing

---

## クイックスタート / Quick Start

### PC版（Python版）/ PC Version (Python)

#### 必要な環境 / Requirements
- Python 3.x
- pygame 2.5.2

#### インストール / Installation
```bash
pip install -r requirements.txt
```

#### 実行 / Run
```bash
python main.py
```

または / Or
```bash
run.bat
```

### Web版 / Web Version

ブラウザで直接プレイ可能（pygbag使用）
Play directly in your browser (using pygbag)

```bash
# 仮想環境でpygbagをインストール後
# After installing pygbag in a virtual environment
pygbag main.py
```

詳細は `pygbag_web移植ガイド.md` を参照
See `pygbag_web移植ガイド.md` for details

---

## ライセンス / License

（未定 / To be determined）

---

開発者向けの詳細情報は `ROADMAP.md` を参照してください。
For developer information, see `ROADMAP.md`.

