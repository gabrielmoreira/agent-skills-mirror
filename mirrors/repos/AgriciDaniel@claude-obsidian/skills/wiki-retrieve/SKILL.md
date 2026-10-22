---
name: wiki-retrieve
description: "Build and query a vault-local contextual BM25 retrieval index with optional multilingual Nomic cosine reranking; use for retrieve, hybrid retrieval, BM25, rerank, contextual retrieval, chunk search, vault search, semantic search, find relevant passages, or retrieval diagnostics. Derived caches stay under .vault-meta, remote egress requires explicit consent, and unavailable reranking falls back deterministically."
---

# Retrieve relevant passages

This extension derives search data from `wiki/` into `.vault-meta/`. It never
changes canonical notes. Always pass the selected vault explicitly.

Resolve the installed product root from this skill's own location, not from the
vault or current working directory:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
PREFIX="$PRODUCT_ROOT/scripts/contextual-prefix.py"
BM25="$PRODUCT_ROOT/scripts/bm25-index.py"
RETRIEVE="$PRODUCT_ROOT/scripts/retrieve.py"
RERANK="$PRODUCT_ROOT/scripts/rerank.py"
test -f "$PREFIX" && test -f "$BM25" && test -f "$RETRIEVE" && test -f "$RERANK"
```

## Pipeline

1. `contextual-prefix.py` splits pages on paragraph boundaries and stores the
   raw chunk plus a short page-level prefix.
2. `bm25-index.py` builds a local, standard-library BM25 index over the
   contextualized text.
3. `retrieve.py` selects BM25 candidates, optionally reranks them, rejects
   invalid records, deduplicates by page, and returns paths and snippets.
4. The caller reads the returned pages and performs synthesis; retrieval output
   is not itself evidence.

## Provision locally

Preview first, then build synthetic prefixes without network egress:

```bash
python3 "$PREFIX" --vault "$VAULT" --all --no-llm --peek
python3 "$PREFIX" --vault "$VAULT" --all --no-llm
python3 "$BM25" --vault "$VAULT" build
python3 "$RETRIEVE" --vault "$VAULT" "wiki" --top 1 --no-rerank --explain
```

Chunk and index files are disposable runtime state. Incremental prefixing skips
records whose chunk hashes, page hashes and provider/model profile still match.
Legacy records without that profile regenerate on an explicit build. A complete scan removes
surplus records for deleted pages, and the prefixer invalidates the BM25 index
before changing its chunk set so a mixed stale index is not served.
Prefix and BM25 build operations share the vault-wide mutation lock with every
other writer; a busy vault fails closed instead of publishing a partial index.

## Contextual-prefix privacy

Synthetic prefixes use only local frontmatter and page text. The explicit
Anthropic API profile can send page bodies off-machine and requires the user's
consent plus `--allow-egress` and a configured API key. There is no Claude CLI
generation tier or ambient subprocess fallback. Never infer consent from an
API key or installed binary. Preview the scope first and state which provider
will receive what data.

Remote Ollama endpoints also require explicit approval and
`--allow-remote-ollama`; the default reranker accepts localhost only.

Local model prefixes are a separate explicit option. Use an already installed
exact `name:tag`; no server is started and no model is installed or pulled:

```bash
python3 "$PREFIX" --vault "$VAULT" --all --local-ollama --ollama-model installed:tag --peek
python3 "$PREFIX" --vault "$VAULT" --all --local-ollama --ollama-model installed:tag
```

The prefix adapter verifies cloud-disabled server status and local model
identity before sending page text. Unsupported or unavailable preflight falls
back to synthetic prefixes for new or changed chunks only; prefixes from the
same endpoint and model stay in place, so a transient outage leaves an
unchanged vault's chunks and BM25 index untouched. This requirement can exclude
older Ollama servers.
Reranking and tiling use the same local-only proof before query, page, chunk,
or embedding cache work. `--allow-remote-ollama` approves the endpoint, not
cloud delegation by the server.
See [prefix providers](../../docs/prefix-providers.md) for the exact policy,
cloud model selection and verification limits. The reranker has its own model
and endpoint policy; selecting local prefixes does not enable reranking.

## Query

For a strictly read-only lookup, use the prebuilt BM25 index:

```bash
python3 "$RETRIEVE" --vault "$VAULT" "$QUERY" --top 5 --no-rerank --explain
```

For an explicitly requested rerank, omit `--no-rerank`. The default is Ollama's
multilingual `nomic-embed-text-v2-moe` model (approximately 958 MB); the product
never pulls it automatically. To use an already-installed, smaller,
English-oriented v1.5 model, pass `--model nomic-embed-text` explicitly.
Nomic models use `search_query:` for the query and `search_document:` for
candidate text. Nomic v2 has a 512-token input context and Ollama truncates
longer embedding inputs by default; BM25 still scores the complete chunk.
Embeddings are cached by exact model, verified digest, input scheme, and hash
of the exact prefixed input. A missing local Ollama service, malformed HTTP
reply, missing selected model, unusable vector, or any candidate embedding
failure falls back for the complete result set to the original BM25 order; it
never mixes cosine and BM25 score scales.

Query input is bounded at 8,000 normalized characters and result counts must be
between 1 and 1,000. Oversized queries and invalid limits fail with an
actionable usage error instead of looking like an empty successful search.
An untagged model request matches only the installed untagged name or its
`:latest` alias; select any other tag explicitly.

Use direct diagnostics when needed:

```bash
python3 "$BM25" --vault "$VAULT" stats
python3 "$BM25" --vault "$VAULT" query "$QUERY" --top 10
python3 "$RERANK" --vault "$VAULT" "$QUERY" --peek
python3 "$RERANK" --vault "$VAULT" "$QUERY" --model nomic-embed-text --peek
```

## Integrity rules

- Accept only relative chunk and page paths whose resolved targets remain under
  `$VAULT/.vault-meta/chunks/` and `$VAULT/wiki/` respectively.
- Reject hashless legacy chunk records and require chunk-body, page, and index
  hashes to match before a cached record can be built or served.
- Reject absolute paths, symlink escapes, missing pages, mismatched chunk IDs,
  changed page hashes, and stale index/chunk hash pairs.
- Rerank the full candidate set, then deduplicate by page, then apply `--top`.
- An empty index is an honest no-result state. A missing or corrupt index makes
  `retrieve.py` exit 10 with a stable rebuild command; callers fall back to the
  standard vault query/text-search path and do not fabricate matches.
- Do not cite benchmark percentages unless a reproducible vault-specific
  benchmark produced them.

Measure a prebuilt index against explicit labels with `bench --queries FILE
--vault VAULT`. See [offline retrieval evaluation](../../docs/retrieval-evaluation.md)
for recall, MRR, missing labels and negative cases. This is a read-only
measurement and never silently rebuilds an index or calls a model.

## Checkpoint

Observe cache readiness and privacy boundaries, think about whether lexical or
semantic ranking is needed, verify returned paths and source freshness, and
grow by measuring retrieval misses against a maintained local query set.
