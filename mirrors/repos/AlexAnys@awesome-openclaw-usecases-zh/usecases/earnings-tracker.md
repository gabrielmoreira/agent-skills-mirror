# AI 驱动的财报追踪器

> 含国内适配：AKShare / 东方财富 / 巨潮资讯

在财报季追踪数十家科技公司意味着需要查看多个信息来源并记住报告日期。你希望紧跟 AI/科技公司的财报动态，而不必手动追踪每一家公司。

这个工作流自动化了财报追踪和推送：

- 每周日预览：扫描即将到来的财报日历，将相关的科技/AI 公司发布到 Telegram
- 你选择关注哪些公司，OpenClaw 为每个财报日期安排一次性的 cron job（定时任务）
- 每份报告发布后，OpenClaw 搜索结果，格式化详细摘要（超预期/不及预期、关键指标、AI 亮点），并推送给你

## 所需技能

- `web_search`（内置）
- OpenClaw 的 cron job（定时任务）支持
- 用于财报更新的 Telegram 话题

## 如何设置

1. 创建一个名为 "earnings" 的 Telegram 话题用于接收更新。
2. 向 OpenClaw 发送以下提示词：
```text
Every Sunday at 6 PM, run a cron job to:
1. Search for the upcoming week's earnings calendar for tech and AI companies
2. Filter for companies I care about (NVDA, MSFT, GOOGL, META, AMZN, TSLA, AMD, etc.)
3. Post the list to my Telegram "earnings" topic
4. Wait for me to confirm which ones I want to track

When I reply with which companies to track:
1. Schedule one-shot cron jobs for each earnings date/time
2. After each report drops, search for earnings results
3. Format a summary including: beat/miss, revenue, EPS, key metrics, AI-related highlights, guidance
4. Post to Telegram "earnings" topic

Keep a memory of which companies I typically track so you can auto-suggest them each week.
```

## 中国用户适配

A 股市场有完善的财报披露制度，而且数据获取比美股更规范。以下是针对 A 股投资者的适配方案。

### A 股 vs 美股财报机制差异

| 维度 | 美股 | A 股 |
|------|------|------|
| 财报日历 | 公司自行公布，需依赖第三方汇总 | 交易所要求提前公布**预约披露时间表**，更规范 |
| 发布节奏 | 季报一次性发布 | **业绩预告 → 业绩快报 → 正式报告**三阶段机制 |
| 数据获取 | 需付费 API（Alpha Vantage 等） | 有免费开源方案（AKShare） |

这意味着 A 股的财报追踪可以做得更精细——你可以在业绩预告阶段就提前获得信号。

### A 股数据源推荐

| 数据源 | 费用 | 说明 |
|--------|------|------|
| **AKShare** | 免费 | 推荐首选，MIT 开源，接口最全 |
| Tushare Pro | 积分制 | 基础免费，高级功能需积分 |
| 东方财富 Choice | 付费 | 专业级，适合机构用户 |
| 巨潮资讯 | 免费 | 官方披露渠道，适合获取原始公告 PDF |

**推荐方案：AKShare**（[GitHub](https://github.com/akfamily/akshare)，10k+ stars，MIT 许可）

安装：

```bash
pip install akshare
```

关键接口：

| 接口 | 用途 | 对应原用例功能 |
|------|------|---------------|
| `stock_yysj_em(date)` | 预约披露时间表 | earnings calendar（核心） |
| `stock_yjyg_em()` | 业绩预告数据 | 提前信号，美股无对应 |
| `stock_yjkb_em()` | 业绩快报 | 快速业绩概览 |
| `stock_yjbb_em()` | 正式业绩报表 | 完整财报数据 |

快速上手示例：

```python
import akshare as ak

# 获取 2025 年一季报预约披露时间表
df = ak.stock_yysj_em(date="20250331")
# 筛选你关注的公司（以股票代码筛选）
watchlist = ["600519", "000858", "601318", "000001"]
my_stocks = df[df["股票代码"].isin(watchlist)]
print(my_stocks[["股票代码", "股票简称", "首次预约时间"]])
```

### 推送渠道适配

| 原版方案 | 国内替代 | 说明 |
|---------|---------|------|
| Telegram | **钉钉群机器人** | Webhook 方式，最简单 |
| Telegram | **飞书机器人** | 支持富文本卡片消息 |
| Telegram | **企业微信应用** | 企业用户首选 |

### 提示词适配

将原版提示词中的美股部分替换为 A 股逻辑：

```text
每周日晚 8 点，运行定时任务：
1. 调用 AKShare 的 stock_yysj_em 接口，获取下周预约披露时间表
2. 筛选我关注的公司（600519 贵州茅台、000858 五粮液、601318 中国平安 等）
3. 将列表推送到钉钉群"财报追踪"
4. 等我确认要跟踪哪些

当我回复确认后：
1. 为每个披露日期安排一次性定时任务
2. 报告发布后，搜索业绩快报和市场解读
3. 格式化摘要：营收、净利润、同比增长、业绩预告对比、机构点评
4. 推送到钉钉群

记住我通常关注的公司列表，每周自动推荐。
同时监控业绩预告（stock_yjyg_em），有预告发布时提前通知我。
```

### 合规提醒

- 数据仅供个人学习研究，不构成投资建议
- 控制 API 调用频率，避免对上游平台造成压力
- AKShare 底层依赖公开网站数据，接口可能因上游变更而需更新，建议关注其 [GitHub Issues](https://github.com/akfamily/akshare/issues)

### 相关链接

- [AKShare 文档](https://akshare.akfamily.xyz/) — 免费开源 A 股数据接口
- [巨潮资讯](https://www.cninfo.com.cn/) — 官方信息披露平台
- [东方财富数据中心](https://data.eastmoney.com/) — 财报日历与数据查询

---

**原文链接**：[English Version](https://github.com/AlexAnys/awesome-openclaw-usecases/blob/main/usecases/earnings-tracker.md)
