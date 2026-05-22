# Runway — Gen-4 / Aleph / Act-Two

官網 `https://runwayml.com/`。好萊塢等級工作流，三個核心模組：
- **Gen-4 Video** — 主力 t2v/i2v 模型
- **Gen-4 References** — 最多 3 張參考圖的一致性生成
- **Aleph** — 影片編輯模型 (add/remove/change/replace/relight/restyle)
- **Act-Two** — performance capture / lip sync，從示範影片驅動角色表情

## Gen-4 Video

### Prompt 結構
Runway 偏向 **敘事式描述**，不要太 tag-heavy：

```
[Subject and context] + [Action] + [Camera] + [Style / Mood]
```

**範例：**
```
A young woman with curly hair sits at a rain-streaked window in a dimly lit
cafe, slowly stirring her coffee as she looks out. Close-up, shallow depth of
field, warm tungsten light from above. Melancholic, cinematic, 35mm film look.
```

### 參數
- 時長：5s / 10s
- 解析度：720p / 1080p / 4K (Gen-4 Turbo)
- Aspect：16:9 / 9:16 / 1:1 / 21:9 / 4:3
- Seed：可固定
- Camera Control：UI 預設 (pan/tilt/dolly/zoom/roll) + 強度 slider

## Gen-4 References

上傳最多 3 張圖作為 **style / character / environment reference**，然後用 prompt 描述場景。

**寫法要點：**
- 標記每張 ref：`@ref1 is the main character; @ref2 is the location`
- 或用自然語言：`the woman shown, in the cafe shown, sitting by the window`
- 描述動作與新元素，不重複 ref 的外觀

## Aleph (影片編輯)

Aleph 把影片丟進去 + 一個編輯指令，輸出改過的影片。不是 text-to-video，是 **video-to-video**。

### Aleph Prompt 公式
```
[動詞 (add/remove/change/replace/relight/restyle)] + [對象] + [新內容]
```

**保持簡潔。** 一次改一件事。

**範例：**
- `add a pair of sunglasses to the subject` (add)
- `remove the car in the background` (remove)
- `change the shirt color to navy blue` (change)
- `replace the sky with a stormy sunset` (replace)
- `relight the scene with warm golden hour light` (relight)
- `restyle the entire shot in Studio Ghibli animation style` (restyle)

### Aleph + Gen-4 Refs 組合工作流
1. 用 Gen-4 Image References 在 **單一首幀** 上精確擺放物件/角色
2. 把編輯好的首幀丟進 Aleph 當 reference
3. Prompt 描述動作要怎麼演變

```
Use the attached frame as the first frame.
The character raises their coffee cup and takes a sip,
steam rising from the cup. Slow dolly-in, cinematic.
```

## Act-Two (表情/口型驅動)

你錄一段自己表演的影片 (臉部、手勢) + 指定一個角色圖，Act-Two 把角色「套」到你的表演上。

**Prompt 重點：**
- 主要輸入是「driver 影片」+「character 圖」，prompt 次要
- Prompt 描述場景與燈光即可，表演由 driver 控制

## 版本變化 (2026)

- Gen-3 → Gen-4 (2025)：一致性、動作流暢度大躍進
- Act-One → **Act-Two** (2025 末)：加入身體姿態 + 聲線轉換
- Aleph 持續精進；與 Gen-4 Refs 整合越來越緊

## 運鏡

支援全套標準英文運鏡詞。Runway 的 Camera Control UI 更精準，prompt 寫運鏡是輔助。

## Negative Prompt

Runway **不使用** 傳統 negative prompt 欄位。要避免的東西直接寫在 prompt 結尾 "avoid..." 或調 seed / 重生。

## 範例

**1. Gen-4 Video — 電影級空拍**
```
Aerial drone shot descending toward a fishing village at sunset, smoke rising
from chimneys, fishing boats returning to harbor. Warm golden hour light,
anamorphic lens flares. Cinematic, Roger Deakins style.
```

**2. Gen-4 References — 角色故事**
```
(Ref 1: protagonist photo, Ref 2: vintage library, Ref 3: leather journal)
The character shown walks into the library shown, opens the leather journal
shown, and begins to write with a fountain pen. Medium shot, soft window
light, warm tones, shallow depth of field.
```

**3. Aleph — 加雪**
```
(影片輸入 + ) add gently falling snow throughout the scene, subtle accumulation
on surfaces, cold blue color grade.
```

**4. Aleph — 換風格**
```
(影片輸入 + ) restyle the entire shot in Studio Ghibli animated film style,
hand-painted backgrounds, soft watercolor palette.
```

**5. Act-Two — 角色表演**
```
Driver video: [自己演出憤怒獨白的影片]
Character reference: [武士角色圖]
Scene prompt: dojo interior, candlelight flickering, low angle close-up,
dramatic shadows.
```

