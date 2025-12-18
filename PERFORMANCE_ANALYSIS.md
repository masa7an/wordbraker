# パフォーマンス分析レポート

## 調査日: 2025-12-18

## 1. Ball.update() / reflect の呼び出し回数

### Ball.update()
- **呼び出し箇所**: `game.py` の `update()` メソッド内（327行目）
- **呼び出し回数**: **1回/フレーム**（ボールが発射されている場合のみ）
- **評価**: ✅ 問題なし（最適化不要）

### reflect メソッドの呼び出し

#### reflect_x()
- **呼び出し箇所**:
  1. `systems/collision.py` → `check_ball_wall_collision()` （左右の壁に当たった時）
  2. `systems/collision.py` → `check_ball_block_collision()` （ブロックの左右に当たった時）
- **呼び出し回数**: 衝突時のみ（通常は0回/フレーム、衝突時は1回/フレーム）
- **評価**: ✅ 問題なし（衝突時のみ呼ばれる）

#### reflect_y()
- **呼び出し箇所**:
  1. `systems/collision.py` → `check_ball_wall_collision()` （上の壁に当たった時）
  2. `systems/collision.py` → `check_ball_block_collision()` （ブロックの上下に当たった時）
- **呼び出し回数**: 衝突時のみ（通常は0回/フレーム、衝突時は1回/フレーム）
- **評価**: ✅ 問題なし（衝突時のみ呼ばれる）

#### reflect_paddle()
- **呼び出し箇所**:
  1. `systems/collision.py` → `check_ball_paddle_collision()` （パドルに当たった時）
- **呼び出し回数**: 衝突時のみ（通常は0回/フレーム、衝突時は1回/フレーム）
- **評価**: ✅ 問題なし（衝突時のみ呼ばれる）

---

## 2. ブロック衝突側のループ構造

### 現在の実装

```python
# systems/collision.py
def check_ball_blocks_collision(ball, blocks, door_unlocked=False):
    for block in blocks:  # ← 全ブロックをループ
        if check_ball_block_collision(ball, block, door_unlocked):
            destroyed = block.hit()
            return (block, destroyed)  # ← 早期終了
    return (None, False)
```

### 呼び出し箇所
- **呼び出し箇所**: `game.py` の `update()` メソッド内（361行目）
- **呼び出し回数**: **1回/フレーム**（ボールが発射されている場合のみ）

### 問題点

1. **全ブロックを毎フレームチェック**
   - 現在のステージでは3ブロックのみ（問題なし）
   - 将来的にブロック数が増えるとパフォーマンスに影響
   - 最悪ケース: 全ブロック数分のループ（例: 30ブロック = 30回のループ/フレーム）

2. **check_ball_block_collision() の処理コスト**
   - `ball.get_rect()` と `block.get_rect()` の呼び出し（キャッシュ済み ✅）
   - `ball_rect.colliderect(block_rect)` の呼び出し（軽量）
   - 前フレーム位置の推定計算（`prev_x`, `prev_y`）
   - 4つの距離計算（`dist_to_left`, `dist_to_right`, `dist_to_top`, `dist_to_bottom`）
   - `min()` 関数の呼び出し
   - 位置補正処理

3. **早期終了の効果**
   - 衝突が見つかったら即座に `return`（良い ✅）
   - しかし、衝突が見つかるまで全ブロックをチェックする可能性がある

### 最適化の余地

#### 優先度: 中（現時点では問題なし、将来的に検討）

1. **空間分割（Spatial Partitioning）**
   - 画面をグリッドに分割し、ボールの位置に近いブロックのみをチェック
   - 効果: ブロック数が増えた場合に有効（例: 30ブロック → 3ブロックのみチェック）
   - 実装コスト: 中（グリッド管理の追加が必要）

2. **ブロックの事前フィルタリング**
   - 破壊済みブロックをリストから除外（現在は `is_destroyed()` でチェック）
   - 効果: ループ回数の削減
   - 実装コスト: 低（破壊時にリストから削除）

3. **距離による事前判定**
   - ボールとブロックの距離を計算し、近いブロックのみをチェック
   - 効果: 遠いブロックのチェックをスキップ
   - 実装コスト: 中（距離計算の追加が必要）

