import { spawn } from 'node:child_process';
import process from 'node:process';
import {
  CHROME_CANDIDATES_BASIC,
  CdpConnection,
  findChromeExecutable,
  getDefaultProfileDir,
  getFreePort,
  sleep,
  waitForChromeDebugPort,
} from './x-utils.js';

const X_ARTICLES_URL = 'https://x.com/compose/articles';

async function testCodeBlockInsertion(): Promise<void> {
  const chromePath = findChromeExecutable(CHROME_CANDIDATES_BASIC);
  if (!chromePath) throw new Error('Chrome not found');

  const profileDir = getDefaultProfileDir();
  const port = await getFreePort();

  console.log('[test] Launching Chrome...');
  const chromeArgs = [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-blink-features=AutomationControlled',
    '--start-maximized',
    X_ARTICLES_URL,
  ];

  if (process.platform === 'darwin') {
    const appPath = chromePath.replace(/\/Contents\/MacOS\/Google Chrome$/, '');
    spawn('open', ['-na', appPath, '--args', ...chromeArgs], { stdio: 'ignore' });
  } else {
    spawn(chromePath, chromeArgs, { stdio: 'ignore' });
  }

  let cdp: CdpConnection | null = null;

  try {
    const wsUrl = await waitForChromeDebugPort(port, 30_000, { includeLastError: true });
    cdp = await CdpConnection.connect(wsUrl, 30_000, { defaultTimeoutMs: 60_000 });

    const targets = await cdp.send<{ targetInfos: Array<{ targetId: string; url: string; type: string }> }>('Target.getTargets');
    let pageTarget = targets.targetInfos.find((t) => t.type === 'page' && t.url.startsWith(X_ARTICLES_URL));

    if (!pageTarget) {
      const { targetId } = await cdp.send<{ targetId: string }>('Target.createTarget', { url: X_ARTICLES_URL });
      pageTarget = { targetId, url: X_ARTICLES_URL, type: 'page' };
    }

    const { sessionId } = await cdp.send<{ sessionId: string }>('Target.attachToTarget', { targetId: pageTarget.targetId, flatten: true });

    await cdp.send('Page.enable', {}, { sessionId });
    await cdp.send('Runtime.enable', {}, { sessionId });
    await cdp.send('DOM.enable', {}, { sessionId });

    console.log('[test] Waiting for page to load...');
    await sleep(5000);

    // 检查页面内容
    console.log('[test] Checking page content...');
    const pageCheck = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
      expression: `(() => {
        return JSON.stringify({
          title: document.title,
          url: window.location.href,
          hasEditor: !!document.querySelector('.DraftEditor-editorContainer'),
          hasWriteButton: !!document.querySelector('[data-testid="empty_state_button_text"]'),
          bodyText: document.body.innerText.substring(0, 500)
        });
      })()`,
      returnByValue: true,
    }, { sessionId });

    console.log('[test] Page info:', pageCheck.result.value);

    // 检查是否需要点击 Write 按钮
    console.log('[test] Checking for Write button...');
    const writeButtonCheck = await cdp.send<{ result: { value: boolean } }>('Runtime.evaluate', {
      expression: `!!document.querySelector('[data-testid="empty_state_button_text"]')`,
      returnByValue: true,
    }, { sessionId });

    if (writeButtonCheck.result.value) {
      console.log('[test] Clicking Write button...');
      await cdp.send('Runtime.evaluate', {
        expression: `document.querySelector('[data-testid="empty_state_button_text"]')?.click()`,
      }, { sessionId });
      await sleep(2000);
    }

    // 等待编辑器出现
    console.log('[test] Waiting for editor...');
    const waitForEditor = async (): Promise<boolean> => {
      for (let i = 0; i < 30; i++) {
        const result = await cdp!.send<{ result: { value: boolean } }>('Runtime.evaluate', {
          expression: `!!document.querySelector('.DraftEditor-editorContainer [contenteditable="true"]')`,
          returnByValue: true,
        }, { sessionId });
        if (result.result.value) return true;
        await sleep(1000);
      }
      return false;
    };

    const editorFound = await waitForEditor();
    if (!editorFound) {
      console.log('[test] Editor not found after 30 seconds!');
      throw new Error('Editor not found');
    }

    console.log('[test] Editor found!');

    // 1. 在编辑器中输入一些文字
    console.log('[test] Inserting text into editor...');
    await cdp.send('Runtime.evaluate', {
      expression: `(() => {
        const editor = document.querySelector('.DraftEditor-editorContainer [contenteditable="true"]');
        if (editor) {
          editor.focus();
          document.execCommand('insertText', false, '测试文字\\n\\n');
          return true;
        }
        return false;
      })()`,
    }, { sessionId });
    await sleep(1000);

    // 2. 点击 Insert 菜单
    console.log('[test] Opening Insert menu...');
    await cdp.send('Runtime.evaluate', {
      expression: `document.querySelector('[aria-label="Add Media"]')?.click()`,
    }, { sessionId });
    await sleep(500);

    // 3. 点击 Code 选项
    console.log('[test] Clicking Code option...');
    await cdp.send('Runtime.evaluate', {
      expression: `(() => {
        const items = document.querySelectorAll('[role="menuitem"]');
        for (const item of items) {
          if (item.textContent.toLowerCase().includes('code')) {
            item.click();
            return true;
          }
        }
        return false;
      })()`,
    }, { sessionId });
    await sleep(1500);

    // 4. 填入语言
    console.log('[test] Filling language...');
    await cdp.send('Runtime.evaluate', {
      expression: `(() => {
        const langInput = document.querySelector('input[data-testid="programming-language-input"]');
        if (langInput) {
          langInput.value = 'python';
          langInput.dispatchEvent(new Event('input', { bubbles: true }));
          return true;
        }
        return false;
      })()`,
    }, { sessionId });

    // 5. 填入代码
    console.log('[test] Filling code...');
    const testCode = `def hello_world():
    print("Hello, World!")
    return True

hello_world()`;

    await cdp.send('Runtime.evaluate', {
      expression: `(() => {
        const codeTextarea = document.querySelector('textarea[name="code-input"]');
        if (codeTextarea) {
          codeTextarea.value = ${JSON.stringify(testCode)};
          codeTextarea.dispatchEvent(new Event('input', { bubbles: true }));
          return true;
        }
        return false;
      })()`,
    }, { sessionId });
    await sleep(500);

    // 6. 点击 Insert 按钮
    console.log('[test] Clicking Insert button...');
    await cdp.send('Runtime.evaluate', {
      expression: `(() => {
        const buttons = Array.from(document.querySelectorAll('button'));
        const insertBtn = buttons.find(btn => btn.textContent.trim() === 'Insert' && !btn.disabled);
        if (insertBtn) {
          insertBtn.click();
          return true;
        }
        return false;
      })()`,
    }, { sessionId });

    // 7. 等待并检查结果
    console.log('[test] Waiting for insertion...');
    await sleep(2000);

    // 7.5 检查对话框是否关闭
    const dialogCheck = await cdp.send<{ result: { value: boolean } }>('Runtime.evaluate', {
      expression: `!!document.querySelector('[data-testid="sheetDialog"]')`,
      returnByValue: true,
    }, { sessionId });
    console.log('[test] Dialog still open:', dialogCheck.result.value);

    if (dialogCheck.result.value) {
      console.log('[test] Dialog still open, waiting more...');
      await sleep(3000);
    }

    // 7.6 尝试点击编辑器来"确认"插入
    console.log('[test] Clicking editor to confirm...');
    await cdp.send('Runtime.evaluate', {
      expression: `(() => {
        const editor = document.querySelector('.DraftEditor-editorContainer [contenteditable="true"]');
        if (editor) {
          editor.click();
          editor.focus();
          return true;
        }
        return false;
      })()`,
    }, { sessionId });
    await sleep(1000);

    // 8. 检查编辑器内容
    console.log('[test] Checking editor content...');
    const editorCheck = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
      expression: `(() => {
        const editor = document.querySelector('.DraftEditor-editorContainer [data-contents="true"]');
        return editor ? editor.innerText : '';
      })()`,
      returnByValue: true,
    }, { sessionId });

    console.log('[test] Editor text:', editorCheck.result.value);
    console.log('[test] Editor text length:', editorCheck.result.value.length);

    // 9. 检查 blocks
    const blocksCheck = await cdp.send<{ result: { value: number } }>('Runtime.evaluate', {
      expression: `document.querySelectorAll('[data-block="true"]').length`,
      returnByValue: true,
    }, { sessionId });

    console.log('[test] Total blocks:', blocksCheck.result.value);

    // 10. 获取所有 blocks 的详细信息
    const blocksInfo = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
      expression: `(() => {
        const blocks = document.querySelectorAll('[data-block="true"]');
        const info = [];
        blocks.forEach((block, i) => {
          info.push({
            index: i,
            tag: block.tagName,
            contenteditable: block.getAttribute('contenteditable'),
            hasCode: !!block.querySelector('code'),
            hasPre: !!block.querySelector('pre'),
            text: block.textContent.substring(0, 100),
            html: block.innerHTML.substring(0, 300)
          });
        });
        return JSON.stringify(info, null, 2);
      })()`,
      returnByValue: true,
    }, { sessionId });

    console.log('[test] Blocks info:', blocksInfo.result.value);

    // 11. 获取编辑器的完整 HTML
    const editorHtml = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
      expression: `(() => {
        const editor = document.querySelector('.DraftEditor-editorContainer [data-contents="true"]');
        return editor ? editor.innerHTML.substring(0, 1000) : '';
      })()`,
      returnByValue: true,
    }, { sessionId });

    console.log('[test] Editor HTML:', editorHtml.result.value);

    console.log('[test] Test complete. Browser will remain open for 60 seconds for inspection.');
    await sleep(60_000);

  } finally {
    if (cdp) {
      cdp.close();
    }
  }
}

await testCodeBlockInsertion().catch((err) => {
  console.error(`Error: ${err instanceof Error ? err.message : String(err)}`);
  process.exit(1);
});
