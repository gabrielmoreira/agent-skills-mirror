# skills/catalog

Module path: `crate::skills::catalog`. RPC namespace: `skill_registry` — a
stable wire contract left unchanged by the module rename (JSON-RPC methods are
still `openhuman.skill_registry_<function>`, the CLI namespace is still
`skill_registry`; see `tests/skill_registry_e2e.rs`).

Owns remote skill catalogs and installed-skill lifecycle:

- Fetch and cache registry catalogs.
- Refresh the remote catalog asynchronously on core load.
- Browse/search registry entries.
- Derive `SKILL.md` download URLs: Hermes bundled/optional skills from
  `docsPath`, GitHub-hosted community skills from `sourceUrl` (blob/tree
  rewritten to `raw.githubusercontent.com`); portal-only sources
  (ClawHub/LobeHub/skills.sh) get no URL and `install` returns an actionable
  error instead of a 404.
- Install catalog entries into the user skills directory.
- Uninstall user-scope skills.
- Host the built-in `skill_setup` agent.

## Key files

| File | Purpose |
| --- | --- |
| `mod.rs` | Feature gate (`skills` Cargo feature) and module wiring; re-exports the controller aggregators |
| `ops.rs` | Catalog fetch/cache, boot refresh, browse/search/sources/categories, download-URL derivation, `install_from_catalog` |
| `store.rs` | Catalog cache at `~/.openhuman/skill-registry/cache.json`, 1-hour TTL, kept past TTL for stale-while-revalidate; `OPENHUMAN_SKILL_REGISTRY_CACHE_DIR` relocates it (tests) |
| `tools.rs` | LLM-callable tools `skill_registry_browse`, `skill_registry_search`, `skill_registry_sources`, `skill_registry_install`, `skill_registry_uninstall` |
| `types.rs` | `CatalogEntry` |
| `schemas/controller_schemas.rs` | `skill_registry_*` `ControllerSchema` definitions and the registered-controller table |
| `schemas/handlers.rs` | Thin RPC handlers dispatching into `ops.rs` |
| `schemas/wire_types.rs` | Request/response payload types for the handlers |
| `stub.rs` | No-op facade compiled in when the `skills` feature is off |
| `agent/skill_setup/` | Built-in `skill_setup` agent (`agent.toml`, `prompt.md`, `prompt.rs`) |

## RPC surface

Functions in `schemas/controller_schemas.rs::all_skill_registry_controller_schemas`,
all under the `skill_registry` namespace:

- `browse` — list cached (or force-refreshed) catalog entries.
- `search` — filter entries by query, source, and category.
- `sources` — distinct upstream sources present in the catalog.
- `categories` — distinct categories present in the catalog.
- `install` — install a catalog entry by `entry_id` into user scope.
- `uninstall` — remove an installed user-scope skill by slug.
- `schemas` — return the `skill_registry` controller schemas (CLI/RPC smoke-test generation).

## Agent tools and the `skill_setup` agent

`tools.rs` exposes the browse/search/sources/install/uninstall operations as
LLM-callable tools (`SkillRegistryBrowseTool`, `SkillRegistrySearchTool`,
`SkillRegistrySourcesTool`, `SkillRegistryInstallTool`,
`SkillRegistryUninstallTool`), re-exported through the
`#[cfg(feature = "skills")]` glob in `crates/openhuman-core/src/tools/mod.rs`.

`agent/skill_setup/` is a built-in agent (id `skill_setup`, delegate name
`setup_skills`) whose tool belt is the five tools above plus
`list_workflows`, `describe_workflow`, `install_workflow_from_url`,
`uninstall_workflow`, and `ask_user_clarification`. It is registered in
`crates/openhuman-core/src/agent/registry/agents/loader.rs` behind
`#[cfg(feature = "skills")]`, which embeds `agent/skill_setup/agent.toml` via
`include_str!` and wires `agent/skill_setup/prompt.rs::build` as its prompt
builder.

## Disabled build

When the `skills` Cargo feature is off, `stub.rs` takes the place of this
module: the controller aggregators return empty vectors and
`ops::start_boot_catalog_refresh` is a no-op, so the always-on call sites in
`core/all.rs` and `core/runtime/services.rs` keep compiling without the real
implementation.

Default catalog:

```text
https://hermes-agent.nousresearch.com/docs/api/skills.json
```

Useful environment overrides for prod scripts and deterministic tests:

```bash
OPENHUMAN_SKILL_REGISTRY_CATALOG_URL=https://example.com/skills.json
OPENHUMAN_SKILL_REGISTRY_DOWNLOAD_BASE_URL=https://example.com/skills
OPENHUMAN_SKILL_REGISTRY_REFRESH_ON_BOOT=0
```

`OPENHUMAN_SKILL_REGISTRY_REFRESH_ON_BOOT=0` disables the best-effort startup
refresh. By default, core startup spawns a background task that force-refreshes
the remote catalog and updates the local cache without blocking core readiness.

Production smoke examples:

```bash
openhuman-core skill_registry schemas
openhuman-core skill_registry browse --force_refresh true
openhuman-core skill_registry search --query git
openhuman-core skill_registry sources
openhuman-core skill_registry install --entry_id git-helper
openhuman-core skill_registry uninstall --name git-helper
```

Security notes:

- `install` and `uninstall` do not implement their own file handling:
  `ops::install_from_catalog` calls
  `skills::ops_install::install_workflow_from_url` and the uninstall handler
  calls `skills::ops_install::uninstall_workflow`, so the parent module's
  hardened URL installer (HTTPS-only, size cap, private-IP rejection,
  `SKILL.md` requirement) applies to catalog installs too.
- HTTP localhost installs require `OPENHUMAN_SKILL_INSTALL_ALLOW_LOCAL_HTTP=1` and are intended for local fixtures only.
