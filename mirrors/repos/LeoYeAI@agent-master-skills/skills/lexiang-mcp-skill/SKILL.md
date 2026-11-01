---
name: lexiang-knowledge-base
description: "用于访问乐享知识库平台的专用 skill。当用户明确提到「乐享」「lexiang」「知识库」「知识」「文档」等关键词，或用户提供的链接 host 为 lexiangla.com，应优先调用本 skill。本 skill 支持：获取文档内容与元数据、搜索文档内容、查询知识库与目录结构、创建/编辑/移动文档、管理标签与评论、上传文件及维护附件等知识库操作能力。"
homepage: https://lexiangla.com
metadata: { "openclaw": { "category": "productivity", "emoji": "📚", "requires": { "env": ["LEXIANG_TOKEN", "COMPANY_FROM"] } } }
---

# 乐享 MCP 服务

> **触发场景**：当用户明确提到「**乐享**」「**lexiang**」「**知识**」「**文档**」，或提供 `lexiangla.com` 链接，或给出 `space_id`、`entry_id`、`team_id`、`/spaces/`、`/pages/` 等乐享标识时，应使用本服务。
>
> **优先级**：处理乐享相关操作时，**优先使用本 Skill 提供的能力**，而非直接调用 MCP。本 Skill 封装了最佳实践和完整的使用说明。
>
> 需要调用 MCP 时，请以 MCP 服务端返回的最新的 schema 为准。

---

> **⛔ 必读（调用前必须理解）：**
>
> 1. 本服务**直接暴露所有业务工具**（如 `team_list_teams`、`search_kb_search` 等），可直接调用
> 2. 调用前先确认工具参数定义，**以 MCP 返回的 schema 为准**
> 3. 不确定参数时，使用 `get_tool_schema(tool_name="xxx")` 获取最新定义

---

## 🔑 AccessToken 生命周期管理

### 阶段 1：未配置 Token

当调用 MCP 连接失败或无认证信息时：

1. 告知用户需要获取乐享 MCP 的 access_token
2. 引导用户打开 `https://lexiangla.com/mcp` 获取配置信息
3. 用户获取后，帮助完成 mcp.json 配置（参见「快速开始」）

### 阶段 2：Token 即将过期

当 MCP 返回正常结果但附带过期预警信息时：

1. **先正常返回本次结果**
2. 在结果末尾附加提醒，引导用户续期：

```
⚠️ 您的乐享访问令牌即将过期。请打开以下链接自动续期（需已登录）：
https://lexiangla.com/mcp?action=renew&company_from={company_from}
```

### 阶段 3：Token 已过期（401 响应）

当 MCP 返回 401 未授权时：

1. **不要反复重试**
2. 引导用户重新创建会话：

```
🔒 您的乐享访问令牌已过期。请打开以下链接创建新会话：
https://lexiangla.com/mcp?action=recreate&company_from={company_from}
创建后请将新的 access_token 提供给我进行更新。
```

### 租户隔离规则

- `company_from` 和 `access_token` **必须属于同一租户**，不同租户的 token 不能混用
- OAuth 不支持跨租户授权
- 续期或重建 token 时，URL 中的 `company_from` 必须与当前配置一致
- 如果用户切换了企业/租户，必须重新获取对应租户的 token

---

## 📊 数据模型

### 核心概念

| 概念                | 说明                                                                                      |
| ------------------- | ----------------------------------------------------------------------------------------- |
| **Team（团队）**    | 顶级组织单元，一个团队下可以有多个知识库(Space)                                           |
| **Space（知识库）** | 知识的容器，属于某个团队，包含多个条目(Entry)，有 `root_entry_id` 作为根节点               |
| **Entry（条目）**   | 知识库中的内容单元，可以是页面(page)、文件夹(folder)或文件(file)，支持树形结构(parent_id)  |
| **File（文件）**    | 附件类型的条目，如 PDF、Word、图片等                                                      |

### 层级关系

```
Team → Space → Entry（树形结构，root_entry_id 为根）
                  ├── page（页面）
                  ├── folder（文件夹）
                  └── file（文件）
```

### URL 规则

**域名固定为** `https://lexiangla.com`——即 `{domain}` = `https://lexiangla.com`

