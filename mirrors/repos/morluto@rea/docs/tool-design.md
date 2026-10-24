# MCP tool design

## Decide whether to add a tool

Design around the analyst question. Inspect the current canonical contracts,
provider capabilities, and nearest existing tool before changing the surface.
Extend a tool when intent and result contract match; add one for a distinct
outcome or materially different authority. Public names and semantics remain
provider-neutral, with exact coverage reported per provider.

Keep the catalog complete; report capability/session availability instead of
truncating schemas. Serialized bytes alone do not establish agent usability.

## Choose the tool shape

| Shape                 | Use it for                                  | Result                                                                    |
| --------------------- | ------------------------------------------- | ------------------------------------------------------------------------- |
| `inspect`             | Facts about one target, object, or resource | Relevant fields, locations, and facet availability                        |
| `search` / `list`     | Candidate discovery                         | Stable ordering and context; pagination when the query or format needs it |
| `trace`               | Relationships across evidence               | Typed edges, supporting facts, and unresolved paths                       |
| `compare`             | Explicitly paired artifacts or observations | Identity, comparable coverage, and supported deltas                       |
| `workflow`            | A recurring outcome needing composition     | Inline answer, contributing evidence, and partial facets                  |
| `observe` / `capture` | Runtime behavior                            | Authority, launch/attach effects, lifecycle, and cleanup status           |

These are task shapes, not mandatory prefixes. Name tools for the action and
object callers reason about. Avoid unrelated discovery/execution/mutation modes
inside one tool.

## Prefer primitives; compose workflows

A primitive reports a reusable fact about an identified object or relationship.
A format-specific decoder qualifies; one application's business interpretation
belongs outside the general contract. The format owner reports source
observations and structural validation; the application or workflow owner
applies use-case-specific admission policy without reinterpreting raw fields.
For example, DOS MZ structure and Windows-header evidence stay separate, while
target resolution decides whether the unresolved header permits admission.
Expose provider APIs when they add a useful capability that existing tools
cannot express.

Compose a workflow when repeated use demonstrates a multi-source outcome REA
can join without hiding caller choices or uncertainty. Batch homogeneous reads
when that removes repeated work while preserving per-item outcomes. Keep prompts
optional and avoid prescribing call sequences that a direct tool can replace.

Agents can compose experiments with ordinary commands, scripts, and local
fixture servers. Custom orchestration languages, replay engines, or separate
prepare/execute plans need an observed requirement those primitives cannot
satisfy. A plan without execution does not establish runtime behavior.

## Define the contract

- Use strict inputs with explicit target identity and required fields. Preserve
  meaningful target, action, capture, and output choices; remove ignored options
  and repeated permission declarations.
- Return the requested facts inline with artifact/provider identity, source
  locations, Evidence references, coverage, and relevant confidence and
  limitations. Use supported selection, summaries or views when they answer
  the question; preserve access to complete source Evidence and honor existing
  contracts and requested detail. Missing coverage is unknown, not absence.
  Avoid extra lookups solely to understand the answer or its provenance.
- Keep observed, derived, and inferred relationships distinct. Preserve
  unresolved edges and partial provider facts instead of requiring every
  provider to supply the same metadata.
  When a format constructor changes defaults or flags, retain the source
  values and use separately derived effective values only for operations
  whose semantics require them.
- For caller/callee reads, `relationship_coverage` describes only the
  provider-observed direct relationship set. `complete` means that set was
  returned without a known read limit; it does not claim every possible runtime
  edge. Provider and execution caveats stay in `limitations` and do not imply
  incomplete relationship coverage. Missing coverage remains `unknown`.
- Declare process, filesystem, network, UI, and mutation effects truthfully;
  enforce the requested target and lifecycle.
- Add limits only for real format, protocol, authority, or measured resource
  constraints. Report pagination, truncation, cancellation, and partial failure.
  An assumed agent budget is insufficient justification for a limit. Name the
  ceiling and its recovery as described in
  [admission limits and recovery](design/limits-and-recovery.md).

### Interpret boundary facts once

Comparison needs separate proofs for lookup, correspondence, content, and
coverage. A hash cannot supply the proof that two retained values belong to
corresponding objects.

| Comparison fact                                                               | What it establishes                             | What remains unknown                          |
| ----------------------------------------------------------------------------- | ----------------------------------------------- | --------------------------------------------- |
| Same capture-local frame or request ID                                        | Lookup within that capture                      | Cross-capture identity                        |
| Same HTTP method, URL, and resource type                                      | A repeated-request group                        | Which individual responses correspond         |
| A partial HTTP response multiset is contained in a complete peer              | Omissions can explain every retained sample     | Equality or modification                      |
| A retained HTTP sample is absent from a complete peer group                   | An observed difference independent of omissions | Other unobserved differences                  |
| Complete WebSocket connection/frame inventories and matching metadata streams | Ordered payload positions can be compared       | Equality of unavailable payload facts         |
| Unique WebMCP name, owner origin, and frame URL                               | Tool correspondence without transient frame IDs | Correspondence between duplicate owners       |
| A complete source digest or decoded storage value                             | Comparable content                              | Missing source bytes or opaque remote objects |

