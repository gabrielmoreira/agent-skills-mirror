---
name: frontend-slides
description: 从零开始创建令人惊叹、动画丰富的 HTML 演示文稿，或通过转换 PowerPoint 文件生成。适用于用户想要构建演示文稿、将 PPT/PPTX 转换为 Web 页面、或为演讲/路演创建幻灯片的场景。帮助非设计师用户通过视觉探索而非抽象选择来发现他们的审美偏好。
origin: ECC
---

# 前端幻灯片（Frontend Slides）

创建零依赖（Zero-dependency）、动画丰富的 HTML 演示文稿，完全在浏览器中运行。

灵感来源于 [zarazhangrui](https://github.com/zarazhangrui) 作品中所展示的视觉探索方法。

## 何时激活

- 创建演讲文稿（Talk Deck）、路演文稿（Pitch Deck）、研讨会文稿或内部演示文稿
- 将 `.ppt` 或 `.pptx` 幻灯片转换为 HTML 演示文稿
- 改进现有 HTML 演示文稿的布局、动效或排版
- 与尚不清楚设计偏好的用户一起探索演示风格

## 核心约束（Non-Negotiables）

1. **零依赖（Zero dependencies）**：默认生成单个自包含的 HTML 文件，内联 CSS 和 JS。
2. **必须适配视口（Viewport fit is mandatory）**：每张幻灯片必须完全填满一个视口，不得有内部滚动。
3. **视觉先行（Show, don't tell）**：使用视觉预览而不是抽象的风格问卷。
4. **独特的设计**：避免使用通用的紫色渐变、白色背景上的 Inter 字体等模板化的设计。
5. **生产级质量**：保持代码注释清晰、具备无障碍性（Accessible）、响应式且性能良好。

在生成之前，请阅读 `STYLE_PRESETS.md` 以了解视口安全 CSS 基础、内容密度限制、预设目录和 CSS 注意事项。

## 工作流（Workflow）

### 1. 检测模式（Detect Mode）

选择一条路径：
- **新演示文稿**：用户有主题、笔记或完整草案
- **PPT 转换**：用户持有 `.ppt` 或 `.pptx` 文件
- **增强**：用户已有 HTML 幻灯片并希望进行改进

### 2. 内容探索（Discover Content）

仅询问最基本的需求：
- 目的：路演、教学、会议演讲、内部更新
- 长度：短（5-10 页）、中（10-20 页）、长（20 页以上）
- 内容状态：已完成的文案、粗略笔记、仅有主题

如果用户已有内容，请要求他们在进行风格设计前粘贴内容。

### 3. 风格探索（Discover Style）

默认为视觉探索。

如果用户已经知道所需的预设，跳过预览并直接使用。

否则：
1. 询问文稿应营造什么感觉：震撼、活力、专注、启发。
2. 在 `.ecc-design/slide-previews/` 中生成 **3 个单页预览文件**。
3. 每个预览必须是自包含的，清晰展示排版/颜色/动效，且幻灯片内容保持在 100 行左右。
4. 询问用户保留哪个预览，或者混合哪些元素。

在将情绪映射到风格时，请参考 `STYLE_PRESETS.md` 中的预设指南。

### 4. 构建演示文稿（Build the Presentation）

输出以下之一：
- `presentation.html`
- `[presentation-name].html`

仅当文稿包含提取的或用户提供的图像时，才使用 `assets/` 文件夹。

要求结构：
- 语义化的幻灯片部分（slide sections）
- 来自 `STYLE_PRESETS.md` 的视口安全 CSS 基础
- 用于主题值的 CSS 自定义属性（Variables）
- 用于键盘、滚轮和触摸导航的演示控制器类
- 用于显示动画的相交观察器（Intersection Observer）
- 减弱动态效果（Reduced-motion）支持

### 5. 强制视口适配（Enforce Viewport Fit）

将其视为硬性关卡。

规则：
- 每个 `.slide` 必须使用 `height: 100vh; height: 100dvh; overflow: hidden;`
- 所有字体和间距必须使用 `clamp()` 进行缩放
- 当内容放不下时，拆分为多张幻灯片
- 绝不通过将文本缩小到不可读的大小来解决溢出问题
- 绝不允许在幻灯片内部出现滚动条

使用 `STYLE_PRESETS.md` 中的密度限制和强制性 CSS 块。

### 6. 验证（Validate）

在以下尺寸下检查完成的文稿：
- 1920x1080
- 1280x720
- 768x1024
- 375x667
- 667x375

如果浏览器自动化工具可用，使用它来验证没有幻灯片溢出，并且键盘导航正常工作。

### 7. 交付（Deliver）

在移交时：
- 删除临时预览文件，除非用户想要保留它们
- 在有用时，使用平台适用的命令打开文稿
- 总结文件路径、使用的预设、幻灯片数量以及简单的方案自定义点

为当前操作系统使用正确的打开命令：
- macOS: `open file.html`
- Linux: `xdg-open file.html`
- Windows: `start "" file.html`

## PPT / PPTX 转换

对于 PowerPoint 转换：
1. 优先使用带有 `python-pptx` 的 `python3` 来提取文本、图像和备注。
2. 如果 `python-pptx` 不可用，询问是否安装它，或者回退到手动/基于导出的工作流。
3. 保留幻灯片顺序、演讲者备注和提取的资产。
4. 提取后，运行与新演示文稿相同的风格选择工作流。

保持转换跨平台。当 Python 可以胜任时，不要依赖仅限 macOS 的工具。

## 实现要求（Implementation Requirements）

### HTML / CSS

- 除非用户明确要求多文件项目，否则使用内联 CSS 和 JS。
- 字体可能来自 Google Fonts 或 Fontshare。
- 偏好大气背景、强大的排版层次结构和清晰的视觉方向。
- 使用抽象形状、渐变、网格、噪声和几何图形，而不是插图。

### JavaScript

包括：
- 键盘导航
- 触摸 / 滑动导航
- 鼠标滚轮导航
- 进度指示器或幻灯片索引
- 进入时显示（reveal-on-enter）的动画触发器

### 无障碍性（Accessibility）

- 使用语义化结构 (`main`, `section`, `nav`)
- 保持对比度可读
- 支持纯键盘导航
- 尊重 `prefers-reduced-motion`

## 内容密度限制（Content Density Limits）

除非用户明确要求更密集的幻灯片且可读性仍然保持，否则请遵循以下最大值：

| 幻灯片类型 | 限制 |
|------------|-------|
| 标题 | 1 个标题 + 1 个副标题 + 可选的标语 |
| 内容 | 1 个标题 + 4-6 个项目符号或 2 个短段落 |
| 功能网格 | 最多 6 个卡片 |
| 代码 | 最多 8-10 行 |
| 引用 | 1 个引用 + 署名 |
| 图像 | 1 张受视口约束的图像 |

## 反模式（Anti-Patterns）

- 没有视觉标识的通用初创公司渐变
- 使用系统字体的文稿，除非是有意的编辑风格
- 长篇的项目符号墙
- 需要滚动的代码块
- 在短屏幕上崩溃的固定高度内容框
- 无效的负值 CSS 函数，如 `-clamp(...)`

## 相关 ECC 技能（Related ECC Skills）

- `frontend-patterns`：用于文稿周围的组件和交互模式
- `liquid-glass-design`：当演示文稿有意借用 Apple 玻璃美学时使用
- `e2e-testing`：如果你需要为最终文稿进行自动化浏览器验证

## 交付清单（Deliverable Checklist）

- 演示文稿可以从本地文件在浏览器中运行
- 每张幻灯片都适配视口且无需滚动
- 风格独特且有针对性
- 动画有意义而非杂乱
- 尊重减弱动态效果（Reduced motion）
- 在移交时说明文件路径和自定义点
