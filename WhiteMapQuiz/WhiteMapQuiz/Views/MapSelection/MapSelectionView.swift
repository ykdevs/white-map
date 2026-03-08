import SwiftUI
import SwiftData

struct MapSelectionView: View {
    @Binding var navigationPath: NavigationPath
    @Environment(\.modelContext) private var modelContext
    @State private var viewModel = MapSelectionViewModel()

    private let columns = [
        GridItem(.adaptive(minimum: 250, maximum: 350), spacing: 20)
    ]

    var body: some View {
        ScrollView {
            LazyVGrid(columns: columns, spacing: 20) {
                ForEach(viewModel.maps) { map in
                    NavigationLink(value: map) {
                        MapCardView(
                            map: map,
                            bestScore: viewModel.bestScores[map.id]
                        )
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding()
        }
        .navigationTitle("白地図クイズ")
        .onAppear {
            viewModel.loadMaps(modelContext: modelContext)
        }
    }
}
