import CoreGraphics

struct PathHitTester {
    struct RegionPath {
        let region: RegionDefinition
        let cgPath: CGPath
        let area: CGFloat
    }

    /// 面積の小さい順にソートされた領域パスの配列
    private let regionPaths: [RegionPath]

    init(regions: [RegionDefinition]) {
        self.regionPaths = regions.map { region in
            let cgPath = SVGPathParser.parse(region.svgPath)
            let bounds = cgPath.boundingBox
            let area = bounds.width * bounds.height
            return RegionPath(region: region, cgPath: cgPath, area: area)
        }
        .sorted { $0.area < $1.area } // 面積の小さい順
    }

    /// ビュー座標からviewBox座標に変換し、該当する領域を返す
    func hitTest(point: CGPoint, in viewSize: CGSize, viewBox: ViewBox) -> RegionDefinition? {
        let mapPoint = convertToViewBoxCoordinates(
            point: point,
            viewSize: viewSize,
            viewBox: viewBox
        )

        for regionPath in regionPaths {
            if regionPath.cgPath.contains(mapPoint) {
                return regionPath.region
            }
        }
        return nil
    }

    /// ビュー座標をviewBox座標に変換
    private func convertToViewBoxCoordinates(
        point: CGPoint,
        viewSize: CGSize,
        viewBox: ViewBox
    ) -> CGPoint {
        let scale = min(
            viewSize.width / viewBox.width,
            viewSize.height / viewBox.height
        )
        let offsetX = (viewSize.width - viewBox.width * scale) / 2
        let offsetY = (viewSize.height - viewBox.height * scale) / 2

        return CGPoint(
            x: (point.x - offsetX) / scale,
            y: (point.y - offsetY) / scale
        )
    }
}
