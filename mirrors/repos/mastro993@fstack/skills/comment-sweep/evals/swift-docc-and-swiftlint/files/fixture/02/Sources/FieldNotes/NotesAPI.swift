import Foundation

/// Errors the notes backend reports.
public enum NotesAPIError: Error, Equatable {
    case unauthorized
    case conflict(serverRevision: Int)
    case server(status: Int)
}

/// Something that can push a note to the server. ``NotesAPI`` in the app, a fake in tests.
public protocol NoteUploading: Sendable {
    func upload(_ note: Note) async throws -> Note
}

/// Talks to the FieldNotes backend over HTTPS.
public struct NotesAPI: NoteUploading {
    public var baseURL: URL
    let session: URLSession

    public init(baseURL: URL, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
    }

    /// Fetches every note the signed-in user can see, newest first.
    ///
    /// - Throws: ``NotesAPIError/unauthorized`` when the session token has expired.
    public func fetchNotes() async throws -> [Note] {
        let (data, response) = try await session.data(from: baseURL.appending(path: "notes"))
        try Self.check(response)
        return try JSONDecoder.notes.decode([Note].self, from: data)
    }

    /// Creates or replaces a note on the server.
    ///
    /// - Parameter note: The note to store; its ``Note/revision`` must match the server's.
    /// - Returns: The note as the server stored it, with the revision bumped by one.
    /// - Throws: ``NotesAPIError/conflict(serverRevision:)`` when the server holds a newer revision,
    ///   ``NotesAPIError/unauthorized`` when the session token has expired, or a `URLError` when offline.
    public func upload(_ note: Note) async throws -> Note {
        #warning("PUT /v2/notes/{id} is behind the sync_v2 flag on the backend; enable it before release")
        var request = URLRequest(url: baseURL.appending(path: "v2/notes/\(note.id.uuidString)"))
        request.httpMethod = "PUT"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder.notes.encode(note)

        let (data, response) = try await session.data(for: request)
        if let http = response as? HTTPURLResponse, http.statusCode == 409 {
            let server = try JSONDecoder.notes.decode(Note.self, from: data)
            throw NotesAPIError.conflict(serverRevision: server.revision)
        }
        try Self.check(response)
        return try JSONDecoder.notes.decode(Note.self, from: data)
    }

    static func check(_ response: URLResponse) throws {
        guard let http = response as? HTTPURLResponse else {
            throw NotesAPIError.server(status: -1)
        }
        switch http.statusCode {
        case 200..<300:
            return
        case 401:
            throw NotesAPIError.unauthorized
        default:
            throw NotesAPIError.server(status: http.statusCode)
        }
    }
}

extension JSONDecoder {
    static let notes: JSONDecoder = {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }()
}

extension JSONEncoder {
    static let notes: JSONEncoder = {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        return encoder
    }()
}
