---
name: geo-optimization
description: "Generative Engine Optimization (GEO): optimize content for AI search engines like ChatGPT, Gemini, Copilot, and Perplexity. Use when the user wants to optimize content for AI visibility, estimate a GEO score, write AI-friendly content, or when terms like 'GEO', 'generative engine optimization', 'AI visibility', 'visible in ChatGPT', 'visible in Gemini', 'AI search engine', 'GEO score', 'AI-friendly content', 'get cited by AI', 'GEO marketing', 'SEO vs GEO', 'content for AI', 'AI-proof content', or 'GEO strategy' are mentioned."
context: fork
---

# GEO — Generative Engine Optimization

GEO = optimizing content so that AI search engines (ChatGPT, Gemini, Copilot, Perplexity) include your brand in generated answers. Core question: "Is my brand being mentioned by AI?"

**Related skills:** seo-strategy (technical SEO, on-page, internal links, content clusters) | seo-keyword-research (keywords) | content-creator (writing & publishing)

SEO and GEO are complementary. Without an SEO foundation, GEO is impossible. Related terms (AI SEO, LLM SEO, LEO, AEO, AIO) all refer to the same goal.

| Aspect            | SEO                              | GEO                                    |
|:------------------|:---------------------------------|:---------------------------------------|
| **Result**        | List of websites (SERP)         | Summarized answer                      |
| **Focus**         | Keywords, technical ranking      | Meaning, intent, relationships         |
| **Measurable via**| Rankings, clicks, traffic        | Mentions, authority, brand recognition |

**When to use which approach:** GEO-first for long-tail (complex, specific questions) where AI Overviews take the most space. SEO-first for navigational and transactional searches where the traditional blue link still dominates for clicks.

## How AI selects sources