---

## 3. その他のボトルネック候補

### 確認済み（最適化済み）
- ✅ テキスト描画のキャッシュ化
- ✅ ブロックの描画をSurface blitに変更
- ✅ パドル・扉の描画をSurface blitに変更
- ✅ Ballの描画をSurface blitに変更
- ✅ Rectオブジェクトのキャッシュ
- ✅ フォントの初期化時キャッシュ
- ✅ 正解ブロック残数をカウンタ管理

### 未確認（今後の調査候補）
- [ ] 音声再生のオーバーヘッド（`sound_manager.play()`）
- [ ] イベント処理のオーバーヘッド（`pygame.event.get()`）
- [ ] 画面更新のオーバーヘッド（`pygame.display.flip()`）
- [ ] 非同期処理のオーバーヘッド（`await asyncio.sleep()`）

---

## 4. 推奨される次のステップ

1. **現時点では問題なし**
   - ブロック数が少ない（3ブロック）ため、ループの最適化は不要
   - FPSは60を維持している

2. **将来的な最適化（ブロック数が増えた場合）**
   - 空間分割の実装を検討
   - 破壊済みブロックのリストからの除外を検討

3. **その他の最適化**
   - 音声再生のオーバーヘッドを調査（必要に応じて）
   - イベント処理の最適化（必要に応じて）

---

## 5. 結論

- **Ball.update() / reflect**: 問題なし ✅
- **ブロック衝突のループ**: 現時点では問題なし、将来的に最適化の余地あり
- **全体的な評価**: 描画最適化は完了しており、衝突判定は現時点で問題なし

---

## 6. フレーム時間詳細計測結果（2025-12-18）

### 計測結果（480フレーム、Web環境）

#### 最適化前（初回計測）
```
Total frames measured: 481

Breakdown by process:
  Event processing:  avg=0.016ms, min=0.000ms, max=0.200ms, median=0.000ms
  Update logic:      avg=0.065ms, min=0.000ms, max=0.600ms, median=0.100ms
  Draw rendering:   avg=12.019ms, min=7.000ms, max=47.900ms, median=11.000ms
  Display flip:     avg=1.135ms, min=0.800ms, max=2.400ms, median=1.100ms
  await sleep:      avg=39.157ms, min=33.500ms, max=50.500ms, median=38.500ms
  Total frame:      avg=52.407ms, min=49.200ms, max=83.500ms, median=50.100ms

Analysis:
  Event:  0.0% of total frame time
  Update: 0.1% of total frame time
  Draw:   22.9% of total frame time
  Flip:   2.2% of total frame time
  Sleep:  74.7% of total frame time
```

#### 最適化後（await sleep最適化実装後）
```
Total frames measured: 481

Breakdown by process:
  Event processing:  avg=0.018ms, min=0.000ms, max=0.200ms, median=0.000ms
  Update logic:      avg=0.056ms, min=0.000ms, max=0.400ms, median=0.100ms
  Draw rendering:   avg=11.214ms, min=6.900ms, max=49.000ms, median=10.800ms
  Display flip:     avg=1.092ms, min=0.800ms, max=1.800ms, median=1.100ms
  await sleep:      avg=35.160ms, min=17.100ms, max=42.000ms, median=37.500ms
  Total frame:      avg=47.552ms, min=32.900ms, max=83.300ms, median=50.000ms

Analysis:
  Event:  0.0% of total frame time
  Update: 0.1% of total frame time
  Draw:   23.6% of total frame time
  Flip:   2.3% of total frame time
  Sleep:  73.9% of total frame time
```

#### 最適化後（計測カウンタ表示削除後）
```
Total frames measured: 481

Breakdown by process:
  Event processing:  avg=0.018ms, min=0.000ms, max=0.200ms, median=0.000ms
  Update logic:      avg=0.061ms, min=0.000ms, max=0.500ms, median=0.100ms
  Draw rendering:   avg=10.499ms, min=5.700ms, max=48.500ms, median=10.000ms
  Display flip:     avg=1.161ms, min=0.800ms, max=2.100ms, median=1.100ms
  await sleep:      avg=36.213ms, min=17.600ms, max=43.400ms, median=38.500ms
  Total frame:      avg=47.967ms, min=33.100ms, max=83.400ms, median=50.000ms

Analysis:
  Event:  0.0% of total frame time
  Update: 0.1% of total frame time
  Draw:   21.9% of total frame time
  Flip:   2.4% of total frame time
  Sleep:  75.5% of total frame time
```

