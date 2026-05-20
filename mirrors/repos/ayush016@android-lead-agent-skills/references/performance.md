# Performance — Baseline Profiles, Recomposition, R8, Startup

Performance is not an optimization phase — it is a design constraint. Every architectural choice (ViewModel scope, composable granularity, LazyList key strategy, image loading configuration) has a performance dimension. Ignoring it until the app ships is how you end up with a Macrobenchmark showing 800ms cold starts and 45fps list scrolls.

---

## Compose Recomposition Optimization

Unnecessary recomposition is the most common Compose performance failure. The goal is not zero recompositions — it is that every recomposition is necessary.

### Stability — the root cause of most recomposition waste

A composable recomposes when its inputs change. "Change" is determined by whether the type is **stable** (can be compared by equality) or **unstable** (the compiler assumes it may have changed every time).

Unstable types that cause over-recomposition:
- Mutable collections (`List<T>`, `Map<K,V>`, `Set<T>`) — use `ImmutableList`, `ImmutableMap` from `kotlinx.collections.immutable`
- Data classes with `var` properties
- Classes the compiler cannot verify as stable (e.g., classes from external modules without Compose compiler access)
- Lambdas that capture unstable values

```kotlin
// BAD — List<T> is unstable; every parent recompose forces this composable to recompose
@Composable
fun ArticleList(articles: List<Article>, onArticleClick: (Article) -> Unit)

// GOOD — ImmutableList signals stability; composable skips if list hasn't changed
@Composable
fun ArticleList(articles: ImmutableList<Article>, onArticleClick: (Article) -> Unit)
```

### @Stable and @Immutable annotations

Use sparingly, only when you own the class and can guarantee the contract:

```kotlin
// @Immutable: all public properties are val and are themselves immutable
@Immutable
data class UserProfile(
    val id: Long,
    val displayName: String,
    val avatarUrl: String?
)

// @Stable: reads are consistent; writes notify Compose
@Stable
class CartState {
    private val _items = mutableStateListOf<CartItem>()
    val items: List<CartItem> get() = _items

    fun add(item: CartItem) { _items.add(item) }
    fun remove(item: CartItem) { _items.remove(item) }
}
```

**Never lie to the compiler.** Marking a mutable class `@Immutable` defeats the purpose and produces incorrect recomposition behaviour.

### Lambda stability

Every lambda created inside a composable is unstable unless remembered. Pass method references or wrap in `remember`:

```kotlin
// BAD — new lambda instance every recompose
ArticleCard(
    article = article,
    onClick = { viewModel.onArticleClicked(article.id) }
)

// GOOD — stable reference; child won't recompose when parent does
val onArticleClick = remember(article.id) {
    { viewModel.onArticleClicked(article.id) }
}
ArticleCard(article = article, onClick = onArticleClick)

// ALSO GOOD — method reference is stable if viewModel is stable
ArticleCard(article = article, onClick = viewModel::onArticleClicked)
```

### derivedStateOf — prevent threshold-driven over-recomposition

When a composable should only update at specific threshold crossings (not on every scroll pixel), use `derivedStateOf`:

```kotlin
// BAD — recomposes on every scroll pixel
val showFab = scrollState.value > 200

// GOOD — recomposes only when the threshold is crossed
val showFab by remember {
    derivedStateOf { scrollState.value > 200 }
}
```

### key() in LazyColumn

Without keys, Compose re-uses composition slots by position — moving an item causes its entire subtree to recompose. With keys, Compose tracks items by identity:

```kotlin
LazyColumn {
    items(
        items = articles,
        key = { article -> article.id },          // stable, unique identity
        contentType = { article -> article.type } // grouping for slot reuse
    ) { article ->
        ArticleCard(article = article, modifier = Modifier.animateItem())
    }
}
```

### Composition locals over parameter drilling

When a value is needed by many composables at different depths, `CompositionLocal` avoids threading it through every intermediate composable (which triggers recomposition of every intermediate when the value changes):

