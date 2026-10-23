# CPython pyc inspection

`inspect_python_pyc` / `inspect-python-pyc` answers which CPython version wrote
one selected local `.pyc` file, how its 16-byte header records source identity,
and which nested code objects marshal stored. It reads the file without running
bytecode and requires no Python installation, active binary target, Hopper,
Ghidra, or IDA.

```bash
rea inspect-python-pyc /absolute/path/to/module.pyc --json
```

The CLI resolves relative paths against the caller's working directory. MCP
requires an absolute filesystem path and preserves that exact selection:

```json
{
  "name": "inspect_python_pyc",
  "arguments": { "path": "/artifacts/module.pyc" }
}
```

## Observations

The inline Evidence result contains the artifact path, SHA-256, and byte length.
`header` contains:

- `magic`, the 16-bit little-endian field;
- `python_version` and `code_layout`, mapped from the pinned CPython 3.7–3.13
  table (`py37`, `py38`, or `py311`); 3.11 alpha magics before 3494 used
  other code layouts and are unsupported;
- `flags`, `hash_based`, and `check_source` from PEP 552;
- `source_hash_hex` for hash-based pycs, or `source_mtime` and `source_size`
  for timestamp pycs.

`code_objects` lists each distinct marshal code object once, the top-level
module code first. `nested_code` holds the indexes of the distinct code objects
reachable from that object's constants, including code nested in tuples and
other containers and the owner itself when a constant container reaches it.
A function shared through a marshal reference is named by index once per owner,
even when that owner reaches it again through the same container. Relationships
are collected after the marshal graph is complete, so a container that a nested
code object also references is not summarized while its items are still missing.
Each object reports name, optional qualname,
filename,
argument counts, flags, names, locals (or `localsplusnames` on 3.11+), const
summaries, and bytecode length plus SHA-256.

Bytecode is not decompiled. Const strings may be truncated in the summary while
the marshal walk still consumed the original bytes; a string summary's `bytes`
is that marshal length. Integer consts report `bits`; their decimal `value` is
`null` above 256 bits. Non-finite float and complex parts use CPython's `inf`,
`-inf`, and `nan` spellings. Dictionary and set lengths follow CPython:
unhashable keys and members fail the walk, equal set members count once, equal
dictionary keys keep the first key object and replace only its value, code
objects are valid keys and members, and a null dictionary value ends the dict
without that entry.

## Limits and failures

The selected file is limited to 16 MiB by default (64 MiB maximum). Marshal
object count, nesting depth, and per-string size are bounded; exceeding a
budget fails without partial success. Argument counts, positional-only counts,
keyword-only counts, local counts, and stack size are signed CPython fields; a
negative encoding is malformed. On the 3.11+ layout, `co_code` must cover a
whole number of code units. Every layout rejects argument counts that do not
fit the local table CPython checks (`co_varnames`, including `*args` /
`**kwargs`, or fast locals on 3.11+). Those files are malformed, so the
workflow does not report complete coverage. 3.7–3.10 still accept an odd
`co_code`, matching those constructors. Nested code collection walks reference
chains iteratively and keeps one shared descendant list for a container that
merely wraps another, instead of copying that list onto every wrapper. Set and
dictionary keys walk tuple and frozenset reference chains the same way, so a
long `TYPE_REF` chain stays within the call stack. A shared child stored twice
still counts its expanded key against the string budget. Code-object equality
keys record each name table's length and each entry's boundaries, so `()` and
`("",)` stay distinct, and `co_varnames`, `co_freevars`, and `co_cellvars` stay
separate tables. Names repeated through a marshal reference, including each
code-constant name the report copies, count against the file budget once per
copy. Empty strings add no bytes, so every copied
name-table entry (`co_names`, varnames, freevars, cellvars, and
`localsplusnames`) counts against the object budget before its array is built.
Copied constant tables and each reported nested code relationship count
against that same object budget. Integer digits and expanded
set or dictionary keys, including a shared tuple repeated at each level, count
against the string budget. Magics outside the pinned 3.7–3.13 table,
truncated headers, trailing marshal bytes, and a non-code top-level object are
typed failures.

A decoded header does not prove the matching `.py` is present. `python_version`
is the magic table, not a running interpreter. This workflow does not recover
source.
