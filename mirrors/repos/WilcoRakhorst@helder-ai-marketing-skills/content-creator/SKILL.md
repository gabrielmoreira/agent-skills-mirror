---
name: content-creator
description: "Create SEO-optimized marketing content with a consistent brand voice. Includes brand voice frameworks, SEO optimizer, content templates, and social media guides. Use when writing blog posts, social media content, developing brand voice, optimizing for SEO, planning content calendars, or when terms like 'content creation', 'brand voice', 'SEO optimization', 'social media marketing', 'blog writing', or 'content strategy' are mentioned."
---

# Content Creator — Strategic Hub

This skill is the **upstream source** for all content. Here you determine the angle, do keyword research, and write brand-consistent text. Publishing to WordPress can be automated via the REST API (see workflow below).

```
Content Creator (this skill)      →  WordPress REST API / CMS
Angle, copy, SEO, voice              HTML blocks, meta tags, publishing
```

## Core workflow — from idea to publication

| Step | What                          | Skill/tool                              |
|:-----|:------------------------------|:----------------------------------------|
| 1    | Angle and keyword             | `seo-keyword-research` or this skill    |
| 2    | Outline + audience scenarios  | `references/content-frameworks.md`      |
| 3    | Write first draft             | Apply brand voice guidelines (see below)|
| 4    | Brand voice check             | Voice rules below + anti-AI filter      |
| 5    | SEO pre-check                 | Signal words, sentence length, keyword  |
| 6    | Proofreading                  | Style control checklist (see below)     |
| 7    | Publish                       | WordPress REST API or manual CMS entry  |

**Step 2 — audience scenarios:** When creating the outline, think about how different audience segments each get a recognizable example. **Check:** does the outline contain at least one specific practical example per key audience? If not, add these before writing.

**Step 3 — hook-first (GEO):** Open every blog article with the core solution or answer in the first two sentences. Avoid long introductions like "In today's world...". This increases the chance that AI search engines (Perplexity, ChatGPT) cite your text as a source.

**Step 3 — E-E-A-T signature:** Look for at least one moment in each article where you can insert first-hand experience ("When I recently visited a client...", "A customer asked me..."). This significantly boosts the Experience score.

**Step 7 — handoff checklist:** When content is ready for publishing, always include:
1. The primary keyphrase
2. The meta description (max 155 characters)
3. All verified source URLs

## Brand voice framework

Choose your brand archetype (see `references/brand-guidelines.md` for the full framework):

**Archetypes:**
- **The Guide** — Wise, patient, instructional. "Let's walk through this together..."
- **The Expert** — Knowledgeable, confident, data-driven. "Research shows that 87% of..."
- **The Friend** — Warm, supportive, conversational. "We get it — marketing can be overwhelming..."
- **The Innovator** — Visionary, bold, forward-thinking. "The future of marketing is here..."
- **The Motivator** — Energetic, positive, inspiring. "You have the power to transform..."

### Writing principles

- **Clarity first:** use simple words, break complex ideas into digestible pieces, lead with the main message
- **Reader-focused:** focus on benefits not features, address pain points directly, use "you" more than "we"
- **Consistency:** same voice across all channels, use approved terminology, follow formatting standards
- **Active voice:** 80% of the time

### Anti-AI word list

These words signal AI-generated text and reduce reader trust:

| Avoid                     | Use instead                          |
|:--------------------------|:-------------------------------------|
| unleash                   | leverage, use                        |
| dive into                 | explore, read more about             |
| revolutionary             | innovative, practical                |
| groundbreaking            | notable, interesting                 |
| game-changer              | major step forward                   |
| seamless                  | smooth, effortless                   |
| cutting-edge              | modern, current                      |
| harness the power         | use the capabilities                 |
| in this digital age       | today, in practice                   |
| transform your business   | improve your workflow                |
| a world of ...            | many possibilities for ...           |

**Burstiness rule:** Vary sentence length. Avoid starting 3+ consecutive sentences with the same word. Mix short punchy sentences with longer explanatory ones.

## SEO + Yoast pre-check

Before publishing, run through this check:

