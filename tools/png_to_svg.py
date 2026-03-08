#!/usr/bin/env python3
"""
PNG白地図から輪郭を抽出し、SVGファイルを生成するツール。

使い方:
    python png_to_svg.py <input_png> <output_svg>

例:
    python png_to_svg.py ../images/KANAGAWA0.png ../map-data/KANAGAWA_raw.svg
"""

import sys
import cv2
import numpy as np
import svgwrite


def extract_contours(image_path: str, min_area: float = 500.0):
    """PNG画像から閉領域の輪郭を抽出する"""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"画像を読み込めません: {image_path}")

    # 二値化（白地図の境界線は黒い線）
    _, binary = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)

    # ノイズ除去
    kernel = np.ones((2, 2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # 輪郭抽出
    contours, hierarchy = cv2.findContours(
        binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
    )

    # 面積でフィルタリング（小さすぎるノイズを除去）
    filtered = []
    if hierarchy is not None:
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area >= min_area:
                # 輪郭を簡略化
                epsilon = 0.001 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                if len(approx) >= 3:
                    filtered.append({
                        "contour": approx,
                        "area": area,
                        "hierarchy": hierarchy[0][i],
                    })

    return filtered, img.shape


def contour_to_svg_path(contour) -> str:
    """OpenCVの輪郭をSVGパス文字列に変換する"""
    points = contour.reshape(-1, 2)
    if len(points) < 3:
        return ""

    parts = [f"M {points[0][0]} {points[0][1]}"]
    for point in points[1:]:
        parts.append(f"L {point[0]} {point[1]}")
    parts.append("Z")
    return " ".join(parts)


def create_svg(contours, image_shape, output_path: str):
    """輪郭からSVGファイルを生成する"""
    height, width = image_shape[:2]

    dwg = svgwrite.Drawing(output_path, size=(width, height))
    dwg.viewbox(0, 0, width, height)

    # 面積の大きい順にソート（背景が先、小さい領域が後）
    sorted_contours = sorted(contours, key=lambda c: c["area"], reverse=True)

    for i, item in enumerate(sorted_contours):
        path_d = contour_to_svg_path(item["contour"])
        if path_d:
            dwg.add(dwg.path(
                d=path_d,
                id=f"region_{i:03d}",
                fill="white",
                stroke="black",
                stroke_width=0.5,
            ))

    dwg.save()
    print(f"SVG生成完了: {output_path}")
    print(f"  画像サイズ: {width} x {height}")
    print(f"  検出領域数: {len(contours)}")


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    contours, shape = extract_contours(input_path)
    create_svg(contours, shape, output_path)


if __name__ == "__main__":
    main()