#### 最適化後（テキスト描画キャッシュ化後）
```
Total frames measured: 481

Breakdown by process:
  Event processing:  avg=0.018ms, min=0.000ms, max=0.200ms, median=0.000ms
  Update logic:      avg=0.060ms, min=0.000ms, max=0.400ms, median=0.100ms
  Draw rendering:   avg=7.008ms, min=2.600ms, max=31.500ms, median=6.200ms
  Display flip:     avg=1.533ms, min=0.800ms, max=4.100ms, median=1.400ms
  await sleep:      avg=38.951ms, min=11.400ms, max=48.700ms, median=41.900ms
  Total frame:      avg=47.585ms, min=32.600ms, max=66.600ms, median=50.000ms

Analysis:
  Event:  0.0% of total frame time
  Update: 0.1% of total frame time
  Draw:   14.7% of total frame time
  Flip:   3.2% of total frame time
  Sleep:  81.9% of total frame time
```

#### 最適化後（音声無効化後）
```
Total frames measured: 481

Breakdown by process:
  Event processing:  avg=0.017ms, min=0.000ms, max=0.200ms, median=0.000ms
  Update logic:      avg=0.062ms, min=0.000ms, max=0.200ms, median=0.100ms
  Draw rendering:   avg=7.327ms, min=2.500ms, max=45.500ms, median=6.400ms
  Display flip:     avg=1.564ms, min=0.800ms, max=4.100ms, median=1.300ms
  await sleep:      avg=38.457ms, min=14.400ms, max=46.900ms, median=41.500ms
  Total frame:      avg=47.447ms, min=32.500ms, max=66.200ms, median=50.000ms

Analysis:
  Event:  0.0% of total frame time
  Update: 0.1% of total frame time
  Draw:   15.4% of total frame time
  Flip:   3.3% of total frame time
  Sleep:  81.1% of total frame time
```

#### 最適化後（await asyncio.sleep(0) に変更 - Geminiのアドバイス）✅ **劇的改善**
```
Total frames measured: 481

Breakdown by process:
  Event processing:  avg=0.014ms, min=0.000ms, max=0.200ms, median=0.000ms
  Update logic:      avg=0.045ms, min=0.000ms, max=0.200ms, median=0.000ms
  Draw rendering:   avg=7.310ms, min=5.600ms, max=54.600ms, median=8.100ms
  Display flip:     avg=0.960ms, min=0.800ms, max=1.100ms, median=1.000ms
  await sleep:      avg=8.423ms, min=0.700ms, max=10.500ms, median=7.600ms
  Total frame:      avg=16.764ms, min=15.900ms, max=56.700ms, median=16.700ms

Analysis:
  Event:  0.1% of total frame time
  Update: 0.3% of total frame time
  Draw:   43.6% of total frame time
  Flip:   5.7% of total frame time
  Sleep:  50.2% of total frame time
```

**改善サマリー:**
- **初回計測**: await sleep 39.2ms（74.7%）、Total 52.4ms（約19FPS）、Draw 12.0ms（22.9%）
- **await sleep最適化後**: await sleep 35.2ms（73.9%）、Total 47.6ms（約21FPS）、Draw 11.2ms（23.6%）
  - await sleep: 約4ms削減（10%改善）
  - Total frame: 約5ms削減（10%改善）
  - 実効FPS: 19FPS → 21FPS（約10%改善）
- **計測カウンタ削除後**: await sleep 36.2ms（75.5%）、Total 48.0ms（約21FPS）、Draw 10.5ms（21.9%）
  - Draw rendering: 11.2ms → 10.5ms（約0.7ms削減、6%改善）
  - Draw の割合: 23.6% → 21.9%（約1.7%改善）
