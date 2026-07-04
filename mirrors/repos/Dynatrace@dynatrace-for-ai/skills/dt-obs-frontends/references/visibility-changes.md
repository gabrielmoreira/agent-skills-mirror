# Visibility Changes & Tab Activity

Monitor when users switch browser tabs or apps to understand engagement patterns.

**Web (RUM JavaScript) only** — mobile captures visibility state changes as part of navigation events, not as separate visibility change events.

**Semantic dictionary:** https://docs.dynatrace.com/docs/semantic-dictionary/model/rum/user-events/navigation-related#visibility-change

**Data Source:** `fetch user.events` with `characteristics.has_visibility_change`

**Key Fields:**

- `visibility.state` - Visibility state when the event fired: `foreground`, `background`, `prerendering`, `unknown` (experimental; RUM JavaScript only)
  - Populated on **all** web events, not only visibility-change events
  - On visibility-change events: only `foreground` and `background` appear
  - On all other event types (requests, user actions, page summaries, etc.): `foreground` and `background` reflect whether the page was visible when the event occurred; `prerendering` means the page was prerendered via the Speculation Rules API; `unknown` means the JS agent loaded too late to determine the state
- `duration` - Time spent in the visibility state (visibility-change events only)
- `dom_event.is_trusted` - Whether the visibility change came from a real user vs. a synthetic event (experimental)

## Contents

- [Visibility State Distribution](#visibility-state-distribution)
- [Tab Switch Frequency](#tab-switch-frequency)
- [Time in Background](#time-in-background)
- [Visibility by Page](#visibility-by-page)
- [Visibility Patterns Over Time](#visibility-patterns-over-time)
- [Session Engagement Quality](#session-engagement-quality)
- [Device Type Comparison](#device-type-comparison)
- [Background Activity](#background-activity)
- [Prerendering Activity](#prerendering-activity)
- [Unknown Visibility State](#unknown-visibility-state)

## Visibility State Distribution

Analyze visibility patterns:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_visibility_change
| summarize
    change_count = count(),
    unique_sessions = countDistinct(dt.rum.session.id),
    by: {frontend.name, visibility.state}
| sort change_count desc
```

**Use Case:** Understand foreground vs background activity.

## Tab Switch Frequency

Count visibility changes per session:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_visibility_change
| summarize change_count = count(), by: {frontend.name, dt.rum.session.id}
| summarize
    sessions = count(),
    avg_switches = avg(change_count),
    p50_switches = percentile(change_count, 50),
    p90_switches = percentile(change_count, 90),
    by: {frontend.name}
```

**Use Case:** Measure user attention patterns.

## Time in Background

Calculate background duration:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_visibility_change
| filter visibility.state == "background"
| summarize
    background_events = count(),
    total_background_time = sum(duration),
    avg_background_duration = avg(duration),
    by: {frontend.name}
```

**Use Case:** Understand how long users leave tabs inactive.

## Visibility by Page

Analyze which pages users leave:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_visibility_change
| filter visibility.state == "background"
| summarize
    background_count = count(),
    avg_background_time = avg(duration),
    by: {frontend.name, page.name}
| sort background_count desc
| limit 20
```

**Use Case:** Identify pages with engagement issues.

## Visibility Patterns Over Time

Track engagement trends:

```dql
fetch user.events, from: now() - 24h
| filter characteristics.has_visibility_change
| summarize
    foreground = countIf(visibility.state == "foreground"),
    background = countIf(visibility.state == "background"),
    by: {frontend.name, time_bucket = bin(start_time, 1h)}
| sort time_bucket asc
```

**Use Case:** Correlate engagement with time of day. 24 one-hour buckets show clear peak/off-peak patterns.

## Session Engagement Quality

Classify session engagement by foreground ratio, excluding synthetic visibility changes:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_visibility_change
| filter dom_event.is_trusted
| summarize
    foreground_count = countIf(visibility.state == "foreground"),
    background_count = countIf(visibility.state == "background"),
    by: {frontend.name, dt.rum.session.id}
| fieldsAdd engagement_ratio = foreground_count / (foreground_count + background_count)
| summarize
    high_engagement = countIf(engagement_ratio > 0.7),
    medium_engagement = countIf(engagement_ratio >= 0.3 and engagement_ratio <= 0.7),
    low_engagement = countIf(engagement_ratio < 0.3),
    by: {frontend.name}
```

**Use Case:** Segment users by attention level. The `foreground_count + background_count` denominator is always ≥ 1 — visibility change events exclusively use `visibility.state == "foreground"` or `"background"`, so every event surviving the filter contributes to one of the two counts.

## Device Type Comparison

Compare visibility patterns across devices:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_visibility_change
| summarize
    visibility_changes = count(),
    background_count = countIf(visibility.state == "background"),
    by: {frontend.name, device.type}
| fieldsAdd background_pct = 100.0 * background_count / visibility_changes
```

**Use Case:** Compare mobile vs desktop engagement.

## Background Activity

Query non-visibility-change events that occurred while the page was in the background. This reveals polling behavior, background data fetches, and other activity that happens without user attention.

Count all events that fired while backgrounded, excluding the visibility-change events themselves:

```dql
fetch user.events, from: now() - 2h
| filter visibility.state == "background"
| filter isFalseOrNull(characteristics.has_visibility_change)
| summarize
    background_events = count(),
    unique_sessions = countDistinct(dt.rum.session.id),
    by: {frontend.name}
| sort background_events desc
```

Find frontends with high background request rates:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_request
| summarize
    total_requests = count(),
    background_requests = countIf(visibility.state == "background"),
    by: {frontend.name}
| fieldsAdd background_pct = 100.0 * background_requests / total_requests
| filter background_requests > 0
| sort background_pct desc
```

**Use Case:** A high background request percentage indicates polling or keep-alive traffic that runs regardless of whether the user is watching. `isFalseOrNull(characteristics.has_visibility_change)` excludes the visibility-change transition events themselves — only events that happened while already backgrounded are counted. `isFalseOrNull` is preferred over `isNull` because it also catches the case where the field is explicitly `false` rather than absent.

## Prerendering Activity

Query events from pages that were in a prerendered state when the event fired. These appear on non-visibility-change event types (page summaries, navigations, requests, etc.) where `visibility.state == "prerendering"`. Use a 24-hour window — prerendering events are sparse on tenants where the Speculation Rules API is not actively used.

```dql
fetch user.events, from: now() - 24h
| filter visibility.state == "prerendering"
| summarize
    event_count = count(),
    unique_sessions = countDistinct(dt.rum.session.id),
    by: {frontend.name}
| sort event_count desc
```

**Use Case:** Monitor Speculation Rules API effectiveness — events with `prerendering` state indicate pages loaded in the background before the user navigated to them. A high count means prefetching is active; a very high count across many sessions may indicate over-aggressive speculation rules causing unnecessary resource consumption.

## Unknown Visibility State

Query events where the visibility state could not be determined. Occurs when the JS agent loads via a tag manager (late load) and creates events with a `start_time` before agent initialisation — the agent cannot know what state the page was in before it loaded.

```dql
fetch user.events, from: now() - 24h
| filter visibility.state == "unknown"
| summarize
    event_count = count(),
    by: {frontend.name, browser.name, browser.version}
| sort event_count desc
```

**Use Case:** Identify pages where late-loading tag managers prevent accurate visibility tracking. Group by browser to rule out browser-specific causes — unknown state from late injection appears across all browsers, while a browser-specific pattern points to a different root cause.
