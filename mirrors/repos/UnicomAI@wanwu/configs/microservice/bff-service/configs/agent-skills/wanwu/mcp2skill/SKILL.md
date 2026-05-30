---
name: mcp2skill
description: 将 MCP Server 的工具列表转换为 Skill 格式的结构化 Markdown 文档
---

# mcp2skill

将 MCP Server 的工具定义转换为 Skill 格式，生成 SKILL.md 概览和每个工具的详情文档。

## MCP Server

- **Transport:** 支持 streamable（默认）和 sse 两种传输方式

## How to Use This Skill

1. 准备 MCP Server 的连接信息（URL + 传输类型）
2. 调用 `mcp2skill` 二进制进行转换
3. 在输出目录中查看生成的 Skill 文件

## Quick Start

```bash
# 通过 streamable URL 转换
mcp2skill name=天气查询 streamableUrl=http://192.168.0.21:8081/mcp/server/streamable?key=xxx description="查询天气" output=./skills

# 通过 SSE URL 转换
mcp2skill name=天气查询 sseUrl=http://192.168.0.21:8081/mcp/server/sse?key=xxx transport=sse description="查询天气" output=./skills
```

## Tools

| Name | Description | Details |
|------|-------------|----------|
| `mcp2skill` | 连接 MCP Server 获取工具列表并转换为 Skill 格式 | [View](references/operations/mcp2skill.md) |
