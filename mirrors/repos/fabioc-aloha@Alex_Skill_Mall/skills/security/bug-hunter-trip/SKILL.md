---
type: skill
lifecycle: stable
inheritance: inheritable
name: trip
description: Knowledge pack: TrIP (Trust in Product) compliance scan. Aggregates TrIP-mapped patterns from security, crypto, secrets, observability, resilience, and code-quality knowledge skills.
tier: standard
applyTo: '**/*bug*,**/*hunter*,**/*trip*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# TrIP Compliance — Knowledge Pack

This knowledge pack aggregates all TrIP-mapped detection patterns from other knowledge skills into a focused TrIP compliance scan. Invoke it directly via `/bug-hunter:trip` for a scan that only checks TrIP-relevant patterns.

**Compliance framework:** Microsoft Trust in Product (TrIP)
**Categories involved:** `security-vulnerabilities`, `cryptographic-weaknesses`, `secret-exposure`, `observability`, `resilience`, `code-quality`

---

## TrIP Control Coverage

When this pack is active, the agent should focus **only** on sub-patterns that have a TrIP `complianceRef`. Below is the mapping of TrIP controls to category skills:

### From `security` skill:
| TrIP Control | Domain | Sub-Pattern |
|---|---|---|
| CM-206 | Configuration Management | SQL Injection |
| AM-006 | Access Management | Missing Auth Attributes |
| ID-053 | Identity | Missing Auth Attributes |
| CM-213 | Configuration Management | CORS Misconfiguration |
| AM-010 | Access Management | Session Timeout |
| CM-213 | Configuration Management | Insecure Cookies |

### From `crypto` skill:
| TrIP Control | Domain | Sub-Pattern |
|---|---|---|
| CK-033 | Cryptographic Key Management | Banned Hash Algorithms |
| NC-071 | Network Controls | Weak TLS |

### From `secrets` skill:
| TrIP Control | Domain | Sub-Pattern |
|---|---|---|
| CK-034 | Cryptographic Key Management | Secrets in Config |
| PR-132 | Privacy | Secrets in Telemetry/Logging |
| CP-029 | Compliance Programs | Secrets in Telemetry/Logging |
| ID-055 | Identity | Missing Secret Storage |
| DS-209 | Data Security | Cached Credentials Not Cleared |

### From `observability` skill:
| TrIP Control | Domain | Sub-Pattern |
|---|---|---|
| OS-077 | Operational Security | Missing Structured Logging |
| OS-078 | Operational Security | Missing Telemetry |
| PR-132 | Privacy | PII in Logs |
| CP-029 | Compliance Programs | PII in Logs |
| PR-134 | Privacy | Missing Audit Trail |

### From `resilience` skill:
| TrIP Control | Domain | Sub-Pattern |
|---|---|---|
| BC-017 | Business Continuity | Missing Retry Policies |
| BC-029 | Business Continuity | No Circuit Breaker |

### From `code-quality` skill:
| TrIP Control | Domain | Sub-Pattern |
|---|---|---|
| CM-108 | Configuration Management | Missing API Documentation |
| CM-205 | Configuration Management | Missing Type Annotations |

### From `dependencies` skill:
| TrIP Control | Domain | Sub-Pattern |
|---|---|---|
| OS-081 | Open Source | Known Vulnerable Packages |
| OS-082 | Open Source | Missing Central Package Management |

### From `auth-authz` skill:
| TrIP Control | Domain | Sub-Pattern |
|---|---|---|
| AM-006 | Access Management | AuthN Inbound — Token Validity (all tokens validated) |
| AM-006 | Access Management | AuthZ Inbound — Authorization Enforcement (scopes/roles checked) |
| AM-006 | Access Management | AuthZ Outbound — No Privilege Elevation |
| AM-010 | Access Management | AuthN Inbound — Monitoring (anomaly detection) |
| AM-010 | Access Management | AuthN Outbound — Monitoring (outbound auth failure detection) |
| ID-053 | Identity | User Context Inbound (oid/tenantId validated against token) |
| ID-053 | Identity | AuthN Inbound — Service Audience (correct audience in token) |
| ID-055 | Identity | AuthN Outbound — Downstream Auth Headers (OBO/Managed Identity) |

---

## TrIP Domains Covered

| Domain | Controls |
|---|---|
| Access Management (AM) | AM-006, AM-010 |
| Business Continuity (BC) | BC-017, BC-029 |
| Configuration Management (CM) | CM-108, CM-205, CM-206, CM-213 |
| Compliance Programs (CP) | CP-029 |
| Cryptographic Key Management (CK) | CK-033, CK-034 |
| Data Security (DS) | DS-209, DS-210 |
| Identity (ID) | ID-053, ID-055 |
| Network Controls (NC) | NC-071 |
| Open Source (OS) | OS-077, OS-078, OS-081, OS-082 |
| Privacy (PR) | PR-132, PR-134 |

> Note: The `auth-authz` skill significantly expands AM-006, AM-010, ID-053, and ID-055 coverage with 8 detailed assessment dimensions.

---

## Usage

**Focused TrIP scan:**
```
/bug-hunter:trip
```

**CLI (non-interactive):**
```bash
agency copilot \
  --input ScanMode=full --input SafeMode=true \
  --agent "bug-hunter:bug-hunter" \
  -p "Run TrIP compliance scan only" -s --allow-all --no-ask-user
```

When this pack is active, findings should always populate `complianceRef.tripControls` with the matched TrIP control ID(s).
