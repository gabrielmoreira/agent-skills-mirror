# Testing — Strategy, Screenshot Tests & Fakes

## Testing Pyramid

```
                    ▲
                   / \
                  / E2E\           UIAutomator / Espresso
                 /-------\
                / UI Tests \       Compose Test Rule, Roborazzi
               /-------------\
              /  Integration   \   Room in-memory, Fake repositories
             /-----------------\
            /    Unit Tests      \  ViewModel, UseCase, Repository (with fakes)
           /---------------------\
```

- **Unit tests** (70%): Fast, JVM-only. Test ViewModels with fake repositories, use cases with fake data sources, mappers, utils.
- **Integration tests** (20%): Test Room DAOs against in-memory database, Retrofit with MockWebServer. JVM-only where possible.
- **Screenshot tests** (8%): Roborazzi on JVM. Capture composables in all theme variants and verify no regression.
- **E2E tests** (2%): UIAutomator or Espresso for the critical happy path only. Slow; run in CI against a real emulator.

---

## ViewModel Unit Testing

```kotlin
class ArticleViewModelTest {

    @get:Rule val mainDispatcherRule = MainDispatcherRule()

    private val fakeRepository = FakeArticleRepository()
    private lateinit var viewModel: ArticleViewModel

    @Before
    fun setUp() {
        viewModel = ArticleViewModel(
            getArticlesUseCase = GetArticlesUseCase(fakeRepository),
            likeArticleUseCase = LikeArticleUseCase(fakeRepository)
        )
    }

    @Test
    fun `loading state emitted on start`() = runTest {
        val states = mutableListOf<ArticleUiState>()
        val job = launch { viewModel.uiState.toList(states) }

        advanceUntilIdle()
        assertThat(states.first()).isEqualTo(ArticleUiState.Loading)
        job.cancel()
    }

    @Test
    fun `ready state emitted after successful load`() = runTest {
        fakeRepository.setArticles(listOf(ArticleFactory.create()))
        viewModel.onAction(ArticleAction.RefreshFeed)

        advanceUntilIdle()
        assertThat(viewModel.uiState.value).isInstanceOf(ArticleUiState.Ready::class.java)
    }

    @Test
    fun `error state emitted on network failure`() = runTest {
        fakeRepository.setError(DomainError.NetworkUnavailable)
        viewModel.onAction(ArticleAction.RefreshFeed)

        advanceUntilIdle()
        assertThat(viewModel.uiState.value).isInstanceOf(ArticleUiState.Error::class.java)
    }
}

// Dispatcher rule for replacing Main dispatcher in unit tests
class MainDispatcherRule(
    private val dispatcher: TestCoroutineDispatcher = TestCoroutineDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }
    override fun finished(description: Description) {
        Dispatchers.resetMain()
        dispatcher.cleanupTestCoroutines()
    }
}
```

---

## Fake Implementations

Fakes are real implementations that operate in memory. They are superior to mocks because they exercise the same contract as production code and naturally surface interface design issues.

```kotlin
// core/testing/src/main/kotlin/.../fake/FakeArticleRepository.kt
class FakeArticleRepository : ArticleRepository {

    private val articlesFlow = MutableStateFlow<List<Article>>(emptyList())
    private var error: DomainError? = null

    fun setArticles(articles: List<Article>) {
        error = null
        articlesFlow.value = articles
    }

    fun setError(domainError: DomainError) {
        error = domainError
    }

    override fun observeArticles(): Flow<DomainResult<List<Article>>> = flow {
        error?.let { emit(DomainResult.Failure(it)); return@flow }
        articlesFlow.collect { emit(DomainResult.Success(it)) }
    }

    override fun observeArticle(id: Long): Flow<DomainResult<Article>> = flow {
        articlesFlow.collect { articles ->
            val article = articles.find { it.id == id }
            if (article != null) emit(DomainResult.Success(article))
            else emit(DomainResult.Failure(DomainError.NotFound))
        }
    }

    override suspend fun likeArticle(id: Long): DomainResult<Unit> {
        error?.let { return DomainResult.Failure(it) }
        articlesFlow.update { articles -> articles.map { if (it.id == id) it.copy(isLiked = true) else it } }
        return DomainResult.Success(Unit)
    }

    override suspend fun refreshArticles(): DomainResult<Unit> {
        error?.let { return DomainResult.Failure(it) }
        return DomainResult.Success(Unit)
    }
}
```

### Factory Objects for Test Data

```kotlin
object ArticleFactory {
    private var idCounter = 0L

    fun create(
        id: Long = ++idCounter,
        title: String = "Test Article $id",
        body: String = "Body content for article $id",
        isLiked: Boolean = false,
    ) = Article(
        id = id,
        title = title,
        body = body,
        isLiked = isLiked,
        publishedAt = Instant.now()
    )

    fun createList(count: Int) = List(count) { create() }
}
```

---

