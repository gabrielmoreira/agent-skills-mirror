# Playwright + CDP recipes (owned Chrome, port 9222)

Copy-paste recipes for agent scripts. All are ESM `.mjs`, run with `node` from a cwd that has
`playwright` installed (reference §1). Every recipe assumes the hard rules in
[safety-rules.md](safety-rules.md): attach-only, own tabs, no credentials, no evasion.

Conventions used throughout:

```js
const OUT = "~/.cursor/browser-hub/out";   // forward slashes are fine in Node
const CDP = "http://127.0.0.1:9222";
const ts  = () => new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
```

---

## R1 — Attach (preferred: `attachHub`; fallback: raw CDP)

```js
// Preferred — hub helper handles ensure-start, own tab, optional site lock.
import { pathToFileURL } from "node:url";
const { attachHub } = await import(
  pathToFileURL("~/.cursor/browser-hub/scripts/connect.mjs").href
);

const hub = await attachHub({
  url: "https://example.com",
  newPage: true,       // ALWAYS true — own-tab discipline
  ensureStart: true,   // runs start.ps1 if CDP is down
  // siteLock: true,   // only for stateful single-composer sites (see R24)
});
// Return shape hedged (reference §15): expect at least a Playwright page + closeOwnPage().
// First use: console.log(Object.keys(hub)) and update this comment to verified.
const page = hub.page ?? hub;
```

```js
// Raw fallback — fully verified Playwright API, no helper.
import { chromium } from "playwright";

const browser = await chromium.connectOverCDP(CDP);       // throws if CDP down → start.ps1 (R3)
const context = browser.contexts()[0];                    // the ONE authed default context
if (!context) throw new Error("no default context — Chrome mid-startup? retry in 2s");
const page = await context.newPage();                     // your tab; track and close it
```

## R2 — Teardown (never quits Chrome)

```js
// In a finally block, always:
try { await page.close(); } catch {}                      // close every page YOU opened
try { hub?.closeOwnPage ? await hub.closeOwnPage() : null; } catch {}
try { await page.unrouteAll?.({ behavior: "ignoreErrors" }); } catch {} // if you used R8
await browser?.close();   // disconnects the CDP client ONLY — real Chrome keeps running (verified)
// NEVER: stop.ps1 here. NEVER: killing chrome.exe.
```

## R3 — Full script skeleton with hub start + diagnostics

```js
import { chromium } from "playwright";
import fs from "node:fs";
import { execSync } from "node:child_process";

const START = `powershell -NoProfile -ExecutionPolicy Bypass -File "${process.env.BROWSER_HUB}\\scripts\\start.ps1"`;

async function connectWithStart() {
  for (let i = 0; i < 2; i++) {
    try { return await chromium.connectOverCDP(CDP, { timeout: 5000 }); }
    catch { if (i === 0) execSync(START, { stdio: "inherit" }); else throw new Error("CDP down after start.ps1 — run doctor.ps1 and report"); }
  }
}

const browser = await connectWithStart();
const context = browser.contexts()[0];
const page = await context.newPage();
const dir = `${OUT}/myjob-${ts()}`; fs.mkdirSync(dir, { recursive: true });
try {
  // ... work ...
  await page.screenshot({ path: `${dir}/shot-final.png`, fullPage: true });
} catch (e) {
  await page.screenshot({ path: `${dir}/shot-FAIL.png`, fullPage: true }).catch(() => {});
  fs.writeFileSync(`${dir}/dom-FAIL.html`, await page.content().catch(() => ""));
  throw e;
} finally {
  await page.close().catch(() => {});
  await browser.close();
}
```

## R4 — Multi-tab fan-out with a concurrency cap

```js
async function fanout(context, urls, worker, limit = 3) {   // tab budget ≤ 4 (reference §4)
  const results = [];
  for (let i = 0; i < urls.length; i += limit) {
    const batch = urls.slice(i, i + limit);
    results.push(...await Promise.all(batch.map(async (url) => {
      const p = await context.newPage();                    // own tab per unit of work
      try {
        await p.goto(url, { waitUntil: "domcontentloaded", timeout: 45_000 });
        return { url, ok: true, data: await worker(p) };
      } catch (e) { return { url, ok: false, error: String(e) }; }
      finally { await p.close().catch(() => {}); }          // no zombie tabs
    })));
  }
  return results;
}
```

## R5 — Capture a popup you triggered

```js
const popupPromise = page.waitForEvent("popup");            // register BEFORE the click
await page.getByRole("link", { name: "Open report" }).click();
const popup = await popupPromise;                           // you own this page too
await popup.waitForLoadState("domcontentloaded");
// ... use popup ...
await popup.close();                                        // and you close it
```

## R6 — Response-gated action (and API harvesting)

```js
const respPromise = page.waitForResponse(
  (r) => r.url().includes("/api/submit") && r.ok(),        // URL AND status — 500 also responds
  { timeout: 20_000 },
);
await page.getByRole("button", { name: "Save" }).click();
const resp = await respPromise;
const payload = await resp.json().catch(() => null);        // harvest JSON instead of scraping DOM
```

