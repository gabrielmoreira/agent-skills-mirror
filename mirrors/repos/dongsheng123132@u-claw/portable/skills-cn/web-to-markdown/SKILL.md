---
name: web-to-markdown
description: "网页转 Markdown - 抓取任意网页正文并转成干净的 Markdown，便于阅读/收藏/二次创作"
metadata: { "openclaw": { "emoji": "🔗" } }
---

# 网页转 Markdown

把用户给的网页链接抓下来，提取正文，转成干净的 Markdown，方便保存、总结或二次创作。

## 能力概述

- **正文提取**：去掉导航/广告/页脚，只留主体内容
- **转 Markdown**：标题、列表、链接、代码块保留结构
- **保存**：可写入本地 .md 文件

## 操作方式

用 Bash 工具。首选 jina.ai 的免费 reader（无需依赖，最省事）：

```bash
# 最简：jina reader 直接返回干净 Markdown（在链接前加 https://r.jina.ai/）
curl -s "https://r.jina.ai/https://example.com/article" -o article.md
echo "已保存 -> article.md"; head -40 article.md
```

离线或 jina 不可用时，用 Python 本地转换：

```bash
python -c "import markdownify,requests" 2>/dev/null || pip install -q markdownify requests beautifulsoup4
python - <<'PY'
import requests, re
from bs4 import BeautifulSoup
from markdownify import markdownify as md
url = "https://example.com/article"
html = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"}).text
soup = BeautifulSoup(html, "html.parser")
for t in soup(["script","style","nav","footer","aside"]): t.decompose()
body = soup.find("article") or soup.find("main") or soup.body
out = md(str(body), heading_style="ATX")
out = re.sub(r"\n{3,}", "\n\n", out).strip()
open("article.md","w",encoding="utf-8").write(out)
print("已保存 -> article.md，", len(out), "字")
PY
```

## 使用建议

- 先问用户要不要保存到文件、文件名
- 微信公众号/知乎等需要登录的页面可能抓取受限，如失败如实告知
- 抓取后可顺手做"总结要点"，结合 china-search / deepseek-helper 技能
