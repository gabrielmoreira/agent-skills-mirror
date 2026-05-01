# Lessons Learned — Anti-Patterns from Real Iterations

Each entry below documents a real mistake made during a real session that cost the user an iteration round. **Read this file when starting any frontend output — these are the traps to avoid.**

The anti-patterns are paired with the correct pattern from `patterns.md` so you can route directly to the fix.

---

## ❌ ANTI-PATTERN 1 — Side-by-side bilingual content
**What I did wrong:** Showed English headline + Hebrew headline stacked vertically (or in 2-column grid) so users got both.

**Why it failed:** Anton at `8vw` and Rubik 900 at `5-6vw` are both display-weight fonts. Stacked, they overlap visually because line-heights below 1.0 cause descenders to invade the next ascender row. User's reaction: "the fonts are way too thick and override each other."

**The fix:** Pattern #1 in `patterns.md` — language toggle with `data-lang` attributes. Show ONE language at a time. Default EN, button to switch.

**Detection:** If you find yourself writing both `<span class="title-en">English</span>` and `<span class="title-he">עברית</span>` in adjacent positions, stop and route through the toggle pattern.

---

## ❌ ANTI-PATTERN 2 — No mobile nav planning
**What I did wrong:** Built a flat horizontal nav with 21 links and `flex-wrap: wrap`. On desktop it looked fine. On mobile, it ate 50% of the viewport.

**Why it failed:** Wrapping is not a mobile strategy. Users don't want a 5-line nav consuming the fold.

**The fix:** Pattern #2 in `patterns.md` — hamburger menu mandatory for `≤880px` if nav has > 6 items.

**Detection:** Count nav links. If > 6, hamburger is required. Don't wait for user feedback — build it from the start.

---

## ❌ ANTI-PATTERN 3 — Two display headlines stacked
**What I did wrong:** Stacked `clamp(46px, 8vw, 120px)` Anton EN headline above `clamp(36px, 6vw, 80px)` Rubik HE headline.

**Why it failed:** Both at `line-height: 0.92` means descenders from Anton invade the ascenders of Rubik. They literally overlap.