## R7 — Poll helper for non-DOM conditions

```js
async function poll(fn, { timeout = 30_000, interval = 500, desc = "condition" } = {}) {
  const t0 = Date.now();
  for (;;) {
    const v = await fn();
    if (v) return v;
    if (Date.now() - t0 > timeout) throw new Error(`poll timeout: ${desc}`);
    await new Promise((r) => setTimeout(r, interval));
    interval = Math.min(interval * 1.5, 4000);              // back off
  }
}
// e.g. await poll(() => page.evaluate(() => window.__game?.state === "ready"), { desc: "game ready" });
```

## R8 — Block third-party noise in YOUR tab only

```js
// page.route only. context.route on the shared context is FORBIDDEN (safety-rules §5).
await page.route(/google-analytics\.com|googletagmanager\.com|doubleclick\.net|segment\.io/, (r) => r.abort());
// teardown (R2): await page.unrouteAll({ behavior: "ignoreErrors" });
```

## R9 — Download, Tier 1: Playwright event (hedged — try first)

```js
const dlPromise = page.waitForEvent("download", { timeout: 60_000 });
await page.getByRole("button", { name: "Export CSV" }).click();
const dl = await dlPromise;
const target = `${dir}/downloads/${dl.suggestedFilename()}`;
await dl.saveAs(target);                                    // if this throws/hangs → R10
```

## R10 — Download, Tier 2: CDP setDownloadBehavior (hedged; reset after!)

```js
const cdp = await browser.newBrowserCDPSession();
const dlDir = `${dir}/downloads`.replace(/\//g, "\\");      // CDP wants an absolute OS path
await cdp.send("Browser.setDownloadBehavior",
  { behavior: "allow", downloadPath: dlDir, eventsEnabled: true });
const done = new Promise((res, rej) => {
  cdp.on("Browser.downloadProgress", (e) => {
    if (e.state === "completed") res(e);
    if (e.state === "canceled") rej(new Error("download canceled"));
  });
});
await page.getByRole("button", { name: "Export CSV" }).click();
await done;
await cdp.send("Browser.setDownloadBehavior", { behavior: "default" }); // ALWAYS reset — browser-global state
await cdp.detach();
```

## R11 — Download, Tier 3: watch the real Downloads folder (always works)

```js
import fs from "node:fs"; import path from "node:path";
const DL = "~/Downloads";
const before = new Set(fs.readdirSync(DL));
await page.getByRole("button", { name: "Export CSV" }).click();
const file = await poll(() => {
  const fresh = fs.readdirSync(DL).filter((f) => !before.has(f) && !f.endsWith(".crdownload"));
  if (!fresh.length) return null;
  const f = path.join(DL, fresh[0]);
  const s1 = fs.statSync(f).size;                           // size-stability check
  return new Promise((r) => setTimeout(() => r(fs.statSync(f).size === s1 && s1 > 0 ? f : null), 1000));
}, { timeout: 120_000, desc: "download in real Downloads dir" });
fs.renameSync(file, `${dir}/downloads/${path.basename(file)}`); // relocate into task artifacts
```

## R12 — Upload

```js
await page.locator('input[type="file"]').setInputFiles("C:/abs/path/asset.png"); // works even if visually hidden
// drop-zone-only UIs: see playwright-test-automation §Advanced (synthetic DataTransfer drop)
```

## R13 — Screenshots for the verify loop

```js
await page.screenshot({ path: `${dir}/shot-01-loaded.png`, fullPage: true });
await page.locator("#pricing-table").screenshot({ path: `${dir}/shot-02-pricing.png` });
const box = await page.locator("canvas").boundingBox();     // region shot (games, widgets)
await page.screenshot({ path: `${dir}/shot-03-canvas.png`, clip: box });
// Then: agent Reads the PNG and judges. Keep every iteration — audit trail (reference §9).
```

## R14 — Cheap change-detection diff (not baseline testing)

```js
import fs from "node:fs"; import crypto from "node:crypto";
const sha = (p) => crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
const changed = sha(`${dir}/shot-before.png`) !== sha(`${dir}/shot-after.png`);
// Byte-hash says "anything changed" (anti-aliasing noise counts). For "did MY region change",
// clip-screenshot the region (R13) first. Real baseline comparison → playwright-test-automation.
```

## R15 — Canvas: focus + held keys

```js
const canvas = page.locator("canvas").first();              // itch/Godot embeds: use frameLocator first (reference §10.1)
const box = await canvas.boundingBox();
await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2); // focus — MANDATORY before keys
await page.bringToFront();                                  // headful Chrome throttles background tabs

await page.keyboard.down("ArrowRight");                     // hold, don't press — games poll key state per frame
await page.waitForTimeout(800);                             // hold duration (sanctioned sleep: expresses gameplay, not waiting)
await page.keyboard.up("ArrowRight");
await page.keyboard.press("Space");                         // discrete actions can use press
```