Complete traversal or inventory does not make unavailable values equal. A
partial aggregate fingerprint difference cannot establish modification when
omissions alone explain it; independently proven differences still survive.

The format or protocol reader owns interpretation. Pass its parsed facts and
explicit uncertainty to consumers; do not make adapters reparse display text,
reconstruct omitted values, or infer success from missing diagnostics.

Keep format recognition separate from provider admission. A recognizable header
can supply useful observations while later structure remains unresolved or a
provider cannot accept the artifact. Report the reason at the affected boundary
without erasing earlier observations or labeling unresolved input malformed.

Derive validation from the field's own format and revision. A runtime API's
narrower argument range need not constrain a wider on-disk field. A shared layout,
magic, or version label need not identify every constructor or equality rule.
When supported producer revisions differ, retain what the input establishes and
state what it cannot distinguish. Static inspection does not establish that the
artifact can execute successfully.

## Own the lifecycle

`SafeOutputTree` publishes only after file readback, nested-directory fsync
from children to parents, and root-parent fsync on hosts that support directory
syncing. Windows skips directory fsync. Failed writes retain a separate pending
identity admission only until identity is captured; rollback retries retain
unremoved file/directory identities and open handles independently, so confirmed
unlink progress cannot be re-admitted through a closed descriptor.

For tools that acquire resources, identify the owner and the observations that
establish each transition. Include temporary files and one-shot commands, as
well as persistent engine sessions. Use the existing provider contracts;
providers need not expose identical state machines.

- Keep target admission, provider readiness, active work, observed process exit,
  and resource release separate. A valid process handle, successful launcher,
  or selected target establishes only its own fact. Publish available identity
  and exit observations even when launch fails; retain unknown ownership.
- Process exit does not establish output closure. The shared process supervisor
  retains at most 64 KiB of additional diagnostics from owned stop entry,
  including pending cleanup and retries, and drains for up to one second after
  verified stop. It marks output incomplete when closure cannot be
  observed and releases owned event-loop references without changing the proven
  process-cleanup outcome. Failed process cleanup retains capture for retry;
  borrowed processes and streams retain their own lifetime and reference state.
- Authenticate and capture identity through the same boundary on initial and
  recovery handshakes. Bound abandoned unauthenticated listeners where the
  protocol permits it; that deadline must not expire authenticated idle sessions
  or long-running native work. Listener expiry does not prove target closure.
- Readiness observations may await owned prerequisite commands. Status must
  remain readable during owner finalization without starting replacement work;
  report readiness as unknown when it cannot be re-observed.
- Shared startup has one producer and independently cancellable caller waits.
  Keep it running while any caller still needs it. The final departing caller
  waits for owned cleanup and retains its failure. Provider closure is distinct
  from caller cancellation. Retained cleanup capabilities block replacement;
  derive readiness from the current startup's completion and live connection.
- Session `cleanup_pending` includes retained blockers from external mutation
  owners until those owners confirm release. Closing the analysis session does
  not release resources owned by an external debugger. Reading a selected
  analysis snapshot is part of `open_binary`; cancellation keeps that operation
  and the caller's reason through the shared JSON reader.
- For cancellable observations, carry cancellation through result consumption
  and awaited cleanup. Before returning success, check the signal after the
  last awaited finalization step.
  Retain collected observations under typed cancellation. Preserve an existing
  primary failure and let incomplete cleanup retain its own classification.
  Preserve the caller's abort reason as the typed cancellation error's cause,
  including when cancellation is observed only after provider completion.
  Shared command owners must retain the observed cancellation reason separately
  from physical failures and cleanup ownership. Carry that fact through failure
  wrapping so adapters can preserve the exact reason without interpreting it.
  ZIP member streams retain the exact signal reason; hdiutil wrappers consume
  the command owner's typed cancellation record and keep physical command
  failures separate, even if a host error is named `AbortError`.
  Client cancellation alone does not prove native work stopped.
  For atomic publication, document the cancellation cutoff and preserve any
  committed output's publication receipt.
  Queued and retried work must retain the complete accepted execution controls,
  including non-default lifecycle deadlines and cancellation signals.
- Release only owned resources. Attaching owns a connection or session unless
  the provider contract explicitly establishes target ownership. A helper exit,
  missing reply, or missing PID does not establish target exit.
- Retain successful child cleanup and retry only unresolved children, including
  when close options change. Preserve observed child failure or activity when
  another child's health is unavailable; idle plus missing coverage stays
  unknown.
  Bind cleanup failures to their exact resource owner. Resolve current cleanup
  uncertainty only after that owner confirms release, while preserving the
  original failure and completed observations. Later failure composition must
  report only resources whose cleanup remains unresolved. Carry cleanup
  capabilities explicitly in typed outcomes so consumers can bind returned errors
  to exact owners without reparsing diagnostic cause chains.
  Bind every caller-visible retry error and aggregate, including an error already
  produced by the provider. An aggregate remains incomplete until all owners it
  reports are released; releasing one child cannot clear another child's status.
