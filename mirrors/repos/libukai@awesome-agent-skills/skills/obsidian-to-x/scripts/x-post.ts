import { spawn } from 'node:child_process';
import fs from 'node:fs';
import { mkdir } from 'node:fs/promises';
import process from 'node:process';
import {
  CHROME_CANDIDATES_FULL,
  CdpConnection,
  cdpPaste,
  copyImageToClipboard,
  findChromeExecutable,
  getDefaultProfileDir,
  getFreePort,
  grantClipboardPermissions,
  pasteFromClipboard,
  sleep,
  waitForChromeDebugPort,
} from './x-utils.js';

const X_COMPOSE_URL = 'https://x.com/compose/post';

interface XBrowserOptions {
  text?: string;
  images?: string[];
  submit?: boolean;
  timeoutMs?: number;
  profileDir?: string;
  chromePath?: string;
}

export async function postToX(options: XBrowserOptions): Promise<void> {
  const { text, images = [], submit = false, timeoutMs = 120_000, profileDir = getDefaultProfileDir() } = options;

  const chromePath = options.chromePath ?? findChromeExecutable(CHROME_CANDIDATES_FULL);
  if (!chromePath) throw new Error('Chrome not found. Set X_BROWSER_CHROME_PATH env var.');

  await mkdir(profileDir, { recursive: true });

  const port = await getFreePort();
  console.log(`[x-browser] Launching Chrome (profile: ${profileDir})`);

  const chrome = spawn(chromePath, [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-blink-features=AutomationControlled',
    '--start-maximized',
    X_COMPOSE_URL,
  ], { stdio: 'ignore' });

  let cdp: CdpConnection | null = null;

  try {
    const wsUrl = await waitForChromeDebugPort(port, 30_000, { includeLastError: true });
    cdp = await CdpConnection.connect(wsUrl, 30_000, { defaultTimeoutMs: 15_000 });

    const targets = await cdp.send<{ targetInfos: Array<{ targetId: string; url: string; type: string }> }>('Target.getTargets');
    let pageTarget = targets.targetInfos.find((t) => t.type === 'page' && t.url.includes('x.com'));

    if (!pageTarget) {
      const { targetId } = await cdp.send<{ targetId: string }>('Target.createTarget', { url: X_COMPOSE_URL });
      pageTarget = { targetId, url: X_COMPOSE_URL, type: 'page' };
    }

    const { sessionId } = await cdp.send<{ sessionId: string }>('Target.attachToTarget', { targetId: pageTarget.targetId, flatten: true });

    await cdp.send('Page.enable', {}, { sessionId });
    await cdp.send('Runtime.enable', {}, { sessionId });
    await cdp.send('Input.setIgnoreInputEvents', { ignore: false }, { sessionId });

    // Grant clipboard permissions so CDP paste works even when Chrome is in background
    const clipboardGranted = await grantClipboardPermissions(cdp);

    console.log('[x-browser] Waiting for X editor...');
    await sleep(3000);

    const waitForEditor = async (): Promise<boolean> => {
      const start = Date.now();
      while (Date.now() - start < timeoutMs) {
        const result = await cdp!.send<{ result: { value: boolean } }>('Runtime.evaluate', {
          expression: `!!document.querySelector('[data-testid="tweetTextarea_0"]')`,
          returnByValue: true,
        }, { sessionId });
        if (result.result.value) return true;
        await sleep(1000);
      }
      return false;
    };

    const editorFound = await waitForEditor();
    if (!editorFound) {
      console.log('[x-browser] Editor not found. Please log in to X in the browser window.');
      console.log('[x-browser] Waiting for login...');
      const loggedIn = await waitForEditor();
      if (!loggedIn) throw new Error('Timed out waiting for X editor. Please log in first.');
    }

    if (text) {
      console.log('[x-browser] Typing text...');
      // Focus the editor first
      await cdp.send('Runtime.evaluate', {
        expression: `document.querySelector('[data-testid="tweetTextarea_0"]')?.focus()`,
      }, { sessionId });
      await sleep(200);

      // Use Input.insertText to insert text (preserves newlines and special characters)
      await cdp.send('Input.insertText', { text }, { sessionId });
      await sleep(500);
    }

    // X Posts support max 4 images
    const maxImages = 4;
    const imagesToUpload = images.slice(0, maxImages);

    if (images.length > maxImages) {
      console.log(`[x-browser] Note: X Posts support max ${maxImages} images. Uploading first ${maxImages} of ${images.length} images.`);
    }

    for (const imagePath of imagesToUpload) {
      if (!fs.existsSync(imagePath)) {
        console.warn(`[x-browser] Image not found: ${imagePath}`);
        continue;
      }

      console.log(`[x-browser] Pasting image: ${imagePath}`);

      if (!copyImageToClipboard(imagePath)) {
        console.warn(`[x-browser] Failed to copy image to clipboard: ${imagePath}`);
        continue;
      }

      // Count uploaded images before paste
      const imgCountBefore = await cdp.send<{ result: { value: number } }>('Runtime.evaluate', {
        expression: `document.querySelectorAll('img[src^="blob:"]').length`,
        returnByValue: true,
      }, { sessionId });

      // Wait for clipboard to be ready
      await sleep(500);

      // Focus the editor
      await cdp.send('Runtime.evaluate', {
        expression: `document.querySelector('[data-testid="tweetTextarea_0"]')?.focus()`,
      }, { sessionId });
      await sleep(200);

      // Paste image: try CDP paste first (works in background), fallback to system paste
      console.log('[x-browser] Pasting from clipboard...');

      let pasteWorked = false;

      // Method 1: CDP paste (no window focus required)
      if (clipboardGranted) {
        await cdpPaste(cdp, sessionId);
        // Quick check: wait up to 5s for image to appear
        const cdpCheckStart = Date.now();
        while (Date.now() - cdpCheckStart < 5_000) {
          const r = await cdp!.send<{ result: { value: number } }>('Runtime.evaluate', {
            expression: `document.querySelectorAll('img[src^="blob:"]').length`,
            returnByValue: true,
          }, { sessionId });
          if (r.result.value >= expectedImgCount) {
            pasteWorked = true;
            console.log(`[x-browser] Image pasted via CDP (background)`);
            break;
          }
          await sleep(500);
        }
      }

      // Method 2: System paste fallback (requires Chrome in foreground)
      if (!pasteWorked) {
        if (clipboardGranted) {
          console.log('[x-browser] CDP paste did not work, falling back to system paste...');
        }
        const pasteSuccess = pasteFromClipboard('Google Chrome', 5, 500);

        if (!pasteSuccess) {
          // Last resort: CDP keyboard events
          console.log('[x-browser] System paste failed, trying CDP keyboard fallback...');
          const modifiers = process.platform === 'darwin' ? 4 : 2;
          await cdp.send('Input.dispatchKeyEvent', {
            type: 'keyDown',
            key: 'v',
            code: 'KeyV',
            modifiers,
            windowsVirtualKeyCode: 86,
          }, { sessionId });
          await cdp.send('Input.dispatchKeyEvent', {
            type: 'keyUp',
            key: 'v',
            code: 'KeyV',
            modifiers,
            windowsVirtualKeyCode: 86,
          }, { sessionId });
        }
      }

      console.log('[x-browser] Verifying image upload...');
      const expectedImgCount = imgCountBefore.result.value + 1;
      let imgUploadOk = pasteWorked; // Skip re-check if CDP paste already verified
      if (!imgUploadOk) {
        const imgWaitStart = Date.now();
        while (Date.now() - imgWaitStart < 15_000) {
          const r = await cdp!.send<{ result: { value: number } }>('Runtime.evaluate', {
            expression: `document.querySelectorAll('img[src^="blob:"]').length`,
            returnByValue: true,
          }, { sessionId });
          if (r.result.value >= expectedImgCount) {
            imgUploadOk = true;
            break;
          }
          await sleep(1000);
        }
      }

      if (imgUploadOk) {
        console.log('[x-browser] Image upload verified');
      } else {
        console.warn('[x-browser] Image upload not detected after 15s. Run check-paste-permissions.ts to diagnose.');
      }
    }

    // Scroll to show uploaded images after all images are uploaded
    if (imagesToUpload.length > 0) {
      console.log('[x-browser] Scrolling to show uploaded images...');
      await cdp.send('Runtime.evaluate', {
        expression: `
          // Try multiple strategies to scroll to bottom

          // Strategy 1: Scroll to the first uploaded image (most reliable)
          const uploadedImage = document.querySelector('img[src^="blob:"]');
          if (uploadedImage) {
            uploadedImage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            console.log('[scroll] Scrolled to uploaded image');
          } else {
            // Strategy 2: Scroll the main compose area
            const composeArea = document.querySelector('[data-testid="toolBar"]')?.parentElement;
            if (composeArea) {
              composeArea.scrollTo({ top: composeArea.scrollHeight, behavior: 'smooth' });
              console.log('[scroll] Scrolled compose area to bottom');
            } else {
              // Strategy 3: Scroll window
              window.scrollBy({ top: 400, behavior: 'smooth' });
              console.log('[scroll] Scrolled window down 400px');
            }
          }
        `,
      }, { sessionId });
      await sleep(1000);
    }

    if (submit) {
      console.log('[x-browser] Submitting post...');
      await cdp.send('Runtime.evaluate', {
        expression: `document.querySelector('[data-testid="tweetButton"]')?.click()`,
      }, { sessionId });
      await sleep(2000);
      console.log('[x-browser] Post submitted!');

      // Close browser after submission
      if (cdp) {
        try { await cdp.send('Browser.close', {}, { timeoutMs: 5_000 }); } catch {}
      }
      setTimeout(() => {
        if (!chrome.killed) try { chrome.kill('SIGKILL'); } catch {}
      }, 2_000).unref?.();
      try { chrome.kill('SIGTERM'); } catch {}
    } else {
      console.log('[x-browser] Post composed (preview mode). Add --submit to post.');
      console.log('[x-browser] Browser remains open for manual review.');
    }
  } finally {
    // Disconnect CDP but keep browser open in preview mode
    if (cdp) {
      cdp.close();
    }
    // Don't kill Chrome - let user review and close manually
  }
}

