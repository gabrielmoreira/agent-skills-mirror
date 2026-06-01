---
name: doa-ppt
description: >
  生成或优化商务PPT演示文稿、产品介绍、技术方案、项目报告，支持多页HTML幻灯片预览、
  HTML转PPT导出，或将PDF、截图、笔记、参考文档等源材料转化为精美演示文稿。
  不用于独立网页或Web应用。
---

# HTML to PPTX — 商务演示文稿生成

## 工作流概览

```
用户输入（描述 + 参考图）
  → 确认PPT规模
  → 使用公司模板（唯一默认模板）
  → 生成可翻页 HTML 预览
  → 逐页检查 HTML 是否越界/裁切/重叠
  → 用户确认/调整 HTML
  → 只有用户明确确认 HTML 无问题后，才进入 PPT 模式选择
  → 默认推荐截图高保真模式（用户如需二次编辑再切换到可编辑）
  → 生成 PPT
```

## 本次实战经验固化

当用户提供 PDF、截图、既有 HTML 或已有 PPT，并要求“基于这个继续生成 / 整合 / 扩展 / 转 PPT”时，必须先把资料链路整理清楚，再改版式。

### 2026-05-30 延峰项目增补（强制）

1. **HTML 是唯一语义源**：`slides.html` 才是可维护源文件；截图型 `.pptx/.pdf` 只作为交付物，不作为反向编辑来源。
2. **双导出链路必须物理分离**：
  - 截图高保真：`export_pptx.py`
  - 可编辑重建：`export_editable_pptx.py`
  - 严禁在同一脚本里混合两种导出逻辑，避免需求反复切换时互相污染。
3. **需求切换优先级规则**：当用户在“可编辑 / 不可编辑”之间反复切换时，始终以“最后一次明确指令”为准，立即切换导出模式，不纠缠历史决策。
4. **先定稿再导出**：只有在用户明确确认“按当前 HTML 导出”后，才执行最终导出；导出阶段不再顺手改布局，避免一边改版一边导出导致版本漂移。
5. **输出文件不得覆盖旧版本**：每次最终交付使用新文件名（建议带日期和后缀，如 `_Editable_YYYYMMDD`、`_HD_YYYYMMDD`），防止 `PermissionError` 和历史交付丢失。
6. **导出后必须二次验证**：至少校验文件存在、页数一致、截图分辨率正确（高清链路应为 `2560×1440`），再对外宣称“已完成交付”。

### 资料驱动型 PPT 的处理顺序

1. **先定位源材料**：在工作区搜索 `.pdf`、`.html`、`.pptx`、生成脚本和相关资源，确认哪一个是主源文件、哪一个是导出结果。
2. **PDF 先提取文本，失败再转图片阅读**：优先用 `pypdf/pdfplumber`；如果每页文本为空，说明多半是扫描型 PDF，应使用 PyMuPDF 渲染为图片后逐页查看。
3. **先总结再入页**：不要把 PDF 原文堆进 PPT。先提炼为“调研范围 → 候选路线 → 选型结论 → 当前方案”的决策链路。
4. **封面优先确认**：封面通常是客户第一眼看到的页面。若用户要求“第 N 页挪到首页作为封面”，必须同步调整 `active` 状态、`data-index` 和页码。
5. **插入/删除页面后整体重编号**：任何插页、删页、重排都要统一更新以下内容，缺一不可：
   - 每页 `data-index` 属性（从 0 连续递增）
   - 每页 `.page-no` 页码（当前页 / **新总数**）
   - 目录页中对应条目的增删和序号重编
   - HTML 注释中的页码标注（如 `<!-- P7: xxx -->`）
   - 使用 `multi_replace_string_in_file` 一次性完成所有页码更新，避免遗漏

### 技术方案类 PPT 推荐叙事结构

对于架构、安全、技术选型类 PPT，优先采用以下结构：

1. 封面：结论导向，明确方案对象、日期和一句话判断
2. 调研范围：说明为什么要调研，选型标准是什么
3. 候选路线：把语言级、进程级、内核级、容器级、云托管等方案放在一张对比页
4. 选型结论：说明为什么选择当前方案，而不是只说“推荐方案”
5. 风险论证：用业务可理解的语言说明备选方案的风险边界
6. 推荐架构：给出控制面、执行面、隔离边界、运行时治理
7. 落地配置：给出参考规格、扩容方式、运维和审计能力
8. 最终结论：用一句客户能复述的话收束，例如“跑自己的任务用 Job，跑别人的代码用沙箱”

### 版式与导出踩坑记录

- 固定幻灯片画布仍使用 `1280×720`。浏览器预览可以通过 CSS/JS 做自适应缩放，但导出截图必须保持 `.slides-viewport` 的原始 1280×720 尺寸。
- 每次新增 layout class 后，要检查它是否覆盖 `.content{height:600px}`。如果直接把 `.grid-*` 用在 `.content` 上，必须补 `.content.grid-*{height:600px}` 防止内容压到 footer。
- 高保真导出脚本激活页面时不要写 `slide.className = 'slide active'`，否则会丢失 `cover` 等特殊 class。应使用 `classList.remove('active','exit-left')` 和 `classList.add('active')`。
- PowerShell 执行带空格路径的 Python 时必须用调用运算符：`& "c:/path with spaces/.venv/Scripts/python.exe" script.py`。
- 如果 PPT 文件可能正被 PowerPoint 打开，优先输出到新文件名，避免 `PermissionError`。

### SVG 装饰插图踩坑记录

- **SVG 默认 `overflow:visible`**：SVG 子元素（`<circle>`, `<rect>` 等）即使超出 `viewBox` 范围，浏览器仍会渲染并占据布局空间。`getBoundingClientRect()` 会返回超出 viewBox 的实际渲染区域，导致边界检查报越界。
- **CSS `overflow:hidden` 对 SVG 子元素的 bounding rect 无效**：给 SVG 父容器加 `overflow:hidden` 只能在视觉上裁剪，但 `getBoundingClientRect()` 仍然返回子元素的完整渲染尺寸，边界检查仍会报 overflow。
- **正确做法：确保 SVG 内容不超出 viewBox**：所有 `<circle>`, `<rect>` 等元素的坐标 + 半径/尺寸必须在 `viewBox` 范围内。例如 `viewBox="0 0 320 320"` 中，`<circle cx="220" r="130">` 右边界为 350，超出 320，必须减小 cx 或 r。
- **不要使用负偏移量让 SVG 超出幻灯片边界**：如 `right:-30px` 会让 SVG 内容溢出 slide 右边界。背景装饰 SVG 应使用 `right:0` 并让视觉内容自然收敛在 viewBox 内。
- **装饰 SVG 推荐写法**：`position:absolute; pointer-events:none; z-index:0; opacity:0.03~0.08`，确保不影响交互且视觉上足够微妙。

### 左右分栏等高对齐踩坑记录

> **强制规则：所有使用左右分栏的内容页，左右两列必须等高对齐，底部齐平。这是不可协商的硬性要求。**

- **`.grid-2 { align-items: stretch }` 只拉伸直接子元素**：grid 子 div 会被拉伸到等高，但内部元素（表格、卡片）不会自动填满。
- **必须在 grid 子 div 上加 `display:flex; flex-direction:column`**：让内部元素参与 flex 布局。
- **需要填满高度的元素加 `flex:1`**：表格用 `style="flex:1"` 填满剩余高度；多张卡片用 `flex:1` 让每张卡片等分空间。
- **左右卡片数量不对等时，少的一侧每张卡片必须加 `flex:1`**：例如左 3 卡片、右 2 卡片，右侧每张卡片必须加 `flex:1` 使其自动拉伸填满。禁止出现一侧比另一侧短、底部有大段空白的情况。
- **左右分栏的父容器必须填满内容区**：`.content` 加 `display:flex;flex-direction:column`，`.grid-2` 加 `flex:1` 或 `style="height:100%"`，确保 grid 占满内容区而非只占内容自然高度。

#### 2026-05-31 图文分栏对齐补充（强制）

