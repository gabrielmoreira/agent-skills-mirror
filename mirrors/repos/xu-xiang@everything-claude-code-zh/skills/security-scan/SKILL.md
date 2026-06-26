---
name: security-scan
description: 使用 AgentShield 扫描您的 Claude Code 配置（.claude/ 目录）是否存在安全漏洞、配置错误和注入风险。检查项包括 CLAUDE.md、settings.json、MCP 服务器、钩子（Hooks）以及智能体（Agent）定义。
origin: ECC
---

# 安全扫描技能 (Security Scan Skill)

使用 [AgentShield](https://github.com/affaan-m/agentshield) 审计您的 Claude Code 配置安全问题。

## 何时激活

- 设置新的 Claude Code 项目时
- 修改 `.claude/settings.json`、`CLAUDE.md` 或 MCP 配置后
- 提交配置更改前
- 加入具有现有 Claude Code 配置的新仓库时
- 定期的安全卫生检查

## 扫描对象

| 文件 | 检查项 |
|------|--------|
| `CLAUDE.md` | 硬编码密钥（Hardcoded secrets）、自动运行指令、提示词注入（Prompt injection）模式 |
| `settings.json` | 过度宽松的允许列表（Allow lists）、缺失的拒绝列表（Deny lists）、危险的绕过标志 |
| `mcp.json` | 风险 MCP 服务器、硬编码环境变量密钥、npx 供应链风险 |
| `hooks/` | 通过插值进行的命令注入、数据外泄、静默错误抑制 |
| `agents/*.md` | 未受限的工具访问、提示词注入攻击面、缺失模型规范 |

## 前置条件

必须安装 AgentShield。如果需要，请检查并安装：

```bash
# 检查是否已安装
npx ecc-agentshield --version

# 全局安装（推荐）
npm install -g ecc-agentshield

# 或通过 npx 直接运行（无需安装）
npx ecc-agentshield scan .
```

## 使用方法

### 基础扫描 (Basic Scan)

针对当前项目的 `.claude/` 目录运行：

```bash
# 扫描当前项目
npx ecc-agentshield scan

# 扫描特定路径
npx ecc-agentshield scan --path /path/to/.claude

# 使用最低严重程度过滤进行扫描
npx ecc-agentshield scan --min-severity medium
```

### 输出格式 (Output Formats)

```bash
# 终端输出（默认） — 带有评分的彩色报告
npx ecc-agentshield scan

# JSON — 用于 CI/CD 集成
npx ecc-agentshield scan --format json

# Markdown — 用于文档记录
npx ecc-agentshield scan --format markdown

# HTML — 独立包含的深色主题报告
npx ecc-agentshield scan --format html > security-report.html
```

### 自动修复 (Auto-Fix)

自动应用安全修复（仅针对标记为可自动修复的项）：

```bash
npx ecc-agentshield scan --fix
```

此操作将：
- 将硬编码密钥替换为环境变量引用
- 将通配符权限收紧为具体范围的替代方案
- 绝不修改仅限手动建议的项

### Opus 4.6 深度分析 (Opus 4.6 Deep Analysis)

运行对抗性三智能体（Three-agent）管道进行更深层次的分析：

```bash
# 需要 ANTHROPIC_API_KEY
export ANTHROPIC_API_KEY=your-key
npx ecc-agentshield scan --opus --stream
```

此操作会运行：
1. **攻击者（红队/Red Team）** — 寻找攻击向量
2. **防御者（蓝队/Blue Team）** — 建议加固措施
3. **审计员（最终裁决）** — 综合两方观点

### 初始化安全配置 (Initialize Secure Config)

从头开始搭建一个新的安全 `.claude/` 配置：

```bash
npx ecc-agentshield init
```

创建内容：
- 带有具体权限范围和拒绝列表（Deny list）的 `settings.json`
- 符合安全最佳实践的 `CLAUDE.md`
- `mcp.json` 占位符

### GitHub Action

添加到您的 CI 流水线：

```yaml
- uses: affaan-m/agentshield@v1
  with:
    path: '.'
    min-severity: 'medium'
    fail-on-findings: true
```

## 严重程度等级 (Severity Levels)

| 等级 | 评分 | 含义 |
|-------|-------|---------|
| A | 90-100 | 安全配置 |
| B | 75-89 | 存在次要问题 |
| C | 60-74 | 需要注意 |
| D | 40-59 | 存在重大风险 |
| F | 0-39 | 存在关键漏洞 |

## 结果解读

### 关键发现（立即修复）
- 配置文件中存在硬编码的 API 密钥或令牌（Tokens）
- 允许列表（Allow list）中包含 `Bash(*)`（不受限的 Shell 访问）
- 钩子（Hooks）中通过 `${file}` 插值存在的命令注入
- 运行 Shell 的 MCP 服务器

### 高风险发现（生产环境部署前修复）
- CLAUDE.md 中的自动运行指令（提示词注入向量）
- 权限设置中缺失拒绝列表（Deny lists）
- 智能体（Agents）拥有不必要的 Bash 访问权限

### 中风险发现（建议修复）
- 钩子（Hooks）中的静默错误抑制（`2>/dev/null`，`|| true`）
- 缺失 PreToolUse 安全钩子（Hooks）
- MCP 服务器配置中的 `npx -y` 自动安装

### 信息类发现（仅供参考）
- MCP 服务器缺失描述信息
- 预防性指令被正确标记为良好实践

## 相关链接

- **GitHub**: [github.com/affaan-m/agentshield](https://github.com/affaan-m/agentshield)
- **npm**: [npmjs.com/package/ecc-agentshield](https://www.npmjs.com/package/ecc-agentshield)
