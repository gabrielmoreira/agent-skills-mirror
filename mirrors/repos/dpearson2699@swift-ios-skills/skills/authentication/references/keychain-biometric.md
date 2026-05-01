# Keychain Token Storage & Biometric Authentication

Self-contained reference for storing authentication tokens in Keychain and
protecting them with biometric authentication (Face ID / Touch ID). Covers
the patterns most commonly needed alongside Sign in with Apple and OAuth flows.

## Contents

- [Storing Tokens in Keychain](#storing-tokens-in-keychain)
- [Reading Tokens from Keychain](#reading-tokens-from-keychain)
- [Deleting Tokens from Keychain](#deleting-tokens-from-keychain)
- [kSecAttrAccessible Values](#ksecattraccessible-values)
- [Biometric Authentication with LAContext](#biometric-authentication-with-lacontext)
- [Biometric-Protected Keychain Items](#biometric-protected-keychain-items)
- [SecAccessControl Flags](#secaccesscontrol-flags)
- [Keychain Error Handling](#keychain-error-handling)

## Storing Tokens in Keychain

The Keychain is the ONLY correct place to store tokens, passwords, API keys, or
secrets. Never store these in UserDefaults, files, or Core Data.

```swift
func saveToKeychain(account: String, data: Data, service: String) throws {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: account,
        kSecAttrService as String: service,
        kSecValueData as String: data,
        kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
    ]

    let status = SecItemAdd(query as CFDictionary, nil)

    if status == errSecDuplicateItem {
        let updateQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: account,
            kSecAttrService as String: service
        ]
        let updates: [String: Any] = [kSecValueData as String: data]
        let updateStatus = SecItemUpdate(updateQuery as CFDictionary, updates as CFDictionary)
        guard updateStatus == errSecSuccess else {
            throw KeychainError.updateFailed(updateStatus)
        }
    } else if status != errSecSuccess {
        throw KeychainError.saveFailed(status)
    }
}
```

## Reading Tokens from Keychain

```swift
func readFromKeychain(account: String, service: String) throws -> Data {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: account,
        kSecAttrService as String: service,
        kSecReturnData as String: true,
        kSecMatchLimit as String: kSecMatchLimitOne
    ]

    var result: AnyObject?
    let status = SecItemCopyMatching(query as CFDictionary, &result)

    guard status == errSecSuccess, let data = result as? Data else {
        throw KeychainError.readFailed(status)
    }
    return data
}
```

## Deleting Tokens from Keychain

```swift
func deleteFromKeychain(account: String, service: String) throws {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: account,
        kSecAttrService as String: service
    ]

    let status = SecItemDelete(query as CFDictionary)
    guard status == errSecSuccess || status == errSecItemNotFound else {
        throw KeychainError.deleteFailed(status)
    }
}
```

## kSecAttrAccessible Values

| Value | When Available | Device-Only | Use For |
|---|---|---|---|
| `kSecAttrAccessibleWhenUnlocked` | Device unlocked | No | General credentials |
| `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` | Device unlocked | Yes | Sensitive credentials |
| `kSecAttrAccessibleAfterFirstUnlock` | After first unlock | No | Background-accessible tokens |
| `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` | After first unlock | Yes | Background tokens, no backup |
| `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly` | Passcode set + unlocked | Yes | Highest security |

Rules:
- Use `ThisDeviceOnly` variants for sensitive data. Prevents backup/restore to other devices.
- Use `AfterFirstUnlock` for tokens needed by background operations.
- Use `WhenPasscodeSetThisDeviceOnly` for most sensitive data. Item is deleted if passcode is removed.
- NEVER use `kSecAttrAccessibleAlways` (deprecated and insecure).

## Biometric Authentication with LAContext

Use `LAContext` from LocalAuthentication for Face ID / Touch ID prompts before
accessing sensitive data or performing protected actions.

```swift
import LocalAuthentication

func authenticateWithBiometrics() async throws -> Bool {
    let context = LAContext()
    var error: NSError?

    guard context.canEvaluatePolicy(
        .deviceOwnerAuthenticationWithBiometrics, error: &error
    ) else {
        // Biometrics not available -- fall back to passcode
        if context.canEvaluatePolicy(.deviceOwnerAuthentication, error: &error) {
            return try await context.evaluatePolicy(
                .deviceOwnerAuthentication,
                localizedReason: "Authenticate to access your account"
            )
        }
        throw AuthError.biometricsUnavailable
    }

    return try await context.evaluatePolicy(
        .deviceOwnerAuthenticationWithBiometrics,
        localizedReason: "Authenticate to access your account"
    )
}
```

### Info.plist Requirement

You MUST include `NSFaceIDUsageDescription` in Info.plist:

```xml
<key>NSFaceIDUsageDescription</key>
<string>Authenticate to access your secure data</string>
```

Missing this key causes a crash on Face ID devices.

### LAContext Configuration

```swift
let context = LAContext()
context.localizedFallbackTitle = "Use Passcode"
context.touchIDAuthenticationAllowableReuseDuration = 30
let currentState = context.evaluatedPolicyDomainState // Compare to detect enrollment changes
```

## Biometric-Protected Keychain Items

Protect keychain items so they require biometric authentication to read:

```swift
let access = SecAccessControlCreateWithFlags(
    nil,
    kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
    .biometryCurrentSet,
    nil
)!

let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrAccount as String: "auth-token",
    kSecValueData as String: tokenData,
    kSecAttrAccessControl as String: access,
    kSecUseAuthenticationContext as String: LAContext()
]
```

## SecAccessControl Flags

| Flag | Behavior |
|------|----------|
| `.biometryCurrentSet` | Requires biometry, invalidated if enrollment changes. Most secure. |
| `.biometryAny` | Requires biometry, survives enrollment changes. |
| `.userPresence` | Biometry or passcode. Most flexible. |

Use `.biometryCurrentSet` for high-security items (tokens, keys). Use
`.userPresence` when you want to allow passcode fallback without a separate
`LAContext` evaluation.

## Keychain Error Handling

```swift
enum KeychainError: Error {
    case saveFailed(OSStatus)
    case updateFailed(OSStatus)
    case readFailed(OSStatus)
    case deleteFailed(OSStatus)

    var localizedDescription: String {
        switch self {
        case .saveFailed(let status),
             .updateFailed(let status),
             .readFailed(let status),
             .deleteFailed(let status):
            return SecCopyErrorMessageString(status, nil) as String? ?? "Unknown error"
        }
    }
}
```
