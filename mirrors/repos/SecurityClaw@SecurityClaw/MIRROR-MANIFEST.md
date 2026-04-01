---
repo: SecurityClaw/SecurityClaw
repoUrl: https://github.com/SecurityClaw/SecurityClaw.git
refType: branch
ref: main
---

# Mirror Manifest

Mirror of `SecurityClaw/SecurityClaw` — 26 default patterns, 0 followed patterns, 44 file(s) materialized.

## Metadata

| Field         | Value |
|---------------|-------|
| Repo          | `SecurityClaw/SecurityClaw` |
| Ref Type      | `branch` |
| Ref           | `main` |
| Default pats  | 26 |
| Followed pats | 0 |
| Files         | 44 |

## Default Sparse Patterns  *(included from config)*

- `**/AGENTS.md`
- `**/CLAUDE.md`
- `**/claude.md`
- `**/gemini.md`
- `**/GEMINI.md`
- `**/SKILL.md`
- `**/skills.md`
- `**/LLMs.txt`
- `**/llms.txt`
- `**/copilot-instructions.md`
- `**/.cursorrules`
- `**/.cursor/rules/**`
- `**/.windsurfrules`
- `**/.continue/**`
- `.github/instructions/**`
- `.github/prompts/**`
- `.agents/**`
- `agents/**`
- `skills/**`
- `skill/**`
- `prompts/**`
- `prompt/**`
- `.cursor/**`
- `.continue/**`
- `.mcp/**`
- `mcp/**`

## Followed Sparse Patterns  *(discovered via markdown refs)*

_None._

## File Index

Legend: **✓** = default pattern · **→** = followed via markdown

| # | S | File |
|---|---|------|
| 1 | ✓ | [`skills/__init__.py`](skills/__init__.py) |
| 2 | ✓ | [`skills/anomaly_triage/instruction.md`](skills/anomaly_triage/instruction.md) |
| 3 | ✓ | [`skills/anomaly_triage/logic.py`](skills/anomaly_triage/logic.py) |
| 4 | ✓ | [`skills/anomaly_triage/manifest.yaml`](skills/anomaly_triage/manifest.yaml) |
| 5 | ✓ | [`skills/baseline_querier/hooks.py`](skills/baseline_querier/hooks.py) |
| 6 | ✓ | [`skills/baseline_querier/instruction.md`](skills/baseline_querier/instruction.md) |
| 7 | ✓ | [`skills/baseline_querier/logic.py`](skills/baseline_querier/logic.py) |
| 8 | ✓ | [`skills/baseline_querier/manifest.yaml`](skills/baseline_querier/manifest.yaml) |
| 9 | ✓ | [`skills/fields_baseliner/instruction.md`](skills/fields_baseliner/instruction.md) |
| 10 | ✓ | [`skills/fields_baseliner/logic.py`](skills/fields_baseliner/logic.py) |
| 11 | ✓ | [`skills/fields_baseliner/manifest.yaml`](skills/fields_baseliner/manifest.yaml) |
| 12 | ✓ | [`skills/fields_querier/instruction.md`](skills/fields_querier/instruction.md) |
| 13 | ✓ | [`skills/fields_querier/logic.py`](skills/fields_querier/logic.py) |
| 14 | ✓ | [`skills/fields_querier/manifest.yaml`](skills/fields_querier/manifest.yaml) |
| 15 | ✓ | [`skills/forensic_examiner/graph.py`](skills/forensic_examiner/graph.py) |
| 16 | ✓ | [`skills/forensic_examiner/hooks.py`](skills/forensic_examiner/hooks.py) |
| 17 | ✓ | [`skills/forensic_examiner/instruction.md`](skills/forensic_examiner/instruction.md) |
| 18 | ✓ | [`skills/forensic_examiner/logic.py`](skills/forensic_examiner/logic.py) |
| 19 | ✓ | [`skills/forensic_examiner/manifest.yaml`](skills/forensic_examiner/manifest.yaml) |
| 20 | ✓ | [`skills/geoip_lookup/__init__.py`](skills/geoip_lookup/__init__.py) |
| 21 | ✓ | [`skills/geoip_lookup/hooks.py`](skills/geoip_lookup/hooks.py) |
| 22 | ✓ | [`skills/geoip_lookup/instruction.md`](skills/geoip_lookup/instruction.md) |
| 23 | ✓ | [`skills/geoip_lookup/logic.py`](skills/geoip_lookup/logic.py) |
| 24 | ✓ | [`skills/geoip_lookup/manifest.yaml`](skills/geoip_lookup/manifest.yaml) |
| 25 | ✓ | [`skills/ip_fingerprinter/__init__.py`](skills/ip_fingerprinter/__init__.py) |
| 26 | ✓ | [`skills/ip_fingerprinter/graph.py`](skills/ip_fingerprinter/graph.py) |
| 27 | ✓ | [`skills/ip_fingerprinter/hooks.py`](skills/ip_fingerprinter/hooks.py) |
| 28 | ✓ | [`skills/ip_fingerprinter/instruction.md`](skills/ip_fingerprinter/instruction.md) |
| 29 | ✓ | [`skills/ip_fingerprinter/logic.py`](skills/ip_fingerprinter/logic.py) |
| 30 | ✓ | [`skills/ip_fingerprinter/manifest.yaml`](skills/ip_fingerprinter/manifest.yaml) |
| 31 | ✓ | [`skills/ip_fingerprinter/port_registry.py`](skills/ip_fingerprinter/port_registry.py) |
| 32 | ✓ | [`skills/network_baseliner/instruction.md`](skills/network_baseliner/instruction.md) |
| 33 | ✓ | [`skills/network_baseliner/logic.py`](skills/network_baseliner/logic.py) |
| 34 | ✓ | [`skills/network_baseliner/manifest.yaml`](skills/network_baseliner/manifest.yaml) |
| 35 | ✓ | [`skills/opensearch_querier/hooks.py`](skills/opensearch_querier/hooks.py) |
| 36 | ✓ | [`skills/opensearch_querier/instruction.md`](skills/opensearch_querier/instruction.md) |
| 37 | ✓ | [`skills/opensearch_querier/logic.py`](skills/opensearch_querier/logic.py) |
| 38 | ✓ | [`skills/opensearch_querier/manifest.yaml`](skills/opensearch_querier/manifest.yaml) |
| 39 | ✓ | [`skills/opensearch_querier/PLANNING_PROMPT.md`](skills/opensearch_querier/PLANNING_PROMPT.md) |
| 40 | ✓ | [`skills/threat_analyst/hooks.py`](skills/threat_analyst/hooks.py) |
| 41 | ✓ | [`skills/threat_analyst/instruction.md`](skills/threat_analyst/instruction.md) |
| 42 | ✓ | [`skills/threat_analyst/logic.py`](skills/threat_analyst/logic.py) |
| 43 | ✓ | [`skills/threat_analyst/manifest.yaml`](skills/threat_analyst/manifest.yaml) |
| 44 | ✓ | [`skills/threat_analyst/reputation_intel.py`](skills/threat_analyst/reputation_intel.py) |

---

*Generated by mirror — do not edit manually*