Five signals (based on GEO research + Google's helpful content guidelines; ranking is a practical prioritization, not an empirically proven hierarchy):

1. **Direct answer:** Lead with the definition, not a lengthy introduction
2. **Completeness:** Topic fully covered with connections; comprehensive articles win over short posts
3. **Recognizable expertise:** Practical examples, nuance, specific insights; generic content gets ignored
4. **Structure:** Clear headings (H2/H3), short paragraphs, logical flow
5. **Domain consistency:** Multiple articles + internal links + expertise direction = topical authority

**Technical signals:** crawlers/indexes (Google + Bing) | semantic structure (H1-H3, definitions) | schema markup | internal links | backlinks | consistent brand name as entity

### FAST framework: AI crawlability test

Load pages with JavaScript disabled — what you see is what GPTBot, ClaudeBot, and PerplexityBot see. Dimensions: **F**etchable, **F**ree bot access, **A**ccessible content, **S**tructured markup, **S**chema drift, **S**upporting llms.txt, **T**rimmed DOM.

See [references/fast-framework.md](references/fast-framework.md) for the full checklist, recommended robots.txt config, and llms.txt template.

## AI platforms

| Platform              | Data source                    | Citation preference                                      | Optimize for                                         |
|:----------------------|:-------------------------------|:---------------------------------------------------------|:-----------------------------------------------------|
| **ChatGPT (OpenAI)**  | Training data + live browsing  | Authority (47.9% Wikipedia-like sources)                 | Entity recognition, authoritative fact claims        |
| **Google Gemini**      | Google Search index            | Brand websites (52% from brand domains)                  | Organization schema, brand consistency               |
| **Perplexity**         | Active web scraping            | Freshness (46.7% Reddit/community sources)               | Recent data with dates, frequent updates             |
| **Microsoft Copilot**  | Bing index + Microsoft Graph   | Bing SEO + schema markup                                 | Technical SEO, structured data                       |
| **Claude**             | Primary sources                | Original research (91.2% attribution accuracy)           | Cited statistics, self-contained paragraphs          |

**Google AI Overviews** (formerly SGE) displays answers directly in search results based on trustworthy, structured content — E-E-A-T and schema markup carry the most weight.

*Citation percentages: Princeton/Georgia Tech research + BrightEdge data 2025-2026. See also `references/anti-patterns-and-references.md`.*

## Testing AI visibility

### Monthly manual audit process

Run a fixed citation audit every month with 20 representative questions your target audience asks:

1. Ask the 20 questions in ChatGPT, Perplexity, Gemini, and Copilot
2. Note per platform per question: cited (yes/no) + correctly described (correct/partial/wrong)
3. Scoring: cited + correct = 2 pts | cited + incorrect = 1 pt | not cited = 0 pts
4. Compare the total score monthly to track progress

**Platform priority order (by reach):**
1. ChatGPT Search + Google AI Overviews — largest reach
2. Perplexity — fastest growing, strong source attribution
3. Copilot + Claude — significant user bases

### AI traffic benchmarks (2025-2026)

| Metric | Baseline | Good | Excellent |
|:-------|:---------|:-----|:----------|
| AI citation rate (target questions) | < 10% | 25-50% | > 50% |
| Brand name accuracy in AI answers | < 70% | 80-90% | > 95% |
| AI traffic growth (year-over-year) | < 50% | 100-300% | > 300% |

**AI traffic distribution by platform (June 2025):** ChatGPT 85.79% | Gemini 4.70% | Perplexity 2.84% | Grok 2.50% | Claude 2.23% | Copilot 1.60%

AI visitors convert on average **4.4× better** than traditional organic search traffic. Total AI referral traffic: ~1.13 billion visits/month with 357% year-over-year growth.

*Source: Backlinko/Semrush AI Traffic Report 2025*

## GEO scorecard

Practical assessment framework (own model, not scientifically validated; based on principles from Aggarwal et al. 2024 and Google E-E-A-T guidelines). Each criterion 1-5, total max 80:

| Criterion                  | Question                                                         |
|:---------------------------|:-----------------------------------------------------------------|
| **Content depth**          | Do articles go in-depth (1,200+ words)?                          |
| **Structure**              | H1-H3 headings, paragraphs, and lists used consistently?        |
| **Question-answer format** | Does content explicitly answer asked questions?                  |
| **Definitions**            | Clear, citable definitions on the site?                          |
| **Internal links**         | Related pages linked to each other?                              |
| **Content clusters**       | Core topics with supporting articles?                            |
| **Brand positioning**      | Brand and expertise consistently mentioned?                      |
| **E-E-A-T signals**        | Author, experience, and expertise visible?                       |
| **Readability**            | Written for people, not for keywords?                            |
| **Freshness**              | Content regularly updated?                                       |
| **Citability**             | Short soundbites and step-by-step guides present?                |
| **Data visualization**     | Tables or lists that summarize data?                             |
| **Unique perspective**     | Unique insight or proprietary methodology present?               |
| **External validation**    | Is the brand mentioned on Reddit, forums, or review sites?       |
| **Niche association**      | Does the brand appear on external industry websites?             |
| **Sentiment**              | Is online coverage of the brand positive?                        |

**Interpretation:** 65-80 AI authority (direct mentions and citations) / 45-64 strong foundation (mentioned for specific queries) / under 45 invisible to AI (focus on structure and expertise).

**Quick GEO check (5 questions):** Does the site answer audience questions? | Do blog posts go in-depth? | Topics internally linked? | Brand consistently present? | Content written for people?

### Extended scoring model: CORE-EEAT (80 items)

For in-depth audits, the CORE-EEAT model is used, with 8 dimensions across two systems:

| System | Focus | Dimensions | Score |
|:-------|:------|:-----------|:------|
| **CORE** | GEO — AI citability | C (Contextual Clarity), O (Organization), R (Referenceability), E (Exclusivity) | GEO Score = (C+O+R+E) / 4 |
| **EEAT** | SEO — source authority | Exp (Experience), Ept (Expertise), A (Authority), T (Trust) | SEO Score = (Exp+Ept+A+T) / 4 |

**Total score:** (GEO Score + SEO Score) / 2 — scale: 90-100 Excellent / 75-89 Good / 60-74 Moderate / 40-59 Low / 0-39 Poor

**Critical veto items** (one fail = score capped at max 60/100):
- **T04** — Affiliate links without disclosure
- **C01** — Clickbait: title promises something the page doesn't deliver
- **R10** — Data on the page contradicts itself

*Source: CORE-EEAT Content Benchmark v3.0 — github.com/aaron-he-zhu/seo-geo-claude-skills*

## GEO content writing guidelines

**Structure:** question-answer in H2/H3 | lead with the answer | short paragraphs (max 3-4 sentences) | definitions in opening paragraphs | bullet points | clear conclusion

**Content length:** under 600 words is too thin | 1,200-1,800 for supporting content | 1,500-2,500 for pillar content. Completeness > length.

**Language:** write as an expert, naturally and clearly | use the exact questions your audience asks | citable answers | no jargon without explanation

**Tone:** educational and neutral; commercial language ("the absolute best", "revolutionary") gets filtered as bias. Consistent voice across all channels so AI builds a stable expertise profile.

**Internal links and content clusters:** see the seo-strategy skill for pillar/supporting structure and anchor texts.

### E-E-A-T signals

| Element               | Application                                              |
|:----------------------|:---------------------------------------------------------|
| **Experience**        | Share first-hand experiences and case studies             |
| **Expertise**         | In-depth, domain-specific content                        |
| **Authoritativeness** | Content clusters, visible authorship                     |
| **Trustworthiness**   | Source citations, author information, publication dates   |

**AI as a tool:** use AI for research, structure, and first drafts. Always add your own expertise. Mass content without editorial review fails.

## Citability (citation triggering)

AI chops text into snippets to cite. The easier your content is to cite, the more often AI mentions you.

- **Soundbites:** core conclusions in a powerful, self-contained sentence
- **Definition blocks:** fixed pattern — [Term] is [Definition]. This works by [Mechanism].
- **Statistical anchors:** your own unique data; AI looks for data to support claims
- **Step-by-step lists:** numbered lists are often adopted verbatim
- **Optimal passage length:** 134-167 words per paragraph for maximum citation chance — too short = no context, too long = AI picks a fragment. *(Source: AgriciDaniel/claude-seo GEO-skill, February 2026)*
- **Tables:** LLMs frequently use Markdown tables as-is for summaries
- **Factual anchors (hallucination killer):** The more specific you write, the more likely AI uses your text as an anchor. Name exact tools, dates, locations, and software packages ("integrates via API with SAP, Salesforce, and Microsoft Dynamics 365" instead of "integrates with many systems"). Present results with start and end points; LLMs anchor on linear progression.

### Top 6 GEO-First priorities (highest impact on AI citations)

| Rank | Item | What it involves | Priority |
|:-----|:-----|:----------------|:---------|
| 1 | **Direct Answer** | Core answer in the first 150 words | All AI engines |
| 2 | **FAQ Coverage** | Structured FAQ with question-answer format | Follows direct search query structure — use FAQPage schema ONLY for government and health authorities (restricted Aug 2023); for commercial sites: HTML structure without schema |
| 3 | **Data Tables** | Comparison data in HTML tables | Most extractable format |
| 4 | **Schema Markup** | Correct JSON-LD matching content type | Helps AI understand content type |
| 5 | **Original Data** | Own research, own statistics | AI prefers exclusive sources |
| 6 | **Summary Box** | TL;DR or "Key takeaways" block | Often cited first |

**Engine-specific focus:**

| Engine | Priority items | Citation style |
|:-------|:---------------|:---------------|
| **Google AI Overviews** | C02, O03, O05, C09 | Snippet extraction from paragraphs, lists, tables, FAQs |
| **ChatGPT Browse** | C02, R01, R02, E01 | Conversational with source links |
| **Perplexity** | E01, R03, R05, Ept05 | Multi-source synthesis + inline citations |
| **Claude** | R04, Ept08, Exp10, R03 | Precision focus with nuanced argumentation |

*Source: CORE-EEAT Content Benchmark v3.0, aaron-he-zhu/seo-geo-claude-skills*

### Princeton GEO methods (proven citation impact)

Ranked by measured impact on AI citations. Source: Princeton KDD 2024 (10,000 searches on Perplexity.ai), extended by AutoGEO ICLR 2026 to 47 methods.

| Priority | Method | Impact | Application |
|:---------|:-------|:-------|:------------|
| 🔴 1 | **Cite sources** | +30-115% | Add authoritative external links for every claim |
| 🔴 2 | **Add statistics** | +40% | Concrete numbers, percentages, and dates |
| 🟠 3 | **Expert quotes** | +30-40% | Format: *"Text" — Name, Title, Organization, Year* |
| 🟠 4 | **Authoritative tone** | +6-12% | Confident, expert-level phrasing |
| 🟡 5 | **Fluent language** | +15-30% | Clear and direct writing, no padding |
| 🟡 6 | **Accessibility** | +8-15% | Explain terms, use analogies |
| 🟢 7 | **Domain jargon (correct)** | +5-10% | Proper terminology for the sector |
| 🟢 8 | **Varied vocabulary** | +5-8% | Deliberately vary word choice |
| ❌ 9 | **Keyword stuffing** | ~0% ⚠️ | Do not apply — neutral to negative effect |

*Tip:* Combine methods 1 + 2 + 3 for maximum impact: a claim with a statistic + external source + expert quote scores on all three at once.

## Brand association

AI builds a knowledge graph. Goal: make your brand name inseparable from your expertise topic.

**Brand mentions > backlinks:** Brand mentions correlate 3× more strongly with AI visibility than backlinks. Signal strength by platform (correlation with AI citations):

| Platform | Correlation | Priority |
|:---------|:-----------|:---------|
| YouTube mentions | ~0.737 | Strongest signal |
| Reddit mentions | high | Very strong |
| Wikipedia presence | high | Very strong |
| LinkedIn presence | medium | Supplementary |
| Domain authority (backlinks) | ~0.266 | Weak signal |

*Source: Ahrefs research December 2025, 75,000 brands. Via AgriciDaniel/claude-seo.*

- **Co-occurrence:** brand name next to niche terms, also on external platforms (guest blogs, industry sites, press releases)
- **Unique terminology:** introduce your own method or model; when people ask about it, AI must mention your brand
- **Entity SEO (sameAs):** link your brand as an entity to Wikidata, Wikipedia, and all social profiles via `sameAs` in Organization schema. AI models build a knowledge graph based on entities — a brand recognizable as an entity across multiple platforms gets cited more quickly and described more accurately.
  ```json
  "sameAs": [
    "https://en.wikipedia.org/wiki/...",
    "https://www.wikidata.org/wiki/...",
    "https://www.linkedin.com/company/...",
    "https://www.youtube.com/@..."
  ]
  ```
- **Source diversity:** AI trusts a source faster when multiple platform types say the same thing. Ensure your core message and unique terms also appear on high-authority places that LLMs weigh heavily: Reddit, specialized industry forums, industry association sites. Positive mentions in unstructured data (forum discussions, reviews) reinforce the trustworthiness of your official web content.
**GEO market perspective (2025-2026):** GEO services market $850M+ (growing to $7.3B in 2031, 34% CAGR) | AI referral traffic +527% year-over-year (SparkToro) | Google AI Overviews: 1.5 billion users/month | Only 23% of marketers actively invest in GEO (2025). *Source: Yahoo Finance/Superlines, SparkToro, Ahrefs Dec 2025, Gartner*

## AEO — Answer Engine Optimization

AEO (Answer Engine Optimization) targets **zero-click rich results**: answers that appear directly on the search results page, before AI Overviews. Complementary to GEO.

| AEO target | Technique | Optimal length |
|:-----------|:----------|:---------------|
| **Featured Snippet** | Direct answer after a relevant H2/H3 | 40-55 words |
| **People Also Ask (PAA)** | H2/H3 exactly as the question, direct answer below | 30-50 words |
| **Knowledge Panel** | Wikipedia + Wikidata QID + `sameAs` schema | Entity presence |

## GEO improvement strategy

1. **Pillar content:** main article per core topic, core question fully answered, definitions, links to supporting content
2. **Supporting content:** in-depth articles and checklists that link back to the pillar
3. **Conversational mapping:** anticipate follow-up questions. The pillar explains what something is, supporting content directly answers "How do I implement this?". Use bridge sentences ("Once the audit is complete, the next step is...") so AI understands the logical chain.
4. **Optimize existing content:** add definitions, convert headings to question format, add internal links, include author information
5. **Combine SEO + GEO:** SEO = getting found, GEO = getting used by AI

## Anti-patterns & references

See [references/anti-patterns-and-references.md](references/anti-patterns-and-references.md).

## Evidence status

See [references/evidence-status.md](references/evidence-status.md) for a breakdown of proven, own-interpretation, and widely-observed-but-unproven claims.
