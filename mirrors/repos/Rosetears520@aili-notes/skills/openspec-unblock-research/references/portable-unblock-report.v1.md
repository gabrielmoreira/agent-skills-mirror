# Portable Unblock Report (JSON) — v1

This is the canonical output. All sink renderings (markdown, task annotations, JSONL logs) are derived from this JSON.

## Top-level shape

```json
{
  "schema": "portable-unblock-report.v1",
  "meta": {
    "created_at": "2026-01-08T12:34:56Z",
    "created_by": "codex",
    "task_id": "optional-caller-id",
    "attempt_id": "optional-caller-id"
  },
  "blocker": {
    "blocker_summary": "...",
    "error_excerpt": "... or null",
    "symptoms": ["..."],
    "already_tried": [
      { "action": "...", "result": "...", "evidence": ["ev:cmd:..."] }
    ],
    "needs": ["..."],
    "environment": {
      "os": "...",
      "shell": "...",
      "runtime": { "name": "...", "version": "..." },
      "tools": [{ "name": "...", "version": "...", "how_verified": "..." }]
    }
  },
  "verification": {
    "repro_command": "... or null",
    "minimal_repro_notes": "...",
    "observed_vs_expected": {
      "expected": "...",
      "observed": "..."
    }
  },
  "research": {
    "query_terms": ["..."],
    "providers_used": [
      {
        "provider_id": "mcp__context7__*",
        "role": "authority",
        "calls": 2,
        "notes": "what was looked up"
      }
    ],
    "evidence": [
      {
        "id": "ev:web:1",
        "kind": "web|docs|repo|cmd-output",
        "pointer": "url|filepath|command",
        "excerpt": "optional short excerpt",
        "captured_at": "2026-01-08T12:34:56Z"
      }
    ]
  },
  "key_conclusions": [
    {
      "claim": "...",
      "confidence": "high|medium|low",
      "because": ["..."],
      "evidence_ids": ["ev:web:1"]
    }
  ],
  "open_questions": [
    {
      "question": "...",
      "why_it_matters": "...",
      "how_to_answer": ["exact command/log to collect", "file to inspect"]
    }
  ],
  "unblock_guidance": [
    {
      "step": 1,
      "action": "exact command / config change / code location",
      "why": "ties to a key conclusion",
      "verify": "how to confirm success",
      "fallback": "what to do if this fails (or null)"
    }
  ],
  "sinks": {
    "requested": [],
    "applied": [],
    "errors": []
  }
}
```

## Confidence rules

- `high`: claim is supported by ≥`min_independent_sources_high_confidence` independent evidence pointers OR one authoritative primary source that unambiguously states the behavior (still include the pointer).
- `medium`: plausible and partially supported but needs a discriminating experiment.
- `low`: hypothesis only; must be phrased conditionally and paired with “how to verify”.

## Sink types (declarative)

Sinks are caller-provided and may be any mix of:

1. `return_only`
   - No filesystem writes; return `report_json` and/or `guidance_md` in-chat.

2. `json_file`
   - Write canonical JSON to `path`.

3. `jsonl_file`
   - Append a one-line JSON object (canonical JSON or a compact summary) to `path`.

4. `markdown_append`
   - Append a rendered markdown block to `path`.

5. `markdown_insert_after_anchor`
   - Insert a rendered markdown block after the first occurrence of `anchor` in `path`.
   - If anchor not found, do not guess; record sink error and fall back to `markdown_append` only if caller explicitly allowed it.

Each sink SHOULD support:
- `content`: `report_json` | `guidance_md` | `both`
- `path`: optional
- `anchor`: optional
- `allow_fallback_append`: optional (default false)

