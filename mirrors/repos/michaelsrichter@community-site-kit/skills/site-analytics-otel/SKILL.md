---
name: site-analytics-otel
description: >-
  Instrument a static community website with Google Analytics 4, Microsoft Clarity and OpenTelemetry
  custom events and metrics sent to Azure Monitor (Application Insights), with consent, Global Privacy
  Control and a documented event taxonomy. Use when asked to add analytics, track clicks or interactions,
  add custom events/metrics, set up GA4 or Clarity, send telemetry to Azure Monitor, or add a new tracked
  feature (every new button should get an event).
---

# Analytics: GA4 + Clarity + OpenTelemetry to Azure Monitor

## Architecture (starter: `src/scripts/analytics.ts`, `api/src/functions/telemetry.js`)

- **First-party telemetry, no cookies:** the browser batches events and sends them with `sendBeacon` to
  `/api/telemetry` (same-origin). The Function validates (`api/src/telemetry-validate.js`: allow-listed
  event names and property keys, safe-character regex, ≤ 8 KB, ≤ 25 items, origin check, simple rate limit)
  and records OpenTelemetry metrics and log events with `@azure/monitor-opentelemetry` using the
  `APPLICATIONINSIGHTS_CONNECTION_STRING` app setting.
- **GA4 and Clarity load only with consent** (opt-in by default; the owner may choose opt-out). Honor
  `navigator.globalPrivacyControl`. Consent banner + "Privacy choices" link in the footer. GA4 with
  `allow_google_signals: false`, ad storage denied. Clarity with `consentv2`. Removing consent deletes
  their cookies.
- IDs come from build-time env (`PUBLIC_GA4_ID`, `PUBLIC_CLARITY_ID`) set as GitHub Actions variables;
  empty = disabled.
- CSP must list the GA/Clarity script and connect origins only when IDs are set (`scripts/postbuild.mjs`).

## Declarative tracking

Any element with `data-track="<event>"` is tracked on click with `data-track-method`,
`data-track-location` (or the nearest ancestor's), `data-track-target`. Scripts call `track(name, props)`.
**When you add an event name, add it in three places:** the client `GA_EVENTS` set, the API allow-list
`EVENT_NAMES` (and any new prop key in `PROP_KEYS`), and `docs/analytics.md`.

## Event taxonomy (copy and extend)

| Event | When | Props |
| --- | --- | --- |
| `page_view` | Every page (OTel; GA4 records its own) | `page_type` |
| `view_event` | Event page | `event_slug`, `event_status`, `days_until` |
| `select_event` | Clicked an event card or "View event details" | `location` |
| `add_to_calendar` | Google, Outlook, Office 365, `.ics`, subscribe | `method`, `location` |
| `share`, `share_open`, `copy_failed` | Share actions | `method`, `event_slug`, `location` |
| `get_directions` | Google/Apple Maps | `method`, `location` |
| `outbound_click` | Teacher/band/organizer/venue site or social, phone, email, reviews | `method`, `location`, `target` (domain) |
| `click_hotline`, `click_email`, `newsletter_click` | Contact actions | `location` |
| `filter_events` | Filters changed | `filter`, `value`, `results` |
| `view_calendar_month` | Month navigation | `method` |
| `show_more` | "Show N more" / "Show fewer" | `method` (expand/collapse), `location` (list), `results` |
| `theme_change` | Light / Dark / Auto | `method`, `location` |
| `faq_open` | FAQ question opened | `question` |
| `empty_state` | Visitor saw "no upcoming events" | `location` |
| `consent_update` | Analytics choice | `value`, `mode` |
| `web_vital` | LCP, INP, CLS, FCP, TTFB (OTel only) | `metric`, `rating` |

Locations: `home_next`, `home`, `event`, `event_aside`, `action_bar`, `events`, `card`, `calendar`, `map`,
`map_pin`, `map_list`, `map_popup`, `venue`, `performer`, `community`, `contact`, `header`, `menu`, `footer`.

## OpenTelemetry metrics (Application Insights `customMetrics`)

`<prefix>` comes from the `METRICS_PREFIX` app setting (default `site`).

| Metric | Type | Dimensions |
| --- | --- | --- |
| `<prefix>.web.page_views` | Counter | `page_type`, `release` |
| `<prefix>.web.event_views` | Counter | `page_type`, `event_status`, `release` |
| `<prefix>.web.interactions` | Counter | `action`, `method`, `location`, `page_type` |
| `<prefix>.web.consent_updates` | Counter | `value`, `mode` |
| `<prefix>.web.vitals.lcp/.inp/.fcp/.ttfb` (ms), `.cls` (×1000) | Histogram | `page_type`, `rating` |
| `<prefix>.telemetry.rejected` | Counter | `reason` |
| `<prefix>.cms.auth` | Counter | `result` |

## Azure setup

- Bicep creates a Log Analytics workspace + workspace-based Application Insights; `deploy.ps1` copies the
  connection string into the Static Web App app setting (never printed).
- Useful KQL: `customMetrics | where name == "site.web.interactions" | summarize sum(valueSum) by tostring(customDimensions.action)`.

## Tests

- API unit tests: rejects bad origin, oversized body, unknown event names, unsafe values; accepts a valid batch.
- Smoke: same-origin beacon → 204; cross-origin → 403.
- Privacy page lists what is measured, cookies, and how to change the choice.
