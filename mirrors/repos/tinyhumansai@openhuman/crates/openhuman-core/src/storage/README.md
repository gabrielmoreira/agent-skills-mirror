# storage

The process's storage backend on the
[tinystoragedrivers](https://github.com/tinyhumansai/tinystoragedrivers)
ports, vendored through `vendor/tinyagents/vendor/tinystoragedrivers`.

One URL picks it: `OPENHUMAN_STORAGE_URL`, else `[storage] url` in
`config.toml` (`config::StorageConfig`). With neither set, the desktop
default, nothing is opened and every domain keeps the classic on-disk layout
under the workspace.

| URL | Driver | Cargo feature |
| --- | --- | --- |
| `memory` | in-process, keeps nothing | always |
| `sqlite:<path>` (a `.db` file, or a directory with one file per database) | SQLite | `storage-sqlite` |
| `mongodb://…/<db>`, `mongodb+srv://…/<db>` | MongoDB, one database shared by every scope | `storage-mongodb` |
| `file:<dir>` | JSON and JSONL files | `storage-file` |

A URL for a driver the build lacks fails at `open`, naming the feature. None
of the features are in the shipped desktop product yet; a cloud build turns
on `storage-mongodb`.

## Entry points

- `configured_url(&Config)` / `url_from(env, &Config)`: the URL in effect.
- `open(url)`: parse and open a backend (credentials are redacted in logs).
- `install(backend)` / `installed()` / `clear()`: the process slot domains
  read the backend from.
- `scope_for_agent(agent_id)`: the storage scope an agent's records live
  under, the same mapping TinyAgents' `DriverSessionStores` uses, so every
  domain agrees.
- `driver_is_shared(driver)` / `installed_is_shared()`: whether other
  processes may write the same backend (MongoDB). Boot-time recovery, such
  as the orphaned-run sweep, is skipped on a shared backend.
- `driver_has_cross_process_cas(driver)`: whether a compare-and-swap on
  that driver is atomic across processes (MongoDB, SQLite), which a
  clustered node's leases need. Memory and file drivers coordinate only
  within one process.
- `current_scope()` / `current_scoped()`: the acting agent's scope (`local`
  on a single-user host; an error in SaaS mode with no acting agent) and the
  installed backend under it.
- `block_on(future)`: runs a storage future from synchronous store code on
  one shared runtime thread.
- `documents::Repo` and `documents::compare_and_swap`: the base the domain
  stores build on. A `Repo` holds one domain's scoped document handle,
  declares its collections and runs each call; `compare_and_swap` is the
  guarded-`UPDATE` loop.

## Leases

`storage::lease` gives one node exclusive, expiring ownership of a key; the
SaaS profile host uses it so exactly one core process serves a profile.
`LeaseStore` has four operations, each taking the caller's clock (`now_ms`)
so the rules never read the wall clock:

- `acquire(key, now_ms)` takes the key when it has no record, or its record
  is released, expired (`now_ms >= expires_at_ms`) or already this node's;
  otherwise `LeaseError::Held(record)` names the owner, its endpoint and
  (`retry_after_ms`) when to retry. Epochs start at 1 and every acquisition
  except a re-entrant one (the same store instance re-acquiring the epoch it
  holds) writes `epoch + 1`.
- `renew(grant, now_ms)` extends the grant by CAS on its record version; any
  write since (a takeover, a release) makes it `LeaseError::Lost`.
- `release(grant)` writes `released = true` under the same CAS and keeps the
  record.
- `holder(key)` returns the stored record, live or not (`is_live(now_ms)`).

A grant's `previous_unclean` is set exactly when the acquisition replaced a
record that was not released and that this store instance did not hold: a
foreign holder that expired, or this node's own id left by a crashed earlier
process. The profile host runs workspace recovery on it. Node ids must be
unique among live processes.

| Store | Where | Use |
| --- | --- | --- |
| `DocumentLeases` | one document per key, scope `cluster`, collection `leases`; every write carries `Precondition::Absent` or `Version` | clustered nodes on a driver with cross-process CAS |
| `LocalLeases` | an exclusive `fs2` flock on `<root>/<sha256(key) hex>/.lease`, record in `.lease.json` beside it; no expiry, the OS drops the lock when the process dies | hosts without a backend |

Keys are 1 to 200 bytes of ASCII letters, digits and `- _ . @`, not starting
with `.`, so they are safe as directory names and document ids. The scope
`cluster` is shared by every node; an agent whose id is literally `cluster`
would map to the same scope (`scope_for_agent`).

