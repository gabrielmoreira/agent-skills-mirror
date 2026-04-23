# GCX1 — Gortex Compact Wire Format

**Status:** Draft v1. Shipped in Gortex v0.9.0.

GCX1 is a tab-delimited, line-oriented, round-trippable wire format
for Gortex MCP tool responses. It is an opt-in alternative to JSON
selected per-call via `format: "gcx"`. On the benchmark bundled at
`bench/wire-format/` it yields a **median −27.4 % tiktoken savings**
vs JSON with **100 % round-trip integrity** across 20 representative
tool responses.

## Goals

- **Round-trippable.** Every GCX payload decodes back to an
  equivalent Go value. No lossy text.
- **Tokenizer-aware.** Field delimiters, escape sequences, and
  header syntax are chosen so tiktoken (cl100k_base) counts them as
  whitespace or single tokens — matching the LLM budget users care
  about, not just raw bytes.
- **Per-tool tunable.** Hot-path tools (`search_symbols`,
  `find_usages`, `analyze`, ...) ship hand-tuned encoders with fixed
  field layouts. Everything else falls through to a generic
  fallback so no tool ever produces invalid GCX.
- **Versioned.** The header carries a protocol version. Decoders
  reject unknown versions and agents can fall back to JSON
  transparently.

## Non-goals

- Binary encoding. GCX1 is text-only; a future `GCX2` may carry
  binary payloads (CBOR / MessagePack) under the same version
  prefix, but v1 stays text so agents can read raw payloads during
  debugging.
- Schema evolution inside a major version. The field layout for a
  given tool is fixed for the lifetime of `GCX1`. New fields ship
  as `GCX2`.
- Streaming. GCX1 is full-response. `GCX1-stream` is a reserved
  future extension.

## Grammar (EBNF)

```
payload       = section { section } ;
section       = header row-line { row-line | comment } ;
header        = TAG SP "tool=" token { SP key-value } SP "fields=" field-list LF ;
key-value     = token "=" value ;
field-list    = token { "," token } ;
row-line      = value { TAB value } LF | LF ;
comment       = "#" [ SP text ] LF ;
value         = { escaped-char | safe-char } ;
escaped-char  = "\\" ( "\\" | "t" | "n" ) ;
safe-char     = any UTF-8 codepoint except TAB, LF, "\\" ;
TAG           = "GCX1" ;
TAB           = U+0009 ;
LF            = U+000A ;
SP            = U+0020 ;
```

## Header

Each section begins with a single-line header:

```
GCX1 tool=<name> fields=<a>,<b>,... [k=v]...
```

- `tool=` is the MCP tool name (or a dot-suffixed sub-section name
  like `get_callers.edges`).
- `fields=` is a comma-separated list declaring the column order for
  subsequent rows. At least one field is required.
- Additional space-separated `k=v` pairs carry metadata (`total`,
  `truncated`, `etag`, `rows`, `ms`, ...). Keys are emitted in
  sorted order so fixtures stay deterministic.

Header values that contain spaces, `=`, tabs, newlines, or backslashes
must be escaped exactly as row values are escaped.

Example:

```
GCX1 tool=search_symbols fields=id,kind,name,path,line,sig rows=3 total=7 truncated=false
```

## Rows

After the header, each non-blank, non-comment line is a row of
tab-separated values in the order declared by `fields=`.

- Fewer values than declared fields: missing trailing columns default
  to `""`.
- More values than declared fields: decoder returns an error.
- Blank lines between rows are ignored.

## Comments

Lines beginning with `#` are comments. Comments carry no data; any
intermediary may drop them. The encoder uses them to annotate the
first row of a section (e.g. `# 3 matches`).

## Escape rules

A row value may contain the following characters by escaping them:

