# profiles

In SaaS mode (`core::runtime::Mode::Saas`), each user is served as one
**profile**: the tenant, with its own config, credential, workspace and
sandbox. This domain maps a gateway user to that profile, lays out the
profile's private state, forces the config it runs with, and keeps the open
profiles of the process. A single-user core never serves it: its controllers
belong to `DomainGroup::Operator`, which only `DomainSet::saas()` enables.

## Layout

```text
<root>/users/<profile-id>/          the desktop's users/<id> shape (config::schema::ProfileLayout)
  profile.toml                      ProfileMeta
  config.toml                       the profile's config_path
  workspace/                        sessions, memory, threads, cron, cost
  sandbox/                          action_dir: the only place it may act
<root>/deprovisioned/<id>-<secs>-<uuid>/   an archived profile
<root>/operator/                    the operator plane's own state
```

The desktop config loader resolves a signed-in user's `users/<id>/config.toml`
and `workspace/` through the same `ProfileLayout`, so the two layouts cannot
drift. The older `<root>/agents/u-<hash>/` layout is gone; data left there is
not migrated.

## Profile ids

The top-level `profile_ids` setting (`profile_ids = "hashed"`, not under a table) picks how a gateway user id becomes a `ProfileId`:

- `"raw"` (the default): a user id matching `^[a-z0-9][a-z0-9_-]{0,63}$` is
  used unchanged, so the desktop's 24-hex backend ids pass through. `local`,
  `operator` and anything starting with `h-` are reserved.
- Anything else, or every id under `"hashed"`, becomes `h-` + the first 32 hex
  characters of `sha256(user_id)`.

Both forms fit the agent-id charset and can never contain a path separator.
Changing the mode may re-map users onto different profiles.

## Files

| File | Purpose |
| --- | --- |
| `types.rs` | `ProfileId` and `ProfileIdMode`, `ProfileMeta`, and the operator-plane result types |
| `layout.rs` | The SaaS side of the shared `ProfileLayout`, archived profiles, and `profile_config`: the forced paths, memory binding (pinned to the legacy layout) and autonomy policy |
| `host.rs` | `ProfileHost`: provisioning, lazy open, LRU and idle eviction (never of a profile in use), each profile's derived `CoreContext`, `current()` |
| `gateway.rs` | Which context a gateway request runs under: the operator plane, or the profile of the user named in `X-OpenHuman-User`, after the signature check |
| `surface.rs` | What a user may call: `USER_METHODS`, the exact allowlist applied at dispatch, in the controller list and in `/schema`; the operator scope sees only the operator plane; user thread-id rules |
| `background.rs` | The SaaS background loop: every minute it sweeps idle profiles and runs each profile's queued memory jobs (deferred ingests, belief builds) under that profile's context |
| `tools.rs` | Which agent tools a user gets: the operator's host tool groups (`host_files`, `host_shell`), the hard-deny list, the tool-list filter, the approval gate's SaaS verdict, and the container policy for a user's shell |
| `credentials.rs` | A profile's TinyHumans credential, stored beside its config |
| `ops.rs` | `provision` / `deprovision` / `list` / `status` / `set_credential` / `clear_credential`, returning `Outcome<T>` |
| `schemas.rs` | The `profiles.*` controllers (`profile_id` in and out) |

## Rules

- **Gateway user ids become profile ids in `ops.rs` and `gateway.rs`.** The
  user id itself is never logged. Under raw mode a user id that fits the
  charset *is* the profile id, so it reaches paths, storage and the
  provisioning response; use `"hashed"` where user ids must not. Log lines and
  `Outcome` messages never carry the profile id.
- **A profile's config is forced, not configured.**
  - Every path sits under the profile's directory.
  - Memory is bound to the profile (`[memory] agent_id`, `root = user:<id>`).
    That binding wins over definition pins and team roots.
  - The memory layout is pinned to the legacy tree (confined to that root by
    `memory::user_scope`). Layout v3 would bind the engine below
    `memory::scope::user_root`, which reads `users/<id>` from the config path
    and would answer `org:<id>` or a minted local root instead.
  - The autonomy policy is on and supervised, with no auto-approval, no tool
    installation and no trusted roots.
- **The isolation boundary is the profile's `CoreContext`.** It carries the forced
  config and `session_agent = <profile id>`, and the user families (threads, channels
  for web chat, memory), narrowed further by `surface::USER_METHODS`. Work for a
  user runs under it, which is what the config loader, the session store and
  the per-thread caches key on.
