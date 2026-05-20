# Data Layer — Networking, Persistence, Offline-First

## Layering

```
ViewModel / UseCase
       ↓ calls
Repository Interface (domain layer)
       ↓ implemented by
RepositoryImpl (data layer)
       ↓ reads/writes
RemoteDataSource + LocalDataSource
       ↓
Retrofit API          Room DAO
```

Repositories are the single source of truth. They decide whether to return cached or fresh data. ViewModels never touch data sources directly.

---

## Networking — Retrofit + OkHttp

### Client Setup

```kotlin
// core/network/src/main/kotlin/com/example/core/network/di/NetworkModule.kt
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor,
        @ApplicationContext context: Context
    ): OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY
                    else HttpLoggingInterceptor.Level.NONE
        })
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    @Provides @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(
                Json { ignoreUnknownKeys = true }
                    .asConverterFactory("application/json".toMediaType())
            )
            .build()
}
```

### Auth Interceptor

```kotlin
class AuthInterceptor @Inject constructor(
    private val tokenRepository: TokenRepository
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokenRepository.getAccessToken()
        val request = chain.request().newBuilder()
            .apply { if (token != null) header("Authorization", "Bearer $token") }
            .build()
        return chain.proceed(request)
    }
}
```

### API Interface

```kotlin
// core/network/src/main/kotlin/.../api/ArticleApi.kt
interface ArticleApi {
    @GET("articles")
    suspend fun getArticles(
        @Query("page") page: Int,
        @Query("limit") limit: Int = 20
    ): List<ArticleDto>

    @GET("articles/{id}")
    suspend fun getArticle(@Path("id") id: Long): ArticleDto

    @POST("articles/{id}/like")
    suspend fun likeArticle(@Path("id") id: Long): Response<Unit>
}
```

### Error Mapping

Map network errors at the data source boundary — never expose `HttpException` or `IOException` to the domain layer.

```kotlin
// Sealed result type — lives in core:domain
sealed interface DomainResult<out T> {
    data class Success<T>(val data: T) : DomainResult<T>
    data class Failure(val error: DomainError) : DomainResult<Nothing>
}

sealed interface DomainError {
    data object NetworkUnavailable : DomainError
    data object Unauthorized : DomainError
    data object NotFound : DomainError
    data class ServerError(val code: Int, val message: String) : DomainError
    data class Unknown(val throwable: Throwable) : DomainError
}

// Mapping function — data layer only
suspend fun <T> safeApiCall(block: suspend () -> T): DomainResult<T> = try {
    DomainResult.Success(block())
} catch (e: HttpException) {
    DomainResult.Failure(
        when (e.code()) {
            401  -> DomainError.Unauthorized
            404  -> DomainError.NotFound
            in 500..599 -> DomainError.ServerError(e.code(), e.message())
            else -> DomainError.Unknown(e)
        }
    )
} catch (e: IOException) {
    DomainResult.Failure(DomainError.NetworkUnavailable)
} catch (e: Exception) {
    DomainResult.Failure(DomainError.Unknown(e))
}
```

---

## Local Persistence — Room

### Entity + DAO

```kotlin
// Entity
@Entity(tableName = "articles")
data class ArticleEntity(
    @PrimaryKey val id: Long,
    val title: String,
    val bodyMarkdown: String,
    val authorId: Long,
    val publishedAt: Long,       // epoch millis — always store time as Long
    val cachedAt: Long,          // when we fetched this from the network
    val isLiked: Boolean = false,
)

// DAO
@Dao
interface ArticleDao {
    @Query("SELECT * FROM articles ORDER BY publishedAt DESC")
    fun observeAll(): Flow<List<ArticleEntity>>  // Flow = reactive; no suspend needed

    @Query("SELECT * FROM articles WHERE id = :id")
    suspend fun getById(id: Long): ArticleEntity?

    @Upsert
    suspend fun upsertAll(articles: List<ArticleEntity>)

    @Query("UPDATE articles SET isLiked = :liked WHERE id = :id")
    suspend fun setLiked(id: Long, liked: Boolean)

    @Query("DELETE FROM articles WHERE cachedAt < :cutoffMs")
    suspend fun purgeOlderThan(cutoffMs: Long)
}
```

### Database

