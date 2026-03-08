import XCTest
@testable import WhiteMapQuiz

final class PathHitTesterTests: XCTestCase {
    func testHitCorrectRegion() {
        let regions = [
            RegionDefinition(
                id: "region_a",
                name: "A区",
                displayName: "テストA区",
                svgPath: "M 0 0 L 50 0 L 50 50 L 0 50 Z",
                labelPoint: LabelPoint(x: 25, y: 25)
            ),
            RegionDefinition(
                id: "region_b",
                name: "B区",
                displayName: "テストB区",
                svgPath: "M 50 0 L 100 0 L 100 50 L 50 50 Z",
                labelPoint: LabelPoint(x: 75, y: 25)
            )
        ]

        let tester = PathHitTester(regions: regions)
        let viewBox = ViewBox(width: 100, height: 50)
        let viewSize = CGSize(width: 100, height: 50)

        let hitA = tester.hitTest(point: CGPoint(x: 25, y: 25), in: viewSize, viewBox: viewBox)
        XCTAssertEqual(hitA?.id, "region_a")

        let hitB = tester.hitTest(point: CGPoint(x: 75, y: 25), in: viewSize, viewBox: viewBox)
        XCTAssertEqual(hitB?.id, "region_b")
    }

    func testMissReturnsNil() {
        let regions = [
            RegionDefinition(
                id: "region_a",
                name: "A区",
                displayName: "テストA区",
                svgPath: "M 0 0 L 50 0 L 50 50 L 0 50 Z",
                labelPoint: LabelPoint(x: 25, y: 25)
            )
        ]

        let tester = PathHitTester(regions: regions)
        let viewBox = ViewBox(width: 100, height: 100)
        let viewSize = CGSize(width: 100, height: 100)

        let hit = tester.hitTest(point: CGPoint(x: 80, y: 80), in: viewSize, viewBox: viewBox)
        XCTAssertNil(hit)
    }
}
