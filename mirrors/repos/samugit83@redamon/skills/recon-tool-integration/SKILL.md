---
name: recon-tool-integration
description: >
  Adding a new tool to the recon pipeline: the enrichment-module contract and its
  isolated wrapper (the actual fan-out and test call path), graph completeness,
  and the preset catalog that silently strips unknown settings. Miss the isolated
  wrapper and the tool never runs in parallel; miss the catalog and AI presets
  drop its config.
  Trigger: adding a tool to the recon pipeline; a new recon/*.py or
  recon/main_recon_modules/*.py enrichment module; editing the execution groups
  in recon/main.py or the IMAGES array in recon/entrypoint.sh.
license: MIT
metadata:
  author: redamon
  version: "1.0.0"
  scope: [recon]
  auto_invoke:
    - "Adding a new tool to the recon pipeline"
    - "Editing recon execution groups, enrichment modules, or the recon image list"
---

## When to Use

- Adding a brand-new scanning/enrichment tool to the scan pipeline.

For adding AI decision-making to an *existing* tool, use `recon-ai-enrichment`.
For the graph write, use `graph-db-writes`. For the settings, use
`project-settings-cascade`. This skill is the module + pipeline wiring.

---

## Critical Rules

- **NEVER ship the enrichment module without its `_isolated` wrapper.**
  `run_<tool>_enrichment_isolated()` is the **actual call path** for the GROUP 3b
  parallel fan-out AND for every unit test; the plain `run_<tool>_enrichment()`
  alone is never fan-out-safe. Reference:
  [recon/main_recon_modules/censys_enrich.py:369](../../recon/main_recon_modules/censys_enrich.py#L369).
- **NEVER vary the top-level result key.** The module writes
  `combined_result["<tool>"]` and the wrapper returns `snapshot.get("<tool>", {})`
  with the **same** identifier used everywhere else in the pipeline
  ([censys_enrich.py:365](../../recon/main_recon_modules/censys_enrich.py#L365)).
- **NEVER collect a field and not write it to the graph.** Every field in the
  output dict must land on a node/relationship or it is silent data loss - see
  `graph-db-writes`.
- **NEVER add a tool setting without updating BOTH preset layers.** Add it to the
  Zod [recon-preset-schema.ts](../../webapp/src/lib/recon-preset-schema.ts) and to
  `RECON_PARAMETER_CATALOG` in
  [webapp/src/app/api/presets/generate/route.ts](../../webapp/src/app/api/presets/generate/route.ts).
  Miss the Zod schema and AI-generated presets **silently strip** the setting;
  miss the catalog and the preset LLM never knows the tool exists.
- **ALWAYS prefix every `print()` log** `[symbol][ToolName]` (`[*]` progress,
  `[+]` success, `[-]` skipped, `[!]` error). Recon stdout is tailed into the SSE
  recon drawer; a bare `print()` is invisibly formatted.
- **ALWAYS place a fan-out tool behind the deep-copy `_isolated` wrapper** and in
  the correct execution group in [recon/main.py](../../recon/main.py); never
  parallelize across a dependency boundary (a tool needing live URLs cannot run
  before GROUP 4).
- **ALWAYS route a new external call through
  [recon/helpers/circuit_breaker.py](../../recon/helpers/circuit_breaker.py).** An
  API endpoint goes through a `Breaker` (`guarded_call`, or a `provider:endpoint`
  breaker with `record(classify_http(...))`); its keys go through a `KeyPool`, not
  a raw main-key read. A loop over scan hosts (HTTP or a Docker tool) gates each
  host with `host_health.allow(url)` / `scope.skip_if_down(url)` and records the
  outcome with `host_alive` / `host_failed` — any HTTP response is life, only a
  connection failure counts. Never log a key or a response body: breaker messages
  carry the provider, endpoint and a refused key's 1-based rotation position only.
- **ALWAYS declare what the tool cut to the coverage accumulator.** Open a
  `scope = circuit_breaker.scope((), label="Tool", unit="host(s)")` at the tool's
  start and call `scope.finish("<phase>", sources=[...], host_source="<graph
  source>", payload=result)` at its end — so the end-of-run prune KEEPS a paused
  source's or a skipped host's prior findings instead of deleting them as "gone",
  and the run shows `partial — N sources skipped`. `host_source` must equal the
  `source` value the tool writes to the graph. A tool whose findings carry no host
  field passes `host_field=False` (the skip is reported at the source level).
- **A new tool setting FAILS THE BUILD until it is in the registry.** Every
  parameter is described once in
  [recon_settings/registry.yaml](../../recon_settings/registry.yaml),
  and a test walking `Prisma.ProjectScalarFieldEnum` fails until every column
  has an entry. Draft it with
  `python3 tooling/scripts/extract_recon_registry.py`, EDIT IT, then
  `python3 recon_settings/build.py`.
- **Tuning is OPEN and controlled at the point of use, not by being refused.**
  A rate is capped to the engagement ceiling at scan start; a wordlist path
  outside the project's own directories is dropped. A container image is a
  closed `values:` list and an out-of-set value is REFUSED at the write, because
  accepting one and replacing it at scan start made `get_recon_settings` echo an
  image the scan would never run.
- **Two things stay closed, and only two.** The engagement SCOPE
  (`mcp: create_only`, set once by `create_project`) and the engagement RECORD
  (`mcp: never`, `deny_reason: engagement-record` - the client, the contacts,
  the dates, the document). The engagement's LIMITS are ordinary `mcp: settable`
  fields in the `engagement_limits` group: they are reachable from the form and
  from MCP alike, and what makes them safe is that each is enforced at scan
  start whatever the setting says. See
  [README.MCP.SERVER.md](../../docs/readmes/README.MCP.SERVER.md).
- **A settable field with no form input fails `parity.test.ts`, and so does a
  form input with no classification.** Neither door may reach something the
  other cannot. `form_section` is joined from the tool's own entry, so a field
  lands beside its tool automatically.
- **A new `rps` field with `traffic: active` and no `roe_capped: true` fails the
  build.** That gap is how three rate limits shipped reachable over MCP and
  outside the ceiling.

---

## Enrichment-module contract (copy target)

```python
def run_censys_enrichment(combined_result: dict, settings: dict) -> dict:
    ...                                              # mutate in place
    combined_result["censys"] = censys_data          # top-level key == tool id, everywhere
    return combined_result

def run_censys_enrichment_isolated(combined_result: dict, settings: dict) -> dict:
    """Thread-safe: does not mutate combined_result. The fan-out + test call path."""
    import copy
    snapshot = copy.deepcopy(combined_result)
    run_censys_enrichment(snapshot, settings)
    return snapshot.get("censys", {})                 # returns only this tool's payload
```

From [recon/main_recon_modules/censys_enrich.py](../../recon/main_recon_modules/censys_enrich.py).

## Commands

```bash
docker compose build recon                            # if you added a Docker-based tool (recon/entrypoint.sh IMAGES)
docker compose exec webapp npx prisma db push         # for new settings (NEVER prisma migrate)
./redamon.sh test unit                                # recon + root-recon sections
```

## Resources

- [docs/readmes/coding_agent_prompts/PROMPT.ADD_RECON_TOOL.md](../../docs/readmes/coding_agent_prompts/PROMPT.ADD_RECON_TOOL.md) - the full ~15-subsystem checklist (graph, report, workflow view, presets, tooltips)
- Related skills: `graph-db-writes`, `project-settings-cascade`, `recon-ai-enrichment`
