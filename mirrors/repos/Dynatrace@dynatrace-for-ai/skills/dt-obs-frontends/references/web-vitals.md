# Web Vitals

Monitor web vitals across page loads and SPA navigations. These metrics directly impact SEO rankings and user experience.

**Reference:** https://web.dev/articles/vitals

**Data Source:** `fetch user.events` scoped by event characteristic — web vitals fields are only available on specific event types:

| Characteristic | Web vitals fields available |
|---|---|
| `characteristics.has_page_summary` | LCP, FCP, FID, INP, CLS, first_input, first_paint, TTFB — all 8 (primary use case) |
| `characteristics.has_view_summary` | Same 8 fields (use for SPA soft navigation analysis) |
| `characteristics.has_user_action` | LCP, FID, INP, CLS, first_input — 5 fields |
| `characteristics.has_request` | TTFB only |

**Concepts:** https://docs.dynatrace.com/docs/observe/digital-experience/new-rum-experience/web-frontends/concepts/pages-views-and-navigations

**Core Web Vitals** — the three metrics in Google's CWV program (https://web.dev/articles/vitals):

- **LCP (Largest Contentful Paint)**: Good < 2.5s | Needs Improvement 2.5–4.0s | Poor > 4.0s (field: `web_vitals.largest_contentful_paint`, nanoseconds; metric: `dt.frontend.web.page.largest_contentful_paint`, milliseconds)
- **INP (Interaction to Next Paint)**: Good < 200ms | Needs Improvement 200–500ms | Poor > 500ms (field: `web_vitals.interaction_to_next_paint`, nanoseconds; metric: `dt.frontend.web.page.interaction_to_next_paint`, milliseconds)
- **CLS (Cumulative Layout Shift)**: Good < 0.1 | Needs Improvement 0.1–0.25 | Poor > 0.25 (field: `web_vitals.cumulative_layout_shift`, double; metric: `dt.frontend.web.page.cumulative_layout_shift` stores CLS × 10,000 as an integer (e.g. 0.127 → 1270) — use event-based queries for threshold-based classification)

**Other Web Vitals** — tracked alongside Core Web Vitals but not part of the CWV program:

- **FCP (First Contentful Paint)**: Good < 1.8s | Needs Improvement 1.8–3.0s | Poor > 3.0s (field: `web_vitals.first_contentful_paint`, nanoseconds; no dedicated metric — use event-based query)
- **FID (First Input Delay)** *(deprecated, replaced by INP in March 2024)*: Good < 100ms | Needs Improvement 100–300ms | Poor > 300ms (field: `web_vitals.first_input_delay`, nanoseconds). Include FID queries only when working with historical data from tenants that collected it before March 2024.

> **Unit difference:** Event-based `web_vitals.*` fields store durations in **nanoseconds** — use duration literals (`2500ms`, `4s`) for thresholds. The `dt.frontend.web.page.*` metrics (LCP, INP, FID) store values in **milliseconds** — use plain numbers (`2500`, `4000`) for thresholds. Exception: `dt.frontend.web.page.cumulative_layout_shift` stores CLS × 10,000 as an integer — not milliseconds.

**Alerting:** Critical if p75 values fall into "poor" range for more than 1 hour

## Contents

