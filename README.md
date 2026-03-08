# 白地図クイズ (WhiteMapQuiz)

macOS / iOS (iPad) 対応の白地図クイズアプリ。市区町村・都道府県・国などの白地図をタップして地名を当てる学習アプリ。

## 機能仕様

### クイズフロー

1. **地図選択**: 複数の地図から回答する地図を選択
2. **クイズ開始**: 開始と同時にタイマーがスタート
3. **出題**: 回答すべき地域名（市区町村・県・国など）を画面に提示
4. **回答**: 該当する白地図の領域をクリック/タップ
5. **判定**:
   - 正答 → 該当箇所を色付きで塗り、次の問題へ
   - 誤答 → 再回答を求める（最大3回まで）
6. **全問完了** → 結果画面を表示

### スコアリング

| 回答回数 | 結果 | 色 | 点数 |
|---------|------|-----|------|
| 1回目で正答 | 正答 | 青色 | 4点 |
| 2回目で正答 | 正答 | 水色 | 2点 |
| 3回目で正答 | 正答 | 薄黄色 | 1点 |
| 3回とも誤答 | 誤答 | 灰色 | 0点 |

### 正答率

```
正答率 = 正答数 / 総回答数
```

- 総回答数には複数回の回答も加算する
- 例: 33問で 1回目正答20問, 2回目正答8問, 3回目正答3問, 不正解2問の場合
  - 正答数 = 31
  - 総回答数 = 20×1 + 8×2 + 3×3 + 2×3 = 51
  - 正答率 = 31 / 51 = 60.8%

### 記録

- 地図ごとに過去5回分の記録を保存
- 記録内容: 日時、経過時間、点数、正答率

### 地図データ

- 各地図は2種類の画像を用意
  - 白地図 (`{MAP_ID}0.png`): 境界線のみ
  - 回答付き地図 (`{MAP_ID}1.png`): 地名入り
- SVGパスデータはビルドツールで生成（開発者のみ地図の追加が可能）

## 技術スタック

| 項目 | 技術 |
|------|------|
| 言語 | Swift |
| UI | SwiftUI (macOS 14+ / iOS 17+) |
| アーキテクチャ | MVVM |
| 地図描画 | SVGパス → CGPath |
| タップ判定 | CGPath.contains() |
| データ保存 | SwiftData |
| ビルドツール | Python (OpenCV, svgpathtools) |

## プロジェクト構成

```
white-map/
├── README.md
├── images/                          # 元画像（ソース素材）
│   ├── KANAGAWA0.png                #   神奈川県 白地図
│   └── KANAGAWA1.png                #   神奈川県 回答付き
├── tools/                           # ビルドツール（Python）
│   ├── requirements.txt
│   ├── png_to_svg.py                #   PNG→SVG輪郭抽出
│   └── svg_to_json.py               #   SVG+ラベル→JSON変換
├── map-data/                        # 生成された中間SVG
└── WhiteMapQuiz/                    # Xcodeプロジェクト
    └── WhiteMapQuiz/
        ├── App/
        │   ├── WhiteMapQuizApp.swift
        │   └── ContentView.swift
        ├── Models/
        │   ├── MapDefinition.swift          # 地図定義（Codable）
        │   ├── RegionDefinition.swift       # 領域定義（Codable）
        │   ├── QuizSession.swift            # クイズ進行状態
        │   └── QuizRecord.swift             # 記録モデル（SwiftData）
        ├── ViewModels/
        │   ├── MapSelectionViewModel.swift
        │   ├── QuizViewModel.swift
        │   └── ResultViewModel.swift
        ├── Views/
        │   ├── MapSelection/
        │   │   ├── MapSelectionView.swift
        │   │   └── MapCardView.swift
        │   ├── Quiz/
        │   │   ├── QuizView.swift
        │   │   ├── MapCanvasView.swift      # SVG描画・タップ判定
        │   │   ├── QuestionBarView.swift    # 出題表示
        │   │   └── ScoreIndicatorView.swift
        │   └── Result/
        │       ├── ResultView.swift
        │       └── RecordHistoryView.swift
        ├── Services/
        │   ├── MapDataLoader.swift          # JSONリソース読込
        │   ├── PathHitTester.swift          # CGPath当たり判定
        │   └── QuizRecordStore.swift        # SwiftData永続化
        ├── Utilities/
        │   ├── SVGPathParser.swift          # SVGパス→CGPath変換
        │   ├── Color+Quiz.swift             # クイズ用カラー定数
        │   └── AdaptiveLayout.swift         # macOS/iPad対応
        └── Resources/
            ├── Assets.xcassets
            └── MapData/                     # バンドルされるJSON
                └── KANAGAWA.json
```

## データモデル

### 地図データ JSON

アプリにバンドルする地図データの構造:

