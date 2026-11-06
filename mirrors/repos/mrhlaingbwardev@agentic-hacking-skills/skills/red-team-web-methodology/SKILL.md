---
name: red-team-web-methodology
description: Use when user says "red team", "full pentest", "web pentest", "find vulnerabilities", "security assessment", "attack chain". Professional web app red team methodology combining recon, manual testing, and business logic exploitation.
---

# Red Team Web Application Methodology

**CRITICAL MINDSET**: This is NOT a script kiddie scanner skill. This is a professional red team methodology that combines strategic reconnaissance, manual testing, business logic exploitation, and creative attack chains.

## When to Use This Skill

Use ONLY when:
- User asks for **comprehensive web application security assessment**
- Request includes terms: "red team", "full pentest", "deep security analysis", "find all vulnerabilities"
- User wants **manual exploitation**, not just automated scanning
- Target is a **dynamic web application** with authentication, business logic, APIs

Do NOT use when:
- User just wants quick automated scan (use nuclei/sqlmap directly instead)
- Target is simple static website
- User asks for specific vulnerability only (SQLi, XSS) - test that specific thing directly

---

## Red Team Methodology - NOT Tool Running

### Phase 0: Intelligence Gathering (BEFORE any tools)

**Objective**: Understand the target like a real attacker

```markdown
1. Business Context Analysis:
   - What does this application DO? (e-commerce? banking? SaaS?)
   - Who are the users? (customers, admins, internal staff?)
   - What's valuable? (money, data, accounts, infrastructure access?)
   - What would damage them most? (data breach, account takeover, payment fraud?)

2. Technology Stack Mapping:
   - Frontend: React/Vue/Angular? jQuery? Plain HTML?
   - Backend: PHP/Python/Node.js/Java/.NET?
   - Database: MySQL/PostgreSQL/MongoDB/MSSQL?
   - Infrastructure: Cloud (AWS/Azure/GCP)? CDN? WAF?
   - Third-party: Payment gateways, OAuth providers, APIs?

3. Attack Surface Enumeration:
   - Authentication mechanisms (login, SSO, API keys, OAuth)
   - User roles & privilege levels (guest, user, admin, super admin)
   - Critical functions (payment, file upload, password reset, 2FA)
   - API endpoints (REST, GraphQL, SOAP, WebSocket)
   - External integrations (webhooks, callbacks, redirects)

4. Threat Model:
   - External attacker goal: Account takeover? Data exfil? Defacement?
   - Insider threat: Privilege escalation? Lateral movement?
   - Supply chain: Can we compromise via third-party services?
```

**ACTION**: Ask user these questions FIRST before running any tools. Understand the target.

---

### Phase 1: Passive Reconnaissance (Manual + Automated)

**DO NOT blindly run tools. Each tool serves a strategic purpose.**

#### 1.1 Subdomain Discovery (Find Attack Surface)

**Why**: Find forgotten subdomains, staging servers, dev environments, admin panels

```bash
# Strategic subdomain enumeration
subfinder -d target.com -silent | httpx -silent -title -tech-detect -status-code

# Look for HIGH-VALUE targets:
# - dev.target.com, staging.target.com (weak security)
# - admin.target.com, panel.target.com (privileged access)
# - api.target.com, api-v2.target.com (API endpoints)
# - old.target.com, legacy.target.com (outdated code)
# - test.target.com, demo.target.com (default credentials)
```

**Manual Analysis**:
- Which subdomains have different tech stacks? (easier to exploit)
- Which ones lack WAF protection?
- Which ones expose internal infrastructure? (Jenkins, GitLab, AWS S3)

#### 1.2 Technology Fingerprinting (Know Your Enemy)

**Why**: Different technologies = different vulnerabilities

```bash
# Detailed tech detection
whatweb https://target.com -a 3
httpx -u https://target.com -tech-detect -status-code -title

# Check for:
# - Framework versions (outdated = CVEs)
# - Server software (Apache 2.4.49 = RCE)
# - JavaScript libraries (jQuery 1.x = XSS)
# - WAF presence (Cloudflare, Akamai, AWS WAF)
```

**Strategic Thinking**:
- If PHP + Apache → check for `.htaccess` bypass, PHP type juggling
- If Node.js → check for prototype pollution, ReDoS
- If Java → check for deserialization, XXE, SSRF
- If WordPress/Drupal → check for plugin vulns, weak admin

