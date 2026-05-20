# Security — Encryption, Biometrics, Network Security, Secrets

Security is not a feature you add at the end. Architecture decisions made early — how credentials are stored, how network traffic is secured, how the app handles untrusted input — are expensive to change later. These patterns should be applied from day one.

---

## Encrypted Storage

### EncryptedSharedPreferences — for sensitive key-value data

```kotlin
// core/security/src/main/kotlin/.../SecureStorage.kt
class SecureStorage @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val prefs: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveAccessToken(token: String) = prefs.edit { putString("access_token", token) }
    fun getAccessToken(): String? = prefs.getString("access_token", null)
    fun clearAll() = prefs.edit { clear() }
}
```

### EncryptedFile — for sensitive file storage

```kotlin
fun writeEncryptedFile(context: Context, fileName: String, data: ByteArray) {
    val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    val file = File(context.filesDir, fileName)
    val encryptedFile = EncryptedFile.Builder(
        context,
        file,
        masterKey,
        EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
    ).build()

    encryptedFile.openFileOutput().use { stream ->
        stream.write(data)
    }
}
```

**Never store sensitive data in:**
- `SharedPreferences` (unencrypted XML on disk)
- Room database without encryption
- External storage
- `Bundle` passed between apps (leaks via Binder transaction logs)
- Logcat (always filter tokens/passwords from logs)

---

## Biometric Authentication

```kotlin
// core/security/src/main/kotlin/.../BiometricAuth.kt
class BiometricAuth @Inject constructor(
    private val context: Context
) {
    private val biometricManager = BiometricManager.from(context)

    fun canAuthenticate(): BiometricCapability {
        return when (biometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG or
            BiometricManager.Authenticators.DEVICE_CREDENTIAL
        )) {
            BiometricManager.BIOMETRIC_SUCCESS -> BiometricCapability.Available
            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> BiometricCapability.NoHardware
            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> BiometricCapability.HardwareUnavailable
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> BiometricCapability.NoneEnrolled
            else -> BiometricCapability.Unknown
        }
    }

    fun showPrompt(
        activity: FragmentActivity,
        title: String,
        subtitle: String,
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle(title)
            .setSubtitle(subtitle)
            .setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG or
                BiometricManager.Authenticators.DEVICE_CREDENTIAL
            )
            .build()

        BiometricPrompt(
            activity,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    onSuccess()
                }
                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    onError(errString.toString())
                }
                override fun onAuthenticationFailed() {
                    // User biometric did not match — prompt stays open; no action needed
                }
            }
        ).authenticate(promptInfo)
    }
}

sealed interface BiometricCapability {
    data object Available : BiometricCapability
    data object NoHardware : BiometricCapability
    data object HardwareUnavailable : BiometricCapability
    data object NoneEnrolled : BiometricCapability
    data object Unknown : BiometricCapability
}
```

---

## Certificate Pinning

Prevent MITM attacks by pinning the server's certificate or public key.

### Via OkHttp CertificatePinner

```kotlin
// core/network/src/main/kotlin/.../NetworkModule.kt
@Provides @Singleton
fun provideOkHttpClient(): OkHttpClient {
    val certificatePinner = CertificatePinner.Builder()
        // Pin by SHA-256 hash of the leaf certificate's public key
        // Generate with: openssl s_client -connect api.example.com:443 | \
        //   openssl x509 -pubkey | openssl pkey -pubin -outform DER | \
        //   openssl dgst -sha256 -binary | base64
        .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        .add("api.example.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=") // backup pin
        .build()

    return OkHttpClient.Builder()
        .certificatePinner(certificatePinner)
        .build()
}
```

### Via Network Security Config (declarative, no code)

```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2026-01-01">
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </pin-set>
    </domain-config>

    <!-- Debug builds only: trust user-added CAs for Charles/Fiddler proxy -->
    <debug-overrides>
        <trust-anchors>
            <certificates src="user" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config"
    android:usesCleartextTraffic="false">
```

---

## Secret Management

### Never put secrets in source code

```kotlin
// BAD — checked into version control, visible in decompiled APK
companion object {
    const val API_KEY = "sk-1234567890abcdef"
}

// BETTER — in BuildConfig (still in APK, but not in source)
// In build.gradle.kts:
android {
    buildTypes {
        release {
            buildConfigField("String", "API_KEY", "\"${System.getenv("API_KEY")}\"")
        }
    }
}

// Access:
val apiKey = BuildConfig.API_KEY

// BEST — API key delivered from your backend at runtime, not embedded in APK
```

