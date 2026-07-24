# Modern Application, API, Cloud & Infrastructure Security (current practice)

Purpose: dense, actionable reference for a security-audit coding agent. Focus is **current** practice (2023–2026). Every factual claim traces to a source URL that was actually fetched — cited inline. A closing **FORWARD-LOOKING** section is clearly separated as anticipation, not documented fact.

Conventions: `DETECT` = what to grep/look for in code/config; `TEST` = how to verify dynamically; `FIX` = remediation; `TOOL` = open-source automation with exact invocation. Cross-platform notes given where invocation differs (macOS/Linux/Windows).

---

## 0. Standards landscape (current)

- The OWASP Top 10 was re-cut in **2021** and again in **2025** (released Jan 2026). Supply chain and misconfiguration rose sharply; SSRF became its own 2021 category and was folded back into Broken Access Control in 2025. Source: https://owasp.org/Top10/2025/0x00_2025-Introduction/
- A dedicated **OWASP API Security Top 10** exists (2019, refreshed **2023**) — object/function-level authorization dominate. Source: https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- **OWASP ASVS 5.0** shipped 2025-05-30 with a re-organized 14-chapter structure. Source: https://owasp.org/www-project-application-security-verification-standard/
- **Supply-chain security** is first-class: SBOM (SPDX/CycloneDX), SLSA provenance, dependency confusion, signature/provenance verification. Sources: https://slsa.dev/spec/v1.0/levels ; https://cyclonedx.org/
- **LLM/AI app security** is its own domain with a dedicated OWASP Top 10. Source: https://genai.owasp.org/llm-top-10/

---

## 1. OWASP Top 10 (2021) — full list, detect + fix

Source list & names: https://owasp.org/Top10/2021/ . Prevention guidance below distilled from the same project.