```json
{
  "id": "KANAGAWA",
  "displayName": "神奈川県",
  "viewBox": { "width": 1000, "height": 800 },
  "regions": [
    {
      "id": "yokohama_nishi",
      "name": "西区",
      "displayName": "横浜市西区",
      "svgPath": "M 350 200 L 370 210 L 365 230 Z",
      "labelPoint": { "x": 360, "y": 215 }
    }
  ]
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `id` | String | 地図の一意識別子 |
| `displayName` | String | 表示名 |
| `viewBox` | Object | SVG座標系のサイズ (width, height) |
| `regions` | Array | 領域定義の配列 |
| `regions[].id` | String | 領域の一意識別子 |
| `regions[].name` | String | 出題時の表示名（短縮名） |
| `regions[].displayName` | String | 正式名称（結果画面用） |
| `regions[].svgPath` | String | SVGのd属性値（パスデータ） |
| `regions[].labelPoint` | Object | ラベル表示座標 (x, y) |

### クイズ記録 (SwiftData)

```swift
@Model
class QuizRecord {
    var mapId: String           // 地図ID
    var date: Date              // 実施日時
    var elapsedTime: TimeInterval // 経過時間（秒）
    var score: Int              // 獲得点数
    var totalQuestions: Int     // 総問題数
    var correctCount: Int       // 正答数
    var totalAttempts: Int      // 総回答数（正答率の分母）
}
```

## 画面設計

### 1. 地図選択画面

```
┌──────────────────────────────────────┐
│  白地図クイズ                         │
├──────────────────────────────────────┤
│                                      │
│  ┌─────────┐  ┌─────────┐           │
│  │ 神奈川県  │  │  ....    │           │
│  │ [サムネ]  │  │ [サムネ]  │           │
│  │ 33市区町村 │  │         │           │
│  │ 最高: 120 │  │         │           │
│  └─────────┘  └─────────┘           │
│                                      │
└──────────────────────────────────────┘
```

- `LazyVGrid` でカード表示
- 各カード: 地図名、領域数、ベストスコア

### 2. クイズ画面

```
┌──────────────────────────────────────┐
│ ⏱ 01:23  Q.12/33  ★48pt    [中断]   │
├──────────────────────────────────────┤
│                                      │
│         ┌─────────────────┐          │
│         │                 │          │
│         │   白地図SVG      │          │
│         │  (正答済は色付)   │          │
│         │                 │          │
│         └─────────────────┘          │
│                                      │
│  ┌────────────────────────────────┐  │
│  │  「横浜市西区」をタップしてください  │  │
│  │   ● ● ○  (残り試行回数)         │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

- 上部: タイマー、進捗、スコア、中断ボタン
- 中央: SVG地図キャンバス（ズーム/パン対応）
- 下部: 出題テキスト、試行回数インジケータ

### 3. 結果画面

```
┌──────────────────────────────────────┐
│           クイズ結果                   │
├──────────────────────────────────────┤
│                                      │
│    ⏱ 02:45    ★ 98 / 132点          │
│    正答率: 60.8%                      │
│                                      │
│    ┌─────────────────────┐           │
│    │ 色分け済み完成地図     │           │
│    └─────────────────────┘           │
│                                      │
│    過去の記録                          │
│    ┌──────┬──────┬─────┬──────┐      │
│    │ 日時  │ 時間  │ 点数 │ 正答率│      │
│    ├──────┼──────┼─────┼──────┤      │
│    │ 3/9  │ 2:45 │ 98  │ 61%  │      │
│    └──────┴──────┴─────┴──────┘      │
│                                      │
│   [もう一度]          [地図選択に戻る]  │
└──────────────────────────────────────┘
```

## 核心技術: SVGパスによるタップ判定

### 処理フロー

```
SVGパス文字列 → SVGPathParser → CGPath → CGPath.contains(point)
```

1. **SVGPathParser**: SVGの`d`属性文字列（M, L, C, Q, Z コマンド）を解析し `CGPath` に変換
2. **PathHitTester**: ビュー座標をviewBox座標に変換し、各領域の `CGPath.contains()` で判定
3. 面積の小さい領域を先に判定（小領域が大領域に囲まれるケースへの対策）

### 座標変換

```
ビュー座標 → (スケール・オフセット補正) → viewBox座標 → CGPath.contains() で判定
```

ズーム/パン操作時もスケール・オフセットを反映して正しく変換する。

## ビルドツール: 地図データ生成

### フロー

```
PNG白地図 → [png_to_svg.py] → 未ラベルSVG → [手動ラベル付け] → [svg_to_json.py] → JSON
```

#### ステップ1: `png_to_svg.py`

- OpenCVで白地図PNGの境界線を検出
- `findContours` → `approxPolyDP` で輪郭を簡略化
- 各閉領域をSVGの`path`要素として出力

#### ステップ2: 手動ラベル付け

- 生成されたSVGの各領域にIDと名前を割り当て
- CSVファイル (`{MAP_ID}_labels.csv`) として管理

#### ステップ3: `svg_to_json.py`

- SVGの`path`要素とラベルCSVを結合
- バウンディングボックス中心から`labelPoint`を自動算出
- アプリバンドル用JSONを出力

