# Nano Banana Image Generation Skill

使用 Chat Completions 格式生成图片的 OpenClaw Skill。

## 功能特性

- 🎨 **文生图**：根据文字描述生成图片
- 📝 **白板图**：生成手写风格的概念图、流程图
- 🖼️ **多种风格**：支持各种艺术风格和场景
- ⚡ **快速响应**：基于 GPT-4o-image 或 Gemini 3 Pro Image

## 快速开始

### 1. 基础使用

```bash
python scripts/generate_image.py \
  --prompt "画一只可爱的橙色猫咪" \
  --filename "cat.png"
```

### 2. 生成白板图

```bash
python scripts/generate_image.py \
  --prompt "生成一张白板图片，内容是OpenClaw核心概念对比表格，手写字体风格" \
  --filename "whiteboard.png"
```

### 3. 指定模型

```bash
python scripts/generate_image.py \
  --prompt "画只猫" \
  --model "gpt-4o-image" \
  --filename "cat.png"
```

## 参数说明

| 参数 | 简写 | 必需 | 说明 |
|------|------|------|------|
| `--prompt` | `-p` | ✅ | 图片描述 |
| `--filename` | `-f` | ❌ | 输出文件名（默认自动生成） |
| `--model` | `-m` | ❌ | 模型名称（默认 gemini-3-pro-image-preview） |
| `--resolution` | `-r` | ❌ | 分辨率：1K/2K/4K |
| `--api-format` | `-a` | ❌ | API 格式：openai/gemini（默认 openai） |
| `--api-key` | `-k` | ❌ | API Key（或使用环境变量） |

## 环境配置

### 方式1：使用默认配置（最简单）

脚本已内置 API 配置，直接使用即可：

```bash
python scripts/generate_image.py -p "画只猫" -f "cat.png"
```

### 方式2：使用环境变量

```bash
# 设置 API Key
export NEXTAI_API_KEY="your-api-key"

# 使用
python scripts/generate_image.py -p "画只猫" -f "cat.png"
```

### 方式3：命令行参数

```bash
python scripts/generate_image.py \
  -p "画只猫" \
  -f "cat.png" \
  -k "your-api-key"
```

## 支持的 API 格式

本 Skill 支持两种 API 格式：

### 1. OpenAI 兼容格式（默认）

```bash
# 端点
POST https://tryallapi.com/v1/chat/completions

# 使用
python scripts/generate_image.py -p "画只猫" -a openai
```

**请求格式**：
```json
{
  "model": "gemini-3-pro-image-preview",
  "messages": [
    {
      "role": "user",
      "content": "画只猫"
    }
  ]
}
```

**响应格式**：
```json
{
  "choices": [
    {
      "message": {
        "content": "![image](https://example.com/image.png)"
      }
    }
  ]
}
```

### 2. Gemini 原生格式

```bash
# 端点
POST https://tryallapi.com/v1beta/models/gemini-3-pro-image-preview:generateContent

# 使用
python scripts/generate_image.py -p "画只猫" -a gemini
```

**请求格式**：
```json
{
  "contents": [
    {
      "parts": [
        {"text": "画只猫"}
      ]
    }
  ],
  "generationConfig": {
    "responseModalities": ["IMAGE"],
    "imageConfig": {
      "imageSize": "2K"
    }
  }
}
```

**响应格式**：
```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "inlineData": {
              "data": "base64_encoded_image_data"
            }
          }
        ]
      }
    }
  ]
}
```

## 实战案例

### 案例1：社交媒体配图

```bash
python scripts/generate_image.py \
  --prompt "生成一张科技感的社交媒体封面图，主题是AI助手，蓝色渐变背景，现代简约风格" \
  --filename "social_cover.png" \
  --resolution 2K
```

### 案例2：概念白板图

```bash
python scripts/generate_image.py \
  --prompt "生成一张白板图片，手写字体风格，内容包含：
  标题：OpenClaw vs ChatGPT
  对比项：
  1. 部署方式：本地 vs 在线
  2. 文件访问：支持 vs 不支持
  3. 扩展性：Skills系统 vs 固定功能
  4. 成本：按需付费 vs 订阅制
  用箭头和框图展示" \
  --filename "comparison_whiteboard.png"
```

### 案例3：Logo 设计

