---
name: game-godot
version: 1.3.1
description: "Tests, exports, and deploys Godot 4 games with GdUnit4 (in-engine) and PlayGodot (external Python E2E). Use when writing GdUnit4 tests, PlayGodot automation, or Godot --export-release CI. Not for GDScript style (godot-gdscript-mastery) or Control/Theme UI (godot-ui). Never vercel deploy --csp — that flag does not exist."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Godot 4.x Game Development, Testing, Build & Deploy

Develop, test, build, and deploy Godot 4.x games with GdUnit4 (in-engine tests) and PlayGodot (external Python E2E on the automation fork).

## When to Use

- Developing, testing, building, or deploying a Godot **4.3+** game (LTS release)
- Writing GDScript **unit/component tests** with GdUnit4 (runs headless inside Godot)
- Writing **E2E / integration / automated-gameplay tests** with PlayGodot (custom Godot automation fork + Python client)
- Simulating mouse, keyboard, touch, or input-action events in scene tests
- Exporting **web or desktop** builds from the command line using Godot 4.3+ export templates
- Wiring Godot tests and exports into a **CI/CD** pipeline (GitHub Actions, GitLab CI)
- Deploying a web build to **Vercel, GitHub Pages, Netlify, or itch.io** with modern compression (Brotli)

### Do Not Use

- **Godot 3.x projects** — the GdUnit4 base classes, scene-runner API, and export flags differ; use the 3.x docs and `gut`/GdUnit3 instead
- **Non-Godot engines** (Unity, Unreal, web canvas frameworks) — none of these tools or CLI invocations apply
- **PlayGodot on stock Godot** — the Python client needs the Randroids-Dojo automation fork
- **Pure asset/art pipelines** with no code under test — there is nothing here to assert against
- **General (non-game) Python testing** — use plain `pytest`/`unittest`; PlayGodot only adds value when driving a live Godot game
- **Manual play-test or visual-only QA** — this skill is for *automated* tests, exports, and deploys
- **Unencrypted network deployments** — Web exports must use HTTPS and Content Security Policy (CSP) headers

## Prerequisites

- **Godot 4.3+** (LTS release) installed and on PATH. Verify: `godot --version`
- **Python 3.10+** for PlayGodot. Verify: `python --version`
- **Git** for cloning GdUnit4 addon. Verify: `git --version`
- **Brotli** compressor for web export optimization. Verify: `brotli --version`
- **Export templates** installed for Godot 4.3+ (via Godot Editor → Editor → Manage Export Templates, or CI setup action)
- **Windows host (PowerShell)** is the primary environment. Use PowerShell-compatible commands. On Linux/macOS, adapt path separators and shell commands accordingly.

### Reference Files

Load these files from this skill folder when you need depth:

- `references/gdunit4-quickstart.md` — GdUnit4 install, first suite, lifecycle
- `references/assertions.md` — assertion catalog
- `references/scene-runner.md` — scene runner / input simulation
- `references/playgodot.md` — PlayGodot E2E (automation Godot fork)
- `references/deployment.md` — web export and host deploy (Vercel without invented flags)
- `references/ci-integration.md` — GitHub Actions / GitLab sketches
- `scripts/run_tests.py`, `scripts/export_build.py`, `scripts/validate_project.py`, `scripts/parse_results.py`

## Procedure

### Step 1: Pick the Test Layer