- **`.screenshot-panel` 默认 padding 导致高度不对齐**：`.screenshot-panel` 类自带 `padding:8px`，会导致图片面板比左侧内容区矮 16px。**必须在 style 中加 `padding:0` 覆盖**，否则左右高度永远对不齐。
- **背景配图必须用 `object-fit:cover`**：背景类图片（非产品截图）用 `width:100%;height:100%;object-fit:cover` 铺满面板，不留白边。产品截图用 `object-fit:contain` 保留完整界面。
- **flex 子元素必须加 `min-height:0`**：flex 容器的子元素默认 `min-height:auto`，内容过多时会撑破容器导致溢出。**所有 flex 子元素（左侧内容区、右侧图片面板）都必须加 `min-height:0`**。
- **图片面板必须加 `overflow:hidden`**：防止图片超出面板边界。
- **图片不要用 `.product-screenshot` 类**：该类自带 `box-shadow` 和 `border`，适用于产品截图，不适用于背景配图。背景配图直接写内联样式 `border-radius:14px`。
- **左侧内容区也要 `min-width:0`**：flex 子元素默认 `min-width:auto`，表格等元素可能撑宽导致右侧图片被压缩。加 `min-width:0` 允许内容区按比例缩小。

#### 对齐问题诊断清单

当左右高度不对齐时，按以下顺序检查：

1. ☐ `.content` 是否有 `display:flex;align-items:stretch`？
2. ☐ 右侧面板是否有 `padding:0` 覆盖默认 padding？
3. ☐ 图片是否有 `width:100%;height:100%;object-fit:cover`？
4. ☐ 左右两侧是否都有 `min-height:0`？
5. ☐ 左侧是否有 `min-width:0`？
6. ☐ 右侧是否有 `overflow:hidden`？
- **典型结构**：
  ```html
  <div class="grid-2">
    <div style="display:flex;flex-direction:column;">
      <div style="...title...">标题</div>
      <table class="cmp-table" style="flex:1;">...</table>
    </div>
    <div style="display:flex;flex-direction:column;">
      <div style="...title...">标题</div>
      <table class="cmp-table" style="flex:1;">...</table>
    </div>
  </div>
  ```

### 减少空白与紧凑排版踩坑记录

- **页眉上边距应紧凑**：`.header { padding: 24px 56px 0 }` 而非 32px，减少页眉到内容区的间距。色条 `.header::after { top: 68px }` 同步调整。
- **内容区高度最大化**：`.content { padding: 16px 56px 10px; height: 600px }` 而非旧值 `40px/32px/548px`，可用面积增加约 20%。
- **`font-size` 全局下限 15px**：整个 PPT 中不允许出现小于 15px 的文字。如果内容放不下，优先精简文案或拆页，不要缩小字号。
- **底部摘要/结论用 `margin-top:auto` 推到底部**：全宽表格页（如对比矩阵 + 底部摘要）应让 `.content` 设为 `display:flex;flex-direction:column`，底部摘要块用 `margin-top:auto` 贴近底部，消除表格与摘要之间的大片空白。
- **警告/提示框不要用 `position:absolute`**：绝对定位的提示框容易与上方内容重叠或在不同内容量时错位。应放在正常文档流中，用 `margin-top:auto` 或 `margin-top:10px` 控制位置。
- **grid-2 内部结合 flex:1 填满高度**：`.grid-2` 的父容器 `.content` 设为 `display:flex;flex-direction:column`，然后 `.grid-2` 自身加 `flex:1` 使其填满剩余空间，避免 grid 与 footer 之间出现大段空白。
- **典型紧凑内容页结构**：
  ```html
  <div class="content" style="display:flex;flex-direction:column;">
    <table class="cmp-table">...</table>
    <div style="margin-top:auto;padding:12px 16px;background:var(--primary-soft);border-radius:8px;">
      <strong>💡 结论：</strong>摘要文字
    </div>
  </div>
  ```

### 字体放大与溢出联动踩坑记录

> **当用户反馈"字太小、看不清"时，必须按以下策略系统性放大字体，同时联动调整布局参数防止溢出。**

- **系统性放大而非逐个调整**：使用 Python 正则脚本批量替换，对 `font-size:Npx` 统一 +2px（13→15, 14→16, 15→17, 16→18, 17→19, 18→20），`.page-title` 从 30→34px。不要只改一两处导致大小不统一。
- **内容区高度联动增加**：字体放大后 `.content { height }` 从 590→600px，`padding` 从 `20px 56px 14px` → `16px 56px 10px`，腾出更多垂直空间。
- **图片高度联动缩减**：字体放大必然挤压空间，图片高度按比例缩减：280→240, 220→190, 200→175, 150→140。优先保证文字可读性，图片可以小一些。
- **放大后必须逐页检查溢出**：使用浏览器 JS 遍历所有 `.slide`，计算 `scrollHeight - clientHeight`，任何 > 2px 的页面必须修复（缩减图片、减少间距、精简文案）。1-2px 的误差属于亚像素渲染，可忽略。
- **时间轴/步骤类页面最容易溢出**：这类页面元素多且垂直堆叠，放大后优先压缩 margin-bottom（20→12px）、图片高度、标题 margin，必要时删除 `<br>` 空行。

### PDF 导出踩坑记录

- **Pillow `Image.save(save_all=True)` 可用于简单场景**：将截图 PNG 合并为多页 PDF，代码最简洁，适合截图高保真模式。需要 `convert('RGB')` 去掉 alpha 通道。
- **reportlab 适合需要自定义页面尺寸的场景**：如果 PDF 页面尺寸需要精确控制（如匹配 2x 截图分辨率 2560×1440），使用 reportlab。
- **同时导出 PPTX + PDF 时，共享截图**：截图只做一次，分别喂给 `build_pptx()` 和 `build_pdf()` 两个函数，避免重复截图。

### 导出后的强制校验

截图高保真 PPT 生成后，必须验证：

1. `.pptx` 文件存在
2. `Presentation(...).slides` 页数等于 HTML 中 `.slide` 数量
3. `ppt/media/image*.png` 数量等于页数
4. 首页截图尺寸应与 `VIEWPORT × DEVICE_SCALE` 一致；标准 2x 高清链路下应为 `2560×1440`
5. 若封面应为深色/有色背景，检查首页或封面页的平均 RGB，避免背景丢失变白
6. 如果封面被挪到其他页，校验对应媒体图，而不是只校验 `image1.png`

## Step 1: 收集需求

向用户收集以下信息：

1. **业务功能描述**：产品/功能的核心卖点、关键特性、目标用户
2. **参考图**（可选）：用于参考布局和内容排版
3. **PPT 规模**（必选）：确认演示文稿的页数范围
4. **特殊要求**（可选）：Logo、指标数据等

### 确认页眉页脚风格

**必须在生成前与用户确认**，使用 `vscode_askQuestions` 工具提问，提供两个选项：

| 选项 | 说明 | 适用场景 |
|------|------|----------|
| **公司品牌模板** | 页眉：左侧渐变圆点 + 标题，右侧 SWO / 微钉双品牌 Logo；页脚：左 "SoftwareOne \| 微钉科技"，右页码胶囊 | 对外商务演示、客户提案、正式交付 |
| **AI 自动设计** | AI 根据 PPT 主题和内容自动决定页眉页脚的图标、品牌名和排版风格 | 内部分享、读书会、技术沙龙、个人演示等非品牌场景 |

选择"公司品牌模板"时，使用 Step 1.5 中定义的 Logo 和页脚规范；选择"AI 自动设计"时，AI 根据内容主题自行设计页眉标识（如书名缩写、主题 icon 等）和页脚文字，但仍遵循相同的布局结构和字号规范。

#### 公司品牌模板 Logo 素材

品牌素材位于 `.claude/skills/doa-ppt/brand-assets/`，生成 PPT 时需复制到 `output/<项目名>/ppt_softwareonemedlasoft_assets/`：

| 文件名 | 用途 |
|--------|------|
| `SoftwareOne.png` | SoftwareOne Logo（黑色，通用于封面/内容页/结尾页） |
| `Medaslsoft.png` | 微钉科技 Logo（彩色，含中英文图标，通用于封面/内容页/结尾页） |
| `Medaslsoft_Sample.png` | 微钉小图标（仅 icon，用于目录页和内容页标题左侧的 `.header-dot`） |

CSS 引用方式（统一用 `background: url(...) center/contain no-repeat`）：
- **页标题左侧图标**：`.header-dot` → `Medaslsoft_Sample.png`（32×32px，替代原来的渐变圆点）
- **封面**：`.cover-logo-swo` → `SoftwareOne.png`，`.cover-logo-medalsoft` → `Medaslsoft.png`
- **内容页页眉右侧**：`.header-logo-swo` → `SoftwareOne.png`，`.header-logo-medalsoft` → `Medaslsoft.png`
- **结尾页**：`.ending-logo-swo` → `SoftwareOne.png`，`.ending-logo-medalsoft` → `Medaslsoft.png`

### 确认 PPT 规模

**必须在生成前与用户确认**，使用 `vscode_askQuestions` 工具提问：

