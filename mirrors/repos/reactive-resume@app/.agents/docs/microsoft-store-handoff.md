# Microsoft Store handoff

Last updated: **2026-10-20**. Not submitted yet.

The Microsoft Store app is the web app at `https://rxresu.me`, wrapped by [PWABuilder](https://www.pwabuilder.com/) into an MSIX package. Windows runs it in Edge's app host, so every web deploy updates it without a new Store submission.

The PWA is manifest-only by decision (May 2026): no service worker and no offline support. PWABuilder lists the missing service worker as a warning, not a blocker. The Store listing must not claim offline use.

## Before packaging

- [ ] Deploy the current web build. PWABuilder reads the live manifest, and the live manifest still declares `favicon.ico`, PWABuilder's only blocking item.
- [ ] Re-run the [report card](https://www.pwabuilder.com/reportcard?site=https://rxresu.me) and confirm **Package For Stores** is enabled.

## One-time Partner Center setup

1. Sign in to [Partner Center](https://partner.microsoft.com/dashboard/home) with a **personal** Microsoft account. Registration is free for individual developers.
2. **Apps and games → New product → MSIX or PWA app**. Reserve **Reactive Resume**.
3. **Product management → Product identity**: copy **Package ID**, **Publisher ID** and **Publisher display name**.

## Package

1. On the report card, select **Package For Stores → Windows → Generate Package**.
2. Paste the three Product identity values. Keep the other defaults.
3. Download the ZIP. It contains an `.msixbundle` (Windows 10 and 11) and a `.classic.appxbundle` (older Windows 10). Upload both.

Before submitting, install the test package on Windows. Check sign-in with email, Apple and GitHub. OAuth pages are on other origins, so they show an address bar inside the app; that is expected. Also check resume import, PDF and DOCX downloads, and the taskbar jump list (Documents, Applications, Career from manifest `shortcuts`).

## Submission

| Field               | Value                                                                                                       |
| ------------------- | ----------------------------------------------------------------------------------------------------------- |
| Pricing             | Free, all markets                                                                                           |
| Category            | Productivity                                                                                                |
| Age rating          | IARC questionnaire; answer as for Google Play (user-generated public resumes, optional AI features)         |
| Privacy policy      | `https://docs.rxresu.me/legal/privacy-policy`                                                               |
| Support / website   | `https://docs.rxresu.me` / `https://rxresu.me`                                                              |
| Description         | Reuse `apps/mobile/store/metadata.json` (English and ten translations)                                      |
| Screenshots         | PNG, 1366 × 768 or larger. Convert `apps/web/public/screenshots/web/*.webp` (1920 × 1080) to PNG            |
| Certification notes | The app needs sign-in. Give the reviewer account from the mobile handoff in Partner Center only, never here |

Review usually takes 24–48 hours.

## Updates

- Web code, styling and copy changes reach Store users on their next launch. No resubmission is needed.
- Manifest changes need a new package and submission: name, icons, colors, `start_url`, `shortcuts`, or new members such as `share_target` or `file_handlers`. The package copies the manifest at build time.
- Keep manifest `id` at `/?source=pwa`. Changing it makes browsers treat the app as a different app.
- Store installs send `Referer: app-info://platform/microsoft-store` on the first navigation, which can separate Store traffic in analytics.

## Later manifest additions

- `related_applications` (Play `me.rxresu`, App Store `6823975835`) with `prefer_related_applications: false`, once the native apps are public.
- `share_target` (receive a job posting URL) or `file_handlers` (open resume files). Both need app code and the matching native-app feature.