```kotlin
val LocalUserPreferences = staticCompositionLocalOf<UserPreferences> {
    error("No UserPreferences provided")
}
// staticCompositionLocalOf: consumers recompose when the value reference changes
// compositionLocalOf: consumers recompose when the value changes (structural equality)
```

Use `staticCompositionLocalOf` when the value rarely changes (theme, feature flags). Use `compositionLocalOf` when it changes frequently.

---

## LazyList Performance

### Avoid state reads inside the measure/layout phase

State reads inside `Modifier.layout {}` or `onGloballyPositioned` block the UI thread and prevent optimisations. Defer reads with `graphicsLayer` where possible:

```kotlin
// graphicsLayer lambda: reads state during the draw phase (off main thread path)
Modifier.graphicsLayer {
    alpha = itemAlpha.value  // read deferred to draw pass
    translationY = scrollOffset.value * parallaxFactor
}
```

### Never nest LazyColumns

A scrollable inside a scrollable requires explicit height constraints or `nestedScroll`. Prefer a single LazyColumn with mixed content types:

```kotlin
LazyColumn {
    item(contentType = "header") { FeedHeader() }
    items(featuredItems, key = { it.id }, contentType = { "featured" }) {
        FeaturedCard(it)
    }
    item(contentType = "section_title") { SectionTitle("Recent") }
    items(recentItems, key = { it.id }, contentType = { "recent" }) {
        RecentRow(it)
    }
}
```

---

## Baseline Profiles

Baseline Profiles tell the Android runtime which code paths to AOT-compile ahead of first use, dramatically reducing cold start time and initial jank.

### Setup

```toml
# gradle/libs.versions.toml
[versions]
profileinstaller = "1.3.1"
macrobenchmark = "1.3.3"
baselineprofile = "1.3.3"

[libraries]
profileinstaller = { group = "androidx.profileinstaller", name = "profileinstaller", version.ref = "profileinstaller" }

[plugins]
baselineprofile = { id = "androidx.baselineprofile", version.ref = "baselineprofile" }
```

```kotlin
// app/build.gradle.kts
plugins {
    alias(libs.plugins.baselineprofile)
}

dependencies {
    implementation(libs.profileinstaller)
    baselineProfile(project(":baselineprofile"))
}
```

### Baseline profile module

```kotlin
// baselineprofile/build.gradle.kts
plugins {
    alias(libs.plugins.android.test)
    alias(libs.plugins.baselineprofile)
}

android {
    targetProjectPath = ":app"
}
```

```kotlin
// baselineprofile/src/main/kotlin/.../BaselineProfileGenerator.kt
@RunWith(AndroidJUnit4::class)
@RequiresDevice
class BaselineProfileGenerator {

    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generate() = rule.collect(packageName = "com.example.app") {
        pressHome()
        startActivityAndWait()

        // Critical user journeys — the most performance-sensitive paths
        device.findObject(By.res("home_feed")).wait(Until.hasObject(By.res("article_card")), 5000)

        // Navigate to detail
        device.findObject(By.res("article_card")).click()
        device.waitForIdle()

        // Return
        device.pressBack()
        device.waitForIdle()
    }
}
```

### Generating and verifying

```bash
# Generate baseline profile
./gradlew :baselineprofile:generateBaselineProfile

# The generated profile is written to:
# app/src/main/baseline-prof.txt

# Verify it's applied correctly
./gradlew :app:assembleRelease

# Benchmark cold start before/after to verify improvement
./gradlew :macrobenchmark:connectedAndroidTest
```

---

## Macrobenchmark

Benchmark real-world user journeys — cold start, scroll performance, navigation transitions.

```kotlin
// macrobenchmark/src/main/kotlin/.../AppStartBenchmark.kt
@RunWith(AndroidJUnit4::class)
class AppStartBenchmark {

    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun coldStart() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        iterations = 5,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
    }

    @Test
    fun scrollFeed() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(FrameTimingMetric()),
        iterations = 5,
        startupMode = StartupMode.WARM
    ) {
        startActivityAndWait()
        val feedList = device.findObject(By.res("home_feed"))
        feedList.fling(Direction.DOWN)
        device.waitForIdle()
    }
}
```

---

## App Startup Optimization