| 规模 | 页数 | 适用场景 | 内容深度 |
|------|------|----------|----------|
| **单页精华版** | 1 页 | 一页纸汇报、功能速览、电梯演讲 | 核心卖点 + 关键指标 |
| **标准版** | 7-12 页 | 产品介绍、项目汇报、方案评审 | 封面 + 概览 + 功能详解 + 架构 + 数据 + 总结 |
| **完整版** | 17-23 页 | 正式提案、年度汇报、深度技术方案 | 全面覆盖背景、现状、方案、细节、规划、附录 |

## Step 1.5: 默认模板 — 公司模板（唯一模板）

所有 PPT 统一使用公司模板，不做主题选择。此模板来源于 DOA-WorkCopilot Skill 产品介绍 PPT 的实际设计成果。

#### 视觉方向

- **整体气质**：科技感 + 柔和感，紫蓝色系为主调，通过大面积薰衣草渐变底色营造精致氛围
- **核心视觉元素**：3D 紫色球体 + 轨道环 + 旋转玻璃菱形，贯穿封面、章节页和结尾页，形成统一视觉母题
- **配色风格**：不走深色系，全程使用浅紫灰渐变底色（`#EDE5F8 → #CDD3EC`），保持明亮通透
- **装饰克制**：内容页只用极轻的 `deco-circle` 渐变圆点缀右上角，不与内容争夺视线

#### 配色体系

| 用途 | 变量 | 色值 |
|------|------|------|
| 主色 | `--primary` | `#4C78FF` |
| 主色深 | `--primary-dark` | `#3B32D4` |
| 主色浅 | `--primary-soft` | `#EEF1FF` |
| 辅助青 | `--accent` | `#46B6FF` |
| 品牌紫 | `--purple` | `#9D6BFF` |
| 品牌橙 | `--amber` | `#F2B27C` |
| 品牌粉 | `--red` | `#F062C0` |
| 品牌绿 | `--green` | `#58BFC8` |
| 文字主色 | `--text-primary` | `#1E1842` |
| 文字次色 | `--text-secondary` | `#4A4567` |
| 文字辅助 | `--text-muted` | `#7D78A0` |
| 边框 | `--border` | `rgba(141, 136, 208, 0.24)` |

#### 页面级背景策略

| 页面类型 | 背景 |
|----------|------|
| **HTML body 背景**（浏览器预览区） | `linear-gradient(135deg, #EDE5F8 0%, #DDD8F0 30%, #D5D6EE 60%, #CDD3EC 100%)` |
| **所有幻灯片统一底色** | `linear-gradient(90deg, #EDE5F8 0%, #DDD8F0 35%, #D5D6EE 65%, #CDD3EC 100%)` |
| **底部色条** | `linear-gradient(90deg, var(--accent), var(--primary), var(--purple), var(--red))` |

> **硬性要求**：`body` 背景色禁止使用深色（如 `#1a1a2e`），必须使用浅紫到浅蓝的渐变色，与幻灯片底色保持视觉一致。公司模板不在页面间做深浅分层，所有页面使用同一底色。通过"球体+玻璃"装饰强度区分页面类型。

#### 核心装饰母题：紫色球体 + 轨道环 + 玻璃菱形

三类页面（封面、章节页、结尾页）共享同一组视觉元素，通过位置和大小变化营造统一感：

**球体**（3D 渐变紫色圆球）：
```css
background: radial-gradient(circle at 38% 32%, #A480F0, #6535D9 55%, #4520B0);
box-shadow: 0 28px 80px rgba(91,48,215,.35);
```

**轨道环**（两层同心圆细线）：
```css
border: 1px solid rgba(180,175,210,.3);   /* 内环 */
border: 1px solid rgba(180,175,210,.18);  /* 外环，更淡 */
```

**玻璃矩形**（旋转 50° 的毛玻璃矩形，带左侧渐变边线）：
```css
background: linear-gradient(160deg, rgba(255,255,255,.48), rgba(245,240,255,.25), rgba(230,220,250,.10));
border: 1.5px solid rgba(255,255,255,.50);
backdrop-filter: blur(14px);
transform: rotate(50deg);
border-radius: 24px;
```
```css
/* 左侧渐变边线 */
.cover-glass1::before {
  content:''; position:absolute; top:20px; bottom:20px; left:-2px;
  width:3px; border-radius:99px;
  background:linear-gradient(180deg, #9D6BFF, #6BB8FF);
}
```

**装饰圆点**（三种颜色点缀）：
- 蓝色：`linear-gradient(135deg, #6BB8FF, #46B6FF)`
- 粉色：`linear-gradient(135deg, #FF6BA0, #FF4081)`
- 紫色：`radial-gradient(circle at 35% 30%, #C4A0FA, #7E50DE 80%)`

**斜切装饰线**（极淡渐变线）：
```css
background: linear-gradient(90deg, transparent, rgba(76,120,255,.15), rgba(157,107,255,.20));
transform: rotate(-30deg);
```

#### 封面页规范

- **布局**：左侧文字（标题+副标题+作者），右侧球体+轨道环+毛玻璃矩形
- **左侧对齐规则（强制）**：Logo、标题内容、底部信息三者左侧必须对齐
  - `.cover-logo { left: 28px }` — Logo 紧靠左侧
  - `.cover-content { padding: 0 48px }` — 标题/副标题/作者信息
  - `.cover-bottom { left: 48px }` — 底部网址和品牌名
- **球体**：460×460px，`right:130px; top:60px`，`z-index:3`
  ```css
  background: radial-gradient(circle at 38% 32%, #B898FA, #8050F0 40%, #6030D8 65%, #4A20C0);
  box-shadow: 0 32px 90px rgba(91,48,215,.28);
  ```
- **轨道环**：两层，`z-index:1`
  - 内环：560×560px，`right:130px; top:40px`，`border: 1px solid rgba(180,175,210,.25)`
  - 外环：660×660px，`right:80px; top:-10px`，`border: 1px solid rgba(180,175,210,.15)`
- **毛玻璃矩形**：560×780px，`rotate(50deg)`，`right:50px; top:300px`，`z-index:4`（在球体前面，半透明覆盖）
  ```css
  background: linear-gradient(160deg, rgba(255,255,255,.48), rgba(245,240,255,.25), rgba(230,220,250,.10));
  border: 1.5px solid rgba(255,255,255,.50);
  backdrop-filter: blur(14px);
  border-radius: 24px;
  ```
- **毛玻璃渐变边线**：左侧竖向紫蓝渐变线（`::before` 伪元素）
  ```css
  .cover-glass1::before { position:absolute; top:20px; bottom:20px; left:-2px; width:3px; border-radius:99px; background:linear-gradient(180deg, #9D6BFF, #6BB8FF); }
  ```
- **装饰圆点**：三个（非四个），各有独特位置
  - 蓝色（22px）：`left:130px; top:140px`，在左侧空白区
  - 粉色（20px）：`right:580px; top:130px`，在轨道环上
  - 紫色（32px）：`left:-6px; top:380px`，半隐藏在页面左边缘
- **× 装饰符号**：`right:50px; top:60px`，18px 淡紫色，`z-index:5`
- **斜切装饰线**：`width:900px; rotate(-25deg); left:-100px; bottom:60px`
- **标题字体**：52px/900 weight，渐变色（`--primary-dark → --primary → --red`）
- **子标题**：36px，用第二渐变（`--purple → --accent → --green`）
- **Logo**：左上方双品牌 Logo，`top:32px; left:28px`，`z-index:5`
- **底部**：`bottom:24px; left:48px; right:48px`，左侧网址链接，右侧 "Medalsoft"

```html
<div class="slide cover active" data-index="0">
  <div class="cover-ring-o2"></div>
  <div class="cover-ring-o1"></div>
  <div class="cover-glass1"></div>
  <div class="cover-sphere"></div>
  <div class="cover-dot1"></div><div class="cover-dot2"></div><div class="cover-dot3"></div>
  <div class="cover-x">×</div>
  <div class="cover-line"></div>
  <div class="cover-content">
    <div class="cover-logo">...</div>
    <div class="cover-title">产品名称<br><span>子标题</span></div>
    <div class="cover-subtitle">描述文字</div>
    <div class="cover-meta">作者 · 公司 · 日期</div>
  </div>
  <div class="cover-bottom"><a href="#">www.medalsoft.com</a><span>Medalsoft</span></div>
</div>
```

#### 章节分隔页规范（标题页）

> **章节分隔页是 PPT 必备页面类型，每个主要章节前必须有一张。球体 + 轨道环 + 毛玻璃面板三要素缺一不可。**

