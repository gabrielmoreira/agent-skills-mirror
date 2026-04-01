---
name: weather
description: "查询全球任意城市的实时天气和未来天气预报。当用户提到天气、气温、降雨、湿度、风力、穿衣建议、出行建议等天气相关话题时使用此技能。支持中英文城市名。例如：'北京天气怎么样'、'明天上海会下雨吗'、'Tokyo weather forecast'、'这周末适合户外活动吗'。"
---

# Weather — 天气查询与预报

使用免费的 Open-Meteo API 查询实时天气和 7 天预报，无需 API Key。

## 工作流程

### 1. 解析城市

从用户消息中提取城市名。如果未指定城市，询问用户或使用上次查询的城市（检查 CONTEXT.md）。

### 2. 获取坐标

使用 Open-Meteo Geocoding API 将城市名转为经纬度：

```bash
curl -s "https://geocoding-api.open-meteo.com/v1/search?name=Beijing&count=1&language=zh"
```

从返回的 JSON 中提取 `latitude`, `longitude`, `name`, `country`。

### 3. 查询天气

**实时天气 + 7天预报**（一次请求全部获取）：

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max&timezone=auto&forecast_days=7"
```

### 4. 解读天气代码

将 `weather_code` 转为可读文字：

| Code | 天气 | | Code | 天气 |
|------|------|-|------|------|
| 0 | 晴天 ☀️ | | 51-55 | 毛毛雨 🌧️ |
| 1-3 | 多云 ⛅ | | 61-65 | 雨 🌧️ |
| 45-48 | 雾 🌫️ | | 71-77 | 雪 ❄️ |
| | | | 80-82 | 阵雨 🌦️ |
| | | | 95-99 | 雷暴 ⛈️ |

### 5. 回复用户

用自然语言回复，包含：

**实时天气**：
- 城市名 + 当前温度 + 体感温度
- 天气状况（晴/多云/雨等）
- 湿度 + 风速风向
- 降水量（如果有）

**未来预报**（按用户需求，默认 3 天）：
- 每天：最高/最低温度 + 天气 + 降水概率

**实用建议**（可选）：
- 穿衣建议（基于温度和风速）
- 出行建议（基于降水概率）
- 紫外线提醒（晴天高温时）

## 回复示例

```
🌤️ 北京今日天气

当前温度 22°C（体感 20°C），多云，湿度 45%，东南风 12 km/h。

📅 未来三天预报：
• 明天（周二）：晴，18-26°C，降水概率 5%
• 后天（周三）：多云转阴，15-22°C，降水概率 35%
• 大后天（周四）：小雨，12-18°C，降水概率 80%

💡 建议：今天适合外出，明天气温回升可穿薄外套。周四建议带伞。
```

## 注意事项

- Open-Meteo 免费无限制，无需 API Key
- 温度单位默认摄氏度，如用户要求可切换华氏度（加 `&temperature_unit=fahrenheit`）
- 如果 geocoding 返回多个结果，选第一个（最相关），必要时确认
- 对中文城市名，geocoding 参数加 `&language=zh` 获得中文结果
