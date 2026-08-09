# Desktop Update Admission

`@tutti-os/desktop-update-admission` is the shared desktop admission boundary
for Tutti Desktop and TSH Desktop. It contains a Go daemon core for policy
transport, scheduling, validation, and feature caching, plus TypeScript
contracts, Electron presentation, updater ownership, preload APIs, and React
UI.

## Ownership

The background daemon (`tuttid` or `desktopd`) owns:

- the production or development policy checker
- the authoritative request identity supplied by its Electron parent
- the proactive startup request
- the 3-second startup and 10-second foreground request timeouts
- foreground throttling and request single-flight
- policy-response validation and fail-open classification
- exact-identity feature-availability persistence
- local snapshot, startup-wait, and refresh APIs

Electron owns:

- resolving the installed or explicitly mocked current version once
- injecting that same identity into the daemon and updater
- sending foreground and retry lifecycle signals to the daemon
- the startup gate and forced-upgrade window
- mandatory updater ownership and minimum-target validation
- renderer IPC and an in-memory projection of the daemon feature snapshot

Product adapters own endpoint selection, the concrete updater, download URLs,
window assets, and the authenticated local-daemon transport. They do not
perform policy HTTP requests or persist feature policy.

## Dependency direction

```text
Electron bootstrap
  -> starts tuttid / desktopd with one immutable desktop identity
  -> daemon proactively checks the policy service
  -> Electron reads the completed startup snapshot over authenticated local HTTP
  -> shared Electron controller applies the startup gate and updater flow

resume / focus / retry
  -> Electron sends a local refresh trigger
  -> daemon applies throttling, timeout, validation, and remote transport
  -> Electron consumes the returned snapshot

business renderer
  -> trusted preload IPC
  -> in-memory feature projection
  -> daemon-owned remote/cache snapshot
```

Tutti's production remote chain is
`Electron -> tuttid -> daemon HTTP client -> policy service`. TSH's chain is
`Electron -> desktopd -> control-plane client -> policy service`. A business
renderer never reads environment variables or accesses either remote endpoint.

## Lifecycle

The daemon starts its initial policy request during construction, before the
local API is consumed. `GET /v1/desktop-update-admission/startup` waits for that
initial request and returns its completed snapshot; it never initiates the
remote request. A failed, malformed, or timed-out request is represented as
`failedOpen`, so Electron opens the application.

`POST /v1/desktop-update-admission/refresh` accepts only `foreground` or
`retry`. Foreground requests are throttled for 30 minutes by default. Retry
bypasses that interval. Concurrent refreshes share the active request.
Electron retains only the one-prompt-per-process presentation rule.

An `upgradeRequired` decision opens the isolated admission window. The forced
flow acquires the updater lease, captures normal configuration, prepares a
channel-matched update, validates the target against the returned minimum,
downloads it, validates again, and requests installation. A later allowed
policy releases the gate and restores normal updater configuration.

## Feature availability

Feature availability is independent from the minimum-version decision. A valid
remote envelope atomically replaces the daemon cache. A missing or invalid
feature envelope retains the previous feature snapshot while a valid minimum
version decision remains usable. A valid empty list explicitly clears the
cache.

The cache lives under the daemon state directory, is accepted only for the
exact product, platform, architecture, and current version, and stores no
minimum version or admission decision. Remote policy is never restored from
disk. Electron and renderer code only receive the daemon's immutable
`remote`, `cache`, or `empty` projection.

## Development boundary

Packaged daemons ignore all `DESKTOP_UPDATE_ADMISSION_*` variables. For an
unpackaged client, Electron resolves only `currentVersion` and updater
simulation fields. It injects the current version into both the daemon identity
and updater. The daemon independently owns policy, feature, timeout scenario,
sequence, and foreground-interval parsing.

With `in-process` transport, the daemon evaluates the local policy scenario.
With `loopback` transport, the standalone mock server exclusively owns policy,
minimum-version, feature-key, sequence, and named-policy fields; the client
daemon receives only the loopback URL and sends the real HTTP request.

Invalid enabled configurations fail daemon startup. The mock server binds only
to `127.0.0.1`. Simulated installation ends in an explicit development state
and never invokes the production installer or restart path.
