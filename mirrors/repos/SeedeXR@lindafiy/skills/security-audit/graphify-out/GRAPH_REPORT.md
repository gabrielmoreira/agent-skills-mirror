# Graph Report - kb  (2026-07-22)

## Corpus Check
- Corpus is ~22,770 words - fits in a single context window. You may not need a graph.

## Summary
- 193 nodes · 169 edges · 49 communities (18 shown, 31 thin omitted)
- Extraction: 69% EXTRACTED · 31% INFERRED · 0% AMBIGUOUS · INFERRED: 53 edges (avg confidence: 0.84)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Injection & LLM Attacks
- Recon, Scanning & Exploitation
- Authentication & JWT Attacks
- Crypto, TLS & Network Sniffing
- Dependency & Supply-Chain Scanning
- Access Control (BOLA/BFLA)
- Misconfiguration & DAST
- Credential Attacks & SSH
- Object-Property Authz & Mass Assignment
- SSRF & Cloud Metadata
- File Inclusion & Path Traversal
- Supply-Chain Integrity & CI/CD
- OSINT & DNS Recon
- Secrets Detection
- Session Token Attacks
- Dependency Confusion & Typosquatting
- Business Logic Flaws
- CSRF
- Misc 18
- Misc 19
- Misc 20
- Misc 21
- Misc 22
- Misc 23
- Misc 24
- Misc 25
- Misc 26
- Misc 27
- Misc 28
- Misc 29
- Misc 30
- Misc 31
- Misc 32
- Misc 33
- Misc 34
- Misc 35
- Misc 36
- Misc 37
- Misc 38
- Misc 39
- Misc 40
- Misc 41
- Misc 42
- Misc 43
- Misc 44
- Misc 45
- Misc 46
- Misc 47
- Misc 48

## God Nodes (most connected - your core abstractions)
1. `A03:2021 Injection (incl. XSS)` - 8 edges
2. `A05:2021 Security Misconfiguration` - 7 edges
3. `BOLA / IDOR (broken object level authorization)` - 6 edges
4. `API2:2023 Broken Authentication` - 6 edges
5. `API8:2023 Security Misconfiguration` - 6 edges
6. `A06:2021 Vulnerable and Outdated Components` - 6 edges
7. `Nmap (network/host)` - 6 edges
8. `JWT secret crack (HS256/512)` - 5 edges
9. `Brute-forcible login` - 5 edges
10. `Security misconfiguration (API)` - 4 edges

## Surprising Connections (you probably didn't know these)
- `BOLA / IDOR (broken object level authorization)` --semantically_similar_to--> `API1:2023 BOLA (modern)`  [INFERRED] [semantically similar]
  api-security.md → modern-security.md
- `NoSQL injection (API)` --semantically_similar_to--> `A03:2021 Injection (incl. XSS)`  [INFERRED] [semantically similar]
  api-security.md → modern-security.md
- `Automated vulnerability scanning (Nessus)` --semantically_similar_to--> `A06:2021 Vulnerable and Outdated Components`  [INFERRED] [semantically similar]
  network-host-security.md → modern-security.md
- `Brute-forcible login` --semantically_similar_to--> `A07:2021 Identification and Authentication Failures`  [INFERRED] [semantically similar]
  web-application-security.md → modern-security.md
- `OSINT footprinting (infra)` --semantically_similar_to--> `Passive OSINT / attack-surface mapping (API)`  [INFERRED] [semantically similar]
  network-host-security.md → api-security.md

## Hyperedges (group relationships)
- **Injection-class vulnerabilities (cross-book)** — kb_api_security_sql_injection, kb_api_security_nosql_injection, kb_api_security_os_command_injection, kb_web_application_security_sql_injection, kb_web_application_security_os_command_injection, kb_web_application_security_xpath_injection, kb_web_application_security_ldap_injection, kb_modern_security_a03_injection [INFERRED 0.85]
- **Authentication / session / access-control attack surface** — kb_web_application_security_brute_force_login, kb_web_application_security_predictable_tokens, kb_web_application_security_session_fixation, kb_web_application_security_broken_access_control, kb_api_security_bola, kb_api_security_bfla, kb_api_security_broken_authentication [INFERRED 0.80]
- **Reconnaissance-phase activities** — kb_api_security_passive_recon, kb_api_security_active_recon, kb_network_host_security_recon_osint, kb_network_host_security_recon_dns, kb_network_host_security_scan_syn [INFERRED 0.80]

## Communities (49 total, 31 thin omitted)

### Community 0 - "Injection & LLM Attacks"
Cohesion: 0.11
Nodes (22): API8:2023 Security Misconfiguration, Information disclosure (API), NoSQL injection (API), OS command injection (API), SQL injection (API), SQLmap, XSS / Cross-API Scripting (API), A03:2021 Injection (incl. XSS) (+14 more)

### Community 1 - "Recon, Scanning & Exploitation"
Cohesion: 0.10
Nodes (20): Active detection & endpoint discovery (API), Kiterunner, Nmap (API), Anonymous / default-access services, Exploited weakness classes (patch/default-creds/backdoor), Host / network hardening checklist, Metasploit, Metasploit framework flow (+12 more)

### Community 2 - "Authentication & JWT Attacks"
Cohesion: 0.15
Nodes (18): API2:2023 Broken Authentication, Hashcat (API), JWT algorithm switch / key confusion (RS256 to HS256), JWT none-algorithm attack, JWT secret crack (HS256/512), jwt_tool, OAuth 2.0 implementation flaws (API), A07:2021 Identification and Authentication Failures (+10 more)

