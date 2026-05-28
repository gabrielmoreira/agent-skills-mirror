---
name: doa-ppt
description: >
  Use when generating or refining business PPT decks, product introductions, technical proposals,
  project reports, multi-page HTML slide previews, HTML-to-PPT export, or turning source material
  such as PDFs, screenshots, notes, and reference docs into a polished presentation. Do not use
  for standalone web pages or web apps.
---

# HTML to PPTX — 商务演示文稿生成

## 工作流概览

```
用户输入（描述 + 参考图）
  → 确认PPT规模
  → 智能推荐主题配色（用户可选）
  → 生成可翻页 HTML 预览
  → 逐页检查 HTML 是否越界/裁切/重叠
  → 用户确认/调整 HTML
  → 只有用户明确确认 HTML 无问题后，才进入 PPT 模式选择
  → 默认推荐截图高保真模式（用户如需二次编辑再切换到可编辑）
  → 生成 PPT
```

## 本次实战经验固化

当用户提供 PDF、截图、既有 HTML 或已有 PPT，并要求“基于这个继续生成 / 整合 / 扩展 / 转 PPT”时，必须先把资料链路整理清楚，再改版式。

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
- 每次新增 layout class 后，要检查它是否覆盖 `.content{height:590px}`。如果直接把 `.grid-*` 用在 `.content` 上，必须补 `.content.grid-*{height:590px}` 防止内容压到 footer。
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

> **强制规则：所有使用 `.grid-2` 左右分栏的内容页，左右两列必须等高对齐，底部齐平。这是不可协商的硬性要求。**

- **`.grid-2 { align-items: stretch }` 只拉伸直接子元素**：grid 子 div 会被拉伸到等高，但内部元素（表格、卡片）不会自动填满。
- **必须在 grid 子 div 上加 `display:flex; flex-direction:column`**：让内部元素参与 flex 布局。
- **需要填满高度的元素加 `flex:1`**：表格用 `style="flex:1"` 填满剩余高度；多张卡片用 `flex:1` 让每张卡片等分空间。
- **左右卡片数量不对等时，少的一侧每张卡片必须加 `flex:1`**：例如左 3 卡片、右 2 卡片，右侧每张卡片必须加 `flex:1` 使其自动拉伸填满。禁止出现一侧比另一侧短、底部有大段空白的情况。
- **左右分栏的父容器必须填满内容区**：`.content` 加 `display:flex;flex-direction:column`，`.grid-2` 加 `flex:1` 或 `style="height:100%"`，确保 grid 占满内容区而非只占内容自然高度。
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
- **内容区高度最大化**：`.content { padding: 20px 56px 14px; height: 590px }` 而非旧值 `40px/32px/548px`，可用面积增加约 17%。
- **`font-size:10px` 全局提升为 11px**：在 `</style>` 前追加 `.content *[style*="font-size:10px"]:not(.step-num):not(.arch-box) { font-size: 11px !important; }`，避免内容页字号过小而浪费视觉空间。
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

### PDF 导出踩坑记录

- **Pillow `Image.save(save_all=True)` 可用于简单场景**：将截图 PNG 合并为多页 PDF，代码最简洁，适合截图高保真模式。需要 `convert('RGB')` 去掉 alpha 通道。
- **reportlab 适合需要自定义页面尺寸的场景**：如果 PDF 页面尺寸需要精确控制（如匹配 2x 截图分辨率 2560×1440），使用 reportlab。
- **同时导出 PPTX + PDF 时，共享截图**：截图只做一次，分别喂给 `build_pptx()` 和 `build_pdf()` 两个函数，避免重复截图。

### 导出后的强制校验

截图高保真 PPT 生成后，必须验证：

1. `.pptx` 文件存在
2. `Presentation(...).slides` 页数等于 HTML 中 `.slide` 数量
3. `ppt/media/image*.png` 数量等于页数
4. 首页截图尺寸是 `1280×720`
5. 若封面应为深色/有色背景，检查首页或封面页的平均 RGB，避免背景丢失变白
6. 如果封面被挪到其他页，校验对应媒体图，而不是只校验 `image1.png`

## Step 1: 收集需求

向用户收集以下信息：

1. **业务功能描述**：产品/功能的核心卖点、关键特性、目标用户
2. **参考图**（可选）：用于提取配色方案和视觉风格
3. **PPT 规模**（必选）：确认演示文稿的页数范围
4. **特殊要求**（可选）：品牌色、Logo、指标数据等

