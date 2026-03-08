import SwiftUI

struct ContentView: View {
    @State private var navigationPath = NavigationPath()

    var body: some View {
        NavigationStack(path: $navigationPath) {
            MapSelectionView(navigationPath: $navigationPath)
                .navigationDestination(for: MapDefinition.self) { map in
                    QuizView(mapDefinition: map, navigationPath: $navigationPath)
                }
        }
        #if os(macOS)
        .frame(minWidth: 800, minHeight: 600)
        #endif
    }
}

#Preview {
    ContentView()
        .modelContainer(for: QuizRecord.self, inMemory: true)
}
