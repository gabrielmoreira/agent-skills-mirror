# Maintainer flow

Follow the [maintenance contract](maintenance-contract.md) and canonical maintainer skill. Required protection and semantic review remain unchanged; orchestration is resumable and component validation replaces unconditional repeated full suites.

`maintainer:dossier` and `release:plan` are read-only reports. They do not grant merge, publication or host-configuration authority. The dossier's policy digest identifies the exact policy consulted; refresh after protected-base changes.

Use `merge:batch -- --prepare-only` for safe analysis before semantic review. Use a private external `--state-dir` to preserve review receipts and batch attempts. A blocked PR does not stop independent PRs, but leaves the command unsuccessful. On resume, current GitHub state and protection override journal hints.

Ordinary source merges do not run a canonical PR cycle. Distribution snapshots and generated credits refresh in the release PR. Final main CI proves the source component plan; full distribution tests belong to the immutable candidate. Separate public release status from personal client reload status.
