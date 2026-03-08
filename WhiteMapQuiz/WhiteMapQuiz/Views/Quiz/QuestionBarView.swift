import SwiftUI

struct QuestionBarView: View {
    let viewModel: QuizViewModel

    var body: some View {
        HStack(spacing: 16) {
            // タイマー
            Label(viewModel.formattedTime(), systemImage: "timer")
                .monospacedDigit()

            Divider()
                .frame(height: 20)

            // 進捗
            Text("Q.\(viewModel.currentQuestionIndex + 1)/\(viewModel.totalQuestions)")

            Divider()
                .frame(height: 20)

            // スコア
            Label("\(viewModel.score)pt", systemImage: "star.fill")
                .foregroundStyle(.orange)

            Spacer()
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(.ultraThinMaterial)
    }
}
