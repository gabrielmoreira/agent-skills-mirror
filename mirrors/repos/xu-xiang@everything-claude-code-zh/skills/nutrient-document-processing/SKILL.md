---
name: nutrient-document-processing
description: 使用 Nutrient DWS API 处理、转换、OCR、提取、脱敏、签名和填充文档。支持 PDF、DOCX、XLSX、PPTX、HTML 和图像。
origin: ECC
---

# Nutrient 文档处理（Nutrient Document Processing）

使用 [Nutrient DWS Processor API](https://www.nutrient.io/api/) 处理文档。转换格式、提取文本和表格、对扫描文档进行 OCR 光学字符识别、脱敏个人身份信息（PII）、添加水印、进行数字签名以及填充 PDF 表单。

## 设置（Setup）

在 **[nutrient.io](https://dashboard.nutrient.io/sign_up/?product=processor)** 获取免费 API 密钥。

```bash
export NUTRIENT_API_KEY="pdf_live_..."
```

所有请求均以 multipart POST 形式发送至 `https://api.nutrient.io/build`，并包含一个 `instructions` JSON 字段。

## 操作（Operations）

### 转换文档（Convert Documents）

```bash
# DOCX 转 PDF
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.docx=@document.docx" \
  -F 'instructions={"parts":[{"file":"document.docx"}]}' \
  -o output.pdf

# PDF 转 DOCX
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"output":{"type":"docx"}}' \
  -o output.docx

# HTML 转 PDF
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "index.html=@index.html" \
  -F 'instructions={"parts":[{"html":"index.html"}]}' \
  -o output.pdf
```

支持的输入格式：PDF, DOCX, XLSX, PPTX, DOC, XLS, PPT, PPS, PPSX, ODT, RTF, HTML, JPG, PNG, TIFF, HEIC, GIF, WebP, SVG, TGA, EPS。

### 提取文本和数据（Extract Text and Data）

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

### OCR 扫描文档（OCR Scanned Documents）

```bash
# OCR 转为可搜索的 PDF（支持 100 多种语言）
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "scanned.pdf=@scanned.pdf" \
  -F 'instructions={"parts":[{"file":"scanned.pdf"}],"actions":[{"type":"ocr","language":"english"}]}' \
  -o searchable.pdf
```

语言：支持 100 多种语言，通过 ISO 639-2 代码指定（例如 `eng`, `deu`, `fra`, `spa`, `jpn`, `kor`, `chi_sim`, `chi_tra`, `ara`, `hin`, `rus`）。也可以使用完整的语言名称，如 `english` 或 `german`。请参阅[完整的 OCR 语言对照表](https://www.nutrient.io/guides/document-engine/ocr/language-support/)以获取所有支持的代码。

### 脱敏敏感信息（Redact Sensitive Information）

```bash
# 基于模式（SSN, 电子邮件）
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

预设（Presets）：`social-security-number`, `email-address`, `credit-card-number`, `international-phone-number`, `north-american-phone-number`, `date`, `time`, `url`, `ipv4`, `ipv6`, `mac-address`, `us-zip-code`, `vin`。

### 添加水印（Add Watermarks）

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"watermark","text":"CONFIDENTIAL","fontSize":72,"opacity":0.3,"rotation":-45}]}' \
  -o watermarked.pdf
```

### 数字签名（Digital Signatures）

```bash
# 自签名 CMS 签名
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"sign","signatureType":"cms"}]}' \
  -o signed.pdf
```

### 填充 PDF 表单（Fill PDF Forms）

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "form.pdf=@form.pdf" \
  -F 'instructions={"parts":[{"file":"form.pdf"}],"actions":[{"type":"fillForm","formFields":{"name":"Jane Smith","email":"jane@example.com","date":"2026-02-06"}}]}' \
  -o filled.pdf
```

## MCP 服务器（替代方案）

对于原生工具集成，可以使用 MCP 服务器代替 curl：

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

## 何时使用

- 在不同格式之间转换文档（PDF, DOCX, XLSX, PPTX, HTML, 图像）
- 从 PDF 中提取文本、表格或键值对
- 对扫描文档或图像进行 OCR
- 在共享文档前脱敏个人身份信息（PII）
- 为草案或机密文档添加水印
- 为合同或协议进行数字签名
- 以编程方式填充 PDF 表单

## 链接（Links）

- [API 游乐场 (API Playground)](https://dashboard.nutrient.io/processor-api/playground/)
- [完整 API 文档](https://www.nutrient.io/guides/dws-processor/)
- [npm MCP 服务器](https://www.npmjs.com/package/@nutrient-sdk/dws-mcp-server)