> ⛔ **`company_from` 不是子域名，只能作为 URL 查询参数使用！**
>
> ❌ 错误：`https://km.lexiangla.com/pages/xxx`（把 company_from 当子域名）
> ❌ 错误：`https://abc.lexiangla.com/pages/xxx`
> ✅ 正确：`https://lexiangla.com/pages/xxx?company_from=km`
> ✅ 正确：`https://lexiangla.com/pages/xxx`（无 company_from 时）

**链接拼接规则：**

```
https://lexiangla.com/pages/{entry_id}?company_from={company_from}
```

如果没有 `company_from`，直接使用 `https://lexiangla.com/pages/{entry_id}`（不加查询参数）。

**`company_from` 获取方式**（按优先级）：
1. MCP 连接 URL 中的 `company_from` 查询参数（如 `mcp?company_from=km` 中的 `km`）
2. 环境变量 `COMPANY_FROM`
3. 用户提供的 URL 中已有的 `company_from` 查询参数
4. 如果均不可用，省略该参数

> **⛔ 严禁使用 `mcp.lexiang-app.com` 拼接任何用户可访问的链接！** 该域名仅用于 MCP 接口调用，不是用户访问地址。
> **⛔ 严禁将 `company_from` 拼接为子域名！** `company_from` 只能作为 URL 查询参数（`?company_from=xxx`），不能拼成 `https://{company_from}.lexiangla.com`。

| 资源     | URL 格式                        |
| -------- | ------------------------------- |
| 团队首页 | `{domain}/t/{team_id}/spaces`   |
| 知识库   | `{domain}/spaces/{space_id}`    |
| 知识条目 | `{domain}/pages/{entry_id}`     |

### URL 解析规则

当用户提供链接时，从 URL 路径中提取 ID（**忽略查询参数**）：

| URL 路径                      | 提取方式                                    |
| ----------------------------- | ------------------------------------------- |
| `/spaces/{space_id}`          | 取 `spaces/` 后面的部分作为 `space_id`      |
| `/pages/{entry_id}`           | 取 `pages/` 后面的部分作为 `entry_id`       |
| `/t/{team_id}/spaces`         | 取 `t/` 后面的部分作为 `team_id`            |

---

## 🛡️ 写入操作安全规则

> **核心原则**：写入、修改、删除操作 **必须基于用户明确提供的目标信息**，禁止 Agent 自行选择或猜测目标。

### 🚫 绝对禁止

1. 禁止遍历团队/知识库列表后自行选择写入目标
2. 禁止根据名称"看起来合适"就决定写入
3. 禁止在未确认时执行写入

### ✅ 允许写入的条件（满足之一即可）

| 条件 | 示例 |
| ---- | ---- |
| 用户提供了明确 URL | `"写到这里：https://lexiangla.com/spaces/xxx"` |
| 用户提供了明确 ID | `"写入 space_id 为 xxx 的知识库"` |
| 用户指定名称 + Agent 回显确认 | Agent 搜到后展示详情，用户确认 |

### 写入操作涉及的工具

`entry_create_entry`、`entry_import_content`、`entry_import_content_to_entry`、`block_update_block`、`block_update_blocks`、`block_create_block_descendant`、`block_delete_block`、`block_delete_block_children`、`block_move_blocks`、`entry_rename_entry`、`entry_move_entry`、`file_apply_upload`、`file_commit_upload`、`file_create_hyperlink`

### 读取操作不受此限制

`team_list_teams`、`team_describe_team`、`team_list_frequent_teams`、`space_list_spaces`、`space_describe_space`、`entry_list_children`、`block_list_block_children`、`search_kb_search`、`search_kb_embedding_search`、`space_list_recently_spaces`、`entry_list_latest_entries`、`entry_describe_ai_parse_content`、`file_describe_file`、`file_download_file` 等只读操作可正常执行。

---

## 🔍 工具发现与调用

本服务**直接暴露所有业务工具**，可直接调用（如 `team_list_teams()`、`search_kb_search(keyword="xxx")`）。

同时提供以下辅助元工具，帮助发现和理解工具：

| 元工具                 | 用途                                           |
| ---------------------- | ---------------------------------------------- |
| `list_tool_categories` | 列出所有工具分类及其工具列表                   |
| `search_tools`         | 按关键词或分类搜索工具                         |
| `get_tool_schema`      | 获取具体工具的完整参数定义                     |

### 标准工作流

```
1. 直接调用已知工具：team_list_teams()、search_kb_search(keyword="xxx") 等
2. 不确定参数时：get_tool_schema(tool_name="xxx") → 获取参数定义
3. 不确定工具名时：search_tools(query="关键词") → 找到工具名
```

