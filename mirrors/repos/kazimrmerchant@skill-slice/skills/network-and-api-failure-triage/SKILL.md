---
name: network-and-api-failure-triage
description: "Localizes a failed API or network call to DNS, TCP, TLS, HTTP, or the app from the exact status, timeout, or errno (ENOTFOUND, ECONNREFUSED, 429, 502/503). Use when curl/fetch fails, the API looks down, or errors are intermittent. Not for Spark shuffle slowness, Android jank traces, or rewriting retry/backoff before the failing layer is known."
version: 1.0.1
risk: safe
source: opus-skills-library
date_added: "2026-05-27"
domain: troubleshooting
kind: leaf
tags: [network, api, http, timeouts, dns, tls]
---

# Network & API Failure Triage

A network or API failure hides behind a status code or a timeout, and "the API is down" is rarely the whole truth. Triage localizes *which layer* failed — DNS, TCP, TLS, HTTP, or the application — and reads the exact failure, because each layer points to a completely different fix.

## When to Use

Use this skill when:

- An API call fails, times out, or returns an unexpected error status (4xx/5xx).
- You see connectivity errors: `ECONNREFUSED`, `ECONNRESET`, `ENOTFOUND`, `ETIMEDOUT`, `getaddrinfo ENOTFOUND`.
- A request works intermittently or only from certain hosts/regions.
- You need to distinguish a client bug from a server outage from a network problem.
- Someone reports "the API is down" and you need to find the actual failing layer.

This skill extends [client-server-split-debugging](../client-server-split-debugging/SKILL.md) down into the network layers beneath the HTTP boundary.

## Prerequisites

- A shell with `curl` available (Windows PowerShell, WSL, or Git Bash).
- `openssl` for TLS handshake checks (included in Git for Windows and WSL).
- `nslookup` or `Resolve-DnsName` for DNS checks (built into Windows).
- `Test-NetConnection` for TCP reachability checks (built into Windows PowerShell).
- Network egress to the target host (or awareness that a proxy/VPN is required).
- No live secrets in commands — use `YOUR_KEY` placeholders when testing authenticated endpoints.

## Procedure

### Step 1 — Capture the exact error before guessing

Before running any diagnostic, record the raw error message, status code, and timeout type. Do not paraphrase "the API is down" — get the exact string.

```powershell
# Capture the full error from your application or test call
# Example: note the exact status, headers, and body
curl -v -s -o NUL -w "HTTP %{http_code} | connect=%{time_connect}s | tls=%{time_appconnect}s | total=%{time_total}s\n" https://api.example.com/health
```

If the error is a stack trace (`ECONNREFUSED`, `ENOTFOUND`, `ETIMEDOUT`, `ECONNRESET`), note the error code — it tells you the layer immediately.

### Step 2 — Localize the failing layer (walk the stack bottom-up)

Test each layer in order. **Stop at the first layer that fails** — that is your primary suspect. Do not skip ahead.

#### Layer 1: DNS — does the name resolve?

```powershell
# Windows PowerShell
Resolve-DnsName api.example.com

# Or classic nslookup
nslookup api.example.com

# WSL / Git Bash
dig +short api.example.com
dig api.example.com ANY
```

**What to check:**
- Does it resolve at all? `ENOTFOUND` / `NXDOMAIN` = DNS failure.
- Does it resolve to the expected IP? Stale records, wrong TTL, split-horizon DNS.
- Does it resolve differently from the failing host vs your machine? Check from the actual environment.

**If DNS fails:** fix records, check `/etc/hosts` or `C:\Windows\System32\drivers\etc\hosts`, verify DNS server, check TTL for stale cache.

#### Layer 2: TCP — does the connection open?

```powershell
# Windows PowerShell
Test-NetConnection -ComputerName api.example.com -Port 443

# WSL / Git Bash
nc -zv api.example.com 443
# Or with timeout
nc -zv -w 5 api.example.com 443
```

