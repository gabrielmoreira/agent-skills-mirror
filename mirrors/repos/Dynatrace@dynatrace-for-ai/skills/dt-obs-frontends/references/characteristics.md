# Event Characteristics

Characteristics are boolean flags set on every `user.events` record that describe what type of event it is and what data it carries. Use them to scope queries to a specific event type — without a characteristic filter, a `fetch user.events` query returns all event types mixed together.

**Usage pattern:** `| filter characteristics.has_X` (bare boolean — do not use `== true`)

**Full field reference:** https://docs.dynatrace.com/docs/semantic-dictionary/model/rum/user-events

## How characteristics combine

An event can carry any combination of characteristics simultaneously. Some characteristics are aggregates — for example, `has_error` is set on every event that carries an error of any kind, whether it is an exception, a crash, a failed request, or a CSP violation. A single event can have both `has_error` and `has_exception` set at the same time.

This means filtering by `characteristics.has_error` is broader than filtering by `characteristics.has_exception` — the former returns all error types, the latter only JavaScript exceptions.

## Deriving an `event_type` label

A built-in field `characteristics.classifier` exists and contains a pre-computed event type string (values: `error`, `page_summary`, `navigation`, `user_action`, etc.). While it can be used in queries, it will not classify events as expected — it is a field used for internal storage optimizations and its classification does not reliably reflect the full event type as seen by the user.

Always prefer deriving the label explicitly from the boolean characteristics using an `if()` chain. This gives you full control over priority order and produces consistent, predictable results:



```dql
fetch user.events
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
| fields event_type
```

**Use case:** Session journey timelines, event-type breakdowns, debugging. See [user-sessions.md](user-sessions.md) for the Session Journey Overview query that uses this pattern.
