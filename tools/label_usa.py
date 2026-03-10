#!/usr/bin/env python3
"""アメリカ合衆国の地図JSONに州名ラベルを付与する

デバッグ画像(USA_debug.png)とラベル付き地図(USA1.png)の照合に基づく。

使い方:
    python label_usa.py
"""

import json

# デバッグ画像とUSA1.pngの照合結果に基づくマッピング
# (region_id, name, displayName, is_main)
# is_main=True: クイズの出題対象, False: 飛び地・離島（本体と連動）
LABELS = [
    # --- 西部 ---
    ("region_000", "テキサス州", "テキサス州", True),
    ("region_001", "モンタナ州", "モンタナ州", True),
    ("region_002", "アラスカ州", "アラスカ州", True),
    ("region_003", "カリフォルニア州", "カリフォルニア州", True),
    ("region_004", "オレゴン州", "オレゴン州", True),
    ("region_005", "ネバダ州", "ネバダ州", True),
    ("region_006", "ワイオミング州", "ワイオミング州", True),
    ("region_007", "ニューメキシコ州", "ニューメキシコ州", True),
    ("region_008", "ミネソタ州", "ミネソタ州", True),
    ("region_009", "コロラド州", "コロラド州", True),
    ("region_010", "アリゾナ州", "アリゾナ州", True),
    ("region_011", "ノースダコタ州", "ノースダコタ州", True),
    # region_012: ワシントン州の飛び地
    ("region_012", "ワシントン州", "ワシントン州", True),
    ("region_013", "サウスダコタ州", "サウスダコタ州", True),
    ("region_014", "アイダホ州", "アイダホ州", True),
    ("region_015", "ユタ州", "ユタ州", True),

    # --- 中西部 ---
    ("region_016", "ネブラスカ州", "ネブラスカ州", True),
    ("region_017", "カンザス州", "カンザス州", True),
    ("region_018", "ミズーリ州", "ミズーリ州", True),
    ("region_019", "ウィスコンシン州", "ウィスコンシン州", True),
    ("region_020", "オクラホマ州", "オクラホマ州", True),
    ("region_021", "アイオワ州", "アイオワ州", True),

    # --- 北東部 ---
    ("region_022", "ニューヨーク州", "ニューヨーク州", True),
    ("region_024", "ペンシルベニア州", "ペンシルベニア州", True),

    # --- 南部 ---
    ("region_023", "ジョージア州", "ジョージア州", True),
    ("region_025", "アーカンソー州", "アーカンソー州", True),
    ("region_026", "ミシガン州", "ミシガン州", True),          # 下部半島（本体）
    ("region_027", "アラバマ州", "アラバマ州", True),
    ("region_028", "ノースカロライナ州", "ノースカロライナ州", True),
    ("region_029", "フロリダ州", "フロリダ州", True),
    ("region_030", "オハイオ州", "オハイオ州", True),
    ("region_031", "ミシシッピ州", "ミシシッピ州", True),
    ("region_032", "メイン州", "メイン州", True),
    ("region_033", "ルイジアナ州", "ルイジアナ州", True),
    ("region_034", "テネシー州", "テネシー州", True),
    ("region_035", "ケンタッキー州", "ケンタッキー州", True),
    ("region_036", "インディアナ州", "インディアナ州", True),
    ("region_037", "バージニア州", "バージニア州", True),
    ("region_038", "サウスカロライナ州", "サウスカロライナ州", True),
    ("region_039", "ウェストバージニア州", "ウェストバージニア州", True),

    # --- 飛び地 ---
    ("region_040", "ミシガン州", "ミシガン州", False),          # ミシガン上部半島

    # --- ニューイングランド ---
    ("region_041", "バーモント州", "バーモント州", True),
    ("region_042", "ニューハンプシャー州", "ニューハンプシャー州", True),
    ("region_043", "マサチューセッツ州", "マサチューセッツ州", True),
    ("region_044", "ニュージャージー州", "ニュージャージー州", True),
    ("region_045", "コネチカット州", "コネチカット州", True),
    ("region_046", "メリーランド州", "メリーランド州", True),
    ("region_047", "ハワイ州", "ハワイ州", True),

    # --- 飛び地 ---
    ("region_048", "メリーランド州", "メリーランド州", False),  # メリーランド東部

    ("region_049", "デラウェア州", "デラウェア州", True),
    ("region_050", "ロードアイランド州", "ロードアイランド州", True),
    ("region_051", "ワシントンD.C.", "ワシントンD.C.", True),
    ("region_052", "イリノイ州", "イリノイ州", True),
]

# 除外するregion_id（地図外・凡例・隣国など）
EXCLUDE_IDS = set()


def main():
    json_path = "map-data/USA_raw.json"
    output_path = "WhiteMapQuiz/WhiteMapQuiz/Resources/MapData/USA.json"

    with open(json_path, "r") as f:
        data = json.load(f)

    # ラベルをdictに変換（最初のエントリが優先）
    label_map = {}
    for region_id, name, display_name, is_main in LABELS:
        if region_id not in label_map:
            label_map[region_id] = (name, display_name, is_main)

    # 飛び地→本体のマッピング
    main_regions = {}
    for region_id, name, display_name, is_main in LABELS:
        if is_main and display_name not in main_regions:
            main_regions[display_name] = region_id

    # 除外IDを除いた新しいregionsリストを構築
    new_regions = []
    unlabeled = []

    for region in data["regions"]:
        rid = region["id"]

        # 除外対象はスキップ
        if rid in EXCLUDE_IDS:
            print(f"  除外: {rid}")
            continue

        if rid in label_map:
            name, display_name, is_main = label_map[rid]
            region["name"] = name
            region["displayName"] = display_name
            if not is_main:
                main_id = main_regions.get(display_name, rid)
                region["parentId"] = main_id
        else:
            unlabeled.append(rid)

        new_regions.append(region)

    # 重複IDを解消（飛び地の_sub接尾辞）
    id_counts = {}
    for region in new_regions:
        if "parentId" in region:
            main_id = region["parentId"]
            sub_id = f"{main_id}_sub"
            if sub_id in id_counts:
                id_counts[sub_id] += 1
                region["id"] = f"{sub_id}_{id_counts[sub_id]}"
            else:
                id_counts[sub_id] = 0
                region["id"] = sub_id

    data["regions"] = new_regions
    data["displayName"] = "アメリカ合衆国"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 統計
    main_count = sum(1 for r in new_regions if "parentId" not in r)
    sub_count = sum(1 for r in new_regions if "parentId" in r)
    print(f"\nラベル付け完了: {output_path}")
    print(f"  出題対象（本体）: {main_count}")
    print(f"  飛び地・離島: {sub_count}")
    print(f"  合計: {len(new_regions)}")

    if unlabeled:
        print(f"\n  未ラベル: {unlabeled}")
        print("  デバッグ画像を確認してラベルを追加してください")


if __name__ == "__main__":
    main()