**What to check:**
- `TcpTestSucceeded: True` — port is reachable.
- `TcpTestSucceeded: False` — firewall, wrong port, host down, or service not listening.
- Connection timeout (vs. refused) — firewall dropping packets vs. host rejecting.

**If TCP fails:** check firewall rules, security groups, port number, whether the service is running and listening on that port.

#### Layer 3: TLS — does the handshake succeed?

```powershell
# Works in PowerShell, WSL, and Git Bash
openssl s_client -connect api.example.com:443 -servername api.example.com < NUL

# Check cert expiry specifically
openssl s_client -connect api.example.com:443 -servername api.example.com < NUL 2>NUL | openssl x509 -noout -dates
```

**What to check:**
- `Verify return code: 0 (ok)` — handshake and cert chain valid.
- Expired cert — `notAfter` date is in the past.
- SNI mismatch — ensure `-servername` matches the expected virtual host.
- Protocol mismatch — server requires TLS 1.2+ and client offers TLS 1.0.
- Self-signed or untrusted CA — cert chain incomplete or private CA not trusted.

**If TLS fails:** check cert expiry, CA bundle, SNI configuration, TLS version compatibility.

#### Layer 4: HTTP — what status and body?

```powershell
# Verbose request with timing breakdown
curl -v -s -w "\nHTTP %{http_code} | connect=%{time_connect}s | tls=%{time_appconnect}s | starttransfer=%{time_starttransfer}s | total=%{time_total}s\n" https://api.example.com/health

# With auth header (use placeholder, never real key)
curl -v -H "Authorization: Bearer YOUR_KEY" https://api.example.com/v1/resource

# Follow redirects explicitly
curl -v -L -w "\nHTTP %{http_code}\n" https://api.example.com/old-path
```

**What to check:**
- Status code (see Step 3 below).
- Response headers — `Retry-After` on 429/503, `Server` header, `CF-Ray` / `X-Request-Id` for tracing.
- Response body — server error message, validation details.
- Timing — `time_connect` vs `time_appconnect` vs `time_starttransfer` reveals where latency sits.

#### Layer 5: App — logic/validation/auth errors behind a 4xx/5xx

Once you have a valid HTTP response, the failure is in the application contract or server logic. Move to:
- Server logs and traces for 5xx errors.
- Request payload, headers, and auth for 4xx errors.
- API documentation / OpenAPI spec for contract mismatches.

> **Load `resources/network-layer-triage.md`** for a per-layer command checklist and a status/timeout decision map when you need the full reference table.

### Step 3 — Read the failure precisely

Interpret the status code or timeout type exactly — each points to a different fix:

| Status / Error | Meaning | Action |
|---|---|---|
| **400 / 422** | Client validation error | Fix the request payload or contract |
| **401** | Not authenticated | Check auth token, expiry, header format |
| **403** | Authenticated but not authorized | Check scopes/permissions, not a token issue |
| **404** | Resource not found | Check URL path, API version, resource ID |
| **429** | Rate limited | Back off using `Retry-After` header; do not retry harder |
| **500** | Server error | Move to server logs/traces |
| **502 / 504** | Gateway/proxy error | Upstream is down or unreachable; check LB/proxy |
| **503** | Service unavailable | Overloaded or maintenance; back off |
| **Connection refused** | Port not listening / firewall reject | Service down or port blocked |
| **Connection timeout** | Packets dropped / firewall drop | Network path blocked or host unreachable |
| **Read timeout** | Connected but no response in time | Server slow, overloaded, or deadlocked |
| **DNS failure** | Name does not resolve | Fix DNS records, cache, or hosts file |

### Step 4 — Handle retries, rate limits, and intermittency correctly

**Distinguish timeout types:**
- **Connect timeout** — could not establish TCP connection. Network or service down.
- **Read timeout** — connection established but no response data within deadline. Server slow or overloaded.

**Retry rules (HARD — never violate):**
1. Retry **only idempotent** requests (GET, PUT, DELETE with stable IDs). Never blindly retry POST/PATCH that could create duplicate writes or charges.
2. Use **exponential backoff with jitter** — never fixed-interval retries.
3. Respect **`Retry-After`** header on 429 and 503 responses.
4. Implement a **circuit breaker** so a struggling dependency is not hammered into collapse.
5. Cap total retry attempts (typically 3–5) and total retry duration.

