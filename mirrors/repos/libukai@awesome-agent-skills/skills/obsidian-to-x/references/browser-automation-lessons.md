# Browser Automation Lessons Learned

本文档总结了开发 `obsidian-to-x` skill 过程中积累的浏览器自动化经验，供其他项目参考。

---

## 演进历程

### Phase 1: 系统剪贴板 + 前台按键（需 Chrome 前台）

```
┌─────────────────────────────────────────────────────────────┐
│  copyImageToClipboard()  →  osascript Cmd+V  →  粘贴成功    │
│  (系统剪贴板)                (前台按键)                      │
└─────────────────────────────────────────────────────────────┘
                          ↓ 问题
            ❌ Chrome 必须在前台，后台不响应按键
            ❌ 用户无法同时做其他事
```

**Commit**: 初始版本

**局限**: 用户必须等待整个发布过程完成，无法 multitask。

---

### Phase 2: CDP Synthetic ClipboardEvent（后台安全）

```
┌─────────────────────────────────────────────────────────────┐
│  CDP Runtime.evaluate  →  构造 ClipboardEvent  →  dispatch  │
│  (页面内执行)              (File + DataTransfer)              │
└─────────────────────────────────────────────────────────────┘
                          ↓ 问题
            ✅ Chrome 可以在后台
            ❌ DraftJS 有时不正确处理合成事件
```

**Commit**: `8278645 feat(obsidian-to-x): 图片粘贴支持 Chrome 后台运行`

**突破**: 通过 CDP 在页面上下文中构造 `ClipboardEvent`，绕过系统剪贴板。

**代码模式**:
```typescript
// 在页面内构造 File + DataTransfer + ClipboardEvent
const expression = `
  const blob = new Blob([bytes], { type: mimeType });
  const file = new File([blob], fileName, { type: mimeType });
  const dt = new DataTransfer();
  dt.items.add(file);
  const pasteEvent = new ClipboardEvent('paste', {
    bubbles: true,
    cancelable: true,
    clipboardData: dt,
  });
  editor.dispatchEvent(pasteEvent);
`;
await cdp.send('Runtime.evaluate', { expression, awaitPromise: true });
```

---

### Phase 3: MutationObserver 替代 sleep 等待（抗后台节流）

```
┌─────────────────────────────────────────────────────────────┐
│  setTimeout/CPU 等待  →  MutationObserver  →  精确等待 DOM   │
│  (固定延时)              (事件驱动)          (不受节流影响)   │
└─────────────────────────────────────────────────────────────┘
                          ↓ 问题
            ✅ 后台 tab 也能精确等待
            ✅ 不再猜测等待时间
```

**Commit**: `7f88e0f refactor(obsidian-to-x): 用 MutationObserver 替代 sleep 等待`

**根因**: 浏览器对后台 tab 的 `setTimeout` 有严重节流（最小 1 秒），导致固定延时不可靠。

**代码模式**:
```typescript
// 用 MutationObserver 等待元素出现（不受后台节流影响）
const waitForElement = (selector, timeoutMs = 15000) => {
  return new Promise((resolve) => {
    if (document.querySelector(selector)) {
      resolve(true);
      return;
    }
    const observer = new MutationObserver(() => {
      if (document.querySelector(selector)) {
        observer.disconnect();
        clearTimeout(timer);
        resolve(true);
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    const timer = setTimeout(() => {
      observer.disconnect();
      resolve(false);
    }, timeoutMs);
  });
};
```

---

### Phase 4: 先删后插模式（解决 DraftJS ContentState 同步问题）

```
┌─────────────────────────────────────────────────────────────┐
│  粘贴替换模式              →  先删后插模式                    │
│  (选中 → 粘贴 → 期望替换)    (选中 → Backspace → 粘贴)        │
└─────────────────────────────────────────────────────────────┘
                          ↓ 问题
            ✅ ContentState 正确更新
            ✅ 占位符不会"复活"
```

**Commit**: `08d0f16 fix(obsidian-to-x): 重构图片插入为"先删后插"模式`

**根因**: DraftJS 处理合成 `ClipboardEvent` 时，有时只插入内容但不删除选区文字（DOM 更新了，ContentState 没有），下次重渲染时"复活"。

**解决方案**:
```typescript
// 旧方案（不可靠）
select(placeholder);
pasteImage(); // 期望 DraftJS 原子替换选区

// 新方案（可靠）
select(placeholder);
backspace(); // 通过键盘事件删除，DraftJS 正确更新 ContentState
pasteImage(); // 在光标位置粘贴
```

---

## 核心经验总结

### 1. ContentState vs DOM

React 框架（如 DraftJS、Slate）维护自己的状态树：

| 操作 | DOM | ContentState | 结果 |
|------|-----|--------------|------|
| `execCommand('delete')` | ✅ 更新 | ❌ 不更新 | 重渲染后复活 |
| `element.innerHTML = ''` | ✅ 更新 | ❌ 不更新 | 重渲染后复活 |
| 键盘 Backspace | ✅ 更新 | ✅ 更新 | 正确 |
| 键盘 Delete | ✅ 更新 | ✅ 更新 | 正确 |

**教训**: 操作 React 控制的内容时，**必须使用框架认可的输入方式**（键盘事件、API），而非直接操作 DOM。

---

### 2. 合成事件 vs 真实事件

