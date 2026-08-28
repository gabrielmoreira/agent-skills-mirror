# jcodemunch-mcp — Project Brief

## Current State
- **Version:** 1.108.303 — **The measurement was the defect.** Five instruments reported a good number about something they could not observe, and four of them were ours. ⚠⚠ **THE RUST FIDELITY HARNESS, SIX DAYS OLD, GRADED A 37.9% NAME-COLLISION RATE AS A PERFECT RUN — it keyed bare names in a SET, and a set cannot COUNT.** Proven by deleting the second symbol of every duplicated name in the fixtures: `extra` and `missing` did not move, so extracting ONE of `defs.rs`'s **108 `is_switch`** scored like extracting all 108. What it hid: `impl Foo { fn new }` and `impl Bar { fn new }` both emitted a bare `new`, kind `function`, parent None, separated only by a `~1`/`~2` id suffix — **the trait's own declaration qualified fine (`T.go`), so traits had an owner and impls did not.** `impl_item` sat in `symbol_node_types` as `"class"` for the extractor's whole life and never produced ONE symbol (no `name_fields` entry could name it), **and a container becomes a parent only if it EMITTED one** — so it is a virtual scope now, emitting nothing, which is what `syn` says an impl block is too. ripgrep @ `3fce3b5b`: 1,331/3,514 (37.9%) across 44/110 files -> **55 (1.6%)**; 2,199 symbols move `function` -> `method`. ⚠ `undercount` and `qual_mismatch` gate at 0 beside `extra`/`wrong_span`; the oracle emits `qual` and tracks its scopes. **The owner is `self_ty`, NEVER the trait** — `impl Display for Foo` puts `fmt` on `Foo`, and keying on `Display` is the same collision one level up. ⚠ Two more gaps fell out of the new buckets, invisible to everything that shipped: a `const` inside an `impl` came out bare (35 in ripgrep) because `_constant_symbol` hardcodes `qualified_name = name`, and `associated_type` (a trait's `type Carried;`) was absent from `RUST_SPEC` — `.302`'s `function_signature_item` again. ⚠⚠ **`tests/test_rust_fidelity.py` listed its three fixture names as a LITERAL in every `parametrize`** — a SECOND roster beside the frozen artifact, where only the artifact had a test keeping it honest; the new `qualification.rs` was ungated on arrival. Read off disk now. ⚠ **Practice 9 fired again**: `test_rust_fn_in_impl` asserted `kind == "function"` under the docstring *"Without the impl parent being extracted, 'new' appears as a top-level function"* — the defect written down as intended behaviour, passing only while it existed. `PARSER_GENERATION` **6 -> 7** (`qualified_name`/`kind`/`parent` on unchanged content). ⚠⚠ **#556 by @otherjoel is THIRTEEN of the eighteen entries** — twelve findings, one per commit, each measured against Racket's EXPANDER, Racket's READER, or five real package layouts on disk rather than against our own output. `#lang` is read before the grammar runs (`#lang punct` was indexing Markdown code samples; `conscript` lost 61% of definitions and FABRICATED ~100 that error recovery re-parented to module level); collection paths resolve through `info.rkt` (splitflap 0/70 -> 13 edges, congame 304 -> 624); **the `define-generics` exemption was REMOVED rather than widened, because `extra: 0` was carrying a fabrication.** ⚠ He declined the `PARSER_GENERATION` bump ON PURPOSE and substituted a per-project `racket_config_digest` stamp — **an absent key is detectable forever, a stamp equal to the constant is not**, our own `.302` lesson used against us correctly. We bumped to 7 anyway for the Rust fix, so those indexes are reached twice; **the stamp is NOT redundant** — it fires when a PROJECT edits `racket_langs`, which no global counter can see. ⚠ Also: **`.next`/`.nuxt`/`.output`/`.svelte-kit`/`.angular`/`.turbo`/`.parcel-cache`/`.dart_tool` were indexed as source** (`.next/server/**` is a TRANSPILED copy of the user's own pages — the `_build` defect a FOURTH time); **the observatory scored eleven public repos on ONE COMMIT** so `churn_surface` read churn 1 everywhere and ranked nothing but complexity (jcm 81.3 B -> 75.6 C, i.e. we were FLATTERING ourselves); **`max_nesting` counted brackets**, which in Python measures the deepest EXPRESSION (`index_folder`: 3 reported, AST truth 6); and the codex cache-hit-rate cut **cannot separate its arms BY CONSTRUCTION** — it is a ratio, so the arm with the least schema scores highest. ⚠ Three of the five were found by reading a competitor's fix titles against our tree. [[a-competitors-fix-list-is-a-free-defect-probe]] [[a-guard-covered-only-by-positive-tests-can-be-deleted]]
- **Prior (1.108.302):** **Nothing we could say about Rust.** Rust had **20 tracker mentions and zero measurement** while the README talked about 70+ languages; Racket has had a fidelity harness since `.298`. **`benchmarks/rust_fidelity/` scores extraction against Rust's own parser (`syn`)**, same asymmetric shape: `extra`/`wrong_span` gated at **0**, `missing` reported BY KIND so a gap has a name. ripgrep @ `3fce3b5b`, 110 files: **95.8%**, 44 clean files, `missing` (156) entirely `module`+`macro`, both deliberate. ⚠⚠ **THE CEILING IS LOWER THAN RACKET'S: `syn` PARSES, it does not EXPAND.** A `macro_rules!`-generated item is invisible to the oracle AND to us, unscored in BOTH directions — a green run is NOT evidence about macro-generated code. ⚠ **All three gaps it found are FIXED** (`PARSER_GENERATION` **4 -> 5**): `union_item` and `function_signature_item` were absent from `RUST_SPEC` — so `union Foo {}` yielded NO symbol at all, and the half of a trait an implementor MUST provide was the half we could not find — and a `const` in a fn body was excluded by the locals gate, **which already let nested `fn`s through, so it was a node-type rule wearing a scope rule's name**. 3474 -> 3514 symbols. ⚠⚠ **The bump is the clearest case that counter has had**: unlike `.mts` (never parsed, so coverage arrives through DISCOVERY) every `.rs` file in an existing index was already parsed at gen 4 with the old symbol set. ⚠⚠ **THREE oracle traps, every one made US look wrong when the HARNESS was**, and the third fired on the FIX: identifier-span not item-span (scored us **40.4%** vs a true **95.4%**; the tell was we were NEVER earlier), walk function bodies (35 phantom fabrications, **inverting the `extra` gate**), and walk NESTED blocks (`for` body, `match` arm). Now `syn::visit::Visit` — **a hand-rolled walk only sees where its author remembered to look.** **Also #555 (@RascoApps): `sd.encode` fails closed on a table under an undeclared key** — the #354 guard needs ROWS to fire and a wrong KEY yields none, which is how `search_ast` served empty tables. ⚠ Placement is the design: it runs POST-transform, so pre-flattening schemas need NO exemption; scanning the RAW response flags `search_text` on every call and an allowlist for it would have been the wrong fix to the right symptom. ⚠ **CLAUDE.md budget 130k -> 140k**, halving the gap to the 150k harness cliff. **That 10k is the last buffer** — next time, rotate or split. [[a-guard-covered-only-by-positive-tests-can-be-deleted]] [[a-fixture-authored-from-the-schema-tests-nothing]]
- **Prior (1.108.301):** **Green on a defect, three times.** Three green signals sat on top of real defects this release, and that is the release. ⚠⚠ **#553 by @RascoApps: `search_ast` served an EMPTY TABLE for every language and every preset** — the encoder declared `results`/`result_count`/`files_searched`, the tool has always returned `matches`/`total_matches`/`files_scanned`. **The fail-closed guard is STRUCTURALLY BLIND to this class**: it raises when a table has ROWS but no declared COLUMN populated (#354), and a wrong KEY yields no rows, so `out_rows` is empty and the check never runs. ⚠ Cross-checked all 17 schemas; the only one. ⚠⚠ **His proposed FIX would have been worse than the defect** — six columns inferred from two presets, where the match dict carries SIXTEEN keys across ten detectors and five are pattern-specific (`marker`, `value`, `callee`, `loop_depth`, `nesting_depth`), i.e. the ones saying what the finding FOUND. Dropping them still populates `file`/`line`, so `any_value` goes true and the guard stays quiet: **a total loud loss becomes a partial silent one.** Demonstrated — with that column list the row test passes and the field test fails. Eleven columns plus one JSON `details` cell (the `search_text` `before`/`after` shape); `sa1` -> `sa2` with `LEGACY_ENCODING_IDS`. ⚠⚠ **It ALREADY HAD a green round-trip test and why is the better half: the fixture was FABRICATED IN THE SCHEMA'S IMAGE** (`result_count`/`results`/`match_type`, none of which the tool returns) so both sides were wrong identically, **and its assertion looped over a HARDCODED list of five table keys** — `matches` absent, so the loop body ran ZERO times and the case asserted nothing. Keys now derive from the RESPONSE; row COUNT, not key presence. ⚠ Fixing the fixture alone was NOT enough — it still passed against the broken schema, because the roster was a second independent hole. ⚠⚠ **#554 by @otherjoel: the declared-forms block REPLACED the descent guard instead of preceding it**, so `_RACKET_SPLICING_HEADS` went defined-and-unreferenced and the walker descended into EVERY unrecognised form, emitting internal definitions as importable bindings. **All 8 CI jobs and the full 8,482-test local suite were GREEN on it**; he measured 86 of 87 Racket tests still passing with the guard deleted, because every assertion on that path is POSITIVE. Corpus effect `extra` 0 -> **5**, `wrong_span` 0 -> **26**, and those five were the exact names **#548's guard was added to suppress — a silent revert of a shipped fix, not a new defect.** ⚠ Caught by READING THE DIFF; no automated signal saw it. ⚠⚠ **He fixed the ROUTE, not just the defect**: the CI-safe fidelity harness was equally blind (no frozen fixture wrapped a `define` in an unrecognised form), so `guards.rkt` now fails on a Racket-free machine. His `results.json` had also been regenerated BEFORE the displacing edit and asserted `extra: 0` against code producing 5. **Also ships `racket_definition_forms`** — declare a project's own defining macros; the KIND is declared, the NAME POSITION is read off the source because one form appears in both shapes — **and `.mts`/`.cts`, which mapped to NO language while sitting in the reindex hook's watched set**: editing one spawned `index-file`, mapped nothing, dropped it as `wrong_extension`, and reported success. ⚠ The import half is inseparable — a TS specifier names the EMITTED file, so `.mts` is imported as `./foo.mjs`, and the map alone would make the file visible and its importers invisible (#550's shape). No `PARSER_GENERATION` bump: coverage, not extraction. [[a-fixture-authored-from-the-schema-tests-nothing]] [[a-guard-covered-only-by-positive-tests-can-be-deleted]]
- **Older releases (1.108.300 and earlier):** see `CHANGELOG.md`. The 1.108.182 entry ("a stall has a name and a ceiling", #375) and the 1.108.177-.181 #377 hardening arc are there in full.
- **Tests:** 8706 passed, 13 skipped, **0 failed** (1.108.303) **+ `uv run ruff check src/` clean**, measured on the settled tree after the merge, the bump and the rotation. ⚠ **8719 TOTAL, +189 over .302's 8530** — decomposed by MEASURING each push, not by counting new files: **+38 ours** (Rust qualification gates and the framework-build-tree parametrize) and **+151 from #556**. ⚠⚠ **Compare TOTALS, never passed counts, and NEVER a skip count across machines** — CI ubuntu skips 26 and windows 19 where this box skips 13, all pre-existing. I once read a CI/local skip gap as a new gate silently skipping and was WRONG; **the before/after delta on the SAME job is the only signal**. ⚠⚠ **A CONTRIBUTOR PR IS TRIAL-MERGED ONTO `main` AND RUN LOCALLY BEFORE THE MERGE, never read off the branch** — #556 was green on its own head, but branch-green is not merged-green and the merge base moves every release. It also touched `extractor.py`, `imports.py` and `index_store.py`, all three of which we had edited hours earlier. ⚠ **@otherjoel reported one failure we could not reproduce** (`test_suggest_corrections.py::test_freshness_correction_no_patch`): it reads the developer's real machine state and fails where a jcm watch service runs, which is the Practice 8 shape and his own diagnosis. It passes here. ⚠ 3.13 CI-env reproduce: **CLEAN** — 8700 passed, 19 skipped, **0 errors**, the SAME 8719 total. ⚠⚠ **A reproduce that ERRORS in `tests/test_sdist_exclusions.py` is NOT environmental noise** — that file is the sdist CREDENTIAL-LEAK guard (v0.2.6), and it errors at setup when the scratch venv must fetch the build backend with DNS blocked. Re-run it explicitly on the release tree; never wave it through. ⚠ Prior (1.108.302): 8517 passed, 13 skipped, **0 failed** (8530 total). ⚠ Prior (1.108.301): 8482 passed, 13 skipped, **0 failed** (8495 total). ⚠ Two full runs contend on the same `~/.code-index` process-lock scopes, the documented cause of .261's 47m outlier, so the 3.13 reproduce runs AFTER the local suite, never beside it.
- **Python:** >=3.10
- **Tool count:** 91 visible in `full` / 94 in catalog (front door hidden; counts verified 2026-07-30 from `jcodemunch-mcp surface`, which is the only place to get them — do NOT hand-type this; +1 v1.108.111 `get_parity_map`, +1 v1.108.112 `get_decorator_census`, +1 v1.108.113 `get_architecture_metrics`); `tool_surface=counter` exposes a 3-tool front door (`order`/`menu`/`route`) instead

## Key Files
```
src/jcodemunch_mcp/
  server.py            # MCP dispatcher (async); CLI subcommand dispatch, auth/rate-limit middleware. v1.108.292: `_mcp_instructions()`/`_tool_search_query()`/`_initialization_options()` — the MCP `initialize` `instructions` string, surface-aware (front door on `counter`, the six core tools on `full`), 1,000-char budget. ⚠ Built per `run()`, never passed to `Server(...)` at import: the surface comes from env+config and neither is settled then. ⚠⚠ It is THE ONLY prose that survives tool deferral — a host over its schema budget ships 91 bare names and withholds every description. All three transports pass it; `tests/test_mcp_instructions.py` parses the dispatcher's AST and fails if any `server.run()` goes back to a bare `create_initialization_options()`, which sends an empty field and raises nothing. ⚠ Same line also sets `Server(..., version=__version__)`: omit it and the SDK reports ITS OWN version in `serverInfo` (hosts showed `1.26.0` while we shipped 1.108.x). ⚠⚠ `__version__` is `"unknown"` under `PYTHONPATH=src`, so a green test here does NOT prove the wire carries a real number — **and CI cannot close that gap either, because it runs from source too.** ⚠ **Closed MANUALLY on 2026-08-24 against the PUBLISHED artifact** (#536): a real stdio handshake to `jcodemunch-mcp==1.108.293` in a clean venv returns `serverInfo {"name":"jcodemunch-mcp","version":"1.108.293"}` and a non-empty `instructions`. Re-verify this way after any change to the handshake; a green suite still does not prove it. ⚠⚠ **The first probe was WRONG and the reason generalises: `uvx jcodemunch-mcp` served a CACHED 1.108.275**, which predates both fixes, so the wire showed the SDK's own version and no instructions — i.e. **exactly the pre-fix symptoms, from a stale cache rather than a defect.** Pin the version and build a fresh venv (`uv venv` + `uv pip install "jcodemunch-mcp==X.Y.Z"`); never probe through bare `uvx` and never read its output as evidence about what we ship. v1.108.66: the Counter front door (order/menu/route) — _effective_surface()/_counter_front_door_tools()/_raw_catalog_tools()/_catalog_names() + surface-collapse in _build_tools_list + _handle_order/menu/route + early front-door branch in call_tool
  counter.py           # (v1.108.66) The Counter: adaptive tool surface logic (pure, no server import). FRONT_DOOR set; STATE_CHANGING_ACTIONS + exec/write-verb tripwire (_FORBIDDEN_VERB_RE) → order_gate(); idf-weighted search_catalog() for menu; _INTENT_RULES + classify_intent()/shape_execute_args() for route. v1.108.124: EXAMPLES (curated per-action example arg objects) + example_for() — catalog_entry attaches `example` into menu rows, _handle_route uses it as the args_template fallback; validated against live inputSchemas in test_counter.py. server.py owns Tool registration + call_tool re-dispatch; counter.py is fed plain data
  watcher.py           # WatcherManager class (dynamic folder watching); watch_folders() wrapper
  progress.py          # MCP progress notifications; ProgressReporter (thread-safe, monotonic), make_progress_notify() bridge. v1.108.189 adds HeartbeatReporter (#383) — the token-less fallback: elapsed-time WARNING lines on the LOG channel, duck-typing ProgressReporter so the dispatcher wires either identically. ⚠ Holds NO notify channel/session ref by construction (not in __slots__) and close() yields no futures, so it CANNOT become an unrequested notification; silent until the first JCODEMUNCH_HEARTBEAT_SECONDS elapses, and finish() is silent if it never spoke
  security.py          # Path validation, skip patterns, file caps. ⚠ **A build tree is excluded in ELEVEN spellings** — `build`, `.build` and (v1.108.295) `_build`, which is what Elixir/Mix, Sphinx and Dune use — plus (v1.108.303) the eight DOTTED framework trees `.next`/`.nuxt`/`.output`/`.svelte-kit`/`.angular`/`.turbo`/`.parcel-cache`/`.dart_tool`. ⚠⚠ **`.next/server/**` holds a TRANSPILED copy of the pages the user WROTE**, so a Next.js project got its own source twice with the generated copy competing in ranking. ⚠ **DOTTED ONLY** — `out`, `bin`, `obj`, `coverage` and `public` all name real source dirs, and `tests/test_framework_build_trees_are_skipped.py` asserts their ABSENCE as firmly as the eight additions. **`mix` copies dependency SOURCES into `_build`**, so this was the v1.108.234 duplicate-source-tree defect wearing a third name, not a new one. ⚠ Add spellings to `_SKIP_DIRECTORY_NAMES`, never to a derived export — `SKIP_DIRECTORIES` (local walk) and `SKIP_PATTERNS` (GitHub indexer) both derive from it, and editing one reaches only half the product. `verify_package_integrity()` runs on EVERY CLI invocation and its checks are ordered cheapest-first — that ordering IS the fix. ⚠⚠ `packages_distributions()` maps every distribution on `sys.path` to answer a question about ONE: **3.35 s uncached on a box with 894 top-level names, and it returned nothing there** (source tree, no distribution describes it). Targeted `distribution("jcodemunch-mcp")` settles the ordinary install in **5 ms**; the map is reached only when the official dist is absent or did not provide the running module. ⚠⚠ **The map must stay REACHABLE** — it alone can NAME the offending distribution, which is the whole warning; a guard that just banned the call would be satisfied by deleting the security check. ⚠ **Installed-and-correctly-named is NOT sufficient**, so the fast path also proves the official dist owns the running `__file__`. ⚠ Invisible while the CLI was human-typed; the whole cost of a hook once hooks spawn it per tool call (`hook-pretooluse` 4.0s -> 0.94s, the rest being the server import). `tests/test_integrity_check_cost.py` asserts the COST as a property, never the call order
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
    schemas/             # Per-tool custom encoders (tier-1, phase 2+); auto-discovered registry. ⚠⚠ **A schema that disagrees with its producer about the table KEY is INVISIBLE to the fail-closed guard**: `schema_driven` raises when a table has rows but no declared column populated (#354), and a wrong key yields NO rows, so `out_rows` is empty and the check never runs. That is #553 -- `search_ast` declared `results` while the tool returned `matches`, and served an empty table for every language and preset. ⚠ `tests/test_search_ast_encoder_contract.py` holds the CI-time ratchet: every declared table key must name something its tool emits. ⚠⚠ **(#555) `sd.encode` now also fails closed at RUNTIME on a list-of-dicts under a key no `TableSpec` declares.** It runs on the dict handed to `encode`, which is POST-transform BY CONSTRUCTION — `search_text._flatten` has already removed the public `results` before the guard sees it, so pre-flattening schemas need NO exemption. **Scanning the RAW response instead flags `search_text` on every call**, and an allowlist entry for it would have been the wrong fix to the right symptom. `allow_undeclared=(...)` is explicit and per-key. Raises rather than warns (dispatcher falls back to JSON, data survives); the full suite is clean with it active, so nothing legitimately drops a table. ⚠ **Columns are the second half and the near-miss**: a heterogeneous row set (search_ast carries 16 keys across 10 detectors, 5 of them pattern-specific) loses its payload silently if only the common columns are declared, because `file`/`line` populate and `any_value` goes true. Pattern-specific keys ride as one JSON cell, the `search_text` `before`/`after` shape. A table-key or column change is a WIRE change: bump `ENCODING_ID` and add the old one to `LEGACY_ENCODING_IDS`
  investigator/
    deletion_safety.py           # (v1.108.214) tri-state proof obligations; `investigate_deletion_safety`. NOT an MCP tool
    retrieval_counterfactual.py  # (v1.108.217) `explain_route(task, expected_action)` / `explain_misses(per_query)` — names the FIRST gate that excluded an action: `catalog_absent` / `empty_query` / `rule_preempted` / `no_lexical_overlap` / `ranked_below_cutoff`, in pipeline order (reporting more than the first is reporting consequences). ⚠ Uses the SAME `counter` functions the live front door uses — never a second scorer. ⚠⚠ `rule_preempted` = **never scored**, because `route` runs the fallback ONLY when no rule matched; do NOT read it as a ranking loss. NOT an MCP tool (item 3 moratorium), test-asserted
    reuse_audit.py               # (v1.108.296) `investigate_reuse_before_write(repo, intent)` -- reuse-before-write as proof obligations. Verdicts reuse_available/adapt_candidate/write_justified/lexical_only/not_established; obligations intent_is_searchable (fatal), no_name_twin, no_lexical_match, no_semantic_match, no_structural_twin (optional, EXCLUDED from `_verdict` and `_confidence` when no `proposed_signature` was passed, still shown in `obligations`). ⚠⚠ **`lexical_only` is the whole point**: an intent of 'modal' shares no token with an existing `Dialog`, so an unavailable embedding channel goes UNESTABLISHED and degrades the verdict instead of licensing a write. `no_provider` and `repo_not_embedded` are separate states with OPPOSITE advice. ⚠⚠ **`search_symbols` emits `score` ONLY under `debug=True`** -- without it every row squashes to 0.0, `strong`/`partial` are empty BY CONSTRUCTION and `strong_match`/`adapt_floor` grade nothing. ~25 ms/sweep vs a 0.5 ms cache hit; losing the cache is correct (an absence claim replayed from a cached row is #377 item 3). ⚠⚠ **Sample `_index_was_rewritten` BEFORE any channel runs, never after** -- our own semantic read opens a read-WRITE connection and moves the very mtime the probe compares, so a post-scan sample reported a rewrite we caused ourselves and made `write_justified` UNREACHABLE. ⚠ `has_any()` returning None is UNKNOWN, not embedded-and-clean. ⚠ A refutation backed only by symbols proved dead yields `adapt_candidate` + `dead_matches`, never `reuse_available` -- and is ordered AHEAD of the absence blockers, because a positive hit is not an absence claim. ⚠ `_STRONG_MATCH`/`_ADAPT_FLOOR` are SEEDED, not calibrated, and had never been evaluated against a non-zero score before v1.108.296. NOT an MCP tool (moratorium: control route@1 40.0% vs a 55.0% bar), registered in `WITHHELD`
  storage/
    selective.py       # (v1.108.216, #398 Arc 2) `SelectiveIndexView` — a `CodeIndex`-SHAPED read view over metadata + named symbol rows. **NOT a subclass**: subclassing would inherit CodeIndex's corpus-wide methods silently operating over a partial `symbols` list, the one outcome this exists to make impossible. `EXACT_FIELDS` are copied onto the instance at construction; **everything else falls through `__getattr__` and promotes to one full load** — including fields invented later. `CORPUS_WIDE` documents the known ones and every entry is parametrized in the test. ⚠ `_PROVENANCE` (`_db_path`/`_loaded_mtime_ns`) MUST stay in `__slots__` — see Current State
    generation.py      # (v1.108.215, #398 Arc 1) THE READ CONTRACT, both halves. `IndexGeneration`/`describe(index)` — the ONE place `indexed_at`/`git_head`/`_db_path`/`_loaded_mtime_ns` are read off an index; empty string normalises to None once (three surfaces used to disagree). `rewritten_since_load` keeps unknown ≠ changed. `connect_readonly(db_path)` / `readonly_uri` / `wal_sidecar_present` — ⚠⚠ **neither single flag is right**: plain `mode=ro` CREATES `-wal`/`-shm` when absent (moves `_db_mtime_ns`, the .185 `rebuilding` bug), `immutable=1` cannot READ them when present (measured: raises `no such table`, which `has_any()` maps to a confident False). Reads the WAL when its sidecar exists, immutably when it does not. **Every read-only opener in the tree routes through this**; `test_generation_contract.py` fails on a hand-rolled `?mode=ro` URI anywhere else
    sqlite_store.py    # CodeIndex, save/load/incremental_save, WAL-aware LRU cache (_db_mtime_ns); get_source_root(). v1.106.0: save_index + migrate_from_json acquire `indexwrite` process_locks before SQLite writes, body extracted to `_save_index_locked` / `_migrate_from_json_locked`; serialises across MCP processes
    process_locks.py   # v1.106.0: generic multi-process coordination (acquire/release/inspect/held). Atomic O_EXCL + fcntl flock (Unix) + PID liveness + scoped lock files. Scopes: `watcher` (one-watcher-per-repo, shared with watcher.py) + `indexwrite` (save coordination). Metadata: pid/client_id/scope/target/started_at. JCODEMUNCH_CLIENT_ID env var sets friendly client name (defaults to sys.argv[0] basename)
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
    refresh.py         # (v1.108.259, #395) Bounded, resumable repo-wide refresh. `run()` slices the corpus through `index_folder(paths=..., force_reparse=True)` under a wall-clock + file budget, persisting a cursor to `<CODE_INDEX_PATH>/refresh_state/<owner>__<name>.json` (atomic write) so N short windows converge like one long one. `status()` reports progress and does NO work. ⚠⚠ Stamps `parser_generation` ONLY after re-running discovery proves full-corpus coverage — drift appends and DEFERS, batch errors block, and `stamp_parser_generation` refuses to go backwards. ⚠⚠ **That check asked only whether the corpus GREW, and for its whole life could not see the opposite failure** (2026-08-25): a source root that has moved, been unmounted, or been cleaned makes discovery return `[]`, so `current` and `known` are both empty, nothing drifts, nothing errors, and the campaign stamps the target generation having re-parsed ZERO files. **UNREPAIRABLE — a stamp equal to the constant is indistinguishable from a genuine one, so the tool built to prevent the exempt bucket was putting indexes INTO it.** Now refuses on `corpus_unreadable` (discovery empty, index not) and `index_unreadable` (`_index_files` returned None — UNKNOWN blocks, same rule as `has_any()`). ⚠ EMPTY-vs-NON-EMPTY deliberately, NOT a shrink threshold: a repo may legitimately lose most of its files, so partial shortfall is DISCLOSED as `indexed_files_not_reparsed` rather than guessed at. ⚠ Found by running the documented command on the three pinned benchmark corpora — bare `.git` dirs, 8,220 stale symbols, all three stamped in under a second. ⚠ `use_ai_summaries` defaults FALSE here (opposite of `index_folder`): a scheduled job must not bill a paid summarizer unasked
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
    get_repo_health.py        # get_repo_health: one-call triage snapshot (delegate aggregator); includes six-axis `radar` field (v1.87.0)
    health_radar.py           # Six-axis health radar (complexity/dead_code/cycles/coupling/test_gap/churn_surface) + diff_health_radar pure-function tool for PR-time diff-grade reporting (v1.87.0). Phase 7 (v1.100.0): optional 7th axis runtime_coverage when caller passes runtime_coverage_pct; axis is omitted otherwise so the composite stays comparable against pre-Phase-7 baselines. diff_radar walks the axes dict generically — picks up the new axis automatically.
    get_untested_symbols.py   # get_untested_symbols: find functions with no test-file reachability (import graph + name matching)
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

⚠ Shipped in 1.108.271. Kept here rather than in the rotation because it is a
STANDING warning about a measurement, not a release note that ages out.

⚠⚠ **Do not quote the arm numbers; the honesty gate fired.** Four arms x three
repeats on FastAPI at a pinned commit, answering an
[r/codex benchmark](https://www.reddit.com/r/codex/comments/1vjfepe/) that put
jCodeMunch at **+28.45% on Codex** and **-3.34% on OpenCode**. Largest arm
difference 568,617 tokens against a baseline varying against ITSELF by
1,143,229. Directions were incoherent too (`full`, carrying 24,007 tokens of
schema, came out CHEAPER than baseline). The hypothesis is **untested, not
disproven** — the instrument cannot resolve an effect that size.

⚠⚠ **The finding that outlived the arms, and it corrects a claim this project
made: 86% of baseline input is CACHED.** The schema block is stable across
requests, so it is paid at full rate roughly ONCE and at cache-read rates after.
Any framing of "24,007 tokens in every request" is wrong, and that framing was
used here before measuring. **The fixed-cost story is a WEAKER explanation for
the r/codex result than the raw number suggests, not a stronger one.**
`--surface-only` still measures the schema exactly (90 tools / 24,007 tokens at
default `full`, 6 / 1,030 at `counter`) and needs no API credits; what it does
not measure is what that costs in practice.

⚠ **Those two numbers are a 2026-07 snapshot from THIS harness and are not the
canonical figures.** `benchmarks/schema_baseline.json` is, written by
`benchmarks/harness/capture_schema_baseline.py` and guarded by
`tests/test_schema_budget.py`; it counts a different payload shape, so the two
sets will never agree digit for digit and neither is wrong. Quote the baseline
file. ⚠⚠ **Reconciled 2026-08-14: the Counter avoids 95.9%, not the ~98% that
`run_route_recall.py` asserted for two months** — that literal is now computed
from the baseline at runtime, with a test that fails if any schema-saving
percentage returns to that file. **The gap existed because the budget guardrail
only walked `tool_profile`, which does not apply to the front door at all**, so
the single largest lever in the project had no test under it.

⚠⚠ **The same run killed `tool_profile: "standard"` as a token lever: it drops 9
of 91 tools and 5.7% of the payload.** Anyone selecting it as the safe middle
setting gets nothing measurable. `core` (74.0%) and `counter` (95.9%) are the
only two settings that move the number; there is no gradient between them, and
the config surface currently implies there is. ⚠ Where the rest sits, from
`--breakdown`: under `full`, tool DESCRIPTIONS are 36% of the payload and
`compact_schemas` rewrites input schemas only, never descriptions. Schema
compaction is near its floor; descriptions are untouched ground.

⚠ Design flaw recorded so nobody repeats it: summing per-invocation input across
a RESUMED conversation counts accumulated context on every step, so the total is
dominated by how much the agent read early on, which compounds.

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
- **A competitor's fix list is a free defect probe.** 08-22: a rival's
  `fix(gini): measure a file's lines as its own span, not the sum of every node`
  named our defect precisely enough to confirm in one query —
  `get_architecture_metrics` summed `byte_length` over nested symbols, inflating
  byte mass 33.4% overall and up to 2.28x per file. Read their commit TITLES
  against whatever we built the same way; it is minutes, and it finds what our
  own tests were written not to see. See CHANGELOG `[Unreleased]`.

## Issue + release policy (2026-07-28)

**1. One issue, one verdict.** A multi-finding report gets SPLIT at triage into
one issue per finding, cross-linked, credit on each. Nothing is dropped and no
detail is discouraged. The reason is closure mechanics: a 4-finding issue closes
only when the last one settles, so three finished fixes sit behind one
unfinished conversation and the tracker cannot say which is which.

⚠ **This is the correction to a mistake we made deliberately.** On 2026-07-27 we
CONSOLIDATED five jdoc issues (#80/#89/#90/#93) into one gate, #95. It cut the
open count from 5 to 1 and manufactured a single artifact with the power to
block a release. **Tracker-tidiness and granularity pull in opposite directions;
do not optimize the count.**

**2. A release is NEVER blocked on an open issue**, including a verification we
asked for. Done + tested + green ships on schedule, carrying a plain-language
verification-status line (the #95 disclosure sentence is the template; it is
deliberately weaker than a sign-off and the changelog must never blur the two).
Late re-verification counts IN FULL and is announced retroactively. Nothing
expires. **Every timebox names its default action** ("verification by X, or Y
ships with disclosure Z"); a date with no stated consequence is a wish.

⚠ **The point is that a reviewer's thoroughness must never become a veto.** If
being careful can stall a release, careful review becomes expensive to accept,
which is backwards.

**2e. NEVER BATCH OUR RELEASE BEHIND SOMEONE ELSE'S CLOCK** (jjg, 2026-08-18,
after it happened). Policy 2 says a release is never blocked on an open issue.
**The way that rule gets broken is not by someone overruling it — it is by an
apparently sensible batching argument that never mentions it.**

⚠⚠ **The exact failure, recorded because it was MINE and it sounded reasonable.**
On 2026-08-18, five fixes were merged and green (#488/#489/#490's siblings,
#495). I recommended holding the release until 08-19/08-20 so it could include
#504 and #447, on the grounds that each of our releases re-conflicts elfrost's
CLA-blocked #443 and batching means resolving once instead of three times. jjg
accepted it. **That recommendation coupled our shipping schedule to a
contributor's CLA signature and a first-time reporter's availability, which is
the precise outcome policy 2 exists to prevent.**

⚠⚠ **It was also wrong ON THE MERITS, which is the part that generalises.**
Batching reduces the NUMBER of conflict resolutions, not whether they happen —
#443 conflicts on whatever release comes next, whenever that is. Each resolution
is a scripted three-way merge plus one suite run, measured at minutes. **The
trade was "finished, tested, user-facing fixes sit unreleased for two days" in
exchange for "we do a cheap chore once instead of three times." Weigh the cost
of the chore against the cost of the delay before proposing a batch; here it was
not close.**

⚠ **The timeboxes are NOT the problem and must not be "fixed".** Every one names
a default that ships the work regardless (policy 3a). A posted window decides
whose commit it is, never whether the fix ships or whether we can release. If a
window ever appears to block a release, the batching decision is what is
blocking it, not the window.

⚠ **The test, before proposing to hold a release:** name the thing being waited
for, and whether it is OURS. If it is anyone else's action — a signature, a PR, a
reply, a re-run — the answer is ship now and let them ride the next one.
Contributor work is never worse off for this: their default still fires, their
credit is unchanged, and their PR merges into a smaller diff.

⚠ **Corollary: "reduce OUR churn" is not a release criterion.** Conflict
resolution, re-runs and re-merges are our costs to absorb. The moment avoiding
them starts shaping WHEN users get fixes, the optimisation has inverted — we are
spending their latency to buy our convenience. [[never-batch-a-release-behind-someone-elses-clock]]

**2f. THE ONE CASE WHERE NOT CUTTING A RELEASE IS LEGAL — and it is narrow**
(jjg, 2026-08-20). 2e forbids holding a release behind someone else's clock.
This is not that, and the difference has to be stated precisely or 2f becomes
the loophole that kills 2e.

⚠⚠ **THE DISCRIMINATOR IS WHETHER A USER IS WAITING FOR ANYTHING IN THE BLOCK.**
In #443 we held a SECURITY FIX behind a contributor's CLA: real users, real
exposure, eight days. In 1.108.289 the entire `[Unreleased]` block is licence
metadata whose ONLY beneficiary is the customer we would be waiting on.
**Shipping it gets no user anything.** So the timing question is not "do we make
users wait" — it is "what serves the one party this release is for", which is a
different question with a different answer.

⚠ **The asymmetry that decides it: released metadata is PERMANENT per version,
unreleased metadata is FREE.** Cutting .289 before the customer confirms the
identifier form risks a THIRD spelling (.288 `-1.1`, .289 `-1`, .290 whatever),
and their allowlist fans out across all three. **This is the same immutability
argument that justified deciding FAST, pointing the other way at the release
step.** Deciding early is cheap; publishing early is not.

⚠⚠ **THE TEST, and it must be applied every time before invoking 2f: name what
is in the block and who is waiting for it. If ANY entry is a fix, a feature or a
correctness change, 2f does not apply and 2e governs — cut it now.** A block that
is entirely metadata for one named recipient is the only shape this covers.

⚠ **Both triggers fire independently and neither can be deferred**: the next
content update ships it regardless of any reply, and a reply ships it regardless
of what else is ready. **A held release with no trigger is a forgotten release**,
which is why the hold is recorded in Current State where it is read every
session, not only here.

⚠ **"We never wait for a reply to ship a fix; we can decline to CUT a release
whose only content is a thing the recipient has not confirmed."** Those are
different acts. Only the first is what 2 and 2e protect against.

**3. A contributor's PR is never the only path.** Timebox it and keep our own
path warm (#388 taught this the expensive way).

**3a. NO TIMEBOX WE OFFER RUNS LONGER THAN 24 HOURS** (jjg, 2026-08-14, widened
the same day from the CLA-only version). It covers **every** shape: signing the
CLA, opening a PR already written, and taking an issue to implement. The CLA case
is the easiest to justify — CLA Assistant prompts the moment a PR opens and
signing takes about 30 seconds, so a longer window parks a finished, green,
reviewed fix behind a form — but the rule is not limited to it.

⚠⚠ **The window is only fair BECAUSE the default action preserves credit.** At
expiry we implement the fix ourselves and credit them in the CHANGELOG, the
release notes and the close comment. So the 24 hours decide whose COMMIT it is,
never whether they are credited and never whether the fix ships. Quote the
default in the same comment as the deadline — a 24-hour clock with an unstated
consequence reads as a threat, and it is not one.

⚠ **An extension the contributor ASKS FOR is not the same as a default we hand
out**, and CONTRIBUTING.md invites the ask by name. Hold it when they ask; the
clock exists to stop work going quiet, not to catch anyone out.

⚠ **Stated consequence, not hidden**: on an IMPLEMENTATION handoff, 24 hours
means in practice that we implement it and they are credited, because nobody
lands an additive-schema-plus-dispatcher change around a job in a day. That is a
change in what a handoff IS, not only in how long it lasts. It is the intended
trade — our throughput over their commit — and it should be made in the open
rather than discovered at expiry.

**3d. `license/cla` IS A REQUIRED STATUS CHECK ON THE DEFAULT BRANCH OF ALL
THREE REPOS** (jjg, 2026-08-17 for jcm; extended suite-wide 2026-08-21).
Enabled because it was NOT one: until this date the repo had **no branch
protection, no rulesets and no required checks**, so the CLA was read but never
enforced and one distracted click could have merged unsigned code. Open PRs now
read `MERGEABLE/BLOCKED` rather than `MERGEABLE/UNSTABLE`.

⚠⚠ **For four days this was fixed in ONE repo of three, which is the recurring
shape.** jdoc was protected but required NOTHING; jdata had **no protection at
all**. Measured 2026-08-21 on jdata PR #5: the CLA was genuinely unsigned, the PR
read `MERGEABLE/UNSTABLE`, and nothing would have stopped the merge. **A setting
fixed in one repo of a suite is fixed in one repo** — the same sentence jdata's
own brief already carried about `fork-pr-contributor-approval`, written after a
contributor hit it first. All three now read identically: `contexts
["license/cla"]`, `strict false`, `enforce_admins false`, force-push and deletion
off.

```bash
# All three; the default branch is `main` for jcm and `master` for jdoc/jdata.
for r in jcodemunch-mcp:main jdocmunch-mcp:master jdatamunch-mcp:master; do
  GITHUB_TOKEN="" gh api "repos/jgravelle/${r%%:*}/branches/${r##*:}/protection"     --jq '{contexts:.required_status_checks.contexts, strict:.required_status_checks.strict, enforce_admins:.enforce_admins.enabled}'
done
```

⚠ **`enforce_admins: false` and `strict: false` are both deliberate.** The admin
override is what lets jjg land a merge pushed to a contributor's fork; `strict`
would force every PR to be up-to-date with `main` before merging, i.e. a rebase
after every release — the exact churn that kept #443 dark for five days.
⚠ Enabling protection also turned OFF force-push and deletion on `main`.
⚠⚠ **This composes with the missing-status hazard and now FAILS CLOSED.** ANY
new head — our push to a fork, or the contributor's own merge of `main` —
arrives with `license/cla` absent, and with the check required that reads as
`BLOCKED` until the bot posts on that SHA. Correct, and it will look like a new
problem the first time.
⚠⚠ **NOTHING IS ERASED AND THE WORD MATTERS — corrected 2026-08-24 on #535.**
This entry said a push "wipes" the status, which frames a per-SHA reporting
model as an act of destruction and sends you chasing the bot or the
contributor's signature. **Measured:** `license/cla` is a **legacy commit
status**, not a check run — every other check on the PR is a `check-run` from
the `github-actions` app, which GitHub re-runs per head automatically; a legacy
status is a record posted to ONE SHA by an external service, and a new commit
starts life with zero of them. On #535 the old head `0db4478` still read
`license/cla success` while the new head `ea12029` read `count=0`. **The old
status was untouched, and the signature — stored per ACCOUNT at
cla-assistant.io — was never in question.**
⚠ **The consequence is the useful part: the gate cannot tell "not signed" from
"not reported", so it fails closed to the same `BLOCKED` for both.** Absent
still means DO NOT MERGE. But the remedy is to get a status posted on the
current head, never to re-verify an agreement that did not change.
⚠ **"Usually under a minute" was optimistic.** On #535 the bot had not posted
30+ minutes after the new head, and it has never commented on that PR at all —
it posted the status directly, which is what it does when the author signed on
an earlier PR.

⚠⚠ **THE RE-TRIGGER, AND IT IS OURS — no contributor action, ~25 seconds**
(established 2026-08-24, #535). `license/cla` comes from a REPO WEBHOOK to
`https://cla-assistant.io/github/webhook/<repo>` on `pull_request`, not from
any in-repo workflow. **The event is not lost and the bot is not down** — the
deliveries list showed his `synchronize` arriving and answering `200 OK`, with
no status posted. **Redelivering that same event makes it post.**

```bash
HID=$(GITHUB_TOKEN="" gh api repos/jgravelle/<repo>/hooks --jq '.[0].id')
# ⚠ jq mangles delivery ids (past float precision) — read them with python.
GITHUB_TOKEN="" gh api "repos/jgravelle/<repo>/hooks/$HID/deliveries?per_page=15" > dv.json
python -c "import json;[print(x['delivered_at'][5:16],x['event']+'/'+str(x.get('action')),x['status_code'],x['id']) for x in json.load(open('dv.json'))[:8]]"
GITHUB_TOKEN="" gh api --method POST "repos/jgravelle/<repo>/hooks/$HID/deliveries/<exact-id>/attempts"
```

⚠ **Diagnose before reaching for it.** Both #535 deliveries were `synchronize`
on a `draft: true` PR and only the later one stayed silent, so **draft is NOT
the discriminator** — the distinguishing feature was a MERGE COMMIT pulling in
commits authored by us. Check the deliveries list first; a delivery that never
arrived is a different problem from one that arrived and did nothing.

⚠⚠ **NEVER POST THE STATUS OURSELVES.** We hold admin and the Status API would
clear the gate in one call. `license/cla` is a legal assertion about an
agreement, and a maintainer-authored `success` is a forged one — it would also
be indistinguishable from the genuine article afterwards. **Redelivering makes
CLA Assistant reach its OWN verdict, which is the whole difference.** If a
redeliver does not produce a status, the answer is a `recheck` comment or a
contributor push, never a hand-written status.
⚠⚠ **It does NOT solve vendor time-wasting and must not be sold as if it does.**
Signing costs a campaign nothing — #485's author has 748 merged PRs across
GitHub, so they clear CLAs routinely. The only contributor this gate blocked in
its first hour was **elfrost**, who found a real security defect. **Legal
exposure and spam are different problems; this closes the first, 3c closes the
second.**

**3c. PROFILE THE AUTHOR BEFORE REVIEWING A VENDOR-SHAPED PR** (jjg,
2026-08-17). Any PR adding a named third-party provider, gateway, SDK or
endpoint gets three queries FIRST, before a line of the diff is read:

```bash
GITHUB_TOKEN="" gh api users/<login> --jq '"created=\(.created_at[0:10]) repos=\(.public_repos) company=\(.company) bio=\(.bio)"'
GITHUB_TOKEN="" gh api "search/issues?q=is:pr+author:<login>&per_page=1" --jq .total_count
GITHUB_TOKEN="" gh api "search/issues?q=is:pr+author:<login>+<vendor>+in:title&per_page=1" --jq .total_count
```

⚠⚠ **The discriminator is the RATIO, not the volume.** A prolific contributor
is fine. #485's author had **3,089 PRs, 2,242 with "minimax" in the title
alone (73%), ~19/day since March**, and a profile reading
`company: Independent Developer`. #487's had 87 forks, 86 PRs, all OrcaRouter,
on a 7-day-old account. **Both were found in under a minute; #485 was reviewed
in depth twice before anyone looked.** That is the cost this rule removes.

⚠ **Also check whether we have a DEMAND signal**, which is the actual #380 bar
and is one query:
`gh api "search/issues?q=repo:jgravelle/jcodemunch-mcp+<vendor>"`. MiniMax
cleared it honestly as a summarizer (#184, a user asking); MiniMax TTS did not,
and the only tracker mention was the PR itself.

⚠⚠ **Quality is NOT the discriminator and must not be used as one.** #485's
diff was better than most human PRs — a real `output_format`-versus-container
finding, a three-point review addressed in hours, a self-corrected test count.
**Good work aimed at something nobody asked for is still something nobody asked
for.** Close on demand, credit the finding, and say plainly that quality was not
the reason.

⚠ **Do not assert employment you cannot prove.** State the numbers, ask the
affiliation question on the thread, and let the ratio speak. #487's author
volunteered their affiliation unprompted and it cost them nothing — that is the
contrast worth drawing, not an accusation.

⚠⚠ **A posted timebox's default can be RETRACTED IN THE OPEN when the facts
change, but never silently.** #485's clock promised that at expiry "we implement
the same change ourselves" and that the window "never decides whether the
feature ships." The authorship-and-credit half was honoured; the feature half
was withdrawn ON THE THREAD, with the reason, because it was written before the
campaign was known. **Letting a promise lapse quietly is the failure mode;
retracting it out loud is not.**

**3b. A MERGEABLE contributor PR merges BEFORE any changelog-touching work of
our own** (jjg, 2026-08-14). Not a courtesy and not a preference — a measured
cost. Every entry we add lands in the same `[Unreleased]` block a contributor's
entry occupies, so each of our merges puts their PR into conflict, and a
CONFLICTING fork PR has **no `refs/pull/N/merge`** and therefore gets no CI at
all. Their branch goes dark for a reason that has nothing to do with their
change.

⚠⚠ **Measured 2026-08-14: #443 conflicted FIVE TIMES IN ONE DAY** — twice from
our own PR merges, twice from releases, once from the docs work — and every one
was resolved by us pushing to their fork. **Five is not five incidents, it is
one wrong merge order repeated.**

⚠ **The boundary, or the rule fails on its first real case.** A BLOCKED
contributor PR cannot go first: #443 was unsigned-CLA the whole time, so
"contributor first" was never available. When it is blocked we ship anyway
(policy 2 — a release is never blocked on an open issue) and **we own the
resolution**: push the merge to their branch, resolve it ourselves, and say on
the thread that the conflict was ours. **This rule is about ORDER when we have a
choice, never about holding our work behind someone else's form.**

⚠⚠ **RE-READ THE THREAD FOR THE OPERATIVE DATE; DO NOT QUOTE ONE FROM HERE OR
FROM MEMORY.** Measured 2026-08-17 on #443: **2026-08-26 was posted 08-12
18:19**, elfrost accepted it on 08-13 13:05 quoting that date, and **08-20 was
posted 85 minutes later at 14:30** and reaffirmed thirteen times since. The
contributor never acknowledged the change and may still be planning around the
older date — which is the concrete harm, not the six days. **A thread can carry
two dates; only the query settles which is in force:**

```bash
GITHUB_TOKEN="" gh api repos/jgravelle/<repo>/issues/<n>/comments \
  --jq '.[] | select(.user.login=="jgravelle") | "\(.created_at[0:16])"' # then grep bodies for dates
```

⚠ The 08-12 wording also promised **"your authorship on the commit"** where the
08-20 wording promises **"credit"** — a second, quieter downgrade in the same
swap. When restating a default, restate the STRONGER posted version or say
explicitly that it changed. jjg's call on 2026-08-17 was that **08-20 stands**;
the lesson recorded here is the silent substitution, not the date.

⚠ **Do not shorten a timebox already posted.** State the new window on new PRs.
A public promise to a contributor outlives the policy that produced it, and
retracting one to save six days costs more than the six days. ⚠⚠ **Reaffirmed by
jjg when this rule widened: #447 (2026-08-20), #465 (2026-08-21) and #456
(2026-08-27) stand AS POSTED.** The new ceiling applies to timeboxes offered
after that date, and to nothing already promised.

⚠⚠ **CLOSED OUT 2026-08-20, and 3a is now ABSOLUTE: 24 hours, no exceptions,
never again.** jjg, on reading the 08-12 comment on #443 offering **2026-08-26**:
"Not again. 24 hour. Tops. Ever." Every grandfathered window above has since
expired or closed and there are no live long timeboxes; **the grandfathering
clause is spent and must not be revived as precedent for a new one.** The next
posted window that exceeds 24 hours is a mistake regardless of what produced it.

⚠⚠ **The failure mode has a NAME now and naming it is the point: a CLA hostage
negotiation.** #443 went eight days — a real security fix, reviewed and green,
held behind a 30-second form, while SEVEN of our own merges conflicted its
branch. Not one of those days bought anything. The window never decides whether
the fix ships (the default action ships it) and never decides credit (the default
preserves it), so **a window longer than 24 hours purchases exactly one thing:
the chance the contributor's commit is theirs — and it pays for that chance in
the user's exposure to an unfixed defect.** Twenty-four hours is already generous
for that trade; eight days is not a trade at all.

⚠⚠ **Do NOT answer "an issue is stuck" with aggregate stats.** Measured
2026-07-28: jcm median 0 days to close (80 issues, 70 within a day, 2 ever past
a week); jdoc median 1 day. **Those numbers are TRUE and they are NOT a
response.** jjg: a fraction of an eyelash commands full attention and impairs
binocularity; "it is a small fraction of your body" helps nobody. The cost of a
blocked issue is CONCENTRATED, not distributed. Design the fix at the OUTLIER
(policy 2), never at the median. See
[[feedback_dont_answer_pain_with_aggregates]].

Surfaces: `CONTRIBUTING.md` ("One issue, one verdict" + "A release is never
blocked on an open issue") and `.github/ISSUE_TEMPLATE/` (bug_report,
multi_finding_report, config.yml pointing parked design at ROADMAP.md).

⚠ **CONTRIBUTING.md is now IDENTICAL suite-wide** (jcm/jdoc/jdata differ only by
product name, repo slug, and jcm's extra quality-gates section). Two pre-existing
bugs fell out of normalizing it: **the documented install command
`pip install -e ".[test]"` was WRONG IN ALL THREE REPOS** — no repo declares a
`test` extra; dev deps live in a PEP 735 `[dependency-groups]` block, so the
FIRST command a new contributor ran failed. And jcm's
`README.md#license-dual-use` anchor pointed at a heading that does not exist
(`## License`). ⚠ **CI installs with `uv sync` and never runs the command the
docs give a human**, which is why this survived: the thing we test is not the
thing they do.

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
