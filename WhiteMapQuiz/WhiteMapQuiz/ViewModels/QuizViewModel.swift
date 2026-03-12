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

    /// 飛び地ID → 本体IDのマッピング
    private let parentIdMap: [String: String]
    /// グループID → 代表領域IDのマッピング
    private let groupRepresentativeMap: [String: String]
    /// 領域ID → グループIDのマッピング（グループに属する出題対象のみ）
    private let regionGroupMap: [String: String]

    init(mapDefinition: MapDefinition) {
        self.mapDefinition = mapDefinition
        self.hitTester = PathHitTester(regions: mapDefinition.regions)

        // 飛び地 → 本体IDのマッピングを構築
        var parentMap: [String: String] = [:]
        for region in mapDefinition.regions {
            if let parentId = region.parentId {
                parentMap[region.id] = parentId
            }
        }
        self.parentIdMap = parentMap

        // グループマッピングを構築
        // 同じgroupIdを持つ出題対象領域のうち、最初の1つを代表とする
        var groupRep: [String: String] = [:]
        var regGroup: [String: String] = [:]
        for region in mapDefinition.regions {
            guard region.parentId == nil, let gid = region.groupId else { continue }
            regGroup[region.id] = gid
            if groupRep[gid] == nil {
                groupRep[gid] = region.id
            }
        }
        self.groupRepresentativeMap = groupRep
        self.regionGroupMap = regGroup

        // 出題対象: 飛び地を除外し、グループは代表のみ
        self.questionOrder = mapDefinition.regions
            .filter { $0.parentId == nil }
            .filter { region in
                if let gid = region.groupId {
                    return groupRep[gid] == region.id
                }
                return true
            }
            .shuffled()

        for region in questionOrder {
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

        // 飛び地をタップした場合は本体IDに解決
        let effectiveId = parentIdMap[tappedRegion.id] ?? tappedRegion.id

        // グループに属する場合は代表IDに解決
        let resolvedId: String
        if let gid = regionGroupMap[effectiveId],
           let repId = groupRepresentativeMap[gid] {
            resolvedId = repId
        } else {
            resolvedId = effectiveId
        }

        // 既に回答済みの領域は無視
        if let state = regionStates[resolvedId], state != .unanswered {
            return
        }

        if resolvedId == currentQuestion.id {
            // 正答
            let attempt = attempts + 1
            regionStates[resolvedId] = .correct(attempt: attempt)
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

    /// 領域IDをグループ代表IDに解決する（グループに属さない場合はそのまま返す）
    func resolveGroupId(_ regionId: String) -> String {
        if let gid = regionGroupMap[regionId],
           let repId = groupRepresentativeMap[gid] {
            return repId
        }
        return regionId
    }

    func formattedTime(_ time: TimeInterval? = nil) -> String {
        let t = time ?? elapsedTime
        let minutes = Int(t) / 60
        let seconds = Int(t) % 60
        return String(format: "%d:%02d", minutes, seconds)
    }
}
