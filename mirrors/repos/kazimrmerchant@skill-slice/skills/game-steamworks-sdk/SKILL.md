---
name: game-steamworks-sdk
version: 1.1.2
description: "Use when integrating the Steamworks SDK into a PC game — Steam achievements and stats, leaderboards, Steam Cloud saves, Workshop (UGC) modding, matchmaking lobbies and P2P, rich presence, DLC ownership checks, and depot/build uploads via SteamPipe. Triggers on Steamworks, ISteamUserStats, ISteamRemoteStorage, ISteamUGC, ISteamMatchmaking, app_id, steam_appid.txt, SteamPipe, achievements, leaderboards, Workshop. Not for mobile App Store/Play IAP (use game-mobile-store-integration), Stripe/web payments (use stripe-integration), or console certification (use game-console-porting-certification)."
risk: safe
source: opus
date_added: 2026-06-27
---

# Steamworks SDK

Integrate Valve's Steamworks SDK for achievements, leaderboards, Cloud saves, Workshop modding, multiplayer lobbies, DLC ownership checks, and SteamPipe depot builds on PC.

## When to Use

Use this skill when the task involves any of the following Steamworks features:

- **Achievements & stats**: unlocking, incrementing, and storing per-user stats via `ISteamUserStats`.
- **Leaderboards**: global/friend score tables, upload and download.
- **Steam Cloud**: cross-machine save sync via Remote Storage or Auto-Cloud.
- **Workshop / UGC**: publishing, subscribing to, and loading mods via `ISteamUGC`.
- **Lobbies & multiplayer**: matchmaking lobbies, P2P, and Game Networking Sockets.
- **DLC & ownership**: gating content by `IsDlcInstalled` / ownership queries.
- **Rich presence, overlay, depots/builds** via SteamPipe.

### Do Not Use

| If the task is… | Use instead |
|---|---|
| iOS/Android in-app purchases or store submission | `game-mobile-store-integration` |
| Web/server payments, subscriptions | `stripe-integration` |
| Console (Switch/PS/Xbox) cert & online | `game-console-porting-certification` |
| Godot networking high-level API only | `game-godot-multiplayer-networking` |

## Prerequisites

