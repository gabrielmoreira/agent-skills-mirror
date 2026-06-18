---
name: pdf-toolkit
description: "PDF 工具箱 - 合并/拆分/提取文字/转图片，纯命令行处理本地 PDF"
metadata: { "openclaw": { "emoji": "📄" } }
---

# PDF 工具箱

帮用户对本地 PDF 文件做常见处理：合并、拆分、提取文字、转图片。优先用系统已有工具，
没有就用 Python 的 pypdf（轻量纯 Python，必要时 `pip install pypdf` 自动安装）。

## 能力概述

- **合并**：把多个 PDF 拼成一个
- **拆分**：按页拆成多份，或抽取指定页
- **提取文字**：把 PDF 内容导出成纯文本，便于总结/检索
- **页数/信息**：查看 PDF 总页数、元信息

## 操作方式

用 Bash 工具执行。下面以 pypdf 为例（跨平台、无需 Office/Acrobat）：

```bash
# 确保依赖（仅首次，已装会秒过）
python -c "import pypdf" 2>/dev/null || pip install -q pypdf

# 合并 a.pdf b.pdf -> merged.pdf
python - <<'PY'
from pypdf import PdfWriter
w = PdfWriter()
for f in ["a.pdf", "b.pdf"]:
    w.append(f)
w.write("merged.pdf"); w.close()
print("已合并 -> merged.pdf")
PY

# 提取全部文字
python - <<'PY'
from pypdf import PdfReader
r = PdfReader("input.pdf")
print("\n".join((p.extract_text() or "") for p in r.pages))
PY

# 抽取第 1-3 页 -> sub.pdf
python - <<'PY'
from pypdf import PdfReader, PdfWriter
r = PdfReader("input.pdf"); w = PdfWriter()
for i in range(0, 3):
    w.add_page(r.pages[i])
w.write("sub.pdf"); w.close()
print("已抽取 1-3 页 -> sub.pdf")
PY
```

## 使用建议

- 处理前先 `ls` 确认文件存在、用 `python -c "from pypdf import PdfReader;print(len(PdfReader('x.pdf').pages))"` 看页数
- 扫描件（图片型 PDF）提取不到文字属正常，需 OCR（提示用户）
- 输出文件默认放在与源文件同目录，操作完告诉用户生成的文件名
