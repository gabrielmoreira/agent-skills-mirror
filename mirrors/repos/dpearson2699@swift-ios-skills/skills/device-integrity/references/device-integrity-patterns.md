# Device Integrity Extended Patterns

Overflow reference for the `device-integrity` skill. Contains server verification details, advanced error handling, and integration patterns.

## Contents

- [Server-Side Attestation Verification](#server-side-attestation-verification)
- [Server-Side Assertion Verification](#server-side-assertion-verification)
- [Server Architecture](#server-architecture)
- [Error Handling](#error-handling)
- [Retry Strategy](#retry-strategy)
- [Handling Invalidated Keys](#handling-invalidated-keys)
- [Full Integration Manager](#full-integration-manager)
- [Gradual Rollout](#gradual-rollout)
- [Environment Entitlement](#environment-entitlement)

## Server-Side Attestation Verification

Your server must:
1. Verify the attestation object is a valid CBOR-encoded structure.
2. Extract the certificate chain and validate it against Apple's App Attest root CA.
3. Verify the `nonce` in the attestation matches `SHA256(challenge)`.
4. Extract and store the public key and receipt for future assertion verification.

See [Validating apps that connect to your server](https://sosumi.ai/documentation/devicecheck/validating-apps-that-connect-to-your-server) for the full server verification algorithm.

## Server-Side Assertion Verification

Your server must:
1. Decode the assertion (CBOR).
2. Verify the authenticator data, including the counter (must be greater than the stored counter).
3. Verify the signature using the stored public key from attestation.
4. Confirm the `clientDataHash` matches the SHA-256 of the received request body.
5. Update the stored counter to prevent replay attacks.

## Server Architecture

### Attestation vs. Assertion

| Phase | When | What It Proves | Frequency |
|-------|------|---------------|-----------|
| **Attestation** | After key generation | The key lives on a genuine Apple device running your unmodified app | Once per key |
| **Assertion** | With each sensitive request | The request came from the attested app instance | Per request |

### Recommended Server Architecture

1. **Challenge endpoint** -- generate a random nonce, store it server-side with a short TTL (e.g., 5 minutes).
2. **Attestation verification endpoint** -- validate the attestation object, store the public key and receipt keyed by `keyId`.
3. **Assertion verification middleware** -- verify assertions on sensitive endpoints (purchases, account changes).

### Risk Assessment

Combine App Attest with [fraud risk assessment](https://sosumi.ai/documentation/devicecheck/assessing-fraud-risk) for defense in depth. App Attest alone does not guarantee the user is not abusing the app -- it confirms the app is genuine.

## Error Handling

### DCError Codes

```swift
import DeviceCheck

func handleAttestError(_ error: Error) {
    if let dcError = error as? DCError {
        switch dcError.code {
        case .unknownSystemFailure:
            // Transient system error -- retry with exponential backoff
            break
        case .featureUnsupported:
            // Device or OS does not support this feature
            // Fall back to alternative verification
            break
        case .invalidKey:
            // Key is corrupted or was invalidated
            // Generate a new key and re-attest
            break
        case .invalidInput:
            // The clientDataHash or keyId was malformed
            break
        case .serverUnavailable:
            // Apple's attestation server is unreachable -- retry later
            break
        @unknown default:
            break
        }
    }
}
```

## Retry Strategy

```swift
extension AppAttestManager {
    func attestKeyWithRetry(maxAttempts: Int = 3) async throws -> Data {
        var lastError: Error?

        for attempt in 0..<maxAttempts {
            do {
                return try await attestKey()
            } catch let error as DCError where error.code == .serverUnavailable {
                lastError = error
                if attempt < maxAttempts - 1 {
                    try await Task.sleep(for: .seconds(pow(2.0, Double(attempt + 1))))
                }
            } catch {
                throw error // Non-retryable errors propagate immediately
            }
        }

        throw lastError ?? DeviceIntegrityError.attestationFailed
    }
}
```

## Handling Invalidated Keys

If `attestKey` returns `DCError.invalidKey`, the Secure Enclave key has been
invalidated (e.g., OS update, Secure Enclave reset). Delete the stored `keyId`
from Keychain and generate a new key:

```swift
extension AppAttestManager {
    func handleInvalidKey() async throws -> String {
        deleteKeyIdFromKeychain()
        keyId = nil
        return try await generateKeyIfNeeded()
    }

    private func deleteKeyIdFromKeychain() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: "app-attest-key-id",
            kSecAttrService as String: Bundle.main.bundleIdentifier ?? ""
        ]
        SecItemDelete(query as CFDictionary)
    }
}
```

## Full Integration Manager

Combine the patterns above into a single `actor` that manages the full lifecycle:
1. Check `isSupported` and fall back to `DCDevice` tokens on unsupported devices.
2. Call `generateKeyIfNeeded()` on launch to create or load the persisted key.
3. Call `attestKeyWithRetry()` once after key generation.
4. Use `generateAssertion(for:)` on each sensitive server request.
5. Handle `DCError.invalidKey` by regenerating and re-attesting.

## Gradual Rollout

Apple recommends a gradual rollout. Gate App Attest behind a remote feature
flag and fall back to `DCDevice` tokens on unsupported devices.

## Environment Entitlement

Set the App Attest environment in your entitlements file. Use `development`
during testing and `production` for App Store builds:

```xml
<key>com.apple.developer.devicecheck.appattest-environment</key>
<string>production</string>
```

When the entitlement is missing, the system uses `development` in debug builds
and `production` for App Store and TestFlight builds.

### Error Type

```swift
enum DeviceIntegrityError: Error {
    case deviceCheckUnsupported
    case keyNotGenerated
    case attestationFailed
    case attestationVerificationFailed
    case assertionFailed
    case serverVerificationFailed
}
```

## Apple Documentation Links

- [DeviceCheck framework](https://sosumi.ai/documentation/devicecheck)
- [DCDevice](https://sosumi.ai/documentation/devicecheck/dcdevice)
- [DCAppAttestService](https://sosumi.ai/documentation/devicecheck/dcappattestservice)
- [Establishing your app's integrity](https://sosumi.ai/documentation/devicecheck/establishing-your-app-s-integrity)
- [Validating apps that connect to your server](https://sosumi.ai/documentation/devicecheck/validating-apps-that-connect-to-your-server)
- [Assessing fraud risk](https://sosumi.ai/documentation/devicecheck/assessing-fraud-risk)
