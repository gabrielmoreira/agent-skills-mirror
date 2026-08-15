# browser-game-architecture — build, performance & shipping

Toolchain selection, build configuration, asset compression, deploy targets (itch.io in detail), performance engineering, and the release checklist. Pre-release audit methodology: compose with `web-game-release-review`; automated QA: `chrome-browser-automation`.

---

## 1. Choosing the toolchain

| | Zero-build (single HTML file or plain ES modules) | Vite |
|---|---|---|
| Use when | Jams, prototypes, single-mechanic games, AI-generated one-file games | Any dependency (Three.js…), >~3 source files, TypeScript, real release |
| Pros | No install, no config, `file://`-openable (single file), trivially portable | Instant dev server + HMR, hashed bundles, minify/treeshake, TS/import graph |
| Cons | No minify/hash, manual dependency management, ES modules **don't work over `file://`** (CORS) — need any static server anyway | Node toolchain, config surface |

Zero-build discipline: one `index.html` with inline `<style>`/`<script>` *or* plain ES modules served by any static server (`npx serve`, `python -m http.server`). CDN deps via `<script type="importmap">` pinned to exact versions. This is a legitimate shipping strategy for small games — don't add a bundler to a 800-line game out of habit.

Everything else: **Vite**. Don't hand-roll esbuild/rollup configs for games; Vite's defaults are the right defaults.

## 2. Vite scaffold for games

```
mygame/
  index.html          # entry — Vite treats it as the root
  vite.config.js
  public/             # copied verbatim, NOT hashed — audio/levels referenced by runtime URL
    assets/...
  src/
    main.js
    core/ systems/ scenes/ game/   # per SKILL.md spine
```

```js
// vite.config.js
import { defineConfig } from 'vite';
export default defineConfig({
  base: './',            // RELATIVE paths — mandatory for itch.io + GitHub Pages subpaths
  build: {
    target: 'es2020',
    assetsInlineLimit: 4096,   // tiny images inline as data URLs
    chunkSizeWarningLimit: 1500,
  },
  server: { host: true },     // LAN-exposed dev server → test on a real phone during development
});
```

Two asset routes, both fine — pick per asset: `import playerUrl from './assets/player.png'` (hashed, cache-forever, breaks if you build URLs dynamically) vs `public/` + manifest paths like `./assets/player.png` (stable names — pair with §10 versioning). Games with a runtime manifest (`reference.md` §4) usually put game assets in `public/` and let code/CSS go hashed.

- Dev: `npm run dev` — with `host: true`, open the LAN URL on your phone; this is how touch input actually gets tested during development, not after.
- Build: `npm run build` → `dist/`. **Always test `dist/` via `npm run preview`** — dev mode hides path bugs (absolute paths work in dev, break on itch).
- TypeScript: worth it beyond jam scope — Vite transpiles TS natively with zero config (`main.ts`, done); run `tsc --noEmit` in CI for actual type checking. Not a religion: a 500-line jam game in JS is fine.

## 3. Asset budgets & compression

Budgets (casual web game, first playable moment):

- **Total initial download ≤ 5MB** (title + core gameplay); ≤ 20MB grudgingly for rich games with a good loading screen. itch.io hard-caps per-file at 1GB [default; verify current limits] but *players* cap you well before that — every MB is bounce rate on mobile.
- Time-to-playable ≤ 5s on a mid connection. Load the rest behind gameplay (`reference.md` §4.5).

Images: WebP as default (universal since 2020, ~30% smaller than PNG); AVIF optional behind capability check; PNG for pixel art after `pngquant`/`oxipng`. Atlas before compressing (`free-tex-packer`, `TexturePacker`). SVG for flat UI at any DPR.

Audio: `.m4a` (AAC) or `.mp3` single-format (`reference.md` §3.3). Music 96–128kbps stereo, SFX 96kbps mono, `ffmpeg -i in.wav -c:a aac -b:a 96k out.m4a`. Music is nearly always the biggest asset — lazy-load it after boot; procedural synth = zero bytes.

Fonts: WOFF2, subset to used glyphs (`pyftsubset`/`glyphhanger`) — 200KB CJK-capable font → 15KB subset.

