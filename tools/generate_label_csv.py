#!/usr/bin/env python3
"""
抽出済みJSONからラベル付け用のCSVテンプレートを生成するツール。
ラベル付き地図画像（*1.png）がある場合、各領域の中心座標も記録する。

使い方:
    python generate_label_csv.py <raw_json> <output_csv>

例:
    python generate_label_csv.py ../map-data/TOKYO_raw.json ../map-data/TOKYO_labels.csv
"""

import sys
import json
import csv
import re


def estimate_bbox_area(svg_path: str) -> float:
    """SVGパスのバウンディングボックス面積を概算する"""
    nums = re.findall(r"[-+]?[0-9]*\.?[0-9]+", svg_path)
    if len(nums) < 4:
        return 0
    xs = [float(nums[j]) for j in range(0, len(nums), 2)]
    ys = [float(nums[j]) for j in range(1, len(nums), 2)]
    return (max(xs) - min(xs)) * (max(ys) - min(ys))


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    vb_w = data["viewBox"]["width"]
    vb_h = data["viewBox"]["height"]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["region_id", "vb_x", "vb_y", "bbox_area", "name", "displayName"])

        for region in data["regions"]:
            lp = region["labelPoint"]
            bbox_area = estimate_bbox_area(region["svgPath"])
            writer.writerow([
                region["id"],
                f"{lp['x']:.1f}",
                f"{lp['y']:.1f}",
                f"{bbox_area:.0f}",
                "",  # name: ユーザーが記入
                "",  # displayName: ユーザーが記入
            ])

    print(f"ラベルCSV生成完了: {output_path}")
    print(f"  領域数: {len(data['regions'])}")
    print(f"  デバッグ画像と照合して name, displayName を記入してください")


if __name__ == "__main__":
    main()