## 常見錯誤

- **Aleph prompt 太複雜** — 一次只改一件。要多個改動 → 跑多輪 Aleph。
- **用 Midjourney 參數 (--ar --s)** — Runway 吃不到，用 UI 欄位。
- **Gen-4 Refs 又長篇描述角色外觀** — 會和 ref 打架。
- **期待 Runway 有原生音訊** — 目前沒有 (2026-04 狀態)。要音訊走 Veo 3 或後期加。

## 連結

- 官網：https://runwayml.com/
- Aleph Prompting Guide：https://help.runwayml.com/hc/en-us/articles/43277392678803-Aleph-Prompting-Guide
- Aleph + Reference Image：https://help.runwayml.com/hc/en-us/articles/44609246167059-Controlling-Aleph-edits-with-a-Reference-Image
- Creating with Gen-4 Video：https://help.runwayml.com/hc/en-us/articles/37327109429011-Creating-with-Gen-4-Video
- Creating with Aleph：https://help.runwayml.com/hc/en-us/articles/43176400374419-Creating-with-Aleph
- Gen-4 總覽：https://help.runwayml.com/hc/en-us/sections/39888423025683-Gen-4
- Runway Academy：https://academy.runwayml.com/ways-to-use-runway
- Research：https://runwayml.com/research

---

## 🆕 Runway 2026 進階功能完整地圖

### 1. Motion Brush 3.0

- **自動偵測可動元素** (主體、衣物、水、煙、頭髮等) — 不用手動塗
- 標記後右側 vector 設 **速度 + 方向**
- **Multi-Motion Brush：最多 5 個獨立區域**
  - 每區獨立 motion parameters
  - 例：頭髮往左飄 + 衣物往右翻 + 背景雲往上移 + 前景葉子旋轉 + 水面漣漪

### 2. Aleph (Video Editing 專用)

Aleph (2025-07 發布) = video-to-video 大模型。**action verb + object + new content** 語法：

| 動作 | 範例 |
|---|---|
| `remove` | `remove the car in background` |
| `transform` | `transform the wooden chair into marble` |
| `generate missing angles` | `generate a reverse-angle shot of the same scene` |
| `modify lighting` | `relight the scene with warm golden hour sun` |
| `add` | `add gently falling snow to the scene` |
| `restyle` | `restyle in Studio Ghibli animation` |

**關鍵：** 一次一個動作，複雜改動多跑幾次 Aleph 累積。

### 3. Act-Two (Performance Capture 2.0)

- Act-One 升級版
- **無需 mocap 設備** — 你用手機錄自己表演 (臉 + 手勢 + 身體)
- + 角色靜態圖
- 輸出：角色完美執行你的表演
- **進階：** 聲線轉換 (你說話 → 角色用自己聲線說)

### 4. Gen-4 Video + 3D Asset Integration (2026 新)

- 原生 3D asset 整合 (不再只有 2D 貼圖)
- 生成場景內可放 3D 模型
- 虛擬製片 (virtual production) pipeline 友善

### 5. Gen-4 References (最多 3 張參考圖)

- 角色 / 風格 / 環境 可同時 reference
- Prompt 用 `@ref1 as the main character, @ref2 as the location`
- 或自然語言 `the woman shown, in the cafe shown`

### 6. 進階 Prompt 工程

**Runway 偏好：**
- **Specific + descriptive** 不 conversational
- **Positive phrasing** (要什麼，不是不要什麼)
- **Active verbs** 描述主體 motion
- 明確 camera movement (`tracking shot`, `low angle`, `crane up`)
- 場景 motion + 環境元素描述
- 定義 visual style (cinematic / vintage / animated)

### 7. Gen-4 + Aleph 合成工作流

```
Step 1: Gen-4 Image References → 精確擺放角色/物件在單一首幀
Step 2: 把首幀丟進 Aleph → prompt 告訴 Aleph 動作怎麼演變
Step 3: Aleph 生成影片
Step 4: Act-Two (若要對口型) → 驅動表演
```

這個 pipeline 是好萊塢等級工作流。

### Runway 不支援什麼

- ❌ 原生音訊 (Veo / Sora / Kling 3.0 才有)
- ❌ 直接生 4K (要 Gen-4 Turbo)
- ❌ 原生 negative prompt 欄位 (要寫進 prompt 尾部 `avoid...`)

### 新連結

- [Runway Changelog](https://runwayml.com/changelog)
- [Motion Brush 3.0](https://www.fluxpro.ai/vm/runway/runway-aleph)
- [Gen-4 Complete Guide](https://aitoolsdevpro.com/ai-tools/runway-guide/)