JS: Vite minifies/treeshakes. A 2D game's own code should gzip < 200KB; Three.js adds ~150–170KB gz — fine, but audit anything larger arriving via npm (`rollup-plugin-visualizer` when the bundle surprises you). Hosts (itch, Pages, Netlify) serve gzip/brotli automatically — don't pre-compress.

## 4. Single-file builds

One self-contained `index.html` (everything inlined) — for jam uploads, embedding, email-able builds:

```js
// npm i -D vite-plugin-singlefile
import { viteSingleFile } from 'vite-plugin-singlefile';
export default defineConfig({ base: './', plugins: [viteSingleFile()] });
```

Binary assets must be inlined too (raise `assetsInlineLimit`, or base64-embed in source) — practical ceiling ~10–15MB before browsers choke on the HTML parse. Beyond that, ship a normal zip. Single-file is also the natural target format when generating complete games via LLM: no path issues, works from `file://`, one artifact.

## 5. Deploy: itch.io (the usual first target)

Upload format — a **zip** with `index.html` at the **zip root** (not inside a subfolder — the #1 upload failure):

```
build.zip
├─ index.html
└─ assets/...        # everything referenced RELATIVELY (base: './')
```

Project settings that matter:

- Kind of project: **HTML** → check **"This file will be played in the browser"** on the uploaded zip.
- **Viewport**: set to your logical resolution or a clean multiple (e.g. 960×540). Your letterbox scaling (`reference.md` §6) handles the rest; enable **fullscreen button**; check **mobile-friendly** if touch works.
- **SharedArrayBuffer support** toggle: only if you need SAB/threads (Wasm, ffmpeg) — it enables COOP/COEP headers which **break third-party iframes/embeds** on the page. Leave off otherwise.
- Games are served from a sandboxed CDN origin (`*.hwcdn.net` / per-game subdomains): localStorage works but is **not guaranteed durable across re-uploads** — say so if progress matters, offer save export (`reference.md` §5.4). No custom headers, no server code.
- Autoplay: itch shows a click-to-run gate, which conveniently satisfies the audio-unlock gesture — but never rely on it; keep your own unlock (`reference.md` §3.1).

CI uploads via **butler** (itch's CLI): `butler push dist mygame/mygame:html5 --userversion 1.2.0` — idempotent, diff-based, scriptable from GitHub Actions.

## 6. Deploy: other static hosts

- **GitHub Pages**: free, versioned by git. Served at `user.github.io/repo/` — a subpath, which is *why* `base: './'` is mandatory. Deploy via `actions/deploy-pages` or push `dist/` to a `gh-pages` branch. HTTPS included (required for PWA/gamepad/etc.).
- **Netlify / Cloudflare Pages / Vercel**: connect the repo, set build command `npm run build`, output `dist/`. Deploy previews per PR (Netlify/Vercel) are genuinely useful for playtesting links. Custom headers/redirects available (`_headers`, `_redirects` on Netlify) — this is where COOP/COEP goes if you self-host a SAB build.
- **Self-hosted**: any static server; set long `Cache-Control` on hashed assets, `no-cache` on `index.html` (§10).
- All of these are static-only — leaderboards/accounts need a separate backend (out of scope; if tempted, start with a serverless function + KV store and **never trust client-submitted scores**).

## 7. Service worker in production

Full strategy in `reference.md` §8.2; deployment notes: register only in production builds (`if (import.meta.env.PROD && 'serviceWorker' in navigator)`); SW requires HTTPS (all hosts above provide it); scope = directory of `sw.js` — put it at build root; **do not ship a SW on itch.io** (their wrapper/origin handling makes it pointless-to-harmful); GitHub Pages/Netlify are the natural SW targets. Test the *second* deploy (the update path), not just the first install.

## 8. Performance engineering

Frame budget at 60fps is **16.6ms** — but plan for ≤ 8ms of your own work; the browser needs the rest for style/paint/composite, and 120Hz displays exist.

### 8.1 GC pressure — the JS-specific killer

Periodic hitches every few seconds with a sawtooth memory graph = allocation in the hot loop. Sources, in offender order: object/array literals in update/render (`{x,y}` vectors, `[...]` spreads), closures created per frame (`arr.forEach(e => ...)` allocates; use indexed `for` in hot paths), string building (`ctx.fillText('Score: ' + score)` — cache until score changes), and per-shot entity `new`.

Fixes: **object pools** for bullets/particles/vectors (implementation: `examples.md` §5) — `pool.get()` resets and reuses; `pool.release(obj)` on death (pair with the deferred-death sweep, `loop-and-state.md` §7); reusable scratch objects for math (`tmpVec`); numbers-in-fields instead of allocated vectors where feasible. Verify in DevTools → Performance: record 10s of gameplay, look for minor-GC frequency and long frames aligned with GC.

### 8.2 Rendering cost

Canvas 2D: draw calls and overdraw dominate — cull off-screen entities before drawing (a bounds check is ~free; a clipped `drawImage` is not); pre-render static layers (`reference.md` §1.2); batch by sprite sheet; avoid `shadowBlur`/`filter` per-frame (rasterize once offscreen); round positions with `|0` when smoothing is off (subpixel = shimmer + cost). WebGL: draw-call/texture discipline per `threejs-game-development`. DOM: compositor-only properties (`reference.md` §1.4).

### 8.3 Loading performance

Decode jank (first-draw stutter) → warm-up blit at load (`reference.md` §4.2). Parse cost: 5MB of JS costs real main-thread time on phones even cached — another reason for the budget. Measure loads with DevTools throttling ("Fast 4G", 4× CPU) — your dev machine on localhost is a lie.

### 8.4 Measuring

Order of operations when "it stutters": (1) Performance recording during actual gameplay — is it GC (§8.1), long update (sim over budget → `loop-and-state.md` §2.3), long paint (rendering §8.2), or decode spikes (§8.3)? (2) Fix the category, not symptoms. (3) Re-measure on the slowest target device, not your workstation. An on-screen dev HUD (fps + update ms + render ms + entity count, toggled by a debug key) catches regressions the profiler is never open for. Methodology depth: `game-performance-profiling`.

## 9. Release checklist

Run `web-game-release-review` for the full audit; the architectural minimum:

**Boot & platform** — builds and runs from `dist/` via `npm run preview` (not just dev mode); works at the deploy URL's real path depth; Chrome + Firefox + Safari desktop; iOS Safari + Android Chrome on hardware, both orientations; in-app browsers (open your link from a social app) at least don't crash with an unhelpful screen.

**The classics** (each maps to a `reference.md` section): audio after first gesture, on iOS hardware (§3); no scroll/zoom fighting on mobile (§2.2); tab-away → return: paused, no dt explosion, music didn't play while hidden (§7); save survives reload; save flushed on mobile task-kill (§5.3); corrupt-save handling — hand-edit localStorage to garbage, game must boot (§5.2); window resize mid-game stays crisp and letterboxed (§6.3); fonts loaded before first text render (§4.3); crash overlay wired (§9); gamepad disconnect pauses (§2.3).

**Performance** — 60fps sustained on a mid phone during the busiest scene; initial download within budget (§3); loading screen shows real progress and handles a failed fetch.

**Automated smoke test** (via `chrome-browser-automation`, run in CI on every deploy): serve `dist/` over HTTP → open → wait for boot → **assert zero console errors** → assert canvas non-blank (sample pixels) → dispatch `pointerdown` (unlock + start) → step 2–3s → assert still zero errors → screenshot artifact. This ~10-line script catches the majority of "shipped a broken build" incidents: path 404s, undefined-variable crashes, blank canvas.

## 10. Versioning & cache busting

The failure this section prevents: player has cached `index.html` referencing hashed assets that no longer exist → broken game until hard-refresh.

- Hashed bundles (Vite default) are self-busting; `index.html` must be revalidated — hosts above default `index.html` to short/no cache (self-hosting: `Cache-Control: no-cache` on it, `max-age=31536000, immutable` on hashed assets).
- `public/` assets have **stable names** → bust manually: manifest URLs like `./assets/player.png?v=13`, with the version stamped from one constant.
- Stamp `APP_VERSION` (from `package.json` via `define` in vite.config) into: the on-screen corner of the title screen (player bug reports become actionable), the save schema envelope (`reference.md` §5.2), the SW cache name (§7), and the `?v=` above. One constant, four consumers.
- itch.io: butler `--userversion` + the on-screen version; their CDN handles asset caching sanely on re-upload.
- Keep a `CHANGELOG.md`; players notice unlabeled balance changes and assume bugs.
