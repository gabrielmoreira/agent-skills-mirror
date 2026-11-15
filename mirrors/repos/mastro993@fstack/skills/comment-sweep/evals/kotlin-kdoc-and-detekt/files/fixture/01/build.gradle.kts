plugins {
    id("com.android.library") version "8.5.2"
    kotlin("android") version "2.0.20"
    id("io.gitlab.arturbosch.detekt") version "1.23.6"
    id("org.jlleitschuh.gradle.ktlint") version "11.6.1"
}

android {
    namespace = "com.example.shop"
    compileSdk = 34

    defaultConfig {
        minSdk = 24
    }

    sourceSets["main"].java.srcDirs("src/main/kotlin")
}

kotlin {
    jvmToolchain(17)
}

detekt {
    config.setFrom(files("config/detekt.yml"))
    buildUponDefaultConfig = true
}

ktlint {
    version.set("0.48.2")
    android.set(true)
}

dependencies {
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")
}
