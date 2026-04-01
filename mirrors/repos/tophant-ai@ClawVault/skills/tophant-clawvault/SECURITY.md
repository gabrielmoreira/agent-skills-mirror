# Security Documentation

## Overview

ClawVault is a security-focused AI protection system that operates as a local HTTP proxy to inspect and protect AI agent traffic. This document explains the security model, potential risks, and best practices for safe deployment.

## How ClawVault Works

### Proxy Architecture

ClawVault runs as a **local HTTP proxy** that intercepts traffic between AI agents and LLM providers:

```
AI Agent → ClawVault Proxy (localhost:8765) → LLM Provider APIs
                    ↓
            Detection Engine
                    ↓
            Dashboard (localhost:8766)
```

**What This Means:**
- All API requests pass through ClawVault for inspection
- ClawVault can see request/response content including API keys
- This is intentional and necessary for threat detection
- The proxy runs locally on your machine, not on external servers

### SSL/TLS Verification

**Default Behavior:**
- ClawVault's default configuration sets `ssl_verify: false` for proxied connections
- This is required for the proxy to inspect HTTPS traffic (MITM-style interception)

**Security Implications:**
- Disabling SSL verification allows ClawVault to decrypt and inspect encrypted traffic
- This is necessary for detecting threats in API requests/responses
- Traffic between your machine and LLM providers is still encrypted
- The decryption happens locally on your machine, not in transit

**Recommendation:**
- Only use ClawVault on trusted networks
- The proxy is designed for local development/testing
- For production, consider using ClawVault's detection rules without the proxy

## Dashboard Security

### Default Configuration (Secure)

```bash
# Dashboard binds to localhost only
clawvault start
# Access: http://127.0.0.1:8766 (local machine only)
```

**This is the recommended configuration** for most users.

### Remote Access Configuration (Risky)

```bash
# Dashboard accessible from any IP
clawvault start --dashboard-host 0.0.0.0
# Access: http://<your-ip>:8766 (anyone on network can access)
```

**⚠️ Security Risks:**
- Dashboard shows sensitive detection data (API keys, PII, etc.)
- No authentication by default
- Anyone on your network can view the dashboard
- Potential data exposure if misconfigured

**When to Use Remote Access:**
- Only in trusted, isolated networks
- Behind a firewall with strict access controls
- For temporary debugging/demonstration purposes

**Production Recommendations:**
1. Keep dashboard on localhost (127.0.0.1)
2. Use SSH tunneling for remote access:
   ```bash
   ssh -L 8766:localhost:8766 user@remote-server
   ```
3. Or use a reverse proxy with authentication (nginx + basic auth)
4. Never expose dashboard to public internet without authentication

## Permissions Explained

The skill requires these permissions:

### `execute_command`
- **Purpose:** Run `pip install clawvault` and start/stop services
- **Risk:** Can execute arbitrary commands on your system
- **Mitigation:** Skill only runs documented installation commands; review clawvault_manager.py source

### `write_files`
- **Purpose:** Create configuration files in `~/.ClawVault/`
- **Risk:** Can write to your home directory
- **Mitigation:** Skill only writes to dedicated ClawVault config directory

### `read_files`
- **Purpose:** Read existing ClawVault configuration
- **Risk:** Can read files on your system
- **Mitigation:** Skill only reads from `~/.ClawVault/` directory

### `network`
- **Purpose:** Download ClawVault package, proxy API traffic, call local dashboard API
- **Risk:** Can make network requests
- **Mitigation:** Network access is essential for proxy functionality; all traffic is logged

## Data Handling

### What Data ClawVault Sees

ClawVault inspects:
- API requests to LLM providers (OpenAI, Anthropic, etc.)
- API responses from LLM providers
- API keys and authentication tokens (in request headers)
- User prompts and AI responses
- Potentially sensitive data (PII, credentials) in prompts/responses

### Where Data Is Stored

- **Audit logs:** `~/.ClawVault/audit.db` (SQLite database)
- **Detection logs:** `~/.ClawVault/logs/detection.log`
- **Configuration:** `~/.ClawVault/config.yaml`

### Data Retention

- Audit logs are stored indefinitely by default
- You can configure retention policies in `config.yaml`
- To clear logs: `rm ~/.ClawVault/audit.db`

### Data Privacy

