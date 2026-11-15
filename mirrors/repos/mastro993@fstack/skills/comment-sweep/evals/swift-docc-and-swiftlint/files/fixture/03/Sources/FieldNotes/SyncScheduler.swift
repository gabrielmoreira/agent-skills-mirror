#if os(iOS)
import BackgroundTasks
import Foundation
import os

/// Drains a ``SyncQueue`` from a background processing task whenever the system grants network time.
public enum SyncScheduler {
    // The identifier must also be listed under BGTaskSchedulerPermittedIdentifiers in the app's
    // Info.plist, or BGTaskScheduler refuses the registration and the submit.
    // https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler
    public static let taskIdentifier = "com.fieldnotes.sync"

    private static let logger = Logger(subsystem: "com.fieldnotes", category: "sync")

    /// Registers the launch handler for ``taskIdentifier``.
    ///
    /// Call it before `application(_:didFinishLaunchingWithOptions:)` returns: the system raises an
    /// exception for handlers registered after launch.
    ///
    /// - Parameter queue: The queue to drain when the task runs.
    /// - Returns: `false` when the system refused the registration.
    @discardableResult
    public static func register(queue: SyncQueue) -> Bool {
        BGTaskScheduler.shared.register(forTaskWithIdentifier: taskIdentifier, using: nil) { task in
            // swiftlint:disable:next force_cast
            handle(task as! BGProcessingTask, queue: queue)
        }
    }

    /// Asks the system to run the sync task once the device has a network connection, no sooner
    /// than 15 minutes from now. Submitting again replaces the earlier request.
    public static func schedule() {
        let request = BGProcessingTaskRequest(identifier: taskIdentifier)
        request.requiresNetworkConnectivity = true
        request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)
        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            logger.error("Couldn't schedule background sync: \(error.localizedDescription)")
        }
    }

    private static func handle(_ task: BGProcessingTask, queue: SyncQueue) {
        schedule()
        let work = Task {
            await queue.drain()
            let remaining = await queue.pendingCount
            task.setTaskCompleted(success: remaining == 0)
        }
        // cancel the drain when the system expires the task
        task.expirationHandler = {
            work.cancel()
        }
    }
}
#endif
