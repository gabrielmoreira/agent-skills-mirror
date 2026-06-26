# 签证材料翻译器 (Visa Document Translator)

自动将签证申请材料图片翻译成专业的英文 PDF 文档。

## 特性 (Features)

- 🔄 **自动 OCR**：支持多种光学字符识别（OCR）方法（macOS Vision, EasyOCR, Tesseract）
- 📄 **双语 PDF**：原始图片 + 专业英文翻译
- 🌍 **多语言支持**：支持中文及其他语言
- 📋 **专业格式**：适用于官方签证申请
- 🚀 **全自动化**：无需人工干预

## 支持的文档 (Supported Documents)

- 存款证明 (Bank deposit certificates)
- 在职证明 (Employment certificates)
- 退休证明 (Retirement certificates)
- 收入证明 (Income certificates)
- 房产证明 (Property certificates)
- 营业执照 (Business licenses)
- 身份证与护照 (ID cards and passports)

## 用法 (Usage)

```bash
/visa-doc-translate <image-file>
```

### 示例 (Examples)

```bash
/visa-doc-translate RetirementCertificate.PNG
/visa-doc-translate BankStatement.HEIC
/visa-doc-translate EmploymentLetter.jpg
```

## 输出 (Output)

生成名为 `<filename>_Translated.pdf` 的文件，包含：
- **第 1 页**：原始文档图片（居中，A4 尺寸）
- **第 2 页**：专业的英文翻译

## 要求 (Requirements)

### Python 库
```bash
pip install pillow reportlab
```

### OCR 引擎（需安装以下之一）

**macOS (推荐)**：
```bash
pip install pyobjc-framework-Vision pyobjc-framework-Quartz
```

**跨平台**：
```bash
pip install easyocr
```

**Tesseract**：
```bash
brew install tesseract tesseract-lang
pip install pytesseract
```

## 工作原理 (How It Works)

1. 必要时将 HEIC 格式转换为 PNG
2. 检查并应用 EXIF 旋转
3. 使用可用的 OCR 方法提取文本
4. 翻译为专业的英文
5. 生成双语 PDF

## 适用场景 (Perfect For)

- 🇦🇺 澳大利亚签证申请
- 🇺🇸 美国签证申请
- 🇨🇦 加拿大签证申请
- 🇬🇧 英国签证申请
- 🇪🇺 欧盟签证申请

## 许可 (License)

MIT
