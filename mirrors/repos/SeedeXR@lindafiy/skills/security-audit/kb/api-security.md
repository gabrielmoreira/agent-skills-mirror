# API Security — Techniques Knowledge Base

A distilled reference of API penetration-testing and security-audit techniques, organized around the OWASP API Security Top 10 (2023). Each entry states the vulnerability class, where it lives, how to detect and test it, remediation, and tooling.

## OWASP API Security Top 10 (2023)

```
API1:2023  Broken Object Level Authorization (BOLA)
API2:2023  Broken Authentication
API3:2023  Broken Object Property Level Authorization (BOPLA)  -- merges Excessive Data Exposure + Mass Assignment
API4:2023  Unrestricted Resource Consumption
API5:2023  Broken Function Level Authorization (BFLA)
API6:2023  Unrestricted Access to Sensitive Business Flows
API7:2023  Server-Side Request Forgery (SSRF)                  -- new in 2023
API8:2023  Security Misconfiguration
API9:2023  Improper Inventory Management
API10:2023 Unsafe Consumption of APIs                          -- new in 2023
```

---

## END-TO-END METHODOLOGY (ordered phases)

0. **Scope the test** — decide black box / gray box / white box. In gray/white box request direct API access + accounts per role so you test the API, not the WAF.
1. **Passive recon** — OSINT only, no target interaction. Cast a wide net (search engines, Shodan, ProgrammableWeb, DNS Dumpster, Amass passive), adapt & focus (GitHub, Pastehunter), document attack surface. Hunt for endpoints, versions, docs, business purpose, and leaked keys/tokens/PII (instant wins).
2. **Active recon** — Phase 0 opportunistic exploit anytime; Phase 1 detection scan (Nmap general + all-port); Phase 2 hands-on analysis as guest/user/admin (browser + DevTools + Burp); Phase 3 targeted scans (Gobuster/Kiterunner/ZAP tuned to findings). Non-linear: loop scan→analyze→scan.
3. **Endpoint analysis** — find request info via documentation, specification import (OpenAPI/Swagger/RAML/Postman collection), or reverse engineering (manual Postman build, or proxy browser→Postman). Add auth (token/key/OAuth) to Postman AND to Kiterunner. Use the API as intended; analyze responses for info disclosure, excessive data exposure, security misconfig, business logic flaws. Test privileged actions as unauth → low-priv → admin. **Distrust the docs; always test undocumented methods/endpoints/params.**
4. **Authentication testing** — brute force, password spray, reset/MFA/OTP brute force, base64 auth, token forgery/analysis, JWT attacks.
5. **Fuzzing** — fuzz wide (one payload across all requests, Postman Collection Runner) then fuzz deep (many payloads into one request, Burp Intruder / Wfuzz). Establish a baseline of normal responses first; detect anomalies by status code, response length, content, timing.
6. **Authorization testing** — locate resource IDs; A-B test for BOLA; A-B-A test for BFLA; side-channel BOLA; test all methods & all privilege levels.
7. **Mass assignment testing** — find targets (registration, profile/user/client mgmt); find variables (docs, fuzzing, blind); combine with BFLA.
8. **Injection testing** — discover input points, then XSS/XAS, SQLi, NoSQLi, OS command injection.
9. **Rate-limit & evasion testing** — detect controls/WAF, use burner accounts, apply evasion (string terminators, case switching, encoding), test/bypass rate limits (path bypass, origin spoofing, IP rotation).
10. **Combine findings & report** — chain low-severity issues (e.g. excessive data exposure → BOLA → tracking). Report with PoC and business impact.

**Golden rules:** Always develop a response baseline before fuzzing. Adopt the adversarial mindset — do the opposite of what docs tell you. Chain vulnerabilities. Avoid destructive tests (DELETE, bulk writes) outside test environments or without written authorization.

---

## RECONNAISSANCE & DISCOVERY

### id: RECON-01 — Passive OSINT / attack-surface mapping
- **what:** Find endpoints, versions, docs, business purpose, and leaked secrets without touching the target.
- **where-it-lives:** search engines, Shodan, ProgrammableWeb (23k+ API directory), GitHub repos, DNS records, SSL certs, Wayback Machine, paste sites.
- **how-to-detect:** Google dorks (`inurl:`, `intitle:`, `filetype:`, `site:`) e.g. `intitle:"index of" api_key OR "api key"`, `inurl:"/wp-json/wp/v2/users"`; use GHDB. Amass `enum -passive -d target | grep api`, `intel -whois`. Shodan `hostname:"target" "content-type: application/json"`, `"wp-json"`. DNS Dumpster for host graph.
- **how-to-test:** Search GitHub Code/Issues/Pull-requests tabs for `api`, `key`, `secret`, `token`, `password`; inspect commit history/Split diffs for keys removed-but-still-in-history. Validate found endpoints later in active recon.
- **remediation:** Rotate leaked keys immediately; scan repos with secret scanners pre-commit; don't publish internal API docs; use short-lived keys with expiry.
- **tools:** Google/GHDB, Shodan (+browser ext), ProgrammableWeb, OWASP Amass, DNS Dumpster, Pastehunter, Wayback Machine, GitHub search.

