---
sidebar_position: 2
---

# extras

skill과 함께 동기화되는 skill이 아닌 리소스(rules, commands, prompts 등)를 관리합니다.

## Overview

Extras는 skillshare가 관리하는 추가 리소스 유형입니다 — "skill이 아닌 콘텐츠를 위한 skill"이라고 생각하면 됩니다. 일반적인 사용 사례로는 AI rules, 에디터 commands, prompt 템플릿을 여러 도구에 걸쳐 동기화하는 것이 있습니다.

각 extra는 다음을 가집니다:
- **name** (예: `rules`, `prompts`, `commands`)
- **source directory** — `extras_source` 또는 extra별 `source`로 설정 가능하며, 기본값은 `~/.config/skillshare/extras/<name>/` (전역) 또는 `.skillshare/extras/<name>/` (프로젝트)
- 파일이 동기화되는 하나 이상의 **target**

## Commands

### `extras init`

새로운 extra 리소스 유형을 생성합니다.

```bash
# Interactive wizard
skillshare extras init

# CLI flags
skillshare extras init <name> --target <path> [--target <path2>] [--mode <mode>]
```

**Options:**

| Flag | 설명 |
|------|-------------|
| `--target <path>` | target 디렉터리 경로 (반복 가능) |
| `--mode <mode>` | 동기화 mode: `merge` (기본값), `copy`, 또는 `symlink` |
| `--flatten` | 하위 디렉터리의 파일을 target 루트에 바로 동기화 (`symlink` mode와 함께 사용 불가) |
| `--source <path>` | 이 extra에 대한 사용자 지정 source 디렉터리 (`extras_source` 및 기본값을 재정의; **전역 모드 전용**) |
| `--force` | extra가 이미 존재하면 덮어쓰기 |
| `--no-tui` | interactive wizard 생략, CLI 플래그만 사용 |
| `--project, -p` | 프로젝트 config(`.skillshare/`)에 생성 |
| `--global, -g` | 전역 config에 생성 |

:::note
`--source`는 전역 모드에서만 지원됩니다. 프로젝트 모드는 항상 `.skillshare/extras/<name>/`를 source 디렉터리로 사용합니다.
:::

**Examples:**

```bash
# Sync rules to Claude and Cursor
skillshare extras init rules --target ~/.claude/rules --target ~/.cursor/rules

# Use a custom source directory
skillshare extras init rules --target ~/.claude/rules --source ~/company-shared/rules

# Overwrite an existing extra with new targets
skillshare extras init rules --target ~/.cursor/rules --force

# Project-scoped extra with copy mode
skillshare extras init prompts --target .claude/prompts --mode copy -p

# Sync agents flat (tools like Claude Code only discover flat files)
skillshare extras init agents --target ~/.claude/agents --flatten
```

### `extras list`

구성된 모든 extra와 동기화 상태를 나열합니다. 기본적으로 interactive TUI를 실행합니다.

```bash
skillshare extras list [--json] [--no-tui] [-p|-g]
```

**Options:**

| Flag | 설명 |
|------|-------------|
| `--json` | JSON 출력 (`source_type`: `per-extra` / `extras_source` / `default` 포함, 설정된 경우 target별 `extension` 필드 포함) |
| `--no-tui` | interactive TUI 비활성화, 일반 텍스트 출력 사용 |
| `--project, -p` | 프로젝트 모드 extras 사용 (`.skillshare/`) |
| `--global, -g` | 전역 extras 사용 (`~/.config/skillshare/`) |

#### Interactive TUI

TUI는 왼쪽에 extras 목록, 오른쪽에 detail 패널이 있는 split-pane 인터페이스를 제공합니다. 키 바인딩:

