import Foundation
import SwiftData

struct QuizRecordStore {
    private let modelContext: ModelContext

    init(modelContext: ModelContext) {
        self.modelContext = modelContext
    }

    /// 記録を保存し、過去5件を超えた古い記録を削除する
    func save(record: QuizRecord) throws {
        modelContext.insert(record)

        // 同じ地図の記録を日時降順で取得
        let mapId = record.mapId
        var descriptor = FetchDescriptor<QuizRecord>(
            predicate: #Predicate { $0.mapId == mapId },
            sortBy: [SortDescriptor(\.date, order: .reverse)]
        )
        descriptor.fetchLimit = 100

        let records = try modelContext.fetch(descriptor)

        // 6件目以降を削除
        if records.count > 5 {
            for record in records.dropFirst(5) {
                modelContext.delete(record)
            }
        }

        try modelContext.save()
    }

    /// 指定地図の過去記録を取得（最新5件、日時降順）
    func fetchRecords(mapId: String) throws -> [QuizRecord] {
        var descriptor = FetchDescriptor<QuizRecord>(
            predicate: #Predicate { $0.mapId == mapId },
            sortBy: [SortDescriptor(\.date, order: .reverse)]
        )
        descriptor.fetchLimit = 5
        return try modelContext.fetch(descriptor)
    }

    /// 指定地図のベストスコアを取得
    func bestScore(mapId: String) throws -> Int? {
        let records = try fetchRecords(mapId: mapId)
        return records.map(\.score).max()
    }
}
