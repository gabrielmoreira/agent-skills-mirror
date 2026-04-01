---
name: tophant-clawvault
version: 0.1.2
description: AI security system for protecting agents from prompt injection, data leakage, and dangerous commands
homepage: https://github.com/tophant-ai/ClawVault
user-invocable: true
disable-model-invocation: false
---

# ClawVault Skill

AI security system for OpenClaw with installation, rule generation, detection, and monitoring.

**Protection Against:**
- Prompt injection attacks
- Data leakage (PII, credentials, API keys)
- Dangerous command execution
- Jailbreak attempts

## Commands

### /clawvault start

Start ClawVault services.

```bash
clawvault start                  # Default: localhost only (secure)
clawvault start --mode strict    # Strict mode
```

### /clawvault install

Install ClawVault.

```bash
/clawvault install --mode quick     # Recommended
/clawvault install --mode standard  # Interactive
/clawvault install --mode advanced  # Full control
```

### /clawvault health

Check service health and status.

```bash
/clawvault health
```

### /clawvault generate-rule

Generate security rules from natural language.

```bash
/clawvault generate-rule "Block all AWS credentials"
/clawvault generate-rule --scenario customer_service --apply
```

**Scenarios:** `customer_service`, `development`, `production`, `finance`

### /clawvault status

Get running status and statistics.

```bash
/clawvault status
```

### /clawvault test

Run detection tests.

```bash
/clawvault test --category all
/clawvault test --category sensitive
```

**Categories:** `all`, `sensitive`, `injection`, `commands`

### /clawvault uninstall

Remove ClawVault.

```bash
/clawvault uninstall
/clawvault uninstall --keep-config  # Keep configuration
```

## Quick Examples

```bash
# Install
/clawvault install --mode quick

# Generate rule
/clawvault generate-rule "Detect database passwords" --apply

# Apply scenario
/clawvault generate-rule --scenario customer_service --apply

# Check health
/clawvault health
```

## Requirements

- Python 3.10+
- Ports 8765, 8766 available

## Permissions

- `execute_command` - Run installation and ClawVault commands
- `write_files` - Create configuration files
- `read_files` - Read configurations
- `network` - Download packages and API calls

## Security Considerations

⚠️ **Important:** ClawVault operates as a local HTTP proxy that inspects AI traffic.

**What This Means:**
- ClawVault can see API requests, responses, and API keys
- This is intentional and necessary for threat detection
- All data stays on your local machine

**Dashboard Security:**
- Default: Binds to `127.0.0.1` (localhost only) ✅ Secure
- **For remote access:** Use SSH tunneling instead of exposing dashboard
- Example: `ssh -L 8766:localhost:8766 user@server`

**Before Installing:**
- Review the [SECURITY.md](./SECURITY.md) documentation
- Understand that ClawVault will inspect all proxied traffic
- Ensure dashboard binding is appropriate for your environment
- Consider running in isolated environment for sensitive use cases

**For Production:**
- Use localhost-only dashboard
- Enable strict mode: `--mode strict`
- Configure audit log retention
- Review detection logs regularly

See [SECURITY.md](./SECURITY.md) for complete security documentation.

## Documentation

- **Full Guide**: https://github.com/tophant-ai/ClawVault/blob/main/doc/OPENCLAW_SKILL.md
- **中文文档**: https://github.com/tophant-ai/ClawVault/blob/main/doc/zh/OPENCLAW_SKILL.md
- **Repository**: https://github.com/tophant-ai/ClawVault

## License

MIT © 2026 Tophant SPAI Lab
