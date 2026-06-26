---
name: security-scan
description: 使用 AgentShield 扫描 Claude Code 配置（.claude/ 目录）中的安全漏洞、配置错误和注入风险。检查 CLAUDE.md、settings.json、MCP 服务端、钩子（Hooks）和智能体（Agents）定义。
---

# 安全扫描技能 (Security Scan Skill)

使用 [AgentShield](https://github.com/affaan-m/agentshield) 审计 Claude Code 配置的安全问题。

## 启动时机

- 设置新的 Claude Code 项目时
- 修改 `.claude/settings.json`、`CLAUDE.md` 或 MCP 配置后
- 提交配置变更前
- 接入具有现有 Claude Code 配置的新仓库时
- 定期进行安全健康检查

## 扫描对象

| 文件 | 检查内容 |
|------|--------|
| `CLAUDE.md` | 硬编码的密钥（Secrets）、自动执行指令、提示词注入（Prompt Injection）模式 |
| `settings.json` | 过度宽松的允许列表（Allowlist）、缺失的拒绝列表（Denylist）、危险的绕过标志位 |
| `mcp.json` | 存在风险的 MCP 服务端、硬编码的环境密钥、npx 供应链风险 |
| `hooks/` | 由插值引起的命令注入、数据泄露、静默错误抑制 |
| `agents/*.md` | 无限制的工具访问、提示词注入攻击面、缺失的模型规范 |

## 前提条件

必须安装 AgentShield。请检查并根据需要进行安装：

```bash
# 确认是否已安装
npx ecc-agentshield --version

# 全局安装（推荐）
npm install -g ecc-agentshield

# 或通过 npx 直接运行（无需安装）
npx ecc-agentshield scan .
```

## 使用方法

### 基础扫描

针对当前项目的 `.claude/` 目录运行：

```bash
# 扫描当前项目
npx ecc-agentshield scan

# 扫描特定路径
npx ecc-agentshield scan --path /path/to/.claude

# 按最小严重程度过滤扫描
npx ecc-agentshield scan --min-severity medium
```

### 输出格式

```bash
# 终端输出（默认） — 带有分级的彩色报告
npx ecc-agentshield scan

# JSON — 用于 CI/CD 集成
npx ecc-agentshield scan --format json

# Markdown — 用于文档
npx ecc-agentshield scan --format markdown

# HTML — 自包含的深色主题报告
npx ecc-agentshield scan --format html > security-report.html
```

### 自动修复

自动应用安全的修复（仅限标记为可自动修复的项目）：

```bash
npx ecc-agentshield scan --fix
```

这将执行以下操作：
- 将硬编码的密钥替换为环境变量引用
- 将通配符权限收紧为带作用域的替代方案
- 不会修改仅限手动建议的项目

### Opus 4.6 深度分析

运行对抗性的三智能体（3-Agent）流水线以进行更深层次的分析：

```bash
# 需要 ANTHROPIC_API_KEY
export ANTHROPIC_API_KEY=your-key
npx ecc-agentshield scan --opus --stream
```

这将执行以下操作：
1. **攻击者（红队/Red Team）** — 发现攻击向量
2. **防御者（蓝队/Blue Team）** — 推荐加固方案
3. **审计员（最终判定）** — 整合双方观点

### 安全配置初始化

从零开始构建新的安全 `.claude/` 配置：

```bash
npx ecc-agentshield init
```

将创建的内容：
- 带有作用域权限和拒绝列表的 `settings.json`
- 包含安全最佳实践的 `CLAUDE.md`
- `mcp.json` 占位符

### GitHub Action

添加到 CI 流水线中：

```yaml
- uses: affaan-m/agentshield@v1
  with:
    path: '.'
    min-severity: 'medium'
    fail-on-findings: true
```

## 严重程度分级 (Severity Levels)

| 分级 | 分数 | 含义 |
|-------|-------|---------|
| A | 90-100 | 安全的配置 |
| B | 75-89 | 轻微问题 |
| C | 60-74 | 需要注意 |
| D | 40-59 | 重大风险 |
| F | 0-39 | 关键漏洞 |

## 结果解读

### 关键发现（立即修复）
- 配置文件中硬编码的 API 密钥或令牌
- 允许列表中的 `Bash(*)`（无限制的 Shell 访问）
- 由 `${file}` 插值引起的钩子（Hooks）内命令注入
- 执行 Shell 的 MCP 服务端

### 高危发现（上线前修复）
- CLAUDE.md 中的自动执行指令（提示词注入向量）
- 权限中缺失的拒绝列表
- 拥有不必要的 Bash 访问权限的智能体（Agent）

### 中度发现（建议修复）
- 钩子（Hooks）内的静默错误抑制（`2>/dev/null`、`|| true`）
- 缺失的 `PreToolUse` 安全钩子
- MCP 服务端配置中的 `npx -y` 自动安装

### 信息级发现（知悉）
- MCP 服务端缺失说明
- 正确标记的禁止指令（良好实践）

## 链接

- **GitHub**: [github.com/affaan-m/agentshield](https://github.com/affaan-m/agentshield)
- **npm**: [npmjs.com/package/ecc-agentshield](https://www.npmjs.com/package/ecc-agentshield)
