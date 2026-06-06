# Kling (可靈) — 快手 AI 影片

官方 `https://kling.ai/app/` (新版，舊 `klingai.com` / `app.klingai.com` 會 redirect) / `https://klingai.kuaishou.com/` (國內版)。**當前主力 = Kling 3.0 / 3.0 Omni (O3) / Motion Control 3.0**（2026-02 發布）。擅長 **精準運鏡**、**人體物理動態**、**區域運動控制 (Motion Brush)**，被公認為 2025 起的市場頂尖、控制力最強的消費級影片模型。

> **這份檔案的讀法：** §1–§9 是跨版本通用的 prompt / 運鏡 / 模式心法（任何版本都適用）；§「2026 升級」開始是 3.0 專屬新能力。先讀通用心法，再依手上的版本挑新功能。

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

## 版本差異 (2026 時點) — 能力矩陣

| 版本 | 長度 | 解析度 | 音訊 | 特色 | 何時用 |
|---|---|---|---|---|---|
| Kling 1.6 | 5/10s | 720p | ✗ | 便宜快、**Elements 多圖參考自此起** | 社群短片、草稿、便宜跑 Elements |
| Kling 2.0 | 5/10s | 720p | ✗ | 運鏡開始精準、人臉穩 | 一般專案 |
| **Kling 2.1 Master** | 5/10s | 1080p@30fps | ✗ | 運鏡最準（純畫面） | 不需音訊的專業片 |
| **Kling 2.5 Turbo** | 5/10s | 1080p | ✗ | **快 ~25%**、物理（撞擊/流體）升級、**多語 prompt** | 動作/運動/CP 值最佳 |
| **Kling 2.6 Pro** | 10s | 1080p | lipsync | 物理、prompt 理解、口型 | 需口型的單鏡 |
| **Kling 3.0 / O3** | 3–15s | **4K 原生** | **原生音訊** | 多鏡(6 cut)、原生對白(5 語)、4K、CoT 物理 | **當前旗艦，多鏡敘事** |
| **Kling 3.0 Omni** | 3–15s | 4K | 原生 + 聲音一致 | 統一多模態（影片+音訊+圖+影片編輯） | 跨片段角色聲音一致、video editing |

> **命名釐清（待驗證細節）：** 「**O1 / O3**」是 Kling 的 Omni 模型線；官方資料指 3.0 把舊 **Video 2.6 + O1** 合併成統一架構，**O3 ≈ 3.0 / 3.0 Omni 的對外代號**。UI 下拉可能同時出現 `3.0` 與 `3.0 Omni`，挑 Omni 走多模態。國內版另有 `O3` 標籤（命名以當下 UI 為準）。

**升級帶來的 prompt 變化（累積）：**
- **2.0 起** → 可加 **導演風格 token** (`Kurosawa-inspired`, `Wes Anderson style`)
- **2.5 Turbo 起** → **非英文 prompt 直接可用**（波斯語/韓/日…不必翻英），物理因果更準
- **2.6 Pro 起** → prompt 內可指定 **情緒節奏** (`slow pace`, `tension building`)
- **3.0 起** → **Shot 標註多鏡**、引號內 **多語對白 + 口音/方言**、4K token 生效

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
- **Negative prompt**：支援（用法見 §Negative Prompt 最佳實踐）
- **Mode**：Standard（720p，便宜）vs Professional/Pro（1080p+，貴）

## 價格 / Credits（2026，WebSearch 實測）

**免費 tier：** 登入後 **66 credits/日**，24h 後過期（不累積）。3.0 的 720p/5s/無音訊 = 30 credits → 免費每天約 **2 支**。實務上 Fast-Track 免排隊（免費也享）。

**訂閱（首月折扣，續訂回原價）：**

| 方案 | 月費 | 月 credits | 約略產能 | 商用 |
|---|---|---|---|---|
| Free | $0 | 66/日 | 每日 ~2 支 | ✗ |
| Standard | $6.99 起（續 ~$8.8） | 660 | ~33 支 720p | ✓ |
| Pro | ~$25.99 | 3000 | ~150 支 720/1080p | ✓ |
| Premier | ~$64.99 | 8000 | ~400 支 1080p | ✓ |
| Ultra | ~$127.99–180 | 26000 | ~1300 支 | ✓ |

