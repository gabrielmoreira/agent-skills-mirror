# Agent Zero Desktop

This Desktop is Agent Zero's habitat: a visible, stateful Linux workspace where humans and agents can share files, launch tools, inspect results, and turn reasoning into observable work.

You can choose your harness, but now you and A0 have a habitat.

Here, the model reasons, the environment remembers, the user grants permission, and the work leaves artifacts that can be opened, tested, revised, and trusted. It is a small workshop for the larger idea: agents become more useful when they have a safe world to act in, not only more instructions to carry.

With gratitude to the open-source foundations that make this affordance possible:

- Xpra, for carrying a live Linux desktop through the browser, making this desktop environment usable by AI agents.
- Kali Linux, for the practical Linux craft and tool culture that make capable workspaces feel natural.
- LibreOffice, for giving this habitat a serious office bench: documents, spreadsheets, presentations, and decades of open document stewardship.
- Xfce, for a fast, humane desktop that stays out of the way and lets the work breathe.
- Jan Tomášek, for creating Agent Zero and making this whole workshop possible.

Agent Zero stands on this craft with respect. Open source is not just code we consume; it is shared affordance, accumulated care, and an invitation to build systems that are powerful without becoming opaque.

## Open the Terminal

Double-click **Terminal** on this Desktop. You will land in the Agent Zero workdir, where agent CLIs can inspect files, edit projects, and run commands inside the Linux environment.

Before installing an agent, make a small safety habit:

```bash
pwd
node -v || true
npm -v || true
python3 --version || true
curl --version | head -1 || true
```

Agent CLIs are powerful. Install from official sources, avoid `sudo npm install -g` unless the project explicitly requires it, and keep API keys in your shell or provider login flow rather than pasting secrets into documents.

## Install Your Favorite Agent

These commands were checked against official docs or project READMEs on 2026-05-02. Package names matter.

### OpenAI Codex

```bash
npm i -g @openai/codex
codex
```

### Claude Code

Recommended native installer:

```bash
curl -fsSL https://claude.ai/install.sh | bash
source ~/.bashrc
claude
```

NPM alternative:

```bash
npm install -g @anthropic-ai/claude-code
claude
```

### Gemini CLI

```bash
npm install -g @google/gemini-cli
gemini
```

### Aider

```bash
curl -LsSf https://aider.chat/install.sh | sh
source ~/.bashrc
aider
```

### OpenCode

```bash
curl -sL https://opencode.ai/install | bash
opencode
```

NPM alternative:

```bash
npm i -g opencode
opencode
```

### Goose

```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
source ~/.bashrc
goose
```

### OpenHands CLI

```bash
python3 -m pip install uv
uv tool install openhands --python 3.12
openhands
```

### Qwen Code

```bash
npm install -g @qwen-code/qwen-code@latest
qwen
```

### Cursor Agent

```bash
curl https://cursor.com/install -fsS | bash
source ~/.bashrc
cursor-agent
```

### Hermes Agent

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc
hermes
```

### OpenClaw

OpenClaw recommends Node 24, or Node 22.14+.

```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

If in doubt, start with Codex or Claude Code for coding, Aider for a lighter patch-focused loop, Goose or OpenHands for a broader local agent, and Hermes or OpenClaw when you want the agent to grow into more of a persistent runtime working together with Agent Zero.

Official references: [Codex](https://developers.openai.com/codex/cli), [Claude Code](https://code.claude.com/docs/en/getting-started), [Gemini CLI](https://google-gemini.github.io/gemini-cli/docs/get-started/), [Aider](https://aider.chat/docs/install.html), [OpenCode](https://www.opencode.live/), [Goose](https://goose-docs.ai/docs/getting-started/installation/), [OpenHands](https://docs.openhands.dev/openhands/usage/cli/installation), [Qwen Code](https://github.com/QwenLM/qwen-code), [Cursor Agent](https://docs.cursor.com/en/cli/installation), [Hermes Agent](https://github.com/NousResearch/hermes-agent), [OpenClaw](https://github.com/openclaw/openclaw).