> **目录条目与章节分隔页 1:1 对应（强制）**：目录页有 N 个条目，就必须有 N 个章节分隔页。例如目录 8 个条目编号 1-8，则必须有 8 个分隔页（sd-num 为 01-08），每个分隔页的标题必须与目录中对应条目的标题一致。不允许"只给部分章节加分隔页"——这会让读者在翻页时失去节奏感。

- **布局**：球体居左偏中，毛玻璃面板右侧延伸，页码数字叠加在球体上
- **球体**：280×280px，`left:210px; top:220px`
- **轨道环**：两层（380px / 460px）
- **毛玻璃面板**（必须还原）：`width:fit-content`，`padding-left:160px; padding-right:50px`
  ```css
  .sd-glass {
    background: linear-gradient(155deg, rgba(255,255,255,.46), rgba(210,200,240,.12));
    border: 1px solid rgba(255,255,255,.50);
    backdrop-filter: blur(6px);
    border-radius: 24px;
  }
  ```
- **页码数字**：92px 白色斜体（Inter），叠在球体中心
- **章节标题**：36px/800 weight，深紫色 `#2E1A6E`
- **不显示底部色条**：`.slide.section-divider::after { display:none; }`
- **编号必须与目录页一致（强制）**：章节分隔页的 `.sd-num` 数字必须等于目录页中对应条目的序号。例如目录第 2 项“认知革命”，则该章节分隔页显示 `02`，而不是独立从 `01` 开始计数。目录页描述文字也必须与对应内容页的标题一致，不得出现通用词糊弄。

```html
<div class="slide section-divider">
  <div class="sd-ring r2"></div>
  <div class="sd-ring r1"></div>
  <div class="sd-sphere"></div>
  <div class="sd-num">01</div>
  <div class="sd-glass"><div class="sd-glass-title">章节标题</div></div>
  <div class="sd-dot pink"></div>
  <div class="sd-dot purple"></div>
  <div class="sd-dot blue"></div>
</div>
```

#### 结尾页规范

- **布局**：封面的镜像 — 球体在左侧，大字 "THANK YOU" 在右侧
- **Logo**：左上方双品牌 Logo，`top:32px; left:28px`（与封面完全一致），`z-index:5`
- **球体**：440×440px，`left:50px; top:100px`，`z-index:3`
  ```css
  background: radial-gradient(circle at 38% 32%, #B898FA, #8050F0 40%, #6030D8 65%, #4A20C0);
  box-shadow: 0 32px 90px rgba(91,48,215,.28);
  ```
- **轨道环**：两层，`z-index:1`
  - 内环：560×560px，`left:-10px; top:40px`，`border: 1px solid rgba(180,175,210,.25)`
  - 外环：660×660px，`left:-60px; top:-10px`，`border: 1px solid rgba(180,175,210,.15)`
- **毛玻璃矩形**：1100×600px，`rotate(28deg)`，`left:450px; top:60px`，`z-index:4`（在球体上面）
  - **与封面的关键差异**：结尾页的毛玻璃矩形更宽更扁、角度更缓（28° vs 封面 50°），覆盖右半区域直到右下角
  - **无上方边框**，只有底部渐变色条（`::after` 伪元素）
  - **无左侧渐变边线**（`::before` 隐藏）
  ```css
  .ending-glass {
    width: 1100px; height: 600px;
    background: linear-gradient(160deg, rgba(255,255,255,.48), rgba(245,240,255,.25), rgba(230,220,250,.10));
    border: none;
    backdrop-filter: blur(10px);
    transform: rotate(28deg);
    border-radius: 0 0 24px 24px;
    overflow: hidden;
  }
  /* 左侧渐变边线隐藏 */
  .ending-glass::before { display: none; }
  /* 底部渐变色条（粉→紫→蓝） */
  .ending-glass::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #E95BC2, #8050F0, #3DA5FF);
    border-radius: 0 0 24px 24px;
  }
  ```
- **装饰圆点**：两个
  - 粉色（24px）：`left:50px; top:100px`，在 Logo 下方
  - 蓝色（18px）：`right:60px; top:140px`，在右侧
- **× 装饰符号**：`right:50px; top:60px`，18px 淡紫色
- **斜切装饰线**：`width:1000px; rotate(-25deg); left:0px; bottom:60px`
- **"THANK YOU"**：108px/900 weight，渐变从粉到紫（`linear-gradient(180deg, #E95BC2, #3F2FD7)`），居右
- **底部**：`bottom:24px; left:48px; right:48px`，左侧 "Medalsoft"，右侧日期

```html
<div class="slide ending" data-index="最后">
  <div class="ending-ring2"></div><div class="ending-ring1"></div>
  <div class="ending-glass"></div><div class="ending-sphere"></div>
  <div class="ending-dot-pink"></div><div class="ending-dot-blue"></div>
  <div class="ending-x">×</div>
  <div class="ending-line"></div>
  <div class="ending-logo-area">
    <div class="ending-logo-swo"></div>
    <div class="ending-logo-divider"></div>
    <div class="ending-logo-medalsoft"></div>
  </div>
  <div class="ending-content">
    <div class="ending-copy">
      <div class="ending-title">THANK<br>YOU</div>
    </div>
  </div>
  <div class="ending-bottom"><span>Medalsoft</span><span>日期</span></div>
</div>
```

#### 内容页组件规范

**页眉**：左侧微钉小图标 `Medaslsoft_Sample.png`（32×32px）+ 标题（34px/800），右侧双品牌 Logo。页眉下方 120px 蓝紫渐变色条。

**卡片**：圆角 20px，白色半透明（.94/.84），双层边框 + 柔和阴影，`backdrop-filter:blur(10px)`。

**终端代码块**：深色 `#1A1730`，带红黄绿三色窗口按钮，代码用 `JetBrains Mono`，高亮色：蓝 `#7dd3fc`、绿 `#86efac`、紫 `#c4b5fd`。

**照片框**：圆角 16px，底部渐变遮罩 + 白色说明文字。

**表格**：表头渐变紫 `linear-gradient(135deg, #6D79C8, #7E6ED7)`，白底行，圆角 14px。

**Before/After 对比列**：粉色（Before）vs 青色（After），用 `justify-content:space-evenly` 均匀分布条目。

**提示框**：白色毛玻璃底，左侧 3px 蓝色竖线，圆角 16px。

**流程步骤**：48px 渐变圆球 + 连接线 + 文字标签，颜色从蓝到绿到紫渐变。

**标签 pill**：5 种颜色变体（green/amber/purple/red/blue），圆角 99px。

**页脚**：左 "SoftwareOne | 微钉科技"，右页码（圆角胶囊式，白底紫文字）。

**目录条目（毛玻璃卡片式）**：每个目录项为一张全宽毛玻璃卡片，左侧标题+描述，右侧编号圆球。必须还原毛玻璃效果。

```css
.toc-item {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; padding: 16px 24px;
  background: linear-gradient(155deg, rgba(255,255,255,.46), rgba(210,200,240,.12));
  border: 1px solid rgba(255,255,255,.50);
  backdrop-filter: blur(6px);
  border-radius: 16px;
  transition: all .3s;
}
.toc-item:hover { box-shadow: var(--shadow); transform: translateY(-2px); }
.toc-num {
  width: 44px; height: 44px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--purple));
  color: white; font-size: 16px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(76,120,255,.25);
}
.toc-text { font-size: 18px; font-weight: 700; color: var(--primary-dark); }
.toc-desc { font-size: 14px; color: var(--text-muted); margin-top: 4px; }
```

**目录页推荐结构**（根据条目数量自动选择布局）：

> **布局规则（强制）**：
> - ≤ 5 个条目：单列堆叠布局，`display:flex;flex-direction:column;gap:12px`
> - 6-8 个条目：双列网格布局，`grid-2`，每列 3-4 个条目，每个条目加 `flex:1` 使同列条目等高
> - 超过 8 个：拆分为多个目录页，或精简章节结构
> 
> 禁止在单列布局中塞入超过 5 个条目——必定导致溢出或压缩到无法阅读的尺寸。

```html
<div class="slide" data-index="1">
  <div class="header">
    <div class="header-left"><div class="header-dot"></div><div class="page-title">目录</div></div>
    <div class="header-brand"><span class="logo-text">品牌名</span></div>
  </div>
  <div class="content" style="display:flex;flex-direction:column;gap:12px;padding-top:16px;">
    <div class="toc-item">
      <div><div class="toc-text">章节标题</div><div class="toc-desc">简要描述</div></div>
      <div class="toc-num">1</div>
    </div>
    <!-- 更多条目... -->
  </div>
  <div class="page-footer"><span>品牌名</span><span class="page-no">02 / N</span></div>
</div>
```

