import CoreGraphics

struct SVGPathParser {
    /// SVGのd属性文字列をCGPathに変換する
    static func parse(_ svgPathString: String) -> CGPath {
        let path = CGMutablePath()
        let tokens = tokenize(svgPathString)
        var index = 0
        var currentPoint = CGPoint.zero
        var lastControlPoint: CGPoint?
        var subpathStart = CGPoint.zero

        while index < tokens.count {
            let token = tokens[index]
            guard let command = token.first, token.count == 1, command.isLetter else {
                index += 1
                continue
            }
            let isRelative = command.isLowercase
            let cmd = Character(command.uppercased())
            index += 1

            switch cmd {
            case "M":
                let coords = readCoordPairs(tokens: tokens, index: &index)
                for (i, point) in coords.enumerated() {
                    if i == 0 {
                        let target = isRelative ? currentPoint + point : point
                        path.move(to: target)
                        currentPoint = target
                        subpathStart = target
                    } else {
                        let target = isRelative ? currentPoint + point : point
                        path.addLine(to: target)
                        currentPoint = target
                    }
                }
                lastControlPoint = nil

            case "L":
                let coords = readCoordPairs(tokens: tokens, index: &index)
                for point in coords {
                    let target = isRelative ? currentPoint + point : point
                    path.addLine(to: target)
                    currentPoint = target
                }
                lastControlPoint = nil

            case "H":
                let values = readNumbers(tokens: tokens, index: &index)
                for val in values {
                    let x = isRelative ? currentPoint.x + val : val
                    let target = CGPoint(x: x, y: currentPoint.y)
                    path.addLine(to: target)
                    currentPoint = target
                }
                lastControlPoint = nil

            case "V":
                let values = readNumbers(tokens: tokens, index: &index)
                for val in values {
                    let y = isRelative ? currentPoint.y + val : val
                    let target = CGPoint(x: currentPoint.x, y: y)
                    path.addLine(to: target)
                    currentPoint = target
                }
                lastControlPoint = nil

            case "C":
                let coords = readCoordPairs(tokens: tokens, index: &index)
                var ci = 0
                while ci + 2 < coords.count {
                    let cp1 = isRelative ? currentPoint + coords[ci] : coords[ci]
                    let cp2 = isRelative ? currentPoint + coords[ci + 1] : coords[ci + 1]
                    let end = isRelative ? currentPoint + coords[ci + 2] : coords[ci + 2]
                    path.addCurve(to: end, control1: cp1, control2: cp2)
                    lastControlPoint = cp2
                    currentPoint = end
                    ci += 3
                }

            case "S":
                let coords = readCoordPairs(tokens: tokens, index: &index)
                var ci = 0
                while ci + 1 < coords.count {
                    let cp1 = lastControlPoint.map { currentPoint + (currentPoint - $0) } ?? currentPoint
                    let cp2 = isRelative ? currentPoint + coords[ci] : coords[ci]
                    let end = isRelative ? currentPoint + coords[ci + 1] : coords[ci + 1]
                    path.addCurve(to: end, control1: cp1, control2: cp2)
                    lastControlPoint = cp2
                    currentPoint = end
                    ci += 2
                }

            case "Q":
                let coords = readCoordPairs(tokens: tokens, index: &index)
                var ci = 0
                while ci + 1 < coords.count {
                    let cp = isRelative ? currentPoint + coords[ci] : coords[ci]
                    let end = isRelative ? currentPoint + coords[ci + 1] : coords[ci + 1]
                    path.addQuadCurve(to: end, control: cp)
                    lastControlPoint = cp
                    currentPoint = end
                    ci += 2
                }

            case "T":
                let coords = readCoordPairs(tokens: tokens, index: &index)
                for point in coords {
                    let cp = lastControlPoint.map { currentPoint + (currentPoint - $0) } ?? currentPoint
                    let end = isRelative ? currentPoint + point : point
                    path.addQuadCurve(to: end, control: cp)
                    lastControlPoint = cp
                    currentPoint = end
                }

            case "A":
                // 楕円弧: rx ry x-rotation large-arc-flag sweep-flag x y
                let values = readNumbers(tokens: tokens, index: &index)
                var vi = 0
                while vi + 6 < values.count {
                    let rx = values[vi]
                    let ry = values[vi + 1]
                    // x-rotation, large-arc-flag, sweep-flag は簡易実装では直線近似
                    let endX = values[vi + 5]
                    let endY = values[vi + 6]
                    let end = isRelative ? CGPoint(x: currentPoint.x + endX, y: currentPoint.y + endY) : CGPoint(x: endX, y: endY)
                    // 弧を直線で近似（完全な弧の実装は複雑なため）
                    if rx == 0 || ry == 0 {
                        path.addLine(to: end)
                    } else {
                        path.addLine(to: end)
                    }
                    currentPoint = end
                    vi += 7
                }
                lastControlPoint = nil

            case "Z":
                path.closeSubpath()
                currentPoint = subpathStart
                lastControlPoint = nil

            default:
                break
            }
        }

        return path
    }

    // MARK: - Tokenizer

    private static func tokenize(_ input: String) -> [String] {
        var tokens: [String] = []
        var current = ""
        var previousWasE = false

        for char in input {
            if char.isLetter && char != "e" && char != "E" {
                if !current.isEmpty {
                    tokens.append(current)
                    current = ""
                }
                tokens.append(String(char))
                previousWasE = false
            } else if char == "," || char == " " || char == "\t" || char == "\n" || char == "\r" {
                if !current.isEmpty {
                    tokens.append(current)
                    current = ""
                }
                previousWasE = false
            } else if char == "-" && !current.isEmpty && !previousWasE {
                tokens.append(current)
                current = String(char)
                previousWasE = false
            } else {
                current.append(char)
                previousWasE = (char == "e" || char == "E")
            }
        }
        if !current.isEmpty {
            tokens.append(current)
        }
        return tokens
    }

    private static func readNumbers(tokens: [String], index: inout Int) -> [CGFloat] {
        var numbers: [CGFloat] = []
        while index < tokens.count {
            if let value = Double(tokens[index]) {
                numbers.append(CGFloat(value))
                index += 1
            } else {
                break
            }
        }
        return numbers
    }

    private static func readCoordPairs(tokens: [String], index: inout Int) -> [CGPoint] {
        var points: [CGPoint] = []
        while index < tokens.count {
            guard let x = Double(tokens[index]) else { break }
            index += 1
            guard index < tokens.count, let y = Double(tokens[index]) else {
                index -= 1
                break
            }
            index += 1
            points.append(CGPoint(x: CGFloat(x), y: CGFloat(y)))
        }
        return points
    }
}

// MARK: - CGPoint arithmetic

extension CGPoint {
    static func + (lhs: CGPoint, rhs: CGPoint) -> CGPoint {
        CGPoint(x: lhs.x + rhs.x, y: lhs.y + rhs.y)
    }

    static func - (lhs: CGPoint, rhs: CGPoint) -> CGPoint {
        CGPoint(x: lhs.x - rhs.x, y: lhs.y - rhs.y)
    }
}