| Key | Action |
|-----|--------|
| `↑↓` | 목록 탐색 |
| `/` | 이름으로 필터링 |
| `Enter` | Content viewer (source 파일 탐색) |
| `N` | 새 extra 생성 |
| `X` | extra 제거 (확인 필요) |
| `S` | extra를 target(들)에 동기화 |
| `C` | target(들)에서 수집 |
| `M` | target의 동기화 mode 변경 |
| `F` | target의 flatten 켜기/끄기 |
| `Ctrl+U/D` | detail 패널 스크롤 |
| `q` / `Ctrl+C` | 종료 |

각 행의 color bar는 종합 동기화 상태를 나타냅니다: cyan = 모두 동기화됨, yellow = drift, red = 동기화 안 됨, gray = source 없음.

여러 target이 있는 extra의 경우, `S`, `C`, `M`, `F`는 target 하위 메뉴를 엽니다. `S`와 `C`는 모든 target을 한 번에 선택할 수 있으며, `M`과 `F`는 특정 target을 선택해야 합니다.

TUI는 `skillshare tui off`로 영구적으로 비활성화할 수 있습니다.

#### Plain text output

TUI가 비활성화된 경우 (`--no-tui`, `skillshare tui off`, 또는 파이프된 출력을 통해):

```
$ skillshare extras list --no-tui

Extras
─────────────────────────────────────────
→ rules  ~/.config/skillshare/extras/rules/ · 2 files
  ✓ ~/.claude/rules  merge
  ✓ ~/.cursor/rules  copy

→ codex-agents  ~/.config/skillshare/agents · 3 files
  ✓ ~/.codex/agents  extension: codex-agents
```

동기화된 행은 아이콘, 경로, mode만 표시합니다. 동기화되지 않은 행은 상태 단어(`drift`, `not synced`, `no source`)를 추가로 표시합니다. transform extension이 있는 target은 동기화 mode 대신 `extension: <name>`으로 표시됩니다 (실제 mode는 항상 `copy`).

### `extras source`

전역 `extras_source` 디렉터리를 표시하거나 설정합니다. 이는 extras source 파일이 저장되는 기본 상위 디렉터리입니다.

```bash
skillshare extras source            # show current value
skillshare extras source <path>     # set new value
```

인수 없이 실행하면 현재 `extras_source` 경로를 표시합니다 (자동 감지된 경우 `(default)` 표시). 경로 인수를 전달하면 전역 config의 `extras_source`를 업데이트합니다.

:::note
이 명령어는 전역 전용입니다. 프로젝트 모드는 항상 `.skillshare/extras/`를 사용하며 `extras_source`를 지원하지 않습니다.
:::

**Examples:**

```bash
# Show current extras_source
skillshare extras source

# Set to a shared directory
skillshare extras source ~/company-shared/extras
```

### Operating on an existing extra

`extras <name>`에 대한 플래그를 통해 target의 동기화 mode나 flatten 설정을 변경하거나, target을 추가/제거합니다 — 모두 config 전용 작업입니다. 이후 디스크에 변경사항을 적용하려면 `skillshare sync extras`를 실행하세요.

```bash
skillshare extras <name> --mode <mode> [--target <path>] [-p|-g]
skillshare extras <name> --flatten | --no-flatten [--target <path>]
skillshare extras <name> --add-target <path> [--mode <mode>] [--flatten] [-p|-g]
skillshare extras <name> --remove-target <path> [--prune] [-p|-g]
```

**Options:**

| Flag | 설명 |
|------|-------------|
| `--mode <mode>` | 새 동기화 mode: `merge`, `copy`, 또는 `symlink` |
| `--flatten` | flatten 활성화 (하위 디렉터리 파일을 target 루트에 동기화) |
| `--no-flatten` | flatten 비활성화 |
| `--add-target <path>` | extra에 새 target 추가 |
| `--remove-target <path>` | extra에서 target 제거 (기본적으로 config 전용) |
| `--prune` | `--remove-target`과 함께: 해당 target 아래의 skillshare 관리 파일도 삭제 |
| `--target <path>` | target 디렉터리 경로 (multi-target extra에서 `--mode`에 필요; 생략 시 `--flatten`/`--no-flatten`은 모든 target에 적용) |
| `--project, -p` | 프로젝트 모드 extras 사용 (`.skillshare/`) |
| `--global, -g` | 전역 extras 사용 (`~/.config/skillshare/`) |

