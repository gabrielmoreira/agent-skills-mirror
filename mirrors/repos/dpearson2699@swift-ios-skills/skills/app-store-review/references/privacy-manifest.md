# Privacy Manifest Reference

## Contents
- When a Privacy Manifest Is Required
- Privacy Manifest Structure
- Required API Reason Codes
- Privacy Manifest Keys Reference
- Third-Party SDK Manifests
- Collected Data Types Declaration

## When a Privacy Manifest Is Required

A `PrivacyInfo.xcprivacy` file is required if your app or any dependency uses these API categories:

- File timestamp APIs (`NSPrivacyAccessedAPICategoryFileTimestamp`)
- System boot time APIs (`NSPrivacyAccessedAPICategorySystemBootTime`)
- Disk space APIs (`NSPrivacyAccessedAPICategoryDiskSpace`)
- User defaults (`NSPrivacyAccessedAPICategoryUserDefaults`) when storing user-identifiable data
- Active keyboard APIs (`NSPrivacyAccessedAPICategoryActiveKeyboards`)

## Privacy Manifest Structure

```xml
<!-- PrivacyInfo.xcprivacy -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSPrivacyTracking</key>
    <false/>
    <key>NSPrivacyTrackingDomains</key>
    <array/>
    <key>NSPrivacyCollectedDataTypes</key>
    <array>
        <!-- Declare every data type you collect -->
    </array>
    <key>NSPrivacyAccessedAPITypes</key>
    <array>
        <dict>
            <key>NSPrivacyAccessedAPIType</key>
            <string>NSPrivacyAccessedAPICategoryUserDefaults</string>
            <key>NSPrivacyAccessedAPITypeReasons</key>
            <array>
                <string>CA92.1</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
```

## Required API Reason Codes

| API Category | Code | Reason |
|---|---|---|
| FileTimestamp | `C617.1` | Access files inside app container |
| FileTimestamp | `3B52.1` | Access user-selected files |
| FileTimestamp | `0A2A.1` | Third-party SDK accessed on behalf of user |
| SystemBootTime | `35F9.1` | Measure elapsed time between events |
| DiskSpace | `E174.1` | Check available space before writes |
| UserDefaults | `CA92.1` | Access within your own app |
| UserDefaults | `1C8F.1` | Access within same app group |
| ActiveKeyboards | `3EC4.1` | Customize UI based on active keyboards |

## Privacy Manifest Keys Reference

| Key | Type | Purpose |
|---|---|---|
| `NSPrivacyTracking` | Boolean | Whether the app tracks users (triggers ATT requirement) |
| `NSPrivacyTrackingDomains` | Array of strings | Domains used for tracking (connected only after ATT consent) |
| `NSPrivacyCollectedDataTypes` | Array of dicts | Each data type collected, its purpose, and whether it is linked to identity |
| `NSPrivacyAccessedAPITypes` | Array of dicts | Each required-reason API used and the justification codes |

## Third-Party SDK Manifests

- Verify each SDK contains `PrivacyInfo.xcprivacy` in its bundle
- Ensure SDK reason codes match actual usage
- Update SDK versions when manifests are missing

## Collected Data Types Declaration

Each `NSPrivacyCollectedDataTypes` entry must specify:

- `NSPrivacyCollectedDataType` (category)
- `NSPrivacyCollectedDataTypeLinked` (linked to identity)
- `NSPrivacyCollectedDataTypeTracking` (used for tracking)
- `NSPrivacyCollectedDataTypePurposes` (purposes array)

Apple cross-references manifests with privacy nutrition labels and network traffic. Mismatches cause rejection.
