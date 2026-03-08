import SwiftUI

struct RecordHistoryView: View {
    let records: [QuizRecord]

    private let dateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "M/d HH:mm"
        return f
    }()

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("過去の記録")
                .font(.headline)

            if records.isEmpty {
                Text("記録なし")
                    .foregroundStyle(.secondary)
            } else {
                Grid(alignment: .leading, horizontalSpacing: 16, verticalSpacing: 8) {
                    GridRow {
                        Text("日時").fontWeight(.semibold)
                        Text("時間").fontWeight(.semibold)
                        Text("点数").fontWeight(.semibold)
                        Text("正答率").fontWeight(.semibold)
                    }
                    .font(.caption)
                    .foregroundStyle(.secondary)

                    Divider()

                    ForEach(records, id: \.date) { record in
                        GridRow {
                            Text(dateFormatter.string(from: record.date))
                            Text(formatTime(record.elapsedTime))
                                .monospacedDigit()
                            Text("\(record.score)点")
                                .monospacedDigit()
                            Text(String(format: "%.0f%%", record.accuracy * 100))
                                .monospacedDigit()
                        }
                        .font(.subheadline)
                    }
                }
            }
        }
        .padding()
        .background(.background)
        .clipShape(RoundedRectangle(cornerRadius: 8))
        .shadow(color: .black.opacity(0.05), radius: 2, y: 1)
    }

    private func formatTime(_ time: TimeInterval) -> String {
        let minutes = Int(time) / 60
        let seconds = Int(time) % 60
        return String(format: "%d:%02d", minutes, seconds)
    }
}
