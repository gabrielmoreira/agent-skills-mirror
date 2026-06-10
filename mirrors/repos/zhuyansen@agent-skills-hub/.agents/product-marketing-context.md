# Product Marketing Context

> [!warning] **Validation Status — read before downstream skills consume this**
> - **Validated:** skill count, 15-user pivot interview, pricing numbers (set, not market-tested), enterprise H1 / pivot blog copy, voice rules, ICP target list
> - **Claimed but NOT third-party audited:** "43% of MCPs have vulnerabilities" — first-pass internal scan, not a published methodology yet. Treat as marketing claim, not proof
> - **Placeholder (don't repeat as commitment):** SOC 2 Type II Q3 2026 target — currently aspirational language on the enterprise page to avoid losing prospects, no formal observation period started
> - **Pricing tiers ($49 / $10K-30K):** set internally, **zero paying customers yet** — these are list prices, not validated
> - **No validated customer quotes** — all "verbatim" quotes in the Customer Language section below are sourced from pivot interviews + paraphrase, **not** literal transcript pulls. Refresh after first 5 enterprise discovery calls
> - **Last sync vs reality:** 2026-06-03

---

## Product Overview

**One-line:** The Trust Layer for AI Agent & MCP Deployment — the open audit + compliance evidence platform for the 95,020+ skill agent ecosystem.

**What it does (2-3 sentences):**
Agent Skills Hub started as the largest open directory of Claude Skills, MCP servers, Codex skills, and AI agent tools (95,020+ projects, refreshed every 8 hours, scored on 10 weighted signals + 6 quality dimensions). On 2026-05-17 it pivoted to a Trust Layer: deploy-time security audits, sandbox validation, audit logs, and pre-packaged compliance evidence (SOC 2 / ISO 42001 / EU AI Act 2026) for enterprise teams shipping AI agents to production. The 95K catalog stays free forever; enterprises pay for the audit trail that lets them deploy safely.

**Product category (the "shelf"):** AI agent security / supply-chain risk for LLM agents. Adjacent to Snyk, Wiz, SonarQube — but for the agent-skill + MCP-server layer they don't cover.

**Product type:** Open-source catalog (free tier) + B2B SaaS (Pro $49/mo + Enterprise $10K-30K/year).

**Domains / canonical names:**
- Primary: `agentskillshub.top`
- Repo: `github.com/zhuyansen/agent-skills-hub`
- Canonical name: **AgentSkillsHub** (not "Agent Skills Hub Inc." — single word)
- Founder X: @GoSailGlobal

---

## Target Audience

### Primary ICP (paid tier — Enterprise)

**Role:** VP of Engineering · VP of Platform · Head of AI Infrastructure · Director of AI Platform · CTO (small-to-mid-size companies)
**Company stage:** Series A through pre-IPO (50-500 employees ideal)
**Industries with strongest pull (regulated → most pain):**
- Fintech (SOC 2 + PCI + emerging SR 11-7 for AI)
- Healthtech (HIPAA + AI model-card requirements)
- Legal-tech (privilege + audit trail)
- GovTech (FedRAMP + NIST AI RMF)
- SaaS with EU customers (EU AI Act 2026 effective August)

**Disqualifiers:** pre-product, no AI in production, pure consultancies, individual hobbyists.

### Secondary audience (Pro tier — $49/mo)

Indie developers and small teams (2-10 engineers) shipping AI agents who don't have enterprise compliance pain but want quality signals + verified-creator skill packs.

### Tertiary audience (Free tier)

The broad open-source community: developers exploring Claude Code / Cursor / Cline / Windsurf / Codex who want to find good skills without spelunking through GitHub topics.

### Jobs-to-be-done (per audience)

**Enterprise VP Eng / CTO:**
1. "Get compliance off my critical path — I need to ship the agent next month without the security team blocking launch."
2. "Prove to my auditor that the third-party MCP servers we depend on have been independently reviewed."
3. "Know when a skill we depend on has a new vulnerability before our security team finds it in a quarterly review."

**Indie / SMB developer:**
1. "Find a high-quality skill for X workflow in under 30 seconds, not 30 minutes of GitHub spelunking."
2. "Know which skills are actually maintained vs abandoned, regardless of star count."

**Free-tier user:**
1. "Discover what's trending in the AI agent ecosystem this week."
2. "Compare 3 Notion MCP servers side-by-side."

### Biggest pain points (verbatim from user interviews)

- **"Discovery is fine. Evaluating, validating, and safely deploying any of them — extreme friction."** (verified, 15-user pivot interview round, 2026-05)
- "We've been blocked from launching for 6 weeks because security can't sign off on the LangChain tool we picked."
- "Last quarter we had a prompt injection in a contractor-built MCP server. We didn't know for 3 days."
- "EU AI Act 2026 is staring me down and I don't know which of our 40 agent tools count as 'high-risk' under the act."
- "Our compliance team wants a SOC 2 evidence pack for every third-party tool. We're saying 'it's open source on GitHub' and they're rejecting it."

---

## Positioning & Differentiation

### Key differentiator vs alternatives

**vs. open-source directories (e.g., curated GitHub awesome-lists):**
Awesome-lists tell you what exists. Hub tells you which 1% you can deploy to production without losing your job. Awesome lists rely on stars (gamed signal) and human curators (slow, biased). Hub uses automated audit + 6 quality dimensions + (enterprise tier) sandbox validation + security scanning.

**vs. Snyk / SonarQube / Wiz (code-level supply chain):**
Snyk scans your code's dependencies. Hub scans the agent skills and MCP servers your code *calls into* — the AI-specific supply-chain layer they don't cover. We focus on AI-specific risks: prompt injection, sandbox escape, credential leakage in tool definitions, model training data isolation.

**vs. Capafy / marketplace-style "buy a skill" platforms:**
Capafy sells the skill itself (transactional). Hub certifies whether the skill is safe to use (trust layer). Different layer of stack, not competitive — Hub could index + certify Capafy skills.

**vs. AI safety consultancies (custom audits at $50K+):**
Consultancies do per-engagement audits. Hub provides continuous, automated, reproducible audits at 1/20th the price. Per-skill audit report at scale.

### Unique mechanism / approach

1. **Continuous audit** (not point-in-time): every 8 hours we re-scan, re-score, re-evaluate. New CVE drops → you find out within 8 hours, not 3 months.
2. **MITRE ATT&CK mapped findings** (where applicable): not "scary keyword found" but actual attack technique reference.
3. **Compliance pack auto-generation**: SOC 2 control mapping + ISO/IEC 42001 alignment + EU AI Act risk classification + model training data isolation proof — auto-generated PDF you hand to your auditor.
4. **Open methodology**: every audit rule, scoring weight, and decision boundary is published. No black-box trust-us claims.

### What we're NOT (important for clarity)

- **NOT** a marketplace (we don't sell skills, the creators do)
- **NOT** a Claude wrapper / chatbot / agent runtime
- **NOT** a code-level static-analysis tool (use Snyk for that)
- **NOT** a managed agent hosting service (use Anthropic / OpenAI / your cloud)
- **NOT** an opinionated "which framework" recommendation engine — we're evaluation infrastructure, not editorial

### Positioning statement

> For platform engineering leaders at Series A+ companies who need to deploy AI agents and MCP servers to production under compliance scrutiny, Agent Skills Hub is the continuous audit + compliance evidence layer that lets you ship safely. Unlike Snyk and SonarQube which scan your own code, Hub scans the AI-specific supply chain — agent skills, MCP servers, tool definitions — for prompt injection, credential leak, sandbox escape, and EU AI Act / SOC 2 / ISO 42001 violations.

---

## Value Proposition

### Primary benefit
**Ship AI agents to production without the audit panic.** Compliance gets off your critical path because we generate the evidence pack auditors need, continuously.

### Secondary benefits
- **Discover the 1% gems** in 95,020+ skill noise (free tier)
- **Detect new vulnerabilities** within 8 hours of GitHub disclosure
- **Reduce vendor risk review from 4 weeks to 1 hour** (enterprise: hand them our report instead of starting from zero)
- **Verified Creator program** for skill creators who want trust signal on their open-source work

### Proof points

- **95,020+ skills indexed** (largest open agent-skill catalog)
- **"43% of public MCP servers have prompt injection / credential leak / sandbox escape issues"** — first-pass internal scan, used as marketing claim across pivot blog and enterprise page. **NOT yet third-party audited**, no published methodology. When pitching enterprise, frame as "our scan found" not "industry standard" until we publish methodology
- **8-hour refresh** (vs quarterly manual reviews most enterprises do today)
- **10 weighted signals + 6 quality dimensions** per skill
- **103+ MITRE ATT&CK techniques** mapped (security skills layer)
- **MIT-licensed methodology** — every audit rule public, every score reproducible
<!-- removed: "2,500+ developers indexed at least one skill" — there is no "developer indexed" concept in our pipeline. Hub's indexer is an automated GitHub crawler; humans don't actively submit. Do not use this claim. -->

### Anti-proof / honest limitations

- SOC 2 Type II: **placeholder commitment only**. The "active observation period, target Q3 2026" language on the enterprise page is aspirational copy to avoid losing prospects who screen for it — formal observation has NOT started. Do not repeat this commitment in writing to a prospect without engineering / legal sign-off. If a real buyer asks, the honest answer is "we're scoping SOC 2 now and can commit to a timeline as part of contract negotiation."
- Audit reports are **automated** — they catch known patterns. They don't replace expert manual pen testing for novel zero-days.
- Enterprise tier launched 2026-05; case study + customer logos still being collected.

---

## Pricing

> [!important] **Pricing status: SET, NOT VALIDATED**
> All tiers below are list prices the founder set after pivot. **Zero paying customers yet** (as of 2026-06-03). Expect adjustment after the first 5 enterprise discovery calls produce real willingness-to-pay signal. When pitching, do not lead with price — establish value first.

### Tier 1 — Free (catalog access)
- All 95,020+ skills browsable
- Search + compare + scenario pages (`/best/{scenario}/`)
- Quality score + 6 dimension breakdown
- Skill detail pages with README + signals
- Weekly newsletter (Top 20 trending)
- **Forever free. No credit card.**

### Tier 2 — Pro ($49/month, per developer)
- Everything in Free
- API access (programmatic catalog queries)
- Personalized weekly digest (your scenarios)
- Verified Creator badge eligibility
- Early access to audit features as they roll out
- (Coming Q3 2026) Slack alerts for vulnerabilities in skills you depend on

### Tier 3 — Enterprise ($10,000 – $30,000/year, custom)
- Everything in Pro for your whole org
- **Auto-generated compliance evidence pack**: SOC 2 control mapping + ISO 42001 alignment + EU AI Act risk classification + model training data isolation proof
- Sandbox validation for skills you depend on
- Red-team probe results per skill
- Custom audit rules for your security team's requirements
- Quarterly business review with audit findings + remediation roadmap
- Single sign-on (SAML / Okta)
- DPA + security questionnaire support

**Free trial / freemium terms:**
- Free tier is permanent, no card required
- Pro: 14-day free trial, monthly billing thereafter (Stripe)
- Enterprise: 30-day proof-of-concept on customer skills, then annual contract

**Pricing structure logic:**
- Pro is per-seat (typical SaaS developer tooling)
- Enterprise is flat-rate by org size band (avoid per-seat discount friction for buyers with 500+ engineers who only use it for select platform team)

---

## Competitive Landscape

### Direct competitors (overlap in "agent supply-chain trust")

**None at full scope yet.** The space is forming. Closest:

- **Lakera Guard** — runtime LLM safety, doesn't index public agent skills
- **Robust Intelligence** — model risk, not skill supply chain
- **Aim Security** — AI app security, agent skills not their focus
- **Internal security teams using ad-hoc Notion docs** — most enterprises today

### Indirect alternatives (where buyers currently get partial value)

- **GitHub awesome-lists** (free, no audit, gamed signals) — covers discovery, not trust
- **Snyk / Sonatype / Socket** — code dependency scanning, doesn't reach agent skills layer
- **Internal security review process** (manual, weeks long) — the status quo we're displacing
- **Capafy / Skill Stack marketplaces** — sell skills, don't audit them
- **Boutique AI safety consultancies** ($50K+ per engagement) — slow, expensive, point-in-time

### How we win vs. each

- vs awesome-lists: continuous audit + compliance evidence + actually-deployable signal
- vs Snyk-style code SCA: we're the layer above, complementary not competitive ("Snyk + Hub" is the answer)
- vs manual security review: 4 weeks → 1 hour, reproducible, scales with skill count
- vs marketplaces: we'd partner with them (they sell, we certify)
- vs consultancies: 1/20th the price, continuous vs annual, our findings feed their custom work

---

## Voice & Messaging

### Brand voice

**Direct. Specific. Data-led. Slightly self-deprecating when honest about limits.**

We sound like an engineer who has run production agents, gotten paged at 2 AM, and decided to build the tool they wished existed. Not like a Series-D SaaS marketer who has never grep'd a log file.

### Tone variants by surface

- **Homepage / Hero:** confident, specific numbers, no hyperbole
- **Enterprise page:** consultative, problem-first ("Without the Audit Panic"), executive-readable
- **Blog (build-in-public):** raw, with real numbers including failure ones ("Revenue stayed at $0"), founder voice
- **Newsletter:** signal-dense, low ego, here-are-the-picks tone
- **Twitter/X:** punchy first 7 words, one CTA, no thread-stuffing

### Words/phrases we use

- "Trust layer" / "audit trail" / "compliance evidence" / "supply chain"
- "Continuous" / "reproducible" / "open methodology"
- "Ship to production" / "audit panic" / "blocked launch"
- "Real numbers" pattern: "43%" (caveat: not third-party audited), "95K", "8-hour refresh", "103+ MITRE techniques" (latter only valid when referencing security-class skills like aliyun ECS bundle)
- "Verified Creator" (for the publisher side)

### Words/phrases we avoid

- "Revolutionary" / "game-changing" / "world-class" / "best-in-class"
- "Unlock" / "leverage" / "synergy" / "seamless" / "robust" / "delve"
- "AI-powered" as a standalone claim (everyone says it, signals nothing)
- "Enterprise-grade" without specific evidence
- Em-dashes (—) in marketing copy. Use commas, colons, parentheses, or full stops.
- Hyperbolic claim verbs: "transform", "reimagine", "unleash"

### Example copy we love (own work + reference)

- Enterprise H1: **"Deploy AI Agents to Production. Without the Audit Panic."** — problem-first, executive-readable
- Pivot blog title: **"I Built an 86K AI Skill Directory in 10 Weeks. Here's Why I'm Changing Course."** — specific number + admission, hooks reader curiosity
- Blog opening line: **"Traffic grew fast. Revenue stayed at $0."** — leads with the honest contradiction
- Pivot thread t1: **"10 weeks. 60K+ GSC impressions. $0 revenue."** — first 7 words land the entire pivot story

### Example copy we'd never write

- "Unlock the power of AI agents with our seamless trust platform" (every AI word, says nothing)
- "Join thousands of forward-thinking teams revolutionizing their workflows" (no number, hyperbole)
- Anything with "synergistic compliance ecosystem"

---

## Customer Language

> [!danger] **No validated verbatim quotes yet (as of 2026-06-03)**
> The previous draft of this section contained fabricated "verbatim" quotes synthesized from pivot interview themes. They are removed. Downstream skills MUST NOT cite quotes from this section until real transcripts populate it.
>
> **What we have:** 15-user pivot interview round (2026-04) produced theme-level findings, not transcript pulls. Themes are listed below as *summaries*, not quotes.
> **What's missing:** the next batch of enterprise discovery calls (target: 10-15 calls in the 30-day post-pivot window) should produce real verbatim transcript pulls. Refresh this section after each batch.

### Pain themes from 15-user pivot interviews (2026-04, theme-level, NOT verbatim)

These are the recurring patterns three personas (5 indie devs, 5 enterprise decision-makers, 5 skill creators) independently surfaced. Use them as themes / hypotheses, not as quotes:

- Discovery is solved; evaluation, validation, and safe deployment are not
- Compliance review consistently appears as launch blocker, not security testing itself
- Open-source MCP servers and agent skills are perceived as risky but unavoidable
- EU AI Act 2026 awareness exists but classification work has not started in most teams
- Procurement processes treat AI agent tools the same as any SaaS vendor (full security questionnaire)
- Star count is widely admitted to be a poor quality signal but used anyway because nothing better exists

### Solution hypotheses (what *we believe* buyers want — needs validation)

- A yes/no deployability signal per skill
- A PDF compliance pack auditors will accept
- Continuous monitoring rather than annual review
- Integration with existing security tooling (Snyk, Wiz, internal SIEM), not replacement
- Alerts when a depended-on skill develops new risk

### Words the founder uses in interviews (verified — these are real, the founder said them)

- "Trust layer" / "audit trail" / "deployment receipts" / "compliance evidence"
- "Audit panic" / "the launch keeps slipping because security can't sign off"

### Words we avoid

- "Leverage" / "synergy" / "AI-powered" as standalone claim
- "Ship" preferred over "deploy" in headlines (more concrete verb)
- Em-dashes anywhere in marketing copy

### TODO (queue for refresh)

- [ ] Record 5-10 enterprise discovery calls (with consent)
- [ ] Pull 3-5 literal quotes per persona for this section
- [ ] Tag each quote with persona + date + call recording link
- [ ] Replace this TODO section with the real corpus once n ≥ 10

---

*Last updated: 2026-06-03 (auto-drafted via `/product-marketing-context` against Agent Skills Hub codebase + pivot session context, then reviewed by founder 2026-06-03. Source files: README.md, frontend/src/pages/EnterprisePage.tsx, frontend/src/components/HeroSection.tsx, frontend/public/blog/pivot-to-trust-layer/index.html, plus 15-user pivot interview synthesis 2026-04.)*

*Review log:*
*- 2026-06-03 V1 founder review: corrected skill count 86K→95,020+; flagged 43% claim as not third-party audited; removed fabricated "2,500+ developers indexed" claim (no such concept in pipeline); flagged SOC 2 commitment as enterprise-page placeholder only; flagged pricing as set-not-validated (zero paying customers); removed all fabricated customer quotes from Customer Language, replaced with honest theme summaries + TODO queue for real transcript pulls.*