### 确认 PPT 规模

**必须在生成前与用户确认**，使用 `vscode_askQuestions` 工具提问：

| 规模 | 页数 | 适用场景 | 内容深度 |
|------|------|----------|----------|
| **单页精华版** | 1 页 | 一页纸汇报、功能速览、电梯演讲 | 核心卖点 + 关键指标 |
| **标准版** | 7-12 页 | 产品介绍、项目汇报、方案评审 | 封面 + 概览 + 功能详解 + 架构 + 数据 + 总结 |
| **完整版** | 17-23 页 | 正式提案、年度汇报、深度技术方案 | 全面覆盖背景、现状、方案、细节、规划、附录 |

## Step 1.5: 智能推荐主题

根据用户提供的内容领域和风格偏好，智能推荐合适的主题配色。使用 `vscode_askQuestions` 工具让用户从推荐主题中选择。

### 预设主题库

| 主题名称 | 主色调 | 适用场景 | CSS 变量示例 |
|----------|--------|----------|-------------|
| **自定义品牌** | 用户自定义 | 需要品牌一致性的对外方案、客户交付 | 用户提供色值和 Logo |
| **科技紫光** | `#7C5CFC` 紫色系 | AI/科技/SaaS 产品 | `--primary: #7C5CFC; --bg: #F5F0FF` |
| **商务蓝** | `#2563EB` 蓝色系 | 企业汇报、方案评审、项目管理 | `--primary: #2563EB; --bg: #EFF6FF` |
| **极简黑白** | `#18181B` 灰黑系 | 高端品牌、设计展示、极简汇报 | `--primary: #18181B; --bg: #FAFAFA` |
| **活力橙** | `#EA580C` 橙色系 | 营销推广、创意方案、活动策划 | `--primary: #EA580C; --bg: #FFF7ED` |
| **自然绿** | `#16A34A` 绿色系 | 环保/健康/农业/ESG 报告 | `--primary: #16A34A; --bg: #F0FDF4` |
| **沉稳深色** | `#1E293B` 深色系 | 高管汇报、年度总结、数据大屏风格 | `--primary: #60A5FA; --bg: #0F172A; --text: #E2E8F0` |
| **优雅酒红** | `#9F1239` 酒红系 | 品牌发布、文化/艺术/奢侈品 | `--primary: #9F1239; --bg: #FFF1F2` |
| **清新青色** | `#0891B2` 青色系 | 医疗/教育/公益/政务 | `--primary: #0891B2; --bg: #ECFEFF` |

### 推荐逻辑

根据用户内容中的关键词和行业信号自动推荐 2-3 个最匹配的主题：

- **科技/AI/SaaS/互联网** → 科技紫光、商务蓝、沉稳深色
- **企业/咨询/金融** → 商务蓝、极简黑白、沉稳深色
- **营销/电商/活动** → 活力橙、清新青色、科技紫光
- **医疗/教育/政务** → 清新青色、商务蓝、自然绿
- **品牌/设计/奢侈品** → 优雅酒红、极简黑白、沉稳深色
- **环保/农业/可持续** → 自然绿、清新青色、商务蓝
- **需要品牌一致性/公司内部** → 自定义品牌（用户提供色值和 Logo）

如果用户提供了参考图，**优先从参考图提取配色**，作为自定义主题，同时展示推荐主题供对比选择。

> **快捷触发**：当用户说"用公司模板""用品牌模板"或在 `vscode_askQuestions` 中选择了"自定义品牌"时，跳过通用主题配色流程，直接进入下方"自定义品牌模板"完整注入流程。

### 自定义品牌模板（完整规范）

当用户选择"自定义品牌"主题时，需要用户提供品牌色值和 Logo 文件，然后自动注入以下全部元素。

#### 配色体系