function printUsage(): never {
  console.log(`Post to X (Twitter) using real Chrome browser

Usage:
  npx -y bun x-browser.ts [options] [text]

Options:
  --image <path>   Add image (can be repeated, max 4)
  --submit         Actually post (default: preview only)
  --profile <dir>  Chrome profile directory
  --help           Show this help

Examples:
  npx -y bun x-browser.ts "Hello from CLI!"
  npx -y bun x-browser.ts "Check this out" --image ./screenshot.png
  npx -y bun x-browser.ts "Post it!" --image a.png --image b.png --submit
`);
  process.exit(0);
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) printUsage();

  const images: string[] = [];
  let submit = false;
  let profileDir: string | undefined;
  const textParts: string[] = [];

  for (let i = 0; i < args.length; i++) {
    const arg = args[i]!;
    if (arg === '--image' && args[i + 1]) {
      images.push(args[++i]!);
    } else if (arg === '--submit') {
      submit = true;
    } else if (arg === '--profile' && args[i + 1]) {
      profileDir = args[++i];
    } else if (!arg.startsWith('-')) {
      textParts.push(arg);
    }
  }

  const text = textParts.join(' ').trim() || undefined;

  if (!text && images.length === 0) {
    console.error('Error: Provide text or at least one image.');
    process.exit(1);
  }

  await postToX({ text, images, submit, profileDir });
}

await main().catch((err) => {
  console.error(`Error: ${err instanceof Error ? err.message : String(err)}`);
  process.exit(1);
});
