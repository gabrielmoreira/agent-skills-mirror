# Offline binary diagnostics

`inspect_binary_layout` / `inspect-binary-layout` answers what an explicit
file contains: section/segment layout, original symbols/relocations, static
linkage names and mitigation indicators. It works without an active Hopper,
Ghidra or IDA target. CTF is one possible use; crash triage, compatibility and
ordinary binary inspection use the same modular capability.

## Bring your own engine

Initial real verification covers **Linux x64, ELF64 x86-64 little-endian
EXEC/DYN/REL**. Provide an absolute Python executable whose environment already
contains unchanged pwntools 4.15.0, pyelftools 0.33 and Unicorn 2.1.2:

```sh
REA_PWNTOOLS_PYTHON=/absolute/isolated-env/bin/python \
  rea inspect-binary-layout ./selected.elf --json
```

```json
{
  "name": "inspect_binary_layout",
  "arguments": { "path": "/artifacts/selected.elf" }
}
```

REA never installs Python, packages or GDB, changes a user init file, launches
the selected object as a host process, or requests runtime library resolution. The Python process
uses isolated mode and an owned cache. Exact upstream profiles are recorded in
[upstream provenance](https://github.com/morluto/rea/blob/main/third_party/pwntools/README.md).

## Interpreting results

- Artifact path, SHA-256 and size identify original selected bytes. All parsing
  reads an owned stable snapshot; the original is unchanged.
- Addresses, offsets, lengths and flags are hexadecimal strings. A linked
  address is not a runtime address. Runtime load base remains null. A zero
  EXEC/DYN entry means absent; a relocatable entry is not applicable.
- Each symbol retains its table and entry index. Its reported value can mean
  undefined, alignment, absolute value, no address, unknown section index,
  section offset, TLS offset or linked virtual address. Duplicate names remain
  separate entries. SHN_XINDEX remains unresolved in the selected upstream
  representation; its external index table is not silently treated as resolved.
- Relocatable objects have section-relative relocations and no executable entry
  claim. Signed REL/RELA relocation addends are decimal strings. Packed RELR
  tables retain full original bytes and upstream-decoded offsets as derived
  evidence, with per-offset packed-word locations and implicit addends unknown.
  Overall relocation inventory completeness remains unknown.
  A relocatable SHN_UNDEF target or inactive SHT_NULL header remains an explicit
  unknown with the original reported section index and offset.
- REL/RELA symbol references retain their original table and entry indices.
  Positive indices resolve through a validated symbol table; symbol index zero
  means a zero symbol value without a table lookup, including when no table is
  linked. Malformed references fail with the affected section and symbol index.
- Section-name and symbol tables require declared SHT_STRTAB links.
  SHN_UNDEF explicitly means no section names: display is empty, raw name and
  location unknown, with the original name offsets retained. Extended section-name
  indices resolve through section zero and undergo the same validation.
- Symbol tables require a declared SHT_STRTAB link. Name offsets and terminators
  must stay inside the declared string table; malformed references fail before
  unrelated bytes can become names. Dynamic dependencies use DT_STRTAB/DT_STRSZ
  with a unique file-backed mapping; ambiguous or unbacked mappings are
  explicitly unsupported.
- Name display strings use UTF-8 replacement for opaque bytes, including
  sectionless dependency names and interpreter paths. Raw name
  bytes and string-table ranges retain observed identity where resolvable;
  ranges include the terminating NUL and base64 bytes exclude it.
- NOBITS and NULL sections provide no file bytes. Reported file-backed ranges
  are checked against snapshot size again at the public boundary. PT_NULL payload
  fields are unused: reported numbers remain, file backing is none and interpreted
  permissions are null. Segments with zero file size also have no file bytes.
- Sectionless dynamic images still report dependency names with raw bytes and
  file locations where uniquely mapped. Missing symbol/relocation section tables
  do not establish that those runtime tables are absent.
  Upstream RELRO/canary heuristics rely on sections and can be incomplete in
  this case; their reported candidates retain an explicit coverage limitation.
- DT_NEEDED/PT_INTERP are reported names, not resolved runtime paths. GOT/PLT
  maps are derived convenience views and may collapse aliases. PLT inference
  can emulate selected instructions in Unicorn; its outputs are static candidates.
  Exec syscall tracing observes host process launches. Map completeness
  remains unknown and original upstream warnings are returned inline.
- Canary, PIE, NX, executable-stack and RELRO are static inferences. NX and
  executable-stack are separate upstream indicators: on x86-64 an executable
  stack can accompany an unknown (`null`) NX indicator. ET_DYN can be a shared
  library, and an absent canary symbol does not prove every function unprotected.

When complete layout Evidence is already retained, `inspect_analysis_view` /
`inspect-analysis-view` projects a summary, the mitigations or linkage facet,
one section or symbol, or a stable page without re-running the decoder. CLI
one-shot invocations pass portable inline Evidence JSON; an MCP session uses
the retained `evidence_id`. Page `limit` is required and bounded by the
measured MCP stdio budget documented on the tool contract.

Over MCP, `inspect_binary_layout` with `"detail": "summary"` retains the
complete layout Evidence in the session and returns only its summary view.
Its `normalized_result.parent_evidence_id` names the retained layout for later
section, symbol, mitigation or linkage views. The default `complete` detail and
CLI output are unchanged.

Complete results have a 32 MiB input, 64 MiB reply, 1 MiB combined diagnostics
and 30-second owned command deadline. `REA_PWNTOOLS_MAX_INPUT_BYTES` raises the
input bound alone, up to 1 GiB; the reply and deadline bounds are unchanged. The
reply budget applies to the decoder record; the CLI/MCP Evidence envelope adds
copies and encoding overhead. The
pinned MCP SDK defaults to a 10 MiB receive buffer. Large complete results need
a caller-configured `StdioClientTransport({ maxBufferSize: ... })` and a matching
server `REA_MCP_MAX_RESPONSE_BYTES`. See [MCP delivery budgets](mcp-contracts.md#tool-results).
These settings affect delivery, not decoder coverage or limits. The large
extended-index verification uses 256 MiB and an explicit five-minute request
timeout in its separate opt-in MCP lane. REA does not silently truncate the result. Python lowers resource soft limits to at most 3 GiB virtual address space,
30 CPU seconds and 64 MiB file output. Inherited tighter soft/hard limits are
retained, and the effective values are returned in the result limitations. Virtual address space is not RSS;
Unicorn needs a large virtual map. Limits fail with no partial success, and
owned process/root cleanup completes independently of cancellation.

Core files, GDB session/state/control, optional pwndbg enrichment and instruction
inspection are separate increments tracked by #969. This increment makes no
real support claim for those features or other operating systems/architectures.

Typed decoder failures retain bounded `captured_output` (stdout, stderr and an
explicit truncation flag) alongside the original failure category and reason.
Successful `diagnostics` also exposes the supervisor's `truncated` flag. Output
beyond the complete diagnostic budget is rejected, including when the decoder
writes a valid reply; cleanup and late cancellation reuse the observed flag.
Memory allocation failures use `resource_constraint`, with effective resource
limits (or an explicit unknown) and memory-specific recovery guidance. A
MemoryError alone does not establish the exact failed allocation or that a
particular budget was exhausted. Invalid undersized symbol entries are rejected
before REA reports source ranges for them.
The bridge reserves 1 MiB to report allocation failures. If even error reporting
or serialization fails with MemoryError, its reserved exit status preserves the
resource classification with unknown effective limits.
Reserved exits require a matching private marker written by the bridge's actual
failure branch. Bare launcher exits or missing/unwritable markers retain process
diagnostics with the resource cause unverified.
Signal termination alone is never classified as observed memory exhaustion.
The small bootstrap also covers catchable MemoryError during adapter imports,
compilation and initialization. Python interpreter startup failures before the
bootstrap runs retain their observed process diagnostics without guessed causes.
SIGXCPU retains a CPU resource diagnostic and CPU-specific recovery advice.
Observed EFBIG writes or SIGXFSZ termination retain a file-size resource
diagnostic and file-size-specific recovery advice. If a tight file limit also
prevents writing the limit record, effective values remain unknown.
The bridge records actual limits in owned storage before analysis; missing or
malformed limit reports remain unknown with their read failure preserved. A
received signal alone does not establish its exact cause. Dynamic tags require
a complete DT_NULL inside PT_DYNAMIC; interpreter names and ranges end at the
first NUL, with any padding still represented by the original segment range.

## Ghidra process failures

When output from the failing Ghidra startup or operation reports
`java.lang.OutOfMemoryError`, REA returns `resource_constraint`. Java heap or GC
overhead exhaustion includes heap-specific recovery advice. Metaspace and array
size failures do not recommend increasing the heap; native-thread exhaustion is
reported as a capacity constraint with unknown limits.

`configured_jvm_max_heap` records the explicit `-Xmx` value selected by REA's
launch builder. It is a configuration fact, not measured memory use or proof of
the effective JVM limit; JVM environment options may affect that limit.
When a Windows script wrapper selects the JVM, this value remains unknown.
Historical stdout and stderr remain available, but classification uses only the
failing operation's `failure_output`. Retained stdout and stderr share an 8 MiB
budget, but every drained byte is scanned for `java.lang.OutOfMemoryError`:
`failure_output.observed_oome` records the latest confirmed token's bounded line per stream from
the failing operation, with its byte offset, even after the budget is spent. These observations own OOME detection; retained text that ends at a class-name prefix cannot confirm a complete token. `line_complete` distinguishes a known line end from an incomplete trailing context; `invalid_utf8` marks replacement-decoded context.
Incomplete operation output without an observed OOME keeps the original failure code and explains that a memory cause cannot be ruled out. Incompleteness alone does not confirm a memory constraint or justify heap-specific advice. Token context stays within the failing operation's checkpoint; a class-name prefix in a different identifier is not OOME evidence. A trailing bare token requires an observed stream EOF to establish its boundary.
Output draining waits at most one second,
subject to earlier cancellation or the startup deadline. `output_incomplete`
marks a snapshot taken before stream closure; cleanup ownership remains with
the session until release succeeds.

## Portable PE resources

`inspect_pe_resources` / `inspect-pe-resources` inspects an explicit PE32 or
PE32+ file without an active target, native engine, Python, or Windows SDK:

```sh
rea inspect-pe-resources ./selected.exe --json
```

```json
{
  "name": "inspect_pe_resources",
  "arguments": { "path": "/artifacts/selected.exe" }
}
```

The complete Evidence identifies the stable artifact snapshot by path, byte
count and SHA-256. Resources retain separate type, name and language identities:
numeric IDs are distinct from UTF-16 names, whose original bytes are also
reported. Directory headers, entries, data entries and payloads retain original
file offsets and lengths. Each opaque payload has its own SHA-256; code page and
reserved data-entry fields are preserved.

RT_GROUP_ICON records expose original image descriptors and RT_ICON candidates.
A reference resolves only when an icon with the same numeric ID and language
exists. Missing references, other-language candidates and declared-size mismatch
remain explicit. Encoded dimensions are preserved (zero denotes 256 pixels).
This is static reference inspection; no image decoding, language fallback,
resource loading or selected-file execution occurs.

An absent resource data directory is a complete empty inventory. Malformed
headers, truncated tables, cycles, duplicate sibling identities, unbacked or
ambiguous RVA mappings, nonidentical overlapping ranges and unsupported tree
shapes fail explicitly, rather than returning partial inventories. Exact shared
payload ranges are supported. The supported tree has three levels: type, name,
and language. Other resource payload formats remain opaque.

`max_file_bytes` defaults to 64 MiB (maximum 512 MiB); `max_entries` defaults to
16384, the largest stock Windows resource image measured with headroom
(maximum 65536). CLI options are `--max-file-bytes` and `--max-entries`.
Metadata is bounded to 8 MiB; exceeding any budget fails without truncation.
Large Evidence envelopes may require a caller-configured MCP transport receive
buffer because envelope copies add overhead. Requests honor cancellation during
snapshot reading, directory traversal and payload hashing. The operation reads
regular files only and rejects symbolic links.

## Byte entropy triage

`inspect_byte_entropy` / `inspect-byte-entropy` profiles any local regular file
without an analysis engine, execution, extraction or network access.

```sh
rea inspect-byte-entropy ./firmware.bin --block-size 4096 --json
rea inspect-byte-entropy ./firmware.bin --offset 4096 --length 65536 --json
```

```json
{
  "name": "inspect_byte_entropy",
  "arguments": { "path": "/artifacts/firmware.bin", "detail": "summary" }
}
```

Complete Evidence includes `artifact` (original path, byte size and SHA-256),
`block_size`, `window`, `file_entropy`, `thresholds`, `blocks`, `runs` and
`limitations`. For a 4096-byte zero-filled file, the entropy fields are:

```json
{
  "block_size": 4096,
  "window": { "offset": 0, "length": 4096 },
  "file_entropy": 0,
  "thresholds": { "high": 7.2, "low": 1 },
  "blocks": [{ "offset": 0, "length": 4096, "entropy": 0 }],
  "runs": [{ "offset": 0, "length": 4096, "classification": "low" }]
}
```

Offsets and lengths are decimal byte counts. Blocks begin at the requested
`offset` (default zero); omitted `length` extends to EOF. Explicit windows past
EOF fail rather than silently clipping. The final block may be shorter.
`block_size` must be a power of two from 256 through 65536, default 4096. A
window may produce at most 32,768 block rows; larger requests fail before the
file scan with a capacity error. Choose a shorter window or larger block size.
SHA-256 and `file_entropy` always cover the entire file, including when a window
is selected. Empty files and empty windows are accepted; empty entropy is zero
by convention. The tool reads the size the file reports. A file that reports size
0, such as a Linux `/proc` entry, returns no blocks with a limitation that the
result does not show the file is empty. File identity, size and timestamps are checked across the read;
detected changes produce an error rather than Evidence.

Shannon entropy is reported in bits per byte from 0 to 8, rounded to four decimal
places. Adjacent blocks with reported entropy at least 7.2 form `high` runs;
blocks at most 1.0 form `low` runs. Other blocks interrupt runs. Entropy does not
prove encryption, and this measure cannot distinguish encrypted from compressed
data. Small blocks can underestimate entropy; the result is a triage clue.

MCP `detail: "summary"` retains complete Evidence in the session and returns
file entropy, block/run counts, thresholds, the selected window, and the ten
longest runs (ties ordered by file offset). Use its `parent_evidence_id` to
retrieve complete Evidence, or request its summary with `inspect_analysis_view`.
The CLI returns complete Evidence through the same service. Summary detail
requires a session capable of retaining Evidence.

Reads use one block-sized buffer and a 256-entry histogram. Complete output
can become very large because it includes one row per selected block, and
summary delivery still retains that full list. Use a shorter length or a
larger block size to reduce it. Full Evidence and its serialization require
memory proportional to the number of selected blocks. The 32,768-row ceiling bounds the actual retained block objects and
their serialized representation: a cap-sized run below produced 1,514,877
serialized bytes and increased V8 heap use by 21.2 MiB on the measured host.
The cap therefore bounds this output independently of file size; it is not a
portable process-memory guarantee. Narrow the window or increase block size to
reduce retained rows further.

Local service measurement (macOS arm64, Node 24.18.0, 100,000,000-byte file,
4096-byte blocks, file already in the OS cache): first process run took 1.113 s
wall / 1.148 s CPU with 145.3 MiB peak RSS; a second run in the same process took
1.015 s / 1.035 s CPU, with cumulative peak RSS 155.8 MiB. Each read 100,000,000
bytes and produced 24,415 blocks. Measurements include Evidence construction,
summary projection and JSON serialization, with no child processes. Complete
Evidence serialized to 1,122,303 bytes and its summary to 2,705 bytes. A
cap-sized 134,217,728-byte sparse file with 4096-byte blocks produced 32,768
rows and 1,514,877 serialized bytes; V8 heap use increased by 21.2 MiB and RSS
by 18.1 MiB in that process. This separate measurement used the same macOS
arm64 host and Node version. Cold disk I/O, token counts and an agent
investigation were not measured; there was no previous equivalent tool to
benchmark. These figures do not establish a portable peak-memory bound,
constant memory for retained Evidence or faster agent task completion.

## Portable native exports

`inspect_native_exports` / `inspect-native-exports` reads the export table of an
explicit PE or ELF image on any supported host, without an active target,
native engine, `objdump` or Windows SDK:

```sh
rea inspect-native-exports ./runtimes/linux-x64/native/libexample.so --json
```

```json
{
  "name": "inspect_native_exports",
  "arguments": { "path": "/artifacts/native/example.dll" }
}
```

The complete Evidence identifies the stable artifact snapshot by path, byte
count and SHA-256.

- PE rows reproduce the export directory: each used export-address-table slot
  with its `ordinal`, one row per name (aliases share an ordinal), `address`
  as the preferred-base virtual address, or `forwarder` text when the slot
  forwards to another DLL. Ordinal-only exports have a null `name`. The
  directory's DLL name, ordinal base and timestamp are reported, and an image
  without an export directory is a complete empty inventory.
- ELF rows list defined `.dynsym` symbols with global, weak or GNU-unique
  binding and default or protected visibility. Each row keeps `value`
  (`st_value` as stored; bit 0 marks Thumb code on 32-bit ARM), `size`, `type`
  and `binding`. `version` is null for an unversioned symbol, the
  `.gnu.version_d` index, name and `hidden` flag for a versioned one, or
  `"unknown"` when the version table cannot be read. A hidden version is not
  the default version that a by-name `dlsym` lookup selects.

Unreadable names, out-of-range name ordinals and unreadable forwarders are
listed in `issues`, their entries are not reported, and coverage is `partial`.
Unresolved symbol versions keep their rows: the version name is null for an
index no definition names, and `version` is `"unknown"` when the version table
cannot be read; coverage is likewise `partial`. A dynamic symbol table without
its null entry is malformed. An ELF without section headers is `unsupported`:
enumerating dynamic symbols from the dynamic segment is not
implemented. Mach-O exports are reported by `inspect_macho`.

`max_file_bytes` defaults to 256 MiB (maximum 512 MiB; CLI `--max-file-bytes`).
Export directories in PE headers are read like those in sections. An export or
dynamic symbol table above 262144 entries, more than 262144 rows, or more than
16 MiB of retained names fails without partial success. Export rows do not establish that a symbol is reachable, safe to call
or loaded at runtime.
