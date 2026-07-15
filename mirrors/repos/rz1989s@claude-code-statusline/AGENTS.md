<!-- Satellite context file — extends the global hub (~/.claude/CLAUDE.md | ~/.pi/agent/AGENTS.md). Host-neutral; project-specific only. Do not duplicate hub standards here. -->

# claude-code-statusline

> A feature-rich, multi-platform statusline for Claude Code — 9-line display with cost tracking, native context %, prayer times, MCP status, GPS location, wellness, CLI analytics, and a responsive width system.

**Org:** rz1989s (personal).

## Project Status

**Current:** v2.27.1 | **Claude Code compatibility:** v2.1.6–v2.1.201 ✓ | **Branch strategy:** `feat/fix/chore` → `nightly` → `main`
**Architecture:** Single `Config.toml` (240+ settings), modular cache (8 sub-modules), JSON abstraction layer, responsive width system.
**Platforms:** macOS, Ubuntu, Arch, Fedora, Alpine Linux.

## Essential Commands

```bash
npm test                              # Run all 940 tests across 56 files
npm run lint:all                      # Lint everything
./statusline.sh --modules             # Show component status
STATUSLINE_DEBUG=true ./statusline.sh # Debug mode

# Configuration testing via env overrides
ENV_CONFIG_THEME=garden ./statusline.sh
ENV_CONFIG_DISPLAY_LINES=3 ./statusline.sh
ENV_CONFIG_LINE1_COMPONENTS="repo_info,commits" ./statusline.sh

# Cache management
rm -rf ~/.cache/claude-code-statusline/
STATUSLINE_DEBUG=true ./statusline.sh 2>&1 | grep "cache"

# Cross-platform testing
bats tests/unit/test_platform_compatibility.bats

# Installation (curl installer, 3-tier download w/ retry)
curl -sSfL https://raw.githubusercontent.com/rz1989s/claude-code-statusline/nightly/install.sh | bash -s -- --branch=nightly
```

## Architecture

**Core Modules** (16): core → security → json_fields → config → themes → cache → git → mcp → cost → prayer → wellness → focus → components → responsive → display.

**Atomic Components** (37): repo_info, commits, submodules, version_info, github · model_info, bedrock_model, cost_repo, cost_live, reset_timer · cost_monthly/weekly/daily · burn_rate, token_usage, cache_efficiency, block_projection, code_productivity · time_display, version_display, context_alert, context_window · mcp_status/servers/plugins · vim_mode, agent_display, session_info, session_mode · total_tokens, usage_limits · wellness · prayer_times, prayer_times_only, prayer_icon, hijri_calendar, location_display · 10 CLI analytics commands.

**Data Flow:** JSON input → schema validation → config loading → theme application → atomic component data collection → 1-9 line dynamic output (default: 9-line with wellness + GPS location).

**Key Functions:**
- `load_module()` — module loading with dependency checking
- `get_json_field()` — safe JSON extraction with path migration (v2.1.66+)
- `validate_json_schema()` — startup schema validation + version detection
- `load_toml_configuration()` — single-source TOML parsing
- `apply_theme()` — color theme management
- `execute_cached_command()` — universal caching with TTL
- `get_context_window_percentage_smart()` — native percentages (v2.1.6+) with transcript fallback

## Development Workflow

```bash
# Branch strategy: feat/*, fix/*, chore/* → nightly → main
git checkout -b feat/my-feature nightly
git push origin feat/my-feature
git checkout nightly && git merge feat/my-feature --no-ff

# Testing
bats tests/unit/test_*.bats           # Unit (45 files)
bats tests/integration/test_*.bats    # Integration (7 files)
bats tests/benchmarks/test_*.bats     # Performance (4 files)

# Pre-commit (optional but recommended)
pip install pre-commit && pre-commit install
pre-commit run --all-files
```

## Configuration

**Single source:** `~/.claude/statusline/Config.toml` (227 settings, all pre-filled).

Key settings include `theme.name`, `display.lines` (1-9), per-line `display.lineN.components` arrays, `features.*`, `cache.isolation.mode` (`repository`/`instance`/`shared`), `prayer.*`, `location.*` (GPS), and `labels.*`.

**Environment overrides:** any TOML setting via `ENV_CONFIG_*` pattern (e.g. `ENV_CONFIG_THEME_NAME=garden`, `ENV_CONFIG_PRAYER_LOCATION_MODE=local_gps`, `ENV_CONFIG_LOCATION_FORMAT=full`).

## Claude Code JSON Input (stdin)

The statusline reads JSON from stdin (`input=$(cat)`), exported as `STATUSLINE_INPUT_JSON`. Only `workspace.current_dir` is required; all other fields optional with graceful fallbacks. Field access uses `get_json_field()` with automatic path migration for backward compatibility.

