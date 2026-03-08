import SwiftUI
import SwiftData

@main
struct WhiteMapQuizApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: QuizRecord.self)
        #if os(macOS)
        .defaultSize(width: 1000, height: 700)
        #endif
    }
}
