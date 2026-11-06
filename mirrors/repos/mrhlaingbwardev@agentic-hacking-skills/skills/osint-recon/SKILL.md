---
name: osint-recon
description: Use when user says "ရှာ", "osint", "recon", "investigate", "research", "target", "ခြေရာခံ", "information gathering", "passive recon", "footprint". Performs nation-level OSINT including passive recon, WHOIS history, DNS archaeology, employee enumeration, technology profiling, and social media mapping WITHOUT touching the target.
---

# OSINT & Passive Reconnaissance

## TRIGGER RULES
Activate when user says: "ရှာ", "osint", "recon", "investigate", "target", "ခြေရာခံ", "စုံစမ်း", "gather info", "passive", "footprint", "whois"

---

## SACRED RULE: NO ACTIVE SCANNING

OSINT = ZERO packets to target. Everything must be from:
- Public databases
- Search engines
- DNS passive sources
- Archived data
- Third-party services
- Certificate transparency logs

---

## PHASE 1: Domain & Infrastructure Mapping

### WHOIS History (multiple sources):
```powershell
# Current WHOIS
whois domain.com

# Historical WHOIS via web (passive)
```
Check: registrar, registrant name, email, phone, creation date, name servers

### DNS Passive Enumeration:
Services to query (via web/API):
- crt.sh (certificate transparency): `https://crt.sh/?q=%.domain.com`
- SecurityTrails
- AlienVault OTX
- DNSDumpster
- Shodan (passive)
- Censys (passive)

### SSL/TLS Certificate Analysis:
- Fetch certs from crt.sh
- Check SAN (Subject Alternative Names) for hidden subdomains
- Check issuer, validity period, organization info

### Historical DNS Records:
- SecurityTrails historical DNS
- DNSDB
- PassiveTotal
- Check for old A records pointing to different IPs
- Check for old MX records (reveals email provider migrations)

### IP Range & ASN:
- Find IP ranges from WHOIS org/ISP
- Map all IP blocks belonging to the organization
- Check neighboring IPs (shared hosting neighbors)

---

## PHASE 2: Technology & Infrastructure Profiling

### Technology Stack (passive):
- BuiltWith: `https://builtwith.com/domain.com`
- Wappalyzer data
- Check HTTP headers via third-party (not direct): securityheaders.com, observatory.mozilla.org
- Wayback Machine for historical tech changes

### Cloud & Hosting:
- IP → cloud provider mapping (AWS, Azure, GCP, DigitalOcean)
- Check for cloud-specific subdomains: `s3.amazonaws.com/domain`, `domain.blob.core.windows.net`
- Check for CDN: Cloudflare, Akamai, Fastly, CloudFront
- Check for email providers: Google Workspace, Microsoft 365 (via MX records)

### JavaScript & Source Analysis (via Wayback/archives):
- Extract all JS files from archived pages
- Search for API endpoints, internal URLs
- Search for credentials accidentally in JS
- Check package.json and dependencies

---

## PHASE 3: Employee & Organization Discovery

### LinkedIn:
- Search: `"Company Name" employees`
- Map: engineering, DevOps, security, IT teams
- Note: seniority, tenure, tech stack mentioned
- Find: potential targets for social engineering

### Email Pattern Discovery:
- Find any leaked emails (Hunter.io, phonebook.cz)
- Determine email format: `first.last@company.com` or `f.last@company.com`
- Validate with email verification services

### GitHub/GitLab:
- Search: `org:company` or `@company.com` in commits
- Find: personal repos of employees
- Look for: `.env` files, configs, credentials committed accidentally
- Check: CI/CD configs, deployment scripts, Terraform files

### Paste Sites & Leaks:
- Search pastebin, pastedump for company domain
- Check haveibeenpwned for employee emails
- Check dehashed, intelx for credential dumps
- Search for exposed API keys

---

## PHASE 4: Web Archive Analysis

### Wayback Machine:
```
http://web.archive.org/cdx/search/cdx?url=*.domain.com/*&output=json&collapse=urlkey
```
Search archived URLs for:
- `*.env`, `*.sql`, `*.tar.gz`, `*.zip`, `*.bak`, `*.backup`
- `/admin`, `/backup`, `/test`, `/dev`, `/staging`
- `api_key=`, `password=`, `token=`, `secret=`
- Old API endpoints that might still work
- Robots.txt from different time periods (reveals hidden paths)

### Google Dorks (passive, via web search):
```
site:domain.com filetype:pdf
site:domain.com filetype:sql
site:domain.com inurl:admin
site:domain.com intitle:"index of"
site:domain.com ext:env
site:domain.com ext:log
site:domain.com "password"
site:domain.com "api_key"
```

---

## PHASE 5: Data Breach & Credential Hunting

### Breach Databases:
- DeHashed
- IntelX
- HaveIBeenPwned domain search
- LeakIX
- SnusBase
- Search for: `@domain.com` in breach data

### Cloud Storage Discovery:
- GrayHatWarfare (public S3 buckets)
- `s3.amazonaws.com/company-name`
- `company-name.s3.amazonaws.com`
- Check Google Cloud Storage: `storage.googleapis.com/company-name`

### Code Repositories:
- GitHub code search: `domain.com password`, `domain.com secret`
- GitLab, Bitbucket, SourceForge
- Search gists for domain references

---

## PHASE 6: Intelligence Synthesis

### Build Target Profile:
```
Organization:
  - Legal name, aliases, subsidiaries
  - Primary domain, subdomains
  - IP ranges, ASN, cloud providers
  - Tech stack: languages, frameworks, databases
  
Employees:
  - Key personnel (CEO, CTO, DevOps leads)
  - Email formats
  - Social media profiles
  
Infrastructure:
  - Email provider (Google/Microsoft/self-hosted)
  - CDN/WAF in use
  - Cloud providers with regions
  - Third-party services (analytics, payment, chat)
  
Security Posture:
  - Bug bounty program? (HackerOne, Bugcrowd)
  - Security.txt? /.well-known/security.txt
  - Known CVEs from tech versions
  - Previous breaches/leaks
```

### Report Format:
1. **Executive Summary** - 3 bullet points of key findings
2. **Attack Surface Map** - domains, IPs, services
3. **Employee Exposure** - key targets, leaked credentials
4. **Technology Stack** - with known CVEs
5. **Sensitive Files Discovered** - from archives, code repos
6. **Recommended Attack Vectors** - based on findings

