#!/usr/bin/env python3
"""
白地図PNGから市区町村の領域を抽出し、アプリ用JSONを生成するツール。

使い方:
    python extract_regions.py <blank_map_png> <map_id> <display_name> <output_json>

例:
    python extract_regions.py ../images/KANAGAWA0.png KANAGAWA 神奈川県 ../WhiteMapQuiz/WhiteMapQuiz/Resources/MapData/KANAGAWA.json

生成されるJSONは座標を画像のアスペクト比に合わせた座標系(viewBox)で出力する。
領域のラベル付けは別途 label_regions.py で行う。
"""

import sys
import json
import cv2
import numpy as np


def extract_regions(image_path: str, min_area: int = 5000, max_area: int = 3000000):
    """白地図PNGから閉領域を検出する"""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"画像を読み込めません: {image_path}")

    h, w = img.shape

    # 1. 境界線検出
    _, lines = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY_INV)

    # 2. 境界線を太くして隙間を埋める
    kernel = np.ones((5, 5), np.uint8)
    thick_lines = cv2.dilate(lines, kernel, iterations=2)

    # 3. クロージングで小さい隙間を完全に埋める
    kernel_close = np.ones((7, 7), np.uint8)
    thick_lines = cv2.morphologyEx(thick_lines, cv2.MORPH_CLOSE, kernel_close, iterations=1)

    # 4. 反転
    white_regions = cv2.bitwise_not(thick_lines)

    # 5. 連結成分ラベリング
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        white_regions, connectivity=4
    )

    # 6. 各領域の輪郭を取得
    regions = []
    for i in range(1, num_labels):  # 0は背景
        area = stats[i, cv2.CC_STAT_AREA]
        if min_area < area < max_area:
            # このラベルのマスクを作成
            mask = (labels == i).astype(np.uint8) * 255

            # 輪郭を取得
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                continue

            # 最大の輪郭を使用
            contour = max(contours, key=cv2.contourArea)

            # 輪郭を簡略化
            epsilon = 0.0008 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            if len(approx) < 3:
                continue

            cx, cy = centroids[i]
            regions.append({
                "contour": approx,
                "area": area,
                "cx": int(cx),
                "cy": int(cy),
                "stat_x": int(stats[i, cv2.CC_STAT_LEFT]),
                "stat_y": int(stats[i, cv2.CC_STAT_TOP]),
                "stat_w": int(stats[i, cv2.CC_STAT_WIDTH]),
                "stat_h": int(stats[i, cv2.CC_STAT_HEIGHT]),
            })

    return regions, (w, h)


def contour_to_svg_path(contour, scale_x: float, scale_y: float) -> str:
    """輪郭をスケーリングしてSVGパス文字列に変換"""
    points = contour.reshape(-1, 2)
    if len(points) < 3:
        return ""

    parts = [f"M {points[0][0] * scale_x:.1f} {points[0][1] * scale_y:.1f}"]
    for point in points[1:]:
        parts.append(f"L {point[0] * scale_x:.1f} {point[1] * scale_y:.1f}")
    parts.append("Z")
    return " ".join(parts)


def filter_legend_and_outer(regions, img_w, img_h):
    """凡例の四角形や地図外の領域を除外する"""
    filtered = []
    for r in regions:
        # 凡例は左上にある四角形（アスペクト比が正方形に近い矩形）
        # かつ左上1/4に位置する
        x, y = r["stat_x"], r["stat_y"]
        w, h = r["stat_w"], r["stat_h"]
        cx, cy = r["cx"], r["cy"]

        # 全体を囲む領域を除外（画像全体に近い大きさ）
        if w > img_w * 0.8 and h > img_h * 0.8:
            print(f"  除外(全体枠): area={r['area']} center=({cx},{cy})")
            continue

        # 凡例領域を除外（左上かつ長方形に近い）
        if cx < img_w * 0.25 and cy < img_h * 0.25:
            aspect = min(w, h) / max(w, h) if max(w, h) > 0 else 0
            if aspect > 0.3:  # 比較的正方形に近い
                print(f"  除外(凡例): area={r['area']} center=({cx},{cy}) aspect={aspect:.2f}")
                continue

        filtered.append(r)

    return filtered


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)

    image_path = sys.argv[1]
    map_id = sys.argv[2]
    display_name = sys.argv[3]
    output_path = sys.argv[4]

    print(f"画像読み込み: {image_path}")
    regions, (img_w, img_h) = extract_regions(image_path)
    print(f"検出された領域数: {len(regions)}")

    # 凡例と外枠を除外
    regions = filter_legend_and_outer(regions, img_w, img_h)
    print(f"フィルタ後の領域数: {len(regions)}")

    # viewBox: 画像座標を800x600の座標系にスケーリング
    vb_width = 800
    vb_height = round(800 * img_h / img_w)
    scale_x = vb_width / img_w
    scale_y = vb_height / img_h

    # 面積の大きい順にソートしてインデックスを付ける
    regions.sort(key=lambda r: -r["area"])

    json_regions = []
    for i, r in enumerate(regions):
        svg_path = contour_to_svg_path(r["contour"], scale_x, scale_y)
        if not svg_path:
            continue

        region_id = f"region_{i:03d}"
        json_regions.append({
            "id": region_id,
            "name": f"地域{i:02d}",
            "displayName": f"地域{i:02d}",
            "svgPath": svg_path,
            "labelPoint": {
                "x": round(r["cx"] * scale_x, 1),
                "y": round(r["cy"] * scale_y, 1),
            },
        })

    data = {
        "id": map_id,
        "displayName": display_name,
        "viewBox": {"width": vb_width, "height": vb_height},
        "regions": json_regions,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nJSON生成完了: {output_path}")
    print(f"  viewBox: {vb_width}x{vb_height}")
    print(f"  地域数: {len(json_regions)}")
    print(f"\n次のステップ:")
    print(f"  python label_regions.py {output_path}")
    print(f"  でラベル付けを行ってください")


if __name__ == "__main__":
    main()