### App Startup library — lazy initialisation

Replace heavyweight `Application.onCreate()` initializers with lazy-loaded, dependency-aware initializers:

```kotlin
// core/startup/src/main/kotlin/.../AnalyticsInitializer.kt
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context): Analytics {
        return Analytics.getInstance(context).also { it.initialize() }
    }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

// AndroidManifest.xml — no explicit initializers needed; discovered automatically
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    android:exported="false"
    tools:node="merge" />
```

### Avoid blocking the main thread in Application.onCreate

```kotlin
class AppApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // NEVER: synchronous network calls, heavy disk I/O, large data parsing
        // OK: lightweight DI setup, registering callbacks
        applicationScope.launch(Dispatchers.IO) {
            // Heavy initialization moved off main thread
            performHeavyInitialization()
        }
    }
}
```

---

## R8 / ProGuard Configuration

### Enable full mode R8 (more aggressive than ProGuard)

```kotlin
// gradle.properties
android.enableR8.fullMode=true
```

### Essential rules for Kotlin + Retrofit + Room

```proguard
# Kotlin serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keepclassmembers class kotlinx.serialization.json.** { *** Companion; }
-keepclasseswithmembers class **$$serializer { CREATOR <fields>; }

# Retrofit — keep service interfaces
-keepattributes Signature, Exceptions
-keep,allowobfuscation,allowshrinking interface retrofit2.Call
-keep,allowobfuscation,allowshrinking class retrofit2.Response

# Room — keep entity classes
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *
-keepclassmembers @androidx.room.Entity class * { *; }

# Hilt
-keepnames @dagger.hilt.android.lifecycle.HiltViewModel class * extends androidx.lifecycle.ViewModel

# Kotlin coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}

# Data classes used in navigation (Serializable routes)
-keepclassmembers @kotlinx.serialization.Serializable class * {
    *** Companion;
    *** serializer();
    <init>(...);
}
```

### Verify R8 output

```bash
# Build a release APK and check size
./gradlew :app:assembleRelease

# Inspect what was kept vs removed
# Output: app/build/outputs/mapping/release/mapping.txt

# Decode an obfuscated stack trace
java -jar tools/r8.jar retrace \
  app/build/outputs/mapping/release/mapping.txt \
  /tmp/stacktrace.txt
```

---

## Memory Management

### Detect leaks with LeakCanary

```toml
# Add only to debug builds
[libraries]
leakcanary = { group = "com.squareup.leakcanary", name = "leakcanary-android", version = "2.14" }
```

```kotlin
// No code required — LeakCanary auto-installs via ContentProvider in debug builds
dependencies {
    debugImplementation(libs.leakcanary)
}
```

### Common Compose memory leak patterns

```kotlin
// BAD — context captured in a long-lived lambda inside viewModelScope
viewModelScope.launch {
    val context = context // captured Activity context — leaks on rotation
}

// GOOD — use ApplicationContext for long-lived operations
@Inject @ApplicationContext val appContext: Context

// BAD — holding a reference to a Composable lambda outside composition
var storedContent: @Composable () -> Unit = {}

// GOOD — never store composable lambdas; recreate them at call site
```

### Bitmap memory

```kotlin
// Always specify exact size for thumbnails — prevents loading full-resolution into memory
AsyncImage(
    model = ImageRequest.Builder(context)
        .data(imageUrl)
        .size(200, 200)      // downsample to display size
        .crossfade(true)
        .build(),
    contentDescription = null
)
```

---

## Build Performance

```kotlin
// gradle.properties
org.gradle.caching=true
org.gradle.parallel=true
org.gradle.configureondemand=true
org.gradle.jvmargs=-Xmx4g -XX:+UseParallelGC

# Configuration cache (Gradle 8+)
org.gradle.configuration-cache=true
org.gradle.configuration-cache.problems=warn
```

```bash
# Generate build scan to identify bottlenecks
./gradlew assembleDebug --scan

# Check configuration cache hits
./gradlew assembleDebug --configuration-cache

# Profile task execution
./gradlew assembleDebug --profile
# Output: build/reports/profile/profile-*.html
```
