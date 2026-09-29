---
name: authenticated-surface-mapping
description: Mapping authenticated routes, role boundaries, and session behavior for authorized access-control testing
---

# Authenticated Surface Mapping

## When to Use
When the target has authentication and you have credentials (operator-supplied or discovered). If no credentials exist, mark this dimension "blocked" and continue.

## Prerequisites
- At least one valid account/session
- Do NOT brute-force credentials or create accounts on production systems without authorization

## Methodology

### Login Flow Analysis
```bash
# Capture the login request
curl -sk -X POST https://TARGET/login -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}' -D tmp/login_headers.txt

# Record: session cookie name, token format, redirect target, error messages
```

### Authenticated Route Discovery
```bash
# Compare anonymous vs authenticated surface
curl -sk https://TARGET/ -o tmp/anon.html
curl -sk https://TARGET/ -H "Cookie: SESSION=test" -o tmp/auth.html
diff tmp/anon.html tmp/auth.html | head -50
```

### Role Boundary Mapping
If multiple roles exist (admin/user/readonly):
```bash
# For each role, capture the accessible routes
curl -sk https://TARGET/admin -H "X-Auth-Token: ADMIN_TOKEN" -o tmp/admin_view.html
curl -sk https://TARGET/admin -H "X-Auth-Token: USER_TOKEN" -o tmp/user_view.html
```

### Session Token Analysis
```bash
# Record the session mechanism: cookie, JWT, Bearer token, custom header
# Record expiry, refresh, logout behavior
```

## Stopping Criteria
- Login flow understood (method, endpoint, session format)
- Authenticated-only routes identified
- Role differences mapped (if multiple roles exist)
- Session mechanism documented

## When Blocked
If no credentials exist:
- Mark the auth-surface dimension as blocked
- Document what was observed about the auth mechanism anonymously
- Continue with unauthenticated testing
