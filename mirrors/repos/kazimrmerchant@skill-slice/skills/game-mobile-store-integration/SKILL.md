---
name: game-mobile-store-integration
version: 1.1.1
description: "Wires mobile games to App Store and Google Play: StoreKit 2 / Play Billing with server-side receipt validation, AdMob/LevelPlay/MAX mediation, and Game Center / Play Games Services v2. Use when the user mentions IAP, receipt validation, App Store Connect, Play Console, rewarded ads, GameKit, or Play Games. Not for Godot export/signing (mobile-development), Steam, Stripe, or console stores. Never grant entitlement from the client SDK alone."
risk: safe
source: opus
date_added: 2026-06-27
---

# Mobile Store Integration

Connect a mobile game to the store platforms it ships on: purchase flows, receipt validation, ad monetization, and social/achievement services on iOS (App Store / StoreKit / Game Center) and Android (Google Play / Billing / Play Games Services).

This skill owns the **store-platform contract** itself — product configuration, the validation server, ad mediation strategy, and social services — which applies across Unity, Unreal, native, and Godot alike. The `mobile-development` skill owns the **Godot engine-side** export and runtime (Billing 5 plugin, StoreKit bridge, AndroidRuntime).

## When to Use

- **In-App Purchases**: configuring consumables, non-consumables, auto-renewing subscriptions; the buy → validate → grant flow.
- **Receipt validation**: verifying purchases **server-side** against Apple/Google to defeat client tampering.
- **Ad monetization**: integrating banner/interstitial/**rewarded** ads via a mediation layer (AdMob, Unity LevelPlay, AppLovin MAX).
- **Social services**: Game Center / Play Games Services authentication, achievements, leaderboards, and cloud saved games.
- **Store submission**: App Store Connect / Play Console product setup, metadata, review-readiness.

### Do Not Use

| If the task is… | Use instead |
|---|---|
| Godot export, signing, AAB/IPA build, Godot billing plugin wiring | `mobile-development` |
| Steam achievements/leaderboards/Workshop/Cloud on PC | `steamworks-sdk` |
| Web/server credit-card payments, Stripe subscriptions | `stripe-integration` |
| Console store/online cert (Switch/PS/Xbox) | `console-porting-certification` |

## Prerequisites

- A paid Apple Developer Program membership (for App Store Connect / StoreKit 2 / Game Center).
- A Google Play Developer account (one-time $25 registration fee) with a configured app in the Play Console.
- A backend server you control for receipt validation — never grant entitlement on the client alone.
- For Google Play Developer API: a Google Cloud service account with the `Android Publisher` role and a downloaded JSON key.
- For Apple App Store Server API: an issuer ID, key ID, and downloaded `.p8` key from App Store Connect → Users and Access → Keys.
- For ad mediation: accounts on each ad network (AdMob, Unity LevelPlay, AppLovin MAX) plus the mediation SDK integrated into your build.
- Store products (IAPs, achievements, leaderboards) defined in App Store Connect / Play Console **before** the client API references their IDs.

## Procedure

### 1. Purchase Flow (the only correct shape)

```
client: request products  ──►  store SDK returns localized price
client: user taps buy     ──►  store SDK runs the payment sheet
store:  returns a signed receipt / purchase token
   │
   ▼  send token to YOUR server (never grant on the client alone)
server: verify with Apple/Google API  ──►  grant entitlement, record txn
   │
   ▼
client: finish/acknowledge the transaction  ◄── only after server confirms
```

**Cardinal rule**: the client never decides a purchase is valid. A jailbroken/rooted device can fake any client-side "success." Entitlement is granted by your server after it verifies the receipt with the platform.

### 2. Configure In-App Purchase Products

| Type | iOS (StoreKit) | Android (Play Billing) | Must be |
|---|---|---|---|
| Consumable (gems, lives) | Consumable | INAPP, consumed after grant | Consumed so it can be re-bought |
| Non-consumable (remove ads, unlock) | Non-Consumable | INAPP, acknowledged | Restorable; never consumed |
| Auto-renewing subscription | Auto-Renewable | SUBS | Server-tracked renewal state |

1. **Define products in the store console first** — App Store Connect → In-App Purchases, or Play Console → Monetize → Products. The client API only references IDs that already exist there.
2. **Consumables** must be **consumed** (Android) / finished (iOS) after the server grants them — otherwise the user can't buy again.
3. **Non-consumables & subscriptions** must support **Restore Purchases** (Apple requires a visible restore path). Re-query entitlements on fresh installs / new devices.
4. **Acknowledge within the window**: Google Play auto-refunds any purchase not acknowledged within 3 days. Acknowledge (or consume) only after your server grants.
5. **Display store-returned localized prices** — never hardcoded strings. Currencies, tiers, and taxes vary by region.

### 3. Implement Server-Side Receipt Validation

#### Apple (StoreKit 2)

1. Use **StoreKit 2** only — StoreKit 1 and `/verifyReceipt` are deprecated.
2. On the server, verify the **JWS signature against Apple's root CA** — don't just decode the payload.
3. Check `bundleId`, `environment` (sandbox vs production), and `transactionId` in the verified payload.
4. Use the **App Store Server API** + **App Store Server Notifications v2** as the source of truth for subscription state, refunds, and revocations.
5. Persist every `transactionId` to detect replays.

#### Google (Play Billing)

1. Ship the current **Play Billing Library major** — Play enforces a minimum version yearly and blocks updates on stale majors.
2. Verify the purchase token with the **Google Play Developer API**:
   - `purchases.products.get` for one-time purchases
   - `purchases.subscriptionsv2.get` for subscriptions
3. Use a service account with the `Android Publisher` role; authenticate with the downloaded JSON key.
4. Acknowledge/consume server-side via the API after granting.
5. Subscribe to **Real-time Developer Notifications (RTDN)** over Pub/Sub for renewals, cancels, refunds.

#### Both platforms

- Persist every transaction id / purchase token to **detect replays** — the same token submitted twice must not double-grant.
- Validate the **bundle id / package name** and product id in the receipt match your app — don't trust the client's claim of what was bought.

### 4. Integrate Ad Mediation

```
Game ── rewarded ad request ──► Mediation SDK (AdMob / LevelPlay / MAX)
                                      │ real-time bidding across networks
                                      ▼ highest-paying fill wins
                              onUserEarnedReward ──► grant reward ONCE
```

1. Use a **mediation** layer, not a single ad network — it fills inventory and raises eCPM via **real-time bidding** (waterfalls are legacy; prefer bidding-first setups). Don't hand-integrate five SDKs separately. LevelPlay is Unity's mediation (formerly ironSource).
2. **Rewarded ads**: grant the reward only in the `onUserEarnedReward` / completion callback, exactly once. Never grant on "ad opened" or on the close callback.
3. **Preload** interstitials/rewarded ahead of the moment you show them; a cold request at the show point fails to fill and feels broken.
4. Respect **ATT (App Tracking Transparency)** on iOS and **consent (UMP/GDPR/CMP)** before initializing ad SDKs, or you violate policy and lose fill.
5. Attribution is privacy-preserving now: **AdAttributionKit** (successor to SKAdNetwork) on iOS, **Privacy Sandbox Attribution Reporting** alongside GAID on Android. Don't build UA measurement on device-ID fingerprinting.
6. Don't interrupt active gameplay with interstitials; show at natural breaks (level end), and cap frequency.

### 5. Wire Social Services (Game Center / Play Games)

Use **Play Games Services v2** on Android — v1 sign-in is shut down; v2 does automatic sign-in at launch with no consent screen for basic auth.

| Capability | Game Center (iOS) | Play Games Services v2 (Android) |
|---|---|---|
| Sign-in | `GKLocalPlayer.authenticate` | `GamesSignInClient` / one-tap |
| Achievements | `GKAchievement` (percent → 100 = unlocked) | incremental or standard, defined in console |
| Leaderboards | `GKLeaderboard` submit/load | `LeaderboardsClient` submit/load |
| Cloud saves | iCloud / GKSavedGame | Snapshots API (handle conflict resolution) |

1. Define achievements/leaderboards in **App Store Connect / Play Console first**; the API only references IDs that already exist there.
2. Authenticate **early and silently**; degrade gracefully if the user declines or is offline — never block game entry on a social sign-in.
3. For cloud saves, you **must** implement conflict resolution (two devices, divergent saves). The Snapshots/GKSavedGame API surfaces conflicts; don't blind-overwrite.

### 6. Prepare for Store Submission

1. **iOS**: app must have at least one IAP submitted **with the app's first review** if monetization is core; provide a **sandbox tester** account flow; privacy nutrition labels and ATT usage string are mandatory.
2. **Android**: upload a **signed AAB**; create products in Play Console (they're inactive until the app is published to a track); use **license testers** for unpaid sandbox purchases.
3. **Stay on the platform treadmill**: Play raises the required **target API level** every August; Apple raises the minimum **Xcode/SDK** every spring. A store-compliant build today is rejectable next year without touching your code.
4. **Alternative billing / external purchase links** (EU DMA, Google user-choice billing, US anti-steering entitlements) are region- and program-gated compliance work — don't treat them as the default flow, and keep the standard store flow working everywhere.
5. Test purchases in **sandbox/test tracks** before production — real charges in review get the build rejected.

## Pitfalls

1. **Client-side entitlement**: granting the item because the client SDK said "purchased." Always validate on a server you control.
2. **Not consuming consumables**: user buys 100 gems once and can never buy again. Consume after grant.
3. **No restore path**: Apple rejects apps with non-consumables/subscriptions that lack Restore Purchases.
4. **Ignoring the Google acknowledge window**: unacknowledged purchases auto-refund in 3 days — the user is charged then refunded and you look broken.
5. **Granting rewarded reward on the wrong callback**: granting on close instead of `onUserEarnedReward` lets users skip the ad and still get paid.
6. **Initializing ad SDKs before consent/ATT**: policy violation, lost fill, possible removal.
7. **Trusting receipt fields blindly**: always re-verify bundle/package id and product id against your catalog; check for replayed transaction ids.
8. **Hardcoding prices**: always show the **store-returned localized price**, never a string you typed — currencies, tiers, and taxes vary by region.
9. **Blocking launch on social sign-in**: make Game Center/Play Games optional and async.
10. **Using Play Games Services v1**: v1 sign-in is shut down. Use v2 only.
11. **Using StoreKit 1 / `/verifyReceipt`**: deprecated. Build on StoreKit 2 and JWS signature verification.
12. **Stale Play Billing Library major**: Play blocks updates on outdated majors. Track the yearly minimum bump.

## Verification

- [ ] Every purchase is verified **server-side** before entitlement is granted.
- [ ] Consumables are consumed/finished after grant; non-consumables & subs support Restore.
- [ ] Google purchases are acknowledged within 3 days; Apple transactions finished after server confirm.
- [ ] Transaction ids / purchase tokens are persisted and replay is rejected.
- [ ] Rewarded reward granted exactly once in the earned-reward callback.
- [ ] ATT (iOS) and consent (UMP/GDPR) handled before ad SDK init.
- [ ] Achievements/leaderboards exist in the store console before the API references them.
- [ ] Cloud saves implement conflict resolution.
- [ ] Localized store prices are displayed, not hardcoded strings.
- [ ] Purchases tested in sandbox / license-tester tracks before production.
- [ ] Play Games Services v2 used (not v1) on Android.
- [ ] StoreKit 2 used (not StoreKit 1) on iOS.
- [ ] Play Billing Library on the current major version.

## Related Skills

- `mobile-development` — Godot engine-side export, signing, and the in-engine billing/ads plugins this contract sits behind.
- `steamworks-sdk` — The PC/Steam equivalent for ownership, achievements, leaderboards, and Cloud.
- `stripe-integration` — Web/server payments when selling outside the mobile stores.
- `console-porting-certification` — Console store and online service equivalents when porting beyond mobile.

## References

- Apple StoreKit 2, App Store Server API, and App Store Server Notifications v2 documentation.
- Google Play Billing Library and Google Play Developer API (purchases & subscriptions) documentation.
- Google Mobile Ads (AdMob) mediation, Unity LevelPlay, and AppLovin MAX integration guides.
- Apple AdAttributionKit and Android Privacy Sandbox Attribution Reporting documentation.
- Apple GameKit (Game Center) and Google Play Games Services v2 documentation.