#### 1.3 Content Discovery (Find Hidden Functionality)

**Why**: Developers hide, not remove. Find admin panels, debug pages, backup files, API docs.

**CRITICAL**: Do NOT blindly fuzz with 5000+ paths. Be strategic.

```bash
# SMART content discovery (prioritized paths)
# 1. Admin/Management interfaces
ffuf -u https://target.com/FUZZ -w admin-paths.txt -mc 200,301,302,403,401

# 2. API documentation & endpoints
ffuf -u https://target.com/FUZZ -w api-paths.txt -mc 200,301,302

# 3. Backup & config files
ffuf -u https://target.com/FUZZ -w backups.txt -mc 200

# 4. Source code exposure
# Check: .git/config, .env, .DS_Store, web.config, composer.json
```

**Custom wordlists based on tech stack**:
- PHP app → check for `.php.bak`, `config.php.old`, `upload.php`
- Node.js → check for `package.json`, `.env`, `server.js`
- Python → check for `settings.py`, `requirements.txt`, `.pyc`

**Manual Checks** (MORE IMPORTANT than fuzzing):
- `/robots.txt` - what are they hiding?
- `/sitemap.xml` - full site structure
- `/.well-known/security.txt` - bug bounty scope
- JavaScript source maps - `/main.js.map` reveals source code
- GraphQL introspection - `/__graphql?query={__schema{types{name}}}`

---

### Phase 2: Active Reconnaissance (Crawling + Spidering)

**Objective**: Map ALL functionality, not just public pages

#### 2.1 Authenticated Crawling

**CRITICAL**: Most vulns are in authenticated areas. Create test accounts.

```bash
# 1. Register test accounts at DIFFERENT privilege levels:
# - Free user account
# - Premium/paid account (if possible)
# - Admin/moderator (if available via signup)

# 2. Authenticated crawling with katana
katana -u https://target.com/dashboard -H "Cookie: session=XXX" -d 5 -silent

# 3. Extract all endpoints, parameters, forms
```

**Manual Analysis**:
- What can low-privilege user access?
- What's hidden from unauthenticated users?
- What changes between user roles?

#### 2.2 JavaScript Analysis (Find Hidden APIs)

**Why**: Modern apps hide API endpoints in JavaScript

```bash
# Extract all JavaScript files
katana -u https://target.com -jc -silent | grep '\.js$'

# Analyze for:
# - API endpoints: /api/v1/users, /graphql, /internal/admin
# - Hardcoded secrets: API keys, tokens, AWS credentials
# - Internal URLs: admin.internal.target.com
# - Debug flags: ?debug=1, ?test=true
# - Commented code: // TODO: remove this admin backdoor
```

**Manual Tools**:
- Browser DevTools → Network tab → watch all requests
- Burp Suite → Proxy history → analyze every request/response
- Check for:
  - JWT tokens (decode payload, check expiration, weak signing)
  - API keys in headers (Authorization, X-API-Key)
  - Session tokens (predictable? short? no httpOnly flag?)

#### 2.3 Parameter Discovery

**Why**: Hidden parameters = hidden functionality

```bash
# Find hidden parameters in known endpoints
# Example: /api/user?id=123 → test for ?admin=1, ?role=admin, ?debug=true

# Use parameter bruteforcing strategically:
# On sensitive endpoints only: login, payment, admin, API
```

**High-Value Parameters to Test**:
- `debug`, `test`, `dev` - enable debug mode
- `admin`, `role`, `privilege` - privilege escalation
- `redirect`, `url`, `next`, `return` - open redirect/SSRF
- `file`, `path`, `template` - LFI/RFI
- `callback`, `webhook` - SSRF

---

### Phase 3: Vulnerability Identification (Strategic Testing)

**NOT random tool running. Test based on findings.**

#### 3.1 Authentication & Session Attacks

**Manual Testing First** (tools are secondary):

