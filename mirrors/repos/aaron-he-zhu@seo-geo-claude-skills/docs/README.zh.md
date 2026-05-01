# SEO & GEO 技能库

**20 个技能。17 个命令。搜索排名 + AI 引用。**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/seo-geo-claude-skills?style=flat)](https://github.com/aaron-he-zhu/seo-geo-claude-skills)
[![Version](https://img.shields.io/badge/version-9.9.5-orange)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/LICENSE)

[English](../README.md) | **中文**

面向搜索引擎优化（SEO）和生成式引擎优化（GEO）的 Claude 技能与命令集。仓库为零依赖 Markdown，支持 Claude Code、OpenClaw、Gemini CLI、Qwen Code、Amp、Kimi、CodeBuddy，以及任何支持 `npx skills` 的 agent。内容质量使用 CORE-EEAT（80 项），域名权威使用 CITE（40 项）。

## 快速开始

| 工具 | 安装 |
|------|------|
| Claude Code | `/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills` |
| OpenClaw | 整包：`clawhub install aaron-he-zhu/aaron-seo-geo`；单技能：`clawhub install aaron-he-zhu/<skill>` |
| Gemini CLI | `gemini extensions install https://github.com/aaron-he-zhu/seo-geo-claude-skills` |
| Qwen Code | `qwen extensions install https://github.com/aaron-he-zhu/seo-geo-claude-skills` |
| Amp | `amp skill add aaron-he-zhu/seo-geo-claude-skills` |
| Kimi Code CLI | `kimi plugin install https://github.com/aaron-he-zhu/seo-geo-claude-skills.git` |
| CodeBuddy | `/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills` 后 `/plugin install aaron-seo-geo` |
| 通用回退 | `npx skills add aaron-he-zhu/seo-geo-claude-skills` |

单技能安装：`npx skills add aaron-he-zhu/seo-geo-claude-skills -s keyword-research`。

示例：

```text
帮我研究"云原生"相关的关键词机会
/seo:audit-page https://example.com
```

## 技能

| 阶段 | 技能与用途 |
|------|------------|
| 研究 | `keyword-research` 关键词机会与选题；`competitor-analysis` 竞品差距；`serp-analysis` 搜索结果与意图；`content-gap-analysis` 内容缺口与编辑日历 |
| 构建 | `seo-content-writer` SEO/GEO 内容草稿；`geo-content-optimizer` AI 引用优化；`meta-tags-optimizer` 标题与元描述；`schema-markup-generator` JSON-LD 结构化数据 |
| 优化 | `on-page-seo-auditor` 页面 SEO 与 CORE-EEAT；`technical-seo-checker` 抓取、索引、速度、安全；`internal-linking-optimizer` 内链与站点架构；`content-refresher` 旧内容刷新 |
| 监控 | `rank-tracker` 排名与 SERP 变化；`backlink-analyzer` 外链质量与机会；`performance-reporter` SEO/GEO 报告；`alert-manager` 预警与监控规则 |
| 协议层 | `content-quality-auditor` 发布质量门；`domain-authority-auditor` CITE 域名可信度；`entity-optimizer` 实体与知识图谱；`memory-management` 项目记忆 |

## 命令

用户命令：`/seo:audit-page`, `/seo:check-technical`, `/seo:generate-schema`, `/seo:optimize-meta`, `/seo:report`, `/seo:audit-domain`, `/seo:write-content`, `/seo:keyword-research`, `/seo:setup-alert`, `/seo:geo-drift-check`。

维护命令：`/seo:wiki-lint`, `/seo:contract-lint`, `/seo:run-evals`, `/seo:sync-versions`, `/seo:validate-library`, `/seo:evolve-skill`, `/seo:skillify`。

日常 SEO/GEO 工作通常只需要用户命令。检查拟新增技能是否完整、可路由时使用 `/seo:skillify`；改进技能库本身时使用 `/seo:evolve-skill`；评审这类改进时使用 `/seo:run-evals`。

发布说明：`v9.9.5` 新增 `/seo:skillify`、派生技能路由索引、兼容的路由 eval 种子，以及 17 个命令的护栏。模拟证据仍然是非验证证据，直到出现可接受的项目本地信号。

## 运行模型

每个技能都遵循统一结构：Quick Start、Skill Contract、Handoff Summary、Data Sources、Instructions、Reference Materials、Next Best Skill。四个跨阶段技能负责协议层：`content-quality-auditor` 做发布质量门，`domain-authority-auditor` 做信任门，`entity-optimizer` 维护实体事实，`memory-management` 管理 HOT/WARM/COLD 项目记忆。

可选工具连接器见 [CONNECTORS.md](../CONNECTORS.md)；没有工具时，每个技能仍可用用户提供的数据运行。

## 质量框架

| 框架 | 作用 |
|------|------|
| [CORE-EEAT](../references/core-eeat-benchmark.md) | 80 项内容质量评分 |
| [CITE](../references/cite-domain-rating.md) | 40 项域名权威评分 |
| [Auditor Runbook](../references/auditor-runbook.md) | 审计 handoff、分数封顶、Artifact Gate |

## 贡献与许可

贡献规则见 [CONTRIBUTING.md](../CONTRIBUTING.md)。版本见 [VERSIONS.md](../VERSIONS.md)。许可证：Apache License 2.0。

*最后同步英文 README：v9.9.5*