## Room Integration Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class ArticleDaoTest {

    private lateinit var db: AppDatabase
    private lateinit var dao: ArticleDao

    @Before
    fun setUp() {
        db = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        ).allowMainThreadQueries().build()
        dao = db.articleDao()
    }

    @After
    fun tearDown() { db.close() }

    @Test
    fun upsertAndObserve() = runTest {
        val entity = ArticleEntityFactory.create(id = 1L, title = "Hello")
        dao.upsertAll(listOf(entity))

        val result = dao.observeAll().first()
        assertThat(result).hasSize(1)
        assertThat(result[0].title).isEqualTo("Hello")
    }

    @Test
    fun upsertUpdatesExisting() = runTest {
        dao.upsertAll(listOf(ArticleEntityFactory.create(id = 1L, title = "Original")))
        dao.upsertAll(listOf(ArticleEntityFactory.create(id = 1L, title = "Updated")))

        val result = dao.observeAll().first()
        assertThat(result).hasSize(1)
        assertThat(result[0].title).isEqualTo("Updated")
    }
}
```

---

## Screenshot Testing with Roborazzi

Roborazzi runs on the JVM using Robolectric — no emulator required. Tests run in CI without hardware.

### Dependency Setup

```toml
# gradle/libs.versions.toml
[versions]
roborazzi = "1.38.0"

[libraries]
roborazzi      = { group = "io.github.takahirom.roborazzi", name = "roborazzi", version.ref = "roborazzi" }
roborazzi-rule = { group = "io.github.takahirom.roborazzi", name = "roborazzi-junit-rule", version.ref = "roborazzi" }

[plugins]
roborazzi = { id = "io.github.takahirom.roborazzi", version.ref = "roborazzi" }
```

### Screenshot Test

```kotlin
@RunWith(AndroidJUnit4::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [33], qualifiers = RobolectricDeviceQualifiers.Pixel6)
class ArticleCardScreenshotTest {

    @get:Rule val composeTestRule = createComposeRule()
    @get:Rule val roborazziRule = RoborazziRule(
        options = RoborazziRule.Options(
            outputDirectoryPath = "src/test/snapshots",
            captureType = RoborazziRule.CaptureType.Screenshot()
        )
    )

    @Test
    fun articleCard_light() {
        composeTestRule.setContent {
            AppTheme(darkTheme = false) {
                Surface {
                    ArticleCard(
                        article = ArticleFactory.create(title = "Screenshot Test Article"),
                        onClick = {}
                    )
                }
            }
        }
        composeTestRule.onRoot().captureRoboImage()
    }

    @Test
    fun articleCard_dark() {
        composeTestRule.setContent {
            AppTheme(darkTheme = true) {
                Surface {
                    ArticleCard(
                        article = ArticleFactory.create(title = "Screenshot Test Article"),
                        onClick = {}
                    )
                }
            }
        }
        composeTestRule.onRoot().captureRoboImage()
    }

    @Test
    fun articleCard_largeFont() {
        composeTestRule.setContent {
            AppTheme {
                CompositionLocalProvider(LocalDensity provides Density(density = 3f, fontScale = 1.5f)) {
                    Surface {
                        ArticleCard(
                            article = ArticleFactory.create(title = "Large Font Screenshot Test"),
                            onClick = {}
                        )
                    }
                }
            }
        }
        composeTestRule.onRoot().captureRoboImage()
    }
}
```

### Gradle Commands

```bash
# Record baseline snapshots (first run or after intentional changes)
./gradlew recordRoborazziDebug

# Verify no visual regression against recorded snapshots
./gradlew verifyRoborazziDebug

# Run in CI
./gradlew testDebugUnitTest  # runs all unit tests including screenshot verification
```

---

## Compose UI Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class ProfileScreenTest {

    @get:Rule val composeTestRule = createComposeRule()

    @Test
    fun displayName_shown_in_ready_state() {
        composeTestRule.setContent {
            AppTheme {
                ProfileScreenContent(
                    uiState = ProfileUiState.Ready(
                        displayName = "Jane Doe",
                        avatarUrl = null,
                        followerCount = 42,
                        isFollowingEnabled = true
                    ),
                    onAction = {}
                )
            }
        }

        composeTestRule
            .onNodeWithText("Jane Doe")
            .assertIsDisplayed()
    }

    @Test
    fun retry_button_triggers_action_on_error() {
        var actionFired: ProfileAction? = null

        composeTestRule.setContent {
            AppTheme {
                ProfileScreenContent(
                    uiState = ProfileUiState.Error("Network error", canRetry = true),
                    onAction = { actionFired = it }
                )
            }
        }

        composeTestRule.onNodeWithText("Retry").performClick()
        assertThat(actionFired).isEqualTo(ProfileAction.RetryLoad)
    }
}
```

---

## Animation Testing

Compose's test APIs pause animations by default. To test animated states:

```kotlin
// Advance time to let animations settle
composeTestRule.mainClock.autoAdvance = false
composeTestRule.mainClock.advanceTimeBy(500L) // advance 500ms

// Assert intermediate state
composeTestRule.onNodeWithTag("animated_button").assertIsDisplayed()

// Re-enable auto advance to let remaining animations complete
composeTestRule.mainClock.autoAdvance = true
```

For screenshot testing animated states (e.g., shimmer loading), capture after a fixed time offset to get a deterministic frame.
