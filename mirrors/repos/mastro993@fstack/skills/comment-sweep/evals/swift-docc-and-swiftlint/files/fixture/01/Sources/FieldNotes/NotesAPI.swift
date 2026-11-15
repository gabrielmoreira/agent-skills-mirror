import Foundation

/// Errors the notes backend reports.
public enum NotesAPIError: Error, Equatable {
    case unauthorized
    case server(status: Int)
}

/// Talks to the FieldNotes backend over HTTPS.
public struct NotesAPI: Sendable {
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
