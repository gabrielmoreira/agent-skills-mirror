---
name: orchestrator-container-spawn
description: >
  Spawning and hardening scan containers from the recon orchestrator: the
  security flags that look correct and break the container, and the sibling
  bind-mount path handling. cap_drop and no-new-privileges were each reverted
  after breaking real scans.
  Trigger: editing recon_orchestrator/container_manager.py; changing how a scan
  container is spawned or hardened; touching _scanner_hardening, sibling_host_path,
  cap_drop, security_opt, or a bind mount for a spawned container.
license: MIT
metadata:
  author: redamon
  version: "1.0.0"
  scope: [recon_orchestrator]
  auto_invoke:
    - "Spawning or hardening a scan container from the orchestrator"
    - "Editing container_manager.py bind mounts or security options"
---

## When to Use

- Changing how the orchestrator launches or secures a scan container
  ([recon_orchestrator/container_manager.py](../../recon_orchestrator/container_manager.py)).

For the no-`env_file` knob rule, see the recon_orchestrator
[AGENTS.md](../AGENTS.md) CRITICAL RULES (not repeated here).

---

## Critical Rules

- **NEVER add `cap_drop: [ALL]` to a scan container that writes to a host-owned
  source bind mount.** It strips `CAP_DAC_OVERRIDE`, so root-in-container can no
  longer write the host-owned files, and the scan breaks. This was reverted after
  breaking recon/partial spawns; hardening is deliberately deferred with
  `drop_caps=False` at **every** spawn site
  ([container_manager.py:837](../../recon_orchestrator/container_manager.py#L837),
  :1798, :2168). Keep it deferred unless the mount is not host-owned.
- **NEVER add `security_opt: no-new-privileges` to these spawns.** It breaks
  `execve` for non-root users inside the recon image (reverted once already):
  [container_manager.py:939](../../recon_orchestrator/container_manager.py#L939).
- **NEVER add a `tmpfs` mount without `uid`/`gid`/`mode` when the container runs
  as a NON-ROOT user and the mount lands on a path that user must write.** Docker
  mounts a tmpfs **root-owned 0755** unless told otherwise (only `/tmp` gets the
  1777 default), and the mount SHADOWS whatever the image built at that path - so
  a tmpfs added to *give* a non-root user writable scratch is what *takes it
  away*. This shipped: the TruffleHog spawn's `/home/trufflehog` tmpfs hid the
  home dir `useradd --create-home` had given uid 10001, and `github_experimental`
  died on "failed to create .trufflehog folder in user's home directory" while
  the other thirteen sources were fine, because it is the only one that writes to
  `$HOME`. Build the spec in
  [`_trufflehog_tmpfs()`](../../recon_orchestrator/container_manager.py#L4644),
  not inline, and size-cap every entry - an uncapped tmpfs is host RAM a hostile
  archive can exhaust.
- **ALWAYS apply hardening through `_scanner_hardening()`**
  ([container_manager.py:567](../../recon_orchestrator/container_manager.py#L567)),
  not ad-hoc per spawn, so all three spawn sites stay consistent.
- **ALWAYS keep `sibling_host_path()` robust to BOTH POSIX (`/`) and Windows
  (`\`) host paths** ([container_manager.py:53](../../recon_orchestrator/container_manager.py#L53)).
  It derives a sibling source dir's host path for bind mounts; a POSIX-only
  assumption breaks spawns on Windows hosts. Its two companions
  [`parent_host_path()`](../../recon_orchestrator/container_manager.py#L77) and
  [`join_host_path()`](../../recon_orchestrator/container_manager.py#L90) carry the
  same POSIX+Windows discipline - never swap in `pathlib` / `Path(...).parent`,
  which collapses a Windows host path on the Linux orchestrator.
- **NEVER assume a scanner source dir is a repo-root sibling.** Scanners live two
  levels deep under `scanners/<name>/`, so a bind mount to a repo-root sibling
  (e.g. `graph_db`) must climb out of `scanners/` first:
  `sibling_host_path(parent_host_path(scanner_path), "graph_db")`, and a
  `scanners/`-nested sibling is reached with
  `join_host_path(parent_host_path(recon_path), "scanners", "supply_chain_common")`.
  The old `sibling_host_path(scanner_path, "graph_db")` now resolves to a
  nonexistent `scanners/graph_db`; Docker silently binds an empty root-owned dir
  there and graph writes / imports fail with no error. The build context climbs
  two parents: `parent_host_path(parent_host_path(scanner_path))`.
- **NEVER bind `/app/graph_db` directly at a spawn site. Always route it through
  `self._graph_db_mount(<derived>, baked_into_image=...)`**
  ([container_manager.py:605](../../recon_orchestrator/container_manager.py#L605)).
  Deriving graph_db's host path is a LAST RESORT, not the mechanism: the real
  path is auto-detected from the orchestrator's own `./graph_db:/app/graph_db:ro`
  mount (`GRAPH_DB_PATH`, resolved in `api.py` exactly like `RECON_PATH`). The
  derivation is only right when Docker reports the literal repo path - Docker
  Desktop on Windows/WSL2 reports rewritten bind `Source` strings whose sibling
  is nowhere, Docker auto-creates that path EMPTY, and the empty dir shadows the
  graph_db baked into the scan image. Every spawned scan then dies with
  `cannot import name 'Neo4jClient' from 'graph_db' (unknown location)`
  (issue #169). `baked_into_image=True` for recon / gvm / github-hunt (they COPY
  graph_db, so no mount beats a wrong mount); `False` only for supply-chain,
  which does not bake it. TruffleHog has NO graph_db mount at all: its container
  is the dirty half of a dirty/clean split and holds no Neo4j credentials, so
  the orchestrator ingests its findings afterwards.
- **ALWAYS resolve a new host source path with `_get_host_path()` + a compose
  mount, not by string surgery on another path.** If a spawn needs host dir `X`,
  mount `X` into the orchestrator so Docker itself reports its source. A missing
  bind source is not an error to Docker; it silently becomes an empty directory.

---

## Why these flags break here

Scan containers run as root and **bind-mount host-owned source** (the live
working tree) so a `.py` change is picked up without a rebuild. Standard
container hardening (drop all caps, no-new-privileges) assumes the container owns
its filesystem and runs unprivileged - neither holds here, so the "secure
defaults" a reviewer would add are exactly what broke production twice.

## Commands

```bash
docker compose restart recon-orchestrator     # container_manager.py is volume-mounted
./redamon.sh test unit                        # recon_orchestrator section
```

## Resources

- [recon_orchestrator/container_manager.py](../../recon_orchestrator/container_manager.py) - the three spawn sites and `_scanner_hardening`
- Related: recon_orchestrator [AGENTS.md](../AGENTS.md) CRITICAL RULES (the no-`env_file` knob rule)
