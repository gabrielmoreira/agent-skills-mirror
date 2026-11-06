---
name: disclosure-communication
description: Use when writing or sending a vulnerability, exposure, or leaked-credential report to a vendor, PSIRT, bug bounty triage, CERT, or a decision-maker. Applies persuasion and communication psychology to get the finding accepted and to obtain a bounty, credit, or certificate. Ethical, non-coercive, professional.
---

# Disclosure Communication

## PURPOSE
Turn a technical finding into a message that gets **acknowledged, fixed, and rewarded**. This skill is about the human layer — framing, tone, timing, rapport, negotiation — not the technical proof. Persuasion is aimed only at remediation and fair recognition.

## TRIGGER
Activate when the user says or implies: "report တင်", "disclosure", "vendor ဆက်သွယ်", "bounty", "CVE", "email ရေး", "PSIRT", "CERT", "CEO ကို ဆက်သွယ်".

---

## HARD RULES
1. **No extortion, no threats, no ultimatums.** Never "pay or I publish".
2. **Persuasion only toward remediation and recognition.** Never manipulate into harm.
3. **Minimal evidence.** Never dump raw data, PII, or full credential values.
4. **Human approves before sending.** Draft first, send only on approval.
5. **Truthful.** Never inflate impact. Credibility is the whole asset.
6. **Never emotional.** Stay calm, professional, and generous regardless of their reply.

---

## PSYCHOLOGY FOUNDATIONS

| Principle | What it does | How to apply |
|---|---|---|
| **Reciprocity** | Give first, they feel obliged | Offer a free, clear fix and to coordinate; ask for reward only after giving value |
| **Commitment & consistency** | Small yes leads to bigger yes | First ask only for "confirm receipt", then move to fix, then recognition |
| **Authority & credibility** | Lowers doubt | State your track record (disclosures, handle, CVE) once, briefly, without bragging |
| **Liking & rapport** | People help those they like | Warm, respectful, mirror their tone and formality |
| **Social proof** | Norms reduce resistance | "Standard 90-day responsible disclosure", reference their own security page |
| **Loss aversion** | Risk of loss motivates more than gain | Frame as "risk to your users/liability you can remove", not "I broke you" |
| **Framing effect** | Same fact, different reaction | Positive frame: "here is how to protect users" not "you are vulnerable" |
| **Anchoring** | First number sets the range | Anchor severity/expectation with facts, not demands |
| **Cognitive ease** | Easy = more likely done | Short message, numbered steps, exact file/line, ready-made fix |
| **Face-saving** | Protects their ego/status | Give a graceful path; never imply incompetence; "easy to miss" |
| **In-group identity** | "One of us" builds trust | "As a fellow security professional…" |
| **Timing & mood** | State affects decisions | Avoid weekends, holidays, finance quarter-end, major incidents |
| **Personalization** | Signals real attention | Use names, reference their product specifically |
| **Urgency without threat** | Motivates without triggering defense | Urgency from impact and timeline, never from a threat |
| **Reciprocity in the ask** | Framing the reward as mutual | "If you have a program, I'd appreciate consideration" |

---

## AUDIENCE PSYCHOLOGY

| Recipient | Wants | Fears | Best angle |
|---|---|---|---|
| Security engineer | Clean fix, credit | Looking bad internally | Technical, exact repro, ready fix |
| PSIRT | Process, completeness | Unmanaged risk, audit findings | Structured report, impact, timeline |
| CISO | Risk reduction, compliance | Breach, regulator, board | Business risk, compliance, metrics |
| CEO / founder | Brand, trust, funding | Reputation, liability | User trust, liability, simple terms |
| Bug bounty triage | Valid, in-scope, clear | Duplicate, noise | In-scope, clear repro, impact |
| CERT / regulator | Public safety, process | Unhandled incidents | Formal, factual, documented timeline |
| Individual dev | Not being judged | Overwhelm | Friendly, minimal, help them fix fast |

**Rule.** Write to the recipient's **incentive**, not to your own frustration.

---

## MESSAGE ARCHITECTURE

