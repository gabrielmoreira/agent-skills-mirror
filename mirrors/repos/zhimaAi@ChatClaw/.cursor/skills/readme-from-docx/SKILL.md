---
name: readme-from-docx
description: Update README and docs/readmes from Word docx (English and Chinese). Use when the user provides docx files to update feature previews, wants to sync README with docx content, or asks to extract docx images and update readmes.
---

# Update README from Docx

当用户提供英文和中文 docx 文件并要求更新 README 功能预览时，使用本技能。

## 用户输入示例

```
请根据新版本的文档 @think_docs/AIParsing/readme-英文V3.docx @think_docs/AIParsing/readme-中文-V3.docx，
更新 README 中的【## 功能预览】中的内容，
以及其他语言的 README 都使用自己的语言翻译内容并替换自己的【## 功能预览】中的内容。
```

## 三个核心原则

### ① 图片必须按文档 rId 顺序提取

> ⚠️ **绝对禁止**用 `word/media/` 在 ZIP 中的文件名排序来命名输出图片！
>
> 图片命名只看一个标准：**图片在文档正文中出现的 rId 顺序**。
> 先读 `word/_rels/document.xml.rels` 建立 `rId → media/path` 映射，再遍历 `word/document.xml` 的 `<w:body>`，在每个 `<w:p>` 中找 `<wp:inline>` 或 `<wp:anchor>` → `<a:blip>` → `r:embed`，按出现顺序编号：第1个 → `image1.png`，第2个 → `image2.png`，依此类推。
>
> 具体步骤见 **Step 1**。

### ② 图片-段落映射每次从文档提取，不依赖历史记录

每次使用技能时，都要重新分析 docx 的 XML 结构，提取 rId 顺序，确定当前版本的图片-章节对应关系。不同版本的 docx 章节顺序和图片数量可能不同（例：英文14张、中文15张），**不要**假设上一版本的映射在新区本中仍然有效。

### ③ 中英文内容可能不一致，其他语言使用英文格式和英文图片

- **根目录 `README.md`** 和 **`README_zh-CN.md`**：中文内容 + `zh-CN` 图片，数量和顺序以中文 docx 为准。
- **`README_en.md`**：英文内容 + `en` 图片，数量和顺序以英文 docx 为准。
- **其他语言**（zh-TW、ja-JP、ko-KR 等 15 种）：翻译文字，图片路径固定使用 `../../images/previews/en/`，章节数量和顺序与英文版保持一致，**不要**引入中文版才有的额外章节或图片。

### ④ 文档中的换行必须对应保留

> ⚠️ **不要**将文档中的多行段落合并为一行输出！
>
> docx 中一个段落在 XML 中可能被拆分为多个 `<w:br/>` 换行或多个 `<w:p>` 连续段落，生成 Markdown 时必须忠实还原：
> - `<w:br/>` 换行符 → Markdown 中的 `  `（两个空格）+ 换行
> - 文档中独立的空行 → Markdown 中保留一个空行
> - 段落内的软换行（如标题与描述文字间的换行）→ 保留 `  \n` 格式
>
> 示例（错误的合并输出）：
> ```markdown
> <!-- ❌ BAD：将多行合并为一行，失去原文排版 -->
> ChatClaw是一款开源的本地知识库、OpenClaw图形化桌面管家应用无需编程，一键部署至本地电脑。
> ```
> 示例（正确的保留换行）：
> ```markdown
> <!-- ✅ GOOD：忠实保留文档换行 -->
> ChatClaw是一款开源的本地知识库、OpenClaw图形化桌面管家应用
> 无需编程，一键部署至本地电脑。可连接 微信、 钉钉、企业微信、QQ、飞书，WhatsApp等主流通讯应用，
> 发送指令即可让 AI 帮你执行任务。内置 OpenClaw 5000+ 技能库，并支持类 ima 的本地知识库管理
> ```
>
> 在提取文本时，按 docx XML 中 `<w:p>` 的自然顺序拼接，保持与原文档一致的段落结构和换行位置。

## Step 1: 提取图片（按文档 rId 顺序）

### 方法概述

