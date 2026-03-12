# 新しい地図の追加手順

白地図クイズアプリに新しい地図問題を追加する手順。

## 前提条件

- Python 3 + OpenCV (`pip install -r tools/requirements.txt`)
- 作業ディレクトリ: プロジェクトルート (`white-map/`)

## 入力パラメータ

追加する地図の以下の情報をユーザーに確認する:

- **MAP_ID**: 英大文字の識別子（例: `KANAGAWA`, `TOKYO`, `USA`, `EUROPE`）
- **DISPLAY_NAME**: 日本語表示名（例: `神奈川県`, `東京都`, `アメリカ合衆国`）

## 手順

### Step 1: 画像の準備

`images/` ディレクトリに2枚のPNG画像があることを確認する:

- `images/{MAP_ID}0.png` — 白地図（黒い境界線のみ）
- `images/{MAP_ID}1.png` — ラベル付き地図（地名入り、照合用）

画像がない場合はユーザーに用意を依頼する。画像ソース: https://freemap.jp/

### Step 2: 領域抽出（PNG → raw JSON）

```bash
python3 tools/extract_regions.py images/{MAP_ID}0.png {MAP_ID} {DISPLAY_NAME} map-data/{MAP_ID}_raw.json
```

出力: `map-data/{MAP_ID}_raw.json`（仮ラベル `地域00`, `地域01`, ... が付いたJSON）

検出された領域数を確認し、想定と大きく異なる場合はユーザーに報告する。

### Step 3: デバッグ画像の生成

```bash
python3 tools/debug_regions.py map-data/{MAP_ID}_raw.json images/{MAP_ID}0.png map-data/{MAP_ID}_debug.png
```

出力: `map-data/{MAP_ID}_debug.png`（各領域を色分けし region_id を重ねた画像）

### Step 4: 比較画像の生成

```bash
python3 tools/debug_compare.py map-data/{MAP_ID}_debug.png images/{MAP_ID}1.png map-data/{MAP_ID}_compare.png
```

出力: `map-data/{MAP_ID}_compare.png`（デバッグ画像とラベル付き地図の横並び比較）

### Step 5: ラベルCSVテンプレートの生成

```bash
python3 tools/generate_label_csv.py map-data/{MAP_ID}_raw.json map-data/{MAP_ID}_labels.csv
```

出力: `map-data/{MAP_ID}_labels.csv`（`name`, `displayName` 列が空のCSV）

### Step 6: ラベル付け（region_id と地名の照合）

デバッグ画像 (`map-data/{MAP_ID}_debug.png`) とラベル付き地図 (`images/{MAP_ID}1.png`) を見比べ、各 region_id がどの地域に対応するかを特定する。

比較画像 (`map-data/{MAP_ID}_compare.png`) も参照すると照合しやすい。

照合結果をもとに `label_{MAP_ID小文字}.py` スクリプトを作成する。スクリプトの構成:

```python
#!/usr/bin/env python3
"""..."""
import json

# (region_id, name, displayName, is_main)
# is_main=True: クイズ出題対象, False: 飛び地・離島（本体と連動）
LABELS = [
    ("region_000", "地名", "正式名称", True),
    # 飛び地の場合: name/displayName を本体と同じにし is_main=False
    ("region_040", "地名", "正式名称", False),
]

# 除外するregion_id（地図外・凡例・隣接地域など）
EXCLUDE_IDS = {
    "region_000",  # 理由をコメント
}
```

既存のラベルスクリプトを参考にする:
- `tools/label_kanagawa.py` — 市区町村（政令市は区単位）
- `tools/label_tokyo.py` — 市区町村 + 23区 + 飛び地除外
- `tools/label_usa.py` — 州単位 + 飛び地（ミシガン上部半島等）

**ラベル付けのポイント:**
- `is_main=True` の領域がクイズ出題対象
- `is_main=False` は飛び地・離島・臨海埋立地で、`name`/`displayName` を本体と一致させることで親子紐付けされる
- `EXCLUDE_IDS` には地図外の領域（海、隣接する他県/国、凡例枠など）を指定
- region_id は面積の大きい順に `region_000`, `region_001`, ... と付番されている

### Step 7: ラベルスクリプトの実行

```bash
python3 tools/label_{MAP_ID小文字}.py
```

出力: `WhiteMapQuiz/WhiteMapQuiz/Resources/MapData/{MAP_ID}.json`

実行後の統計（出題対象数、飛び地数、合計、未ラベル）を確認する。未ラベルがある場合は Step 6 に戻って追加する。

### Step 8: アプリのビルド確認

```bash
cd WhiteMapQuiz && xcodegen generate && cd ..
xcodebuild build -project WhiteMapQuiz/WhiteMapQuiz.xcodeproj -scheme WhiteMapQuiz -destination "platform=macOS" -quiet
```

ビルドが成功し、新しい地図が地図選択画面に表示されることを確認する。

## ファイル一覧（生成物）

| ファイル | 用途 |
|---------|------|
| `images/{MAP_ID}0.png` | 白地図（入力） |
| `images/{MAP_ID}1.png` | ラベル付き地図（入力） |
| `map-data/{MAP_ID}_raw.json` | 抽出済み生JSON |
| `map-data/{MAP_ID}_debug.png` | デバッグ可視化画像 |
| `map-data/{MAP_ID}_compare.png` | 比較画像 |
| `map-data/{MAP_ID}_labels.csv` | ラベルCSVテンプレート |
| `tools/label_{map_id}.py` | ラベル付けスクリプト |
| `WhiteMapQuiz/.../MapData/{MAP_ID}.json` | アプリ用最終JSON |
