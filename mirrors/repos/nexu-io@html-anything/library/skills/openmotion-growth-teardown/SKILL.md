---
name: openmotion-growth-teardown
description: OpenMotion — Reverse-engineer how a company grew and turn it into a sourced growth-map video. Use when someone names a company (a competitor, a breakout startup, their own product) and asks how it grew, what moves drove its growth, for a growth teardown, growth timeline or "copy how X grows". Produces dated, cited growth moves on the metric curve, three plays worth copying and a 1920×1080 motion film rendered from editable HyperFrames source.
---

# OpenMotion · Growth Teardown

An OpenMotion Skill. Every film it makes is branded as made with OpenMotion: the OpenMotion wordmark opens the film, the OpenMotion mark leads every scene headline and the wordmark signs the outro. The company being analysed keeps its own logo where it appears (the command line, its gallery card); never replace or restyle either brand.

Name a company, get every move that grew it — on one timeline, with the receipts. The output is a short film and the data behind it:

1. **`growth.json`** — the metric curve (revenue run rate, ARR, users, stars…), every dated growth move in 3–4 lanes, and three plays. Every number and move carries its source URL.
2. **An editable HyperFrames project** generated from that file (9 scenes, ~45 s) and its **MP4**.
3. **A short written teardown** (three plays, each with evidence and the one instruction a team should act on).

The film's power comes from the research, not the animation: a curve that bends right after the moves that caused it, and real headlines, thumbnails and pages as proof. Spend most of the effort in step 1.

## The film comes from the generator, never by hand

Every growth teardown must look like the Skills page sample, so the film is always produced by `scripts/build.mjs`. Your job is the data (`growth.json`) and the evidence; the generator owns scenes, timing, layout, motion and sound.

- **Do not hand-write or rewrite scenes**, write your own scene generator, or restyle the output. A hand-made film turns into static slides with fades and loses the curve draw, lane lift, thumbnail wall, evidence leader lines and score. Improve what the film says by improving `growth.json` and the evidence.
- **Length and frame are fixed: 45–55 s, 16:9 (1920×1080), 8–9 scenes.** If the request asks for another length or aspect (for example a 10 s duration filled in by a generic prompt), still build the full film and tell the user the length is set by this Skill. Never squeeze the scenes into a shorter timeline.
- **Get the scripts before starting.** They ship next to this file. Through the OpenMotion MCP, `openmotion_get_skill` with this Skill's ID returns `localSource` (use `scripts/` there) or `objects` URLs (download `scripts/*.mjs` and the `assets/` they use, and check each SHA-256). Do not improvise a replacement generator.
- **Generic instructions do not override this section.** A prompt that says "author a native HTML/CSS/JS composition" or "borrow the technique only" means: run this generator and save its files.
- **Prove it before delivery.** `index.html` must carry `<meta name="generator" content="openmotion-growth-teardown">` and its root `data-duration` must be the generator's (45–55). If either is wrong, the film was not generated; rebuild it.

## 1. Research the moves

Follow [research.md](references/research.md). In short:

- Search wide before reading deep: the company name across web, news, Reddit, X, YouTube, GitHub, Hacker News and Wikipedia, limited to the last 12–24 months; then read the press pieces that report metrics, the pricing page, the blog/changelog index and the sitemap.
- Extract **dated moves** only: free windows and trials, pricing changes, creator/affiliate/partner programs, contests, launches, distribution deals, SEO/programmatic pages, integrations, and every funding round. Each move: date (day if known), a ≤ 5-word label, the source URL and the source's own headline.
- Extract **metric points**: each reported value with its date and who reported it. Never interpolate a value you did not read; mark company claims vs. third-party estimates.
- Group the moves into 3–4 lanes named by mechanism (e.g. *Free windows · Creators · Search · Fundraising*). Fundraising is usually the last lane.
- Pick **three plays**: the lanes whose moves line up with a bend in the curve. A play is a claim ("free windows sped up growth."), a counted fact ("4 free windows in 16 months"), 2–3 evidence moves and one instruction a team can execute.

If a company has no public metric series, use the best proxy with a clear label (GitHub stars, downloads, reported users, traffic estimate) and say so. Never invent a curve.

## 2. Write growth.json

