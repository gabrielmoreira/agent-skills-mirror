import Observation
import SwiftUI

/// Sync progress for ``SyncStatusView``, fed by ``SyncQueue/events()``.
@Observable
public final class SyncStatus {
    public private(set) var pending = 0
    public private(set) var dropped = 0
    public private(set) var isSyncing = false
    public private(set) var lastUploadAt: Date?

    public init() {}

    // Must be called on the main actor: SyncStatusView renders these properties, and SwiftUI
    // expects the state it observes to change on the main thread.
    func apply(_ event: SyncEvent) {
        switch event {
        case .started(let count):
            isSyncing = true
            pending = count
        case .uploaded:
            pending = max(pending - 1, 0)
            lastUploadAt = .now
        case .dropped:
            pending = max(pending - 1, 0)
            dropped += 1
        case .finished(_, let remaining):
            isSyncing = false
            pending = remaining
        }
    }
}

/// A compact banner showing how many offline changes are waiting to sync, with a button to sync now.
public struct SyncStatusView: View {
    let queue: SyncQueue
    @State private var status = SyncStatus()

    public init(queue: SyncQueue) {
        self.queue = queue
    }

    public var body: some View {
        HStack(spacing: 8) {
            icon
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline.weight(.semibold))
                if let subtitle {
                    Text(subtitle)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            Spacer()
            if status.pending > 0 && !status.isSyncing {
                Button("Sync now") {
                    Task { await queue.drain() }
                }
                .buttonStyle(.bordered)
                // .tint(.orange)
            }
        }
        .padding(12)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 12))
        .task {
            for await event in await queue.events() {
                status.apply(event)
            }
        }
    }

    // MARK: - Subviews

    @ViewBuilder private var icon: some View {
        if status.isSyncing {
            ProgressView()
        } else if status.pending == 0 {
            Image(systemName: "checkmark.icloud")
        } else {
            Image(systemName: "icloud.slash")
        }
    }

    private var title: String {
        // show "All synced" when nothing is pending
        if status.pending == 0 {
            return "All synced"
        }
        return status.pending == 1 ? "1 change waiting" : "\(status.pending) changes waiting"
    }

    private var subtitle: String? {
        if status.dropped > 0 {
            return "\(status.dropped) couldn't be uploaded"
        }
        guard let lastUploadAt = status.lastUploadAt else { return nil }
        return "Last synced \(lastUploadAt.formatted(.relative(presentation: .named)))"
    }
}
