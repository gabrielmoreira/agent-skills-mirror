---
name: a0-setup-cli
description: Guide the user through installing and connecting the A0 CLI on the host machine so Dockerized Agent Zero can work on real local files. Use when asked to install A0, set up the CLI connector, connect Agent Zero to local files, or troubleshoot host-vs-container setup confusion.
version: 1.1.0
author: Agent Zero Team
tags: ["agent-zero", "a0", "cli", "connector", "docker", "setup", "local-files"]
trigger_patterns:
  - "install a0"
  - "install a0 cli"
  - "set up a0 cli"
  - "set up a0 cli connector"
  - "connect a0 to agent zero"
  - "connect agent zero to local files"
  - "let agent zero work on my local files"
  - "install the terminal connector"
  - "help me set up the a0 cli connector"
  - "install a0 connector"
---

# A0 CLI Host Setup

Use this skill to guide the user through installing `a0` on their host machine and connecting it to Agent Zero.

## Core Boundary

- Agent Zero stays in Docker or its sandboxed runtime.
- `a0` installs and runs on the user's host machine.
- The whole point is to let Agent Zero work on the real files on the user's computer.

## Response Flow

### 1. Ask whether they already tried

Start here:

> Have you already tried installing `a0`? If so, what command did you run, where did you run it, and what happened?

If they already tried, diagnose that attempt before repeating instructions.

### 2. Stop container installs immediately

If the user is inside the Agent Zero container, `/a0`, `docker exec`, or another sandbox shell, stop and say:

> `a0` does not get installed inside the Agent Zero container. Exit to your normal host terminal first. Agent Zero stays in Docker; `a0` belongs on your machine.

Do not keep giving install commands until they are back on the host.

### 3. Identify the host OS only as needed

If the platform is unclear, ask one short question:

> Are you on macOS/Linux shell or Windows PowerShell on the host machine?

Then use the matching installer.

### 4. Use the installer-first flow

Treat these public installer URLs as placeholders for now. Use them first, but be ready to switch to the manual `uv tool install` path if the raw GitHub URL is blocked, private, or unreachable.

macOS / Linux:

```bash
curl -LsSf https://raw.githubusercontent.com/agent0ai/a0-connector/main/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/agent0ai/a0-connector/main/install.ps1 | iex
```

The installer will install `uv` if needed, then run `uv tool install --upgrade <package-spec>` for the CLI.

### 5. Use the manual `uv tool install` fallback when needed

If the placeholder installer URL is unavailable, switch to a manual `uv tool install` flow instead of stopping.

Public Git fallback:

```bash
uv tool install --upgrade git+https://github.com/agent0ai/a0-connector
```

Local checkout or internal mirror examples:

```bash
uv tool install --upgrade /path/to/a0-connector
uv tool install --upgrade git+ssh://git.example.com/team/a0-connector.git
```

If they want to reuse the stock installer with a custom package source, explain that the installer honors `A0_PACKAGE_SPEC`.

### 6. Tell them to run `a0`

After install, the next step is always:

```bash
a0
```

If the command is not found yet, tell them to open a new terminal and run `a0` again.

### 7. Explain how to connect

Tell the user what to expect:

- `a0` opens the host picker first.
- If Agent Zero is running locally, `a0` may discover it automatically.
- If not, the user can enter the Agent Zero web URL manually in the custom URL field.
- The custom URL can be either a normal address with a port, such as `http://localhost:50001`, or a tunnel URL.
- For Flare Tunnel, tell the user to open `Settings > External Services > Flare Tunnel`, click `Create Tunnel`, then copy and paste the HTTPS URL into `a0` exactly as shown.
- Tunnel URLs such as `https://example.trycloudflare.com` do not need a port appended.
- `AGENT_ZERO_HOST` can prefill the target host without bypassing the picker.

Example:

```bash
export AGENT_ZERO_HOST=http://localhost:50001
a0
```

Tunnel example:

```bash
export AGENT_ZERO_HOST=https://example.trycloudflare.com
a0
```

### 8. Define success clearly

Successful setup looks like this:

- `a0` starts on the host machine.
- It connects to the user's Agent Zero instance or reaches the login step.
- The user can open a chat from the terminal.
- Agent Zero can now act on real files on the host through the connector flow while Agent Zero itself still runs in Docker.

## Troubleshooting

- If the user says they installed inside Docker or shows `/a0` paths, redirect them to the host-machine install.
- If `a0` gets a connector `404`, explain that the running Agent Zero build likely does not include the builtin `_a0_connector` support yet and should be updated.
- If the browser UI works but `a0` does not, remind them the web UI can run without connector support but the CLI cannot.
- If Docker discovery does not find the instance, have them enter the exact Agent Zero URL with `host:port`, or create a Flare Tunnel in `Settings > External Services > Flare Tunnel` and paste that HTTPS URL directly.

## Example Requests And Responses

### Example 1

User: "Help me set up the A0 CLI connector."

Respond like this:

1. Ask whether they already tried and whether they are on the host machine.
2. If the OS is unknown, ask whether they are in macOS/Linux shell or Windows PowerShell.
3. Give the matching installer command.
4. Tell them to run `a0`.
5. Explain what the host picker and successful connection should look like.

### Example 2

User: "I'm inside the Agent Zero container. How do I install A0?"

Respond like this:

- Stop the flow.
- Explain that `a0` must be installed on the host, not in the container.
- Tell them to exit Docker, open a normal terminal on the machine, then continue with the host installer.

### Example 3

User: "The raw GitHub installer URL is blocked on our network."

Respond like this:

- Say the public installer URL is only a placeholder path.
- Switch to a manual `uv tool install --upgrade <package-spec>` flow.
- Offer examples for a local checkout, internal Git host, or the public Git URL if that one works.
- Then tell them to run `a0` and connect to Agent Zero.
