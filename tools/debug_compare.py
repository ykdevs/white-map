#!/usr/bin/env python3
"""
デバッグ画像とラベル付き地図を横に並べた比較画像を生成するツール。
領域のIDとラベル付き地図の市区町村名を照合するために使用する。

使い方:
    python debug_compare.py <debug_png> <labeled_png> <output_png>

例:
    python debug_compare.py ../map-data/TOKYO_debug.png ../images/TOKYO1.png ../map-data/TOKYO_compare.png
"""

import sys
import cv2
import numpy as np


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    debug_path = sys.argv[1]
    labeled_path = sys.argv[2]
    output_path = sys.argv[3]

    debug_img = cv2.imread(debug_path)
    labeled_img = cv2.imread(labeled_path)

    if debug_img is None:
        raise FileNotFoundError(f"画像を読み込めません: {debug_path}")
    if labeled_img is None:
        raise FileNotFoundError(f"画像を読み込めません: {labeled_path}")

    # 高さを揃える
    h1, w1 = debug_img.shape[:2]
    h2, w2 = labeled_img.shape[:2]
    target_h = max(h1, h2)

    if h1 != target_h:
        scale = target_h / h1
        debug_img = cv2.resize(debug_img, (int(w1 * scale), target_h))
    if h2 != target_h:
        scale = target_h / h2
        labeled_img = cv2.resize(labeled_img, (int(w2 * scale), target_h))

    # 横に並べる
    combined = np.hstack([debug_img, labeled_img])

    # ヘッダーテキスト
    cv2.putText(combined, "Debug (region IDs)", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
    cv2.putText(combined, "Labeled Map", (debug_img.shape[1] + 10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

    cv2.imwrite(output_path, combined)
    print(f"比較画像生成完了: {output_path}")


if __name__ == "__main__":
    main()