### .gitignore for local secrets

```gitignore
# local.properties — where you put API keys for local dev
local.properties
*.jks          # signing keystores
keystore.properties
google-services.json  # if it contains sensitive project config
```

```kotlin
// local.properties (never committed)
# API_KEY=your-actual-key-here

// build.gradle.kts — read from local.properties
val localProperties = Properties().apply {
    val file = rootProject.file("local.properties")
    if (file.exists()) load(file.inputStream())
}

android {
    buildTypes.all {
        buildConfigField(
            "String",
            "API_KEY",
            "\"${localProperties.getProperty("API_KEY") ?: System.getenv("API_KEY") ?: ""}\""
        )
    }
}
```

---

## Input Validation and Injection Prevention

### Validate all external input at system boundaries

```kotlin
// Repository layer — validate before using in queries
class UserRepository @Inject constructor(private val dao: UserDao) {

    suspend fun searchUsers(query: String): List<User> {
        // Sanitise: strip characters that could affect parameterised queries
        val sanitised = query.trim().take(100)
        if (sanitised.isBlank()) return emptyList()
        return dao.searchUsers(sanitised) // Room uses parameterised queries — safe
    }
}

// Room parameterised query — never build SQL strings by concatenation
@Dao interface UserDao {
    @Query("SELECT * FROM users WHERE display_name LIKE '%' || :query || '%'")
    suspend fun searchUsers(query: String): List<User>
}
```

### WebView security

```kotlin
// Minimum secure WebView configuration
webView.apply {
    settings.apply {
        javaScriptEnabled = false           // disable unless your content requires it
        allowFileAccess = false             // prevent file:// URI access
        allowContentAccess = false
        domStorageEnabled = false
        setSupportZoom(false)
    }
    webViewClient = object : WebViewClient() {
        override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
            val url = request.url
            // Only allow your own domain
            if (url.host == "example.com") return false
            // Block everything else
            return true
        }
    }
}
```

---

## ProGuard / R8 — Security-Relevant Rules

```proguard
# Strip all logging in release builds — prevents leaking data in logcat
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}

# Strip Timber debug logs
-assumenosideeffects class timber.log.Timber {
    public static *** d(...);
    public static *** v(...);
}

# Prevent reflection attacks on internal classes
-keep class com.example.app.model.** { *; }  # only what the API needs
```

---

## Content Provider Security

```xml
<!-- AndroidManifest.xml -->
<!-- Never export providers unless required by other apps -->
<provider
    android:name=".data.AppContentProvider"
    android:authorities="${applicationId}.provider"
    android:exported="false"      <!-- explicit false — don't rely on default -->
    android:grantUriPermissions="true" />

<!-- FileProvider for sharing files with other apps -->
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true">
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>
```

---

## Play Integrity

Verify the app is running on a genuine, unmodified Android device from the Play Store:

```kotlin
// Typically called before a sensitive operation (payment, account creation)
class IntegrityChecker @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val integrityManager = IntegrityManagerFactory.create(context)

    suspend fun requestToken(nonce: String): String = suspendCoroutine { cont ->
        val request = IntegrityTokenRequest.builder()
            .setNonce(nonce)          // server-generated nonce to prevent replay
            .setCloudProjectNumber(BuildConfig.CLOUD_PROJECT_NUMBER)
            .build()

        integrityManager.requestIntegrityToken(request)
            .addOnSuccessListener { response ->
                cont.resume(response.token())
            }
            .addOnFailureListener { exception ->
                cont.resumeWithException(exception)
            }
    }
}

// Send token to your backend for verification — never verify on-device
// Backend verifies via Google Play Integrity API
```

---

## Security Checklist Before Release

- [ ] No API keys, tokens, or passwords in source code or committed files
- [ ] `android:usesCleartextTraffic="false"` in manifest
- [ ] Certificate pinning configured for all API endpoints
- [ ] `android:exported="false"` on all Activities/Services/Receivers not intended for external access
- [ ] All exported components require explicit permissions
- [ ] Input validation at every external boundary (user input, API response, intent extras)
- [ ] `android:debuggable` not set to `true` in release build type
- [ ] ProGuard/R8 rules strip all debug logging
- [ ] EncryptedSharedPreferences for all sensitive preferences
- [ ] File sharing uses FileProvider, not `file://` URIs
- [ ] WebView JavaScript disabled unless required; URL filtering applied
