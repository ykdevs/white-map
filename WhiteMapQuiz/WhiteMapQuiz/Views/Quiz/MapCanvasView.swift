import SwiftUI

struct MapCanvasView: View {
    let viewModel: QuizViewModel

    @State private var scale: CGFloat = 1.0
    @State private var lastScale: CGFloat = 1.0
    @State private var offset: CGSize = .zero
    @State private var lastOffset: CGSize = .zero

    var body: some View {
        GeometryReader { geometry in
            let viewBox = viewModel.mapDefinition.viewBox
            let fitScale = min(
                geometry.size.width / viewBox.width,
                geometry.size.height / viewBox.height
            )
            let mapWidth = viewBox.width * fitScale
            let mapHeight = viewBox.height * fitScale
            let baseOffsetX = (geometry.size.width - mapWidth) / 2
            let baseOffsetY = (geometry.size.height - mapHeight) / 2

            ZStack {
                // 地図領域の描画
                ForEach(viewModel.mapDefinition.regions) { region in
                    // 飛び地は本体の状態に連動
                    let effectiveId = region.parentId ?? region.id
                    let state = viewModel.regionStates[effectiveId] ?? .unanswered
                    let cgPath = SVGPathParser.parse(region.svgPath)

                    Path(cgPath)
                        .transform(
                            CGAffineTransform.identity
                                .translatedBy(x: baseOffsetX + offset.width, y: baseOffsetY + offset.height)
                                .scaledBy(x: fitScale * scale, y: fitScale * scale)
                        )
                        .fill(Color.forRegionState(state))

                    Path(cgPath)
                        .transform(
                            CGAffineTransform.identity
                                .translatedBy(x: baseOffsetX + offset.width, y: baseOffsetY + offset.height)
                                .scaledBy(x: fitScale * scale, y: fitScale * scale)
                        )
                        .stroke(Color.black, lineWidth: 0.5)

                    // 正答済みの領域にラベルを表示
                    if state != .unanswered {
                        let labelX = region.labelPoint.x * fitScale * scale + baseOffsetX + offset.width
                        let labelY = region.labelPoint.y * fitScale * scale + baseOffsetY + offset.height
                        Text(region.name)
                            .font(.system(size: max(8, 10 * scale)))
                            .foregroundStyle(.black)
                            .position(x: labelX, y: labelY)
                    }
                }
            }
            .contentShape(Rectangle())
            .onTapGesture { location in
                // ズーム・オフセットを考慮してviewBox座標に変換
                let adjustedPoint = CGPoint(
                    x: (location.x - baseOffsetX - offset.width) / scale,
                    y: (location.y - baseOffsetY - offset.height) / scale
                )
                let viewSize = CGSize(
                    width: geometry.size.width,
                    height: geometry.size.height
                )
                // hitTestはviewBox座標への変換も行うので、fitScale適用済みの座標を渡す
                let pointInView = CGPoint(
                    x: adjustedPoint.x + baseOffsetX,
                    y: adjustedPoint.y + baseOffsetY
                )
                viewModel.handleTap(at: pointInView, in: viewSize)
            }
            .gesture(
                MagnifyGesture()
                    .onChanged { value in
                        scale = lastScale * value.magnification
                        scale = min(max(scale, 0.5), 5.0)
                    }
                    .onEnded { _ in
                        lastScale = scale
                    }
            )
            .simultaneousGesture(
                DragGesture()
                    .onChanged { value in
                        offset = CGSize(
                            width: lastOffset.width + value.translation.width,
                            height: lastOffset.height + value.translation.height
                        )
                    }
                    .onEnded { _ in
                        lastOffset = offset
                    }
            )
        }
        .background(Color(white: 0.95))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
}
