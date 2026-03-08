#!/usr/bin/env python3
"""神奈川県の地図JSONに正確なラベルを付与する"""

import json

# デバッグ画像とKANAGAWA1.pngの照合に基づく正確なマッピング
# (region_id, name, displayName, is_main)
# is_main=True: クイズの出題対象, False: 飛び地・島嶼部（本体と連動）
LABELS = [
    # 相模原市
    ("region_000", "緑区", "相模原市緑区", True),
    ("region_002", "中央区", "相模原市中央区", True),
    ("region_018", "南区", "相模原市南区", True),

    # 川崎市
    ("region_037", "麻生区", "川崎市麻生区", True),
    ("region_040", "多摩区", "川崎市多摩区", True),
    ("region_041", "高津区", "川崎市高津区", True),
    ("region_050", "宮前区", "川崎市宮前区", True),
    ("region_051", "中原区", "川崎市中原区", True),
    ("region_057", "幸区", "川崎市幸区", True),
    ("region_060", "川崎区", "川崎市川崎区", True),

    # 横浜市
    ("region_022", "瀬谷区", "横浜市瀬谷区", True),
    ("region_010", "緑区", "横浜市緑区", True),
    ("region_006", "旭区", "横浜市旭区", True),
    ("region_017", "都筑区", "横浜市都筑区", True),
    ("region_020", "青葉区", "横浜市青葉区", True),
    ("region_031", "港北区", "横浜市港北区", True),
    ("region_024", "鶴見区", "横浜市鶴見区", True),
    ("region_034", "神奈川区", "横浜市神奈川区", True),
    ("region_027", "保土ケ谷区", "横浜市保土ケ谷区", True),
    ("region_046", "泉区", "横浜市泉区", True),
    ("region_028", "南区", "横浜市南区", True),
    ("region_023", "西区", "横浜市西区", True),
    ("region_036", "中区", "横浜市中区", True),
    ("region_030", "港南区", "横浜市港南区", True),
    ("region_035", "戸塚区", "横浜市戸塚区", True),
    ("region_045", "栄区", "横浜市栄区", True),
    ("region_033", "磯子区", "横浜市磯子区", True),
    ("region_054", "金沢区", "横浜市金沢区", True),

    # 横須賀・三浦
    ("region_008", "横須賀市", "横須賀市", True),
    ("region_026", "三浦市", "三浦市", True),

    # 鎌倉・逗子・葉山
    ("region_025", "鎌倉市", "鎌倉市", True),
    ("region_043", "逗子市", "逗子市", True),
    ("region_048", "葉山町", "葉山町", True),

    # 湘南
    ("region_011", "藤沢市", "藤沢市", True),
    ("region_021", "寒川町", "寒川町", True),
    ("region_015", "茅ヶ崎市", "茅ヶ崎市", True),
    ("region_042", "大磯町", "大磯町", True),
    ("region_044", "平塚市", "平塚市", True),

    # 県央
    ("region_005", "海老名市", "海老名市", True),
    ("region_013", "座間市", "座間市", True),
    ("region_012", "大和市", "大和市", True),
    ("region_053", "綾瀬市", "綾瀬市", True),

    # 西部
    ("region_003", "厚木市", "厚木市", True),
    ("region_016", "愛川町", "愛川町", True),
    ("region_009", "伊勢原市", "伊勢原市", True),
    ("region_056", "秦野市", "秦野市", True),
    ("region_019", "清川村", "清川村", True),

    # 足柄
    ("region_038", "中井町", "中井町", True),
    ("region_052", "大井町", "大井町", True),
    ("region_061", "松田町", "松田町", True),
    ("region_004", "山北町", "山北町", True),
    ("region_049", "二宮町", "二宮町", True),
    ("region_039", "南足柄市", "南足柄市", True),
    ("region_001", "小田原市", "小田原市", True),
    ("region_007", "箱根町", "箱根町", True),
    ("region_062", "湯河原町", "湯河原町", True),
    ("region_014", "真鶴町", "真鶴町", True),
    ("region_052", "開成町", "開成町", True),

    # 残りの領域（横浜右側エリアなど）
    ("region_059", "南区", "横浜市南区", False),      # 南区飛び地
    ("region_019", "保土ケ谷区", "横浜市保土ケ谷区", False),  # 飛び地

    # 島嶼部・臨海部飛び地
    ("region_055", "三浦市", "三浦市", False),         # 城ヶ島
    ("region_058", "横須賀市", "横須賀市", False),     # 猿島
    ("region_065", "川崎区", "川崎市川崎区", False),   # 扇島
    ("region_063", "鶴見区", "横浜市鶴見区", False),   # 大黒ふ頭
    ("region_064", "鶴見区", "横浜市鶴見区", False),   # 飛び地
    ("region_066", "鶴見区", "横浜市鶴見区", False),   # 飛び地
    ("region_029", "神奈川区", "横浜市神奈川区", False), # 臨海部
    ("region_032", "鶴見区", "横浜市鶴見区", False),   # 臨海部
    ("region_047", "金沢区", "横浜市金沢区", False),   # 臨海部
]

def main():
    json_path = 'WhiteMapQuiz/WhiteMapQuiz/Resources/MapData/KANAGAWA.json'

    with open(json_path, 'r') as f:
        data = json.load(f)

    # ラベルをdictに変換（最初のエントリが優先）
    label_map = {}
    for region_id, name, display_name, is_main in LABELS:
        if region_id not in label_map:
            label_map[region_id] = (name, display_name, is_main)

    # 飛び地→本体のマッピング（displayNameで紐付け）
    main_regions = {}
    for region_id, name, display_name, is_main in LABELS:
        if is_main and display_name not in main_regions:
            main_regions[display_name] = region_id

    # JSONを更新
    for region in data['regions']:
        rid = region['id']
        if rid in label_map:
            name, display_name, is_main = label_map[rid]
            if not is_main:
                # 飛び地: IDを本体のIDの派生にする
                main_id = main_regions.get(display_name, rid)
                region['id'] = f"{main_id}_sub"
                region['parentId'] = main_id
            region['name'] = name
            region['displayName'] = display_name

    # 重複IDを解消（_sub が複数ある場合に連番を付ける）
    id_counts = {}
    for region in data['regions']:
        rid = region['id']
        if rid in id_counts:
            id_counts[rid] += 1
            region['id'] = f"{rid}_{id_counts[rid]}"
        else:
            id_counts[rid] = 0

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 統計
    main_count = sum(1 for r in data['regions'] if 'parentId' not in r)
    sub_count = sum(1 for r in data['regions'] if 'parentId' in r)
    print(f"ラベル付け完了: {json_path}")
    print(f"  出題対象（本体）: {main_count}")
    print(f"  飛び地・島嶼部: {sub_count}")
    print(f"  合計: {len(data['regions'])}")


if __name__ == '__main__':
    main()