> **关键**：`.toc-item` 必须使用 `backdrop-filter: blur(6px)` + 半透明白色渐变背景实现毛玻璃效果，不要用纯白卡片。编号圆球放在右侧（`justify-content: space-between`），而非左侧。

#### 动画规范

- **fadeUp**：从下方 24px 淡入
- **fadeScale**：从下方 12px + 缩放 0.97 淡入
- 封面标题依次入场（delay 0.1s → 0.2s）
- 卡片、终端、照片、提示框统一用 fadeScale 0.5s
- 目录条目依次入场（delay 0.02s 递增 0.06s）
- 章节页球体 fadeScale 0.6s → 数字 fadeUp 0.6s → 玻璃面板 fadeScale 0.6s

#### 实战踩坑要点

1. **玻璃面板宽度用 `fit-content`**：不要固定宽度，自适应标题文字长度，`padding-right:50px` 控制右侧留白
2. **Before/After 列不要用 `<br>` 堆行**：改为 `<div>` + `flex-direction:column; justify-content:space-evenly`，避免底部大片空白
3. **照片与下方提示框之间要留 `margin-top:12px`**：避免紧贴重叠
4. **左右分栏的短列元素加 `flex:1`**：卡片、表格、终端都要 `flex:1` 撑满，避免左右不等高
5. **表格容器要 `display:flex;flex-direction:column`**：让 `<table style="flex:1">` 生效
6. **球体 z-index 层级**：轨道环 z1 → 球体 z3 → 玻璃矩形 z4 → 装饰点/内容 z5
7. **所有页面统一底色**：不分页面类型做深浅差异，只靠装饰元素密度区分

### 各规模推荐页面结构

**单页精华版（1 页）**：
- 标题 + 功能描述 + 特性卡片 + 交互预览 + 关键指标

**标准版（7-12 页）**：
1. 封面（标题 + 副标题 + 日期）
2. 目录 / 议程
3. 背景与痛点
4. 产品/功能概览
5. 核心特性详解（2-4 页，每页 1-2 个特性）
6. 技术架构 / 工作原理
7. 关键数据与成效
8. 路线图 / 下一步计划
9. 总结 / Q&A

**完整版（17-23 页）**：
1. 封面
2. 目录
3. 执行摘要
4. 背景与现状分析（2-3 页）
5. 痛点与需求（1-2 页）
6. 解决方案概览
7. 核心功能详解（4-6 页，每页聚焦一个功能）
8. 技术架构（1-2 页）
9. 交互体验展示（1-2 页）
10. 数据与成效（1-2 页）
11. 案例 / 场景演示
12. 竞品对比 / 优势分析
13. 实施路线图
14. 团队与资源
15. 风险与应对
16. 总结与展望
17. Q&A / 附录

## Step 2: 生成可翻页 HTML 预览

基于收集的需求和确认的规模，使用公司模板生成**一个可左右翻页的 HTML 文件**，模拟幻灯片放映效果。

### 翻页 HTML 结构

**所有页面合并为一个 `slides.html` 文件**，内置翻页交互：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>PPT 预览</title>
  <style>
    /* 主题 CSS 变量（根据选定主题填充） */
    :root { ... }

    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: linear-gradient(135deg, #EDE5F8 0%, #DDD8F0 30%, #D5D6EE 60%, #CDD3EC 100%);
      display: flex; justify-content: center; align-items: center;
      min-height: 100vh; font-family: 'Noto Sans SC', sans-serif;
      overflow: hidden;
    }

    /* 幻灯片容器 */
    .slides-viewport {
      position: relative;
      width: 1280px; height: 720px;
      overflow: hidden; border-radius: 8px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    .slide {
      position: absolute; top: 0; left: 0;
      width: 1280px; height: 720px;
      opacity: 0; transform: translateX(100px);
      transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
      pointer-events: none;
    }
    .slide.active {
      opacity: 1; transform: translateX(0);
      pointer-events: auto;
    }
    .slide.exit-left {
      opacity: 0; transform: translateX(-100px);
    }

    /* 导航控件 */
    .nav-btn {
      position: fixed; top: 50%; transform: translateY(-50%);
      width: 50px; height: 50px; border-radius: 50%;
      background: rgba(255,255,255,0.5); border: none;
      color: #4A4567; font-size: 24px; cursor: pointer;
      backdrop-filter: blur(10px);
      transition: background 0.3s;
      z-index: 100;
    }
    .nav-btn:hover { background: rgba(255,255,255,0.7); }
    .nav-btn.prev { left: 30px; }
    .nav-btn.next { right: 30px; }
    .nav-btn:disabled { opacity: 0.3; cursor: not-allowed; }

    /* 页码指示器 */
    .page-indicator {
      position: fixed; bottom: 30px; left: 50%;
      transform: translateX(-50%);
      display: flex; gap: 8px; z-index: 100;
    }
    .page-dot {
      width: 10px; height: 10px; border-radius: 50%;
      background: rgba(76,120,255,0.25);
      cursor: pointer; transition: all 0.3s;
    }
    .page-dot.active {
      background: #4C78FF; transform: scale(1.3);
    }

    /* 键盘提示 */
    .keyboard-hint {
      position: fixed; bottom: 60px; left: 50%;
      transform: translateX(-50%);
      color: rgba(74,69,103,0.4); font-size: 13px;
    }
      transform: translateX(-50%);
      display: flex; gap: 8px; z-index: 100;
    }
    .page-dot {
      width: 10px; height: 10px; border-radius: 50%;
      background: rgba(76,120,255,0.25);
      cursor: pointer; transition: all 0.3s;
    }
    .page-dot.active {
      background: #4C78FF; transform: scale(1.3);
    }

    /* 键盘提示 */
    .keyboard-hint {
      position: fixed; bottom: 60px; left: 50%;
      transform: translateX(-50%);
      color: rgba(74,69,103,0.4); font-size: 13px;
    }
  </style>
</head>
<body>
  <div class="slides-viewport">
    <div class="slide active" data-index="0">
      <!-- 第 1 页内容 -->
    </div>
    <div class="slide" data-index="1">
      <!-- 第 2 页内容 -->
    </div>
    <!-- ... 更多页面 ... -->
  </div>

  <button class="nav-btn prev" onclick="navigate(-1)">‹</button>
  <button class="nav-btn next" onclick="navigate(1)">›</button>

  <div class="page-indicator">
    <!-- JS 动态生成 -->
  </div>
  <div class="keyboard-hint">← → 方向键翻页 | 点击圆点跳转</div>

  <script>
    let current = 0;
    const slides = document.querySelectorAll('.slide');
    const total = slides.length;
    const indicator = document.querySelector('.page-indicator');
    const prevBtn = document.querySelector('.nav-btn.prev');
    const nextBtn = document.querySelector('.nav-btn.next');

    // 生成页码圆点
    for (let i = 0; i < total; i++) {
      const dot = document.createElement('div');
      dot.className = 'page-dot' + (i === 0 ? ' active' : '');
      dot.onclick = () => goTo(i);
      indicator.appendChild(dot);
    }

    function goTo(index) {
      if (index < 0 || index >= total || index === current) return;
      const dir = index > current ? 1 : -1;
      if (dir > 0) slides[current].classList.add('exit-left');
      slides[current].classList.remove('active');
      current = index;
      slides[current].classList.remove('exit-left');
      slides[current].classList.add('active');
      updateControls();
    }
    function navigate(dir) { goTo(current + dir); }
    function updateControls() {
      prevBtn.disabled = current === 0;
      nextBtn.disabled = current === total - 1;
      document.querySelectorAll('.page-dot').forEach((d, i) =>
        d.className = 'page-dot' + (i === current ? ' active' : '')
      );
    }
    // 键盘导航
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') navigate(-1);
      if (e.key === 'ArrowRight') navigate(1);
    });
    updateControls();
  </script>
