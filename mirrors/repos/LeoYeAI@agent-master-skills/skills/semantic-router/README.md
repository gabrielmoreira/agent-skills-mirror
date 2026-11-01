# Semantic Router

[![Version](https://img.shields.io/badge/version-7.9.5-blue)](https://clawhub.ai/halfmoon82/semantic-router)
[![License](https://img.shields.io/badge/license-MIT--0-green)](https://spdx.org/licenses/MIT-0.html)
[![Status](https://img.shields.io/badge/status-production_ready-brightgreen)](https://clawhub.ai/halfmoon82/semantic-router)

> **Production-grade session routing system for OpenClaw agents.**

Automatically select the optimal AI model based on conversation context. Four-layer recognition (system filtering → keywords → indicators → semantic similarity), four-pool architecture (Highspeed/Intelligence/Humanities/Agentic), five-branch routing with automatic fallback.

## 🎯 What Problem Does This Solve?

- **Cron Jobs resetting user sessions** — Background tasks interrupting active conversations
- **Discord/Telegram sessions suddenly clearing** — Long tasks losing context
- **AGENTS.md injection failures** — Large files exceeding 20KB limit
- **Model switching overridden by global config** — Routing not taking effect

## ⚠️ Security & Permissions Declaration

**This skill performs privileged operations — all are intentional and user-initiated:**

| Operation | Purpose | Scope |
|-----------|---------|-------|
| Read/patch `~/.openclaw/openclaw.json` | Configure model routing pools | Local config only |
| Read/write `~/.openclaw/workspace/.lib/pools.json` | Store model pool configuration | Workspace only |
| Read/write `~/.openclaw/workspace/.lib/tasks.json` | Store task type definitions | Workspace only |
| Run `semantic_check.py` locally | Classify user messages for routing | No network required |
| Patch session model via `sessions.patch` | Switch active model pool | Current session only |
| Restart OpenClaw Gateway | Apply routing config changes | Local service only |
| Update Cron Job `sessionTarget` | Isolate background tasks from user sessions | Cron jobs only |

**What this skill does NOT do:**
- Does NOT exfiltrate data to external servers
- Does NOT access API keys or secrets directly
- Does NOT modify files outside `~/.openclaw/`
- Does NOT run with elevated privileges
- Does NOT auto-install packages

## 🚀 Quick Start

### Installation

```bash
# Install from ClawHub
clawhub install https://clawhub.ai/halfmoon82/semantic-router

# Or manual installation
cp -r ~/.openclaw/workspace/skills/semantic-router ~/my-projects/
```

### Configuration

```bash
# Run interactive setup wizard
python3 ~/.openclaw/workspace/skills/semantic-router/scripts/setup_wizard.py
```

### Isolate Existing Cron Jobs

```bash
# List your Cron Jobs
cron list | jq '.jobs[] | {id, name, sessionKey}'

# Isolate jobs using channel sessions
cron update {job_id} \
  --patch '{"sessionKey": null, "sessionTarget": "isolated"}'
```

## 🏗️ Architecture

### Four-Pool Model Architecture

| Pool | Purpose | Example Models | Characteristics |
|------|---------|----------------|-----------------|
| **Highspeed** | Queries, retrieval, search | gemini-2.5-flash | Fast, cost-effective |
| **Intelligence** | Development, coding, complex tasks | claude-sonnet-4.6 | Precise, capable |
| **Humanities** | Content generation, translation | gemini-2.5-pro | Balanced, fluent |
| **Agentic** | Long-context agents, Computer Use | gpt-5.4 | 1M context, tool calling |

### Five-Branch Routing

| Branch | Trigger | Action | Session Behavior |
|--------|---------|--------|------------------|
| **A** | Keyword match | Switch to target pool | Switch model, no reset |
| **B** | Indicator (continuation) | Keep current | No action |
| **B+** | Medium correlation (0.08~0.15) | Keep + warn | Drift warning |
| **C** | New task keyword | Switch to target pool | Switch model, no reset |
| **C-auto** | Low correlation (<0.08) | Reset + switch pool | `/new` + switch model |

## 📚 Documentation

- [SKILL.md](SKILL.md) — Full skill documentation (Chinese)
- [README_v3_PRODUCTION.md](references/README_v3_PRODUCTION.md) — Production deployment guide (English)
- [declaration-format.md](references/declaration-format.md) — Declaration format specification

## 🔧 Requirements

- Python 3.8+
- OpenClaw Gateway running
- Configured model providers

## 📄 License

MIT-0 — Free to use, modify, and redistribute. No attribution required.

---

**Maintainer**: halfmoon82  
**ClawHub**: https://clawhub.ai/halfmoon82/semantic-router  
**Last Updated**: 2026-03-12
