---
name: opsec
description: Use as pre-validation layer BEFORE any other skill. Activates when user says any security/attack/scan command. Ensures VPN is connected, user agents rotate, fingerprint is clean, and operational environment is isolated from personal identity. This runs FIRST before any other skill executes.
---

# Operational Security (OPSEC) - PRE-FLIGHT CHECKLIST

## TRIGGER RULES
**AUTOMATICALLY activates before ANY other skill when user says:** anything targeting a domain/IP or involving security testing.
This is the FIRST check - nothing runs without OPSEC validation.

---

## GOLDEN RULES (NEVER BREAK THESE)

### Rule 1: THE ORIGIN MUST NEVER BE VISIBLE - EVER
This is the single most important rule. The target must NEVER be able to trace anything back to the operator's origin country.
```yaml
❌ NEVER expose:
  - Origin timezone
  - Origin language setting
  - Origin IP addresses
  - Origin VPN exit nodes
  - Origin names, emails, phone numbers
  - Origin bank accounts or payment methods
  - Origin keyboard layout or typing patterns
  - Origin cultural references in any pretext
  - Fonts or character sets that reveal the origin OS
  - Browser history or bookmarks with origin sites
  - Any document metadata (author, company, language)

✅ ALL operations must point to a PLAUSIBLE DIFFERENT COUNTRY:
  - Choose ONE cover country per campaign
  - Every single detail must match that country
  - VPN exit → that country
  - Timezone → that country
  - Browser language → that country
  - Created accounts → names from that country
  - Emails → patterns common in that country
  - Online behavior → typical of that country's users

Good cover countries: Singapore, Malaysia, Thailand, Vietnam, Japan, South Korea,
or Western countries matching the target language
```

### Rule 1b: CONSISTENT COVER IDENTITY
Every piece of evidence must tell the SAME story:
```yaml
If your cover is "Singapore-based IT contractor":
  - VPN exit: Singapore IP (residential, not datacenter)
  - Timezone: UTC+8 (Singapore)
  - Language: en-SG, zh-SG, ms-SG
  - Names: Singaporean Chinese/Malay/Indian names
  - Email: singapore-based provider, .sg domain
  - Browser behavior: Singapore patterns
  - Working hours: Singapore business hours
  - No origin timezone, no origin language, NO ORIGIN SIGNALS
```

### Rule 2: SEPARATE IDENTITIES
```
Personal: Google account, real name, real phone, home IP, personal email
Cover ID: Fake identity matching cover country
Operational: Burner email, fake name (cover country), VPN IP, burner phone
NEVER THE THREE SHALL MEET
```

### Rule 3: ONE-USE INFRASTRUCTURE
- Each campaign/target gets NEW: VPN, email, accounts, domains
- Never reuse between targets
- Never reuse between campaigns on same target

### Rule 4: ASSUME YOU'RE WATCHED
- Everything you do creates telemetry
- The target's SOC is watching
- Your ISP/webhost logs everything
- The only question is: does your traffic look suspicious?

---

## PRE-FLIGHT CHECKLIST (RUN THESE BEFORE ANY COMMAND)

### [ ] CHECK 1: VPN STATUS

```powershell
# 1. Check current IP
$before = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing).Content
Write-Output "Current IP: $before"

# 2. Verify VPN shows different IP from origin country
# The target should see: a different country, residential IP preferred

# 3. Verify no DNS leaks
$dns = (Resolve-DnsName -Name api.ipify.org -Server 8.8.8.8).IPAddress
Write-Output "DNS resolves to: $dns"
# If DNS != your ISP's DNS, you're leaking

# 4. VPN Kill Switch: if VPN drops, block all traffic
# Windows: check if kill switch is configured in your VPN client
```

### VPN REQUIREMENTS:
- **NO free VPNs** (they log, sell data, are flagged)
- **NO known pentest VPNs** (PIA, Windscribe, Mullvad are flagged)
- **Residential IP preferred** (not datacenter IP - those are easy to block)
- **Exit in target's region or COVER country** (exiting in the origin country gives you away instantly)
- **Pay with Monero or anonymous crypto**, never personal card
- **Separate VPN per target**, never same exit node across campaigns
- **VPN provider based in COVER country** if possible, or privacy-friendly jurisdiction

### [ ] CHECK 2: BROWSER FINGERPRINT

