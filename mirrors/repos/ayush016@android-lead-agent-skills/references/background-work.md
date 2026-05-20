# Background Work — WorkManager, Foreground Services, Alarms

Android aggressively kills background processes to preserve battery. WorkManager is the correct API for the vast majority of background work — it survives process death, device reboots, and Doze mode. Foreground Services are for user-aware, ongoing work. AlarmManager is for exact-time triggers. Using the wrong one causes either killed jobs or battery drain.

---

## WorkManager — Deferrable Background Work

### When to use WorkManager

- Uploading data when connectivity is available
- Syncing data on a schedule
- Processing images (compression, transcoding)
- Sending analytics events in batches
- Any work that must complete even if the app is closed

### Setup

```toml
[libraries]
work-runtime-ktx = { group = "androidx.work", name = "work-runtime-ktx", version = "2.10.0" }
hilt-work = { group = "androidx.hilt", name = "hilt-work", version = "1.2.0" }
```

### Basic Worker with Hilt injection

```kotlin
@HiltWorker
class ArticleSyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted workerParams: WorkerParameters,
    private val articleRepository: ArticleRepository,
    private val notificationHelper: NotificationHelper
) : CoroutineWorker(context, workerParams) {

    override suspend fun doWork(): Result {
        return try {
            // Read input data
            val forceRefresh = inputData.getBoolean(KEY_FORCE_REFRESH, false)

            // Update progress — visible in WorkInfo observers
            setProgress(workDataOf(KEY_PROGRESS to 0))

            val result = articleRepository.refreshArticles(forceRefresh)
            if (result is DomainResult.Success) {
                setProgress(workDataOf(KEY_PROGRESS to 100))
                Result.success(
                    workDataOf(KEY_ARTICLES_SYNCED to result.data.size)
                )
            } else {
                // Retry if transient error; failure if permanent
                if (runAttemptCount < MAX_RETRIES) Result.retry()
                else Result.failure(workDataOf(KEY_ERROR to "Sync failed after $MAX_RETRIES attempts"))
            }
        } catch (e: CancellationException) {
            throw e // always rethrow
        } catch (e: Exception) {
            if (runAttemptCount < MAX_RETRIES) Result.retry()
            else Result.failure()
        }
    }

    companion object {
        const val KEY_FORCE_REFRESH = "force_refresh"
        const val KEY_PROGRESS = "progress"
        const val KEY_ARTICLES_SYNCED = "articles_synced"
        const val KEY_ERROR = "error"
        const val MAX_RETRIES = 3
        const val WORK_NAME = "article_sync"
    }
}
```

### Scheduling strategies

```kotlin
// One-time with constraints
fun scheduleOneTimeSync(workManager: WorkManager, forceRefresh: Boolean = false) {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .setRequiresBatteryNotLow(true)
        .build()

    val request = OneTimeWorkRequestBuilder<ArticleSyncWorker>()
        .setConstraints(constraints)
        .setInputData(workDataOf(ArticleSyncWorker.KEY_FORCE_REFRESH to forceRefresh))
        .setBackoffCriteria(
            BackoffPolicy.EXPONENTIAL,
            WorkRequest.DEFAULT_BACKOFF_DELAY_MILLIS,
            TimeUnit.MILLISECONDS
        )
        .addTag("sync")
        .build()

    // KEEP: if a pending request exists with this name, keep it (don't replace)
    workManager.enqueueUniqueWork(
        ArticleSyncWorker.WORK_NAME,
        ExistingWorkPolicy.KEEP,
        request
    )
}

// Periodic — minimum interval is 15 minutes (OS-enforced)
fun schedulePeriodicSync(workManager: WorkManager) {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build()

    val request = PeriodicWorkRequestBuilder<ArticleSyncWorker>(
        repeatInterval = 1,
        repeatIntervalTimeUnit = TimeUnit.HOURS,
        flexTimeInterval = 15,
        flexTimeIntervalUnit = TimeUnit.MINUTES  // OS may run within this flex window
    )
        .setConstraints(constraints)
        .build()

    workManager.enqueueUniquePeriodicWork(
        ArticleSyncWorker.WORK_NAME,
        ExistingPeriodicWorkPolicy.UPDATE,  // UPDATE replaces with new constraints/params
        request
    )
}
```

### Chaining workers

```kotlin
// Sequential chain: step 1 → step 2 → step 3
workManager
    .beginWith(OneTimeWorkRequestBuilder<DownloadWorker>().build())
    .then(OneTimeWorkRequestBuilder<ProcessWorker>().build())
    .then(OneTimeWorkRequestBuilder<UploadWorker>().build())
    .enqueue()

// Parallel then merge
val download1 = OneTimeWorkRequestBuilder<DownloadWorker>().build()
val download2 = OneTimeWorkRequestBuilder<DownloadWorker>().build()
val merge = OneTimeWorkRequestBuilder<MergeWorker>().build()

workManager
    .beginWith(listOf(download1, download2))
    .then(merge)
    .enqueue()
```

### Observing work status

```kotlin
// In ViewModel
val syncState: StateFlow<SyncState> = workManager
    .getWorkInfosForUniqueWorkFlow(ArticleSyncWorker.WORK_NAME)
    .map { workInfoList ->
        val workInfo = workInfoList.firstOrNull()
        when (workInfo?.state) {
            WorkInfo.State.ENQUEUED, WorkInfo.State.BLOCKED -> SyncState.Pending
            WorkInfo.State.RUNNING -> {
                val progress = workInfo.progress.getInt(ArticleSyncWorker.KEY_PROGRESS, 0)
                SyncState.Running(progress)
            }
            WorkInfo.State.SUCCEEDED -> {
                val count = workInfo.outputData.getInt(ArticleSyncWorker.KEY_ARTICLES_SYNCED, 0)
                SyncState.Succeeded(count)
            }
            WorkInfo.State.FAILED -> SyncState.Failed(
                workInfo.outputData.getString(ArticleSyncWorker.KEY_ERROR) ?: "Unknown error"
            )
            WorkInfo.State.CANCELLED -> SyncState.Cancelled
            null -> SyncState.Idle
        }
    }
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), SyncState.Idle)
```

