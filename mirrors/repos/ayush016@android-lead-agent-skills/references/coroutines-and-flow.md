# Coroutines & Flow — Structured Concurrency, Dispatchers, Operators

Coroutines are not just "async/await with nicer syntax." They are a structured concurrency model: every coroutine has a parent, a lifetime is bounded by its scope, and cancellation propagates automatically. Flow is the observable, backpressure-aware stream built on coroutines. Understanding both deeply is required to write Android code that handles cancellation, rotation, process death, and lifecycle correctly.

---

## Structured Concurrency

Every coroutine must be launched inside a scope. The scope defines the lifetime:

| Scope | Lifetime | Use for |
|-------|---------|---------|
| `viewModelScope` | ViewModel alive | ViewModel business logic, data loading |
| `lifecycleScope` | Activity/Fragment alive | UI-tied work, collecting flows in composables |
| `rememberCoroutineScope()` | Composable in composition | User-triggered one-shot actions from composables |
| `applicationScope` (custom) | App process alive | App-wide background work, analytics |
| `viewModelScope + SupervisorJob` | Independent failure | Parallel operations that shouldn't cancel siblings |

```kotlin
// Custom application scope — survives ViewModel death
@Singleton
class ApplicationScope @Inject constructor() {
    val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
}
```

### SupervisorJob — isolate sibling failures

```kotlin
// Without SupervisorJob: if one child fails, all siblings cancel
viewModelScope.launch {
    launch { loadUserProfile() }  // if this throws, next line cancels too
    launch { loadFeedItems() }
}

// With SupervisorScope: siblings are independent
viewModelScope.launch {
    supervisorScope {
        launch { loadUserProfile() }   // failure here does NOT cancel sibling
        launch { loadFeedItems() }
    }
}
```

---

## Dispatcher Selection

Never hardcode dispatchers in production code — inject them for testability.

```kotlin
// core/coroutines/src/main/kotlin/.../AppDispatchers.kt
data class AppDispatchers(
    val main: CoroutineDispatcher = Dispatchers.Main,
    val io: CoroutineDispatcher = Dispatchers.IO,
    val default: CoroutineDispatcher = Dispatchers.Default,
    val unconfined: CoroutineDispatcher = Dispatchers.Unconfined
)

// DI binding
@Module @InstallIn(SingletonComponent::class)
object DispatchersModule {
    @Provides @Singleton
    fun provideDispatchers() = AppDispatchers()
}

// Usage in Repository
class ArticleRepositoryImpl @Inject constructor(
    private val api: ArticleApi,
    private val dao: ArticleDao,
    private val dispatchers: AppDispatchers
) : ArticleRepository {

    override suspend fun refreshArticles() {
        withContext(dispatchers.io) {
            val response = api.getArticles()
            dao.upsertAll(response.map(ArticleDto::toEntity))
        }
    }
}

// Usage in test
val testDispatchers = AppDispatchers(
    main = StandardTestDispatcher(),
    io = StandardTestDispatcher(),
    default = StandardTestDispatcher()
)
```

### Which dispatcher for what work

| Work type | Dispatcher | Reason |
|-----------|------------|--------|
| UI updates | `Main` | Only main thread can touch UI |
| Network calls | `IO` | Blocking I/O; thread pool sized for it |
| Database reads/writes | `IO` | Blocking I/O |
| CPU-intensive computation | `Default` | Thread pool sized for CPU count |
| JSON parsing (large) | `Default` | CPU-bound |
| File reads (small) | `IO` | Blocking I/O |
| Everything with `suspend` Retrofit | No context switch needed | Retrofit suspends, doesn't block |

---

## Flow — Operators That Matter

### collect vs collectLatest

```kotlin
// collect: processes every emission, even if next arrives before done
viewModelScope.launch {
    searchQueryFlow.collect { query ->
        delay(500) // if new query arrives mid-delay, this runs again after
        search(query)
    }
}

// collectLatest: cancels in-flight processing when next emission arrives
// USE THIS for search, type-ahead, anything where only latest result matters
viewModelScope.launch {
    searchQueryFlow.collectLatest { query ->
        delay(500)  // cancelled if new query arrives before delay completes
        search(query)  // only runs for the latest query
    }
}
```

