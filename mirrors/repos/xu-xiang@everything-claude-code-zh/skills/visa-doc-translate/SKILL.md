---
name: visa-doc-translate
description: 将签证申请文件（图像）翻译成英文，并创建包含原文和译文的双语 PDF。
---

你正在协助翻译用于签证申请的文件。

## 指令 (Instructions)

当用户提供图像文件路径时，**自动 (AUTOMATICALLY)** 执行以下步骤，**无需 (WITHOUT)** 请求确认：

1. **图像转换 (Image Conversion)**：如果文件是 HEIC 格式，使用 `sips -s format png <input> --out <output>` 将其转换为 PNG。

2. **图像旋转 (Image Rotation)**：
   - 检查 EXIF 方向数据。
   - 根据 EXIF 数据自动旋转图像。
   - 如果 EXIF 方向为 6，则逆时针旋转 90 度。
   - 根据需要应用额外的旋转（如果文档看起来是倒置的，尝试旋转 180 度）。

3. **OCR 文本提取 (OCR Text Extraction)**：
   - 自动尝试多种 OCR 方法：
     - macOS Vision 框架（macOS 首选）。
     - EasyOCR（跨平台，无需 tesseract）。
     - Tesseract OCR（如果可用）。
   - 从文档中提取所有文本信息。
   - 识别文档类型（存款证明、在职证明、退休证明等）。

4. **翻译 (Translation)**：
   - 以专业水准将所有文本内容翻译成英文。
   - 保持原始文档的结构和格式。
   - 使用适用于签证申请的专业术语。
   - 保持专有名词为原语言，并在括号内注明英文。
   - 对于中文姓名，使用拼音格式（例如：WU Zhengye）。
   - 准确保留所有数字、日期和金额。

5. **PDF 生成 (PDF Generation)**：
   - 使用 PIL 和 reportlab 库创建一个 Python 脚本。
   - 第 1 页：显示旋转后的原始图像，居中并缩放以适应 A4 页面。
   - 第 2 页：显示具有正确格式的英文翻译：
     - 标题居中且加粗。
     - 内容左对齐，并保持适当的间距。
     - 适用于官方文件的专业布局。
   - 在底部添加注释："This is a certified English translation of the original document"。
   - 执行脚本生成 PDF。

6. **输出 (Output)**：在同一目录下创建一个名为 `<original_filename>_Translated.pdf` 的 PDF 文件。

## 支持的文件类型 (Supported Documents)

- 银行存款证明 (Bank deposit certificates)
- 收入证明 (Income certificates)
- 在职证明 (Employment certificates)
- 退休证明 (Retirement certificates)
- 房产证明 (Property certificates)
- 营业执照 (Business licenses)
- 身份证和护照 (ID cards and passports)
- 其他官方文件

## 技术实现 (Technical Implementation)

### OCR 方法（按顺序尝试）

1. **macOS Vision 框架**（仅限 macOS）：
   ```python
   import Vision
   from Foundation import NSURL
   ```

2. **EasyOCR**（跨平台）：
   ```bash
   pip install easyocr
   ```

3. **Tesseract OCR**（如果可用）：
   ```bash
   brew install tesseract tesseract-lang
   pip install pytesseract
   ```

### 所需 Python 库

```bash
pip install pillow reportlab
```

对于 macOS Vision 框架：
```bash
pip install pyobjc-framework-Vision pyobjc-framework-Quartz
```

## 重要指南 (Important Guidelines)

- **不要**在每个步骤都请求用户确认。
- 自动确定最佳旋转角度。
- 如果一种 OCR 方法失败，请尝试多种方法。
- 确保所有数字、日期和金额都得到准确翻译。
- 使用整洁、专业的格式。
- 完成整个过程并报告最终 PDF 的位置。

## 使用示例 (Example Usage)

```bash
/visa-doc-translate RetirementCertificate.PNG
/visa-doc-translate BankStatement.HEIC
/visa-doc-translate EmploymentLetter.jpg
```

## 输出示例 (Output Example)

该技能（Skill）将：
1. 使用可用的 OCR 方法提取文本。
2. 翻译成专业的英文。
3. 生成带有以下内容的 `<filename>_Translated.pdf`：
   - 第 1 页：原始文档图像。
   - 第 2 页：专业的英文翻译。

非常适合向澳大利亚、美国、加拿大、英国和其他需要翻译文件的国家提交签证申请。
