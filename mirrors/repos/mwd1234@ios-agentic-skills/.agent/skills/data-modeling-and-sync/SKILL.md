---
name: data-modeling-and-sync
description: Data modeling and sync audit for iOS + watchOS. Covers WCSession reliability, conflict resolution, migrations, and offline behavior.
---

# Data Modeling & Sync

Ensure data integrity across iPhone and Apple Watch, with predictable conflict handling and resilient offline behavior.

## When to use this skill

- When adding new data models or persistence changes
- After any WCSession messaging changes
- Before App Store submission
- When users report missing or out-of-sync data

---

## Step 1: Model Stability & Migrations

Checklist:
- Models have stable identifiers (UUID or stable hash)
- Stored models include schema version
- Migration strategy exists for added/removed fields

If using Codable + UserDefaults:
- Provide default values for new fields
- Handle missing keys gracefully

---

## Step 2: WCSession Reliability

```bash
WATCH_DIR="YourApp Watch App"

# WCSession usage
rg --type swift 'WCSession|sendMessage|transferUserInfo|updateApplicationContext' "$WATCH_DIR/"
rg --type swift 'WCSession' YourApp/
```

Checklist:
- `WCSession.isReachable` only used for interactive UI messages
- `transferUserInfo` for eventual delivery
- `updateApplicationContext` for latest state only
- Retries or fallbacks for failures

---

## Step 3: Conflict Resolution

Define a clear strategy:
- Last-write-wins with timestamps, or
- Merge by stable ID, or
- User choice for conflicts

Ensure conflict handling is deterministic and tested.

---

## Step 4: Offline & Edge Cases

Checklist:
- App behaves predictably offline
- Pending changes queued and replayed
- No data loss if watch/app restarts mid-sync

---

## Step 5: Data Integrity Tests

Suggested tests:
- Encode/decode round-trip for each model
- Migration tests between schema versions
- Sync payload validation
- Conflict-resolution unit tests

---

## Output Format

| Category | Issues | Status |
|----------|--------|--------|
| Model stability | X | ✅/❌ |
| Migration strategy | X | ✅/❌ |
| WCSession reliability | X | ✅/❌ |
| Conflict handling | X | ✅/❌ |
| Offline behavior | X | ✅/❌ |
| Integrity tests | X | ✅/❌ |
