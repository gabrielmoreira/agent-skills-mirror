# Performance Analysis & Diagnostics

Advanced performance analysis including request timing, navigation patterns, geographic distribution, long tasks, and regression detection.

## Contents

- [Metric-Based Queries](#metric-based-queries)
  - [Request Throughput Analysis](#request-throughput-analysis)
  - [Request Duration Performance](#request-duration-performance)
  - [Request Performance SLA Monitoring](#request-performance-sla-monitoring)
  - [Geographic Performance Distribution](#geographic-performance-distribution)
  - [Performance vs Error Rate Correlation](#performance-vs-error-rate-correlation)
  - [Request Performance Degradation Detection](#request-performance-degradation-detection)
- [Event-Based Queries](#event-based-queries)
  - [Request Timing Analysis](#request-timing-analysis)
    - [Request Timing Breakdown](#request-timing-breakdown)
    - [Third-Party Resource Performance](#third-party-resource-performance)
    - [HTTP Protocol Performance](#http-protocol-performance)
    - [Response Size Analysis](#response-size-analysis)
    - [Render-Blocking Resources](#render-blocking-resources)
  - [Navigation Patterns](#navigation-patterns)
    - [External Referrers](#external-referrers)
    - [Internal Navigation Flows](#internal-navigation-flows-spa--soft-navigations)
    - [Page Reload Analysis](#page-reload-analysis)
  - [Long Tasks & JavaScript Performance](#long-tasks--javascript-performance)
    - [Long Tasks Overview](#long-tasks-overview)
    - [Long Tasks by Page](#long-tasks-by-page)
    - [Third-Party Long Tasks](#third-party-long-tasks)
    - [Critical Long Tasks](#critical-long-tasks)
  - [Page & ISP Analysis](#page--isp-analysis)
    - [Time on Page](#time-on-page)
    - [ISP Performance Analysis](#isp-performance-analysis)

## Metric-Based Queries

Monitor frontend request performance, response times, and throughput using aggregated RUM metrics.

> **`scalar: true` vs array (`[]`) notation:** `scalar: true` collapses the entire time window into one value per row — total across all buckets. Use it for overall rates, sorting, and alerting. Without `scalar: true`, metric columns are arrays (one value per interval); use `[]` notation for per-bucket trend analysis. When filtering or sorting on an array column, choose the aggregation that matches your intent: `arrayMax(col)` for **spike and threshold queries** ("did this ever exceed X in any bucket?") or `arrayAvg(col)` for **sustained-rate ranking** ("what was the typical level?"). Avoid `arrayAvg` of a cardinality metric — it is not a statistically correct overall rate; use `scalar: true` instead.

**Key Metrics:**

- `dt.frontend.request.count` - Total frontend requests
- `dt.frontend.request.duration` - Request response times in milliseconds

**Alerting Thresholds:**

- Critical: p95 duration > SLA threshold (typically 2-3s)
- Warning: p95 duration approaching SLA threshold
- Track performance degradation > 20% hour-over-hour

### Request Throughput Analysis

Monitor frontend request volume and patterns:

```dql
timeseries request_count = sum(dt.frontend.request.count),
          avg_per_min = avg(dt.frontend.request.count, scalar: true),
          by: {frontend.name, device.type},
          from: now() - 2h,
          interval: 1m
| filter avg_per_min > 100
| sort avg_per_min desc
```

**Use Case:** **Per-bucket trend.** Track frontend request volume by application and device type. `interval: 1m` pins bucket width so `avg_per_min` is always requests per minute regardless of timeframe; `> 100` filters low-traffic frontends.

### Request Duration Performance

Analyze frontend request latency:

```dql
timeseries avg_duration = avg(dt.frontend.request.duration),
          p75_duration = percentile(dt.frontend.request.duration, 75),
          p95_duration = percentile(dt.frontend.request.duration, 95),
          by: {frontend.name},
          from: now() - 1h
| filter arrayMax(p95_duration) > 3000
| sort arrayMax(p95_duration) desc
```

**Use Case:** **Per-bucket trend.** Identify applications where p95 request duration spiked above 3000ms in any bucket. `arrayMax` catches brief post-deploy spikes that `arrayAvg` would smooth away.

### Request Performance SLA Monitoring

Track adherence to performance SLAs:

```dql
timeseries request_count = sum(dt.frontend.request.count),
          avg_duration = avg(dt.frontend.request.duration),
          p95_duration = percentile(dt.frontend.request.duration, 95),
          by: {frontend.name},
          from: now() - 1h

| fieldsAdd
    sla_threshold_ms = 2000
| fieldsAdd
    sla_compliance_ratio = arrayAvg(iCollectArray(if(p95_duration[] < sla_threshold_ms, 1, else: 0))),
    sla_buffer = sla_threshold_ms - arrayAvg(p95_duration)
| sort sla_buffer asc
```

**Use Case:** **Overall compliance rate** across the time window. Monitor and report on performance SLA compliance.

### Geographic Performance Distribution

Compare request performance across regions:

```dql
timeseries request_count = sum(dt.frontend.request.count),
          avg_duration = avg(dt.frontend.request.duration),
          by: {frontend.name, geo.country.iso_code},
          from: now() - 4h

| fieldsAdd
    avg_duration_sec = arrayAvg(avg_duration) / 1000
| filter arraySum(request_count) > 50
| sort avg_duration_sec desc
```

**Use Case:** **Overall average** across the time window, ranked by region. Identify geographic regions experiencing poor performance for CDN optimization.

### Performance vs Error Rate Correlation

Correlate slow requests with error occurrences:

```dql
timeseries request_count = sum(dt.frontend.request.count, scalar: true),
          error_count = sum(dt.frontend.error.count, scalar: true),
          avg_duration = avg(dt.frontend.request.duration, scalar: true),
          by: {frontend.name},
          from: now() - 1h

| fieldsAdd
    error_rate_percent = error_count * 100.0 / request_count,
    avg_duration_sec = avg_duration / 1000
| filter error_rate_percent > 5
| sort error_rate_percent desc
```

**Use Case:** **Overall rate** across the time window. Identify if slow requests correlate with increased error rates.

### Request Performance Degradation Detection

Monitor request duration trends for regressions:

```dql
timeseries {
    avg_duration = avg(dt.frontend.request.duration),
    p95_duration = percentile(dt.frontend.request.duration, 95),
    request_count = sum(dt.frontend.request.count)
},
  by: {frontend.name},
  from: now() - 24h,
  interval: 1h

| join [
  timeseries {
    prev_avg_duration = avg(dt.frontend.request.duration)
  },
    by: {frontend.name},
    from: now() - 24h,
    interval: 1h,
    shift: 1h

], on: { frontend.name }, fields: { prev_avg_duration }

| fieldsAdd
    duration_change_percent = coalesce((avg_duration[] - prev_avg_duration[]) * 100.0 / (prev_avg_duration[]), 0)
| filter arrayMax(duration_change_percent) > 20
| sort arrayMax(duration_change_percent) desc
```

**Use Case:** **Per-bucket trend** (compares adjacent 1-hour intervals). Detect performance regressions after deployments or infrastructure changes. `arrayMax` catches a single post-deploy spike that `arrayAvg` would dilute across 24 buckets.

## Event-Based Queries

### Request Timing Analysis

Analyze W3C Resource Timing data to diagnose WHERE latency occurs in frontend requests.

**Data Source:** `fetch user.events` with `characteristics.has_request`

**Key Timing Phases (all in nanoseconds):**

- `performance.domain_lookup_start/end` - DNS resolution
- `performance.connect_start/end` - TCP connection
- `performance.secure_connection_start` - TLS handshake start
- `performance.request_start` - Request sent to server
- `performance.response_start` - First byte received (TTFB)
- `performance.response_end` - Download complete

#### Request Timing Breakdown

Analyze timing phases for slow requests:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_request
| filter duration > 1s
| fieldsAdd
    dns_time = performance.domain_lookup_end - performance.domain_lookup_start,
    connect_time = performance.connect_end - performance.connect_start,
    tls_time = performance.connect_end - performance.secure_connection_start,
    server_time = performance.response_start - performance.request_start,
    download_time = performance.response_end - performance.response_start
| summarize
    avg_dns = avg(dns_time),
    avg_connect = avg(connect_time),
    avg_tls = avg(tls_time),
    avg_server = avg(server_time),
    avg_download = avg(download_time),
    request_count = count(),
    by: {url.domain}
| sort avg_server desc
| limit 20
```

**Use Case:** Identify bottleneck phase (DNS, connection, server, download).

#### Third-Party Resource Performance

Compare first-party vs third-party resource timing:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_request
| summarize
    avg_duration = avg(duration),
    p75_duration = percentile(duration, 75),
    request_count = count(),
    by: {url.provider, url.domain}
| filter request_count > 50
| sort p75_duration desc
| limit 30
```

**Use Case:** Identify slow third-party resources impacting page performance.

#### HTTP Protocol Performance

Analyze performance by HTTP protocol version:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_request
| summarize
    avg_duration = avg(duration),
    p90_duration = percentile(duration, 90),
    request_count = count(),
    by: {performance.next_hop_protocol}
| sort request_count desc
```

**Use Case:** Compare HTTP/1.1 vs HTTP/2 vs HTTP/3 performance.

#### Response Size Analysis

Identify oversized responses:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_request
| filter performance.transfer_size > 100000
| fieldsAdd
    compression_ratio = if(performance.encoded_body_size > 0,
        toDouble(performance.decoded_body_size) / toDouble(performance.encoded_body_size),
        else: 1.0)
| summarize
    avg_transfer_size = avg(performance.transfer_size),
    avg_compression_ratio = avg(compression_ratio),
    request_count = count(),
    by: {url.domain, url.path}
| sort avg_transfer_size desc
| limit 20
```

**Use Case:** Find large payloads and compression opportunities.

#### Render-Blocking Resources

Identify resources blocking page render:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_request
| filter performance.render_blocking_status == "blocking"
| summarize
    avg_duration = avg(duration),
    request_count = count(),
    by: {url.domain, url.path, performance.initiator_type}
| sort avg_duration desc
| limit 20
```

**Use Case:** Optimize critical rendering path.

### Navigation Patterns

Analyze user navigation flows, referrers, and navigation types in web applications.

**Data Source:** `fetch user.events` with `characteristics.has_navigation`

**Key Fields:**

- `navigation.type` - Dynatrace navigation type: `hard` (full page reload), `soft` (SPA navigation without full reload)
- `performance.type` - W3C Navigation Timing type (hard navigations only): `navigate`, `reload`, `back_forward`
- `navigation.tab_state` - `new`, `existing`, `existing_invalid`, `duplicated`
- `view.source.name` - Entity-normalised name of the previous view (symmetric with `view.name`; use for navigation flow matrices)
- `view.source.url.path` - Raw URL path of the previous view (asymmetric with `view.name` entity name)
- `page.source.url.*` - Referrer URL components

**W3C Timing References:**
- Resource Timing: https://www.w3.org/TR/resource-timing/ — https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming
- Navigation Timing: https://www.w3.org/TR/navigation-timing/ — https://developer.mozilla.org/en-US/docs/Web/API/PerformanceNavigationTiming
- Timing phase diagram: https://www.w3.org/TR/resource-timing/#attribute-descriptions

**Reference:** https://docs.dynatrace.com/docs/observe/digital-experience/new-rum-experience/web-frontends/analyze-and-alert/monitor-web-performance-with-dql

#### External Referrers

Analyze traffic sources from external sites. Uses `performance.type == "navigate"` (W3C first-load navigation) rather than `navigation.type == "hard"` alone — reloads and back/forward navigations are also hard navigations but carry the original referrer domain, not a new external arrival. Uses `page.source.url.domain != page.url.domain` to exclude same-domain referrers (redirects, cross-subdomain hops).

> **Note:** Results depend on the browser sending the [`Referer` header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referer). Many navigations omit it — for example when the referring page uses `Referrer-Policy: no-referrer`, when navigating from HTTPS to HTTP, or from bookmarks and address bar entries. Absence of a referrer does not mean no external traffic; it means the origin is unknown.

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_navigation
| filter navigation.type == "hard"
| filter performance.type == "navigate"
| filter isNotNull(page.source.url.domain)
| filter page.source.url.domain != page.url.domain
| summarize
    referral_count = count(),
    unique_sessions = countDistinct(dt.rum.session.id),
    by: {frontend.name, page.source.url.domain}
| sort referral_count desc
| limit 20
```

**Use Case:** Identify top external traffic sources. Counts are a lower bound — referrers suppressed by browser privacy policy appear as direct traffic.

#### Internal Navigation Flows (SPA — soft navigations)

Track view-to-view navigation within single-page applications:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_navigation
| filter navigation.type == "soft"
| filter isNotNull(view.source.name)
| summarize
    flow_count = count(),
    by: {frontend.name, view.source.name, view.name}
| sort flow_count desc
| limit 30
```

**Use Case:** Visualize common user journeys within SPAs. Note: source action handling for hard navigations is not yet available — a hard navigation equivalent of this query does not exist yet.

#### Page Reload Analysis

Monitor page reloads (W3C `performance.type` field — only available on hard navigations):

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_navigation
| filter performance.type == "reload"
| summarize
    reload_count = count(),
    unique_sessions = countDistinct(dt.rum.session.id),
    by: {frontend.name, page.name}
| sort reload_count desc
| limit 20
```

**Use Case:** Identify pages with high reload rates (potential UX issues).

### Long Tasks & JavaScript Performance

Analyze long-running JavaScript tasks that block the main thread and affect interactivity.

**Data Source:** `fetch user.events` with `characteristics.has_long_task`

**Key Fields:**

- `duration` - Task duration (nanoseconds)
- `long_task.name` - Context attribution: self, same-origin, cross-origin, etc.
- `long_task.attribution.container_*` - Container details for iframe tasks

**Performance Thresholds:**

- Long task: > 50ms (blocks interaction)
- Critical: > 100ms (noticeable lag)
- Severe: > 250ms (frustrating UX)

#### Long Tasks Overview

Query all long tasks:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_long_task
| summarize
    task_count = count(),
    avg_duration = avg(duration),
    p75_duration = percentile(duration, 75),
    p95_duration = percentile(duration, 95),
    max_duration = max(duration),
    by: {frontend.name}
```

**Use Case:** Baseline long task frequency and severity.

#### Long Tasks by Page

Identify pages with performance issues:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_long_task
| summarize
    task_count = count(),
    avg_duration = avg(duration),
    p90_duration = percentile(duration, 90),
    by: {frontend.name, page.name}
| sort p90_duration desc
| limit 20
```

**Use Case:** Prioritize pages for JavaScript optimization.

#### Third-Party Long Tasks

Find blocking third-party scripts:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_long_task
| filter in(long_task.name, "cross-origin-ancestor", "cross-origin-descendant", "cross-origin-unreachable")
| summarize
    task_count = count(),
    total_blocking_time = sum(duration),
    by: {frontend.name, long_task.attribution.container_src}
| sort total_blocking_time desc
| limit 15
```

**Use Case:** Evaluate third-party script impact.

#### Critical Long Tasks

Find severely blocking tasks:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_long_task
| filter duration > 250ms
| summarize
    critical_tasks = count(),
    avg_duration = avg(duration),
    affected_sessions = countDistinct(dt.rum.session.id),
    by: {frontend.name, page.name}
| sort critical_tasks desc
| limit 20
```

**Use Case:** Address worst performance offenders.

### Page & ISP Analysis

Event-based analysis of page engagement and network provider performance.

#### Time on Page

Analyze engagement depth:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_page_summary
| summarize
    page_views = count(),
    avg_foreground = avg(page.foreground_time),
    p50_foreground = percentile(page.foreground_time, 50),
    p90_foreground = percentile(page.foreground_time, 90),
    by: {frontend.name, page.name}
| filter page_views > 50
| sort avg_foreground desc
| limit 20
```

**Use Case:** Identify high-engagement pages.

#### ISP Performance Analysis

Identify network provider issues:

```dql
fetch user.events, from: now() - 2h
| filter characteristics.has_request
| summarize
    avg_duration = avg(duration),
    p90_duration = percentile(duration, 90),
    request_count = count(),
    by: {client.isp, geo.country.iso_code}
| filter request_count > 100
| sort p90_duration desc
| limit 20
```

**Use Case:** Detect ISP-specific performance degradation.