```kotlin
@Database(
    entities = [ArticleEntity::class, UserEntity::class],
    version = 2,
    exportSchema = true
)
@TypeConverters(AppTypeConverters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun articleDao(): ArticleDao
    abstract fun userDao(): UserDao

    companion object {
        fun create(context: Context): AppDatabase =
            Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
                .addMigrations(MIGRATION_1_2)
                .build()
    }
}
```

### DataStore — Lightweight Preferences

Use DataStore for user preferences, session data, and feature flags. Never use SharedPreferences in new code.

```kotlin
val Context.settingsDataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

object PreferenceKeys {
    val DARK_MODE_ENABLED = booleanPreferencesKey("dark_mode_enabled")
    val ONBOARDING_COMPLETE = booleanPreferencesKey("onboarding_complete")
    val NOTIFICATION_FREQUENCY = intPreferencesKey("notification_frequency")
}

class SettingsRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {
    val darkModeEnabled: Flow<Boolean> = context.settingsDataStore.data
        .map { prefs -> prefs[PreferenceKeys.DARK_MODE_ENABLED] ?: false }

    suspend fun setDarkMode(enabled: Boolean) {
        context.settingsDataStore.edit { prefs ->
            prefs[PreferenceKeys.DARK_MODE_ENABLED] = enabled
        }
    }
}
```

---

## Offline-First Strategy

### Read: Stale-While-Revalidate

Show cached data immediately; refresh in the background. The UI never blocks on a network call for content it might already have.

```kotlin
class ArticleRepositoryImpl @Inject constructor(
    private val api: ArticleApi,
    private val dao: ArticleDao,
    private val dispatchers: AppDispatchers
) : ArticleRepository {

    override fun observeArticles(): Flow<DomainResult<List<Article>>> = flow {
        // 1. Emit cached data immediately (may be empty list)
        val cached = dao.observeAll()
            .map { entities -> DomainResult.Success(entities.map(ArticleEntity::toDomain)) }
        emitAll(cached)

        // 2. Refresh from network in background
        withContext(dispatchers.io) {
            val result = safeApiCall { api.getArticles(page = 1) }
            if (result is DomainResult.Success) {
                dao.upsertAll(result.data.map(ArticleDto::toEntity))
            }
            // If network fails, cached data is already emitted — no error interruption
        }
    }
}
```

### Write: Optimistic Local + Background Sync

Write the local state immediately (zero-latency feedback), then sync to the server. If the sync fails, surface an error and optionally roll back.

```kotlin
override suspend fun likeArticle(id: Long): DomainResult<Unit> {
    // 1. Optimistic local update
    dao.setLiked(id, liked = true)

    // 2. Sync to server
    return safeApiCall { api.likeArticle(id) }
        .also { result ->
            if (result is DomainResult.Failure) {
                dao.setLiked(id, liked = false) // rollback
            }
        }
}
```

### Background Sync with WorkManager

For periodic or deferred sync (push unsynced writes, refresh stale cache):

```kotlin
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val syncRepository: SyncRepository
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = try {
        syncRepository.syncPendingChanges()
        Result.success()
    } catch (e: Exception) {
        if (runAttemptCount < 3) Result.retry() else Result.failure()
    }

    companion object {
        fun schedule(context: Context) {
            val request = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .build()
                )
                .build()
            WorkManager.getInstance(context)
                .enqueueUniquePeriodicWork("sync", ExistingPeriodicWorkPolicy.KEEP, request)
        }
    }
}
```

---

## Repository Interface Pattern

Repositories always expose:
- `Flow<T>` for data the UI observes over time (lists, profiles, settings)
- `suspend fun`: `DomainResult<T>` for operations (save, delete, sync)

```kotlin
// core/domain/src/main/kotlin/.../repository/ArticleRepository.kt
interface ArticleRepository {
    fun observeArticles(): Flow<DomainResult<List<Article>>>
    fun observeArticle(id: Long): Flow<DomainResult<Article>>
    suspend fun likeArticle(id: Long): DomainResult<Unit>
    suspend fun refreshArticles(): DomainResult<Unit>
}
```

Never return `List<T>` directly from a repository. Even a one-shot load should use `suspend fun`: `DomainResult<T>` so errors surface correctly rather than being swallowed in a try/catch somewhere in the ViewModel.