- All data stays on your local machine
- ClawVault does not send data to external servers (except when proxying to LLM providers)
- No telemetry or analytics are collected
- You control all data through local configuration files

## Installation Security

### Package Sources

The skill installs ClawVault from:
1. **Primary:** PyPI (`pip install clawvault`)
2. **Fallback:** GitHub (`git+https://github.com/tophant-ai/ClawVault.git`)

**Security Considerations:**
- PyPI packages can be updated by maintainers
- No version pinning or checksum verification in the skill
- Installing from GitHub uses the latest main branch code

**Recommendations:**
1. Review the ClawVault package source before installing:
   - PyPI: https://pypi.org/project/clawvault/
   - GitHub: https://github.com/tophant-ai/ClawVault
2. Pin to specific version: `pip install clawvault==0.1.0`
3. Verify package integrity if concerned about supply chain attacks

### Installation Process

What happens during installation:
1. Checks Python version (requires 3.10+)
2. Runs `pip install clawvault`
3. Creates `~/.ClawVault/` directory
4. Generates default `config.yaml`
5. Optionally starts services on ports 8765, 8766

## Threat Model

### What ClawVault Protects Against

✅ **Prompt injection attacks** - Detects attempts to manipulate AI behavior
✅ **Data leakage** - Identifies PII, credentials, API keys in prompts/responses
✅ **Dangerous commands** - Flags risky shell commands in AI outputs
✅ **Jailbreak attempts** - Detects attempts to bypass AI safety measures

### What ClawVault Does NOT Protect Against

❌ **Malicious ClawVault package** - If the upstream package is compromised, the skill will install it
❌ **Local system compromise** - If your machine is compromised, ClawVault data can be accessed
❌ **Network attacks** - ClawVault does not protect against network-level attacks
❌ **Supply chain attacks** - No verification of package integrity during installation

## Best Practices

### For Development/Testing

```bash
# Safe configuration for local development
clawvault start --dashboard-host 127.0.0.1 --mode interactive

# Review detection logs regularly
tail -f ~/.ClawVault/logs/detection.log

# Test with non-sensitive data first
clawvault test --category all
```

### For Production

```bash
# Use strict mode for automated blocking
clawvault start --mode strict

# Keep dashboard local, use SSH tunnel for remote access
ssh -L 8766:localhost:8766 user@server

# Configure audit retention
# Edit ~/.ClawVault/config.yaml:
audit:
  enabled: true
  retention_days: 30
```

### For Sensitive Environments

1. **Review the source code** before installation
2. **Run in isolated environment** (VM, container)
3. **Use firewall rules** to restrict network access
4. **Rotate API keys** regularly
5. **Monitor audit logs** for suspicious activity
6. **Disable dashboard** if not needed: `--no-dashboard`

## Security Checklist

Before installing ClawVault skill:

- [ ] Reviewed ClawVault package source code
- [ ] Understand that ClawVault will see API keys and request content
- [ ] Verified dashboard will bind to localhost (not 0.0.0.0)
- [ ] Understand SSL verification implications
- [ ] Have plan for audit log retention/cleanup
- [ ] Running in appropriate environment (dev/test/prod)
- [ ] Firewall configured if using remote dashboard
- [ ] Understand what permissions the skill requires

## Reporting Security Issues

If you discover a security vulnerability in ClawVault or this skill:

**For Critical Vulnerabilities (RCE, data exfiltration, credential theft):**
1. Open a [GitHub Security Advisory](https://github.com/tophant-ai/ClawVault/security/advisories/new) (private disclosure)
2. Or email: security@tophant.com
3. Include detailed description and reproduction steps
4. We will respond within 48 hours and work on a fix

**For Non-Critical Issues (documentation errors, configuration issues, minor bugs):**
1. Open a public [GitHub Issue](https://github.com/tophant-ai/ClawVault/issues/new)
2. Tag with `security` label
3. Community can discuss and contribute fixes

We encourage responsible disclosure and will credit security researchers who report vulnerabilities.

## Additional Resources

- **ClawVault Documentation:** https://github.com/tophant-ai/ClawVault/tree/main/doc
- **OpenClaw Security:** https://docs.openclaw.ai/gateway/security
- **Threat Model:** https://github.com/tophant-ai/ClawVault/blob/main/doc/architecture.md

## License

This security documentation is part of the ClawVault project.
MIT © 2026 Tophant SPAI Lab
