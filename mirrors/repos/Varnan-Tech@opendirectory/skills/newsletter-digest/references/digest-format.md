# Digest Format Reference

Rules for structuring newsletter digests. Read this before generating any content.

---

## Three Digest Formats

### Format 1: Weekly Roundup

Use for: General weekly digest covering top stories across all monitored feeds.

Target length: 350-500 words.

Structure:
1. **This Week in [Topic/Industry]** — one sentence capturing the week's theme
2. **Top Story** — 100-150 words on the single most significant story. Include one specific data point or quote from the source.
3. **Also Worth Reading** — 3-5 stories, each 40-60 words with a source attribution link
4. **Quick Takes** — 3-5 one-line bullets for minor stories
5. **Until Next Week** — 1-2 sentence closing

Example section structure:

```
This Week in Developer Tools

The npm ecosystem had a rough week.

Top Story
[Title as H3]
[100-150 word summary. Every stat from the source. Source attribution link at end.]

Also Worth Reading
[Title as H3, linked to article]
[40-60 words. Key insight. [Source: Name](URL)]

Quick Takes
- [One-line summary. Source.](URL)
- [One-line summary. Source.](URL)

Until Next Week
[Closing sentence. No CTA filler.]
```

---

### Format 2: Topic Deep Dive

Use for: A focused issue on a single topic (e.g., "AI agents this week", "security incidents this week").

Target length: 450-650 words.

Structure:
1. **The Big Picture** — 80-100 words on why this topic matters this week
2. **Key Developments** — 3-4 sections, each 80-100 words, covering one development each
3. **What to Watch** — 2-3 bullet points on what happens next
4. **Resources** — list of all source articles with URLs

---

### Format 3: Curated Picks

Use for: "Editor's choice" digest with opinionated selection of the best reads.

Target length: 250-350 words.

Structure:
1. **This Week's Picks** — one sentence framing the selection
2. **5 picks** — each with title (linked), 30-40 word description, and a one-line "Why read it" note
3. **One to skip** — optional: one overhyped story and why it did not make the cut

---

## Length Rules

| Format | Min | Target | Max |
|--------|-----|--------|-----|
| Weekly Roundup | 300 | 400 | 500 |
| Topic Deep Dive | 400 | 550 | 650 |
| Curated Picks | 200 | 300 | 380 |

If Gemini output is too long, cut the Quick Takes section first, then trim the Also Worth Reading summaries.

---

## Attribution Rules

Every non-obvious claim needs a source link. Format:

- Inline: `[Source: Publication Name](https://full-url)`
- Section header links: `### [Story Title](https://full-url)`
- Bullet links: `- [Headline](https://full-url) — one-line summary`

Never write a data point, statistic, or quote without a linked attribution.

---

## Tone Rules

- Write for a reader who is busy. They scan. Use short paragraphs.
- No hype. No "this is huge." Let the facts speak.
- No first-person plural ("we noticed"). Write as a neutral observer.
- One idea per paragraph, maximum three sentences per paragraph.
- Dates: use full dates (April 10, 2026) not relative dates (this Tuesday).

---

## HTML Output Rules

When generating HTML for Ghost:
- Use `<h2>` for section headings (e.g., "Top Story", "Also Worth Reading")
- Use `<h3>` for individual story titles
- Use `<p>` for body text
- Use `<ul>` and `<li>` for Quick Takes and bullet lists
- Use `<a href="URL">` for all source links
- Do not use `<div>` with inline styles
- Do not use markdown syntax in the HTML output

When generating Markdown for Substack:
- Use `##` for section headings
- Use `###` for story titles
- Use `[text](url)` for links
- Use `-` for bullet points