- **テキスト描画キャッシュ化後**: await sleep 38.9ms（81.9%）、Total 47.6ms（約21FPS）、Draw 7.0ms（14.7%）
  - **Draw rendering: 10.5ms → 7.0ms（約3.5ms削減、33%改善）** ✅
  - **Draw の割合: 21.9% → 14.7%（約7.2%改善）** ✅
  - **最大値: 48.5ms → 31.5ms（約17ms削減、35%改善）** ✅
  - 描画スパイクの大幅削減
  - `font.render()` の呼び出し回数削減（毎フレーム4回 → 通常0回）
- **音声無効化後**: await sleep 38.5ms（81.1%）、Total 47.4ms（約21FPS）、Draw 7.3ms（15.4%）
  - **音声無効化による影響: ほぼなし（誤差範囲内）** ✅
  - Draw rendering: 7.0ms → 7.3ms（約0.3ms増加、誤差範囲）
  - await sleep: 38.9ms → 38.5ms（約0.4ms削減、誤差範囲）
  - Total frame: 47.6ms → 47.4ms（約0.2ms削減、誤差範囲）
  - **結論: 音声再生のオーバーヘッドは無視できるレベル**
- **await asyncio.sleep(0) に変更後（Geminiのアドバイス）**: await sleep 8.4ms（50.2%）、Total 16.8ms（約60FPS）、Draw 7.3ms（43.6%）
  - **await sleep: 38.5ms → 8.4ms（約30ms削減、78%改善）** ✅✅✅
  - **Total frame: 47.4ms → 16.8ms（約30ms削減、65%改善）** ✅✅✅
  - **実効FPS: 21FPS → 約60FPS（約3倍改善）** ✅✅✅
  - **体感の「もっさり感」が劇的に改善（ユーザー確認済み）** ✅✅✅
  - **結論: Geminiのアドバイスが正しかった。await asyncio.sleep(0) によるVSync同期が最適解**

### 問題点の特定

1. **await asyncio.sleep() が最大のボトルネック（74.7%）**
   - 平均39.2ms（目標16.7msの約2.3倍）
   - GPT5.2の指摘通り、「Web移植時のフレーム駆動方式」が原因
   - Python ↔ JS ↔ ブラウザ描画同期の待ち時間が大きい

2. **描画処理も重い（22.9%）**
   - 平均12.0ms（最適化の余地あり）
   - 最大47.9ms（スパイク発生）

3. **実効FPSが低い**
   - 平均52.4ms/フレーム = 約19FPS（目標60FPSの約1/3）
   - 体感の「もっさり感」の原因

### 最適化の優先順位

#### 優先度: 最高
1. **await asyncio.sleep() の最適化** ✅ 実装済み（一部改善）
   - ✅ 条件付きsleep（処理時間に応じて調整） - 実装済み
   - **最適化前**: 平均39.2ms（74.7%）、Total: 52.4ms（約19FPS）
   - **最適化後**: 平均35.2ms（73.9%）、Total: 47.6ms（約21FPS）
   - **改善**: 約4ms削減（10%改善）、最小値17.1ms（最適化は効いている）
   - **残課題**: 平均がまだ高い（目標16.7msの約2倍）
   - **次のステップ**: 
     - `await asyncio.sleep()` 自体のオーバーヘッド調査
     - 最小待機時間（0.001秒）の見直し
     - より積極的な最適化（フレームスキップ制御など）
     - `requestAnimationFrame` 主導の構造への変更を検討

#### 優先度: 高
2. **描画処理のさらなる最適化**
   - 描画スパイク（最大47.9ms）の原因調査
   - 不要な描画の削減
   - 描画バッファリングの検討

#### 優先度: 中
3. **その他の最適化**
   - イベント処理の最適化（現時点では0.0%なので不要）
   - 更新処理の最適化（現時点では0.1%なので不要）

### 次のステップ

1. **await asyncio.sleep() の最適化**
   - 処理時間を計測し、残り時間だけsleepする
   - 例: `await asyncio.sleep(max(0, frame_interval - elapsed_time))`

2. **描画処理の最適化**
   - 描画スパイクの原因を特定
   - 不要な描画の削減

3. **requestAnimationFrame 主導への移行**
   - pygbagの制約を確認
   - 可能であれば、Python側のフレーム制御を最小化

