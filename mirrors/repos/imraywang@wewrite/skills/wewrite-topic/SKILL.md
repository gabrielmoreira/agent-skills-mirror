---
name: wewrite-topic
description: |
  WeWrite 选题模块：抓取全网热点 + 垂类高频需求 + 历史表现分析 + 搜索需求，为公众号
  生成 10 个评分排序的选题（含高频角度与常青选题）。
  触发关键词：公众号选题、找几个选题、今天写什么、热点选题、热搜选题、爆款选题、选题建议。
  需要公众号/微信上下文；不应被抖音/短视频/网站的选题需求触发。
allowed-tools:
  - Bash
  - Read
  - Write
  - WebSearch
---

# wewrite-topic — 选题

## 运行约定

- **CLI**：确定性操作走 `wewrite` 命令（需在 PATH；缺失则引导 `uv tool install wewrite`，或在仓库里 `bash install.sh`）。
- **{home}**：用户状态目录 = `$WEWRITE_HOME` 或 `~/.wewrite`（`wewrite home` 可查）。config/style/history/playbook/output/exemplars 全在 {home}，不在仓库；references 文档中的状态路径同此约定。
- **`读取: <路径>`** = 用文件读取工具真实读完该文件再继续，不是注释。
- **references/**：本 skill 自带 `{skill_dir}/references/`；references 文档内的 `{skill_dir}` 即本 skill 目录。
- **任务状态**：通过 `wewrite run show/update/step` 读取和更新；不直接改状态文件。

## 前置

- `{home}/style.yaml` 存在 → 提取 `topics`、`content_style`。不存在 → 问用户"你的
  公众号主要写哪几个方向？"用回答临时代替 topics，并提示可用 **wewrite-style** 完成完整设置。

## 2.1 热点抓取

```bash
wewrite hotspots --limit 30
```

**降级**：脚本报错 → WebSearch "今日热点 {topics第一个垂类}"

## 2.1b 高频需求参考

对 `topics` 的前 1-2 个垂类词各搜一次近一周的公众号文章：

```bash
wewrite search-articles "{垂类词}" -n 15 -t 2
```

产出近一周同垂类公众号文章列表（标题/摘要/发布时间/账号），作为「已验证的内容需求」
信号供 2.3 使用。搜狗结果不带阅读量，因此只能说明同题出现频率，不能声称文章“爆款”。

**降级**：命令报错 / 结果为空（搜狗反爬限流）→ 跳过本步，不阻断，选题构成退回默认。

## 2.2 历史分析 + SEO

```
读取: {home}/history.yaml（不存在则跳过）
```

```bash
wewrite seo --json {关键词}
```

历史分析（有 stats 数据时）：
- 统计哪种 `framework` 的文章表现最好（阅读量/分享率）→ 推荐框架时加权
- 统计哪种 `enhance_strategy` 的文章表现最好 → 增强策略选择时参考
- 近 7 天已写的关键词降分（去重）

**降级**：SEO 脚本报错 → LLM 判断；history 无 stats → 跳过效果分析，仅做去重

## 2.3 生成选题

```
读取: {skill_dir}/references/topic-selection.md
```

生成 **10 个选题**，其中：
- **5-6 个热点选题**：基于 2.1 的热点，按 topic-selection.md 规则评分
- **2-3 个高频角度选题**（仅 2.1b 有产出时）：基于近一周同题文章，按
  topic-selection.md 规则评分，标注“高频需求”；2.1b 无产出时份额还给热点
- **2-3 个常青选题**：不依赖热点，从用户的 `topics` 领域生成长尾内容（教程/方法论/经验总结/工具推荐），标注为"常青"。适合 content_style 为干货型/测评型的用户

每个选题含标题、评分、点击率潜力、SEO 友好度、推荐框架。

- 自动模式 → 选最高分
- 交互模式 / 单独激活 → 展示全部，等用户选

## 完成

用 `wewrite run update --patch` 写入 `topic.title`、`topic.keywords`、`topic.source`
（“热点抓取” / “高频需求” / “常青”）、`topic.framework_hint`，然后
`wewrite run step topic completed`。
单独激活且用户只要选题列表时，展示 10 个选题即可；用户选定后写入状态并提示
"可以直接说'就写这个'进入写作（wewrite-write）"。
