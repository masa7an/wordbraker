# Word Breaker リポジトリマップ

> 作成日: 2026-07-17（プロジェクト再開時の現状把握用）

## リポジトリ全体像

| 場所 | 役割 | 状態 |
|---|---|---|
| `master` ブランチ | **ソースコード本体（作業のベースはここ）** | 最新（2025-12-19） |
| `main` ブランチ | 公開用ドキュメント（README, 完了報告書, 移植ガイド） | ドキュメントのみ |
| `gh-pages` ブランチ | Webビルド成果物（index.html / wordbraker.apk / favicon.png） | デプロイ済みと一致 |
| `C:\Users\masa7\Cursor\wordbreaker_pygame` | **旧スナップショット（pygbag移植前）— 使用禁止** | 古い（git管理外） |

- 公開URL: https://masa7an.github.io/wordbraker/
- ビルドは `pygbag main.py`（run_web.bat）→ `build/web/` に生成 → `gh-pages` に手動デプロイ

## ファイルマップ（master）

```
wordbraker/
├── main.py                  # エントリーポイント（asyncio.run、Web対応）
├── config.py                # 全定数（画面1280x720、速度、色、フォント、GameState/WordState）
├── game.py                  # Gameクラス：状態遷移＋更新＋描画＋入力の中枢（772行）
│
├── entities/
│   ├── ball.py              # Ball：発射角度制御、Arkanoid反射、減衰/加速
│   ├── paddle.py            # Paddle：マウス追従、移動方向検出
│   ├── block.py             # Block：CORRECT(HP2)/INCORRECT(無敵)/DECORATIVE
│   └── door.py              # Door：全正解破壊でアンロック→ゴール
│
├── systems/
│   ├── collision.py         # 関数群：壁/パドル/ブロック/扉の当たり判定と反射
│   ├── word_manager.py      # WordManager：出題選択（復習語重み付き）、正解/ミス記録
│   ├── score_manager.py     # ScoreManager：スコア、コンボ、ライフ、PERFECT判定
│   └── sound_manager.py     # SoundManager：bounce/correct/clear の3音
│
├── states/                  # ※空（__init__.pyのみ）。状態管理は game.py に集約されている
│
├── data/words.json          # 単語69語 {id, word, ja, category, level, choices}
├── asset/
│   ├── fonts/NotoSansJP-Regular.ttf   # Web用日本語フォント（pygbagに埋め込み）
│   └── sound/*.wav          # 効果音3種
│
├── run.bat                  # ローカル実行
├── run_web.bat              # venv有効化 → pygbag main.py（Webローカルサーバー）
│
└── ドキュメント
    ├── README.md                     # プレイヤー向け（日英併記）
    ├── ROADMAP.md / PERFORMANCE_ANALYSIS.md
    ├── pygbag_web移植ガイド.md        # Web移植の禁止事項・必須パターン集（重要）
    └── コミュニケーションガイド.md / 人間用の覚え書き_2025_12_18.md
```

## アーキテクチャ / データフロー

```
main.py ──> Game(screen).run()  [async メインループ]
              │
              ├─ handle_event()  クリック/H/←→/ゲームパッド → _handle_action()
              ├─ update(dt=1.0)  状態別更新（PLAYING が中心）
              │     ├─ 入力統合: マウス/スティック/十字キー → virtual_paddle_x
              │     ├─ collision.py で 壁→パドル→ブロック→扉 の順に判定
              │     ├─ 正解破壊 → ScoreManager.add_block_score() + WordManager.mark_correct()
              │     ├─ 不正解命中 → reset_combo() + mark_miss()（再出題の重みに反映）
              │     └─ remaining_correct_blocks == 0 → door.unlock()
              └─ draw()          状態別描画（テキスト/SurfaceはすべてキャッシュしてWASM対応）
```

### 状態遷移（GameState）

```
TITLE ─click→ STAGE_START ─click(発射)→ PLAYING ─扉に命中→ STAGE_CLEAR ─1.5s→ 次ステージ
                                          │                              └─10面クリア→ RESULT
                                          └─ライフ0→ GAME_OVER ─click→ コンティニュー（スコア保持）
RESULT: click=通常モード再開 / H=ハードモード再挑戦 / Esc=終了
```

### ゲームの骨子

- 1問 = 英単語1語 + 3択ブロック（正解1・不正解2）。正解はHP2、不正解は無敵。
- 全正解ブロック破壊で扉アンロック → 不正解ブロックは当たり判定消滅＋正解テキスト表示（復習演出）。
- 出題制御: 1ステージ3〜5語、新出語は最大5語、ミスした語はミス回数の重み付きで再出題。
- ハードモード(H): 正解ブロックも赤表示で見分け不可。

