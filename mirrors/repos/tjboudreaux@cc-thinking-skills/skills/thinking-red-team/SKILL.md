---
name: thinking-red-team
description: Use when reviewing code, auth, or APIs for security vulnerabilities — adopt an attacker mindset, enumerate the attack surface, report only findings with a concrete reproducible attack path.
---

# Red Team Thinking

## Overview

Red teaming is **adversarial security review**: deliberately attacking a system you control to find vulnerabilities before an attacker does. This skill is scoped to security/code vulnerability detection — it is NOT for plan stress-testing or decision challenge (use `thinking-pre-mortem` or `thinking-steel-manning` for those).

**The anti-fabrication gate is the most important rule:** every reported finding MUST include a concrete, reproducible attack path — entry point → exact steps → realized impact. If you cannot describe how the attack actually executes against *this* code/config, it is not a finding. Drop it. A short report of real, demonstrable vulnerabilities beats a long list of speculation.

**Core Principle:** Attack yourself before others do. But only report what you can actually break.

## When to Use

- Security review of code, authentication, authorization, APIs, or infrastructure you control
- Pre-launch security hardening of a system that handles auth, data, or money
- Evaluating whether a specific vulnerability class (injection, XSS, auth bypass, etc.) is present in your code

Decision flow:

```
Reviewing a system for security?
  → Can you demonstrate an attack path? → No → Don't report it
  → Is the finding reproducible against this code/config? → No → Drop it
  → Is this plan stress-testing or decision challenge? → Yes → Use thinking-pre-mortem or thinking-steel-manning
  → No → RED TEAM IT
```

## When NOT to Use

- **Speculative claims without a reproducible attack path.** This is the anti-fabrication gate. "Best practice says X" or "this could theoretically be vulnerable" is not a finding. State the entry point, exact steps, and realized impact — or drop it.
- **Plan, strategy, or decision stress-testing.** For "how could this plan fail," use `thinking-pre-mortem`. For "what's the strongest case against this decision," use `thinking-steel-manning`.
- **Architecture review without security focus.** For architecture resilience, use `thinking-systems` or `thinking-pre-mortem`.
- **Running scanners replaces thinking.** Where you can actually run a SAST tool, fuzzer, or PoC, do that. This skill structures the adversarial thinking; it doesn't replace automated verification.
- **Padding the report to look thorough.** A short list of real vulnerabilities beats a long list of theoretical ones. Resist the incentive to add "informational" or "best-practice" items.

## Procedure

### Step 1: Define the Target and Scope

```markdown
Target: [System/component under review]
Scope: [What to attack — be specific]
Out of scope: [What to skip]
Goal: [What constitutes a successful attack — e.g., unauthorized access, data exfiltration, privilege escalation]
```

### Step 2: Adopt the Adversary Mindset

Identify who would attack this system and what they want:

```markdown
Adversary profiles:
- External attacker (no access): targets public endpoints, auth bypass, injection
- Authenticated user (basic access): targets privilege escalation, IDOR, business logic
- Insider (elevated access): targets data exfiltration, audit bypass

For each profile, ask: "If I wanted to cause maximum damage with their access level, how would I?"
```

### Step 3: Enumerate the Attack Surface

Map every entry point and trust boundary:

| Surface | Exposure | Trust Boundary |
|---------|----------|----------------|
| Login form | Public internet | Anonymous → Authenticated |
| API /graphql | Public (with key) | Authenticated → Application |
| Password reset flow | Public | Anonymous → Account owner |
| Admin panel | Internal network | Authenticated → Admin |
| File upload endpoint | Authenticated | User data → Server storage |

### Step 4: Execute Attack Scenarios

For each attack surface, attempt to break the system:

```markdown
Attack: Credential stuffing against login
Steps:
1. Obtain breach database of known credentials
2. Script requests against /login with varied credentials
3. Observe rate limiting, account lockout, timing differences
Findings:
- Rate limiting: 10 req/min per IP (bypassable via distribution)
- Account lockout: none
- Timing: response time reveals valid vs invalid usernames ← VULNERABILITY
```

For each attack scenario, record: the entry point, exact steps taken, observed behavior, and whether a vulnerability was found.

### Step 5: Attempt Defense Bypass

For each defense encountered, try to bypass it:

| Defense | Bypass Attempt | Result |
|---------|---------------|--------|
| IP-based rate limiting | Distribute requests across IPs | BYPASSED |
| Input validation | Unicode normalization attacks | RESISTED |
| Session timeout | Replay expired token with modified timestamp | BYPASSED |

### Step 6: Document Findings — With the Anti-Fabrication Gate

For EVERY finding, fill out:

```markdown
Finding: [Title]
Severity: Critical / High / Medium / Low
Attack path (REQUIRED):
  Entry point: [URL, endpoint, parameter, file]
  Steps: [1. Send X, 2. Observe Y, 3. Escalate to Z]
  Realized impact: [What the attacker actually achieves — data access, privilege, DoS]
Remediation: [Concrete fix]
```

**If you cannot fill out the attack path completely, drop the finding.** Do not report "Missing HttpOnly flag" as a standalone finding without demonstrating session token theft. Do not report "No rate limiting" without demonstrating a viable brute-force attack.

## Output Contract

A completed Red Team report produces:

1. **Target and Scope** — what was reviewed and what was excluded
2. **Attack Surface Map** — entry points with exposure levels and trust boundaries
3. **Attack Scenarios Executed** — each scenario with steps, observations, and outcome
4. **Findings Report** — each with severity AND a concrete, reproducible attack path (entry point → steps → impact)
5. **Defense Bypass Results** — which defenses held and which were circumvented
6. **Remediation Recommendations** — prioritized by severity with concrete fixes

Findings without a complete attack path are excluded from the report. A report with zero findings is acceptable if no reproducible vulnerabilities were discovered.

## Anti-Patterns

| Anti-Pattern | Symptom | Correction |
|---|---|---|
| **Speculative claims** | Findings that say "could be vulnerable" or "best practice says" without a demonstrated attack path | Drop them; only report what you can actually break |
| **Padding the report** | Adding "informational" or "best-practice" items to look thorough | A short report of real vulns beats a long list of theory |
| **Non-security red-teaming** | Using this skill for plan stress-testing or decision challenge | Use `thinking-pre-mortem` (plans) or `thinking-steel-manning` (decisions) |
| **Skipping the adversary model** | Attacking without defining who the attacker is and what access they have | Define the adversary profile first; attacks make sense only in context |
| **Missing the attack path** | Reporting a vulnerability without showing how to reach it | Every finding needs: entry point → steps → impact |
| **Scanner-as-substitute** | Running a SAST tool and reporting its output without adversarial thinking | The tool finds patterns; red-teaming finds exploitable paths |