- **Host tools are opt-in and confined.** A user's context has no `Platform`
  family, so shell and file tools are absent unless the operator lists their
  group in `tool_allowlist`:
  - `host_files` (`file_read`, `file_write`, `edit`, `apply_patch`, `grep`,
    `glob`, `list`, `csv_export`, `read_workspace_state`) runs in-process,
    confined by the forced policy to the profile's `sandbox/`. In SaaS the
    policy grants neither `~/OpenHuman/projects` nor `/tmp/openhuman`, which
    every user would share.
  - `host_shell` runs every command in a fresh Docker container
    (`[sandbox]`: image, network, memory and CPU limits): read-only root
    filesystem, all capabilities dropped, no host environment, and the
    profile's `sandbox/` as its only writable mount. If the container cannot
    start, the command fails; it never falls back to the host.
  - Tools that change the process, install code or reach shared state are
    hard-denied whatever the allowlist says (`tools::HARD_DENIED`).
  - There is no per-user approval surface, so the approval gate never parks
    in SaaS: it allows tools from an allowlisted group and refuses the rest.
- **Deprovisioning archives.** The profile's directory moves to
  `<root>/deprovisioned/<id>-<unix-secs>-<uuid>/`. Nothing is deleted. A profile
  still in use is not archived; the call fails and can be retried.

## Gateway contract

```text
Authorization: Bearer <service token>                                  every request
X-OpenHuman-User: <gateway user id>                                    work for a user
X-OpenHuman-User-Sig: t=<unix secs>,v1=<hex hmac-sha256(token, "<t>.<user id>")>
```

- No user header: the request runs on the operator plane.
- With one, `openhuman-rpc`'s `saas_gateway` layer handles it in this order:
  1. It checks the bearer **before** anything else. An unauthenticated caller
     cannot tell which users exist, and cannot open profiles.
  2. It checks the signature: ±60 s, bound to the user id. It is required
     unless the operator sets `require_user_signature = false`.
  3. It opens the user's profile, which must already be provisioned
     (`403` otherwise).
  4. It runs the request under that profile's context. A user's context cannot
     reach the operator plane.
- Routes a SaaS core never serves answer `404`: `/v1`, `/events*`, `/ws/*`,
  `/socket.io`, `/dev/connect` and `/oauth/*`.

## Credentials

The gateway installs each user's session JWT or API key with
`profiles.set_credential`. The credential is stored in the profile's own
auth-profile store, so any backend call made under that profile's context
resolves that user's credential and no other. The process-wide
`auth.set_credential` / `clear_credential` refuse in SaaS mode, because they
activate a user directory and rebind process globals. The core never validates
or echoes a credential.

## User surface

- **What a user's context can reach.** It enables the user families
  (`host::user_domains`: threads so far). Within them, only the methods on
  `surface::USER_METHODS` are live. Anything unlisted answers as an unknown
  method and is absent from `/schema`.
- **Why the operator registers those families too.** `DomainSet::saas()`
  registers them so user contexts can derive them. The surface gate keeps the
  operator scope on the operator plane, so the operator never serves user
  methods on its own workspace.
- **Per-user storage.** Threads live under each profile's workspace. The on-disk
  session store is installed for SaaS and resolves the workspace of the
  calling context, so transcripts and turn states are per user too.
- **Thread ids.** A user may choose ids for their own threads (`threads.upsert`)
  of 1–128 characters from `[A-Za-z0-9_-]`. The core-reserved prefixes
  `channel:`, `proactive:` and `subagent:` are refused.
- **Web chat.** `channel.web_chat`, `web_cancel` and the `web_queue_*` methods
  are open, along with the turn-starting thread methods. Every `WebChannelEvent` is
  stamped with the publishing context's `session_agent` (the profile id) (`WebChannelEvent::agent`, never
  serialized). A user's `GET /events?client_id=` stream runs under that user's
  gateway scope and carries only events stamped with that user's profile. Two
  users on the same client id never see each other's turns. An unstamped event
  belongs to no user. The operator has no chat stream, and browser bind tokens
  are not accepted in SaaS.
- **Per-profile keys.** The web chat session cache, the in-flight turns and the
  parallel (forked) turns are keyed by `session_agent` (the profile id) and id, so caller-chosen thread
  and request ids never collide across users.
- **Deprovisioning** also clears the profile's credential, which lives in the
  process keyring under the profile id. Otherwise a re-provisioned user would
  inherit the old credential.
- **Prompt.** In SaaS the runtime section says `Host: hosted` instead of the
  server's hostname. The `## User` identity block stays empty, because no
  process-wide identity is ever set.

## Background work

A single-user core drains memory jobs from a cron system job behind the process-wide scheduler gate. A SaaS core cannot use either: the cron service is off, and the gate reflects the operator, who holds no credential. So `background::spawn` (started by `saas::build`) runs one loop per process instead. Each tick:

- sweeps idle profiles;
- visits every provisioned profile whose workspace has queued memory jobs (`memory::lifecycle::jobs::has_pending`);
- opens that profile and runs its due jobs under the profile's own context, with its config, credential and memory root.

Profiles with nothing queued are not opened.

On the **first** open of a profile in a process, `recover_workspace` settles anything a previous process left in that profile's workspace:

- turns that were mid-flight are marked interrupted;
- run-ledger rows left running are closed.

A re-open after an eviction never sweeps again, because this process may still be running one of that profile's turns.

User cron jobs are not served yet: the cron RPCs are not on the user surface.
