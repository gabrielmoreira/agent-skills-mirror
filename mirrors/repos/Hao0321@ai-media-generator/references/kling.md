# Kling (可靈) — 快手 AI 影片

官方 `https://klingai.com/` (國際版) / `https://klingai.kuaishou.com/` (國內版)。目前主力版本 2.1 / 2.6 Pro / 3.0。擅長 **精準運鏡** 與 **人體物理動態**，被公認為 2025 起的市場頂尖。

## Prompt 公式

Kling 官方推薦四段式：

```
[Subject] + [Subject Motion] + [Scene] + [Camera + Lighting + Atmosphere]
```

或加強版五段式：

```
[主體+細節] + [動作+情緒] + [場景+時間+氛圍] + [鏡頭語言] + [風格/光影]
```

**範例：**

```
A stoic samurai in weathered black armor (subject)
walks deliberately forward, sword held low at his side (action)
through a misty bamboo forest at dawn, fog swirling around his ankles (scene)
slow low-angle dolly-in tracking shot from behind (camera)
cinematic, Kurosawa-inspired, muted earth tones, volumetric morning light (style)
```

## 版本差異 (2026 時點)

| 版本 | 特色 | 何時用 |
|---|---|---|
| Kling 1.6 | 便宜、快，基本 t2v/i2v | 社群短片、草稿 |
| Kling 2.0 | 運鏡開始精準，人臉穩 | 一般專案 |
| **Kling 2.1 Master** | 1080p@30fps、運鏡最準 | 多數專業用 |
| **Kling 2.6 Pro** | 提升物理、lipsync、prompt 理解 | 當前旗艦 |
| Kling 3.0 | 長片、原生音訊、更強敘事 | 最新，測試中 |

升級帶來的 prompt 變化：2.0 起可以加 **導演風格 token** (`Kurosawa-inspired`, `Wes Anderson style`)；2.6 Pro 起可在 prompt 內指定 **情緒節奏** (`slow pace`, `tension building`)。

## 模式

| 模式 | 用途 | Prompt 重點 |
|---|---|---|
| **Text-to-Video (T2V)** | 純文字生影片 | 完整五段式 |
| **Image-to-Video (I2V)** | 首幀+prompt | prompt 只描述 **動作與演變**，不重複描述畫面已有的內容 |
| **Extend** | 從現有片段往後接 | 描述下一秒發生什麼 |
| **Start/End Frame** | 首尾幀 | 兩張圖 + 中間過程描述 |
| **Multi-Image Reference** | 多圖參考 | 指明每張圖代表什麼 (角色/場景) |
| **Motion Brush** | 塗抹指定移動區域 | UI 上塗，prompt 描述整體氛圍 |
| **Camera Control** | UI 選運鏡預設 | prompt 就不用再寫運鏡 |
| **Lip Sync** | 口型對齊 | 上傳音訊；prompt 描述情緒 |
| **Elements (角色+物件)** | 組合式生成 | 角色圖 + 物件圖 + prompt |

## 參數

- **時長**：5s (預設) / 10s
- **畫面比**：16:9 / 9:16 / 1:1
- **解析度**：720p (Standard) / 1080p (Pro/Master)
- **CFG / Creativity**：0–1，預設 0.5。越高越貼 prompt，但太高會僵
- **Negative prompt**：支援

## 運鏡常用詞 (Kling 最準的組合)

- `slow dolly-in` — 最穩的情緒推進
- `tracking shot from behind` — 跟隨
- `low-angle orbit 180` — 英雄鏡
- `crane up revealing landscape` — 揭示
- `handheld, subtle shake` — 紀實感
- `static wide shot, subject walks into frame` — 經典入鏡

**Kling 運鏡禁忌：**
- 一次超過 2 個運鏡
- `infinite zoom` / `spiral zoom` (會失控)
- 自相矛盾 (pan left + pan right)

## Negative Prompt 常用

```
blurry, deformed face, extra limbs, extra fingers, distorted hands, warped anatomy,
low quality, watermark, text overlay, logo, subtitle, jittery motion, frame stutter,
plastic skin, uncanny valley, oversaturated, artifacts
```

中文版：
```
模糊、畸形臉、多出的手指、扭曲身體、低畫質、浮水印、字幕、卡頓、塑膠皮膚
```

## 進階技巧

### 1. 情緒節奏詞 (2.6 Pro+)
在 camera 段加入節奏描述：
- `slow pace, contemplative`
- `rising tension`
- `sudden impact, then stillness`

### 2. 物理提示 (physics prompt)
Kling 對物理關鍵字敏感：
- `hair blowing in the wind, cloth flowing naturally`
- `water splashing realistically`
- `dust particles catching the light`

### 3. 鏡頭時序控制 (10s 片段)
```
First 2 seconds: establishing wide shot of the street.
Then camera slowly pushes in to medium shot.
Last 3 seconds: close-up on the character's face as they realize something.
```
(Kling 2.6+ 會照做；2.1 以下較難)

### 4. I2V 的黃金法則
**不要描述畫面裡已有的東西**，只描述動作：
- ✗ `A woman with red hair in a blue dress standing by the window turns and smiles.`
- ✓ `She slowly turns toward the camera and smiles softly, her hair catching the light as she moves.`

## 高品質範例

**1. 環境空拍**
```
Aerial drone shot descending toward a mountain monastery at golden hour, prayer
flags fluttering in the wind, snow-capped peaks in the distance, golden sunlight
bathing the ancient stone walls. Cinematic, Lord of the Rings style, anamorphic
lens, warm grade.
```

