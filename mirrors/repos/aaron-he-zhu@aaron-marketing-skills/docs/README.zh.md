# Aaron 营销技能库

**38 个技能。5 个命令。SEO/GEO 与红人营销，共享同一套契约。**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/aaron-marketing-skills?style=flat)](https://github.com/aaron-he-zhu/aaron-marketing-skills)
[![Version](https://img.shields.io/badge/version-10.0.1-orange)](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/LICENSE)

[English](../README.md) | **中文**

面向两类营销工作、共用一套运行契约的 Claude 技能与命令集：

- **搜索（SEO/GEO）** — 20 个技能：关键词研究、内容创作、技术审计、结构化数据、监控、质量门、实体事实、项目记忆。
- **红人营销（IMPACT）** — 18 个技能：受众洞察、红人发现、活动规划、外联、内容放大、ROI 追踪。

技能内容为零依赖 Markdown；Claude Code hooks 使用轻量 Bash runner。内置三套评估框架：[CORE-EEAT](../references/core-eeat-benchmark.md)（80 项内容质量）、[CITE](../references/cite-domain-rating.md)（40 项域名权威）、[C³](../references/c3-benchmark.md)（红人 创作者/内容/活动）。

> 本仓库为合集（由 `seo-geo-claude-skills` 改名而来，stars/fork/issue/历史一并继承）。只做搜索的用户可继续使用原 [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) URL 上的独立仓库（内容不变）。

## 快速开始

常用安装方式如下。

| 工具 | 安装 |
|------|------|
| Claude Code | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` 然后 `/plugin install aaron-marketing@aaron` |
| skills.sh / 通用 Agent Skills 宿主 | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| 任意宿主 | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

在 Claude Code 中，`marketplace add` 只是注册目录——还需运行 `/plugin install aaron-marketing@aaron`（或在 `/plugin` 中选择）才能真正启用技能与命令。通用宿主单技能安装：`npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`。

自然语言示例（需宿主支持自动路由）：

```text
帮我研究"云原生"相关的关键词机会
```

```text
帮我为一个护肤品牌找 TikTok 红人并给适配度打分
```

Slash 命令宿主的稳定入口：

```text
/aaron-marketing:auto audit https://example.com
```

## 技能

### 搜索 — SEO/GEO（20）

| 阶段 | 技能与用途 |
|------|------------|
| 研究 | `keyword-research` 关键词机会与选题；`competitor-analysis` 竞品差距；`serp-analysis` 搜索结果与意图；`content-gap-analysis` 内容缺口与编辑日历 |
| 构建 | `seo-content-writer` SEO/GEO 内容草稿；`geo-content-optimizer` AI 引用优化；`meta-tags-optimizer` 标题与元描述；`schema-markup-generator` JSON-LD 结构化数据 |
| 优化 | `on-page-seo-auditor` 页面 SEO 与 CORE-EEAT；`technical-seo-checker` 抓取、索引、速度、安全；`internal-linking-optimizer` 内链与站点架构；`content-refresher` 旧内容刷新 |
| 监控 | `rank-tracker` 排名与 SERP 变化；`backlink-analyzer` 外链质量与机会；`performance-reporter` SEO/GEO 报告；`alert-manager` 预警与监控规则 |
| 协议层 | `content-quality-auditor` 发布质量门；`domain-authority-auditor` CITE 域名可信度；`entity-optimizer` 实体与知识图谱；`memory-management` 项目记忆 |

### 红人 — IMPACT（18）

| 阶段 | 技能与用途 |
|------|------------|
| Insight 洞察 | `audience-analyzer` 受众画像；`niche-researcher` 细分赛道与关键声音；`trend-spotter` 趋势与话题 |
| Map 匹配 | `influencer-discovery` 跨平台红人发现；`fit-scorer` 红人-品牌适配度（C³ ACE 打分）；`competitor-tracker` 竞品红人策略 |
| Plan 规划 | `campaign-planner` 活动策略；`brief-generator` 红人 brief；`budget-optimizer` 预算分配 |
| Activate 启动 | `outreach-manager` 外联与谈判；`content-reviewer` 内容审核（ART 门，含 FTC 披露）；`contract-helper` 合作协议 |
| Convert 转化 | `content-amplifier` 内容放大；`ugc-repurposer` UGC 二次利用；`landing-optimizer` 落地页优化 |
| Track 追踪 | `performance-analyzer` 表现分析；`roi-calculator` ROI 与 CVI；`report-generator` 活动报告 |

## 命令
5 个命令覆盖搜索工作流端到端；红人技能按名称调用或经 `/aaron-marketing:auto` 路由。日常工作从 `/aaron-marketing:auto` 开始；其余四个是显式的模式入口：

- `/aaron-marketing:auto` — 推断意图并执行最小够用的工作流（加 `--deep` 进行穷尽/压测）
- `/aaron-marketing:research` — 关键词需求、SERP 意图、竞品、内容缺口、站点/主题/实体地图
- `/aaron-marketing:create` — brief、写作、系列、刷新、CMS 中立发布包（`--brief`/`--series`/`--refresh`/`--publish`/`--meta`/`--schema`）
- `/aaron-marketing:audit` — on-page + CORE-EEAT 质量、技术 SEO、AI 可见性、域权威（`--full`/`--tech`/`--visibility`/`--authority`）
- `/aaron-marketing:track` — 排名、告警、绩效报告、项目记忆（`--alert`/`--report`/`--remember`）

破坏性改名说明：当前命令使用 `/aaron-marketing:`。旧 `/seo:*` 与 `/aaron-seo-geo:*` 命令可粘贴给 `/aaron-marketing:auto` 来恢复新路由；例如 `/aaron-marketing:auto /aaron-seo-geo:audit https://example.com/blog/post` 会返回 `/aaron-marketing:audit https://example.com/blog/post`。

## 运行模型

每个技能都遵循统一结构：Quick Start、Skill Contract、Handoff Summary、Data Sources、Instructions、Reference Materials、Next Best Skill。四个跨阶段技能负责协议层：`content-quality-auditor` 做发布质量门，`domain-authority-auditor` 做信任门，`entity-optimizer` 维护实体事实，`memory-management` 管理 HOT/WARM/COLD 项目记忆。

可选工具连接器见 [CONNECTORS.md](../CONNECTORS.md)；没有工具时，每个技能仍可用用户提供的数据运行。

## 质量框架

| 框架 | 作用 |
|------|------|
| [CORE-EEAT](../references/core-eeat-benchmark.md) | 80 项内容质量评分 |
| [CITE](../references/cite-domain-rating.md) | 40 项域名权威评分 |
| [C³](../references/c3-benchmark.md) | 红人 创作者/内容/活动 评分（ACE/ART/ROI，9 维） |
| [Auditor Runbook](../references/auditor-runbook.md) | 审计 handoff、分数封顶、Artifact Gate |

## 免责声明

这些技能用于辅助 SEO/GEO 与红人营销工作流，但不保证排名、AI 引用、流量、互动或任何业务结果。红人合规检查（FTC 披露、声明真实性）为指引，非法律意见。在用于重大策略或法律决策之前，请与具备资质的专业人士核实建议。

## 贡献与许可

贡献规则见 [CONTRIBUTING.md](../CONTRIBUTING.md)。版本见 [VERSIONS.md](../VERSIONS.md)。许可证：Apache License 2.0。

*最后同步英文 README：v10.0.0*

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
 </picture>
</a>