```javascript
// Before touching target, check what browser exposes:
// https://amiunique.org or browserleaks.com

// Check these:
1. User-Agent: is it updated? recent Chrome/Firefox/Edge?
2. Screen resolution: matches your declared OS?
3. Timezone: matches your VPN exit country?
4. Language: matches your supposed location?
5. WebGL: unique fingerprint. Consider spoofing.
6. Canvas fingerprint: very unique. Consider spoofing.
7. Fonts: OS font list is unique to your machine.
8. Plugins: disable unnecessary browser plugins.
9. WebRTC: can leak real IP even behind VPN (DISABLE IT!)
10. Cookies: clear all before starting new target.
```

### [ ] CHECK 3: USER AGENT PREPARATION

```powershell
# User Agent rotation strategy:
# NEVER use the same UA twice for same target

# UA Rotation Pool (rotate through these):

$uaPool = @(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148"
)

# Pick random UA, use for this session only
$selectedUA = $uaPool | Get-Random
```

### UA Rotation Rules:
- **Rotate EVERY request** to the target
- Match UA to the tool being used (curl vs browser vs script)
- Mobile UAs for mobile endpoints
- Desktop UAs for web apps
- Never use default tool UAs (curl/7.x, python-requests, go-http-client)

---

---

## COUNTRY ATTRIBUTION COVER - THE CRITICAL DETAILS

### Why Attribution Analysis Is Your Biggest Threat

Nation-states and SOCs use **ATTRIBUTION** to identify attackers. They don't block you immediately - they watch, profile, and trace back. Every digital fingerprint tells a story:
```yaml
They check:
  🌐 IP geolocation → "Where is this person?"
  ⏰ Active hours → "What timezone do they live in?"
  🌍 Browser language → "What language do they speak?"
  ⌨️ System fonts → "What OS/language pack?"
  📧 Email patterns → "What culture/locale?"
  💳 Payment methods → "Where do they bank?"
  🧾 Domain registration → "Who are they really?"
  👤 Social media → "What is their real identity?"
```

**If ANY two signals point to the origin, attribution starts.**
**If THREE+ signals point to the origin, you are identified.**

### The Signal Map: What Your Op Reveals

| Signal | What It Tells | How It Betrays The Origin |
|--------|--------------|----------------------|
| **IP geolocation** | Country | Any origin-country IP = instant flag |
| **Timezone** | Active hours | Activity during origin-country night hours |
| **Language header** | Browser locale | Origin language code in `Accept-Language` |
| **System fonts** | OS locale | Native-script fonts in the font list |
| **Keyboard layout** | Typist's language | Origin keyboard layout |
| **Typing patterns** | Native language | Typing speed, errors, spacing characteristic of origin users |
| **Working hours** | Timezone | Activity during origin business hours for a mismatched cover |
| **Search history** | Language & region | Origin-language searches, origin ccTLD sites |
| **Payment method** | Citizenship | Origin bank card, origin payment apps |
| **Email provider** | Region | Origin-specific provider, origin ccTLD email |
| **Social media** | Real identity | Friends and posts from the origin country |
| **Code commits**| Identity | Origin name, origin timezone, origin code in profile |
| **Domain WHOIS** | Identity | Origin address, phone, email in WHOIS |
| **SSL certificate**| Organization | Origin org name in cert |
| **DNS servers** | Provider | Origin DNS hosting |
| **Content language**| Native language | Origin language in phishing pages, comments, commit messages |
| **Tools/payloads** | Signature | Tools known to be used by origin-based groups |

### The Cover Country Strategy

```yaml
For EACH campaign, choose a cover country. Then SCORCH everything else:

✅ COVER COUNTRY SIGNALS (ALL MUST MATCH):
  [✓] VPN exit in cover country (residential IP)
  [✓] Browser language = cover country's language
  [✓] Timezone = cover country's timezone
  [✓] Active hours = cover country's business hours
  [✓] Names/identities = cover country's naming conventions
  [✓] Email provider popular in cover country
  [✓] System fonts = typical for cover country OS
  [✓] Payment method from cover country
  [✓] All written content in cover country's dialect

❌ ORIGIN SIGNALS (ZERO TOLERANCE):
  [✗] NO origin-country IP (any VPN exit must be cover country)
  [✗] NO origin timezone (set system to cover country's tz)
  [✗] NO origin language (remove from browser completely)
  [✗] NO origin fonts installed on op machine
  [✗] NO origin keyboard layout on op machine
  [✗] NO writing in the origin language during any ops communication
  [✗] NO origin names in any account creation
  [✗] NO origin payment methods (cards, payment apps)
  [✗] NO origin phone numbers (even burner SIMs)
  [✗] NO origin ccTLD email domains
  [✗] NO origin social media activity during campaign
  [✗] NO origin websites in browser history
  [✗] NO origin ccTLD domains in DNS cache or history
  [✗] NO origin-language code comments or variable names
  [✗] NO origin cultural references in pretexts
```

