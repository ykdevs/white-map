import Foundation
import SwiftData
import Observation

@Observable
class ResultViewModel {
    let quizViewModel: QuizViewModel
    private(set) var pastRecords: [QuizRecord] = []
    private(set) var isSaved = false

    init(quizViewModel: QuizViewModel) {
        self.quizViewModel = quizViewModel
    }

    func saveAndLoad(modelContext: ModelContext) {
        guard !isSaved else { return }
        isSaved = true

        let store = QuizRecordStore(modelContext: modelContext)

        let record = QuizRecord(
            mapId: quizViewModel.mapDefinition.id,
            date: Date(),
            elapsedTime: quizViewModel.elapsedTime,
            score: quizViewModel.score,
            totalQuestions: quizViewModel.totalQuestions,
            correctCount: quizViewModel.correctCount,
            totalAttempts: quizViewModel.totalAttempts
        )

        try? store.save(record: record)
        pastRecords = (try? store.fetchRecords(mapId: quizViewModel.mapDefinition.id)) ?? []
    }
}
