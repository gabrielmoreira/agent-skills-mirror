# Local Agents

Settings → Local Agents lists CLI clients independently of model providers. Choose an Agent, open its official download guide when missing, complete sign-in in its own terminal, refresh its models, and select the Agent/model to use. Default Agent & models and the header model selector share the saved default. Media model defaults remain independent of the Agent that edits the project.

The registry contains Codex, Claude Code, Kimi Code, OpenCode, Gemini CLI, Cursor Agent, GitHub Copilot CLI, DeepSeek Harness, Qwen Code, Pi, Hermes, Antigravity, Kiro CLI, Kilo Code, Mistral Vibe, Amp, Devin, Grok Build, CodeBuddy Code, Qoder CLI, Trae CLI, MiMo Code, Aider, AtomCode, DeepSeek TUI, DeepSeek Reasonix, OpenClaude, Cline and IBM Bob. Availability depends on the installed CLI version and platform. Desktop model servers are not Agent clients.

## Detection and model selection

Listing Agents checks executable locations without launching every client. Inspecting an installed Agent runs bounded version/help and supported discovery commands. Only Codex, Claude-compatible authentication status and Cursor expose the authentication probes used here; other clients display “Sign-in managed by Agent” unless ACP explicitly reports missing authentication. Installation is not proof of login or model entitlement.

| Agent | Model discovery |
| --- | --- |
| Codex | `debug models`, excluding hidden models; supported reasoning levels |
| Claude Code, OpenClaude | Agent-managed `sonnet`, `opus`, `haiku` aliases, explicitly labeled as aliases |
| OpenCode, Cursor Agent, Grok Build | `models` catalogue output |
| Pi | `--list-models`, preserving provider/model identity |
| Qwen Code | Model IDs/names from the local settings model-provider list; credentials are not returned |
| Kimi Code, Kiro CLI, Kilo Code, Trae CLI | ACP initialize and session/new model options in a temporary directory; no prompt or client tool operation |
| CodeBuddy Code | Supported model choices advertised by CLI help |
| Other clients or unsupported CLI versions | Follow the Agent default, or manually enter an exact model ID |

Model discovery failures retain an actionable refresh message. An exact manually entered model ID does not assert that the account can use it. The Agent remains the authority for authentication and entitlement. Probe processes are bounded and their raw output is not returned to the browser or stored. An npm Windows `.cmd` shim is resolved to its JavaScript entry point for shell-free probes; unsupported shims fall back to manual guidance.

## Launch and connection

“Use in this project” prepares a quoted command scoped to the current project directory. If the installed CLI advertises `--model`, the selected model is passed directly. Otherwise the connection instruction includes the model selection for the user to apply in the Agent. Codex reasoning effort is passed through its supported configuration argument. The normal Agent approval controls remain enabled.

The dialog offers Open terminal, Copy command and Copy connection instruction. Opening the terminal is an explicit action; no Agent package is installed automatically. Sign-in uses the official CLI command or its interactive login flow. The connection instruction opens the existing local MCP guide for the chosen host. A launched terminal does not establish successful sign-in, MCP registration, active-chat connectivity or completion of a project edit. These are verified in the Agent. This feature does not introduce an embedded conversational runner.

Preferences are stored privately in `agents/preferences.json` under the installation data directory, outside the checkout and project exports. They contain only Agent/model IDs, reasoning selection and manual model IDs. They never contain copied Agent credentials. macOS/Linux terminal launch scripts are private and remove themselves when started. The application does not terminate the interactive Agent when the dialog closes.

## Verification and sources

Deterministic tests exercise discovery parsers, auth distinctions, default persistence, validation, terminal quoting, npm shim resolution, ACP negotiation and refusal of client operations. UI tests exercise the download/login/model/default/launch flow without starting real external sessions. Real provider calls, native Windows/Linux terminal acceptance and a complete external Agent editing session require separate verification.

The registry and discovery contracts were checked against [OpenDesign runtime definitions](https://github.com/nexu-io/open-design/tree/main/apps/daemon/src/runtimes/defs), [Paradev](https://github.com/paradevai/paradev), [Orca](https://github.com/stablyai/orca), [Hyperframes](https://github.com/heygen-com/hyperframes) and the official URLs in [the registry](../shared/local-agents.ts). Kimi's current upstream is [Kimi Code](https://github.com/MoonshotAI/kimi-code). Provider/Agent artwork attribution remains in the [design-system notices](../packages/design-system/providers/NOTICE.md); clients without sourced artwork use neutral shared icons.

## In-app asset conversations

The [Assets workspace](assets.md) can execute conversations through an installed Codex app-server using its existing login. Replies, asset tool calls, approvals and generation progress appear in Studio; thread identity is retained for follow-up turns. Other registered clients continue to use external MCP. Detection, model discovery, a successful protocol handshake and a paid Agent/media turn are separate checks. Closing the creator does not automatically cancel a running turn; use Stop, or reopen the saved conversation.