</body>
</html>
```

### 每页幻灯片内容结构

每个 `.slide` div 内部是完整的幻灯片内容，与之前的单页 HTML 结构一致。所有页面共享同一套 CSS 变量和样式。

### 设计原则

- **商务简约**：清晰的视觉层次，不过度装饰
- **配色统一**：从选定主题的 CSS 变量体系出发，所有页面风格一致
- **信息密度适中**：标题 + 功能描述 + 特性卡片 + 交互预览 + 指标数据
- **翻页流畅**：CSS 过渡动画，支持键盘 / 点击 / 圆点导航

### 封面与内容页差异化设计准则

#### 封面页：简洁美观

- **极简主义**：封面只保留 Logo、主标题、副标题/日期，不堆砌信息
- **大量留白**：封面的视觉重心靠留白和色彩营造高级感，而非密集排版
- **品牌调性突出**：深色渐变背景 + 品牌色装饰线 + Logo 居中，一眼传达品牌气质
- **文字层级鲜明**：主标题 36-48px 加粗，副标题 16-20px 轻量，不超过 3 层信息

#### 内容页：详实丰富、图文搭配

- **信息密度高**：每页应充分利用版面承载核心观点，避免"一句话占一整页"
- **图文搭配**：纯文字页面占比不超过 30%，优先使用图标、图表、架构图、截图等视觉元素辅助表达
- **数据可视化**：关键指标用数字高亮卡片、进度条、对比图表呈现，而非纯文字罗列
- **案例 + 截图**：技术方案页配架构图，功能页配界面截图或交互示意

#### 图文结合的反 AI 味准则（强制）

> **核心原则：从第一稿开始，每个内容页都必须图文结合，使用真实图片（联网搜索或用户提供），严禁 Emoji 图标，严禁纯文字页面。不要先用 Emoji 占位再让用户修改——第一版就必须到位。**

- **第一稿就必须配图，不允许后期修补**：生成 HTML 的同时就要完成图片搜索/下载/引用，不能先出纯文字版让用户反复要求加图。这是硬性门禁，没有配图的内容页不得交付。
- **每个内容页必须包含至少一张真实图片**：不是装饰，而是承载信息的视觉元素。产品类用界面截图，技术类用架构图/截图，书籍类用封面照，历史类用文物/遗址/古画照片。纯文字卡片堆叠的页面观感极差。
- **数据/表格页也必须有图**：即使是规则表格、对比矩阵等数据密集页面，也要做图文分栏——左侧缩窄表格/数据区，右侧配主题相关的背景图。不允许全宽纯文字表格独占整页。
- **严禁使用 Emoji 作为图标或装饰（从第一稿起）**：不要用 🔥📊🚀💡🛡️ 等 Emoji 充当视觉元素。如需图标效果，使用纯色圆角方块 + 中文单字的 `.icon-bar` 组件：
  ```html
  <div class="icon-bar">
    <span class="ib" style="background:var(--primary);">审</span>
    <span class="ib" style="background:var(--purple);">核</span>
    <span class="ib" style="background:var(--green);">验</span>
  </div>
  ```
  `.ib` 样式：`display:inline-flex; width:28px; height:28px; border-radius:7px; color:#fff; font-size:13px; font-weight:700; align-items:center; justify-content:center;`
- **不要只堆卡片和 bullet**：如果一页全是等宽小卡片 + 抽象文案，AI 味会非常重。至少给关键页加入一张真实截图、业务场景图或结构图。
- **图片要承担信息功能**：图片不是装饰填空。界面优化页用真实界面截图，实施页用流程图/时间轴，问题页用现状截图，对比页用前后对照。
- **单页至少一个视觉主角**：每页应有一个主视觉元素，通常是大图、表格、时间轴、架构图、数据横幅中的一个，而不是所有元素平均铺开。
- **同一张图不要反复滥用**：若素材不足，可复用同类风格图，但不要整套稿件只靠一张图裁来裁去。至少在封面、现状、方案、交付几个阶段使用不同视觉来源。
- **咨询稿结构优先**：推荐采用 `左文右图`、`上图下结论`、`大图 + 侧栏摘要`、`主图 + 底部指标条` 这类结构，避免平均分配成四宫格信息墙。
- **图片与文字的视觉重量要互补**：大图页应减少正文密度；文字多时图片只保留一张主图或局部截图，避免图和字同时抢焦点。

#### 图片素材获取与回退策略（强制）

> **图片是内容页质量的决定性因素，必须主动获取，不能跳过。**

##### 有联网能力时（默认流程）

1. **主动利用联网能力搜索高质量图片**：使用 Tavily/Unsplash/Pexels 等可商用图源，根据 PPT 主题关键词批量搜索相关图片。每个内容页至少配一张，整套 PPT 至少准备 8-15 张不同图片。
2. **图片下载到本地 `images/` 目录**：所有网络图片必须下载到 `output/<项目名>/images/` 目录，HTML 中使用相对路径 `images/xxx.jpg` 引用，不依赖外部 URL。
3. **图片语义匹配**：不要随便拿风景图填技术页。书籍类用封面/作者/场景照，历史类用文物/遗址/古画，技术类用架构截图/产品界面，商务类用办公/团队/数据可视化照片。
4. **下载失败立即换源**：Wikimedia 缩略图限制较多（400 错误常见），优先使用 Unsplash（`https://images.unsplash.com/photo-xxx?w=800`），备选 Pexels。某张图 404 时立即换另一张同主题图，不要阻塞流程。
5. **图片尺寸建议**：宽度 600-1200px 即可，不需要超高清。JPG 格式优先，单张控制在 50-250KB。

##### 无联网能力时（回退流程）

1. **立即告知用户**：明确提示"当前环境无法联网下载图片，请您手动收集相关图片放入 `output/<项目名>/images/` 文件夹"。
2. **提供图片清单**：列出每页需要的图片主题和建议文件名，如：
   ```
   images/cover.jpg      — 书籍封面或主题封面照
   images/scene_01.jpg   — 第一章节主题配图
   images/scene_02.jpg   — 第二章节主题配图
   ...
   ```
3. **先生成 HTML 框架**：即使图片暂缺，也先生成完整 HTML，图片位置用 placeholder 占位（灰色背景 + 文字提示），等用户补图后自动显示。
4. **用户补图后再做最终检查**：图片到位后重新在浏览器中检查每页渲染效果。

##### 通用规则

- **优先级顺序**：本地截图 / 项目现状图 / 品牌资产 / 用户提供图片 / 可商用网络图片。
- **本地素材也要讲语义**：即便只能使用本地截图，也要按"现状页、方案页、交付页"分别选图，不能随便拿一张图填所有页面。
- **禁止为补图而破坏版权边界**：仅使用用户提供、本地已有、品牌资产或可明确商用的图片来源（Unsplash/Pexels 均为免费商用授权）。

#### 图文分栏布局标准模式（强制）

> **所有内容页必须使用图文分栏布局。不允许任何内容页只有纯文字/纯表格而没有图片。**

内容页标准结构为 **左文右图** flex 分栏：

```html
<div class="content" style="display:flex;gap:20px;align-items:stretch;">
  <!-- 左侧：文字/卡片/表格 -->
  <div style="flex:1;display:flex;flex-direction:column;min-width:0;min-height:0;">
    <!-- 内容区 -->
    <div class="highlight-box" style="margin-top:auto;padding:8px 14px;">
      <p style="font-size:12px;margin:0;"><strong>总结文字</strong></p>
    </div>
  </div>
  <!-- 右侧：图片面板 -->
  <div class="screenshot-panel" style="flex:0 0 340px;overflow:hidden;min-height:0;padding:0;">
    <img src="images/xxx.jpg" style="width:100%;height:100%;object-fit:cover;border-radius:14px;" alt="描述">
  </div>
</div>
```

##### 关键规则

| 项目 | 规则 | 原因 |
|------|------|------|
| **flex 容器** | `display:flex;gap:20px;align-items:stretch` | stretch 让左右等高 |
| **左侧内容区** | `flex:1;display:flex;flex-direction:column;min-width:0;min-height:0` | min-height:0 防止内容撑破容器 |
| **右侧图片面板** | `flex:0 0 300~400px;overflow:hidden;min-height:0;padding:0` | 固定宽度，padding:0 覆盖默认值 |
| **图片样式** | `width:100%;height:100%;object-fit:cover;border-radius:14px` | cover 填满面板，不留白边 |
| **底部摘要** | `margin-top:auto` 推到底部 | 消除中间空白 |

##### 不同页面类型的图片面板宽度建议

| 页面类型 | 图片面板 `flex-basis` | 说明 |
|----------|----------------------|------|
| 常规文字+卡片 | `flex:0 0 400px` | 文字少图片大 |
| 数据表格（单表） | `flex:0 0 340px` | 表格需要更多宽度 |
| 数据表格（双表/密集） | `flex:0 0 300px` | 给表格让出更多空间 |
| 产品截图（精确展示） | `flex:1`（与文字等宽） | 截图需要大面积 |

##### 产品截图 vs 背景配图