- Await one-shot cleanup without discarding the completed result or primary
  diagnostic. Preserve partial observations, remaining resources, and the cleanup
  owner's recovery instructions. While cleanup remains unconfirmed, canonical
  errors keep `cleanup_incomplete` and live resources while taking category,
  operation and failure details from the retained typed primary. Nested cleanup
  composition does not replace that semantic identity. Finalization reports
  remain attached to their owning envelope while cleanup is pending and after
  confirmed release. CLI adapters should reuse
  [`finishAnalysisCommand`](https://github.com/morluto/rea/blob/main/src/cli/finishAnalysisCommand.ts) where its contract
  applies rather than duplicate close/finally handling.
- Give descriptor-backed reads an owner before opening the file. A rejected
  close must retain the exact handle and preserve any earlier failure. If an
  abortable caller stops waiting, keep the underlying work in that owner's
  lifetime so shutdown cannot report release before finalization settles.
  Admit the entire inspection once, including later reads and finalization.
  Helpers must borrow that admission or use an operation child scope; re-entering
  the same draining scope can make cleanup wait for its own caller.
  Retry retained cleanup before admitting new work and keep admission blocked
  while it remains unresolved. Link the originating cleanup error to its exact
  owner so confirmed release resolves its cleanup marker while preserving the
  earlier diagnostic. Shared CLI/MCP adapters cannot infer that confirmation.
- Provider profile selection owns every asynchronous candidate through its
  terminal result and finalization. The registry owns profile-file cleanup,
  joins all automatic-selection children, and closes those file owners before
  reporting candidate shutdown. Final caller cancellation joins the selection;
  an adapter that ignores cancellation remains active and owned until it settles.
  Block new admission during shutdown and while cleanup remains unresolved;
  reopen after confirmed retry. Preserve failed results before considering a
  later signal, and retain every child's attributed cleanup in mixed outcomes.
- Release child descriptors before removing their containing root. Retain a
  composite owner when either stage fails so retry preserves that ordering.
  A Windows command leader's exit does not establish Job Object closure. Keep
  the process-tree observer and command lock alive through failed cleanup retries
  until the owned tree's close event.

Exercise the applicable [lifecycle regression scenarios](testing.md#lifecycle-regressions)
through the producing owner and affected CLI/MCP consumers.

## Implement and evaluate

Put provider protocols/parsing in adapters and shared CLI/MCP workflows in the
application layer. Share Evidence provenance, unknown projection, and session
retention semantics; matching payloads alone do not establish parity.

Measure the resource before choosing a budget and enforce it before the costly
step. Account for value alternatives, trace-frame products, retained records,
serialization expansion, and temporary-file growth separately. Derive facet
completeness from examined records and exhaustiveness, rather than diagnostic
prose or an empty failure list. Preserve observations independently of cleanup
success.

For example, if ten applicable records are discovered, eight are examined, and
five are returned, the five returned records do not establish complete coverage
of the ten. Keep discovered, applicable, examined, and retained scope distinct.
A filtered page can be complete for its selection while the parent inventory
remains partial. Carry the upstream coverage and unresolved reasons through
filtering and paging; an item missing from that page is not proved absent from
the target. Structured completeness and absence fields must agree with the
stated limitations.

File-error wrappers retain the format owner's specific diagnostic and recovery
text. Strict JSON file input, for example, keeps the byte-order-mark explanation
and UTF-8 recovery through CLI/MCP projection rather than replacing it with
generic invalid-file advice. Consumers do not classify parser message text.

Update canonical contracts, output schemas, examples, generated artifacts, and
relevant docs together. Verify converted advertised schemas and success,
malformed, unavailable, cancellation, and partial outcomes through affected
consumers. Real-engine claims require the matching provider lane; see
[testing.md](testing.md).

For fixed tuples in public contracts, use `src/domain/fixedTupleSchema.ts`:
Zod's tuple projection omits implicit length bounds and Draft 2020-12 `items`,
which some clients require even alongside `prefixItems`. Tuples with a rest
schema also need explicit minimum lengths. Check parser/schema parity for empty,
short, overlong, and malformed values in both input and output projections.

CLI translations must reuse the canonical semantic fields, enum membership and
list bounds. Document transport differences such as relative path spelling and
JSON text decoding; reject empty selections before path normalization. Preserve
required alternatives across positional arguments and options. When the CLI
schema format separates those groups and cannot express their relationship,
state the required choice in command discovery/help and retain aggregate admission
before target access. Test emitted schemas and parser behavior together, including
omission, empty strings, alternatives, conflicts and boundary list counts.

Expected input failures must retain caller field/index paths and safe constraints.
Internal operation/input envelopes are not caller paths. Reuse the input issue
projector at the admission owner; a schema cause alone does not supply correction
metadata to either adapter.

When discoverability changes, evaluate representative broad, direct, and negative
tasks on the intended host. Record host/model/catalog, selected tools, arguments,
errors, retries, and task outcomes. Schema validity and keyword heuristics do not
establish successful tool selection. See [mcp-contracts.md](mcp-contracts.md) for
shipped runtime behavior.
