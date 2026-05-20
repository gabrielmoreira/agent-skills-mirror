# Architecture — State, ViewModel & Navigation

## Architectural Pattern

Every feature follows **MVVM with unidirectional data flow (UDF)**, layered by Clean Architecture:

```
Presentation  →  Domain  →  Data
  (UI + VM)      (UseCases)  (Repos + Sources)
```

The domain layer has zero Android dependencies — it is plain Kotlin. ViewModels depend on UseCases (or Repositories directly for simple features). The data layer depends on nothing in the app layer.

---

## UI State Modelling

Model UI state as a **sealed class** with a distinct subtype per meaningful screen condition. Avoid boolean flags that combine into invisible state combinations.

```kotlin
// feature/profile/src/main/kotlin/com/example/feature/profile/ProfileUiState.kt

sealed interface ProfileUiState {
    data object Loading : ProfileUiState

    data class Ready(
        val displayName: String,
        val avatarUrl: String?,
        val followerCount: Int,
        val isFollowingEnabled: Boolean,
    ) : ProfileUiState

    data class Error(
        val message: String,
        val canRetry: Boolean,
    ) : ProfileUiState
}
```

**Rules:**
- `Loading` — never carries data. The screen shows a skeleton.
- `Ready` — carries everything the screen needs. No nullable fields without a reason.
- `Error` — carries the failure message and whether recovery is user-actionable.
- Never add a `data` field to `Loading` or ad-hoc boolean flags to `Ready` (e.g. `isRefreshing`). Add a distinct state or a wrapper instead.

---

## One-Time Events

Use `SharedFlow(replay = 0)` for transient events — navigation triggers, snackbar messages, toast signals. `replay = 0` is non-negotiable: it prevents the event from re-firing on recomposition or lifecycle restart.

```kotlin
// In ViewModel
private val _events = MutableSharedFlow<ProfileEvent>(replay = 0)
val events: SharedFlow<ProfileEvent> = _events.asSharedFlow()

fun onFollowClicked() {
    viewModelScope.launch {
        // ... business logic
        _events.emit(ProfileEvent.ShowFollowConfirmation)
    }
}

// Sealed events
sealed interface ProfileEvent {
    data object ShowFollowConfirmation : ProfileEvent
    data class NavigateToPost(val postId: Long) : ProfileEvent
    data class ShowError(val message: String) : ProfileEvent
}

// In composable — collect with lifecycle awareness
LaunchedEffect(Unit) {
    viewModel.events
        .flowWithLifecycle(lifecycle, Lifecycle.State.STARTED)
        .collect { event ->
            when (event) {
                is ProfileEvent.ShowFollowConfirmation -> snackbarHostState.showSnackbar("Following!")
                is ProfileEvent.NavigateToPost -> onNavigateToPost(event.postId)
                is ProfileEvent.ShowError -> snackbarHostState.showSnackbar(event.message)
            }
        }
}
```

---

## ViewModel Structure

```kotlin
@HiltViewModel
class ProfileViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val getProfileUseCase: GetProfileUseCase,
    private val toggleFollowUseCase: ToggleFollowUseCase,
) : ViewModel() {

    private val profileId: Long = savedStateHandle.toRoute<ProfileRoute>().profileId

    private val _uiState = MutableStateFlow<ProfileUiState>(ProfileUiState.Loading)
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    private val _events = MutableSharedFlow<ProfileEvent>(replay = 0)
    val events: SharedFlow<ProfileEvent> = _events.asSharedFlow()

    init { loadProfile() }

    fun onAction(action: ProfileAction) {
        when (action) {
            ProfileAction.RetryLoad -> loadProfile()
            ProfileAction.FollowClicked -> toggleFollow()
        }
    }

    private fun loadProfile() {
        viewModelScope.launch {
            _uiState.update { ProfileUiState.Loading }
            getProfileUseCase(profileId)
                .onSuccess { profile ->
                    _uiState.update {
                        ProfileUiState.Ready(
                            displayName = profile.displayName,
                            avatarUrl = profile.avatarUrl,
                            followerCount = profile.followers,
                            isFollowingEnabled = profile.canFollow,
                        )
                    }
                }
                .onFailure { error ->
                    _uiState.update {
                        ProfileUiState.Error(
                            message = error.localizedMessage ?: "Something went wrong",
                            canRetry = true
                        )
                    }
                }
        }
    }

    private fun toggleFollow() {
        viewModelScope.launch {
            toggleFollowUseCase(profileId)
                .onSuccess { _events.emit(ProfileEvent.ShowFollowConfirmation) }
                .onFailure { _events.emit(ProfileEvent.ShowError("Couldn't follow. Try again.")) }
        }
    }
}
```

---

## DI Graph — Hilt Layering

```kotlin
// app/src/main/kotlin/com/example/app/di/AppModule.kt
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides @Singleton
    fun provideOkHttpClient(): OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(AuthInterceptor())
        .connectTimeout(30, TimeUnit.SECONDS)
        .build()
}

// core/data/src/main/kotlin/com/example/core/data/di/DataModule.kt
@Module
@InstallIn(SingletonComponent::class)
abstract class DataModule {
    @Binds
    abstract fun bindProfileRepository(impl: ProfileRepositoryImpl): ProfileRepository
}

// feature/profile/src/main/kotlin/com/example/feature/profile/di/ProfileModule.kt
@Module
@InstallIn(ViewModelComponent::class)
object ProfileModule {
    @Provides
    fun provideGetProfileUseCase(repository: ProfileRepository) =
        GetProfileUseCase(repository)
}
```

**Layer rules:**
- `SingletonComponent` — app-wide singletons: networking, database, repositories
- `ViewModelComponent` — use cases scoped to ViewModel lifetime
- `ActivityComponent` — activity-scoped dependencies (rare; avoid)
- Never inject `Context` directly into ViewModels; use `ApplicationContext` if unavoidable via `@ApplicationContext`

---

## SavedStateHandle

Use `SavedStateHandle.toRoute<T>()` to extract navigation arguments in ViewModels. This handles process death correctly and works with type-safe routes.

```kotlin
@HiltViewModel
class DetailViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val getItemUseCase: GetItemUseCase
) : ViewModel() {

    // Type-safe route extraction — survives process death
    private val route: DetailRoute = savedStateHandle.toRoute()
    private val itemId: Long = route.itemId

    // Alternatively, for a primitive:
    // private val itemId: Long = checkNotNull(savedStateHandle["itemId"])
}
```

---

## Actions Pattern

Use a **sealed interface for user actions** rather than individual callback lambdas. This makes the API surface of a screen composable clean and makes the ViewModel easier to test.

```kotlin
sealed interface ProfileAction {
    data object RetryLoad : ProfileAction
    data object FollowClicked : ProfileAction
    data class ShareClicked(val profileUrl: String) : ProfileAction
}

// Screen composable receives one lambda:
@Composable
fun ProfileScreenContent(
    uiState: ProfileUiState,
    onAction: (ProfileAction) -> Unit,
    modifier: Modifier = Modifier
)

// ViewModel handles one method:
fun onAction(action: ProfileAction) { ... }
```
