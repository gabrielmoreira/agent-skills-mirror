# 晋江：采集与分析

选择晋江时读取，先用 `/browser-cdp` 启动 Chrome。脚本从 `topten.php` 取频道、书名、作者与链接中的 `novelid`，排除「X 向《书名》投了 Y」霸王票记录，再请求 `onebook.php?novelid=` 补详情；详情 HTML 按 gb18030 解码。

## 榜单与命令

URL `jjwxc.net/topten.php?orderstr={榜单ID}&t={频道ID}`（t=0 全站）。orderstr：收入金榜 12 / 月榜 7 / 季度榜 8 / 完结金榜 14 / 新手金榜 15 / 千字金榜 17。

```bash
node scripts/jjwxc-rank-scraper.js --type 12 --outdir {输出目录}        # 列表全保留；每频道前 10 补详情，总上限 100
node scripts/jjwxc-rank-scraper.js --type 12 --top 15 --detail-limit 60  # 调整每频道补详情本数/详情总量
node scripts/jjwxc-rank-scraper.js --type 12 --list-only                 # 只采列表（快，无核心指标）
```

默认收入金榜 + 月榜。本数含全列表，热度只含详情样本；覆盖见本次榜单文件头的「详情采集」。

## 字段与硬性要求

频道（聚合时当题材）、排名、书名、作者、novelid、收藏数（核心，聚合的热度口径）、营养液、积分、字数、状态、作品页链接。指标分析须有收藏、营养液或积分、字数；`--list-only` 或 `[仅列表-无核心指标]` 只支持看书目，指标分析前要重采详情。

## 分析维度

| 维度 | 看什么 |
|---|---|
| 金榜 | 观察上榜作品构成，不把名次还原为收入 |
| 季度榜 | 中期趋势 |
| 红字/黑字 | 当前脚本不采页面颜色，不能据此判断负面评价 |
| 收藏/营养液 | 女频市场的核心指标 |
