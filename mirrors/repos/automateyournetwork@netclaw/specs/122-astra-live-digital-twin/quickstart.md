# Quickstart / Manual Verification: Astra Live Digital Twin

This is the human checkpoint checklist — run it at the checkpoints defined in loop.md (after
iteration 0, end of each pass-schedule phase, any stall halt), not as a substitute for the automated
gates in `harness/`.

## Prerequisites

- [ ] `PYATS_TESTBED` points at a CML lab testbed on the lab allowlist (`harness/assert_lab_only.py`
      passes against it standalone: `python3 harness/assert_lab_only.py "$PYATS_TESTBED"`).
- [ ] `OPENAI_API_KEY` present in `.env`; no production credential variables
      (`NETCLAW_PROD_TOKEN`, `PROD_DEVICE_PASSWORD`, `NETBOX_TOKEN`, `SERVICENOW_PASSWORD`) set in the
      loop's shell environment.
- [ ] `codex exec --version` runs successfully.

## Phase A checkpoint — Collector & schema

- [ ] `astra-twin-mcp`'s `get_snapshot()` returns real nodes/links matching what's actually running in
      the lab testbed (cross-check against a direct pyATS query).
- [ ] Stop a lab device or shut a lab interface; within one poll interval, `get_deltas(since_seq=...)`
      returns the corresponding delta.
- [ ] Confirm `astra-twin-mcp` has no write-capable tool in its `tools/list` response — inspect it
      directly, don't take documentation's word for it (FR-005: "not merely unused, but absent").

## Phase B checkpoint — Verification harness (mandatory before Phase C starts)

- [ ] Deliberately break something the gate should catch (e.g., have the collector return a malformed
      snapshot, or blank the HUD's render target) and confirm `harness/run_gates.sh` actually fails.
      This is the "prove the gates catch things" check loop.md requires after iteration 0 — a harness
      that always passes is worse than no harness.
- [ ] `harness/visual_verify.py` produces a non-blank screenshot with the expected node/link element
      counts against a known-good lab snapshot.

## Phase C checkpoint — Live HUD integration

- [ ] Open the HUD, note current camera position, wait for a live delta to arrive — camera position is
      unchanged (FR-008).
- [ ] The node/link that just changed is visually distinguishable from stable state at the moment the
      delta lands (FR-009) — screenshot it, don't just read the code that claims to do this.
- [ ] Disconnect the lab testbed (or the collector) and confirm the HUD's freshness indicator visibly
      goes stale within a reasonable window, rather than silently continuing to show last-known state
      as if it were current (FR-010).
- [ ] Time a real lab change end-to-end (make the change, start a stopwatch, watch the HUD) — under 30
      seconds, no manual reload (SC-001).

## Phase D checkpoint — Astra Twin enrollment & constitution coherence

- [ ] `scripts/in2n-member.py` (or its lookup equivalent) shows "Astra Twin" as a distinct member with
      `model_provider: openai` — an administrator should be able to find this without reading source.
- [ ] Walk the Artifact Coherence Checklist (constitution.md) item by item against the actual diff:
      README.md, `scripts/lib/catalog.sh`, `scripts/lib/install-steps.sh`,
      `scripts/verify-catalog-coverage.py` (run it — zero unexplained gaps), `ui/netclaw-visual/`,
      SOUL.md, `.env.example`, TOOLS.md, `config/openclaw.json`, `mcp-servers/astra-twin-mcp/README.md`.
      Each unchecked item is a Phase D task still outstanding, not a detail to wave through.

## Done-gate

- [ ] Every FR-001..FR-011 and SC-001..SC-006 in spec.md has a named, checkable piece of evidence in
      `loop/state/verdicts.md` — not an assertion that it was "implemented."
