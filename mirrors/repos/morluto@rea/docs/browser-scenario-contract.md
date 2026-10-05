# Browser scenario contract

`capture_browser_scenario` accepts the provider-neutral
`browserScenarioSchema` through both MCP and the
`capture-browser-scenario INPUT_JSON` CLI command. The request is declarative:
it admits a fixed action vocabulary, exact HTTP(S) origins, deterministic
browser settings, explicit storage and request replay, and provider-owned
liveness deadlines. `INPUT_JSON` may be inline JSON or a JSON file path.

The minimal request contains only browser launch/connect authority, `start_url`,
`allowed_origins`, and at least one `actions` entry. Environment settings,
empty storage, disabled request replay, the required redaction policy, and a
final sanitized URL capture are supplied by default. Add secret declarations,
storage seeds, replay routes, query redaction names, and additional artifact or
event capture only when the investigation needs them. Action, secret, storage,
and replay-route counts are not capped. Duration, action, and navigation
timeouts remain fixed provider-owned liveness limits; the request does not
accept a caller-controlled `limits` object.

The browser boundary is part of the contract. Launch mode requires a
caller-selected absolute executable, a provider-owned temporary profile,
headless operation, and close-plus-delete cleanup. Connect mode accepts only an
explicit-port loopback CDP endpoint, declares the browser externally owned, and
permits disconnect-only cleanup. The Playwright driver preserves this
distinction: it closes and deletes provider-owned profiles, but only disconnects
from an external CDP browser. Real-browser verification checks both outcomes and
confirms that an attached external browser remains alive.

URLs contain a query-free HTTP(S) base plus ordered query entries. Every query,
form, storage, cookie, and replay value is either an explicitly public literal
or a reference to a declared environment-backed secret. Raw credentials in
URLs and literal credential headers are rejected. Secret query names must also
appear in the redaction policy, and the required credential headers cannot be
removed from that policy. Durable results must replace resolved secret values
with their secret references.

Every start, navigation, storage, replay, and redirect origin must be listed in
`allowed_origins`. Unsupported action tags, unknown fields, duplicate step or
route IDs, undeclared or unused secrets, and provider-owned replay headers fail
validation. HTTP and WebSocket routing enforces the same declared scope. Exact
replay may abort unmatched requests or pass through only approved origins.

The result is Evidence with an initial state followed by one record per
declared action. Each step reports action status, elapsed time, sanitized URLs,
event bounds, and independently typed capture states for screenshot, DOM,
accessibility, URL, history, and storage. Console, page-error, network,
WebSocket, frame, worker, popup, and cancelled-download events are attributed to
steps and all observed events and requested artifacts are returned inline.
There are no event, frame, worker, popup, WebSocket, DOM-node,
accessibility-node, storage-entry, screenshot-count, or cumulative
metadata-byte caps. Requested artifacts and observed events are returned
inline without application-defined size ceilings. Other missing sections
remain explicit and make the capture ineligible for equality claims.
Attach-mode captures also declare the unavoidable pre-attach event gap.

Browser automation is disabled by default. The administrator ceiling is
configured with:

- `REA_BROWSER_SCENARIO_ENABLED`
- `REA_BROWSER_SCENARIO_EXECUTABLE_ROOTS_JSON`
- `REA_BROWSER_SCENARIO_CDP_ENDPOINTS_JSON`
- `REA_BROWSER_SCENARIO_ALLOWED_ORIGINS_JSON`
- `REA_BROWSER_SCENARIO_ALLOWED_ENV_JSON`

Unlike passive observation, browser automation is not granted automatically.
Use an explicit project/session grant, or opt into the administrator grant with
`REA_BROWSER_SCENARIO_AUTO_GRANT=true` for a trusted unattended environment.
Authorization commits the exact executable or CDP endpoint, origins, environment
variable names, network class, and scenario digest before any browser side
effect.

## Scenario comparison

`compare_web_captures` and `compare-web-captures` also accept two complete
browser scenario captures. Steps align only by exact, unique `step_id`.
Duplicate IDs, missing counterparts, changed action kinds, and incompatible
browser/origin capture context are returned as alignment failures. They prevent
an unchanged claim; observed differences may still prove a changed result.

The comparison records its full normalization commitment and SHA-256 digest.
Built-in rules exclude step elapsed time and event sequence/index fields,
compare screenshots by content digest, and compare DOM/accessibility captures
by normalized text. Optional caller rules are bounded exact-literal
replacements over named artifact kinds. Rules and artifact-kind lists are
sorted canonically before application, making the same policy reproducible
regardless of input order. Rules operate only on already-redacted durable
capture fields and are preserved in the result.

Each aligned step reports changed, unchanged, or unknown. Changed and unknown
action, screenshot, DOM, accessibility, URL, history, storage, and event
artifacts carry their normalized before/after digests and capture states.
Every changed or unknown artifact record is returned inline for each aligned
step. Missing, truncated, or mismatched capture coverage remains unknown
instead of being treated as equality.