**Examples:**

```bash
# Change rules mode (single target — auto-resolved)
skillshare extras rules --mode copy

# Specify target explicitly (required for multi-target extras)
skillshare extras rules --mode copy --target ~/.claude/rules

# Enable / disable flatten on all targets at once
skillshare extras agents --flatten
skillshare extras agents --no-flatten

# Add a new target to an existing extra (then sync)
skillshare extras rules --add-target ~/.cursor/rules
skillshare extras commands --add-target ~/.config/opencode/commands --mode copy

# Remove a target (leaves synced files in place)
skillshare extras rules --remove-target ~/.cursor/rules

# Remove a target and delete its synced files
skillshare extras rules --remove-target ~/.cursor/rules --prune
```

Web UI(각 target의 mode 드롭다운과 flatten 체크박스)와 TUI(`M` 키)에서도 사용할 수 있습니다.

### `extras remove`

config에서 extra를 제거합니다.

```bash
skillshare extras remove <name> [--force] [-p|-g]
```

source 파일과 동기화된 target은 삭제되지 않습니다 — config 항목만 제거됩니다.

### `extras collect`

target의 로컬 파일을 extras source 디렉터리로 다시 수집합니다. 파일은 source로 복사되고 symlink로 대체됩니다.

```bash
skillshare extras collect <name> [--from <path>] [--dry-run] [-p|-g]
```

**Options:**

| Flag | 설명 |
|------|-------------|
| `--from <path>` | 수집할 target 디렉터리 (여러 target이 있으면 필수) |
| `--dry-run` | 변경 없이 수집될 항목 미리보기 |

**Example:**

```bash
# Collect rules from Claude back to source
skillshare extras collect rules --from ~/.claude/rules

# Preview what would be collected
skillshare extras collect rules --from ~/.claude/rules --dry-run
```

---

## Sync Modes

| Mode | Behavior |
|------|----------|
| `merge` (기본값) | target에서 source로의 파일별 symlink |
| `copy` | 파일별 복사 |
| `symlink` | 디렉터리 전체 symlink |

mode를 전환할 때 (예: `merge`에서 `copy`로), 다음 `sync`는 기존 symlink를 새 mode 형식으로 자동으로 대체합니다. `--force`는 필요하지 않습니다 — symlink는 항상 안전하게 대체됩니다. 로컬에서 생성된 일반 파일을 덮어쓰려면 `--force`가 필요합니다.

---

## Flatten

일부 AI 도구(예: Claude Code의 `/agents`)는 config 디렉터리의 **최상위 레벨**에 있는 파일만 인식합니다 — 하위 디렉터리로 재귀 탐색하지 않습니다. extras source가 구성을 위해 하위 디렉터리를 사용하는 경우, 동기화된 파일이 해당 도구에는 보이지 않게 됩니다.

`flatten` 옵션은 source의 하위 디렉터리 깊이와 상관없이 모든 파일을 target 루트에 바로 동기화하여 이를 해결합니다:

```yaml
extras:
  - name: agents
    targets:
      - path: ~/.claude/agents
        flatten: true
```

**Behavior:**
- `flatten: true`: `source/curriculum/tactician.md` → `target/tactician.md`
- `flatten: false` (기본값): `source/curriculum/tactician.md` → `target/curriculum/tactician.md`

**Filename collisions:** 서로 다른 하위 디렉터리에 있는 두 파일이 같은 이름을 가질 때 (예: `team-a/agent.md`와 `team-b/agent.md`), 첫 번째 파일이 우선합니다 (경로 기준 알파벳순 정렬). 이후 충돌은 경고와 함께 건너뜁니다.

