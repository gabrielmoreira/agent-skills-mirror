# Core Data Coexistence

Standalone Core Data patterns for projects not yet on SwiftData, strategies
for running Core Data and SwiftData side by side against the same store, and
migration guidance for transitioning from Core Data to SwiftData.

## Contents

- [Standalone Core Data Stack](#standalone-core-data-stack)
- [Core Data + SwiftData Coexistence](#core-data--swiftdata-coexistence)
- [Migration from Core Data to SwiftData](#migration-from-core-data-to-swiftdata)

## Standalone Core Data Stack

For teams that haven't adopted SwiftData, Core Data remains a fully supported
persistence framework.

Docs: [NSPersistentContainer](https://sosumi.ai/documentation/coredata/nspersistentcontainer),
[Setting up a Core Data stack](https://sosumi.ai/documentation/coredata/setting-up-a-core-data-stack)

### NSPersistentContainer Setup

`NSPersistentContainer` encapsulates the Core Data stack: the managed object
model, the persistent store coordinator, and the managed object context.

```swift
import CoreData

final class CoreDataStack: @unchecked Sendable {
    static let shared = CoreDataStack()

    let container: NSPersistentContainer

    private init() {
        // Name must match the .xcdatamodeld file name
        container = NSPersistentContainer(name: "MyAppModel")

        container.loadPersistentStores { description, error in
            if let error {
                fatalError("Core Data store failed to load: \(error)")
            }
        }

        // Automatically merge changes from background contexts
        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
    }

    /// The main-thread context for UI reads
    var viewContext: NSManagedObjectContext {
        container.viewContext
    }

    /// A new background context for writes
    func newBackgroundContext() -> NSManagedObjectContext {
        container.newBackgroundContext()
    }
}
```

### NSManagedObjectContext Usage

The `viewContext` is bound to the main queue; use it for reads and UI. Use
background contexts for writes and batch operations.

```swift
// Reading on the main context
func fetchTrips() throws -> [CDTrip] {
    let context = CoreDataStack.shared.viewContext
    let request = CDTrip.fetchRequest()
    request.sortDescriptors = [NSSortDescriptor(keyPath: \CDTrip.startDate, ascending: true)]
    return try context.fetch(request)
}

// Writing on a background context
func createTrip(name: String, destination: String) async throws {
    let context = CoreDataStack.shared.newBackgroundContext()
    try await context.perform {
        let trip = CDTrip(context: context)
        trip.name = name
        trip.destination = destination
        trip.startDate = Date.now
        trip.id = UUID()
        try context.save()
    }
}
```

### NSFetchRequest with NSPredicate and NSSortDescriptor

```swift
import CoreData

func fetchUpcomingTrips(destination: String) throws -> [CDTrip] {
    let context = CoreDataStack.shared.viewContext
    let request: NSFetchRequest<CDTrip> = CDTrip.fetchRequest()

    // Predicate: filter by destination and future start date
    request.predicate = NSCompoundPredicate(andPredicateWithSubpredicates: [
        NSPredicate(format: "destination ==[cd] %@", destination),
        NSPredicate(format: "startDate > %@", Date.now as NSDate)
    ])

    // Sort: newest first
    request.sortDescriptors = [
        NSSortDescriptor(keyPath: \CDTrip.startDate, ascending: false)
    ]

    // Performance: limit results and prefetch relationships
    request.fetchLimit = 20
    request.relationshipKeyPathsForPrefetching = ["accommodation"]

    return try context.fetch(request)
}

// Counting without loading objects
func countFavoriteTrips() throws -> Int {
    let request: NSFetchRequest<CDTrip> = CDTrip.fetchRequest()
    request.predicate = NSPredicate(format: "isFavorite == YES")
    return try CoreDataStack.shared.viewContext.count(for: request)
}
```

### Saving Context and Error Handling

```swift
func saveContext(_ context: NSManagedObjectContext) throws {
    guard context.hasChanges else { return }

    do {
        try context.save()
    } catch {
        // Roll back unsaved changes to prevent inconsistent state
        context.rollback()

        if let nsError = error as NSError? {
            // Check for common Core Data errors
            switch nsError.code {
            case NSManagedObjectConstraintMergeError:
                // Unique constraint violation -- handle merge conflict
                throw PersistenceError.constraintViolation(nsError)
            case NSValidationMissingMandatoryPropertyError:
                // Required property is nil
                throw PersistenceError.validationFailed(nsError)
            default:
                throw PersistenceError.saveFailed(nsError)
            }
        }
        throw error
    }
}

enum PersistenceError: Error {
    case constraintViolation(NSError)
    case validationFailed(NSError)
    case saveFailed(NSError)
}
```

### Background Processing Pattern

```swift
func importTrips(_ records: [TripRecord]) async throws {
    let context = CoreDataStack.shared.newBackgroundContext()
    try await context.perform {
        // Batch insert for performance (iOS 13+)
        let batchInsert = NSBatchInsertRequest(
            entity: CDTrip.entity(),
            objects: records.map { record in
                [
                    "id": record.id,
                    "name": record.name,
                    "destination": record.destination,
                    "startDate": record.startDate
                ] as [String: Any]
            }
        )
        batchInsert.resultType = .count
        let result = try context.execute(batchInsert) as? NSBatchInsertResult
        print("Inserted \(result?.result as? Int ?? 0) trips")

        // Merge changes into viewContext
        NSManagedObjectContext.mergeChanges(
            fromRemoteContextSave: [NSInsertedObjectsKey: []],
            into: [CoreDataStack.shared.viewContext]
        )
    }
}
```

## Core Data + SwiftData Coexistence

Core Data and SwiftData can share the same underlying SQLite store. This
enables gradual migration: keep existing Core Data code running while
introducing SwiftData for new features.

Docs: [Adopting SwiftData for a Core Data app](https://sosumi.ai/documentation/coredata/adopting_swiftdata_for_a_core_data_app)

### Using the Same Underlying Store

Both stacks must point to the same SQLite file and agree on the schema. The
Core Data `.xcdatamodeld` and SwiftData `@Model` classes must describe the
same entities and properties.

```swift
import SwiftData
import CoreData

// 1. Determine the store URL that Core Data already uses
let storeURL = NSPersistentContainer.defaultDirectoryURL()
    .appendingPathComponent("MyAppModel.sqlite")

// 2. Point SwiftData at the same store
let config = ModelConfiguration(
    "MyAppModel",
    url: storeURL
)

let container = try ModelContainer(
    for: Trip.self,
    configurations: config
)
```

### ModelConfiguration Pointing to Existing Core Data Store

Key rules for coexistence:

1. The `@Model` class name must match the Core Data entity name.
2. Property names and types must match exactly.
3. Use `@Attribute(originalName:)` if you renamed properties.
4. Both stacks should use the same store file.

```swift
// Core Data entity: CDTrip (entity name "Trip" in .xcdatamodeld)
// Attributes: name (String), destination (String), startDate (Date),
//             isFavorite (Boolean), imageData (Binary Data)

// Matching SwiftData model
@Model
class Trip {
    var name: String
    var destination: String
    var startDate: Date
    var isFavorite: Bool = false
    @Attribute(.externalStorage) var imageData: Data?

    init(name: String, destination: String, startDate: Date) {
        self.name = name
        self.destination = destination
        self.startDate = startDate
    }
}
```

### Gradual Coexistence Strategy

```swift
// Phase 1: Core Data stack still handles writes;
//          SwiftData reads the same store for new UI
@main
struct MyApp: App {
    let coreDataStack = CoreDataStack.shared  // Existing Core Data

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        // SwiftData reads from the same store
        .modelContainer(for: Trip.self, configurations:
            ModelConfiguration(url: coreDataStack.storeURL)
        )
    }
}

// Phase 2: New features use SwiftData for both reads and writes
// Phase 3: Migrate remaining Core Data code to SwiftData
// Phase 4: Remove Core Data stack and .xcdatamodeld
```

### Important Coexistence Rules

- **Do not write to the same entity from both stacks simultaneously.** Pick
  one stack per entity for writes to avoid conflicts.
- Core Data's `automaticallyMergesChangesFromParent` and
  `NSPersistentStoreRemoteChangeNotification` help detect changes from the
  other stack.
- Test thoroughly -- schema mismatches between the `.xcdatamodeld` and
  `@Model` cause crashes.

## Migration from Core Data to SwiftData

### Step 1: Map Core Data Entities to @Model Classes

Create a `@Model` class for each Core Data entity. Property names and types
must align with the `.xcdatamodeld` definition.

```swift
// Core Data entity "Article"
// Attributes: id (UUID), title (String), body (String),
//             createdAt (Date), isDraft (Boolean)
// Relationships: author (to-one → Author), tags (to-many → Tag)

@Model
class Article {
    @Attribute(.unique) var id: UUID
    var title: String
    var body: String
    var createdAt: Date
    var isDraft: Bool = true

    @Relationship(deleteRule: .nullify, inverse: \Author.articles)
    var author: Author?

    @Relationship(deleteRule: .nullify, inverse: \Tag.articles)
    var tags: [Tag] = []

    init(id: UUID = UUID(), title: String, body: String, createdAt: Date = .now) {
        self.id = id
        self.title = title
        self.body = body
        self.createdAt = createdAt
    }
}

@Model
class Author {
    @Attribute(.unique) var id: UUID
    var name: String
    var articles: [Article] = []

    init(id: UUID = UUID(), name: String) {
        self.id = id
        self.name = name
    }
}

@Model
class Tag {
    @Attribute(.unique) var id: UUID
    var name: String
    var articles: [Article] = []

    init(id: UUID = UUID(), name: String) {
        self.id = id
        self.name = name
    }
}
```

### Type Mapping Reference

| Core Data Type | SwiftData Type |
|---|---|
| String | String |
| Boolean | Bool |
| Integer 16/32/64 | Int |
| Float / Double | Float / Double |
| Date | Date |
| Binary Data | Data |
| UUID | UUID |
| URI | URL |
| Decimal | Decimal |
| Transformable | Codable struct (composite, iOS 18+) |
| To-one relationship | Optional reference to @Model |
| To-many relationship | Array of @Model |

### Step 2: Schema Versioning Considerations

If the Core Data store has existing data, SwiftData must be able to open it.
Use `VersionedSchema` and `SchemaMigrationPlan` for non-trivial changes.

```swift
// If the SwiftData model exactly matches the Core Data schema,
// no migration is needed -- SwiftData opens the store directly.

// For schema differences, define versioned schemas:
enum SchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] { [Article.self, Author.self] }

    @Model class Article {
        var id: UUID
        var title: String
        var body: String
        var createdAt: Date
        init(id: UUID, title: String, body: String, createdAt: Date) {
            self.id = id; self.title = title
            self.body = body; self.createdAt = createdAt
        }
    }

    @Model class Author {
        var id: UUID
        var name: String
        init(id: UUID, name: String) { self.id = id; self.name = name }
    }
}

enum SchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] { [Article.self, Author.self, Tag.self] }

    @Model class Article {
        var id: UUID
        var title: String
        var body: String
        var createdAt: Date
        var isDraft: Bool = true  // New property
        init(id: UUID, title: String, body: String, createdAt: Date) {
            self.id = id; self.title = title
            self.body = body; self.createdAt = createdAt
        }
    }

    @Model class Author {
        var id: UUID
        var name: String
        init(id: UUID, name: String) { self.id = id; self.name = name }
    }

    @Model class Tag {
        var id: UUID
        var name: String
        init(id: UUID, name: String) { self.id = id; self.name = name }
    }
}

enum ArticleMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] { [SchemaV1.self, SchemaV2.self] }
    static var stages: [MigrationStage] {
        [MigrationStage.lightweight(fromVersion: SchemaV1.self, toVersion: SchemaV2.self)]
    }
}
```

### Step 3: Testing Migration Paths

Always test migration with real production data copies before shipping.

```swift
import XCTest
import SwiftData

final class MigrationTests: XCTestCase {

    func testCoreDataToSwiftDataMigration() throws {
        // 1. Copy a known Core Data store into the test bundle
        let sourceURL = Bundle(for: type(of: self))
            .url(forResource: "TestStore", withExtension: "sqlite")!

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)

        let destURL = tempDir.appendingPathComponent("TestStore.sqlite")
        try FileManager.default.copyItem(at: sourceURL, to: destURL)

        // Copy WAL and SHM if they exist
        for ext in ["-wal", "-shm"] {
            let src = sourceURL.deletingLastPathComponent()
                .appendingPathComponent("TestStore.sqlite\(ext)")
            if FileManager.default.fileExists(atPath: src.path) {
                try FileManager.default.copyItem(
                    at: src,
                    to: tempDir.appendingPathComponent("TestStore.sqlite\(ext)")
                )
            }
        }

        // 2. Open with SwiftData
        let config = ModelConfiguration(url: destURL)
        let container = try ModelContainer(
            for: SchemaV2.Article.self,
            migrationPlan: ArticleMigrationPlan.self,
            configurations: config
        )

        // 3. Verify data survived migration
        let context = ModelContext(container)
        let articles = try context.fetch(FetchDescriptor<SchemaV2.Article>())
        XCTAssertFalse(articles.isEmpty, "Migration should preserve existing articles")

        // 4. Verify new properties have defaults
        for article in articles {
            XCTAssertTrue(article.isDraft, "New isDraft property should default to true")
        }

        // Cleanup
        try FileManager.default.removeItem(at: tempDir)
    }
}
```

### Migration Checklist

- [ ] Every Core Data entity has a matching `@Model` class with identical property names and types
- [ ] Relationship inverse properties are specified in both directions
- [ ] `VersionedSchema` and `SchemaMigrationPlan` defined for non-trivial schema changes
- [ ] `ModelConfiguration` points to the existing Core Data SQLite file
- [ ] Tested migration with a copy of production data
- [ ] Only one stack writes to each entity during coexistence
- [ ] `automaticallyMergesChangesFromParent` enabled on Core Data's `viewContext`
- [ ] `.xcdatamodeld` removed only after full migration is verified
