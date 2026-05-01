# MCP 工具详细定义

本文档详细定义小遥搜索 MCP 服务器提供的 5 个搜索工具。

## 1. semantic_search

### 功能描述

基于 BGE-M3 向量模型的语义搜索，支持自然语言查询理解。

### 适用场景

- 用自然语言描述搜索内容
- 需要理解查询意图
- 查找语义相关的文档

### 参数定义

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| query | string | 是 | - | 搜索关键词（1-500字符） |
| limit | int | 否 | 20 | 返回结果数量（1-100） |
| threshold | float | 否 | 0.7 | 相似度阈值（0.0-1.0） |
| file_types | string[] | 否 | null | 文件类型过滤 |

### 返回格式

```json
{
  "total": 10,
  "search_time": 0.523,
  "results": [
    {
      "file_name": "example.md",
      "file_path": "D:/docs/example.md",
      "file_type": "markdown",
      "relevance_score": 0.95,
      "preview_text": "文档预览..."
    }
  ]
}
```

### 错误处理

| 错误码 | 说明 |
|--------|------|
| query 长度超限 | 返回 400 错误 |
| limit 超出范围 | 返回 400 错误 |

---

## 2. fulltext_search

### 功能描述

基于 Whoosh 的全文搜索，支持精确关键词匹配和中文分词。

### 适用场景

- 查找特定关键词
- 搜索代码片段
- 精确短语匹配

### 参数定义

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| query | string | 是 | - | 搜索关键词（1-500字符） |
| limit | int | 否 | 20 | 返回结果数量（1-100） |
| file_types | string[] | 否 | null | 文件类型过滤 |

### 返回格式

```json
{
  "total": 10,
  "search_time": 0.123,
  "results": [
    {
      "file_name": "example.py",
      "file_path": "D:/code/example.py",
      "file_type": "python",
      "relevance_score": 1.0,
      "highlight": "...async def main():...",
      "preview_text": "代码预览..."
    }
  ]
}
```

---

## 3. hybrid_search

### 功能描述

结合语义搜索和全文搜索，使用 RRF（Reciprocal Rank Fusion）算法融合结果。

### 适用场景

- 需要全面搜索结果
- 不确定使用哪种搜索方式
- 希望获得更准确的排序

### 参数定义

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| query | string | 是 | - | 搜索关键词（1-500字符） |
| limit | int | 否 | 20 | 返回结果数量（1-100） |
| threshold | float | 否 | 0.7 | 相似度阈值（0.0-1.0） |
| file_types | string[] | 否 | null | 文件类型过滤 |

### 返回格式

```json
{
  "total": 20,
  "search_time": 0.678,
  "results": [
    {
      "file_name": "example.md",
      "file_path": "D:/docs/example.md",
      "file_type": "markdown",
      "relevance_score": 0.95,
      "source": "semantic",
      "preview_text": "文档预览..."
    },
    {
      "file_name": "code.py",
      "file_path": "D:/code/code.py",
      "file_type": "python",
      "relevance_score": 0.92,
      "source": "fulltext",
      "highlight": "...关键词匹配...",
      "preview_text": "代码预览..."
    }
  ]
}
```

---

## 4. image_search

### 功能描述

基于 CN-CLIP 模型的图像搜索，通过图片查找相似内容。

### 适用场景

- 用参考图查找相似图片
- 查找包含相似元素的文档
- 设计素材搜索

### 参数定义

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| image_path | string | 是 | - | 图片绝对路径 |
| limit | int | 否 | 20 | 返回结果数量（1-100） |
| threshold | float | 否 | 0.7 | 相似度阈值（0.0-1.0） |

### 支持格式

- jpg, jpeg, png, gif, bmp, webp

### 文件限制

- 最大：10MB
- 最小：1KB

### 返回格式

```json
{
  "total": 10,
  "search_time": 1.245,
  "results": [
    {
      "file_name": "design_v1.png",
      "file_path": "D:/design/design_v1.png",
      "file_type": "image",
      "relevance_score": 0.92,
      "preview_text": "设计稿版本1..."
    }
  ],
  "input_info": {
    "file_path": "C:/Users/test/reference.png",
    "file_size_kb": 256.5,
    "file_format": ".png"
  }
}
```

### 错误处理

| 错误 | 说明 |
|------|------|
| 文件不存在 | 返回错误提示 |
| 文件过大 | 返回错误提示（>10MB） |
| 不支持格式 | 返回错误提示 |

---

## 5. voice_search

### 功能描述

基于 FasterWhisper 的语音搜索，将语音转为文字后进行搜索。

### 适用场景

- 语音输入搜索
- 快速记录查找
- 会议记录搜索

### 参数定义

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| audio_path | string | 是 | - | 音频绝对路径 |
| search_type | string | 否 | semantic | 搜索类型 |
| limit | int | 否 | 20 | 返回结果数量（1-100） |
| threshold | float | 否 | 0.7 | 相似度阈值（0.0-1.0） |
| file_types | string[] | 否 | null | 文件类型过滤 |
| enable_query_enhancement | bool | 否 | true | 启用LLM查询增强 |

### search_type 选项

- semantic：语义搜索
- fulltext：全文搜索
- hybrid：混合搜索

### 支持格式

- wav, mp3, m4a, flac, aac, ogg, opus

### 文件限制

- 最大：10MB（约30秒音频）
- 最小：1KB

### 返回格式

```json
{
  "total": 3,
  "search_time": 2.567,
  "results": [
    {
      "file_name": "meeting.md",
      "file_path": "D:/meetings/meeting.md",
      "file_type": "markdown",
      "relevance_score": 0.88,
      "preview_text": "会议记录..."
    }
  ],
  "transcription": {
    "text": "帮我找一下上周的会议记录",
    "enhanced_query": "上周会议记录",
    "language": "zh",
    "duration": 3.5
  },
  "input_info": {
    "file_path": "C:/Users/test/voice.mp3",
    "file_size_kb": 128.0,
    "file_format": ".mp3"
  }
}
```

### 错误处理

| 错误 | 说明 |
|------|------|
| 语音识别失败 | 返回错误提示 |
| 文件不存在 | 返回错误提示 |
| 文件过大 | 返回错误提示（>10MB） |
| 不支持格式 | 返回错误提示 |