### Community 3 - "Crypto, TLS & Network Sniffing"
Cohesion: 0.16
Nodes (14): A02:2021 Cryptographic Failures, testssl.sh, TLS configuration hardening, ARP cache poisoning (MITM), DNS cache poisoning / spoofing, Ettercap / arpspoof / sslstrip, Credential-hygiene findings, Traffic capture / sniffing (+6 more)

### Community 4 - "Dependency & Supply-Chain Scanning"
Cohesion: 0.15
Nodes (13): A06:2021 Vulnerable and Outdated Components, Checkov, Grype, IaC / config misconfiguration, npm audit, OSV-Scanner, SARIF (normalized findings format), SBOM (CycloneDX / SPDX) (+5 more)

### Community 5 - "Access Control (BOLA/BFLA)"
Cohesion: 0.20
Nodes (12): API1:2023 BOLA, API5:2023 BFLA, BFLA (broken function level authorization), BOLA / IDOR (broken object level authorization), Burp Suite, GraphQL BOLA & injection, Postman, A01:2021 Broken Access Control (+4 more)

### Community 6 - "Misconfiguration & DAST"
Cohesion: 0.25
Nodes (9): Security misconfiguration (API), OWASP ZAP (API), A05:2021 Security Misconfiguration, Container / Dockerfile runtime hardening, CORS misconfiguration, nuclei, Security response headers, OWASP ZAP (DAST) (+1 more)

### Community 7 - "Credential Attacks & SSH"
Cohesion: 0.25
Nodes (8): Broken authentication / brute force / spraying (API), Wfuzz, Hydra (network/host), SSHExec / token impersonation, Online password guessing (brute/dictionary), SSH hardening checklist, Brute-forcible login, Username enumeration

### Community 8 - "Object-Property Authz & Mass Assignment"
Cohesion: 0.50
Nodes (5): API3:2023 Broken Object Property Level Authorization, Arjun, Excessive data exposure, Mass assignment, API3:2023 BOPLA (modern)

### Community 9 - "SSRF & Cloud Metadata"
Cohesion: 0.50
Nodes (5): API7:2023 Server Side Request Forgery, Server-side request forgery (API annotation), A10:2021 Server-Side Request Forgery, SSRF + cloud metadata (IMDS v1/v2), Web server used as an open proxy

### Community 10 - "File Inclusion & Path Traversal"
Cohesion: 0.40
Nodes (5): WAF / security-control evasion (API), Fuzzing strategy (wide & deep), Manual analysis & research (directory traversal, LFI), Remote / local file inclusion, Path / directory traversal

### Community 11 - "Supply-Chain Integrity & CI/CD"
Cohesion: 0.40
Nodes (5): A08:2021 Software and Data Integrity Failures, Artifact signing & provenance verification (Sigstore/cosign), CI/CD security (GitHub Actions hardening), cosign, SLSA build provenance

### Community 12 - "OSINT & DNS Recon"
Cohesion: 0.50
Nodes (4): OWASP Amass, Passive OSINT / attack-surface mapping (API), DNS recon & zone transfer, OSINT footprinting (infra)

### Community 13 - "Secrets Detection"
Cohesion: 0.50
Nodes (4): Exposed / leaked credentials & keys (API), gitleaks, Secrets detection, trufflehog

### Community 14 - "Session Token Attacks"
Cohesion: 0.50
Nodes (4): Token forgery / weak token entropy (API), HTTP header injection & response splitting, Predictable session tokens, Session fixation

### Community 15 - "Dependency Confusion & Typosquatting"
Cohesion: 0.50
Nodes (4): Dependency confusion, Lockfile integrity, A03:2025 Software Supply Chain Failures, Typosquatting

### Community 16 - "Business Logic Flaws"
Cohesion: 0.67
Nodes (3): API6:2023 Unrestricted Access to Sensitive Business Flows, Business logic flaw abuse (API), Application logic flaws

### Community 17 - "CSRF"
Cohesion: 0.67
Nodes (3): CSRF (modern defenses), Cross-site request forgery (XSRF), On-site request forgery (OSRF)

## Knowledge Gaps
- **99 isolated node(s):** `API Security (KB)`, `Modern Security (KB)`, `Network & Host Security (KB)`, `Web Application Security (KB)`, `Exposed / leaked credentials & keys (API)` (+94 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Brute-forcible login` connect `Credential Attacks & SSH` to `Authentication & JWT Attacks`, `Access Control (BOLA/BFLA)`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `A03:2021 Injection (incl. XSS)` connect `Injection & LLM Attacks` to `Dependency & Supply-Chain Scanning`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `Burp Suite (web app)` connect `Access Control (BOLA/BFLA)` to `Credential Attacks & SSH`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `A03:2021 Injection (incl. XSS)` (e.g. with `NoSQL injection (API)` and `Reflected (first-order) XSS`) actually correct?**
  _`A03:2021 Injection (incl. XSS)` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `BOLA / IDOR (broken object level authorization)` (e.g. with `API1:2023 BOLA (modern)` and `Broken access control (vertical & horizontal privilege escalation)`) actually correct?**
  _`BOLA / IDOR (broken object level authorization)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `API Security (KB)`, `Modern Security (KB)`, `Network & Host Security (KB)` to the rest of the system?**
  _99 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Injection & LLM Attacks` be split into smaller, more focused modules?**
  _Cohesion score 0.11255411255411256 - nodes in this community are weakly interconnected._