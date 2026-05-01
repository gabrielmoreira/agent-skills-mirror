# Production Patterns

Copy-paste code templates extracted from real sites built with this skill (most recently [effects.yuv.ai](https://effects.yuv.ai)). Each pattern has been tested in production, hardened against edge cases, and refined over multiple iterations. **Use these verbatim** instead of re-deriving — they encode lessons that already cost iterations.

## Table of contents

1. [Bilingual toggle (EN/HE with flag emojis)](#1-bilingual-toggle-enhe-with-flag-emojis)
2. [Mobile hamburger nav](#2-mobile-hamburger-nav)
3. [Effect-ID copy chip](#3-effect-id-copy-chip)
4. [Hyperframes hero reel](#4-hyperframes-hero-reel)
5. [IntersectionObserver demo pause](#5-intersectionobserver-demo-pause)
6. [Course CTA (practical.yuv.ai)](#6-course-cta-practicalyuvai)
7. [Liquid glass card with 3D tilt-pop](#7-liquid-glass-card-with-3d-tilt-pop)
8. [Connect / social grid](#8-connect--social-grid)

---

## 1. Bilingual toggle (EN/HE with flag emojis)

The complete, tested, hardened pattern. Three pieces: HTML for the toggle, CSS for show/hide, JS for state.

### HTML (place inside the topbar nav)

```html
<div class="lang-toggle" role="group" aria-label="Language toggle">
  <button class="lang-btn active" data-lang-set="en" aria-label="English">
    <span class="flag">🇺🇸</span>EN
  </button>
  <button class="lang-btn" data-lang-set="he" aria-label="עברית">
    <span class="flag">🇮🇱</span>HE
  </button>
</div>
```

For every translatable element, mark with `data-lang`:

```html
<h1>
  <span data-lang="en">Pick the effect, not the code.</span>
  <span data-lang="he">בחר את האפקט, לא את הקוד.</span>
</h1>
```

Inline mixed content is fine — the spans hide/show as needed.

### CSS

```css
/* universal — show one language, hide the other */
html:not([lang="he"]) [data-lang="he"] { display: none !important; }
html[lang="he"] [data-lang="en"] { display: none !important; }

/* Hebrew text gets RTL + correct font auto-routing */
[data-lang="he"] {
  direction: rtl;
  unicode-bidi: embed;
}
[data-lang="he"]:where(p, span, em, strong) {
  font-family: 'Assistant', 'Inter', sans-serif;
}
h1 [data-lang="he"], h2 [data-lang="he"], h3 [data-lang="he"], h4 [data-lang="he"] {
  font-family: 'Rubik', sans-serif;
  font-weight: 900;
}

/* toggle button styling */
.lang-toggle {
  display: inline-flex;
  align-items: center;
  background: rgba(10,10,10,0.05);
  padding: 2px;
  border: 1px solid rgba(10,10,10,0.1);
  border-radius: 999px;
}
.lang-btn {
  font-family: var(--font-display, 'Anton', sans-serif);
  font-size: 12px;
  letter-spacing: 0.10em;
  text-transform: uppercase;
  padding: 5px 12px;
  background: transparent;
  border: 0;
  cursor: pointer;
  color: var(--charcoal, #1A1A1A);
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  line-height: 1;
  transition: background .18s ease, color .18s ease;
}
.lang-btn .flag { font-size: 13px; }
.lang-btn.active {
  background: var(--pink, #FF1464);
  color: var(--off-white, #FAFAF7);
  box-shadow: 0 4px 14px rgba(255, 20, 100, 0.3);
}
```

### JS

```js
(function () {
  const root = document.documentElement;
  const KEY = 'site-lang';
  const buttons = document.querySelectorAll('[data-lang-set]');

  /* ALSO swap document.title — this is critical for native UX */
  const TITLES = {
    en: 'Site Title — English',
    he: 'כותרת האתר — עברית',
  };

  function setLang(lang) {
    root.setAttribute('lang', lang);
    document.title = TITLES[lang] || TITLES.en;
    buttons.forEach(b => b.classList.toggle('active', b.dataset.langSet === lang));
    try { localStorage.setItem(KEY, lang); } catch {}
  }

  buttons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      setLang(btn.dataset.langSet);
    });
  });

  /* restore saved choice on page load */
  let saved = 'en';
  try { saved = localStorage.getItem(KEY) || 'en'; } catch {}
  setLang(saved);
})();
```

### Hard rules
- Default lang is `en` (most users globally). Don't default to HE without explicit instruction.
- The toggle goes at the **end of the nav** (right side on LTR, left on RTL).
- Don't set `dir="rtl"` on `<html>` — keeps layout consistent. Hebrew TEXT containers get RTL via the universal `[data-lang="he"]` rule.
- For mobile, see pattern #2 — the toggle moves into the topbar-mobile-right cluster, the inside-nav copy gets hidden.

---

## 2. Mobile hamburger nav

Required for any nav with > 6 links at viewport ≤ 880px. Tested on the 21-link effects.yuv.ai topbar.

### HTML

```html
<header class="topbar">
  <div class="topbar-inner">
    <div class="brand">YUV<span>.AI</span></div>

    <!-- mobile-only cluster (lang toggle + hamburger) -->
    <div class="topbar-mobile-right">
      <div class="lang-toggle lang-toggle-mobile" role="group" aria-label="Language toggle">
        <button class="lang-btn active" data-lang-set="en" aria-label="English"><span class="flag">🇺🇸</span>EN</button>
        <button class="lang-btn" data-lang-set="he" aria-label="עברית"><span class="flag">🇮🇱</span>HE</button>
      </div>
      <button class="nav-toggle" id="nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
        <span class="nav-toggle-line"></span>
        <span class="nav-toggle-line"></span>
        <span class="nav-toggle-line"></span>
      </button>
    </div>

    <nav class="nav" id="primary-nav">
      <a href="#section-1">Section 1</a>
      <a href="#section-2">Section 2</a>
      <!-- ... -->
      <div class="lang-toggle" role="group" aria-label="Language toggle">
        <button class="lang-btn active" data-lang-set="en" aria-label="English"><span class="flag">🇺🇸</span>EN</button>
        <button class="lang-btn" data-lang-set="he" aria-label="עברית"><span class="flag">🇮🇱</span>HE</button>
      </div>
    </nav>
  </div>
</header>
```

Note: lang toggle appears **twice** — inside-nav (visible on desktop) and topbar-mobile-right (visible on mobile). CSS hides the wrong one per breakpoint. JS listens to all `[data-lang-set]` buttons so both work identically.

### CSS

```css
.topbar { position: sticky; top: 0; z-index: 100; background: rgba(250,250,247,0.92); backdrop-filter: saturate(180%) blur(14px); }
.topbar-inner { max-width: 1440px; margin-inline: auto; padding: 14px 4vw; display: flex; align-items: center; gap: 24px; justify-content: space-between; }

/* mobile cluster — hidden on desktop */
.topbar-mobile-right { display: none; align-items: center; gap: 10px; }
.lang-toggle-mobile { display: none; }
.nav-toggle {
  display: none;
  width: 40px; height: 40px;
  background: var(--charcoal, #1A1A1A);
  border: 0; cursor: pointer;
  padding: 0;
  flex-direction: column; justify-content: center; align-items: center;
  gap: 5px;
  border-radius: 999px;
  transition: background .18s ease;
}
.nav-toggle:hover { background: var(--pink, #FF1464); }
.nav-toggle-line {
  display: block;
  width: 18px; height: 2px;
  background: var(--off-white, #FAFAF7);
  border-radius: 2px;
  transition: transform .25s ease, opacity .2s ease;
}
.nav-toggle[aria-expanded="true"] { background: var(--pink, #FF1464); }
.nav-toggle[aria-expanded="true"] .nav-toggle-line:nth-child(1) { transform: translateY(7px) rotate(45deg); }
.nav-toggle[aria-expanded="true"] .nav-toggle-line:nth-child(2) { opacity: 0; }
.nav-toggle[aria-expanded="true"] .nav-toggle-line:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

.nav { display: flex; gap: 6px; flex-wrap: wrap; }

/* mobile breakpoint */
@media (max-width: 880px) {
  .topbar-inner { align-items: center; flex-wrap: nowrap; }
  .topbar-mobile-right { display: flex; margin-inline-start: auto; }
  .lang-toggle-mobile { display: inline-flex; }
  .nav-toggle { display: inline-flex; }
  .nav .lang-toggle:not(.lang-toggle-mobile) { display: none; }

  .nav {
    position: absolute;
    top: 100%; left: 0; right: 0;
    background: var(--off-white, #FAFAF7);
    border-bottom: 1px solid rgba(10,10,10,0.08);
    box-shadow: 0 18px 40px rgba(0,0,0,0.12);
    padding: 14px 4vw 22px;
    flex-direction: column; align-items: stretch;
    gap: 4px;
    max-height: 0;
    overflow: hidden;
    opacity: 0;
    pointer-events: none;
    transition: max-height .35s ease, opacity .25s ease, padding .25s ease;
  }
  .nav.open {
    max-height: calc(100vh - 80px);
    overflow-y: auto;
    opacity: 1;
    pointer-events: auto;
    padding: 18px 4vw 24px;
  }
  .nav a {
    width: 100%;
    text-align: start;
    padding: 12px 14px;
    font-size: 16px;
    border-radius: 8px;
    border: 1px solid transparent;
  }
  .nav a:hover, .nav a.active {
    background: var(--charcoal, #1A1A1A);
    color: var(--off-white, #FAFAF7);
    border-color: var(--charcoal, #1A1A1A);
  }
}
```

### JS

```js
(function () {
  const btn = document.getElementById('nav-toggle');
  const nav = document.getElementById('primary-nav');
  if (!btn || !nav) return;

  function setOpen(open) {
    nav.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    document.body.style.overflow = open ? 'hidden' : '';
  }

  btn.addEventListener('click', (e) => {
    e.preventDefault();
    setOpen(!nav.classList.contains('open'));
  });

  /* close on link click — page scrolls smoothly to the section */
  nav.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', () => setOpen(false));
  });

  /* Escape closes */
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && nav.classList.contains('open')) setOpen(false);
  });

  /* close when window resizes back to desktop */
  window.addEventListener('resize', () => {
    if (window.innerWidth > 880 && nav.classList.contains('open')) setOpen(false);
  });
})();
```

### Hard rules
- Hamburger animates the 3 lines into an X via CSS only (no SVG icon swap).
- Body scroll locks (`overflow: hidden`) when menu is open — feels native.
- Esc + resize-to-desktop both close the menu.
- Click on a link closes the menu before scrolling, so the user sees the destination.

---

## 3. Effect-ID copy chip

For any "browse and pick" interface where the user picks an item by ID. Click to copy, toast confirms.

### HTML

```html
<div class="demo">
  <div class="demo-stage" data-demo="kara-scale">
    <!-- live demo here -->
  </div>
  <div class="demo-meta">
    <h3>Karaoke · Scale Pop</h3>
    <p>Inactive words at 45% opacity, active word slams to 1.0.</p>
    <span class="demo-id" data-id="captions.karaoke.scale-pop">captions.karaoke.scale-pop</span>
  </div>
</div>

<!-- toast (one global) -->
<div class="toast" id="toast">copied</div>
```

### CSS

```css
.demo-id {
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 11.5px;
  background: var(--charcoal, #1A1A1A);
  color: var(--yellow, #E5FF00);
  padding: 6px 10px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  user-select: all;
  align-self: flex-start;
  transition: background .15s ease;
}
.demo-id::before { content: '◐'; font-size: 10px; color: var(--pink, #FF1464); }
.demo-id:hover { background: var(--pink, #FF1464); color: var(--off-white, #FAFAF7); }
.demo-id.copied { background: var(--pink, #FF1464); color: var(--off-white, #FAFAF7); }
.demo-id.copied::before { content: '✓'; color: var(--off-white, #FAFAF7); }

.toast {
  position: fixed;
  bottom: 30px; left: 50%;
  transform: translate(-50%, 80px);
  background: var(--charcoal, #1A1A1A);
  color: var(--yellow, #E5FF00);
  font-family: var(--font-mono, monospace);
  font-size: 13px;
  padding: 12px 18px;
  z-index: 200;
  transition: transform .35s cubic-bezier(.2,.9,.3,1.4);
  pointer-events: none;
}
.toast.show { transform: translate(-50%, 0); }
```

### JS

```js
(function () {
  const toast = document.getElementById('toast');
  let toastTimer;

  document.querySelectorAll('.demo-id').forEach(chip => {
    chip.addEventListener('click', async (e) => {
      /* if chip is inside a clickable card, prevent navigation */
      e.preventDefault();
      e.stopPropagation();

      const id = chip.dataset.id || chip.textContent.trim();
      try {
        await navigator.clipboard.writeText(id);
      } catch {
        /* fallback for old browsers / restricted contexts */
        const r = document.createRange();
        r.selectNodeContents(chip);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(r);
        document.execCommand('copy');
      }
      chip.classList.add('copied');
      toast.textContent = 'copied · ' + id;
      toast.classList.add('show');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => {
        toast.classList.remove('show');
        chip.classList.remove('copied');
      }, 1600);
    });
  });
})();
```

### Hard rules
- Always `e.stopPropagation()` if the chip is inside a parent `<a>` or clickable card — otherwise click navigates AND copies.
- Use `navigator.clipboard.writeText` with a `try/catch` fallback to `document.execCommand('copy')` for compatibility.
- Visual feedback (chip turns pink + checkmark) is as important as the toast.

---

## 4. Hyperframes hero reel

Top of every major site. The site itself becomes a Hyperframes-renderable artifact.

### HTML structure (skeleton)

```html
<section class="hero-video" id="hero-video">
  <div class="hv-stage"
       data-composition-id="hero-reel"
       data-start="0"
       data-duration="14"
       data-width="1920"
       data-height="1080">

    <canvas class="hv-particles" id="hv-particles"></canvas>
    <div class="hv-grid"></div>

    <!-- N independent scenes, each absolute, opacity 0 by default -->
    <div class="hv-scene" id="hv-s1">
      <span class="hv-eyebrow">POV</span>
      <h1 class="hv-headline">
        <span class="hv-word">YOUR</span>
        <span class="hv-word accent">HEADLINE</span>
      </h1>
    </div>

    <div class="hv-scene" id="hv-s2">...</div>
    <div class="hv-scene" id="hv-s3">...</div>
    <!-- etc. -->

    <!-- progress + meta tags -->
    <div class="hv-progress"><div class="hv-progress-bar" id="hv-progress-bar"></div></div>
    <div class="hv-meta">
      <span class="hv-meta-tag">REC</span>
      <span class="hv-meta-time" id="hv-meta-time">00:00 / 00:14</span>
      <span class="hv-meta-tag">9:16 · 16:9</span>
    </div>
    <a class="hv-skip" href="#first-section">EXPLORE ↓</a>
  </div>
</section>
```

### Key CSS rules
- `.hero-video` is `position: relative; height: clamp(420px, 70vh, 720px); background: #04050a; overflow: hidden;`
- All `.hv-scene` start with `opacity: 0` and are positioned `absolute; inset: 0;`
- `.hv-headline` uses Anton with `text-shadow: 0 4px 0 rgba(0,0,0,0.4), 0 14px 42px rgba(0,0,0,0.85);` and `-webkit-text-stroke: 1px rgba(0,0,0,0.55)` for visual weight
- Particles canvas is absolute, z-index 1, opacity 0.55

### JS — master timeline

```js
{
  const stage = document.querySelector('#hero-video .hv-stage');
  const tl = gsap.timeline({ paused: true, repeat: -1, repeatDelay: 0.6 });
  const TOTAL = 14; /* seconds */

  /* progress bar ticks across full duration */
  const progress = document.getElementById('hv-progress-bar');
  const meta = document.getElementById('hv-meta-time');
  tl.to(progress, { width: '100%', duration: TOTAL, ease: 'none' }, 0);
  const tobj = { t: 0 };
  tl.to(tobj, { t: TOTAL, duration: TOTAL, ease: 'none', onUpdate: () => {
    const s = Math.floor(tobj.t).toString().padStart(2, '0');
    meta.textContent = `00:${s} / 00:14`;
  }}, 0);

  /* hide all scenes by default */
  ['hv-s1','hv-s2','hv-s3'].forEach(id => gsap.set('#' + id, { opacity: 0 }));

  /* scene 1 — 0 to 2.4s */
  const s1Words = document.querySelectorAll('#hv-s1 .hv-word');
  tl.to('#hv-s1', { opacity: 1, duration: 0.2 }, 0);
  tl.fromTo(s1Words,
    { opacity: 0, y: 50, scale: 0.9 },
    { opacity: 1, y: 0, scale: 1, duration: 0.42, ease: 'back.out(1.7)', stagger: 0.10 },
    0.15);
  tl.to('#hv-s1', { opacity: 0, duration: 0.25 }, 2.2);

  /* ... more scenes ... */

  stage.__tl = tl;
  tl.play();
  observer.observe(stage); /* see pattern #5 */
}
```

### Hard rules
- The stage MUST have `data-composition-id`, `data-width`, `data-height`, `data-duration` — otherwise it's not Hyperframes-renderable.
- Each scene has its own `id` and is shown/hidden via `tl.to('#sN', { opacity: 1/0 })` rather than CSS classes — keeps the timeline as the single source of truth.
- Progress bar + timecode + REC tag give it the "video" feel even though it's HTML.
- Particles canvas uses deterministic seeded math (no `Math.random()` in the position loop) so Hyperframes captures identical frames each render.

---

## 5. IntersectionObserver demo pause

Required for any catalog with > 8 GSAP demos. Without this, the page cooks the user's CPU.

### JS (place once, at the top of your script)

```js
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    const tl = entry.target.__tl;
    if (!tl) return;
    if (entry.isIntersecting) tl.play();
    else tl.pause();
  });
}, { threshold: 0.15 });

/* observe every stage */
document.querySelectorAll('.demo-stage').forEach(s => observer.observe(s));
```

### Pattern in each demo's setup

```js
{
  const stage = document.querySelector('[data-demo="kara-scale"]');
  const tl = gsap.timeline({ paused: true, repeat: -1, repeatDelay: 0.6 });
  /* build timeline */
  tl.to(/* ... */);
  /* attach to stage */
  stage.__tl = tl;
}
```

The observer reads `stage.__tl`, plays when intersecting, pauses when not. **All demos paused by default** (`paused: true`) — observer fires `play()` once they're visible.

### Hard rules
- `threshold: 0.15` — demo plays when 15% visible. Tuned for catalog cards.
- Each stage is its own observer target (use `.demo-stage` class consistently).
- Hero-video is a special case: also call `tl.play()` directly so it starts before the observer fires.

---

## 6. Course CTA (practical.yuv.ai)

Reusable template for embedding Yuval's Claude Desktop course in any site. **Always cross-check actual content from practical.yuv.ai before shipping** — prices, modules, and CTAs change.

### HTML (use verified content from practical.yuv.ai)

```html
<section class="course-cta" id="course">
  <div class="course-inner">

    <div class="course-eyebrow">
      <span data-lang="en">Course by Yuval Avidani</span>
      <span data-lang="he">הקורס של יובל אבידני</span>
    </div>

    <h2 class="course-headline" data-lang="en">Master <em>Claude Desktop.</em><br>Practical AI Training.</h2>
    <h2 class="course-headline-he" data-lang="he">תשתלטו על <em>Claude Desktop.</em><br>קורס מעשי, צעד אחר צעד.</h2>

    <p class="course-sub" data-lang="en">A recorded, step-by-step Hebrew course where Yuval teaches you to make Claude Desktop your most powerful work tool...</p>
    <p class="course-sub he" data-lang="he">קורס מוקלט, מעשי, צעד-אחר-צעד שבו יובל מלמד אתכם להפוך את Claude Desktop לכלי העבודה הכי חזק שיש לכם...</p>

    <!-- 6 modules grid (verified from page) -->
    <div class="course-grid">
      <div class="course-mod">
        <span class="course-mod-tag">01 · CORE</span>
        <span class="course-mod-name" data-lang="en">Full Claude Mastery</span>
        <span class="course-mod-name" data-lang="he">שליטה מלאה ב-Claude</span>
        <!-- ... -->
      </div>
      <!-- 5 more modules -->
    </div>

    <!-- bonus -->
    <div class="course-bonus">
      <span class="course-bonus-tag" data-lang="en">🎁 Bonus · Free</span>
      <span class="course-bonus-tag" data-lang="he">🎁 מתנה · חינם</span>
      <span class="course-bonus-text" data-lang="en">~200 ready-to-use prompts guide (PDF) — worth ₪497, included free.</span>
      <span class="course-bonus-text" data-lang="he">מדריך כ-200 פרומפטים מוכנים לשימוש מיידי (PDF) — שווי ₪497, חינם עם הקורס.</span>
    </div>

    <!-- price + CTA -->
    <div class="course-pricerow">
      <div class="course-price">
        <span class="v">₪1,480</span>
        <span class="l" data-lang="en">One-time · VAT included</span>
        <span class="l" data-lang="he">תשלום חד-פעמי · כולל מע"מ</span>
      </div>
      <div class="course-cta-row">
        <a class="course-btn" href="https://learn.yuv.ai/practical" target="_blank" rel="noopener" data-lang="en">
          <span>Get Instant Access</span><span class="course-btn-arrow">→</span>
        </a>
        <a class="course-btn" href="https://learn.yuv.ai/practical" target="_blank" rel="noopener" data-lang="he">
          <span>הצטרפו עכשיו</span><span class="course-btn-arrow">←</span>
        </a>
        <a class="course-btn secondary" href="https://learn.yuv.ai/practical/igjgizI" target="_blank" rel="noopener" data-lang="en">
          <span>Watch a Full Lesson Free</span><span class="course-btn-arrow">→</span>
        </a>
        <a class="course-btn secondary" href="https://learn.yuv.ai/practical/igjgizI" target="_blank" rel="noopener" data-lang="he">
          <span>צפו בפרק מלא בחינם</span><span class="course-btn-arrow">←</span>
        </a>
      </div>
    </div>

  </div>
</section>
```

### URLs to use (verified, do not change)
- Main course page: `https://practical.yuv.ai`
- Direct enroll: `https://learn.yuv.ai/practical`
- Free preview lesson: `https://learn.yuv.ai/practical/igjgizI`

### Trust signals (verified, real)
- GitHub Star × 2
- AWS Gen AI Superstar × 2
- ~19 years in tech
- Featured on Israeli media (Channel 12)
- Speaks at conferences worldwide

### Hard rules
- Always `target="_blank" rel="noopener"` so the visitor doesn't lose the host site.
- Use `data-lang` for all text — bilingual users get HE button; the same CTA works for both.
- **Never invent**. Always re-verify content from practical.yuv.ai using Claude-in-Chrome (it's an SPA, WebFetch returns shell only).
- Place the section between Tech Explainer and Connect — peak buying intent zone.

---

## 7. Liquid glass card with 3D tilt-pop

Real `backdrop-filter`, never pre-baked.

### CSS

```css
.glass-card {
  position: relative;
  border-radius: 24px;
  padding: 18px 22px;
  background: rgba(255, 255, 255, 0.10);
  backdrop-filter: blur(22px) saturate(160%);
  -webkit-backdrop-filter: blur(22px) saturate(160%);
  border: 1.5px solid rgba(255, 255, 255, 0.20);
  box-shadow: 0 12px 40px rgba(0,0,0,0.45), inset 0 2px 0 rgba(255,255,255,0.18);
  color: var(--off-white);
  display: flex;
  flex-direction: column;
  gap: 6px;
  will-change: transform, opacity;
}
.glass-card.dark { background: rgba(0, 0, 0, 0.55); }
```

### JS — entrance animation

```js
gsap.fromTo(card,
  { opacity: 0, scale: 0.85, y: 60, rotationY: -12, transformPerspective: 900 },
  { opacity: 1, scale: 1, y: 0, rotationY: 0, duration: 0.65, ease: 'back.out(1.6)' }
);
/* idle float */
gsap.to(card, { y: -8, duration: 0.9, ease: 'sine.inOut', yoyo: true, repeat: -1 });
```

### Hard rules
- Always `back.out(1.6)` or `back.out(1.7)` — the YUV.AI signature overshoot.
- Border radius 24px or 56px — never 8/12/16px.
- Always real backdrop-filter, never pre-baked PNGs.

---

## 8. Connect / social grid

Footer-style social block. Real handles, real URLs, hover sweeps in the brand color.

### HTML

```html
<section class="connect-wrap" id="connect">
  <div class="connect-inner">
    <div class="connect-eyebrow">Find me everywhere</div>
    <h2 class="connect-headline">CONNECT.<br>SHIP <em>VIRAL.</em></h2>

    <div class="connect-grid">
      <a class="connect-link" href="https://yuv.ai" target="_blank">
        <div><div class="platform">Website</div><span class="handle">yuv.ai</span></div>
        <span class="arrow">→</span>
      </a>
      <a class="connect-link yellow" href="https://linktr.ee/yuvai" target="_blank">
        <div><div class="platform">Linktree</div><span class="handle">linktr.ee/yuvai</span></div>
        <span class="arrow">→</span>
      </a>
      <a class="connect-link" href="https://x.com/yuvalav" target="_blank">
        <div><div class="platform">X</div><span class="handle">@yuvalav</span></div>
        <span class="arrow">→</span>
      </a>
      <a class="connect-link yellow" href="https://www.instagram.com/yuval_770" target="_blank">
        <div><div class="platform">Instagram</div><span class="handle">@yuval_770</span></div>
        <span class="arrow">→</span>
      </a>
      <a class="connect-link" href="https://www.tiktok.com/@yuval.ai" target="_blank">
        <div><div class="platform">TikTok</div><span class="handle">@yuval.ai</span></div>
        <span class="arrow">→</span>
      </a>
      <a class="connect-link yellow" href="https://www.youtube.com/@yuv-ai" target="_blank">
        <div><div class="platform">YouTube</div><span class="handle">@yuv-ai</span></div>
        <span class="arrow">→</span>
      </a>
      <a class="connect-link" href="https://www.facebook.com/yuval.avidani" target="_blank">
        <div><div class="platform">Facebook</div><span class="handle">@yuval.avidani</span></div>
        <span class="arrow">→</span>
      </a>
      <a class="connect-link yellow" href="https://github.com/hoodini" target="_blank">
        <div><div class="platform">GitHub</div><span class="handle">@hoodini</span></div>
        <span class="arrow">→</span>
      </a>
    </div>
  </div>
</section>
```

### Verified handles — do not change

| Platform | URL | Handle |
|---|---|---|
| Website | https://yuv.ai | yuv.ai |
| Linktree | https://linktr.ee/yuvai | linktr.ee/yuvai |
| X | https://x.com/yuvalav | @yuvalav |
| Instagram | https://www.instagram.com/yuval_770 | @yuval_770 |
| TikTok | https://www.tiktok.com/@yuval.ai | @yuval.ai |
| YouTube | https://www.youtube.com/@yuv-ai | @yuv-ai |
| Facebook | https://www.facebook.com/yuval.avidani | @yuval.avidani |
| GitHub | https://github.com/hoodini | @hoodini |
| Course | https://practical.yuv.ai | — |

### Hard rules
- Alternate `.connect-link` and `.connect-link.yellow` so the hover-sweep colors alternate pink/yellow across the grid.
- Always `target="_blank" rel="noopener"`.
- The hover effect is a `::before` pseudo-element that translates X from -100% to 0 — the brand color "sweeps in" from the left.

---

## Pre-ship checklist

Before declaring frontend work complete, verify ALL:

- [ ] **Mobile responsive at 375×812** — screenshot shows no overflow, hamburger present if > 6 nav items
- [ ] **Bilingual toggle works** — clicking 🇮🇱 HE swaps content + document.title; reload preserves choice
- [ ] **All Hebrew text** has correct font (Rubik for display, Assistant for body) and renders RTL
- [ ] **No `#FFFFFF`** anywhere — only `#FAFAF7`
- [ ] **No 8/12/16px border radius** — only 0, 999px, or 24-56px (glass)
- [ ] **No default Tailwind colors** (slate-*, zinc-*, indigo-*, etc.)
- [ ] **GSAP timelines** for any non-trivial motion — never CSS keyframes for animations longer than 0.5s
- [ ] **IntersectionObserver** if there are > 8 demos
- [ ] **Effect-ID chips** copy correctly with `stopPropagation` if nested
- [ ] **Hyperframes data-* attributes** on hero stage (if you used pattern #4)
- [ ] **`document.title`** swaps with language toggle
- [ ] **`localStorage`** persists language preference

If any item fails, fix before shipping.
