import Foundation

/// A single field note, as stored on the device and on the server.
public struct Note: Identifiable, Codable, Hashable, Sendable {
    public typealias ID = UUID

    public let id: ID
    // The note's title.
    public var title: String
    public var body: String
    public var updatedAt: Date

    public init(id: ID = UUID(), title: String, body: String, updatedAt: Date = .now) {
        self.id = id
        self.title = title
        self.body = body
        self.updatedAt = updatedAt
    }
}