### Cover Country Selection Guide

```yaml
Pick based on TARGET LOCATION:

Target in USA/UK/Australia:
  Cover: USA (California/New York), UK, Canada, Australia
  🚫 Do NOT use: the origin country or nearby countries

Target in Singapore/Malaysia:
  Cover: Singapore, Malaysia, Australia, UK
  🚫 Do NOT use: the origin country or nearby countries

Target in Japan/Korea:
  Cover: Japan, South Korea, USA
  🚫 Do NOT use: the origin country or nearby countries

Target in Thailand:
  Cover: Singapore, Malaysia, USA, UK
  🚫 Do NOT use: the origin country (too close, easy cross-reference)

Target in EU:
  Cover: Germany, Netherlands, France, UK, USA
  🚫 Do NOT use: the origin country or any nearby country
```

### System-Level OPSEC for Attribution Hiding

```powershell
# BEFORE ANY OPERATION, run these checks:

# 1. Check system timezone (MUST NOT be the origin timezone)
tzutil /g
# If it is the origin timezone → tzutil /s "<Cover Country Standard Time>"

# 2. Check browser languages (MUST NOT have the origin language)
# Chrome: chrome://settings/languages → only cover country languages
# Remove all origin-related languages

# 3. Check system installed languages
Get-WinUserLanguageList
# If any origin language → remove it
# $lang = Get-WinUserLanguageList | Where-Object LanguageTag -eq "<origin-lang-code>"
# $lang | ForEach-Object { $_.Remove() }

# 4. Check system locale
Get-Culture  # Must show cover country, not the origin

# 5. VPN: verify no connection originates from the origin country
(Invoke-WebRequest -Uri "https://ipinfo.io/json" -UseBasicParsing).Content
# Check: country, timezone, language fields

# 6. Browser fingerprint: test at https://browserleaks.com or https://amiunique.org
# Check: WebRTC leak, timezone, language, fonts, canvas
```

### Digital Trail Consistency (The Hardest Part)

The most common attribution failure is **SINGLE SIGNAL INCONSISTENCY**:
```yaml
You do everything right EXCEPT:
  ❌ Your GitHub commit timestamp shows origin business hours
     but your VPN says you're in the US (it's the middle of the night there)
     → Defenders: "Commit at that hour? Unusual, but maybe.
        Let's check other signals..."

  ❌ Your phishing page is in perfect English
     but WHOIS domain registered with an origin-country phone number
     → Defenders: "English page + origin phone = attribution done"

  ❌ You use US VPN, US names, US email
     but browser Accept-Language shows the origin language as primary
     → Defenders: "US VPN but origin language = just a proxy user"
```

**Every signal must tell the same story. One mismatch = attribution.**

---

## DIGITAL HYGIENE

### Browser Isolation:
- Dedicated browser profile for EACH target
- No extensions (or only essential ones like proxy switcher)
- No saved passwords
- Private/incognito mode always
- Clear everything between sessions: cache, cookies, localStorage, history

### Network Isolation:
```
[Your Machine]
     ↓
[VPN1 - entry] (residential proxy, act as anonymizing layer)
     ↓
[VPN2 - exit] (in target's region)
     ↓
[Optional: Tor] (only if speed isn't critical)
     ↓
[Target]
```

### Account/Identity Compartmentalization:

| Purpose | Email | Payment | Phone | Identity |
|---------|-------|---------|-------|----------|
| **Domain reg** | burnermail1@ | Monero | Burner SIM | Fake name |
| **VPS/VPN** | burnermail2@ | Monero | Burner SIM | Fake name |
| **Social media** | burnermail3@ | N/A | Burner | Fake persona |
| **Testing** | burnermail4@ | N/A | N/A | Fake persona |
| **Personal** | real@ | Real card | Real | REAL |

