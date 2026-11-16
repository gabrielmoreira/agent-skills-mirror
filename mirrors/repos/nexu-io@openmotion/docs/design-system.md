# OpenMotion Design System

The maintained system lives in [`packages/design-system`](../packages/design-system/README.md). `tokens.json` generates both browser `tokens.css` and Studio `studio/tokens.css`; Studio semantic aliases, fonts, controls, materials, loading states, icon rendering and brand assets belong to this package. Application modules consume its entry points and retain their layout and interaction logic. The template browser now uses shared theme roles instead of a separate fixed palette.

The server exposes the positive public-asset list at `/design-system/`, with `/design-system` as the read-only catalog and `/web/design-system/` as a compatibility URL alias. Stable README logos and font-license paths are generated mirrors. No npm workspace dependency or separate publication is introduced.

Brand materials are maintained in [the package Brandkit](../packages/design-system/brand/BRANDKIT.md) and [art direction](../packages/design-system/brand/MOTION_DESIGN.md); Library entries forward to those sources. They remain explicit creative context and do not automatically style authored videos. All Agents follow the [shared styling rules](../AGENTS.md#shared-design-system--required-for-every-agent).

The current MVP opens directly into the editor. The home/session/browser rules below describe retained source surfaces, not additional MVP navigation. Native project iframes and export content never import application theme styles.

## Visual foundation

Collapsible navigation uses explicit `data-collapsed` state for geometry and visibility. Keep `aria-hidden` and `inert` for accessibility and interaction blocking: modal focus management may temporarily hide background regions from assistive technology without collapsing them or moving the workspace.

产品界面视觉对齐到 **OpenDesign 主仓库 `20c49e75c`**。本次迁移只影响宿主 UI，保留现有首页、会话、浏览器、面板与时间轴的结构、尺寸、间距及行为。

来源与适配关系：

| OpenDesign 来源文件 | Motion 落点 | 迁移范围 |
| --- | --- | --- |
| `apps/web/src/styles/tokens.css` | `packages/design-system/tokens.json` → `tokens.css` | 双主题灰阶、品牌色、中性主操作、圆角与阴影 |
| `apps/web/src/styles/base.css` | `base.css`、`fonts.css` 与 Studio 主题适配层 | Albert Sans 字体体系、中性键盘焦点；保留 Motion 字号、字重主体、行高和尺寸 |
| `apps/web/src/styles/material.css` | `packages/design-system/material.css` | 菜单/Popover 磨砂材质、弹窗统一遮罩、减少透明度和不支持滤镜时的降级 |
| `packages/components/src/button.module.css` | `controls.css`、Studio `Button.tsx` 视觉钩子与 `packages/design-system/studio/adapter.css` | 中性主按钮、悬停与禁用视觉；保留原尺寸和事件 |
| `packages/components/src/form-controls.module.css` | `controls.css`、Studio `Input.tsx` 共享视觉钩子 | 面板底色与中性焦点；保留可见键盘焦点及错误状态 |
| `packages/components/src/dialog.module.css` | `material.css` | 实色浮层、12px 圆角、阴影和遮罩；保留定位、宽高、层级及关闭逻辑 |

采用按语义映射的样式迁移，不引入 OD React 组件包。OD 的 body 字重 600 与紧凑行高不全局照搬，以免改变 Motion 的文本换行和布局。共享设计变量仍以 JSON 为唯一真源，生成 CSS；材质降级变量集中在 `material.css`。产品流程见 [产品架构](product/architecture.md)。

## 视觉规范

Functional editor icons use Remix Icon 4.9.1, matching the [reference icon catalog](https://open-design-system-leon.leon-wcl.chatgpt.site/#/icons). Original vector paths are bundled in `packages/design-system/icons.svg`, with the upstream license and notice beside it. `packages/design-system/react/RemixIcons.tsx` provides the shared React interface and legacy-name mappings, with `studio/src/icons/RemixIcons.tsx` as a forwarding entry; `MotionIcon` uses the same vectors. React consumers inline the package-owned glyphs into their SVGs, with an explicit 24×24 viewBox and currentColor, so native-dialog controls remain visible when a sprite request would fail or the runtime disconnects. Static HTML can continue using the shared sprite URL. Brand avatars use the paired asset-logo background/ink tokens, providing a stable light backing for transparent source logos in either theme. Controls default to line icons; play/pause and explicit filled states retain distinct glyphs. Brand artwork and timeline drawing geometry remain separate. MVP side-panel tabs and the preview title use text without icons. A tab strip with only one panel shows a plain heading without a selected underline. Selected tabs use the strong neutral text token, semibold weight and a 2px neutral underline. Enabled toolbar toggles use the same strong text on an inset neutral background; inactive and disabled controls retain separate contrast levels.

The application header and template library share `packages/design-system/react/BrandLogo.tsx`, using the maintained `brand/openmotion-logo.svg` lockup: the unmodified upstream OpenDesign symbol with the OpenMotion name. The shared mask recipe follows the selected application theme through currentColor. Narrow editor headers show the same symbol without the wordmark. Original upstream assets and attribution remain in the package.

`packages/design-system/metadata.js` owns application titles, localized descriptions and Open Graph/Twitter cards. Website metadata uses the package-owned OpenDesign Motion name and The fullstack agentic video editor headline across languages; descriptions cover motion creation, media and voice generation, editing, animation, reference recreation and brand templates/design systems. `npm run design:tokens` generates the marked HTML head blocks in Studio and the independent workbench; Studio updates the same fields when its language changes. Browser chrome colors follow the selected theme using generated shell tokens. The adaptive SVG favicon and opaque 32px/180px bookmark icons reuse the original symbol. The legacy `/favicon.svg` remains a generated mirror. Social cards reference the existing public, immutable 1280×640 brand artwork documented in the Brandkit. These are local application surfaces, so they declare `noindex, nofollow` and omit a public canonical/`og:url` rather than publishing local project or session URLs. Public hosting and social-crawler acceptance require a separately configured public site; these tags do not make loopback pages shareable.

Provider settings and model choices use locally bundled brand icons from `provider-icons.js`, with source revisions and licenses in [the provider notice](../packages/design-system/providers/NOTICE.md). Brand artwork retains its colors on a shared neutral tile in both themes; custom connections use initials and unverified brands use an explicit generic symbol.

| 用途 | 浅色 | 深色 |
| --- | --- | --- |
| 工作区 | `#ffffff` | `#202020` |
| 面板 | `#fafafa` | `#353535` |
| 浮层 | `#ffffff` | `#353535` |
| 输入底色 | `#fafafa` | `#353535` |
| 正文 | `#494949` | `#ededed` |
| 辅助文字 | `#696969` | `#c0c0c0` |
| 品牌选中辅助 | `#007106` | `#adf788` |
| 表单与键盘焦点 | `#353535` | `#fafafa` |
| 主操作 | `#202020` | `#fafafa` |

品牌绿为 `#87ea5c`。绿色用于选中辅助、标题高亮与创作辅助；主要操作和表单焦点采用中性色。The application header and left control rail share the `shell` background. The central workspace uses the `workspace` surface with a 4px outer inset and 10px corners; internal panel dividers remain local separators. Chrome icons use the muted `chrome-icon` role; `chrome-hover` and `chrome-active` provide distinct inset navigation states without raised shadows. Navigation width and opacity transition over 200ms while the editor and sidebar content stay mounted. Collapsed navigation is immediately inert and hidden from assistive technology; reduced motion disables transitions. Home toggles the project sidebar. When collapsed on desktop, a delayed hover reveals an opaque, anchored project-navigation preview using the same workspace surface, width, full workspace height and internal layout as the pinned sidebar. Its portal stays inside the application theme scope and follows the workspace bounds as the host resizes. The preview does not resize the editor or take focus; pointer travel into it is protected, and search focus keeps it open until dismissal. Mobile retains the click-operated drawer.

Albert Sans / 苹方统一用于界面与引导标题。时间码、编号与数值保留 Motion 已有的 IBM Plex Mono，不复制 OD 的 JiduMono 字体资产。本地字体及 SIL OFL 许可保存在 `packages/design-system/fonts/`。

- 正文 14px、控件 13px、说明 12px、密集标注至少 11px；标题 16 / 20 / 24 / 32px。
- Common spacing follows 4 / 8 / 12 / 16 / 24 / 32px. The shared radius scale is 2 / 4 / 6 / 10 / 12px (`xs` through `xl`); application controls use 6px, cards and menus 10px, and dialogs 12px.
- Standard application controls are 32px, compact controls 28px and icon buttons 32px. This is a deliberate global density setting shared by asset creation, navigation, settings and template browsing. The application header is 40px, with a 48px control rail, centered 32px square rail buttons and 18px rail icons; the nested MVP editor toolbar is 32px; panel headings retain their existing measured geometry. The editor toolbar and preview transport share the flat panel surface and subtle separator treatment. The toolbar uses equal side columns around its centered, content-sized editable project title, with a muted, tabular automatic-save indicator on the left and actions on the right; the template entry remains in the application rail.
- 常规反馈 150 / 200ms，点阵加载 1043ms；减少动态效果偏好停用循环动画。
- Studio saves Light, Dark or System in `hf-studio-ui-preferences`. System resolves before the first paint and follows live device changes; embedded editors continue to follow the host. Appearance cards preview the actual light/dark tokens, including the split System sample. Startup and crash recovery share a centered, bounded surface, rounded error details and neutral actions; copy/export results use floating Toasts.

## 首页与全局导航

首页使用居中内容区、大尺寸新建入口、最近项目、分类模板与底部创作输入，沿用本仓库主题与字体。按用户反馈移除宣传标题和解释段落，仅保留功能标签。共享侧栏位于最左侧，展开 224px、收起完全隐藏；760px 以下为抽屉。主区域贴齐视口，移除全局顶栏和外层圆角容器；连接 Agent、模型设置、主题、语言收纳到侧栏。

The conversation and browser sit side by side from the top of the viewport. Their title and tab bars are both 40px high, use `--motion-inset`, and have 1px separators; the project toolbar belongs to the Artifact Viewer on the right. The browser provides tabs, an address bar, new-tab and close actions. Expand/restore and close stay at the far right of the tab bar, in that order; expand uses outward corners, restore uses inward corners, and narrow layouts use a return-to-conversation icon. The conversation defaults to 340px and resizes between 280px and 480px, capped at 42% of available width; below 900px, the workspace switches between conversation and browser. Closing either side preserves the other usable area, and restoring preserves width and tabs. Hiding only the editor does not remount the player or Dock. The sidebar uses the shared product brand without a redundant collapse arrow. Global navigation sits above the conversation, moves above the browser when the conversation is hidden, and uses a local upper-left button on the home page. Collapsing the sidebar leaves no icon rail. The browser uses compact tabs, a separate navigation button group and a rounded address bar; the selected tab scrolls into view automatically.

新建入口使用点阵底纹；项目卡片采用工程图标，避免把图标当作实际影片截图。模板使用已有真实封面，`kind=builtin` 显示「可以二次剪辑」；首页统一先选择模板，再从 Motion 模式输入框提交为会话，接入弹框保留复制指令。详情见 [首页与项目会话](project-workspace.md)。

## 文件与职责

```text
packages/design-system/
  tokens.json     唯一设计变量源，双主题与提取来源
  tokens.css      从 JSON 生成，不手工修改
  ui.css          可移植样式入口
  fonts.css       本地字体声明
  base.css        作用域基础样式、焦点、减少动态效果
  controls.css    按钮、输入、标签、空态、进度、加载
  material.css    浮层材质、弹窗遮罩及透明度降级
  icons.svg       共享线性图标
  theme.js        可选的整页外观控制器
  index.html     可交互组件目录 /design-system
  catalog.*      组件目录布局与交互
  fonts/         字体与授权文件
packages/design-system/studio.css      Shared Studio presentation
packages/design-system/tailwind.css    Generated semantic utility adapter
studio/src/motion/theme.css             Editor layout and token-based details
studio/src/motion/workspace.css         首页、共享侧栏、创作会话、模板卡片与窄屏适配
studio/src/motion/MotionStudioHost.tsx  顶栏品牌、工程、MCP 与模板插槽
studio/src/motion/ConnectionDialog.tsx  MCP 与模板统一弹框
web/connect.*                          接入页面、配置下载与指南
web/template-gallery.*                 成片卡片、预览、出处、分类与热度
shared/integration.ts                  客户端配置与 Agent 指引
```

`tokens.json` 以 `motion.ui-tokens@1` 标识版本。`shared` 定义跨主题变量，`themes` 定义同名的亮暗变量，统一生成 `--motion-*`。原参考项目的 `--mc-*` 改为独立命名空间；保留编辑器与接入内容需要的变量。小字号辅助文字、错误/警告与时间轴领域色保留 Motion 的可读性适配，未机械复制 OD 的较浅文字色；正文及状态文字对比度通过 4.5:1 检查。视频预览仍用独立深色遮罩，作品 iframe 不加载宿主样式。

Connection setup keeps its native dialog. Template discovery has a separate full-viewport gallery and detail dialog; Escape closes the active menu or detail before returning to the gallery. Cards use immersive media and hover metadata, while author/source links, downloads and repository links remain in detail. Recreate copies the Agent instruction directly and reports success through the floating Toast layer. The right-aligned filter trigger shows only its icon, with an accessible name and a small active indicator; its menu aligns to the trigger's end and remains within viewport bounds. The legacy `/connect` address redirects to `?panel=connections`, while `?templates=1` opens discovery. See [template catalog data rules](template-catalog.md).

## 复用

Use the package entry points described in its [integration guide](../packages/design-system/README.md). Keep one maintained source; do not copy its styles into feature directories.

```html
<link rel="stylesheet" href="./design-system/ui.css">
<section data-motion-ui data-theme="light">
  <label class="ui-field">标题
    <input class="ui-input" placeholder="写一句，让人记住的话">
  </label>
  <button class="ui-button ui-button--primary">开始创作</button>
</section>
```

Tokens、基础规则和控件全部限定在 `[data-motion-ui]` 内，不重置外部宿主元素。主题由根容器的 `data-theme="light|dark"` 控制；没有该属性时按系统外观回退。宿主集成应直接设置容器属性。Studio 的 `[data-motion-studio]` 适配层按原生 `data-theme="paper"` 映射浅色，无该属性映射暗色。`theme.js` 用于本项目整页运行，操作 `document.documentElement`，移植到其他路径时同步调整其中的图标地址，嵌入其他应用时可不加载。

通用控件：`.ui-button` 支持 `--primary`、`--ghost`、`--accent`、`--danger`、`--sm`、`--icon`；`.ui-field` 与 `.ui-input` 用于原生表单；`.ui-badge` 表达状态；`.ui-empty`、`.ui-loader`、`.ui-progress` 提供空态与进度。图标用 SVG `use` 引用 `icons.svg#icon-*`，控制按钮须提供可读标签。

UI 主题不修改 Hyperframes 工程的 HTML、CSS 或 GSAP 动画。影片由工程源文件渲染，编辑器外观不会影响导出。

## 开发与验证

时间轴的素材操作栏是随选择出现的上下文入口，侧栏模型设置管理工作区能力（嵌入视图保留编辑器内入口），二者职责不同。操作栏复用 `--motion-*` 变量和原生时间轴状态；生成面板承载常用参数、候选与采用动作。完整的触发、隐藏、关闭/重开、时间参数和「交给 Agent」语义见 [时间轴交互设计](product/media-generation-design.md#时间轴交互规则及原因)。参考产品的价格或模型卡片不能直接成为本产品的收费与可用性说明。

```sh
npm run design:dev      # Independent visual workbench
npm run design:test     # Source-save, conflict and standalone checks
npm run design:tokens   # 修改 tokens.json 后生成 CSS
npm run design:check    # 检查生成同步、主题完整性、变量和文字对比度
npm run check          # 已包含设计检查
npm test
npm run test:studio
npm run typecheck:studio
npm run build:studio
npm run package:plugin
```

The independent visual workbench starts with `npm run design:dev` at `http://127.0.0.1:4187`; it can also run from a standalone copy of the package with `npm run dev`. Its inspector edits existing shared colors, fonts, radii, spacing, motion and component roles, reviews changes and saves the package token source plus generated styles. Agent edits use the same source, with refresh and conflict handling in the workbench. The application-hosted `/design-system` route is a read-only presentation with preview and JSON/CSS export. The workbench has no Studio, application-service or business-module dependency. See the [workbench guide](../packages/design-system/README.md#visual-editing-and-agent-editing) for scope and concurrency limits.

插件打包包含编辑器源码、构建产物、设计系统和字体许可。编辑器依赖本地 Hyperframes 服务，不再提供旧 Canvas 预览的单文件离线构建。

面板由原版 Dock 管理；1040px 以下顶栏允许换行，650px 以下模板库为单列。MCP、模板库、撤销/重做、历史、预览与布局入口均在顶栏对齐。预览关闭后可一键恢复；布局菜单提供面板显示、预设和重置，版本历史也是可拖动面板。面板边界使用连续 1px 分隔线，滑条使用 2px 轨道与 6px 滑块。验收覆盖深浅主题、键盘焦点、窄屏、原生编辑保存与撤销、版本恢复、布局恢复、模板切换、MCP 配置和真实 MP4 导出。


## Immersive template discovery

The Studio template library uses the editor's active light or dark theme. The
shared token source defines `gallery-surface`, `gallery-control`, `gallery-border`
and `gallery-stage-wash` in both themes. Studio's template aliases consume these
values alongside existing text, focus, selection, overlay and shadow tokens.
Video-overlay text retains its media-specific contrast independently of the theme.
The highlighted Submit video action uses `brand` and `on-brand`; secondary actions
use the same neutral control and menu surfaces as the editor.

Sorting and industry pickers reuse Studio's Base UI `Menu` and radio items, with
an inline portal inside the native dialog, keyboard navigation and consistent
chevron spacing. The gallery has no separate playback toolbar button. Purpose
categories describe intended videos; style, industry and other facets remain
independently selectable. The full-window detail provides direct copy actions and
repository links without a second recreation modal.

The shared `Skeleton` primitive uses `skeleton-base` and `skeleton-highlight` tokens in both themes, with reduced-motion support. Catalog placeholders reserve the final card geometry; lazy poster placeholders stay static to avoid animating offscreen cards. Detail preview buffering and retry states stay inside the media frame. Discovery filter menus are non-modal, keep checkbox selection open, and expose removable condition chips. Search uses a single outer focus treatment; detail action rows and guide summaries share inset padding and rounded hover surfaces. Recreate and submit uses the bundled Remix git-branch icon.


## Interaction and feedback contract

This contract applies to new and changed product UI, including the editor, template discovery and native dialogs. The repository-wide entry is [AGENTS.md](../AGENTS.md#ui-design-system-and-interaction-feedback).

| Situation | Required presentation |
| --- | --- |
| Copy, save, download or other short action result | Floating Toast, outside document flow; no paragraph beneath the triggering button |
| Quick filtering or sorting | Anchored, non-modal shared Menu; immediate results, removable conditions and clear-all |
| Grouped multi-select filtering | Anchored, non-modal shared Popover with category tabs, a live draft match count, Apply and clear-current/clear-all actions |
| Resource loading | Shared Skeleton in the resource's reserved geometry; retain a usable poster during video loading |
| Resource failure | Recoverable state within that same reserved region, with retry or meaningful fallback |
| Persistent input validation | Associated with the field and its reserved error space; distinct from an operation-result Toast |

Use `useToast` with `StudioToastViewport`. The viewport uses `FeedbackLayer`, which follows the active native dialog or shared application dialog marked with `data-feedback-modal` and uses the browser top layer where supported. Notifications remain visible and interactive above modal content while the surrounding overlay is transparent to pointer input. Do not create an ad hoc toast store or render `StudioToast` as an ordinary content row. Ordinary info feedback expires after three seconds; actionable failures remain dismissible. Optional Toast actions remain available until dismissed, completed or displaced by the bounded stack, prevent duplicate execution while pending, and remain retryable after failure. Repeated messages coalesce by action identity as well as content so independent Undo targets stay distinct. A copy failure may expose selectable instruction content for recovery, but its notification still floats.

Menus, popovers and Toasts must open in the intended floating layer, stay inside viewport bounds and preserve the user's working context. Multi-select filter items keep their menu open. Escape dismisses the active menu first, returning focus to its trigger. Clicking a condition's remove action clears only that condition. Routine copy sends the complete brief to the clipboard in one action, without a second instruction modal.

Use semantic surface, text, border, selected, focus and overlay tokens in both themes. Hover backgrounds stay inside a rounded item with breathing room: standard discovery menus use 6px outer padding and 8px by 10px item padding; detail action rows use 10px by 12px padding and 8px corners. Keep chevrons in a fixed trailing slot. Composite search fields have one outer focus treatment, never a second inset input outline; keyboard focus remains visible.

Shared Skeletons reserve the final proportions, use subtle theme-aware contrast, and stop animation for reduced motion. Lazy offscreen poster placeholders remain static. Real images fade in after decoding, failed images retain a meaningful title fallback, buffering stays inside the video frame, and known failures end loading and expose retry. Keep transient notifications separate from these resource states. Do not add decorative status badges that duplicate adjacent metadata.

Browser acceptance includes actual open dropdowns, copy success/failure Toasts above a native dialog, stable content coordinates before/after feedback, keyboard dismissal, loading-to-content/error transitions, both themes and a narrow viewport. Source inspection and a component screenshot alone do not establish these behaviors.

The package-owned `studio/editor-workspace.css` defines continuous editor surfaces, panel dividers, layout-menu icon alignment and timeline control-column, row, grid and icon-control styling. Project navigation, dock panels, toolbars, preview transport and timeline boundaries use a single 1px line in the shared subtle-border role. Resize hit areas and active drag feedback retain their existing geometry. Studio supplies measured dock widths, row heights and tick spacing; both themes use the same semantic roles, and authored clip artwork remains independent.

The dark theme uses neutral near-black workspace surfaces, a restrained raised-control layer and low-emphasis structural borders. Text and interactive states retain the shared contrast checks. Timeline track controls and the resizable control-column divider consume package-owned recipes; project artwork and preview iframe colors are unaffected.

### Grouped discovery filters and alignment

The icon-only discovery filter opens an anchored, non-modal panel. Its 640px desktop layout combines category tabs with a two-column option grid. Choices remain a draft while switching tabs; a live count previews the result, Apply commits once, and dismissal discards changes. Quick purpose and industry controls still apply immediately. Clear selection resets the active group; Clear filters resets draft facets and editability while retaining the independent search. Applied conditions remain individually removable. Groups with more than twelve choices provide local search without losing hidden selections.

Header, content and footer share one panel gutter; detail navigation and body share one sidebar gutter. Trailing icon actions use fixed control geometry and do not shrink when labels wrap. Checkboxes retain visible outlines in both themes, and selected glyphs inherit the selected text role. Hover fills remain rounded and inset. Verify the opened panel and detail in both themes and at narrow widths; inspect visible SVG paths, not just the presence of an empty SVG element.

### Creative surfaces and execution

Application controls use the shared 32px `control` height, with 28px compact actions. The `om-control-row` recipe aligns search fields, plain or icon-bearing selects and adjacent icon buttons to the same baseline; leading artwork must not increase a trigger's height. Multiline fields and descriptive menu options can grow with their content. Creative surfaces use compact typography, 24px icon tiles, 64px decorative emblems and restrained card borders. Keep panel spacing in feature layout styles and all control, typography and material recipes in the package.

The package-owned `studio/application.css` provides creative media identities, prompt surfaces, suggestion cards, Agent messages and compact generation rows. The `creative-image`, `creative-video`, `creative-audio` and `creative-agent` semantic roles are defined for both themes in `tokens.json`. Icons and labels carry meaning alongside color. Generation rows use a 32px thumbnail or waveform, a single-line prompt, compact phase steps and expandable errors. Large decorative emblems remain limited to empty-state introductions. Orbit and waveform motion indicate an active task; real service phases drive submitted, creating and saved states without invented percentages. Reduced motion disables these animations, and hidden creation surfaces pause them. Known preview failures retain a static media emblem and the result action. Features own panel geometry, scrolling and task data; direct creation keeps its submit action outside the scrolling input area.
