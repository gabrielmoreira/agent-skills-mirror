# ELF note tables

`inspect_elf_notes` / `inspect-elf-notes` answers whether one selected local
ELF32/ELF64 image declares `PT_NOTE` program headers or `SHT_NOTE` sections,
which note owners and types those tables store, and which GNU build-id or
ABI-tag fields those notes carry. It reads the file without executing it and
does not require a disassembler, debug package, or package catalog.

```bash
rea inspect-elf-notes /absolute/path/to/program --json
```

The CLI resolves relative paths against the caller's working directory. MCP
requires an absolute filesystem path and preserves that exact selection:

```json
{
  "name": "inspect_elf_notes",
  "arguments": { "path": "/artifacts/program" }
}
```

## Observations

The inline Evidence result contains the artifact path, SHA-256, and byte length.
`tables` lists each declared note program header or section, including the
section name when a string table is present. Each `entries[]` item reports owner,
type, descriptor SHA-256, and a hex preview for descriptors of 64 bytes or less.

For GNU notes, `gnu.build_id_hex`, `gnu.abi_tag`, or `gnu.gold_version` are
filled when the descriptor matches that type. Other owners keep `gnu` null.

`PT_NOTE` and `SHT_NOTE` are examined independently. The same file range may
appear twice when both tables declare it.

A missing table list is observed absence of those declarations. It is not proof
the image never carried notes in another container or overlay.

## Limits and failures

The selected file is limited to 64 MiB by default (512 MiB maximum). At most
32 note entries are examined by default across every table. Retained note
names, section names, and GNU descriptor text share that file's byte budget,
and repeated table ranges count again. Each descriptor range is hashed once,
and each GNU version's trailing NUL run is scanned once; neither walk may
exceed that byte ceiling. Malformed ELF headers, truncated header
tables, declared note tables that extend past the file, and truncated
note entries fail without partial success. ELF extended
numbering (`PN_XNUM`, including a section count stored when `e_shnum` is 0) is
unsupported.

This workflow does not execute the image or verify GNU build-id uniqueness
against package catalogs.