| 类型 | 来源 | 用途 | 样式差异 |
|------|------|------|----------|
| **产品截图** | Playwright 截图 + 裁剪 | 精确展示界面功能 | `object-fit:contain`，保留白底，加 `box-shadow` 和 `border` |
| **背景配图** | Unsplash/Pexels 联网下载 | 视觉氛围、主题烘托 | `object-fit:cover`，铺满面板，`padding:0` |

##### 表格页图文分栏示例

数据密集的表格页也必须有图片，做法是缩窄表格列宽 + 减小字号：

```html
<div class="content" style="display:flex;gap:20px;align-items:stretch;">
  <div style="flex:1;display:flex;flex-direction:column;min-width:0;">
    <table class="cmp-table" style="flex:1;font-size:13px;">
      <thead><tr><th style="width:50px;">编号</th><th style="width:120px;">名称</th><th>描述</th><th style="width:70px;">等级</th></tr></thead>
      <tbody><!-- 数据行 --></tbody>
    </table>
    <div class="highlight-box" style="margin-top:auto;padding:8px 14px;">
      <p style="font-size:12px;margin:0;"><strong>总结</strong></p>
    </div>
  </div>
  <div class="screenshot-panel" style="flex:0 0 340px;overflow:hidden;min-height:0;padding:0;">
    <img src="images/bg_theme.jpg" style="width:100%;height:100%;object-fit:cover;border-radius:14px;" alt="主题图">
  </div>
</div>
```

#### 内容间距规范（强制）

> **不同内容块之间必须有可见间距，禁止紧贴在一起。**

| 元素 | 间距规则 | CSS |
|------|----------|-----|
| **表格行间距** | 每行之间留 8px 间距 | `border-spacing: 0 8px;` |
| **卡片之间** | 卡片之间留 12-16px 间距 | `gap: 12px` 或 `gap: 16px` |
| **标题与内容** | 标题下方留 10-12px | `margin-bottom: 10px` |
| **内容与底部摘要** | 自动推到底部 | `margin-top: auto` |
| **左右分栏间隔** | 左侧内容与右侧图片之间 | `gap: 20px` |
| **图文分栏内部** | 左列内部元素之间 | `gap: 10px` |
| **全宽表格 td** | 单元格内边距 | `padding: 14px 16px` |

##### 表格行间距实现

```css
.cmp-table {
  border-spacing: 0 8px;   /* 行间距 8px */
  border-collapse: separate; /* 必须用 separate 才能生效 */
}
.cmp-table td {
  padding: 14px 16px;      /* 单元格内边距 */
}
```

##### 禁止的紧凑写法

- **禁止** `border-spacing: 0` 或 `border-collapse: collapse` 导致行间无间距
- **禁止** 卡片之间 `gap: 0` 或无 gap 导致卡片紧贴
- **禁止** 多个 `highlight-box` 或提示框之间无 margin 导致视觉糊在一起

#### 多元素对称与布局规范

- **网格对齐**：多卡片/多模块布局必须基于网格系统，保证等宽、等高、等间距
- **偶数列优先**：2 列、4 列布局天然对称；3 列时确保中间列居中，左右等距
- **视觉重量平衡**：左右分栏时，文字侧与图片侧视觉重量应大致相当（文字多则配大图，文字少则配小图 + 留白）
- **垂直节奏统一**：同一页内所有卡片顶部对齐、底部对齐，标题到内容的间距一致
- **重复元素模板化**：同类卡片（如特性卡片、步骤卡片）必须使用完全相同的尺寸、圆角、阴影和内边距
- **奇数元素处理**：当出现 3/5/7 个元素时，优先考虑拆行（如 3+2、4+3）或用留白/装饰块补位，避免末行孤立元素靠左

### 硬性版式约束

- **不得超出页面边界**：任何标题、正文、图表、卡片、页码、页脚、装饰元素都不能溢出 `1280×720` 幻灯片安全区域
- **左右分栏必须等高对齐**：所有使用 `.grid-2` 的内容页，左右两列底部必须对齐，禁止出现一侧比另一侧短、底部留有大片空白的情况。通过 `flex:1` 让卡片/表格自动拉伸填满
- **优先缩内容，不挤边界**：若内容放不下，优先精简文案、拆分页面、减少卡片数量或降低局部字号，不允许为了塞内容而越出边界
- **保留安全边距**：正文和关键组件应默认保留至少 24-40px 的可视边距，避免贴边或在截图/PPT中被裁切
- **生成后必须检查越界**：如果预览中出现裁切、遮挡、重叠、贴边或翻页控件覆盖正文，必须先调整版式再继续导出 PPT

### 推荐布局结构

**每页 HTML 尺寸固定**：`width: 1280px; height: 720px`（16:9）

#### 封面页布局
```
┌─────────────────────────────────────────────┐
│  [SWO Logo] | [微钉Logo]    ← 左上角        │
│                         [装饰图] ← 右上角    │
│           主标题（大号加粗渐变）              │
│           副标题                             │
│           补充信息                            │
│                                             │
└─────────────────────────────────────────────┘
```

#### 内容页布局（左右分栏）
```
┌─────────────────────────────────────────────┐
│ ● 页面标题           [SWO Logo]|[微钉Logo]  │
│ ────                                        │
│  左侧（文字描述 + 卡片）  │  右侧（图/预览）  │
│  ← flex:1 等高拉伸 →     │ ← flex:1 等高 →  │
│─────────────────────────────────────────────│
│  SoftwareOne | 微钉科技            02 / 20  │
└─────────────────────────────────────────────┘
```

#### 内容页布局（全宽）
```
┌─────────────────────────────────────────────┐
│ ● 页面标题           [SWO Logo]|[微钉Logo]  │
│ ────                                        │
│  3-4 列并排卡片 / 流程图 / 架构图            │
│                                             │
│─────────────────────────────────────────────│
│  SoftwareOne | 微钉科技            03 / 20  │
└─────────────────────────────────────────────┘
```

#### 总结页 / Q&A 页布局
```
┌─────────────────────────────────────────────┐
│                [装饰图] ← 右上角             │
│     [SWO Logo] | [微钉Logo]                 │
│           产品名称                           │
│           副标题描述                          │
│      [数据统计卡片] (可选)                   │
│           Thank You & Q&A                   │
└─────────────────────────────────────────────┘
```

### 多页 PPT 的设计一致性

- 所有页面共享同一套 CSS 变量（配色体系）
- Header 区域（Logo + 页标题）位置保持一致
- 页脚区域风格统一（可加页码）
- 每页使用相同的字体大小层级（页面主标题 34px，卡片标题 18-20px，正文 17px，辅助/标签 15px）
- **最小字体硬性下限 15px**：整个 PPT 中任何可见文字（含页脚、标签、图片说明）不得小于 15px。禁止使用 10-14px 等小字号——在投影仪上完全无法阅读
- 卡片正文使用 `font-size: 17px; line-height: 1.7`，确保在 1280×720 画布和投影场景下清晰可读
- 优先通过精简文案来适配版面，而不是缩小字号塞更多内容

### HTML 技术要点

- 使用 Google Fonts（`Noto Sans SC` 中文 + 一款英文字体）
- CSS 变量定义配色体系（`--primary`, `--primary-light`, `--accent` 等）
- Flexbox/Grid 布局，固定 `width: 1280px; min-height: 720px`
- 卡片组件带 `border-left` 色条、圆角、轻阴影
- 渐变色仅用于装饰横幅，正文区域保持纯色

### 交付物

- 生成一个 `slides.html` 文件（内置翻页交互，所有幻灯片在同一个文件中）

保存到用户工作目录，提示用户在浏览器中预览，根据反馈迭代调整。

### HTML 预览后的强制门禁

- **必须先逐页检查边界**：生成 `slides.html` 后，必须逐页检查每一页是否存在越界、裁切、遮挡、重叠、贴边或导航控件压住正文的问题
- **检查不通过不得生成 PPT**：只要任意一页存在版式问题，必须先修改 HTML 并重新检查，直到全部页面通过为止
- **用户修改 HTML 后不得自动继续导出**：如果用户要求“修改这个 HTML / 调整这几页 / 优化版式”，完成修改后只能停在 HTML 预览确认阶段，不能直接继续生成 PPT
- **必须等待用户明确确认**：只有当用户明确表达“HTML 没问题了 / 可以生成 PPT / 按这个版本导出”这类确认后，才允许进入 PPT 生成步骤
- **禁止默认代替用户确认**：即使边界检查通过，也不能把“看起来没问题”当成用户确认

### HTML 检查清单

逐页至少检查以下项目：