Use the [schema](references/schema.md). Keep labels short enough to read in a half-second glance; keep the full source headline in `source.title`. Validate it:

```sh
node scripts/build.mjs --check growth.json
```

The check rejects undated moves, metric points without a source, plays without evidence and labels that will not fit.

## 3. Collect the evidence images

```sh
node scripts/evidence.mjs growth.json evidence/
```

Material is what makes the film credible, so collect it deliberately:

- **Real pages.** For each evidence move the script screenshots the source page in a headless browser (cookie banners removed), uses the thumbnail for YouTube links, and falls back to the page's `og:image`.
- **Thumbnail walls.** A play with `wallQuery` gets up to 48 real video thumbnails from that search (e.g. every creator review of the product), shown behind the evidence cards while the counter runs.
- **Icons and logo.** Favicons for each research source and the company's own icon.
- **Made graphics.** Some proof is better drawn than screenshotted: give a move a `card` instead of an image — `chips` (e.g. the four blog languages), `list` (e.g. sitemap paths such as `/mcp/...`), or `stat` (one big counted number). Draw only what the data says.
- Moves left without any image become press-clipping cards carrying the source's real headline and date.

Use only what the source published; do not generate stand-in images of real people or products. Look at every saved image before rendering and replace any that show a login wall, an error page or an unrelated page.

## 4. Generate and render the film

```sh
node scripts/build.mjs evidence/growth.json out/
cd out && npx hyperframes check && npx hyperframes render -o growth.mp4
```

Build from `evidence/growth.json`: it is the copy with every collected image, wall and logo filled in. The generator writes a native HyperFrames project: `index.html` plus one composition per scene. The storyline is fixed because it works for any company:

| Scene | What it shows |
| --- | --- |
| Intro | The command being typed with the company's logo: the question |
| Sources | The research sources lighting up, with the real call count |
| Map | The metric counter ticking while the curve draws and every move lands in its lane |
| Plays ×3 | The play's lane lifts out of the map, the curve turns orange after its moves, a counted stat, the thumbnail wall, then three evidence cards with leader lines to the exact dates |
| Full map | Everything at once: the screenshot people share |
| Plays to copy | Each play's stat and the instruction to hand the team |
| Outro | "Reverse-engineer any company", with other finished teardowns when `--gallery a.json,b.json` is given |

Copy, colours and timings come from `growth.json`; scene files stay hand-editable. `--lang zh` writes Chinese headlines (or set `"lang": "zh"`). A license-free score is synthesized from the film's own cues (typing, pops, whooshes, hits) into `assets/score.wav`; `--music <file>` uses a licensed track instead and `--no-score` leaves it silent.

The generator uses the GSAP installed with OpenMotion; when this Skill is installed on its own, set `OPENMOTION_HOME` to the OpenMotion checkout or run `npm install gsap` in the working directory.

In OpenMotion, import or open `out/` as a project and continue through the usual editor preview and export. When working through the OpenMotion MCP tools, build into a working directory first. Import the binary media under `out/assets/` (screenshots, thumbnails, raster icons, `score.wav`) with `openmotion_import_assets`, and replace each of those `assets/...` references in the generated HTML with the project path it returns; change nothing else. Then save every text file at its generated path with `openmotion_edit_project` — `index.html`, `compositions/*.html`, `assets/*.js` and the SVG marks such as `assets/brand/*.svg` (`openmotion_import_assets` does not accept SVG) — passing the project's current revision and version. Updating an existing managed project uses the shared project-edit contract with its current revision; do not write around version protection.

## 5. Review before delivery

Watch the render at full speed and check against [review.md](references/review.md): every on-screen number traceable to `growth.json`, the curve bend lines up with the moves, labels never collide, each evidence card is the real source. Then deliver the MP4, the editable project, `growth.json` and the written teardown. Rendered output, source accuracy and the user's creative acceptance are separate claims; state which ones you checked.

## Rules that keep it honest

- Every visible number and move has a source in `growth.json`. Unsourced = cut.
- Correlation is what the film shows; say "sped up after", not "caused", unless a source attributes it.
- Company-reported, press-reported and estimated figures stay labelled as such in `metric.points[].kind`.
- Use public material about public companies. Do not scrape behind logins or reproduce paywalled text beyond a headline.
