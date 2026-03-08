import SwiftUI

struct ScoreIndicatorView: View {
    let state: RegionState

    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(Color.forRegionState(state))
                .frame(width: 16, height: 16)

            Text(label)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }

    private var label: String {
        switch state {
        case .unanswered:
            return "未回答"
        case .correct(let attempt):
            return "\(attempt)回目正答 (+\(state.score))"
        case .failed:
            return "不正解"
        }
    }
}
