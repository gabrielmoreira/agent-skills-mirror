# Slow Page Load Playbook

Start by segmenting the problem by page, browser, geo location, and `dt.rum.user_type`.

> This playbook is designed to diagnose slow page loads for **one specific frontend**. All queries use `frontend.name == "my-frontend"` as a placeholder — replace it with the actual frontend name before running.

**JS agent scope:** All `performance.*` W3C timing fields are JavaScript agent only (`dt.rum.agent.type == "javascript"`). Mobile request events do not carry these fields.

**Cross-origin timing restriction:** Cross-origin requests without a `Timing-Allow-Origin` header have timing fields set to `null`. `performance.incomplete_reason == "cache_or_cors"` identifies these requests. See also `"local_cache"` (served from browser cache) and `"invalid_timings"` (timing validation failed).

Heuristics:
- High TTFB → slow backend
- High LCP with normal TTFB → render bottleneck
- High CLS → layout shifts (late-loading content, ads, fonts)
- Long tasks dominate → JavaScript execution bottlenecks (heavy frameworks, large bundles)

## Contents

- [Backend latency (high TTFB)](#backend-latency-high-ttfb)
- [Heavy JavaScript execution (long tasks)](#heavy-javascript-execution-long-tasks)
- [Large JavaScript bundles](#large-javascript-bundles)
- [Large resources](#large-resources)
- [Cache effectiveness](#cache-effectiveness)
- [Compression waste](#compression-waste)
- [Network issues](#network-issues)
- [Third-party dependencies](#third-party-dependencies)

## Backend latency (high TTFB)

**Page-level TTFB** from page summary events (pre-calculated field; use for overall page assessment):

```dql
fetch user.events, from: now() - 2h
| filter frontend.name == "my-frontend"
| filter characteristics.has_page_summary
| filter page.name == "/checkout"
| summarize
    avg_ttfb = avg(web_vitals.time_to_first_byte),
    p75_ttfb = percentile(web_vitals.time_to_first_byte, 75),
    by: {page.name}
```

**Request-level TTFB** from request events (calculated from W3C timing fields; JS agent only):

```dql
fetch user.events, from: now() - 2h
| filter frontend.name == "my-frontend"
| filter characteristics.has_request
| filter isNull(performance.incomplete_reason)
| fieldsAdd ttfb = performance.response_start - performance.start_time
| summarize
    avg_ttfb = avg(ttfb),
    p75_ttfb = percentile(ttfb, 75),
    avg_duration = avg(duration),
    by: {url.domain, url.path}
| sort p75_ttfb desc
| limit 20
```

If TTFB is high, analyze backend spans by correlating frontend events with backend traces using `trace.id`.

## Heavy JavaScript execution (long tasks)

Long tasks by page:

```dql
fetch user.events, from: now() - 2h
| filter frontend.name == "my-frontend"
| filter characteristics.has_long_task
| summarize
   long_task_count = count(),
   total_blocking_time = sum(duration),
   by: {page.name}
| sort total_blocking_time desc
| limit 20
```

Long tasks by script source:

```dql
fetch user.events, from: now() - 2h
| filter frontend.name == "my-frontend"
| filter characteristics.has_long_task
| summarize
   long_task_count = count(),
   total_blocking_time = sum(duration),
   by: {long_task.attribution.container_src}
| sort total_blocking_time desc
| limit 20
```

## Large JavaScript bundles

```dql
fetch user.events, from: now() - 2h
| filter frontend.name == "my-frontend"
| filter characteristics.has_request
| filter endsWith(url.full, ".js")
| summarize dls = max(performance.decoded_body_size), by: url.full
| sort dls desc
| limit 20
```

## Large resources

```dql
fetch user.events, from: now() - 2h
| filter frontend.name == "my-frontend"
| filter characteristics.has_request
| summarize dls = max(performance.decoded_body_size), by: url.full
| sort dls desc
| limit 20
```

## Cache effectiveness

```dql
fetch user.events, from: now() - 2h
| filter frontend.name == "my-frontend"
| filter characteristics.has_request
| fieldsAdd cache_status = if(
   performance.incomplete_reason == "local_cache" or performance.incomplete_reason == "cache_or_cors" or
   (performance.transfer_size == 0 and (performance.encoded_body_size > 0 or performance.decoded_body_size > 0)),
   "cached",
   else: if(performance.transfer_size > 0, "network", else: "uncached")
  )
| summarize
   request_count = count(),
   avg_duration = avg(duration),
   by: {url.domain, cache_status}
```

Note: `cache_or_cors` requests have `null` timing fields (cross-origin without `Timing-Allow-Origin`) — they are grouped with cached requests since no network timing is available.

## Compression waste

Find resources that should be compressed but are being served uncompressed:

```dql
fetch user.events, from: now() - 2h
| filter frontend.name == "my-frontend"
| filter characteristics.has_request
| filter isNotNull(performance.encoded_body_size) and isNotNull(performance.decoded_body_size)
| filter performance.encoded_body_size == performance.decoded_body_size
| filter performance.decoded_body_size > 10000
| summarize
   requests = count(),
   avg_uncompressed_bytes = avg(performance.decoded_body_size),
   total_uncompressed_bytes = sum(performance.decoded_body_size),
   by: {url.domain, url.path}
| sort total_uncompressed_bytes desc
| limit 50
```

Note: equal `encoded_body_size` and `decoded_body_size` means no compression is applied. Large values here represent compression opportunities.

## Network issues

Compare by location and domain when TTFB is high but backend performance is good:

```dql
fetch user.events, from: now() - 2h
| filter frontend.name == "my-frontend"
| filter characteristics.has_request
| summarize
   request_count = count(),
   avg_duration = avg(duration),
   p75_duration = percentile(duration, 75),
   p95_duration = percentile(duration, 95),
   by: {geo.country.iso_code, url.domain}
| sort p95_duration desc
| limit 50
```

Analyze DNS time:

```dql
fetch user.events, from: now() - 2h
| filter frontend.name == "my-frontend"
| filter characteristics.has_request
| filter isNotNull(performance.domain_lookup_start) and isNotNull(performance.domain_lookup_end)
| fieldsAdd dns_ms = performance.domain_lookup_end - performance.domain_lookup_start
| summarize
   request_count = count(),
   avg_dns_ms = avg(dns_ms),
   p75_dns_ms = percentile(dns_ms, 75),
   p95_dns_ms = percentile(dns_ms, 95),
   by: {url.domain}
| sort p95_dns_ms desc
| limit 50
```

Analyze by protocol (http/1.1, h2, h3):

```dql
fetch user.events, from: now() - 2h
| filter frontend.name == "my-frontend"
| filter characteristics.has_request
| summarize cnt = count(), by: {url.domain, performance.next_hop_protocol}
| sort cnt desc
| limit 50
```

## Third-party dependencies

Analyze request performance by domain:

```dql
fetch user.events, from: now() - 2h
| filter frontend.name == "my-frontend"
| filter characteristics.has_request
| summarize
   request_count = count(),
   avg_duration = avg(duration),
   p75_duration = percentile(duration, 75),
   p95_duration = percentile(duration, 95),
   by: {url.domain}
| sort p95_duration desc
| limit 50
```
