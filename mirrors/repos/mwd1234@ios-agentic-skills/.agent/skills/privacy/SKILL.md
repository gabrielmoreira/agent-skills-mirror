---
name: privacy
description: Audit for App Store privacy compliance - Info.plist purpose strings, permission prompts, data collection, and least-privilege access. Use before App Store submission or when adding new permissions.
---

# Privacy & Permissions Audit

Verify Info.plist purpose strings, permission prompts, and data handling. Ensure least-privilege and clear disclosures.

## When to use this skill

- Before App Store submission (required for App Privacy labels)
- When adding new permissions (camera, microphone, location, etc.)
- When reviewing data collection practices
- After adding analytics or third-party SDKs

## Quick Reference: Required Purpose Strings

| Permission | Info.plist Key | When Required |
|------------|----------------|---------------|
| Camera | `NSCameraUsageDescription` | Photo/video capture |
| Microphone | `NSMicrophoneUsageDescription` | Audio recording |
| Photo Library (read) | `NSPhotoLibraryUsageDescription` | Accessing photos |
| Photo Library (add) | `NSPhotoLibraryAddUsageDescription` | Saving photos only |
| Location (in-use) | `NSLocationWhenInUseUsageDescription` | Location while app open |
| Location (always) | `NSLocationAlwaysAndWhenInUseUsageDescription` | Background location |
| Bluetooth | `NSBluetoothAlwaysUsageDescription` | BLE device connection |
| HealthKit | `NSHealthShareUsageDescription` | Reading health data |
| Tracking (ATT) | `NSUserTrackingUsageDescription` | Cross-app tracking/IDFA |
| Notifications | N/A (runtime prompt) | Push/local notifications |
| Haptics | N/A | No permission needed |

---

## Step 1: Info.plist Audit

### 1.1 Find All Purpose Strings

```bash
# iOS app
rg 'UsageDescription' YourApp/Info.plist 2>/dev/null || echo "Check Xcode target Info tab"

# Watch app
rg 'UsageDescription' "YourApp Watch App/Info.plist" 2>/dev/null
```

### 1.2 Purpose String Localization

```bash
# Check for InfoPlist.strings in both targets
find YourApp -name "InfoPlist.strings" 2>/dev/null
find "YourApp Watch App" -name "InfoPlist.strings" 2>/dev/null
```

**HIG Requirement:** Purpose strings must:
- Explain **why** the app needs permission (not just "uses X")
- Be user-friendly, not technical
- Be localized for all supported languages

**Examples:**
```
❌ "This app uses the camera"
✅ "Take photos of your timer setup to share with friends"
```

---

## Step 2: Permission Request Audit

### 2.1 Find All Permission Requests

```bash
# Notifications
rg --type swift -g '!*Tests*' 'requestAuthorization|UNUserNotificationCenter' YourApp/

# Camera
rg --type swift -g '!*Tests*' 'AVCaptureDevice|requestAccess.*video' YourApp/

# Microphone
rg --type swift -g '!*Tests*' 'requestAccess.*audio|AVAudioSession.*requestRecordPermission' YourApp/

# Photo Library
rg --type swift -g '!*Tests*' 'PHPhotoLibrary|requestAuthorization.*readWrite' YourApp/

# Location
rg --type swift -g '!*Tests*' 'requestWhenInUseAuthorization|requestAlwaysAuthorization|CLLocationManager' YourApp/

# HealthKit
rg --type swift -g '!*Tests*' 'requestAuthorization.*HKHealthStore|HKObjectType' YourApp/

# Bluetooth
rg --type swift -g '!*Tests*' 'CBCentralManager|CBPeripheralManager' YourApp/

# Tracking (ATT)
rg --type swift -g '!*Tests*' 'ATTrackingManager|requestTrackingAuthorization' YourApp/
```

### 2.2 Verify User-Initiated Prompts

> **Critical:** Permission prompts should be **user-initiated**, not on app launch.

```bash
# Check if permissions requested in App/Scene delegate (bad pattern)
rg --type swift 'requestAuthorization|requestAccess' YourApp/App/ 2>/dev/null
rg --type swift 'didFinishLaunching.*request|applicationDidBecomeActive.*request' YourApp/
```

