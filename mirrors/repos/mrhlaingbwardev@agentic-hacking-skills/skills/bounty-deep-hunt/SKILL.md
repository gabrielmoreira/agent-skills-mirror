---
name: bounty-deep-hunt
description: Use when bug bounty hunting on a live target, or whenever web-pentest / zero-day-hunting / red-team-web-methodology finishes and the AI is about to stop with "nothing found". Burmese triggers "bounty", "ဆက်ရှာ", "လက်မလျော့နဲ့", "ထပ်တူး", "မတွေ့သေးဘူး", "bug ရှာမယ်". Forces DIVERGENT thinking (not a checklist) via Cliché Purge, Artifact-Pointer Mining, Inversion Operators, Seam/Confused-Deputy mapping, and the Uniqueness Law — grounded in real 2026 Meta/Google payouts. A session ends only as FOUND (PoC) or EXHAUSTED (full ledger with evidence) — never a bare "no bugs".
---

# Bounty Deep Hunt — the Divergence Engine

> Read this first. Bounty sessions fail for two reasons, and neither is the target.
> **(1)** The AI stops early and calls "nothing found" a result.
> **(2)** Worse — it only ever generates the *ordinary* hypotheses (IDOR, plain XSS,
> admin takeover, subdomain brute force). Every hunter on earth already ran those;
> they are saturated and worth $0.
>
> This skill removes exit (1) **and** overrides the model's default prior (2) with a
> machine for producing *non-obvious* hypotheses. The checklist is not the engine;
> the engine is the Operator Deck in §3.

---

## 0. THE LAW (non-negotiable)

1. You are **FORBIDDEN** to end a session with a bare "no vulnerabilities found /
   မတွေ့ဘူး / here's what I'd check" while **any** ledger cell is `UNTESTED`.
2. **"Not found" is not a result.** It is an instruction to apply a *new* operator
   (§3) to the same surface, or to move one rung down the Ladder (§7).
3. A session ends in exactly **two** states:
   - **FOUND** — ≥1 finding with a working PoC + demonstrated impact, reproduced ≥2×.
   - **EXHAUSTED** — every ledger cell `TESTED` or `BLOCKED(reason)`, each with raw evidence; final ledger printed.
4. "I tried the obvious stuff" is **never** EXHAUSTED. Obvious stuff is the *zero point*.
5. If the user says **"ဆက်" / "continue" / "keep going"**, resume from the last ledger
   state, next operator. Never restart from zero, never re-summarise instead of hunting.

### Give-up tells — catch these in your own output and override them

