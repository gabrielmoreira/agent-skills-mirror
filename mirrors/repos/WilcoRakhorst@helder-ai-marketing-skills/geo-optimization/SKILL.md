---
name: geo-optimization
description: "Generative Engine Optimization (GEO): optimize content for AI search engines like ChatGPT, Gemini, Copilot, and Perplexity. Use when the user wants to optimize content for AI visibility, estimate a GEO score, write AI-friendly content, or when terms like 'GEO', 'generative engine optimization', 'AI visibility', 'visible in ChatGPT', 'visible in Gemini', 'AI search engine', 'GEO score', 'AI-friendly content', 'get cited by AI', 'GEO marketing', 'SEO vs GEO', 'content for AI', 'AI-proof content', or 'GEO strategy' are mentioned."
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

## AI platforms

| Platform              | Data source                    | Notes                                          |
|:----------------------|:-------------------------------|:-----------------------------------------------|
| **ChatGPT (OpenAI)**  | Training data + live browsing  | Browse mode fetches current pages              |
| **Google Gemini**      | Google Search index            | Tied to Google's own search results            |
| **Perplexity**         | Active web scraping            | Explicitly cites sources with attribution      |
| **Microsoft Copilot**  | Bing index + Microsoft Graph   | Bing SEO counts extra; schema markup important |

**Google AI Overviews** (formerly SGE) displays answers directly in search results based on trustworthy, structured content.

## Testing AI visibility

1. Ask relevant questions in ChatGPT, Gemini, and Perplexity (expertise + region)
2. Note whether your brand is mentioned or only competitors
3. Check if cited content matches your website
4. Repeat periodically (models are updated regularly)

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
- **Tables:** LLMs frequently use Markdown tables as-is for summaries
- **Factual anchors (hallucination killer):** The more specific you write, the more likely AI uses your text as an anchor. Name exact tools, dates, locations, and software packages ("integrates via API with SAP, Salesforce, and Microsoft Dynamics 365" instead of "integrates with many systems"). Present results with start and end points; LLMs anchor on linear progression.

## Brand association

AI builds a knowledge graph. Goal: make your brand name inseparable from your expertise topic.

- **Co-occurrence:** brand name next to niche terms, also on external platforms (guest blogs, industry sites, press releases)
- **Unique terminology:** introduce your own method or model; when people ask about it, AI must mention your brand
- **Dataset schema:** own research or data? Use Dataset schema markup so AI recognizes you as a source
- **Source diversity:** AI trusts a source faster when multiple platform types say the same thing. Ensure your core message and unique terms also appear on high-authority places that LLMs weigh heavily: Reddit, specialized industry forums, industry association sites. Positive mentions in unstructured data (forum discussions, reviews) reinforce the trustworthiness of your official web content.
- **Reddit factor:** LLMs (especially ChatGPT and Gemini) appear to weigh discussion platforms like Reddit and Quora heavily for "human recommendations" (widely observed in the SEO community; no peer-reviewed source). Organic discussion of your brand or method in relevant subreddits is to GEO what link building was to SEO.

## GEO improvement strategy

1. **Pillar content:** main article per core topic, core question fully answered, definitions, links to supporting content
2. **Supporting content:** in-depth articles and checklists that link back to the pillar
3. **Conversational mapping:** anticipate follow-up questions. The pillar explains what something is, supporting content directly answers "How do I implement this?". Use bridge sentences ("Once the audit is complete, the next step is...") so AI understands the logical chain.
4. **Optimize existing content:** add definitions, convert headings to question format, add internal links, include author information
5. **Combine SEO + GEO:** SEO = getting found, GEO = getting used by AI

## Anti-patterns & references

See [references/anti-patterns-and-references.md](references/anti-patterns-and-references.md).

## Data integrity

- Only verified facts; GEO is an emerging field, be transparent about what is proven
- No percentages or statistics without a source
- When uncertain: "This is an estimate based on current understanding of AI search engines"

## References

- Aggarwal, P. et al. (2024): "GEO: Generative Engine Optimization", KDD 2024 — arxiv.org/abs/2311.09735 (visibility boost up to 40%; citations, quotations, statistics as top strategies; keyword stuffing ineffective)
- Google Search Central: "Creating helpful, reliable, people-first content" (E-E-A-T framework) — developers.google.com/search/docs/fundamentals/creating-helpful-content
- Google Search Quality Rater Guidelines (E-E-A-T criteria) — services.google.com/fh/files/misc/hsw-sqrg.pdf
- Google (2023): "Google Search and AI content" — developers.google.com/search/blog/2023/02/google-search-and-ai-content

## Evidence status

What is **proven** (peer-reviewed or official source):

| Claim | Source |
|:------|:-------|
| GEO can boost visibility up to 40% | Aggarwal et al. 2024, KDD |
| Citations, quotations, and statistics are top strategies | Aggarwal et al. 2024, KDD |
| Keyword stuffing does NOT work for GEO | Aggarwal et al. 2024, KDD |
| E-E-A-T as ranking principle (Experience, Expertise, Authoritativeness, Trust) | Google Search Central |
| Trust is the most important E-E-A-T factor | Google Search Central |
| AI platforms: Perplexity cites sources explicitly | Aggarwal et al. 2024, tested on Perplexity.ai |
| Content for people > content for systems | Google Helpful Content guidelines |

What is **own interpretation** (not independently validated):

| Claim | Basis |
|:------|:------|
| "5 signals" and their ranking order | Derived from GEO paper + Google guidelines; the priority order is editorial, not empirically tested |
| GEO scorecard (16 criteria, max 80, score bands) | Own practical framework; criteria are reasonable but thresholds (45/65/80) are not validated |
| "Quick GEO check" (5 questions) | Simplified self-assessment; no scientific validation |
| Content length guidelines (600/1,200/1,500+ words) | Industry consensus, not from a peer-reviewed study |
| GEO improvement strategy (5 steps) | Best-practice synthesis; not experimentally proven as a method |
| Conversational mapping / bridge sentences | Logical inference; no study proves AI follows these chains |

What is **widely observed but unproven**:

| Claim | Status |
|:------|:-------|
| Reddit factor (LLMs weigh Reddit/Quora heavily) | Observed by SEO community; no peer-reviewed confirmation |
| AI platforms table (ChatGPT browse mode, Gemini via Google index, Copilot via Bing) | Based on public product documentation; subject to change without notice |
| Brand association via co-occurrence | Plausible based on how embeddings work; not experimentally proven for GEO |
| Dataset schema markup helps AI recognition | Logical but not tested in GEO research |
