import XCTest
@testable import WhiteMapQuiz

final class SVGPathParserTests: XCTestCase {
    func testBasicMoveAndLine() {
        let path = SVGPathParser.parse("M 0 0 L 100 0 L 100 100 L 0 100 Z")
        let bounds = path.boundingBox
        XCTAssertEqual(bounds.width, 100, accuracy: 0.1)
        XCTAssertEqual(bounds.height, 100, accuracy: 0.1)
    }

    func testRelativeCoordinates() {
        let path = SVGPathParser.parse("M 10 10 l 50 0 l 0 50 l -50 0 z")
        let bounds = path.boundingBox
        XCTAssertEqual(bounds.minX, 10, accuracy: 0.1)
        XCTAssertEqual(bounds.minY, 10, accuracy: 0.1)
        XCTAssertEqual(bounds.width, 50, accuracy: 0.1)
        XCTAssertEqual(bounds.height, 50, accuracy: 0.1)
    }

    func testHorizontalAndVertical() {
        let path = SVGPathParser.parse("M 0 0 H 100 V 50 H 0 Z")
        let bounds = path.boundingBox
        XCTAssertEqual(bounds.width, 100, accuracy: 0.1)
        XCTAssertEqual(bounds.height, 50, accuracy: 0.1)
    }

    func testContainsPoint() {
        let path = SVGPathParser.parse("M 0 0 L 100 0 L 100 100 L 0 100 Z")
        XCTAssertTrue(path.contains(CGPoint(x: 50, y: 50)))
        XCTAssertFalse(path.contains(CGPoint(x: 150, y: 150)))
    }
}