**Core schema (v2.1.201):** `version`, `cwd`, `workspace` (`current_dir`, `project_dir`, `added_dirs`, `repo`{host,owner,name}), `model` (`id`, `display_name`), `session_id`, `transcript_path`, `output_style`, `context_window` (`used_percentage`, `remaining_percentage`, `context_window_size`, `current_usage`, `total_input_tokens`, `total_output_tokens`), `exceeds_200k_tokens`, `cost`, `vim.mode` (NORMAL/INSERT/VISUAL/VISUAL_LINE), `agent.name`, `mcp.servers`, `pr` (`number`, `url`, `review_state`), `worktree`, `rate_limits` (`five_hour`, `seven_day`), `effort.level`, `thinking.enabled`.

**Compatibility:** Fully compatible through v2.1.201 via feature detection (field existence), not version comparison. See [`docs/CC_COMPATIBILITY.md`](docs/CC_COMPATIBILITY.md) for per-version notes from v2.1.77 onward — skipped releases, polish/UX fixes, statusline-render fixes, and non-schema CC changes. The full per-version changelog narrative lives there.

**Pricing tiers (statusline cost tracking):** Opus 4.6/4.7/4.8 = $5/$25; Fable 5 = $10/$50 (🔮 icon, v2.1.170); Sonnet 5 (default, v2.1.197) = $2/$10 promo through 2026-08-31, then $3/$15 (date-aware, v2.27.0). Patterns live in `lib/cost/pricing.sh`.

**1M context (v2.1.75+):** Opus 4.6, Sonnet 4.6, Opus 4.7/4.8, Fable 5, Sonnet 5 support 1M context at standard pricing. `context_window_size` = `1000000`; handled dynamically via `get_native_context_window_size()`. `exceeds_200k_tokens` remains the only threshold marker (no `exceeds_1m_tokens`).

**Usage limits:** `rate_limits.*` native since CC v2.1.80 (zero-latency, no network); OAuth fallback for older CC. Native `resets_at` is Unix epoch (int); OAuth returns ISO 8601 — both supported.

**macOS note:** Requires bash 4+ (`brew install bash`). Settings.json should use `/opt/homebrew/bin/bash` (Apple Silicon) or `/usr/local/bin/bash` (Intel).

## Testing & Debugging

```bash
STATUSLINE_DEBUG=true ./statusline.sh          # debug logging
./statusline.sh --modules                      # module status
git log --since="today 00:00" --oneline | wc -l  # commit-count sanity check
rm -rf ~/.cache/claude-code-statusline/git_commits_since_*   # clear commit cache

bats tests/benchmarks/test_performance.bats
bats tests/benchmarks/test_cache_performance.bats

# Prayer / GPS testing
bats tests/unit/test_prayer_functions.bats
ENV_CONFIG_PRAYER_LOCATION_MODE=local_gps ./statusline.sh
ENV_CONFIG_LOCATION_FORMAT=full ./statusline.sh
STATUSLINE_DEBUG=true ./statusline.sh 2>&1 | grep -i "gps\|location\|coordinates"
```

## Cache System

XDG-compliant with repository isolation: `~/.cache/claude-code-statusline/` (primary), `~/.local/share/claude-code-statusline/` (fallback). TTLs: session-wide (cmd existence), 15min (CC version), 2min (MCP list), 30s (git status), 10s (branch), 5s (working dir). Isolation modes: `repository` (recommended), `instance`, `shared` (legacy).

## Responsive Width System

Always-on, zero config. Detects terminal width (`ENV_CONFIG_TERMINAL_WIDTH` → `$COLUMNS` → fallback 120), drops lower-priority components per line, truncates as safety net. CC **v2.1.153+ passes `COLUMNS`/`LINES`** to statusline commands natively. Component priority 1 (essential) → 4 (first to go); unregistered default to 3 (table in `lib/responsive.sh`).

## Technical Implementation

- **Required deps:** `jq` (JSON), `git` (repo). **Prayer:** `curl`, `date`. **GPS:** macOS CoreLocationCLI, Linux geoclue2. **Optional:** `timeout`/`gtimeout`.
- **Security:** input sanitization (`lib/security.sh`), timeout protection, secure path handling.
- **Performance:** single-pass jq (64→1 calls), intelligent caching, parallel ops.
- **Module loading:** include guards `[[ "${STATUSLINE_*_LOADED:-}" == "true" ]] && return 0`.

## Installation

Two methods: **curl installer** (recommended — macOS/Linux/WSL, auto settings.json, any branch) and **Homebrew** (macOS only — `brew tap rz1989s/tap && brew install claude-code-statusline`, manual settings.json). Curl uses a 3-tier download architecture (direct raw → GitHub API → retry w/ backoff) for 100% download guarantee.

## Prayer + GPS Location

Display: `🕌 24 Rabi' al-awwal 1447 🌙 │ Fajr 04:28 (8h 19m) │ Dhuhr 11:47 ✓`. Prayer times cached 24h, GPS coords cached fresh. Location hierarchy: local system GPS (95%) → IP geolocation (85%) → timezone mapping (70%) → manual override (100%). Coverage: 2B+ Muslims across SE Asia, South Asia, Middle East, North Africa, Europe, Americas.