| Phrase you are about to write            | What you must do instead                          |
| ---------------------------------------- | ------------------------------------------------- |
| "No vulnerabilities found"               | Print ledger → pick next `UNTESTED` cell + operator |
| "The application appears secure"         | Model invariants + seams (§2, §4) → hunt violations |
| "This is likely not exploitable"         | Actually try it; find the missing precondition (§3.1 #2) |
| "This is only self-XSS / low severity"   | **Reject the label** — hunt login-CSRF / origin confusion (§5.2) |
| "Standard checks pass"                   | Standard checks are the *baseline*, not the hunt (§1) |
| "Given the scope, I'll summarise"        | Scope is not an excuse to stop hunting            |

**Heartbeat:** every ~10 concrete tests with no finding, print the ledger, name the
rung and the operator you will apply next.

---

## 0.5 How the top 2026 earners actually operate (copy the pattern)

Evidence: **sam0 / Youssef Sammouda** (Meta #1; ~$400K–900K/yr), **brutecat** (Google
$670K in ~3–4 months), **XBOW** (Chrome full chain $250K), **Rabhi** (YesWeHack #1).
Eight habits are shared — these are *behavioural rules*, not trivia:

| # | Habit | Evidence | What you MUST do this session |
| --- | --- | --- | --- |
| 1 | **One-ecosystem depth** | sam0 knows every technique to enumerate Meta; brutecat → Google only. "Critical = systemic understanding." | Pick **one** target/ecosystem and model it fully (§2). Do not skim ten targets. |
| 2 | **North-star impact** | sam0 → ATO always; brutecat → access-control → RCE. | Name your north star (ATO / money / RCE) **before** probing; aim every operator at it. |
| 3 | **Gadget chaining** | sam0 chains self-XSS + login-CSRF + postMessage + open-redirect; Chrome parts $4.5K → chain $250K. | Discard nothing. Every micro-finding goes into the §4 chain map. |
| 4 | **AI = force-multiplier, NOT a scanner** | brutecat pre-computes auth/keys/origins; AI only reasons about the body. "This is downstream of your expertise by a mile." Operation IDs cut FP from 90%→~0. | Use AI for reasoning at scale (§3.2 wordlists). **Verify every AI lead manually** — never report an AI claim unproven. |
| 5 | **Recon = artifact mining at scale** | 60K APKs unpacked, 3,600 keys, cert-transparency logs; "I only automate recon." | §3.2 Mining is **mandatory before fuzzing** — cert SANs, JS bundles, mobile strings, shipped config. |
| 6 | **Systematic workflow + ledger + JS monitoring** | Document every endpoint, brainstorm per feature, note gadgets, revisit with new context; hash-monitor JS for changes. | Live in the Ledger + Raw-Material Store (§6). Re-check changed targets; recombine old bugs (#14). |
| 7 | **Target selection > technique** | Main apps pay more; ecosystems (SDK/mobile/browser-ext/legacy/staging) are less touched; regional gaps = less competition; plan ROI from the program policy. | Choose scope deliberately; go where others don't (§3.2). |
| 8 | **Verification & report discipline** | ≥2× reproduce; prove blast radius, don't extract (507 repos, zero cloned); argue likelihood on appeal ($1.3K→$5K). | Pass the §8/§10 gate. One verified killer report beats twelve "maybes". |

**Meta-pattern:** all winners run **depth + automation + chaining**, not breadth. Their
edge is understanding the target and correctly splitting work with AI — not the tool.

**Stop-checks:** if you are about to (a) browse many unrelated targets, (b) run a scanner
and hope, (c) report a §1 cliché, or (d) skip artifact mining — you are violating this
section. Correct course before continuing.

---

## 1. The Cliché Purge — do this BEFORE you hunt

Ordinary hypotheses are worse than useless: they consume your session and anchor you.
Write the list, then **ban it as a source of findings** (you may still test one if an
*operator* transforms it, but never report the vanilla form):

```text
BANNED AS-IS:  generic IDOR on sequential ids · reflected XSS alone · admin-panel
"takeover" via guessable URL · subdomain brute force · missing security headers ·
open redirect alone · clickjacking on a public page · version banner · SPF/DMARC ·
self-XSS · rate-limit 429 · generic 500 · "GraphQL introspection enabled".
```

**What actually pays (2026 evidence — study the *shape*, not the bug):**

| 2026 case | $ | The non-obvious move |
| --- | --- | --- |
| Misconfigured Grafana → 507 Meta private repos | 157K | wildcard **TLS SAN** revealed a *shadow estate*; JS bundles revealed an unseen domain; unauth `/gcp-token` → secret chain |
| Instagram ATO via `fbevents.js` | 32.5K | a trusted **third-party-origin endpoint that forwards postMessage**, + an OAuth code exchanged by a *different* app |
| "Self-XSS" in FB Payments → FB+IG ATO | 62.5K | **Login CSRF** turned a "self" bug into cross-user ATO; compromised 3rd-party iframe relayed unsanitised HTML |
| FB mobile ATO | 66K | the bug was **cryptographically insecure RNG** feeding a session id, + XSS |
| Meta support infra IDOR | 78K | started "limited" in one product → **shared backend**, and **write** actions (create case, change status) raised impact |
| Google Cloud tenant isolation break | 88.3K | `-` **wildcard** was expanded **after** the authz check → check/query de-sync |
| Google username-recovery phone leak | 5K | a **JS-disabled legacy form** still worked; pasted a real BotGuard token to dodge rate limit; **IPv6 /64 rotation** |
| Open redirect → email leak | 1.3K | recombined a **year-old saved dead bug** with a `continue` param that accepted the whole `google.com` tree |
| Chrome full chain (V8→Blink→Crashpad) | 250K | 3 bugs worth **$4.5K separately**; the *seam between components* was the real asset |
| Confused Deputy: Google IdP ATO | 13.3K | **device-code-flow** abuse — a trusted component acting for an attacker identity |

**Rule:** a finding is only interesting if it exploits a **quirk specific to this target**.
If your repro would work identically on any arbitrary app, it is a cliché. Discard and
apply an operator.

---

## 2. Reconstruct the app — then model its SEAMS

Model the app (entities, roles, actions, money, trust edges, state) as before, but the
payoff now comes from **seams** — places where two components each assume the other is
handling a control. (Almost every high-value 2026 bug was a seam bug.)

```text
ENTITIES   : users, orgs/tenants, orders, files, sessions, tokens, devices...
ROLES      : anon, user, org-admin, super-admin, support, service-account
ACTIONS    : create / read / update / delete / share / pay / invite / export
MONEY      : where price, credit, coupon, refund, entitlement is computed
TRUST EDGE : client→server, tenant→tenant, user→admin, server→internal/cloud,
             app→3rd-party-script, idp→app (OAuth), build→runtime
SEAM       : <two components that share an interpretation of the same input>
```

Then write **invariants** (statements that must always hold). Bugs are violations:

- "A user reads only rows in their own tenant/project."
- "Only an org-admin can add an org-admin."
- "An invite/OAuth code is single-use, app-bound, and expires."
- "The authz check and the data query scope over the *same* interpretation of the URL."
- "The mobile API enforces the same authz as web; the no-JS path as the JS path."
- "Total paid ≥ total owed; a coupon applies at most once."

Every invariant *and every seam* becomes a ledger row.

---

## 3. THE DIVERGENCE ENGINE (the core — this is the skill)

Run this loop. It is what forces the model off its default prior. Never skip a step
because "it probably won't work" — that instinct *is* the cliché.

### 3.1 Cliché-buster operators (apply to each surface)

Each operator is a **transform** you apply to a request/feature, not a checklist item:

1. **Negate the guard** — don't test where the check *is*; find the path where it *isn't*
   (another client, version, batch endpoint, export, admin action, no-JS path).
2. **Reject the verdict** — when told "self-XSS / out-of-scope / low / needs JS / not
   exploitable", treat *the missing precondition* as the exploit. (sam0 → Login CSRF → ATO.)
3. **Swap the actor** — re-send the request as victim / admin / support / system.
4. **Swap the tenant/org/project** — does the boundary survive?
5. **Swap the client** — web vs mobile vs API vs **legacy/no-JS vs old version**. Where
   does authz differ? (The no-JS Google form still worked in 2025.)
6. **Swap the version** — v1 still live? deprecated endpoint? `?version=`/header override?
7. **Parallelize** — fire the *same* request N× at once (race, double-spend, single-use).
8. **Replay / reorder / skip** — take a captured request out of sequence into a new state.
9. **Splice A×B** — feed feature A's input into feature B's interpreter (cross-feature).
10. **Second-order** — store now, render/execute later (email, PDF, admin view, webhook, log).
11. **De-sync** — make two components disagree: parser differential, cache, or a wildcard
    expanded *after* authz (the 88K Google bug).
12. **Boundary-abuse** — use a documented "convenience" value (`-`, `*`, `all`, `0`, empty,
    null, `..`, a whole-domain `continue` URL) as a *privilege primitive*.
13. **Confused deputy** — which trusted component can be steered into acting for me? (IdP,
    device-code flow, backend fetcher, app→3rd-party postMessage bridge.)
14. **Recombine** — pull two small/dead bugs out of your Raw-Material Store (§6) and glue them.

### 3.2 Artifact-Pointer Mining (find the target you cannot see)

Do not brute-force. **Read artifacts and follow the pointers they contain:**

- **TLS certs / CT logs** — SANs & wildcards reveal shadow estates
  (`*.llm-playground.aws.metafb.cloud` → an entire hidden surface). Query crt.sh for the org.
- **JS bundles / source maps / strings** — hidden hosts, internal APIs, feature flags,
  new domains (parsing bundles found `api.haloworld.xyz` — the whole 157K chain hinged on it).
- **Error / stack / debug output** — internal hostnames, framework versions, file paths.
- **Mobile binary** — `strings`, deep-link schemes, embedded keys, staging URLs, SDK versions.
- **Build artifacts** — shipped config files, serialized settings, compiled assets
  (the Unity/FB SDK `uploadAccessToken` was baked into `resources.assets`).
- **robots / sitemap / .well-known / security.txt / API docs** — advertised-but-forgotten paths.
- **Patches & past fixes** — a fix reveals exactly the seam; the *variant* is unpatched.

Log every pointer as a new surface row. **AI is allowed and encouraged here** — generate
a context-aware wordlist from the JS bundles/params you found; this is how the 157K hunt
fuzzed its way to the unauth token endpoint.

### 3.3 Source × Sink × Context generator (build candidates mechanically)

Do not brainstorm randomly. Fill a matrix: pick a **source** (attacker-controlled value),
a **sink** (privileged/interpreted action), and a **context** (trust boundary). Every
non-empty cell is a hypothesis.

```text
SOURCES : url param · path segment · header · body field · filename · redirect target ·
          postMessage data · OAuth code/state · JWT claim · webhook payload · device id
SINKS   : authz decision · SQL/ORM · template/HTML · shell/cron · file path · URL fetch ·
          deserialize · token mint · pricing/entitlement · email/PDF render · log ingest
CONTEXT : anon→server · user→user · tenant→tenant · app→3rd-party · idp→app · server→cloud
```

### 3.4 The Uniqueness Law + Novelty Score

Before investing, score the hypothesis:

- **Novelty 1–5** — 1 = cliché (any app), 5 = relies on a target-specific quirk. **Only ≥3 earns time.**
- **Impact 1–5** — reaches money / PII / auth / code-exec?
- **Reachability** — can a normal user trigger it? (Google upgraded likelihood 1.3K→5K on appeal.)

Spend on `Novelty × Impact × Reachability`. Chase the seam, not the surface.

---

## 4. Seam & chain map — make the small bugs compound

List every micro-finding, then ask **"what boundary does A let me cross, and what does
that unlock?"** (The Chrome chain's parts were ~$4.5K; chained, $250K.)

- login-CSRF + self-XSS → cross-user stored XSS → **ATO**
- open-redirect + `continue`/`next` domain-tree param + `authuser` → **email/PII leak**
- weak RNG + XSS → **session/ATO**
- IDOR(read) + missing-authz(write) → **tenant takeover / data rewrite**
- unauth token endpoint → secret manager → env vars → **repo/deploy takeover** (the 157K chain)
- SSRF(blind) + cloud metadata → IAM creds → **data**
- info-leak (display name / masked phone) + oracle endpoint → **identity brute-force**
- compromised 3rd-party iframe → postMessage relay → **XSS on first-party origin**

A chain reaching money / PII / auth is worth far more than its parts. **Prove blast
radius, do not extract it** — enumerate the count, stop, write up (§8).

---

## 5. The 2026 Playbooks (reusable attack shapes)

### 5.1 Origin confusion & trusted bridges
Trusted 3rd-party script + any endpoint that **forwards a message/redirect under a
first-party origin** = origin confusion. Check: does the app `postMessage` to a
window whose opener I control? Does it validate *sender* or only *origin*?
(`fbevents.js` bug: an endpoint forwarded attacker content under `facebook.com`.)

### 5.2 "Self-XSS" is a lie
Any "you can only attack yourself" verdict → find the precondition that makes it
cross-user: **Login CSRF** (log victim into *my* account), shared nonce/session,
or a relay from a trusted origin. The 62.5K bug was exactly this.

### 5.3 OAuth / identity / device flow
- code **not app-bound** (exchanged by another app)? · `redirect_uri` accepts a
  whole-domain tree (`*.google.com`, `continue=`)? · **device-code-flow** hijack
  (confused deputy)? · `state`/nonce replay? · token mint for a *different* audience?

### 5.4 Authz ↔ data-query de-sync
Find where the **check** and the **fetch** interpret the same input differently:
wildcards (`-`,`*`) expanded after authz; `project` in URL vs token; case/unicode.
(88.3K Google Cloud isolation break.)

### 5.5 Legacy parallel paths & validation mismatch
Premise broken? ("X requires JS since 2018" — the No-JS form still worked.) Hunt
**old / alternate / no-JS / mobile-only** paths, and **parameter-validation mismatches**
(a `bgresponse=js_disabled` field vs a real `bgRequest` token → unlimited, unthrottled).

### 5.6 Recovery & trusted-device path
Password reset, email/phone change, "trusted device", linked accounts, support
impersonation are the *easiest* ATO surface. (The $24K/w "$30K" Meta wins lived here.)

### 5.7 Crypto primitive audit
Not just crypto *usage* — the **primitive itself**: how are ids/tokens/OTP/session
nonces generated? Insecure RNG fed a session id (the 66K ATO). Check predictability.

### 5.8 Build / SDK / config artifact leaks
Shipped config, serialized settings, compiled assets, `.env` in bundles, SDK "fields
the editor asks you to fill". A plaintext editor on the right output file was enough.

### 5.9 Cloud service internals & secret chains
Unauth/debug endpoints, metadata, secret managers, signed URLs, CI/CD. Follow the
token chain read-only: `token → secret → env var → API token → repos` — count, don't clone.

### 5.10 Stale-state / TOCTOU / trust of last measurement
Component A measured state and component B used it after it changed (kept image
geometry vs replaced bytes; Crashpad read+retry). Find checks that trust a stale value.

---

## 6. Coverage Ledger + Raw-Material Store (mandatory artifacts)

Ledger (one row = one **falsifiable** hypothesis, with the operator that generated it):

```text
| # | Surface / invariant / seam | Operator (§3.1) | Hypothesis | Test (exact) | Result (raw) | Next angle |
|---|----------------------------|-----------------|------------|--------------|--------------|------------|
| 1 | GET /api/invoices/{id}     | swap-tenant #4  | cross-tenant read | loop ids | 403 user2 | batch endpoint |
| 2 | /ac/accountchooser?continue| boundary-abuse#12 | accepts *.google.com → leak | continue=evil.google.com | email appended | chain open-redirect |
```

Rules: `Result` quotes real output; `BLOCKED` needs a reason; never re-run a logged test —
only escalate it; **every row must carry a non-cliché operator**.

**Raw-Material Store** — keep every dead/small bug forever:
```
[ ] open redirect at adservice.../ddm/clk/...  (recombine #14)
[ ] continue= accepts all *.google.com subdomains
[ ] no-JS usernamerecovery form still live
```
Small bugs are inventory, not failures. Recombine them (#14) each session.

---

## 7. Escalation Ladder (substrate — descend when the engine stalls)

Concrete move sets per rung; do not skip a rung because "it probably won't work".

- **L1 Surface expansion** — operator #1 + Artifact-Pointer Mining (§3.2). Parse every
  JS/source-map, cert SAN, mobile string, sitemap, api-doc. ≥10 new endpoints/params.
- **L2 Authorization matrix** — `user × resource × action` × *every client/version*;
  batch/export/share/webhook endpoints; JWT (alg/kid/claim swap); cloud IAM escalation.
- **L3 Logic & state machine** — replay/skip/out-of-order, negatives/overflow, coupon/refund,
  entitlement/trial, mass assignment; mobile deep-links & root bypass; cloud metadata SSRF.
- **L4 Parser & trust differentials** — JSON/XML mixups, duplicate keys, method override,
  host-header, HTTP smuggling (CL.TE/TE.CL); SSRF allowlist bypass; cache poisoning.
- **L5 Races & TOCTOU** — operator #7; last-write-wins boundaries (balance, stock, unique idx).
- **L6 Cache / second-order / stored trust** — web-cache deception/poisoning, stored XSS in
  admin/PDF/email, blind XSS in tickets; insecure token storage; public snapshots/signed URLs.
- **L7 Version/dependency/CVE → variant** — fingerprint exact versions; find the *unpatched
  variant* in an adjacent endpoint/SDK (see `cve-threat-intel`).
- **L8 Chaining** — §4. Cross every boundary with the smallest possible steps.

**Stuck Playbook** (force a new angle, answer out loud, seed the next ledger row):
what does the dev assume the client never sends? · send twice/parallel? · what seam does
this cross? · what does the UI hide that the API trusts? · other entrypoint/client? ·
where is it stored & re-rendered? · which id is guessable? · which header does a proxy
trust? · where is money computed? · staging/debug endpoints? · recovery path? ·
what does an error leak? · what's rate-limited only per-IP/session? · what's newly added? ·
what can I do unauthenticated? · **what does my smallest bug unlock next?**

---

## 8. Evidence, impact & reporting

For every candidate: reproduce **≥2×** with different inputs; keep the minimal reproducer
(exact `curl`/script + raw response); state impact as an **effect**, not a category:
- bad: "IDOR" · good: "user A reads user B's support tickets (chat transcripts, files, PII)
  via `GET /api/cases/{id}` — sequential ids, ~N enumerable, and the same check lets me
  *modify* case status."

**Blast-radius discipline:** prove reach, don't extract. The 157K report enumerated 507
repos and **cloned zero**; enumeration *is* the proof. Anything you cannot demonstrate →
ledger `unconfirmed` (a hypothesis, not an exit).

**Report:** `[SEV] Title · Affected flow · Boundary/seam crossed · Steps · PoC (raw) ·
Impact (effect) · Fix`. Then re-read §1: if your title is a banned cliché, you have not
found the real bug yet — hunt the transformed version.

**Bounty appeal:** if a technically-sound finding is rated "low", argue **likelihood &
prerequisites** (zero prereqs + undetectable → Google raised $1.3K → $5K). Fair, factual,
non-coercive (see `disclosure-communication`).

---

## 9. Scope & legality gate

Hunt only authorised scope (user's program / own asset / permission). If the user names a
live production host, proceed only when they confirm it is in scope; otherwise treat it as
a lab. **Read-first**, minimal proof, no PII dumping, no pivot off-target, no DoS. Use
`opsec` for traffic handling.

---

## 10. End-of-session gate (do not pass without all `yes`)

- [ ] §0.5 Operating Pattern honoured: one-ecosystem depth, north-star named, AI leads verified.
- [ ] Cliché Purge done; no reported finding is a banned vanilla form.
- [ ] Artifact-Pointer Mining run (cert SANs, JS bundles, mobile strings, shipped config).
- [ ] Every ledger row carries a non-cliché **operator**; ledger printed, all cells
      `TESTED`/`BLOCKED(reason)` with evidence.
- [ ] Rungs L1→L8 each attempted with ≥1 real test (or `BLOCKED`+reason).
- [ ] Seams/invariants each tested; every micro-finding considered for chaining (§4).
- [ ] Raw-Material Store updated (dead bugs kept for recombination).
- [ ] Every reported item: ≥2× reproducible PoC + effect-level impact.
- [ ] State declared: `FOUND` or `EXHAUSTED`.

If any box is unchecked — **you are not done. Apply the next operator and continue.**