| 用途 | 变量 | 色值 |
|------|------|------|
| 主色 | `--primary` | `#2F80ED` |
| 主色深 | `--primary-dark` | `#1456C8` |
| 主色浅 | `--primary-soft` | `#EEF6FF` |
| 辅助青 | `--accent` | `#35C6F4` |
| 辅助青浅 | `--accent-soft` | `#EAFBFF` |
| 品牌紫 | — | `#9D9AFE` |
| 品牌青绿 | `--neon` | `#89E0D4` |
| 品牌橙 | `--amber` | `#F3A875` |
| 品牌粉 | `--red` | `#FB5387` |
| 绿色 | `--green` | `#20B8A8` |
| 背景灰1 | — | `#F6F8FB` |
| 背景灰2 | — | `#ECEFF1` |
| 边框灰 | `--border` | `rgba(193,199,217,.58)` |
| 文字主色 | `--text-primary` | `#111111` |
| 文字次色 | `--text-secondary` | `#333333` |
| 文字辅助 | `--text-muted` | `#666666` |

#### 品牌资产

以下文件应放在 `ppt_brand_assets/` 目录下（用户需提供自己的品牌素材）：

| 文件 | 用途 | 使用位置 |
|------|------|----------|
| `Home_Logo.png` | 白色 Logo（用于深色背景） | 封面左上角 `.cover-logo-primary` |
| `Home_Logo_Secondary.png` | 白色副品牌 Logo（用于深色背景） | 封面左上角 `.cover-logo-secondary`（可选） |
| `Content_Logo.png` | 深色 Logo（用于浅色背景） | 内容页右上角 `.header-logo-primary`、结尾页 `.ending-logo-primary` |
| `Content_Logo_Secondary.png` | 彩色副品牌 Logo（用于浅色背景） | 内容页右上角 `.header-logo-secondary`（可选） |
| `BackGround_Decoration.png` | 品牌装饰图（圆环+曲线纹理） | 封面右上角 `.slide.cover::before`、结尾页 `.slide.ending::before`（可选） |

> **兼容旧资产**：如果工作区已有其他命名方式的品牌素材目录，可直接引用，只需调整 CSS 中的路径。

#### 自动注入的 CSS 覆盖规则

选择自定义品牌模板后，在 `</style>` 前追加以下覆盖样式块（核心要点，色值和 Logo 路径替换为用户提供的值）：