1. A **Steam App ID** issued by Valve (requires a paid Steam Direct app).
2. The **Steamworks SDK** downloaded from the partner site and linked into the project (headers + `steam_api64.lib` / `steam_api64.dll` on Windows).
3. The **Steam client** running and logged in for local development testing.
4. Achievements, stats, and leaderboards **defined on the Steamworks partner site** before the API can reference them.
5. `steamcmd` installed for SteamPipe build uploads (download from Valve's SteamPipe docs).

## Procedure

### 1. Setup Contract

1. Obtain an **App ID** from Valve (paid Steam Direct app).
2. Place `steam_appid.txt` (containing only the App ID as plain text) next to the executable **for development only** — never ship it; the launched-from-Steam client provides the App ID in production.
3. Call `SteamAPI_Init()` early in startup; if it fails, the game was not launched through Steam (or `steam_appid.txt` / running client is missing) — handle gracefully.
4. Call `SteamAPI_RunCallbacks()` **every frame**, and `SteamAPI_Shutdown()` on exit.

```cpp
if (!SteamAPI_Init()) {
    // Not launched via Steam, or Steam client not running.
    // Fail soft: disable Steam features, don't crash.
}
// per frame:
SteamAPI_RunCallbacks();   // REQUIRED — without it, no callbacks fire
// on exit:
SteamAPI_Shutdown();
```

**Hard rule**: `steam_appid.txt` must be excluded from all shipping/release builds. Shipping it lets the game run without ownership checks.

### 2. Achievements & Stats

```cpp
// SDK 1.61+ requests the current user's stats automatically at startup
// (RequestCurrentStats was removed). On older SDKs, call
// SteamUserStats()->RequestCurrentStats() and wait for UserStatsReceived.

// Unlock + push to server (StoreStats is what actually persists/displays).
SteamUserStats()->SetAchievement("ACH_FIRST_BLOOD");
SteamUserStats()->SetStat("enemies_killed", killCount);
SteamUserStats()->StoreStats();   // batch then store once, not per-kill
```

Steps:
1. Define every achievement and stat on the **Steamworks partner site first**; the API only references IDs that already exist there. Undefined IDs cause silent no-ops.
2. Batch `SetStat` / `SetAchievement` calls, then call `StoreStats()` once — calling `StoreStats()` per event is rate-limited and slow.
3. For testing, use `ClearAchievement()` and `ResetAllStats(true)` to reset progress.

### 3. Leaderboards

```cpp
// Find-or-create, then upload. Both are async (SteamCall + callback).
SteamAPICall_t h = SteamUserStats()->FindOrCreateLeaderboard(
    "HighScores", k_ELeaderboardSortMethodDescending,
    k_ELeaderboardDisplayTypeNumeric);
// in the callback, with the handle:
SteamUserStats()->UploadLeaderboardScore(
    leaderboard, k_ELeaderboardUploadScoreMethodKeepBest, score, nullptr, 0);
```

- Use `KeepBest` for high-score tables.
- Use `ForceUpdate` only when the latest value must always win (e.g. fastest current time where lower is better but semantics differ from a simple max).

### 4. Steam Cloud Saves

- **Simplest path**: enable **Auto-Cloud** in the partner site (map file globs to Cloud) — zero code, but no conflict logic.
- **Code path**: use `ISteamRemoteStorage::FileWrite` / `FileRead` with a quota check.
- **Hard rule**: handle the **sync conflict** case (two machines, newer save) explicitly; never blind-overwrite. Blind overwrites lose progress on multi-PC users.
- Keep saves small and versioned; Cloud has per-user quota.

### 5. Workshop (UGC)

```cpp
// Create an item, then update its content/preview, then submit.
SteamAPICall_t c = SteamUGC()->CreateItem(appId, k_EWorkshopFileTypeCommunity);
// in callback (PublishedFileId_t id):
UGCUpdateHandle_t u = SteamUGC()->StartItemUpdate(appId, id);
SteamUGC()->SetItemContent(u, "C:/mod/content");
SteamUGC()->SetItemPreview(u, "C:/mod/preview.png");
SteamUGC()->SubmitItemUpdate(u, "initial version");
```

For consuming mods:
1. Call `GetSubscribedItems` to enumerate subscribed items.
2. Call `GetItemInstallInfo` to get the local folder path.
3. Load mod content from disk.
4. **Never assume a mod folder exists**; users unsubscribe mid-session. Always check validity before loading.

### 6. Lobbies & Networking

- **Matchmaking lobbies** (`ISteamMatchmaking::CreateLobby`, `RequestLobbyList`, lobby data key/values) for grouping players and exchanging connection metadata.
- For transport, prefer **Steam Game Networking Sockets** (`ISteamNetworkingSockets`) over the legacy P2P API — it provides NAT punch-through, relays (SDR), and encryption.
- Lobby data is the meeting point; actual gameplay traffic goes over the sockets connection negotiated via the lobby.

**Hard rule**: do not use the legacy P2P API for new projects. Use Game Networking Sockets for NAT traversal + encryption.

### 7. DLC & Ownership

- Gate DLC content with `SteamApps()->IsDlcInstalled(dlcAppId)`.
- Centralize the App ID; mismatches break ownership and stats queries.

### 8. SteamPipe Builds

| Concept | Meaning |
|---|---|
| **Depot** | A bucket of files (e.g. per-OS, per-DLC) |
| **App build** | A set of depot snapshots published to a branch |
| **Branch** | `default` (live) or beta branches (password-gated) |

Upload via `steamcmd` + a `app_build_*.vdf` script (or the Web/Steamworks UI).

**Hard rule**: always publish to a **beta branch first**, validate, then promote to `default`.

Example PowerShell command to upload a build:

```powershell
steamcmd +login <build_account> +run_app_build /path/to/app_build_480.vdf +quit
```

Replace `<build_account>` with your Steamworks build account (never hardcode live credentials in scripts).

## Pitfalls

1. **Shipping `steam_appid.txt`**: lets the game run without ownership checks — remove it from release builds.
2. **Never calling `RunCallbacks()`**: every async result (stats, leaderboards, UGC) silently never returns.
3. **`StoreStats()` per event**: rate-limited and slow. Batch `SetStat`/`SetAchievement`, then `StoreStats()` once.
4. **Using achievements that aren't defined on the partner site**: API calls no-op silently.
5. **Blind Cloud overwrite**: loses progress on multi-PC users. Implement conflict handling.
6. **Assuming Steam is always present**: `SteamAPI_Init` can fail (offline, no client). Degrade gracefully, never hard-crash.
7. **Legacy P2P for new projects**: use Game Networking Sockets for NAT traversal + encryption.
8. **Hardcoding the App ID in many places**: centralize it; mismatches break ownership/stats.

## Verification

- [ ] `SteamAPI_Init` failure is handled (game still launches, features disabled).
- [ ] `SteamAPI_RunCallbacks()` runs every frame; `SteamAPI_Shutdown()` on exit.
- [ ] `steam_appid.txt` is excluded from shipping builds.
- [ ] Achievements/stats exist on the partner site; stats batched then `StoreStats()`.
- [ ] Leaderboard upload uses the correct method (`KeepBest` vs `ForceUpdate`).
- [ ] Cloud sync handles the multi-machine conflict case.
- [ ] Workshop consumption tolerates missing/unsubscribed items.
- [ ] Builds publish to a beta branch and are validated before promotion to `default`.

## Related Skills

- `game-mobile-store-integration` — the mobile-store equivalent (IAP, store services).
- `game-console-porting-certification` — console online/cert when porting beyond PC.
- `game-godot-multiplayer-networking` / `game-unreal-engine` — engine-side networking these lobbies feed into.

## References

- **Steamworks SDK documentation**: Stats & Achievements, Leaderboards, Remote Storage, UGC, Matchmaking, Game Networking Sockets, SteamPipe — available on the Steamworks partner site.
- Load `references/` files when deeper API surface detail is needed (e.g. callback structures, VDF schema examples). Check the `references/` directory for supplementary docs before writing complex integration code.
