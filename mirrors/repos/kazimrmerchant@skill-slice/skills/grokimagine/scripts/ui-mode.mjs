/**
 * Shared Grok Imagine UI helpers — Aug 2026 composer.
 * Modes are aria-label radios inside [aria-label="Generation mode"].
 * Default landing is often Video — always set mode explicitly.
 */
import fs from "fs";
import path from "path";

export async function selectGenerationMode(page, mode) {
  const want = String(mode || "Image");
  const label =
    want === "Image" || want === "Video" || want === "Agent"
      ? want
      : want.charAt(0).toUpperCase() + want.slice(1).toLowerCase();

  // Prefer exact aria-label radio (text is often empty when unselected)
  const radio = page.locator(`[role="radio"][aria-label="${label}"]`);
  if (await radio.count()) {
    await radio.first().click({ force: true }).catch(() => {});
    await page.waitForTimeout(700);
  } else {
    const byRole = page.getByRole("radio", { name: new RegExp(`^${label}$`, "i") });
    if (await byRole.count()) {
      await byRole.first().click({ force: true }).catch(() => {});
      await page.waitForTimeout(700);
    } else {
      return { ok: false, how: "not_found", label };
    }
  }

  const group = page.locator('[aria-label="Generation mode"]');
  let groupText = "";
  if (await group.count()) {
    groupText = ((await group.first().innerText().catch(() => "")) || "").trim();
  }
  const url = page.url();
  const checked =
    (await radio.first().getAttribute("aria-checked").catch(() => null)) === "true" ||
    (await page
      .getByRole("radio", { name: new RegExp(`^${label}$`, "i") })
      .first()
      .getAttribute("aria-checked")
      .catch(() => null)) === "true";
  // Prefer aria-checked; groupText often only shows the selected label
  const ok =
    label === "Agent"
      ? /\/imagine\/agent/i.test(url) || /Agent/i.test(groupText) || checked
      : checked || new RegExp(label, "i").test(groupText) || groupText === "";
  return { ok, how: "aria-radio", label, groupText, url, checked };
}

export async function setImageQuality(page) {
  const quality = page.getByRole("radio", { name: /^Quality$/i });
  if (await quality.count()) {
    await quality.first().click({ force: true }).catch(() => {});
    await page.waitForTimeout(300);
    return "quality-radio";
  }
  const btn = page.getByRole("button", { name: /^Quality$/i });
  if (await btn.count()) {
    await btn.first().click({ force: true }).catch(() => {});
    return "quality-button";
  }
  return "none";
}

export async function setAspect169(page) {
  const ar = page.locator('[aria-label="Aspect Ratio"]');
  if (!(await ar.count())) return "no-aspect";
  const txt = ((await ar.first().innerText().catch(() => "")) || "").trim();
  if (/16:9/.test(txt)) return "already-16:9";
  await ar.first().click({ force: true }).catch(() => {});
  await page.waitForTimeout(400);
  const opt = page.getByRole("option", { name: /16:9/i });
  if (await opt.count()) {
    await opt.first().click({ force: true }).catch(() => {});
    return "option-16:9";
  }
  const item = page.locator('[role="menuitem"], button, div').filter({ hasText: /^16:9$/ });
  if (await item.count()) {
    await item.first().click({ force: true }).catch(() => {});
    return "menuitem-16:9";
  }
  await page.keyboard.press("Escape").catch(() => {});
  return "opened-no-option";
}

export async function setVideoPrefs(page, { resolution = "720p", duration = "10s" } = {}) {
  // Prefer aria-label radios (same pattern as Generation mode)
  const resAria = page.locator(`[role="radio"][aria-label="${resolution}"]`);
  if (await resAria.count()) await resAria.first().click({ force: true }).catch(() => {});
  else {
    const res = page.getByRole("radio", { name: new RegExp(`^${resolution}$`, "i") });
    if (await res.count()) await res.first().click({ force: true }).catch(() => {});
  }
  const durAria = page.locator(`[role="radio"][aria-label="${duration}"]`);
  if (await durAria.count()) await durAria.first().click({ force: true }).catch(() => {});
  else {
    const dur = page.getByRole("radio", { name: new RegExp(`^${duration}$`, "i") });
    if (await dur.count()) await dur.first().click({ force: true }).catch(() => {});
  }
  await page.waitForTimeout(400);
  return { resolution, duration };
}

/** Video audio speaker toggle — aria-pressed true = native audio on */
export async function setVideoAudio(page, enabled = true) {
  const btn = page.locator('[aria-label="Video audio"]');
  if (!(await btn.count())) return { ok: false, reason: "no_audio_btn" };
  const pressed = (await btn.first().getAttribute("aria-pressed")) === "true";
  if (pressed !== !!enabled) {
    await btn.first().click({ force: true }).catch(() => {});
    await page.waitForTimeout(300);
  }
  const after = (await btn.first().getAttribute("aria-pressed")) === "true";
  return { ok: after === !!enabled, enabled: after };
}