### flatMapLatest vs flatMapMerge vs flatMapConcat

```kotlin
// flatMapLatest — cancel previous inner flow when new outer emission arrives
// USE FOR: search, paginated loading where only current page matters
val results: Flow<List<Result>> = searchQuery
    .debounce(300)
    .filter { it.length >= 2 }
    .flatMapLatest { query ->
        repository.search(query)  // previous search cancelled on new query
    }

// flatMapMerge — run all inner flows concurrently, merge results
// USE FOR: parallel data fetching where all results matter
val allData: Flow<DataItem> = itemIds
    .flatMapMerge(concurrency = 4) { id ->
        repository.fetchItem(id)
    }

// flatMapConcat — run inner flows sequentially, one after another
// USE FOR: ordered operations where sequence matters
val processedItems = itemQueue.flatMapConcat { item ->
    processItem(item)
}
```

### combine vs zip

```kotlin
// combine: emit when ANY upstream emits; uses latest value from others
val uiState: Flow<ProfileUiState> = combine(
    userRepository.observeUser(userId),
    settingsRepository.observeSettings()
) { user, settings ->
    ProfileUiState.Ready(user, settings.theme)
}

// zip: pair emissions one-to-one; waits for both to emit before producing
val pairs: Flow<Pair<User, Post>> = zip(
    userFlow,
    postFlow
) { user, post -> user to post }
```

### stateIn — convert cold flow to hot StateFlow

```kotlin
// In ViewModel — make a cold repository flow into a StateFlow the UI can observe
val articles: StateFlow<ArticleUiState> = repository
    .observeArticles()
    .map { result ->
        when (result) {
            is DomainResult.Success -> ArticleUiState.Ready(result.data)
            is DomainResult.Failure -> ArticleUiState.Error(result.error.message)
        }
    }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000),
        initialValue = ArticleUiState.Loading
    )
```

`SharingStarted.WhileSubscribed(5_000)`: upstream collection starts when first subscriber appears; stops 5 seconds after last subscriber disappears (handles configuration changes gracefully).

### shareIn — hot SharedFlow for one-to-many

```kotlin
// Multicast an expensive upstream flow to multiple collectors
val sharedLocationUpdates: SharedFlow<Location> = locationRepository
    .observeLocation()
    .shareIn(
        scope = applicationScope,
        started = SharingStarted.WhileSubscribed(),
        replay = 1  // new collectors immediately get the last location
    )
```

---

## Flow Error Handling

```kotlin
// catch: handle errors in the flow pipeline
repository.observeArticles()
    .catch { throwable ->
        emit(DomainResult.Failure(mapError(throwable)))
    }
    .collect { result -> ... }

// retry with exponential backoff
repository.observeArticles()
    .retryWhen { cause, attempt ->
        if (cause is IOException && attempt < 3) {
            delay(2.0.pow(attempt.toInt()).toLong() * 1000)
            true
        } else {
            false
        }
    }
    .collect { ... }

// onEach for side effects (logging, analytics) without breaking the chain
repository.observeArticles()
    .onEach { result -> analytics.track("articles_loaded", mapOf("count" to result.size)) }
    .catch { Timber.e(it, "Failed to load articles") }
    .collect { ... }
```

---

## Collecting in Compose

### collectAsStateWithLifecycle (always prefer over collectAsState)

```kotlin
// collectAsState: collects even when app is in background — wastes battery, causes issues
val uiState by viewModel.uiState.collectAsState() // BAD

// collectAsStateWithLifecycle: suspends collection when lifecycle drops below STARTED
val uiState by viewModel.uiState.collectAsStateWithLifecycle() // GOOD
```

### One-time events (SharedFlow) in composables

```kotlin
LaunchedEffect(viewModel) {
    viewModel.events
        .flowWithLifecycle(lifecycle, Lifecycle.State.STARTED)
        .collect { event ->
            when (event) {
                is UiEvent.NavigateTo -> navController.navigate(event.route)
                is UiEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
            }
        }
}
```

