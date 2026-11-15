import XCTest
@testable import FieldNotes

final class NoteTests: XCTestCase {
    func testNoteRoundTripsThroughJSON() throws {
        let note = Note(title: "Ridge survey", body: "Two kestrels near the cairn.",
                        updatedAt: Date(timeIntervalSince1970: 1_700_000_000))

        let data = try JSONEncoder.notes.encode(note)
        let decoded = try JSONDecoder.notes.decode(Note.self, from: data)

        XCTAssertEqual(decoded, note)
    }
}
