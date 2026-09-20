---
sidebar_position: 3
---

# mcp

이식 가능한 MCP 연결 정의를 관리하고 네이티브 Agent 설정과 동기화합니다.
[Set up MCP once](/docs/how-to/daily-tasks/sharing-mcp)부터 시작하세요.

## Commands

```bash
skillshare mcp
skillshare mcp add
skillshare mcp edit
skillshare mcp edit docs --url https://updated.example/mcp --no-tui
skillshare mcp add docs --url https://example.com/mcp --target claude --sync
skillshare mcp add local --target codex -- company-mcp --workspace /path/to/workspace
skillshare mcp import docs --from claude --target claude --target cursor --sync
skillshare mcp import docs --file ./provider.json --target claude
skillshare mcp list --json
skillshare mcp remove docs --sync
skillshare mcp restore BACKUP_ID --dry-run
skillshare sync mcp --dry-run --json
skillshare sync mcp
skillshare sync --all
```

| Option | Meaning |
|---|---|
| `--target CLIENT` | 수신 client; 여러 client를 선택하려면 반복 지정 |
| `--url URL` | `add`용 Streamable HTTP 엔드포인트 |
| `-- command args...` | `add`용 로컬 실행 파일과 리터럴 인자 |
| `--disabled` | project mode에서 `add`와 함께 사용: Agent의 global 설정이 정의한 서버를 끕니다. [아래](#turn-off-a-global-server-in-one-project) 참고 |
| `--from CLIENT` | import할 기존 client, 또는 `--file`의 형식 |
| `--file PATH` | 네이티브 JSON/JSONC, TOML 또는 Goose YAML; `.toml`은 기본적으로 Codex로 처리되며, 다른 형식은 MCP 섹션에서 감지됨; 명시적인 방언을 지정하려면 `--from` 사용 |
| `--sync` | 저장 후 동기화; noninteractive add/import/remove는 그렇지 않으면 저장만 함 |
| `--replace` | add/import 중 기존 source 정의를 명시적으로 교체; import 시 가져온 client의 항목이 다르면 이것도 다시 작성 |
| `--dry-run`, `-n` | 저장하거나 네이티브 구성을 작성하지 않고 미리보기 |
| `--json` | 구조화된 출력; sync/preview 보고서에는 이름, 경로, 작업만 포함되며 서버 값은 포함되지 않음 |
| `--no-tui` | 대화형 메뉴 비활성화; `tui: false`, `--json`, 또는 비터미널 입출력에서도 비활성화됨 |
| `--revision ID` | add/import/remove 또는 `sync mcp`에 일치하는 미리보기 요구 |
| `--global`, `-g` | global Skillshare 구성 사용 |
| `--project`, `-p` | project Skillshare 구성 사용 |

서브커맨드 없이 실행하면 `mcp`는 대화형 터미널에서 검색 가능한 관리자를 열거나,
noninteractive mode에서는 상태를 출력합니다. 이름 없이 noninteractive import를 실행하면
선택할 수 있도록 파싱된 후보 목록을 표시하며 저장하지 않습니다. 후보는 이식 가능한
정의를 포함하며, 인식 가능한 시크릿은 참조로 변환됩니다. Agent 고유 필드는 경고로
표시되고 제외되며, 비활성화된 서버와 지원되지 않는 전송 방식은 후보를 차단합니다.
`restore`는 적용 전에 항상 다시 미리보기를 표시하며, 적용하지 않고 확인하려면
`--dry-run`을 사용하세요.

`sync mcp`는 scope flag, `--dry-run`, `--json`, `--no-tui`, `--revision`을 받습니다.
`sync --all`은 skill, agent, extras, MCP를 포함하며, 일반 `sync`는 기존 리소스 동작을
유지합니다. MCP 충돌은 `--all`이 다른 리소스를 변경하기 전에 확인됩니다. 리소스 유형과
네이티브 파일은 하나의 트랜잭션이 아니라 별개의 작업입니다.

## Interactive management

`skillshare mcp` 또는 `skillshare mcp list`를 실행하세요. skill 목록과 마찬가지로, 관리자는
검색을 위한 `/`와 상세 정보를 위한 `Enter`를 지원합니다. 연결 목록은 인자, 헤더, 환경 변수
값을 숨기며 URL 쿼리를 생략합니다.

| Key | Action |
|---|---|
| `a` | 연결 추가 |
| `i` | 하나 이상의 연결 import |
| `e` | 선택한 연결 편집 |
| `x` | 선택한 연결 제거 |
| `s` | 동기화 미리보기 및 확인 |
| `b` | client별로 백업 탐색, 최신순 |
| `r` | 상태 새로고침 |
| `q` | 종료 |

`mcp edit`, `mcp remove`, `mcp restore`는 이름이나 백업 ID가 생략된 경우 선택 메뉴를
제공합니다. 편집기는 command/URL, 인자, 환경 변수, HTTP 헤더, bearer-token 환경 참조,
수신 target을 다룹니다. 인자는 줄당 하나의 리터럴 인자 또는 JSON 배열로 입력할 수
있습니다. 전송 방식을 전환하면 새 연결 유형에 적용되지 않는 필드는 지워집니다.

Add, edit, remove, import는 **Save and sync** 또는 **Save only** 전에 미리보기를
표시합니다. Escape를 누르면 대기 중인 초안이 취소됩니다. Restore는 Agent 항목에 대한
변경 사항을 미리보고 확인하지만, source 정의는 다시 작성하지 않습니다.

서버 이름 없이 import하면 여러 항목을 선택할 수 있습니다(`Space`로 토글, `a`로 전체
선택). 유효하지 않은 후보는 건너뛰며, `--replace`를 지정하지 않는 한 기존 source 이름은
건너뜁니다. 배치 전체에 대해 호환되는 하나의 수신 client 집합을 선택하세요. 전체 배치는
source가 한 번 저장되기 전에 검증되며, 이후의 네이티브 파일 I/O 실패는 기존 복구 동작을
유지합니다.

스크립트에서는 이름과 flag를 제공하세요. `mcp edit NAME --url URL`,
`mcp edit NAME --target CLIENT`, `mcp edit NAME -- command args...`는 다른 해당 설정을
유지하면서 지정된 필드만 업데이트합니다. `--sync`가 추가되지 않는 한 저장만 합니다.
`--no-tui`를 사용하면 remove는 이름이, restore는 백업 ID가 필요합니다. `--dry-run`은
변경 사항을 저장하거나 동기화하지 않습니다.

## Source fields

인라인 `mcp.servers` 또는 `sources.mcp`로 지정한 외부 파일 중 하나를 선택하세요.
외부 파일에는 최상위 `servers` 매핑이 있습니다. `mcp.targets`는 Skillshare 설정에
남아 있습니다. 스키마는 저장소의 `schemas/mcp.schema.json`입니다.

| Server field | Meaning |
|---|---|
| `command` | 로컬 실행 파일; `url`과 함께 사용 불가 |
| `args` | 로컬 실행 파일용 리터럴 인자 목록 |
| `env` | 로컬 환경 값: 문자열 또는 `{fromEnv: VARIABLE}` |
| `url` | HTTP(S) MCP 엔드포인트; 자격 증명이나 fragment 포함 불가 |
| `headers` | HTTP 헤더: 문자열 또는 `{fromEnv: VARIABLE}` |
| `bearerToken` | `{fromEnv: VARIABLE}`; Authorization 헤더와 공존 불가 |
| `transport` | 선택적으로 `stdio` 또는 `streamable-http`; 생략 시 추론됨 |
| `targets` | 선택적 수신 client; `mcp.targets`를 재정의 |
| `disabled` | `true`만 가능, project mode 전용, 다른 연결 필드 불가. [아래](#turn-off-a-global-server-in-one-project) 참고 |

Client ID는 `claude`, `codex`, `cursor`, `vscode`, `opencode`, `kilocode`,
`grok`, `antigravity`, `amp`, `claude-desktop`, `cline`, `copilot`, `factory`, `gemini`,
`goose`, `junie`, `kiro`, `lmstudio`, `warp`, `windsurf`, `pi`입니다.
`grok`은 공식 xAI Grok CLI를 의미합니다. 서버 이름은 문자, 숫자, 점, 밑줄, 하이픈을
사용합니다. 서버는 동기화 전에 직접 또는 `mcp.targets`를 통해 최소 하나의 client를
선택해야 합니다.

Grok의 경우, 이름은 문자나 밑줄로 시작해야 하고, 문자·숫자·하이픈·단일 밑줄만 포함할
수 있으며, 밑줄로 끝날 수 없습니다. `company-docs`와 같은 이름은 지원되는 모든
client에서 동작합니다.

## Native destinations {#native-destinations}

| Client | Global | Project | Section |
|---|---|---|---|
| Claude Code | `~/.claude.json` | `.mcp.json` | `mcpServers` |
| Codex | `~/.codex/config.toml` | `.codex/config.toml` | `mcp_servers` |
| Cursor | `~/.cursor/mcp.json` | `.cursor/mcp.json` | `mcpServers` |
| VS Code | User `mcp.json` (below) | `.vscode/mcp.json` | `servers` |
| OpenCode | `~/.config/opencode/opencode.json` | `opencode.json` | `mcp` |
| Kilo Code | `~/.config/kilo/kilo.jsonc` | `kilo.jsonc` | `mcp` |
| Grok CLI | `~/.grok/config.toml` | `.grok/config.toml` | `mcp_servers` |
| Antigravity (AGY) | `~/.gemini/config/mcp_config.json` | `.agents/mcp_config.json` | `mcpServers` |
| [Amp](https://ampcode.com/docs/customize/mcp) | `~/.config/amp/settings.json` | `.amp/settings.json` | `amp.mcpServers` (literal key) |
| [Claude Desktop](https://modelcontextprotocol.io/docs/develop/connect-local-servers) | Claude application data directory, `claude_desktop_config.json` | Global only | `mcpServers` |
| [Cline](https://github.com/cline/cline/tree/main/apps/vscode/src/services/mcp) | `~/.cline/data/settings/cline_mcp_settings.json` | Global only | `mcpServers` |
| [Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers) | `~/.copilot/mcp-config.json` | `.github/mcp.json` | `mcpServers` |
| [Factory Droid](https://docs.factory.ai/harness/mcp) | `~/.factory/mcp.json` | `.factory/mcp.json` | `mcpServers` |
| [Gemini CLI](https://geminicli.com/docs/tools/mcp-server/) | `~/.gemini/settings.json` | `.gemini/settings.json` | `mcpServers` |
| [Goose](https://block.github.io/goose/docs/guides/config-files/) | `~/.config/goose/config.yaml` | Global only | `extensions` (YAML) |
| [Junie](https://junie.jetbrains.com/docs/junie-cli-mcp-configuration.html) | `~/.junie/mcp/mcp.json` | `.junie/mcp/mcp.json` | `mcpServers` |
| [Kiro](https://kiro.dev/docs/mcp/configuration/) | `~/.kiro/settings/mcp.json` | `.kiro/settings/mcp.json` | `mcpServers` |
| [LM Studio](https://lmstudio.ai/docs/app/mcp) | `~/.lmstudio/mcp.json` | Global only | `mcpServers` |
| [Warp](https://docs.warp.dev/agents/capabilities/mcp/) | `~/.warp/.mcp.json` | `.warp/.mcp.json` | `mcpServers` |
| [Windsurf (Cascade)](https://docs.devin.ai/desktop/cascade/mcp) | `~/.codeium/windsurf/mcp_config.json` | Global only | `mcpServers` |

대시보드의 서버 폼은 `fromEnv` 참조를 포함해 HTTP 헤더를 환경 변수와 동일한 방식으로
편집합니다. 서버 메뉴와 폼의 파일 개수 옆에 있는 **View what each Agent gets**는,
선택한 client에 대해 Sync가 작성할 네이티브 텍스트를 읽기 전용으로 보여줍니다. 폼에서는
아직 저장되지 않은 편집 내용이 반영됩니다. 시크릿은 참조 형태로 유지됩니다.

JSON 항목은 파일 자체의 들여쓰기에 맞춰 필드마다 한 줄씩 작성됩니다. Skillshare가
소유하지만 여전히 한 줄에 있는 항목은 `update`로 보고되며 다시 레이아웃되어 작성됩니다.
소유하지 않는 항목과 사람이 직접 서식을 지정한 항목은 레이아웃이 유지됩니다.

대시보드는 현재 scope와 호스트 플랫폼에서 사용 가능한 대상만 제공합니다. 각 서버는
한 행이며, 오른쪽의 카운트 버튼은 해당 서버의 전체 client 목록을 엽니다. Global 전용
client는 project mode에서 선택할 수 없습니다. 오른쪽의 **Sync** 박스는 아직 작성되지
않은 변경 사항을 나열합니다: client를 체크하면 source만 편집되며, Sync 페이지에서
확인한 후에 파일이 작성됩니다. 그 아래의 **Agents**는 이 머신에서 감지된 client를
나열합니다. client의 MCP 파일이 존재하거나, 해당 client가 설정을 보관하는 폴더가
존재하면 감지된 것으로 간주하므로, MCP 파일이 아직 없는 새 설치도 표시됩니다. project
mode에서는 프로젝트에 MCP 파일이 있거나 client가 전역적으로 감지된 경우 나열됩니다.

추가 client 세부 정보:

- `codex` 대상은 Codex CLI, Codex IDE 확장, ChatGPT 데스크톱 앱이 공유하는 하나의
  `config.toml`이므로, `codex`로 동기화된 서버는 셋 모두에 나타납니다. ChatGPT
  데스크톱 앱은 **Settings → MCP servers**에 이를 나열합니다. Codex는 신뢰하는
  프로젝트에서만 `.codex/config.toml`을 읽습니다. 신뢰하지 않는 프로젝트에서는
  동기화된 서버가 오류 없이 로드되지 않습니다. `cwd`, `http_headers_helper`, 도구
  목록과 승인 모드, 타임아웃, `oauth` 테이블은 이식 가능한 형태가 없습니다: import는
  이를 경고와 함께 제외하고, sync는 기존 항목에 그대로 유지합니다. Codex 플러그인이
  번들하는 MCP 서버는 `plugins.<plugin>.mcp_servers` 아래에 구성되며 여기서 관리되지
  않습니다.
- Claude Desktop 파일 동기화는 macOS와 Windows에서 **stdio만** 지원합니다.
  디렉터리는 macOS에서 `~/Library/Application Support/Claude`, Windows에서
  `%APPDATA%/Claude`입니다. 원격 커넥터는 애플리케이션에서 구성하세요.
- Cline은 기본 VS Code Stable 프로필을 대상으로 하며, Cline CLI나 다른 IDE는
  대상이 아닙니다.
- Copilot CLI는 새 항목에 대해 `tools: ["*"]`를 내보내고 기존 도구 필터는 유지합니다.
  프로젝트 `.mcp.json`이 존재하면, Copilot이 `.github/mcp.json`보다 그 파일을 먼저
  읽기 때문에 sync가 중단됩니다. 먼저 파일을 통합하세요. project mode에서 Claude
  Code와 Copilot CLI를 함께 선택하는 것도 파일을 작성하기 전에 차단됩니다. 이 중 하나의
  client에는 global mode를 사용하세요.
- Gemini는 Streamable HTTP에 `httpUrl`을 사용합니다. `url` 필드는 레거시 SSE를
  의미하며 import 시 거부됩니다. Cline은 `type: streamableHttp`를, Goose는
  `type: streamable_http`와 `uri`를 사용합니다. Skillshare가 이를 자동으로 변환합니다.
- Windows용 Goose는 `%APPDATA%/Block/goose/config/config.yaml`을 사용합니다. YAML
  편집은 관련 없는 설정, 주석, 내장 확장을 유지하지만 서식이 바뀔 수 있습니다.
  Alias, merge, 중복 키, 다중 문서는 편집을 차단합니다. 내장 확장과 keychain
  `env_keys`는 이식 가능한 MCP 연결로 import할 수 없습니다.
- Claude Code는 내장 서버용으로 예약된 이름인 `workspace`, `claude-in-chrome`,
  `computer-use`라는 이름의 서버를 건너뜁니다. 또한 자체 자격 증명을 원격 서버로
  전송하지 않습니다: `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`,
  `AWS_BEARER_TOKEN_BEDROCK`, `HTTPS_PROXY`, `NPM_TOKEN`은 `url`과 `headers`에서
  빈 값으로 읽힙니다. Skillshare는 Claude에 대해 둘 다 거부합니다. 자격 증명은
  자체적으로 이름을 지은 변수에 복사하세요.
- Claude Code는 로컬 scope도 가지고 있습니다: `--scope` 없이 `claude mcp add`로
  추가된 서버는 프로젝트별로 `~/.claude.json`에 저장됩니다. 로컬 서버는 `.mcp.json`
  이나 user scope에 있는 동일한 이름의 서버보다 항상 우선합니다. project mode에서
  Skillshare는 이러한 서버를 그것이 가리는 항목 옆에 표시하며, sync를 막지는
  않습니다. 프로젝트 폴더에서 `claude mcp remove NAME -s local`로 제거하세요.
- Cline의 VS Code 확장, CLI, SDK는 `~/.cline/data/settings/`를 공유합니다. 확장은
  이전 VS Code `globalStorage` 파일을 한 번 그곳으로 옮긴 후 더 이상 읽지 않으므로,
  Skillshare는 `~/.cline/data`가 아직 존재하지 않을 때만 이전 파일에 씁니다.
  `CLINE_MCP_SETTINGS_PATH`, `CLINE_DATA_DIR`, `CLINE_DIR`은 이 순서로 존중됩니다.
- Windsurf 지원은 문서화된 Cascade 구성을 대상으로 합니다. Windsurf의 최신 Devin
  Local agent는 자체 `~/.config/devin/mcp_config.json`을 읽으며, Skillshare는 이를
  관리하지 않습니다. Warp 프로젝트 연결은 세션마다 Warp 내부에서 승인이 필요합니다.
- Amp는 `amp mcp approve <name>` 이후에만 프로젝트의 `.amp/settings.json`에서
  서버를 실행합니다. Global 서버는 승인이 필요 없습니다.
- Kiro는 "Mcp Approved Env Vars" 설정에 나열된 이름에 대해서만 `${VARIABLE}`을
  확장하며, localhost에 한해 `http://` URL을 허용합니다.
- VS Code는 `User/profiles/` 아래의 기본이 아닌 각 프로필마다 별도의 `mcp.json`을
  유지합니다. Skillshare는 기본 프로필의 파일을 관리합니다.

환경 참조는 Amp, Copilot CLI, Factory, Gemini CLI, Kiro에 대해 `${VARIABLE}`로,
Cline과 Windsurf에 대해 `${env:VARIABLE}`로 내보내집니다. Claude Desktop, Goose,
Junie, LM Studio, Warp는 네이티브 보간이 검증되지 않았기 때문에 현재 `fromEnv`와
`bearerToken` export를 거부합니다. 사용자 정의 자격 증명이 없는 연결을 사용하거나,
지원되는 경우 수신 client에서 인증하세요. Skillshare는 참조를 평문으로 해석하지
않습니다.

Antigravity는 원격 연결용 `serverUrl`을 포함한 현재 [공식 MCP 구성](https://antigravity.google/docs/mcp)을
사용합니다. Skillshare는 이식 가능한 `url`을 자동으로 변환합니다. 이전
`.gemini/antigravity/`와 `.gemini/antigravity-cli/` 구성 위치는 관리되지 않습니다.
Antigravity의 `fromEnv`와 `bearerToken` export는 문서화된 구성에 환경 보간이
명시되어 있지 않기 때문에 차단됩니다. 사용자 정의 시크릿 헤더가 필요 없는 연결을
사용하고, 지원되는 OAuth 로그인을 Antigravity 내부에서 완료하세요. Skillshare는
참조를 평문 자격 증명으로 확장하지 않습니다.

OpenCode는 global 디렉터리에 대해 `XDG_CONFIG_HOME`을 존중합니다. 기존
`opencode.jsonc`는 `opencode.json`을 생성하는 대신 사용됩니다. 선택한 디렉터리에
둘 다 존재하면 동기화 전에 통합하세요. 사용자 지정 OpenCode 구성 경로, 디렉터리
오버라이드, 인라인 구성, 상속된 상위 파일은 관리되지 않습니다. 이들은 OpenCode에서
선택한 대상을 재정의할 수 있습니다.

Kilo Code는 OpenCode와 동일한 형식을 사용합니다. 프로젝트 루트와 `.kilo/`에서
`kilo.jsonc`와 `kilo.json`을 읽고 병합하므로, Skillshare는 이미 존재하는 파일에
쓰며 아무것도 없을 때만 `kilo.jsonc`를 생성합니다. 둘 이상 존재하면 동기화 전에
통합하세요. `KILO_CONFIG`, `KILO_CONFIG_DIR`, 이전 VS Code 확장의
`mcp_settings.json`은 관리되지 않습니다.

Kilo Code는 프로젝트 구성을 신뢰할 수 없는 것으로 취급합니다. 그곳에서는
`{env:VARIABLE}` 참조를 허용하지 않으며, 그런 참조를 발견하면 프로젝트 파일 전체를
무시합니다. 따라서 project mode에서 Skillshare는 `fromEnv`나 `bearerToken`을
사용하는 Kilo Code 서버를 거부합니다. 참조가 허용되는 global mode에서 해당 서버를
정의하세요.

OpenCode와 Kilo Code는 `local`/`remote` 유형과 `{env:VARIABLE}` 참조를 사용하며,
Grok은 `${VARIABLE}` 참조를 사용합니다. Skillshare가 이를 자동으로 변환합니다.
Claude의 `"type": "streamable-http"`는 HTTP로 import됩니다. 비활성화된 연결은
import를 차단합니다. Codex의 `startup_timeout_sec`나 `envFile`처럼 이식 가능한
대응 항목이 없는 다른 네이티브 옵션은 경고와 함께 import에서 제외되며, sync는
Agent의 기존 항목에 이를 유지합니다. Pi는 명시적으로 선택된 서드파티 확장을 통해
지원됩니다. 아래를 참고하세요.

VS Code Stable의 기본 사용자 파일은 다음과 같습니다.

- macOS: `~/Library/Application Support/Code/User/mcp.json`
- Linux: `${XDG_CONFIG_HOME:-~/.config}/Code/User/mcp.json`
- Windows: `%APPDATA%/Code/User/mcp.json`

Global Claude, Codex, Grok, Copilot 경로는 `CLAUDE_CONFIG_DIR`, `CODEX_HOME`,
`GROK_HOME`, `COPILOT_HOME`을 존중합니다. `OPENCODE_CONFIG`와
`OPENCODE_CONFIG_DIR`은 관리되지 않습니다. Amp와 Goose는 `.config` 경로를 사용하는
플랫폼에서 `XDG_CONFIG_HOME`을 존중합니다.
Project 대상은 선택한 프로젝트 루트를 기준으로 합니다. 프로젝트 신뢰, 서버 승인,
인증은 여전히 수신 Agent의 책임입니다.

## Turn off a global server in one project {#turn-off-a-global-server-in-one-project}

Agent는 자체 global MCP 파일과 프로젝트 파일을 함께 읽습니다. 따라서 global 파일에
정의된 서버는 모든 프로젝트에서 로드됩니다. 특정 프로젝트에서 로드되지 않도록
막으려면, **Agent의 global 파일이 사용하는 것과 동일한 이름**으로 항목을 추가하고
`disabled`로 표시하세요.

이는 다음 네 client에서만 동작합니다.

| Client | Supported | What Skillshare writes |
|---|---|---|
| Claude Code | 예 | `~/.claude.json`: 이름을 이 프로젝트의 `disabledMcpServers` 목록에 추가 |
| OpenCode | 예 | `opencode.json`: `"NAME": {"enabled": false}` |
| Kilo Code | 예 | `kilo.jsonc`: `"NAME": {"enabled": false}` |
| Pi with `pi-mcp-adapter` | 예 | `.pi/mcp.json`: `"NAME": {"disabled": true}` |
| Pi with `pi-mcp-extension` | 아니요 | disable 필드가 없음 |
| Codex | 아니요 | 아래 참고 |
| Every other client | 아니요 | 하나를 선택하면 오류가 발생하며 아무것도 작성되지 않음 |

스위치만 작성됩니다. Agent는 global 항목의 command나 URL을 그대로 유지합니다. 다른
client는 전체 global 항목을 프로젝트 항목으로 대체하거나 프로젝트 파일이 없기
때문에 거부됩니다. 그런 경우 단독 스위치만으로는 서버를 끄는 대신 오히려 서버를
망가뜨리게 됩니다.

Codex는 다른 이유로 거부됩니다. Codex는 `.codex/config.toml`을 필드 단위로 global
파일 위에 병합하므로, global 구성이 해당 서버를 정의하는 머신에서는
`enabled = false`만으로도 동작합니다. 정의하지 않는 머신에서는 병합된 항목에
`command`나 `url`이 없어 Codex는 `invalid transport`로 전체 구성을 로드하지
못합니다. `.codex/config.toml`은 보통 커밋되므로, 한 팀원의 스위치가 다른 팀원의
Codex 시작을 막을 수 있습니다. 대신 `~/.codex/config.toml`에서 `enabled = false`로
머신별로 서버를 끄세요.

### OpenCode and Kilo Code

```bash
cd my-project
skillshare mcp add company-docs --disabled --target opencode --target kilocode
skillshare sync mcp
```

```yaml
# .skillshare/config.yaml
mcp:
  servers:
    company-docs:
      disabled: true
      targets: [opencode, kilocode]
```

### Claude Code

Claude Code는 한 scope에서 전체 서버 항목을 가져오며 필드를 병합하지 않으므로,
`.mcp.json`의 스위치는 서버를 끄는 대신 대체해 버립니다. Claude Code는 `/mcp` 패널이
편집하는, `~/.claude.json`에 있는 자체 프로젝트별 off 목록을 유지합니다. Skillshare는
이 프로젝트의 절대 경로 아래에 이름을 추가하며, `.mcp.json`에는 아무것도 쓰지
않습니다.

```bash
skillshare mcp add company-docs --disabled --target claude
skillshare sync mcp
```

- 이 목록은 저장소가 아니라 여러분의 머신에 있습니다. 각 팀원은 자신의 체크아웃에서
  `skillshare sync mcp`를 한 번 실행합니다.
- `/mcp`에서 직접 끈 이름은 절대 가져오거나 제거되지 않습니다.
- `/mcp`에서 서버를 다시 켜면, 다음 sync에서 충돌이 보고됩니다.
  `.skillshare/config.yaml`에서 항목을 제거하거나, replace하여 다시 끄세요.
- 목록은 프로젝트의 경로로 키가 지정되므로, 프로젝트를 이동하면 새 sync가
  필요합니다.

### Pi

Pi는 모든 Pi 항목과 마찬가지로 `piExtension`이 필요하며, 반드시
`pi-mcp-adapter`여야 합니다. OpenCode와 Kilo Code는 이 필드를 무시하므로, 하나의
항목으로 셋 모두를 커버할 수 있습니다.

```bash
skillshare mcp add company-docs --disabled --target pi --pi-extension pi-mcp-adapter
```

```yaml
mcp:
  servers:
    company-docs:
      disabled: true
      piExtension: pi-mcp-adapter
      targets: [opencode, pi]
```

### Rules

- **Project mode only.** `skillshare init -p`로 생성된 `.skillshare/config.yaml`이
  있는 프로젝트 안에서 실행하거나 `-p`를 전달하세요. global mode에서는 거부됩니다.
- **`disabled`는 단독으로 사용됩니다.** 항목은 `targets`와, Pi의 경우
  `piExtension`을 받습니다. `command`, `url`, `env`, `headers`를 추가하면 오류입니다.
- **`targets`는 명시하는 것이 좋습니다.** 명시하지 않으면 항목은 `mcp.targets`를
  상속하며, 해당 목록에 지원되지 않는 client가 있으면 오류입니다.
- **이름이 일치해야 합니다.** Skillshare는 Agent의 global 파일을 읽지 않으므로,
  이 이름의 서버가 그곳에 존재하는지 확인할 수 없습니다. 아무것도 일치하지 않는
  이름은 문제가 되지 않습니다: Agent가 이를 무시할 뿐입니다.
- **다시 켜려면**, 항목을 제거하고(`skillshare mcp remove company-docs`) sync하세요.
  프로젝트 파일에서 스위치가 제거됩니다.
- **Skillshare가 직접 정의하는 서버는 이것이 필요 없습니다.** 대신 해당 서버에서
  Agent 선택을 해제하면, 다음 sync에서 그 항목이 제거됩니다.

대시보드에서는 서버를 추가할 때 `stdio`와 `streamable-http` 옆에 있는 **Off in
this project** 선택지가 이에 해당합니다. project mode에서만 표시됩니다.

## Safety and limitations

- JSONC 주석과 관련 없는 설정은 보존됩니다. 변경된 소유 항목은 하나의 단위로
  교체되므로, 해당 항목 안의 주석은 바뀔 수 있습니다. Skillshare가 작성하는 필드만
  비교되고 교체되며, 타임아웃 같은 Agent 고유 필드는 유지됩니다.
  `"type": "stdio"`, 빈 `env`, 헤더 이름 대소문자처럼 Agent가 채우는 기본값은
  변경으로 간주되지 않습니다. `enabled: false`나 `disabled: true`로 관리되는 서버를
  끄는 것은 충돌로 보고됩니다.
- Claude Code가 `~/.claude.json`에서 하는 것처럼 Agent가 같은 파일의 관련 없는
  설정을 다시 쓰는 동안에도 미리보기는 유효하게 유지됩니다. 해당 파일의 MCP 항목이
  변경된 경우에만 새 미리보기가 필요합니다.
- Codex와 Grok 편집은 일반적인 `[mcp_servers.NAME]` 테이블과 그 하위 테이블을
  지원합니다. 업데이트된 항목은 제자리에 유지되며, CRLF 줄바꿈도 유지됩니다.
  인라인/점 표기 MCP 정의는 작성하기 전에 테이블로 변환해야 하며, 그렇지 않으면
  파일을 수정하지 않고 거부됩니다.
- 네이티브 파일 symlink, 손상된 파일, 중복 JSON 속성은 쓰기를 차단합니다.
  symlink된 Skillshare `config.yaml`은 그 대상으로 전달되어 작성됩니다. 파일
  권한은 보존되며, 새 네이티브 파일, 소유권 기록, 백업은 private 권한을 사용합니다.
- source와 이미 일치하는 항목은, 예를 들어 팀원의 변경 사항을 pull한 후처럼, 쓰기
  없이 unchanged로 보고됩니다. 프로젝트를 이동한 후처럼 이 구성이 이전에 이를
  관리하지 않았다면 unmanaged 상태로 남습니다: 서버를 제거해도 import하기 전까지는
  그대로 남습니다. 다른 unmanaged 항목은 import나 명시적인 항목별 replace가
  필요합니다. 소유하는 구성 파일이 여전히 존재하는 동안에는 다른 Skillshare
  구성의 소유권을 재정의할 수 없습니다. 이동하거나 삭제된 경우에는 그 항목을 영원히
  해제할 수 없으므로, 명시적인 import나 replace가 이를 가져옵니다. 충돌 메시지는
  소유 파일의 이름을 표시합니다.
- 대시보드의 MCP 설정은 브라우저가 `localhost`나 IP 주소로 대시보드를 열 때만
  동작합니다. 리버스 프록시를 포함한 도메인 이름을 통하면 MCP 요청은 403을
  반환합니다. DNS rebinding 공격은 항상 도메인 이름을 사용하기 때문입니다.
- 자격 증명은 환경 참조를 사용합니다. 시크릿 저장소, OAuth 세션 동기화, 런타임
  상태 확인, 패키지 설치, 게이트웨이, 레지스트리, 플러그인 동기화는 없습니다.
- VS Code Insiders, 사용자 지정 프로필, 원격 워크스페이스, 레거시 SSE는 이 버전에서
  지원되지 않습니다.
- VS Code는 현재 `headers` 안에서 `${env:VARIABLE}`을 치환하지 않으므로
  ([microsoft/vscode#336232](https://github.com/microsoft/vscode/issues/336232)),
  VS Code로 동기화된 헤더와 `bearerToken` 참조는 해당 문제가 수정될 때까지 서버에
  해석되지 않은 채로 도달합니다.
- 로컬 작업 기록은 Skillshare state 디렉터리의 `mcp/` 아래에 존재합니다:
  `state.json`, 쓰기 중의 `pending.json`, 그리고 `backups/`(Agent 파일별 최신 20개).
  이 디렉터리를 이식 가능한 매니페스트로 공유하지 마세요.


## Pi: choose your MCP extension {#pi-choose-your-mcp-extension}

Pi는 [pi-mcp-adapter](https://pi.dev/packages/pi-mcp-adapter) 또는
[pi-mcp-extension](https://pi.dev/packages/pi-mcp-extension) 중 하나를 통해 MCP를
사용할 수 있습니다. 이들은 Pi 웹사이트에 나열된 서드파티 패키지이며, 내장 Pi
기능이 아닙니다. Pi에는 **하나만** 설치하세요.

```bash
pi install npm:pi-mcp-adapter
```

설치 후 Pi를 재시작하세요. Skillshare의 MCP 폼에서 **Pi**를 선택한 다음, 설치한
패키지를 선택하세요. import 대화 상자도 동일한 선택지를 제공합니다. 터미널에서는
`mcp add` / `mcp edit`이 선택을 안내하며, 스크립트는 반드시 `--pi-extension`을
제공해야 합니다.

```bash
skillshare mcp add docs --url https://example.com/mcp --target pi --pi-extension pi-mcp-adapter --no-tui
skillshare sync mcp --dry-run
skillshare sync mcp
```

저장된 서버 정의는 다음과 같습니다.

```yaml
mcp:
  servers:
    docs:
      url: https://example.com/mcp
      targets: [pi]
      piExtension: pi-mcp-adapter
```

다른 패키지를 사용하려면 install 명령과 선택지 모두에서 `pi-mcp-extension`을
사용하세요. 두 패키지 모두 동일한 대상 파일을 읽으므로, Skillshare source 안에서
Pi를 대상으로 하는 모든 서버는 동일한 패키지를 선택해야 합니다.

| Package | Native output | What to do after sync |
|---|---|---|
| `pi-mcp-adapter` | `command`/`args` 또는 `url`; `${VARIABLE}` 참조 | Pi 재시작/재로드; `/mcp`로 연결 확인. 도구는 필요 시 연결됨 |
| `pi-mcp-extension` | 명시적인 `transport: stdio` 또는 `streamable-http` | Pi 재시작; 새 서버는 기본적으로 `/mcp:start <server>`로 수동 시작. 기존 `lifecycle` 설정은 유지됨 |

둘 다 global에서는 `~/.pi/agent/mcp.json`을, project mode에서는 `.pi/mcp.json`을
사용합니다. Skillshare는 이러한 Pi 전용 파일을 사용하며, adapter가 공유하는
`.mcp.json`이나 `~/.config/mcp/mcp.json` 입력은 사용하지 않습니다. 프로젝트 항목은
동일한 이름의 global 항목을 재정의합니다. adapter의 경우, global
`PI_CODING_AGENT_DIR` 오버라이드가 존중됩니다. extension은 이 오버라이드를
존중하지 않으므로, global sync는 extension이 무시할 파일을 작성하는 대신 이를
거부합니다.

adapter는 환경 변수와 HTTP 헤더에서 `fromEnv`를 지원합니다. extension은 환경
참조를 보간하지 **않습니다**: 일치하는 stdio 변수(예: `TOKEN: {fromEnv: TOKEN}`)는
대신 Pi의 프로세스에서 상속되며, 변수 이름 변경과 환경 기반 HTTP 자격 증명은
거부됩니다. 이런 경우에는 adapter를 사용하세요. Skillshare는 시크릿 값을 절대
읽거나 복사하지 않습니다.

`--from pi`로 import하면 Pi 전용 파일을 읽습니다. import한 연결을 저장할 때
`--pi-extension`을 선택하세요. 파일만으로는 어떤 패키지가 설치되어 있는지 식별할
수 없습니다. 지원되지 않는 레거시 SSE는 계속 차단됩니다. OAuth와 패키지 전용
옵션은 Pi 안에서 계속 관리됩니다. Sync 성공은 구성이 작성되었음을 의미할 뿐, 확장이
설치되었거나 서버가 연결되었음을 의미하지 않습니다.
