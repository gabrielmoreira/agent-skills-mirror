# Source-quality Preflight

## 目的

判断当前载体是否足以支持可追溯蒸馏。把“正式出版物经过校对”与“后来转换出的 DOCX/OCR 是否保真”分开评价。

## adapter 边界

自动结构提取承诺项目随附的 DOCX adapter、扫描 PDF adapter，或符合项目 schema 的
规范化 bundle。DOCX 先无 OCR 地确定性抽取文本/结构，再对全部内嵌图片运行本地
Tesseract；扫描 PDF 用 Poppler 固定 300 DPI 渲染全部页面后逐页 OCR。其他 PDF、EPUB
和第三方 OCR 输出没有兼容 bundle 时仍只能有限 preflight。

DOCX adapter 位于 Skill 自身，不依赖工作区根目录的同名脚本：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/normalize_docx_source.py SOURCE.docx --source-id SOURCE_ID --output-dir NORMALIZED_DIR
```

该脚本只使用 Python 标准库，不执行 OCR 或术语修正。图片抽取后另运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/ocr_book_source.py docx-bundle NORMALIZED_DIR \
  --source-id SOURCE_ID --sources-manifest SOURCES_MANIFEST --output-dir OCR_DIR \
  --languages chi_sim+eng
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/ocr_book_source.py scanned-pdf SOURCE.pdf \
  --source-id SOURCE_ID --sources-manifest SOURCES_MANIFEST --output-dir OCR_DIR \
  --languages chi_sim+eng
```

Tesseract、所声明语言包以及扫描 PDF 所需的 `pdfinfo/pdftoppm` 必须预先存在；Skill 不安装
依赖、不联网、不上传。命令的 `--languages` 必须与 source 的 `ocr_policy.languages` 顺序和
内容完全一致。生成 evidence 后，用下列只读检查解析 locator：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/verify_normalized_locators.py DISTILLATION_DIR NORMALIZED_ROOT \
  --sources-manifest SOURCES_MANIFEST
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/verify_ocr_locators.py DISTILLATION_DIR OCR_ROOT \
  --sources-manifest SOURCES_MANIFEST --normalized-root NORMALIZED_ROOT
```

DOCX OCR verifier 必须传 `--normalized-root`，以便重新验证 normalization checksums、
`media-map.yml`、全部 asset 与 occurrence；只验证扫描 PDF 时可省略。verifier 还会按 manifest
的 `local_path` 复算原来源，并对扫描 PDF 现场调用 `pdfinfo` 复核页数。

## 只读检查

进入来源登记、规范化或结构扫描前，先读取 Gate 1 的 sequence/supersedes/is_current 链。
只有 current 决定为 `approved` 或 `approved-with-conditions` 才能继续；否则回到 Gate 1，
不得规范化、扫描或读取待蒸馏正文。现有来源文件或 manifest 记录不构成替代授权。

1. **身份与登记**：以版权页等书内信息确认书名、作者、版次、ISBN 和完整性；文件名只作
   线索。确认后分配稳定 source ID，并向已有 manifest 增量登记，不以“已登记”作为开始
   登记的前置条件，也不以模板覆盖 manifest。
2. **完整性**：检查目录、正文、图表、脚注、附录和留出材料是否存在，记录缺页或截断。
3. **稳定性**：规范化前后核对原文件 SHA-256、大小和修改时间。
4. **结构**：比较目录与正文标题，检查样式层级、阅读顺序、表格、页眉页脚、分页和 section。
5. **文本层**：抽样核对缺字、乱码、OCR 混淆、专业术语、科学符号、公式和多栏错序。
6. **图像层**：记录 relationship、文档顺序、原始字节、像素/显示尺寸、alt、图注和前后正文；
   全部图片/页面必须 OCR，不得凭“装饰图”分类跳过。empty 仍记录 `ocr-empty`，failed 或缺失 occurrence 使覆盖不完整；
   OCR 不用于猜测箭头、公式、图文关系或不可读标签。
7. **元数据**：比较应用报告的页数/字数与实际结构，标记模板化或失真的属性。
8. **留出隔离**：确认评测材料完整，且不含用于规则提取的作者点评或答案。
9. **恢复检查**：若蒸馏目录已存在，比较原 source ID/checksum、adapter 版本、已有
   source map 和 overlay；默认恢复，不覆盖人工路径或问题记录。

规范化器和 OCR runner 不写原文件；派生 bundle、页图和日志只写到私有、被忽略的来源
区。处理前后复核原文件 checksum。OCR 原始输出可保留，但用于 accepted evidence 前必须
人工审阅；术语、科学符号、公式或 OCR 修正进入 overlay。

## 载体特定 locator

DOCX 优先使用：

```text
source_id + heading_path + OOXML block index + content hash
```

需要时增加 figure/table ID。印刷页码只作辅助。扫描 PDF 使用页码、300 DPI 页图 hash、
OCR record/region、bbox 与文本 hash；EPUB 或其他 PDF 只有在已验证 adapter
或规范化 bundle 明确定义时，才使用可重复的 spine/fragment、图像或内容 hash；
否则只记录 preflight 观察，不宣称已经建立蒸馏 locator。

Gate 4 不得把 DOCX resolver 强加给兼容非 DOCX bundle：DOCX 使用随附 resolver；其他
bundle 只能使用其已验证 locator checker。若没有 checker，则阻断依赖该定位的 run。

## 处置

- `usable`：结构和内容足以支持冻结任务；
- `usable-with-overlay`：允许继续不依赖问题的范围，但人工 source map 和 correction overlay 必须覆盖已知问题；
- `blocked`：缺少稳定 locator、关键内容或可读图像，不能安全提取。

blocked 应记录范围。单个块、图像或术语失败时阻断依赖它的 claim/rule；来源身份、合法
处理边界、全局 locator 或冻结任务必需内容失败时才整体阻断。

原始文本永不就地修正。将疑点、候选修正、依据、影响 claim、待解除 quality flags、
审核人和决定写入独立 overlay；使用修正解释的 claim 必须列出 correction IDs。科学
术语和 OCR 修正不得自动升级为 accepted，清空 quality flag 也不能替代 overlay 决定。
