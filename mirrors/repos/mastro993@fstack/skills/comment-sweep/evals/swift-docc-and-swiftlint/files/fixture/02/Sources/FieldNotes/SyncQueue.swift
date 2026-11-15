import Foundation

/// A note change waiting to be uploaded.
public struct PendingChange: Codable, Hashable, Sendable {
    public let note: Note
    public var attempts: Int

    public init(note: Note, attempts: Int = 0) {
        self.note = note
        self.attempts = attempts
    }
}

/// Errors thrown by ``SyncQueue``.
public enum SyncQueueError: Error, Equatable {
    /// ``SyncQueue/capacity`` changes are already pending.
    case queueFull
}

/// What happened during a drain, for the status UI.
public enum SyncEvent: Sendable, Equatable {
    case started(pending: Int)
    case uploaded(Note.ID)
    case dropped(Note.ID, attempts: Int)
    case finished(uploaded: Int, remaining: Int)
}

// Moved this off the main actor per PR feedback.
/// Holds note changes made while offline and uploads them, oldest first, once the device is back online.
///
/// The queue writes its journal to disk after every change, so pending edits survive the app being killed.
public actor SyncQueue {
    /// The most changes the queue holds before ``enqueue(_:)`` throws.
    public static let capacity = 500

    private let uploader: any NoteUploading
    private let journalURL: URL
    private let maxAttempts: Int
    private let baseRetryDelay: Double
    private var pending: [PendingChange] = []
    private var isDraining = false
    private var continuations: [UUID: AsyncStream<SyncEvent>.Continuation] = [:]

    /// Creates a queue backed by a journal file.
    ///
    /// - Parameters:
    ///   - uploader: Where changes are sent; ``NotesAPI`` in the app.
    ///   - journalURL: The file the queue persists to. Use a location the user can't see, such as
    ///     Application Support; the queue creates the file on the first ``enqueue(_:)``.
    ///   - maxAttempts: Failed uploads after which a change is dropped and reported as
    ///     ``SyncEvent/dropped(_:attempts:)``. Being offline doesn't count as a failure.
    ///   - baseRetryDelay: Seconds to wait before the first retry; the wait doubles after each failure.
    public init(uploader: any NoteUploading, journalURL: URL, maxAttempts: Int = 5, baseRetryDelay: Double = 2) {
        self.uploader = uploader
        self.journalURL = journalURL
        self.maxAttempts = maxAttempts
        self.baseRetryDelay = baseRetryDelay
    }

    /// The number of changes waiting to upload.
    public var pendingCount: Int { pending.count }

    /// Adds a change to the queue and writes the journal before returning.
    ///
    /// A newer change to a note that is already pending replaces the older one, so each note
    /// uploads at most once per drain.
    ///
    /// - Parameter note: The note as it should end up on the server.
    /// - Throws: ``SyncQueueError/queueFull`` when ``capacity`` changes are already pending, or the
    ///   file system error when the journal can't be written. The queue is unchanged either way.
    public func enqueue(_ note: Note) throws {
        if let index = pending.firstIndex(where: { $0.note.id == note.id }) {
            let previous = pending[index]
            pending[index] = PendingChange(note: note)
            do {
                try persist()
            } catch {
                pending[index] = previous
                throw error
            }
            return
        }
        guard pending.count < Self.capacity else { throw SyncQueueError.queueFull }
        // append to the queue
        pending.append(PendingChange(note: note))
        do {
            try persist()
        } catch {
            pending.removeLast()
            throw error
        }
    }

    /// Removes the pending change with the given id.
    ///
    /// - Parameter id: The id.
    public func remove(id: Note.ID) throws {
        pending.removeAll { $0.note.id == id }
        try persist()
    }

    /// Events from every drain, starting with the next one.
    ///
    /// Each call returns a new stream, which finishes when its consumer stops iterating.
    public func events() -> AsyncStream<SyncEvent> {
        let (stream, continuation) = AsyncStream.makeStream(of: SyncEvent.self)
        let id = UUID()
        continuations[id] = continuation
        continuation.onTermination = { [weak self] _ in
            Task { await self?.removeContinuation(id) }
        }
        return stream
    }

    // MARK: - Draining

    // swiftlint:disable function_body_length
    /// Uploads pending changes, oldest first, until the queue is empty or the device goes offline.
    ///
    /// Only one drain runs at a time: calling this while a drain is in progress returns `0` at once.
    ///
    /// - Returns: The number of changes uploaded. Changes dropped after `maxAttempts` failures
    ///   aren't counted.
    @discardableResult
    public func drain() async -> Int {
        guard !isDraining else { return 0 }
        isDraining = true
        defer { isDraining = false }

        emit(.started(pending: pending.count))
        var uploaded = 0
        // TODO: upload changes to different notes in parallel (https://github.com/fieldnotes/fieldnotes-ios/issues/212)
        // loop over pending items
        while let change = pending.first, !Task.isCancelled {
            do {
                _ = try await uploader.upload(change.note)
                pending.removeAll { $0.note == change.note }
                try? persist()
                uploaded += 1
                emit(.uploaded(change.note.id))
            } catch let error as URLError where error.code == .notConnectedToInternet {
                break
            } catch {
                guard let index = pending.firstIndex(where: { $0.note == change.note }) else { continue }
                pending[index].attempts += 1
                if pending[index].attempts >= maxAttempts {
                    let dropped = pending.remove(at: index)
                    try? persist()
                    emit(.dropped(dropped.note.id, attempts: dropped.attempts))
                    continue
                }
                try? persist()
                // TODO: add exponential backoff
                // Wait baseRetryDelay milliseconds before retrying, doubled after each failure.
                let delay = baseRetryDelay * pow(2, Double(pending[index].attempts - 1))
                try? await Task.sleep(for: .seconds(delay))
            }
        }

        emit(.finished(uploaded: uploaded, remaining: pending.count))
        return uploaded
    }
    // swiftlint:enable function_body_length

    /* Polling version, replaced by SyncScheduler:
    func startPolling() {
        /* every 30 seconds while the app is open */
        Task {
            while !Task.isCancelled {
                try await Task.sleep(for: .seconds(30))
                await drain()
            }
        }
    }
    */

    // MARK: - Persistence

    /// Loads the journal a previous launch wrote. Call it once, before the first ``enqueue(_:)``.
    ///
    /// - Throws: The decoding error when the journal is corrupt. A missing journal isn't an error.
    public func restore() throws {
        guard FileManager.default.fileExists(atPath: journalURL.path) else { return }
        let data = try Data(contentsOf: journalURL)
        pending = try JSONDecoder.notes.decode([PendingChange].self, from: data)
    }

    private func persist() throws {
        let data = try JSONEncoder.notes.encode(pending)
        try data.write(to: journalURL, options: .atomic)
    }

    private func emit(_ event: SyncEvent) {
        for continuation in continuations.values {
            continuation.yield(event)
        }
    }

    private func removeContinuation(_ id: UUID) {
        continuations[id] = nil
    }
}
