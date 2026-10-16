# 刺猬猫：采集与分析

先用 `/browser-cdp` 启动 Chrome。脚本解析 rank-index 各榜，按去空白书名匹配作品页链接。

## 榜单与命令

`node scripts/ciweimao-rank-scraper.js --type {榜单} --outdir {输出目录}`：click 点击榜 / favor 收藏榜 / recommend 推荐榜 / subscribe 订阅榜 / monthly 月票榜 / tsukkomi 吐槽榜 / newbook 新书榜 / blade 刀片榜 / update 更新榜 / all 全部（默认）。

## 字段

排名、书名、作者（仅榜首有）、题材（其余名次有）、榜单值与作品页链接。各榜值分别解读；同方向不足 10 本标稀疏，聚合加 `--sparse 10`。作者信息不齐，同书可能跨榜未合并，核对样本本数。

多榜聚合取同书最大「榜单值」，热度回查单榜。

## 分析维度

| 维度 | 看什么 |
|---|---|
| 月票/订阅榜 | 付费认可 |
| 新书榜 | 二次元新梗与新设定 |
| 吐槽/刀片榜 | 看互动强度；争议点需有内容证据 |
