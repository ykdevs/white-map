import Foundation
import SwiftData

@Model
class QuizRecord {
    var mapId: String
    var date: Date
    var elapsedTime: TimeInterval
    var score: Int
    var totalQuestions: Int
    var correctCount: Int
    var totalAttempts: Int

    var accuracy: Double {
        guard totalAttempts > 0 else { return 0 }
        return Double(correctCount) / Double(totalAttempts)
    }

    init(mapId: String, date: Date, elapsedTime: TimeInterval, score: Int, totalQuestions: Int, correctCount: Int, totalAttempts: Int) {
        self.mapId = mapId
        self.date = date
        self.elapsedTime = elapsedTime
        self.score = score
        self.totalQuestions = totalQuestions
        self.correctCount = correctCount
        self.totalAttempts = totalAttempts
    }
}