---

## Cancellation and Cleanup

### CancellationException is not a failure

```kotlin
// WRONG — catching CancellationException prevents coroutine from cancelling
try {
    doWork()
} catch (e: Exception) { // catches CancellationException!
    handleError(e)
}

// CORRECT — always rethrow CancellationException
try {
    doWork()
} catch (e: CancellationException) {
    throw e  // must rethrow
} catch (e: Exception) {
    handleError(e)
}

// SIMPLEST — catch only specific exceptions
try {
    doWork()
} catch (e: IOException) {
    handleNetworkError(e)
}
```

### withContext is cancellation-safe

```kotlin
// withContext properly handles cancellation and restores context after
suspend fun processData(data: ByteArray): Result {
    return withContext(Dispatchers.Default) {
        // CPU work; if coroutine is cancelled here, withContext propagates it
        heavyComputation(data)
    }
}
```

### ensureActive — check cancellation in loops

```kotlin
suspend fun processItems(items: List<Item>) {
    for (item in items) {
        ensureActive()  // throws CancellationException if coroutine is cancelled
        processItem(item)
    }
}
```

---

## Flow Testing with Turbine

```kotlin
// build.gradle.kts
testImplementation(libs.turbine)  // "app.cash.turbine:turbine:1.2.0"

@Test
fun `search flow emits results after debounce`() = runTest {
    val viewModel = SearchViewModel(fakeRepository)

    viewModel.searchResults.test {
        // Initial emission
        assertThat(awaitItem()).isEqualTo(SearchUiState.Idle)

        // Simulate typing
        viewModel.onSearchQueryChanged("kotlin")
        testScheduler.advanceTimeBy(350) // advance past 300ms debounce

        // Assert results arrived
        val resultState = awaitItem()
        assertThat(resultState).isInstanceOf(SearchUiState.Results::class.java)

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `error state emitted on network failure`() = runTest {
    fakeRepository.setError(DomainError.NetworkUnavailable)
    val viewModel = ArticleViewModel(fakeRepository)

    viewModel.uiState.test {
        assertThat(awaitItem()).isEqualTo(ArticleUiState.Loading)
        advanceUntilIdle()
        assertThat(awaitItem()).isInstanceOf(ArticleUiState.Error::class.java)
        cancelAndIgnoreRemainingEvents()
    }
}
```

---

## Channels — when Flow isn't right

Use `Channel` for producer-consumer patterns where backpressure or buffering is needed, or when one event must be delivered to exactly one consumer:

```kotlin
// Work queue pattern — items produced faster than consumed
class TaskQueue @Inject constructor() {
    private val channel = Channel<Task>(capacity = Channel.UNLIMITED)
    val tasks: ReceiveChannel<Task> = channel

    suspend fun enqueue(task: Task) = channel.send(task)
}

// Exactly-once event delivery (not replay-able like SharedFlow)
class EventBus {
    private val channel = Channel<AppEvent>(capacity = Channel.BUFFERED)

    suspend fun send(event: AppEvent) = channel.send(event)
    suspend fun receive(): AppEvent = channel.receive()
    fun tryReceive(): AppEvent? = channel.tryReceive().getOrNull()
}
```

---

## Common Anti-Patterns

```kotlin
// GlobalScope — never use; not structured, survives app death
GlobalScope.launch { ... } // BAD

// runBlocking on main thread — blocks UI
runBlocking { fetchData() } // BAD on main thread

// Launching coroutines in composables without remember
@Composable
fun MyScreen() {
    val scope = rememberCoroutineScope()
    // GOOD — scope tied to composition lifetime
    Button(onClick = { scope.launch { doSomething() } }) { Text("Go") }
}

// Collecting Flow from a composable without lifecycle awareness
@Composable
fun MyScreen(viewModel: MyViewModel) {
    // BAD — collects in background, wastes battery
    val state = viewModel.state.collectAsState()

    // GOOD — suspends when app goes to background
    val state = viewModel.state.collectAsStateWithLifecycle()
}
```
