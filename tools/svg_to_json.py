#!/usr/bin/env python3
"""
SVGファイルとラベルCSVから、アプリバンドル用のJSONデータを生成するツール。

使い方:
    python svg_to_json.py <input_svg> <labels_csv> <output_json>

例:
    python svg_to_json.py ../map-data/KANAGAWA.svg ../map-data/KANAGAWA_labels.csv ../WhiteMapQuiz/WhiteMapQuiz/Resources/MapData/KANAGAWA.json

CSVフォーマット:
    region_id,name,displayName
    region_000,西区,横浜市西区
    region_001,幸区,川崎市幸区
    ...
"""

import sys
import json
import csv
import re
from xml.etree import ElementTree


def parse_svg(svg_path: str):
    """SVGファイルからpath要素を抽出する"""
    tree = ElementTree.parse(svg_path)
    root = tree.getroot()

    # SVG名前空間
    ns = {"svg": "http://www.w3.org/2000/svg"}

    # viewBox取得
    viewbox_str = root.get("viewBox", "0 0 1000 800")
    viewbox_parts = viewbox_str.split()
    viewbox = {
        "width": float(viewbox_parts[2]),
        "height": float(viewbox_parts[3]),
    }

    # path要素を抽出
    paths = {}
    for path_elem in root.findall(".//svg:path", ns):
        path_id = path_elem.get("id", "")
        path_d = path_elem.get("d", "")
        if path_id and path_d:
            paths[path_id] = path_d

    # 名前空間なしでも試行
    if not paths:
        for path_elem in root.findall(".//path"):
            path_id = path_elem.get("id", "")
            path_d = path_elem.get("d", "")
            if path_id and path_d:
                paths[path_id] = path_d

    return viewbox, paths


def calculate_label_point(svg_path_d: str):
    """SVGパスのバウンディングボックスの中心座標を計算する"""
    numbers = re.findall(r"[-+]?[0-9]*\.?[0-9]+", svg_path_d)
    if len(numbers) < 2:
        return {"x": 0, "y": 0}

    xs = [float(numbers[i]) for i in range(0, len(numbers), 2)]
    ys = [float(numbers[i]) for i in range(1, len(numbers), 2)]

    return {
        "x": round((min(xs) + max(xs)) / 2, 1),
        "y": round((min(ys) + max(ys)) / 2, 1),
    }


def load_labels(csv_path: str):
    """ラベルCSVを読み込む"""
    labels = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels[row["region_id"]] = {
                "name": row["name"],
                "displayName": row["displayName"],
            }
    return labels


def generate_json(map_id: str, display_name: str, viewbox, paths, labels, output_path: str):
    """アプリバンドル用JSONを生成する"""
    regions = []

    for path_id, path_d in paths.items():
        if path_id not in labels:
            print(f"  警告: ラベルなし - {path_id} (スキップ)")
            continue

        label = labels[path_id]
        label_point = calculate_label_point(path_d)

        regions.append({
            "id": path_id,
            "name": label["name"],
            "displayName": label["displayName"],
            "svgPath": path_d,
            "labelPoint": label_point,
        })

    data = {
        "id": map_id,
        "displayName": display_name,
        "viewBox": viewbox,
        "regions": regions,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"JSON生成完了: {output_path}")
    print(f"  地域数: {len(regions)}")


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    svg_path = sys.argv[1]
    csv_path = sys.argv[2]
    output_path = sys.argv[3]

    # ファイル名からmap_idを推定
    import os
    map_id = os.path.splitext(os.path.basename(svg_path))[0]

    viewbox, paths = parse_svg(svg_path)
    labels = load_labels(csv_path)

    # display_nameはCSVの最初の行のdisplayNameから都道府県名を推定
    # またはコマンドライン引数で指定可能にする
    display_name = map_id  # デフォルト

    generate_json(map_id, display_name, viewbox, paths, labels, output_path)


if __name__ == "__main__":
    main()
