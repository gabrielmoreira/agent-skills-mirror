# Chrome Browser Automation — worked examples

End-to-end flows composing the recipes (R#) and reference sections (§#). Each example states the
trigger, risk tier ([safety-rules.md](safety-rules.md) §3), and the verification that closes it.

---

## E1 — Research fan-out: harvest three docs pages → JSONL

**Trigger:** "Compare the rate-limit docs of these three APIs." **Tier:** green (public docs).

```js
// run from known-good playwright cwd (reference §1); skeleton from R3
const urls = [
  "https://docs.example-a.com/rate-limits",
  "https://docs.example-b.com/limits",
  "https://docs.example-c.com/api/quotas",
];
const results = await fanout(context, urls, async (p) => {   // R4, limit 3
  await p.locator("main, article").first().waitFor({ timeout: 15_000 });
  return {
    title: await p.title(),
    headings: await p.locator("main h1, main h2, article h1, article h2").allInnerTexts(),
    text: (await p.locator("main, article").first().innerText()).slice(0, 20_000),
  };
});
fs.writeFileSync(`${dir}/harvest.jsonl`,
  results.map((r) => JSON.stringify({ ...r, fetched_at: new Date().toISOString() })).join("\n"));
```

**Verify:** every line parses as JSON; `ok:false` entries reported, not hidden. Failures include a
`shot-FAIL` screenshot per R3. Large-scale/repeated crawling → route to `end-to-end-web-scraping`
(robots/ToS gates) instead of scaling this up.

---

## E2 — Web app: form fill + network-confirmed submit + visual verify

**Trigger:** "Add a new project named Q3-Report in the dashboard." **Tier:** yellow (logged-in
SaaS, reversible create). Auth check first per workflow step 4.

```js
await page.goto("https://app.example.com/projects", { waitUntil: "domcontentloaded" });
// Signed-in gate: the task's element, not cookies alone (browser-connection signals doctrine)
await page.getByRole("button", { name: "New project" }).waitFor({ timeout: 15_000 })
  .catch(async () => { await page.screenshot({ path: `${dir}/signed-out.png` });
                       throw new Error("STOP: signed out or wrong account — human signs in via hub window"); });

await page.getByRole("button", { name: "New project" }).click();
await page.getByLabel("Project name").fill("Q3-Report");

const resp = page.waitForResponse((r) => r.url().includes("/api/projects") && r.request().method() === "POST" && r.ok()); // R6
await page.getByRole("button", { name: "Create" }).click();
const created = await (await resp).json();                   // harvest the API truth

await page.getByRole("link", { name: "Q3-Report" }).waitFor(); // UI reflects it
await page.screenshot({ path: `${dir}/shot-created.png`, fullPage: true });
fs.writeFileSync(`${dir}/result.json`, JSON.stringify({ created }, null, 2));
```

**Verify:** three independent signals — 2xx POST response body, the new item visible in DOM, and
the screenshot (agent Reads it). Any mismatch = report, don't declare success.

---

## E3 — CSV export download, tier-escalating

**Trigger:** "Download the transactions CSV from the analytics app." **Tier:** yellow.

```js
let csvPath;
try {                                                        // Tier 1 (R9)
  const dl = page.waitForEvent("download", { timeout: 30_000 });
  await page.getByRole("button", { name: /export csv/i }).click();
  const d = await dl; csvPath = `${dir}/downloads/${d.suggestedFilename()}`;
  await d.saveAs(csvPath);
} catch {
  csvPath = await tier3WatchDownloads();                     // R11 — always works
}
// Completion criteria (reference §7): exists, >0 bytes, actually parses as CSV
const text = fs.readFileSync(csvPath, "utf8");
if (!text.trim() || text.startsWith("<!DOCTYPE") ) throw new Error("got an HTML error page, not CSV");
const header = text.split(/\r?\n/)[0].split(",");
fs.writeFileSync(`${dir}/result.json`, JSON.stringify({ csvPath, rows: text.split(/\r?\n/).length - 1, header }));
```

**Verify:** header columns match expectation; row count > 0 reported to user. If the export needs
a date-range dialog you can't validate → screenshot the dialog and ask, don't guess ranges on
financial-ish data.

---

## E4 — Canvas game smoke test (local build)

**Trigger:** "Smoke-test my HTML5 game build before review." **Tier:** green (localhost).
Composes with `web-game-release-review` (this run produces its live evidence) and
`game-debugging` (adding `window.__game` hooks when probes come back blind).

```powershell
# 1. Serve the build (reference §14) — your server, your process
Push-Location "C:\dev\mygame\dist"; $srv = Start-Process -PassThru npx -ArgumentList "http-server","-p","8080","-s"
```

```js
// 2. Drive it
const errors = installCollectors(page);                      // R19 — BEFORE goto
await page.goto("http://localhost:8080", { waitUntil: "domcontentloaded" });
const canvas = page.locator("canvas").first();
await canvas.waitFor({ timeout: 20_000 });
await page.screenshot({ path: `${dir}/shot-boot.png` });     // menu/boot state

// 3. Start + play: focus, then held-key input (R15/R16)
const b = await canvas.boundingBox();
await page.mouse.click(b.x + b.width / 2, b.y + b.height / 2);
await page.bringToFront();
await page.keyboard.press("Enter");                          // start (game-specific)
await page.keyboard.down("ArrowRight"); await page.waitForTimeout(1500); await page.keyboard.up("ArrowRight");
await page.screenshot({ path: `${dir}/shot-after-input.png`, clip: await canvas.boundingBox() });

// 4. Probes: movement happened (screenshot hash differs — R14), state hook if present, FPS (R17)
const state = await page.evaluate(() => window.__game ?? null);   // hedged: only if build exposes it
const fps = await sampleFps(page, 3);

// 5. Verdict data
fs.writeFileSync(`${dir}/result.json`, JSON.stringify({
  fps, state, errors,
  moved: sha(`${dir}/shot-boot.png`) !== sha(`${dir}/shot-after-input.png`),
}, null, 2));
```

```powershell
# 6. Teardown server
Stop-Process -Id $srv.Id; Pop-Location
```

**Verify (invariants, not exact states — reference §10.4):** canvas rendered non-blank; input
produced visual change; `errors.page` empty; FPS ≥ 30 (or the game's stated target); screenshots
Read by the agent for obvious rendering garbage. Blind pixel probes on a WebGL build → use the
screenshot path, not `getImageData` (R18 note).

---

## E5 — Failure recovery walkthrough

**Scenario:** attach fails, then a tab crashes, then a login wall — the three most common breaks,
handled per reference §12.

1. `connectOverCDP` → `ECONNREFUSED`. Run `start.ps1` (only permitted launcher), retry once.
   Still down → `doctor.ps1 -Deep`, attach its output to the report, **stop**. Never improvise a
   `chromium.launch()` "just to get the task done" — that is the historical failure mode on this
   machine.
2. Mid-task `Target crashed`: the tab is gone, the browser is fine. `context.newPage()`, re-navigate,
   resume from the last checkpoint recorded in `run.log`. Second crash on the same URL → stop and
   report with `shot-FAIL` + DOM dump (R23 wrote them).
3. The app shows a login form: **hard stop.** Screenshot, then report exactly per
   `browser-connection`: which site, which expected identity (the account already
   signed in for that site, or whatever the task stated), and that the human should sign in **in the hub window**.
   Never type credentials (HR8), never conclude "broken selectors" before checking the signed-in
   signals — signed-out and wrong-account mimic broken pages.

---

## E6 — Visual iteration loop for frontend work

**Trigger:** "Tweak the hero section until it matches the mock." **Tier:** green (localhost dev
server). This is the edit → reload → screenshot → judge loop; the agent's eyes are the Read tool.

```js
// after each code edit (dev server hot-reloads):
await page.reload({ waitUntil: "domcontentloaded" });
await page.locator("#hero").waitFor();
await page.evaluate(() => document.fonts.ready);             // typography settles (reference §9)
await page.locator("#hero").screenshot({ path: `${dir}/hero-iter${n}.png` });
```

Then Read `hero-iter<n>.png`, compare against the mock, edit code, repeat. Keep every iteration
numbered — the sequence is the review trail. Aesthetic judgment rubric → `ui-visual-fidelity-audit`;
durable regression tests for the final state → `playwright-test-automation` (`toHaveScreenshot`).
