# Static-site rebuild pitfalls (3D-printing-business case)

Post-mortem from a landing-page rebuild where the page came back with a broken/blank middle. Root causes and the exact fixes that worked. Read before shipping any redesign of an existing HTML/CSS/JS page.

## 1. CSS class-name mismatch (silent no-op)
**Symptom:** Page looks unstyled / partially broken after a "redesign". No JS errors.
**Cause:** A full CSS rewrite targeted selectors that don't exist in the HTML (e.g. `.hero-title` when the HTML uses `.hero h1`, or entirely new BEM names the HTML never received).
**Fix:** Before writing CSS, read the HTML and list the real class names. Write CSS against those. If you want new class names, edit the HTML too. Verify by searching the HTML for each top-level class your CSS uses — a class with zero DOM matches is a dead rule.

## 2. Reveal-on-scroll vs JS-injected DOM (the blank-middle bug)
**Symptom:** Hero + first section fine, but materials/gallery/services (anything rendered by JS) is completely invisible — yet the DOM nodes exist when you inspect.
**Cause:** CSS `.reveal-item { opacity: 0; transform: translateY(20px); }` revealed by an IntersectionObserver that runs once on init. JS injects cards into the DOM *after* init, so they never get observed → they sit at opacity:0 forever.
**Fix (pick one):**
- Reveal injected nodes explicitly right after you append them: `el.classList.add('revealed')` (or set inline `opacity = 1`).
- After injecting, re-query and observe the new nodes: `newNodes.forEach(n => observer.observe(n))`.
- Give injected elements `opacity:1` by default and apply the reveal pattern only to static, above-the-fold content.
**Rule of thumb:** any element created by JS must either start visible or be revealed by the same code that creates it.

## 3. Parallel `patch` calls can corrupt files
**Symptom:** A section gets the wrong classes (e.g. `footer-grid` became `services-grid`) even though you "patched" it correctly.
**Cause:** Issuing multiple `patch` tool calls in the same turn where `old_string` is a short token also present elsewhere — the fuzzy matcher applied the replacement to the wrong occurrence/element.
**Fix:** Make every `old_string` unique by including distinctive surrounding context (an adjacent class, a comment, the element's id). Avoid firing several structural HTML patches in one block; serialize the risky ones.

## 4. Verification when the vision model is down
- `browser_console` → check `js_errors` is empty and your init log fired.
- `browser_snapshot` → confirm sections/cards are present in the DOM (if something looks missing, check computed style, not just node presence — opacity:0 nodes still appear in the snapshot).
- `browser_vision` may 404 if the active model isn't vision-capable (e.g. `tencent/hy3:free`). Capture the screenshot path and tell the user to inspect it; do NOT claim the look "passes."