1. 解压 docx（本质是 ZIP）。
2. 读 `word/_rels/document.xml.rels`，建立 `rId → word/media/XXX.png` 的映射。
3. 读 `word/document.xml`，遍历 `<w:body>` 下每个 `<w:p>` 段落，查找其中的 `<wp:inline>` 或 `<wp:anchor>` 元素，从中取出 `<a:blip r:embed="rIdX">`，记录出现的 rId。
4. 按 rId 在文档中首次出现的顺序，依次将图片文件重命名为 `image1.png`、`image2.png`… 保存到目标目录。

### Python 参考脚本

```python
import zipfile
import xml.etree.ElementTree as ET
import os

def extract_by_doc_order(docx_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(docx_path) as z:
        # 1. 读 rels，建立 rId -> 实际ZIP路径的映射
        with z.open('word/_rels/document.xml.rels') as f:
            rels = ET.fromstring(f.read())
        rid_to_zip_path = {}
        for rel in rels:
            rid = rel.get('Id')
            target = rel.get('Target')       # 如 "media/image7.png"
            if target and 'media/' in target:
                # rels中是相对路径，ZIP中实际路径需要加 "word/" 前缀
                rid_to_zip_path[rid] = 'word/' + target

        # 2. 遍历 document.xml，按正文出现顺序收集图片
        with z.open('word/document.xml') as f:
            doc = ET.fromstring(f.read())

        wp_ns = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
        r_ns  = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
        blip_ns = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
        body = doc.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body')

        seen, seq = set(), 0
        for elem in body:
            if elem.tag.split('}')[-1] != 'p':
                continue
            for dw in (elem.findall(f'.//{wp_ns}inline') +
                       elem.findall(f'.//{wp_ns}anchor')):
                for blip in dw.findall(f'.//{blip_ns}blip'):
                    embed = blip.get(f'{r_ns}embed')
                    if embed and embed in rid_to_zip_path and embed not in seen:
                        seen.add(embed)
                        seq += 1
                        out_name = f'image{seq}.png'
                        with open(os.path.join(output_dir, out_name), 'wb') as f:
                            f.write(z.read(rid_to_zip_path[embed]))
                        print(f'  [{seq}] {rid_to_zip_path[embed]} -> {out_name}')

    print(f'  提取到: {output_dir} ({seq} 张)')

# 用法
extract_by_doc_order('readme-英文V3.docx', 'images/previews/en/')
extract_by_doc_order('readme-中文-V3.docx', 'images/previews/zh-CN/')
```

### 输出目标

| 文档 | 输出目录 | 图片数量 |
|------|----------|----------|
| 英文 docx | `images/previews/en/` | image1.png ~ image14.png |
| 中文 docx | `images/previews/zh-CN/` | image1.png ~ image15.png |

**先提取，再分析章节结构**，不要在提取图片前假设章节数量或顺序。

## Step 2: 分析章节-图片映射（从提取结果推断）

图片提取完成后，通过对比文档文本和图片的出现顺序，建立当前版本的章节-图片对应关系：

- 遍历 docx 正文，每个 `<w:p>` 段落提取纯文本。
- 段落含图片 → 对应一张图片（图片在该段落或紧邻的下一段落）。
- 记录"章节标题段落"和"对应图片编号"的对应关系。
- 输出一个章节列表（含序号、标题、图片编号），作为后续替换的基准。

**映射示例（V3）：**

| 序号 | 图片 | 英文标题 | 中文标题 |
|------|------|----------|----------|
| 1 | image1.png | AI Chatbot Assistant | AI 聊天助手 |
| 2 | image2.png | （续图） | （续图） |
| 3 | image3.png | Multi-Agent Mode… | 多Agent模式… |
| … | … | … | … |

**注意**：英文 docx 和中文 docx 的章节顺序和数量可能不同，必须分别分析。

## Step 3: 更新英文 README

### 文件与路径

| 文件 | 图片路径 |
|------|----------|
| `README.md`（根目录） | `./images/previews/zh-CN/`（**中文内容 + zh-CN 图片**） |
| `docs/readmes/README_en.md` | `../../images/previews/en/`（英文内容 + en 图片） |

### 替换逻辑

在 `## Previews`（英文）或其语言等价标题，到下一个顶级 `## …` 标题之间，用分析出的章节-图片映射重写整个区块。每个功能块：

```markdown
### 英文标题

描述段落。

![](./images/previews/zh-CN/imageN.png)
```

