# Output Templates

Three templates — one per digest format. Replace every [BRACKETED FIELD] with content from the fetched articles. Never leave bracket text in the final output. Skip sections that have no source material rather than inventing content.

---

## Template 1: Weekly Roundup

```html
<h2>This Week in [INDUSTRY/TOPIC]</h2>
<p>[ONE SENTENCE capturing the week's theme or dominant story. Specific, not generic.]</p>

<h2>Top Story</h2>
<h3><a href="[ARTICLE_URL]">[ARTICLE_TITLE]</a></h3>
<p>[100-150 word summary of the most significant story this week. Include one specific data point or quote directly from the article. No invented statistics.] <a href="[ARTICLE_URL]">[SOURCE_NAME]</a></p>

<h2>Also Worth Reading</h2>

<h3><a href="[ARTICLE_2_URL]">[ARTICLE_2_TITLE]</a></h3>
<p>[40-60 word summary. Key insight from the article.] <a href="[ARTICLE_2_URL]">[SOURCE_2_NAME]</a></p>

<h3><a href="[ARTICLE_3_URL]">[ARTICLE_3_TITLE]</a></h3>
<p>[40-60 word summary. Key insight from the article.] <a href="[ARTICLE_3_URL]">[SOURCE_3_NAME]</a></p>

<h3><a href="[ARTICLE_4_URL]">[ARTICLE_4_TITLE]</a></h3>
<p>[40-60 word summary. Key insight from the article.] <a href="[ARTICLE_4_URL]">[SOURCE_4_NAME]</a></p>

<h2>Quick Takes</h2>
<ul>
  <li><a href="[ARTICLE_5_URL]">[ARTICLE_5_TITLE]</a> — [One-line summary.]</li>
  <li><a href="[ARTICLE_6_URL]">[ARTICLE_6_TITLE]</a> — [One-line summary.]</li>
  <li><a href="[ARTICLE_7_URL]">[ARTICLE_7_TITLE]</a> — [One-line summary.]</li>
</ul>

<p>[1-2 sentence closing. No CTA filler. No "see you next week".]</p>
```

Worked example:

```html
<h2>This Week in Developer Tools</h2>
<p>A major npm supply chain incident and two new runtime releases dominated developer news.</p>

<h2>Top Story</h2>
<h3><a href="https://blog.npmjs.org/post/supply-chain">npm Detects Malicious Package Injecting Crypto Miner</a></h3>
<p>The npm security team removed 47 packages after discovering a supply chain attack targeting Node.js build environments. The packages had been downloaded 2.3 million times before detection. The attack injected a crypto miner into postinstall scripts. npm is rolling out mandatory provenance attestation for all new package versions by June 2026. <a href="https://blog.npmjs.org/post/supply-chain">npm Blog</a></p>

<h2>Also Worth Reading</h2>

<h3><a href="https://bun.sh/blog/bun-1.2">Bun 1.2 Ships with Built-In S3 and SQL Support</a></h3>
<p>Bun 1.2 adds first-party APIs for S3 storage and SQL databases without any npm packages. The release also brings a 20% startup time improvement. <a href="https://bun.sh/blog/bun-1.2">Bun Blog</a></p>

<h2>Quick Takes</h2>
<ul>
  <li><a href="https://nodejs.org/en/blog/release/v22.14.0">Node.js 22.14.0 Released</a> — Minor patch with V8 12.4 backports and a fix for the http2 memory leak.</li>
  <li><a href="https://deno.com/blog/deno-2.2">Deno 2.2 Adds WebGPU Compute Shaders</a> — First runtime to support GPU compute from server-side JavaScript.</li>
</ul>

<p>Four feeds, 34 articles, one interesting week.</p>
```

---

## Template 2: Topic Deep Dive

```html
<h2>The Big Picture</h2>
<p>[80-100 words on why this topic is significant this week. Ground in specific events, not general claims. One data point from a source.]</p>

<h2>[DEVELOPMENT_1_HEADING]</h2>
<h3><a href="[ARTICLE_URL]">[ARTICLE_TITLE]</a></h3>
<p>[80-100 word summary. Specific facts, no invented details.] <a href="[ARTICLE_URL]">[SOURCE_NAME]</a></p>

<h2>[DEVELOPMENT_2_HEADING]</h2>
<h3><a href="[ARTICLE_URL]">[ARTICLE_TITLE]</a></h3>
<p>[80-100 word summary.] <a href="[ARTICLE_URL]">[SOURCE_NAME]</a></p>

<h2>[DEVELOPMENT_3_HEADING]</h2>
<h3><a href="[ARTICLE_URL]">[ARTICLE_TITLE]</a></h3>
<p>[80-100 word summary.] <a href="[ARTICLE_URL]">[SOURCE_NAME]</a></p>

<h2>What to Watch</h2>
<ul>
  <li>[Next development to follow, grounded in current events.]</li>
  <li>[Second thing to watch.]</li>
  <li>[Third thing to watch.]</li>
</ul>

<h2>This Week's Sources</h2>
<ul>
  <li><a href="[URL_1]">[TITLE_1]</a> — [SOURCE_NAME_1]</li>
  <li><a href="[URL_2]">[TITLE_2]</a> — [SOURCE_NAME_2]</li>
</ul>
```

---

## Template 3: Curated Picks

```html
<h2>This Week's Picks</h2>
<p>[One sentence framing the selection — what connects these picks or what made them stand out.]</p>

<h3>1. <a href="[ARTICLE_1_URL]">[ARTICLE_1_TITLE]</a></h3>
<p>[30-40 word description. Key takeaway.]</p>
<p><strong>Why read it:</strong> [One sentence. Specific reason.] <a href="[ARTICLE_1_URL]">[SOURCE_1_NAME]</a></p>

<h3>2. <a href="[ARTICLE_2_URL]">[ARTICLE_2_TITLE]</a></h3>
<p>[30-40 word description. Key takeaway.]</p>
<p><strong>Why read it:</strong> [One sentence. Specific reason.] <a href="[ARTICLE_2_URL]">[SOURCE_2_NAME]</a></p>

<h3>3. <a href="[ARTICLE_3_URL]">[ARTICLE_3_TITLE]</a></h3>
<p>[30-40 word description.]</p>
<p><strong>Why read it:</strong> [One sentence.] <a href="[ARTICLE_3_URL]">[SOURCE_3_NAME]</a></p>

<h3>4. <a href="[ARTICLE_4_URL]">[ARTICLE_4_TITLE]</a></h3>
<p>[30-40 word description.]</p>
<p><strong>Why read it:</strong> [One sentence.] <a href="[ARTICLE_4_URL]">[SOURCE_4_NAME]</a></p>

<h3>5. <a href="[ARTICLE_5_URL]">[ARTICLE_5_TITLE]</a></h3>
<p>[30-40 word description.]</p>
<p><strong>Why read it:</strong> [One sentence.] <a href="[ARTICLE_5_URL]">[SOURCE_5_NAME]</a></p>
```

---

## Fill-in Rules

1. Replace every [BRACKETED FIELD] with content from the fetched articles
2. Never leave bracket text in the output
3. Every URL must be an absolute URL (starts with `https://`)
4. Every non-obvious claim needs a linked source attribution
5. Skip a section if there is no source material for it
6. Check word count before presenting — see references/digest-format.md for targets
7. Do not use markdown in HTML output; do not use HTML tags in Markdown output
8. Write the Markdown version after the HTML version by converting heading tags and links