/** Prefer hidden file input under Upload (images only, may be multiple refs) */
export async function attachReferenceImages(page, imagePaths) {
  const paths = (Array.isArray(imagePaths) ? imagePaths : [imagePaths]).filter(Boolean);
  if (!paths.length) return { ok: true, how: "none", count: 0 };
  for (const p of paths) {
    if (!fs.existsSync(p)) return { ok: false, reason: "missing_image", path: p };
  }
  const abs = paths.map((p) => path.resolve(p));
  const inputs = page.locator('input[type="file"]');
  if (await inputs.count()) {
    await inputs.first().setInputFiles(abs.length === 1 ? abs[0] : abs);
    await page.waitForTimeout(1500);
    return { ok: true, how: "input-file", count: abs.length };
  }
  const upload = page.locator('[aria-label="Upload"]');
  if (await upload.count()) {
    try {
      const [chooser] = await Promise.all([
        page.waitForEvent("filechooser", { timeout: 5000 }),
        upload.first().click({ force: true }),
      ]);
      await chooser.setFiles(abs);
      await page.waitForTimeout(1500);
      return { ok: true, how: "filechooser", count: abs.length };
    } catch (e) {
      return { ok: false, reason: "chooser_failed", error: String(e).slice(0, 120) };
    }
  }
  return { ok: false, reason: "no_file_input" };
}

export async function ensureOneImagineTab(context, { allowMulti = false } = {}) {
  const pages = context.pages();
  const imagine = pages.filter(
    (p) => /grok\.com\/imagine\/?(\?|$|#)/i.test(p.url()) && !/\/imagine\/agent/i.test(p.url()),
  );
  const agent = pages.filter((p) => /\/imagine\/agent/i.test(p.url()));
  if (!allowMulti) {
    for (let i = 1; i < imagine.length; i++) {
      await imagine[i].close().catch(() => {});
    }
    // Keep at most one agent tab too when cleaning for Image/Video work
    for (let i = 1; i < agent.length; i++) {
      await agent[i].close().catch(() => {});
    }
  }
  const keep =
    imagine.find((p) => /grok\.com\/imagine\/?(\?|$|#)/i.test(p.url()) && !/\/imagine\/(post|agent)\//i.test(p.url())) ||
    imagine[0] ||
    pages.find((p) => /grok\.com/i.test(p.url())) ||
    pages[0];
  if (keep) await keep.bringToFront().catch(() => {});
  return keep;
}

export async function goCleanImagineHome(page) {
  if (!/grok\.com\/imagine\/?(\?|$|#)/i.test(page.url()) || /\/imagine\/(agent|post)\//i.test(page.url())) {
    await page.goto("https://grok.com/imagine", {
      waitUntil: "domcontentloaded",
      timeout: 60000,
    });
    await page.waitForTimeout(2000);
  }
  const ng = page.locator('[aria-label="New Generation"]');
  if (await ng.count()) {
    await ng.first().click({ force: true }).catch(() => {});
    await page.waitForTimeout(1200);
  } else {
    const ngText = page.getByText(/^New Generation$/i);
    if (await ngText.count()) {
      await ngText.first().click({ force: true }).catch(() => {});
      await page.waitForTimeout(1200);
    }
  }
}

/** Submit: prefer Send/Submit; else up-arrow near composer; else Enter */
export async function submitImagine(page) {
  const send = page.locator(
    'button[aria-label="Send"], button[aria-label="Submit"], button[aria-label*="Send" i]',
  );
  if (await send.count()) {
    const btn = send.last();
    if (!(await btn.isDisabled().catch(() => false))) {
      await btn.click();
      return "send";
    }
  }
  // Circular up-arrow submit (common 2026 UI) — often no "Send" label
  const candidates = page.locator("button");
  const n = await candidates.count();
  for (let i = n - 1; i >= 0; i--) {
    const el = candidates.nth(i);
    const box = await el.boundingBox().catch(() => null);
    if (!box || box.y < 400 || box.width > 80 || box.height > 80) continue;
    const aria = (await el.getAttribute("aria-label").catch(() => "")) || "";
    const disabled = await el.isDisabled().catch(() => true);
    if (disabled) continue;
    if (!aria || /send|submit|generate|arrow|post/i.test(aria)) {
      await el.click({ force: true }).catch(() => {});
      return aria ? `btn:${aria}` : "near-composer-btn";
    }
  }
  await page.keyboard.press("Enter");
  return "enter";
}
