import Foundation

struct RegionDefinition: Codable, Identifiable {
    let id: String
    let name: String
    let displayName: String
    let svgPath: String
    let labelPoint: LabelPoint
    let parentId: String?

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        displayName = try container.decode(String.self, forKey: .displayName)
        svgPath = try container.decode(String.self, forKey: .svgPath)
        labelPoint = try container.decode(LabelPoint.self, forKey: .labelPoint)
        parentId = try container.decodeIfPresent(String.self, forKey: .parentId)
    }
}

struct LabelPoint: Codable {
    let x: CGFloat
    let y: CGFloat

    var cgPoint: CGPoint {
        CGPoint(x: x, y: y)
    }
}
