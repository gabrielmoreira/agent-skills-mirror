# Fixture and qualification quickstart

**Mac-first sequencing (owner, 2026-10-18):** [MAC-COMPLETION.md](MAC-COMPLETION.md) records the completed Mac engineering gate. Use the new Mac-complete handoff for Windows smoke/platform differences, followed by Mac regression and final human walkthrough/recording. Existing 84-task scope is unchanged.

Run from `153-ide-installer` or its dedicated WSL qualification branch. Unit/integration fixture state, runtime homes, source copies, editor data and client configuration belong under new disposable roots. Actual production-engine native tests create fresh temporary runtime homes but intentionally use the account's normal authoritative setup journal/lock root and exclusively named launchd/systemd definitions; record that footprint and exercise scoped cleanup. This does not constitute clean-OS qualification. Do not load the owner's existing runtime homes, credential stores or checkout `.env`. Use explicit sanitized subprocess environments; do not alter the shell's HOME. Source-development tests do not package a VSIX or publish anything.

## Local contract sequence

1. Record `git status`, baseline catalog `--list`, source revision and existing test results. Create an OS temporary fixture directory and per-test state/source/home subdirectories; seed distinct fake sibling canaries. Fake values are generated at test runtime and not copied from this host.
2. Run catalog schema/metadata/joins/generation parity and existing installer inventory/coverage checks. Every real skill/component has a disposition; missing authored metadata fails.
3. Run Python engine tests: strict plans/hashes, source/host review binding, classified secret frames, write-ahead journal, unknown observation, writer-survival locks, disconnect pause, explicit resume, component failures, scoped cleanup and secret/private-ID projection. Inject adapters in-process only; no fixture bypass exists in a production plan.
4. Run extension TypeScript check/build and Node contract/regression tests. Simulate every Windows UTF-8/UTF-16/localized gate fixture, malformed outputs and zero-write observations; test non-secret handoff round trips separately.
5. Run isolated source-development editor preview with empty trusted workspace/profile and no runtime. Exercise tree keyboard traversal, invalidation preview, native secret inputs, effect review, cancellation, unknown/pause and explicit resume, report export and two saved connections. Inspect 360px/200%/light/dark/high-contrast layouts. Report real UI observations separately from unit fixtures.
6. Launch the bundled setup MCP adapter using the editor executable with PATH containing no Node. Initialize/list tools, validate closed inputs, try forbidden apply/secret/command payloads, submit native review and prove no automatic effects. Run all three client integration fixtures with isolated configuration and stamped skill copies.
7. Initialize stable Specify 0.7.1 in isolated deployment workspaces, one per client. Add preset, resolve effective commands, test override/collision cases, generate/validate a secret-free plan, submit review, and write back a default redacted report. No unattended dispatch.

Implementation supplies exact commands and actual results in `verification.md`; commands here are a qualification procedure, not fabricated passing evidence.

## Disposable host acceptance

Use a clean Apple-silicon Mac and clean WSL2 Ubuntu 24.04/26.04 targets with snapshots. Native Windows matrix: WSL disabled, WSL1-only, no distro, unsupported distro, missing/disabled extension, unknown list evidence, supported candidate and explicit handoff. Gate snapshots must be unchanged; handoff snapshots may contain only disclosed private state/VS Code remote setup.

For each install target, build focused OpenClaw and Hermes via the wizard and apply the same canonical plan via CLI/Copilot/Claude/Codex/Spec pathways. Compare manifests, selected skill/config registrations and readiness, ignoring only run IDs/times/paths. Create a same-harness second installation and prove detection disclosure, unique homes/services/endpoints/credentials and unchanged first-install files/service state/saved connections. Switch every management control between bindings and verify only the selected identity changes.

For each Border harness, create >=3 members with both harnesses and >=2 providers, covering all four pairs and explicit/inherited choices. Exercise hot and on-demand lifecycles, enrollment uncertainty and controlled routed self-status. Test missing production controls before apply and resume, and explicit testing re-review. Record actual provider/harness/control versions and qualified profiles. Unsupported closures stop rather than inherit historical evidence.

Inject network loss, closed/reloaded editor, canceled native prompt, engine death, host reboot, surviving child, competing run, occupied target, symlink race, port collision and modified/shared cleanup artifact. Assert zero later phases after disconnect and no automatic reopening continuation. Snapshot sibling resources before/after.

Real hosted-provider, channel and network tiers require owner-designated disposable test accounts/endpoints and consent; each external test message needs separate approval. Network tier is read-only. No credentials or transcripts containing them enter artifacts. Record each unrun tier as unverified, with fixture/controlled-provider/live-provider evidence labels.

## Usability and release boundaries

Per the owner's 2026-10-18 SC-002 amendment, run repeatable synthetic scenarios and an owner/build-agent walkthrough. Cover focused setup, shape selection/override, detected existing claws, multiclaw management, cancellation/resume and reports. Record automated versus owner completion, decision time, download time, assistance and shape explanation separately. Record accessibility and minimal-profile performance against the remaining criteria. Community feedback after release is follow-up, not fabricated pre-release participant evidence. Local fixtures do not establish live Tier4 acceptance.

The user authorized implementation/testing on this branch, not changes to real installations, packaging, push, merge or publication. Complete the local preview and present evidence before any separately authorized distribution step. Keep `milestone-draft.md` local and no external tickets/messages are sent by this procedure.