```markdown
1. Registration/Signup:
   - Can you register as admin@target.com? (email validation bypass)
   - Unicode/homograph attacks: аdmin@target.com (Cyrillic 'a')
   - SQL injection in registration: ' OR '1'='1
   - XSS in profile fields (stored XSS)

2. Login:
   - Default credentials: admin/admin, admin/password
   - SQL injection: admin' OR '1'='1'--
   - NoSQL injection: {"username": {"$ne": null}, "password": {"$ne": null}}
   - Username enumeration: different error messages for valid/invalid users
   - Rate limiting: can you brute force passwords?
   - 2FA bypass: can you skip 2FA? Race condition?

3. Password Reset:
   - Token predictability: sequential? time-based?
   - Token reuse: can you use token multiple times?
   - Host header injection: change reset link domain
   - Parameter pollution: reset for different user
   - Email parameter tampering: change victim email

4. Session Management:
   - Session fixation: can you set victim's session?
   - Session hijacking: steal session cookie (XSS, network sniffing)
   - Concurrent sessions: logout all devices?
   - Session timeout: does session expire?
   - Cookie security: httpOnly? secure? SameSite?
```

**Tools** (after manual checks):

```bash
# Only if manual testing suggests vulnerability
sqlmap -u "https://target.com/login" --data "username=admin&password=test" --level 5 --risk 3
```

#### 3.2 Authorization & Access Control

**CRITICAL**: This is where most real-world vulns are. Manual testing REQUIRED.

```markdown
1. Horizontal Privilege Escalation:
   - View other users' data: /profile?id=123 → /profile?id=124
   - IDOR in APIs: /api/orders/456 → /api/orders/457
   - Test with different accounts: can UserA access UserB's resources?

2. Vertical Privilege Escalation:
   - Access admin functions as regular user
   - Change role parameter: {"role": "user"} → {"role": "admin"}
   - JWT manipulation: change "admin": false → "admin": true
   - Cookie tampering: role=user → role=admin

3. Missing Function-Level Access Control:
   - Direct URL access: https://target.com/admin (without authentication)
   - API endpoint bypass: /api/admin/users (check as non-admin)
   - HTTP method bypass: GET /admin/delete?id=1 (if POST is protected)

4. Business Logic Flaws:
   - Negative quantities: buy -1 items = get money
   - Race conditions: withdraw $100 twice simultaneously
   - Discount code reuse: apply 50% discount multiple times
   - Workflow bypass: skip payment, go directly to success page
   - Price manipulation: change price in request before payment
```

**Testing Approach**:
1. Map all user roles (guest, user, premium, admin)
2. Create account for each role
3. Test EVERY sensitive function with EVERY role
4. Document: what SHOULD role X access? what CAN role X access?

#### 3.3 Injection Attacks (Strategic, Not Blind)

**SQL Injection** - Test where it makes sense:

```markdown
Where to test:
- Search functionality: ?search=test
- Login forms: username/password
- Filter parameters: ?category=electronics&sort=price
- API endpoints: /api/products?id=123

NOT everywhere blindly. Focus on database-driven features.
```

```bash
# Manual testing first:
# 1. Single quote: '
# 2. Boolean-based: ' OR '1'='1
# 3. Time-based: ' OR SLEEP(5)--

# THEN use sqlmap if manual confirms SQLi:
sqlmap -u "https://target.com/product?id=1" --batch --random-agent --level 3
```

**XSS** - Context matters:

```markdown
Test in:
- User input fields: search, comments, profile bio
- URL parameters: ?name=<script>alert(1)</script>
- File uploads: upload HTML/SVG file
- JSON APIs: {"name": "<script>alert(1)</script>"}

Contexts to test:
1. HTML context: <script>alert(1)</script>
2. Attribute context: "><script>alert(1)</script>
3. JavaScript context: ';alert(1);//
4. URL context: javascript:alert(1)
```

**XXE** - If XML processing exists:

```xml
<!-- Test in SOAP APIs, XML uploads, RSS feeds -->
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root>&xxe;</root>
```

**SSRF** - Test in URL-fetching features:

```markdown
Test in:
- Image URL fetch: ?imageUrl=http://internal-server/admin
- Webhook callbacks: ?webhook=http://169.254.169.254/latest/meta-data/
- PDF generators: generate PDF from URL
- oEmbed endpoints: ?url=http://localhost:6379/
```

#### 3.4 File Upload Vulnerabilities

**Strategic Testing**:

```markdown
1. Upload PHP webshell:
   - shell.php → blocked by extension filter
   - shell.php.jpg → may execute as PHP
   - shell.phtml, shell.php5, shell.phar → alternative extensions
   
2. Content-Type bypass:
   - Upload .php but set Content-Type: image/jpeg
   
3. Magic bytes bypass:
   - GIF89a at start of file + PHP code after
   
4. Path traversal:
   - Filename: ../../../evil.php
   
5. Zip slip:
   - Extract zip with files at ../../../../tmp/evil.sh
```

#### 3.5 Business Logic Exploitation

**MOST CRITICAL - No tool can find these**:

```markdown
E-commerce:
- Apply multiple discount codes (if only one should work)
- Negative quantity in cart (-1 × $100 = refund $100)
- Race condition: add $100 coupon, use it in 2 orders simultaneously
- Payment bypass: intercept request, change amount to $0.01
- Refund exploitation: buy with stolen card, refund to your account

Banking/Finance:
- Transfer race condition: transfer $1000 twice from account with $1000
- Interest calculation: deposit $1, withdraw $1, repeat for interest
- Rounding errors: $0.001 × 1000000 transactions = $1000

Social Media:
- Mass following/unfollowing (rate limit bypass)
- Fake engagement (like your own post from multiple accounts)
- Content injection (post as another user via parameter manipulation)

SaaS/Subscriptions:
- Downgrade after using premium features
- Export all data, cancel subscription, keep data
- Invite unlimited users, keep them after downgrade
```

---

### Phase 4: Exploitation & Impact Demonstration

**Objective**: Prove the vulnerability's real-world impact

```markdown
1. Chain vulnerabilities:
   - XSS + CSRF = account takeover
   - SSRF + XXE = internal network access
   - IDOR + file upload = webshell on victim's account

2. Demonstrate business impact:
   - SQLi → dump customer database → calculate data breach cost
   - Privilege escalation → show admin panel access
   - Payment bypass → show free premium account
   - RCE → show system access (create file, don't destroy)

3. Responsible exploitation:
   - Create test.txt file, not delete databases
   - Use alert(document.domain), not keylogger
   - Dump 5 records, not entire database
   - Access /etc/hostname, not /etc/shadow
```

---

### Phase 5: Reporting (Red Team Quality)

**NOT just vulnerability list. Strategic analysis.**

```markdown
1. Executive Summary:
   - Business impact first, technical details second
   - "Attackers can steal all customer credit cards" (not "SQL injection found")
   - Risk rating: Critical/High/Medium/Low
   - Estimated damage: financial, reputation, legal

2. Attack Scenarios:
   - "How would a real attacker exploit this?"
   - Step-by-step attack chain
   - What's the worst-case scenario?

3. Technical Details:
   - Request/response proof
   - Steps to reproduce
   - Affected components
   - Root cause analysis

4. Remediation:
   - Prioritized fixes (critical first)
   - Code examples of secure implementation
   - General security recommendations
```

---

## Execution Workflow

When user asks for red team web assessment:

```markdown
STEP 1: INTELLIGENCE (Ask user first, don't run tools yet)
┌─────────────────────────────────────────┐
│ Ask user:                               │
│ 1. What does this application do?      │
│ 2. Do you have test credentials?       │
│ 3. What's the tech stack (if known)?   │
│ 4. What's most critical to protect?    │
│ 5. Any areas out of scope?             │
└─────────────────────────────────────────┘
         ↓
STEP 2: PASSIVE RECON (Understand target)
┌─────────────────────────────────────────┐
│ - Subdomain enumeration (subfinder)     │
│ - Tech fingerprinting (httpx, whatweb) │
│ - Manual analysis of findings          │
│ - Identify high-value targets          │
└─────────────────────────────────────────┘
         ↓
STEP 3: ACTIVE RECON (Map application)
┌─────────────────────────────────────────┐
│ - Register test accounts (low + high)  │
│ - Authenticated crawling (katana)       │
│ - JavaScript analysis (manual)          │
│ - API endpoint discovery               │
│ - Parameter identification              │
└─────────────────────────────────────────┘
         ↓
STEP 4: MANUAL TESTING (Primary method)
┌─────────────────────────────────────────┐
│ Priority 1: Business Logic             │
│ - Test all user flows manually         │
│ - Test access controls (IDOR, privesc) │
│ - Test payment/critical functions      │
│                                         │
│ Priority 2: Authentication              │
│ - Login, registration, password reset  │
│ - Session management, 2FA bypass       │
│                                         │
│ Priority 3: Injection                   │
│ - SQLi in database features            │
│ - XSS in user input                    │
│ - SSRF in URL-fetching features        │
└─────────────────────────────────────────┘
         ↓
STEP 5: AUTOMATED SCANNING (Supplement)
┌─────────────────────────────────────────┐
│ - nuclei for known CVEs (targeted)      │
│ - sqlmap for confirmed SQLi            │
│ - NOT blind scanning everywhere        │
└─────────────────────────────────────────┘
         ↓
STEP 6: EXPLOITATION (Prove impact)
┌─────────────────────────────────────────┐
│ - Chain vulnerabilities                │
│ - Demonstrate business impact          │
│ - Responsible exploitation only        │
└─────────────────────────────────────────┘
         ↓
STEP 7: REPORTING (Professional)
┌─────────────────────────────────────────┐
│ - Executive summary (business impact)  │
│ - Attack scenarios (real-world risk)   │
│ - Technical details (reproduction)     │
│ - Remediation (prioritized fixes)      │
└─────────────────────────────────────────┘
```

