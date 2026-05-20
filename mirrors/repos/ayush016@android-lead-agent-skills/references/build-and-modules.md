# Build & Modules — Gradle, Convention Plugins, Version Catalogs

## Module Structure

```
:app                          ← entry point; application manifest only
:core:ui                      ← shared Compose components, theme, tokens
:core:domain                  ← use cases, domain models; zero Android deps
:core:data                    ← repositories, data sources, Room, Retrofit
:core:network                 ← OkHttp, Retrofit setup, interceptors
:core:testing                 ← fake implementations, test utilities
:feature:home                 ← home screen (presentation only)
:feature:profile              ← profile screen
:feature:settings             ← settings screen
:build-logic                  ← composite build with convention plugins
```

**Module rules:**
- Feature modules depend on `:core:*` modules, never on other `:feature:*` modules
- `:core:domain` must not import anything from `android.*` or `androidx.*`
- `:core:ui` and `:app` are the only modules that import Compose dependencies
- Cross-feature navigation is handled through a `:core:navigation` module with shared route definitions

---

## Composite Build Setup

```kotlin
// settings.gradle.kts (root)
pluginManagement {
    includeBuild("build-logic")  // registers convention plugins
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "YourApp"
include(
    ":app",
    ":core:ui",
    ":core:domain",
    ":core:data",
    ":core:network",
    ":core:testing",
    ":feature:home",
    ":feature:profile",
)
```

```kotlin
// build-logic/settings.gradle.kts
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
    versionCatalogs {
        create("libs") {
            from(files("../gradle/libs.versions.toml"))
        }
    }
}
rootProject.name = "build-logic"
include(":convention")
```

---

## Convention Plugins

```kotlin
// build-logic/convention/src/main/kotlin/AndroidLibraryConventionPlugin.kt
class AndroidLibraryConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) = with(target) {
        with(pluginManager) {
            apply("com.android.library")
            apply("org.jetbrains.kotlin.android")
        }

        extensions.configure<LibraryExtension> {
            compileSdk = 35
            defaultConfig.minSdk = 21

            compileOptions {
                sourceCompatibility = JavaVersion.VERSION_17
                targetCompatibility = JavaVersion.VERSION_17
            }
        }

        extensions.configure<KotlinAndroidProjectExtension> {
            jvmToolchain(17)
        }
    }
}

// build-logic/convention/src/main/kotlin/AndroidLibraryComposeConventionPlugin.kt
class AndroidLibraryComposeConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) = with(target) {
        pluginManager.apply("com.android.library")

        val libs = extensions.getByType<VersionCatalogsExtension>().named("libs")

        extensions.configure<LibraryExtension> {
            buildFeatures.compose = true
        }

        dependencies {
            add("implementation", platform(libs.findLibrary("compose-bom").get()))
            add("implementation", libs.findLibrary("compose-ui").get())
            add("implementation", libs.findLibrary("compose-material3").get())
            add("debugImplementation", libs.findLibrary("compose-ui-tooling").get())
        }
    }
}

// build-logic/convention/build.gradle.kts
plugins { `kotlin-dsl` }

dependencies {
    compileOnly(libs.android.gradlePlugin)
    compileOnly(libs.kotlin.gradlePlugin)
    compileOnly(libs.compose.gradlePlugin)
}

gradlePlugin {
    plugins {
        register("androidLibrary") {
            id = "yourapp.android.library"
            implementationClass = "AndroidLibraryConventionPlugin"
        }
        register("androidLibraryCompose") {
            id = "yourapp.android.library.compose"
            implementationClass = "AndroidLibraryComposeConventionPlugin"
        }
        register("androidHilt") {
            id = "yourapp.android.hilt"
            implementationClass = "AndroidHiltConventionPlugin"
        }
    }
}
```

Usage in a feature module:

```kotlin
// feature/profile/build.gradle.kts
plugins {
    alias(libs.plugins.yourapp.android.library)
    alias(libs.plugins.yourapp.android.library.compose)
    alias(libs.plugins.yourapp.android.hilt)
}
// That's it. All Android, Kotlin, Compose, and Hilt config is inherited.
```