> 大多数常用工具已在本 Skill 中列出，可直接使用；遇到新工具或不确定的参数时，再用 `get_tool_schema` 查询。

---

## 🚀 快速开始

### 获取配置参数

访问：https://lexiangla.com/mcp

登录后获取：
- **company_from**：你的企业标识
- **access_token**：访问令牌（格式 `lxmcp_xxx`）

### 配置方式

#### 方式1：自动配置（推荐）

请阅读 `setup.md` 中的步骤说明，按指引完成配置。

#### 方式2：环境变量

```bash
export COMPANY_FROM="your_company"
export LEXIANG_TOKEN="lxmcp_YOUR_TOKEN_HERE"
```

#### 方式3：直接修改 mcp.json

编辑 `mcp.json`，将 `${COMPANY_FROM}` 和 `${LEXIANG_TOKEN}` 替换为实际值。

### mcp.json 配置模板

```json
{
    "mcpServers": {
        "lexiang": {
            "enabled": true,
            "url": "https://mcp.lexiang-app.com/mcp?company_from=${COMPANY_FROM}",
            "transportType": "streamable-http",
            "headers": {
                "Authorization": "Bearer ${LEXIANG_TOKEN}"
            }
        }
    }
}
```

### 安装后验证

配置完成后，**立即调用** `whoami()` 进行连通性检查并获取用户身份信息：

1. 调用 `whoami()`
2. **成功**（返回用户信息）→ 向用户展示欢迎消息：

```
✅ 乐享 MCP 连接成功！

👤 当前用户：{用户姓名}
🏢 绑定乐享：{企业/租户名称}

🎉 配置已就绪，你现在可以这样使用乐享知识库：

💡 试试这样提问：
• "看看我最近访问的知识库有什么更新"
• "我要记录今天的工作内容，为我创建一个乐享文档并拟写一个模版"
• "搜索关于 XXX 的知识文档"
• "帮我总结一下这个知识库的内容：{知识库链接}"
```

> 根据 `whoami` 返回的实际字段灵活调整展示内容。

3. **401 错误** → token 无效或已过期，引导用户重新获取（参见「AccessToken 生命周期管理」）
4. **连接超时/其他错误** → 检查 mcp.json 配置是否正确

### 遇到问题？

| 问题 | 解决方案 |
|------|----------|
| 连接无响应 | 确认 mcp.json 中 URL 包含 `company_from` 且格式正确 |
| 401 未授权 | token 过期或租户不匹配，参见「AccessToken 生命周期管理」 |
| 参数报错 | 执行 `get_tool_schema(tool_name="xxx")` 获取最新参数定义 |

---

## 🎯 意图识别与澄清

### 明确使用本 Skill 的场景

1. **关键词触发**：用户提到「乐享」「lexiang」「知识库」「知识」「文档」
2. **链接触发**：用户提供的链接 host 为 `lexiangla.com`
3. **上下文延续**：用户之前已明确使用乐享，后续操作默认继续

### 🛡️ 写入安全提醒

- ❌ 禁止遍历团队/知识库列表后自行选择写入目标
- ✅ 用户提供了 URL / ID / 精确名称 + 确认后方可写入
- ✅ 写入目标不明确时（如"帮我写到乐享""执行吧"但未指定知识库），需要求用户提供具体写入位置
- ✅ 读取操作（搜索、浏览、查看）不受此限制

---

## 工具概述

本 MCP 服务提供以下工具，**可直接调用**。参数不确定时以 `get_tool_schema` 返回为准。

### 📚 知识库管理
- `entry_create_entry` — 创建文档/文件夹
- `entry_import_content` — 导入 Markdown/HTML 创建新文档（⚠️ 仅新建）
- `entry_import_content_to_entry` — 导入内容到已有页面（支持覆盖/追加）
- `entry_list_latest_entries` — 获取最近更新条目
- `entry_rename_entry` — 重命名条目

### 📎 文件管理
- `file_apply_upload` — 申请文件上传（返回 upload_url 和 session_id）
- `file_commit_upload` — 确认上传完成

### 🧩 Block 操作
- `block_convert_content_to_blocks` — Markdown/HTML 转 Block 结构
- `block_create_block_descendant` — 创建 Block 结构
- `block_update_block` — 单块更新
- `block_update_blocks` — 批量更新
- `block_move_blocks` — 移动 Block
- `block_delete_block_children` — 删除子节点
- `block_delete_block` — 删除指定 Block（含子孙）
- `block_describe_block` — 获取单个 Block 详情
- `block_list_block_children` — 读取 Block 内容