### id: RECON-02 — Active detection & endpoint discovery
- **what:** Directly probe the target to find live APIs, ports, versions, hidden paths.
- **where-it-lives:** ports 80/443 and non-standard (8000/8080/8087/8888/5000…); `/robots.txt` Disallow entries; JS source files; `/api`, `/wp-json/wp/v2`, `/docs`, `/swagger`.
- **how-to-detect:** Nmap `-sC -sV target -oA out` then `-p- target`. Look for `Content-Type: application/json`, JSON/XML bodies, `X-Powered-By`. Chrome DevTools: Network tab (XHR), open JS in Sources, search `api/APIkey/secret/password`; Memory heap snapshot search `api,v1,v2,swagger,rest,dev`; Performance tab to catch background API calls on click.
- **how-to-test:** Burp Repeater: send request → 401/verbose `WWW-Authenticate` validates API; compare vs gibberish path (404) to learn the target's not-found behavior. Crawl with ZAP; brute-force URIs with Gobuster (`dir -u URL -w common_apis_160 -x 200,202,301 -b 302`); discover endpoints/methods with Kiterunner (`kr scan URL -w routes-large.kite`, replays realistic GET/POST/PUT/DELETE + API path shapes). Add auth header to Kiterunner (`-H 'x-access-token: ...'`) for far better results.
- **remediation:** Disable debug pages; strip version-leaking headers; restrict robots.txt exposure of sensitive paths; retire dev/test endpoints.
- **tools:** Nmap, Chrome DevTools, Burp Suite, OWASP ZAP, Gobuster/Dirbuster, Kiterunner, Assetnote wordlists.

---

## API1:2023 — BROKEN OBJECT LEVEL AUTHORIZATION (BOLA / IDOR)

