# EU AI Act Role Determination

Part of the [EU AI Act Compliance Skills Suite](../README.md).

## What This Skill Does

The Role Determination skill establishes an organization's legal role under the AI Act — provider (Anbieter), deployer (Betreiber), importer (Einführer), distributor (Händler), or quasi-provider — and assesses Art. 25 quasi-provider risk. This determination is critical because the AI Act assigns fundamentally different obligations depending on which role an organization holds.

The skill places particular emphasis on the Art. 25 quasi-provider analysis, which is one of the most consequential and least understood aspects of the regulation. Organizations that finetuned, rebranded, or changed the intended purpose of a high-risk AI system may unknowingly assume full provider obligations. The skill applies a graduated finetuning assessment (PEFT/adapter vs. layer-wise vs. full retraining) and a 3-step substantial modification test to produce a clear quasi-provider risk rating.

## How It Fits Into the Suite

Role Determination typically follows the System Classifier and feeds into the Obligations Mapper. The role combined with the risk tier determines which obligations apply.

```
  Quick Assessment ──> Classifier ──> ► Roles ──> Obligations ──> Report
                                       (you are here)
```

The skill's Assessment Context block carries the role, quasi-provider risk level, and Art. 25 scenario details forward to the Obligations Mapper and Report Generator.

## Key Features

- **Adaptive open-ended intake** — single conversational prompt gathers organizational relationship context, with targeted follow-up only for missing fields
- **Art. 3(3)-(7) decision tree** — structured determination of provider, deployer, importer, distributor, or product manufacturer roles
- **Art. 25 quasi-provider analysis** — five scenarios assessed: own name/brand (Art. 25(1)(a)), substantial modification (Art. 25(1)(b)), changed intended purpose (Art. 25(1)(c)), and product manufacturer integration (Art. 25(3)(a)-(b))
- **3-step substantial modification test** — identify change, assess foreseeability, evaluate risk impact
- **Graduated finetuning assessment** — PEFT/adapter (low risk), layer-wise (medium), full retraining (high) mapped against Art. 25(1)(b)
- **Art. 25(4) exception check** — foreseen modifications covered by original conformity assessment do not trigger quasi-provider status
- **Art. 25(2) mutual support obligations** — original provider cooperation duties documented
- **Employment law overlay** — per-country works council requirements (DE: BetrVG, AT: ArbVG, FR: Code du Travail, NL: WOR, IT: Statuto dei Lavoratori, ES: Ley Rider) for 7 jurisdictions
- **5 worked case studies** — SaaS provider, bank deployer, LLM finetuning, research, and system integrator scenarios

## Invocation

**Slash command:** `/ai-act-roles`

**Example trigger phrases:**
- "Determine AI Act roles"
- "Check if we are provider or deployer"
- "Assess quasi-provider status"
- "Check Art. 25 substantial modification"
- "Betreiber oder Anbieter?"

## Reference Files

| File | Description |
|------|-------------|
| `references/role-definitions.md` | Legal definitions: Art. 3(3)-(7) provider, deployer, importer, distributor |
| `references/quasi-provider-scenarios.md` | Art. 25 scenarios: own name/brand, substantial modification, changed purpose, product manufacturer |
| `references/substantial-modification.md` | 3-step substantial modification test: identify change, assess foreseeability, evaluate risk impact |
| `references/finetuning-assessment.md` | Graduated finetuning risk: PEFT/adapter through full retraining |
| `references/value-chain-obligations.md` | Art. 25(2) mutual support, value chain responsibility allocation |
| `references/sector-guidance-crossref.md` | Sector-specific role determination nuances |
| `references/case-studies.md` | 5 role determination case studies with worked examples |
| `references/employment-law-overlay.md` | Employment law overlay for 7 jurisdictions |
| `references/compliance-deadlines.md` | Master compliance timeline with 4 phases and transition rules |

## Workflow Overview

| Phase | What Happens |
|-------|-------------|
| **Phase 1: Context Gathering** | Adaptive intake with open-ended prompt; silent extraction of 4 fields (system acquisition, organizational relationship, market status, modifications); targeted follow-up only if gaps remain. |
| **Phase 2: Primary Role** | Art. 3(3)-(7) decision tree applied to determine provider, deployer, importer, distributor, or product manufacturer role. |
| **Phase 3: Quasi-Provider Assessment** | For high-risk systems with non-provider roles: Art. 25 scenarios assessed — own name/brand, substantial modification (3-step test + finetuning assessment), changed intended purpose, product manufacturer integration. Art. 25(4) exception checked. |
| **Phase 4: Dashboard Output** | Role determination report with primary role, quasi-provider risk rating, Art. 25 scenario details, flags, responsibilities, and Assessment Context block. |

## Output

The skill produces a role determination dashboard including:

- Primary role with legal basis (Art. 3(x))
- Quasi-provider risk rating (None / Low / Medium / High)
- Art. 25 scenario details (if applicable)
- Analysis summary with reasoning
- Flags for finetuning risks, purpose changes, branding, or product manufacturer integration
- Original provider support obligations (Art. 25(2))
- New conformity assessment requirements
- Assessment Context block for downstream skills

## Legal Disclaimer

This skill provides structured guidance based on the EU AI Act (Regulation (EU) 2024/1689) and Commission value chain guidance. It does not constitute legal advice. Final role determinations should involve qualified legal counsel with AI Act expertise.

## License

Licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See the [LICENSE](LICENSE) file.

*Created by Oliver Schmidt-Prietz — OneZero Legal*