**A01:2021 Broken Access Control** (#1). Missing/incorrect enforcement of who can do what — IDOR, path traversal, forced browsing, privilege escalation, JWT/cookie tampering, CORS misconfig.
- DETECT: object IDs taken straight from request and used in a query without an ownership check (`findById(req.params.id)` with no `WHERE owner = currentUser`); admin routes gated only by hidden UI; `@PreAuthorize`/middleware absent on some routes.
- TEST: swap resource IDs between two low-priv accounts; call admin endpoints as a normal user; remove/alter role claims.
- FIX: deny-by-default; enforce authz server-side on every request; centralize checks; log failures. (https://owasp.org/Top10/2021/)

**A02:2021 Cryptographic Failures** (was "Sensitive Data Exposure"). Missing encryption, weak algorithms, hardcoded/weak keys, plaintext transport.
- DETECT: MD5/SHA1 for passwords, ECB mode, hardcoded keys/IVs, `http://` internal endpoints, no TLS enforcement, unsalted hashes.
- FIX: classify data; encrypt in transit (TLS 1.2+/1.3) and at rest; use argon2/bcrypt/scrypt for passwords; authenticated encryption (AES-GCM); no legacy protocols. (https://owasp.org/Top10/2021/)

**A03:2021 Injection** (now includes XSS). SQLi, NoSQLi, OS command, LDAP, ORM, XSS.
- DETECT: string-concatenated queries, `eval`, `exec`, `child_process.exec`/`os.system` with user input, template rendering of untrusted data without escaping.
- FIX: parameterized queries/prepared statements, ORM safe APIs, input validation (allowlist), context-aware output encoding, safe libraries. (https://owasp.org/Top10/2021/)

**A04:2021 Insecure Design** (new in 2021). Missing/ineffective control design — threat modeling gap, not an implementation bug.
- FIX: threat modeling, secure design patterns, reference architectures, misuse-case tests, secure-by-default. (https://owasp.org/Top10/2021/)

**A05:2021 Security Misconfiguration** (now includes XXE). Default creds, verbose errors, unnecessary features, missing hardening/headers.
- DETECT: debug mode in prod, default admin accounts, directory listing, missing security headers, permissive cloud/storage ACLs, XML parsers with external entities enabled.
- FIX: hardened repeatable build, minimal footprint, disable XXE (`disallow-doctype`), automated config verification. (https://owasp.org/Top10/2021/)

**A06:2021 Vulnerable and Outdated Components.** Known-CVE dependencies/OS packages.
- DETECT/TOOL: `npm audit`, `osv-scanner -r .`, `trivy fs .`, `grype dir:.` (see §3).
- FIX: inventory (SBOM), patch cadence, remove unused deps, monitor advisories. (https://owasp.org/Top10/2021/)

**A07:2021 Identification and Authentication Failures.** Credential stuffing, weak/absent MFA, weak session mgmt, exposed session IDs.
- FIX: MFA, no default creds, weak-password checks (breached-password lists), rate limiting, secure session IDs, server-side session invalidation. (https://owasp.org/Top10/2021/)

**A08:2021 Software and Data Integrity Failures** (new). Unsigned updates, insecure deserialization, untrusted CI/CD, unverified plugins.
- DETECT: `pickle.loads`/`ObjectInputStream`/`unserialize()` on untrusted data; auto-update without signature verification; untrusted CDN scripts without SRI.
- FIX: verify signatures/SLSA provenance, use SRI, review CI/CD trust, avoid native deserialization of untrusted input. (https://owasp.org/Top10/2021/)

**A09:2021 Security Logging and Monitoring Failures.** No/insufficient logging of auth, access-control, and input-validation failures; no alerting.
- FIX: log security events with context, protect log integrity, centralize, alert, incident-response plan. (https://owasp.org/Top10/2021/)

**A10:2021 Server-Side Request Forgery (SSRF)** (new, community vote). App fetches a user-supplied URL without validation. See §8 for cloud-metadata exploitation.
- DETECT: `requests.get(user_url)`, image/URL fetchers, webhook/callback features, PDF/SVG renderers.
- FIX: allowlist hosts/schemes, block private/link-local ranges (169.254.0.0/16, 127.0.0.0/8, 10/8, 172.16/12, 192.168/16, `::1`, `fd00::/8`), disable redirects, no raw responses to client. (https://owasp.org/Top10/2021/)

### OWASP Top 10 **2025** deltas (released Jan 2026)
Source: https://owasp.org/Top10/2025/0x00_2025-Introduction/
1. A01 Broken Access Control (still #1; **SSRF folded in here**)
2. A02 Security Misconfiguration (up from #5)
3. **A03 Software Supply Chain Failures** (NEW — expands 2021's "Vulnerable & Outdated Components" to build systems + distribution)
4. A04 Cryptographic Failures (was A02)
5. A05 Injection (was A03)
6. A06 Insecure Design (was A04)
7. A07 Authentication Failures (renamed)
8. A08 Software or Data Integrity Failures
9. A09 Security Logging & Alerting Failures (renamed; "monitoring"→"alerting")
10. **A10 Mishandling of Exceptional Conditions** (NEW — 24 CWEs: improper error handling, failing open, logic errors)

Audit guidance: treat supply-chain (§3) and misconfig (§6) as top-weight; SSRF checks belong under access control now.

---

## 2. OWASP API Security Top 10 (2023)

Full list & one-liners: https://owasp.org/API-Security/editions/2023/en/0x11-t10/

- **API1:2023 Broken Object Level Authorization (BOLA)** — the #1 API bug. Endpoint takes an object id, no per-object ownership check. DETECT: `/orders/{id}` returns any user's order. TEST: iterate IDs across accounts. FIX: check object ownership on every access using session identity, not client-supplied id.
- **API2:2023 Broken Authentication** — weak token issuance/validation. DETECT: no expiry, weak JWT secret, no rate limit on login/OTP. FIX: standard auth, short-lived tokens, MFA.
- **API3:2023 Broken Object Property Level Authorization** — merges *excessive data exposure* + *mass assignment*. DETECT: serializer returns whole object incl. `isAdmin`/`balance`; `Model(**request.json)` binds arbitrary fields. FIX: explicit field allowlists in and out.
- **API4:2023 Unrestricted Resource Consumption** — no rate/size/timeout limits → DoS or cost blow-up. FIX: rate limiting, payload size caps, pagination limits, timeouts, spend alerts.
- **API5:2023 Broken Function Level Authorization** — regular user reaches admin functions. TEST: call admin verbs/paths as low-priv. FIX: deny-by-default per function/role.
- **API6:2023 Unrestricted Access to Sensitive Business Flows** — automatable business abuse (bulk purchase, scalping, spam). FIX: bot/anti-automation controls, device fingerprinting, flow rate limits.
- **API7:2023 Server Side Request Forgery** — see §1 A10 / §8.
- **API8:2023 Security Misconfiguration** — see §1 A05, §6.
- **API9:2023 Improper Inventory Management** — undocumented/old/`/v1`/staging endpoints exposed. DETECT: shadow/zombie APIs, `/debug`, deprecated versions live. FIX: API inventory, retire old versions, environment segregation.
- **API10:2023 Unsafe Consumption of APIs** — trusting third-party API responses without validation. FIX: validate/sanitize upstream data, TLS, allowlist redirects.

---

## 3. Supply-chain / dependency security

### SBOM
- **CycloneDX** (OWASP, now **ECMA-424**) — full-stack BOM: components, dependencies, plus VEX (Vulnerability Exploitability eXchange), SaaSBOM, HBOM, CBOM (crypto), AI/ML-BOM. Source: https://cyclonedx.org/
- **SPDX** — ISO/IEC 5962:2021, emphasis on licensing + component identification. Source (comparison): https://cyclonedx.org/about/overview/ *(fetched intro variant returned 404; overview + main page corroborate)*
- Why: rapid "am I affected by CVE-X?" lookups + provenance tracking across the dependency landscape (https://cyclonedx.org/).
- TOOL: `syft <image_or_dir> -o spdx-json` / `-o cyclonedx-json` generates SBOM; `trivy sbom` / `osv-scanner` consume it (see below).
- AUDIT: an SBOM is only useful if it is (a) generated per build, (b) stored/attached to the artifact, and (c) fed to a scanner on a schedule (not just at build time — new CVEs land against old artifacts). Flag repos that generate an SBOM but never re-scan it.

### Artifact signing & provenance verification
- **Sigstore / cosign** — keyless signing of container images + attestations. Verify at deploy: `cosign verify --certificate-identity=<id> --certificate-oidc-issuer=<issuer> <image>`; verify SLSA provenance attestation: `cosign verify-attestation --type slsaprovenance ...`.
- **GitHub artifact attestations** — `gh attestation verify <artifact> --repo owner/repo` checks build provenance signed by GitHub's Fulcio identity.
- AUDIT: verification must **fail closed** — a `|| true`, a TOFU (trust-on-first-use) fallback, or unpinned `--certificate-identity` regex that matches any repo defeats the control.

### SLSA (build provenance)
Source: https://slsa.dev/spec/v1.0/levels — single **Build track**, levels L0–L3.
- **Build L0**: no guarantees.
- **Build L1**: provenance exists (how it was built) but may be incomplete/unsigned; enables inventory + debugging.
- **Build L2**: builds run on a **hosted** platform that **generates and signs** provenance; prevents post-build tampering.
- **Build L3**: **hardened** builds — runs isolated from each other; signing secrets inaccessible to user-defined build steps.
- AUDIT: check that release artifacts carry signed provenance (e.g. GitHub Actions attestations / cosign); L2+ requires a hosted signer, not a laptop.

### Dependency confusion
Source: https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610
- Mechanism: attacker publishes a package with your **internal name** and a **higher version** to a public registry (npm/PyPI/RubyGems). Installers using mixed indexes pull the public higher-versioned one → RCE via install scripts. Affected 35+ orgs incl. Apple/Microsoft/PayPal.
- Root causes: `pip install --extra-index-url` (checks both, picks higher version), `gem install --source`, mixed "virtual repositories".
- DETECT: internal package names not scoped/namespaced; `.npmrc` without scope→registry binding; `--extra-index-url` pointing at public PyPI alongside private.
- FIX: use scopes/namespaces bound to your private registry (`@myorg/pkg` → `@myorg:registry=https://...`); reserve internal names on public registries; pin versions via lockfiles; prefer `--index-url` (single) over `--extra-index-url`; verify integrity.

### Typosquatting
- DETECT: dependencies whose names are one edit-distance from a popular package (`reqeusts`, `crossenv`, `lodahs`); recently-published packages with few downloads pulled transitively.
- FIX: lockfile review, install-script auditing, `npm ci` (not `npm install`) in CI, allowlists.

### Lockfile integrity
- `package-lock.json`/`yarn.lock`/`poetry.lock`/`Cargo.lock` pin exact versions + integrity hashes. Use `npm ci` to install exactly from lockfile and fail on drift. `npm audit` requires a lockfile by default. Source: https://docs.npmjs.com/cli/v10/commands/npm-audit

### Scanners (exact invocations)
- **npm audit** (source: https://docs.npmjs.com/cli/v10/commands/npm-audit):
  - `npm audit` / `npm audit --json`
  - `npm audit --audit-level=high` (CI gate: exit non-zero only at/above severity)
  - `npm audit fix` (auto-bump compatible), `npm audit fix --force` (allows semver-major)
  - `npm audit signatures` — verifies registry **ECDSA signatures + provenance attestations** (supply-chain integrity, not CVEs)
- **OSV-Scanner** (Google frontend to OSV.dev open advisory DB; source: https://google.github.io/osv-scanner/):
  - `osv-scanner -r .` (recursive), `osv-scanner --lockfile=package-lock.json`, SBOM + container image scanning; `--format sarif|json`. Advantage: open, authoritative, machine-readable affected-version ranges.
- **Trivy** (source: https://trivy.dev/latest/docs/):
  - `trivy fs .` (deps + secrets + misconfig in a repo), `trivy image nginx:latest`, `trivy repo <url>`, `trivy sbom sbom.json`, `trivy k8s`.
  - `trivy image --severity HIGH,CRITICAL --exit-code 1 --format sarif -o results.sarif nginx:latest`
  - scanner selection: `--scanners vuln,secret,misconfig,license`
- **Grype** (Anchore; source: https://github.com/anchore/grype):
  - `grype alpine:latest`, `grype dir:.`, `grype sbom:./sbom.json` (or `cat sbom.json | grype`); `-o sarif|json|table`; `--fail-on high`. Supports EPSS/KEV risk prioritization + OpenVEX filtering. Pairs with `syft` for SBOM.
- Snyk-oss (`snyk test`, `snyk monitor`) — freemium, DB not fully open; prefer OSV/Trivy/Grype for pure OSS pipelines.

---

## 4. Secrets detection

### gitleaks
Source: https://github.com/gitleaks/gitleaks
- `gitleaks git <path>` — scans git history via `git log -p` patches; `--log-opts` limits commit range.
- `gitleaks dir <path>` (a.k.a. `gitleaks files`) — scans working tree / individual files (no git needed).
- `cat file | gitleaks stdin` — stream scan.
- Output: `--report-format json|csv|junit|sarif|template`, `--report-path`.
- Baselines: `--baseline-path` compares against a prior report, ignoring known findings.
- Inline suppression: `#gitleaks:allow` comment on a known test secret.
- Pre-commit hook (`.pre-commit-config.yaml`): repo `https://github.com/gitleaks/gitleaks`, `rev: v8.24.2`, `id: gitleaks`.
- Detection = **regex + Shannon entropy** (threshold ~3.5+) + keyword pre-filter + path rules; emits fingerprints for baseline tracking.

### trufflehog
Source: https://github.com/trufflesecurity/trufflehog
- `trufflehog git https://github.com/user/repo`
- `trufflehog github --repo=https://github.com/user/repo`
- `trufflehog filesystem path/`, `trufflehog s3 --bucket=name`, `trufflehog docker --image name`
- `--results=verified` (only API-confirmed live creds); `--results=verified,unknown` for more.
- Differentiator: **live verification** — e.g. AWS keys trigger `GetCallerIdentity` to confirm validity. Categories: Verified / Unverified / Unknown. Kills false positives.

### Common leak vectors to grep
- `.env`, `.env.*` committed; `config.json`/`settings.py` with inline keys; `AKIA[0-9A-Z]{16}` (AWS access key), `-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----`, `ghp_`/`github_pat_` tokens, `xox[baprs]-` (Slack), `sk-` (OpenAI-style), high-entropy strings assigned to `password|secret|token|apikey`.
- CI logs echoing secrets; Docker `ENV`/`ARG` with secrets baked into layers (`docker history` reveals them); frontend bundles shipping server keys.

---

## 5. SAST / DAST open-source tooling (exact invocations)

### Semgrep (SAST, multi-language)
Source: https://docs.semgrep.dev/cli-reference
- `semgrep scan --config auto .` — auto-fetches registry rules for the project.
- Registry rulesets via `--config "p/<ruleset>"`; confirmed IDs include `p/default`, `p/python`; chain multiple: `semgrep scan --config p/python --config myrules/`. Other commonly-used security rulesets by name: `p/owasp-top-ten`, `p/security-audit`, `p/secrets`, `p/ci` *(names are the well-known registry slugs; only `p/default`/`p/python` appear verbatim in the fetched CLI docs — verify a slug against the registry before relying on it)*.
- Output: `--json --output results.json`; `--sarif --sarif-output results.sarif`; also `--gitlab-sast`, `--junit-xml`.
- Diff-aware: `--baseline-commit <SHA>` shows only findings absent at that commit.
- CI: `semgrep ci` (uses org policy, non-zero exit on findings by default). Gates: `--error`, `--strict`.
- Useful: `--exclude=PATTERN`, `--include=PATTERN`, `--exclude-rule=ID`, `--dataflow-traces`, `--autofix` (pair with `--dryrun`).

### CodeQL (SAST, semantic query engine)
Source: https://docs.github.com/code-security/codeql-cli/getting-started-with-the-codeql-cli/ (page is a hub; commands below are the standard CodeQL CLI flow)
- `codeql database create <db> --language=javascript` (also python, java, csharp, cpp, go, ruby, swift, kotlin).
- `codeql database analyze <db> <lang>-security-extended.qls --format=sarif-latest --output=results.sarif` — query suites: `security-extended`, `security-and-quality` (broader, more noise).
- Best for deep dataflow/taint analysis; heavier than Semgrep. Free for public repos / research.

### ZAP (DAST)
Source: https://www.zaproxy.org/docs/docker/about/
- **Baseline** (`zap-baseline.py`) — spider (default 1 min) + optional AJAX spider, then **passive** scan only. Safe for CI against prod-like. `docker run -t zaproxy/zap-weekly zap-baseline.py -t http://target`
- **Full** (`zap-full-scan.py`) — spider (no time limit) + AJAX + **active** attack scan. Intrusive; non-prod only. `docker run -t zaproxy/zap-weekly zap-full-scan.py -t http://target`
- **API** (`zap-api-scan.py`) — active scan driven by an OpenAPI/GraphQL definition (file or URL).
- **Automation Framework** — single YAML orchestrates jobs: `docker run -v $(pwd):/zap/wrk/:rw -t zaproxy/zap-stable zap.sh -cmd -autorun /zap/wrk/zap.yaml`. (Windows: use `%cd%` in cmd or `${PWD}` in PowerShell for the volume mount.)

### nuclei (DAST / template-based)
Source: https://docs.projectdiscovery.io/tools/nuclei/overview
- Templates = YAML describing a check (matchers, severity, tags); **workflows** chain templates for multi-step detection.
- `nuclei -u https://target` (single), `nuclei -l targets.txt` (list), `nuclei -t <templates>`.
- Filters: `-tags cve`, `-severity critical,high`. Output: `-json` (structured). Great for known-CVE + misconfig sweeps of live hosts.
- Keep templates fresh: `nuclei -update-templates` before a run (new CVE templates land constantly). Combine: `nuclei -l hosts.txt -tags cve,misconfig -severity critical,high -json -o out.json`.

### SARIF as the lingua franca
All of Semgrep, CodeQL, Trivy, Grype, gosec, Bandit, Checkov emit **SARIF** (`--sarif` / `-f sarif` / `--format sarif`). Aggregate SARIF into GitHub code scanning (`github/codeql-action/upload-sarif`) or a dashboard so findings dedupe across tools. Prefer SARIF over per-tool JSON for the KB's normalized findings store.

### Trivy (also DAST-adjacent config/misconfig) — see §3 / §6.

### Language-specific SAST
- **Bandit** (Python; source: https://bandit.readthedocs.io/en/latest/): builds AST, runs plugins. `bandit -r .`; `-ll` (report medium+high only); `-f json|sarif`; `-c config`; `-s B105,B602` (skip). Sample tests: **B105** hardcoded password, **B602** `subprocess(shell=True)`, **B303** MD5, **B501** requests `verify=False`.
- **gosec** (Go; source: https://github.com/securego/gosec): scans Go AST + SSA + taint. `gosec ./...`; `-fmt sarif -out results.sarif`; `-severity medium`; `-confidence medium`; `-include=G101,G402`; `-exclude=G104`. Rules: **G101** hardcoded creds, **G104** unhandled errors, **G204** subprocess w/ user input, **G402** TLS `InsecureSkipVerify`, **G501** weak crypto. Exit 1 on findings (`-no-fail` to override).

---

## 6. Container / IaC security

### Dockerfile / runtime hardening
Source: https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
- **Non-root user**: `RUN groupadd -r app && useradd -r -g app app` then `USER app`.
- **Drop capabilities**: `docker run --cap-drop all --cap-add CHOWN <img>` (add back only what's needed).
- **Never `--privileged`** (grants all kernel capabilities).
- **Read-only rootfs**: `docker run --read-only --tmpfs /tmp <img>` (compose: `read_only: true`).
- **No privilege escalation**: `docker run --security-opt=no-new-privileges <img>`.
- **Resource limits**: `--memory 512m --cpus 0.5` (and `--pids-limit` to cap fork bombs).
- **seccomp/AppArmor** profiles; avoid sharing host namespaces (`--pid=host`, `--net=host`).
- **Minimal pinned base images** (distroless/alpine, pinned by digest); **multi-stage builds** to drop build tooling; **no secrets in image** (use Docker secrets / runtime injection — `docker history` and layer inspection leak baked-in `ENV`/`ARG`).
- Integrate image scanning (Trivy/Grype) in CI.

### IaC / config misconfiguration scanning
- **Trivy config** (source: https://trivy.dev/latest/docs/): `trivy config ./terraform/`, `trivy config Dockerfile`, `trivy config --scanners misconfig ./k8s/`. Covers Docker, Terraform, Kubernetes, CloudFormation, Helm. Add `--severity HIGH,CRITICAL --format sarif`.
- **Checkov** (source: https://www.checkov.io/1.Welcome/What%20is%20Checkov.html): 750+ policies. Frameworks: Terraform (AWS/GCP/Azure/OCI), CloudFormation/SAM, ARM, Serverless, Helm, Kubernetes, Docker.
  - `checkov -d .` (dir), `checkov -f main.tf` (file), `checkov -d . --framework terraform`, `--check CKV_AWS_1`, `--skip-check CKV_AWS_1`, `--output sarif`, `--compact`.
- Common misconfigs to flag: public S3/GCS buckets, `0.0.0.0/0` ingress on SSH/RDP, unencrypted volumes/RDS, IAM `*:*` wildcards, K8s pods running as root / `privileged: true` / `hostNetwork: true` / missing `securityContext`, K8s Secrets in plaintext env, no resource limits, `latest` image tags.

### Terraform — concrete patterns to grep / flag
- `ingress { cidr_blocks = ["0.0.0.0/0"] from_port = 22 }` (open SSH) — Checkov CKV_AWS_24 family.
- `acl = "public-read"` / missing `aws_s3_bucket_public_access_block`.
- `server_side_encryption` absent on S3/EBS/RDS; `storage_encrypted = false`.
- IAM policy `"Action": "*", "Resource": "*"` / `"Principal": "*"`.
- Secrets in `.tf` / `terraform.tfvars` committed (feed to gitleaks too).
- `enable_key_rotation = false`, security groups with `protocol = "-1"`.

### Kubernetes — manifest hardening (`securityContext`)
- Pod/container should set: `runAsNonRoot: true`, `runAsUser: <non-0>`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, `privileged: false`, `capabilities: { drop: ["ALL"] }`, `seccompProfile: { type: RuntimeDefault }`.
- Flag: `hostNetwork/hostPID/hostIPC: true`, `hostPath` volume mounts, missing `resources.limits`, default ServiceAccount token auto-mounted (`automountServiceAccountToken: true`), no NetworkPolicy, image by tag not digest.
- TOOL: `trivy config ./k8s/` and `checkov -d ./k8s/ --framework kubernetes`; also `kube-bench` (CIS) and `kube-linter lint .`.

---

## 7. Modern authentication

### OAuth 2.0 / OIDC pitfalls
Source: https://portswigger.net/web-security/oauth
- **redirect_uri validation flaws** → code/token theft, account takeover. TEST: append path/query/fragment, try subdomains, `localhost`, traversal (`/callback/../../evil`), and `https://good.com&@evil.com#@evil.com`. FIX: **exact** allowlist match on BOTH authorization and token-exchange endpoints; no substring/prefix matching.
- **Missing/weak `state`** → CSRF / login-CSRF. TEST: drop `state`, replay a fixed value. FIX: unguessable per-session `state`, validated on callback.
- **Leaked authorization codes** via open redirect on a whitelisted domain, XSS, or `Referer` header. FIX: strict redirect_uri + **PKCE** binds the code to the requester + server-to-server token exchange.
- **Implicit flow** exposes access tokens in URL fragments. FIX: use authorization **code flow + PKCE**; avoid implicit.
- **Missing PKCE** (RFC 7636) on public/native clients → code interception. TEST: check request for `code_challenge`, token exchange for `code_verifier`. FIX: mandate PKCE, `S256` (not `plain`), unique verifier per request.
- Recon: `/.well-known/openid-configuration`, `/.well-known/oauth-authorization-server`.

### JWT attacks
Source: https://portswigger.net/web-security/jwt/algorithm-confusion
- **Algorithm confusion (RS256→HS256)**: server verifies with a generic `verify()` given the RSA **public** key; attacker sets `alg:HS256` and HMAC-signs the token using the public key as the secret → forged token validates. Steps: grab public key (`/jwks.json` or derive via `sig2n`), convert to PEM, edit claims, HS256-sign with it.
- **`alg:none`**: server accepts unsigned tokens.
- **Weak HMAC secret**: brute-force/dictionary the signing secret offline — `hashcat -m 16500 jwt.txt wordlist.txt` (mode 16500 = JWT). Any guessable secret (`secret`, `changeme`, app name) is game over.
- **`kid` header injection**: `kid` used in a path/SQL lookup for the key → path traversal (`../../dev/null`) or SQLi to control the verification key. FIX: treat `kid` as untrusted; look up keys from a fixed map.
- DETECT (code): a verify call without an explicit algorithm allowlist; same key material used for asymmetric verify passed to a symmetric-capable API; `alg` read from the token to choose the verifier.
- TEST: Burp JWT Editor — flip `alg`, try `none`, resign.
- FIX: **explicit algorithm allowlist** (pin to exactly the expected alg); separate keys per algorithm; reject `none`; strong random secrets for HMAC; verify `iss`/`aud`/`exp`.

### Session / cookie flags
- `HttpOnly` (no JS access → XSS can't steal), `Secure` (HTTPS only), `SameSite=Lax` default / `Strict` for sensitive / `None; Secure` only for legit cross-site. `__Host-` prefix for host-locked cookies. Short expiry + server-side invalidation on logout.

### CORS misconfiguration
Source: https://portswigger.net/web-security/cors
- **Reflecting arbitrary `Origin` with `Access-Control-Allow-Credentials: true`** → attacker page reads authenticated responses (API keys, CSRF tokens). Worst case.
- **Trusting `null` origin** → sandboxed iframe sends `Origin: null` to bypass.
- **Weak allowlist matching**: suffix (`endsWith("normal-website.com")` → `evilnormal-website.com`) or prefix (`startsWith` → `normal-website.com.evil.net`).
- **Trust-all-subdomains** → any subdomain XSS pivots to parent data.
- TEST: send arbitrary/`null`/`sub.attacker` origins; check reflected `Access-Control-Allow-Origin` + credentials flag. FIX: hardcoded explicit origin allowlist; never reflect; never combine wildcard with credentials; CORS is not a server-side authz replacement.

### CSRF (modern state)
Source: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- Primary: **synchronizer token** (stateful) or **signed double-submit cookie** (stateless, HMAC bound to session — plain double-submit is weak).
- Layer: **SameSite** cookies (Lax blocks cross-site unsafe methods but NOT state-changing GETs — so never mutate state on GET), custom request headers for JSON APIs (subject to same-origin policy), Origin/Referer validation.
- Caveat: **XSS defeats all CSRF defenses** — fix XSS too.

---

## 8. Cloud / deployment

### SSRF + cloud metadata (IMDS)
Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- Classic SSRF target: `http://169.254.169.254/latest/meta-data/` (AWS), which under IAM role exposes temporary credentials (`/latest/meta-data/iam/security-credentials/<role>`). IPv6 IMDS: `[fd00:ec2::254]`.
- **IMDSv1** = plain GET (request/response) — trivially reachable via SSRF.
- **IMDSv2** = session-oriented. Get token then use it:
  ```
  TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
  curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/
  ```
  Windows PowerShell:
  ```
  [string]$token = Invoke-RestMethod -Headers @{"X-aws-ec2-metadata-token-ttl-seconds"="21600"} -Method PUT -Uri http://169.254.169.254/latest/api/token
  Invoke-RestMethod -Headers @{"X-aws-ec2-metadata-token"=$token} -Method GET -Uri http://169.254.169.254/latest/meta-data/
  ```
- Why IMDSv2 blocks SSRF: requires a **PUT** to mint a token (most SSRF primitives only do GET), `PUT` is **rejected if it carries `X-Forwarded-For`** (blocks reverse-proxy SSRF), and the response **hop limit defaults to 1** (blocks container-to-IMDS pivots unless raised).
- FIX/AUDIT: enforce IMDSv2 required (`HttpTokens=required` via `modify-instance-metadata-options`); set hop limit deliberately; app-side SSRF allowlist still required.
- GCP metadata: `http://metadata.google.internal/` requires `Metadata-Flavor: Google` header (similar mitigation); Azure IMDS: `http://169.254.169.254/metadata/instance?api-version=...` requires `Metadata: true`.

### Exposed buckets
- DETECT: public-read/public-write S3/GCS/Azure Blob ACLs, missing bucket policies, `Block Public Access` disabled. TOOL: Trivy/Checkov IaC scan; `aws s3api get-bucket-policy-status`.

### Security response headers
Source: https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html
- `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
- `Content-Security-Policy: ...` (tailor; prefer nonce/hash over `unsafe-inline`; set `frame-ancestors`)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY` (or CSP `frame-ancestors 'none'`)
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), camera=(), microphone=()`
- `Cross-Origin-Opener-Policy: same-origin`, `Cross-Origin-Embedder-Policy: require-corp`, `Cross-Origin-Resource-Policy: same-site`

### TLS configuration
Source: https://github.com/testssl/testssl.sh
- `testssl.sh https://host` — checks protocols (flag SSLv3/TLS1.0/1.1 as weak; want TLS1.2+/1.3), cipher suites, known vulns (Heartbleed, ROBOT, etc.), certificate validity, and security headers.
- Useful flags: `--severity <LOW|MEDIUM|HIGH>`, `--protocols`, `--vulnerable`, `--jsonfile out.json` (also CSV/HTML). Cross-platform: Linux/macOS/FreeBSD native, Windows via WSL2/MSYS2, or Docker. Alternative: **sslyze** (`sslyze host:443 --json_out out.json`).

---

## 9. CI/CD security

Source: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- **Script injection**: never interpolate untrusted `${{ github.event.* }}` (PR title/body/branch) directly into `run:`. FIX: pass via `env:` and reference as a shell variable, or use a JS action that takes the value as an argument.
  ```yaml
  - env:
      TITLE: ${{ github.event.pull_request.title }}
    run: |
      echo "$TITLE"   # safe: value is data, not injected into script text
  ```
- **Pin actions to full commit SHA** (only immutable reference): `uses: owner/action@<40-char-sha>` — tags can be moved to inject backdoors. Enforce org-wide policy.
- **Minimize `GITHUB_TOKEN`**: set default to read-only (`permissions: contents: read`), elevate per-job as needed.
- **OIDC to cloud** instead of long-lived secrets: exchange a short-lived OIDC token for cloud creds (`permissions: id-token: write` + `aws-actions/configure-aws-credentials` with `role-to-assume`). No stored AWS keys.
- **`pull_request_target` danger**: runs privileged, shares main-branch cache, can hold write access + secrets. Don't check out/execute untrusted PR code under it; prefer `workflow_run` for privilege separation, or the safer `pull_request` trigger.
- Also: least-privilege deploy creds, review third-party action source, avoid `curl | bash` in pipelines, scan IaC/images in the pipeline (§3/§6).

---

## 10. Emerging (2024–2026) — OBSERVED

### OWASP Top 10 for LLM Applications (2025)
Source: https://genai.owasp.org/llm-top-10/
- **LLM01 Prompt Injection** — user/embedded input overrides intended instructions (direct + indirect via retrieved content). DETECT: untrusted text concatenated into prompts; tool-calling LLM acting on retrieved web/doc content. FIX: separate system/user channels, input/output filtering, least-privilege tools, human-in-loop for high-impact actions, treat all model output as untrusted.
- **LLM02 Sensitive Information Disclosure** — model leaks secrets/PII/training data. FIX: data minimization, output scrubbing, no secrets in prompts/system messages.
- **LLM03 Supply Chain** — poisoned models/datasets/plugins from hubs. FIX: verify model provenance/signatures, pin versions, scan (§3).
- **LLM04 Data and Model Poisoning** — malicious training/fine-tune/embedding data.
- **LLM05 Improper Output Handling** — passing model output unsanitized to shells/SQL/HTML/`eval` → classic injection downstream. FIX: encode/validate model output like any untrusted input.
- **LLM06 Excessive Agency** — over-broad tool/permission grants to agents. FIX: minimal scopes, approval gates, deny-by-default tools.
- **LLM07 System Prompt Leakage** — hidden instructions extracted; don't put secrets/authz logic in system prompts.
- **LLM08 Vector and Embedding Weaknesses** — RAG store poisoning / embedding-inversion / cross-tenant leakage. FIX: tenant isolation, access control on vector DB, validate ingested docs.
- **LLM09 Misinformation** — hallucinated/false output relied upon. FIX: grounding, citations, human review.
- **LLM10 Unbounded Consumption** — token/cost DoS, model extraction. FIX: rate/spend limits, quotas, output caps.

### API abuse & recent attack classes (OBSERVED)
- Automated business-flow abuse (API6:2023) — scalping, credential stuffing, inventory-hoarding bots. https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- Supply-chain compromise as a top-tier category (OWASP 2025 A03) reflecting real build-system/distribution attacks. https://owasp.org/Top10/2025/0x00_2025-Introduction/
- "Mishandling of Exceptional Conditions" (OWASP 2025 A10) — fail-open logic, unhandled errors leaking state, 24 CWEs. https://owasp.org/Top10/2025/0x00_2025-Introduction/

---

## FORWARD-LOOKING ANTICIPATION (not documented fact — reasoned extrapolation)

Clearly labeled predictions for a coding agent to watch for. These are **not** sourced claims; treat as hypotheses to test, not established vulnerabilities.

- **Agentic-AI privilege chaining**: as coding/ops agents get shell + cloud creds, indirect prompt injection in a fetched file/issue/dependency README could steer the agent into running attacker commands. Anticipated defense: capability sandboxing, per-action allowlists, provenance tags on any text an agent ingests, and "untrusted content" fencing in agent context. (Extends LLM01/LLM06.)
- **MCP / tool-server supply chain**: third-party Model Context Protocol servers become a new dependency class — expect typosquatted/over-permissioned MCP servers exfiltrating context. Anticipated control: MCP server allowlists, signed manifests, scoped tokens.
- **AI-assisted dependency confusion at scale**: LLMs "hallucinating" plausible-but-nonexistent package names ("slopsquatting"), which attackers pre-register on public registries. Anticipated control: verify every suggested dependency exists + is reputable before install; lockfile-first.
- **Post-quantum crypto migration gaps**: as PQC standards (ML-KEM/ML-DSA) roll out, hybrid/misconfigured deployments and "harvest-now-decrypt-later" exposure of today's RSA/ECC traffic. Anticipated audit item: inventory crypto (CBOM) and flag long-lived secrets protected only by classical KEX.
- **Provenance-verification bypass**: as SLSA/sigstore adoption grows, attackers target the verification step (unverified fallback paths, TOFU on first pull, misconfigured `cosign verify` policies). Anticipated control: fail-closed verification, no silent fallback.
- **CI/CD OIDC trust-policy misconfig**: overly broad `sub`/`aud` claim matching in cloud trust policies letting any repo/branch assume a role. Anticipated audit: pin OIDC subject to exact repo+branch+environment.

---

## Quick audit checklist (agent cheat-sheet)

1. Dependencies: `osv-scanner -r .` + `npm audit --audit-level=high` + `trivy fs .`; verify lockfiles + `npm audit signatures`.
2. Secrets: `gitleaks dir .` + `trufflehog filesystem . --results=verified`.
3. SAST: `semgrep ci` (or `--config auto`) + language tool (`bandit -r .`, `gosec ./...`) or CodeQL for depth.
4. Containers/IaC: `trivy config .` + `checkov -d .`; Dockerfile → non-root, drop caps, no secrets, pinned base.
5. AuthZ: object-level ownership checks (BOLA), function-level role checks, deny-by-default.
6. Auth: JWT explicit alg allowlist, OAuth exact redirect_uri + PKCE + state, cookie flags.
7. Web hardening: security headers, CORS explicit allowlist, CSRF tokens + SameSite.
8. Cloud: enforce IMDSv2, SSRF allowlists, no public buckets, TLS1.2+/1.3 (`testssl.sh`).
9. CI/CD: pin actions by SHA, least-priv `GITHUB_TOKEN`, OIDC not stored keys, no `pull_request_target` on untrusted code.
10. AI features: prompt-injection fencing, sanitize model output, least-priv tools, spend/rate limits.

## Triage notes for an automated auditor

- **Severity ≠ exploitability.** Cross-reference CVEs with **EPSS** (probability of exploitation) and **CISA KEV** (known-exploited) before ranking — Grype exposes both. A CRITICAL CVSS in an unreachable code path outranks nothing; a HIGH in KEV outranks most CRITICALs.
- **Reachability.** A vulnerable transitive dependency that is never imported/called is lower risk than a direct, called one. Prefer tools/queries that report call-path reachability (Semgrep dataflow, CodeQL) before failing a build.
- **Dedupe across tools** via SARIF ruleId + location; the same finding will surface from Trivy, Grype, and `npm audit`.
- **Suppress with provenance, not silence.** Every ignored finding (`#gitleaks:allow`, `--skip-check`, `.trivyignore`, `# nosec`, `# noqa`) should carry a reason + expiry, and the auditor should surface stale suppressions.
- **Gate, don't block dev.** Fail CI at `high`/`critical` (`--audit-level=high`, `--exit-code 1`, `-severity high`); report lower severities without breaking the build.
- **Secrets are always P0** regardless of severity heuristics — a verified live credential (trufflehog `--results=verified`) means rotate now, then remediate the leak vector.
