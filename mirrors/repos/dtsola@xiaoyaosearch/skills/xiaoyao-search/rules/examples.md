# 使用示例

本文档提供小遥搜索 MCP 工具的详细使用示例。

## 示例 1：语义搜索

### 场景

用户想要查找关于"机器学习算法优化"的文档。

### 调用

```python
semantic_search(
    query="机器学习算法优化",
    limit=10,
    threshold=0.7
)
```

### 响应

```json
{
  "total": 10,
  "search_time": 0.523,
  "results": [
    {
      "file_name": "ml_optimization_guide.md",
      "file_path": "D:/docs/ml_optimization_guide.md",
      "file_type": "markdown",
      "relevance_score": 0.95,
      "preview_text": "机器学习算法优化指南..."
    },
    {
      "file_name": "gradient_descent.py",
      "file_path": "D:/code/gradient_descent.py",
      "file_type": "python",
      "relevance_score": 0.89,
      "preview_text": "梯度下降算法实现..."
    }
  ]
}
```

---

## 示例 2：全文搜索代码

### 场景

用户想找包含 `async def` 的 Python 文件。

### 调用

```python
fulltext_search(
    query="async def",
    limit=20,
    file_types=["python"]
)
```

### 响应

```json
{
  "total": 5,
  "search_time": 0.123,
  "results": [
    {
      "file_name": "async_handler.py",
      "file_path": "D:/code/async_handler.py",
      "file_type": "python",
      "relevance_score": 1.0,
      "highlight": "...async def process_request():...",
      "preview_text": "异步请求处理函数..."
    }
  ]
}
```

---

## 示例 3：图像搜索

### 场景

用户有一张参考图片，想要找相似的设计稿。

### 调用

```python
image_search(
    image_path="C:/Users/test/reference.png",
    limit=10
)
```

### 响应

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

---

## 示例 4：语音搜索

### 场景

用户通过语音输入"帮我找一下上周的会议记录"。

### 调用

```python
voice_search(
    audio_path="C:/Users/test/voice.mp3",
    search_type="semantic"
)
```

### 响应

```json
{
  "total": 3,
  "search_time": 2.567,
  "results": [
    {
      "file_name": "meeting_2024_01_15.md",
      "file_path": "D:/meetings/meeting_2024_01_15.md",
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

---

## 示例 5：混合搜索

### 场景

用户想要全面搜索"Vue3 组件开发"的资料。

### 调用

```python
hybrid_search(
    query="Vue3 组件开发",
    limit=20,
    threshold=0.6
)
```

### 响应

```json
{
  "total": 20,
  "search_time": 0.678,
  "results": [
    {
      "file_name": "vue3_components.md",
      "file_path": "D:/docs/vue3_components.md",
      "file_type": "markdown",
      "relevance_score": 0.95,
      "source": "semantic",
      "preview_text": "Vue3 组件开发指南..."
    },
    {
      "file_name": "Component.vue",
      "file_path": "D:/code/Component.vue",
      "file_type": "vue",
      "relevance_score": 0.92,
      "source": "fulltext",
      "highlight": "...<script setup>...组件...",
      "preview_text": "Vue3 组件示例..."
    }
  ]
}
```

---

## 最佳实践

### 1. 选择合适的搜索类型

| 场景 | 推荐搜索类型 |
|------|-------------|
| 自然语言描述 | semantic_search |
| 精确关键词 | fulltext_search |
| 全面搜索 | hybrid_search |
| 图片参考 | image_search |
| 语音输入 | voice_search |

### 2. 调整阈值

- 高阈值（>0.8）：精确匹配
- 中阈值（0.5-0.8）：平衡
- 低阈值（<0.5）：更多结果

### 3. 文件类型过滤

```python
# 只搜索文档
file_types=["pdf", "doc", "docx", "md", "txt"]

# 只搜索代码
file_types=["py", "js", "ts", "java", "go"]

# 只搜索图片
file_types=["jpg", "png", "gif"]
```

### 4. 限制结果数量

- 详细研究：limit=10-20
- 快速浏览：limit=5
- 全面搜索：limit=50-100