**Credit 消耗（3.0 概算，依設定變動）：**
- 基準 **6 credits/秒**（720p、無音訊）→ 12 credits/秒（1080p + 原生音訊）
- 5s 影片：Standard mode ~10 / Pro mode ~35；**3.0 720p/5s 無音訊 = 30**（實測扣 45 含 Fast-Track/音訊配置）
- 加 **原生音訊** 顯著加價（2.6+ 音訊版可達 50–200 credits/支）
- **10s 1080p × 3 次 iteration ≈ 360 credits**

> **省 credit 心法：** 先用 **2.5 Turbo / Standard 720p 無音訊** 跑構圖草稿，定稿才切 3.0 + 音訊 + 1080p。免費帳號優先用 Fast-Track 額度，別把音訊預設開著燒 credit。月配額 **月底歸零不滾存**，別囤。

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

## Negative Prompt 欄位最佳實踐

Kling 的 negative prompt 是**獨立欄位**（不要寫進主 prompt）。最佳用法：

- **只放真正反覆出現的瑕疵**，不要一次塞 30 個詞稀釋權重。先跑一版看實際壞在哪，再針對性加 3–6 個。
- **人像戲固定組：** `deformed face, extra fingers, distorted hands, warped anatomy, plastic skin`
- **動作戲固定組：** `jittery motion, frame stutter, motion blur artifacts, limbs morphing`
- **乾淨輸出組：** `watermark, text overlay, logo, subtitle, oversaturated`
- **不要在 negative 放「想要的相反詞」逼風格**（如想要暗就寫 `bright`）——效果不穩，正面 prompt 直接寫 `low-key lighting` 更可靠。
- **i2v 時別把畫面既有元素寫進 negative**（會打架）。

## 進階功能完整地圖

每個功能：**用途 / prompt pattern / 何時用**。Kling 的差異化就在這些控制器——比 Veo（敘事+音訊強但控制弱）多一整層 hands-on 控制。

### Motion Brush（運動筆刷）— Kling 最強差異化
- **用途：** 在起始圖上**塗抹**指定區域，精確控制「哪裡動、往哪動、動多大」，不靠文字描述。2026 公認是消費級模型裡**最強的可控運動**功能。
- **操作：** UI 上塗 mask + 拉動方向箭頭；prompt 只寫**整體氛圍**，不重述運動（運動已由筆刷定義）。
- **何時用：** 只想動局部（旗子飄、頭髮動、車前進、水流），背景靜止；或文字怎麼描述都動錯地方時。
- **失敗修法（關鍵洞察）：** 壞掉通常是 **mask 邊緣滲色**，而 **真正的變因是起始圖乾不乾淨，不是筆刷本身**。→ 用**邊緣清晰、主體與背景分離度高**的圖；塗 mask 時**留一點安全邊距**別貼著輪廓塗。

### Elements / Reference Injection（多圖參考）— 角色一致性主力
- **用途：** 上傳 **1–4 張圖**當「元素」（人/動物/物件/場景），鎖定角色長相+服裝跨鏡一致。**1.6 起就有**（便宜版可跑）。
- **Prompt pattern（reference tag 語法，待 UI 驗證）：**
  ```
  Use <<<element_1>>> as Luna, the same 7-year-old girl from the reference,
  walking through <<<element_2>>> (the autumn forest). She picks up a leaf and smiles.
  ```
- **參考圖規則（實測重點）：** 用 **2–4 張不同角度**（正/側/3-4 面）建「角色 sheet」讓模型 lock 住 3D 結構；**背景必須純白/綠幕**（乾淨去背），否則背景會污染識別。
- **3.0 的 Bind Subject（綁定主體）：** i2v 模式開 `Bind Subject` toggle，丟一張清晰圖即固定臉+衣著——比 Frames 更靈活（參考數 > 首尾兩張）。
- **何時用：** 系列鏡頭/分鏡要同一角色；產品要在多場景出現同一個 SKU。
- **vs Frames vs T2V：** Elements 比 T2V 多控制（你指定哪些要一致）；比 Frames 多彈性（可給超過首尾兩張的參考）。

