# Semantic Router 语义路由器

[![版本](https://img.shields.io/badge/version-7.9.5-blue)](https://clawhub.ai/halfmoon82/semantic-router)
[![许可证](https://img.shields.io/badge/license-MIT--0-green)](https://spdx.org/licenses/MIT-0.html)
[![状态](https://img.shields.io/badge/status-生产就绪-brightgreen)](https://clawhub.ai/halfmoon82/semantic-router)

> **OpenClaw 代理的生产级会话路由系统**

让 AI 代理根据对话内容自动选择最合适的模型。四层识别（系统过滤→关键词→指示词→语义相似度），四池架构（高速/智能/人文/代理），五分支路由，全自动 Fallback 回路。支持 trigger_groups_all 非连续词组命中。

## 🎯 解决什么问题？

- **Cron Job 导致会话频繁重置** — 后台定时任务打断用户交互
- **Discord/Telegram 渠道会话突然清空** — 长任务无法延续
- **AGENTS.md 被截断注入** — 大文件超过 20KB 限制
- **模型自动切换被全局配置覆盖** — 切换不生效

## ⚠️ 安全与权限声明

**本技能执行以下特权操作 — 均为有意且由用户主动发起：**

| 操作 | 目的 | 范围 |
|------|------|------|
| 读取/修改 `~/.openclaw/openclaw.json` | 配置模型路由池 | 仅本地配置 |
| 读取/写入 `~/.openclaw/workspace/.lib/pools.json` | 存储模型池配置 | 仅工作区 |
| 读取/写入 `~/.openclaw/workspace/.lib/tasks.json` | 存储任务类型定义 | 仅工作区 |
| 本地运行 `semantic_check.py` | 分类用户消息进行路由 | 无需网络 |
| 通过 `sessions.patch` 修改会话模型 | 切换活动模型池 | 仅当前会话 |
| 重启 OpenClaw Gateway | 应用路由配置变更 | 仅本地服务 |
| 更新 Cron Job `sessionTarget` | 隔离后台任务与用户会话 | 仅 Cron 作业 |

**本技能不会做什么：**
- 不会向外部服务器泄露数据
- 不会直接访问 API 密钥或机密
- 不会修改 `~/.openclaw/` 之外的文件
- 不会以提升的权限运行
- 不会自动安装软件包

## 🚀 快速开始

### 安装

```bash
# 从 ClawHub 安装
clawhub install https://clawhub.ai/halfmoon82/semantic-router

# 或手动安装
cp -r ~/.openclaw/workspace/skills/semantic-router ~/my-projects/
```

### 配置

```bash
# 运行交互式配置向导
python3 ~/.openclaw/workspace/skills/semantic-router/scripts/setup_wizard.py
```

### 隔离现有 Cron Job

```bash
# 列出你的 Cron Job
cron list | jq '.jobs[] | {id, name, sessionKey}'

# 隔离使用渠道会话的 Job
cron update {job_id} \
  --patch '{"sessionKey": null, "sessionTarget": "isolated"}'
```

## 🏗️ 架构

### 四池模型架构

| 池名 | 用途 | 示例模型 | 特点 |
|------|------|----------|------|
| **高速池** | 查询、检索、搜索 | gemini-2.5-flash | 快速、成本低 |
| **智能池** | 开发、编程、复杂任务 | claude-sonnet-4.6 | 精准、能力强 |
| **人文池** | 内容生成、翻译 | gemini-2.5-pro | 平衡、流畅 |
| **代理池** | 长上下文代理、Computer Use | gpt-5.4 | 1M上下文、工具调用 |

### 五分支路由

| 分支 | 触发条件 | 动作 | 会话行为 |
|------|----------|------|----------|
| **A** | 关键词匹配 | 切换到目标池 | 切换模型，不重置 |
| **B** | 指示词（延续） | 保持当前 | 无动作 |
| **B+** | 中等关联度（0.08~0.15） | 保持 + 警告 | 输出漂移警告 |
| **C** | 新任务关键词 | 切换到目标池 | 切换模型，不重置 |
| **C-auto** | 低关联度（<0.08） | 重置 + 切换池 | `/new` + 切换模型 |

## 📚 文档

- [SKILL.md](SKILL.md) — 完整技能文档（中文）
- [README_v3_PRODUCTION.md](references/README_v3_PRODUCTION.md) — 生产部署指南（英文）
- [declaration-format.md](references/declaration-format.md) — 声明格式规范

## 🔧 要求

- Python 3.8+
- OpenClaw Gateway 运行中
- 已配置的模型提供商

## 📄 许可证

MIT-0 — 可自由使用、修改和分发。无需署名。

---

**维护者**: halfmoon82  
**ClawHub**: https://clawhub.ai/halfmoon82/semantic-router  
**最后更新**: 2026-03-12