| | GdUnit4 | PlayGodot |
|---|---------|-----------|
| Type | Unit / scene tests | Game automation (E2E) |
| Language | GDScript | Python (async/await) |
| Runs | Inside Godot | External process |
| Requires | Godot 4.x editor binary + addon | Custom Godot **automation fork** ([Randroids-Dojo/godot](https://github.com/Randroids-Dojo/godot)) + `pip install playgodot` |
| Best for | Fast GDScript assertions | Driving a live game from Python |

Use **GdUnit4** for unit/component/scene tests. Add **PlayGodot** only when you have the automation fork — stock Godot does not expose those debugger commands.

### Step 2: Install GdUnit4

```powershell
# AssetLib in the editor is preferred. Git clone without inventing a tag:
git clone --depth 1 https://github.com/godot-gdunit-labs/gdUnit4.git addons/gdUnit4
```

Then enable the plugin: **Project Settings → Plugins → GdUnit4 → Enable**

Expected project structure:

```
project/
├── addons/gdUnit4/          # GdUnit4 addon
├── test/                    # Test directory
│   ├── game_test.gd
│   └── player_test.gd
└── scripts/
    └── game.gd
```

### Step 3: Write GdUnit4 Unit Tests

Create test suites extending `GdUnitTestSuite`. Always free nodes with `auto_free()` to prevent memory leaks.

```gdscript
# test/game_test.gd
extends GdUnitTestSuite

@warning_ignore("unused_parameter")
var game: Node

func before_test() -> void:
    game = auto_free(load("res://game.gd").new())

func test_initial_state() -> void:
    assert_that(game.is_game_active()).is_true()
    assert_that(game.get_current_player()).is_equal("X")

@warning_ignore("return_value_discarded")
func test_make_move() -> void:
    var success := game.make_move(4)
    assert_that(success).is_true()
    assert_that(game.get_board_state()[4]).is_equal("X")
```

### Step 4: Write GdUnit4 Scene Tests with Input Simulation

Use `scene_runner(...)` to load scenes and simulate input. Always call `await_input_processed` after simulating input.

```gdscript
# test/game_scene_test.gd
extends GdUnitTestSuite

var runner: GdUnitSceneRunner

func before_test() -> void:
    runner = scene_runner("res://scenes/main.tscn")

func after_test() -> void:
    runner.queue_free()

func test_click_cell() -> void:
    await runner.await_idle_frame()

    var cell := runner.find_child("Cell4") as Control
    runner.set_mouse_position(cell.global_position + cell.size / 2)
    runner.simulate_mouse_button_pressed(MOUSE_BUTTON_LEFT)
    await runner.await_input_processed()

    var game := runner.scene()
    assert_that(game.get_board_state()[4]).is_equal("X")

func test_keyboard_restart() -> void:
    runner.simulate_key_pressed(KEY_R)
    await runner.await_input_processed()
    assert_that(runner.scene().is_game_active()).is_true()
```

#### GdUnit4 Assertion Quick Reference

```gdscript
# Null checks
assert_that(value).is_null()
assert_that(value).is_not_null()

# Type checks
assert_that(node).is_instanceof(CharacterBody2D)

# Signal verification
await assert_signal(player).is_emitted("died")
await assert_signal(ui).is_not_emitted("popup_closed", timeout_ms=1000)

# Collection assertions
assert_that([1, 2, 3]).contains_exactly([1, 2, 3]).in_order()
assert_that({"a": 1}).has_key("a")
```

### Step 5: Run GdUnit4 Tests Headless

Official CLI options (from `GdUnitTestCIRunner`): `-a`/`--add`, `-i`/`--ignore`, `-c`/`--continue`, `-rd`/`--report-directory`, `--ignoreHeadlessMode`. There is **no** `--run-tests` or `--report-format` flag.

```powershell
# All tests under ./test  (headless requires --ignoreHeadlessMode)
godot --headless --path . -s res://addons/gdUnit4/bin/GdUnitCmdTool.gd --ignoreHeadlessMode -a res://test -rd ./reports

# Specific suite
godot --headless --path . -s res://addons/gdUnit4/bin/GdUnitCmdTool.gd --ignoreHeadlessMode -a res://test/player_test.gd
```

Or: `python scripts/run_tests.py --project . --report ./reports`

### Step 6: Set Up PlayGodot

Requires the **Randroids-Dojo automation fork** of Godot, not stock Godot. PyPI package is `playgodot` (current line is 0.5.x — do **not** pin a fictional `>=3.0.0`). Official launch API: `Godot.launch(project_path, ...)` — there is no `GodotConfig` class.

```powershell
python -m pip install playgodot pytest pytest-asyncio
python -c "import playgodot; print(playgodot.__version__)"
```

```python
import pytest
from playgodot import Godot

@pytest.fixture
async def game():
    async with Godot.launch(
        ".",
        headless=True,
        timeout=30000,
        godot_path="godot",  # path to the automation-fork binary
    ) as g:
        await g.wait_for_node("/root/Main")
        yield g
```

### Step 7: Write PlayGodot E2E Tests

```python
import pytest

@pytest.mark.asyncio
async def test_complex_interaction(game):
    await game.wait_for_node("/root/Main/UI/NameInput")
    await game.click("/root/Main/UI/NameInput")
    await game.type_text("Player1")
    name = await game.get_property("/root/Main/UI/NameInput", "text")
    assert name == "Player1"
    await game.press_action("ui_accept")
    await game.wait_for_node("/root/Game", timeout=5000)
```

Documented extras (PlayGodot README): `game.call(...)`, `game.screenshot(...)`, `game.assert_screenshot(...)`, `game.change_scene(...)`. Do not invent `mock_method` or a `Key` enum unless you have verified them in the installed package.

### Step 8: Run PlayGodot Tests

```powershell
# Run all PlayGodot tests (PowerShell)
pytest tests/ -v
```

### Step 9: Export Web Build

Official CLI: `godot --headless --path <project> --export-release <preset_name> <output_path>`
([command line tutorial](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html)).
The target directory must exist. Preset name must match `export_presets.cfg`.

Godot Web export has **no** `html/security/csp_enabled` key. Threaded web builds need COOP/COEP headers on the **server**
([exporting for web](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html)):

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

Or enable Progressive Web App in the export preset so Godot can simulate those headers.

```ini
[preset.0]
name="Web"
platform="Web"
runnable=true
export_path="build/index.html"

[preset.0.options]
html/export_icon=true
vram_texture_compression/for_mobile=false
```

```powershell
New-Item -ItemType Directory -Force -Path ./build | Out-Null
godot --headless --path . --export-release "Web" ./build/index.html
```

### Step 10: Deploy

Vercel CLI has **no** `--csp` flag ([vercel deploy](https://vercel.com/docs/cli/deploy)). Set headers in `vercel.json`:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Cross-Origin-Opener-Policy", "value": "same-origin" },
        { "key": "Cross-Origin-Embedder-Policy", "value": "require-corp" }
      ]
    }
  ]
}
```

```powershell
npx vercel deploy ./build --prod --yes
```

For GitHub Pages, itch.io, or Netlify, upload `./build/` over HTTPS and add the same COOP/COEP headers at the host.

### Step 11: Automate in CI/CD

```yaml
name: Godot CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Godot 4.3
        uses: chickensoft-games/setup-godot@v3
        with:
          version: 4.3.0
          export-templates: true
          
      - name: Run GdUnit4 tests
        run: |
          godot --headless --path . \
            -s res://addons/gdUnit4/bin/GdUnitCmdTool.gd \
            --ignoreHeadlessMode -a res://test -rd ./reports
            
      - name: Run PlayGodot tests
        run: |
          python -m pip install playgodot pytest-asyncio
          pytest tests/ -v
          
      - name: Upload test results
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: |
            reports/
            test-results.xml