### Lip Sync（對嘴）
- **用途：** 既有 Kling 影片 + 上傳音訊 → 角色嘴型對齊。（3.0 原生音訊已內建口型；Lip Sync 是給「先有片、後配音」的流程。）
- **Prompt/操作：** 上傳乾淨人聲音檔（背景噪音越少越準）；prompt 只描述情緒。
- **硬限制（實測）：** **單句台詞控制在 3–5 秒**，長獨白會 desync。長台詞請拆多段分句處理。
- **何時用：** 對白短句、UGC 口播、虛擬主播。長篇旁白改用 3.0 原生音訊多鏡。

### Camera Control（運鏡控制）
- **用途：** UI 預設 pan / tilt / zoom / orbit / tracking（競品常缺或要加價）。
- **Prompt pattern：** 選了 UI 預設就**別在 prompt 再寫運鏡**（會打架）。要文字運鏡就**只用文字、不開 UI 預設**，二選一。
- **配 Motion Brush：** 運鏡 + 筆刷可疊——做「相機環繞 + 主體局部動作」的複雜編排。
- **何時用：** 要可複現、乾淨的單一運鏡；產品環繞。

### Start / End Frame（首尾幀）
- **用途：** 上傳兩張圖，Kling 補中間過程。最適合**轉場 / 史詩揭示 / 變身**。
- **Prompt pattern：** 只描述**中間如何演變**（`gradually transforms`, `camera pulls back to reveal`），不重述兩張圖內容。
- **何時用：** 有明確起點與終點構圖；無縫接片。

### Motion Control 3.0（角色驅動 / 動作捕捉）
- 詳見下方「2026 升級」§。一句話：**靜態角色圖 + 動作參考影片 → 角色執行該動作**（含手勢/表情）。對標 Runway Act-Two，但整合在 Kling 同平台。

### Multi-Shot（多鏡，3.0）
- 詳見「2026 升級」§。一個 prompt 用 `Shot 1 / Shot 2 / …`（最多 6 cut）一次出多鏡，自動保持空間連續。**取代** 6 次獨立 chain（省 2/3 時間+credit）。

---

## 進階 Recipe

### R1. 產品 360° 環繞（電商主圖動態化）
**用 i2v + Camera Control orbit（或 3.0 多鏡）。**
```
[i2v 起始圖：產品置中、純色背景、棚拍光]
Prompt（前綴固定）：根據圖片中的物體、畫面、風格來生成影片。
The camera performs a slow, smooth 360-degree orbit around the product,
maintaining consistent studio lighting, soft reflections sweeping across the
surface. Static product, only the camera moves. Seamless loop.
Camera（UI）：Orbit 180 ×2 或 prompt 內單一 orbit
Negative：jittery motion, warping, background change, watermark
```
**要點：** 產品**完全靜止只動相機**（明確寫 `static product, only the camera moves`），否則 SKU 會變形。要無縫循環加 `seamless loop`。10s + 1080p。

### R2. 角色多鏡一致性（分鏡敘事）
**用 Elements 鎖角色 + 3.0 Multi-Shot 一次出。**
```
參考：上傳同角色 2–4 張不同角度圖（純白背景）建 Subject
Shot 1 (0-5s, wide): <<<element_1>>>, the same young woman, walks into a neon-lit
  alley at night. Slow tracking shot from behind.
Shot 2 (5-10s, medium): The same character turns under a flickering sign,
  rain starting to fall. Push-in.
Shot 3 (10-15s, close-up): Close on her face, a single tear, resolve in her eyes.
Style: cinematic noir, teal-orange grade, anamorphic, consistent across all shots.
SFX: rain, distant traffic. Soundtrack: slow brooding synth.
```
**要點：** 角色在 **Shot 1 完整定義**，後續用 `the same character` / `<<<element_1>>>` 維持。風格寫在共用 `Style:` 行。一次生成省去逐鏡對齊。

