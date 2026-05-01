#!/usr/bin/env bun
/**
 * 简单检查编辑器占位符
 */

import { CdpConnection, waitForChromeDebugPort } from './x-utils.js';

async function main() {
  const port = 9222;

  console.log('Connecting to Chrome on port', port);
  const wsUrl = await waitForChromeDebugPort(port, 5000);
  const cdp = await CdpConnection.connect(wsUrl, 5000);

  try {
    const targets = await cdp.send<{ targetInfos: Array<{ targetId: string; url: string; type: string }> }>('Target.getTargets');
    const pageTarget = targets.targetInfos.find((t) => t.type === 'page' && t.url.includes('x.com'));

    if (!pageTarget) {
      console.error('No X.com page found');
      process.exit(1);
    }

    const { sessionId } = await cdp.send<{ sessionId: string }>('Target.attachToTarget', {
      targetId: pageTarget.targetId,
      flatten: true,
    });

    // 获取编辑器内容
    const editorContent = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
      expression: `document.querySelector('.DraftEditor-editorContainer [data-contents="true"]')?.innerText || ''`,
      returnByValue: true,
    }, { sessionId });

    const content = editorContent.result.value;

    console.log('\n=== Editor Content Analysis ===\n');
    console.log(`Total length: ${content.length} chars\n`);

    // 检查代码占位符
    const codePlaceholders = content.match(/XCODEPH_\d+/g) || [];
    console.log(`Code placeholders remaining: ${codePlaceholders.length}`);
    if (codePlaceholders.length > 0) {
      console.log('  Found:', codePlaceholders.join(', '));

      // 显示每个占位符的上下文
      console.log('\n=== Placeholder Context ===\n');
      for (const placeholder of codePlaceholders) {
        const index = content.indexOf(placeholder);
        const before = content.substring(Math.max(0, index - 40), index);
        const after = content.substring(index + placeholder.length, Math.min(content.length, index + placeholder.length + 40));
        console.log(`${placeholder}:`);
        console.log(`  ...${before}[${placeholder}]${after}...`);
        console.log('');
      }
    } else {
      console.log('  ✅ No code placeholders found - all replaced!');
    }

    // 检查代码块元素
    const codeBlocksCount = await cdp.send<{ result: { value: number } }>('Runtime.evaluate', {
      expression: `document.querySelectorAll('.DraftEditor-editorContainer pre').length`,
      returnByValue: true,
    }, { sessionId });

    console.log(`Code blocks (pre elements): ${codeBlocksCount.result.value}`);

  } finally {
    await cdp.close();
  }
}

main().catch(console.error);
