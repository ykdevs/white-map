import SwiftUI
import SwiftData

struct ResultView: View {
    let quizViewModel: QuizViewModel
    let onRetry: () -> Void
    let onBackToMapList: () -> Void
    @State private var resultViewModel: ResultViewModel
    @Environment(\.modelContext) private var modelContext

    init(quizViewModel: QuizViewModel, onRetry: @escaping () -> Void, onBackToMapList: @escaping () -> Void) {
        self.quizViewModel = quizViewModel
        self.onRetry = onRetry
        self.onBackToMapList = onBackToMapList
        self._resultViewModel = State(initialValue: ResultViewModel(quizViewModel: quizViewModel))
    }

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // スコアサマリ
                VStack(spacing: 12) {
                    Text("クイズ結果")
                        .font(.title)
                        .fontWeight(.bold)

                    HStack(spacing: 32) {
                        VStack {
                            Label(quizViewModel.formattedTime(), systemImage: "timer")
                                .font(.title2)
                            Text("経過時間")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }

                        VStack {
                            Text("\(quizViewModel.score) / \(quizViewModel.maxScore)")
                                .font(.title2)
                                .fontWeight(.semibold)
                            Text("点数")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }

                        VStack {
                            Text(String(format: "%.1f%%", quizViewModel.accuracy * 100))
                                .font(.title2)
                                .fontWeight(.semibold)
                            Text("正答率")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
                .padding()

                // 凡例
                HStack(spacing: 16) {
                    ScoreIndicatorView(state: .correct(attempt: 1))
                    ScoreIndicatorView(state: .correct(attempt: 2))
                    ScoreIndicatorView(state: .correct(attempt: 3))
                    ScoreIndicatorView(state: .failed)
                }

                // 色分け済み完成地図
                CompletedMapView(viewModel: quizViewModel)
                    .frame(height: 300)
                    .padding(.horizontal)

                // 過去の記録
                RecordHistoryView(records: resultViewModel.pastRecords)
                    .padding(.horizontal)

                // ボタン
                HStack(spacing: 20) {
                    Button("もう一度") {
                        onRetry()
                    }
                    .buttonStyle(.bordered)

                    Button("地図選択に戻る") {
                        onBackToMapList()
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding(.bottom)
            }
        }
        .navigationBarBackButtonHidden(true)
        .onAppear {
            resultViewModel.saveAndLoad(modelContext: modelContext)
        }
    }
}

struct CompletedMapView: View {
    let viewModel: QuizViewModel

    var body: some View {
        GeometryReader { geometry in
            let viewBox = viewModel.mapDefinition.viewBox
            let fitScale = min(
                geometry.size.width / viewBox.width,
                geometry.size.height / viewBox.height
            )
            let offsetX = (geometry.size.width - viewBox.width * fitScale) / 2
            let offsetY = (geometry.size.height - viewBox.height * fitScale) / 2

            ZStack {
                ForEach(viewModel.mapDefinition.regions) { region in
                    let state = viewModel.regionStates[region.id] ?? .unanswered
                    let cgPath = SVGPathParser.parse(region.svgPath)
                    let transform = CGAffineTransform(translationX: offsetX, y: offsetY)
                        .scaledBy(x: fitScale, y: fitScale)

                    Path(cgPath)
                        .transform(transform)
                        .fill(Color.forRegionState(state))

                    Path(cgPath)
                        .transform(transform)
                        .stroke(Color.black, lineWidth: 0.5)

                    let labelX = region.labelPoint.x * fitScale + offsetX
                    let labelY = region.labelPoint.y * fitScale + offsetY
                    Text(region.name)
                        .font(.system(size: max(6, 8 * fitScale)))
                        .foregroundStyle(.black)
                        .position(x: labelX, y: labelY)
                }
            }
        }
    }
}
