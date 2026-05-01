---
type: skill
lifecycle: stable
inheritance: inheritable
name: sdl
description: Knowledge pack: SDL (Security Development Lifecycle) compliance scan. Aggregates SDL-mapped patterns from security, crypto, secrets, dependencies, observability, and code-quality knowledge skills.
tier: standard
applyTo: '**/*bug*,**/*hunter*,**/*sdl*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# SDL Compliance — Knowledge Pack

This knowledge pack aggregates all SDL-mapped detection patterns from other knowledge skills into a focused SDL compliance scan. Invoke it directly via `/bug-hunter:sdl` for a scan that only checks SDL-relevant patterns.

**Compliance framework:** Microsoft Security Development Lifecycle (SDL)
**Categories involved:** `security-vulnerabilities`, `cryptographic-weaknesses`, `secret-exposure`, `dependency-risk`, `observability`, `code-quality`

---

## SDL Requirement Coverage

When this pack is active, the agent should focus **only** on sub-patterns that have an SDL `complianceRef`. Below is the mapping of SDL requirements to category skills:

### From `security` skill:
| SDL Requirement | Sub-Pattern |
|---|---|
| Safely handle database access | SQL Injection |
| PowerShell injection | Command Injection |
| Web App Security Vulns | XSS |
| SSRF protections | SSRF |
| Safe deserializers | Unsafe Deserialization |
| XSLT scripting | XSLT Scripting |
| Least privilege | Least Privilege Violations |
| Banned APIs | Banned APIs |
| Memory Corruption | Memory Corruption |

### From `crypto` skill:
| SDL Requirement | Sub-Pattern |
|---|---|
| Approved hash functions | Banned Hash Algorithms |
| Approved block ciphers | Banned Symmetric Ciphers |
| No stream ciphers | Banned Stream Ciphers |
| Approved asymmetric algorithms | Weak Asymmetric Keys |
| Approved RNGs | Weak RNG for Security |
| Approved block cipher modes | Hardcoded/Static IVs |
| Single-purpose keys | Key Reuse |
| Self-signed certs | Self-Signed Certificates |
| Encrypt data in transit | Weak TLS |
| Integrity protection | Unauthenticated Encryption |
| JWT integrity | JWT Weaknesses |
| Approved crypto libraries | Custom Crypto |
| Encrypt at-rest | Unencrypted Sensitive Data at Rest |
| Approved KDFs | Weak KDF |

### From `secrets` skill:
| SDL Requirement | Sub-Pattern |
|---|---|
| Secrets not in code | Secrets in Source Code |
| Secrets not in URLs | Secrets in URLs |
| Secret Storage | Missing Secret Storage |
| Approved Identity SDKs | Non-Approved Identity SDKs |

### From `dependencies` skill:
| SDL Requirement | Sub-Pattern |
|---|---|
| Assess OSS components | Known Vulnerable Packages |
| Package management | Unpinned Versions |
| Approved sources | Non-Approved Sources |
| Currently supported | EOL Packages/Runtimes |
| SBOM generation | Missing SBOM Config |
| Appropriate package sources | Unofficial Feeds |

### From `observability` skill:
| SDL Requirement | Sub-Pattern |
|---|---|
| Security event auditing | Security Events Not Logged |
| No debug disclosure | Debug Interfaces in Production |

### From `code-quality` skill:
| SDL Requirement | Sub-Pattern |
|---|---|
| Secure DLL loading | Insecure DLL Loading |
| Fix compiler warnings | Compiler Warnings Ignored |

### From `auth-authz` skill:
| SDL Requirement | Sub-Pattern |
|---|---|
| Approved Identity SDKs | AuthN Inbound — Token Validity (MISE/Microsoft.Identity.Web) |
| Approved Identity SDKs | AuthN Outbound — Downstream Auth Headers (OBO/Managed Identity) |
| Least privilege | AuthZ Outbound — No Privilege Elevation |
| Secret Storage | AuthN Outbound — Downstream Auth Headers (no static API keys) |

---

## Usage

**Focused SDL scan:**
```
/bug-hunter:sdl
```

**CLI (non-interactive):**
```bash
agency copilot \
  --input ScanMode=full --input SafeMode=true \
  --agent "bug-hunter:bug-hunter" \
  -p "Run SDL compliance scan only" -s --allow-all --no-ask-user
```

When this pack is active, findings should always populate `complianceRef.sdlRequirements` with the matched SDL requirement title(s).