```css
/* ========== 自定义品牌模板覆盖 ========== */
:root {
  --primary: #2F80ED; --primary-soft: #EEF6FF; --primary-dark: #1456C8;
  --accent: #35C6F4; --accent-soft: #EAFBFF;
  --green: #20B8A8; --green-soft: #E9FBF8;
  --amber: #F3A875; --amber-soft: #FFF3E8;
  --red: #FB5387; --red-soft: #FFF0F6;
  --purple: #9D9AFE;
  --text-primary: #111; --text-secondary: #333; --text-muted: #666;
  --border: rgba(193,199,217,.58);
  --bg-card: rgba(255,255,255,.94);
  --shadow: 0 20px 52px rgba(47,128,237,.12);
  --shadow-soft: 0 10px 28px rgba(17,17,17,.055);
  --neon: #89E0D4;
}

/* ── 页面背景 & 底部色条 ── */
.slide { background: linear-gradient(180deg, #FFF 0%, #F8FBFF 100%); overflow: hidden; }
.slide::after {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0;
  height: 4px; background: linear-gradient(90deg, #2F80ED, #35C6F4, #9D9AFE);
}

/* ── 封面页 ── */
/* 深色渐变背景 */
.slide.cover {
  background: radial-gradient(circle at 82% 25%, rgba(137,224,212,.26), transparent 34%),
              linear-gradient(125deg, #081227, #123A8C 52%, #129AC0);
  color: white;
}
.slide.cover::after { background: linear-gradient(90deg, #2F80ED, #89E0D4, #9D9AFE); }

/* 封面右上角品牌装饰图（圆环+曲线纹理，大尺寸从右上角铺入） */
.slide.cover::before {
  content: ''; position: absolute; top: 0; right: 0;
  width: 900px; height: 560px;
  background: url('ppt_brand_assets/BackGround_Decoration.png') right top/contain no-repeat;
  opacity: 1; pointer-events: none; z-index: 0;
}

/* 封面品牌 Logo — 左上角，白色版本（适配深色背景） */
.cover-logo {
  position: absolute; top: 32px; left: 48px;
  display: flex; align-items: center; gap: 16px;
  z-index: 1;
}
.cover-logo-primary {
  width: 140px; height: 36px;
  background: url('ppt_brand_assets/Home_Logo.png') center/contain no-repeat;
}
.cover-logo-divider { width: 1px; height: 28px; background: rgba(255,255,255,0.3); }
.cover-logo-secondary {
  width: 120px; height: 36px;
  background: url('ppt_brand_assets/Home_Logo_Secondary.png') center/contain no-repeat;
}

/* 封面标题样式 */
.cover-title {
  font-size: 44px; font-weight: 900; margin-bottom: 16px;
  background: linear-gradient(135deg, #fff, #89E0D4);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.cover-subtitle { font-size: 20px; font-weight: 300; opacity: 0.85; margin-bottom: 48px; }
.cover-meta { font-size: 13px; opacity: 0.6; }

/* ── 内容页页眉：左标题 + 右双品牌 Logo ── */
.header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 24px 56px 0; position: relative;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.header-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--purple); flex-shrink: 0;
}
.page-title { font-size: 24px; font-weight: 700; color: var(--text-primary); }
.header-brand { display: flex; align-items: center; gap: 10px; }
.header-logo-primary {
  width: 80px; height: 28px;
  background: url('ppt_brand_assets/Content_Logo.png') center/contain no-repeat;
}
.header-logo-divider { width: 1px; height: 22px; background: var(--border); }
.header-logo-secondary {
  width: 100px; height: 28px;
  background: url('ppt_brand_assets/Content_Logo_Secondary.png') center/contain no-repeat;
}
/* 页眉下方蓝青渐变色条 */
.header::after {
  content: ''; position: absolute; left: 56px; top: 68px;
  width: 120px; height: 3px; border-radius: 999px;
  background: linear-gradient(90deg, #2F80ED, #89E0D4);
}

/* ── 内容页页脚：左文字 + 右页码 ── */
.page-footer {
  position: absolute; bottom: 16px; left: 56px; right: 56px;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 11px; color: var(--text-muted);
}
.page-footer .brand-text { color: var(--text-muted); }
.page-no { font-weight: 500; }

/* ── 网格布局对齐规则（左右列等高填满） ── */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: stretch; }
.grid-2 > div { display: flex; flex-direction: column; min-height: 0; }
.grid-2 > div > .card { flex: 1; }
.grid-2 > div > div[style*="flex-direction:column"] { flex: 1; }
.grid-2 > div > div[style*="flex-direction:column"] > .card { flex: 1; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; align-items: stretch; }
.grid-3 > div, .grid-3 > .card { display: flex; flex-direction: column; }
.grid-3 > .card { flex: 1; }

/* ── 结尾页 ── */
.slide.ending {
  background: radial-gradient(circle at 50% 50%, rgba(47,128,237,0.08), transparent 60%),
              linear-gradient(180deg, #FFF 0%, #F0F7FF 100%);
  overflow: hidden;
}
/* 结尾页右上角装饰图（与封面呼应） */
.slide.ending::before {
  content: ''; position: absolute; top: 0; right: 0;
  width: 700px; height: 500px;
  background: url('ppt_brand_assets/BackGround_Decoration.png') right top/contain no-repeat;
  opacity: 1; pointer-events: none; z-index: 0;
}
.ending-content {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; height: 100%; text-align: center;
  position: relative; z-index: 1;
}
.ending-logo {
  display: flex; align-items: center; justify-content: center; gap: 20px;
  margin-bottom: 24px;
}
.ending-logo-primary {
  width: 120px; height: 42px;
  background: url('ppt_brand_assets/Content_Logo.png') center/contain no-repeat;
}
.ending-logo-divider { width: 1px; height: 28px; background: var(--border); }
.ending-logo-secondary {
  width: 160px; height: 42px;
  background: url('ppt_brand_assets/Content_Logo_Secondary.png') center/contain no-repeat;
}

/* 卡片：圆角 12px、浅色、轻阴影 */
.card { border-color: rgba(193,199,217,.62); border-radius: 12px; }

/* pill 标签 */
.pill       { background: #EEF6FF; border-color: rgba(47,128,237,.2); color: #1456C8; }
.pill.green { background: #E9FBF8; color: #158A80; }
.pill.amber { background: #FFF3E8; color: #B66B21; }
.pill.red   { background: #FFF0F6; color: #D72F6B; }

/* 表格/矩阵/规格表头渐变 */
.matrix .head, .table .head, .spec-title {
  background: linear-gradient(135deg, #2F80ED, #35C6F4 58%, #9D9AFE);
}
```

#### HTML 结构约定

##### 封面页 HTML 结构