---

## Version Catalog

```toml
# gradle/libs.versions.toml
[versions]
kotlin = "2.0.21"
compose-bom = "2024.12.01"
hilt = "2.52"
navigation = "2.8.5"
room = "2.7.0"
retrofit = "2.11.0"
coil = "3.0.4"
roborazzi = "1.38.0"
ksp = "2.0.21-1.0.28"

[libraries]
# Compose
compose-bom                = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-ui                 = { group = "androidx.compose.ui", name = "ui" }
compose-ui-tooling         = { group = "androidx.compose.ui", name = "ui-tooling" }
compose-ui-tooling-preview = { group = "androidx.compose.ui", name = "ui-tooling-preview" }
compose-material3          = { group = "androidx.compose.material3", name = "material3" }
compose-animation          = { group = "androidx.compose.animation", name = "animation" }

# Navigation
navigation-compose         = { group = "androidx.navigation", name = "navigation-compose", version.ref = "navigation" }

# Hilt
hilt-android               = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler              = { group = "com.google.dagger", name = "hilt-compiler", version.ref = "hilt" }
hilt-navigation-compose    = { group = "androidx.hilt", name = "hilt-navigation-compose", version = "1.2.0" }

# Room
room-runtime               = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
room-ktx                   = { group = "androidx.room", name = "room-ktx", version.ref = "room" }
room-compiler              = { group = "androidx.room", name = "room-compiler", version.ref = "room" }

# Networking
retrofit-core              = { group = "com.squareup.retrofit2", name = "retrofit", version.ref = "retrofit" }
retrofit-kotlinx-serialization = { group = "com.squareup.retrofit2", name = "converter-kotlinx-serialization", version.ref = "retrofit" }
okhttp-logging             = { group = "com.squareup.okhttp3", name = "logging-interceptor", version = "4.12.0" }

# Image loading
coil-compose               = { group = "io.coil-kt.coil3", name = "coil-compose", version.ref = "coil" }
coil-network-okhttp        = { group = "io.coil-kt.coil3", name = "coil-network-okhttp", version.ref = "coil" }

# Testing
roborazzi                  = { group = "io.github.takahirom.roborazzi", name = "roborazzi", version.ref = "roborazzi" }
roborazzi-rule             = { group = "io.github.takahirom.roborazzi", name = "roborazzi-junit-rule", version.ref = "roborazzi" }

# Build logic dependencies (referenced from build-logic only)
android-gradlePlugin       = { group = "com.android.tools.build", name = "gradle", version = "8.7.3" }
kotlin-gradlePlugin        = { group = "org.jetbrains.kotlin", name = "kotlin-gradle-plugin", version.ref = "kotlin" }

[plugins]
android-application        = { id = "com.android.application", version = "8.7.3" }
android-library            = { id = "com.android.library", version = "8.7.3" }
kotlin-android             = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
kotlin-compose             = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
kotlin-serialization       = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
hilt                       = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
ksp                        = { id = "com.google.devtools.ksp", version.ref = "ksp" }
roborazzi                  = { id = "io.github.takahirom.roborazzi", version.ref = "roborazzi" }

# Convention plugins (from build-logic)
yourapp-android-library          = { id = "yourapp.android.library", version = "unspecified" }
yourapp-android-library-compose  = { id = "yourapp.android.library.compose", version = "unspecified" }
yourapp-android-hilt             = { id = "yourapp.android.hilt", version = "unspecified" }
yourapp-android-application      = { id = "yourapp.android.application", version = "unspecified" }
```

---

## Internal API Exposure

Modules expose only what other modules need. Use Kotlin's `internal` modifier for implementation details within a module. In Gradle, use `api` vs `implementation` dependencies to control transitive exposure:

```kotlin
// core/data/build.gradle.kts
dependencies {
    // implementation: consumers of :core:data cannot see retrofit directly
    implementation(libs.retrofit.core)
    
    // api: consumers of :core:data CAN see these (only if truly needed upstream)
    api(libs.kotlinx.coroutines.core)
}
```

