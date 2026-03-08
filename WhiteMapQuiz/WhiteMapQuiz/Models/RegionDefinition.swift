import Foundation

struct RegionDefinition: Codable, Identifiable {
    let id: String
    let name: String
    let displayName: String
    let svgPath: String
    let labelPoint: LabelPoint
}

struct LabelPoint: Codable {
    let x: CGFloat
    let y: CGFloat

    var cgPoint: CGPoint {
        CGPoint(x: x, y: y)
    }
}
