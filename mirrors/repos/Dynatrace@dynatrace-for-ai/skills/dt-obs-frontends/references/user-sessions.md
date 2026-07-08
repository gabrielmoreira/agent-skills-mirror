# User Sessions & Analytics

Track active user sessions, unique users, engagement patterns, and leverage custom properties for business insights.

**Data model:** https://docs.dynatrace.com/docs/observe/digital-experience/new-rum-experience/concepts/data-model

## Contents

- [Schema Reference: `user.sessions`](#schema-reference-usersessions)
- [Core Session Metrics](#core-session-metrics)
- [Active User Session Monitoring](#active-user-session-monitoring)
- [Unique Active User Tracking](#unique-active-user-tracking)
- [Geographic User Distribution](#geographic-user-distribution)
- [Device Type Usage Patterns](#device-type-usage-patterns)
- [Browser Adoption Tracking](#browser-adoption-tracking)
- [Bounce Rate & Session Quality](#bounce-rate--session-quality)
- [Session Duration Distribution](#session-duration-distribution)
- [Session End Reasons](#session-end-reasons)
- [Sessions with User Tags](#sessions-with-user-tags)
- [Sessions with Errors](#sessions-with-errors)
- [Session Journey Overview](#session-journey-overview)
- [New vs Returning Users](#new-vs-returning-users)
- [User Interactions](#user-interactions)
- [Page & View Analysis](#page--view-analysis)

## Schema Reference: `user.sessions`

`user.sessions` contains session-level aggregates produced by the session aggregation service from `user.events`. **Field names differ from `user.events`** — sessions use underscores where events use dots.

> Note: there is no limit on the number of user actions per session in RUM on the latest Dynatrace — this differs from RUM Classic.

**Session identity and context:**
- `dt.rum.session.id` — Session ID (NOT `dt.rum.session_id`)
- `dt.rum.instance.id` — Instance ID
- `frontend.name` — array of frontends involved in session
- `dt.rum.application.type` — `web` or `mobile`
- `dt.rum.user_type` — `real_user`, `synthetic`, or `robot`

**Session aggregates (underscore naming — NOT dot):**

| Field | Description | ⚠️ NOT this |
|-------|-------------|-------------|
| `navigation_count` | Number of navigations | ~~`navigation.count`~~ |
| `user_interaction_count` | Clicks, form submissions | ~~`user_interaction.count`~~ |
| `user_action_count` | User actions | ~~`user_action.count`~~ |
| `request_count` | XHR/fetch requests | ~~`request.count`~~ |
| `event_count` | Total events in session | ~~`event.count`~~ |
| `page_summary_count` | Page views (web) | ~~`page_summary.count`~~ |
| `view_summary_count` | Views (mobile/SPA) | ~~`view_summary.count`~~ |

**Error fields (dot naming — same as events):**
- `error.count`, `error.exception_count`, `error.http_4xx_count`, `error.http_5xx_count`
- `error.anr_count`, `error.csp_violation_count`, `error.has_crash`

**Session lifecycle:**
- `start_time`, `end_time`, `duration` (nanoseconds)
- `end_reason` — `timeout`, `synthetic_execution_finished`, etc.
- `characteristics.is_bounce` — Boolean bounce flag
- `characteristics.has_replay` — Session replay available

**User identity:**
- `user.identifier` — Real user identifier (typically email, username or customerId). **Not always populated** — only present when the frontend explicitly sets the user identity. This is a **session-level field** — query it from `user.sessions` where it is reliably present; on `user.events` it is only available on the standalone `has_user_identifier` event, not on every event. **Sensitive field** — hidden by default; requires the `builtin-sensitive-user-events-and-sessions` fieldset permission. See [Field permissions](https://docs.dynatrace.com/docs/shortlink/rum-on-grail-permissions#field-permissions).
- `dt.rum.instance.id` — Persistent pseudonymous device ID, available on every event and session. Not a real user identity but useful for tracking anonymous users across sessions. On web, based on a persistent cookie (can be deleted by the user).

**Client/device context:**
- `browser.name`, `browser.version`, `device.type`, `os.name`
- `geo.country.iso_code`, `client.isp`
- `client.ip` — **sensitive field**; hidden by default. See [Field permissions](https://docs.dynatrace.com/docs/shortlink/rum-on-grail-permissions#field-permissions).

**Synthetic-only fields:**
- `dt.entity.synthetic_test`, `dt.entity.synthetic_location`, `dt.entity.synthetic_test_step`

**Time window behavior:**
- `fetch user.sessions, from: X, to: Y` only returns sessions that **started** in `[X, Y]` — NOT sessions that were merely active during that window.
- Sessions can last 8h+ (the aggregation service waits 30+ minutes of inactivity before closing a session).
- To find all sessions active during a time window, extend the lookback by at least 8 hours: e.g., to cover events from the last 24h, query `fetch user.sessions, from: now() - 32h`.
- This matters for correlation queries (e.g., matching `user.events` to `user.sessions` by session ID) — a narrow `user.sessions` window will miss long-running sessions and produce false "orphans."

**Session creation delay:**
- The session aggregation service waits for ~30+ minutes of inactivity before closing a session and writing the `user.sessions` record.
- This means **recent events (last ~1 hour) will not yet have a matching `user.sessions` entry** — this is normal, not a data gap.
- When correlating `user.events` with `user.sessions`, exclude recent data (e.g., use `to: now() - 1h`) to avoid counting in-progress sessions as orphans.

**Zombie sessions (events without a `user.sessions` record):**
- Not every `dt.rum.session.id` in `user.events` will have a corresponding `user.sessions` record. The session aggregation service intentionally skips **zombie sessions** — sessions with no real user activity (zero navigations and zero user interactions).
- Zombie sessions contain only background, machine-driven activity (e.g., automatic XHR requests, heartbeats) with no page views or clicks. Serializing them would add no value to users.
- When correlating `user.events` with `user.sessions`, expect a large number of unmatched session IDs. This is **by design**, not a data gap. Filter to sessions with activity before diagnosing orphans:

```dql
fetch user.events, from: now() - 2h, to: now() - 1h
| filter isNotNull(dt.rum.session.id)
| summarize navs = countIf(characteristics.has_navigation),
    interactions = countIf(characteristics.has_user_interaction),
    by: {dt.rum.session.id}
| filter navs > 0 or interactions > 0
```

## Core Session Metrics

**Key Metrics:**

- `dt.frontend.session.active.estimated_count` - Active user sessions (cardinality metric; use `countDistinct()` aggregation)
- `dt.frontend.user.active.estimated_count` - Unique active users (cardinality metric; use `countDistinct()` aggregation)

**Key Fields (Event-Based):**

- `dt.rum.session.id` - Unique session identifier
- `dt.rum.instance.id` - Unique user/device instance
- `user.identifier` - Real user identifier (session-level; query from `user.sessions`)
- `session_properties.__property_name__` - Custom session properties
- `event_properties.__property_name__` - Custom event properties

**Alerting Thresholds:**

- Critical: Active sessions dropping > 50%
- Track user growth trends for capacity planning

## Active User Session Monitoring

Track active user sessions by application:

```dql
timeseries active_sessions = countDistinct(dt.frontend.session.active.estimated_count),
          by: {frontend.name},
          from: now() - 4h
| fieldsAdd avg_sessions = arrayAvg(active_sessions)
| sort avg_sessions desc
```

**Use Case:** Monitor real-time user engagement and capacity planning.

## Unique Active User Tracking

Monitor unique active users:

```dql
timeseries unique_users = countDistinct(dt.frontend.user.active.estimated_count, scalar: true),
          active_sessions = countDistinct(dt.frontend.session.active.estimated_count, scalar: true),
          by: {frontend.name},
          from: now() - 2h
| fieldsAdd sessions_per_user = active_sessions / unique_users
| sort unique_users desc
```

**Use Case:** Understand user engagement patterns and identify power users.

## Geographic User Distribution

Analyze user distribution across regions:

```dql
timeseries unique_users = countDistinct(dt.frontend.user.active.estimated_count, scalar: true),
          active_sessions = countDistinct(dt.frontend.session.active.estimated_count, scalar: true),
          by: {frontend.name, geo.country.iso_code},
          from: now() - 6h
| fieldsAdd sessions_per_user = active_sessions / unique_users
| filter unique_users > 5
| sort unique_users desc
```

**Use Case:** Identify key geographic markets and plan regional infrastructure investments.

## Device Type Usage Patterns

Compare user activity across device types:

```dql
timeseries unique_users = countDistinct(dt.frontend.user.active.estimated_count, scalar: true),
          active_sessions = countDistinct(dt.frontend.session.active.estimated_count, scalar: true),
          by: {frontend.name, device.type},
          from: now() - 4h
| fieldsAdd session_ratio = active_sessions / unique_users
| sort unique_users desc
```

**Use Case:** Optimize mobile-first or desktop-first strategies based on device usage.

## Browser Adoption Tracking

Track browser distribution among active users:

```dql
timeseries unique_users = countDistinct(dt.frontend.user.active.estimated_count, scalar: true),
          active_sessions = countDistinct(dt.frontend.session.active.estimated_count, scalar: true),
          by: {frontend.name, browser.name},
          from: now() - 24h,
          interval: 1h
| filter unique_users > 1
| sort unique_users desc
```

**Use Case:** Prioritize browser compatibility testing based on actual user distribution.

## Bounce Rate & Session Quality

Analyze bounce rate per frontend (uses `user.sessions` directly for accuracy):

```dql
fetch user.sessions, from: now() - 24h
| filter dt.rum.user_type == "real_user"
| expand frontend.name
| summarize
    total_sessions = count(),
    bounces = countIf(characteristics.is_bounce),
    avg_duration_s = avg(toLong(duration)) / 1000000000,
    by: {frontend.name}
| fieldsAdd bounce_rate_pct = round((bounces * 100.0) / total_sessions, decimals: 1)
| sort bounce_rate_pct desc
```

**Use Case:** Identify frontends with high bounce rates indicating UX or performance issues.

## Session Duration Distribution

Analyze how long sessions last (uses `user.sessions` directly):

```dql
fetch user.sessions, from: now() - 24h
| filter dt.rum.user_type == "real_user"
| expand frontend.name
| summarize
    session_count = count(),
    avg_duration_s = avg(toLong(duration)) / 1000000000,
    p50_duration_s = percentile(toLong(duration), 50) / 1000000000,
    p75_duration_s = percentile(toLong(duration), 75) / 1000000000,
    p90_duration_s = percentile(toLong(duration), 90) / 1000000000,
    by: {frontend.name}
| sort p75_duration_s desc
```

**Use Case:** Understand user engagement depth across frontends.

## Session End Reasons

Analyze why sessions close:

```dql
fetch user.sessions, from: now() - 24h
| filter dt.rum.user_type == "real_user"
| expand frontend.name
| summarize
    session_count = count(),
    by: {frontend.name, end_reason}
| sort session_count desc
```

**Use Case:** Distinguish natural timeouts from synthetic or forced session ends.

## Sessions with User Tags

Query sessions with identified users (uses `user.sessions` — the authoritative source for user identity):

```dql
fetch user.sessions, from: now() - 24h
| filter isNotNull(user.identifier)
| expand frontend.name
| summarize
    session_count = count(),
    by: {frontend.name, user.identifier}
| sort session_count desc
| limit 50
```

**Use Case:** Analyze behavior of specific identified users.

> **Sensitive field:** `user.identifier` is hidden by default. Without the `builtin-sensitive-user-events-and-sessions` fieldset permission, this query returns no results. See [Field permissions](https://docs.dynatrace.com/docs/shortlink/rum-on-grail-permissions#field-permissions).

## Session Journey Overview

Trace a user journey through an app. The `event_type` label is derived from characteristics — see [characteristics.md](characteristics.md) for the full derivation logic and priority order.

```dql
fetch user.events, from: now() - 2h
| filter dt.rum.session.id == "<session_id>"
| fieldsAdd event_type = if(characteristics.is_invalid, "Invalid",
    else: if(characteristics.has_error, "Error",
    else: if(characteristics.has_page_summary, "Page summary",
    else: if(characteristics.has_view_summary, "View summary",
    else: if(characteristics.has_app_start, "App start",
    else: if(characteristics.has_user_action, "User action",
    else: if(characteristics.has_navigation, "Navigation",
    else: if(characteristics.has_visibility_change, "Visibility change",
    else: if(characteristics.has_user_interaction, "User interaction",
    else: if(characteristics.has_long_task, "Long task",
    else: if(characteristics.has_event_properties or characteristics.has_session_properties, "Event or session property",
    else: if(characteristics.has_user_identifier, "User identifier",
    else: if(characteristics.has_request, "Request",
    else: if(characteristics.is_api_reported, "API",
    else: if(characteristics.is_self_monitoring, "Selfmonitoring",
    else: "Unknown")))))))))))))))
| fields
    start_time,
    event_type,
    view.name,
    page.name,
    interaction.type,
    error.type
| sort start_time asc
```

**Use Case:** Debug specific user session issues. The default `from: now() - 2h` window covers most active sessions. RUM sessions last up to 8 hours, so extend to `from: now() - 510m` when investigating older sessions — 510 minutes (8.5h) ensures full coverage with a buffer for sessions still being aggregated after the 8h activity window. DQL duration literals are integers only; fractional hours like `8.5h` are not valid.

## Sessions with Errors

Find sessions that experienced errors, using session-level error counts from `user.sessions`.

All users (by anonymous device ID):

```dql
fetch user.sessions, from: now() - 24h, to: now() - 1h
| filter dt.rum.user_type == "real_user"
| filter error.count > 0
| expand frontend.name
| summarize
    session_count = count(),
    total_errors = sum(toLong(error.count)),
    total_exceptions = sum(toLong(error.exception_count)),
    has_crash = countIf(error.has_crash),
    by: {frontend.name, dt.rum.instance.id}
| sort total_errors desc
| limit 20
```

Identified users only (requires user identity to be set in the frontend):

```dql
fetch user.sessions, from: now() - 24h, to: now() - 1h
| filter dt.rum.user_type == "real_user"
| filter error.count > 0
| filter isNotNull(user.identifier)
| expand frontend.name
| summarize
    session_count = count(),
    total_errors = sum(toLong(error.count)),
    total_exceptions = sum(toLong(error.exception_count)),
    has_crash = countIf(error.has_crash),
    by: {frontend.name, user.identifier}
| sort total_errors desc
| limit 20
```

**Use Case:** Identify frustrated users for follow-up. `user.identifier` gives the real user identity (email, username); `dt.rum.instance.id` is the anonymous fallback. Use `to: now() - 1h` to exclude in-progress sessions not yet written to `user.sessions`.

> **Sensitive field:** `user.identifier` is hidden by default. Without the `builtin-sensitive-user-events-and-sessions` fieldset permission, the identified-users variant above returns no results. Use the anonymous variant (by `dt.rum.instance.id`) as a fallback. See [Field permissions](https://docs.dynatrace.com/docs/shortlink/rum-on-grail-permissions#field-permissions).

## New vs Returning Users

Analyze user retention patterns over 30 days:

```dql
fetch user.events, from: now() - 30d
| filter characteristics.has_navigation
| filter dt.rum.user_type == "real_user"
| summarize
    sessions = countDistinct(dt.rum.session.id),
    by: {frontend.name, dt.rum.instance.id}
| summarize
    single_session_users = countIf(sessions == 1),
    returning_users = countIf(sessions > 1),
    by: {frontend.name}
```

**Use Case:** Measure user retention and engagement.

## User Interactions

Analyze user clicks, form inputs, scrolls, and other interactions for UX insights.

**Data Source:** `fetch user.events` with `characteristics.has_user_interaction`

**Key Fields:**

- `interaction.type` - Type: `blur`, `change`, `click`, `drag`, `drop`, `focus`, `key_press`, `long_press`, `mouse_over`, `resize`, `scroll`, `touch`, `zoom`
- `ui_element.name` - Element identifier (aria-label, title, name, etc.)
- `ui_element.custom_name` - Custom name via `data-dt-name` attribute
- `ui_element.tag_name` - HTML tag or mobile component type
- `ui_element.features` - Feature grouping via `data-dt-features`

### All User Interactions

Query all interaction types:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_user_interaction
| summarize
    interaction_count = count(),
    session_count = countDistinct(dt.rum.session.id),
    by: {frontend.name, interaction.type}
| sort interaction_count desc
```

### Click Analysis

Analyze button/link clicks:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_user_interaction
| filter interaction.type == "click"
| summarize
    click_count = count(),
    unique_users = countDistinct(dt.rum.instance.id, precision: 9),
    by: {frontend.name, ui_element.name, ui_element.tag_name}
| sort click_count desc
| limit 30
```

**Use Case:** Identify most-clicked UI elements.

### Feature Usage Analysis

Analyze custom feature areas:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_user_interaction
| filter isNotNull(ui_element.features)
| summarize
    interaction_count = count(),
    unique_users = countDistinct(dt.rum.instance.id, precision: 9),
    by: {frontend.name, ui_element.features}
| sort interaction_count desc
```

**Use Case:** Measure feature adoption using `data-dt-features`.

## Page & View Analysis

Analyze page summaries (web) and view summaries (mobile) for engagement metrics.

**Key Fields:**

- `page.name` / `view.name` - Page/view identifier (`page.name` groups dynamic URLs; preferred over `page.url.path`)
- `page.foreground_time` / `view.foreground_time` - Active time
- `page.background_time` / `view.background_time` - Hidden time
- `view.sequence_number` - View position in session
- `navigation.type` - Navigation type: `hard` (full page reload), `soft` (SPA navigation)

### Page Views Overview

Query all page views (web):

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_page_summary
| summarize
    page_views = count(),
    unique_sessions = countDistinct(dt.rum.session.id),
    unique_users = countDistinct(dt.rum.instance.id, precision: 9),
    by: {frontend.name, page.name}
| sort page_views desc
| limit 30
```

**Use Case:** Identify most visited pages.

### Entry Pages

Analyze landing pages:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_page_summary
| filter view.sequence_number == 1
| summarize
    entry_count = count(),
    unique_sessions = countDistinct(dt.rum.session.id),
    by: {frontend.name, page.name}
| sort entry_count desc
| limit 20
```

**Use Case:** Optimize landing page performance. Captures entry pages for both MPA and SPA frontends — SPA sessions always begin with a full page load that produces a `has_page_summary` event before any soft navigation. Subsequent SPA route changes produce `has_view_summary` events and are not captured here.

### Views per Session

Analyze session depth:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_page_summary or characteristics.has_view_summary
| summarize max_sequence = max(view.sequence_number), by: {frontend.name, dt.rum.session.id}
| summarize
    sessions = count(),
    avg_views = avg(max_sequence),
    p50_views = percentile(max_sequence, 50),
    p90_views = percentile(max_sequence, 90),
    by: {frontend.name}
```

**Use Case:** Measure user journey depth.
