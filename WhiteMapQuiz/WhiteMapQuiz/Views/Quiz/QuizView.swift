import SwiftUI

struct QuizView: View {
    let mapDefinition: MapDefinition
    @Binding var navigationPath: NavigationPath
    @State private var viewModel: QuizViewModel
    @State private var navigateToResult = false

    init(mapDefinition: MapDefinition, navigationPath: Binding<NavigationPath>) {
        self.mapDefinition = mapDefinition
        self._navigationPath = navigationPath
        self._viewModel = State(initialValue: QuizViewModel(mapDefinition: mapDefinition))
    }

    var body: some View {
        VStack(spacing: 0) {
            // ヘッダー: タイマー・進捗・スコア
            QuestionBarView(viewModel: viewModel)

            // 地図キャンバス
            MapCanvasView(viewModel: viewModel)
                .frame(maxWidth: .infinity, maxHeight: .infinity)

            // 出題エリア
            if let question = viewModel.currentQuestion {
                VStack(spacing: 8) {
                    Text("「\(question.displayName)」をタップしてください")
                        .font(.title3)
                        .fontWeight(.medium)

                    // 試行回数インジケータ
                    HStack(spacing: 6) {
                        ForEach(0..<3, id: \.self) { index in
                            Circle()
                                .fill(index < viewModel.attempts ? Color.red : Color.gray.opacity(0.3))
                                .frame(width: 12, height: 12)
                        }
                    }
                }
                .padding()
                .frame(maxWidth: .infinity)
                .background(.ultraThinMaterial)
            }
        }
        .navigationTitle(mapDefinition.displayName)
        #if os(iOS)
        .navigationBarTitleDisplayMode(.inline)
        #endif
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button("中断") {
                    viewModel.stop()
                    navigationPath.removeLast()
                }
            }
        }
        .navigationDestination(isPresented: $navigateToResult) {
            ResultView(
                quizViewModel: viewModel,
                onRetry: {
                    // 結果画面を閉じてQuizViewに戻り、新しいViewModelでリスタート
                    navigateToResult = false
                    viewModel = QuizViewModel(mapDefinition: mapDefinition)
                    viewModel.start()
                },
                onBackToMapList: {
                    // ルートまで戻る
                    navigationPath = NavigationPath()
                }
            )
        }
        .onChange(of: viewModel.isFinished) { _, finished in
            if finished {
                navigateToResult = true
            }
        }
        .onAppear {
            viewModel.start()
        }
    }
}
