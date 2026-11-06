---
name: cookie-session-audit
description: Use when user says cookie check, session verify, cookies txt/zip/json, or bulk cookie validation. Safely validates cookie health, expiry, security flags, and session usability.
---

# Cookie Session Audit (TXT/JSON/ZIP)

Use this skill to audit cookies quickly and safely.

Goal: detect which cookies are usable, expired, risky, or blocked by security controls.

## Trigger Rules

Activate when user asks to:
- check cookies
- validate session cookies from txt/json/zip
- bulk cookie audit
- verify live/dead session status

## Scope & Safety

- Only test cookies the user owns or is authorized to test.
- No bypass instructions for login, MFA, CAPTCHA, or anti-bot.
- Never print full cookie values in output.
- Mask values as `prefix...suffix`.
- Never commit raw cookies to git.

## Input Rules

Accepted inputs:
- `.txt`
- `.json` / `.jsonl`
- Netscape cookie format
- browser export format
- `.zip` containing any of the above

If `.zip` is provided:
1. extract to temp folder
2. parse supported files recursively
3. deduplicate cookie records

## Fast Audit Pipeline

### Phase 1 - Parse & Normalize (offline)

1. parse cookies into normalized fields:
   - `name`, `value`, `domain`, `path`, `expires`, `secure`, `httpOnly`, `sameSite`
2. ignore invalid lines/records
3. deduplicate by `domain + path + name + value`
4. classify `session` vs `persistent`

### Phase 2 - Static Security Audit (offline)

For each cookie, detect:
- missing `Secure`
- missing `HttpOnly`
- weak `SameSite` (`None` without `Secure`, or missing)
- overly broad domain/path scope
- expired timestamps

Static result labels:
- `EXPIRED`
- `WEAK_FLAGS`
- `SCOPE_TOO_BROAD`
- `FORMAT_INVALID`
- `STATIC_OK`

### Phase 3 - Live Session Check (online, optional)

Run only when target base URL is provided by user.

1. build cookie jar per domain
2. send lightweight authenticated probe to low-impact endpoint:
   - preferred: `/api/me`, `/me`, `/account`, `/profile`
3. follow minimal redirects
4. classify by HTTP status + response signal

Live status labels:
- `SESSION_ACTIVE`
- `SESSION_EXPIRED`
- `UNAUTHORIZED`
- `MFA_REQUIRED`
- `CAPTCHA_REQUIRED`
- `IP_BINDING_MISMATCH`
- `CSRF_BLOCKED`
- `RATE_LIMITED`
- `TEMP_ERROR`

### Phase 4 - Stability Probe (optional)

For active sessions only:
- send 2 low-cost checks
- compare consistency of status

Stability labels:
- `STABLE`
- `UNSTABLE`

## Error Classification Standard

Use exact categories:
- `COOKIE_EXPIRED`
- `COOKIE_REVOKED`
- `INVALID_FORMAT`
- `MISSING_SECURE`
- `MISSING_HTTPONLY`
- `SAMESITE_WEAK`
- `DOMAIN_SCOPE_RISK`
- `PATH_SCOPE_RISK`
- `SESSION_ACTIVE`
- `SESSION_INVALID`
- `MFA_REQUIRED`
- `CAPTCHA_REQUIRED`
- `RATE_LIMITED`
- `NETWORK_ERROR`
- `PROVIDER_DOWN`

## Performance Rules

- Parse and static-check first.
- Live check only for non-expired candidates.
- Use controlled concurrency.
- Stop early on definitive expired/invalid records.

Default limits:
- concurrency: 8
- timeout: 10s
- retries: 1 (only on network/5xx)

## Output Format (Required)

Always produce:

1. `cookie_summary.txt`
- total parsed
- valid format count
- expired count
- active session count
- weak flag count

2. `cookie_results.json`
Per record include:
- `masked_cookie`
- `domain`
- `name`
- `expires_at`
- `static_status`
- `live_status`
- `stability`
- `http_code`
- `risk_flags`
- `error_hint`

3. `active_cookies.txt`
- only `SESSION_ACTIVE`
- masked by default
- full value only if user explicitly requests and secure context is confirmed

## Final Response Style

When reporting to user:
- show totals first
- show active vs expired vs blocked
- show top security issues (missing Secure/HttpOnly/SameSite)
- give next actions:
  - rotate sensitive cookies
  - tighten flags
  - reduce domain/path scope
  - shorten TTL for high-risk sessions
