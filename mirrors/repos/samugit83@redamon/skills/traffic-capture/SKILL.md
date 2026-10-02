---
name: traffic-capture
description: >
  Working on the HTTP capture proxy and its replay/fuzz path: the egress guard
  that stops the proxy becoming an SSRF pivot, why it checks the resolved IP, and
  keeping capture off the scan's critical path.
  Trigger: editing scanners/capture_proxy/ (capture_addon.py, egress.py, ingest_worker.py);
  adding a forward/replay/fuzz path; changing EgressPolicy or the internal
  denylist; wiring an agent tool that replays captured traffic.
license: MIT
metadata:
  author: redamon
  version: "1.0.0"
  scope: [capture_proxy]
  auto_invoke:
    - "Editing the capture proxy, egress guard, or replay/fuzz path"
---

## When to Use

- Changing how the proxy forwards, captures, ingests, or replays traffic.

The one-line "route every egress through the guard" rule is in the capture_proxy
[AGENTS.md](../../scanners/capture_proxy/AGENTS.md) CRITICAL RULES; this skill is the mechanism.

---

## Critical Rules

- **NEVER match the internal denylist on the hostname alone.** The guard denies
  on the **resolved IP** (RFC1918 and friends), because a hostname that resolves
  to an internal address (or re-resolves after a check) is the SSRF/DNS-rebinding
  case. See [scanners/capture_proxy/egress.py](../../scanners/capture_proxy/egress.py) (the block
  conditions operate on the resolved IP).
- **NEVER build a replay/fuzz target from unvalidated LLM output and send it
  straight out.** The replay path is a new egress path; it must pass the same
  `EgressPolicy` guard as captured traffic, or the agent can be steered into an
  internal pivot. Args must not reach the wire un-guarded.
- **NEVER remove a block condition to "make replay work".** Each condition is
  individually toggleable via `EgressPolicy` (surfaced in settings); loosen it
  there, per-condition, not by deleting the check.
- **ALWAYS keep capture and ingest off the scan's critical path.** Capture writes
  an append-only spool; a separate worker tails it into Postgres
  ([scanners/capture_proxy/ingest_worker.py](../../scanners/capture_proxy/ingest_worker.py)). That
  decoupling is deliberate - capture must never block or slow the scan it observes.

---

## The capture pipeline

| Stage | File | Note |
| --- | --- | --- |
| intercept | [capture_addon.py](../../scanners/capture_proxy/capture_addon.py) | mitmproxy addon; request/response hooks |
| egress guard | [egress.py](../../scanners/capture_proxy/egress.py) | resolved-IP denylist + `EgressPolicy` toggles; the SSRF backstop |
| ingest | [ingest_worker.py](../../scanners/capture_proxy/ingest_worker.py) | tails the spool -> Postgres; off the scan path |

## Commands

```bash
docker compose --profile tools build capture-proxy    # image rebuild (Dockerfile change)
./redamon.sh test unit                                # capture_proxy section
```

## Resources

- [docs/readmes/README.TRAFFIC.md](../../docs/readmes/README.TRAFFIC.md) - capture/replay/fuzz architecture and settings
- Related: capture_proxy [AGENTS.md](../../scanners/capture_proxy/AGENTS.md) CRITICAL RULES (route egress through the guard)
