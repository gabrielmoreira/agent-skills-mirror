# platform

Host-platform services for the core process: lifecycle, self-update, diagnostics, and the local transport surfaces the desktop shell talks to. Nothing here is feature-gated. A build whose only inference driver is an external backend still has to start, stay healthy, report cost, and be reachable over Socket.IO, so this module ships in every build.

## What's in it

| Folder | Purpose |
| --- | --- |
| [`about_app/`](about_app/README.md) | The desktop app's user-facing capability catalog: what each feature does, its maturity, and its privacy disclosure. |
| [`connectivity/`](connectivity/README.md) | Reachability diagnostics (`connectivity_diag`) and the listen-port selection logic used when the core binds its HTTP listener. |
| [`cost/`](cost/README.md) | Local token-usage and USD cost tracking, with a 7-day dashboard over JSON-RPC. |
| [`doctor/`](doctor/README.md) | Self-check probes over config, workspace, the daemon state file, and the embedding provider, aggregated into a `DoctorReport`. |
| [`health/`](health/README.md) | In-process component health registry, driven by domain events, backing `GET /health`. |
| [`proc_metrics/`](proc_metrics/README.md) | Cross-platform process (and process-tree) RSS sampling used by the RSS benchmark harness. |
| [`service/`](service/README.md) | Installs the core as a per-user OS service and drives self-restart / graceful shutdown. |
| [`socket/`](socket/README.md) | The persistent Socket.IO client that keeps the core connected to the hosted backend. |
| [`startup/`](startup/README.md) | One-shot workspace migrations run during core boot. |
| [`update/`](update/README.md) | Self-update: checks GitHub Releases, downloads and stages a new binary, and triggers a restart. |

## How it fits

Everything under `platform/` answers questions about the process itself rather than about what the agent is doing: is it running, is it healthy, what did it cost, is it connected, does it need an update. Most of these domains expose a small `*.rs` RPC surface registered into the global controller registry in `crates/openhuman-core/src/core/all.rs`, the same way business-domain modules do, so the frontend and CLI reach them through ordinary JSON-RPC rather than a side channel.

A few subfolders read state that other domains own instead of maintaining their own: `doctor` reads the daemon state file that `service` writes and the memory-tree database that `memory` owns, and `health` is driven entirely by events other domains publish rather than by direct calls into them.

## Key types

There is no single shared type across `platform/`; each subfolder defines its own (`DoctorReport`, `HealthSnapshot`, `CostTracker`, `ServiceStatus`, and so on). See each subfolder's README for its public surface.

## Where next

Start with the subfolder README for the concern you're touching. `service/README.md` and `update/README.md` are the pair to read together if you're changing how the core restarts itself; `health/README.md` and `connectivity/README.md` if you're changing what "is the app connected" means to the frontend.