**2. 人物情緒特寫**
```
Close-up of a young woman in her 20s, tears slowly forming in her eyes as she
looks up. Soft natural window light from the left, shallow depth of field. Slow
subtle push-in. Muted desaturated palette, intimate and melancholic.
```

**3. 動作 + 物理**
```
A parkour athlete leaps from a rooftop to the next, arms extended, shirt
billowing in the wind. Low angle tracking shot following his trajectory. Sunset
cityscape, lens flare. High contrast, urban cinematic grade.
```

## 連結

- 官網：https://klingai.com/
- 官方 prompt 指南 (ImagineArt 整理)：https://www.imagine.art/blogs/kling-2-1-prompting-guide
- Leonardo.Ai 官方合作指南：https://leonardo.ai/news/kling-ai-prompts/
- Kling 3.0 公式 (glbgpt)：https://www.glbgpt.com/hub/kling-3-0-prompt-guide-for-better-ai-videos
- 2.6 Pro (fal.ai)：https://fal.ai/learn/devs/kling-2-6-pro-prompt-guide
- 運鏡大全 (glbgpt)：https://www.glbgpt.com/hub/kling-ai-camera-movements-explained
- Ambience AI 2026 指南：https://www.ambienceai.com/tutorials/kling-prompting-guide

---

## 🆕 2026 Kling 3.0 / 3.0 Omni / Motion Control 3.0 完整升級

**重要：** 2026-02-05 發布 Kling 3.0，2026-03-04 Motion Control 3.0。舊 2.1/2.6 Pro 仍可用但 3.0 是主力。

### Kling 3.0 核心差異 (vs 2.6 Pro)

| 項目 | 2.6 Pro | **3.0** |
|---|---|---|
| 長度 | 10s | **15s 原生** + custom duration |
| 多鏡 | 單鏡 | **多鏡最多 6 camera cuts** (single generation) |
| 音訊 | lipsync only | **原生 audio + dialogue (多口音多語) + 自訂 SFX** |
| 輸出 | 1080p | **1080p / 4K @ 30fps + 16-bit HDR** |
| 物理 | 強 | **3D Spacetime Joint Attention + CoT reasoning** |
| 多模態 | 分離處理 | **統一架構** (video + audio + image 一個模型) |

### Kling 3.0 Prompt 新格式 (Shot 標註)

舊 2.6 五段式升級為 **Shot 1 / Shot 2 / Shot 3** 明確標註：

```
Shot 1 (0-4s, wide establishing):
[subject + action + environment + camera]

Shot 2 (4-9s, medium tracking):
[continue / cut to / new angle]

Shot 3 (9-15s, close-up):
[emotional beat + resolution]

Style: [shared style across all shots]
SFX: [per shot or unified]
Soundtrack: [full piece]
```

**關鍵規則：**
- 角色/物件/場景在 **Shot 1 開頭完整定義**，後續用 `The same character` 維持
- 每角色明確 dialogue (Kling 3.0 自動 match 角色與台詞)
- 導演風格/藝術風 token 反應更準 (3.0 升級)

### Kling 3.0 Omni (Unified Multimodal)

Omni 是 3.0 的「全能版」— 一個模型同時做：
- 影片生成 (含音訊)
- 角色聲音一致性 (voice consistency 跨片段)
- Video source editing (編輯既有影片)
- Image 3.0 Omni (靜態圖 4K)

**Image 3.0 Omni Series Mode：** 多張靜態圖保持角色一致敘事 (類似 Nano Banana Pro 的 storyboarding)，原生 2K / 4K 輸出。

### Motion Control 3.0 (角色驅動)

**功能：** 靜態角色圖 + 參考動作影片 → 3.0 映射全身姿態 + 手勢 + 表情。

**輸入：**
- 1 張角色靜態圖 (character reference)
- 3-30 秒動作參考影片 (mocap source)

**輸出：** 角色完美執行該動作，物理合理。

**進階功能：**
- Facial binding：多參考圖/影片綁定面部，複雜表情 + 遮擋處理
- Omni One physics engine

**類比 Runway：** 像 Act-Two 但 Kling 3.0 Omni 整合在同平台。

### Custom Multi-Shot 工作流

1. 單一 prompt 內寫 `Shot 1 / Shot 2 / ... / Shot 6`
2. 開 `Multi-Shot` toggle
3. 設 custom duration (5-15s)
4. 3.0 自動在各 shot 之間做連貫剪接 + 保持元素一致

### Start + End Frame (首尾幀)

在 Kling UI `Add start and end frames` 按鈕，上傳兩張圖，3.0 生成中間過程。

### 免費 tier 可用模型

- **v4.5-all** 級別 (相當 2.1 Standard)
- 高階 (3.0 / 3.0 Omni / Motion Control 3.0) 需訂閱或 **Fast-Track credits** (實測 45 credits / 5s)

### 新連結

- [Kuaishou 官方公告](https://ir.kuaishou.com/news-releases/news-release-details/kling-ai-launches-30-model-ushering-era-where-everyone-can-be/)
- [Kling VIDEO 3.0 User Guide](https://app.klingai.com/global/quickstart/klingai-video-3-model-user-guide)
- [Motion Control 3.0](https://kling3.io/motion-control-3-0)
- [Kling 3.0 Omni Guide](https://soravideo.art/blog/kling-3-omni-guide)
