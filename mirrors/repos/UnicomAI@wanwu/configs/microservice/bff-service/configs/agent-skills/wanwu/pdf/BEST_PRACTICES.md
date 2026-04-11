# PDF 生成最佳实践

## 核心原则

**推荐方法**：直接使用 `Paragraph` 生成 PDF，而不是先转换为 markdown。

## 快速开始

### ✅ 推荐方法：直接生成 PDF

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# 1. 注册字体
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# 2. 创建文档
doc = SimpleDocTemplate(
    "output.pdf",
    pagesize=A4,
    rightMargin=2*cm,
    leftMargin=2*cm,
    topMargin=2*cm,
    bottomMargin=2*cm
)

# 3. 创建样式
title_style = ParagraphStyle(
    'Title',
    fontName='STSong-Light',
    fontSize=18,
    spaceAfter=20
)

body_style = ParagraphStyle(
    'Body',
    fontName='STSong-Light',
    fontSize=11,
    leading=16,
    firstLineIndent=22
)

# 4. 构建内容
story = []
story.append(Paragraph("文档标题", title_style))
story.append(Paragraph("正文内容会自动换行，不会超出页面边界。", body_style))
story.append(Paragraph("支持中英文混合文本。", body_style))

# 5. 生成 PDF
doc.build(story)
```

**优势**：
- ✅ 完全控制内容和样式
- ✅ 自动换行，不会越界
- ✅ 支持中英文
- ✅ 无需中间格式

## 常见问题及解决方案

### ❌ 问题 1：内容越界、丢失

**错误示例**：
```python
from reportlab.pdfgen import canvas

c = canvas.Canvas("output.pdf", pagesize=A4)
c.setFont('STSong-Light', 12)
c.drawString(100, 750, "这是一个非常长的文本，会超出页面边界导致内容丢失...")
c.save()
```

**问题**：
- `drawString` 不会自动换行
- 文本超出页面边界
- 内容丢失

**✅ 正确方法**：
```python
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle

doc = SimpleDocTemplate("output.pdf", pagesize=A4)
story = []

style = ParagraphStyle(
    'Custom',
    fontName='STSong-Light',
    fontSize=12,
    leading=16
)

# Paragraph 会自动换行
story.append(Paragraph("这是一个非常长的文本，会自动换行，不会超出页面边界。", style))

doc.build(story)
```

### ❌ 问题 2：没有处理格式

**错误示例**：
```python
# 所有文本样式相同
c.drawString(100, y, "标题")
c.drawString(100, y, "正文")
```

**问题**：
- 标题、正文样式相同
- 没有视觉层次

**✅ 正确方法**：
```python
# 使用不同的样式
title_style = ParagraphStyle('Title', fontName='STSong-Light', fontSize=18, spaceAfter=20)
body_style = ParagraphStyle('Body', fontName='STSong-Light', fontSize=11, leading=16)

story.append(Paragraph("标题", title_style))
story.append(Paragraph("正文内容", body_style))
```

**可选**：如果有 markdown 内容，可以使用 `markdown_to_pdf` 工具：
```python
from markdown_to_pdf import markdown_to_pdf

markdown_text = """
# 标题

**粗体文本**

- 列表项
"""

markdown_to_pdf(markdown_text, "output.pdf")
```

### ❌ 问题 3：简单的行分割

**错误示例**：
```python
for line in content.split('\n'):
    c.drawString(100, y, line)
    y -= 20
```

**问题**：
- 没有考虑文本宽度
- 长行仍然会越界
- 没有自动换行

**✅ 正确方法**：
```python
# 使用 Paragraph 自动处理换行
for line in content.split('\n'):
    story.append(Paragraph(line, style))
```

## 最佳实践

### 1. 使用 SimpleDocTemplate + Paragraph

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

# 创建文档（自动处理页面边距）
doc = SimpleDocTemplate(
    "output.pdf",
    pagesize=A4,
    rightMargin=2*cm,
    leftMargin=2*cm,
    topMargin=2*cm,
    bottomMargin=2*cm
)

# 创建样式
style = ParagraphStyle(
    'Custom',
    fontName='STSong-Light',
    fontSize=11,
    leading=16,
    firstLineIndent=22  # 首行缩进
)

# 构建内容（自动换行）
story = []
story.append(Paragraph("长文本会自动换行，不会越界。", style))

# 生成 PDF
doc.build(story)
```

### 2. 正确设置字体

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# 注册中文字体（CIDFont，无需字体文件）
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# 英文使用 PDF 内置字体（Times-Roman，无需注册）
style_chinese = ParagraphStyle('Chinese', fontName='STSong-Light', fontSize=11)
style_english = ParagraphStyle('English', fontName='Times-Roman', fontSize=11)
```

## 对比总结

| 方法 | 自动换行 | 格式支持 | 内容完整性 | 推荐度 |
|------|---------|---------|-----------|--------|
| `drawString` | ❌ 不支持 | ❌ 不支持 | ❌ 易丢失 | ⭐ 不推荐 |
| `Paragraph` | ✅ 支持 | ✅ 完全控制 | ✅ 完整 | ⭐⭐⭐⭐ **强烈推荐** |
| `markdown_to_pdf` | ✅ 支持 | ✅ Markdown | ✅ 完整 | ⭐⭐⭐ 可选工具 |

## 快速开始

### 推荐方法：直接生成 PDF

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# 注册字体
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# 创建文档
doc = SimpleDocTemplate("output.pdf")

# 创建样式
style = ParagraphStyle('Custom', fontName='STSong-Light', fontSize=11)

# 构建内容
story = [Paragraph("文档内容会自动换行", style)]

# 生成 PDF
doc.build(story)
```

### 可选：从 Markdown 生成

如果已有 markdown 内容，可以使用辅助工具：

```python
from markdown_to_pdf import markdown_to_pdf

markdown = """
# 文档标题

## 章节 1

这是正文内容，会自动换行。

**粗体文本** 和普通文本。

- 列表项 1
- 列表项 2
"""

markdown_to_pdf(markdown, "output.pdf")
```

## 相关文件

- [markdown_to_pdf.py](scripts/markdown_to_pdf.py) - Markdown 转 PDF 工具
- [test_improved_pdf.py](scripts/test_improved_pdf.py) - 测试脚本
- [SKILL.md](SKILL.md) - 完整使用文档
