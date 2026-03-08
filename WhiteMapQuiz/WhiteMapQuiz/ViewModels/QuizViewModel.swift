import Foundation
import SwiftUI
import Observation

@Observable
class QuizViewModel {
    let mapDefinition: MapDefinition
    let hitTester: PathHitTester

    private(set) var questionOrder: [RegionDefinition]
    private(set) var currentQuestionIndex: Int = 0
    private(set) var attempts: Int = 0
    private(set) var regionStates: [String: RegionState] = [:]
    private(set) var elapsedTime: TimeInterval = 0
    private(set) var isFinished: Bool = false
    private(set) var lastTapCorrect: Bool?

    private var timer: Timer?
    private var startDate: Date?

    var currentQuestion: RegionDefinition? {
        guard currentQuestionIndex < questionOrder.count else { return nil }
        return questionOrder[currentQuestionIndex]
    }

    var totalQuestions: Int {
        questionOrder.count
    }

    var score: Int {
        regionStates.values.reduce(0) { $0 + $1.score }
    }

    var maxScore: Int {
        totalQuestions * 4
    }

    var correctCount: Int {
        regionStates.values.filter {
            if case .correct = $0 { return true }
            return false
        }.count
    }

    var totalAttempts: Int {
        regionStates.values.reduce(0) { total, state in
            switch state {
            case .correct(let attempt):
                return total + attempt
            case .failed:
                return total + 3
            case .unanswered:
                return total
            }
        }
    }

    var accuracy: Double {
        guard totalAttempts > 0 else { return 0 }
        return Double(correctCount) / Double(totalAttempts)
    }

    init(mapDefinition: MapDefinition) {
        self.mapDefinition = mapDefinition
        self.hitTester = PathHitTester(regions: mapDefinition.regions)
        self.questionOrder = mapDefinition.regions.shuffled()

        for region in mapDefinition.regions {
            regionStates[region.id] = .unanswered
        }
    }

    func start() {
        startDate = Date()
        timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            guard let self, let startDate = self.startDate else { return }
            self.elapsedTime = Date().timeIntervalSince(startDate)
        }
    }

    func stop() {
        timer?.invalidate()
        timer = nil
    }

    func handleTap(at point: CGPoint, in viewSize: CGSize) {
        guard !isFinished, let currentQuestion else { return }

        guard let tappedRegion = hitTester.hitTest(
            point: point,
            in: viewSize,
            viewBox: mapDefinition.viewBox
        ) else {
            lastTapCorrect = nil
            return
        }

        // 既に回答済みの領域は無視
        if let state = regionStates[tappedRegion.id], state != .unanswered {
            return
        }

        if tappedRegion.id == currentQuestion.id {
            // 正答
            let attempt = attempts + 1
            regionStates[tappedRegion.id] = .correct(attempt: attempt)
            lastTapCorrect = true
            advanceToNext()
        } else {
            // 誤答
            attempts += 1
            lastTapCorrect = false
            if attempts >= 3 {
                regionStates[currentQuestion.id] = .failed
                advanceToNext()
            }
        }
    }

    private func advanceToNext() {
        attempts = 0
        currentQuestionIndex += 1
        if currentQuestionIndex >= questionOrder.count {
            isFinished = true
            stop()
        }
    }

    func formattedTime(_ time: TimeInterval? = nil) -> String {
        let t = time ?? elapsedTime
        let minutes = Int(t) / 60
        let seconds = Int(t) % 60
        return String(format: "%d:%02d", minutes, seconds)
    }
}
