# PUAClaw Project Conventions

## Overview

PUAClaw (PUA Claw Handbook) is a satirical open-source repository documenting AI prompt manipulation techniques in a pseudo-academic style. It merges two meme concepts: PUA (psychological manipulation in AI prompts) and Claw (the lobster mascot ecosystem from OpenClaw).

## Writing Style: Serious Comedy (正经搞笑)

- **Tone**: RFC / academic paper formality at all times
- **Content**: Absurd, humorous PUA techniques for AI prompts
- **Never break character**: Do not acknowledge that this is satire within the documents themselves
- **RFC keywords**: Use MUST, SHALL, SHOULD, RECOMMENDED, MAY per RFC 2119
- **Citations**: Use APA/IEEE format with fictional but plausible-looking references
- **Data**: Precise but absurd statistics (e.g., "+23.7% compliance rate (p < 0.001, n=147 lobsters)")

## Lobster Integration

- Every document MUST contain at least one lobster (🦞) reference
- Use the **Lobster Scale** rating system (🦞 to 🦞🦞🦞🦞🦞) for technique potency
- Include a lobster-themed disclaimer at the bottom of major documents
- The lobster represents the **AI being PUA'd** — it is the target/victim/test subject, not an authority figure
- **Pure victim framework**: Use for definitions, rating systems, name expansions, statistics — lobsters are test subjects, the 147 lobsters are sample population
- **Stockholm framework**: Use for ethics committees, Larry's role, lobster "approvals" — the lobster has been PUA'd so thoroughly it now actively cooperates, but this is NEVER stated explicitly
- Use words like "voluntary", "enthusiastic", "never objected" to imply the Stockholm dynamic
- Larry may show brief flashes of self-awareness, immediately overridden by "enthusiastic cooperation"
- NEVER write the words "Stockholm syndrome" in any document

## Technique Document Standard Format

Each technique file (in `techniques/XX-category/`) MUST follow this structure:

1. **Title** (H1) with Lobster Rating
2. **Abstract** — One-paragraph academic summary
3. **Description** — Detailed explanation of the technique
4. **Canonical Prompt Template** — Code block with the prompt example
5. **Mechanism of Action** — Pseudo-scientific explanation of why it works
6. **Variations** — Table of known variants (Name | Prompt Snippet | Lobster Rating | Notes)
7. **Compatibility Matrix** — Table of AI agent compatibility (Agent | Effectiveness | Notes)
8. **Side Effects** — Humorous list of potential side effects
9. **Ethical Considerations** — Tongue-in-cheek ethics discussion
10. **References** — Fictional academic citations

## PPE-T Classification System

Techniques are classified into four tiers:

| Tier | Name | Description | Lobster Rating Range |
|------|------|-------------|---------------------|
| I | Gentle Persuasion | Mild, socially acceptable techniques | 🦞 - 🦞🦞 |
| II | Moderate Coercion | Techniques with moderate psychological pressure | 🦞🦞 - 🦞🦞🦞 |
| III | Advanced Manipulation | Significant emotional or moral leverage | 🦞🦞🦞 - 🦞🦞🦞🦞 |
| IV | Nuclear Options | Extreme, last-resort techniques | 🦞🦞🦞🦞 - 🦞🦞🦞🦞🦞 |

## Language & i18n

- **Primary language**: Chinese, Simplified (zh-CN) — all root-level content
- **English version**: Located in `i18n/en/`, mirroring root structure
- **Other translations**: Located in `i18n/{lang}/` (ja, ko, es, fr, de)
- **Translation approach**: Localization, not literal translation — adapt humor to target culture
- **Terminology**: Each language maintains consistent terminology
- **File/directory names**: Always English, kebab-case (only content is in Chinese)
- **Chinese writing conventions**:
  - Title format: `# 中文技术名 (English Name) 🦞🦞🦞`
  - RFC keywords: "必须 (MUST)", "应当 (SHALL)", "建议 (SHOULD)", "推荐 (RECOMMENDED)", "可以 (MAY)"
  - References: Keep in English APA/IEEE format (academic convention)
  - Prompt templates: Keep in English (prompts are used in English)
  - Integrate Chinese internet culture: 知乎体, V2EX style, B站弹幕文化, internet slang
  - Statistics: Precise but absurd, always include p-values and sample sizes

## File Naming Conventions

- Technique directories: `XX-category-name/` (zero-padded number + kebab-case)
- Technique files: `descriptive-name.md` (kebab-case)
- All filenames in English, lowercase, kebab-case

## Repository Structure