```html
<div class="slide cover active" data-index="0">
  <div class="cover-decoration"></div>   <!-- 右上角光晕装饰 -->
  <div class="cover-decoration2"></div>  <!-- 左下角光晕装饰 -->
  <div class="cover-content">
    <!-- 左上角品牌 Logo（白色版本，适配深色背景） -->
    <div class="cover-logo">
      <div class="cover-logo-primary"></div>
      <div class="cover-logo-divider"></div>
      <div class="cover-logo-secondary"></div>
    </div>
    <div class="cover-title">产品名称</div>
    <div class="cover-subtitle">副标题</div>
    <div class="cover-meta">补充信息</div>
  </div>
</div>
```

**封面布局要点**：
- Logo 固定在**左上角** (`top: 32px; left: 48px`)，使用白色版本 (`Home_*.png`)
- 右上角通过 `::before` 伪元素铺入品牌装饰图 (`BackGround_Decoration.png`)，尺寸 900×560px
- 标题居中，渐变文字（白→青绿）
- 两个 `cover-decoration` 做辅助光晕效果

##### 内容页 HTML 结构

```html
<div class="slide" data-index="N">
  <div class="header">
    <!-- 左侧：圆点 + 页面标题 -->
    <div class="header-left">
      <div class="header-dot"></div>
      <div class="page-title">页面标题</div>
    </div>
    <!-- 右侧：品牌 Logo（深色版本，适配浅色背景） -->
    <div class="header-brand">
      <div class="header-logo-primary"></div>
      <div class="header-logo-divider"></div>
      <div class="header-logo-secondary"></div>
    </div>
  </div>
  <div class="content">
    <!-- 页面内容 -->
  </div>
  <div class="page-footer">
    <span class="brand-text">{brand_name}</span>
    <span class="page-no">02 / 20</span>
  </div>
</div>
```

**内容页布局要点**：
- 页眉左侧 = 紫色圆点 + 页面标题；右侧 = 主品牌 Logo + 分隔线 + 副品牌 Logo
- 页眉下方有蓝青渐变色条（通过 `.header::after` 实现）
- 页脚左侧 = 品牌名称纯文字；右侧 = 页码 "NN / 总数"
- 内容区 `.content` 高度 590px，padding: 20px 56px 14px（紧凑模式，最大化可用面积）

##### 结尾页 HTML 结构

```html
<div class="slide ending" data-index="最后">
  <div class="ending-content">
    <div class="ending-logo">
      <div class="ending-logo-primary"></div>
      <div class="ending-logo-divider"></div>
      <div class="ending-logo-secondary"></div>
    </div>
    <div class="ending-title">产品名称</div>
    <div class="ending-sub">副标题描述</div>
    <!-- 可选：数据统计卡片 -->
    <div style="font-size:14px;color:var(--text-muted);">Thank You & Q&A</div>
  </div>
</div>
```

**结尾页布局要点**：
- 右上角通过 `.slide.ending::before` 铺入装饰图（与封面呼应，尺寸 700×500px）
- 内容区 `z-index: 1` 确保在装饰图之上
- 品牌 Logo 居中，使用深色版本 (`Content_*.png`)

##### 左右布局对齐规则（关键）

当内容页使用 `.grid-2` 左右分栏布局时，**左右列必须等高对齐，页面高度尽量填满**：

```css
/* 网格列拉伸 + 卡片填满列高 */
.grid-2 { align-items: stretch; }
.grid-2 > div { display: flex; flex-direction: column; min-height: 0; }
.grid-2 > div > .card { flex: 1; }
.grid-2 > div > div[style*="flex-direction:column"] { flex: 1; }
.grid-2 > div > div[style*="flex-direction:column"] > .card { flex: 1; }
```

**验证要点**：左右两列底部必须对齐，卡片不应在中间留大片空白。如果内容不均匀，通过 `flex: 1` 让较短一侧的卡片自动拉伸。左右不等高视为版式缺陷，必须修复后才能继续导出。

#### 资产准备（自动注入）

用户需将品牌素材放在本 Skill 的 `brand-assets/` 目录中：