**Constraints:**
- `merge`와 `copy` mode에서만 작동합니다 — `symlink` mode와는 함께 사용할 수 없습니다
- `collect`는 새로 수집된 파일을 source 루트에 배치합니다 (신규 파일에 대한 하위 디렉터리 매핑 없음)

---

## Extension transforms

일부 도구는 markdown을 읽지 않습니다. Gemini CLI는 TOML commands를, Codex CLI는 TOML agents를 요구합니다. target의 `extension` 필드는 동기화 중 각 source 파일을 target의 네이티브 형식으로 변환하는 외부 스크립트를 실행합니다.

```yaml
extras:
  - name: commands
    targets:
      - path: .claude/commands        # no extension — synced as-is
      - path: .gemini/commands
        extension: gemini-commands           # transform during sync
```

**Resolution** — 단순 이름은 extensions 디렉터리(`~/.config/skillshare/extensions/<name>` 전역, `.skillshare/extensions/<name>` 프로젝트) 아래에서 해석됩니다. 경로(`./x.sh`, `/abs/x`)는 그대로 사용됩니다.

**Copy semantics** — `extension`은 `copy` mode를 암시합니다. `extension`이 있는 target에 `mode: merge` 또는 `mode: symlink`를 설정하면 오류입니다.

**One-way** — transform은 source → target 방향으로만 실행됩니다. `extras collect`는 extension target을 건너뜁니다.

**Overwrite safety** — 생성된 출력은 `copy` mode와 동일한 충돌 규칙을 따릅니다. 출력 경로에 남아 있는 symlink는 자동으로 대체됩니다. 사용자가 직접 만든 기존 일반 파일이나 디렉터리는 그대로 유지되며 `--force`를 전달하지 않으면 건너뜁니다 (`--force`를 사용하면 충돌하는 디렉터리가 생성된 파일로 완전히 대체됩니다).

### Extension layout

단일 실행 파일이거나, manifest가 있는 디렉터리입니다:

```
.skillshare/extensions/gemini-commands/
├── extension.yaml
├── convert.js        # mapping rules you edit
└── md-toml.js        # helper for markdown/frontmatter/TOML
```

`extension.yaml`:

```yaml
run: ["node", "convert.js"]      # explicit command (argv), execed directly
output_ext: toml                  # .md → .toml; omit to keep the source extension
description: "Markdown command → Gemini CLI TOML"
```

manifest가 없는 단순 단일 파일 실행 파일은 직접 exec됩니다 (Unix에서는 shebang에 의존) 그리고 source 확장자를 유지합니다. 확장자 이름을 변경하는 transform은 디렉터리 형식을 사용해야 합니다.

### Execution contract

- source 파일 내용은 **stdin**으로 전달되며, 스크립트는 변환된 내용을 **stdout**으로 씁니다.
- 환경 변수: `SS_SRC_PATH`, `SS_REL_PATH` (source 루트 기준 상대 경로 — Gemini의 `/namespace:command` 네이밍에 유용), `SS_TARGET_DIR`, `SS_MODE`.
- 0이 아닌 종료 코드는 해당 파일을 실패로 표시합니다. 다른 파일은 계속 처리됩니다.

### Cross-platform

이 메커니즘은 크로스 플랫폼입니다. extension이 실행되는지 여부는 해당 인터프리터에 따라 달라집니다. `run`이 명시적인 명령어이기 때문에, `node`나 `python3`용으로 작성된 extension은 Windows, macOS, Linux에서 모두 작동합니다. 순수 `bash` 스크립트는 셸을 사용할 수 있는 환경(Unix, 또는 Git Bash가 설치된 Windows)에서만 실행됩니다. 모든 플랫폼에 균일하게 제공되므로 참조용 extension에는 Node가 선호되는 인터프리터입니다.

### Reference extensions

skillshare 저장소는 `extensions/` 아래에 예제 extension(`gemini-commands`, `codex-agents`)을 제공합니다. 하나를 extensions 디렉터리로 복사하여 조정하세요 — 이들은 참조용이며 자동으로 설치되지 않습니다. 각 참조 extension은 `convert.js`를 짧게 유지하여 필드 매핑만 편집하면 되도록 하며, `md-toml.js`가 markdown 읽기, 단순 frontmatter 파싱, TOML 작성을 처리합니다.

