#!/usr/bin/env python3
"""
抽出した領域をデバッグ用に可視化するツール。
各領域をランダムな色で塗り分け、region_idを表示する。

使い方:
    python debug_regions.py <raw_json> <original_png> <output_png>

例:
    python debug_regions.py ../map-data/TOKYO_raw.json ../images/TOKYO0.png ../map-data/TOKYO_debug.png
    python debug_regions.py ../map-data/KANAGAWA_raw.json ../images/KANAGAWA0.png ../map-data/KANAGAWA_debug.png
"""

import sys
import json
import re
import cv2
import numpy as np


def parse_svg_path_to_points(svg_path: str, scale_x: float, scale_y: float):
    """SVGパス文字列を画像座標の点列に変換する"""
    tokens = re.findall(r"[MLZ]|[-+]?[0-9]*\.?[0-9]+", svg_path)
    points = []
    i = 0
    while i < len(tokens):
        if tokens[i] in ("M", "L"):
            i += 1
            x = float(tokens[i]) / scale_x
            y = float(tokens[i + 1]) / scale_y
            points.append([int(round(x)), int(round(y))])
            i += 2
        elif tokens[i] == "Z":
            i += 1
        else:
            i += 1
    return np.array(points, dtype=np.int32) if points else None


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    json_path = sys.argv[1]
    original_path = sys.argv[2]
    output_path = sys.argv[3]

    # JSONデータ読み込み
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 元画像読み込み
    img = cv2.imread(original_path)
    if img is None:
        raise FileNotFoundError(f"画像を読み込めません: {original_path}")

    h, w = img.shape[:2]
    vb_w = data["viewBox"]["width"]
    vb_h = data["viewBox"]["height"]
    scale_x = vb_w / w
    scale_y = vb_h / h

    # カラフルな配色を生成（HSV色空間で均等に分布）
    n_regions = len(data["regions"])
    colors = []
    for i in range(n_regions):
        hue = int(180 * i / n_regions)
        color_hsv = np.array([[[hue, 180, 220]]], dtype=np.uint8)
        color_bgr = cv2.cvtColor(color_hsv, cv2.COLOR_HSV2BGR)[0][0]
        colors.append(tuple(int(c) for c in color_bgr))

    # 半透明のオーバーレイを作成
    overlay = img.copy()

    for i, region in enumerate(data["regions"]):
        pts = parse_svg_path_to_points(region["svgPath"], scale_x, scale_y)
        if pts is None or len(pts) < 3:
            continue
        cv2.fillPoly(overlay, [pts], colors[i])

    # 元画像とオーバーレイをブレンド
    result = cv2.addWeighted(img, 0.3, overlay, 0.7, 0)

    # フォントサイズを画像サイズに応じて調整
    font_scale = max(0.4, min(1.2, w / 2000))
    font_thickness = max(1, int(font_scale * 2))

    # 各領域にIDを描画
    for region in data["regions"]:
        lp = region["labelPoint"]
        cx = int(lp["x"] / scale_x)
        cy = int(lp["y"] / scale_y)

        label = region["id"].replace("region_", "")

        # 背景付きテキスト（読みやすくするため）
        (tw, th), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness
        )
        cv2.rectangle(
            result,
            (cx - tw // 2 - 3, cy - th - 3),
            (cx + tw // 2 + 3, cy + 5),
            (255, 255, 255),
            -1,
        )
        cv2.putText(
            result, label, (cx - tw // 2, cy),
            cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness,
        )

    cv2.imwrite(output_path, result)
    print(f"デバッグ画像生成完了: {output_path}")
    print(f"  領域数: {n_regions}")


if __name__ == "__main__":
    main()
