---
name: yj-ocr
description: 元景OCR图片文字识别服务。当用户需要从图片中提取文字、识别图片内容、OCR识别、图片转文字、扫描文档识别等场景时使用。支持图片 URL 与本地文件输入,统一先下载到本地再以文件形式上传解析。即使只提到"识别图片"或"提取文字"而未明确说OCR,也应考虑使用此技能。
---

# 元景 OCR 识别技能

## 功能概述

本技能调用元景 OCR API,从图片中识别并提取文字内容。

## 核心能力

- **图片文字识别**: 从各种格式的图片中提取文本内容
- **统一处理流程**: 无论输入是 URL 还是本地路径,统一先下载到本地再以文件形式上传解析
- **详细识别结果**: 返回识别文本及其位置信息

## 使用场景

当用户需要以下操作时,主动使用此技能:

- 从图片中提取文字内容
- OCR 文字识别
- 扫描文档数字化
- 图片文字提取
- 识别图片中的文本信息
- 将图片转为可编辑文字

即使未明确提及"OCR",只要涉及图片文字识别的需求,都应考虑使用。

## API 端点

**POST** `https://maas-api.ai-yuanjing.com/openapi/v1/unicom-ocr`

## 认证方式

使用 Bearer Token 认证:
```
Authorization: Bearer {$YJ_OCR_API_KEY}
```

## 变量配置

本技能需要配置 API Key 环境变量才能正常使用。

### 必需变量

- **YJ_OCR_API_KEY**: 元景 OCR API 访问令牌(Access Token)

### 配置方式

**方式 1: 环境变量(推荐)**

```bash
# Linux/macOS
export YJ_OCR_API_KEY="your-access-token-here"

# Windows (CMD)
set YJ_OCR_API_KEY=your-access-token-here

# Windows (PowerShell)
$env:YJ_OCR_API_KEY="your-access-token-here"
```

### 获取 API Key

如需获取 Access Token,请联系元景平台管理员或访问元景控制台。

## 输入参数

请求体为 `multipart/form-data` 格式,统一使用 `file` 参数上传图片二进制:

| 参数 | 类型 | 说明 |
|------|------|------|
| `file` | binary | 图片二进制文件(必填) |

**说明**: 即使用户提供的是图片 URL,也必须先将图片下载到本地,然后以 `file` 形式上传,不直接传 URL 给 OCR 接口。

## 输出格式

成功响应包含以下字段:

```json
{
  "code": 0,
  "message": "成功",
  "version": "20240904",
  "timestamp": "1234567890",
  "id": "request-unique-id",
  "sha1": "file-sha1-hash",
  "time_cost": 1.23,
  "data": [
    {
      "page_num": 1,
      "length": 100,
      "type": "text",
      "text": "识别出的文本内容"
    }
  ]
}
```

**字段说明**:
- `code`: 状态码(0=成功, 1=图片格式异常, 2=识别出错)
- `message`: 状态描述信息
- `data`: 识别结果数组
  - `page_num`: 所在页码
  - `length`: 文本长度
  - `type`: 元素类型
  - `text`: 识别出的文本

## 使用流程

1. **配置环境变量**: 设置 YJ_OCR_API_KEY 环境变量
2. **获取本地文件**:
   - 如果输入是 URL: 先下载图片到本地临时文件
   - 如果输入已是本地路径: 直接使用
3. **调用 API**: 以 `multipart/form-data` 的 `file` 参数上传本地图片
4. **解析结果**: 从返回的 `data` 数组中提取识别的文本
5. **清理临时文件**: 如有下载产生的临时文件,处理完成后删除

## 示例用法

### 示例 1: 输入为 URL — 先下载再上传

```bash
# 1. 下载图片到本地临时文件
TMP_FILE=$(mktemp --suffix=.img)
curl -sSL "$IMAGE_URL" -o "$TMP_FILE"

# 2. 以文件形式上传到 OCR 接口
curl -X POST https://maas-api.ai-yuanjing.com/openapi/v1/unicom-ocr \
  -H "Authorization: Bearer $YJ_OCR_API_KEY" \
  -F "file=@$TMP_FILE"

# 3. 清理临时文件
rm -f "$TMP_FILE"
```

### 示例 2: 输入为本地文件 — 直接上传

```bash
curl -X POST https://maas-api.ai-yuanjing.com/openapi/v1/unicom-ocr \
  -H "Authorization: Bearer $YJ_OCR_API_KEY" \
  -F "file=@/path/to/image.png"
```

## Python 示例

```python
import os
import tempfile
import requests

OCR_URL = "https://maas-api.ai-yuanjing.com/openapi/v1/unicom-ocr"


def _get_headers():
    access_token = os.getenv('YJ_OCR_API_KEY')
    if not access_token:
        raise ValueError("未设置 YJ_OCR_API_KEY 环境变量")
    return {"Authorization": f"Bearer {access_token}"}


def download_image(image_url: str) -> str:
    """下载图片到本地临时文件,返回临时文件路径"""
    resp = requests.get(image_url, stream=True, timeout=30)
    resp.raise_for_status()
    fd, tmp_path = tempfile.mkstemp(suffix=".img")
    with os.fdopen(fd, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return tmp_path


def ocr_from_file(file_path: str) -> dict:
    """上传本地文件进行 OCR"""
    with open(file_path, 'rb') as f:
        files = {"file": f}
        response = requests.post(OCR_URL, headers=_get_headers(), files=files)
    return response.json()


def ocr_from_url(image_url: str) -> dict:
    """输入 URL:先下载到本地,再以文件形式上传"""
    tmp_path = download_image(image_url)
    try:
        return ocr_from_file(tmp_path)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
```

## 错误处理

- **code = 1**: 图片格式异常,检查图片是否损坏或格式不支持
- **code = 2**: 图片无内容或识别出错,可能是图片质量问题

## 注意事项

1. **环境变量配置**: 必须设置 YJ_OCR_API_KEY 环境变量,不要在代码中硬编码 API Key
2. **图片格式**: 确保图片格式正确,推荐使用常见格式(JPG, PNG等)
3. **网络连接**: 确保能够访问 maas-api.ai-yuanjing.com
4. **结果处理**: 返回的文本可能包含多个元素,需要遍历 `data` 数组
5. **安全提示**: 将 API Key 添加到 .gitignore,避免提交到版本控制系统

## 快速集成

如果用户提供了图片文件或 URL,按以下步骤处理:

1. 检查 YJ_OCR_API_KEY 环境变量是否已设置
2. 判断输入类型(URL/本地文件)
3. 如果是 URL,先下载到本地临时文件;如果已是本地路径则跳过
4. 统一以 `file` 参数上传到 OCR 接口
5. 发送请求并解析结果,提取并展示识别的文本内容
6. 清理下载产生的临时文件

## 输出示例

假设用户上传了一张包含文字的图片,返回结果可以这样展示:

```
识别成功!共找到 3 段文本:

[第1段] 
文本内容: 这是第一段文字
长度: 8 字符

[第2段]
文本内容: 这是第二段文字  
长度: 8 字符

[第3段]
文本内容: 这是第三段文字
长度: 8 字符

处理耗时: 1.23 秒
请求ID: request-unique-id
```
