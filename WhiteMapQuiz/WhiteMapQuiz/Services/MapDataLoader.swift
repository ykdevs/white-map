import Foundation

struct MapDataLoader {
    /// バンドル内の全地図定義を読み込む
    static func loadAllMaps() -> [MapDefinition] {
        guard let urls = Bundle.main.urls(forResourcesWithExtension: "json", subdirectory: nil) else {
            return []
        }

        return urls.compactMap { url in
            loadMap(from: url)
        }
        .sorted { $0.displayName < $1.displayName }
    }

    /// 指定IDの地図定義を読み込む
    static func loadMap(id: String) -> MapDefinition? {
        guard let url = Bundle.main.url(forResource: id, withExtension: "json") else {
            return nil
        }
        return loadMap(from: url)
    }

    private static func loadMap(from url: URL) -> MapDefinition? {
        guard let data = try? Data(contentsOf: url) else { return nil }
        return try? JSONDecoder().decode(MapDefinition.self, from: data)
    }
}