### id: BOLA-01 — Object-level authorization bypass
- **what:** API returns another user's resources because it authenticates but fails to verify the requester owns/may access the object.
- **where-it-lives:** resource IDs anywhere — URL path (`/api/v1/user/account/1111`), query (`?user_id=15`), request body (`{"Account":2222}`), headers, nested JSON objects, encoded/predictable tokens, emails/phones/org IDs as identifiers.
- **how-to-detect:** Map how objects are identified. Look for predictable/sequential IDs, ID-combo requests (`/UserA/data/2222`), group IDs, GUIDs. Predictable IDs alone ≠ BOLA — must confirm unauthorized access.
- **how-to-test:** **A-B testing:** create resource as UserA, note ID + request shape; swap to UserB's token; request UserA's resource. Try all methods (not just GET) and all ID locations. Variants (all with UserA's token): sequential ID swap, integer-as-ID, email-as-ID, nested object `{"Account":{"Account":3333}}`, multiple objects `{"Account":2222,"Account":3333}`, group ID swap. **Side-channel BOLA:** if 404 = nonexistent but 405/other = existing-but-unauthorized, enumerate usernames/IDs/phones via status code, response length, or timing (X-Response-Time). Automate across a collection with Postman collection variables (swap token) or Burp Match & Replace on the auth header. Chain with excessive-data-exposure leaks to harvest valid IDs/GUIDs. **Non-destructive for GET/read; brute-forcing wide is loud — throttle.**
- **remediation:** Enforce object ownership checks server-side on every request; use random unguessable IDs (defense-in-depth, not a fix); deny-by-default; test authz per object per method.
- **tools:** Burp Repeater/Intruder + Match&Replace, Postman Collection Runner, Wfuzz.
- **real-world:** T-Mobile `msisdn` BOLA; Instagram GraphQL media_id BOLA; crAPI vehicle-location GUID BOLA.

---

## API2:2023 — BROKEN AUTHENTICATION

### id: AUTH-01 — Password brute force / spraying / reset & MFA/OTP brute force
- **what:** Weak or missing anti-automation on auth, reset, and MFA lets you guess credentials or codes.
- **where-it-lives:** login/registration endpoints (JSON body, sometimes base64), password-reset endpoints accepting OTP/SMS codes, MFA verification.
- **how-to-detect:** Check for rate limiting on auth; verbose errors that distinguish "user does not exist" vs "invalid password" (username enumeration). Inspect reset flow for 4–6 digit OTP with no attempt cap.
- **how-to-test:** Wfuzz: `wfuzz -d '{"email":"a@x.com","password":"FUZZ"}' --hc 405 -H 'Content-Type: application/json' -z file,rockyou.txt URL`. **Spraying:** cluster-bomb users × short list of policy-valid passwords (`Season+Year+Symbol`, `Password1!`) staying under lockout. **OTP brute force:** Burp Intruder brute-forcer payload, charset+length matching the code (e.g. digits, len 4 → 10,000 tries). **base64 auth:** add Base64-encode payload-processing rule in Intruder. Filter with `--hc`/status/length; successes usually 200/300.
- **remediation:** Rate limit + lockout on all auth/reset/MFA endpoints; generic error messages; cap OTP attempts and expire codes; strong password policy.
- **tools:** Wfuzz, Burp Intruder, Mentalist / CUPP (targeted lists).

### id: AUTH-02 — Token forgery / weak token entropy
- **what:** Predictable or low-entropy tokens can be forged or hijacked.
- **where-it-lives:** custom auth tokens in headers/cookies; token generation endpoints.
- **how-to-detect:** Collect 100+ tokens; Burp Sequencer manual-load or live-capture (up to 20k) → entropy + character-position analysis. Find static vs variable positions.
- **how-to-test:** Brute-force only the variable positions (Intruder cluster bomb or Wfuzz `-z list`/`-z range`) against a token-required endpoint; replay valid tokens in Postman collection to map privileges.
- **remediation:** Use cryptographically random, high-entropy tokens; invalidate old tokens; short expiry.
- **tools:** Burp Sequencer/Intruder, Wfuzz.

### id: AUTH-03 — Exposed / leaked credentials & keys
- **what:** Hardcoded/exposed API keys, tokens, Bearer tokens grant instant access (stateless APIs → key = username+password).
- **where-it-lives:** JS source, GitHub commits/issues/PRs, code comments, URLs, HTTP (cleartext) traffic.
- **how-to-detect:** grep JS for `api/key/secret/token`; decode base64 `Basic` headers; capture cleartext tokens with Wireshark on HTTP.
- **how-to-test:** Use the discovered key/token in a request; base64-decode `Basic` creds; prove access with a benign authenticated request.
- **remediation:** Never ship secrets client-side; rotate on exposure; enforce HTTPS; secret scanning in CI.
- **tools:** DevTools, Wireshark, Burp Decoder.
- **real-world:** BambooHR base64 `Basic` key; exposed Bearer token → BFLA.

### id: JWT-01 — JWT "none" algorithm attack
- **what:** `"alg":"none"` (unsigned) JWT lets you rewrite the payload freely.
- **where-it-lives:** `Authorization: Bearer` JWTs (3 base64 parts, header/payload start with `ey`).
- **how-to-detect:** Decode header (Burp Decoder / jwt.io / `jwt_tool`); check `alg`.
- **how-to-test:** Edit payload (e.g. `"username":"admin"`), base64-encode, set `alg:none`, drop the signature (keep trailing `.`), send. `jwt_tool <JWT> -X a` generates none-variants.
- **remediation:** Reject `none`; pin allowed algorithms server-side.
- **tools:** jwt_tool, jwt.io, Burp Decoder.

### id: JWT-02 — Algorithm switch / key confusion (RS256→HS256)
- **what:** If the provider accepts multiple algs, sign with the public RSA key as an HMAC secret.
- **where-it-lives:** JWTs using RS256 where the public key is obtainable.
- **how-to-test:** First try stripping the signature (keep trailing `.`); then flip `alg` to `none`; then key-confusion: `jwt_tool <JWT> -X k -pk public-key.pem` (public key saved locally). Forge admin/other-user tokens if accepted.
- **remediation:** Enforce a single expected algorithm; separate verification keys per alg; validate `alg` against an allowlist.
- **tools:** jwt_tool.

### id: JWT-03 — JWT secret crack (HS256/512)
- **what:** Weak HMAC secret can be cracked offline → forge arbitrary valid tokens.
- **where-it-lives:** HS256/HS384/HS512 JWTs.
- **how-to-test:** `jwt_tool <JWT> -C -d wordlist.txt` or Hashcat (GPU). Offline — no requests to target. On success, forge tokens for other/admin users (`jwt_tool ... -S HS512 -p "<secret>"`), inject via Repeater/Postman.
- **remediation:** Long random secret (256-bit+); rotate; prefer asymmetric signing with protected keys.
- **tools:** jwt_tool, Hashcat.
- **real-world:** crAPI lab — cracked secret `crapi` → forged robot user token.

### id: OAUTH-01 — OAuth 2.0 implementation flaws
- **what:** OAuth adds attack surface; flaws are usually in the provider's implementation.
- **where-it-lives:** authorization-request/redirect flows, token exchange between services.
- **how-to-detect / test:** Look for token injection, authorization-code reuse, CSRF on the grant, open/invalid redirect URIs, phishing via the consent flow. Test per flaw class with intercepted flows.
- **remediation:** Validate redirect URIs strictly; one-time codes; state parameter/PKCE; short-lived scoped tokens.
- **tools:** Burp Suite.

---

## API3:2023 — BROKEN OBJECT PROPERTY LEVEL AUTHZ (Excessive Data Exposure + Mass Assignment)

### id: EDE-01 — Excessive data exposure
- **what:** Endpoint returns more data than needed, relying on the client to filter.
- **where-it-lives:** any GET/list/search response; forum/post feeds; user/account lookups.
- **how-to-detect:** Use the API as intended and read every field. Watch for other users' PII, admin flags, MFA status, emails, IDs, GUIDs, tokens in responses to a single-object request. Run wide with Postman Collection Runner to review many responses fast.
- **how-to-test:** Request your own object; inspect for foreign/privileged data. Judge usefulness (full name+email+DOB = finding; last-login timestamp = noise). If one endpoint over-exposes, test siblings.
- **remediation:** Return only fields the caller needs; filter server-side; never rely on client filtering; define response schemas per role.
- **tools:** Postman Collection Runner, Burp.
- **real-world:** crAPI `/community/api/v2/community/posts/recent` exposed emails + vehicleid (chained into BOLA); Peloton, USPS breaches.

### id: MASS-01 — Mass assignment
- **what:** API binds client-supplied params to server objects without an allowlist → privilege escalation or field tampering.
- **where-it-lives:** account registration, profile/user/client/company update, password reset — any request accepting client input.
- **how-to-detect:** Read docs for sensitive params (esp. admin sections); compare low-priv vs admin create requests; intercept requests for bonus params (`uam`, `mfa`, `account`, `credit`, `org`, `isAdmin`).
- **how-to-test:** Add likely privileged keys to a request: `{"admin":true}`, `"role":"admin"`, `"org":"CompanyB"`. **Blind mass assignment:** send many candidate keys in one request; vulnerable API ignores junk and honors the matching one. Automate with Arjun (`arjun --headers "Content-Type: application/json" -u URL -m JSON --include='{$arjun$}'`) or Burp Intruder over a param wordlist. If APIs reject too-many-params (400/413), cycle candidates one per request. **Combine with BFLA:** update another user's email+`mfa:false`, then reset their password.
- **remediation:** Allowlist bindable properties; separate DTOs for input vs model; ignore/deny unknown fields; server-side authorization on each writable property.
- **tools:** Arjun, Burp Intruder, Postman.
- **real-world:** crAPI — POST to `/workshop/api/shop/products` (undocumented method + no admin check) set negative `price` → +$5000 balance (mass assignment + BFLA).

---

## API4:2023 — UNRESTRICTED RESOURCE CONSUMPTION (Rate Limiting)

### id: RATE-01 — Rate-limit existence & bypass testing
- **what:** Missing/weak/ bypassable rate limiting enables DoS, cost inflation, and unlimited brute force.
- **where-it-lives:** all endpoints; auth/reset especially; headers `x-rate-limit`, `x-rate-limit-remaining`, `Retry-After`, `429`.
- **how-to-detect:** Read docs/marketing/headers for limits. Send a burst; look for `429 Too Many Requests`. Check whether exceeding the limit has any consequence at all (misconfig if none).
- **how-to-test (bypass):** **Path bypass** — alter path with string terminators/case/meaningless params: `/api/myprofile%00`, `/api/MyProfile`, `/api/myprofile?test=1` (rotate the junk value per request; Burp pitchfork). **Origin header spoofing** — add `X-Forwarded-For`, `X-Forwarded-Host`, `X-Host`, `X-Originating-IP`, `X-Remote-IP`, `X-Client-IP`, `X-Remote-Addr` (try 127.0.0.1, private IPs); rotate `User-Agent` from SecLists. **IP rotation** — Burp `IP Rotate` extension via AWS API Gateway (real distinct source IPs). **Stay-under** — throttle Wfuzz (`-t` conns, `-s` delay) or Burp Intruder Resource Pool (ms delay) to fit a lax limit. Success = `x-rate-limit` resets or requests succeed after a block.
- **remediation:** Rate limit by token AND IP AND normalized path; ignore client-controlled origin headers for limiting; enforce consistently across path variants; add spend caps/quotas.
- **tools:** Wfuzz, Burp Intruder + Resource Pool + IP Rotate (Boto3/Jython/AWS IAM), SecLists User-Agents.

---

## API5:2023 — BROKEN FUNCTION LEVEL AUTHORIZATION (BFLA)

### id: BFLA-01 — Function/privilege-level authorization bypass
- **what:** A user performs actions of another role/group (lateral or privilege escalation) — unauthorized *actions* (vs BOLA's unauthorized *access*).
- **where-it-lives:** admin endpoints (`/admin/...`), role-gated functions, and method-gated functions (unrestricted GET/POST/PUT/DELETE); user-management, group-add, account-edit.
- **how-to-detect:** Find admin functionality in docs (often public), collections, or by reverse engineering. Note different endpoints per privilege level.
- **how-to-test:** **A-B-A testing:** CRUD a resource as UserA; swap to UserB's token; send GET/PUT/POST/DELETE for UserA's resource; validate the change back as UserA. Make admin requests as a low-priv/unauth user (`POST /api/admin/find/user` with low-priv token). If blocked, switch the HTTP method (POST↔PUT — often only one is protected). Escalate: make UserA admin, UserB basic, retry. **DELETE is destructive — never fuzz DELETE outside a test env; test on a small scale.** Automate token-swap across a collection (Postman vars / Burp Match & Replace).
- **remediation:** Deny-by-default per function; centralized role checks; protect all methods equally; don't expose admin docs publicly.
- **tools:** Postman, Burp Repeater/Intruder + Match&Replace.
- **real-world:** Starbucks & academy.target.com BFLA via exposed Bearer token.

---

## API6:2023 — UNRESTRICTED ACCESS TO SENSITIVE BUSINESS FLOWS (Business Logic)

### id: BIZ-01 — Business logic flaw abuse
- **what:** Intended features abused maliciously; trust used as a "control." Automated scanners miss these.
- **where-it-lives:** upload features, MFA toggles (`MFA=true`), partner/proxy integrations, coupon/discount flows, anything the docs say "only do X" / "do not do Y" / "admins only."
- **how-to-detect:** Read docs for trust assumptions and "don't do this" statements — then do exactly that. Assume browser-only usage is not enforced.
- **how-to-test:** Intercept and flip logic params (`MFA:true`→`false`). Upload disallowed/oversized/encoded files if docs say formats "aren't validated" (→ RCE/DoS). Manipulate partner/proxy requests exposed to the client (Experian partner leak pattern). Wildcard/enumeration abuse of search (USPS `email=*@gmail.com`). Chain with mass assignment (crAPI negative-price coupon/product).
- **remediation:** Enforce every rule server-side; validate uploads (type/size/content); don't trust partners/clients; add anti-automation on sensitive flows.
- **tools:** Burp Proxy/Repeater, Postman.
- **real-world:** Experian, USPS, Peloton user-search.

---

## API7:2023 — SERVER-SIDE REQUEST FORGERY (SSRF)

### id: SSRF-01 — Server-side request forgery
- **what:** API fetches a client-supplied URL/host server-side; attacker points it at internal services or cloud metadata.
- **where-it-lives:** import-from-URL, webhook, image-fetch, PDF/preview, and any request taking a `host`/`url`/`path`/`scheme` parameter. A GraphQL `importPaste(host,port,path,scheme)` mutation is exactly this server-side-fetch shape — the same input that enables OS command injection is also an SSRF vector.
- **how-to-detect:** Identify params that cause the server to make outbound requests; observe SSRF via out-of-band callbacks or differential responses/timing.
- **how-to-test:** Point the fetch at `http://127.0.0.1`, internal hostnames, and cloud metadata endpoints; use a collaborator/OOB listener to confirm. **Authorized targets only.**
- **remediation:** Allowlist outbound hosts/schemes; block private/link-local ranges and metadata IPs; disable redirects; no raw response reflection.
- **tools:** Burp Collaborator/Repeater, Wfuzz.

---

## API8:2023 — SECURITY MISCONFIGURATION & INJECTION

### id: MISCONF-01 — Security misconfiguration
- **what:** Header/TLS/default-account/method/error misconfigs that leak info or enable attacks.
- **where-it-lives:** response headers (`X-Powered-By`, `X-XSS-Protection:0`, `X-Response-Time`, missing `X-Frame-Options`/`X-Content-Type-Options`), TLS config, debug pages, default creds, allowed HTTP methods.
- **how-to-detect:** Inspect headers/cookies/SSL/params manually or with scanners. `X-Powered-By` → version → known exploits. `X-Response-Time` side channel: consistent baseline vs elevated time reveals existing records (brute-force ranges, compare timing). Debug pages (e.g. Django) leak endpoints/stack.
- **how-to-test:** Enumerate accepted methods via Wfuzz `-X FUZZ` (`-z list,GET-POST-PUT-PATCH-TRACE-OPTIONS-CONNECT`), find undocumented allowed methods (200/anomalous). MITM cleartext with Wireshark; check downgrade to HTTP. Try default accounts.
- **remediation:** Strip version headers; enforce TLS; disable debug in prod; restrict methods; remove default creds; consistent error handling.
- **tools:** Nessus, Qualys, OWASP ZAP, Nikto, Wireshark, Wfuzz.

### id: INFO-01 — Information disclosure
- **what:** Any response detail (verbose errors, unique status codes, headers, user data) that fuels further attacks.
- **where-it-lives:** verbose errors, differential status codes (`404` vs `401`/`405`), headers, docs.
- **how-to-detect/test:** Compare responses for existent vs nonexistent users/resources → username/record enumeration; brute-force query params treating 404=absent, 401/405=present. Verbose SQL/OS errors reveal backend. Track every disclosure the provider hands you.
- **remediation:** Generic errors; uniform status codes; suppress stack traces.
- **tools:** Burp Comparer, Wfuzz.

### id: INJ-01 — SQL injection
- **what:** Unsanitized input reaches a SQL DB and executes.
- **where-it-lives:** API keys, tokens, headers, URL query strings, POST/PUT body params — anything reaching a DB.
- **how-to-detect:** "Request the unexpected" (string where number expected, huge numbers, wrong types) → verbose SQL error. Fuzz all inputs; watch for DB errors/anomalies.
- **how-to-test:** Metacharacters: `'`, `''`, `;%00`, `-- -`, `' OR 1=1-- -`, `" OR 1=1 -- -`, `OR 1=1`. Auth bypass via `' OR 1=1-- -` in user/pass. Automate with SQLmap on a saved Burp request: `sqlmap -r req -p param`; `--dump`/`--dump-all`/`-T -C -D`; `--os-shell`/`--os-pwn` for RCE. **`--os-shell`/`--os-pwn` and `--dump-all` are intrusive — authorization required.**
- **remediation:** Parameterized queries/prepared statements; input validation; least-privilege DB user; WAF as defense-in-depth.
- **tools:** Burp, Wfuzz, SQLmap.

### id: INJ-02 — NoSQL injection
- **what:** Operator/metacharacter injection into NoSQL (e.g. MongoDB) queries → auth bypass, data leak.
- **where-it-lives:** JSON body params; login; coupon/validation; anything hitting a NoSQL store (common in APIs).
- **how-to-detect:** Fuzz with NoSQL payloads; watch for verbose JSON parse errors (`Unexpected token`), 422, or behavioral change.
- **how-to-test:** Payloads: `$gt`, `{"$gt":""}`, `{"$ne":""}`, `{"$ne":-1}`, `{"$nin":[1]}`, `'||'1'=='1`, `{"$where":"sleep(1000)"}`. **Placement matters** — include or exclude the surrounding quotes to form valid nested objects (the injection point is the `coupon_code` value in `{"coupon_code":"TEST!"}`, tested with and without its quotes); disable Burp URL-encoding so `$`/`{}` reach the app. Nested operators bypass outer-value validation.
- **remediation:** Validate/cast types; reject query operators in user input; use parameterized NoSQL drivers.
- **tools:** Burp Intruder (URL-encode off), Postman, Wfuzz.
- **real-world:** crAPI coupon `{"$gt":""}`/`{"$nin":[1]}` → valid coupon; Pixi login bypass.

### id: INJ-03 — OS command injection
- **what:** Input reaches the shell → arbitrary command execution.
- **where-it-lives:** query strings, params, headers, and any request that threw OS-info/verbose errors; URL/host/path params in fetch features.
- **how-to-detect:** Know the OS (from Nmap). Fuzz with separator+command pairs.
- **how-to-test:** Command separators: `|`, `||`, `&`, `&&`, `'`, `"`, `;`, `'"`. Commands — *nix: `whoami`, `ls`, `uname -a`, `pwd`, `; cat /etc/passwd`; Windows: `ipconfig`, `dir`, `ver`, `echo %CD%`. Burp cluster-bomb (separators × commands) or Wfuzz two payload lists (`WFUZZ`/`WFUZ2Z`). Look for 200s, anomalous length, command output in response. **RCE is destructive/high-impact — read-only PoC (`whoami`) then stop; authorization required for further.**
- **remediation:** Never pass input to shell; use safe APIs/allowlists; drop privileges; input validation.
- **tools:** Burp Intruder, Wfuzz.
- **real-world:** DVGA GraphQL `path` variable → `whoami` as root, `cat /etc/passwd`.

### id: INJ-04 — XSS / Cross-API Scripting (XAS)
- **what:** Script injected via API data executes in a browser (XSS) or propagates through a linked/third-party API into a web app (XAS).
- **where-it-lives:** requests whose data is rendered in a web UI — profile updates, likes, store products, forum/comments; third-party feeds (e.g. LinkedIn→blog sidebar).
- **how-to-detect:** Submit payloads via API to fields shown in the browser; refresh the page to see execution. Most attempts return 400/405; watch outliers.
- **how-to-test:** `<script>alert("xss")</script>`, `<script>alert(1);</script>`, `<%00script>alert(1)</%00script>`, `SCRIPT>alert("XSS");///SCRIPT>`; bypass filters with null bytes/case. XAS: send via profile update or a third-party API; try `Content-Type: text/html` to coax HTML acceptance. Fuzz large XSS lists to find non-400 responses.
- **remediation:** Output-encode/escape on render; input sanitization; CSP; set `X-XSS-Protection`/CT options.
- **tools:** Burp, Wfuzz, PayloadBox XSS list, SecLists.

---

## API9:2023 — IMPROPER INVENTORY / ASSETS MANAGEMENT

### id: ASSET-01 — Improper assets management (old/dev/test versions)
- **what:** Retired or in-development API versions exposed, usually less protected → gateway to EDE/BOLA/mass assignment/injection/weak rate limiting.
- **where-it-lives:** version paths `/v1/ /v2/ /v3/`, `/alpha/ /beta/ /test/ /uat/ /demo/ /internal/ /mobile/ /legacy/ /old/`; `/api/v2/internal/users`, `/api/internal/v2/users`.
- **how-to-detect:** Outdated docs/changelogs/repos referencing retired paths; version patterns.
- **how-to-test:** Fuzz **wide** with Postman: set `baseURL`/`path` as a variable, use Find&Replace to swap `v2`→variable, run Collection Runner across all requests; baseline with a bogus path (expect 404), then test `v1,v3,test,mobile,uat,internal`; flag any non-baseline (e.g. 200 or a differently-sized 500). Then attack the exposed version with the weakness the changelog says was fixed.
- **remediation:** Inventory & retire old versions; block dev/test in prod; keep docs in sync; consistent controls across versions.
- **tools:** Postman Collection Runner, Kiterunner, Amass (finds `legacy-api.` subdomains).
- **real-world:** crAPI `/v2` OTP endpoint had no attempt limit while `/v3` did → 4-digit OTP brute-forceable in ≤10,000 requests.

---

## GRAPHQL-SPECIFIC ATTACKS

### id: GQL-01 — GraphQL recon & endpoint discovery
- **what:** Find the single GraphQL endpoint and any IDE.
- **where-it-lives:** one endpoint (all POST): `/graphql`, `/v1/graphql`, `/api/graphql`, `/graphiql`, `/console`, `/query`, `/playground`, `/altair`; cookies like `env=graphiql:disable`; `Set-Cookie`/title hints; responses are 200 JSON even on error.
- **how-to-detect:** Nmap/Nikto for host+misconfig; DevTools Network for a `graphql` source + JSON preview; directory brute force (Kiterunner/Gobuster with `seclists/Discovery/Web-Content/graphql.txt`), try version/path variants.
- **how-to-test:** Note GraphQL uses `query` (read) and `mutation` (create/update/delete), not HTTP verbs; single request can do both.
- **tools:** Nmap, Nikto, Kiterunner, DevTools, SecLists.

### id: GQL-02 — Introspection & schema reverse engineering
- **what:** Introspection dumps the full schema (types/fields/args) — an info-disclosure gold mine.
- **where-it-lives:** `__schema` introspection query; GraphiQL Docs Explorer (auto-runs introspection).
- **how-to-detect/test:** Send `query IntrospectionQuery { __schema { queryType{name} mutationType{name} types{...} } }`. Capture the GraphiQL introspection request via proxy. **Cookie tampering** to unlock a disabled IDE: base64-decode `env` cookie (`graphiql:disable`) → re-encode `graphiql:enable`, set it in DevTools Storage. Build a Postman collection from the schema; rename opaque requests by body contents. Use **InQL** Burp extension (needs Jython) to auto-enumerate queries/mutations → Repeater.
- **remediation:** Disable introspection in production; disable IDEs; don't gate IDE access on a client-editable cookie.
- **tools:** Burp + InQL (Jython), Postman, GraphiQL Docs Explorer.

### id: GQL-03 — GraphQL BOLA & injection
- **what:** Missing authz on object-ID fields (BOLA) and unsanitized mutation variables (injection).
- **where-it-lives:** query args (`pId`, media ID), mutation `variables` (each `$var`, keys/values at body end).
- **how-to-detect:** Baseline responses are all 200 — detect success by body content and length, not status. Read error bodies for disclosures.
- **how-to-test:** **BOLA:** send a paste/object query, set the ID as Intruder payload position, brute-force sequential IDs; `"public":false` in a response = private data leaked (auth bypass). **Injection:** attack `variables` (query is read-only; hit mutations). Set two payload positions (separator + command) inside a variable, encoding off; the `path` variable in DVGA `importPaste` was OS-command-injectable (`whoami` as root, `; cat /etc/passwd`). **Destructive commands need authorization.**
- **remediation:** Per-object authorization on all ID fields; input validation on resolver args; don't shell out with user input.
- **tools:** Burp Repeater/Intruder + InQL.
- **real-world:** Instagram GraphQL media_id BOLA ($30k), Peloton unauth GraphQL.

---

## FUZZING & EVASION (cross-cutting)

### id: FUZZ-01 — Fuzzing strategy (wide & deep)
- **what:** Wide = one payload across all requests (find improper assets, valid methods, token issues, disclosures); Deep = many payloads into one request (BOLA/BFLA/injection/mass assignment).
- **how-to-test:** Establish a baseline (send expected/failing values, note status+length+content). Generic payloads: long `AAAA...`/`9999...` strings, `~'!@#$%^&*()-_+`, `{}[]|\:";'<>?,./`, `%00`, `0x00`, `$ne`/`$gt` (+`%24ne`/`%24gt`), `|whoami`, `-- -`, `' OR 1=1-- -`, multibyte chars, emojis. Request the unexpected (type/size mismatches); append fuzz after a valid-looking value to escape validation (`a@b.com%00` followed by the fuzz payload, cluster-bomb escape×payload). Detect anomalies with Burp Comparer (Sync Views). Fuzz-for-directory-traversal: `..`, `..\`, `../`, `\..\`, `\..\.\`.
- **tools:** Postman Collection Runner (wide), Burp Intruder / Wfuzz (deep), SecLists (`big-list-of-naughty-strings.txt`), fuzzdb, Wfuzz `All_attack.txt`.

### id: EVADE-01 — WAF / security-control evasion
- **what:** Bypass WAF/input-validation to land payloads.
- **how-to-detect:** Attack noisily to reveal controls, OR (preferred) use the API normally first and inspect for WAF headers (`X-CDN: Imperva/fastly/akamai/Incapsula`, `Server: Zenedge/Kestrel`, `X-Zen-Fury`), 302→CDN. Nmap `--script http-waf-detect`; Wafw00f/W3af/Bypass WAF.
- **how-to-test:** **Burner accounts** (unique identity/IP per account) to probe thresholds safely. **String terminators:** `%00 0x00 // ; % ! ? [] %5B%5D %09 %0a %0b %0c %0e` placed in payloads (e.g. `<s%00cript>`). **Case switching:** `<sCriPt>`, `SeLeCT @@vErSion`. **Encoding:** URL (best), HTML, base64; double-encode if the stack decodes twice. Automate: Burp Intruder Payload Processing (encode→prefix `%00`→suffix `%00`); Wfuzz encoders (`-z file,list,base64`, chain with `-` or stack per-payload with `@`, e.g. `base64@random_upper`).
- **remediation:** Canonicalize/normalize input before validation; decode fully once; consistent filtering; don't rely on WAF alone.
- **tools:** Burp Decoder/Intruder, Wfuzz, Wafw00f/W3af, Awesome-WAF repo, SecLists.

---

## CORE TOOLKIT
Chrome DevTools (Network/Sources/Memory/Performance), Burp Suite (Proxy, Repeater, Intruder, Sequencer, Comparer, Decoder, Extender: InQL, IP Rotate), Postman (collections, environments, Collection Runner, proxy capture, tests), Nmap, OWASP ZAP, Gobuster/Dirbuster, Kiterunner, Wfuzz, Arjun, SQLmap, jwt_tool, Hashcat, OWASP Amass, Nikto, Wireshark, FoxyProxy, SecLists / fuzzdb / Assetnote wordlists, Mentalist/CUPP.

---

## API SECURITY TESTING CHECKLIST

- [ ] **Approach:** black / gray / white box?
- [ ] **Passive recon:** attack-surface discovery; exposed secrets.
- [ ] **Active recon:** scan ports/services; use app as intended; DevTools inspection; find API directories; discover endpoints.
- [ ] **Endpoint analysis:** find/review docs; reverse engineer; use as intended; analyze responses for info disclosure / excessive data exposure / business logic.
- [ ] **Authentication:** basic-auth testing; attack/manipulate tokens (forge, none, alg-switch, crack).
- [ ] **Fuzz all the things** (wide then deep).
- [ ] **Authorization:** discover resource-ID methods; test BOLA; test BFLA.
- [ ] **Mass assignment:** discover standard params; test mass assignment; combine with BFLA.
- [ ] **Injection:** find input-accepting requests; XSS/XAS; DB-specific (SQL/NoSQL); OS command.
- [ ] **Rate limits:** existence; avoidance (throttle); bypass (path/origin/IP-rotate).
- [ ] **Evasion:** string terminators; case switching; encoding; combine; re-run all prior attacks with evasion.
- [ ] **Combine findings & report** with PoC + business impact.