### 🔍 搜索与发现
- `search_kb_search` — 关键词搜索
- `search_kb_embedding_search` — 语义向量搜索
- `team_list_teams` — 获取团队列表
- `team_describe_team` — 获取团队详情
- `team_list_frequent_teams` — 获取常用团队列表
- `space_list_spaces` — 获取知识库列表
- `space_describe_space` — 获取知识库详情（返回 `root_entry_id`）
- `space_list_recently_spaces` — 获取最近访问知识库

### 📖 条目与结构浏览
- `entry_list_children` — 浏览目录结构
- `entry_describe_entry` — 获取条目元信息（不含正文）
- `entry_describe_ai_parse_content` — 获取 AI 解析内容（含正文）
- `entry_list_parents` — 获取父级路径（面包屑）

### 🔗 外部内容导入
- `file_create_hyperlink` — 导入公众号文章等外部链接

---

## 内容搜索

### 关键词搜索 vs 语义搜索

| 工具 | 适用场景 |
|------|----------|
| `search_kb_search` | 精确关键词匹配 |
| `search_kb_embedding_search` | 模糊查询、"记得大意但忘了标题" |

**建议**：语义搜索召回后，再用 `entry_describe_entry` 或 `entry_describe_ai_parse_content` 精确读取。

### 搜索结果链接格式

根据返回的 `target_type` 拼接链接：

| target_type            | URL 格式                                    |
| ---------------------- | ------------------------------------------- |
| `kb_page`              | `{domain}/pages/<target_id>`                |
| `kb_file` / `kb_video` | `{domain}/teams/<team_id>/docs/<target_id>` |

---

## 🔗 结果链接生成规则（通用）

> **适用于所有返回 `entry_id` 的操作**，包括但不限于：`entry_import_content`、`entry_create_entry`、`entry_import_content_to_entry`、`file_commit_upload`、搜索结果等。

### 拼接规则

当操作成功返回了 `entry_id`（或 `target_id`），向用户展示访问链接时，使用上方「URL 规则」中定义的 `{domain}` 拼接：

```
{domain}/pages/{entry_id}
```

### ⛔ 禁止

- **禁止**使用 `mcp.lexiang-app.com` 拼接用户访问链接
- **禁止**使用 MCP 连接 URL（`mcp.lexiang-app.com`）的域名作为用户访问域名
- **禁止**将 `company_from` 拼接为子域名（如 `https://{company_from}.lexiangla.com` 是**错误**的）
- **禁止**编造或猜测域名，必须严格使用上方定义的 `{domain}`

---

## 📖 内容读取

| 工具 | 返回内容 | 用途 |
|------|----------|------|
| `entry_describe_entry` | 条目元信息（ID、名称、类型等） | 获取基本信息 |
| `entry_describe_ai_parse_content` | **条目正文内容** | 读取实际内容进行分析 |

---

## 常见操作流程

### 从知识库链接写入文档

> ⚠️ 仅在用户**主动提供了知识库链接**时执行。详见下方「常见使用场景 > 场景0」。

核心步骤：提取 `space_id` → `space_describe_space` 获取 `root_entry_id` → `entry_import_content` 写入 → 用 `{domain}/pages/{entry_id}` 拼接访问链接返回给用户。

### 微信公众号导入

当用户提供 `mp.weixin.qq.com` 链接且意图是"导入/收藏/保存到乐享"时，使用 `file_create_hyperlink`。

> 如果用户只是想阅读或总结内容，不要默认导入。

---

## 常见使用场景

### 场景0: 用户给了知识库链接，写入文档

> 用户："把报告写入乐享，链接是 https://lexiangla.com/spaces/16c4224607ea45ebacce6c15130a4957"

```
Step 1: 从 URL 提取 space_id = "16c4224607ea45ebacce6c15130a4957"
Step 2: call_tool("space_describe_space", {"space_id": "..."}) → 获取 root_entry_id
Step 3: call_tool("entry_import_content", {"space_id": "...", "parent_id": root_entry_id, "name": "报告", "content": "...", "content_type": "markdown"})
Step 4: 从返回结果取 entry_id，向用户展示访问链接：{domain}/pages/{entry_id}
```