**The fix:** One display headline per section. If bilingual, use the toggle (pattern #1). If you need a subhead, make it `font-size: 50%` of the headline and don't use a display font for it.

**Detection:** Two `font-size: clamp(40px+, ...)` declarations stacked = visual collision. Avoid.

---

## ❌ ANTI-PATTERN 4 — Assigning HTML strings to element content
**What I did wrong:** Used the unsafe DOM-property assignment that takes a raw HTML string for dynamic content swaps.

**Why it failed:** Security hooks blocked it (rightfully). Even when content was author-controlled at write time, the moment a variable becomes user-data, it's an XSS hole.

**The fix:** Use `el.textContent = value` for plain text. Use `createElement` + `appendChild` for structured content. Reserve direct HTML-string assignment for compile-time literal strings only (the ones you typed directly into source code).

**Detection:** Any direct HTML-string assignment using a variable (not a literal string) is wrong. Refactor immediately.

---

## ❌ ANTI-PATTERN 5 — Forgot to translate `<title>`
**What I did wrong:** Implemented language toggle that swapped visible content but left the browser tab title in English.

**Why it failed:** User feedback: "the title doesn't change when I click on HE."

**The fix:** Make `document.title` part of the language toggle:
```js
const TITLES = { en: '...', he: '...' };
function setLang(lang) {
  /* ...visible content... */
  document.title = TITLES[lang] || TITLES.en;
}
```

**Detection:** If your site has bilingual support but `document.title` is set once in HTML and never updated, you have this bug.

---

## ❌ ANTI-PATTERN 6 — Generic install command for a single skill
**What I did wrong:** Suggested `npx skills add hoodini/ai-agents-skills` (whole repo) when the user wanted just one skill.

**Why it failed:** That command is interactive — it shows a checkbox list of all skills in the repo and forces the user to pick. Bad UX for "I want this one specific skill."

**The fix:** Per-skill install command using sparse-checkout:
```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/hoodini/ai-agents-skills /tmp/x \
  && cd /tmp/x && git sparse-checkout set skills/<skill-name> \
  && mkdir -p ~/.claude/skills && cp -R skills/<skill-name> ~/.claude/skills/ \
  && rm -rf /tmp/x
```

**Detection:** Recommending `npx skills add <repo>` for a single skill = wrong. Use sparse-clone.

---

## ❌ ANTI-PATTERN 7 — WebFetch on JS-rendered SPAs
**What I did wrong:** Called WebFetch on `https://practical.yuv.ai` to extract course content. Got back only the page title — the rest is rendered client-side by JS.

**Why it failed:** WebFetch reads the static HTML, which for SPAs is just shell + script tags. The actual content is built by JavaScript at runtime.

**The fix:** For JS-rendered SPAs (Teachable, learn.*, builder.io, most modern landing-page builders), use **Claude-in-Chrome** with `read_page` or `get_page_text`. It runs the actual browser and reads the rendered DOM.

**Detection:** If the page is on a domain like `learn.*`, `*.teachable.com`, `*.kajabi.com`, `practical.*`, etc., assume SPA and skip directly to Claude-in-Chrome.

---

## ❌ ANTI-PATTERN 8 — Inventing content for CTAs
**What I did wrong:** When user asked "add a CTA for my course," I almost wrote modules / prices / testimonials I hadn't verified — typical AI confabulation risk.

**Why it failed:** Would have published wrong information on a live site. User explicitly said "don't invent things beyond what's there."

**The fix:** Read the actual source page first (pattern #6 in `patterns.md` and the WebFetch / Claude-in-Chrome routing above). Quote verbatim. If a field isn't on the page, write "not on page" and ask. Never bridge a gap with plausible-sounding invention.

**Detection:** Any "and probably the course covers X / Y / Z" thinking = stop. Read the page. Verify.

---

## ❌ ANTI-PATTERN 9 — Skipping IntersectionObserver
**What I did wrong:** Initial catalog had 45 GSAP timelines all running on load. Page worked but cooked the user's CPU.

**Why it failed:** GSAP is fast, but 45 simultaneous timelines × 30fps = 1,350 callback executions per second. Each one triggers a layout/paint. Browsers protest.

**The fix:** Pattern #5 in `patterns.md` — IntersectionObserver pauses every demo when its stage is offscreen. CPU stays sane.

**Detection:** Any catalog with > 8 demos must use IntersectionObserver. No exceptions.

---

## ❌ ANTI-PATTERN 10 — Catalog scope creep across iterations
**What I did wrong:** Built initial catalog with 9 sections / 45 demos. User asked for "more" three times. Final: 19 sections / 71+ demos. Should have built comprehensive on first pass.

**Why it failed:** Scope creep means same problem solved 3 times. Initial build, then 3 expansions. Each iteration adds risk and CSS conflicts.

**The fix:** When user asks for a "catalog of effects" or "showcase of components," **build comprehensive on first pass**. Use this checklist:
- Captions / Markers / Cards / Devices / Magic / 3D / Themes / Transitions / Text / Charts / SFX / Layouts / Features / GSAP / Prompts / Scenarios / Tech / Skills / Connect / Course (where applicable)

That's the proven 18+ section structure. Plan for it from minute 1.

**Detection:** Building a catalog with < 10 sections = probably under-scoped. Ask "what else in this domain?" before declaring done.

---

## ❌ ANTI-PATTERN 11 — Inline `lang-toggle` without mobile duplicate
**What I did wrong:** Originally placed lang toggle inside `.nav` only. On mobile, the toggle got hidden along with the nav — users on mobile couldn't switch languages without opening the hamburger.

**Why it failed:** Language preference is a top-level affordance. Hiding it inside a hamburger menu makes it discoverable only after one extra interaction.

**The fix:** Place lang toggle in **two places**:
1. Inside `.nav` (visible on desktop, hidden on mobile)
2. Inside `.topbar-mobile-right` (visible on mobile, hidden on desktop)

Both sets of buttons get the same `data-lang-set` attribute, so the same JS handler controls both. CSS hides the wrong one per breakpoint.

**Detection:** Mobile users can't see the lang toggle without opening the hamburger = bug. Duplicate the toggle into the always-visible mobile cluster.

---

## ❌ ANTI-PATTERN 12 — Cert provisioning impatience
**What I did wrong:** GH Pages cert state stuck at `none` after correct DNS. Waited and the user complained.

**Why it failed:** GitHub's auto-provisioning sometimes silently stalls.

**The fix:** If cert state is `none` after > 15 min with correct DNS, toggle the custom domain off and back on:
```bash
gh api -X PUT /repos/{owner}/{repo}/pages -f "cname="
sleep 5
gh api -X PUT /repos/{owner}/{repo}/pages -f "cname=<your-domain>"
```
This kicks Let's Encrypt validation. Cert lands within 15 min.

**Detection:** Cert state stays `none` for > 15 min = stuck. Toggle.

---

## ❌ ANTI-PATTERN 13 — Skipping the mobile screenshot before declaring done
**What I did wrong:** Built and shipped, then user shipped to live, then user took a mobile screenshot showing broken nav.

**Why it failed:** I never resized the preview to mobile size during build. Desktop was fine; mobile was broken.

**The fix:** Before declaring frontend work complete, **always**:
1. `preview_resize { preset: 'mobile' }` (375×812)
2. Take screenshot
3. Eyeball: nav fits? text overflows? grid collapses correctly? spacing OK?
4. If anything looks broken, fix and re-screenshot

This is a 30-second check that prevents shipped bugs.

**Detection:** "I built it but didn't check mobile" = guaranteed mobile bug.

---

## ❌ ANTI-PATTERN 14 — Forgetting `e.stopPropagation` on inner clickable elements
**What I did wrong:** Built skill-card with code-block inside an `<a>` wrapper. Clicking the code copied the install command BUT also navigated the parent link to GitHub. Two actions for one click.

**Why it failed:** Click events bubble up the DOM. The inner copy handler ran, then the parent link handled the click and navigated.

**The fix:** Always `e.preventDefault()` + `e.stopPropagation()` on inner click handlers when the element is nested inside a clickable parent:
```js
code.addEventListener('click', (e) => {
  e.preventDefault();
  e.stopPropagation();
  /* ...copy logic... */
});
```

**Detection:** A clickable card with a clickable child element = potential bubble bug. Stop propagation on inner.

---

## ❌ ANTI-PATTERN 15 — Trusting WebFetch output as ground truth
**What I did wrong:** WebFetch returned "title: Practical AI with Claude" and I almost wrote a CTA based on that one fact.

**Why it failed:** WebFetch lies of omission for SPAs. The HTML it sees IS the static title + scripts; the rendered content is invisible to it.

**The fix:** When WebFetch returns suspiciously thin output (only title, only meta tags, none of the visible page content), assume SPA and re-route to Claude-in-Chrome. Verify before quoting.

**Detection:** WebFetch returns < 500 chars of meaningful content = probably an SPA. Use Claude-in-Chrome.

---

## Quick reference — corrective pattern routing

| Anti-pattern | Goes to |
|---|---|
| #1 Side-by-side bilingual | `patterns.md` § 1 (Bilingual toggle) |
| #2 No mobile nav | `patterns.md` § 2 (Mobile hamburger nav) |
| #3 Stacked display headlines | SKILL.md rule #3 (one display per section) |
| #4 Direct HTML string assignment | SKILL.md rule #4 (textContent / createElement) |
| #5 Untranslated title | `patterns.md` § 1 (TITLES object in setLang) |
| #6 Generic install command | SKILL.md rule #6 (sparse-clone command) |
| #7 WebFetch on SPA | SKILL.md rule #7 (Claude-in-Chrome) |
| #8 Invented CTA content | SKILL.md rule #7 + `patterns.md` § 6 |
| #9 No IntersectionObserver | `patterns.md` § 5 |
| #10 Scope creep | SKILL.md "When this skill applies" — build comprehensive |
| #11 Mobile-hidden toggle | `patterns.md` § 2 (duplicate toggle in mobile cluster) |
| #12 Cert impatience | SKILL.md rule #12 |
| #13 Skipping mobile check | SKILL.md rule #8 |
| #14 Missing stopPropagation | `patterns.md` § 3 (Effect-ID chip) |
| #15 Trusting WebFetch on SPAs | SKILL.md rule #7 |

If a future iteration hits any of these problems, it's because the lesson didn't make it from this file into the build. Add the pattern. Update this file. Don't relearn.