#### 依存パッケージ

```
opencv-python>=4.8
numpy>=1.24
svgwrite>=1.4
svgpathtools>=1.6
```

## 開発フェーズ

| Phase | 内容 |
|-------|------|
| 1 | Xcodeプロジェクト作成、SwiftDataセットアップ、NavigationStack |
| 2 | SVGPathParser + PathHitTester 実装・テスト |
| 3 | ビルドツール作成、神奈川県の地図JSONデータ作成 |
| 4 | MapCanvasView: SVGパス描画 + タップ判定統合 |
| 5 | QuizViewModel + QuizView: クイズのコアループ |
| 6 | ResultView + QuizRecordStore: 結果表示と記録保存 |
| 7 | MapSelectionView: 地図選択とナビゲーション |
| 8 | ズーム/パン対応、アニメーション、macOS最適化 |
| 9 | 追加地図データ、テスト、ポリッシュ |

## macOS / iPad 対応

| 要素 | iPad | macOS |
|------|------|-------|
| 地図選択 | LazyVGrid 2列 | 2-4列（ウィンドウ幅依存） |
| 地図キャンバス | 画面幅いっぱい | 左に地図、右にサイドパネル可 |
| ズーム | ピンチジェスチャー | トラックパッド / ScrollWheel |
| 最小ウィンドウ | - | 800×600 |

## ビルド & インストール

### 前提条件

- macOS 14 (Sonoma) 以降
- Xcode 15 以降
- Apple ID（無料でOK）

### 初回セットアップ

```bash
# xcodegen をインストール（未導入の場合）
brew install xcodegen

# Xcodeプロジェクトを生成
cd WhiteMapQuiz
xcodegen generate
```

### Mac 用ビルド & インストール

1. Xcodeでプロジェクトを開く

```bash
open WhiteMapQuiz/WhiteMapQuiz.xcodeproj
```

2. Signing 設定
   - 左のプロジェクトナビゲーターで「WhiteMapQuiz」プロジェクトを選択
   - 「Signing & Capabilities」タブを開く
   - 「Team」にApple IDを設定
   - 「Bundle Identifier」が赤くなっている場合は適宜変更

3. 実行先を「My Mac」に設定
   - Xcode上部のツールバーで実行先を「My Mac」に変更

4. ビルド & 実行
   - `Cmd + R` で実行
   - またはメニュー「Product > Run」

5. アプリとしてインストールしたい場合
   - メニュー「Product > Archive」でアーカイブを作成
   - 「Distribute App」→「Copy App」で .app ファイルを書き出し
   - 書き出した .app を `/Applications` フォルダにコピー

### iPad 用ビルド & インストール

1. iPadをMacにUSBケーブルで接続

2. Xcodeでプロジェクトを開く（Mac用と同じ）

```bash
open WhiteMapQuiz/WhiteMapQuiz.xcodeproj
```

3. Signing 設定（Mac用と同じ手順）

4. 実行先をiPadに設定
   - Xcode上部のツールバーで接続されたiPadを選択
   - 初回接続時は iPad 側で「このコンピュータを信頼」をタップ

5. iPad側のデベロッパモード有効化（初回のみ）
   - iPad の「設定 > プライバシーとセキュリティ > デベロッパモード」をON
   - 再起動が求められる場合あり

6. ビルド & 実行
   - `Cmd + R` で実行
   - 初回は iPad 側で「デベロッパを信頼」のダイアログが表示されるので許可
   - 信頼設定: iPad の「設定 > 一般 > VPNとデバイス管理」から開発者を信頼

### コマンドラインからビルド（CI/上級者向け）

```bash
cd WhiteMapQuiz

# Mac 用ビルド & インストール
xcodebuild archive \
  -project WhiteMapQuiz.xcodeproj \
  -scheme WhiteMapQuiz \
  -destination "platform=macOS" \
  -archivePath build/WhiteMapQuiz.xcarchive

xcodebuild -exportArchive \
  -archivePath build/WhiteMapQuiz.xcarchive \
  -exportOptionsPlist ExportOptions.plist \
  -exportPath build/export

# 方法1: 直接コピーでインストール
cp -r build/export/WhiteMapQuiz.app /Applications/

# 方法2: インストーラー(.pkg)を作成
pkgbuild \
  --root build/export \
  --install-location /Applications \
  --identifier com.whitemap.WhiteMapQuiz \
  --version 1.0 \
  build/WhiteMapQuiz.pkg

# build/WhiteMapQuiz.pkg をダブルクリックでインストール可能

# iPad 用ビルド（接続中のデバイス向け）
xcodebuild build \
  -project WhiteMapQuiz.xcodeproj \
  -scheme WhiteMapQuiz \
  -destination "platform=iOS,name=<iPadのデバイス名>"

# テスト実行
xcodebuild test \
  -project WhiteMapQuiz.xcodeproj \
  -scheme WhiteMapQuiz \
  -destination "platform=macOS"
```

## 参考

- [白磁図専門店](https://freemap.jp/)
