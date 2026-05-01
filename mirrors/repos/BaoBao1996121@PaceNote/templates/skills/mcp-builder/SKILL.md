---
name: mcp-builder
description: |
  MCP Server 开发指南 - 帮助创建高质量的 MCP (Model Context Protocol) 服务器。
  当需要构建 MCP 服务器来集成外部 API 或服务时使用，支持 Python (FastMCP) 和 Node/TypeScript (MCP SDK)。
  触发关键词: mcp开发, mcp服务器, model context protocol, 构建mcp, 创建mcp
---

# MCP Server 开发指南

## 执行声明规范

**每次使用本 Skill 时，必须向用户明确告知：**

### 开始执行时
```
🔧 **正在执行: MCP Builder** (`#mcp-builder`)

✅ 已加载 Skill 指引
⭕ 当前步骤: [步骤描述]
```

### 执行完成时
```
✅ **执行完成**: MCP Builder

参考来源:
- Skill: `#mcp-builder`
- 参考文档: [使用的参考文档]

产出物: [MCP Server 代码/配置]
```

---

## 概述

创建 MCP (Model Context Protocol) 服务器，使 LLM 能够通过精心设计的工具与外部服务交互。
MCP 服务器的质量取决于它如何有效地帮助 LLM 完成实际任务。

---

## 高层工作流

创建高质量 MCP 服务器涉及四个主要阶段：

### 阶段1: 深度研究和规划

#### 1.1 理解现代 MCP 设计

**API 覆盖 vs 工作流工具**:
平衡全面的 API 端点覆盖与专业工作流工具。当不确定时，优先考虑全面的 API 覆盖。

**工具命名和可发现性**:
清晰、描述性的工具名称帮助代理快速找到正确的工具。使用一致的前缀（如 `github_create_issue`、`github_list_repos`）和面向动作的命名。

**可操作的错误消息**:
错误消息应引导代理找到解决方案，包含具体建议和后续步骤。

#### 1.2 研究 MCP 协议文档

**导航 MCP 规范**:
- 站点地图: `https://modelcontextprotocol.io/sitemap.xml`
- 使用 `.md` 后缀获取 Markdown 格式页面

**关键页面**:
- 规范概述和架构
- 传输机制 (streamable HTTP, stdio)
- 工具、资源和提示定义

#### 1.3 研究框架文档

**推荐技术栈**:
- **语言**: TypeScript（高质量 SDK 支持，良好的执行环境兼容性）
- **传输**: 远程服务器使用 Streamable HTTP，本地服务器使用 stdio

**框架文档**:
- [MCP 最佳实践](reference/mcp_best_practices.md)
- [TypeScript 指南](reference/node_mcp_server.md)
- [Python 指南](reference/python_mcp_server.md)

#### 1.4 规划实现

**理解 API**: 查看服务的 API 文档，识别关键端点、认证要求和数据模型。

**工具选择**: 优先考虑全面的 API 覆盖。列出要实现的端点，从最常见的操作开始。

---

### 阶段2: 实现

#### 2.1 设置项目结构

详见语言特定指南：
- [TypeScript 指南](reference/node_mcp_server.md) - 项目结构、package.json、tsconfig.json
- [Python 指南](reference/python_mcp_server.md) - 模块组织、依赖项

#### 2.2 实现核心基础设施

创建共享工具：
- 带认证的 API 客户端
- 错误处理助手
- 响应格式化 (JSON/Markdown)
- 分页支持

#### 2.3 实现工具

对于每个工具：

**输入 Schema**:
- 使用 Zod (TypeScript) 或 Pydantic (Python)
- 包含约束和清晰的描述
- 在字段描述中添加示例

**输出 Schema**:
- 尽可能定义 `outputSchema`
- 在工具响应中使用 `structuredContent`

**工具描述**:
- 功能的简洁摘要
- 参数描述
- 返回类型 schema

**注解**:
- `readOnlyHint`: true/false
- `destructiveHint`: true/false
- `idempotentHint`: true/false
- `openWorldHint`: true/false

---

### 阶段3: 审查和测试

#### 3.1 代码质量

审查：
- 无重复代码 (DRY 原则)
- 一致的错误处理
- 完整的类型覆盖
- 清晰的工具描述

#### 3.2 构建和测试

**TypeScript**:
```bash
npm run build
npx @modelcontextprotocol/inspector
```

**Python**:
```bash
python -m py_compile your_server.py
```

---

### 阶段4: 创建评估

实现 MCP 服务器后，创建全面的评估来测试其有效性。

详见 [评估指南](reference/evaluation.md)。

---

## 快速参考

### 服务器命名
- **Python**: `{service}_mcp` (如 `slack_mcp`)
- **Node/TypeScript**: `{service}-mcp-server` (如 `slack-mcp-server`)

### 工具命名
- 使用 snake_case 加服务前缀
- 格式: `{service}_{action}_{resource}`
- 示例: `slack_send_message`, `github_create_issue`

### 响应格式
- 支持 JSON 和 Markdown 两种格式
- JSON 用于程序化处理
- Markdown 用于人类可读性

### 分页
- 始终尊重 `limit` 参数
- 返回 `has_more`, `next_offset`, `total_count`
- 默认 20-50 项

### 传输选择

| 标准 | stdio | Streamable HTTP |
|------|-------|-----------------|
| **部署** | 本地 | 远程 |
| **客户端** | 单个 | 多个 |
| **复杂度** | 低 | 中 |
| **实时** | 否 | 是 |

---

## 参考文档

加载这些资源以获取详细指导：

### 核心 MCP 文档
- [MCP 最佳实践](reference/mcp_best_practices.md) - 通用 MCP 指南

### 语言特定实现指南
- [Python 实现指南](reference/python_mcp_server.md) - FastMCP 完整指南
- [TypeScript 实现指南](reference/node_mcp_server.md) - TypeScript SDK 完整指南

### 评估指南
- [评估指南](reference/evaluation.md) - 完整的评估创建指南

---

## Azure DevOps MCP 示例

当前项目使用 Azure DevOps MCP，以下是配置示例：

### VS Code 配置 (.vscode/mcp.json)

```json
{
  "mcpServers": {
    "azuredevops": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-azure-devops"],
      "env": {
        "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/your-org",
        "AZURE_DEVOPS_AUTH_METHOD": "pat",
        "AZURE_DEVOPS_PAT": "${env:AZURE_DEVOPS_PAT}"
      }
    }
  }
}
```

### 工具调用示例

```typescript
// 搜索代码 - 必须指定仓库过滤器
mcp_azuredevops_search_code({
  searchText: "IDataLoadService",
  filters: { Repository: ["{{PLATFORM_REPO}}"] }
});

// 获取文件内容 - 必须指定版本
mcp_azuredevops_get_file_content({
  repositoryId: "{{PLATFORM_REPO}}",
  path: "/DataLoad/src/Service.cs",
  versionType: "branch",
  version: "{{PLATFORM_BRANCH}}"
});

// 获取工作项
mcp_azuredevops_get_work_item({
  id: 1073716
});
```

---

## 参考来源声明

使用本 Skill 时，必须声明参考来源：

```markdown
📚 **参考来源**:
- Skill: `#mcp-builder`
- 参考文档: [使用的参考文档名称]
- 外部资源: [MCP 官方文档等]
```
