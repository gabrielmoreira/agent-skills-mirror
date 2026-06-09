---
name: china-weather
description: 使用中国国家级公开天气数据查询中国天气。支持国家气象中心/中央气象台 nmc.cn、中国气象局天气页面 weather.cma.cn、中国天气网 weather.com.cn 的公开天气信息，覆盖城市实况、7 天预报、预警、空气质量、近期小时观测、未来逐小时预报、全国实况/预报地图、实况排行、雷达/卫星图层、全国预警列表、交通/环境/灾害/台风海洋/农业/数值预报等官方产品页；当用户需要判断未来具体时段是否下雨、出行、通勤、骑行、航班/高铁安排或天气风险时，按需返回可访问来源的数据、来源和发布时间。
---

# 中国天气

## 数据源策略

使用 `scripts/nmc_weather.py` 作为统一入口。不要在技能层规定哪个网站优先、哪个网站次要；当多个来源都返回数据时，保留各来源的字段、来源、发布时间和抓取时间，让调用智能体结合用户问题自行判断。

当用户问到未来具体小时段，例如“明天下午两点有没有雨”“几点开始下雨”“骑车路上会不会淋雨”，加 `--hourly-forecast`，脚本会返回 `https://www.weather.com.cn` 的未来逐小时预报数据。

`https://weather.cma.cn` 是中国气象局天气展示页面，可用 `cma-healthcheck`、`cma-city`、`cma-page` 或 `query --include-cma` 查询。这个站点在某些网络或客户端环境里可能被安全策略拦截或断开；如果返回 `ok:false`，保留失败状态，不要绕过拦截，也不要编造这个来源的数据。

不要抓取广告、访谈、社交组件、推荐服务或页面装饰。只保留可用于智能体判断的天气数据、官方产品文字、官方产品图片地址、来源和时间。

这个技能只提供结构化数据、来源、发布时间和风险字段。不要规定调用智能体的用户回复口吻、格式或固定话术；让调用智能体根据用户问题、记忆和人设自行组织回答。

如果来源不可访问、字段缺失或城市无法唯一解析，返回脚本给出的失败数据，不要编造天气值。

## 快速使用

先查看能力和产品清单：

```bash
python scripts/nmc_weather.py catalog
python scripts/nmc_weather.py catalog --group 台风海洋
```

城市天气：

```bash
python scripts/nmc_weather.py query 北京
python scripts/nmc_weather.py query 朝阳 --province 北京
python scripts/nmc_weather.py query 上海 --province 上海 --hourly-forecast --hourly-forecast-limit 96
python scripts/nmc_weather.py query 广州 --province 广东 --hourly-forecast --include-cma
python scripts/nmc_weather.py query 北京 --daily-chart 7 --include-climate
```

全国和区域数据：

```bash
python scripts/nmc_weather.py map-weather --kind real --city 广州 --limit 20
python scripts/nmc_weather.py map-weather --kind tomorrow --city 天津 --limit 20
python scripts/nmc_weather.py rank --type rain --hours 1 --limit 20
python scripts/nmc_weather.py alerts --province 北京 --limit 20
python scripts/nmc_weather.py layers --kind radar --limit 12
python scripts/nmc_weather.py layers --kind satellite --limit 12
```

官方产品页、公报和图像产品：

```bash
python scripts/nmc_weather.py product weather-bulletin
python scripts/nmc_weather.py product precipitation-1d
python scripts/nmc_weather.py product traffic
python scripts/nmc_weather.py product geohazard
python scripts/nmc_weather.py product typhoon-warning
python scripts/nmc_weather.py product marine-weather
```

中国气象局天气页面：

```bash
python scripts/nmc_weather.py cma-healthcheck
python scripts/nmc_weather.py cma-city 广州 --province 广东
python scripts/nmc_weather.py cma-page traffic
```

安装或连通性检查：

```bash
python scripts/nmc_weather.py healthcheck
```

## 入口选择

用户问单个中国城市当前和未来几天天气：用 `query`；需要同时返回中国气象局天气页面城市数据时加 `--include-cma`。

用户问某个未来小时是否下雨：用 `query --hourly-forecast`；需要同时返回中国气象局天气页面城市数据时加 `--include-cma`。

用户明确需要多个官方页面数据或想查中国气象局天气展示页：用 `query --include-cma` 或 `cma-city`。如果 `cma_city_page.ok` 为 false，保留失败状态，并继续查看其它已经返回的数据。

用户问全国或某省哪里正在下雨、气温、风速、湿度、站点实况：用 `map-weather --kind real`。

用户问全国或某省今天/明天城市预报分布：用 `map-weather --kind today` 或 `map-weather --kind tomorrow`。

用户问“哪里雨最大”“哪里最热/最低温”“风最大”：用 `rank`。

用户问预警信号、灾害预警、某省当前预警：用 `alerts`；单个城市结果里的 `warning` 也需要纳入判断。

用户问雷达、卫星、云图、降水回波、临近降水形势：用 `layers` 或 `product radar-china`、`product satellite-fy4b`。

用户问官方公报、交通气象、山洪、地灾、渍涝、森林/草原火险、环境气象、海洋、台风、农业或数值预报：先用 `catalog` 找产品标识，再用 `product <id>`。

用户问 weather.cma.cn 上的展示页、首页排行、城市预报地图、预警地图、卫星、降水或交通气象展示：可以运行 `cma-healthcheck` 检查脚本访问状态。可访问时用 `cma-page <id>`；不可访问时保留失败状态，并继续查看其它已经返回的数据。

城市名歧义时加 `--province`。已知国家气象中心站点代码时可用：

```bash
python scripts/nmc_weather.py query --station-id Wqsps
```

## 数据使用契约

先检查 `schema_version` 和 `ok`。如果 `ok` 为 false，把结果视为来源或查询失败。

评估天气风险时同时查看：

- 城市预警信号或 `alerts`
- 数据发布时间与当前查询时间的距离
- 今天和明天预报
- 未来逐小时预报数据
- 雷达、卫星、实况地图和实况排行
- 近期小时观测中的降水、风力趋势
- 后续 3-7 天预报和官方产品页

`recent_hourly` 是近期观测，不是未来预报。`hourly_forecast` 是未来逐小时预报数据，不是实况。`product` 和 `layers` 返回的是官方页面/图像产品信息，必须查看产品时间、页面生成时间、图上时间与当前查询时间的距离。

`cma_city_page` 和 `cma-page` 是中国气象局天气展示页数据。它们可能因站点安全策略返回 `ok:false`；这种情况下不要重试绕过，也不要编造这个来源的结论。

当用户关心“某天某个小时是否下雨”时，读取 `hourly_forecast.hours[]` 中的 `time`、`weather`、`temperature_c`、`humidity_percent` 和 `precipitation_signal`。如果 `hourly_forecast.ok` 为 false，保留失败状态，并继续查看其它已经返回的数据。

把 `null` 当作缺失数据。脚本会把国家气象中心的 `9999` 等占位值转成 `null`，不要当成有效天气值。

面向智能体的状态值使用中文。风险 `level` 使用 `低` / `中` / `高` / `严重`，日期关系使用 `过去` / `今天` / `未来` / `未知`。

使用 `publish_time`、`publish_age_minutes`、`source.retrieved_at`、`page_generated_time`、图像 `time`、`current_risk`、`overall_risk` 作为结构化输入。只提醒调用智能体注意比较数据发布时间与当前查询时间的距离；本技能不做时效等级判断。

## 来源细节

需要端点细节、字段含义或更新频率边界时，再读取 `references/nmc-source.md`。
