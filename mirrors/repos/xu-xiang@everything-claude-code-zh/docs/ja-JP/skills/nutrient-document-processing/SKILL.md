---
name: nutrient-document-processing
description: 使用 Nutrient DWS API 进行文档处理、转换、OCR、提取、脱敏、签名以及表单填充。支持 PDF、DOCX、XLSX、PPTX、HTML 和图像格式。
---

# Nutrient 文档处理 (Document Processing)

使用 [Nutrient DWS 处理程序 API (Processor API)](https://www.nutrient.io/api/) 处理文档。它可以进行格式转换、文本与表格提取、扫描文档的光学字符识别 (OCR)、个人身份信息 (PII) 脱敏、添加水印、数字签名以及 PDF 表单填充。

## 设置 (Setup)

请在 **[nutrient.io](https://dashboard.nutrient.io/sign_up/?product=processor)** 获取免费的 API 密钥。

```bash
export NUTRIENT_API_KEY="pdf_live_..."
```

所有请求都以多部分 POST (multipart POST) 的形式发送到 `https://api.nutrient.io/build`，其中包含 `instructions` JSON 字段。

## 操作 (Operations)

### 文档转换

```bash
# 从 DOCX 转换为 PDF
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.docx=@document.docx" \
  -F 'instructions={"parts":[{"file":"document.docx"}]}' \
  -o output.pdf

# 从 PDF 转换为 DOCX
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"output":{"type":"docx"}}' \
  -o output.docx

# 从 HTML 转换为 PDF
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "index.html=@index.html" \
  -F 'instructions={"parts":[{"html":"index.html"}]}' \
  -o output.pdf
```

支持的输入格式：PDF、DOCX、XLSX、PPTX、DOC、XLS、PPT、PPS、PPSX、ODT、RTF、HTML、JPG、PNG、TIFF、HEIC、GIF、WebP、SVG、TGA、EPS。

### 文本与数据提取

```bash
# 提取纯文本
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"output":{"type":"text"}}' \
  -o output.txt

# 将表格提取为 Excel
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"output":{"type":"xlsx"}}' \
  -o tables.xlsx
```

### 扫描文档的 OCR

```bash
# 对扫描件进行 OCR 并生成可搜索的 PDF（支持 100 多种语言）
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "scanned.pdf=@scanned.pdf" \
  -F 'instructions={"parts":[{"file":"scanned.pdf"}],"actions":[{"type":"ocr","language":"english"}]}' \
  -o searchable.pdf
```

语言：通过 ISO 639-2 代码支持 100 多种语言（例如：`eng`、`deu`、`fra`、`spa`、`jpn`、`kor`、`chi_sim`、`chi_tra`、`ara`、`hin`、`rus`）。完整语言名称如 `english` 或 `german` 也可使用。有关所有受支持的代码，请参阅 [完整 OCR 语言列表](https://www.nutrient.io/guides/document-engine/ocr/language-support/)。

### 敏感信息脱敏 (Redaction)

```bash
# 基于模式（社会安全号码 SSN、电子邮件）
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"redaction","strategy":"preset","strategyOptions":{"preset":"social-security-number"}},{"type":"redaction","strategy":"preset","strategyOptions":{"preset":"email-address"}}]}' \
  -o redacted.pdf

# 基于正则表达式
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"redaction","strategy":"regex","strategyOptions":{"regex":"\\b[A-Z]{2}\\d{6}\\b"}}]}' \
  -o redacted.pdf
```

预设 (Presets)：`social-security-number`、`email-address`、`credit-card-number`、`international-phone-number`、`north-american-phone-number`、`date`、`time`、`url`、`ipv4`、`ipv6`、`mac-address`、`us-zip-code`、`vin`。

### 添加水印 (Watermarking)

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"watermark","text":"CONFIDENTIAL","fontSize":72,"opacity":0.3,"rotation":-45}]}' \
  -o watermarked.pdf
```

### 数字签名 (Digital Signatures)

```bash
# 自签名 CMS 签名
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"sign","signatureType":"cms"}]}' \
  -o signed.pdf
```

### PDF 表单填充 (Form Filling)

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "form.pdf=@form.pdf" \
  -F 'instructions={"parts":[{"file":"form.pdf"}],"actions":[{"type":"fillForm","formFields":{"name":"Jane Smith","email":"jane@example.com","date":"2026-02-06"}}]}' \
  -o filled.pdf
```

## MCP 服务端 (代替方案)

对于原生工具集成，使用 MCP 服务端 (MCP Server) 代替 curl：

```json
{
  "mcpServers": {
    "nutrient-dws": {
      "command": "npx",
      "args": ["-y", "@nutrient-sdk/dws-mcp-server"],
      "env": {
        "NUTRIENT_DWS_API_KEY": "YOUR_API_KEY",
        "SANDBOX_PATH": "/path/to/working/directory"
      }
    }
  }
}
```

## 使用场景

- 不同格式间的文档转换（PDF、DOCX、XLSX、PPTX、HTML、图像）
- 从 PDF 提取文本、表格和键值对
- 对扫描文档或图像进行 OCR
- 在共享文档前对 PII 进行脱敏
- 在草案或机密文档中添加水印
- 对合同或协议进行数字签名
- 以编程方式填充 PDF 表单

## 相关链接

- [API 游乐场 (Playground)](https://dashboard.nutrient.io/processor-api/playground/)
- [完整 API 文档](https://www.nutrient.io/guides/dws-processor/)
- [npm MCP 服务端](https://www.npmjs.com/package/@nutrient-sdk/dws-mcp-server)