```powershell
# Example: retry with exponential backoff (conceptual)
# attempt 1: wait 1s + jitter
# attempt 2: wait 2s + jitter
# attempt 3: wait 4s + jitter
# attempt 4: wait 8s + jitter
# then fail / circuit break
```

**Intermittent faults:**
- Correlate failures to a specific instance, region, or pod — partial outages masquerade as flakiness.
- Check for recent DNS/LB changes, deployments, or cert rotations that coincide with the start of failures.
- Compare success rate across instances/regions to isolate the failing subset.

### Step 5 — Correlate across services

For multi-service failures, use [log-correlation-across-services](../log-correlation-across-services/SKILL.md) to trace a request ID across service boundaries and pinpoint where the chain breaks.

## Pitfalls

- **"The API is down" with no layer localization** — the fault is often DNS, TLS, or one bad instance behind a load balancer. Always walk the stack before concluding the server is down.
- **Retry storms** — aggressive retries on a struggling dependency amplify the outage. A 5-second blip becomes a 5-minute collapse when every client retries at once.
- **Retrying non-idempotent calls** — blind retries on POST/PATCH create duplicate writes, duplicate charges, duplicate emails. Check idempotency before retrying.
- **Ignoring 429** — hammering through a rate limit instead of backing off makes the rate limit worse, not better.
- **Cert blindness** — an expired TLS certificate is a common root cause that is invisible if you skip the TLS layer check. Always run `openssl s_client` when handshakes fail.
- **Confusing connect timeout with read timeout** — they have completely different causes and fixes. Connect timeout = network/service down. Read timeout = server slow/overloaded.
- **Testing from your machine, not the failing environment** — DNS split-horizon, firewall rules, and proxy configs differ by environment. Reproduce from the actual failing host.
- **Assuming 502/504 means the origin is down** — it means the *gateway* could not reach the origin. The origin might be up but slow, or the gateway config might be wrong.
- **Stale DNS cache** — Windows DNS cache (`ipconfig /displaydns`) can serve old records past TTL. Flush with `ipconfig /flushdns` when DNS changes are suspected.

## Verification

Confirm the triage is complete by checking every item:

```powershell
# 1. Verify DNS resolves to expected IP
Resolve-DnsName api.example.com

# 2. Verify TCP port is reachable
Test-NetConnection -ComputerName api.example.com -Port 443

# 3. Verify TLS handshake and cert validity
openssl s_client -connect api.example.com:443 -servername api.example.com < NUL 2>NUL | openssl x509 -noout -dates

# 4. Verify HTTP returns expected status
curl -v -s -o NUL -w "HTTP %{http_code}\n" https://api.example.com/health

# 5. Flush DNS cache if DNS changes were made
ipconfig /flushdns
```

**Checklist — all must be true:**

- [ ] Failing layer localized (DNS / TCP / TLS / HTTP / app) — not assumed.
- [ ] Exact status code or timeout type read and interpreted (not paraphrased).
- [ ] Retries limited to idempotent calls with exponential backoff + jitter (no retry storms).
- [ ] Rate limiting (429) handled by backing off per `Retry-After`, not retrying harder.
- [ ] TLS/cert validity and expiry checked when handshakes fail.
- [ ] Intermittent faults correlated to an instance, region, or recent change.
- [ ] Diagnostics run from the failing environment, not just your local machine.

## Related Skills

- [client-server-split-debugging](../client-server-split-debugging/SKILL.md) — split client vs server vs contract before diving into network layers.
- [contract-and-api-verification](../../verification/contract-and-api-verification/SKILL.md) — verify the API contract matches the implementation.
- [log-correlation-across-services](../log-correlation-across-services/SKILL.md) — trace a request ID across service boundaries.
- [modern-app-building/apis](../../modern-app-building/apis/SKILL.md) — API design patterns for robust, retry-safe interfaces.
