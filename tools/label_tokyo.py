#!/usr/bin/env python3
"""東京都の地図JSONに正確なラベルを付与する

デバッグ画像(TOKYO_debug.png)とラベル付き地図(TOKYO1.png)の照合に基づく。
TOKYO_labels.csvの内容を元にマッピング。

使い方:
    python label_tokyo.py
"""

import json

# TOKYO_labels.csvの照合結果に基づくマッピング
# (region_id, name, displayName, is_main)
# is_main=True: クイズの出題対象, False: 飛び地（本体と連動）
LABELS = [
    # --- 西多摩 ---
    ("region_003", "奥多摩町", "奥多摩町", True),
    ("region_006", "檜原村", "檜原村", True),
    ("region_007", "青梅市", "青梅市", True),
    ("region_009", "あきる野市", "あきる野市", True),
    ("region_020", "日の出町", "日の出町", True),
    ("region_034", "瑞穂町", "瑞穂町", True),
    ("region_051", "羽村市", "羽村市", True),
    ("region_054", "福生市", "福生市", True),

    # --- 北多摩（西） ---
    ("region_037", "武蔵村山市", "武蔵村山市", True),
    ("region_042", "東大和市", "東大和市", True),
    ("region_031", "昭島市", "昭島市", True),
    ("region_022", "立川市", "立川市", True),
    ("region_027", "小平市", "小平市", True),
    ("region_033", "東村山市", "東村山市", True),
    ("region_049", "国分寺市", "国分寺市", True),
    ("region_056", "国立市", "国立市", True),
    ("region_046", "小金井市", "小金井市", True),

    # --- 北多摩（東） ---
    ("region_058", "清瀬市", "清瀬市", True),
    ("region_043", "東久留米市", "東久留米市", True),
    ("region_035", "西東京市", "西東京市", True),
    ("region_057", "武蔵野市", "武蔵野市", True),

    # --- 南多摩 ---
    ("region_004", "八王子市", "八王子市", True),
    ("region_021", "日野市", "日野市", True),
    ("region_024", "多摩市", "多摩市", True),
    ("region_032", "稲城市", "稲城市", True),
    ("region_019", "府中市", "府中市", True),
    ("region_025", "調布市", "調布市", True),
    ("region_036", "三鷹市", "三鷹市", True),
    ("region_059", "狛江市", "狛江市", True),
    ("region_010", "町田市", "町田市", True),

    # --- 23区 ---
    ("region_014", "練馬区", "練馬区", True),
    ("region_018", "板橋区", "板橋区", True),
    ("region_026", "北区", "北区", True),
    ("region_012", "足立区", "足立区", True),
    ("region_052", "荒川区", "荒川区", True),
    ("region_044", "豊島区", "豊島区", True),
    ("region_038", "中野区", "中野区", True),
    ("region_016", "杉並区", "杉並区", True),
    ("region_029", "新宿区", "新宿区", True),
    ("region_047", "文京区", "文京区", True),
    ("region_050", "台東区", "台東区", True),
    ("region_017", "葛飾区", "葛飾区", True),
    ("region_041", "墨田区", "墨田区", True),
    ("region_040", "渋谷区", "渋谷区", True),
    ("region_048", "千代田区", "千代田区", True),
    ("region_053", "中央区", "中央区", True),
    ("region_028", "港区", "港区", True),
    ("region_023", "江東区", "江東区", True),
    ("region_011", "世田谷区", "世田谷区", True),
    ("region_039", "目黒区", "目黒区", True),
    ("region_030", "品川区", "品川区", True),
    ("region_013", "大田区", "大田区", True),
    ("region_015", "江戸川区", "江戸川区", True),

    # --- 飛び地 ---
    ("region_061", "品川区", "品川区", False),       # 品川区臨海部
    ("region_064", "江東区", "江東区", False),       # 江東区臨海部
]

# 除外するregion_id（地図外・凡例など）
EXCLUDE_IDS = {
    "region_000",  # 海/他県（南側大領域）
    "region_001",  # 他県（左側・山梨/埼玉）
    "region_002",  # 他県（右側・千葉/海）
    "region_005",  # 他県（右上・埼玉/千葉）
    "region_008",  # 凡例周辺
    "region_045",  # 凡例枠
    "region_055",  # 右上端
    "region_060",  # 川崎市（神奈川県）
    "region_062",  # 千葉県
    "region_063",  # 地図外
}


def main():
    json_path = "map-data/TOKYO_raw.json"
    output_path = "WhiteMapQuiz/WhiteMapQuiz/Resources/MapData/TOKYO.json"

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
    data["displayName"] = "東京都"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 統計
    main_count = sum(1 for r in new_regions if "parentId" not in r)
    sub_count = sum(1 for r in new_regions if "parentId" in r)
    print(f"\nラベル付け完了: {output_path}")
    print(f"  出題対象（本体）: {main_count}")
    print(f"  飛び地・臨海部: {sub_count}")
    print(f"  合計: {len(new_regions)}")

    if unlabeled:
        print(f"\n  未ラベル: {unlabeled}")
        print("  デバッグ画像を確認してラベルを追加してください")


if __name__ == "__main__":
    main()