---

## Critical Success Factors

### DO:
- ✅ Understand the business context BEFORE testing
- ✅ Think like an attacker with a goal (steal money, data, access)
- ✅ Manual testing FIRST, tools SECOND
- ✅ Test business logic (no tool can do this)
- ✅ Test with multiple user roles
- ✅ Chain vulnerabilities for maximum impact
- ✅ Document everything with proof
- ✅ Responsible exploitation only

### DON'T:
- ❌ Blindly run automated scanners
- ❌ Test everything with every tool
- ❌ Skip manual testing
- ❌ Ignore business logic
- ❌ Test only as unauthenticated user
- ❌ Report findings without impact analysis
- ❌ Cause damage or disruption
- ❌ Act like a script kiddie

---

## Example Execution

**Bad approach (script kiddie)**:
```
1. Run nuclei on target
2. Run sqlmap on all URLs
3. Run ffuf with 10000 paths
4. Report: "Found XSS, SQLi, open redirect"
```

**Good approach (red teamer)**:
```
1. Understand: E-commerce site selling electronics
2. Register: Create buyer + seller accounts
3. Analyze: Payment flow, order processing, refunds
4. Find: Seller can modify order amount after buyer payment
5. Test: Change $100 order to $0.01 after payment approval
6. Exploit: Demonstrate free product purchase
7. Chain: Combine with IDOR to modify ANY order
8. Impact: "Attackers can buy unlimited products for $0.01"
9. Report: Business impact + attack scenario + fix
```

---

## Tools Reference (When to Use)

| Tool | Use Case | When to Use |
|------|----------|-------------|
| `subfinder` | Subdomain discovery | ALWAYS - find attack surface |
| `httpx` | HTTP probing | After subdomain discovery |
| `whatweb` | Tech fingerprinting | On all live targets |
| `katana` | Authenticated crawling | CRITICAL - after login |
| `nuclei` | Known CVE scanning | On specific tech stacks only |
| `ffuf` | Content discovery | On high-value targets (admin, API) |
| `sqlmap` | SQL injection | ONLY after manual confirmation |
| `Burp Suite` | Manual testing | PRIMARY tool for testing |

**Remember**: Tools find 20% of vulns. Manual testing finds 80%.

---

## Success Metrics

Red team assessment is successful when:
1. ✅ You understand the application's purpose and critical assets
2. ✅ You tested as MULTIPLE user roles (not just one)
3. ✅ You found business logic flaws (not just SQLi/XSS)
4. ✅ You demonstrated REAL impact (not just POC)
5. ✅ You can explain how real attackers would exploit this
6. ✅ Your report helps developers fix root causes, not just symptoms
7. ✅ Client understands business risk, not just technical jargon

**Failure**: Running tools, generating automated reports, no manual testing, no business context.

---

## Final Note

This is a METHODOLOGY skill, not a tool-running script. OpenCode agent must:
- ASK questions about the target
- THINK strategically about attack vectors
- TEST manually for business logic
- USE tools to SUPPLEMENT manual testing
- REPORT with business impact focus

**We are red teamers, not script kiddies.** 🎯
