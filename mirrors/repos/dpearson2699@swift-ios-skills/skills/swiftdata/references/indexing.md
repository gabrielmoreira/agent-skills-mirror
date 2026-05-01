# SwiftData Indexing

Indexes speed up queries on frequently filtered or sorted properties.

Docs: [Index macro](https://sosumi.ai/documentation/swiftdata/index(_:)-74ia2)

## #Index (iOS 18+)

### Single-Property Index

```swift
@Model
class Trip {
    @Attribute(.unique) var id: UUID
    var destination: String
    var startDate: Date
    var isFavorite: Bool

    init(destination: String, startDate: Date) {
        self.id = UUID()
        self.destination = destination
        self.startDate = startDate
        self.isFavorite = false
    }
}
```

Use `#Index` on the model to declare indexes:

```swift
@Model
class Trip {
    #Index<Trip>([\.destination], [\.startDate])
    // ...
}
```

This creates two single-column indexes: one on `destination` and one on `startDate`.

### Compound Index

```swift
@Model
class Trip {
    #Index<Trip>([\.isFavorite, \.startDate])
    // ...
}
```

A compound index on `(isFavorite, startDate)` accelerates queries that filter on `isFavorite` and sort by `startDate`.

## When to Index

**Index when:**
- A property appears in `#Predicate` filters on large collections (1000+ rows)
- A property is used in `SortDescriptor` on large collections
- `@Attribute(.unique)` properties (automatically indexed)

**Don't index when:**
- The collection is small (< few hundred rows)
- The property is rarely queried
- The property changes very frequently (index maintenance cost)
- The property has very low cardinality (e.g., a Boolean on a small table)

## Index and Migration

Adding or removing an index is a lightweight migration — SwiftData handles it automatically without a `SchemaMigrationPlan`. The index is rebuilt on first launch after the schema change.

## Verifying Index Usage

Use Instruments > Core Data template to verify that queries use indexes. Look for "Full Table Scan" warnings on frequently executed fetches — these indicate a missing index.