**Fix:** Request permissions when user takes a relevant action:
```swift
// ❌ On launch
func application(_ app: UIApplication, didFinishLaunchingWithOptions: ...) {
    UNUserNotificationCenter.current().requestAuthorization(...)  // BAD
}

// ✅ User-initiated
Button("Enable Reminders") {
    UNUserNotificationCenter.current().requestAuthorization(...)  // GOOD
}
```

---

## Step 3: Data Collection Audit

### 3.1 Analytics & Tracking

```bash
# Common analytics SDKs
rg --type swift -g '!*Tests*' 'Analytics|Firebase|Amplitude|Mixpanel|AppsFlyerLib' YourApp/

# Ad SDKs and attribution
rg --type swift -g '!*Tests*' 'SKAdNetwork|AdServices|GADMobileAds|FBAudienceNetwork' YourApp/
```

### 3.2 User Data Storage

```bash
# UserDefaults (check for sensitive data)
rg --type swift -g '!*Tests*' 'UserDefaults|@AppStorage' YourApp/ | head -20

# Keychain (should be used for sensitive data)
rg --type swift -g '!*Tests*' 'Keychain|SecItem' YourApp/

# CloudKit/iCloud
rg --type swift -g '!*Tests*' 'CKContainer|NSUbiquitousKeyValueStore|\.cloudKitContainerIdentifier' YourApp/
```

**Verify:**
- Sensitive data (tokens, passwords) → Keychain
- Non-sensitive preferences → UserDefaults
- User content sync → Clearly disclosed

### 3.3 Network Requests

```bash
# URLs and network calls
rg --type swift -g '!*Tests*' 'URLSession|URLRequest|https://' YourApp/ | head -20
```

---

## Step 4: App Privacy Label Verification

Check data types for App Store Connect:

| Data Type | Collected? | Used for Tracking? | Linked to User? |
|-----------|------------|-------------------|-----------------|
| Identifiers | ❓ | ❓ | ❓ |
| Usage Data | ❓ | ❓ | ❓ |
| Diagnostics | ❓ | ❓ | ❓ |

```bash
# Check for device identifiers
rg --type swift -g '!*Tests*' 'identifierForVendor|deviceToken|UIDevice\.current' YourApp/
```

---

## Step 5: Watch App Privacy

```bash
WATCH_DIR="YourApp Watch App"

# Watch-specific permissions
rg --type swift 'HealthKit|CLLocationManager|WKExtendedRuntimeSession' "$WATCH_DIR/"

# Data sync to phone
rg --type swift 'WCSession|sendMessage|transferUserInfo' "$WATCH_DIR/"

# Watch InfoPlist.strings localization
find "$WATCH_DIR" -name "InfoPlist.strings" 2>/dev/null
```

---

## Step 6: Third-Party SDK Audit

### 6.1 SPM Dependencies

```bash
# Check Package.resolved for third-party packages
cat *.xcworkspace/xcshareddata/swiftpm/Package.resolved 2>/dev/null | head -40
```

**Verify:** Each SDK's privacy policy is compatible with your App Privacy label.

### 6.2 Monetization SDKs (if applicable)

```bash
# Ad networks require SKAdNetwork configuration
rg 'SKAdNetworkIdentifier' VibratorForReals/Info.plist 2>/dev/null

# AdServices attribution
rg --type swift 'AAAttribution|AdServices' VibratorForReals/
```

---

## Skip Patterns

- `*Tests*/`, `*UITests*/`
- Debug/development configurations

---

## Output Format

| Category | Issues | Status |
|----------|--------|--------|
| Info.plist purpose strings | X | ✅/❌ |
| Purpose string localization | X | ✅/❌ |
| User-initiated prompts | X | ✅/❌ |
| Analytics disclosure | X | ✅/❌ |
| Sensitive data storage | X | ✅/❌ |
| Network endpoints | X | ✅/❌ |
| Third-party SDKs | X | ✅/❌ |
| Watch app privacy | X | ✅/❌ |