| Character | Escape |
|-----------|:------:|
| `\` (backslash) | `\\` |
| TAB (U+0009)    | `\t` |
| LF (U+000A)     | `\n` |

Any other `\x` sequence decodes to the literal byte `x` so a
pathological payload cannot wedge the decoder. Callers should treat
decoded values as untrusted input.

CR (U+000D) is stripped on encode so Windows CRLF input round-trips as
`\n`-only output.

## Multi-section payloads

A GCX1 payload may contain multiple sections concatenated back-to-back.
Each new section begins with its own `GCX1` header line. Decoders
detect section boundaries by scanning for the header tag after the
current section's rows exhaust.

Multi-section is used by:

- `get_callers`, `get_call_chain`, `get_dependencies`,
  `get_dependents`, `find_implementations` — emit `<tool>.nodes`
  then `<tool>.edges`.
- `get_editing_context` — emits `target`, `callers`,
  `dependencies`, `tests` sections.
- `get_repo_outline` — one section per top-level key
  (`languages`, `communities`, `hotspots`, `most_imported`,
  `entry_points`).

## Per-tool field layouts (GCX1 v1)

### `search_symbols`

| field | type | description |
|-------|------|-------------|
| id    | string | node ID |
| kind  | string | `function`, `method`, `type`, `interface`, `variable`, `contract` |
| name  | string | short name |
| path  | string | file path |
| line  | int    | start line |
| sig   | string | extracted signature, optional |

Header meta: `total`, `truncated`.

### `get_symbol_source`

| field      | type   | description |
|------------|--------|-------------|
| id         | string | |
| kind       | string | |
| name       | string | |
| path       | string | |
| start_line | int    | |
| end_line   | int    | |
| from_line  | int    | first line of returned source (may precede `start_line` by `context_lines`) |
| sig        | string | |
| etag       | string | content hash for `if_none_match` caching |
| source     | string | full source text, tab/newline-escaped |

Exactly one row.

### `batch_symbols`

| field      | type   |
|------------|--------|
| id         | string |
| kind       | string |
| name       | string |
| path       | string |
| start_line | int    |
| end_line   | int    |
| sig        | string |
| source     | string | *(present only when `include_source=true`)* |
| error      | string | non-empty when the symbol could not be resolved |

### `find_usages`

| field      | type   | description |
|------------|--------|-------------|
| from       | string | caller symbol ID |
| to         | string | called symbol ID (the query subject) |
| edge_kind  | string | `calls`, `references`, `implements`, ... |
| origin     | string | tier: `lsp_resolved`, `lsp_dispatch`, `ast_resolved`, `ast_inferred`, `text_matched` |
| confidence | float  | 0..1 |
| from_name  | string | caller short name |
| from_path  | string | caller file path |
| from_line  | int    | caller start line |

### `get_file_summary`

| field | type   |
|-------|--------|
| id    | string |
| kind  | string |
| name  | string |
| line  | int    |
| sig   | string |

Header meta: `total_nodes`, `total_edges`, `truncated`, `etag`.

### `get_callers` / `get_call_chain` / `get_dependencies` / `get_dependents` / `find_implementations`

Two sections: `<tool>.nodes` then `<tool>.edges`.

- `.nodes` fields: `id`, `kind`, `name`, `path`, `line`.
- `.edges` fields: `from`, `to`, `kind`, `origin`, `confidence`, `label`.

### `get_editing_context`

Four sections. Fields:

- `.target`: `id`, `kind`, `name`, `path`, `start_line`, `end_line`,
  `sig`, `etag`. One row.
- `.callers`: `id`, `kind`, `name`, `path`, `line`.
- `.dependencies`: same as `.callers`.
- `.tests`: `path`.

### `smart_context`

Two sections: `.task` (one row, field `task`) and `.symbols` with
fields `id`, `kind`, `name`, `path`, `line`, `score`, `reason`.

### `analyze`

Kind-polymorphic header tag (`analyze.dead_code`,
`analyze.hotspots`, `analyze.cycles`, `analyze.<other>`):

- `analyze.dead_code`: `id`, `kind`, `name`, `path`, `line`, `reason`.
- `analyze.hotspots`: `id`, `name`, `path`, `line`, `fan_in`,
  `fan_out`, `cross_cut`, `score`.
- `analyze.cycles`: `size`, `severity`, `nodes` (comma-separated).
- Anything else falls through to the generic fallback encoder.

### `contracts`

- `contracts.list`: `id`, `type`, `method`, `path`, `service`,
  `providers`, `consumers` (comma-separated lists).
- `contracts.orphans` (only when `action=check`): `contract_id`,
  `side`, `repo`, `symbol`.

## Generic fallback

Any tool without a hand-tuned encoder routes through the generic
fallback. The fallback inspects the canonical JSON shape:

| Input shape | Output |
|-------------|--------|
| `{}` object | one section, one row, fields = sorted keys |
| `[]` array of objects | one section, one row per element, fields = union of keys (sorted) |
| `[]` array of scalars | one section, field `value`, one row per element |
| scalar | one section, field `value`, one row |

Nested values (arrays / objects) inside a cell serialise to compact
JSON so the cell stays on a single physical line. Decoders may
re-hydrate by `JSON.parse` on such cells.

## Versioning

- The literal header prefix `GCX1` is stable for the lifetime of
  version 1.
- A decoder that sees a different prefix (e.g., `GCX2`) must
  treat the payload as unknown and MAY fall back to JSON by
  re-issuing the MCP call without `format: "gcx"`.
- Field layouts for declared tools are frozen within `GCX1`.
  Additions ship as `GCX2` — renaming a tool's field set is
  a breaking change.

## Rationale

- **Tab delimiter (not comma):** symbol names routinely contain
  commas (`(int, string)`) and parentheses. Tab is rare in source
  and absent from identifiers. Escape pressure stays low.
- **Newline-terminated rows:** tokenizer-friendly and
  transport-transparent (no binary framing). SSE / chunked HTTP
  can forward one row per frame without re-parsing.
- **Minimal escape alphabet:** two-byte `\t` / `\n` / `\\` keeps
  the hot path cheap. Code payloads rarely contain raw tabs or
  unescaped backslashes, so escape overhead is a rounding error
  in practice.
- **Header-based metadata:** `total`, `truncated`, `etag` live on
  the header rather than a per-row phantom column. That keeps the
  row schema flat and lets the encoder skip meta work when the
  tool doesn't care.

## Reference implementations

- **Go encoder / decoder:** MIT-licensed standalone module at
  [`github.com/gortexhq/gcx-go`](https://github.com/gortexhq/gcx-go)
  (`go get github.com/gortexhq/gcx-go`) — header + row + escape
  primitives + generic fallback. Per-tool hand-tuned encoders live in
  `internal/mcp/gcx.go`.
- **TypeScript decoder:** MIT-licensed standalone package at
  [`github.com/gortexhq/gcx-ts`](https://github.com/gortexhq/gcx-ts)
  (npm: [`@gortex/wire`](https://www.npmjs.com/package/@gortex/wire)).

## Benchmark

See `bench/wire-format/`. The harness scores bytes, tiktoken tokens,
gzip bytes, and round-trip integrity across 20 representative tool
responses and emits a markdown scorecard. Rerun after any change to
the upstream `gcx-go` module or `internal/mcp/gcx.go` to catch regressions.
