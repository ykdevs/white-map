import Foundation
import SwiftData
import Observation

@Observable
class MapSelectionViewModel {
    private(set) var maps: [MapDefinition] = []
    private(set) var bestScores: [String: Int] = [:]

    func loadMaps(modelContext: ModelContext) {
        maps = MapDataLoader.loadAllMaps()

        let store = QuizRecordStore(modelContext: modelContext)
        for map in maps {
            bestScores[map.id] = try? store.bestScore(mapId: map.id)
        }
    }
}
