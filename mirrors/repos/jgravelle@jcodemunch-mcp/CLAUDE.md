# jcodemunch-mcp — Project Brief

## Current State
- **Version:** 1.108.306 — **A count taken after the page, and a field nobody read.** Four issues from @lilubot, two sharing a root cause and a third falling out of the first. ⚠⚠ **`get_untested_symbols` computed `untested_count = len(symbols)` AFTER the `max_results` slice and derived `reached_pct` from it, and `get_repo_health` asks for `max_results=1` because it "only needs the count"** — so the PUBLISHED health/radar test axis read ~100% reach on every repository with untested code (**4,893 of 6,352, 23.0%, published as 100**). It reached the grade and the observatory. ⚠⚠ **The sweep for other instances found NONE, and that is the finding** — `find_importers`/`find_references`/`get_dead_code_v2` all count before slicing. **The defect is invisible to any single call, because one call's number is self-consistent**; only two page sizes over the SAME repo can see it, which is what `test_counts_survive_truncation.py` does. ⚠⚠ **`detect_framework` persists `entry_point_patterns` into `context_metadata` on every index, and a tree-wide search found that key WRITTEN IN ONE PLACE AND READ IN NONE.** Three tools each reproduced their own answer to "is this a root?" and every one was Python (`_ENTRY_POINT_FILENAMES` is eleven `.py` names plus `Makefile`), so a Next.js repo detected ZERO entry points: v2 returned `dead_symbols: []`, and 203 of 366 "unstable" files were `route.ts` handlers whose Ca is 0 BY CONSTRUCTION. ⚠⚠ **Consuming that field naively would have been FAR WORSE than the defect: Flask and FastAPI shipped `"*.py"` in it**, and under fnmatch a `*` crosses `/`, so the first reader would have declared every Python file in a Flask repo a live root — dead-code detection off across an ecosystem, silently, with those repos' coupling denominators emptied. Removed at the source AND refused by `_is_catch_all`, gated over every profile; **directory SCOPE is what saves a pattern** (`routes/*.php` fine, `**/*.php` not). ⚠⚠ **Coupling excludes entry points from the DENOMINATOR as well as the numerator** — numerator-only shrinks a count without shrinking what it is a fraction of, **the 84.0 B -> 88.8 B sign error of .305 pointing the other way**. So an entry point with a real `Ce` problem is graded by nothing; the count and profile are disclosed. ⚠ Only the DETECTED profile excludes: widening to `_ENTRY_POINT_FILENAMES` moves every Python repo's published score on a heuristic and needs its own measurement. ⚠⚠ **A REFUSAL IS NOT A ZERO** — v2 returning `[]` WITH a `signal_warning` became `dead_code_pct: 0.0` and an axis of 100, the strongest claim assembled from an admission that nothing was established; it withholds composite and grade through .305's own `unmeasurable_axes` now. ⚠ Toolchain manifests leave the dead-code population by NAME (nothing imports a lockfile by design; **`package.json` was reported dead by the same run that READS it to find entry points**) — never by extension, so an orphaned `data/fixtures.json` is still a finding. ⚠ #560 was VERIFIED, not fixed: all four type-only import spellings resolve. Tested anyway, because the claim rested on nothing. ⚠⚠ **Found on the way: THREE consumers reading keys their producers never emit, two in one renderer** — the post-task untested diagnostic and `assemble_task_context`'s audit stage were dark for their whole lives. **The test guarding the first was the reason nobody noticed: its mock returned the INVENTED key**, and a fabricated producer makes an absent-key defect structurally invisible to a test written about that exact code path. ⚠⚠ **The unmocked replacement PASSED against the reintroduced defect on its first version** — it asserted the name appeared in the message, and the name appears in three sections. **An assertion that does not name which producer put the string there proves nothing about that producer.** [[a-mock-can-supply-a-contract-the-producer-lacks]] [[grep-a-persisted-field-for-its-readers]]
- **Prior (1.108.305):** **Only the reader was never fixed.** Nine tools run `git log --since=N days`; a shallow clone answers every churn question with a small number and exit 0, so `churn_surface` ranked nothing but complexity and the grade came out FLATTERING. ⚠⚠ **We had fixed this TWICE — Practice 6's Action `fetch --depth=1`, and the observatory's cloner (81.3 B vs 75.6 C at ONE identical commit) — and both times we made OUR clones deep.** `actions/checkout` defaults to `fetch-depth: 1`, so every user running the Action or `jcodemunch-mcp health` in their own CI kept the defect **on their own pull requests**. Third instance of the standing lesson. ⚠ `tools/_git_history.py` asks COVERAGE, not shallowness: `--is-shallow-repository` is the mechanism, "reaches past the window" is the property — a `--depth=900` clone at 90 days is shallow AND complete, and a false alarm there teaches people to ignore the flag. Tri-state; a young repo is not a truncated one. ⚠⚠ **THE FIRST FIX MADE THE NUMBER WORSE, which is the release.** Omitting `churn_surface` the way `runtime_coverage` is omitted took the tree **84.0 B -> 88.8 B** against a truth of **77.3 C**: dropping a LOW-scoring axis RAISES a mean. **NOT APPLICABLE and COULD NOT MEASURE are different states and only the first may be dropped silently.** `compute_radar` takes `unmeasurable_axes` and **withholds composite AND grade**; measured axes stand. Default path byte-for-byte unchanged. ⚠⚠ **Two `None` sites the tests then found, both user-facing**: `diff_radar`'s `.get("composite", 0.0)` — **the default NEVER fires for a present key holding None** — and `_verdict`, which would have printed **"no meaningful change"** on a contributor's PR on the one occasion nothing was measured. ⚠⚠ **CI caught a 3.10 break I could not reproduce on ANY local version: git renders a UTC offset as `Z`, unparseable by `fromisoformat` before 3.11 — and git only emits `Z` on a UTC host.** Runners are UTC, this box is CDT and got `-05:00`. **The host's timezone selected the input format**, so the version matrix was not the axis; the guard is a UNIT test over all four spellings. The tri-state held under the fault (`complete: None`, not a wrong verdict). ⚠⚠ **Also: `relnotes.md`, a scratch copy of the release notes, SHIPPED INSIDE THE PUBLISHED 1.108.304 SDIST** via `git add -A`. The canary tests prove NAMED bad paths are absent and could never have caught it — **a denylist catches the instance, an allowlist catches the class** — and `ALLOWED_ROOT_FILES` found a SECOND instance minutes later: `suite.log`, from this session's own gate runs. ⚠⚠ **@Ticki84 ran the new breakdown on the first build that had it and it answered at once: `save=9.906s` of a `10.000s` total, everything else summing to 0.094s** — the cost is entirely `incremental_save`. **That lock is taken BEFORE the write, so from the caller's timer a CONTENDED LOCK and a SLOW WRITE are the same number**; `process_locks` now reports `waited_seconds` and NAMES the holder past 1s. ⚠ The round `10.000s` says contention, but that is a HYPOTHESIS and shipping the instrument beats asking the reporter to test it — three earlier ones on this issue were each measured dead by him. [[a-module-that-imports-clean-has-been-tested-for-nothing]] [[a-one-directional-check-certifies-its-blind-side]]
- **Prior (1.108.304):** **Three hypotheses, each measured, each wrong.** #557 (@Ticki84, Windows, ~10s to reindex one file where `index_file` took ~0.2s) drew an old version, the watcher's hash-cache reload, the `JCODEMUNCH_INDEX_CACHE_TTL` cliff and context providers. He answered all of it: **1.108.303, TTL unset, providers confirmed off FROM THE LOG'S OWN SILENCE, and the DEBUG line's `(10.31s)` is `index_folder`'s OWN duration** — so the time is inside indexing and every hypothesis we offered is dead. ⚠⚠ **He answered SIX HOURS BEFORE our next comment, which re-asked all three.** ⚠⚠ **What the hunt found instead: the fast path OPENED with `store.load_index(owner, repo_name)  # always load base for branch check`** — a full symbol hydration on every watcher event, INSIDE the block whose entire purpose is to skip loading the index and THREE LINES ABOVE the `use_memory_hash_cache` flag that exists to make the store's hashes unnecessary. **The saving that flag names was never realised on a cold read, because this ran first regardless.** Every question that path asks of it is metadata (`branch`, `git_head`, `file_hashes`, `has_source_file`, the two re-parse stamps), so it is a `SelectiveIndexView` now: **zero symbol rows, 0.172s -> under 1ms cold on 13,906 symbols.** ⚠⚠ **`parser_generation` and `racket_config_digest` HAD TO JOIN `EXACT_FIELDS` or the fix moves the cost instead of removing it** — absent from that tuple they fall through `__getattr__`, which promotes, so the per-event upgrade check would still load every symbol to read one integer. **If it lives in a `meta` row it belongs in `EXACT_FIELDS`.** ⚠⚠ **The test asserts `promoted is False`, NOT that `open_selective` was called** — the mechanism check stays green while a newly added `existing_index.symbols` hydrates the corpus behind it, which is the only regression worth catching (Practice 9's shape, caught at authoring time for once). 4 of 5 new tests fail pre-fix; the 5th guards a future regression and is honestly vacuous today. ⚠ **NOT his 10s and the thread says so** — his index is 6,352 symbols, where that load costs under a tenth of a second here. Shipped because it is wrong. ⚠⚠ **So the release's real deliverable is the INSTRUMENT: the watcher's re-index line now splits its own duration** (`[base_index= classify= read_hash= parse= git_head= save=]`, also `phase_seconds` on the result). Three rounds of guessing spent a reporter's patience; one line of one log now names the subsystem. ⚠ **A full walk emits NO breakdown rather than a zeroed one** — an empty bracket would read as "the fast path ran and cost nothing", the opposite of what happened, so absence means the fast path was not taken, which is the first thing worth knowing. ⚠ **Practice 10's first real case, and it held**: touched files 122 tests in 10s, suite once as the gate at 10:18. ⚠⚠ **A background-task banner reported "exit code 0" for a suite that NEVER RAN** (`--timeout` plugin absent, pytest exited on argparse). Only the log's own `EXIT=` line is evidence; the banner is not. [[a-trailing-command-hides-pytests-exit-code]] [[a-module-that-imports-clean-has-been-tested-for-nothing]]
- **Older releases (1.108.303 and earlier):** see `CHANGELOG.md` (1.108.303 in `ISSUE-HISTORY.md`). The 1.108.182 entry ("a stall has a name and a ceiling", #375) and the 1.108.177-.181 #377 hardening arc are there in full.
- **Tests:** 8794 passed, 13 skipped, **0 failed** (1.108.306) **+ `uv run ruff check src/` clean**, measured on the settled tree after the bump and the rotation. ⚠ **8807 TOTAL, +45 over .305's 8762.** ⚠⚠ **READ THE SKIP COUNT, NOT JUST THE EXIT CODE AND THE TOTAL.** A .305 3.13 reproduce came back **exit 0 with the total reconciling EXACTLY** while `passed` fell 8,721 -> 8,634 and `skipped` rose **19 -> 124**: 105 tests silently did not execute, because the documented command never built CI's environment (no sync, no `--extra watch`). See **Reproducing CI's environment**. ⚠⚠ **Compare TOTALS, never passed counts, and NEVER a skip count ACROSS machines** — CI ubuntu skips 26 and windows 19 where this box skips 13, all pre-existing; **the before/after delta on the SAME job is the only signal**, and that is exactly what caught it. ⚠⚠ **A BACKGROUND-TASK BANNER SAYING "exit code 0" IS NOT A GREEN SUITE** — one run reported exit 0 having never started pytest (`--timeout` plugin absent), and **this release had a banner say exit 0 over a log whose own `EXIT=` line said 1.** **Redirect the exit code INTO the log (`{ pytest; echo "EXIT=$?"; } > log`) and grep that line**; a bare `&` does not survive the shell either. ⚠⚠ **A CONTRIBUTOR PR IS TRIAL-MERGED ONTO `main` AND RUN LOCALLY BEFORE THE MERGE** — branch-green is not merged-green and the merge base moves every release. ⚠ **CI on the pre-release PR (#563) was green on all 12 checks with the skip counts CORRECT**: ubuntu 3.10 8781/26, windows 3.13 8788/19, both totalling 8807. ⚠⚠ **A reproduce that ERRORS in `tests/test_sdist_exclusions.py` is NOT environmental noise** — that file is the sdist CREDENTIAL-LEAK guard (v0.2.6), and it errors at setup when the scratch venv must fetch the build backend with DNS blocked. Re-run it explicitly; never wave it through. ⚠ Prior (1.108.305): 8749 passed, 13 skipped, **0 failed** (8762 total). ⚠ Prior (1.108.304): 8727 passed, 13 skipped, **0 failed** (8740 total). ⚠ Two full runs contend on the same `~/.code-index` process-lock scopes, the documented cause of .261's 47m outlier, so the 3.13 reproduce runs AFTER the local suite, never beside it.
- **Python:** >=3.10
- **Tool count:** 91 visible in `full` / 94 in catalog (front door hidden; counts verified 2026-07-30 from `jcodemunch-mcp surface`, which is the only place to get them — do NOT hand-type this; +1 v1.108.111 `get_parity_map`, +1 v1.108.112 `get_decorator_census`, +1 v1.108.113 `get_architecture_metrics`); `tool_surface=counter` exposes a 3-tool front door (`order`/`menu`/`route`) instead

## Key Files
```
src/jcodemunch_mcp/
  server.py            # MCP dispatcher (async); CLI subcommand dispatch, auth/rate-limit middleware. v1.108.292: `_mcp_instructions()`/`_tool_search_query()`/`_initialization_options()` — the MCP `initialize` `instructions` string, surface-aware (front door on `counter`, the six core tools on `full`), 1,000-char budget. ⚠ Built per `run()`, never passed to `Server(...)` at import: the surface comes from env+config and neither is settled then. ⚠⚠ It is THE ONLY prose that survives tool deferral — a host over its schema budget ships 91 bare names and withholds every description. All three transports pass it; `tests/test_mcp_instructions.py` parses the dispatcher's AST and fails if any `server.run()` goes back to a bare `create_initialization_options()`, which sends an empty field and raises nothing. ⚠ Same line also sets `Server(..., version=__version__)`: omit it and the SDK reports ITS OWN version in `serverInfo` (hosts showed `1.26.0` while we shipped 1.108.x). ⚠⚠ `__version__` is `"unknown"` under `PYTHONPATH=src`, so a green test here does NOT prove the wire carries a real number — **and CI cannot close that gap either, because it runs from source too.** ⚠ **Verify the handshake MANUALLY against the PUBLISHED artifact** after any change to it (#536): pin the version and build a fresh venv (`uv venv` + `uv pip install "jcodemunch-mcp==X.Y.Z"`), then do a real stdio handshake. ⚠⚠ **NEVER probe through bare `uvx`** — it served a CACHED build once and showed the SDK's own version with no instructions, i.e. **exactly the pre-fix symptoms from a stale cache rather than a defect.** (2026-08-24, ISSUE-HISTORY.md) v1.108.66: the Counter front door (order/menu/route) — _effective_surface()/_counter_front_door_tools()/_raw_catalog_tools()/_catalog_names() + surface-collapse in _build_tools_list + _handle_order/menu/route + early front-door branch in call_tool
  counter.py           # (v1.108.66) The Counter: adaptive tool surface logic (pure, no server import). FRONT_DOOR set; STATE_CHANGING_ACTIONS + exec/write-verb tripwire (_FORBIDDEN_VERB_RE) → order_gate(); idf-weighted search_catalog() for menu; _INTENT_RULES + classify_intent()/shape_execute_args() for route. v1.108.124: EXAMPLES (curated per-action example arg objects) + example_for() — catalog_entry attaches `example` into menu rows, _handle_route uses it as the args_template fallback; validated against live inputSchemas in test_counter.py. server.py owns Tool registration + call_tool re-dispatch; counter.py is fed plain data
  watcher.py           # WatcherManager class (dynamic folder watching); watch_folders() wrapper
  progress.py          # MCP progress notifications; ProgressReporter (thread-safe, monotonic), make_progress_notify() bridge. v1.108.189 adds HeartbeatReporter (#383) — the token-less fallback: elapsed-time WARNING lines on the LOG channel, duck-typing ProgressReporter so the dispatcher wires either identically. ⚠ Holds NO notify channel/session ref by construction (not in __slots__) and close() yields no futures, so it CANNOT become an unrequested notification; silent until the first JCODEMUNCH_HEARTBEAT_SECONDS elapses, and finish() is silent if it never spoke
  security.py          # Path validation, skip patterns, file caps. ⚠ **A build tree is excluded in ELEVEN spellings** — `build`, `.build` and (v1.108.295) `_build`, which is what Elixir/Mix, Sphinx and Dune use — plus (v1.108.303) the eight DOTTED framework trees `.next`/`.nuxt`/`.output`/`.svelte-kit`/`.angular`/`.turbo`/`.parcel-cache`/`.dart_tool`. ⚠⚠ **`.next/server/**` holds a TRANSPILED copy of the pages the user WROTE**, so a Next.js project got its own source twice with the generated copy competing in ranking. ⚠ **DOTTED ONLY** — `out`, `bin`, `obj`, `coverage` and `public` all name real source dirs, and `tests/test_framework_build_trees_are_skipped.py` asserts their ABSENCE as firmly as the eight additions. **`mix` copies dependency SOURCES into `_build`**, so this was the v1.108.234 duplicate-source-tree defect wearing a third name, not a new one. ⚠ Add spellings to `_SKIP_DIRECTORY_NAMES`, never to a derived export — `SKIP_DIRECTORIES` (local walk) and `SKIP_PATTERNS` (GitHub indexer) both derive from it, and editing one reaches only half the product. `verify_package_integrity()` runs on EVERY CLI invocation and its checks are ordered cheapest-first — that ordering IS the fix. ⚠⚠ `packages_distributions()` maps every distribution on `sys.path` to answer a question about ONE: **3.35 s uncached on a box with 894 top-level names, and it returned nothing there** (source tree, no distribution describes it). Targeted `distribution("jcodemunch-mcp")` settles the ordinary install in **5 ms**; the map is reached only when the official dist is absent or did not provide the running module. ⚠⚠ **The map must stay REACHABLE** — it alone can NAME the offending distribution, which is the whole warning; a guard that just banned the call would be satisfied by deleting the security check. ⚠ **Installed-and-correctly-named is NOT sufficient**, so the fast path also proves the official dist owns the running `__file__`. ⚠ Invisible while the CLI was human-typed; the whole cost of a hook once hooks spawn it per call (`hook-pretooluse` 4.0s -> 0.94s). `tests/test_integrity_check_cost.py` asserts the COST as a property, never the call order
  redact.py            # Response-level secret redaction; regex patterns for AWS/GCP/Azure/JWT/GitHub/Slack/PEM/API keys/private IPs; redact_dict() post-processor
  config.py            # JSONC config: global + per-project layering, env var fallback, language/tool gating
  agent_selector.py    # Complexity scoring + model routing (off/manual/auto); default provider batting orders
  cli/
    policy.py          # (cycles refactor) CLAUDE.md policy text + surface detection + tool filtering; `active_policy()` is the ONE entry point. ⚠⚠ Extracted from `init.py` to break a REAL cycle — `skills.py` needed the policy half, `init.py` needed `install_claude_skill`. This is the LEAF both share and must import NEITHER. ⚠⚠ **`init.py` re-exports every name and that is a MONKEYPATCH TRAP**: patching `init._effective_tool_surface` does NOT affect `policy.active_policy`, which resolves through `policy`'s globals — silently, nothing warns. **Patch `cli.policy`.**
    init.py            # `jcodemunch-mcp init` — one-command onboarding (client detection, config patching, CLAUDE.md, Cursor rules, Windsurf rules, hooks); --demo flag. v1.105.1: `install <agent>` / `uninstall` / `install-status` verbs. v1.107.0: `--skills` flag on install, skills block in install_status report
    skills.py          # v1.107.0: Claude Agent Skill bundle writer. _build_skill_content() composes YAML frontmatter + tier-filtered tool-usage decision tree. install_claude_skill / uninstall_claude_skill / skill_status. Lives at ~/.claude/skills/jcodemunch/SKILL.md (global) or ./.claude/skills/jcodemunch/SKILL.md (project). Reuses _filter_policy_for_tools from init.py for tier awareness
    hooks/             # Claude Code hook handlers, one module per family: steering.py (PreToolUse Read/Grep/Glob/Bash-search), reindex.py (PostToolUse auto-reindex + Copilot variant), snapshot.py (PreCompact transcript-root registration only — no exit-0 output channel — + SessionStart snapshot restore), landmarks.py, taskcomplete.py (post-task diagnostics, live-journal fed), briefing.py (surface-aware SubagentStart), _common.py; __init__.py re-exports run_* for server.py dispatch
  groq/
    cli.py             # `gcm` CLI entrypoint — codebase Q&A (single question + --chat mode)
    config.py          # GcmConfig dataclass: GROQ_API_KEY, model, token_budget, system prompt
    retriever.py       # Bridge to jCodeMunch: ensure_indexed(), retrieve_context()
    inference.py       # Groq API streaming + batch via OpenAI-compatible client
  parser/
    complexity.py      # cyclomatic / max_nesting / param_count from body TEXT, no AST. ⚠⚠ **`max_nesting` is `max(bracket_channel, indent_channel)` and BOTH are required.** Brackets alone cannot see Python control flow — `if`/`for`/`while` open a block with a colon and contribute NO bracket depth, so the field reported the deepest EXPRESSION under the same name (`index_folder`: brackets 3, AST truth 6, an underreport by HALF that supported the OPPOSITE conclusion about the symbol). Indentation alone cannot see MINIFIED code, which has none. Max can only RAISE a depth, so brace languages are unmeasured-by-neither and unchanged. ⚠ `max_nesting` is REPORTED (get_symbol_complexity / get_hotspots / get_extraction_candidates / get_pr_risk_profile) and SCORED NOWHERE — `hotspot_score` and `_complexity_assessment` use cyclomatic alone, so correcting it moves no grade. ⚠⚠ A literal BACKSPACE (0x08) once replaced `` in the opener regex and **compiled, ran and passed ruff**; `tests/test_nesting_depth_channels.py` pins the boundary behaviourally and scans for stray control characters
    languages.py       # LANGUAGE_REGISTRY, extension → language map, LanguageSpec
    extractor.py       # parse_file() dispatch; custom parsers for Erlang, Fortran, SQL, Razor
    imports.py         # Regex import extraction (19 languages); extract_imports(), resolve_specifier(), build_psr4_map(). ⚠⚠ **`_JS_SPECIFIER_REWRITES` exists because a TS specifier names the EMITTED file, not the source**: `.mts` is imported as `./foo.mjs` and `.cts` as `./foo.cjs`, extensions that are NEVER on disk. Adding an extension to `LANGUAGE_EXTENSIONS` without its rewrite entry makes the file visible and its importers invisible -- which reads downstream as a file nobody imports, i.e. #550 in a new costume. The `.js -> .ts/.tsx` rule predates the table and is unchanged; `test_ts_module_extensions.py` asserts that byte-for-byte
    fqn.py             # PHP FQN ↔ symbol_id translation (PSR-4); symbol_to_fqn(), fqn_to_symbol()
  encoding/
    __init__.py          # Dispatcher: encode_response(tool, response, format) — auto/compact/json
    format.py            # MUNCH on-wire primitives: header, legends (@N), scalars, CSV tables
    gate.py              # 15% savings threshold (JCODEMUNCH_ENCODING_THRESHOLD override)
    generic.py           # Shape-sniffer fallback encoder (covers all tools w/o custom encoder)
    decoder.py           # Public decode() — rehydrates MUNCH payloads back to dicts
    schemas/             # Per-tool custom encoders (tier-1, phase 2+); auto-discovered registry. ⚠⚠ **A schema that disagrees with its producer about the table KEY is INVISIBLE to the fail-closed guard**: `schema_driven` raises when a table has rows but no declared column populated (#354), and a wrong key yields NO rows, so `out_rows` is empty and the check never runs. (#553: `search_ast` declared `results` where the tool returns `matches`, serving an empty table for every language and preset.) ⚠ `tests/test_search_ast_encoder_contract.py` is the CI ratchet: every declared table key must name something its tool emits. ⚠⚠ **(#555) `sd.encode` also fails closed at RUNTIME on a list-of-dicts under a key no `TableSpec` declares.** It runs POST-transform BY CONSTRUCTION — `search_text._flatten` has already removed the public `results` — so pre-flattening schemas need NO exemption; **scanning the RAW response instead flags `search_text` on every call**, and an allowlist entry for it would be the wrong fix to the right symptom. `allow_undeclared=(...)` is explicit and per-key; raises rather than warns (dispatcher falls back to JSON, data survives). ⚠ **Columns are the second half and the near-miss**: a heterogeneous row set (search_ast carries 16 keys across 10 detectors, 5 of them pattern-specific) loses its payload silently if only the common columns are declared, because `file`/`line` populate and `any_value` goes true. Pattern-specific keys ride as one JSON cell, the `search_text` `before`/`after` shape. A table-key or column change is a WIRE change: bump `ENCODING_ID` and add the old one to `LEGACY_ENCODING_IDS`
  investigator/
    deletion_safety.py           # (v1.108.214) tri-state proof obligations; `investigate_deletion_safety`. NOT an MCP tool
    retrieval_counterfactual.py  # (v1.108.217) `explain_route(task, expected_action)` / `explain_misses(per_query)` — names the FIRST gate that excluded an action: `catalog_absent` / `empty_query` / `rule_preempted` / `no_lexical_overlap` / `ranked_below_cutoff`, in pipeline order (reporting more than the first is reporting consequences). ⚠ Uses the SAME `counter` functions the live front door uses — never a second scorer. ⚠⚠ `rule_preempted` = **never scored**, because `route` runs the fallback ONLY when no rule matched; do NOT read it as a ranking loss. NOT an MCP tool (item 3 moratorium), test-asserted
    reuse_audit.py               # (v1.108.296) `investigate_reuse_before_write(repo, intent)` -- reuse-before-write as proof obligations. Verdicts reuse_available/adapt_candidate/write_justified/lexical_only/not_established; obligations intent_is_searchable (fatal), no_name_twin, no_lexical_match, no_semantic_match, no_structural_twin (optional, EXCLUDED from `_verdict` and `_confidence` when no `proposed_signature` was passed, still shown in `obligations`). ⚠⚠ **`lexical_only` is the whole point**: an intent of 'modal' shares no token with an existing `Dialog`, so an unavailable embedding channel goes UNESTABLISHED and degrades the verdict instead of licensing a write. `no_provider` and `repo_not_embedded` are separate states with OPPOSITE advice. ⚠⚠ **`search_symbols` emits `score` ONLY under `debug=True`** -- without it every row squashes to 0.0, `strong`/`partial` are empty BY CONSTRUCTION and `strong_match`/`adapt_floor` grade nothing. ~25 ms/sweep vs a 0.5 ms cache hit; losing the cache is correct (an absence claim replayed from a cached row is #377 item 3). ⚠⚠ **Sample `_index_was_rewritten` BEFORE any channel runs, never after** -- our own semantic read opens a read-WRITE connection and moves the very mtime the probe compares, so a post-scan sample reported a rewrite we caused ourselves and made `write_justified` UNREACHABLE. ⚠ `has_any()` returning None is UNKNOWN, not embedded-and-clean. ⚠ A refutation backed only by symbols proved dead yields `adapt_candidate` + `dead_matches`, never `reuse_available` -- and is ordered AHEAD of the absence blockers, because a positive hit is not an absence claim. ⚠ `_STRONG_MATCH`/`_ADAPT_FLOOR` are SEEDED, not calibrated, and had never been evaluated against a non-zero score before v1.108.296. NOT an MCP tool (moratorium: control route@1 40.0% vs a 55.0% bar), registered in `WITHHELD`
  storage/
    selective.py       # (v1.108.216, #398 Arc 2) `SelectiveIndexView` — a `CodeIndex`-SHAPED read view over metadata + named symbol rows. **NOT a subclass**: subclassing would inherit CodeIndex's corpus-wide methods silently operating over a partial `symbols` list, the one outcome this exists to make impossible. `EXACT_FIELDS` are copied onto the instance at construction; **everything else falls through `__getattr__` and promotes to one full load** — including fields invented later. `CORPUS_WIDE` documents the known ones and every entry is parametrized in the test. ⚠ `_PROVENANCE` (`_db_path`/`_loaded_mtime_ns`) MUST stay in `__slots__` — see Current State. ⚠⚠ **A metadata field left OUT of `EXACT_FIELDS` costs a full hydration to read one value, silently** — `parser_generation`/`racket_config_digest` (#557) were read by the watcher's per-event upgrade check and promoted the whole corpus to answer an integer. **If it lives in a `meta` row, it belongs in `EXACT_FIELDS`.** ⚠ Assert `promoted is False` after the reads, never that `open_selective` was called — the latter stays green while a new `.symbols` access hydrates behind it
    generation.py      # (v1.108.215, #398 Arc 1) THE READ CONTRACT, both halves. `IndexGeneration`/`describe(index)` — the ONE place `indexed_at`/`git_head`/`_db_path`/`_loaded_mtime_ns` are read off an index; empty string normalises to None once (three surfaces used to disagree). `rewritten_since_load` keeps unknown ≠ changed. `connect_readonly(db_path)` / `readonly_uri` / `wal_sidecar_present` — ⚠⚠ **neither single flag is right**: plain `mode=ro` CREATES `-wal`/`-shm` when absent (moves `_db_mtime_ns`, the .185 `rebuilding` bug), `immutable=1` cannot READ them when present (measured: raises `no such table`, which `has_any()` maps to a confident False). Reads the WAL when its sidecar exists, immutably when it does not. **Every read-only opener in the tree routes through this**; `test_generation_contract.py` fails on a hand-rolled `?mode=ro` URI anywhere else
    sqlite_store.py    # CodeIndex, save/load/incremental_save, WAL-aware LRU cache (_db_mtime_ns); get_source_root(). v1.106.0: save_index + migrate_from_json acquire `indexwrite` process_locks before SQLite writes, body extracted to `_save_index_locked` / `_migrate_from_json_locked`; serialises across MCP processes
    process_locks.py   # v1.106.0: generic multi-process coordination (acquire/release/inspect/held). Atomic O_EXCL + fcntl flock (Unix) + PID liveness + scoped lock files. Scopes: `watcher` (one-watcher-per-repo, shared with watcher.py) + `indexwrite` (save coordination). Metadata: pid/client_id/scope/target/started_at. JCODEMUNCH_CLIENT_ID env var sets friendly client name (defaults to sys.argv[0] basename) ⚠⚠ **(#557) `held.__enter__` records `waited_seconds` and REPORTS it** — DEBUG for any wait, **WARNING past `_SLOW_WAIT_SECONDS` (1.0) with the holder NAMED** (pid/client_id/age). **A CONTENDED LOCK AND SLOW WORK ARE INDISTINGUISHABLE FROM THE CALLER'S TIMER**: `incremental_save` takes this lock before writing, so a reporter measuring `save=9.906s` cannot tell queueing from working and only this function can. ⚠ `watch-all` watches EVERY indexed repo, so a second watcher or an editor-side MCP server is exactly the shape that queues here — naming the holder is the point, because "something else has the lock" sends the reader hunting in the wrong process.
  embeddings/
    ../storage/embedding_matrix.py # (v1.108.223, #399) Process-local cache of the L2-NORMALISED matrix, keyed by a size+mtime stamp over the .db AND its -wal/-shm sidecars. `get_matrix(db_path)` -> `EmbeddingMatrix | None`; `score_all(q)` is ONE `matrix @ q` under numpy and a norm-hoisted Python loop without it. ⚠ **numpy is opportunistic, never a dependency** — `_scores_python` is tested with numpy forced absent. ⚠ **The sidecars are load-bearing in the stamp**: a write lands in the WAL and may not touch the .db until a checkpoint, so a .db-only stamp pins a stale matrix across exactly the write it must see. ⚠ Rows are `array.array('f')` in the fallback, not `list[float]` (~8x the memory, and this is HELD not thrown away). Bounded to 2 repos; `JCODEMUNCH_EMBED_MATRIX_CACHE=0` disables retention only
    ../storage/embedding_store.py  # CRUD over symbol_embeddings. ⚠ **Five read paths, pick deliberately**: `iter_raw()` (.223, read-only, UNDECODED blobs, for embedding_matrix only); `get_all()` (read-WRITE conn, bumps .db mtime), `get_all_readonly()` (.185, `mode=ro&immutable=1`, does not), `get_many(ids)` (.210, targeted + read-only, chunked at 900 for SQLITE_MAX_VARIABLE_NUMBER), `has_any()` (.211, `SELECT 1 ... LIMIT 1`, read-only, TRI-STATE — `None` means could-not-establish and is NEVER `False`). ⚠ `count()` and `get_all()` both use `_connect()`, which runs PRAGMA+CREATE-TABLE on EVERY connection — an existence check is NOT free and moves the mtime. Prefer `get_many` whenever the caller already knows its ids, and `has_any` over `count()` for a pure existence question
    local_encoder.py   # Bundled ONNX local encoder (all-MiniLM-L6-v2, 384-dim); WordPiece tokenizer, encode_batch(), download_model()
  enrichment/
    lsp_bridge.py      # LSP bridge — opt-in compiler-grade call graph resolution via pyright/gopls/ts-language-server/rust-analyzer; LSPServer lifecycle, LSPBridge multi-server manager, enrich_call_graph_with_lsp() + enrich_dispatch_edges() (interface/trait dispatch resolution)
  retrieval/
    subject_state.py     # (v1.108.178) #377 item 3: what a scan's answer depends on, cheap enough to re-check. capture() at cache-WRITE (index generation, .db mtime, live git HEAD, + working-tree fingerprint ONLY for an absence) / changed() at cache-READ / revalidate_verdict() downgrades a replayed `absent` and strips the stale evidence token. UNKNOWN is never a change. v1.108.179 adds moved_during_scan() (item 6: before/after identity around a scan, fresh_head bypasses the TTL cache) + changed(when=) so the cached-replay and live-scan refusals read differently. v1.108.181 adds working_tree_state() (item 5: scope-level clean/dirty_in_scope/dirty_outside_scope/unknown/not_applicable; blocks ONLY on in-scope dirt the index has not re-read) + _parse_porcelain/_in_scope/_unreflected_in_index
    signal_fusion.py   # Weighted Reciprocal Rank (WRR) fusion: lexical + structural + similarity + identity channels
    ledger_trust.py    # (v1.108.186/.187) THE ONE RULE for which ranking_events labels are evidence, shared by tuning.py + regret.py + tools/analyze_perf.py instead of copied. semantic_label_is_trustworthy(row) refuses exactly (tool="get_ranked_context_fusion", semantic_used=1) — pre-fix rows from an exit that built no similarity channel. identity_label_is_trustworthy(row) (.187) refuses rows that RETURNED symbols while recording NO top1_score — the only exact signature of the exit that passed no ledger features; ⚠ it deliberately does NOT match on identity_hit itself (pre-fix is always 0 and 0 is an honest post-fix answer), and search_symbols_fusion's history is UNSEPARABLE (no discriminator exists, window is the only remedy). ⚠⚠ **(#440) `search_symbols` is unseparable for the SAME reason and over a MUCH larger share of the table** — both non-fusion exits built the same score-only ledger input, they too always passed top1_score, and search_symbols is the highest-volume producer in the ledger. Producers fixed via `_ledger_identity_rows` (see Current State); **do NOT read "the fusion rows are handled" as "the identity_hit column is clean"** — it is clean only for rows written after that fix. UNKNOWN, not False: consumers put them in a THIRD bucket and disclose the count. A short row is TRUSTED (this refuses a KNOWN lie; refusing the unclassifiable would be silent data loss). ⚠ The semantic rule EXPIRES if that exit ever builds a similarity channel — drift guard in tests/test_v1_108_186.py
    regret.py          # (v1.108.68) analyze_regret: mines the ranking_events ledger for SIX retrieval-regret signals (requery_churn/low_confidence/thin_result/ambiguous_top/stale_at_query/vocabulary_gap) as severity-ranked clusters. Pure read via token_tracker.ranking_db_query; no new tables. Consumed by suggest_corrections + the digest one-liner. **v1.108.290 adds `_detect_inflation`** (arXiv:2608.13571): retrieval inflation = calls per information need, where a need is `(session_uid, query_hash)` — clusters name WHICH queries went wrong, this says what the wrongness COST. ⚠⚠ **The basis is CALLS and the `basis` field says so on every shape** — `ranking_events` has no token column, so a ratio named after tokens would be measuring one thing and named for another; renaming it needs a column, not an adjective. ⚠⚠ **A NULL `session_uid` is UNKNOWN and EXCLUDED, never folded into a synthetic session** — #456 added the column by ALTER, so every pre-#456 row carries NULL and folding them collapses the whole historical ledger into ONE need with a spectacular fake ratio. ⚠⚠ **`repeats_after_index_change` is DISCLOSED AND NOT SUBTRACTED** — a re-ask after the index moved is arguably a different question, but subtracting it LOWERS OUR OWN NUMBER, and a self-flattering adjustment applied silently is the one direction this metric must not drift. ⚠ Reads via `token_tracker.ranking_db_inflation_rows`, a SECOND query returning **None for could-not-ask, never `[]`**: `ranking_db_query`'s 12-tuple is read positionally by four modules and opens the db outside `_ensure_perf_db`, so selecting a maybe-absent column there would hit its catch-all and return `[]` for every consumer — one missing column, all six signals dark. ⚠ Floor of `INFLATION_MIN_NEEDS=5`; below it the block refuses rather than reporting noise
  summarizer/
    batch_summarize.py # 3-tier: Anthropic > Gemini > OpenAI-compat > signature fallback
  tools/
    index_folder.py    # Local indexer (sync → asyncio.to_thread in server.py). v1.108.0 adds `paths=[...]` arg via new `resolve_explicit_paths()` helper to skip the directory walk when the caller supplies an explicit file/subdir list; security matches the walk path (outside-root / traversal / symlink-escape / oversize / unsupported-ext all warn-and-skip with per-entry warnings). v1.108.6 adds `identity_mode: "config"|"local"|"git"` arg — delegates to `storage/git_root.resolve_index_identity()` which is the single source of truth for local-folder → repo-ID resolution (replacing duplicated logic across watcher.py / resolve_repo.py / index_folder.py).
    refresh.py         # (v1.108.259, #395) Bounded, resumable repo-wide refresh. `run()` slices the corpus through `index_folder(paths=..., force_reparse=True)` under a wall-clock + file budget, persisting a cursor to `<CODE_INDEX_PATH>/refresh_state/<owner>__<name>.json` (atomic write) so N short windows converge like one long one. `status()` reports progress and does NO work. ⚠⚠ Stamps `parser_generation` ONLY after re-running discovery proves full-corpus coverage — drift appends and DEFERS, batch errors block, and `stamp_parser_generation` refuses to go backwards. ⚠⚠ **A growth-only check cannot see an EMPTY corpus**: a moved/unmounted/cleaned source root makes discovery return `[]`, nothing drifts, nothing errors, and the campaign stamps the generation having re-parsed ZERO files — UNREPAIRABLE, because a stamp equal to the constant is indistinguishable from a genuine one. Refuses on `corpus_unreadable` and `index_unreadable` (UNKNOWN blocks, same rule as `has_any()`). ⚠ EMPTY-vs-NON-EMPTY deliberately, NOT a shrink threshold: a repo may legitimately lose most of its files, so partial shortfall is DISCLOSED as `indexed_files_not_reparsed`. (2026-08-25, ISSUE-HISTORY.md) ⚠ `use_ai_summaries` defaults FALSE here (opposite of `index_folder`): a scheduled job must not bill a paid summarizer unasked
    index_repo.py      # GitHub indexer (async, httpx)
    get_symbol.py      # get_symbol_source: shape-follows-input (id→flat, ids[]→{symbols,errors}). v1.108.70 bounded-source mode: optional source_start_line/source_end_line/max_source_lines/max_source_bytes/max_total_source_bytes return an explicitly-labeled slice (source_truncated + range/total metadata, source_is_bounded_view); verify stays full-body; context_lines+bound rejected. Pure helpers _utf8_safe_truncate + _bound_source
    search_columns.py  # Column search across dbt/SQLMesh models
    get_context_bundle.py   # Symbol + imports bundle; token_budget/budget_strategy
    get_ranked_context.py   # Query-driven budgeted context (BM25 + PageRank)
    resolve_repo.py    # O(1) path→repo-ID lookup
    find_importers.py  # Files that import a given file (import graph); cross_repo param
    find_references.py # Files that reference a given identifier. v1.108.96: _attach_scip_to_response unions SCIP compiler-verified reference edges (compile-time evidence P1)
    _scip_consume.py   # (v1.108.118) Shared SCIP-evidence reader for the graph consumers (P2): open_scip_reader (mode=ro, honest-None when scip_edges absent/empty incl. pre-v17) + scip_meta_and_stale + scip_meta_block. Used by get_blast_radius._attach_scip_to_blast + get_call_hierarchy._attach_scip_to_hierarchy
    test_summarizer.py # Diagnostic tool: probe AI summarizer, report status (disabled by default)
    package_registry.py # Cross-repo package registry: manifest parsing, registry building, specifier resolution
    get_cross_repo_map.py # Cross-repo dependency map at the package level
    _call_graph.py       # Shared AST-derived call-graph helpers (callers/callees, BFS)
    get_call_hierarchy.py # get_call_hierarchy: callers+callees for a symbol, N levels deep
    decision_context.py   # (v1.108.59) resolve_decision_context: read-only git-archaeology surfacer. Mines decision-bearing commits (revert/perf/refactor/rename/bugfix) for a set of files, reusing get_symbol_provenance's _run_git/_classify_commit/_extract_intent; dedupes by SHA, ranks by category weight × recency, emits digest + by_category + volatility + summary. Surface-only, nothing persisted. Consumed by get_blast_radius / get_impact_preview via include_decisions
    get_impact_preview.py # get_impact_preview: transitive "what breaks?" analysis. v1.108.59: include_decisions attaches a read-only `decisions` block (decision_context)
    plan_refactoring.py   # plan_refactoring: edit-ready plans for rename/move/extract/signature refactorings
    get_symbol_complexity.py  # get_symbol_complexity: cyclomatic/nesting/param_count for a symbol
    get_churn_rate.py         # get_churn_rate: git commit count for file or symbol over N days
    get_delivery_metrics.py   # (v1.108.69) get_delivery_metrics: durable-change delivery over a window. Classifies each non-merge commit into one bucket (revert_authored/reverted/reworked/durable) via _run_git; commits_durable is the numerator for cost-per-outcome (the `delivery` CLI's --cost divides AI spend by it). Hub files (CHANGELOG/version/monolithic dispatch, co-touched by >=max(4,20%) of commits) excluded from the rework signal (auditable via _meta.hub_files_excluded); commits_provisional flags the trailing tail. Reuses get_symbol_provenance._classify_commit for by_category. Read-only, no new tables
    get_symbol_provenance.py  # get_symbol_provenance: full git archaeology per symbol — authorship lineage, semantic commit classification, evolution narrative. Phase 5: optional stack_frequency block reading runtime_stack_events over a 30-day window — per-severity counts + first/last seen; narrative gains an appended sentence when error count >= 3
    get_pr_risk_profile.py    # get_pr_risk_profile: unified PR/branch risk assessment — fuses blast radius + complexity + churn + test gaps + volume into composite score. Phase 7: when runtime traces have been ingested, adds a 6th signal (runtime_traffic; W=0.15 with the static five rebalanced to 0.85 of their original weights) plus a runtime_dark_code_introduced flag for PRs that add code in files with zero runtime evidence. Static-only callers (no traces) keep the historical 5-signal mix bit-for-bit.
    get_architecture_metrics.py # (v1.108.113) get_architecture_metrics: concentration (Gini over per-file symbols/bytes/fan_in/fan_out + top concentrators) + depth (Lakos levelization, longest chain over SCC-condensed DAG) + modularity (WCC clusters + back_edges = DSM hidden coupling). Reuses _build_adjacency (get_dependency_graph) + _find_cycles. One tool vs their 3; NO N×N matrix; does NOT touch radar composite. Read-only analytics. Standard tier
    get_decorator_census.py   # (v1.108.112) get_decorator_census: repo-wide census of decorators/annotations/attributes. Aggregates the index's stored per-symbol `decorators` (cross-language, no parser work); normalized histogram (_normalize_decorator strips @/args/[]; _short_raw flattens+caps raw_forms), per-bucket symbol_kinds + file count; name_filter/scope_path/kind filters, include_sites. Read-only ANALYTICS (no tokens-saved _meta). Standard tier
    get_parity_map.py         # (v1.108.111) get_parity_map: correspondence-aware migration parity between a SOURCE and TARGET symbol tree (two subpaths of one repo, or two repos). Exact + rename matching (reuses find_similar_symbols _signature_tokens/_callee_set/_jaccard/_byte_ratio), status per source symbol (ported/ported_diverged/unported/orphaned/added), dependency-ordered port_plan (adjacency from _callee_set, SCC grouping via get_dependency_cycles._find_cycles, Kahn topo, unblocked/blocking_deps). Read-only/plan-only; parity_axes reserved for P3 suite axes. Standard tier
    find_dead_code.py         # ⚠⚠ **`_ENTRY_POINT_FILENAMES` is Python and nothing else** -- eleven `.py` names plus `Makefile` -- so on a JS repo it names NOTHING (#562). Framework roots come from `_entry_points.entry_point_spec`, never from this list. ⚠⚠ **`_TOOLCHAIN_MANIFESTS`**: nothing imports a lockfile BY DESIGN, so `zero_importers` is a tautology there -- `pnpm-lock.yaml`, `tsconfig.json` and `package.json` were reported dead, the last by the same run that READS it to find entry points. **Excluded by NAME, never by extension**: an orphaned `data/fixtures.json` is a real finding and must keep being reported. `Makefile` was already in the set above for exactly this reason.
    get_hotspots.py           # get_hotspots: top-N high-risk symbols by complexity x churn
    get_repo_map.py           # get_repo_map: query-less, token-budgeted, signature-level repo overview ranked by PageRank — cold-start orientation. Reuses cached PageRank, emits signatures only (no bodies), greedy-packs per-file under token_budget
    find_similar_symbols.py   # find_similar_symbols: multi-signal consolidation detection — semantic (embeddings) + structural (signature/size) + behavioral (callee Jaccard); union-find clustering, verdict tier (near_duplicate / similar_logic / parallel_implementation), canonical pick by PageRank, differs_by breakdown. BM25 inverted-index pre-filter for sub-N^2 cost. Skips tests/dunders/generated by default.
    get_group_contracts.py    # get_group_contracts: cross-repo shared-symbol API surface for a group of indexed repos. Resolves named imports through the package registry, classifies each shared symbol into 4 verdict tiers (de_facto_api / leaky_internal / dead_contract / version_skew), attaches stability score (churn-weighted), last_breaking_change (from provenance), and runtime_hits (when traces exist). Pairs with get_cross_repo_map: that gives repo-level edges; this zooms in to the symbol-level surface.
    find_implementations.py   # find_implementations: multi-source concrete-impl discovery for interfaces/abstracts/methods. Four resolution channels with confidence scoring — LSP dispatch (1.0), AST class hierarchy (0.85), duck-typed name match (0.65), decorator handler (0.45). Classifies each impl (subclass_override / interface_impl / duck_typed / decorator_handler / subclass), ranks by PageRank × byte_length, attaches differs_by breakdown, optional cross_repo discovery.
    check_delete_safe.py      # check_delete_safe: composite preflight — can this symbol be deleted? Combines find_importers (cross_repo) + check_references + find_dead_code + runtime evidence + entry-point heuristics into a single verdict (safe_to_delete / test_coverage_only / internal_only / internal_uses_blocking / external_uses_blocking / cross_repo_blocking / runtime_observed / entry_point) plus top-5 blockers ranked by severity plus a one-line recommended_action. Read-only. Pairs with check_rename_safe for the rename-and-delete refactor flows. v1.104.1: track test_import_count separately from external_import_count so test-only consumption correctly downgrades to test_coverage_only. v1.108.6: honest-hint caveat — when `safe_to_delete` is reached AND `include_runtime=True` AND no traces are ingested for the repo (`_runtime_data_present()` returns False), the `recommended_action` surfaces that the verdict rests on static signals only and points at `import-trace`. `signals.runtime_data_present` surfaced for callers to introspect. Back-ported from `check_column_drop_safe` in jdatamunch-mcp v1.8.0.
    assemble_task_context.py  # assemble_task_context: task-aware single-call context orchestrator. Auto-classifies the task into one of six intents (explore/debug/refactor/extend/audit/review) via keyword scoring, auto-extracts anchor symbol names from the task, runs the intent-appropriate sub-tool sequence (digest + hotspots + tectonic for explore; anchor + callers + callees + blast + runtime for debug; anchor + rename_safe + delete_safe + implementations + similar for refactor; anchor + implementations + similar + decorators for extend; anchor + risk + blast + dead_code + untested for audit; changed + blast + risk + similar_changed for review), packs results into a single source-attributed capsule under token_budget. Each entry tagged with stage + source_tool. Intent classification is explainable (returns intent_keywords_matched + intent_confidence). Caller can override intent and include to force specific stages.
    get_tectonic_map.py       # get_tectonic_map: logical module topology via 3-signal fusion (structural+behavioral+temporal) + label propagation
    get_signal_chains.py      # get_signal_chains: entry-point-to-leaf pathway discovery; traces how HTTP/CLI/task/event signals propagate through the call graph; discovery + lookup modes. v1.108.58: include_flow_edges param consumes flow_edges.py — string-dispatched handlers become http gateways, rendered templates attach as a per-chain `views` list
    get_endpoint_impact.py    # (v1.108.90) Endpoint-centric impact: "what breaks if I change GET /users?" _collect_endpoints unifies flow_edges route edges (string-dispatch) + get_signal_chains decorator gateways (Flask/FastAPI/Spring local path) into one endpoint table; _match_endpoints (verb+path exact→suffix); _impact_for_handler fuses get_blast_radius (importers+callers) + render→view edges. Read-only, standard tier. handler_symbol_id bypasses URL resolution for prefixed routes. First slice of the framework-routes design; FastAPI prefix / Spring class-mapping composition is the follow-on. ⚠ The PRD this used to cite (`docs/prd-framework-routes-endpoint-impact.md`) **has never existed** — not on disk, not in git history. A citation to a document nobody can open is worse than none, because it sends a reader hunting; the design intent above is the part that was real
    flow_edges.py             # (v1.108.58) Language-agnostic framework flow-edge resolver. resolve_flow_edges(index, store, owner, name, kinds=("route","render")) emits typed edges the AST call graph misses: route→handler (Django path/re_path/url, Express/Fastify/Koa .get(p,h), Flask add_url_rule view_func=, Rails to:"ctrl#action") resolved to symbols via the import graph; render→view (render/render_template/res.render/view string templates) resolved to the template file when indexed. Shape-keyed (one resolver, not per-framework plugins); reuses _ContentCache/_symbol_body/build_symbols_by_file/resolve_specifier. Pure read path, no reindex. Decorator-bound handlers NOT re-emitted (they already surface as gateways)
    render_diagram.py         # render_diagram: universal Mermaid renderer; auto-detects source tool, picks optimal diagram type (flowchart/sequence), encodes metadata as visual signals; 3 themes, smart pruning; optional `open_in_viewer` (config-gated, spawns mmd-viewer)
    mermaid_viewer.py         # mmd-viewer spawn helper for render_diagram; resolve_viewer_path/open_diagram/cleanup_temp_dir; jcm- prefix for safe cleanup; config-gated via render_diagram_viewer_enabled + mermaid_viewer_path
    get_project_intel.py      # get_project_intel: auto-discover+parse non-code knowledge (Dockerfiles, CI configs, compose, K8s, .env templates, Makefiles, scripts); cross-references to code symbols; 6 categories. v1.108.0 adds `scope_path` arg to restrict discovery to a monorepo subpath (use list_workspaces.path values); validates against source_root (traversal/absolute/non-existent all error).
    list_workspaces.py        # (v1.108.0) Enumerate monorepo workspace members. Detects pnpm (pnpm-workspace.yaml), yarn/npm (package.json `workspaces:`), turborepo (turbo.json), lerna (lerna.json), rush (rush.json), Go (go.work `use (...)`, module name from go.mod), Cargo (Cargo.toml `[workspace] members`). Returns `[{path, package_name, manager}, ...]` plus `is_monorepo` + `managers`. Read-only, dependency-free (hand-rolled minimal TOML/YAML readers).
    get_repo_health.py        # get_repo_health: one-call triage snapshot (delegate aggregator); includes six-axis `radar` field (v1.87.0) ⚠⚠ **`_count_unstable_modules` excludes framework entry points from BOTH sides of the ratio (#561)** -- the rule it already applied to tests, whose own comment says they have "Ca=0 by construction". Numerator-only would shrink a count without shrinking what it is a fraction of: **the 84.0 B -> 88.8 B sign error of 1.108.305.** ⚠ So an entry point with a real `Ce` problem is graded by NOTHING; `coupling_entry_points_excluded` + `coupling_framework_profile` disclose it. ⚠ Only the DETECTED profile excludes -- widening to `_ENTRY_POINT_FILENAMES` moves every Python repo's published score on a heuristic, and needs its own measurement. ⚠⚠ **A REFUSAL IS NOT A ZERO**: `get_dead_code_v2` returning `[]` WITH a `signal_warning` became `dead_code_pct: 0.0` and a dead_code axis of 100 -- the strongest claim assembled from an admission that nothing was established. `dead_code_measurable` feeds `unmeasurable_axes`, which withholds composite and grade.
    _entry_points.py          # (#561/#562) `entry_point_spec(index)` -- reads the framework profile `detect_framework` persists into `context_metadata`. ⚠⚠ **That key was WRITTEN in one place and READ IN NONE for its whole life**, so three tools each reproduced their own Python-only answer to "is this a root?" and a Next.js repo detected ZERO entry points -- v2 returned `dead_symbols: []`, and 203 of 366 "unstable" files were `route.ts` handlers whose Ca is 0 BY CONSTRUCTION. ⚠⚠ **Flask/FastAPI shipped `"*.py"` there**, which under fnmatch declares the whole tree; catch-alls are removed at the source AND refused by `_is_catch_all`, gated by a test over every profile. Directory SCOPE saves a pattern (`routes/*.php` is fine, `**/*.php` is not). ⚠ Three dialects, all shipped: glob, bare filename (ROOT-LEVEL only -- `main.py` must not claim `src/vendor/main.py`), and directory prefix (`cmd/`, which fnmatch never matches). ⚠⚠ **`matches()` False is NOT "an ordinary module"** -- `profile_name is None` is the tell for no-declaration-available. [[grep-a-persisted-field-for-its-readers]]
    _git_history.py           # (#shallow) `history_coverage(cwd, days)` -- does the history REACH BACK past the window a churn tool is about to read? ⚠⚠ **Nine tools run `git log --since=N days` and none could tell a TRUNCATED history from a QUIET one**; git answers exit 0 with a short log, so `churn_surface` ranked nothing but complexity and the grade came out FLATTERING. ⚠⚠ **Fixed twice in the CLONERS (Practice 6, the observatory) and never in a READER** -- `actions/checkout` defaults to `fetch-depth: 1`, so every user kept it. ⚠ Asks COVERAGE, not shallowness: `--is-shallow-repository` is the mechanism, "reaches past the window" is the property -- a `--depth=900` clone at 90 days is shallow AND complete, and flagging it would teach people to ignore the flag. A young repo is not a truncated one. ⚠ TRI-STATE (`complete: None` = could not establish, never False); `churn_is_measurable()` collapses None to do-not-publish at the grade gate. ⚠ `attach_history_coverage` is SILENT on a covered window by design, and discloses an UNKNOWN
    health_radar.py           # Six-axis health radar (complexity/dead_code/cycles/coupling/test_gap/churn_surface) + diff_health_radar pure-function tool for PR-time diff-grade reporting (v1.87.0). Phase 7 (v1.100.0): optional 7th axis runtime_coverage when caller passes runtime_coverage_pct; axis is omitted otherwise so the composite stays comparable against pre-Phase-7 baselines. diff_radar walks the axes dict generically — picks up the new axis automatically.
    get_untested_symbols.py   # get_untested_symbols: find functions with no test-file reachability (import graph + name matching) ⚠⚠ **`untested_count`/`reached_pct` are measured BEFORE the `max_results` cut (#559)**; the page length is `returned_count`. The count used to be `len(symbols)` POST-slice and `get_repo_health` asks for `max_results=1`, so the published test axis read ~100% reach on every repo with untested code (4,893 of 6,352 published as 100). ⚠ **The response key is `symbols`** -- three consumers invented `untested_symbols`/`untested`/`results` and fell through to `[]` in silence. [[a-mock-can-supply-a-contract-the-producer-lacks]]
    search_ast.py             # search_ast: cross-language AST pattern matching; 10 preset anti-patterns + custom mini-DSL (call:, string:, comment:, nesting:, loops:, lines:); enriched with symbol context
    winnow_symbols.py         # winnow_symbols: multi-axis constraint-chain query; AND-intersects kind/language/name/file/complexity/decorator/calls/summary/churn in one round trip; ranks by importance/complexity/churn/name
    audit_agent_config.py    # audit_agent_config: token waste audit for CLAUDE.md, .cursorrules, etc.; cross-refs against index. Reused by suggest_corrections (_discover_files / _fuzzy_suggest / stale-config findings). Skill-candidate advisory (_check_skill_candidates / _split_sections / _best_subtree): flags always-resident H2 sections whose index-resolved refs concentrate in ONE subtree, gated by `skill_advisor_mode` (default off). ⚠ The signal is CONCENTRATION, not size — it returns [] with no index, and `subtreeShareCap` (0.25) not `concentrationFloor` is the discriminator, because a narrow subtree failing the floor hands selection to its permissive parent. ⚠ Findings state relevance was NOT measured; nothing records which section a turn needed
    suggest_corrections.py   # (v1.108.68) Retrieval-regret synthesis: fuses regret.analyze_regret clusters + audit_agent_config + WeightTuner dry-run into SUGGESTED corrections (routing/vocabulary/index-freshness/stale-config/skill-candidate) with difflib unified-diff CLAUDE.md previews. Read-only charter — never writes a user file; apply_weights touches only tuning.jsonc. Honest no-telemetry hint. ⚠ v1.108.290 passes `inflation` through EVEN WHEN UNMEASURABLE — a caller who cannot see WHY the ratio is absent reads its absence as zero inflation (#500: a number computed and discarded is the same defect as not computing it). ⚠ `_stale_config_corrections` read `f["type"]` while audit findings carry `category`, so stale_config had NEVER emitted; both spellings accepted now. ⚠ skill_candidate keeps `suggested_patch: None` deliberately — a diff showing only the deletion reads as "delete this section"
    analyze_perf.py          # analyze_perf: per-tool latency telemetry (p50/p95/max/error_rate) + cache hit-rate; reads in-memory session ring or persistent telemetry.db (opt-in via perf_telemetry_enabled); compare_release="X" loads benchmarks/token_baselines/vX.json and adds baseline_diff. ⚠⚠ **`hit_rate` is RAW key-presence and is stamped `hit_rate_basis: "raw_key_presence"`** — a hit is presence in the 256-entry session LRU, i.e. how often the cache ANSWERED, never whether the answer still described the index. arXiv:2608.20280 measured raw 51-60% falling to **1.1-2.2%** once validity was checked; we published the bare number. ⚠ The raw rate is KEPT (it answers a real question) and can no longer be read alone: `hits_validated_fresh`/`hits_validated_stale`/`hits_unvalidated`/`hit_rate_revalidated`/`validated_share` sit beside it. ⚠⚠ **THREE buckets, and `hit_rate_revalidated` is `None` not `0.0` when nothing was validated** — of the three result-cache consumers ONLY `search_symbols` revalidates (via `subject_state`, the #377-item-3 path), so `hits_unvalidated` is non-empty BY CONSTRUCTION and folding it anywhere invents data. Same UNKNOWN-is-not-False rule as `ledger_trust`. ⚠ Invalidation is PROCESS-LOCAL (5 sites, index-mutating tools only), so the PostToolUse `index-file` spawn, the watcher, `refresh` and a second server instance all move the index without the cache hearing it
  runtime/
    __init__.py          # Trace ingestion package (Phases 0-5): re-exports redact_trace_record, resolve_to_symbol_id, parse_otel_file, ingest_otel_file, OtelSpan, parse_sql_log_file, ingest_sql_log_file, SqlQueryRecord, parse_stack_log_file, ingest_stack_log_file, StackEvent, StackFrame, VALID_SOURCES = {'otel','sql_log','stack_log','apm'}
    redact.py            # Single chokepoint redact_trace_record(record, source) — strips emails, IPv4, SQL literals/numerics, JSON value blocks, Python locals reprs, plus all secret patterns from ../redact.py
    resolve.py           # resolve_to_symbol_id(conn, file, line, name) — best-effort (file, line, function) → symbol_id with suffix-match fallback for absolute trace paths against repo-relative index paths
    otel.py              # Phase 1 OTel JSON parser — handles JSON-Lines, single-document JSON, top-level array, and .gz transparently; extracts code.filepath / code.lineno / code.function / duration into OtelSpan
    ingest.py            # Phase 1 orchestrator ingest_otel_file(db_path, file_path, redact_enabled, max_rows) — parse → redact → resolve → upsert; computes per-batch p50/p95 from span durations; FIFO-evicts runtime_calls + runtime_unmapped down to max_rows when exceeded; persists per-pattern redaction counts to runtime_redaction_log
    sql_log.py           # Phase 4 SQL log parser — pg_stat_statements CSV (header autodetect; total_time/total_exec_time + mean_time/mean_exec_time aliases) + generic JSON-Lines (.jsonl/.json/.log) + top-level array fallback + .gz transparent; extracts table refs (FROM/JOIN/UPDATE/INSERT INTO/DELETE FROM/MERGE INTO; schema-qualified names → trailing ident) and column refs (qualified alias.col + bare idents in SELECT/WHERE/ON/HAVING/GROUP BY/ORDER BY)
    sql_ingest.py        # Phase 4 orchestrator ingest_sql_log_file(db_path, file_path, redact_enabled, max_rows) — parse → redact → resolve → upsert; resolver builds a one-shot read-only metadata snapshot (file-stem map, exact-name map, dbt_columns/sqlmesh_columns set); upserts runtime_calls + runtime_columns + runtime_unmapped + runtime_redaction_log under source='sql_log'; FIFO-evicts all three runtime tables
    stack_log.py         # Phase 5 stack-frame parser — Python tracebacks (`File "...", line N, in <name>` pairs), JVM tracebacks (`at pkg.Class.method(File.java:N)` + flattened `Caused by:` chains), Node.js stacks (named `at funcName (file.js:N:N)` + anonymous `at file.js:N:N` + node:events-style module paths). Plain-text + JSON-Lines structured-log + top-level array + .gz. Severity heuristic: looks 3 lines back for FATAL/CRITICAL/ERROR/WARN[ING]/INFO; default 'info'.
    stack_ingest.py      # Phase 5 orchestrator ingest_stack_log_file(db_path, file_path, redact_enabled, max_rows) — parse → redact (event.message) → resolve each frame → upsert; populates BOTH runtime_calls (severity-agnostic rollup so confidence-stamping fires) AND runtime_stack_events (per-severity counts). FIFO-evicts runtime_calls + runtime_unmapped + runtime_stack_events. Phase 6 adds ingest_stack_log_stream() that takes an in-memory text payload via the shared _ingest_stack_iter() pipeline.
    http_routes.py       # Phase 6 Starlette route handlers: POST /runtime/otel, POST /runtime/sql, POST /runtime/stack. Off by default — gated by runtime_ingest_enabled config + JCODEMUNCH_HTTP_TOKEN bearer auth. Per-repo asyncio.Lock serialises writes against the same SQLite DB. Body cap (default 5 MB) checked separately for on-wire and decompressed sizes (gzip-bomb guard). Repo selection via X-JCM-Repo header or ?repo= query. Mounted on both SSE and streamable-http transports.
    confidence.py        # Phase 2 RuntimeConfidenceProbe + attach_runtime_confidence (symbol-keyed) + attach_runtime_confidence_by_file (file-keyed). Stamps `_runtime_confidence` ∈ {confirmed, declared_only, unmapped} on result entries; emits `_meta.runtime_freshness` summary. Read-only connections use ?mode=ro&immutable=1 so they never bump WAL mtime and invalidate the CodeIndex LRU cache. Zero-cost when runtime_calls is empty.
  evidence/
    receipts.py          # (v1.108.183) #377 Phase 2 P1: the `jcodemunch.evidence/v1` envelope + session store. evidence_id() hashes EXACTLY (subject, effective_search, snapshot) — full sha256, never 12 hex; build_envelope/record_receipt (fail-closed on id reuse over differing content: an id that ever named two receipts names NEITHER after); lookup() returns (envelope, reason) with reason naming never_recorded/evicted/collision; PROOF_KINDS holds the jdoc/jdata halves too so parity attaches to ONE enum; coverage_fingerprint() is the OPAQUE Phase-5 (#385) extension point; envelope_json() is deterministic so repeated resource reads are byte-identical; _absence_links maps a Phase-3 `absent:` token to its receipt. Session-scoped, in memory, bounded at 500 + an evicted set
    producers.py         # (v1.108.183) #377 Phase 2 P2 — THE GATE. PRODUCERS registry (4 entries: get_symbol_source symbol_definition only / search_symbols + get_ranked_context symbol_definition+symbol_lookup_absence / search_text literal_text_absence only), each declaring verdict shape, proof kinds, canonical projector arg sets (scope_args NARROW, mode_args change WHICH operation ran), and completeness/freshness/coverage/integrity semantics. mint() is called from the call_tool chokepoint, so it is immune to early returns BY CONSTRUCTION; `_verdict_shape` is the gate — an exit that asserts an answer without the registered build_verdict shape cannot mint (the v1.108.179 class made structural). `_snapshot(trust_channel=)` binds subject_state.capture + repo_freshness + index_coverage_meta + verdict.working_tree; trust_channel=False for the symbol-verdict shape because ITS channels.index says `fresh` for a revisionless folder. `_row_subject` reads the SERVED row only and names what was not served in `limitations`
    scip.py              # (v1.108.96) Hand-rolled SCIP protobuf wire-format reader (no protobuf dep): _read_varint/_iter_fields walk varint + length-delimited fields, unknown fields skipped by construction. Parses Index/Metadata/Document/Occurrence/SymbolInformation/Relationship subset; packed AND unpacked int32 ranges, 3-/4-int range forms, .gz by magic sniff; ValueError (honest) on non-SCIP input. display_name_from_symbol = best-effort last-descriptor name (resolution FALLBACK only; primary channel is (file,line))
    scip_ingest.py       # (v1.108.96) ingest_scip_file: parse → resolve (definition map scip-symbol→(file,line) from Definition-role occurrences; enclosing symbol via runtime/resolve.resolve_to_symbol_id) → persist scip_edges (kinds: reference, implementation) / scip_unmapped (reasoned) / scip_meta (tool, ingested_at, git_head staleness anchor). Skips counted: Import-role occurrences (import graph covers) + `local N` symbols. _ensure_scip_tables covers pre-v17 DBs; FIFO eviction per JCODEMUNCH_SCIP_MAX_ROWS
  tools/
    get_runtime_coverage.py  # Phase 3: coverage histogram for repo or single file. {total_symbols, confirmed, declared_only, coverage_pct, sources, last_seen, unmapped_runtime[]}.
    find_hot_paths.py        # Phase 3: top-N symbols by runtime hit count, with p50/p95, sources, last_seen. Optional name substring filter. Pairs with get_blast_radius.
    find_unused_paths.py     # Phase 3 + 4: symbols with zero/stale runtime hits over the window. Excludes test files and entry-point filenames by default. Refuses when runtime_calls is empty (would trivially flag everything). Phase 4 dbt-aware extension: when context_metadata has *_columns + runtime_columns has rows, rescues SQL-file model symbols that have observed column reads (column-only audit-log shape) and surfaces dbt models whose declared columns have zero hits with reason='dbt_model_no_column_reads' + unused_columns list.
    get_redaction_log.py     # Phase 6: forensic accounting of PII redactions — surfaces per-pattern counts from runtime_redaction_log so operators can verify the redaction chokepoint is firing on production traffic. Filters by source + since_days. Read-only / immutable connection.
  retrieval/
    scoring.py         # (cycles refactor) BM25 constants, tokenizer, stemmer, `_ABBREV_MAP`, `_identity_score`, `_cosine_similarity`. ⚠⚠ Extracted from `tools/search_symbols.py` to break a REAL cycle with `signal_fusion.py` — retrieval primitives that happened to be written inside the first tool needing them. Imports NEITHER; both import it. ⚠ `search_symbols` re-exports all 14 names (~30 call sites) — same monkeypatch trap as `cli/policy.py`, patch HERE
    confidence.py        # compute_confidence/attach_confidence: 0-1 retrieval confidence score (geometric mean of gap, strength, identity, freshness sub-signals); attached to _meta.confidence on search_symbols / plan_turn / get_ranked_context
    freshness.py         # FreshnessProbe: v1.108.180 adds repo_freshness (fresh/stale/unknown/not_tracked, #377 item 4 — the boolean repo_is_stale rendered 'could not find out' as fresh) + _is_git_backed (walks up, so a monorepo subdir is not mislabeled not_tracked). per-result _freshness classification (fresh / edited_uncommitted / stale_index / **unknown, v1.108.209**); compares index SHA vs git HEAD + per-file mtime vs CodeIndex.file_mtimes; wired into search_symbols / get_symbol_source / get_context_bundle / get_ranked_context. ⚠ **classify() must NEVER answer `fresh` for a comparison it could not make** — no source root, moved root, file absent from the tree, stat raised, or no baseline (neither per-file mtime nor parseable indexed_at) all return `unknown`. That was .209's whole fix and it is easy to reintroduce, because the unmeasurable paths are the ones no local dev box ever exercises. summary() carries an `unknown` count and its buckets must sum to the entry count
    tuning.py            # WeightTuner + get_semantic_weight: learns per-repo semantic_weight from v1.78.0 ranking_events ledger; ±0.05 step (clamp 0.1-0.8) when mean confidence between semantic_used groups differs by ≥0.05; persists to ~/.code-index/tuning.jsonc; applied at query time when caller leaves semantic_weight at the default (identity_boost learning removed v1.108.102 — audit W6, was never consumed at query time)
    embed_drift.py       # CANARY_STRINGS (16) + capture_canary/check_drift: pins canary embeddings to ~/.code-index/embed_canary.json, re-checks cosine drift via check_embedding_drift MCP tool; catches silent provider model changes (Gemini/OpenAI/bundled-ONNX); default threshold 0.05 cosine distance
```

## CLI Subcommands
| Subcommand | Purpose |
|------------|---------|
| `serve` (default) | Run the MCP server (`stdio`, `sse`, or `streamable-http`) |
| `init` | Interactive one-command onboarding: detect MCP clients, write config, install CLAUDE.md policy, hooks, index |
| `install <agent>` | (v1.105.1) Per-agent shortcut over `init`; targets: `claude-code`, `claude-desktop`, `cursor`, `windsurf`, `continue`, `all`. `install --list` enumerates; `install --status` reports state (JSON via `--json`). **v1.107.0:** `--skills` also emits the Claude Agent Skill bundle (`~/.claude/skills/jcodemunch/SKILL.md` by default; `--skills-scope project` for project-local) |
| `install-status` | (v1.105.1) Read-only report of which clients / policies / hooks currently have jcodemunch wired; `--json` for scripting. **v1.107.0:** also reports `skills.global.present` and `skills.project.present` |
| `uninstall [target]` | (v1.105.1) Reverse `init` / `install`. Preserves user-authored hook rules and content outside our policy region; removes files only when empty after stripping. `--keep-claude-md`, `--keep-hooks`, etc. scope what's reversed |
| `watch <paths>` | File watcher — auto-reindex on change |
| `watch-claude` | Auto-discover and watch Claude Code worktrees |
| `watch-all` | Auto-discover **every** locally-indexed repo and keep it fresh; rediscovers on interval |
| `watch-install` | Install `watch-all` as a login service (systemd / launchd / Task Scheduler) |
| `watch-uninstall` | Remove the installed `watch-all` login service |
| `watch-status` | Print service state + per-repo reindex status (also exposed as MCP tool `get_watch_status`) |
| `hook-event create\|remove` | Record a worktree lifecycle event (called by Claude Code hooks) |
| `index [target]` | Index a local folder (default: `.`) or GitHub repo (`owner/repo`). One command, no init required |
| `index-file <path>` | Re-index a single file within an existing indexed folder (used by PostToolUse hooks) |
| `refresh [path]` | (v1.108.259, #395) Re-parse an INDEXED repo in bounded, resumable slices — `--max-seconds` / `--max-files` / `--pause-ms` / `--batch-size` / `--status` / `--reset` / `--ai-summaries` / `--json`. For fleets where a full re-index is a scheduled maintenance event. ⚠ Does NOT build a first index; refuses with the command that does. ⚠ Stamps `parser_generation` only after VERIFIED full-corpus coverage |
| `import-trace [--otel <path> \| --sql-log <path> \| --stack-log <path>] [--repo <id>] [--no-redact]` | (Phases 1 + 4 + 5) Ingest a runtime trace file into the runtime_* tables. `--otel` takes JSON / JSON-Lines / .gz and maps spans by `(code.filepath, code.lineno, code.function)`; `--sql-log` takes pg_stat_statements CSV or generic SQL JSON-Lines and maps queries by referenced tables + dbt/SQLMesh column metadata; `--stack-log` takes plain-text app log or JSON-Lines record set with Python / JVM / Node.js tracebacks and writes severity-tagged frame counts to runtime_stack_events. Redacts PII at the chokepoint by default. Pass exactly one source flag. |
| `import-scip <path.scip> [--repo <id>]` | (v1.108.96) Ingest a SCIP index file (compiler-verified cross-references from scip-typescript / scip-python / scip-java / scip-go / rust-analyzer; .gz accepted) into the scip_* tables. Hand-rolled protobuf reader, no deps. `find_references` then tags `compiler_verified` refs + appends compiler-only refs. Cap via `JCODEMUNCH_SCIP_MAX_ROWS`. |
| `config` | Print effective configuration grouped by concern |
| `config set <key> <value>` / `config unset <key>` | (v1.108.51) Write/clear a config key in the global config.jsonc (typed, comment-preserving, validated; `--json` for tooling) |
| `config --check` | Also validate prerequisites (storage writable, AI pkg installed, HTTP pkgs present) |
| `config --upgrade` | Add missing keys from current template to existing config.jsonc, preserving user values |
| `download-model` | Download bundled ONNX embedding model (all-MiniLM-L6-v2) for zero-config semantic search; `--target-dir` override |
| `install-pack [id]` | Download and install a Starter Pack pre-built index; `--list` for catalog, `--license KEY` for premium |
| `hook-pretooluse` | PreToolUse hook: steer Read/Grep/Glob/leading-Bash-search toward jCodemunch inside indexed repos (reads JSON stdin) |
| `hook-posttooluse` | PostToolUse hook: auto-reindex files after Edit/Write (reads JSON stdin) |
| `hook-precompact` | PreCompact hook: register transcript root before compaction (reads JSON stdin; snapshot delivery is `hook-sessionstart`) |
| `hook-taskcomplete` | TaskCompleted hook: post-task diagnostics — dead code, untested symbols, dangling refs (reads JSON stdin) |
| `hook-subagent-start` | SubagentStart hook: inject condensed repo orientation for spawned agents (reads JSON stdin) |
| `hook-sessionstart` | (v1.108.255, #420) SessionStart hook: re-inject the PreCompact snapshot into MODEL context on `compact`/`resume`/`fork`. Silent on `startup`/`clear`, because an unrelated session's journal presents stale files as current focus. Also the earliest point a custom-profile transcript root can be learned (#421), so registration runs BEFORE the source gate |
| `whatsnew` | Refresh README recency block + write `whatsnew.json` from `CHANGELOG.md` (release flow) |
| `receipt` | Token-economy ledger from Claude transcripts — modeled tokens-saved + dollar value at Fable/Opus/Sonnet/Haiku rates; `--explain`, `--export csv\|json`, `--days` (rolling), `--model`. v1.108.134: `--since`/`--until` for calendar windows (local dates; `--until` exclusive) + `--by-day` for a per-day series in the JSON export. v1.108.135: `--rates` dumps the model price table as JSON (scans nothing) so consumers price from the one table instead of a drifting copy |
| `digest` | Agent stand-up briefing — composes since-last-session delta + risk surface + dead-code candidates; tracks per-repo last-seen SHA at `~/.code-index/digest_state/`; also exposed as MCP tool `digest`. v1.108.68 adds a one-line retrieval-regret summary when the ledger has clusters |
| `reflect` | (v1.108.68) Surface retrieval regret as SUGGESTED config corrections — `reflect [repo] [--project-path] [--window-days N] [--all] [--apply-weights] [--json]`. Thin CLI over the `suggest_corrections` tool; read-only (only `--apply-weights` writes, and only the tuning.jsonc sidecar) |
| `delivery` | (v1.108.69) Print durable-change delivery metrics for a window — `delivery [repo] [--window-days N] [--rework-horizon-days N] [--cost DOLLARS] [--json]`. Thin CLI over `get_delivery_metrics`; `--cost` prints the headline cost-per-durable-change (how much got done for how little). Read-only git archaeology |
| `parity` | (v1.108.111) Map migration parity between two symbol trees — `parity <source> <target> [--source-path P] [--target-path P] [--match-threshold F] [--divergence signature\|signature+body\|name_only] [--no-rename] [--no-port-plan] [--json]`. Thin CLI over `get_parity_map`: ported/diverged/unported/orphaned/added counts + dependency-ordered port plan. Read-only/plan-only |
| `health` | Print `get_repo_health` JSON to stdout (includes six-axis radar). For CI/scripting; `--radar-only` for just the radar sub-field. Used by the v1.88.0 health-radar GitHub Action |
| `file-risk` | Print per-symbol risk JSON for a file (composite score + four-axis breakdown). Used by the v0.2.0 VS Code risk-density gutter |
| `observatory build\|init` | Public OSS code-health observatory pipeline — clones, indexes, scores a configured repo list; writes static HTML + RSS + JSON to an output dir. v1.90.0; CI repo-id bug fixed in v1.90.1. Live at https://jgravelle.github.io/jcodemunch-observatory/ |
| `org-report` / `org-rollup` | (v1.108.38/39) Team SKU: record this seat's savings under its org / aggregate across seats. `org-rollup` is the licensed feature (v1.108.42 gate). |
| `license` | (v1.108.42) Check jCodeMunch license status — `license [--key KEY] [--json]`; reports licensed / evaluation / unlicensed, tier, trial days left. Gates `org-rollup` only. |
| `surface` | (v1.108.154) Print the tool-surface schema receipt (same block `get_session_stats` reports as `tool_surface`) — surface/profile, visible vs catalog counts, schema tokens, avoided, heaviest schemas. `--json` for tooling (the Console's Tool surface cost card shells it). Scans nothing. |

## Architecture Notes
- `index_folder` is **synchronous** — dispatched via `asyncio.to_thread()` in server.py to avoid blocking the event loop
- `index_repo` is **async** (uses httpx for GitHub API)
- `has_index()` distinguishes "no file on disk" from "file exists but version rejected"
- Symbol lookup is O(1) via `__post_init__` id dict in `CodeIndex`

## Custom Parsers
Tree-sitter grammar lacks clean named fields for these — custom regex extractors:
- **Erlang**: multi-clause function merging by (name, arity); arity-qualified names (e.g. `add/2`)
- **Fortran**: module-as-container, qualified names (`math_utils::multiply`), parameter constants
- **SQL**: `_parse_sql_symbols` + `sql_preprocessor.py` strips Jinja (dbt); macro/test/snapshot/materialization as symbols
- **Razor/Blazor** (.cshtml/.razor): `@functions/@code` → C#, `@page`/`@inject` → constants, HTML ids

## Env Vars
| Var | Default | Purpose |
|-----|---------|---------|
| `CODE_INDEX_PATH` | `~/.code-index/` | Index storage location |
| `JCODEMUNCH_MAX_INDEX_FILES` | 10,000 | File cap for repo indexing |
| `JCODEMUNCH_MAX_FOLDER_FILES` | 2,000 | File cap for folder indexing |
| `JCODEMUNCH_FILE_TREE_MAX_FILES` | 500 | Cap for get_file_tree results |
| `JCODEMUNCH_GITIGNORE_WARN_THRESHOLD` | 500 | Missing-.gitignore warning threshold (0 = disable) |
| `JCODEMUNCH_USE_AI_SUMMARIES` | auto | AI summarization mode: `auto` (detect provider), `true` (use explicit config), `false`/`0`/`no`/`off` (disable) |
| `JCODEMUNCH_SUMMARIZER_PROVIDER` | — | Explicit summarizer provider: `anthropic`, `gemini`, `openai`, `minimax`, `glm`, `openrouter`, `none` |
| `JCODEMUNCH_SUMMARIZER_MODEL` | — | Model name override for the selected summarizer provider |
| `JCODEMUNCH_TRUSTED_FOLDERS` | — | Roots trusted for index_folder; whitelist mode by default |
| `JCODEMUNCH_EXTRA_IGNORE_PATTERNS` | — | Always-on gitignore patterns (comma-sep or JSON array) |
| `JCODEMUNCH_PATH_MAP` | — | Cross-platform path remapping; format: `orig1=new1,orig2=new2` |
| `JCODEMUNCH_STALENESS_DAYS` | 7 | Days before get_repo_outline emits a staleness_warning |
| `JCODEMUNCH_MAX_RESULTS` | 500 | Hard cap on search_columns result count |
| `JCODEMUNCH_HTTP_TOKEN` | — | Bearer token for HTTP transport auth (opt-in) |
| `JCODEMUNCH_RATE_LIMIT` | 0 | Max requests/minute per client IP in HTTP transport (0 = disabled) |
| `JCODEMUNCH_REDACT_SOURCE_ROOT` | 0 | Set 1 to replace source_root with display_name in responses |
| `JCODEMUNCH_SHARE_SAVINGS` | 1 | Set 0 to disable anonymous token savings telemetry |
| `JCODEMUNCH_REDACT_RESPONSE_SECRETS` | 1 | Set 0 to disable response-level secret redaction (AWS/GCP/Azure/JWT/etc.) |
| `JCODEMUNCH_STATS_FILE_INTERVAL` | 3 | Calls between session_stats.json writes; 0 = disable |
| `JCODEMUNCH_PERF_TELEMETRY` | 0 | Set 1 to enable persistent perf SQLite sink at ~/.code-index/telemetry.db (per-tool latency + ok flag + repo). In-memory ring is always tracked; the env var only controls durable persistence. |
| `JCODEMUNCH_PERF_TELEMETRY_MAX_ROWS` | 100000 | Rolling cap on persisted perf rows; oldest rows trimmed in 1k-row batches once exceeded. |
| `JCODEMUNCH_RUNTIME_MAX_ROWS` | 100000 | (Phase 0) Per-repo cap on rows in runtime_* tables (ingested in Phase 1+); FIFO eviction in 1k batches once exceeded. |
| `JCODEMUNCH_RUNTIME_REDACT` | 1 | (Phase 0) Set 0 to disable PII redaction at the runtime trace ingest chokepoint. Off ONLY for offline debugging on synthetic data — never on production traces. |
| `JCODEMUNCH_RUNTIME_INGEST_ENABLED` | 0 | (Phase 6) Set 1 to enable the HTTP live-ingest endpoints (POST /runtime/otel, /runtime/sql, /runtime/stack). Requires JCODEMUNCH_HTTP_TOKEN. Off by default — write endpoints are a deliberate two-key turn. |
| `JCODEMUNCH_RUNTIME_INGEST_MAX_BODY_BYTES` | 5242880 | (Phase 6) Per-request body cap in bytes (post-decompression). Decompressed size is checked separately from on-wire size — gzip-bomb guard. Minimum 1024. |
| `JCODEMUNCH_CLIENT_ID` | basename(`sys.argv[0]`) | (v1.106.0) Friendly client name recorded in `process_locks` metadata. Auto-detected for common runtimes (claude, cursor, codex). Override for custom or wrapper runtimes so `get_watch_status.watcher_holder.client_id` surfaces a meaningful name to other processes. |
| `ANTHROPIC_API_KEY` | — | Enables Claude Haiku summaries (`pip install "jcodemunch-mcp[anthropic]"`) |
| `GOOGLE_API_KEY` | — | Enables Gemini Flash summaries (`pip install "jcodemunch-mcp[gemini]"`) |
| `OPENAI_API_BASE` | — | Local LLM endpoint (Ollama, LM Studio) |
| `OPENAI_WIRE_API` | — | Set `responses` to use OpenAI Responses API instead of chat/completions |
| `JCODEMUNCH_OPENAI_EXTRA_BODY` | — | JSON object merged into every OpenAI-compatible `/chat/completions` + `/responses` summarizer request (config key `openai_extra_body`, project-overridable). Disable a thinking model's reasoning so the output budget isn't burned on reasoning tokens, e.g. `{"chat_template_kwargs":{"enable_thinking":false}}` (#323) |
| `OPENROUTER_API_KEY` | — | Enables OpenRouter summaries (default model: `meta-llama/llama-3.3-70b-instruct:free`) |
| `JCODEMUNCH_LOCAL_EMBED_MODEL` | — | Override path to bundled ONNX model directory (default: `~/.code-index/models/all-MiniLM-L6-v2/`) |
| `GEMINI_EMBED_TASK_AWARE` | 1 | Set `0`/`false`/`no`/`off` to disable task-type hints (`RETRIEVAL_DOCUMENT` / `CODE_RETRIEVAL_QUERY`) when using Gemini embeddings |
| `JCODEMUNCH_CROSS_REPO_DEFAULT` | 0 | Set 1 to enable cross-repo traversal by default in find_importers, get_blast_radius, get_dependency_graph |
| `JCODEMUNCH_EVENT_LOG` | — | Set `1` to write `_pulse.json` on every tool call (per-call activity signal for dashboards) |
| `JCODEMUNCH_WATCH_POLL_DELAY_MS` | 1000 | (v1.108.83) Poll interval (ms) used ONLY when watchfiles falls back to polling — which it auto-enables under WSL (#356). Default raised from watchfiles' 300ms to cut idle CPU; ignored when native FS events are in use. Falls back to `WATCHFILES_POLL_DELAY_MS` if set; non-positive/garbage → default. For Linux-filesystem repos under WSL, `WATCHFILES_FORCE_POLLING=false` opts back into inotify (~0 idle CPU). |
| `JCODEMUNCH_LIVE_JOURNAL` | 1 | (v1.108.57) Set `0`/`false`/`no`/`off` to disable the live session-journal write (`<CODE_INDEX_PATH>/_session_live.json`). On by default so the out-of-process PreCompact hook can read real session state (#334); throttled ≤1/~2s, paths+queries only, no file contents. |
| `JCODEMUNCH_TOOL_SURFACE` | `full` | (v1.108.66) Tool surface selector (config key `tool_surface`; env wins). `counter` collapses `list_tools` to the 3-tool front door (`order`/`menu`/`route`) + always-present controls. Any other value (default `full`) preserves existing tiered behavior byte-for-byte — front-door tools stay hidden but callable. Composes with the `core`/`standard`/`full` tier profiles. |
| `JCODEMUNCH_PARSE_CACHE` | — | Shared directory for the content-addressed parse cache (v1.108.40). Point all seats on a multi-home-dir box at the same path so identical files parse once across seats. Unset = disabled (no caching). |
| `JCODEMUNCH_PARSE_CACHE_MAX_ROWS` | 50000 | (v1.108.41) Row cap for the shared parse cache; FIFO-trimmed oldest-first by rowid after each write (stale-content/stale-version rows go first). `<= 0` disables the cap (unbounded). |
| `JCODEMUNCH_ORG_ID` | — | Org identifier for the team-SKU rollup (`org-report` / `org-rollup`) |
| `JCODEMUNCH_ORG_ENDPOINT` | — | Org host URL that `org-report` POSTs seat savings to (`/org/report`); unset = record locally |
| `JCODEMUNCH_ORG_INGEST_ENABLED` | 0 | Set 1 on the org host to accept `POST /org/report` (two-key turn with `JCODEMUNCH_HTTP_TOKEN`) |
| `JCODEMUNCH_LICENSE_KEY` | — | (v1.108.42) jCodeMunch license key (config key `license_key`). Gates the `org-rollup` team feature ONLY; everything else is free. Validated online vs `validate.php` (sticky-offline cache; 14-day grace for new orgs). **Requires a multi-seat tier — Studio or Platform** (v1.108.43); Builder doesn't unlock org-rollup. Check with the `license` CLI. |
| `JCODEMUNCH_INDEX_CACHE_TTL` | 0 (off) | (v1.108.172) Seconds an unused hydrated index may sit in the in-memory cache before being released. **OPT-IN: 0/unset/garbage = disabled = today's behavior exactly.** ⚠ **Do NOT default this on** — cold hydration of a 665k-symbol index was measured at 7.5-11.4 min (#370), so evicting during a quiet spell hands the next query that bill. For hosts whose MCP client leaks stdio servers (#375: 25+ instances, ~17 GB), where each idle process otherwise sits on its own cache. Swept on access, no timer thread. |
| `JCODEMUNCH_PROVIDER_BUDGET_SECONDS` | 30.0 | (v1.108.182) Wall-clock ceiling on ONE context provider's `detect()`+`load()`. Discovery runs before a single file is indexed, so an unbounded provider takes the whole index down with it (#375). On overrun the provider is skipped and NAMED in `providers_skipped` + `warnings`. `0`/negative = no ceiling (pre-.182 inline behaviour). ⚠ **A watchdog stops the CALLER waiting; it cannot stop the work** — Python cannot preempt a thread, so the abandoned provider keeps burning CPU until it finishes or polls `budget_expired()`. Only the Express walk polls it so far. |
| `JCODEMUNCH_PARSE_BUDGET_SECONDS` | 20.0 | (v1.108.182) Per-file wall-clock ceiling on `parse_file`, via `parse_file_budgeted`. On overrun the file is skipped and named in the index result's `warnings` instead of the run hanging. ⚠ **Armed only at or above 128 KiB** (`_PARSE_WATCHDOG_MIN_BYTES`) so the common path stays inline — a 2 KB file that takes 20s is a bug to see, not to paper over. `0`/negative disables. Same no-preemption caveat: tree-sitter is C code. |
| `JCODEMUNCH_MAX_FILE_SIZE` | 512000 | (v1.108.193, @dkiaulakis) Per-file byte cap for indexing (config key `max_file_size`; **settable per-project in `.jcodemunch.jsonc` as of v1.108.197 — before that the project file was parsed and then ignored**). ⚠ **This was the ONE limit of three with no route at all** — its neighbours `max_index_files`/`max_folder_files` each had a resolver, this was hardcoded. **Default deliberately UNCHANGED**; this is an escape hatch. ⚠ A file over the cap is `too_large`, which is now **WITHHELD** (real+current+wanted) rather than an ordinary exclusion, so it makes coverage `complete: false` and **refuses absence claims**. |
| `JCODEMUNCH_RESPECT_CACHEDIR_TAG` | 1 | (v1.108.270) Honour the Cache Directory Tagging Specification (<https://bford.info/cachedir/>): prune any directory holding a `CACHEDIR.TAG` whose **first 43 bytes** are the spec signature (config key `respect_cachedir_tag`). ⚠⚠ **The signature is VERIFIED — a file merely NAMED `CACHEDIR.TAG` excludes nothing.** A name-only check is an assertion about one instance of the property instead of the property, which is the exact defect class this answers. ⚠ The only exclusion rule here **declared by the WRITER** rather than listed by us, so a tool that drops a cache in your tree is honoured without jcm knowing its name, and it covers caches that are **not dotted** (which a dot-dir rule cannot). Counted as `cache_dir` in `discovery_skip_counts`; **NOT a withheld reason**, so absence stays citable — a tagged dir is derived data by its writer's own declaration, i.e. corpus definition like `gitignore`. Only an explicit `false` disables it. ⚠ Local walks only; `index_repo` is deliberately uncovered because validating the signature needs blob CONTENT the tree listing does not carry. |
| `JCODEMUNCH_RESPONSE_MAX_BYTES` | 1048576 | (v1.108.257, #425) Ceiling on a SINGLE MCP tool response in bytes, enforced in a wrapper AROUND the `call_tool` dispatcher (config key `response_max_bytes`). ⚠⚠ **This is a RESPONSE limit, deliberately NOT `max_file_size`** - before it existed, an INDEXING cap in another subsystem bounded reply size by coincidence, so raising that key to cover a large generated file silently raised the maximum reply. ⚠ Over the cap the call REFUSES with a structured error naming size, limit and the key that moves it; it never truncates, because a shortened body is indistinguishable from a complete one. `0` disables; any other invalid value falls back to the default so a typo cannot uncap the server. |
| `JCODEMUNCH_HEARTBEAT_SECONDS` | 30.0 | (v1.108.189, #383) Elapsed wall-clock seconds between heartbeat log lines when the client sent **no `progressToken`** — the MCP spec makes progress notifications the client's opt-in, so the fallback signal goes to the log instead. Emitted at **WARNING** (the default `log_level`, or nobody sees it) and **only after the first interval elapses**, so a run finishing inside the window is byte-for-byte as silent as before. ⚠ **Garbage parses to the DEFAULT, not to 0** — a typo must not reintroduce the silence this exists to fix. `0`/negative disables. |
| `JCODEMUNCH_EMBED_MATRIX_CACHE` | 1 | (v1.108.223, #399) Set `0`/`false`/`no`/`off` to stop RETAINING the decoded embedding matrix between queries. ⚠ **It does not disable the fast path** — the matrix is still built per call and scored in one vectorised pass, so only the SQLite decode is re-paid. On by default because the cache is what turns a ~2 s semantic query into ~3 ms; bounded to 2 repositories (~46 MB each at 30k x 384 float32) and dropped on every write to the store. Process memory only: nothing written, no network, dies with the process. Disclosed in README's "Background behavior". |
| `JCODEMUNCH_SCIP_MAX_ROWS` | 200000 | (v1.108.96) Row cap for `scip_edges` / `scip_unmapped` (compile-time evidence from `import-scip`); FIFO-evicted oldest-first in 1k batches. Negative disables the cap; env-only, deliberately not a config key. |
| `JCODEMUNCH_LAUNCH_ID` | — | (v1.108.152) Opaque host-supplied launch token echoed back as `launch_id` in the `munch://runtime/identity` resource (#371). Fallback: suite-generic `MUNCH_LAUNCH_ID`. Omitted from the payload when unset. Env-only, not a config key. |

## PR / Issue History
See `git log` and CHANGELOG.md. Active contributors: MariusAdrian88, DrHayt, tmeckel, drax1222, oderwat, thomasmodeneis, gokhanozdemir, horknfbr.

### Tool-description quality (`benchmarks/description_smells/`)

Descriptions are scored against the rubric in arXiv:2602.14878. Two rules when you
touch a tool description:

- **`core_compact` has a HARD ceiling of 4,000 tokens** (v2 §10). The drift ratchet
  in `tests/test_schema_budget.py` offers "or update the baseline"; the sibling
  ceiling tests forbid it. Trim the description instead. Currently 3,990, so a
  core-tier tool has roughly ten tokens of slack, not a sentence's worth.
- **`tests/test_description_smells.py` gates Purpose and Length.** A new tool with a
  one-line description fails it. Two substantive sentences minimum: what it does and
  returns, plus one boundary or usage cue.

⚠ The audit reports two frames. The paper's scanner never sees `inputSchema`, so
schema-documented parameters score 1/5 by its rubric. Quote both frames or neither.

### Rust fidelity (`benchmarks/rust_fidelity/`)

Rust extraction vs **Rust's own parser** (`syn`). Four buckets gate at **0**:
`extra`, `wrong_span`, `undercount`, `qual_mismatch`; `missing` is reported by
kind. ripgrep @ `3fce3b5b`, 110 files: **95.8%**, 3,517 symbols, `missing` (156)
entirely `module`+`macro`, both deliberate.

⚠⚠ **CEILING LOWER THAN RACKET'S: `syn` PARSES, it does not EXPAND.** A
`macro_rules!`-generated item is invisible to the oracle AND to us, unscored in
BOTH directions — a green run is NOT evidence about macro-generated code.

⚠⚠ **THE FIRST THREE BUCKETS KEYED BARE NAMES IN A SET, AND A SET CANNOT
COUNT.** Proven by deleting the second symbol of every duplicated name in the
fixtures: `extra` and `missing` did not move, so a run extracting ONE of
`defs.rs`'s 108 `is_switch` graded like a complete one. It was hiding a **37.9%
in-file name-collision rate** (1,331/3,514, 44 of 110 files). `undercount`
counts qualified names; `qual_mismatch` compares owners. **The owner is
`self_ty`, never the trait.**

⚠⚠ **FOUR oracle traps, every one makes US look wrong when the HARNESS is.**
(1) Read the **identifier's** span, not the item's — `Item::span()` starts at the
first doc comment, scoring us **40.4%** vs a true **95.4%**; the tell was we were
NEVER earlier. (2) Walk **function bodies** — `#[cfg]`-paired inner `fn`, 8× in
one ripgrep file; stopping at item level **inverts the `extra` gate**. (3) Walk
**nested** blocks (`for` body, `match` arm) — hence `syn::visit::Visit`, because
**a hand-rolled walk only sees where its author remembered to look.** (4) A self
type with no path (`&[u8]`, `(u8, u8)`) must be rendered from its TOKENS;
returning nothing there files those members under a bare name and puts the
oracle BELOW the extractor it scores.

⚠ `build_oracle()` once reused a STALE binary after a failed rebuild, reporting
the numbers UNCHANGED — which reads as "the change had no effect" rather than
"the change did not compile". It always rebuilds now.

⚠⚠ **`test_rust_fidelity.py` listed its fixture names as a LITERAL in every
`parametrize`** — a second roster beside the frozen artifact, and only the
artifact had a test keeping it honest, so a new fixture was ungated on arrival.
Read off disk now. CI runs it off FROZEN oracle data (no toolchain, no network);
regenerate per `tests/fixtures/rust/REGENERATE.md`.

### Codex tool-surface benchmark (`benchmarks/codex_surface/`) — NEGATIVE result

⚠ Shipped in 1.108.271. A STANDING warning about a measurement, not a release
note that ages out. Forensics in `ISSUE-HISTORY.md` (2026-07).

⚠⚠ **Do not quote the arm numbers; the honesty gate fired.** The largest arm
difference was smaller than the baseline's variation against ITSELF, and the
directions were incoherent. The hypothesis is **untested, not disproven** — the
instrument cannot resolve an effect that size.

⚠⚠ **The finding that outlived the arms, and it corrects a claim this project
made: 86% of baseline input is CACHED.** The schema block is stable across
requests, so it is paid at full rate roughly ONCE and at cache-read rates after.
Any framing of "24,007 tokens in every request" is wrong, and that framing was
used here before measuring. **The fixed-cost story is a WEAKER explanation for
the r/codex result than the raw number suggests, not a stronger one.**

⚠⚠ **`tool_profile: "standard"` is NOT a token lever: it drops 9 of 91 tools and
5.7% of the payload.** `core` (74.0%) and `counter` (95.9%) are the only two
settings that move the number; there is no gradient between them, and the config
surface implies there is. ⚠ Under `full`, tool DESCRIPTIONS are 36% of the
payload and `compact_schemas` rewrites input schemas only — schema compaction is
near its floor, descriptions are untouched ground.

⚠⚠ **Quote `benchmarks/schema_baseline.json`, never a figure from the harness.**
It is written by `benchmarks/harness/capture_schema_baseline.py` and guarded by
`tests/test_schema_budget.py`; the harness counts a different payload shape, so
the two will never agree digit for digit and neither is wrong. The Counter
avoids **95.9%**, not the ~98% `run_route_recall.py` asserted for two months —
that literal is computed from the baseline at runtime now, with a test that
fails if any schema-saving percentage returns to that file. **The gap existed
because the budget guardrail only walked `tool_profile`, which does not apply to
the front door at all**, so the largest lever in the project had no test under it.


**Dated entries are rotated out.** Closed issue and PR history lives in
`ISSUE-HISTORY.md`, verbatim, and is NOT loaded into a session. Grep it by
date or issue number. ⚠⚠ **Never quote an open-issue count, an open-PR count or a
timebox date from either file — run the query.** Those are the only facts here
with a guaranteed expiry date, and this section carried a self-contradictory one
for three weeks before the rotation caught it.

```bash
GITHUB_TOKEN="" gh issue list --state open ; GITHUB_TOKEN="" gh pr list --state open
```

### Standing lessons

Each names a date to grep for in `ISSUE-HISTORY.md`.

- **We fix the reported call site and leave the mechanism.** Three times in three
  days (08-19, #506/#507/#508/#509): a second generator, a second call site, a
  second derivation. The one-sentence fix each time is *ask the authority instead
  of reproducing its logic*.
- **Write the ratchet before concluding the reported list is the list.** 08-18
  #489 reported three sites; a test over the PROPERTY found five. Same at #447
  (three spellings of one path rule) and #491.
- **A test for a destructive defect EXECUTES it on the non-vacuity pass.** 08-20
  #447 wrote a real file into a real Windows system directory because the target
  came from the report verbatim. The target must be somewhere the test owns.
- **A concurrency test must pin the interleaving.** 08-17 #490: signal-and-race
  passed against the broken source. The non-vacuity count is the tell (7/8, then
  8/8). [[a-concurrency-test-must-pin-the-interleaving]]
- **A mock broad enough to satisfy an assertion can bypass what the assertion is
  about.** 08-13 #439/#453, three costumes in one day, including a guard that
  could not fire because it raised `AssertionError` into a bare `except`.
- **A parameter that is present and does nothing is indistinguishable from the
  defect it was added to fix.** 08-19 #508: `repo=` threaded through six sites
  with nothing on the path loading what it reads.
- **Fixing a producer does not fix its history.** 08-05 #414: re-indexing is a
  no-op when the corrupt rows sit in files that never changed. Hence
  `PARSER_GENERATION`, checked BEFORE every early-returning fast path.
  [[feedback_fixing_a_producer_does_not_fix_its_history]]
- **Verify at the user's entry point.** 08-04 #412: the defect was real one layer
  down and the served response was merely contradictory.
  [[feedback_verify_at_the_users_entry_point]]
- **A principle stated over a set can be right for part of it.** 08-18 #488:
  "explicit beats default" was safe for the free on-machine provider and would
  have started billing a remote account for the paid ones. A red test was the
  spec. [[a-principle-over-a-set-may-be-right-for-part-of-it]]
- **A version line is a CONVENTION, and conventions do not fail builds.** 08-20
  #521: LICENSE condition 2 gained an obligation while the header stayed at 1.1.
  Pin the terms by digest so the substantive-or-editorial call happens AT the edit.
- **Measure the safe fix before choosing the risky one.** 08-13 #442: the obvious
  low-risk shape captured 2% of the available saving.
- **A setting fixed in one repo of a suite is fixed in one repo.** 08-20: jdoc and
  jdata had matrices that had never run, under a check nobody reported.
- **A defect is not evidence against the number it did not produce.** 08-22: a
  per-call over-count in six analytical tools was written up as putting a basis
  change behind the PUBLISHED savings figure. The number quoted was one seat's
  statusline, the site's is a separate opt-in aggregate, and the tools feeding it
  already deduped by file. **Trace the path to the specific figure before
  implicating it, and never net coverage-conservatism against a per-call basis
  error — they are different axes.** [[a-defect-is-not-evidence-against-the-number-it-did-not-produce]]
- **A ratchet can pass against the defect it names.** 08-22: the savings-baseline
  guard used a depth-limited regex and walked straight past
  `sum(int(s.get("byte_length", 0) or 0) for ...)`, two parens deep. It only
  showed up on the non-vacuity pass. **Run a text-scanning ratchet against the
  reintroduced defect, never only against the fixed tree** — a green ratchet and
  an absent ratchet look identical.
- **A guard sampled AFTER the work can be tripped by the work.** 08-24: the
  reuse audit read the .db-rewritten probe at the end of its scan, and its own
  semantic channel opens a read-WRITE connection that moves that mtime -- so it
  reported a concurrent rebuild it had caused itself and made its best verdict
  unreachable. **Ask what the check's own footprint does to the thing it
  measures, then sample before it.** Excluding a known false positive repairs a
  proxy; it does not weaken the guard.
- **A module that imports clean has been tested for nothing.** 08-24: 884 lines
  written in one pass, imports clean, four defects on first execution -- three
  of them a check that could not observe what it claimed to check, including a
  `match_strength` published on every row that was always 0.0 because
  `search_symbols` emits `score` only under `debug=True`. **Run it before
  reviewing it; the read-through found none of these.**
- **A set cannot count, and a comparison built on one cannot fail.** 08-27: the
  Rust fidelity harness graded a 37.9% name-collision rate as a perfect run,
  because both sides keyed bare names into sets and every repeat of a name
  collapsed to one entry. **The tell is that the check would report the same
  answer if half the matches vanished** — test that directly by deleting them.
  Same shape as #553's fixture and #554's positive-only assertions: a green
  signal about something the instrument cannot observe.
  [[a-guard-covered-only-by-positive-tests-can-be-deleted]]
- **Ask what a measurement's DENOMINATOR does when the thing you are testing
  changes.** 08-27: cache-hit RATE cannot separate tool-surface arms, because a
  stable prefix raises numerator and denominator together, so the arm carrying
  the least schema scores the highest. The cut was not merely inconclusive, it
  was incapable — and it will be suggested again by the next cache paper.
- **Dropping an unmeasurable axis is not the same as omitting an inapplicable
  one, and the difference has a SIGN.** 08-28: gating `churn_surface` on a
  shallow clone by omitting it — the convention `runtime_coverage` already uses
  — took the same tree from **84.0 B to 88.8 B** while full-clone truth was
  **77.3 C**. **Removing a low-scoring axis RAISES a mean**, so the fix moved
  the published grade further from reality than the defect had. NOT APPLICABLE
  may be dropped silently; COULD NOT MEASURE must withhold the composite and
  the grade. ⚠ Ask which direction a "safe" omission moves the number before
  shipping it. [[a-one-directional-check-certifies-its-blind-side]]
- **`.get(key, default)` is not a None guard when the key EXISTS.** 08-28:
  `diff_radar`'s `.get("composite", 0.0)` raised the moment a composite was
  legitimately `None` — the default never fires for a present key. ⚠ And the
  0.0 it would have supplied was worse than the crash: a ~77-point regression
  reported against a side nobody measured. Same shape as
  [[a-module-that-imports-clean-has-been-tested-for-nothing]].
- **The host's timezone can select a test's INPUT FORMAT.** 08-28: git renders
  a UTC offset as `Z`, which `datetime.fromisoformat` could not parse before
  3.11 — so a boundary date was unreadable on 3.10, in CI only. Every runner is
  UTC; this box is CDT and got `-05:00`, which parses everywhere. ⚠⚠ **No local
  run on any version could reproduce it, `uv run --python 3.13` included** —
  the version matrix was not the axis that mattered. Pin format-sensitive
  parsing with a UNIT test over every spelling; an integration test can only
  observe the one its host emits. [[a-module-that-imports-clean-has-been-tested-for-nothing]]
- **A command that does not CREATE its environment is testing whatever was
  left there.** 08-28: the release checklist's CI-env reproduce ran
  `uv run --python 3.13 python -m pytest` with no sync and no `--extra watch`,
  so it inherited `.venv`. It looked right for months because a previous sync's
  packages survived; switching interpreters cleared them and **105 tests
  silently stopped executing while the run reported exit 0 and the totals
  reconciled exactly**. ⚠ Read the SKIP count, not just the exit code and the
  total. ⚠⚠ The fix is in a GITIGNORED skill file, so the durable copy and its
  ratchet live in the repo — `tests/test_ci_env_reproduce_command.py` binds
  CLAUDE.md's command to `test.yml`'s install line.
  [[pipes-and-missing-xdist-both-report-exit-zero]]
- **A denylist catches the instance; an allowlist catches the class.** 08-28:
  `relnotes.md`, a scratch copy of the release notes, was swept up by
  `git add -A` and shipped inside the published sdist. The sdist canary tests
  prove NAMED bad paths are absent and could never have seen it — a scratch
  file has no name to plant a canary under. ⚠ **Build release notes outside the
  repository**; a `.gitignore` entry protects only the spelling someone
  remembered. ⚠ Assert the allowlist in BOTH directions — an entry naming a
  file that no longer ships makes the list stop describing the artifact.
  ⚠⚠ **It found a SECOND instance minutes later and it was mine**: `suite.log`,
  the pytest redirect used for every gate run that day, sitting in the repo
  root. A release cut while one existed ships it, and a pytest log carries
  absolute paths and usernames. **Redirect gate runs to the scratchpad, never
  the repo.**
- **A field written by nobody's reader is a defect with no symptom.** 08-28
  (#561/#562): `detect_framework` persisted `entry_point_patterns` into
  `context_metadata` at index time, and a tree-wide search found that key
  written in ONE place and read in NONE. Three tools each reproduced their own
  "is this a root?" answer and every one was Python, so a Next.js repo detected
  zero entry points. ⚠⚠ **An unconsumed field also rots unnoticed**: Flask and
  FastAPI carried `"*.py"` there, which under fnmatch declares the whole tree —
  the first naive reader would have switched dead-code detection off across an
  ecosystem. **Grep a persisted field for its readers before trusting it, and
  before adding one.** [[a-module-that-imports-clean-has-been-tested-for-nothing]]
- **A count taken after the page is cut describes the page.** 08-28 (#559):
  `untested_count = len(symbols)` ran after the `max_results` slice, so
  `get_repo_health`'s `max_results=1` published ~100% test reach on every repo
  with untested code. ⚠ **Invisible to any single-call test** — one call's
  number is self-consistent; only two page sizes over the SAME repo can see it.
  ⚠ And the paired half: **a refusal is not a zero.** `get_dead_code_v2`
  returning `[]` WITH a `signal_warning` became `dead_code_pct: 0.0` and an axis
  of 100. [[a-one-directional-check-certifies-its-blind-side]]
- **A competitor's fix list is a free defect probe.** 08-22: a rival's
  `fix(gini): measure a file's lines as its own span, not the sum of every node`
  named our defect precisely enough to confirm in one query —
  `get_architecture_metrics` summed `byte_length` over nested symbols, inflating
  byte mass 33.4% overall and up to 2.28x per file. Read their commit TITLES
  against whatever we built the same way; it is minutes, and it finds what our
  own tests were written not to see. See CHANGELOG `[Unreleased]`.

## Issue + release policy (2026-07-28)

⚠⚠ **The forensics behind every rule here are in `ISSUE-HISTORY.md` §
"issue + release policy forensics (2026-08-28)" — measurements, dates and the
incidents that produced each one. READ THEM BEFORE ARGUING WITH A POLICY.**
Several were written after we broke them ourselves; 2e is recorded in the first
person because the wrong call sounded reasonable at the time.

**1. One issue, one verdict.** A multi-finding report gets SPLIT at triage into
one issue per finding, cross-linked, credit on each. Nothing is dropped and no
detail is discouraged. The reason is closure mechanics: a 4-finding issue closes
only when the last one settles, so three finished fixes sit behind one
unfinished conversation. ⚠ This corrects a mistake we made deliberately —
consolidating five jdoc issues into one gate cut the open count from 5 to 1 and
manufactured a single artifact with the power to block a release.
**Tracker-tidiness and granularity pull in opposite directions; do not optimize
the count.**

**2. A release is NEVER blocked on an open issue**, including a verification we
asked for. Done + tested + green ships on schedule, carrying a plain-language
verification-status line. Late re-verification counts IN FULL and is announced
retroactively. Nothing expires. **Every timebox names its default action** ("verification
by X, or Y ships with disclosure Z"); a date with no stated consequence is a wish.
⚠ **The point is that a reviewer's thoroughness must never become a veto.** If
being careful can stall a release, careful review becomes expensive to accept.

**2e. NEVER BATCH OUR RELEASE BEHIND SOMEONE ELSE'S CLOCK** (jjg, 2026-08-18,
after it happened). ⚠⚠ **Policy 2 does not get broken by someone overruling it —
it gets broken by an apparently sensible batching argument that never mentions
it.** I once recommended holding five merged, green, user-facing fixes for two
days so a release could absorb a contributor's CLA-blocked PR and save three
conflict resolutions. jjg accepted it. That coupled our schedule to a
contributor's signature, which is exactly what policy 2 exists to prevent — and
it was wrong on the merits, because batching reduces the NUMBER of resolutions,
not whether they happen, and each is minutes.
⚠ **The test, before proposing to hold a release:** name the thing being waited
for, and whether it is OURS. If it is anyone else's action — a signature, a PR, a
reply, a re-run — ship now and let them ride the next one.
⚠ **Corollary: "reduce OUR churn" is not a release criterion.** Conflict
resolution and re-merges are our costs to absorb. The moment avoiding them shapes
WHEN users get fixes, the optimisation has inverted.
⚠ **The timeboxes are NOT the problem and must not be "fixed".** Every one names
a default that ships the work regardless. If a window appears to block a release,
the batching decision is what is blocking it. [[never-batch-a-release-behind-someone-elses-clock]]

**2f. THE ONE CASE WHERE NOT CUTTING A RELEASE IS LEGAL — and it is narrow**
(jjg, 2026-08-20). ⚠⚠ **THE DISCRIMINATOR IS WHETHER A USER IS WAITING FOR
ANYTHING IN THE BLOCK.** A block that is entirely metadata for one named
recipient is the only shape this covers, because shipping it gets no user
anything. ⚠ The asymmetry that decides it: **released metadata is PERMANENT per
version, unreleased metadata is FREE** — the same immutability argument that
justifies deciding fast, pointing the other way at the release step.
⚠⚠ **THE TEST, applied every time before invoking 2f: name what is in the block
and who is waiting for it. If ANY entry is a fix, a feature or a correctness
change, 2f does not apply and 2e governs — cut it now.**
⚠ A held release with no trigger is a forgotten release, so record the hold in
Current State, not only here. [[declining-to-cut-is-not-holding-a-fix]]

**3. A contributor's PR is never the only path.** Timebox it and keep our own
path warm (#388 taught this the expensive way).

**3a. NO TIMEBOX WE OFFER RUNS LONGER THAN 24 HOURS** (jjg, 2026-08-14, widened
same day; **made ABSOLUTE 2026-08-20 — "Not again. 24 hour. Tops. Ever."**). It
covers every shape: signing the CLA, opening a PR already written, taking an
issue to implement.
⚠⚠ **The window is only fair BECAUSE the default action preserves credit.** At
expiry we implement it ourselves and credit them in the CHANGELOG, the release
notes and the close comment. So the 24 hours decide whose COMMIT it is, never
whether they are credited and never whether the fix ships. **Quote the default in
the same comment as the deadline** — a clock with an unstated consequence reads
as a threat.
⚠⚠ **The failure mode has a name: a CLA hostage negotiation.** #443 went eight
days — a real security fix, reviewed and green, held behind a 30-second form,
while seven of our own merges conflicted its branch. **A window longer than 24
hours purchases exactly one thing: the chance the contributor's commit is theirs
— and it pays for that chance in the user's exposure to an unfixed defect.**
⚠ An extension the contributor ASKS FOR is different from a default we hand out;
CONTRIBUTING.md invites the ask. Hold it when they ask.
⚠ **Do not shorten a timebox already posted**, and **re-read the thread for the
operative date — never quote one from here or from memory.** A thread can carry
two. The grandfathering clause is spent and must not be revived.
[[re-read-the-thread-for-the-operative-timebox]] [[timebox-comments-state-deadline-and-default-only]]

**3b. A MERGEABLE contributor PR merges BEFORE any changelog-touching work of
our own** (jjg, 2026-08-14), including a release commit.

```bash
GITHUB_TOKEN="" gh pr list --state open --json number,author,mergeable,mergeStateStatus \
  --jq '.[] | select(.author.login != "jgravelle") | "#\(.number) \(.author.login) \(.mergeable) \(.mergeStateStatus)"'
```

Any row reading `MERGEABLE CLEAN` goes in before ours. ⚠⚠ The reason is
mechanical: our `[Unreleased]` edits land in the same block a contributor's entry
occupies, so each of our merges conflicts their branch, and **a CONFLICTING fork
PR has no `refs/pull/N/merge` and therefore gets NO CI AT ALL** — their branch
goes dark for a reason unrelated to their change. Measured: #443 conflicted FIVE
TIMES IN ONE DAY, which is one wrong merge order repeated, not five incidents.
⚠ **The boundary:** a BLOCKED PR cannot go first. Then we ship anyway (policy 2)
and **we own the resolution** — push the merge to their branch and say on the
thread that the conflict was ours. **This rule governs ORDER when we have a
choice; it never holds our work behind someone else's form.**
⚠⚠ **Do NOT answer "an issue is stuck" with aggregate stats.** jcm's median
time-to-close is 0 days; that is TRUE and it is NOT a response. The cost of a
blocked issue is CONCENTRATED, not distributed. Design the fix at the OUTLIER.
[[feedback_dont_answer_pain_with_aggregates]] [[push-to-the-fork-remote-by-name]]

**3c. PROFILE THE AUTHOR BEFORE REVIEWING A VENDOR-SHAPED PR** (jjg,
2026-08-17). Any PR adding a named third-party provider, gateway, SDK or endpoint
gets three queries FIRST, before a line of the diff is read:

```bash
GITHUB_TOKEN="" gh api users/<login> --jq '"created=\(.created_at[0:10]) repos=\(.public_repos) company=\(.company) bio=\(.bio)"'
GITHUB_TOKEN="" gh api "search/issues?q=is:pr+author:<login>&per_page=1" --jq .total_count
GITHUB_TOKEN="" gh api "search/issues?q=is:pr+author:<login>+<vendor>+in:title&per_page=1" --jq .total_count
```

⚠⚠ **The discriminator is the RATIO, not the volume.** #485's author had 3,089
PRs, 2,242 with "minimax" in the title (73%), ~19/day. Found in under a minute;
the PR had been reviewed in depth twice before anyone looked.
⚠ Also check whether we have a DEMAND signal, the actual #380 bar:
`gh api "search/issues?q=repo:jgravelle/jcodemunch-mcp+<vendor>"`.
⚠⚠ **Quality is NOT the discriminator and must not be used as one.** #485's diff
was better than most human PRs. **Good work aimed at something nobody asked for
is still something nobody asked for.** Close on demand, credit the finding, and
say plainly that quality was not the reason.
⚠ Do not assert employment you cannot prove — state the numbers and ask.
⚠ **A posted timebox's default can be RETRACTED IN THE OPEN when the facts
change, but never silently.** [[profile-the-author-before-reviewing-a-vendor-pr]]

**3d. `license/cla` IS A REQUIRED STATUS CHECK ON THE DEFAULT BRANCH OF ALL
THREE REPOS** (jjg, 2026-08-17 for jcm; suite-wide 2026-08-21). ⚠⚠ **A setting
fixed in one repo of a suite is fixed in one repo** — for four days jdoc required
nothing and jdata had no protection at all.

```bash
for r in jcodemunch-mcp:main jdocmunch-mcp:master jdatamunch-mcp:master; do
  GITHUB_TOKEN="" gh api "repos/jgravelle/${r%%:*}/branches/${r##*:}/protection" \
    --jq '{contexts:.required_status_checks.contexts, strict:.required_status_checks.strict, enforce_admins:.enforce_admins.enabled}'
done
```

⚠ `enforce_admins: false` and `strict: false` are both deliberate: the admin
override lets jjg land a merge pushed to a contributor's fork, and `strict` would
force a rebase after every release.
⚠⚠ **NOTHING IS ERASED — `license/cla` is a legacy commit STATUS, not a check
run.** Every other check is a check-run that GitHub re-runs per head; a legacy
status is posted to ONE SHA, so a new commit starts with zero of them. The old
head keeps its status and the signature (stored per ACCOUNT at cla-assistant.io)
was never in question. **The gate cannot tell "not signed" from "not reported",
so it fails closed to `BLOCKED` for both. Absent still means DO NOT MERGE — but
the remedy is to get a status posted on the current head, never to re-verify an
agreement that did not change.**

```bash
# count=0 means NOT SIGNED or NOT REPORTED. Never merge on absence.
GITHUB_TOKEN="" gh api "repos/jgravelle/<repo>/commits/<head-sha>/status" --jq '"state=\(.state) count=\(.statuses|length)"'
```

⚠⚠ **THE RE-TRIGGER IS OURS — no contributor action, ~25 seconds.** The status
comes from a repo WEBHOOK to cla-assistant.io on `pull_request`, not an in-repo
workflow. A delivery can arrive, answer `200 OK`, and post nothing; redelivering
that same event makes it post.

```bash
HID=$(GITHUB_TOKEN="" gh api repos/jgravelle/<repo>/hooks --jq '.[0].id')
# ⚠ jq mangles delivery ids (past float precision) — read them with python.
GITHUB_TOKEN="" gh api "repos/jgravelle/<repo>/hooks/$HID/deliveries?per_page=15" > dv.json
python -c "import json;[print(x['delivered_at'][5:16],x['event']+'/'+str(x.get('action')),x['status_code'],x['id']) for x in json.load(open('dv.json'))[:8]]"
GITHUB_TOKEN="" gh api --method POST "repos/jgravelle/<repo>/hooks/$HID/deliveries/<exact-id>/attempts"
```

⚠ Diagnose first — a delivery that never arrived is a different problem from one
that arrived and did nothing. ⚠ CLA Assistant can also fail to fire on PR OPEN,
which reads identically and has the opposite cause; check comments as well as
statuses. ⚠ Our own push to their branch is a `synchronize` and provokes a
missing status.
⚠⚠ **NEVER POST THE STATUS OURSELVES.** We hold admin and the Status API would
clear the gate in one call. `license/cla` is a legal assertion about an
agreement, and a maintainer-authored `success` is a forged one —
indistinguishable from the genuine article afterwards. **Redelivering makes CLA
Assistant reach its OWN verdict, which is the whole difference.**
⚠ It does NOT solve vendor time-wasting and must not be sold as if it does;
signing costs a campaign nothing. Legal exposure and spam are different problems.
[[a-push-reprovokes-a-missing-cla-status]] [[org-forks-cannot-be-pushed-to]]

Surfaces: `CONTRIBUTING.md` ("One issue, one verdict" + "A release is never
blocked on an open issue") and `.github/ISSUE_TEMPLATE/`.
⚠ **CONTRIBUTING.md is IDENTICAL suite-wide** (differing only by product name,
repo slug, and jcm's quality-gates section). Two pre-existing bugs fell out of
normalizing it: the documented `pip install -e ".[test]"` was WRONG IN ALL THREE
REPOS (no repo declares a `test` extra; dev deps are a PEP 735
`[dependency-groups]` block), and jcm's `README.md#license-dual-use` anchor
pointed at a heading that does not exist. ⚠ **CI installs with `uv sync` and
never runs the command the docs give a human**, which is why it survived: the
thing we test is not the thing they do.
## Registry verification reads a NESTED row (2026-08-27)

⚠⚠ **The MCP registry API nests each row as `{server: {...}, _meta: {...}}`**
(schema `2025-12-11`). `name`, `version` and `packages[]` sit under `server`;
`isLatest` and `publishedAt` sit under
`_meta["io.modelcontextprotocol.registry/official"]`. **A flat `row["name"]`
read returns ZERO rows on a publish that completely succeeded** — measured
minutes after `mcp-publisher` confirmed 1.108.301, where the flat parse found
0 of 45 rows and the nested parse found all 45 with `isLatest: 1.108.301`.

⚠⚠ **This is a SECOND false negative on top of the known paging trap, and
unlike that one it SURVIVES `&limit=100`** — so the documented remedy does not
help and the symptom is indistinguishable from a failed publish. **Never
re-publish on a zero-row read; fix the parse.** Also confirm
`server.packages[].version` advanced, not only `server.version` — an entry can
move one and not the other.

⚠ **The release checklist itself lives at `.claude/skills/release/SKILL.md`,
which is GITIGNORED** (`.gitignore:58`, the v0.2.6 credential-leak fix, with
the matching sdist exclusion asserted by `tests/test_sdist_exclusions.py`). So
corrections there are MACHINE-LOCAL: not in git, not in CI, gone on a fresh
checkout. That is why this note is here instead. **Do not un-ignore `.claude/`
to fix that** — it reintroduces the vector that got five releases yanked.

## Reproducing CI's environment (release step 2c)

⚠⚠ **The release checklist lives in `.claude/skills/release/SKILL.md`, which is
GITIGNORED, so a correction there is machine-local and gone on a fresh
checkout.** This is the copy that survives, and
`tests/test_ci_env_reproduce_command.py` binds it to the workflow so the two
cannot drift apart unnoticed.

```bash
uv sync --locked --group dev --extra watch --python 3.13
uv run --python 3.13 pytest tests/ -q
```

⚠⚠ **Step 2c read `uv run --python 3.13 python -m pytest tests/ -q` until
2026-08-28 and NEVER built CI's environment** — no `--extra watch`, no
dev-group sync. It only looked correct while `.venv` happened to carry the
extras from an earlier sync, i.e. **the command was inheriting a state it did
not create**. CI runs `uv sync --locked --group dev --extra watch` first.

⚠⚠ **Caught mid-release, and the near-miss is the lesson: it returned EXIT 0
and the totals reconciled EXACTLY** (8,740 + 18 new tests = 8,758) — the two
things "green" normally means here. Meanwhile `passed` fell 8,721 → 8,634 and
`skipped` rose **19 → 124**: 105 tests silently did not execute, because
`watchfiles` (the `[watch]` extra CI installs BY NAME) was absent.

⚠ **READ THE SKIP COUNT, not just the exit code and the total.** Expect the
documented 19–26 range; a jump means the environment, not the code. The
before/after delta on the SAME job is the only signal.

⚠ Third instance of one family, and CONTRIBUTING.md already carries the
sentence: *CI installs with `uv sync` and never runs the command the docs give a
human, so the thing we test is not the thing they do.* The first was
`pip install -e ".[test]"` (an extra no repo declares); the second was
`-n 4 --dist loadfile` under a bare `python -m pytest`, which collects nothing
and exits 0. [[pipes-and-missing-xdist-both-report-exit-zero]]

## Maintenance Practices

1. **Document every tool before shipping.** Any PR adding a new tool to `server.py`
   must simultaneously update: README.md (tool reference), CLAUDE.md (Key Files),
   CHANGELOG.md, and at least one test.
2. **Log every silent exception.** Every `except Exception:` block must emit at
   minimum `logger.debug("...", exc_info=True)`. For user-facing fallbacks (AI
   summarizer, index load), use `logger.warning(...)`.
3. **CHANGELOG.md** is the authoritative version history — update it with every release.
4. **Never hand-type a jCodeMunch benchmark number.** The comparison harnesses
   (`run_rag_baseline.py`, `run_odysseus_compare.py`) read
   `benchmarks/jcm_reference.json`, written by `run_benchmark.py --reference`.
   ⚠ **The failure this closes was invisible for four months:** our side was a
   2026-03-28 constant while the other side of every ratio was re-measured each
   run, so published ratios drifted on their own. Re-measuring moved all three
   per-repo figures AGAINST us and flipped a published winner (gin: `jcm 1.2x
   leaner` → `RAG 1.1x leaner`). ⚠ **A repo outside the artifact renders "not
   measured" — there is deliberately no estimator.** The removed one allocated
   our cost proportionally to repo size, i.e. it assumed the opposite of what we
   claim. `tests/test_benchmark_reference.py` fails on a returning `JCODEMUNCH_*`
   constant and asserts the estimator absent BY NAME. ⚠ **FOUR artifacts mirror
   one run** — `results.md`, `METHODOLOGY.md`, README, and
   `benchmarks/provenance/measured.json`. Re-syncing three and missing the
   fourth failed `test_provenance.py`, **inside the known 12 local-ONNX env
   failures**. `--reference` now rewrites the provenance block itself; two
   committed artifacts disagreeing is the same defect in a different costume.
   ⚠ **v1.108.222: the corpus is PINNED by upstream commit** in
   `benchmarks/tasks.json`, and `--reference` refuses to publish a number
   measured against an unpinned, drifted, or unknown-completeness corpus. **A
   fifth artifact now mirrors the run: `benchmarks/REPRODUCING.md`**, and a test
   fails if it does not name every pinned SHA. ⚠ **Never state a repo's file
   count as a property of the repo** — it is a property of the INSTALLATION
   (grammar pack, size limits, skip patterns), which is the whole point of the
   .221 capability certificate. Say which commit, and let the count live in the
   artifact beside the SHA that produced it.
5. **Rotate, never delete — and the budget is the WHOLE FILE, not one section.**
   `Current State` keeps the 3 newest releases and the `Tests:` line keeps the same
   three; closed dated entries go to `ISSUE-HISTORY.md`, which no session loads.
   `tests/test_claude_md_size.py` is the gate.
   ⚠⚠ **The prose version of this rule was followed and the file broke anyway.**
   On 2026-08-21 CLAUDE.md hit 200,543 chars and the harness refused to load it,
   while `Current State` — the only section this practice named — was 14% of it.
   The growth was in dated issue history (82k) and a `Tests:` line carrying
   per-release counts back to 1.108.268 (16k). **A rule that names one section
   licenses every other section to grow.**
   ⚠ When an entry rotates out, ask what LESSON it earned and put that one line in
   **Standing lessons** with its date. An entry with no reusable lesson needs no
   line; an entry whose lesson is already there needs no second one.
   ⚠⚠ **MEASURE THE SECTIONS BEFORE CHOOSING WHAT TO ROTATE — the answer has
   twice been a section nobody suspected.** On 2026-08-28 at 139,184/140,000 I
   proposed rotating **Standing lessons** and was wrong: it was 6.4% of the
   file, where **Key Files was 40.1% (55,643 chars)** and the issue/release
   policy 15.4%. Rotating what I proposed would have recovered almost nothing.
   Split by heading and sort by size first; it is one script and it settles it.
   ⚠ **Key Files at 40% is the NEXT rotation target and the hardest**, because
   it is also the most load-bearing — the per-file ⚠⚠ warnings are what stop a
   defect recurring. Rotate its dated INCIDENT prose, never its rules.
   ⚠⚠ **MEASURED 2026-08-28: Key Files has almost NO rotatable narrative left.**
   A scan of its 119 entries found FOUR provenance clauses (1,713 chars), three
   of them rules; Standing lessons and Current State each duplicate NOTHING from
   it. **It is 42% of the file because it is 119 modules of non-redundant
   invariants, not because it is padded** — so documenting one release under
   Practice 1 cost more than a full rotation pass recovered. **The next lever is
   a SPLIT and it is jjg's call.** Do not raise `BUDGET` (the gate says its 10k
   buffer is the last one) and do not buy room by deleting ⚠⚠ rules.
   ⚠ The 2026-08-28 pass took the issue/release policy from 21,448 to 12,391 by
   keeping every rule, every operational command and every prohibition, and
   moving only the forensics — verified by asserting all nine policy numbers,
   six commands and seven prohibitions still resolve. **Write that check as a
   script; a rotation reviewed by eye is how a command goes missing.**
6. **A CI step that produces a PUBLIC verdict is product surface — test its text.**
   `tests/test_health_radar_action.py` opened by asserting that the Action's shell
   and YAML steps "can only be exercised by running the Action in a real CI
   environment", and under that exemption
   `git fetch origin "$BASE" --depth=1` sat unread in the base-checkout step.
   ⚠ **`--depth=1` does not merely limit a download — against an already complete
   clone it SHORTENS it**, writing `.git/shallow`. `churn_surface` is
   `complexity x log(1 + churn)` with churn counted by `git log --since=<N> days
   ago`, so the base saw ONE commit, scored every file at churn <= 1, and came
   back artificially healthy. ⚠⚠ **Measured 2026-08-10 at a single commit,
   identical tree hash both sides: shallow 82.2 (B), full 75.5 (C), and
   `churn_surface` the only axis that moved.** The same commit graded B against
   itself. Every PR was charged for the gap, publicly, on the contributor's own
   thread. **Cannot execute it is not cannot check it** — the guard that closes
   this reads step text, which is weaker than running the Action and is still
   exactly what was missing.
7. **`confidence` is certainty language; ship a stop rule beside it.** A score
   says how sure we are, which invites the caller to go get surer.
   `tools/_stop_rule.py` answers the other question: can anything make it surer?
   ⚠ **`terminal` means FINAL, not SAFE** — a blocking verdict is terminal too.
   ⚠⚠ **A false `terminal: true` on a destructive action is the worst error this
   contract can make**, so every uncertainty resolves to False, including an
   unrecognised verdict. Motivated by arXiv 2608.01347, which measures
   verification loops as a distinct TOOL-borne waste carrier: the highest
   redundant-verification runs cost 18x the clean-run median and 2.5x the tool
   calls at no success gain. ⚠ `already_consulted` lives in the tool
   DESCRIPTION, not the response, because it is static per call and the
   description is cached — the same fixed-prefix versus per-turn split that
   paper measures. That makes it prose nobody diffs, so `test_stop_rule.py`
   binds it to real import sites and fails if a tool stops calling what we
   claim it consulted.
8. **A test must never read or write the developer's real global config.**
   `load_config()` with no `storage_path` resolves to `CODE_INDEX_PATH` or
   `~/.code-index/config.jsonc`, reads it, and with the default
   `create_missing=True` WRITES it when absent. ⚠⚠ **conftest's
   `_reset_global_config` already guarded this and already cited #411; a bare
   `load_config()` in a fixture runs AFTER that reset and re-pulls the real config
   straight past it.** The guard existed and the call sites walked around it, which
   is why `tests/test_config_isolation_guard.py` checks the CALL, not the reset.
   ⚠ **The write half is the worse half:** on a storage dir that looks like an
   existing install (any `.db`) with no config file, the config a test run creates
   has `tool_surface` ABSENT, resolving to `full`, and `_fresh_config_content` is
   explicit that `upgrade_config` can never back-inject it. A test run could pin a
   user to a surface nothing migrates them off. Found as three failures @lilubot
   hit on PR #433 and reasonably blamed on their own machine (#437). Our suite was
   green because this box has `max_folder_files` commented out, CI green because
   the runner has no config at all. **A test that passes on two machines and fails
   on a third, for a reason none of the three can see, is the defect.**
9. **When a fix turns an OLD test red, check whether that test was encoding the
   defect before "fixing" the code back.** Four instances in one release cycle
   (2026-08-18/19): `test_generate_full_snippet` required EVERY canonical tool
   name to appear in the guide, so it could only pass while #495 existed;
   `test_embed_drift` pinned a literal error wording, which is how that site kept
   a stale copy through #489; `test_full_surface_still_honours_profile` asserted
   equality with the baked `_PROFILE_TIERS`, which is #507's premise; and two of
   my own in #489 asserted on the CONSTANT rather than the call site, so they
   checked the fix instead of the site.
   ⚠ **The tell is that the test states the mechanism rather than the outcome.**
   "every canonical name appears", "equals the tier table", "the message is this
   string" are all restatements of an implementation. "what it advertises is what
   it will dispatch" is the property. ⚠ A red suite invites fixing the tests; run
   the non-vacuity pass on the OLD test too — if it passes only against the
   pre-fix tree, it was the defect's witness, not its guard.
10. **Run the touched test files BEFORE the full suite** (jjg, 2026-08-28). The
   suite is a RELEASE gate, not an edit loop. Measured on #558: full suite 12:55
   (6 failures) -> fix -> 10:47 -> CI 9:21 = **33 minutes of blocking wait**,
   where `pytest` on the three affected files reproduces all six failures in
   **3 seconds**. Order: touched files, then `uv run ruff check src/` (it catches
   the syntax class without running anything), then the suite once as the gate.
   ⚠ **The exception is narrow: a change whose blast radius cannot be named** —
   a shared primitive like `PARSER_GENERATION`, a store schema, a skip-list
   constant reaches files no import graph predicts, and there the suite IS the
   first check. Say which case applies; `get_blast_radius` answers it directly.
   ⚠⚠ **APPENDED as 10, not inserted at 8 where it fits by topic.** The first
   attempt slotted it beside the other testing practices and renumbered the two
   below it, which silently broke live cross-references in
   `tests/test_build_tree_spellings.py`, `tests/test_hook_steering_fixes.py`
   and `tests/test_hardening.py`, plus dated CHANGELOG and ISSUE-HISTORY
   entries that were correct when written. **These numbers are an index, not a
   ranking, and nothing fails a build when one drifts** — so a new practice
   goes on the END.
   ⚠ **Measure a wait, never estimate it.** I reported this as "two suite runs,
   that's the whole 40 minutes"; 2x13 is 26, and jjg did the arithmetic.