```bash
python scripts/generate_image.py \
  --prompt "设计一个极简风格的AI机器人Logo，蓝色和白色配色，线条简洁，适合科技公司" \
  --filename "logo.png" \
  --resolution 1K
```

### 案例4：产品海报

```bash
python scripts/generate_image.py \
  --prompt "生成一张产品海报，展示智能手机，白色背景，专业摄影风格，高端质感" \
  --filename "product_poster.png" \
  --resolution 4K
```

### 案例5：流程图

```bash
python scripts/generate_image.py \
  --prompt "生成一张流程图，手绘风格，展示OpenClaw的工作流程：
  1. 用户发送消息
  2. Gateway接收
  3. AI处理
  4. 执行Skills
  5. 返回结果
  用箭头连接各个步骤" \
  --filename "workflow.png"
```

## 提示词技巧

### 1. 白板图提示词模板

```
生成一张白板图片，手写字体风格，内容包含：
- 标题：[主题]
- 要点1：[内容]
- 要点2：[内容]
- 要点3：[内容]
使用箭头、框图、列表等元素
```

### 2. 对比表格提示词模板

```
生成一张对比表格图片，清晰易读，包含：
- 标题：[A vs B]
- 对比维度：[维度1、维度2、维度3]
- 每个维度的对比结果
使用表格形式展示
```

### 3. 概念图提示词模板

```
生成一张概念图，展示[主题]的核心概念：
- 中心概念：[核心]
- 相关概念：[概念1、概念2、概念3]
- 概念之间的关系
使用思维导图或网络图形式
```

## API 配置说明

### 默认配置

```python
API_KEY = "sk-HoyC9xe8aB0CRC6j4EvuM0zRcN9TTYnIMjACMCeGvd95tuhQ"
BASE_URL = "https://tryallapi.com"
MODEL = "gemini-3-pro-image-preview"
```

### API 格式

使用 OpenAI Chat Completions 兼容格式：

```bash
POST https://tryallapi.com/v1/chat/completions
Content-Type: application/json
Authorization: Bearer {API_KEY}

{
  "model": "gemini-3-pro-image-preview",
  "messages": [
    {
      "role": "user",
      "content": "画只猫"
    }
  ]
}
```

### 响应格式

```json
{
  "choices": [
    {
      "message": {
        "content": "![image](https://example.com/image.png)"
      }
    }
  ]
}
```

## 成本说明

### 价格（参考）

- 1K 分辨率：约 $0.04/张
- 2K 分辨率：约 $0.08/张
- 4K 分辨率：约 $0.16/张

### 省钱技巧

1. **优先使用 1K 分辨率**：日常使用足够
2. **批量生成**：一次性生成多个版本
3. **精确提示词**：减少重复生成次数

## 常见问题

### Q1: 生成失败怎么办？

**检查以下几点**：
- API Key 是否正确
- 网络连接是否正常
- 提示词是否符合内容政策

### Q2: 如何提高生成质量？

**建议**：
- 使用详细的提示词
- 指定风格、颜色、构图
- 提供参考描述

### Q3: 支持中文提示词吗？

支持！模型对中文理解很好。

### Q4: 生成速度如何？

- 通常 10-30 秒
- 复杂图片可能需要 1-2 分钟

## 文件结构

```
skills/bananapro-image-gen/
├── SKILL.md                    # 本文档
├── README.md                   # 快速开始
├── scripts/
│   └── generate_image.py       # 生成脚本
├── examples/                   # 示例图片
│   ├── cat.png
│   ├── whiteboard.png
│   └── logo.png
└── test_output/                # 测试输出
```

## 更新日志

### v1.0.0 (2026-02-11)

- ✅ 初始版本
- ✅ 支持 Chat Completions 格式
- ✅ 支持多种模型
- ✅ 自动提取图片 URL
- ✅ 完整的错误处理

## 参考资源

- [API 文档](https://api.nextaicore.com/docs)
- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [Gemini 3 Pro Image](https://deepmind.google/models/gemini-image/pro/)

## 作者

- GitHub: [@xianyu110](https://github.com/xianyu110)
- 教程: [OpenClaw 超级个体实战指南](https://github.com/xianyu110/awesome-openclaw-tutorial)

## 许可证

MIT License