### Keyword
- Focus keyword in title, first paragraph, and 2-3 H2 headings
- Density: 3x at 750 words, 5x at 1,500 words
- Focus keyword in meta description (max 155 characters)

### Readability
- **Flesch score**: At least 60 ("standard/plain English") — 70+ = "fairly easy". Note: since Yoast SEO 19.3 (July 2022), Flesch is shown in the Insights tab only; the active readability analysis now uses **word complexity** and **sentence length** checks instead.
- **Transition words**: At least 30% of sentences contain a transition word. **Vary position** — not only at the start, also mid-sentence ("...is therefore...", "...however works...") to maintain natural rhythm
- **Sentence length**: Max 25% of sentences longer than 20 words
- **Passive voice**: Max 10% passive sentences
- **Paragraph length**: No paragraphs longer than 150 words
- **Consecutive sentences**: Don't start 3+ sentences in a row with the same word

### Word count
- Standard blog post: **800-1,200 words**
- In-depth article: **1,200-1,800 words**
- Short update/news: **400-800 words**

---

## References

- Yoast (2025): "The Flesch reading ease score: Why & how to use it" — score 60–69 = "Standard" (plain English) — yoast.com/flesch-reading-ease-score/
- Note: Since Yoast SEO 19.3 (July 2022), Flesch is no longer an active readability check; replaced by word complexity + sentence length assessments
- Google Search Central: Creating helpful content — developers.google.com/search/docs/fundamentals/creating-helpful-content

Longer texts only when the topic demands it — for a busy professional, brevity is a quality.

## WordPress REST API automation

Content publishing can be automated via the WordPress REST API:

**Creating a post:**
```
POST /wp-json/wp/v2/posts
{
  "title": "Your Post Title",
  "content": "<!-- wp:paragraph --><p>Your content...</p><!-- /wp:paragraph -->",
  "status": "draft",
  "categories": [category_id],
  "meta": {
    "_yoast_wpseo_title": "SEO Title %%sep%% %%sitename%%",
    "_yoast_wpseo_metadesc": "Your meta description here"
  }
}
```

**What you can automate:**
- Post creation (title, content, categories, tags)
- Yoast SEO title and meta description
- Featured image (upload via `/wp-json/wp/v2/media`, then set `featured_media`)
- Post status (draft → publish)

**What typically requires manual action:**
- Yoast focus keyphrase (not always exposed via REST API)
- Final visual review in the editor

## Social media — repurposing

One blog post can yield:
- 1 LinkedIn post (core message + personal experience)
- 1 newsletter block (summary + link)
- 1-2 Instagram/Facebook posts (visual quote or tip)

Platform-specific guidelines: see `references/social-media-optimization.md`

## Proofreading checklist

After writing, before publishing:

- [ ] **Anti-AI filter**: No words from the banned list above
- [ ] **Audience check**: Are different audience segments organically represented (where relevant)?
- [ ] **Sources**: Every statistic or claim has a source URL
- [ ] **Transition words**: At least 30% of sentences
- [ ] **Sentence length**: Max 25% over 20 words
- [ ] **Jargon**: No technical terms without explanation in reader-facing content
- [ ] **Special characters**: Mark characters needing HTML entity conversion for web publishing

## Common mistakes

- Writing before doing keyword research
- Sending text straight to CMS without SEO pre-check
- Leaving AI clichés in ("unleash the power of AI")
- Citing statistics without a source URL
- Writing over 1,800 words without good reason
- Not adapting content per platform/audience
- Publishing without the anti-AI filter
- Placing transition words only at the start of sentences
- Opening articles with a long introduction instead of the answer (hurts GEO score)
- No first-hand experience in the content (hurts E-E-A-T)

## References

| File                                       | Purpose                                             |
|:-------------------------------------------|:----------------------------------------------------|
| `references/brand-guidelines.md`           | Brand voice, voice attributes, word choices         |
| `references/content-frameworks.md`         | Templates per content type, reuse matrix            |
| `references/social-media-optimization.md`  | Platform-specific guidelines, hashtag strategy      |

---

## Data integrity

- NO percentages, numbers, or statistics without a documented source
- NO comparative claims without evidence
- Every statistic must have a source URL
- When in doubt: leave it out, never guess
