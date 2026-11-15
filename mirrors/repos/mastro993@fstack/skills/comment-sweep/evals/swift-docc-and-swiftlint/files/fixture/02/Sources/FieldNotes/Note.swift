import Foundation

/// A single field note, as stored on the device and on the server.
public struct Note: Identifiable, Codable, Hashable, Sendable {
    public typealias ID = UUID

    public let id: ID
    // The note's title.
    public var title: String
    public var body: String
    public var updatedAt: Date
    /// The server revision this copy was edited from. The server rejects an upload whose
    /// revision is behind its own with ``NotesAPIError/conflict(serverRevision:)``.
    public var revision: Int

    public init(id: ID = UUID(), title: String, body: String, updatedAt: Date = .now, revision: Int = 0) {
        self.id = id
        self.title = title
        self.body = body
        self.updatedAt = updatedAt
        self.revision = revision
    }
}
