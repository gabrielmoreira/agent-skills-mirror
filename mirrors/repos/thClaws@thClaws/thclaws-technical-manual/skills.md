# Skills

User-defined prompt+script bundles that extend the agent without modifying core code. A skill is a directory with a `SKILL.md` (YAML frontmatter + markdown instructions) and an optional `scripts/` sibling. The agent loads the skill on demand via the `Skill` tool, which materializes the body, substitutes path placeholders, and auto-surfaces runtime hints.

This doc covers the discovery model, lazy-loading internals, in-skill script execution (interpreter auto-detection + requirements.txt + auto-venv), the three system-prompt rendering strategies, install dispatch (git + zip + marketplace), trust/policy gates, and the lifecycle from `/skill install` to first `Skill(name: …)` call.

**Source modules:**
- `crates/core/src/skills.rs` — types, discovery, lazy loading, install dispatch, `Skill` / `SkillList` / `SkillSearch` tools
- `crates/core/src/shared_session.rs` — system-prompt rendering (`append_skills_section`)
- `crates/core/src/config.rs` — `skills_listing_strategy` field + project merge boundary
- `crates/core/src/plugins.rs` — `plugin_skill_dirs()` for plugin-contributed skills
- `crates/core/src/tools/bash.rs` — `maybe_wrap_with_venv()` (Python skills' transparent venv layer)
- `crates/core/src/policy/mod.rs` — `external_scripts_disallowed()` (EE policy gate)
- `crates/core/src/memory.rs` — `parse_frontmatter()` (shared YAML reader)
- `crates/core/src/marketplace.rs` — catalogue used to resolve `name → install_url`

---

## 1. Anatomy of a skill

```
<skill_dir>/
├── SKILL.md            # required — YAML frontmatter + markdown body
├── scripts/            # optional — pre-built executables, model invokes via Bash
│   ├── render.py
│   ├── setup.sh
│   └── transform.ts
├── requirements.txt    # optional — Python deps, auto-surfaced as install hint
└── (any other assets the body references)
```

**`SKILL.md` shape:**

```markdown
---
name: pdf
description: Render PDFs from markdown input.
whenToUse: When the user asks for a PDF or printable document.
license: Apache-2.0 — complete terms in LICENSE.txt
---

# PDF skill

Use {skill_dir}/scripts/render.py to convert the input file to PDF.
```

Frontmatter is YAML between two `---` fences. Recognized keys (all parsed by `crates/core/src/memory.rs:289`):

| Key | Required | Notes |
|---|---|---|
| `name` | recommended | Falls back to the directory name if absent |
| `description` | recommended | Surfaced verbatim in the system prompt + `/skills` listing |
| `whenToUse` *or* `when_to_use` | optional | Trigger criteria; rendered as `Trigger: …` in "full" mode |
| `model` | optional | Recommended default model — single string or inline array. Triggers a per-turn auto-switch via `skills_state::request_model` when the user has an API key for the named provider. See §11 below. |
| anything else | optional | Ignored by the loader; useful as documentation for skill authors |

`{skill_dir}` in the body is substituted with the **canonical absolute path** to the skill directory at load time (`skills.rs:196`), so script references resolve regardless of CWD.

---

## 2. Discovery

`SkillStore::discover()` (`skills.rs:270`) walks five categories of directory in this load order. `HashMap::insert` is last-wins, so directories later in the list override earlier ones with the same skill name.

| # | Directory | Source | Wins over |
|---|---|---|---|
| 1 | `~/.claude/skills/` | User's Claude Code skills (compatibility) | — |
| 2 | `~/.config/thclaws/skills/` | User's thClaws skills | (1) |
| 3 | `<plugin>/skills/` (or manifest-declared) | Plugin contributions, all enabled scopes | (1)–(2) |
| 4 | `.claude/skills/` | Project's Claude Code skills | (1)–(3) |
| 5 | `.thclaws/skills/` | Project's thClaws skills (highest priority) | All |

**Why this order:** project always beats plugins which always beat user. A project that explicitly installed a skill at `.thclaws/skills/<name>` should not be silently shadowed by a user-installed plugin contributing the same name. M6.14 fixed an earlier bug where plugins came after project dirs and could shadow them — see `dev-log/132`.

**Plugin contributions** (`plugins.rs:428`):
```rust
pub fn plugin_skill_dirs() -> Vec<PathBuf> {
    let mut dirs = Vec::new();
    for plugin in installed_plugins_all_scopes() {
        let manifest = plugin.manifest()?;
        if manifest.skills.is_empty() {
            // Convention-over-configuration fallback
            let conventional = plugin.path.join("skills");
            if conventional.is_dir() { dirs.push(conventional); }
        } else {
            for rel in &manifest.skills {
                dirs.push(plugin.path.join(rel));
            }
        }
    }
    dirs
}
```

Plugins can declare an explicit `skills` field in their manifest, otherwise the loader falls back to a conventional `skills/` subdir. Same pattern Claude Code uses, so anthropics-style plugins install in thClaws unchanged.

---

## 3. Lazy loading (dev-plan/06 P1)

Boot-time discovery only reads each `SKILL.md`'s frontmatter — capped at 4096 bytes via `read_until_frontmatter_end()`. The body stays on disk until the first `SkillTool::call` triggers materialization. Shipped in `dev-log/130`.

### Why

A workspace with 50 skills × ~10 KB body each = 500 KB read at every launch even when only one skill is used per session. Lazy reads cut boot I/O to ~50 × 4 KB = ~200 KB of frontmatter, plus zero body bytes until invocation.

### `SkillContent` enum (`skills.rs:49`)

```rust
enum SkillContent {
    Eager(String),                        // tests, in-memory construction
    Lazy {                                // discovery path
        skill_md_path: PathBuf,           // ABSOLUTE path (M6.14 fix)
        abs_dir: PathBuf,                 // canonical; powers {skill_dir} substitution
        cell: OnceLock<String>,           // first reader wins, subsequent calls are cache hits
    },
}
```

`OnceLock<String>` makes the first reader's `read_to_string` + frontmatter strip + `{skill_dir}` substitute the canonical body. All subsequent `.content()` calls on the same `SkillDef` return the cached value with no I/O.

### `parse_skill` (`skills.rs:330`)

```rust
let abs_dir = dir.canonicalize().unwrap_or_else(|_| dir.to_path_buf());
let abs_skill_md = abs_dir.join("SKILL.md");
SkillDef {
    // ...
    content: SkillContent::Lazy {
        skill_md_path: abs_skill_md,    // M6.14: absolute, not relative
        abs_dir,
        cell: OnceLock::new(),
    },
}
```

**Why absolute?** Discovery often runs from a relative `.thclaws/skills` path. The GUI sidebar's workspace switch (`gui.rs:1998`) calls `std::env::set_current_dir`, after which relative paths resolve under the wrong workspace. Pre-M6.14 this caused every project skill to silently return empty content. See `dev-log/132`.

### Frontmatter-only reader (`skills.rs:209`)

```rust
fn read_until_frontmatter_end(path: &Path) -> std::io::Result<String> {
    // Read 1 KB chunks; stop on closing `---\n` fence or at MAX_FRONTMATTER_BYTES (4096).
    // Files without an opening `---\n` short-circuit immediately ("no frontmatter to find").
}
```

Cap is generous — realistic frontmatter is < 1 KB; edge cases up to 4 KB still parse cleanly. Frontmatter that exceeds 4 KB silently degrades (description becomes empty, name falls back to directory name) — known limitation, no surface yet.

### Custom serde

`SkillDef` derives `Serialize` / `Deserialize` but routes the `content` field through hand-written impls:

```rust
#[serde(serialize_with = "serialize_skill_content")]   // materialize Lazy → string
#[serde(deserialize_with = "deserialize_skill_content")] // always lands in Eager
content: SkillContent,
```

Serializing a `Lazy` variant force-reads the body (best-effort — empty string on read failure). Deserializing always produces `Eager`, since there's no on-disk path to load lazily from once a SkillDef has been serialized to JSON.

---

## 4. Tools registered into the agent

Three tools all share the same `Arc<Mutex<SkillStore>>` handle so `/skill install` can repopulate the store mid-session without rebuilding the registry.

### `Skill(name: <skill-name>)` (`skills.rs:1059`)

The model's primary entry point. Loads the named skill's body (lazy on first call), substitutes `{skill_dir}`, appends auto-detected runtime hints, returns the assembled string.

```rust
async fn call(&self, input: Value) -> Result<String> {
    let name = req_str(&input, "name")?;
    let store = self.store.lock().unwrap();
    let skill = store.get(name).ok_or_else(|| /* "not found, available: …" */)?;

    let mut result = skill.content().into_owned();    // lazy materialization
    append_skill_runtime_hints(&mut result, &skill.dir);  // scripts + requirements.txt
    Ok(result)
}
```

The tool's `description()` instructs the model to call `Skill` **first** when a request matches an installed skill's trigger, before any Bash / Edit / Write attempt at the task. The `input_schema()` enumerates available skill names dynamically so the model sees the live catalog.

### `SkillList()` (`skills.rs:1252`, P2)

Returns every installed skill's name + description + trigger. Cheap; no input. Used by the model to discover the catalog when the system prompt is in `names-only` or `discover-tool-only` mode.

### `SkillSearch(query: …)` (`skills.rs:1308`, P2)

Substring search across name + description + trigger, ranked name > description > trigger. Case-insensitive. Use when the model suspects a skill exists but doesn't remember the exact name.

### Registration site (`shared_session.rs:663`)

```rust
let skill_tool   = SkillTool::new_from_handle(skill_store.clone());
let skill_list   = SkillListTool::new_from_handle(skill_store.clone());
let skill_search = SkillSearchTool::new_from_handle(skill_store.clone());
tools.register(Arc::new(skill_tool));
tools.register(Arc::new(skill_list));
tools.register(Arc::new(skill_search));
```

All three are always registered regardless of `skills_listing_strategy` so any strategy can fall back to dynamic discovery.

---

## 5. User-facing invocation: the `/<skill-name>` slash shortcut

In addition to letting the LLM call `Skill(...)` itself, the user can invoke a skill directly with `/<skill-name> [args]` from either the chat composer or the terminal tab. This matches Claude Code's unified slash UX and is the primary "I want this skill, now" entry point — no waiting for the model to notice a trigger phrase.

### How resolution works

Both surfaces (CLI and GUI) follow the same resolution order, first match wins:

1. **Built-in slash commands** — `/help`, `/model`, `/skill marketplace`, `/clear`, etc. (handled by `parse_slash` in `repl.rs:591`)
2. **Installed skills** — if `parse_slash` returns `Unknown(word)` and `word` matches an installed skill name → rewrite to a synthetic "call Skill(...)" prompt and run the agent
3. **Prompt commands (`.md` templates)** — user, project, or plugin-contributed Claude-Code-style command templates → render the body with `$ARGUMENTS` substitution and run the agent. CLI: `repl.rs:2624`. GUI worker: `shared_session.rs::handle_line` (the `command_store` arm right after the skill check). Both surfaces re-discover with `CommandStore::discover_with_extra(&plugin_command_dirs())` per call so freshly-installed plugin commands surface without a restart.

CLI (`repl.rs:2601-2632`) and GUI worker (`shared_session.rs:1357-1410`) implement the rewrite identically. The skill rewrite is:

```
The user ran the `/<word>` slash command. Call `Skill(name: "<word>")`
right away and follow the instructions it returns. The user's task for
this skill: <args>
```

The `<args>` clause is omitted when no args follow the slash. The line is then handed to `agent.run_turn(rewritten)` like any normal user message — the model invokes `Skill(name: ...)`, materializes the body (lazy-loaded on first call), and follows the returned instructions.

### Why a synthetic prompt instead of direct dispatch

A direct call to `SkillTool.call({name: word})` would skip the agent loop entirely — the user would see the raw skill body as a tool result, with no model interpretation of the args. Routing through the agent gives:

- Args naturally land in the model's context as part of the user's intent
- The model can ask follow-up questions if the skill needs more info
- Streaming output, mid-turn tool calls, and approval gates all work the same way as a regular turn

Trade-off: one extra LLM round-trip vs. instant dispatch. For interactive use the round-trip is invisible; for scripted batch use, calling `Skill` via tool-use API directly is faster.

### Discovery in the GUI slash popup

The slash popup (`SlashCommandPopup.tsx`) shows three groups: `Built-in`, `Custom` (user + plugin prompt commands via `CommandStore::discover_with_extra(&plugin_command_dirs())`), and `Skills` (installed skill names with `source: "skill"`). Built by `gui.rs:1815-1862` — keep the discover-with-extras call in lock-step with the worker's resolution path so popup-shown items always actually fire.

Skills section build:

```rust
let skill_store = crate::skills::SkillStore::discover();
for s in skill_entries {
    entries.push(serde_json::json!({
        "name": s.name,
        "description": s.description,
        "category": "Skills",
        "usage": "",
        "source": "skill",
    }));
}
```

Selecting an entry inserts `/<skill-name> ` (with trailing space) into the input — `acceptSlashCommand` at `ChatView.tsx:481`. The user can then type args or hit Enter immediately.

### CLI feedback

In CLI mode, the rewrite is announced inline so the user knows what happened:

```
❯ /pdf convert spec.md
(/pdf → Skill(name: "pdf"))
[model proceeds to call Skill(name: "pdf") and run the workflow]
```

In GUI mode the same hint surfaces via `emit_skill_resolution_hint(events_tx, &word)` (subtle dim text in the chat).

### Edge cases

- **Unknown slash + no matching skill** → falls through to `dispatch_slash` which emits `unknown command: <detail>`. The user sees the standard error.
- **Skill name collides with a built-in command** → built-in wins (resolution order step 1). A skill named `clear` would be unreachable via `/clear` because `parse_slash` returns `SlashCommand::Clear` first. Skill authors should avoid names that overlap with the built-in command set.
- **Args containing further slashes or special characters** → passed verbatim into the rewritten prompt's `args_note` clause. The model handles them as natural-language text.

---

## 6. System-prompt rendering strategies

Configurable via `skills_listing_strategy` in `settings.json` (project) or `AppConfig` (in-memory). Default is `"full"`, which preserves pre-P2 behavior. Renderer at `shared_session.rs:476`.

| Strategy | Per-skill cost | What's in the prompt | When to use |
|---|---|---|---|
| `full` (default) | ~200 chars × N | Name, description, trigger for every skill | < 20 skills; need guaranteed coverage |
| `names-only` | ~30 chars × N | Comma-separated names; tells the model to call `SkillSearch` for detail | 20–100 skills; some token pressure |
| `discover-tool-only` | constant | No names listed; only mentions `SkillList` / `SkillSearch` | 100+ skills; willing to trade coverage for token budget |

Validation lives in `config.rs:405` — unknown values silently fall back to `"full"` (matches `plan_context_strategy` convention).

**Trade-off:** `discover-tool-only` makes the agent rely on tool calls to find skills. The model may miss a skill it should have invoked if it doesn't think to call `SkillList` first. Only set this when token budget matters more than guaranteed coverage.

---

## 7. In-skill scripts: how they actually run

Skills typically contain pre-built scripts the model invokes via the existing `Bash` tool. The `Skill` response auto-surfaces every script under `scripts/` with a per-extension interpreter hint, plus a `pip install -r` hint if `requirements.txt` is present. Combined with `bash.rs`'s auto-venv layer, Python skills work end-to-end with zero model-side reasoning about environments.

### Auto-listing (`append_skill_runtime_hints`, `skills.rs:1173`)

After the body materializes, this helper appends two optional sections.

**Python deps (when `requirements.txt` exists):**

```
## Python dependencies

Run once before invoking this skill:

  pip install -r /abs/path/skill-name/requirements.txt

(Bash will auto-activate the project venv. Idempotent: repeated installs are no-ops.)
```

**Available scripts (when `scripts/` exists and is non-empty):**

```
## Available scripts

Invoke via Bash. Do NOT rewrite them.

  - `python /abs/path/scripts/render.py`
  - `bash /abs/path/scripts/setup.sh`
  - `npx tsx /abs/path/scripts/transform.ts`
  - /abs/path/scripts/legacy_binary
```

### Interpreter mapping (`suggest_interpreter`, `skills.rs:1221`)

| Extension | Suggestion |
|---|---|
| `.py` | `python` |
| `.sh`, `.bash` | `bash` |
| `.zsh`, `.fish` | `zsh`, `fish` |
| `.js`, `.mjs`, `.cjs` | `node` |
| `.ts`, `.mts` | `npx tsx` |
| `.rb` | `ruby` |
| `.pl` | `perl` |
| `.php` | `php` |
| `.lua` | `lua` |
| `.deno` | `deno run` |
| no ext / unknown | path only — model decides from SKILL.md |

Case-insensitive (`Foo.PY` → `python`). Skill author can override the suggestion by writing an explicit `Run: <command> {skill_dir}/scripts/foo.py` line in their SKILL.md body — that lands BEFORE the auto-section, so the model reads it first.

### The auto-venv layer (`bash.rs:333` — `maybe_wrap_with_venv`)

When the model executes one of the suggested commands, the `Bash` tool's pre-execution wrapper checks if the command needs a Python venv. If yes, it activates `.venv/bin/activate` (or creates the venv first). Detection rules in `needs_venv()`:

```rust
lower.starts_with("python ")
    || lower.starts_with("python3 ")
    || lower.contains("pip install")
    || lower.contains("pip3 install")
    || lower.contains("uvicorn ")
    || lower.contains("gunicorn ")
    || lower.contains("flask run")
    || lower.contains("django")
    || lower.contains("manage.py")
    // …
```

Result: a Python skill ships `requirements.txt` + `render.py`. The first invocation:

1. `Skill(name: "pdf")` → response contains `pip install -r .../requirements.txt` hint + `python .../render.py` listing
2. Model issues `Bash(command: "pip install -r ...")` → wrapper sees `pip install`, creates `.venv` if missing, runs `source .venv/bin/activate && pip install -r ...`
3. Model issues `Bash(command: "python .../render.py input.md")` → wrapper sees `python`, runs `source .venv/bin/activate && python .../render.py input.md`

Skill author writes zero venv boilerplate. Two commits forming this convention: `dev-log/130` (interpreter hints + requirements.txt detection) and the pre-existing `bash.rs:333` (M6.8).

### Where the auto-section lives

The auto-listing comes **after** the SKILL.md body. If a skill author needs `uv run` (PEP 723 inline deps) or `poetry run` instead of bare `python`, they write `Run: uv run {skill_dir}/scripts/foo.py` in their body. The auto-section below it lists the same path with the conventional `python` suggestion — but the body's explicit instruction wins because the model reads in order.

---

## 8. Install dispatch

Entry point: `install_from_url` (`skills.rs:383`). Routes by URL shape:

```
/skill install <name|url> [override-name] [--project]
                  │
                  ↓
       resolve_skill_install_target  (marketplace name → install_url)
                  │
                  ↓
              install_from_url
                  │
        ┌─────────┴─────────┐
        ↓ url.ends_with .zip ↓ everything else
   install_from_zip      install_from_git
```

### Marketplace name resolution

`/skill install <name>` (no URL) looks up `<name>` in the loaded marketplace catalogue. If found, the entry's `install_url` is used (which may carry a `#<branch>:<subpath>` fragment for monorepo-style repos). If not found, the call falls through to treating the input as a literal URL.

### Git installs (`install_from_git`, `skills.rs:692`)

```
1. Determine target_root  → ~/.config/thclaws/skills  OR  $CWD/.thclaws/skills
2. Parse `#branch:subpath` extension from URL
3. Derive skill name from URL (or use override)
4. git clone --depth 1 [--branch <b>] <base_url> <stage_or_final>
5. If subpath was requested:
     - move stage_dir/<subpath> → final_dir
     - reject if no SKILL.md in subpath
     - reject if scripts/ present and policy disallows external scripts
6. Else if cloned root has SKILL.md → single-skill install (apply policy gate)
7. Else → bundle install: walk for every SKILL.md under root, promote each to a sibling
```

**Subpath syntax** (`parse_git_subpath`, `skills.rs:936`):
```
https://github.com/x/r.git                   → (url, None,         None)
https://github.com/x/r.git#main              → (url, Some("main"), None)
https://github.com/x/r.git#main:skills/foo   → (url, Some("main"), Some("skills/foo"))
https://github.com/x/r.git#:skills/foo       → (url, None,         Some("skills/foo"))
```

The marketplace baseline uses `#main:skills/<name>` to install one skill from the shared `thClaws/marketplace` monorepo without dragging in the rest.

### Zip installs (`install_from_zip`, `skills.rs:442`)

```
1. Download zip into memory (cap 64 MiB, 30s timeout — M6.14)
2. Extract under staging dir (target_root/.thclaws-install-<uuid>/)
3. If staging has exactly one subdir + no files → descend into wrapper
4. If source has SKILL.md → single-skill install (apply policy gate, atomic rename)
5. Else → bundle install (same walk + promote logic as git path)
```

Zip-slip is prevented via `entry.enclosed_name()` — entries whose paths escape the destination are rejected. Unix execute bits are preserved when present (`std::os::unix::fs::PermissionsExt`).

### Bundle install (both paths)

When the cloned/extracted root has no SKILL.md but contains nested skill dirs, `find_skill_dirs` (`skills.rs:875`) walks the tree and collects every directory that directly contains a `SKILL.md`. Skips `.git`, `node_modules`, `target`. Each found skill is renamed to a sibling under `target_root/<skill_name>`. Conflicts (existing names) are reported in the install output, not auto-resolved.

**Known limitation:** the bundle path silently ignores `--name <override>`. Filed in `dev-log/132` as deferred (BUG 3).

### Live-refresh after install

Both `shell_dispatch.rs:945` (GUI) and `repl.rs:3300+` (CLI) re-run `SkillStore::discover()` after a successful install and atomically replace the shared store. The system prompt rebuilds so `# Available skills` lists the new skill in the same session — no restart needed.

---

## 9. Trust and policy

### Org policy gate (EE)

`crate::policy::check_url(url)` runs at the top of `install_from_url` (`skills.rs:392`). Returns `AllowDecision::Denied { reason }` when the URL doesn't match the allowed_hosts list of an active enterprise policy. Open-core builds with no policy active fall through to `AllowDecision::NoPolicy`. See `marketplace.md` § 6 for the broader policy model.

### Scripts policy

When `policies.plugins.allow_external_scripts: false` and a policy is active, `enforce_scripts_policy` (`skills.rs:410`) refuses to install any skill whose `scripts/` directory is non-empty. Applied at every install rename point so the rejection happens before the skill reaches its final location. The clone/staging dir is cleaned up on rejection.

### Marketplace `[blocked by policy]` tag

The `/skill marketplace` listing renders a `[blocked by policy]` suffix next to entries whose `install_url` would fail the policy check — saves the user a discovery cycle on entries they can't install. See `marketplace.md` § 4 (M6.12).

---

## 10. Lifecycle: install → discover → invoke

```
USER: /skill install pdf-from-md
    │
    ▼
shell_dispatch::SlashCommand::SkillInstall (gui.rs)
or
repl::handle_skill_install (cli)
    │
    ▼
resolve_skill_install_target  (marketplace lookup)
    │
    ▼
skills::install_from_url
    ├── policy gate (open-core: no-op)
    ├── git clone or zip extract → target_root/<name>/
    ├── enforce_scripts_policy
    └── Ok(report)
    │
    ▼
SkillStore::discover()  (rebuilds store)
    └── parse_skill (frontmatter only) for each <name>/SKILL.md
        └── stores SkillDef with SkillContent::Lazy { abs_skill_md, abs_dir, cell }
    │
    ▼
state.skill_store.lock() = refreshed   (atomic swap)
    │
    ▼
state.rebuild_system_prompt()  (re-renders # Available skills)
state.rebuild_agent(true)       (preserves history; new system prompt)
    │
    ▼
GUI: SlashOutput "(skill available in this session — no restart needed)"

────────── time passes; model receives a matching user request ──────────

MODEL: Skill(name: "pdf-from-md")
    │
    ▼
SkillTool::call
    ├── store.get("pdf-from-md") → SkillDef
    ├── skill.content() → first call materializes via OnceLock
    │     ├── std::fs::read_to_string(abs_skill_md)
    │     ├── parse_frontmatter (strip header)
    │     └── body.replace("{skill_dir}", abs_dir)
    └── append_skill_runtime_hints(&mut result, &skill.dir)
        ├── if requirements.txt exists → "Python dependencies" section
        └── if scripts/ exists → per-script interpreter hints

→ tool result returned to model

MODEL: Bash(command: "pip install -r /…/requirements.txt")
    │
    ▼
BashTool::call
    └── maybe_wrap_with_venv → "source .venv/bin/activate && pip install …"
        (creates venv if missing)

MODEL: Bash(command: "python /…/scripts/render.py input.md")
    │
    ▼
maybe_wrap_with_venv → "source .venv/bin/activate && python …"
```

---

## 11. Code organization

```
crates/core/src/
├── skills.rs                  ── ~1800 LOC, the whole skill subsystem
│   ├── SkillContent enum + serde         (lazy load core)
│   ├── SkillDef + SkillStore             (catalog)
│   ├── parse_skill / load_dir            (discovery)
│   ├── install_from_url + dispatchers    (zip + git installers)
│   ├── enforce_scripts_policy            (EE gate)
│   ├── append_skill_runtime_hints        (auto-listing)
│   ├── suggest_interpreter               (extension → command map)
│   ├── SkillTool / SkillListTool / SkillSearchTool   (model-facing tools)
│   └── tests                             (32 unit + integration)
│
├── shared_session.rs
│   ├── append_skills_section             (system-prompt strategy renderer)
│   └── WorkerState.skill_store           (Arc<Mutex<SkillStore>> shared handle)
│
├── config.rs
│   ├── AppConfig.skills_listing_strategy (default "full")
│   └── ProjectConfig.skillsListingStrategy + merge boundary validation
│
├── plugins.rs
│   └── plugin_skill_dirs                 (manifest skills field + skills/ fallback)
│
├── tools/bash.rs
│   ├── maybe_wrap_with_venv              (transparent venv activation)
│   └── needs_venv                        (Python tool detection)
│
└── policy/mod.rs
    ├── check_url                         (allowlist gate)
    └── external_scripts_disallowed       (scripts policy)
```

---

## 12. Testing

`skills.rs` ships ~30 tests. Highlights:

- **Discovery + lazy loading:**
  - `discover_does_not_eagerly_read_skill_bodies` — confirms `SkillContent::Lazy` after discovery, OnceLock empty
  - `skill_content_loads_on_first_call_and_caches` — mutates file between calls; second call returns cached value
  - `frontmatter_reader_caps_at_max_bytes` — 1 MB body, reader stops well under the cap
  - `missing_skill_md_after_discovery_returns_empty_content` — defensive fallback
  - **`skill_content_survives_cwd_change_after_discovery`** — M6.14 regression test for the absolute-path fix
  - **`project_skills_beat_plugin_skills_with_same_name`** — M6.14 regression test for the priority order

- **Install dispatch:**
  - `derive_name_strips_dot_git_and_path` — name derivation from various URL shapes
  - `is_zip_url_detects_zip_suffix_with_and_without_query` — query/fragment-aware
  - `parse_git_subpath_extracts_branch_and_subpath` — `#branch:subpath` parser
  - `derive_name_uses_subpath_leaf` — monorepo subpath wins over repo basename

- **Tool calls:**
  - `skill_tool_returns_content_with_scripts` — body + Available scripts section
  - `skill_tool_suggests_interpreter_per_script_extension` — polyglot fixture
  - `skill_tool_surfaces_requirements_txt_when_present` — Python deps section
  - `skill_search_substring_matches_with_ranking` — name > description > trigger
  - `skill_list_handles_empty_store` — empty catalog message

- **Strategy rendering** (in `shared_session::tests`):
  - `skills_section_full_strategy_lists_descriptions_and_triggers`
  - `skills_section_names_only_strategy_omits_descriptions`
  - `skills_section_discover_tool_only_omits_names_too`
  - `skills_section_unknown_strategy_falls_back_to_full`

CWD-mutating tests use a `with_cwd(dir, closure)` helper (`skills.rs::tests`) backed by a static `Mutex<()>` to serialize against parallel test runs. Same pattern as `agent::tests::with_cwd`. Without it `set_current_dir` races would flake.

---

## 13. Migration notes / known limitations

### M6.14 fixes (`dev-log/132`)

- **CWD survival:** `parse_skill` now stores `abs_dir.join("SKILL.md")` instead of the raw (possibly relative) `skill_md` path. Project skills survive GUI workspace switches.
- **Project priority:** `discover_with_extra` reorders to user → plugins → project. Project `.thclaws/skills/<name>` always wins; matches the documented priority.
- **`download_zip` timeout:** 30s end-to-end timeout added so a hostile/slow server can't hang `/skill install`.

### Known limitations (not yet fixed)

- **Frontmatter > 4 KB silently degrades** — description goes empty, name falls back to dir name. No surface to the user. Would need a logging channel that `parse_skill` doesn't currently have.
- **`scripts/` symlinks dropped from auto-listing** — `entry.file_type().is_file()` doesn't follow symlinks. Skill authors who symlink scripts from a shared location lose them from the listing.
- **Bundle install ignores `--name <override>`** — only the single-skill path applies the override; bundles use each skill's directory name. No warning emitted.
- **Unknown `skills_listing_strategy` falls back silently** — typo `"names_only"` (underscore) would be silently accepted as `"full"`. Consistent with `plan_context_strategy` validation, but worth a one-time stderr nudge.

### Sprint chronology

| Sprint | Dev-log | What shipped |
|---|---|---|
| dev-plan/06 P1 | `130` | Lazy disk reads — `SkillContent::Lazy` + OnceLock + frontmatter-only reader |
| dev-plan/06 P2 | `130` | `SkillList` + `SkillSearch` tools + `skills_listing_strategy` config |
| Skill polish | `131` | Interpreter auto-detection + `requirements.txt` auto-surfacing |
| M6.14 | `132` | CWD survival, project priority, zip timeout (regression tests included) |

---

## 14. Skill-recommended model (`model:` frontmatter)

Skills that assume capabilities not every model has — vision (OCR a namecard, parse a receipt image), long context (summarise a 200-page PDF), structured output (XLSX cell formulas) — encode a default-model recommendation in the frontmatter. When the user has an API key for the recommended provider, the agent silently swaps for the duration of the turn the skill was invoked in. When they don't, the skill body gets a one-line note explaining the recommendation and proceeds with the user's current model.

### YAML accepted forms

```yaml
model: claude-sonnet-4-6                     # → SkillModelSpec::Single
model: [claude-sonnet-4-6, gpt-4o]           # → SkillModelSpec::Priority
model: ["claude-sonnet-4-6", 'gpt-4o']       # → quoted items unwrapped
```

The simple line-based frontmatter parser at `memory.rs:749` only knows `key: value` (string), so `parse_skill_model` (`skills.rs`) post-processes the raw value: detects `[...]` syntax, splits on commas, trims quotes/whitespace, collapses single-element arrays back to `Single`. Fully empty arrays produce `None`.

### End-to-end flow

```
SkillTool::call(name="namecard-to-excel")
   │
   │ skill.model = Some(SkillModelSpec::Priority([claude-sonnet-4-6, gpt-4o]))
   ▼
crate::skills_state::request_model(&spec)
   │
   │ Worker-registered resolver runs:
   │   for candidate in spec.candidates() {
   │       if ProviderKind::detect(candidate)?.has_key_available() {
   │           override_handle.lock() = Some(candidate);
   │           skills_state::mark_swap_active();
   │           events_tx.send(ViewEvent::SkillModelNote(...));
   │           return Switched(candidate);
   │       }
   │   }
   │   events_tx.send(ViewEvent::SkillModelNote(warn));
   │   return KeptCurrent { recommended: spec.candidates()[0] };
   ▼
SkillTool body returned with appended note
   │
   ▼
Agent::run_turn iteration N+1 reads `model_override` slot fresh:
   let active_model = model_override.lock().clone().unwrap_or(model);
   ▼
provider.stream(req with active_model=claude-sonnet-4-6)  ← swap takes effect
   ▼
... iterations continue with overridden model ...
   ▼
Done yields → Agent clears model_override slot → drive_turn_stream sees
              skills_state::take_swap_active() == true → emits
              ViewEvent::SkillModelNote("[model → <baseline> (skill ended)]")
```

### Components

| Layer | File | What it does |
|---|---|---|
| Type | `skills.rs::SkillModelSpec` | `#[serde(untagged)]` enum with `Single(String)` + `Priority(Vec<String>)` variants |
| Parser | `skills.rs::parse_skill_model` | Post-processor turning the raw frontmatter string into `Option<SkillModelSpec>` |
| Field | `skills.rs::SkillDef::model` | `Option<SkillModelSpec>` populated by `parse_skill` from the frontmatter map |
| Broadcaster | `skills_state.rs` | `set_resolver` / `request_model` mirror of `plan_state` pattern; `mark_swap_active` / `take_swap_active` AtomicBool flag for revert signaling |
| Agent slot | `agent.rs::Agent::model_override` | `Arc<Mutex<Option<String>>>` read fresh at the top of every iteration's request build |
| Override clear | `agent.rs` Done-yield sites | Both natural-stop and max-iterations paths clear `model_override` before yielding `AgentEvent::Done` |
| Worker resolver | `shared_session.rs` | Registers closure that probes `ProviderKind::has_key_available`, writes to override slot, emits `ViewEvent::SkillModelNote` |
| Key probe | `providers/mod.rs::ProviderKind::has_key_available` | True iff `api_key_env()` is None (no auth required) OR env var set OR `secrets::get(provider_name)` returns Some |
| IPC | `event_render.rs` | `ViewEvent::SkillModelNote(String)` → `chat_skill_model_note` envelope |
| Frontend | `ChatView.tsx` | Renders the note as a muted system bubble (same path as `chat_slash_output`) |

### Per-turn semantics

The override is scoped to a single `run_turn` invocation:

- **Skill A invoked mid-turn → swap to X (mark_swap_active flag set).**
- **Same turn, skill B invoked → swap to Y (resolver overwrites override slot).**
- **Done yields → agent clears slot → worker emits revert note → next user prompt starts from baseline.**

`/model` switches the user types explicitly are unaffected because they happen between turns, not during the override-active window.

### Failure modes

- **No resolver registered (CLI surface)** — `request_model` returns `NoResolver`. SkillTool appends nothing to the body; user keeps current model. CLI is intentionally untouched: no GUI = no chat surface for the swap notes anyway.
- **Spec has candidates but none have keys** — resolver emits a warning note, returns `KeptCurrent { recommended }`. SkillTool appends a "you don't have a key for that provider" line to the body so the model can mention it.
- **Mutex poisoning on the override Arc** — agent's `unwrap_or` on a poisoned lock falls back to the baseline model; same posture as `plan_state::fire`'s recovery.

### Test surface

| File | Test | Covers |
|---|---|---|
| `skills.rs::tests` | `parse_skill_model_handles_single_string` | Single-form parse |
| `skills.rs::tests` | `parse_skill_model_handles_inline_array` | Priority-form parse |
| `skills.rs::tests` | `parse_skill_model_strips_quotes_in_array` | Quoted-item handling |
| `skills.rs::tests` | `parse_skill_model_single_element_array_collapses_to_single` | `[a]` → `Single(a)` |
| `skills.rs::tests` | `parse_skill_model_empty_returns_none` | Empty inputs → None |
| `skills.rs::tests` | `parse_skill_picks_up_model_frontmatter_single` | End-to-end frontmatter discovery (single) |
| `skills.rs::tests` | `parse_skill_picks_up_model_frontmatter_array` | End-to-end (array) |
| `skills.rs::tests` | `parse_skill_without_model_field_yields_none` | Backward compat — skills without `model:` parse as before |

The agent-side override read + clear is exercised indirectly by every existing run_turn test via the `model_override = Arc::new(Mutex::new(None))` default in `Agent::new`.

### Cross-references

- [`subagent.md`](subagent.md) — `AgentDef::model` is a parallel concept for subagents; both fields shape per-call model selection but at different timing scales (subagent = whole subagent invocation, skill = single turn).
- [`compaction.md`](compaction.md) — the override is read by the same `run_turn` that builds compaction-eligible history; compaction sees `req.messages` only, not the model name, so the override is invisible to the compactor.