```

## Pitfalls

1. **Godot 3.x incompatibility** — GdUnit4 base classes, scene-runner API, and export flags differ from 3.x. Do not attempt to use this skill with Godot 3.x projects. Use `gut`/GdUnit3 for 3.x.
2. **PlayGodot without the automation fork** — stock Godot will not honor PlayGodot debugger commands. Pin `playgodot` from PyPI; do not invent a 3.x requirement.
3. **Memory leaks from unfreed nodes** — Always use `auto_free()` for nodes created in GdUnit4 tests and `queue_free()` for scene runners in `after_test()`.
4. **Missing `await_input_processed`** — Input simulations without awaiting processing will produce flaky tests. Always call `await runner.await_input_processed()` after `simulate_mouse_button_pressed`, `simulate_key_pressed`, or similar.
5. **Missing export templates** — `--export-release` will fail silently or produce broken builds if export templates are not installed. Verify templates before exporting.
6. **Invented CSP export keys** — There is no `html/security/csp_enabled` in Godot Web export. Use COOP/COEP on the host (or PWA export option).
7. **`vercel deploy --csp`** — Not a Vercel CLI flag. Use `vercel.json` headers + `npx vercel deploy ./build --prod --yes`.
8. **Invented GdUnit flags** — `--run-tests` and `--report-format` are not CmdTool options. Use `-a` / `-rd` / `--ignoreHeadlessMode`.
9. **Headless UI tests** — Godot does not transport InputEvents in headless mode; GdUnit documents this. Prefer `--ignoreHeadlessMode` only for non-UI suites.
10. **PowerShell path separators** — Godot uses `res://` paths internally regardless of OS. For filesystem paths in PowerShell, `./` works.

## Verification

Confirm each item before merging or shipping. Run these checks:

```powershell
# 1. Godot editor binary
godot --version

# 2. GdUnit4 (official flags)
godot --headless --path . -s res://addons/gdUnit4/bin/GdUnitCmdTool.gd --ignoreHeadlessMode -a res://test -rd ./reports

# 3. PlayGodot (only with automation-fork binary)
pytest tests/ -v

# 4. PlayGodot package
python -c "import playgodot; print(playgodot.__version__)"

# 5. Web export artifacts
Get-ChildItem -Path ./build -Recurse | Select-Object Name, Length
```

Checklist:

- [ ] GdUnit4 tests pass with `-a` / `--ignoreHeadlessMode` (not `--run-tests`)
- [ ] PlayGodot tests pass with `pytest tests/ -v` **and** the automation fork
- [ ] Test resources are freed (`auto_free()` / `queue_free()`)
- [ ] Input simulations await processing (`await_input_processed`)
- [ ] Web export dir exists before `--export-release`
- [ ] Host sends COOP/COEP (or PWA workaround) — not a fake CSP export key
- [ ] `vercel deploy` has no `--csp` flag

## Examples

### Quick Reference Commands

```powershell
# GdUnit4
godot --headless --path . -s res://addons/gdUnit4/bin/GdUnitCmdTool.gd --ignoreHeadlessMode -a res://test

# PlayGodot (automation fork required)
pip install playgodot
pytest tests/ -v

# Export web build (create ./build first)
godot --headless --path . --export-release "Web" ./build/index.html

# Deploy (no --csp)
npx vercel deploy ./build --prod --yes
```

## Related Skills

- **`godot-gdscript-mastery`** — typed GDScript standards (not this test/export pack).
- **`godot-ui`** — Control/Theme/focus UI.
- **`godot-export-builds`** — export/presets depth if that v1 chair is installed.
- **`deploy-to-vercel`** — Vercel CLI (real flags only).

## References

- [GdUnit4 Documentation](https://mikeschulze.github.io/gdUnit4/)
- [PlayGodot README / API](https://github.com/Randroids-Dojo/PlayGodot)
- [Godot 4.3 Export Docs](https://docs.godotengine.org/en/4.3/tutorials/export/)
- [Web Security Best Practices](https://owasp.org/www-project-secure-headers/)
