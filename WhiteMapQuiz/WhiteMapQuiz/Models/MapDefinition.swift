import Foundation

struct MapDefinition: Codable, Identifiable, Hashable {
    static func == (lhs: MapDefinition, rhs: MapDefinition) -> Bool {
        lhs.id == rhs.id
    }
    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }

    let id: String
    let displayName: String
    let viewBox: ViewBox
    let regions: [RegionDefinition]
}

struct ViewBox: Codable {
    let width: CGFloat
    let height: CGFloat
}
