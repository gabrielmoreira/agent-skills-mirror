---
name: doa-e2etest
description: "端到端测试全流程：安装配置 Playwright → 编写 E2E 测试用例 → 执行测试 → 生成精美 HTML 报告 → 输出 PDF。USE FOR: E2E测试、端到端测试、Playwright测试、前端自动化测试、编写E2E用例、生成测试报告、测试报告PDF、测试报告HTML、Playwright配置、自动化回归测试、UI测试、冒烟测试。DO NOT USE FOR: 单元测试（使用 test-driven-development skill）、API测试、性能测试。"
argument-hint: "描述要测试的页面/功能，或直接说'全流程'来自动检测并测试"
---

# E2E Test → Report Pipeline

Playwright 端到端测试全流程 skill：从环境搭建到生成精美的 HTML/PDF 测试报告。

## When to Use

- 需要为前端项目搭建 E2E 测试
- 需要编写或补充 Playwright 测试用例
- 需要运行测试并生成可交付的报告（HTML / PDF）
- 项目验收、迭代交付时需要测试报告产物

## Procedure

### Phase 1: 环境检测与安装

1. **检测前端技术栈**
   - 读取 `package.json` 确认框架（React/Vue/Next.js/Angular 等）
   - 确认 UI 组件库（Ant Design / Element Plus / MUI 等）
   - 确认构建工具（Vite / Webpack / Next.js 内置等）
   - 确认前端开发服务器端口

2. **安装 Playwright**
   ```bash
   npm install -D @playwright/test
   ```

3. **检测可用浏览器**
   - 优先尝试 `npx playwright install chromium`
   - 如网络受限，使用系统已安装的浏览器：
     - Windows: `channel: 'msedge'`
     - macOS: `channel: 'chrome'`
   - 在配置中设置正确的 channel

4. **生成 playwright.config.ts**
   - 参考 [配置模板](./references/playwright-config-template.md)
   - 根据实际检测结果填充 `baseURL`、`channel`、`testDir` 等

5. **添加 npm scripts**
   ```json
   {
     "test:e2e": "playwright test",
     "test:e2e:ui": "playwright test --ui"
   }
   ```

### Phase 2: 编写测试用例

1. **分析应用路由和页面**
   - 读取路由配置文件（`routes/index.tsx` 等）
   - 识别所有可测试页面

2. **按功能模块组织测试文件**
   - 目录结构：`e2e/{module}.spec.ts`
   - 每个文件对应一个功能模块

3. **测试用例编写规则**
   - 参考 [测试编写指南](./references/test-writing-guide.md)
   - 使用中文测试标题（`test('应显示登录表单', ...)`）
   - 优先使用语义化定位器（`getByRole`、`getByText`、`getByPlaceholder`）
   - 为需要登录的测试创建 `login` 辅助函数
   - 每个 `describe` 块使用 `beforeEach` 处理前置条件

4. **常见陷阱处理**
   - Ant Design 按钮文本可能有空格（如 "登 录"），使用正则：`/登\s*录/`
   - `networkidle` 等待确保页面资源完全加载
   - 401 拦截器可能干扰登录测试，检查 axios 拦截器逻辑
   - Strict mode 报错时缩小选择器范围（如 `.ant-result-title`）

### Phase 3: 执行测试

1. **确认服务可用**
   - 检查前端 dev server 是否运行
   - 检查后端 API 是否运行
   - 如未运行，提示用户启动或使用 `webServer` 配置自动启动

2. **运行测试**
   ```bash
   npx playwright test --reporter=list
   ```

3. **失败用例调试**
   - 分析错误信息，定位原因
   - 常见原因：选择器不匹配、超时、网络请求失败
   - 修复后重新运行验证

4. **导出 JSON 结果**
   ```bash
   npx playwright test --reporter=json 2>$null | Out-File -Encoding utf8 playwright-report/results.json
   ```

### Phase 4: 生成测试报告

1. **读取 JSON 测试结果**
   - 解析 `playwright-report/results.json`
   - 提取：套件信息、用例状态、耗时、时间线

2. **生成 HTML 报告**
   - 使用 [报告模板](./references/report-template.md) 生成精美 HTML
   - 包含以下区块：
     - **Header**: 项目名、执行时间、Playwright 版本、浏览器、Workers 数、测试模式
     - **摘要卡片**: 总用例数、通过数（通过率）、失败/跳过、总耗时（平均耗时）
     - **结论横幅**: 全通过绿色 / 有失败红色
     - **进度条**: 通过/失败/跳过比例可视化
     - **用例详情**: 按测试套件分组，每条含状态图标、标题、功能描述、Badge、耗时、源码位置
     - **耗时分布图**: 水平条形图，按耗时降序
     - **执行时间线**: Worker 调度和完成时序
     - **功能覆盖矩阵**: 功能模块 × 覆盖场景 × 状态
     - **运行环境**: OS、Node.js、框架、浏览器、地址等
   - 输出到 `playwright-report/detailed-report.html`

3. **生成 PDF**
   - 使用 Playwright 本身将 HTML 转为 PDF：
   ```javascript
   const { chromium } = require('playwright');
   const browser = await chromium.launch({ channel: 'msedge' });
   const page = await browser.newPage();
   await page.goto('file:///path/to/detailed-report.html', { waitUntil: 'networkidle' });
   await page.pdf({
     path: 'playwright-report/E2E测试报告.pdf',
     format: 'A4',
     printBackground: true,
     margin: { top: '10mm', bottom: '10mm', left: '10mm', right: '10mm' }
   });
   await browser.close();
   ```
   - 输出到 `playwright-report/E2E测试报告.pdf`

### Phase 5: 交付与清理

1. **在浏览器中预览 HTML 报告**
2. **确认 PDF 生成成功**
3. **产物清单**：
   - `playwright-report/detailed-report.html` — 可交互 HTML 报告
   - `playwright-report/E2E测试报告.pdf` — 可打印 PDF 报告
   - `playwright-report/results.json` — 原始 JSON 数据

## Design Tokens (报告主题)

```css
--primary: #006D75;         /* 主题主色 */
--primary-light: #E6FFFB;
--success: #52C41A;
--success-bg: #F6FFED;
--error: #FF4D4F;
--error-bg: #FFF2F0;
--text: #1F1F1F;
--text-secondary: #595959;
--border: #F0F0F0;
--bg: #FAFAFA;
```

报告应根据项目品牌色自动调整，读取项目 CSS 变量或 Ant Design 主题配置。

## Reference Files

- [Playwright 配置模板](./references/playwright-config-template.md)
- [测试编写指南](./references/test-writing-guide.md)
- [报告 HTML 模板](./references/report-template.md)