## R16 — Canvas: mouse at relative coordinates

```js
async function canvasClick(page, canvas, relX, relY) {      // rel 0..1 → resize-proof
  const b = await canvas.boundingBox();
  await page.mouse.click(b.x + relX * b.width, b.y + relY * b.height);
}
async function canvasDrag(page, canvas, from, to, steps = 12) {
  const b = await canvas.boundingBox();
  await page.mouse.move(b.x + from[0] * b.width, b.y + from[1] * b.height);
  await page.mouse.down();
  await page.mouse.move(b.x + to[0] * b.width, b.y + to[1] * b.height, { steps }); // steps → smooth, game-visible motion
  await page.mouse.up();
}
```

## R17 — FPS sample

```js
const fps = await page.evaluate(async (seconds) => {
  let frames = 0; const t0 = performance.now();
  await new Promise((done) => {
    const tick = () => { frames++; (performance.now() - t0 < seconds * 1000) ? requestAnimationFrame(tick) : done(); };
    requestAnimationFrame(tick);
  });
  return frames / seconds;
}, 3);
// Tab must be frontmost (R15 bringToFront) or Chrome throttles rAF to ~1fps.
```

## R18 — Canvas pixel probe

```js
// 2D canvas — direct pixel read:
const px = await page.evaluate(({ x, y }) => {
  const c = document.querySelector("canvas");
  const d = c.getContext("2d")?.getImageData(x, y, 1, 1)?.data;
  return d ? [...d] : null;                                 // null ⇒ WebGL canvas → fall through
}, { x: 100, y: 100 });

// WebGL — getImageData/toDataURL are blank unless preserveDrawingBuffer:true (reference §10.3).
// Immune path: compositor screenshot of the canvas region (R13), then judge visually or
// decode the PNG in Node if a programmatic pixel value is truly required.
```

## R19 — Console / pageerror / requestfailed collectors

```js
const IGNORE = [/favicon\.ico/, /ResizeObserver loop/];
const errors = { console: [], page: [], net: [] };
page.on("console", (m) => { if (m.type() === "error" && !IGNORE.some((r) => r.test(m.text()))) errors.console.push(m.text()); });
page.on("pageerror", (e) => errors.page.push(e.message));
page.on("requestfailed", (r) => errors.net.push(`${r.method()} ${r.url()} — ${r.failure()?.errorText}`));
// Attach IMMEDIATELY after newPage, assert at the end:
// if (errors.page.length) → task fails with the list; write errors to `${dir}/errors.json` either way.
```

## R20 — Dialogs (register before triggering)

```js
page.on("dialog", async (d) => { await d.dismiss(); });     // default-dismiss on an authed shared browser
// Only accept() when the dialog is an expected part of YOUR flow and its text matches:
page.once("dialog", async (d) => { d.message().includes("Export all rows?") ? await d.accept() : await d.dismiss(); });
```

## R21 — Read page storage (read-only)

```js
const storage = await page.evaluate(() => ({
  local: { ...localStorage }, session: { ...sessionStorage },
}));
// READ ONLY. Never clear/overwrite storage or cookies on the shared browser (safety-rules §5).
// Never write harvested tokens into artifacts — redact before saving (safety-rules §6).
```

## R22 — Scroll & lazy-load harvest

```js
const items = new Map();
for (let i = 0; i < 20; i++) {                              // hard iteration cap — no infinite loops
  for (const el of await page.locator("[data-item-id]").all()) {
    const id = await el.getAttribute("data-item-id");
    if (!items.has(id)) items.set(id, await el.innerText());
  }
  const before = items.size;
  await page.mouse.wheel(0, 1200);
  await page.waitForLoadState("domcontentloaded");
  await poll(() => page.locator("[data-item-id]").count().then((c) => c > before || null),
             { timeout: 4000, desc: "more items" }).catch(() => {});
  if (items.size === before) break;                         // saturated
}
```

## R23 — Retry wrapper with diagnostics on failure

```js
async function step(name, fn, { retries = 1 } = {}) {       // ONE retry, changed-hypothesis rule (reference §12)
  for (let a = 0; ; a++) {
    try { return await fn(); }
    catch (e) {
      await page.screenshot({ path: `${dir}/FAIL-${name}-a${a}.png`, fullPage: true }).catch(() => {});
      if (a >= retries) { fs.writeFileSync(`${dir}/FAIL-${name}.html`, await page.content().catch(() => "")); throw e; }
      await page.reload({ waitUntil: "domcontentloaded" }).catch(() => {});
    }
  }
}
```

## R24 — Site lock for stateful flows

```js
// Preferred: attachHub({ url, newPage: true, siteLock: true })
// Manual:
const { acquireSiteLock } = await import(
  pathToFileURL("~/.cursor/browser-hub/scripts/connect.mjs").href
);
const release = await acquireSiteLock("example.com");       // waits/fails if held & fresh — never delete a fresh lock
try { /* stateful single-composer work */ } finally { await release?.(); }
```
