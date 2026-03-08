import SwiftUI

extension Color {
    /// 1回目正答: 青色
    static let quizCorrect1st = Color.blue
    /// 2回目正答: 水色
    static let quizCorrect2nd = Color.cyan
    /// 3回目正答: 薄黄色
    static let quizCorrect3rd = Color.yellow.opacity(0.5)
    /// 3回不正解: 灰色
    static let quizFailed = Color.gray.opacity(0.5)
    /// 未回答: 白
    static let quizUnanswered = Color.white

    static func forRegionState(_ state: RegionState) -> Color {
        switch state {
        case .unanswered:
            return .quizUnanswered
        case .correct(let attempt):
            switch attempt {
            case 1: return .quizCorrect1st
            case 2: return .quizCorrect2nd
            case 3: return .quizCorrect3rd
            default: return .quizUnanswered
            }
        case .failed:
            return .quizFailed
        }
    }
}
