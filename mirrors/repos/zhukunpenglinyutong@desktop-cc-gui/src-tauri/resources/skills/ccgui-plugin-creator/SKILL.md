---
name: ccgui-plugin-creator
description: 为 CC GUI 桌面客户端创建、修改、迭代插件（Tier-0 声明式 CSS/JSON，或 Tier-1 单文件 ESM）。当用户要"做一个插件 / 给 CC GUI 加个功能 / 改输入框或界面样式 / 加设置页、侧边栏或状态栏入口 / 加面板页签或命令面板命令 / 把某套工作流包装成插件 / 改一下我做过的那个插件"，或提到 ccgui 插件、插件目录、从本地目录安装插件时使用。
---

# CC GUI 插件创建

产出是**一个可被 CC GUI 直接安装的目录**（不是仓库、不是 PR）：用户在 CC GUI 侧边栏「插件」→「从本地目录安装」选这个目录即可生效。

## 1. 先决定 Tier（决定要不要写 JS）

| 用户要的效果 | Tier | 目录内容 | 需要构建 |
|---|---|---|---|
| 换配色/主题 token、改界面样式、加静态状态栏文字、加命令面板命令（只发事件） | `declarative` | `manifest.json` + `styles.css`（可无样式） | 否 |
| 加设置页、面板页签、侧边栏入口、命令面板命令（要逻辑）、Markdown 渲染、读写存储、调网络/命令、起 agent 轮次 | `js` | `manifest.json` + `main.js` | 否（单文件 ESM） |

**两层都能做到时优先 declarative**：不用写 JS、出错面小、用户看得懂。只有需要运行时逻辑（读写、事件、新 UI 组件、网络）才选 `js`。

## 2. 目录与文件名（宿主按名字找）

```
<插件目录>/                 # 默认放 ~/ccgui-plugins/<id>/；用户指定了路径就听用户的
├── manifest.json          # 必须在该目录根；宿主按 manifest.id 安置，目录名随意但 id 全局唯一
├── main.js                # 仅 Tier-1：单文件 ESM，export default function activate(ctx)
└── styles.css             # 可选；Tier-1 也可用 ctx.theme.injectCss 注入样式
```

- 安装会**复制**整棵目录（跳过 `node_modules` 与 `.git`，单文件上限 16MB）到 `~/.ccgui-next/plugins/<id>/`；目录名随意，宿主按 manifest 的 `id` 安置。
- 因此 `main.js` 必须自包含：**不能** `import` 任何模块（`react`、`@ccgui/plugin-sdk`、相对路径都不行），也不需要打包器；`main.js` 里用 `ctx.react.createElement` 建组件（不要 JSX）。

## 3. 写 manifest.json（硬性校验，违反装不上）

```jsonc
{
  "id": "my-panel",                    // ^[a-z0-9][a-z0-9-]{1,63}$，全局唯一，上架后不可改
  "name": "我的面板",                   // 显示名
  "version": "1.0.0",                  // ^\d+\.\d+\.\d+$（本地迭代可保持在 0.1.0）
  "tier": "js",                        // "declarative" | "js"（必填）
  "description": "在右侧面板显示……",   // 一句话，用户能看懂
  "permissions": ["ui:panel-tab"]      // 只声明真正用到的；调用未声明的能力会抛错
}
```

可选字段：`author`、`minAppVersion`（宿主最低版本）、`sdkVersion`（SDK 区间，如 `"^0.3"`）、`contributes`（声明式贡献点）、`configSchema`（自动生成设置表单）。
**字段与权限的完整清单以 `references/sdk-api.md` 为准**（该文件由 SDK 源码生成，不要凭记忆写字段名/权限名）。

## 4. 两个最小可用样例

### Tier-0：主题 + 状态栏文字（零 JS）

```json
{
  "id": "midnight-theme",
  "name": "午夜主题",
  "version": "0.1.0",
  "tier": "declarative",
  "description": "深蓝夜间配色",
  "permissions": ["theme", "ui:status-bar"],
  "contributes": {
    "themes": [{ "name": "Midnight", "tokens": { "dark": { "--background-primary-default": "#0b1020" } } }],
    "statusBarItems": [{ "text": "Midnight" }]
  }
}
```

token 名字取自宿主语义 token（`src/styles/theme.css` 的 `--*` 变量），不要自己发明前缀；不确定就问用户想要哪种效果，再用少数几个 token 达成。

