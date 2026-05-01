# HealthKit Extended Patterns

Overflow reference for the `healthkit` skill. Contains advanced patterns that exceed the main skill file's scope.

## Contents

- [Workout Session Lifecycle](#workout-session-lifecycle)
- [Anchored Object Queries](#anchored-object-queries)
- [Predicate-Based Filtering](#predicate-based-filtering)
- [Statistics Collection for Charts](#statistics-collection-for-charts)
- [HealthKit + SwiftUI Integration](#healthkit--swiftui-integration)
- [Characteristic Types](#characteristic-types)

## Workout Session Lifecycle

### Full Workout Manager

```swift
import HealthKit

@Observable
@MainActor
final class WorkoutManager: NSObject {
    let healthStore = HKHealthStore()

    private var session: HKWorkoutSession?
    private var builder: HKLiveWorkoutBuilder?

    var heartRate: Double = 0
    var activeCalories: Double = 0
    var distance: Double = 0
    var elapsedTime: TimeInterval = 0
    var isActive = false

    func startWorkout(activityType: HKWorkoutActivityType) async throws {
        let configuration = HKWorkoutConfiguration()
        configuration.activityType = activityType
        configuration.locationType = .outdoor

        let session = try HKWorkoutSession(
            healthStore: healthStore,
            configuration: configuration
        )
        let builder = session.associatedWorkoutBuilder()

        builder.dataSource = HKLiveWorkoutDataSource(
            healthStore: healthStore,
            workoutConfiguration: configuration
        )

        session.delegate = self
        builder.delegate = self

        self.session = session
        self.builder = builder

        session.startActivity(with: Date())
        try await builder.beginCollection(at: Date())
        isActive = true
    }

    func pause() {
        session?.pause()
    }

    func resume() {
        session?.resume()
    }

    func end() async throws {
        guard let session, let builder else { return }
        session.end()
        try await builder.endCollection(at: Date())
        try await builder.finishWorkout()
        isActive = false
        self.session = nil
        self.builder = nil
    }
}

// MARK: - HKWorkoutSessionDelegate

extension WorkoutManager: HKWorkoutSessionDelegate {
    nonisolated func workoutSession(
        _ workoutSession: HKWorkoutSession,
        didChangeTo toState: HKWorkoutSessionState,
        from fromState: HKWorkoutSessionState,
        date: Date
    ) {
        Task { @MainActor in
            switch toState {
            case .running:
                isActive = true
            case .paused:
                isActive = false
            case .ended, .stopped:
                isActive = false
            default:
                break
            }
        }
    }

    nonisolated func workoutSession(
        _ workoutSession: HKWorkoutSession,
        didFailWithError error: Error
    ) {
        Task { @MainActor in
            print("Workout session failed: \(error)")
            isActive = false
        }
    }
}

// MARK: - HKLiveWorkoutBuilderDelegate

extension WorkoutManager: HKLiveWorkoutBuilderDelegate {
    nonisolated func workoutBuilderDidCollectEvent(
        _ workoutBuilder: HKLiveWorkoutBuilder
    ) {
        // Handle workout events (pause, resume, lap, etc.)
    }

    nonisolated func workoutBuilder(
        _ workoutBuilder: HKLiveWorkoutBuilder,
        didCollectDataOf collectedTypes: Set<HKSampleType>
    ) {
        Task { @MainActor in
            for type in collectedTypes {
                guard let quantityType = type as? HKQuantityType else { continue }

                let statistics = workoutBuilder.statistics(for: quantityType)

                switch quantityType {
                case HKQuantityType(.heartRate):
                    heartRate = statistics?.mostRecentQuantity()?
                        .doubleValue(for: HKUnit.count().unitDivided(by: .minute())) ?? 0

                case HKQuantityType(.activeEnergyBurned):
                    activeCalories = statistics?.sumQuantity()?
                        .doubleValue(for: .kilocalorie()) ?? 0

                case HKQuantityType(.distanceWalkingRunning):
                    distance = statistics?.sumQuantity()?
                        .doubleValue(for: .meter()) ?? 0

                default:
                    break
                }
            }

            elapsedTime = workoutBuilder.elapsedTime
        }
    }
}
```

### Multi-Device Mirroring (watchOS + iOS)

```swift
// On watchOS: start mirroring to companion iPhone
func startMirroring() async throws {
    try await session?.startMirroringToCompanionDevice()
}

// On iOS: receive the mirrored session
func setupMirroredSessionHandler() {
    healthStore.workoutSessionMirroringStartHandler = { mirroredSession in
        // mirroredSession is an HKWorkoutSession with type == .mirrored
        mirroredSession.delegate = self
        let builder = mirroredSession.associatedWorkoutBuilder()
        builder.delegate = self
    }
}

// Send data between devices
func sendDataToRemote(_ data: Data) async throws {
    try await session?.sendToRemoteWorkoutSession(data: data)
}
```

## Anchored Object Queries

Use `HKAnchoredObjectQuery` for incremental updates -- only fetches samples added or deleted since the last anchor.

```swift
@Observable
final class StepTracker {
    private let healthStore = HKHealthStore()
    private var anchor: HKQueryAnchor?
    private var observerQuery: HKObserverQuery?

    var totalSteps: Double = 0

    func startMonitoring() {
        let stepType = HKQuantityType(.stepCount)

        // Initial fetch + ongoing updates
        let anchoredQuery = HKAnchoredObjectQuery(
            type: stepType,
            predicate: nil,
            anchor: anchor,
            limit: HKObjectQueryNoLimit
        ) { [weak self] query, added, deleted, newAnchor, error in
            guard let self else { return }
            self.anchor = newAnchor
            self.processNewSamples(added ?? [])
        }

        // Enable updates handler for real-time monitoring
        anchoredQuery.updateHandler = { [weak self] query, added, deleted, newAnchor, error in
            guard let self else { return }
            self.anchor = newAnchor
            self.processNewSamples(added ?? [])
        }

        healthStore.execute(anchoredQuery)
    }

    private func processNewSamples(_ samples: [HKSample]) {
        for sample in samples {
            guard let quantitySample = sample as? HKQuantitySample else { continue }
            let steps = quantitySample.quantity.doubleValue(for: .count())
            totalSteps += steps
        }
    }
}
```

### Anchored Query with Async Descriptor

```swift
import HealthKit

let stepType = HKQuantityType(.stepCount)
let descriptor = HKAnchoredObjectQueryDescriptor(
    predicates: [.quantitySample(type: stepType)],
    anchor: savedAnchor
)

// One-shot
let result = try await descriptor.result(for: healthStore)
let newSamples = result.addedSamples
let deletedObjects = result.deletedObjects
let newAnchor = result.newAnchor

// Long-running with updates
for try await result in descriptor.results(for: healthStore) {
    // Process result.addedSamples and result.deletedObjects
}
```

## Predicate-Based Filtering

### Time-Based Predicates

```swift
// Samples from today
let today = Calendar.current.startOfDay(for: Date())
let tomorrow = Calendar.current.date(byAdding: .day, value: 1, to: today)!
let todayPredicate = HKQuery.predicateForSamples(
    withStart: today, end: tomorrow
)

// Samples from the last 7 days
let oneWeekAgo = Calendar.current.date(byAdding: .day, value: -7, to: Date())!
let weekPredicate = HKQuery.predicateForSamples(
    withStart: oneWeekAgo, end: Date()
)

// Strict: sample must be entirely within the range
let strictPredicate = HKQuery.predicateForSamples(
    withStart: today, end: tomorrow,
    options: .strictStartDate
)
```

### Source-Based Predicates

```swift
// Only samples from the current app
let sourcePredicate = HKQuery.predicateForObjects(
    from: HKSource.default()
)

// Only samples from Apple Watch
let devicePredicate = HKQuery.predicateForObjects(
    withDeviceProperty: HKDevicePropertyKeyModel,
    allowedValues: ["Watch"]
)
```

### Compound Predicates

```swift
let todayFromWatch = NSCompoundPredicate(
    andPredicateWithSubpredicates: [todayPredicate, devicePredicate]
)

let descriptor = HKSampleQueryDescriptor(
    predicates: [.quantitySample(type: stepType, predicate: todayFromWatch)],
    sortDescriptors: [SortDescriptor(\.endDate, order: .reverse)]
)
```

## Statistics Collection for Charts

### Weekly Step Count Chart Data

```swift
struct DailyStepData: Identifiable {
    let id = UUID()
    let date: Date
    let steps: Double
}

func fetchWeeklyStepData() async throws -> [DailyStepData] {
    let calendar = Calendar.current
    let today = calendar.startOfDay(for: Date())
    let endDate = calendar.date(byAdding: .day, value: 1, to: today)!
    let startDate = calendar.date(byAdding: .day, value: -7, to: endDate)!

    let stepType = HKQuantityType(.stepCount)
    let predicate = HKQuery.predicateForSamples(
        withStart: startDate, end: endDate
    )
    let samplePredicate = HKSamplePredicate.quantitySample(
        type: stepType, predicate: predicate
    )

    let query = HKStatisticsCollectionQueryDescriptor(
        predicate: samplePredicate,
        options: .cumulativeSum,
        anchorDate: endDate,
        intervalComponents: DateComponents(day: 1)
    )

    let collection = try await query.result(for: healthStore)

    var data: [DailyStepData] = []
    collection.statisticsCollection.enumerateStatistics(
        from: startDate, to: endDate
    ) { statistics, _ in
        let steps = statistics.sumQuantity()?
            .doubleValue(for: .count()) ?? 0
        data.append(DailyStepData(date: statistics.startDate, steps: steps))
    }

    return data
}
```

### Hourly Heart Rate Averages

```swift
func fetchHourlyHeartRate(for date: Date) async throws -> [(hour: Date, bpm: Double)] {
    let calendar = Calendar.current
    let startOfDay = calendar.startOfDay(for: date)
    let endOfDay = calendar.date(byAdding: .day, value: 1, to: startOfDay)!

    let heartRateType = HKQuantityType(.heartRate)
    let predicate = HKQuery.predicateForSamples(
        withStart: startOfDay, end: endOfDay
    )
    let samplePredicate = HKSamplePredicate.quantitySample(
        type: heartRateType, predicate: predicate
    )

    let query = HKStatisticsCollectionQueryDescriptor(
        predicate: samplePredicate,
        options: .discreteAverage,
        anchorDate: endOfDay,
        intervalComponents: DateComponents(hour: 1)
    )

    let collection = try await query.result(for: healthStore)
    let unit = HKUnit.count().unitDivided(by: .minute())

    var hourlyData: [(hour: Date, bpm: Double)] = []
    collection.statisticsCollection.enumerateStatistics(
        from: startOfDay, to: endOfDay
    ) { statistics, _ in
        if let avg = statistics.averageQuantity()?.doubleValue(for: unit) {
            hourlyData.append((hour: statistics.startDate, bpm: avg))
        }
    }

    return hourlyData
}
```

## HealthKit + SwiftUI Integration

### HealthKit Manager with @Observable

```swift
import HealthKit
import SwiftUI

@Observable
@MainActor
final class HealthManager {
    let healthStore = HKHealthStore()

    var isAuthorized = false
    var todaySteps: Double = 0
    var recentHeartRate: Double = 0

    var isAvailable: Bool {
        HKHealthStore.isHealthDataAvailable()
    }

    func requestAuthorization() async throws {
        let typesToRead: Set<HKObjectType> = [
            HKQuantityType(.stepCount),
            HKQuantityType(.heartRate)
        ]

        try await healthStore.requestAuthorization(
            toShare: [],
            read: typesToRead
        )
        isAuthorized = true
    }

    func refreshData() async {
        async let steps = fetchTodaySteps()
        async let heartRate = fetchLatestHeartRate()

        todaySteps = (try? await steps) ?? 0
        recentHeartRate = (try? await heartRate) ?? 0
    }

    private func fetchTodaySteps() async throws -> Double {
        let calendar = Calendar.current
        let startOfDay = calendar.startOfDay(for: Date())
        let predicate = HKQuery.predicateForSamples(
            withStart: startOfDay, end: Date()
        )
        let stepType = HKQuantityType(.stepCount)
        let samplePredicate = HKSamplePredicate.quantitySample(
            type: stepType, predicate: predicate
        )
        let query = HKStatisticsQueryDescriptor(
            predicate: samplePredicate, options: .cumulativeSum
        )
        return try await query.result(for: healthStore)?
            .sumQuantity()?.doubleValue(for: .count()) ?? 0
    }

    private func fetchLatestHeartRate() async throws -> Double {
        let heartRateType = HKQuantityType(.heartRate)
        let descriptor = HKSampleQueryDescriptor(
            predicates: [.quantitySample(type: heartRateType)],
            sortDescriptors: [SortDescriptor(\.endDate, order: .reverse)],
            limit: 1
        )
        let results = try await descriptor.result(for: healthStore)
        let unit = HKUnit.count().unitDivided(by: .minute())
        return results.first?.quantity.doubleValue(for: unit) ?? 0
    }
}
```

### SwiftUI View with HealthKit

```swift
struct HealthDashboardView: View {
    @Environment(HealthManager.self) private var healthManager

    var body: some View {
        NavigationStack {
            Group {
                if !healthManager.isAvailable {
                    ContentUnavailableView(
                        "HealthKit Unavailable",
                        systemImage: "heart.slash",
                        description: Text("This device does not support HealthKit.")
                    )
                } else if !healthManager.isAuthorized {
                    authorizationPrompt
                } else {
                    healthDataView
                }
            }
            .navigationTitle("Health")
        }
    }

    private var authorizationPrompt: some View {
        ContentUnavailableView {
            Label("Health Access", systemImage: "heart.text.square")
        } description: {
            Text("Grant access to view your health data.")
        } actions: {
            Button("Authorize") {
                Task {
                    try? await healthManager.requestAuthorization()
                }
            }
            .buttonStyle(.borderedProminent)
        }
    }

    private var healthDataView: some View {
        List {
            Section("Today") {
                LabeledContent("Steps") {
                    Text(healthManager.todaySteps, format: .number.precision(.fractionLength(0)))
                }
                LabeledContent("Heart Rate") {
                    Text("\(Int(healthManager.recentHeartRate)) bpm")
                }
            }
        }
        .task {
            await healthManager.refreshData()
        }
        .refreshable {
            await healthManager.refreshData()
        }
    }
}
```

### App Entry Point Wiring

```swift
@main
struct MyHealthApp: App {
    @State private var healthManager = HealthManager()

    var body: some Scene {
        WindowGroup {
            HealthDashboardView()
                .environment(healthManager)
        }
    }
}
```

## Characteristic Types

Characteristic types are read-only values set by the user in the Health app. They do not require sample queries.

```swift
func readCharacteristics() throws {
    // Date of birth
    let dobComponents = try healthStore.dateOfBirthComponents()
    let calendar = Calendar.current
    if let dob = calendar.date(from: dobComponents) {
        let age = calendar.dateComponents([.year], from: dob, to: Date()).year ?? 0
        print("Age: \(age)")
    }

    // Biological sex
    let biologicalSex = try healthStore.biologicalSex().biologicalSex
    switch biologicalSex {
    case .female: print("Female")
    case .male: print("Male")
    case .other: print("Other")
    case .notSet: print("Not set")
    @unknown default: break
    }

    // Blood type
    let bloodType = try healthStore.bloodType().bloodType
    switch bloodType {
    case .aPositive: print("A+")
    case .aNegative: print("A-")
    case .bPositive: print("B+")
    case .bNegative: print("B-")
    case .abPositive: print("AB+")
    case .abNegative: print("AB-")
    case .oPositive: print("O+")
    case .oNegative: print("O-")
    case .notSet: print("Not set")
    @unknown default: break
    }

    // Fitzpatrick skin type
    let skinType = try healthStore.fitzpatrickSkinType().skinType
    print("Skin type: \(skinType.rawValue)")

    // Wheelchair use
    let wheelchair = try healthStore.wheelchairUse().wheelchairUse
    print("Wheelchair: \(wheelchair == .yes)")
}
```

**Important:** These throw an error if the value is not set, so always use `try` and handle the `HKError.errorNoData` case.

```swift
do {
    let dob = try healthStore.dateOfBirthComponents()
    // Use dob
} catch let error as HKError where error.code == .errorNoData {
    // User hasn't set date of birth in Health app
} catch {
    // Other error
}
```
