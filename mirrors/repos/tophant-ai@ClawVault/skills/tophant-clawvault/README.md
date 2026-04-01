# ClawVault Skill

AI security system for OpenClaw - protect your AI agents from prompt injection, data leakage, and dangerous commands.

## ⚠️ Security Notice

**Important:** ClawVault operates as a local HTTP proxy that inspects AI traffic.

- ClawVault can see API requests, responses, and API keys
- This is intentional and necessary for threat detection
- All data stays on your local machine
- **Review [SECURITY.md](./SECURITY.md) before installing**

**Dashboard Security:**
- Default: Binds to `127.0.0.1` (localhost only) - Secure ✅
- Remote: `--dashboard-host 0.0.0.0` - Exposes to network ⚠️
- **Recommendation:** Use SSH tunneling for remote access

## Quick Start

### Installation

**Option 1: Install from ClawHub (Recommended)**

```bash
# Install from ClawHub
openclaw skills install tophant-clawvault

# Or use clawhub CLI
clawhub install tophant-clawvault
```

**ClawHub:** https://clawhub.ai/Martin2877/tophant-clawvault

**Option 2: Install from Local Repository**

```bash
# Copy to OpenClaw skills directory
cp -r skills/tophant-clawvault ~/.openclaw/skills/

# Or create symbolic link
ln -s /path/to/ClawVault/skills/tophant-clawvault ~/.openclaw/skills/tophant-clawvault

# Restart OpenClaw
openclaw restart
```

### Basic Usage

```bash
# Install ClawVault
/clawvault install --mode quick

# Check health
/clawvault health

# Generate security rule
/clawvault generate-rule "Block all AWS credentials" --apply

# Run tests
/clawvault test --category all
```

## Features

- **AI-guided installation** - Quick, standard, or advanced setup modes
- **Rule generation** - Create security rules from natural language
- **Scenario templates** - Pre-configured policies (customer_service, development, production, finance)
- **Detection testing** - Built-in test suites for validation
- **Health monitoring** - Real-time service status

## Documentation

- **Security Guide**: [SECURITY.md](./SECURITY.md) ⚠️ **Read this first**
- **Skill Reference**: [SKILL.md](./SKILL.md)
- **Complete Guide**: [../../doc/OPENCLAW_SKILL.md](../../doc/OPENCLAW_SKILL.md)
- **中文文档**: [../../doc/zh/OPENCLAW_SKILL.md](../../doc/zh/OPENCLAW_SKILL.md)

## Requirements

- Python 3.10+
- OpenClaw installed
- Ports 8765, 8766 available

## Support

- **Repository**: https://github.com/tophant-ai/ClawVault
- **Issues**: https://github.com/tophant-ai/ClawVault/issues
- **Documentation**: https://github.com/tophant-ai/ClawVault/tree/main/doc

## License

MIT © 2026 Tophant SPAI Lab