| 事件类型 | 创建方式 | 框架信任度 | 使用场景 |
|----------|----------|-----------|----------|
| 真实键盘 | 用户按键 / CDP Input.dispatchKeyEvent | ✅ 高 | 删除、导航、提交 |
| 真实粘贴 | 用户 Ctrl+V / osascript | ✅ 高 | 需要前台 |
| 合成粘贴 | `new ClipboardEvent()` + `dispatchEvent()` | ⚠️ 中 | 后台操作，可能不稳定 |
| 合成输入 | `execCommand()` | ❌ 低 | 不推荐用于 React |

**教训**: 合成事件可能不被框架完整处理。优先使用：
1. CDP `Input.dispatchKeyEvent` 模拟键盘
2. CDP `Input.insertText` 模拟输入
3. 合成 `ClipboardEvent` 作为 fallback

---

### 3. 后台 Tab 节流

浏览器对后台 tab 的限制：

| API | 前台 | 后台 |
|-----|------|------|
| `setTimeout` | 正常 | 最小 1000ms |
| `setInterval` | 正常 | 最小 1000ms |
| `requestAnimationFrame` | 正常 | 暂停 |
| `MutationObserver` | 正常 | ✅ 正常 |
| CDP `Runtime.evaluate` | 正常 | ✅ 正常 |
| CDP `Input.dispatch*` | 正常 | ✅ 正常 |

**教训**: 后台操作时：
- 用 `MutationObserver` 替代 `setTimeout` 轮询
- 用 CDP 直接操作，不依赖浏览器事件循环

---

### 4. 光标和焦点管理

DraftJS 等框架依赖光标位置决定插入点：

```
┌─────────────────────────────────────────────────────────────┐
│  光标在空 block  →  点击按钮  →  插入位置可能错误           │
│  光标在空 block  →  collapseToStart()  →  插入位置正确      │
└─────────────────────────────────────────────────────────────┘
```

**安全模式**:
```typescript
// 插入前确保焦点和光标位置
editor.focus();
const sel = window.getSelection();
if (blockIsEmpty) {
  sel.collapseToStart(); // 明确光标位置
}
await sleep(300); // 让框架同步状态
```

---

### 5. 边界条件：第一个/最后一个 Block

删除操作在边界处有特殊行为：

```
┌─────────────────────────────────────────────────────────────┐
│  [Block 1] ← 第一个 block 的 Backspace 可能跳到标题        │
│  [Block 2]                                                  │
│  [Block 3] ← 最后一个 block 的 Delete 可能无效果           │
└─────────────────────────────────────────────────────────────┘
```

**安全检查**:
```typescript
// 检查是否安全执行第二个 Backspace（删除空 block）
const prevBlock = block.previousElementSibling;
const isFirstBlock = !prevBlock;
const prevIsAtomic = prevBlock?.getAttribute('contenteditable') === 'false';

if (!isFirstBlock && !prevIsAtomic) {
  // 安全：可以执行第二个 Backspace
  sendBackspace();
}
```

---

## 工具选择指南

### CDP (Chrome DevTools Protocol)

**适用场景**:
- 需要后台操作
- 需要精确控制输入
- 需要访问页面内部状态

**常用命令**:
```typescript
// 执行 JavaScript
cdp.send('Runtime.evaluate', { expression: '...' });

// 键盘输入
cdp.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Backspace' });
cdp.send('Input.insertText', { text: 'hello' });

// 鼠标点击
cdp.send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y });
```

### Playwright / Puppeteer

**适用场景**:
- 需要跨浏览器支持
- 需要截图、PDF
- 简单的页面自动化

**局限**:
- 对已有浏览器实例的控制不如 CDP 直接

---

## 调试技巧

### 1. 可视化调试

```typescript
// 高亮当前操作的元素
await cdp.send('Runtime.evaluate', {
  expression: `
    const el = document.querySelector('${selector}');
    el.style.outline = '3px solid red';
    setTimeout(() => el.style.outline = '', 2000);
  `
});
```

### 2. 日志注入

```typescript
// 在页面内打印日志
await cdp.send('Runtime.evaluate', {
  expression: `console.log('[debug]', window.getSelection().toString())`
});
```

### 3. 状态快照

```typescript
// 获取编辑器完整状态
const state = await cdp.send('Runtime.evaluate', {
  expression: `
    JSON.stringify({
      selection: window.getSelection().toString(),
      cursorNode: window.getSelection().focusNode?.nodeName,
      cursorOffset: window.getSelection().focusOffset,
      blockCount: document.querySelectorAll('[data-block]').length
    })
  `,
  returnByValue: true
});
```

---

## Checklist: 新项目启动时

- [ ] 确定目标框架（DraftJS? Slate? ContentEditable?）
- [ ] 测试合成事件是否被框架正确处理
- [ ] 确定是否需要后台运行
- [ ] 设计占位符系统（如果需要替换插入）
- [ ] 实现焦点管理逻辑
- [ ] 处理边界条件（第一个/最后一个 block）
- [ ] 添加充分的日志和错误处理
- [ ] 测试前台和后台两种场景

---

## 参考资源

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [DraftJS Architecture](https://draftjs.org/docs/advanced-topics-intro/)
- [MutationObserver MDN](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver)
- [Background Tab Throttling](https://developer.chrome.com/blog/timer-throttling-in-chrome-88/)
