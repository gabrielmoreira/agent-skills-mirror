# 连接配置指南

本文档说明如何配置各种 AI 助手连接到小遥搜索 MCP 服务器。

## MCP SSE 端点

**地址**：`http://127.0.0.1:8000/mcp`

## Claude Code / Claude Desktop 配置

### Windows

编辑文件：`%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp",
      "type": "sse"
    }
  }
}
```

### macOS

编辑文件：`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp",
      "type": "sse"
    }
  }
}
```

### Linux

编辑文件：`~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp",
      "type": "sse"
    }
  }
}
```

## VS Code (with MCP extension)

打开设置，添加以下配置：

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp",
      "type": "sse"
    }
  }
}
```

## Cursor 配置

编辑 `~/.cursor/settings.json` 或在设置中添加：

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp",
      "type": "sse"
    }
  }
}
```

## OpenCode 配置

编辑配置文件（通常在 `~/.opencode/config.json`）：

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp",
      "type": "sse"
    }
  }
}
```

## Codex 配置

编辑 `~/.codex/config.json`：

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp",
      "type": "sse"
    }
  }
}
```

## 环境变量配置

在 `backend/.env` 文件中配置：

```bash
# MCP 服务器配置
MCP_SSE_ENABLED=true
MCP_SERVER_NAME=xiaoyao-search
MCP_SERVER_VERSION=1.0.0
MCP_DEFAULT_LIMIT=20
MCP_DEFAULT_THRESHOLD=0.5
MCP_VOICE_ENABLED=true
MCP_LOG_LEVEL=INFO
```

## 连接测试

### 测试 1：检查后端服务

```bash
curl http://127.0.0.1:8000/api/system/health
```

预期响应：
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 测试 2：检查 MCP 端点

```bash
curl http://127.0.0.1:8000/mcp
```

预期响应：SSE 连接响应（会保持连接打开）

### 测试 3：使用 MCP CLI 测试

```bash
# 安装 mcp CLI
pip install mcp[cli]

# 测试服务器连接
mcp dev python -c "
from app.mcp.server import create_mcp_server
mcp = create_mcp_server()
print([t.name for t in mcp._tools])
"
```

## 故障排查

### 问题：连接失败

1. 确认后端服务正在运行
2. 检查端口 8000 是否被占用
3. 确认防火墙允许访问
4. 检查 URL 是否正确

### 问题：工具不可见

1. 重启 AI 助手
2. 检查 MCP 配置是否保存成功
3. 查看 AI 助手日志

### 问题：搜索返回空结果

1. 确认索引已构建
2. 降低 threshold 值
3. 使用混合搜索尝试

### 问题：图像/语音搜索失败

1. 确认文件路径为绝对路径
2. 检查文件格式是否支持
3. 检查文件大小是否在限制内（10MB）
