# Security Policy

## Reporting a vulnerability

**Do not** open a public GitHub issue for security vulnerabilities.

Email the maintainer directly at **mbektasgh@outlook.com** with:

- A description of the vulnerability and the impact you observed.
- Steps to reproduce, including affected versions of NBI, JupyterLab, and Python.
- Any proof-of-concept code or logs (redact secrets).

Expect an acknowledgement within five business days. Once we confirm the issue, we'll work with you on a coordinated disclosure timeline.

## Supported versions

NBI follows semantic versioning starting with 4.0.0. Security fixes land on the latest minor release of the current major line. Earlier major lines are not actively maintained.

| Version | Supported          |
| ------- | ------------------ |
| 6.x     | Yes (latest minor) |
| < 6.0   | No                 |

## Scope

In-scope:

- The `notebook_intelligence` server extension and its HTTP handlers.
- The `@plmbr/notebook-intelligence` JupyterLab frontend.
- Built-in tools (`nbi-notebook-edit`, `nbi-notebook-execute`, `nbi-python-file-edit`, `nbi-file-edit`, `nbi-file-read`, `nbi-command-execute`).
- The Claude Skills import and managed-manifest reconciler.
- ACP agent mode: the protocol router, what NBI serves or refuses an agent, and the credential handling around the adapter subprocess.
- The Chatbook kernel and its generate API, which execute model-written code as the user.
- The UI-tools relay (`/notebook-intelligence/ui-tools`) and the `notebook_intelligence.mcp_ui_proxy` standalone server.

Out of scope:

- Vulnerabilities in upstream dependencies (`litellm`, `anthropic`, `openai`, `ollama`, `claude-agent-sdk`, `mcp`, `agent-client-protocol`) — please report those upstream. We will pick up patched releases when they ship.
- Vulnerabilities in MCP servers users install from third-party sources.
- Vulnerabilities in LLM providers themselves (data handling at OpenAI, Anthropic, GitHub Copilot, etc.).

## Security model

NBI is a **per-user** tool. The server extension runs inside the user's Jupyter Server process and inherits that user's permissions. Built-in tools shell out as the user, MCP stdio servers run as the user, the Chatbook kernel executes generated code as the user, and the Claude Code CLI inherits the user's environment. There is no privilege boundary between the extension and the user's account.

Within that, a few boundaries are deliberate and worth stating, because they are what a report should be measured against:

- **An ACP agent is not lent the client's reach.** NBI refuses filesystem reads and writes, terminal methods, and agent extension requests at the protocol router, so the agent does its own I/O under its own sandbox rather than through the Jupyter server process. The approval cards are the mediation point, with the honest limit that the agent chooses what to ask about.
- **Approval prompts are rendered so they cannot be forged.** Command text is fenced with a collision-resistant delimiter and bidirectional control characters are rejected, so what an approval card shows is what would run.
- **Commands the backend can ask the frontend to run are allowlisted** at a single chokepoint, rather than being any JupyterLab command id. `run-command-in-terminal` stays on that list, so shell reachability is unchanged by it.
- **`mcp_stdio_command_allowlist`** is the mitigation admins have for stdio MCP servers, which otherwise run any command an `mcp.json` names. See [Restricting MCP stdio commands](docs/admin-guide.md#restricting-mcp-stdio-commands).

For multi-tenant deployments, see [`docs/admin-guide.md`](docs/admin-guide.md) for guidance on disabling features that are unsafe to expose without additional sandboxing (notably `nbi-command-execute` and `nbi-file-edit`).