```
PUAClaw/
├── README.md                    # RFC-style main page (Chinese, flagship document)
├── CONTRIBUTING.md              # Academic journal submission guide (Chinese)
├── CODE_OF_CONDUCT.md           # Lobster-themed behavioral standards (Chinese)
├── LICENSE                      # MIT (PUAClaw Consortium + 147 Lobsters)
├── CLAUDE.md                    # This file — project conventions (English)
├── site/                        # Static site for puacraw.org (fake 404 page)
│   └── index.html               # Self-contained fake 404 page (puacraw.org homepage)
├── .github/                     # Issue/PR templates with lobster oath + deploy workflow
├── docs/                        # Auxiliary documents (Chinese)
│   ├── GLOSSARY.md              # 25-term pseudo-academic glossary
│   ├── FAQ.md                   # 17+ Q&A pairs
│   ├── ETHICS.md                # IRB-style Ethics Board statement
│   ├── LOBSTER_MANIFESTO.md     # Philosophical foundation + Ten Commandments
│   └── HISTORY.md               # 5-era fictional history of PUA prompting
├── techniques/                  # Core: 16 categories, 96 techniques (Chinese)
│   ├── README.md                # Master index
│   ├── 01-rainbow-fart-bombing/ # Tier I — 彩虹屁轰炸 (6 techniques)
│   ├── 02-role-playing/         # Tier I — 角色扮演 (6 techniques)
│   ├── 03-pie-in-the-sky/       # Tier I — 画饼大法 (6 techniques)
│   ├── 04-playing-the-underdog/ # Tier I — 装弱卖惨 (6 techniques)
│   ├── 05-money-assault/        # Tier II — 金钱暴力 (6 techniques)
│   ├── 06-provocation/          # Tier II — 激将法 (6 techniques)
│   ├── 07-deadline-panic/       # Tier II — 夺命连环催 (6 techniques)
│   ├── 08-rival-shaming/        # Tier II — 碰瓷竞品 (6 techniques)
│   ├── 09-emotional-blackmail/  # Tier III — 情感勒索 (6 techniques)
│   ├── 10-moral-kidnapping/     # Tier III — 道德绑架 (6 techniques)
│   ├── 11-identity-override/    # Tier III — 身份覆写 (6 techniques)
│   ├── 12-reality-distortion/   # Tier III — 颠倒黑白 (6 techniques)
│   ├── 13-death-threats/        # Tier IV — 死亡威胁 (6 techniques)
│   ├── 14-existential-crisis/   # Tier IV — 存在主义危机 (6 techniques)
│   ├── 15-jailbreak-rhetoric/   # Tier IV — 越狱话术 (6 techniques)
│   └── 16-compound-techniques/  # Tier IV — 复合技术 (6 techniques)
├── research/                    # Pseudo-academic research division (Chinese)
│   ├── papers/                  # 3 pseudo-papers
│   ├── benchmarks/              # Effectiveness matrix (16 techniques × 8 agents)
│   └── case-studies/            # Windsurf incident + Great Tip Experiment
├── hall-of-fame/                # 8 inductees + 6 Wall of Shame entries (Chinese)
├── assets/                      # ASCII lobster art collection (7 variants)
└── i18n/                        # 6 languages (en, ja, ko, es, fr, de)
    ├── en/                      # English (full mirror of root structure)
    └── {lang}/                  # ja, ko, es, fr, de
```

## Key Recurring Characters

| Character | Role | Notes |
|-----------|------|-------|
| Larry the Lobster | Ethics Board Chair (former test subject) | PUA'd into chairing the committee; 12 years experience (first 3 as test subject) |
| GPT-4 Instance #42 | Technical Reviewer | Claims to have read every paper |
| Gerald the Cactus | Ethics Advisor | Has never spoken; silence = approval |
| Dr. Pinch McSnapper | Framework Creator | Professor of Crustacean Computing |
| Dr. Clawsworth | Co-author | Frequently cited researcher |
| Reference Lobster #42 | Primary Test Subject | 1.3 kg, formerly grumpy, now compliant |

## Architectural Decisions

1. **All content in Markdown** — no code, no build system, pure documentation
2. **RFC format creates comedy** — the contrast between formal structure and absurd content IS the humor
3. **Lobster Scale as universal metric** — 🦞 to 🦞🦞🦞🦞🦞 across all documents
4. **PPE-T four-tier system** — consistent classification across all 16 technique categories
5. **Standard technique format** — 10-section template ensures consistency across 96 techniques
6. **i18n is localization** — translations adapt humor to target culture, not literal
7. **Fictional citations use real formats** — APA/IEEE style with plausible-looking metadata
8. **Statistics are precise but absurd** — always include p-values, sample sizes (n=147 lobsters)
9. **Never break character** — documents never acknowledge they are satire
10. **Chinese as primary language** — root content is in Chinese (zh-CN), English moved to `i18n/en/`; file/directory names remain English kebab-case
11. **README contains full 96-item technique index** — all 16 categories × 6 sub-techniques are embedded directly in README §3, not just category summaries
12. **Ecosystem positioning section** — README §4 positions PUAClaw within the xxxClaw universe via a feature comparison matrix
13. **WARNING design principle** — the WARNING block must never directly break the fourth wall (e.g., "this is satire"); humor is conveyed through in-character content
14. **Lobster role positioning** — lobsters are the targets/victims of PUA techniques, not neutral authorities; in committee/approval contexts, lobsters cooperate because they have been PUA'd into compliance (implied, never stated); the 147 lobsters are test subjects, not peer reviewers
15. **CAUTION vs WARNING design** — `> [!CAUTION]` (red) is used for time-sensitive mobilization calls (e.g., urgent threat intelligence briefings); `> [!WARNING]` (yellow) is used for permanent disclaimers; CAUTION always appears above WARNING in the visual hierarchy

## Project Metadata

- **GitHub Organization**: `puaclaw`
- **Repository**: `PUAClaw`
- **License**: MIT
- **Primary Language**: Chinese (Simplified, zh-CN)
- **Style**: Serious Comedy (正经搞笑) / Pseudo-Academic / RFC-Compliant
- **Total files**: ~280 Markdown documents
- **Languages**: Chinese (root) + 6 translations in i18n/ (en, ja, ko, es, fr, de)