### Expedited workers (Android 12+)

For high-priority, user-initiated work that should start immediately:

```kotlin
val expeditedRequest = OneTimeWorkRequestBuilder<SendMessageWorker>()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()

workManager.enqueue(expeditedRequest)

// The worker must override getForegroundInfo for pre-Android 12 compatibility
@HiltWorker
class SendMessageWorker @AssistedInject constructor(...) : CoroutineWorker(...) {
    override suspend fun getForegroundInfo(): ForegroundInfo {
        return ForegroundInfo(
            NOTIFICATION_ID,
            NotificationCompat.Builder(applicationContext, CHANNEL_ID)
                .setContentTitle("Sending message...")
                .setSmallIcon(R.drawable.ic_send)
                .build()
        )
    }

    override suspend fun doWork(): Result { ... }
}
```

---

## Foreground Services

Use foreground services for work the user is actively aware of: music playback, navigation, downloads in progress, location tracking.

**Android 14 requirement**: Declare the specific foreground service type.

```xml
<!-- AndroidManifest.xml -->
<service
    android:name=".service.MusicPlaybackService"
    android:foregroundServiceType="mediaPlayback"
    android:exported="false" />

<service
    android:name=".service.LocationTrackingService"
    android:foregroundServiceType="location"
    android:exported="false" />

<!-- Required permissions by type -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
```

### Foreground Service with notification

```kotlin
class DownloadForegroundService : Service() {

    private val notificationManager by lazy {
        getSystemService(NotificationManager::class.java)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val downloadUrl = intent?.getStringExtra(EXTRA_URL) ?: return START_NOT_STICKY

        createNotificationChannel()

        val notification = buildProgressNotification(progress = 0)
        startForeground(NOTIFICATION_ID, notification)

        CoroutineScope(Dispatchers.IO + Job()).launch {
            try {
                downloadFile(downloadUrl) { progress ->
                    notificationManager.notify(
                        NOTIFICATION_ID,
                        buildProgressNotification(progress)
                    )
                }
                showCompletionNotification()
            } finally {
                stopSelf()
            }
        }

        return START_NOT_STICKY
    }

    private fun buildProgressNotification(progress: Int) =
        NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Downloading...")
            .setProgress(100, progress, progress == 0)
            .setSmallIcon(R.drawable.ic_download)
            .setOngoing(true)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
            .build()

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "Downloads",
            NotificationManager.IMPORTANCE_LOW
        ).apply { setShowBadge(false) }
        notificationManager.createNotificationChannel(channel)
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        const val EXTRA_URL = "url"
        const val CHANNEL_ID = "downloads"
        const val NOTIFICATION_ID = 1001
    }
}
```

---

## AlarmManager — Exact Time Triggers

Use only when the user explicitly needs something at a precise time (calendar reminder, timer alarm). Inexact alarms are preferred for everything else.

```kotlin
// Exact alarm (requires SCHEDULE_EXACT_ALARM permission on Android 12+)
class AlarmScheduler @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val alarmManager = context.getSystemService(AlarmManager::class.java)

    fun scheduleReminder(reminderTimeMs: Long, reminderId: Int, message: String) {
        // Check permission on Android 12+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (!alarmManager.canScheduleExactAlarms()) {
                // Direct user to settings
                context.startActivity(
                    Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM)
                )
                return
            }
        }

        val intent = Intent(context, ReminderReceiver::class.java).apply {
            putExtra(ReminderReceiver.EXTRA_ID, reminderId)
            putExtra(ReminderReceiver.EXTRA_MESSAGE, message)
        }

        val pendingIntent = PendingIntent.getBroadcast(
            context,
            reminderId,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        alarmManager.setExactAndAllowWhileIdle(
            AlarmManager.RTC_WAKEUP,
            reminderTimeMs,
            pendingIntent
        )
    }

    fun cancelReminder(reminderId: Int) {
        val intent = Intent(context, ReminderReceiver::class.java)
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            reminderId,
            intent,
            PendingIntent.FLAG_NO_CREATE or PendingIntent.FLAG_IMMUTABLE
        ) ?: return
        alarmManager.cancel(pendingIntent)
    }
}

// BroadcastReceiver triggered by alarm
class ReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val reminderId = intent.getIntExtra(EXTRA_ID, -1)
        val message = intent.getStringExtra(EXTRA_MESSAGE) ?: return
        // Show notification
        NotificationHelper.showReminder(context, reminderId, message)
    }

    companion object {
        const val EXTRA_ID = "reminder_id"
        const val EXTRA_MESSAGE = "message"
    }
}
```

### Reschedule alarms after reboot

```kotlin
// Manifest
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

<receiver
    android:name=".receiver.BootReceiver"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>

// BroadcastReceiver
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // Re-schedule all saved alarms from database
            val goAsync = goAsync()
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    // Load saved reminders from Room and reschedule
                    val reminderRepository = // inject via EntryPoint
                    reminderRepository.getAllPendingReminders().forEach { reminder ->
                        AlarmScheduler(context).scheduleReminder(
                            reminder.triggerTimeMs,
                            reminder.id,
                            reminder.message
                        )
                    }
                } finally {
                    goAsync.finish()
                }
            }
        }
    }
}
```