- [Metric-Based Queries](#metric-based-queries)
  - [Core Web Vitals Overview](#core-web-vitals-overview)
  - [Core Web Vitals Trend](#core-web-vitals-trend)
- [Event-Based Queries](#event-based-queries)
  - [Core Web Vitals (Page Loads)](#core-web-vitals-page-loads)
  - [Core Web Vitals (SPA Views)](#core-web-vitals-spa-views)
  - [Largest Contentful Paint (LCP)](#largest-contentful-paint-lcp) — Core Web Vital
  - [Interaction to Next Paint (INP)](#interaction-to-next-paint-inp) — Core Web Vital
  - [Cumulative Layout Shift (CLS)](#cumulative-layout-shift-cls) — Core Web Vital
  - [First Contentful Paint (FCP)](#first-contentful-paint-fcp) — Diagnostic Metric
  - [First Input Delay (FID)](#first-input-delay-fid) — Deprecated (March 2024)
  - [Web Vitals Trends](#web-vitals-trends)
  - [Web Vitals by Page](#web-vitals-by-page)
  - [Web Vitals by View (SPA)](#web-vitals-by-view-spa)
  - [Web Vitals by Device](#web-vitals-by-device)

## Metric-Based Queries

> **`scalar: true` vs array (`[]`) notation:** `scalar: true` collapses the entire time window into one value per row. Use it for overall current state, sorting, and alerting. Without `scalar: true`, metric columns are arrays (one value per interval) — use `[]` for trend analysis.

### Core Web Vitals Overview

Current p75 state per frontend with threshold ratings. Metric values are in **milliseconds**:

```dql
timeseries
    lcp_p75 = percentile(dt.frontend.web.page.largest_contentful_paint, 75, scalar: true),
    inp_p75 = percentile(dt.frontend.web.page.interaction_to_next_paint, 75, scalar: true),
    cls_p75 = percentile(dt.frontend.web.page.cumulative_layout_shift, 75, scalar: true),
    by: {frontend.name},
    from: now() - 2h
| fieldsAdd
    lcp_rating = if(isNull(lcp_p75), "no_data", else: if(lcp_p75 < 2500, "good", else: if(lcp_p75 < 4000, "needs_improvement", else: "poor"))),
    inp_rating = if(isNull(inp_p75), "no_data", else: if(inp_p75 < 200, "good", else: if(inp_p75 < 500, "needs_improvement", else: "poor")))
| sort lcp_p75 desc
```

**Use Case:** **Overall state** across the time window. Monitor which frontends are in "poor" range for CWV alerting. LCP and INP are in milliseconds — thresholds match directly. The CLS metric stores values as CLS × 10,000 (e.g. 0.127 → 1270); use the event-based CLS query for threshold-based classification.

### Core Web Vitals Trend

Track CWV trends over time for regression detection:

```dql
timeseries
    lcp_p75 = percentile(dt.frontend.web.page.largest_contentful_paint, 75),
    inp_p75 = percentile(dt.frontend.web.page.interaction_to_next_paint, 75),
    cls_p75 = percentile(dt.frontend.web.page.cumulative_layout_shift, 75),
    by: {frontend.name},
    from: now() - 24h
```

**Use Case:** **Per-bucket trend.** Detect CWV regressions after deployments. LCP and INP values are in milliseconds; the CLS metric stores CLS × 10,000 — suitable for relative trend comparison only.

## Event-Based Queries

### Core Web Vitals (Page Loads)

Overview of Core Web Vitals from page summary events (traditional full-page navigations):

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_page_summary
| summarize
    lcp_p75 = percentile(web_vitals.largest_contentful_paint, 75),
    inp_p75 = percentile(web_vitals.interaction_to_next_paint, 75),
    cls_p75 = percentile(web_vitals.cumulative_layout_shift, 75),
    by: {frontend.name}
```

**Use Case:** Baseline CWV health per frontend for traditional multi-page applications. For per-page breakdown see [Web Vitals by Page](#web-vitals-by-page).

### Core Web Vitals (SPA Views)

Overview of Core Web Vitals from view summary events (SPA soft navigations):

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_view_summary
| filter dt.rum.application.type == "web"
| summarize
    lcp_p75 = percentile(web_vitals.largest_contentful_paint, 75),
    inp_p75 = percentile(web_vitals.interaction_to_next_paint, 75),
    cls_p75 = percentile(web_vitals.cumulative_layout_shift, 75),
    by: {frontend.name}
```

**Use Case:** Baseline CWV health per frontend for single-page applications. For per-route breakdown see [Web Vitals by View (SPA)](#web-vitals-by-view-spa).

**The following three sections cover the individual Core Web Vitals: LCP, INP, CLS.**

### Largest Contentful Paint (LCP)

Monitor LCP performance:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_page_summary
| summarize
    p50_lcp = percentile(web_vitals.largest_contentful_paint, 50),
    p75_lcp = percentile(web_vitals.largest_contentful_paint, 75),
    p90_lcp = percentile(web_vitals.largest_contentful_paint, 90),
    by: {frontend.name}
| fieldsAdd
    lcp_rating = if(
        p75_lcp < 2500ms,
        "good",
        else: if(
            p75_lcp < 4s,
            "needs_improvement",
            else: "poor"
        )
    )
```

**Use Case:** LCP measures when the largest visible content element finishes loading — the primary page-load Core Web Vital for SEO. Use `lcp_rating` to rank frontends; for per-page breakdown see [Web Vitals by Page](#web-vitals-by-page).

### Interaction to Next Paint (INP)

Monitor responsiveness — the Core Web Vital for interactivity (replaced FID as a Core Web Vital in March 2024):

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_page_summary
| summarize
    p75_inp = percentile(web_vitals.interaction_to_next_paint, 75),
    p95_inp = percentile(web_vitals.interaction_to_next_paint, 95),
    by: {frontend.name}
| fieldsAdd
    inp_rating = if(
        p75_inp < 200ms,
        "good",
        else: if(
            p75_inp < 500ms,
            "needs_improvement",
            else: "poor"
        )
    )
```

**Use Case:** INP measures interaction responsiveness throughout the page lifecycle. Use `inp_rating` to identify frontends with poor interactivity; Good < 200ms, Needs Improvement < 500ms.

### Cumulative Layout Shift (CLS)

Monitor visual stability:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_page_summary
| summarize
    p75_cls = percentile(web_vitals.cumulative_layout_shift, 75),
    by: {frontend.name}
| fieldsAdd
    cls_rating = if(
        p75_cls < 0.1,
        "good",
        else: if(
            p75_cls < 0.25,
            "needs_improvement",
            else: "poor"
        )
    )
```

**Use Case:** CLS measures visual layout stability. Use `cls_rating` to identify frontends with unstable layouts. Note: `dt.frontend.web.page.cumulative_layout_shift` stores CLS × 10,000 (integer) — use this event-based query for threshold-based classification.

**The following two sections cover other web vitals: FCP (diagnostic metric) and FID (deprecated March 2024, replaced by INP).**

### First Contentful Paint (FCP)

Monitor when the first content renders. FCP is a diagnostic metric — not part of the Core Web Vitals program:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_page_summary
| summarize
    p75_fcp = percentile(web_vitals.first_contentful_paint, 75),
    p90_fcp = percentile(web_vitals.first_contentful_paint, 90),
    by: {frontend.name}
| fieldsAdd
    fcp_rating = if(
        p75_fcp < 1800ms,
        "good",
        else: if(
            p75_fcp < 3s,
            "needs_improvement",
            else: "poor"
        )
    )
| sort p75_fcp desc
```

**Use Case:** FCP measures when the browser first renders any content. A high FCP relative to LCP indicates slow initial rendering; a high FCP with normal LCP points to render-blocking resources.

### First Input Delay (FID)

> **Deprecated March 2024:** FID was retired as a Core Web Vital when INP became stable. Use [INP](#interaction-to-next-paint-inp) for new implementations. Include this query only when working with historical data from tenants that collected FID before March 2024.

Monitor legacy interactivity metric:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_page_summary
| summarize
    p75_fid = percentile(web_vitals.first_input_delay, 75),
    p95_fid = percentile(web_vitals.first_input_delay, 95),
    by: {frontend.name}
| fieldsAdd
    fid_rating = if(
        p75_fid < 100ms,
        "good",
        else: if(
            p75_fid < 300ms,
            "needs_improvement",
            else: "poor"
        )
    )
```

**Use Case:** FID measures delay between first user input and browser response. Deprecated since March 2024 — prefer [INP](#interaction-to-next-paint-inp) for new implementations; include FID only when supporting tenants with historical pre-INP data.

### Web Vitals Trends

Track LCP trends over time for deployment regression detection:

```dql
fetch user.events, from: now() - 24h
| filter characteristics.has_page_summary
| summarize
    p75_lcp = percentile(web_vitals.largest_contentful_paint, 75),
    by: {frontend.name, time_bucket = bin(start_time, 1h)}
| sort time_bucket asc
```

### Web Vitals by Page

Analyze per-page performance:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_page_summary
| summarize
    page_views = count(),
    p75_lcp = percentile(web_vitals.largest_contentful_paint, 75),
    by: {frontend.name, page.name}
| filter page_views > 100
| sort p75_lcp desc
| limit 20
```

### Web Vitals by View (SPA)

Analyze per-route performance in single-page applications using view summaries:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_view_summary
| filter dt.rum.application.type == "web"
| summarize
    view_count = count(),
    p75_lcp = percentile(web_vitals.largest_contentful_paint, 75),
    p75_inp = percentile(web_vitals.interaction_to_next_paint, 75),
    p75_cls = percentile(web_vitals.cumulative_layout_shift, 75),
    by: {frontend.name, view.name}
| filter view_count > 50
| sort p75_lcp desc
| limit 20
```

**Use Case:** Identify SPA routes with poor CWV. Use `view.name` for SPA route-level analysis; use `page.name` (previous section) for traditional MPA page-level analysis. Both can be on the same event — SPAs often have both page and view summaries.

### Web Vitals by Device

Compare performance across devices:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_page_summary
| summarize
    p75_lcp = percentile(web_vitals.largest_contentful_paint, 75),
    p75_inp = percentile(web_vitals.interaction_to_next_paint, 75),
    p75_cls = percentile(web_vitals.cumulative_layout_shift, 75),
    by: {frontend.name, device.type}
```