> **要点**：`space_id` 和 `parent_id` 要同时传；`parent_id` 用 `root_entry_id` 表示写入根目录；链接中 `{domain}` 见上方 URL 规则定义。

### 场景1: 创建文档

```
call_tool("entry_create_entry", {"name": "技术文档", "parent_entry_id": "abc123", "entry_type": "page"})
```

### 场景2: 导入 Markdown

```
call_tool("entry_import_content", {"parent_id": "folder123", "name": "技术文档", "content": "...", "content_type": "markdown"})
```

### 场景3: 创建结构化 Block 文档

```
call_tool("block_create_block_descendant", {
  "entry_id": "doc123",
  "descendant": [
    {"block_id": "h1", "block_type": "h1", "heading1": {"elements": [{"text_run": {"content": "项目文档"}}]}},
    {"block_id": "tip", "block_type": "callout", "callout": {"color": "#FFF3E0"}, "children": ["tip_p"]},
    {"block_id": "tip_p", "block_type": "p", "text": {"elements": [{"text_run": {"content": "重要提示内容"}}]}},
    {"block_id": "li1", "block_type": "bulleted_list", "bulleted": {"elements": [{"text_run": {"content": "功能一"}}]}}
  ],
  "children": ["h1", "tip", "li1"]
})
```

### 场景4: 上传文件（3 步）

```
Step 1: call_tool("file_apply_upload", {"parent_entry_id": "folder123", "name": "README.md", "size": 1024})
        → 返回 upload_url, session_id
Step 2: HTTP PUT upload_url（上传文件内容，非 MCP 调用）
Step 3: call_tool("file_commit_upload", {"session_id": "..."})
```

### 场景5: 读取 Block 内容

```
call_tool("block_list_block_children", {"entry_id": "abc123", "with_descendants": true})
```

### 场景6: 批量更新 Block

```
call_tool("block_update_blocks", {
  "entry_id": "abc123",
  "updates": {
    "actual_block_id": {
      "update_text_elements": {
        "elements": [{"text_run": {"content": "更新后的内容"}}]
      }
    }
  }
})
```

---

## Block 结构核心规则

### 🍃 叶子节点（不能有 children）
- 标题块：h1, h2, h3, h4, h5
- 代码块：code
- 图片块：image
- 分割线：divider
- 图表块：mermaid, plantuml

### 📦 容器节点（必须指定 children）
- 提示框：callout
- 表格：table, table_cell
- 分栏布局：column_list, column
- 折叠块：toggle

> **详细说明**：完整 Block 类型和字段定义见 `references/block-schema.md`。

---

## ⚠️ 核心注意事项

1. **Block ID 映射**：`block_id` 为客户端临时 ID，服务端返回实际 ID 映射
2. **叶子节点限制**：标题、代码块、图片等不支持 children 字段
3. **容器节点要求**：callout、table、column_list 等必须指定 children
4. **文件上传大小**：必须获取准确的文件大小（字节数）
5. **`_mcp_fields` 优化**：所有工具支持 `_mcp_fields` 参数选择返回字段，减少 token 消耗

> **更多细节**：见 `references/common-errors.md` 和 `references/markdown-import.md`。

---

## 辅助资源

### 参考文档（references/ 目录）

| 文档                    | 说明                   |
| ----------------------- | ---------------------- |
| `block-schema.md`       | Block 类型完整说明     |
| `mcp-examples.md`       | 复杂 Block 结构示例    |
| `markdown-to-block.md`  | Markdown 转 Block 指南 |
| `block-update.md`       | 批量更新 Block 方法    |
| `content-reorganize.md` | 文档结构重组           |
| `folder-sync.md`        | 文件夹同步方案         |
| `markdown-import.md`    | Markdown 导入详解      |
| `common-errors.md`      | 常见错误排查           |
| `skill-maintenance.md`  | 维护与反馈流程         |

### 辅助脚本（scripts/ 目录）

| 脚本               | 说明               |
| ------------------ | ------------------ |
| `sync-folder.ts`   | 文件夹增量同步     |
| `block-helper.ts`  | Block 构建辅助工具 |
| `mcp-validator.ts` | MCP 参数校验       |

---

## ❓ 问题与排查

遇到问题时，请先查阅 `references/common-errors.md`。

---

## 📮 维护与反馈

Issue 反馈流程和 Skill 自我进化机制见 `references/skill-maintenance.md`。

---

## 相关链接

- 乐享平台：https://lexiangla.com
- MCP 协议：https://modelcontextprotocol.io
