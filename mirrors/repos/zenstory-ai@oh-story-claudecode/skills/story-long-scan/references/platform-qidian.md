# 起点：采集与分析

选择起点时读取。脚本默认先读 `https://m.qidian.com` 页面的 SSR 内嵌数据，失败才回退 CDP/PC；文件头 `抓取方式` 标 `mobile-ssr` 或 `cdp-pc`。书库新书只走 Chrome，先说明并用 `/browser-cdp` 启动。

## 榜单与命令

`node scripts/qidian-rank-scraper.js --type {榜单} --outdir {输出目录}`（`--type all` 全采；`--mode mobile|cdp` 强制方式；`--detail yes` 仅在 CDP 模式补详情）

| 榜单 | --type | URL | 看什么 |
|------|--------|-----|--------|
| 新人签约新书榜 | newsign | qidian.com/rank/newsign/ | 新人签约作品，新风向 |
| 签约作者新书榜 | signnewbook | qidian.com/rank/signnewbook/ | 已签约作者新作风向 |
| 公众作者新书榜 | pubnewbook | qidian.com/rank/pubnewbook/ | 发现潜力作者 |
| 新人作者新书榜 | newauthor | qidian.com/rank/newauthor/ | 新人赛道 |
| 三江推荐 | sanjiang | qidian.com/sanjiang/ | 编辑精选，按周分组（非 /rank/ 路径） |
| 月票榜 | yuepiao | qidian.com/rank/yuepiao/ | 付费认可度最高 |
| 畅销榜 | hotsales | qidian.com/rank/hotsales/ | 真金白银投票 |
| 阅读指数榜 | readindex | qidian.com/rank/readindex/ | 阅读量综合 |
| 收藏榜 | collect | qidian.com/rank/collect/ | 读者关注热度 |
| 原创推荐榜 | recom | qidian.com/rank/recom/ | 读者推荐票表现 |

默认组合：新人签约新书榜 + 签约作者新书榜 + 月票榜 + 畅销榜。文件名 `起点{榜单}_{YYYYMMDD}.md`。移动端两个签约榜均取 `/rank/sign/`，`collect` 取书友榜；以文件头「移动端实际榜单」为准。

### 书库新书

要看「新书」「最近冒头」「什么在起量」时再加，默认组合不采。qidian.com/all/action0-size1-update1/ 筛选男生、连载、30 万字以下、三日内更新的作品，按人气排，每页 20 本，可补充已下新书榜但仍在更新的书。

```bash
node scripts/qidian-rank-scraper.js --type library --pages 3 --outdir {输出目录}   # 默认 3 页，最多 10，不进 --type all
```

所有页合写 `起点男频书库人气新书_{YYYYMMDD}.md`，名次连续，表示人气排名。字数由字体解码，签约/收费由移动端详情补，缺值写 `[待补]`；「新书总推荐」不进聚合热度。该筛选会拉低字数中位。跟作者说「起点最近三天还在更新的 30 万字以内新书，按人气取前 3 页，要开浏览器」。

## 字段

排名、书名、作者、题材（主类·子类）、状态、签约、收费模式、字数、总推荐、标签/最新更新/简介、作品页链接；题材、字数、总推荐缺失写 `[待补]`。聚合按主类分题材、子类作标签，热度以表头口径为准；同源的两个签约榜不作独立交叉验证。

## 分析维度

| 维度 | 看什么 |
|---|---|
| 月票榜/畅销榜 | 观察付费榜表现，不等同于订阅或追读原数 |
| 各新书榜 | 新作者、新题材的早期信号；和月票/畅销榜的题材占比对照 |
| 三江推荐 | 平台力推方向 |
| 追读率 | 当前榜单不提供，不能由月票/畅销排名换算 |
