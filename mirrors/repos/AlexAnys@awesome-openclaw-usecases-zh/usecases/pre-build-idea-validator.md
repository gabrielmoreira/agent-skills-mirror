# 开发前创意验证器

> 含国内适配：百度指数 / 微信指数 / V2EX / 少数派

在 OpenClaw 动手写代码之前，它会自动检查你的创意是否已经存在——扫描 GitHub、Hacker News、npm、PyPI 和 Product Hunt 五大数据源，根据竞争程度决定下一步行动。

## 功能介绍

- 在编写任何代码之前，自动扫描 5 个真实数据源（GitHub、Hacker News、npm、PyPI、Product Hunt）
- 返回 `reality_signal` 竞争度评分（0-100），直观显示该领域的拥挤程度
- 展示头部竞品及其 Star 数和描述
- 当领域饱和时，自动建议差异化方向
- 作为开发前的"关卡"：高分 = 停下来讨论，低分 = 直接开干

## 痛点

你告诉智能体"帮我做一个 AI 代码审查工具"，它高高兴兴地写了 6 个小时代码。然而 GitHub 上已有 143,000+ 个相关仓库——排名第一的有 53,000 颗 Star。智能体从不检查，因为你没让它查，它也不知道该查。你投入大量时间之后才发现竞争对手早已成熟。这个模式在每一个新项目中反复上演。

## 所需技能

- [idea-reality-mcp](https://github.com/mnemox-ai/idea-reality-mcp) — 扫描真实数据源并返回竞争度评分的 MCP 服务器

## 如何设置

1. 安装 idea-reality-mcp：

```bash
uvx idea-reality-mcp
```

2. 在 OpenClaw 配置中添加 MCP 服务器：

```json
{
  "mcpServers": {
    "idea-reality": {
      "command": "uvx",
      "args": ["idea-reality-mcp"]
    }
  }
}
```

3. 将以下指令添加到你的 OpenClaw 智能体设置中：

```text
Before starting any new project, feature, or tool, always run idea_check first.

Rules:
- If reality_signal > 70: STOP. Report the top 3 competitors with star counts.
  Ask me if I want to proceed, pivot, or abandon.
- If reality_signal 30-70: Show me the results and pivot_hints.
  Suggest a niche angle that existing projects don't cover.
- If reality_signal < 30: Proceed to build.
  Mention that the space is open.
- Always show the reality_signal score and top competitors before writing any code.
```

## 真实案例

**你：** "帮我做一个 AI 代码审查的 CLI 工具"

OpenClaw 运行 `idea_check("AI code review tool")` 并回复：

> **reality_signal: 90/100（非常高）**
>
> 头部竞品：
> 1. Gitea — 53,940 stars
> 2. reviewdog — 9,104 stars
> 3. Danger (Ruby) — 5,649 stars
>
> 该领域有 143,000+ 个相关仓库，头部产品成熟且资金充裕。
>
> **差异化建议：**
> - 聚焦特定语言（Rust/Go 专用 AI 代码审查）
> - 针对特定框架（React/Vue 组件审查）
> - 针对特定行业（金融/医疗代码合规审查）
>
> 要继续做差异化版本，还是换一个方向？

**你：** "那做一个开发前创意验证的 MCP 服务器呢？"

> **reality_signal: 8/100（非常低）**
>
> PyPI 和 npm 上没有直接竞品。GitHub 上有一些沾边的仓库，但没有一个解决完全相同的问题。
>
> 这个领域完全空白。开始开发。

## 进阶玩法

- **深度模式**：使用 `depth="deep"` 同时扫描全部 5 个数据源（GitHub + HN + npm + PyPI + Product Hunt），适合重大项目决策。
- **批量验证**：在黑客马拉松前，给 OpenClaw 一份 10 个创意的清单，让它按 `reality_signal` 排名——分数最低的 = 最具原创性的机会。
- **先试用 Web 版**：在 [mnemox.ai/check](https://mnemox.ai/check) 免费试用，看看这个工作流是否适合你的需求。

## 关键洞察

- 这能防止开发中最昂贵的错误：**解决一个已经被解决的问题**。
- `reality_signal` 基于真实数据（仓库数量、Star 分布、HN 讨论量），而不是 LLM 猜测。
- 高分不意味着"别做"——而是"要么差异化，要么别白费力气"。
- 低分意味着真正的蓝海。这才是个人开发者胜算最大的方向。

## 中国用户适配

### idea-reality-mcp 已支持中文

v0.3.0 版本新增了三阶段关键词提取管线，内置 150+ 中英术语映射（覆盖 15+ 领域），可以直接用中文描述你的创意。例如输入"宠物预约看诊 app"，会自动映射为"pet appointment veterinary booking app"进行搜索。

### 数据源说明

idea-reality-mcp 扫描的 5 个数据源（GitHub、Hacker News、npm、PyPI、Product Hunt）均为国际平台。对于面向国内市场的项目，建议补充以下国内数据源进行交叉验证：

| 国际数据源 | 国内对应平台 | 用途 |
|-----------|-------------|------|
| Product Hunt | V2EX [创意] 板块、少数派 | 发现国内新产品和竞品 |
| Hacker News | V2EX、掘金、CSDN | 技术社区讨论热度 |
| GitHub | Gitee | 国内开源项目搜索 |
| npm / PyPI | npm（通用）/ Gitee 镜像 | 包管理和依赖检索 |

### 补充国内市场数据验证

在 idea-reality-mcp 给出国际竞争度评分后，建议进一步通过国内数据平台验证市场需求：

- **百度指数**（index.baidu.com）：查看关键词搜索趋势，判断用户是否在主动搜索你要解决的问题
- **微信指数**：微信小程序内查看关键词在微信生态的热度，适合 C 端产品验证
- **巨量算数**（trendinsight.oceanengine.com）：抖音/头条生态数据，了解短视频和内容领域的趋势
- **阿里指数 / 生意参谋**：电商领域需求验证，查看商品搜索趋势和竞争程度
- **36氪、IT桔子**：查看该领域是否已有融资项目，评估竞争格局

### 建议补充的提示词

在原版提示词基础上，可以添加以下规则以覆盖国内市场：

```text
After running idea_check, also help me research the Chinese market:
- Search for similar products on V2EX, 少数派, and 36氪
- Check Baidu Index trends for related keywords
- Look for competing projects on Gitee
- Summarize whether the idea has more or less competition in China vs. internationally
```

### 适用场景

这个用例对国内开发者和创业者的价值尤其突出：

- **独立开发者**：在 Product Hunt 或国内社区发布前，快速验证创意的全球竞争度
- **出海团队**：验证产品在国际市场的竞争空间，找到差异化角度
- **黑客马拉松参赛者**：批量筛选最具原创性的选题
- **产品经理**：在立项前用数据说话，避免重复造轮子

## 相关链接

- [idea-reality-mcp GitHub](https://github.com/mnemox-ai/idea-reality-mcp)
- [Web 在线体验](https://mnemox.ai/check)（无需安装即可试用）
- [PyPI](https://pypi.org/project/idea-reality-mcp/)

---

**原文链接**：[English Version](https://github.com/AlexAnys/awesome-openclaw-usecases/blob/main/usecases/pre-build-idea-validator.md)