Tests: `lease_tests.rs` (the acquire rule), `lease_documents_tests.rs`
(contention, expiry, takeover, stale renew, clean release, and an
eight-thread race on a SQLite file with `--features storage-sqlite`),
`lease_local_tests.rs` (two instances on one root, crashed holder), and
`lease_model_tests.rs`, a proptest state machine of random acquire, renew,
release, clock and crash steps across 2 to 4 nodes checked against a
reference model.

## Consumers

- The session store: `openhuman_rpc::session_store::install_for_host` opens
  the configured backend before boot and installs `DriverSessionStores`
  over it. See that module's README.
- Domain stores that switch to the document port when a backend is
  installed, each in a `store_documents.rs` beside its SQLite `store.rs`:
  approvals (`security::approval`), paired devices (`security::devices`),
  notifications (`desktop::notifications`) and task sources
  (`integrations::task_sources`).
- tinyflows' own stores on the ports (`tinyflows-drivers`), picked per call
  the same way: cron jobs and runs (`cron::store`, `CronDocuments`), the flow
  catalog and drafts (`flows::store`, `flows::draft_store`,
  `FlowCatalogDocuments`), per-flow engine state and dedup settlement
  (`flows::tinyflows::state::FlowState`), and the flow-run checkpointer
  (`DriverCheckpointer`). The delegation graph's checkpointer uses
  tinyagents-graph's `DriverCheckpointer`.
- `block_on_anyhow(future)`: `block_on` for those stores, whose errors are
  `anyhow::Error` (a typed `FlowUpdateError` passes through unchanged).
- Approvals (`security::approval`), through `store_documents.rs`.
- Secrets (`storage::secrets`): the keyring's user secrets
  (`security::keyring::get` / `set` / `delete`) and the credential stores'
  files (`auth-profiles.json`, `http-credentials.json`) become encrypted
  documents (`DocumentSecrets`, `enc2:`) in the acting agent's scope. Each
  scope's data key is derived with HKDF-SHA256 from the keyring master key
  (`OPENHUMAN_KEYRING_MASTER_KEY` / `_FILE`, else the OS keychain); with no
  master key they fail closed. The config encryption key stays on the
  process keyring, because `config.toml` is loaded before any agent acts.

## Background work and agent scopes

Work done inside an agent's turn runs under that agent's `CoreContext`
(`session_agent`, set for embed agents and SaaS profiles), so with a
backend installed its records land in that agent's scope. Background work
runs under the process default context and on its own would only see
`local`. `storage::agents` closes the gap:

- Known agents: the live ones are `core::runtime::AgentContextRegistry`'s
  (embed registers each agent it builds and deregisters it on drop).
  `AgentContextRegistry::register` also records the agent id in the
  backend's `local` scope (`storage_agents`, `agents::record`), so a
  restarted process still knows it; `agents::contexts()` lists both.
- `for_each_scope(label, step)`: runs `step` for `local`, then under each
  known agent's context — its live one, or the default context acting for it
  (`CoreContext::for_agent`). `for_each_agent` skips `local`.
- `within_agent(agent, fut)` / `context_for(agent)`: re-enter an agent's
  scope when background work learned whose record it is handling.
- `find_owner(label, probe)`: the scope (`local` first, then each agent)
  where a record named only by id lives — for event subscribers, whose
  events carry ids but no agent.

Users: the task-source poller, the flows boot sweep and schedule-trigger reconcile, the run reaper,
the device tunnel (a paired device's frames run as the agent that paired
it, `security::devices::owner`), and the event subscribers: a flow's
schedule tick, run digest and dedup settlement run as the flow's owner
(`flows::bus::owner`); Composio app-event triggers and new connections are
matched in every scope; a cron job's completion notification is stored with
the job's owner. Without a backend these run once, as
before. The cron scheduler visits live agents only
(`cron::scheduler::tick_live_agents`): an agent's jobs need its live
context (host tools, prompt) to run, so a recorded agent's jobs wait until
it is live again; with a backend it no longer needs the agent's `jobs.db`. In SaaS mode agent ids are not recorded and `local` is skipped;
per-user background work there is `profiles::background`.

## Boundaries

The ports, drivers, scopes and conformance suites are tinystoragedrivers';
the session store over them is `tinyagents-session`. This domain only
resolves the URL, opens the backend, and holds it for the process. The
`[storage]` section is bootstrap configuration and is never read from
storage itself.
