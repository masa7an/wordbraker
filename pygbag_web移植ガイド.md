# pygbag / WebAssembly 移植ガイド

> **対象**: pygbag（Pygame→WebAssembly）移植作業を行うAIエージェント  
> **目的**: Web環境特有の問題を事前に回避する

---

## ■ 非同期処理の設計原則

pygbag は **ブラウザのイベントループと協調** して動作する。  
`await asyncio.sleep(0)` は「最低限の譲渡」であり、**万能ではない**。

### 🚫 禁止事項

| 禁止 | 理由 |
|------|------|
| `pygame.time.wait()` | ブラウザをブロックする |
| `time.sleep()` | ブラウザをブロックする |
| `clock.tick()` のみでのFPS制御 | Web環境では期待通り動作しない |
| フレーム毎の `asyncio.create_task()` | タスク未回収でメモリ詰まり |
| 1フレーム内での重い計算・大量ループ | 描画更新が止まる |

### ✅ 必須事項

```python
# FPS制御は await asyncio.sleep(0) を使用（VSync同期）
# 時間指定（sleep(0.016)など）はNG - ブラウザのタイミングとズレる
await asyncio.sleep(0)  # ループの最後に1回だけ呼ぶ

# dt はフレーム単位で固定（秒単位にしない）
dt = 1.0  # NOT: dt_ms / 1000.0
```

### ⚠️ 重要な注意事項

1. **時間指定はNG**
   - ❌ `await asyncio.sleep(0.016)` や `await asyncio.sleep(1/60)` のように時間指定してはいけません
   - ブラウザのタイミングとズレて、カクつきの原因になります
   - ✅ `await asyncio.sleep(0)` を使用してください（VSync同期）

2. **await asyncio.sleep(0) の呼び出し**
   - ✅ メインループの**最後に1回だけ**呼ぶ
   - ❌ ループの途中や、衝突判定の for ループ内などで呼んではいけません
   - 呼ぶたびに次のフレームまで待たされるため、劇的に遅くなります

---

## ■ パフォーマンス最適化（WASM環境では必須）

WebAssembly上のPythonは **オブジェクト生成が激重**。  
ネイティブPygameで許された処理密度は、Webでは即ボトルネックになる。

### 🚫 毎フレームで行ってはいけないこと

```python
# ❌ 毎フレームRect生成
def get_rect(self):
    return pygame.Rect(self.x, self.y, self.w, self.h)

# ❌ 毎フレームフォント読み込み
font = get_japanese_font(size)

# ❌ 毎フレームリスト内包表記で全走査
correct = [b for b in blocks if b.is_correct()]
```

### ✅ 正しいパターン

```python
# ✅ 初期化時にキャッシュ、座標のみ更新
def __init__(self):
    self._rect = pygame.Rect(x, y, w, h)

def update(self):
    self._rect.x = self.x
    self._rect.y = self.y

# ✅ フォントは初期化時にキャッシュ
self.font_cache = get_japanese_font(size)

# ✅ カウンタで管理
self.remaining_count -= 1
if self.remaining_count == 0: ...
```

---

## ■ 入力デバイス共存パターン

マウスとゲームパッド（十字キー/スティック）を併用する場合、  
**仮想位置パターン** を使用すること。

### ⚠️ ゲームパッドについて

**Web環境ではゲームパッドは非推奨**です。
- ゲームパッドのトリガー取得がWebでは難しい
- 代わりにキーボードの左右キー（←→）を使用することを推奨
- ゲームパッド対応は実装可能だが、Web環境での動作が不安定な場合がある

```python
self.virtual_paddle_x = SCREEN_WIDTH // 2
self.prev_mouse_x = None

# マウスは絶対位置（実際に動いた時のみ）
if mouse_x != self.prev_mouse_x:
    self.virtual_paddle_x = mouse_x
    self.prev_mouse_x = mouse_x

# ゲームパッドは相対移動
self.virtual_paddle_x += hat_x * speed

# パドルは仮想位置を参照
paddle.update(self.virtual_paddle_x)
```

---

## ■ デバッグ・安全設計

```python
# フレームカウンタ（暴走検知用）
self.frame_count = 0
MAX_FRAMES = 100000

while self.running:
    self.frame_count += 1
    if self.frame_count > MAX_FRAMES:
        print("Emergency stop: too many frames")
        break
    # ...
    await asyncio.sleep(1/60)
```

---

## ■ RTA用タイマー表示

コンマ秒数表示は **毎フレーム更新しない**（間引き表示にする）。

```python
# 100ms間隔で更新
if current_time - self.last_timer_update > 100:
    self.display_time = format_time(current_time)
    self.last_timer_update = current_time
```

---

## ✅ pygbag移植チェックリスト

### 非同期処理
- [ ] `pygame.time.wait()` / `time.sleep()` を使用していない
- [ ] `await asyncio.sleep(0)` をループの最後に1回だけ呼んでいる（時間指定はNG）
- [ ] `clock.tick()` に依存していない
- [ ] 1フレーム内に重い処理がない
- [ ] `asyncio.create_task()` を毎フレーム呼んでいない

### パフォーマンス
- [ ] `pygame.Rect` は初期化時にキャッシュしている
- [ ] フォントは初期化時にキャッシュしている
- [ ] 毎フレームのリスト内包表記を排除した
- [ ] dt はフレーム単位（`dt = 1.0`）で計算している

### 入力デバイス
- [ ] マウス/ゲームパッド併用時は仮想位置パターンを使用
- [ ] ゲームパッドは非推奨（Web環境ではキーボードの左右キーを推奨）

### 表示
- [ ] RTA用タイマーは間引き表示している

### 安全設計
- [ ] フレームカウンタ等の暴走検知がある
- [ ] エラー時にループを抜ける手段がある

