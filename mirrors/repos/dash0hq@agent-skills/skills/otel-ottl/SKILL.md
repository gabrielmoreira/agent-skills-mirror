---
name: otel-ottl
description: OpenTelemetry Transformation Language (OTTL) expert. Use when writing or debugging OTTL expressions for any OpenTelemetry Collector component that supports OTTL (processors, connectors, receivers, exporters). Triggers on tasks involving telemetry transformation, filtering, attribute manipulation, data redaction, sampling policies, routing, or Collector configuration. Covers syntax, contexts, functions, error handling, and performance.
metadata:
  author: dash0
  version: '1.0.0'
---

# OpenTelemetry Transformation Language (OTTL)

## Components that use OTTL

OTTL is not limited to the transform and filter processors.
Processors (transform, filter, attributes, span, tailsampling, cumulativetodelta, logdedup, lookup), connectors (routing, count, sum, signaltometrics), and the hostmetrics receiver all accept OTTL expressions.
See [components](./rules/components.md) for the full list with use cases.

## OTTL syntax

### Path expressions

Navigate telemetry data using dot notation:

```
span.name
span.attributes["http.method"]
resource.attributes["service.name"]
```

**Contexts** (first path segment): `resource`, `scope`, `span`, `spanevent`, `metric`, `datapoint`, `log`.

### Enumerations

Use int64 constants for enumeration fields:

```
span.status.code == STATUS_CODE_ERROR
span.kind == SPAN_KIND_SERVER
```

### Operators

Assignment: `=` — Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=` — Logical: `and`, `or`, `not`

### Functions

**Converters** (uppercase, return values):

```
ToUpperCase(span.attributes["http.request.method"])
Substring(log.body.string, 0, 1024)
Concat(["prefix", span.attributes["request.id"]], "-")
IsMatch(metric.name, "^k8s\\..*$")
```

**Editors** (lowercase, modify data in-place):

```
set(span.attributes["region"], "us-east-1")
delete_key(resource.attributes, "internal.key")
limit(log.attributes, 10, [])
```

See [function-reference](./rules/function-reference.md) for the full list of editors and converters.

### Conditional statements

Use `where` to apply transformations conditionally:

```
span.attributes["db.statement"] = "REDACTED" where resource.attributes["service.name"] == "accounting"
```

### Nil checks

Use `nil` for absence checking (not `null`):

```
resource.attributes["service.name"] != nil
```

## Validation workflow

1. **Validate config syntax** — run `otelcol validate --config=config.yaml` to catch compilation errors before starting the Collector.
2. **Test with the debug exporter** — route transformed telemetry to a `debug` exporter and inspect the output:

```yaml
exporters:
  debug:
    verbosity: detailed

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [transform, batch]
      exporters: [debug]   # swap in production exporter once validated
```

3. **Set `error_mode: ignore` in production** — see [Error handling](#error-handling).
4. **Promote to production exporters** — replace `debug` with the production exporter.

## Common patterns

### Set attributes

```
set(resource.attributes["k8s.cluster.name"], "prod-aws-us-west-2")
```

### Redact sensitive data

See [redaction](./rules/redaction.md) for strategies (replace, mask, hash, delete, drop) with examples.

### Drop telemetry by pattern

```
IsMatch(metric.name, "^k8s\\.replicaset\\..*$")
```

### Drop stale data

```
time_unix_nano < UnixNano(Now()) - 21600000000000
```

### Backfill missing timestamps

```yaml
processors:
  transform:
    log_statements:
      - context: log
        statements:
          - set(log.observed_time, Now()) where log.observed_time_unix_nano == 0
          - set(log.time, log.observed_time) where log.time_unix_nano == 0
```

### Filter processor example

```yaml
processors:
  filter:
    metrics:
      datapoint:
        - 'IsMatch(ConvertCase(String(metric.name), "lower"), "^k8s\\.replicaset\\.")'

service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [filter, batch]
      exporters: [debug]
```

### Transform processor example

```yaml
processors:
  transform:
    trace_statements:
      - context: span
        statements:
          - set(span.status.code, STATUS_CODE_ERROR) where span.attributes["http.response.status_code"] >= 500
          - set(span.attributes["env"], "production") where resource.attributes["deployment.environment"] == "prod"

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [transform, batch]
      exporters: [debug]
```

### Defensive nil checks

```
resource.attributes["service.namespace"] != nil
and
IsMatch(ConvertCase(String(resource.attributes["service.namespace"]), "lower"), "^platform.*$")
```

See [cardinality](./rules/cardinality.md) for normalizing high-cardinality attributes (path segments, IP masking, attribute count/length limits) and [enrichment](./rules/enrichment.md) for adding static resource attributes.

## Error handling

### Compilation errors

Occur during processor initialization and prevent Collector startup:
- Invalid syntax (missing quotes)
- Unknown functions
- Invalid path expressions
- Type mismatches

### Runtime errors

Occur during telemetry processing:
- Accessing non-existent attributes
- Type conversion failures
- Function execution errors

### Error mode configuration

Always set `error_mode` explicitly.

| Mode | Behavior | When to use |
|------|----------|-------------|
| `propagate` (default) | Stops processing current item | Development and strict environments where you want to catch every error |
| `ignore` | Logs error, continues processing | **Production** — set this unless you have a specific reason not to |
| `silent` | Ignores errors without logging | High-volume pipelines with known-safe transforms where error logs are noise |

```yaml
processors:
  transform:
    error_mode: ignore
    trace_statements:
      - context: span
        statements:
          - set(span.attributes["parsed"], ParseJSON(span.attributes["json_body"]))
```
## Performance

Use `where` clauses to skip items early.

```
# BAD — runs replace_pattern on every span
replace_pattern(span.attributes["url.path"], "/\\d+", "/{id}")

# GOOD — skips spans that lack the attribute
replace_pattern(span.attributes["url.path"], "/\\d+", "/{id}") where span.attributes["url.path"] != nil
```

## References

- [OTTL Guide](https://www.dash0.com/guides/opentelemetry-transformation-language-ottl)
- [OTTL Specification](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/pkg/ottl)
- [OTTL Functions Reference](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/pkg/ottl/ottlfuncs)
- [OTTL Playground](https://ottl.run)