声明式贡献点走的是同一套权限门禁，`permissions` 要相应声明：`themes` → `theme`，`i18n` → `i18n`，`statusBarItems` → `ui:status-bar`，`commands` → `ui:command`，`configSchema` → `ui:settings-section`（自动生成设置页）。只放一个 `styles.css` 的声明式插件不需要任何权限，`permissions` 写 `[]` 即可。

### Tier-1：面板页签 + 设置页（单文件 ESM，无构建）

```js
// main.js —— 不能有任何 import/JSX；组件用 ctx.react.createElement 建
export default function activate(ctx) {
  const { createElement: h, useState, useEffect } = ctx.react;

  function Panel({ workspacePath }) {
    const [count, setCount] = useState(0);
    useEffect(() => {
      let alive = true;
      ctx.storage.get("count").then((v) => { if (alive && typeof v === "number") setCount(v); });
      return () => { alive = false; };            // 每个副作用都要有清理
    }, []);
    return h("div", { style: { padding: 12 } },
      h("p", null, `工作区：${workspacePath}`),
      h("button", { onClick: () => { const next = count + 1; setCount(next); void ctx.storage.set("count", next); } },
        `点了 ${count} 次`));
  }

  ctx.ui.registerPanelTab({ label: () => "计数", component: Panel });
  // 所有 register* 返回 Disposer，宿主自动回收；返回函数可做额外清理（停定时器等）。
}
```

对应 manifest：`"tier": "js"`，`"permissions": ["ui:panel-tab", "storage"]`。

## 5. 交付给用户的安装与迭代路径（必须说清楚）

1. **安装**：CC GUI 侧边栏「插件」→「从本地目录安装」→ 选插件目录（里面有 `manifest.json` 的那一层）。
2. **验收**：让用户确认看到效果（新页签/新设置页/样式变化）；没看到就让用户看插件页该行的错误提示，别猜。
3. **迭代**：改完文件重新走一次「从本地目录安装」——它会**热重载**新代码（同一 id 覆盖），不需要重启应用，也别新建插件目录。
4. **卸载/回滚**：插件页卸载即可；插件数据保留 30 天。

## 6. 硬性约束（写错了宿主会拒绝或崩溃）

- `id` 必须匹配 `^[a-z0-9][a-z0-9-]{1,63}$`；`version` 必须匹配 `^\d+\.\d+\.\d+$`；`tier` 只能是 `declarative` 或 `js`。
- 权限**最小化**且必须存在于 `references/sdk-api.md` 的权限目录里；未知权限 = 加载期拒绝，未声明的能力 = 调用即抛错。
- Tier-1 的 `main.js` 是唯一入口：`export default function activate(ctx)`（可返回清理函数），不能有 bare import，不要用 JSX/eval/`new Function`。
- 不直接调 Tauri（`window.__TAURI__` 已被宿主移除）；没有文件系统/终端的直接 API，只能经 `ctx.bridge.invoke` 的 `exec:` 授权（用户在权限清单里看得到），不碰别的插件的数据、不绕过 SDK 抓宿主 store/DOM。
- 注入的 CSS 必须自包含：禁止 `@import`、禁止 `url(http…)` 等远程引用。
- 出网与执行外部命令只能经 `ctx.bridge.invoke`（命令表与所需授权见 `references/sdk-api.md`），且必须先声明 `network:<host>` / `exec:<bin>` 授权（`network:none` 只是"不用网络"的声明，不是授权）。
- 用户可见文案默认中文；要支持多语言时用 `ctx.i18n.addBundle`（需 `i18n` 权限）注册 `zh-CN` / `en` 资源。

## 7. 完成前自检

- [ ] 目录里有 `manifest.json`，`id`/`version`/`tier` 合法，`permissions` 与实际调用一一对应（不多不少）
- [ ] Tier-1 的 `main.js` 无任何 `import`，且 `activate` 里的每个订阅/定时器/监听都有清理
- [ ] 用到的每个 `ctx.*` 方法都在 `references/sdk-api.md` 里存在（没写到的就是不存在）
- [ ] 已告诉用户：装哪里、怎么装、怎么再装一次、怎么卸载

## 8. 深挖

- `references/sdk-api.md`：由 `packages/plugin-sdk` 源码生成 —— manifest 字段、`PluginContext` 全量签名、每个扩展点需要的权限、权限目录与授权形状。
- 更长的规范（仓库结构、git tag 与 Release 附件、审核标准、上架流程）见项目文档 `docs/plugin-development-guide.zh-CN.md`；**上架前请以仓库内最新版本为准**，本 skill 不复制它以免出现第二份过期快照。
