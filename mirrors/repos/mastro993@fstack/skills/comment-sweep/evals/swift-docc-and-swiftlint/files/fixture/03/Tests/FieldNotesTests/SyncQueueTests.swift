import XCTest
@testable import FieldNotes

final class SyncQueueTests: XCTestCase {
    private var journalURL: URL!

    override func setUp() {
        super.setUp()
        journalURL = FileManager.default.temporaryDirectory.appending(path: "journal-\(UUID().uuidString).json")
    }

    override func tearDown() {
        try? FileManager.default.removeItem(at: journalURL)
        super.tearDown()
    }

    func testEnqueueKeepsOnlyTheLatestChangePerNote() async throws {
        let uploader = FakeUploader()
        let queue = SyncQueue(uploader: uploader, journalURL: journalURL)
        var note = Note(title: "Ridge survey", body: "Two kestrels.")

        try await queue.enqueue(note)
        note.body = "Three kestrels."
        try await queue.enqueue(note)

        let pending = await queue.pendingCount
        XCTAssertEqual(pending, 1)
        await queue.drain()
        let uploaded = await uploader.uploaded
        XCTAssertEqual(uploaded.map(\.body), ["Three kestrels."])
    }

    func testDrainUploadsOldestFirst() async throws {
        let uploader = FakeUploader()
        let queue = SyncQueue(uploader: uploader, journalURL: journalURL)
        let first = Note(title: "First", body: "")
        let second = Note(title: "Second", body: "")

        try await queue.enqueue(first)
        try await queue.enqueue(second)
        let count = await queue.drain()

        XCTAssertEqual(count, 2)
        let uploaded = await uploader.uploaded
        XCTAssertEqual(uploaded.map(\.id), [first.id, second.id])
    }

    func testPendingChangesSurviveARestart() async throws {
        let note = Note(title: "Before the crash", body: "")
        try await SyncQueue(uploader: FakeUploader(), journalURL: journalURL).enqueue(note)

        let relaunched = SyncQueue(uploader: FakeUploader(), journalURL: journalURL)
        try await relaunched.restore()

        let pending = await relaunched.pendingCount
        XCTAssertEqual(pending, 1)
    }

    func testNoteBodyHoldingSourceCodeSurvivesTheJournal() async throws {
        let body = """
            // not a comment
            let total = items.count /* also not */
            """
        let note = Note(title: "Snippet", body: body)
        try await SyncQueue(uploader: FakeUploader(), journalURL: journalURL).enqueue(note)

        let uploader = FakeUploader()
        let relaunched = SyncQueue(uploader: uploader, journalURL: journalURL)
        try await relaunched.restore()
        await relaunched.drain()

        let uploaded = await uploader.uploaded
        XCTAssertEqual(uploaded.first?.body, body)
    }

    func testChangeIsDroppedAfterMaxAttempts() async throws {
        let uploader = FakeUploader(failures: 3)
        let queue = SyncQueue(uploader: uploader, journalURL: journalURL, maxAttempts: 3, baseRetryDelay: 0)
        try await queue.enqueue(Note(title: "Doomed", body: ""))

        let count = await queue.drain()

        XCTAssertEqual(count, 0)
        let pending = await queue.pendingCount
        XCTAssertEqual(pending, 0)
    }

    func testDrainStopsWhenOffline() async throws {
        let uploader = FakeUploader(error: URLError(.notConnectedToInternet), failures: 1)
        let queue = SyncQueue(uploader: uploader, journalURL: journalURL)
        try await queue.enqueue(Note(title: "Later", body: ""))

        let count = await queue.drain()

        XCTAssertEqual(count, 0)
        let pending = await queue.pendingCount
        XCTAssertEqual(pending, 1)
    }
}

private actor FakeUploader: NoteUploading {
    private(set) var uploaded: [Note] = []
    private var failures: Int
    private let error: Error

    init(error: Error = URLError(.badServerResponse), failures: Int = 0) {
        self.error = error
        self.failures = failures
    }

    func upload(_ note: Note) async throws -> Note {
        if failures > 0 {
            failures -= 1
            throw error
        }
        uploaded.append(note)
        return note
    }
}
