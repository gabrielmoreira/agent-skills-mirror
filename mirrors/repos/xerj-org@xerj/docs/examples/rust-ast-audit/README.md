# Rust AST security substrate for XERJ

Tools that turn a Rust workspace into a queryable security substrate in XERJ, so
an AI agent can *interrogate* the code instead of reading all of it. Built to
audit XERJ's own engine — see the case study in
[`../../case-studies/xerj-self-audit/`](../../case-studies/xerj-self-audit/).

## Scripts

- **`rust_ast_index.py`** — tree-sitter-rust extractor. Walks a workspace and
  emits three NDJSON streams (`functions`, `calls`, `routes`) plus `coverage.json`
  and `unsafe_inventory.json`. Records carry the security-relevant AST facts:
  unsafe ops, panic/abort sites, `as` casts, allocation-from-parameter shapes,
  axum extractors, filesystem/process/deserialize sinks, validator calls, and
  lock-across-await. 100% function coverage on XERJ's engine, asserted against an
  independent AST node count.
- **`ingest.py`** — creates three XERJ indices with **explicit** mappings (exact
  values are `keyword`, code bodies are `text`) and bulk-loads the streams,
  asserting sent == indexed.
- **`find_recursion_cycles.py`** — the query grep cannot express: strongly-
  connected components of the free-function call graph, flagging cycles with no
  depth guard (the stack-overflow-from-nesting shape). Method-call edges are
  excluded on purpose (unresolvable without type inference).

## Quick start

```bash
python3 -m venv venv && . venv/bin/activate
pip install tree-sitter==0.26.0 tree-sitter-rust==0.24.2
python3 rust_ast_index.py ../../../engine --out ./ast-out
# boot xerj on 9310 (see the case study REPRODUCE.md), then:
python3 ingest.py ./ast-out --url http://127.0.0.1:9310
python3 find_recursion_cycles.py ./ast-out
```

Audit queries with live hit counts: [`QUERY_COOKBOOK.md`](QUERY_COOKBOOK.md).
Committed sample outputs: `sample-coverage.json`, `sample-unsafe-inventory.json`.
