import Foundation

enum RegionState: Equatable {
    case unanswered
    case correct(attempt: Int)  // 1, 2, 3
    case failed                 // 3回不正解

    var score: Int {
        switch self {
        case .correct(let attempt):
            switch attempt {
            case 1: return 4
            case 2: return 2
            case 3: return 1
            default: return 0
            }
        case .unanswered, .failed:
            return 0
        }
    }
}