1. 标题、副标题、正文、卡片、图表、页码、页脚都在 `1280×720` 安全区域内
2. 底部 footer、页码、导航按钮不会被内容挤出画布
3. 左右分栏、网格卡片、时间线、流程块之间无重叠
4. **左右分栏 (.grid-2) 两列底部必须对齐**，不得出现一侧短、另一侧留有大片空白的情况
5. 关键正文与边缘至少保留安全边距，不出现明显贴边
6. 翻页控件、页码圆点、键盘提示不会遮挡正文内容

如果任一项不满足，返回 HTML 调整步骤，不得继续生成 PPT

## Step 3: 用户确认 HTML 后，选择 PPT 生成模式

只有在同时满足以下两个条件后，才允许进入此步骤：

1. HTML 已完成逐页边界与版式检查，确认没有越界或遮挡问题
2. 用户已明确确认当前 HTML 内容和版式没有问题，可以开始生成 PPT

进入此步骤前，使用 `vscode_askQuestions` 或用户明确文本确认，拿到类似以下结论之一：

- `按当前 HTML 生成 PPT`
- `HTML 没问题，可以导出`
- `就用这个版本生成`

拿到确认后，再使用 `vscode_askQuestions` 工具让用户选择导出格式和模式：

#### 导出格式选择

使用 `vscode_askQuestions` 让用户选择输出格式：

| 格式 | 说明 | 适用场景 |
|------|------|----------|
| **PPTX**（默认推荐） | 生成 .pptx 演示文稿 | 需要在 PowerPoint 中放映或编辑 |
| **PDF** | 生成 .pdf 文档 | 只读分发、邮件附件、打印 |
| **都要** | 同时生成 .pptx 和 .pdf | 既要放映也要分发 |

#### PPT 生成模式选择（仅 PPTX 格式时）

**默认推荐：截图高保真 PPT。**
只有在用户明确要求“后续需要在 PowerPoint 里继续改字、改布局、改单页内容”时，才优先选择可编辑模式。

| 模式 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| **截图高保真模式** | 将每页 HTML 截图为图片插入 PPT | 还原度 100%，与 HTML 完全一致，最适合作为默认推荐 | 内容不可编辑，文件体积较大 |
| **可编辑模式** | python-pptx 逐元素重建 | 文字/形状均可编辑，灵活修改 | 还原度约 85-90%，复杂布局可能有偏差 |

#### 导出模式切换规则（新增）

1. 同一轮会话内，用户若改口“还是要不可编辑高清 PPT”，应立即从可编辑链路切回截图高保真链路。
2. 切换模式后不复用对方输出文件名，必须生成新的目标文件并保留历史版本。
3. 对外反馈时必须明确告知本次产物属于哪种模式（可编辑 / 高保真），避免用户误判可改性。

### 模式 A: 截图高保真 PPT（默认推荐，HTML → 截图 → 插入）

将每页 HTML 幻灯片截图为高清图片，再逐张插入 PPT 作为全页背景图。

#### 截图转换参考模板

读取 [references/screenshot-pptx-template.py](references/screenshot-pptx-template.py) 获取完整的截图转 PPT 脚本模板。

该模板包含：
- `capture_slides()` — Playwright 逐页截图（2x 高清）
- `build_pptx()` — 截图插入 PPT 全屏背景
- `auto_detect_total()` — 自动检测 HTML 中幻灯片总数
- CONFIG 区域只需修改 `HTML_FILE` 和 `OUTPUT_PPTX` 路径即可运行

#### 截图时隐藏导航控件（强制要求）

不管输出 PPTX 还是 PDF，只要使用截图方式，**必须在截图前通过 JS 隐藏所有导航控件**（左右箭头、页码圆点、键盘提示），避免遮挡幻灯片内容：

```javascript
// 在页面加载完成后、开始截图前执行
document.querySelectorAll('.nav-btn, .page-indicator, .keyboard-hint')
    .forEach(el => el.style.display = 'none');
```

模板脚本 `screenshot-pptx-template.py` 已内置此逻辑。自定义脚本也必须包含此步骤。

#### 截图高保真执行步骤

前置条件：HTML 已逐页检查通过，且用户已明确确认可导出。

1. 确认依赖已安装：`pip install python-pptx playwright`，然后 `playwright install chromium`
2. 复制模板脚本，修改 CONFIG 中的文件路径
3. 运行脚本生成 .pptx 文件
4. 告知用户输出路径

### 模式 B: 可编辑 PPT（用户明确要求可修改时，python-pptx 转换）

使用 `python-pptx` 库将 HTML 内容逐元素映射为 PPT 原生对象。

### 转换参考模板

读取 [references/pptx-converter-template.py](references/pptx-converter-template.py) 获取完整的可编辑 PPT 转换脚本模板和工具函数库。

该模板包含：
- 颜色常量定义模式
- `add_rounded_rect()` — 圆角矩形（支持圆角半径调整）
- `add_text_box()` — 文本框（支持字体、颜色、对齐、垂直锚点）
- `add_multiline_text()` — 多行文本段落
- `add_rich_paragraph()` — 富文本（多 run，混合粗体/颜色）
- `add_circle()` — 圆形形状
- `set_slide_bg()` — 幻灯片背景色

### PPT 生成要点

1. **幻灯片尺寸**：`Inches(13.333) × Inches(7.5)`（16:9 宽屏）
2. **使用 blank layout**：`prs.slide_layouts[6]`
3. **字体统一为 `Microsoft YaHei`**（PPT 中不依赖 Google Fonts）
4. **颜色不用渐变**：python-pptx 中渐变配置复杂，改用纯色近似
5. **圆角矩形**：通过 `a:avLst` 的 `adj` 值控制圆角半径
6. **富文本**：单个文本框内用多个 `run` 实现粗体/颜色混排
7. **垂直居中**：通过设置 `bodyPr` 的 `anchor='ctr'` 实现

### 执行步骤

前置条件：HTML 已逐页检查通过，且用户已明确确认可导出。

1. 确认 `python-pptx` 已安装：`pip install python-pptx`
2. 基于模板生成定制化 Python 脚本
   - 单页版：一个函数构建一页 slide
   - 多页版：每页一个 `build_slideN()` 函数，共享颜色常量和工具函数，主函数循环调用
3. 运行脚本生成 .pptx 文件
4. 告知用户输出路径

### 模式 C: 截图高保真 PDF（HTML → 截图 → 合并 PDF）

将每页 HTML 幻灯片截图为高清图片，再使用 reportlab 合并为 PDF 文档。

#### PDF 导出执行步骤

前置条件：HTML 已逐页检查通过，且用户已明确确认可导出。

1. 确认依赖已安装：`pip install playwright reportlab`，然后 `playwright install chromium`
2. 截图流程与模式 A 完全相同（包括隐藏导航控件）
3. 使用 Pillow 或 reportlab 将截图合并为 PDF：

```python
# 方式 A：Pillow（最简洁，推荐）
from PIL import Image
images = [Image.open(s).convert('RGB') for s in screenshots]
images[0].save(output_pdf, save_all=True, append_images=images[1:], resolution=144.0)

# 方式 B：reportlab（精确控制页面尺寸）
from reportlab.pdfgen import canvas
page_w = VIEWPORT_W * DEVICE_SCALE  # 2560
page_h = VIEWPORT_H * DEVICE_SCALE  # 1440
c = canvas.Canvas(output_pdf, pagesize=(page_w, page_h))
for img_path in screenshots:
    c.drawImage(img_path, 0, 0, width=page_w, height=page_h)
    c.showPage()
c.save()
```

4. 告知用户输出路径

> **两种方式均可**：Pillow 方式代码最简但页面尺寸由图片分辨率决定；reportlab 方式可精确控制 PDF 页面尺寸。如果同时导出 PPTX + PDF，截图只需做一次，分别喂给两个构建函数。

### 元素映射关系（HTML → PPT，仅可编辑模式）

| HTML 元素 | PPT 实现 |
|-----------|----------|
| 渐变背景 | 纯色 `RGBColor` 近似 |
| `border-left` 色条 | `MSO_SHAPE.RECTANGLE` 窄矩形 |
| 圆角卡片 | `MSO_SHAPE.ROUNDED_RECTANGLE` + `avLst` |
| 图标 emoji | `add_text_box()` 文本框放 emoji |
| 富文本（粗体/链接色） | 多个 `run` 设置不同 `font` 属性 |
| 输入框 | 圆角矩形 + 文本框叠加 |
| 分隔线 | 极窄矩形 `height=Pt(1.5)` |
| 圆形头像/状态点 | `MSO_SHAPE.OVAL` |
| 底部指标横幅 | 圆角矩形 + 居中文本框 |
