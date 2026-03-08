import SwiftUI

struct MapCardView: View {
    let map: MapDefinition
    let bestScore: Int?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 地図サムネイル（SVGパスを縮小描画）
            MapThumbnailView(map: map)
                .frame(height: 160)
                .clipShape(RoundedRectangle(cornerRadius: 8))

            VStack(alignment: .leading, spacing: 4) {
                Text(map.displayName)
                    .font(.headline)
                    .foregroundStyle(.primary)

                Text("\(map.regions.count) 地域")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)

                if let bestScore {
                    Text("最高: \(bestScore)点")
                        .font(.subheadline)
                        .foregroundStyle(.blue)
                } else {
                    Text("未挑戦")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .padding()
        .background(.background)
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .shadow(color: .black.opacity(0.1), radius: 4, y: 2)
    }
}

struct MapThumbnailView: View {
    let map: MapDefinition

    var body: some View {
        GeometryReader { geometry in
            let scale = min(
                geometry.size.width / map.viewBox.width,
                geometry.size.height / map.viewBox.height
            )
            let offsetX = (geometry.size.width - map.viewBox.width * scale) / 2
            let offsetY = (geometry.size.height - map.viewBox.height * scale) / 2

            ZStack {
                ForEach(map.regions) { region in
                    Path(SVGPathParser.parse(region.svgPath))
                        .transform(
                            CGAffineTransform(translationX: offsetX, y: offsetY)
                                .scaledBy(x: scale, y: scale)
                        )
                        .fill(Color.white)
                        .overlay(
                            Path(SVGPathParser.parse(region.svgPath))
                                .transform(
                                    CGAffineTransform(translationX: offsetX, y: offsetY)
                                        .scaledBy(x: scale, y: scale)
                                )
                                .stroke(Color.gray, lineWidth: 0.5)
                        )
                }
            }
        }
    }
}