**Default**: Use `implementation`. Only promote to `api` when a dependency type surfaces in a public API of the module (e.g., a `Flow<T>` in a repository interface where `T` lives in a different module).

---

## Gradle Wrapper — the File Everyone Forgets

`gradle/wrapper/gradle-wrapper.properties` is the single most important file for build reproducibility. Without it, every developer and every CI machine uses whatever Gradle version their IDE happens to bundle — and Gradle/AGP version mismatches are the #1 source of new-project build failures.

```properties
# gradle/wrapper/gradle-wrapper.properties
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.7-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
```

### AGP ↔ Gradle compatibility matrix

| AGP version | Required Gradle | Notes |
|-------------|----------------|-------|
| 8.5.x | 8.7 | Stable; recommended combination for 2024 projects |
| 8.6.x | 8.7 | Minor bump |
| 8.7.x | 8.9 | Required — do NOT use with Gradle 8.11+ (breaks `debugRuntimeClasspathCopy`) |
| 8.8.x | 8.10.2 | Gradle 8.11 strict mode compatible |

**Rule**: Always set the wrapper URL explicitly. Never rely on the IDE's bundled Gradle.

```bash
# Regenerate the wrapper with a specific version
./gradlew wrapper --gradle-version=8.7 --distribution-type=bin
```

---

## App Bootstrap Resources

Every new `:app` module needs these XML resources before the first Gradle build or AAPT will fail with "resource not found" errors. These are not optional — even a Compose-only app with no XML layouts needs them.

### Minimum required files

```
app/src/main/res/
├── values/
│   ├── strings.xml    ← android:label in manifest
│   └── themes.xml     ← android:theme in manifest (no-action-bar for Compose)
├── drawable/
│   ├── ic_launcher_background.xml   ← adaptive icon background
│   └── ic_launcher_foreground.xml   ← adaptive icon foreground
└── mipmap-anydpi-v26/
    ├── ic_launcher.xml              ← adaptive icon (API 26+)
    └── ic_launcher_round.xml        ← same, for round launchers
```

### themes.xml (no-ActionBar for Compose)

```xml
<resources>
    <style name="Theme.YourApp" parent="android:Theme.Material.Light.NoActionBar" />
</resources>
```

### Adaptive icon setup (no PNG files needed if minSdk ≥ 26)

```xml
<!-- drawable/ic_launcher_background.xml -->
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="#006874" />   <!-- use your brand primary color -->
</shape>

<!-- drawable/ic_launcher_foreground.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path android:fillColor="#FFFFFF"
          android:pathData="M54,24 A30,30 0,1,0 54,84 A30,30 0,0,0 54,24Z
                            M54,76 A22,22 0,1,1 54,32 A22,22 0,0,1 54,76Z"/>
</vector>

<!-- mipmap-anydpi-v26/ic_launcher.xml -->
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
</adaptive-icon>
```

**minSdk note**: If your minSdk is < 26, you must also provide PNG fallbacks in `mipmap-hdpi/`, `mipmap-xhdpi/`, `mipmap-xxhdpi/`, and `mipmap-xxxhdpi/`. Standard sizes: hdpi=72dp, xhdpi=96dp, xxhdpi=144dp, xxxhdpi=192dp. For new apps in 2025, minSdk 26 is the practical minimum (API 26 = ~99% device coverage).

**VectorDrawable element restriction**: Android VectorDrawable only supports `<path>`, `<group>`, and `<clip-path>` elements — NOT SVG shape elements like `<circle>`, `<rect>`, or `<ellipse>`. Draw all shapes as path data:

```xml
<!-- WRONG — <circle> is SVG, not Android VectorDrawable -->
<circle android:cx="54" android:cy="54" android:r="8" />

<!-- CORRECT — circle as two arc path commands -->
<!-- Center (54,54), radius 8: start at leftmost point, arc to rightmost, arc back -->
<path android:pathData="M46,54 A8,8 0 1 0 62,54 A8,8 0 1 0 46,54 Z" />

<!-- CORRECT — rectangle as M (moveto) + L (lineto) commands -->
<path android:pathData="M10,10 L90,10 L90,90 L10,90 Z" />
```