1. **Subject** — factual, calm, specific. `[Security] Exposed <asset> — responsible disclosure`. No drama, no "URGENT!!!", no "hacked".
2. **Opener** — who you are + why you are writing. `Hi <name>, I'm a security researcher. While researching <area> I noticed <issue>. I'm reporting it responsibly.`
3. **Credibility** — one line, only if relevant. `I've reported similar issues to <orgs>.`
4. **Impact** — what an attacker could do, in their language (business + user).
5. **Evidence** — minimal: count, redacted sample, screenshot, hash. Never raw data.
6. **Reproduction** — numbered, minimal, safe.
7. **Remediation** — concrete fix; make it easy.
8. **Ask** — ack, fix timeline, and (gently) consideration for reward/credit.
9. **Close** — cooperation and gratitude. `Happy to provide more detail.`

**Subject-line psychology.** Calm and specific beats alarming. "Exposed customer database" lands; "YOUR SITE IS HACKED" triggers defense.

---

## LANGUAGE PATTERNS

**Use**
- "I noticed…" / "I wanted to report this responsibly…"
- "This could allow an attacker to…"
- "Suggested remediation…"
- "I'm happy to coordinate on timing."
- "Please confirm receipt."
- "Thank you for your work on <product>."

**Avoid**
- "Your site is vulnerable" / "I can hack you"
- "Pay me or I publish"
- "I demand" / "You must"
- Blame, sarcasm, urgency theater
- Raw data dumps
- Long walls of text

**Tone dial.** Enterprise = formal, structured, compliance-aware. Startup = warm, concise, direct. Individual = friendly, low-pressure. Keep all three **respectful and face-saving**.

---

## PER-TARGET PLAYBOOKS

**Bank / enterprise**
- Lead with compliance and user protection. Formal structure. Mention data protection obligations.
- Offer to coordinate with their PSIRT and to keep it confidential.
- Ask for a security contact if the first channel is wrong.
- Escalation is a process step, not a threat.

**Startup**
- Lead with user trust and brand. Short, human, direct.
- Offer to help them fix fast. Be generous; they remember.
- Reward is often a credit or certificate — accept it graciously.

**Big tech**
- Follow the program's format exactly. In-scope, clear repro, CVE if eligible.
- Be patient with triage. Do not spam.

**Individual developer**
- Friendly, non-judgmental. "Easy to miss." Give the fix directly.
- Gratitude matters more than reward.

**CEO / owner**
- Plain language, no jargon. Business impact and liability.
- Give a single, easy next step (forward to your security team).

---

## NEGOTIATION PSYCHOLOGY

- **Ask, do not demand.** "If you have a bounty or recognition program, I'd appreciate consideration. If not, a credit or certificate is fine."
- **Anchor with facts** — impact and fix justify value; do not name a price.
- **Reciprocity** — you gave a free fix; a reward is a fair exchange, framed as mutual.
- **Give them the win** — let them look good publicly and internally.
- **Never negotiate with a threat.** No deadline tied to publishing for leverage.
- **CVE as a good** — "I can help with a CVE request if eligible" adds value to them.
- **Accept small wins** — a "thank you" or credit is still a recorded, usable outcome.

---

## FOLLOW-UP & ESCALATION PSYCHOLOGY

```
Day 0   first contact
Day 7   polite check: "Just confirming receipt — happy to provide anything you need."
Day 14  gentle reminder + one-line severity recap
Day 30  escalation notice, factual: "I'll need to escalate to <CERT/regulator> if unaddressed."
Day 90  coordinated public disclosure
```
- **Escalate the channel, not the emotion.** Calm tone at every step.
- **Never sound like a threat.** Frame escalation as policy and public safety.
- **Persistence reads as professionalism**, not harassment, when the cadence is predictable and polite.

---

## DE-ESCALATION

- **If they are defensive or angry** — acknowledge, reduce threat: "I understand. Let me clarify the impact with a safer, minimal proof."
- **If they ignore you** — continue the cadence; do not escalate emotionally.
- **If they dispute it** — re-explain impact calmly, offer a safer PoC, never argue.
- **If they lowball or dismiss** — stay gracious; document; the record still has value.
- **If you are tempted to react** — pause. Emotional replies destroy credibility.

---

## OUTPUT
- `report.md` — minimal, redacted disclosure report.
- `outreach.md` — the message tailored to the recipient profile.
- `profile.json` — recipient role, incentive, channel, tone, timing.
- Tracker update — status, channel, sent_at, next follow-up.

---

## BOUNDARIES
- Allowed: drafting, tailoring, negotiating recognition, tracking outcomes.
- Not allowed: extortion, threats, inflated impact, raw-data disclosure, harassment, auto-sending without human approval.
- If the user asks to pressure, threaten, or harm a target, refuse and offer the ethical path instead.
