#!/usr/bin/env python3
"""アジアの地図JSONに国名ラベルを付与する

CSVラベルデータに基づく。

使い方:
    python label_asia.py
"""

import json

# CSVラベルデータに基づくマッピング
# (region_id, name, displayName, is_main)
# is_main=True: クイズの出題対象, False: 飛び地・離島（本体と連動）
# ※ groupIdは GROUPS で別途定義
LABELS = [
    ("region_001", "中華人民共和国", "中華人民共和国", True),
    ("region_002", "カザフスタン", "カザフスタン", True),
    ("region_003", "インド", "インド", True),
    ("region_004", "モンゴル", "モンゴル", True),
    ("region_005", "サウジアラビア", "サウジアラビア", True),
    ("region_006", "イラン", "イラン", True),
    ("region_009", "パキスタン", "パキスタン", True),
    ("region_011", "トルコ", "トルコ", True),
    ("region_012", "アフガニスタン", "アフガニスタン", True),
    ("region_014", "トルクメニスタン", "トルクメニスタン", True),
    ("region_015", "ミャンマー", "ミャンマー", True),
    ("region_016", "ウズベキスタン", "ウズベキスタン", True),
    ("region_018", "イラク", "イラク", True),
    ("region_023", "イエメン", "イエメン", True),
    ("region_025", "タイ", "タイ", True),
    ("region_027", "インドネシア", "インドネシア", True),
    ("region_029", "オマーン", "オマーン", True),
    ("region_031", "インドネシア", "インドネシア", False),
    ("region_032", "キルギス", "キルギス", True),
    ("region_035", "日本", "日本", True),
    ("region_036", "シリア", "シリア", True),
    ("region_039", "パキスタン", "パキスタン", False),
    ("region_040", "ラオス", "ラオス", True),
    ("region_041", "インド", "インド", False),
    ("region_042", "カンボジア", "カンボジア", True),
    ("region_043", "タジキスタン", "タジキスタン", True),
    ("region_044", "朝鮮民主主義人民共和国", "朝鮮民主主義人民共和国", True),
    ("region_045", "ネパール", "ネパール", True),
    ("region_047", "バングラデシュ", "バングラデシュ", True),
    ("region_048", "ベトナム", "ベトナム", True),
    ("region_049", "ベトナム", "ベトナム", False),
    ("region_051", "大韓民国", "大韓民国", True),
    ("region_052", "マレーシア", "マレーシア", True),
    ("region_053", "ジョージア", "ジョージア", True),
    ("region_054", "ヨルダン", "ヨルダン", True),
    ("region_055", "アゼルバイジャン", "アゼルバイジャン", True),
    ("region_058", "日本", "日本", False),              # 北海道
    ("region_059", "インドネシア", "インドネシア", False),
    ("region_062", "フィリピン", "フィリピン", True),
    ("region_064", "インド", "インド", False),
    ("region_065", "アラブ首長国連邦", "アラブ首長国連邦", True),
    ("region_066", "フィリピン", "フィリピン", False),
    ("region_068", "スリランカ", "スリランカ", True),
    ("region_069", "レバノン", "レバノン", True),
    ("region_070", "イスラエル", "イスラエル", True),
    ("region_071", "アルメニア", "アルメニア", True),
    ("region_072", "アゼルバイジャン", "アゼルバイジャン", False),
    ("region_073", "キプロス", "キプロス", True),
    ("region_074", "クウェート", "クウェート", True),
    ("region_075", "カタール", "カタール", True),
    ("region_076", "バーレーン", "バーレーン", True),
    ("region_077", "ウズベキスタン", "ウズベキスタン", False),
    ("region_078", "タジキスタン", "タジキスタン", False),
    ("region_079", "キルギス", "キルギス", False),
    ("region_080", "ブータン", "ブータン", True),
    ("region_081", "ミャンマー", "ミャンマー", False),
    ("region_082", "タイ", "タイ", False),              # タイ飛び地
    ("region_083", "タイ", "タイ", False),              # タイ飛び地
    ("region_084", "シンガポール", "シンガポール", True),
    ("region_085", "ブルネイ", "ブルネイ", True),
    ("region_086", "台湾", "台湾", True),
    ("region_087", "日本", "日本", False),              # 九州
    ("region_088", "日本", "日本", False),              # 四国
    ("region_089", "フィリピン", "フィリピン", False),
    ("region_090", "フィリピン", "フィリピン", False),
    ("region_091", "フィリピン", "フィリピン", False),
    ("region_092", "マレーシア", "マレーシア", False),
    ("region_093", "フィリピン", "フィリピン", False),
    ("region_094", "フィリピン", "フィリピン", False),
    ("region_095", "フィリピン", "フィリピン", False),
    ("region_096", "フィリピン", "フィリピン", False),
    ("region_097", "フィリピン", "フィリピン", False),
    ("region_098", "フィリピン", "フィリピン", False),
    ("region_099", "フィリピン", "フィリピン", False),
    ("region_102", "インドネシア", "インドネシア", False),
    ("region_103", "インドネシア", "インドネシア", False),
    ("region_104", "インドネシア", "インドネシア", False),
    ("region_105", "東ティモール", "東ティモール", True),
    ("region_106", "インドネシア", "インドネシア", False),
    ("region_108", "インドネシア", "インドネシア", False),
    ("region_109", "インドネシア", "インドネシア", False),
    ("region_110", "インドネシア", "インドネシア", False),
    ("region_112", "インドネシア", "インドネシア", False),
    ("region_113", "インドネシア", "インドネシア", False),
    ("region_114", "インドネシア", "インドネシア", False),
    ("region_115", "インドネシア", "インドネシア", False),
    ("region_116", "インドネシア", "インドネシア", False),
    ("region_117", "インドネシア", "インドネシア", False),
    ("region_118", "インドネシア", "インドネシア", False),
    ("region_119", "インドネシア", "インドネシア", False),
    ("region_120", "インドネシア", "インドネシア", False),
    ("region_121", "インドネシア", "インドネシア", False),
    ("region_122", "インドネシア", "インドネシア", False),
    ("region_123", "インドネシア", "インドネシア", False),
    ("region_124", "インドネシア", "インドネシア", False),
    ("region_125", "インドネシア", "インドネシア", False),
    ("region_126", "モルディブ", "モルディブ", False),
    ("region_127", "モルディブ", "モルディブ", False),
    ("region_128", "モルディブ", "モルディブ", False),
    ("region_129", "モルディブ", "モルディブ", False),
    ("region_130", "モルディブ", "モルディブ", False),
    ("region_131", "モルディブ", "モルディブ", False),
    ("region_132", "モルディブ", "モルディブ", True),
    ("region_133", "中華人民共和国", "中華人民共和国", False),  # 海南島
    ("region_134", "インドネシア", "インドネシア", False),
    ("region_135", "インドネシア", "インドネシア", False),
    ("region_136", "パレスチナ", "パレスチナ", True),       # ヨルダン川西岸
    ("region_137", "パレスチナ", "パレスチナ", False),      # ガザ
]

# 除外するregion_id（地図外・凡例・隣接地域など）
EXCLUDE_IDS = set()

# グループ定義: 同じグループの出題対象領域はどれをタップしても正答になる
# {groupId: [region_id, ...]}
GROUPS = {
    "israel_palestine": ["region_070", "region_136"],  # イスラエル & パレスチナ
}


def main():
    json_path = "map-data/ASIA_raw.json"
    output_path = "WhiteMapQuiz/WhiteMapQuiz/Resources/MapData/ASIA.json"

    with open(json_path, "r") as f:
        data = json.load(f)

    # ラベルをdictに変換（最初のエントリが優先）
    label_map = {}
    for region_id, name, display_name, is_main in LABELS:
        if region_id not in label_map:
            label_map[region_id] = (name, display_name, is_main)

    # region_id → groupId のマッピングを構築
    group_map = {}
    for group_id, region_ids in GROUPS.items():
        for rid in region_ids:
            group_map[rid] = group_id

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
            if rid in group_map:
                region["groupId"] = group_map[rid]
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
    data["displayName"] = "アジア"

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
