// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "WhiteMapQuiz",
    platforms: [
        .macOS(.v14),
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "WhiteMapQuiz",
            targets: ["WhiteMapQuiz"]
        )
    ],
    targets: [
        .target(
            name: "WhiteMapQuiz",
            path: "WhiteMapQuiz",
            resources: [
                .process("Resources")
            ]
        ),
        .testTarget(
            name: "WhiteMapQuizTests",
            dependencies: ["WhiteMapQuiz"],
            path: "WhiteMapQuizTests"
        )
    ]
)