根目录 `README.md` 用中文内容（见 Step 4），路径前缀 `./`。
`docs/readmes/` 下的文件路径前缀 `../../`。

## Step 4: 更新中文 README（根目录 + docs/readmes）

根目录 `README.md` 和 `docs/readmes/README_zh-CN.md` 都用中文内容。

### 文件与路径

| 文件 | 图片路径 |
|------|----------|
| `README.md`（根目录） | `./images/previews/zh-CN/` |
| `docs/readmes/README_zh-CN.md` | `../../images/previews/zh-CN/` |

中文版章节数量和顺序以中文 docx 为准（通常与英文一致，但可能多一张二维码图 image15.png）。

## Step 5: 翻译其他语言

### 范围

`docs/readmes/` 下除 `README_en.md` 和 `README_zh-CN.md` 以外的所有 `README_*.md`。

### 规则

- **图片**：固定使用 `../../images/previews/en/imageN.png`（与英文版相同，**不要**引入 zh-CN 图片）。
- **章节数量和顺序**：与英文版严格对齐（不要因为中文版多一张图就加章节）。
- **排版格式**：使用英文版的 Markdown 结构（标题层级、图片数量和位置与英文版一致）。
- **翻译内容**：只翻译 `## Previews` 区块（章节标题、`###` 小标题、描述段落），其余内容（安装说明、服务器部署、技术栈等）保持原样。

### 语言专属章节标题

| 语言 | 代码 | Previews 标题 | Server Mode 标题 |
|------|------|---------------|------------------|
| 简体中文 | zh-CN | `## 功能预览` | `## 服务器模式部署` |
| 繁体中文 | zh-TW | `## 功能預覽` | `## 伺服器模式部署` |
| 英语 | en | `## Previews` | `## Server Mode Deployment` |
| 日语 | ja-JP | `## プレビュー` | `## サーバーモードデプロイ` |
| 韩语 | ko-KR | `## 미리보기` | `## 서버 모드 배포` |
| 阿拉伯语 | ar-SA | `## المعاينة` | `## نشر وضع الخادم` |
| 孟加拉语 | bn-BD | `## প্রিভিউ` | `## সার্ভার মোড ডিপ্লয়মেন্ট` |
| 德语 | de-DE | `## Vorschau` | `## Server-Modus-Bereitstellung` |
| 西班牙语 | es-ES | `## Previsualizaciones` | `## Despliegue en Modo Servidor` |
| 法语 | fr-FR | `## Aperçus` | `## Déploiement en Mode Serveur` |
| 印地语 | hi-IN | `## पूर्वावलोकन` | `## सर्वर मोड परिनियोजन` |
| 意大利语 | it-IT | `## Anteprime` | `## Distribuzione Modalità Server` |
| 葡萄牙语 | pt-BR | `## Visualizações` | `## Implantação em Modo Servidor` |
| 斯洛文尼亚语 | sl-SI | `## Predogledi` | `## Namestitev v načinu strežnika` |
| 土耳其语 | tr-TR | `## Önizlemeler` | `## Sunucu Modu Dağıtımı` |
| 越南语 | vi-VN | `## Xem trước` | `## Triển khai Chế độ Máy chủ` |

完整的小标题翻译对照见 [reference.md](reference.md)。

## 完成前检查清单

- [ ] 图片已按 rId 顺序提取：`images/previews/en/` 14 张，`images/previews/zh-CN/` 15 张（或以实际提取数量为准）。
- [ ] 章节-图片映射已从当前文档分析得出（不是引用旧版本记录）。
- [ ] 根 `README.md` 用中文内容 + `./images/previews/zh-CN/`。
- [ ] `docs/readmes/README_en.md` 用英文内容 + `../../images/previews/en/`。
- [ ] `docs/readmes/README_zh-CN.md` 用中文内容 + `../../images/previews/zh-CN/`。
- [ ] 所有其他语言 README 的 Previews 区块已翻译，图片路径固定 `../../images/previews/en/`，章节数量和顺序与英文版一致。
- [ ] 图片引用后有空行，不与下一个 `##` 标题粘连。
- [ ] 文档中段落内的换行已忠实还原（`<w:br/>` → `  \n`），没有合并为单行。
