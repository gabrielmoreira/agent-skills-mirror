---
name: doa-image
description: "从用户提供的内容生成精美现代化的 HTML 页面，并可转为高清 PNG 图片。USE FOR: 生成美观HTML页面、创建精美长图、HTML转图片、内容可视化、旅游攻略图、活动海报、信息图表、排版设计、HTML生成PNG、漂亮网页。DO NOT USE FOR: 复杂Web应用（使用 frontend-design skill）、PPT生成（使用 doa-ppt skill）、PDF文档（使用 pdf skill）。"
argument-hint: "描述你要生成的内容主题和要求"
---

# HTML Beautiful Page → Image

将用户提供的内容（文字、数据、攻略等）生成一张格式精美、排版现代、配色雅致的 HTML 页面，用户确认后将其转为高清 PNG 长图。

## When to Use

- 需要把文字内容变成精美可视化页面
- 生成旅游攻略、活动日程、项目简报等长图
- 制作信息图表、清单、排行榜等
- 任何需要 "内容 → 精美HTML → 图片" 的场景

## Design Principles

### 风格自动匹配
根据内容主题自动选择最合适的视觉风格：

| 内容类型 | 推荐风格 | 配色方向 |
|---------|---------|---------|
| 旅游/自然 | 清新自然 | 绿色系、蓝绿色系 |
| 商务/报告 | 专业简约 | 深蓝、灰色系 |
| 美食/生活 | 温暖雅致 | 暖橙、米色系 |
| 科技/产品 | 现代极简 | 深色 + 亮色点缀 |
| 节日/庆祝 | 活泼明快 | 红金、多彩 |
| 文化/历史 | 古典雅致 | 褐色、墨绿 |

### 通用设计规范
1. **字体**：优先使用 `Noto Serif SC`（标题）+ `Noto Sans SC`（正文），通过 Google Fonts 引入
2. **布局**：最大宽度 960px 居中，卡片式布局，圆角 + 柔和阴影
3. **间距**：充足留白，section 间距 40-48px，卡片内边距 24-32px
4. **配色**：使用 CSS 变量统一管理，主色 + 辅色 + 背景 + 文字色
5. **响应式**：添加 `@media (max-width: 600px)` 适配移动端
6. **装饰**：适度使用 emoji 增强表达，避免过度堆砌
7. **Hero 区**：渐变背景 + 标题 + 副标题 + 关键信息，营造视觉焦点

### HTML 结构模板
```
Hero 区（渐变背景 + 标题）
├── 总览/概要（grid 卡片）
├── 主体内容（分节卡片 + 时间线/列表）
├── 补充信息（grid 网格展示）
├── 数据/表格（简洁表格）
├── 提示/备注（tip 卡片网格）
└── 页脚（点睛之笔）
```

## Procedure

### Step 1: 理解需求
- 确认用户要生成的内容主题
- 如果内容不够充分，主动询问补充细节
- 确定视觉风格偏好（或自动匹配）

### Step 2: 生成 HTML
- 创建单文件 HTML（CSS 内联在 `<style>` 中）
- 遵循上述设计规范
- 文件名使用中文描述性名称，如 `湖州五一旅游攻略.html`
- 输出目录：`output/{内容描述性名称}/`（每次新任务创建独立子文件夹）

### Step 3: 用户确认
- 提示用户在浏览器中预览 HTML
- 等待用户确认或提出修改意见
- 如需修改，迭代调整后再次确认

### Step 4: 转为图片
用户确认后，使用 html2image + Edge/Chrome 浏览器将 HTML 截图为 PNG。

生成转换脚本并执行：

```python
import os
from html2image import Html2Image

# 自动查找浏览器
for p in [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]:
    if os.path.exists(p):
        browser_path = p
        break

hti = Html2Image(
    browser_executable=browser_path,
    output_path="<输出目录>",
    custom_flags=["--no-sandbox", "--disable-gpu", "--hide-scrollbars"],
)
hti.screenshot(
    html_file="<HTML文件路径>",
    save_as="<输出文件名>.png",
    size=(1080, <根据内容估算高度>),
)
```

**高度估算参考**：
- 简短内容（1屏）：800-1200px
- 中等内容（2-3屏）：2000-3000px
- 长内容（攻略/报告）：3500-5000px

### Step 5: 验证输出
- 使用 `view_image` 工具查看生成的 PNG
- 确认内容完整、排版正确
- 报告文件路径和大小

## Prerequisites
- Python 包：`html2image`（如未安装需先安装）
- 系统浏览器：Edge 或 Chrome（Windows 默认已安装 Edge）

## Notes
- HTML 中不使用外部图片资源（避免截图时加载失败）
- emoji 和 SVG 内联图形可正常渲染
- 如用户提供了参考图或风格要求，优先按用户偏好设计