```
doa-ppt/
├── SKILL.md
├── references/
│   ├── screenshot-pptx-template.py
│   └── pptx-converter-template.py
└── brand-assets/                          ← 用户放入品牌素材
    ├── BackGround_Decoration.png          (装饰图，封面/结尾页，可选)
    ├── Content_Logo.png                   (深色 Logo，内容页/结尾页)
    ├── Content_Logo_Secondary.png         (副品牌 Logo，可选)
    ├── Home_Logo.png                      (白色 Logo，封面)
    └── Home_Logo_Secondary.png            (白色副品牌 Logo，可选)
```

**自动注入流程**：当用户选择"自定义品牌"主题时，在生成 HTML 之前自动执行：

1. 定位本 Skill 的 `brand-assets/` 目录（路径：`{skill-root}/brand-assets/`）
2. 在 PPT 输出目录下创建 `ppt_brand_assets/` 子目录
3. 将 `brand-assets/` 下的文件复制到该子目录
4. 如目标目录已存在且文件齐全，跳过复制

```python
# 自动注入示例（在生成脚本开头执行）
import shutil
from pathlib import Path

skill_root = Path(__file__).parent  # 或通过 Skill 路径定位
brand_src = skill_root / "brand-assets"
# 也可以直接用已知的 Skill 安装路径：
# brand_src = Path.home() / ".claude/skills/doa-ppt/brand-assets"

output_dir = Path("output/{产出名称}")
brand_dst = output_dir / "ppt_brand_assets"

if brand_src.exists() and not brand_dst.exists():
    shutil.copytree(brand_src, brand_dst)
```

> **无需手动复制**：团队成员只要安装了 doa-ppt skill，选择自定义品牌模板时品牌素材会自动出现在输出目录中。

---

### 每个主题包含完整配色方案

选定主题后，生成完整的 CSS 变量体系：

```css
:root {
  --primary: #主色;
  --primary-light: #浅色变体;
  --primary-dark: #深色变体;
  --accent: #点缀色;
  --bg-slide: #幻灯片背景;
  --bg-card: #卡片背景;
  --text-primary: #主文字;
  --text-secondary: #次要文字;
  --text-muted: #辅助文字;
  --border: #边框色;
  --banner: #横幅/按钮色;
  --divider: #分隔线色;
}
```

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

如果用户提供了参考图，分析其：
- 主色调和辅助色
- 视觉风格（深色/浅色、扁平/立体）
- 布局偏好

## Step 2: 生成可翻页 HTML 预览

基于收集的需求、确认的规模和选定的主题，生成**一个可左右翻页的 HTML 文件**，模拟幻灯片放映效果。

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
      background: #1a1a2e;
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
      background: rgba(255,255,255,0.15); border: none;
      color: white; font-size: 24px; cursor: pointer;
      backdrop-filter: blur(10px);
      transition: background 0.3s;
      z-index: 100;
    }
    .nav-btn:hover { background: rgba(255,255,255,0.3); }
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
      background: rgba(255,255,255,0.3);
      cursor: pointer; transition: all 0.3s;
    }
    .page-dot.active {
      background: white; transform: scale(1.3);
    }

    /* 键盘提示 */
    .keyboard-hint {
      position: fixed; bottom: 60px; left: 50%;
      transform: translateX(-50%);
      color: rgba(255,255,255,0.4); font-size: 12px;
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
│  [品牌 Logo]              ← 左上角        │
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
│ ● 页面标题               [品牌 Logo]      │
│ ────                                        │
│  左侧（文字描述 + 卡片）  │  右侧（图/预览）  │
│  ← flex:1 等高拉伸 →     │ ← flex:1 等高 →  │
│─────────────────────────────────────────────│
│  {brand_name}                      02 / 20  │
└─────────────────────────────────────────────┘
```

#### 内容页布局（全宽）
```
┌─────────────────────────────────────────────┐
│ ● 页面标题               [品牌 Logo]      │
│ ────                                        │
│  3-4 列并排卡片 / 流程图 / 架构图            │
│                                             │
│─────────────────────────────────────────────│
│  {brand_name}                      03 / 20  │
└─────────────────────────────────────────────┘
```

#### 总结页 / Q&A 页布局
```
┌─────────────────────────────────────────────┐
│                [装饰图] ← 右上角             │
│     [品牌 Logo]                              │
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
- 每页使用相同的字体大小层级（标题 22-28px，正文 12-14px，辅助 11-12px）
- 卡片正文 `.card-text` 使用 `font-size: 12px; line-height: 1.7`，避免过小导致阅读困难

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
