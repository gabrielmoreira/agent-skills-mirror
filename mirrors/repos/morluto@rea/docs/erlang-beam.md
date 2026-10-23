# Erlang BEAM files

`inspect_erlang_beam` / `inspect-erlang-beam` answers whether one selected
local file is a `FOR1`/`BEAM` IFF container, which chunks that form stores, and
which atom, export, import, lambda, and Code-header fields those chunks carry.
It reads the file without executing bytecode and does not require an Erlang
installation or BEAM emulator.

```bash
rea inspect-erlang-beam /absolute/path/to/app.beam --json
```

The CLI resolves relative paths against the caller's working directory. MCP
requires an absolute filesystem path and preserves that exact selection:

```json
{
  "name": "inspect_erlang_beam",
  "arguments": { "path": "/artifacts/app.beam" }
}
```

## Observations

The inline Evidence result contains the artifact path, SHA-256, and byte length.
`chunks` lists every IFF chunk name, file range, and payload SHA-256.

When `AtU8` or `Atom` is present, `atoms` is the 1-based name table and
`module` is atom 1. Both the pre-OTP 28 table and the OTP 28+ compact table
(negated count, compact-encoded name lengths) are read. `exports`, `imports`, and `lambdas` resolve atom indices to
those names when the table is present; unresolved indices keep `function` or
`module` null.

`code` reports the Code chunk instruction-set, opcode maximum, label count,
function count, and the instruction stream's file range. Missing optional
tables are null, not empty-everywhere.

## Limits and failures

The selected file is limited to 64 MiB by default (512 MiB maximum). At most
64 chunks and 4096 atoms are examined by default, and at most 65536 export,
import, and lambda rows together. Malformed `FOR1`/`BEAM` headers, truncated
chunks, and `AtU8` names that are not valid UTF-8 fail without partial success.

This workflow does not execute bytecode, inflate `LitT` literals, or decode
`Attr`/`CInf` external-term payloads.