### 設計上の意図（誤って"修正"しないこと）

- **誤答は `words.json` の `choices` を使わず、全単語の訳語からランダムに選ぶ**
  （[game.py `arrange_blocks()`](game.py) ）。`choices` は固定値のため毎回同じ3択になりマンネリ化する。
  全単語プールから引くことで、**語数が少なくても組み合わせが毎回変わり**、選択肢の位置や並びの
  丸暗記を防げる。`choices` フィールドが未使用なのは意図的。

- **`dt = 1.0` 固定（フレーム単位・秒単位にしない）**
  pygbag移植ガイドの必須事項。この設計上「ループ回転数 = ゲーム速度」に直結するため、
  **FPS制御を外すとゲーム速度が壊れる**（実際に発生。下記の修正履歴を参照）。

## Web(pygbag)対応の要点

`pygbag_web移植ガイド.md` に集約。コード全体に適用済みのパターン:

- メインループ末尾で `await asyncio.sleep(0)` を1回だけ（VSync同期、時間指定NG）
- `dt = 1.0` 固定（フレーム単位、秒単位にしない）
- Rect/フォント/テキストSurface/描画Surfaceはすべて初期化時キャッシュ（WASMではオブジェクト生成が激重）
- 正解ブロック残数はカウンタ管理（毎フレームのリスト内包禁止）

## 修正履歴・既知の問題

### ✅ ローカル版が約77倍速になっていた（2026-07-17 修正）

`run.bat` でのローカル実行時、ボールが超高速で飛び操作不能だった。

- **原因**: Web移植時にメインループのペース制御を `await asyncio.sleep(0)` のみにしたため。
  これはブラウザのVSyncに同期する仕組みで、**VSyncの無いローカルCPythonでは即座に返る**。
  `self.clock` / `self.FPS = 60` は `__init__` にあるが `clock.tick()` がどこからも呼ばれていなかった。
  `dt = 1.0` 固定設計のため、ループ回転数がそのままゲーム速度になっていた。
- **実測**: 4608 FPS（≒77倍速）／ボール 21245 px/秒（設計値 277 px/秒）
- **修正**: `IS_WEB = (sys.platform == "emscripten")` で環境を判定し、
  **ローカルでのみ** ループ末尾で `self.clock.tick(self.FPS)` を呼ぶ。
  Web側は従来どおり `sleep(0)` のみ（移植ガイドの「二重待機を避ける」を維持）。
- **修正後**: 60.3 FPS ／ボール 281 px/秒（設計値どおり）

### ⚠️ 既知の問題（再開時に要対応）

1. ~~**【バグ】`WordManager.reset()` が存在しない**~~ → **修正済み（2026-07-17）**
   [game.py:432](game.py#L432) と [game.py:459](game.py#L459)（RESULT画面からの再スタート/ハードモード再挑戦）が `self.word_manager.reset()` を呼ぶのに、[word_manager.py](systems/word_manager.py) に `reset()` が未定義で、**全クリア後に再挑戦すると AttributeError でクラッシュしていた**。`reset()`（全単語をUNSEENに戻し、ミス回数もクリア）を追加し、`load_words()` の初期化もこれを使うよう統一。
   **⚠️ 公開中のWeb版にはこのバグが残っているため、再デプロイが必要。**

2. ~~**words.json の `choices` フィールドが未使用**~~ → **仕様（問題なし）**
   下記「設計上の意図」を参照。

3. **`BALL_MAX_VX`（config.py:24）が未使用のまま**
   `ball.py:41` で `self._max_vx` にキャッシュされるが、どこからも参照されていない（デッドコード）。パドル反射時の速度上昇（`+1.0`／回）に上限が無い状態。現状は壁・ブロック反射の減衰（×0.8）と釣り合っている想定だが、上限を効かせたいなら `reflect_paddle()` でクランプする必要がある。

4. **未コミットの残骸**
   - リポジトリ直下の `favicon.png` / `index.html` / `wordbraker.apk`（未追跡）は `build/web/` と同一内容のコピー。削除してよい。
   - `main` ブランチ向けの変更（改行コード＋移植ガイド2件の削除）が stash に退避中（`git stash list` 参照）。

## 今後の拡張候補（PROJECT_COMPLETION.md より）

- モバイル対応（タッチ操作） / ランキング / 逆向き出題（日→英） / 装飾ブロック活用 / PWA化
