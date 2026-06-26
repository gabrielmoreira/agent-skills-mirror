---
name: frontend-slides
description: 从零开始或通过转换 PowerPoint 文件创建令人惊叹、动画丰富的 HTML 演示文稿（Presentations）。适用于用户想要构建演示文稿、将 PPT/PPTX 转换为 Web 页面或为演讲/路演创建幻灯片（Slides）的场景。通过视觉探索而非抽象选择，帮助非设计师发掘其审美偏好。
origin: ECC
---

# 前端幻灯片（Frontend Slides）

创建零依赖、动画丰富且完全在浏览器中运行的 HTML 演示文稿。

灵感来源于 [zarazhangrui](https://github.com/zarazhangrui) 作品中所展示的视觉探索方法。

## 何时激活

- 创建演讲稿、路演包（Pitch Deck）、工作坊课件或内部演示文稿
- 将 `.ppt` 或 `.pptx` 幻灯片转换为 HTML 演示文稿
- 改进现有 HTML 演示文稿的布局、动态效果或排版
- 与尚不确定设计偏好的用户一起探索演示风格

## 核心原则（不可逾越）

1. **零依赖（Zero dependencies）**：默认使用内联 CSS 和 JS 的自包含（Self-contained）单 HTML 文件。
2. **强制视口适配（Viewport fit）**：每张幻灯片必须适配单个视口（Viewport），严禁内部滚动。
3. **展示而非言传（Show, don't tell）**：使用视觉预览，而非抽象的风格调查问卷。
4. **独特设计（Distinctive design）**：避免通用的紫色渐变、白底 Inter 字体等模板感过强的设计。
5. **生产级质量（Production quality）**：保持代码注释清晰、具备可访问性（Accessible）、响应式且性能良好。

在生成之前，请阅读 `STYLE_PRESETS.md` 以获取视口安全 CSS 基准、密度限制、预设目录和 CSS 注意事项。

## 工作流（Workflow）

### 1. 检测模式（Detect Mode）

选择一条路径：
- **新演示文稿**：用户已有主题、笔记或完整草稿
- **PPT 转换**：用户持有 `.ppt` 或 `.pptx` 文件
- **增强（Enhancement）**：用户已有 HTML 幻灯片并希望进行改进

### 2. 发现内容（Discover Content）

仅询问最少必要信息：
- 目的：路演、教学、会议演讲、内部更新
- 长度：短（5-10 页）、中（10-20 页）、长（20+ 页）
- 内容状态：已完成的文案、粗略笔记、仅有主题

如果用户已有内容，请在设计样式前要求其粘贴。

### 3. 发现风格（Discover Style）

默认采用视觉探索方式。

如果用户已知所需的预设（Preset），则跳过预览并直接使用。

否则：
1. 询问幻灯片应营造的感觉：震撼（Impressed）、活力（Energized）、专注（Focused）、启发（Inspired）。
2. 在 `.ecc-design/slide-previews/` 中生成 **3 个单页幻灯片预览文件**。
3. 每个预览必须是自包含的，清晰展示排版/颜色/动态效果，且幻灯片内容保持在 100 行以内。
4. 询问用户保留哪个预览或混合哪些元素。

在将情绪映射到风格时，请参考 `STYLE_PRESETS.md` 中的预设指南。

### 4. 构建演示文稿（Build the Presentation）

输出以下之一：
- `presentation.html`
- `[presentation-name].html`

仅当演示文稿包含提取的或用户提供的图像时，才使用 `assets/` 文件夹。

必要结构：
- 语义化的幻灯片部分（Slide Sections）
- 来自 `STYLE_PRESETS.md` 的视口安全 CSS 基准
- 用于主题值的 CSS 自定义属性
- 用于键盘、滚轮和触摸导航的演示文稿控制器类
- 用于揭示动画（Reveal Animations）的 Intersection Observer
- 减弱动态效果（Reduced-motion）支持

### 5. 强制视口适配（Enforce Viewport Fit）

将其视为严格的准入门槛。

规则：
- 每个 `.slide` 必须使用 `height: 100vh; height: 100dvh; overflow: hidden;`
- 所有字体和间距必须使用 `clamp()` 进行缩放
- 当内容不适配时，拆分为多张幻灯片
- 严禁通过将文本缩小到可读尺寸以下来解决溢出问题
- 严禁在幻灯片内部出现滚动条

使用 `STYLE_PRESETS.md` 中的密度限制和强制性 CSS 代码块。

### 6. 验证（Validate）

在以下尺寸检查完成的幻灯片：
- 1920x1080
- 1280x720
- 768x1024
- 375x667
- 667x375

如果浏览器自动化工具可用，请使用它来验证没有幻灯片溢出且键盘导航正常工作。

### 7. 交付（Deliver）

交付时：
- 删除临时预览文件，除非用户希望保留
- 在有用时使用相应平台的打开命令打开演示文稿
- 总结文件路径、所用预设、幻灯片数量以及简易的主题自定义点

为当前操作系统使用正确的打开命令：
- macOS: `open file.html`
- Linux: `xdg-open file.html`
- Windows: `start "" file.html`

## PPT / PPTX 转换

对于 PowerPoint 转换：
1. 优先使用带有 `python-pptx` 的 `python3` 来提取文本、图像和备注。
2. 如果 `python-pptx` 不可用，询问是否安装或回退到手动/基于导出的工作流。
3. 保留幻灯片顺序、演讲者备注和提取的资产（Assets）。
4. 提取后，运行与新演示文稿相同的风格选择工作流。

保持转换的跨平台性。当 Python 可以胜任时，不要依赖仅限 macOS 的工具。

## 实现要求（Implementation Requirements）

### HTML / CSS

- 除非用户明确要求多文件项目，否则使用内联 CSS 和 JS。
- 字体可来自 Google Fonts 或 Fontshare。
- 偏好氛围感背景、强大的排版层级和清晰的视觉方向。
- 使用抽象形状、渐变、网格、噪点和几何图形，而非插图。

### JavaScript

包含：
- 键盘导航
- 触摸 / 滑动导航
- 鼠标滚轮导航
- 进度指示器或幻灯片索引
- 进入视图时的揭示动画触发器（Reveal-on-enter animation triggers）

### 可访问性（Accessibility）

- 使用语义化结构（`main`, `section`, `nav`）
- 保持对比度清晰可读
- 支持纯键盘导航
- 尊重 `prefers-reduced-motion`

## 内容密度限制（Content Density Limits）

除非用户明确要求更密集的幻灯片且仍保持可读性，否则请遵循以下最大值：

| 幻灯片类型 | 限制 |
|------------|-------|
| 标题 | 1 个主标题 + 1 个副标题 + 可选的标语 |
| 内容 | 1 个标题 + 4-6 个要点或 2 个短段落 |
| 功能网格 | 最多 6 个卡片 |
| 代码 | 最多 8-10 行 |
| 引用 | 1 个引用 + 出处 |
| 图像 | 1 张受视口约束的图像 |

## 反模式（Anti-Patterns）

- 缺乏视觉特性的通用创业公司风格渐变
- 使用系统字体（除非是有意的社论风格）
- 长篇累牍的要点列表（Bullet walls）
- 需要滚动的代码块
- 在短屏幕上会崩溃的固定高度内容框
- 无效的负值 CSS 函数，如 `-clamp(...)`

## 相关 ECC 技能（Related ECC Skills）

- `frontend-patterns`：用于幻灯片的组件和交互模式
- `liquid-glass-design`：当演示文稿有意借用 Apple 玻璃拟态美学时
- `e2e-testing`：如果需要对最终幻灯片进行自动化浏览器验证

## 交付清单（Deliverable Checklist）

- 演示文稿可通过本地文件在浏览器中运行
- 每张幻灯片适配视口且无需滚动
- 风格独特且具有设计感
- 动画有意义而非噪音
- 尊重减弱动态效果（Reduced motion）设置
- 交付时已说明文件路径和自定义点
