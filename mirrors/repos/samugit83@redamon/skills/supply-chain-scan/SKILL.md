---
name: supply-chain-scan
description: >
  Working on RedAmon's supply-chain scanner (offline OSV + GuardDog + retire +
  trufflehog): the offline OSV database that the scan path does not bootstrap,
  the world-readable requirement for the hardened scanner, and the soft-error
  markers that record what was never analysed.
  Trigger: editing scanners/supply_chain_common/, scanners/supply_chain_analyzer/ or
  scanners/supply_chain_scan/; touching osv_db_sync.py, osv_runner.py, guarddog_runner.py,
  deep_recovery.py, or the offline OSV database handling.
license: MIT
metadata:
  author: redamon
  version: "1.0.0"
  scope: [supply_chain]
  auto_invoke:
    - "Editing the supply-chain scanner or its offline OSV database handling"
---

## When to Use

- Changing any of the three supply-chain layers (OSV, GuardDog, retire/trufflehog)
  or the offline database plumbing.

The `supply_chain_common`-must-be-bind-mounted rule is in the
[AGENTS.md](../../scanners/supply_chain_scan/AGENTS.md) CRITICAL RULES; this skill is the
scanning behaviour.

---

## Critical Rules

- **NEVER assume the offline OSV database is populated.** It is filled lazily,
  per-ecosystem, only on the explicit `--download-offline-databases` step - NOT on
  every scan and NOT at install time
  ([scanners/supply_chain_common/osv_db_sync.py](../../scanners/supply_chain_common/osv_db_sync.py)).
  A scan against an unsynced ecosystem must report it as missing, not crash.
- **NEVER `chmod` the OSV DB tighter than world-readable.** The scanner runs
  hardened and non-root; `osv_db_sync.py` makes the whole tree
  world-readable/traversable on purpose so the scanner can read it. Restricting it
  breaks offline scans silently.
- **NEVER erase an existing soft-error marker on a failed/invalid analysis.** A
  package the analyzer never actually inspected is recorded as a `soft_error`
  ([scanners/supply_chain_common/deep_recovery.py](../../scanners/supply_chain_common/deep_recovery.py));
  invalid GuardDog output must be dropped, not allowed to overwrite those markers
  (regression fixed in commit `c5cd6a16`).
- **NEVER run the OSV binary without the `--offline` pairing.** Offline mode uses
  the `--offline --download-offline-databases` pair; using one without the other
  either hits the network or reads an empty DB.

---

## Layers

| Layer | Runner | Note |
| --- | --- | --- |
| known vulns | [osv_runner.py](../../scanners/supply_chain_common/osv_runner.py) + [osv_db_sync.py](../../scanners/supply_chain_common/osv_db_sync.py) | offline OSV DB (named volume, lazily synced) |
| malicious behaviour | [guarddog_runner.py](../../scanners/supply_chain_common/guarddog_runner.py) | GuardDog heuristics; soft-errors via [deep_recovery.py](../../scanners/supply_chain_common/deep_recovery.py) |
| dispatch | [analyzer_dispatch.py](../../scanners/supply_chain_common/analyzer_dispatch.py) | routes a package to the right analyzer |

## Commands

```bash
./redamon.sh supply-chain-sync <ecosystems>    # bootstrap the offline OSV DB (separate from scans)
./redamon.sh test unit                         # supply_chain_* under the root-agent section
```

## Resources

- [docs/readmes/README.SUPPLY_CHAIN.md](../../docs/readmes/README.SUPPLY_CHAIN.md) - the 3-layer architecture and offline DB volume
- Related: supply_chain [AGENTS.md](../../scanners/supply_chain_scan/AGENTS.md) CRITICAL RULES (bind-mount `supply_chain_common`)