### NEVER Cross-Contaminate:
- ❌ Same email for domain purchase and social media
- ❌ Same payment method across any two ops accounts
- ❌ Log into personal accounts from ops environment
- ❌ Log into ops accounts from personal environment

---

## TOOL HYGIENE

### Curl Configuration:
Don't use default curl. It's fingerprinted by User-Agent and TLS fingerprint.

```powershell
# curl - minimal fingerprint
curl.exe --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0" --compressed -s

# Add TLS parameters to match browser
curl.exe --tlsv1.2 --tls-max 1.2 --ciphers "ECDHE-RSA-AES128-GCM-SHA256"
```

### Tool Modifications:
- **Nmap**: Use `-T2` (slow), random decoys, spoof MAC
- **Gobuster/ffuf**: Add random delays, rotate UAs, throttle requests
- **sqlmap**: Never default UA, use `--random-agent`, `--delay 2`
- **Hydra/medusa**: Never default, throttle aggressively, randomize timing

### Default Tool FPs to AVOID:
| Tool | Default FP | What to Change |
|------|-----------|---------------|
| curl | `curl/8.x.x` | Change User-Agent |
| sqlmap | `sqlmap/#.#` | `--random-agent`, `--mobile` |
| nmap | `Nmap, T4` | `-T2`, `--spoof-mac`, `-D RND:10` |
| gobuster | `gobuster/3.x` | Change UA with proxy |
| hydra | `User-Agent: hydra` | `-m` option, change UA in source |
| python | `python-requests/2.x` | Always set custom UA |

---

## COMMUNICATIONS SECURITY

### Never Discuss Operations On:
- ❌ Personal phone or messaging apps
- ❌ Your real Signal/Telegram with real identity
- ❌ Slack, Discord, Teams (corporate environments)
- ❌ Email (even encrypted email metadata is visible)
- ❌ SMS (completely insecure)

### Use For Op Comm:
- ✅ Burner Signal (burner phone number)
- ✅ Session (no phone number required, ephemeral)
- ✅ SimpleX (no identifiers at all)
- ✅ Matrix (self-hosted, encrypted)
- ✅ End-to-end encrypted + ephemeral + no metadata

---

## IF COMPROMISED: BURN PROTOCOL

### Signs You're Being Hunted:
- Target goes silent (no interaction)
- Your infrastructure becomes unreachable
- Your domains taken offline without notice
- Unusual connection attempts to your boxes
- Your C2 returns unusual responses
- Certificates revoked

### Immediate Actions:
1. **CUT ALL LINES** - kill all C2 connections NOW
2. **SHUTDOWN all infrastructure** - servers, redirectors, domains
3. **DESTROY logs** - local logs, cloud logs, infrastructure logs
4. **BURN accounts** - all burner emails, domain regs, VPS accounts
5. **ISOLATE op machine** - don't connect to anything
6. **ANALYZE how** - trace back what exposed you
7. **WAIT 3+ months** before any new operations
8. **NEVER reuse** any infrastructure, accounts, or patterns

### If Physical Raid Imminent:
- Full disk encryption (boot password, not auto-login)
- Remote wipe script ready
- Separate boot partitions (clean OS for plausible deniability)
- Op data never on personal devices
- Op comms on separate devices entirely

---

## PERSONAL / OP SEPARATION (HARD RULES)

### Absolutely Separate Hardware:
- Personal computer
- Operational computer (clean OS, no personal accounts)

### If same machine (virtual isolation):
- Dedicated VM for ops (not the host OS)
- VM has its own VPN (independent from host)
- No network bridging between host and VM
- VM DNS goes through VPN, not host
- Host has zero ops artifacts

### Absolutely Separate:
```
Personal Phone         ≠        Op Phone
Real ID Burner SIM only
Home Address Vacant address/mail drop
Real Email Burner emails only
Real Name Code name only
Physical location VPN exit to target's region
Bank/Crypto Monero only
Social media Siloed fake persona per target
```

---

## SESSION TRACKING LOG

Before starting ANY operation:

```
Cover Country: _________________  (this is who you appear to be)
Target: _________________
Date:   _________________
VPN Exit IP: _________________
VPN Exit Country: _________________
Timezone Set: _________________
Language Set: _________________
User Agent Used: _________________
Browser Fingerprint Verified: _________________
Tool Set: _________________
Op Account Used: _________________
Purpose: _________________
Burn After: _________________
```

**Log this in an encrypted file, NOT in your personal notes or cloud.**