### Recipe: Codex agents

Codex CLI는 markdown이 아닌 TOML agents를 요구합니다. `source`가 임의의 디렉터리를 가리킬 수 있으므로, agents source를 extras source로 재사용하고 `codex-agents`로 변환할 수 있습니다:

```yaml
extras:
  - name: codex-agents
    source: ~/.config/skillshare/agents   # reuse the agents source
    targets:
      - path: ~/.codex/agents
        extension: codex-agents
```

`skillshare sync extras`는 각 `<agent>.md`를 `~/.codex/agents/<agent>.toml`로 변환하여, frontmatter의 `name`, `description`, `model`을 매핑하고 markdown 본문을 `developer_instructions`로 접어 넣습니다 (다른 frontmatter 키는 제거됩니다). [Codex custom agent schema](https://developers.openai.com/codex/subagents#custom-agent-file-schema)는 `name`, `description`, `developer_instructions`를 요구하므로, 참조 transform은 해석된 name, description, 또는 Markdown 본문이 비어 있을 경우 명확한 오류를 보고합니다. agents의 별도 사본은 필요하지 않습니다.

---

## Recipe: shared instructions across agents

현재 대부분의 코딩 agent는 표준 지침을 위해 `AGENTS.md`를 읽지만, 각 agent는
사용자 레벨 사본을 서로 다른 디렉터리에 보관합니다. 여러 target을 가진 extra 하나로
단일 source 파일을 모두에게 배포할 수 있습니다:

```bash
skillshare extras init instructions \
  --target ~/.codex \
  --target ~/.config/opencode \
  --target ~/.claude \
  --target ~/.gemini \
  --no-tui
```

`AGENTS.md`를 해석된 source 디렉터리
(기본값 `~/.config/skillshare/extras/instructions/`)에 넣은 다음
`skillshare sync extras`를 실행하세요.

| Agent | Global path | `AGENTS.md` 읽는 방식 |
|-------|-------------|-------------------|
| Codex CLI | `~/.codex/AGENTS.md` | 직접 |
| opencode | `~/.config/opencode/AGENTS.md` | 직접 |
| Claude Code | `~/.claude/AGENTS.md` | `CLAUDE.md` import를 통해 |
| Antigravity | `~/.gemini/AGENTS.md` | `GEMINI.md` import를 통해 |

두 agent는 사용자 레벨에서 자신만의 고정된 파일명을 읽으므로, 각각 동기화된 파일 옆에
한 줄짜리 파일이 필요합니다. 이것을 한 번만 작성하면 skillshare는 다시 건드리지
않습니다:

```markdown title="~/.claude/CLAUDE.md"
@AGENTS.md
```

```markdown title="~/.gemini/GEMINI.md"
@AGENTS.md
```

Claude Code는 `AGENTS.md`가 아니라 `CLAUDE.md`를 읽으며, 이 import 방식은
[memory documentation](https://code.claude.com/docs/en/memory)에서 다른 agent와 하나의
파일을 공유하기 위해 권장하는 방법입니다. Antigravity는 전역 rules를
`~/.gemini/GEMINI.md`에 보관하며 상대 경로 `@filename`을 rules 파일 자체의
디렉터리를 기준으로 해석하므로, 동일한 한 줄이 동기화된 `AGENTS.md`를 인식합니다.
`~/.gemini` target은 동일한 전역 파일을 읽는 Antigravity CLI도 함께 커버합니다.

source 파일 이름은 `AGENTS.md`로 유지하세요. `memory.md`와 같은 중립적인 이름도
동기화는 똑같이 되지만 더 이상 읽히지 않게 됩니다: Codex는 이름으로 `AGENTS.md`
파일들을 연결하며 import 문법이 없으므로, 그 이름으로만 파일을 인식합니다.

target은 디렉터리이므로, 모든 target은 각 파일을 source 이름 그대로 받습니다.
source 디렉터리는 모든 곳에 배포하고 싶은 파일로만 유지하세요 — 여분의 파일이
있으면 네 개의 target 모두에 그대로 전달됩니다.

:::note
이 레시피는 사용자가 작성한 지침을 공유하는 것이지, agent가 스스로 작성하는
메모리를 공유하는 것이 아닙니다. Agent는 자신만의 학습 내용을 비공개 형식으로
저장합니다 — Claude Code는 Markdown 디렉터리, Codex는 데이터베이스, Cursor는
파일이 아닌 저장소를 사용하며, 이러한 것들은 target 간 파일 복사로 이식할 수
없습니다.
:::

---

## Directory Structure

```
~/.config/skillshare/
├── config.yaml          # extras config lives here
├── skills/              # skill source
└── extras/              # extras source root
    ├── rules/           # extras/rules/ source files
    │   ├── coding.md
    │   └── testing.md
    └── prompts/
        └── review.md
```

---

## Configuration

`config.yaml`에서:

```yaml
# Optional: set a global default extras source directory
extras_source: ~/my-extras

extras:
  - name: rules
    source: ~/company-shared/rules    # optional per-extra override
    targets:
      - path: ~/.claude/rules
      - path: ~/.cursor/rules
        mode: copy
  - name: agents
    targets:
      - path: ~/.claude/agents
        flatten: true                  # sync subdirectory files flat
  - name: prompts
    targets:
      - path: ~/.claude/prompts
```

### Source Resolution Priority

각 extra의 source 디렉터리는 세 단계 우선순위로 해석됩니다:

1. **Per-extra `source`** (최우선) — 정확한 경로, 있는 그대로 사용
2. **`extras_source`** — `<extras_source>/<name>/`
3. **Default** — `~/.config/skillshare/extras/<name>/` (전역) 또는 `.skillshare/extras/<name>/` (프로젝트)

`extras list --json` 출력에는 어느 단계에서 경로가 해석되었는지를 나타내는
`source_type` 필드(`per-extra`, `extras_source`, 또는 `default`)가 포함됩니다.

:::tip Auto-populated
`skillshare init`을 실행하거나 `extras init`으로 첫 extra를 생성하면 `extras_source`는
자동으로 기본 경로(`~/.config/skillshare/extras/`)로 설정됩니다. 나중에 변경하려면
`skillshare extras source <path>`를 사용하세요.
:::

---

## Syncing

Extras는 다음으로 동기화됩니다:

```bash
skillshare sync extras        # sync extras only
skillshare sync --all         # sync skills + extras together
```

`--json`, `--dry-run`, `--force` 옵션을 포함한 전체 동기화 문서는
[sync extras](/docs/reference/commands/sync#sync-extras)를 참고하세요.

---

## Workflow

```bash
# 1. Create a new extra
skillshare extras init rules --target ~/.claude/rules --target ~/.cursor/rules

# 1b. Or with a custom source directory
skillshare extras init rules --target ~/.claude/rules --source ~/my-rules

# 1c. Reconfigure an existing extra (overwrite)
skillshare extras init rules --target ~/.cursor/rules --force

# 2. Add files to the source directory
# (edit the resolved source dir — check with: skillshare extras list --json)

# 3. Sync to targets
skillshare sync extras

# 4. List status (source_type shows where each extra's source is resolved from)
skillshare extras list

# 5. Collect a file edited in a target back to source
skillshare extras collect rules --from ~/.claude/rules

# 6. Change the global extras source directory
skillshare extras source ~/company-shared/extras
```

---

## See Also

- [sync](/docs/reference/commands/sync#sync-extras) — extras를 target에 동기화
- [status](/docs/reference/commands/status) — extras 파일 및 target 수 표시
- [Configuration](/docs/reference/targets/configuration#extras) — Extras config 레퍼런스
