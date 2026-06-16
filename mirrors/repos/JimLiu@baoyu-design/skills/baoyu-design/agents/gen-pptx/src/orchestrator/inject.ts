// Loads the compiled capture IIFE into the page once, then exposes typed
// wrappers that drive window.__genpptx via page.evaluate(). Replaces the
// original's string-template executeJavaScript with a bundled, typed surface.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import type { Page } from "playwright";
import type {
  FontSwap,
  MediaRef,
  ResolvedMedia,
  SetupResult,
  SlideSpec,
} from "../types.ts";
import type { SetupInput } from "../browser/setup.ts";
import type { EditableCapture } from "../browser/capture-editable.ts";

let cached: string | null = null;
function bundleSource(): string {
  if (cached == null) {
    // At runtime this module is bundled into dist/cli.mjs; capture.iife.js
    // sits beside it.
    const path = fileURLToPath(new URL("./capture.iife.js", import.meta.url));
    cached = readFileSync(path, "utf8");
  }
  return cached;
}

export async function injectCaptureBundle(page: Page): Promise<void> {
  await page.addScriptTag({ content: bundleSource() });
  const ok = await page.evaluate(
    () => typeof (window as unknown as { __genpptx?: unknown }).__genpptx === "object",
  );
  if (!ok) throw new Error("capture bundle failed to initialise window.__genpptx");
}

type Win = { __genpptx: import("../browser/entry.ts").GenPptxApi };

export function callSetup(page: Page, input: SetupInput): Promise<SetupResult> {
  return page.evaluate((arg) => (window as unknown as Win).__genpptx.setup(arg), input);
}

export function callCaptureEditable(
  page: Page,
  spec: SlideSpec,
  fontSwaps: FontSwap[],
): Promise<EditableCapture> {
  return page.evaluate(
    ([s, f]) => (window as unknown as Win).__genpptx.captureEditable(s, f),
    [spec, fontSwaps] as [SlideSpec, FontSwap[]],
  );
}

export function callCaptureScreenshot(page: Page, spec: SlideSpec): Promise<void> {
  return page.evaluate((s) => (window as unknown as Win).__genpptx.captureScreenshot(s), spec);
}

export function callResolveMedia(page: Page, refs: MediaRef[]): Promise<ResolvedMedia[]> {
  return page.evaluate((r) => (window as unknown as Win).__genpptx.resolveMedia(r), refs);
}