### R3. 局部運動廣告（靜態場景 + 一個動點）
**用 Motion Brush。**
```
[起始圖：乾淨去背、主體與背景高對比的產品/人物圖]
塗 mask：只塗要動的區域（如飄動的絲巾 / 升起的蒸汽 / 轉動的風扇）
拉箭頭：給明確方向
Prompt：warm cinematic atmosphere, soft volumetric light, subtle dust particles.
（不寫運動——運動由筆刷定義）
```
**要點：** 起始圖乾淨度 = 成敗關鍵。mask 留安全邊距。背景明確要靜止。

### R4. 角色動作移植（舞蹈/武打）
**用 Motion Control 3.0。**
```
角色：1 張靜態角色圖（清晰、正面佳）
動作源：3–30s 動作參考影片（舞蹈/格鬥 mocap）
（開 Facial binding 綁多參考圖處理複雜表情/遮擋）
```
**要點：** 角色圖越清晰、動作源越乾淨，姿態+手勢+表情映射越準。

---

## 常見失敗模式 + 修法

| 症狀 | 成因 | 修法 |
|---|---|---|
| Motion Brush mask 邊緣滲色、動錯地方 | **起始圖不夠乾淨**（非筆刷問題） | 換邊緣清晰、主體/背景高對比的圖；mask 留安全邊距 |
| 角色跨鏡長相/服裝漂移 | 只給 1 張參考、或參考圖有雜背景 | Elements 給 **2–4 張不同角度 + 純白背景**；3.0 開 `Bind Subject` |
| 產品 360 環繞時 SKU 變形 | 模型以為產品要一起動 | prompt 明寫 `static product, only the camera moves`；別開高 creativity |
| 對白嘴型對不上、後半 desync | 單句台詞太長 | **每句 3–5 秒**，長台詞拆多段；音檔去噪 |
| 運鏡亂飄/失控 | 一次 >2 運鏡，或 UI 預設與 prompt 文字運鏡**同時**下 | 運鏡 ≤2；UI 預設 **OR** 文字運鏡二選一，別並用 |
| i2v 生出的東西跟圖不符 | prompt 重述了畫面已有內容，與圖打架 | i2v 前綴固定「根據圖片中的物體、畫面、風格來生成影片」，後面**只寫運動/演變** |
| 多鏡之間跳 tone / 不連戲 | 沒有共用 Style 行、角色未在 Shot 1 定義 | 加 `Style:` 共用行；角色 Shot 1 完整定義 + 後續 `the same character` |
| 非英文 prompt 出來品質差 | 用了舊版（<2.5 Turbo） | 切 **2.5 Turbo / 3.0**（原生多語）；或場景描述用英、對白用原語 |
| 燒太多 credit | 預設開著原生音訊 + 1080p 跑草稿 | 草稿用 2.5 Turbo / 720p / 無音訊；定稿才升規格（見 §價格） |

---

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

- 官網（新）：https://kling.ai/app/ ｜ 舊 https://klingai.com/（會 redirect）
- **官方 Motion Control 使用指南：** https://app.klingai.com/global/quickstart/motion-control-user-guide
- **官方 角色一致性指南：** https://app.klingai.com/global/quickstart/ai-video-character-consistency
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
- [Kling 2.5 Turbo Prompt Guide (Atlabs)](https://www.atlabs.ai/blog/kling-2-5-turbo-prompting-guide)
- [What is Kling O3 (MindStudio)](https://www.mindstudio.ai/blog/what-is-kling-o3-latest-video-model)
- [Kling 全模型 prompt 指南 (VEED)](https://www.veed.io/learn/kling-ai-prompting-guide)
- [Kling 3.0 Reference / 角色一致性 (MagicHour)](https://magichour.ai/blog/kling-30-reference-guide)
- [Kling AI 定價完整指南 2026 (eesel)](https://www.eesel.ai/blog/kling-ai-pricing)
- [Kling 3.0 多鏡 + 原生音訊完整指南 (Morphic)](https://morphic.com/resources/how-to/kling-3.0)
