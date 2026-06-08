# 反瑕疵品質控制 Playbook (Quality Control / Anti-Flaw)

**定位：** 當生成結果「看起來爛」「有瑕疵」「不夠精緻」，這裡是**系統化排查 + 修法**。不是換 prompt 賭運氣，是針對**已知失敗模式**對症下藥。

**核心心法：** 90% 的「廣告級瑕疵」來自 3 個根因 ——
1. **時間不穩定** (temporal instability)：物件在 frame 間變形 / 閃爍 / 漂移
2. **物理不可信** (physics break)：液體、布料、光影、重量感不對
3. **主體完整性破壞** (subject integrity loss)：產品 logo / 文字 / 形狀在動畫中走樣

對應 3 招：**鎖時間、鎖物理、鎖主體**。下面逐一拆。

---

## 0. 先分類瑕疵 — 對症才能下藥

看到爛結果，先問「是哪一類瑕疵」：

| 症狀 | 類別 | 跳到 |
|---|---|---|
| 產品/臉/手在影片中途變形、扭曲、長出多餘部分 | 主體完整性 | §1 |
| 畫面閃爍、抖動、材質沸騰 (texture boiling) | 時間穩定 | §2 |
| 液體/煙/布/水花動得很假、像果凍 | 物理可信度 | §3 |
| 文字/logo 變成鬼畫符 | 文字渲染 | §4 |
| 整體「塑膠感」「AI 感」「廉價感」 | 質感分級 | §5 |
| 運鏡亂飄、多鏡頭硬切突兀 | 運鏡控制 | §6 |
| 構圖死板、主體置中無聊、留白怪 | 構圖 | §7 |

**多重瑕疵 → 從 §1 主體完整性 先修**（最毀廣告），再往下。

---

## 1. 主體完整性 (Subject Integrity) — 廣告最致命

產品廣告的鐵律：**產品本身絕不能變形**。客戶能容忍背景普通，不能容忍 logo 歪、瓶身扭、鞋子變鞋。

### 根因
- 模型對「主體」沒有強約束，動畫過程中重新詮釋形狀
- Prompt 把太多注意力放在運鏡/氛圍，主體描述反而薄弱
- 運鏡太劇烈（快速 orbit / 大角度）→ 模型每幀「重新想像」產品

### 修法（prompt 側）
1. **主體描述放最前 + 給足細節錨點**：材質、輪廓、剛性。
   - ❌ `a perfume bottle rotating`
   - ✅ `a rigid glass perfume bottle with a fixed metallic cap, solid unchanging form, the bottle maintains exact shape and proportions throughout`
2. **明寫「形狀不變」指令**（多數新模型吃）：
   - `the product maintains consistent shape, label, and proportions across all frames`
   - `rigid object, no deformation, no morphing, structural integrity preserved`
3. **限制運鏡幅度**：產品鏡頭用 `slow`、`subtle`、`gentle`，避免 `fast orbit 360`。一次最多 180° 環繞。
4. **i2v 優於 t2v 做產品**：先用 Seedream 5.0 / Nano Pro / MJ 定死產品 hero 圖 → i2v 只動畫化。**這是產品廣告最可靠路徑**，但要校準期待 ↓。

> **⚠️ 實測校準（2026-06-05 OiiOii Seedance i2v）：i2v 鎖形狀 ≠ 完美凍結。**
> 用 Seedream 5.0 hero（精華液瓶）→ Seedance 2.0 pro i2v 實測：**構圖 / 材質 / 打光 / 配色 / 主體類型忠實沿用**，但**瓶身比例仍中度漂移**（影片版較寬、液位變、自己長出水珠）。
> 結論：i2v 把「這是什麼 + 什麼質感」鎖得很好，但「精確輪廓比例」在 Seedance 仍有重繪空間。
> **要更嚴格的形狀凍結：** (a) hero 圖背景極簡乾淨（少干擾）；(b) i2v prompt 明寫 `產品 rigid 形狀不變`；(c) 改用 **Kling 3.0 Start Frame**（首幀鎖定比 Seedance i2v 更硬）+ Motion Brush 只刷背景/光，產品本體不刷 = 幾乎不動；(d) 運鏡越小（subtle dolly > 大 orbit）漂移越少。

### 修法（negative 側，支援的模型）
```
deformed product, morphing shape, warping geometry, melting object,
inconsistent label, distorted logo, shape-shifting, structural collapse,
liquid product (若是固體), bending rigid object
```

### Seedance / Kling 專屬
- Seedance 2.0：產品鏡頭關鍵字 `solid form`、`rigid structure`、`product integrity`；運鏡用「ONE camera motion per shot」
- Kling：用 **Start Frame 鎖死產品圖** + Motion Brush 只刷「要動的部分」（如水花），產品本體不刷 = 不動

---

## 2. 時間穩定 (Temporal Stability) — 閃爍/抖動/沸騰

### 症狀
材質表面「沸騰」(texture boiling)、細節在幀間跳動、整體閃爍、地平線漂移。

### 根因
- 太多高頻細節（密集紋理、大量小物件）模型每幀重算不一致
- 缺乏「穩定」指令
- 解析度/模型檔次不足以 hold 住複雜場景

### 修法
1. **明寫穩定指令**：
   - `temporally stable, consistent textures across frames, no flickering, steady detail`
   - `locked-off composition` (如果是固定機位)
   - `stable horizon, no drift`
2. **減少高頻雜訊**：背景簡化（純色 / 漸層 / 柔焦 bokeh），讓模型專注主體。「純黑虛空」「攝影棚無縫背景」是穩定神器。
3. **降低同時運動的元素數量**：一個鏡頭最多 1-2 個主要運動。
4. **加 motion blur 詞**：`subtle motion blur` 反而讓抖動看起來像有意的動態，不是 bug。
5. **升檔次**：Seedance pro > fast；Kling Pro > Std；解析度拉到模型上限。

### Negative
```
flickering, texture boiling, temporal artifacts, jittery, frame stutter,
shimmering, strobing, unstable detail, popping, ghosting
```

---

## 3. 物理可信度 (Physics) — 液體/布料/煙/重量

廣告最容易露餡的地方。AI 的水花、布料、煙常常「動得很假」。

### 通用修法
- **明寫物理引擎級詞彙**（新模型理解）：
  - `physically accurate, realistic weight and momentum, natural gravity`
  - `ray-traced fluid simulation`（流體）
  - `cloth simulation with natural drape and inertia`（布料）
  - `volumetric smoke with natural turbulence and dissipation`（煙）
- **給時間感**：慢動作讓物理更可信 — `extreme slow motion, high-speed camera capture, 1000fps detail`
- **參考真實攝影**：`macro product photography, commercial beauty shot` 觸發模型的「廣告攝影」先驗，物理較準

### 分材質速查

| 材質 | 關鍵 token | 常見 bug | 修法 |
|---|---|---|---|
| 水/液體 | `crown splash, surface tension, caustics, ray-traced refraction` | 像果凍、不連續 | 加 `slow motion` + `physically accurate fluid` |
| 玻璃 | `subsurface scattering, refraction, specular highlights` | 反射閃爍、穿透錯 | 簡化背景、固定光源 |
| 金屬 | `brushed metal, anisotropic reflection, metallic specular` | 反射沸騰 | `stable reflections` + 慢運鏡 |
| 布料/絲 | `flowing fabric, natural drape, cloth inertia` | 僵硬或亂飄 | `gentle motion` + `natural weight` |
| 煙/霧 | `volumetric, turbulent flow, natural dissipation` | 像棉花糖 | `wispy, fine particulate, god rays` |
| 食物 | `fresh, glistening, steam rising, appetizing` | 塑膠感 | `natural texture, subsurface scattering, soft key light` |

### Veo / Sora-class（強物理）
Runway Gen-4.5、Veo 3.1 物理理解最強。複雜流體/碰撞優先用這兩個，不要用弱物理模型硬做。

---

## 4. 文字渲染 (Text) — logo / 字幕 / 包裝字

### 鐵律
- **影片模型幾乎都不會渲染清晰文字**。Seedance/Kling/Runway 的文字 = 鬼畫符。
- **⚠️ 例外（2026-06-08 實測）：Google Gemini Omni Flash（Flow）能渲染短英數品牌名**。引號標注 + 指定載體（招牌/燈籠）成功出「Hao0321」清楚可讀。適用 ~7 字內短店名；長句仍不可靠。Veo 3.1 同級亦較強。其他影片模型仍守鐵律。
- **要精準文字 → 圖像階段先做好**：Ideogram 3.0（文字王）/ Seedream（中英）/ MJ V8.1（改善但仍弱）。
- **影片 prompt 明寫 `no text, no logo, no captions`** 反而乾淨 —— 讓後製加字。

### 產品包裝字
- i2v：用 Ideogram/Seedream 把包裝字做對 → i2v 動畫化（字已在圖上，模型只需 hold 住，比生成準）
- 仍會輕微抖 → 運鏡避免正面大特寫掃過文字

### Negative（影片）
```
garbled text, distorted letters, gibberish writing, warped logo,
fake characters, unreadable text, morphing typography
```

---

## 5. 質感分級 (反「AI 感 / 塑膠感 / 廉價感」)

「說不上來哪裡爛，就是廉價」= 缺電影/廣告的**質感層**。

### 加質感的 token 層（挑 3-5 個）
- **攝影器材**：`Phase One IQ4 medium format, Hasselblad, ARRI Alexa, anamorphic lens`
- **底片/感光**（圖+部分影片）：`Kodak Vision3 500T, Cinestill 800T, fine grain`
- **光質**：`soft directional key light, single-source window light, Rembrandt lighting, volumetric god rays`（單一柔光 > 平光）
- **景深**：`shallow depth of field, creamy bokeh, f/1.4`（淺景深 = 高級感）
- **色彩分級**：`cinematic color grade, teal-and-orange, A24 muted palette, bleach bypass`
- **製作等級**：`AAA commercial production, luxury brand campaign, editorial photography`

### 反「塑膠感」negative
```
plastic look, CGI render, video game graphics, overly smooth, waxy,
artificial sheen, uncanny, cheap stock footage, oversaturated, flat lighting,
HDR overcook, AI-generated look
```

### 關鍵洞察
**單一柔和方向光 + 淺景深 + 簡潔背景 = 廣告高級感公式**。平光 + 深景深 + 雜亂背景 = 廉價感。光打對了，質感自動上來。

---

## 6. 運鏡控制 (Camera) — 飄移/硬切

### 修法
- **一鏡一運動**：`ONE camera motion per shot`。禁 `zoom while panning and tilting`。
- **給運鏡速度**：`slow dolly-in`、`gentle orbit`、`subtle push`。不寫速度 = 模型亂飄。
- **多鏡頭用 cinematic transition 詞**讓切換平滑（不要硬剪）：
  - `Smooth transition to` / `Match cut to` / `seamless transition` / `whip pan to` / `dissolve to`
- **鎖機位**：固定鏡頭明寫 `locked-off camera, static tripod shot`。

詳見 [camera-language.md](camera-language.md) + [editing-transitions.md](editing-transitions.md)。

---

## 7. 構圖 (Composition)

- **避免死板置中**（除非對稱美學）：`rule of thirds, dynamic composition, negative space on the left`
- **給明確景別**：`extreme close-up` / `medium shot` / `wide establishing`，別讓模型猜
- **前景層次**：`foreground bokeh elements, layered depth` 增加電影感
- **產品 hero**：`hero product shot, centered with breathing room, premium negative space`

---

## 8. 通用「廣告級」保底 negative（影片，12 句）

90% 產品/廣告影片直接套：
```
deformed product, morphing shape, distorted logo, garbled text, flickering,
texture boiling, plastic look, CGI render, jittery camera, oversaturated,
warped reflection, low quality
```

圖像（產品攝影）：
```
blurry, low quality, watermark, distracting background, fingerprints, dust,
warped text, bad reflection, plastic look, oversaturated, harsh flat lighting,
distorted product shape
```

---

## 9. 迭代策略 — 爛了怎麼救（不要瞎換 prompt）

1. **先判類別**（§0 表）→ 鎖定 1-2 個根因
2. **一次只改一個變數**：改主體描述 OR 改運鏡 OR 改 negative，別一次全改（無法歸因）
3. **產品類優先切 i2v**：t2v 三次還爛 → 換 i2v（先定死 hero 圖）。形狀問題 90% 靠這招解
4. **換模型而非硬調**：弱物理模型做複雜流體永遠爛 → 換 Runway Gen-4.5 / Veo 3.1
5. **升檔次**：Seedance fast → pro、Kling Std → Pro，瑕疵常常直接消失
6. **不要疊太多修正詞**：negative 列 30 個會稀釋訊號，挑最相關的 8-12 個

---

## 10. 平台「物理/穩定」強弱速查（2026-06）

| 平台 | 物理 | 時間穩定 | 主體一致 | 產品廣告適性 |
|---|---|---|---|---|
| Runway Gen-4.5 | ⭐ 頂級 | ⭐ | References 系統強 | ⭐ 首選複雜物理 |
| Veo 3.1 | ⭐ | ⭐ | 中 | 強（+ 原生音訊） |
| Seedance 2.0 pro | 強 | 強 | 中（i2v 補） | 強（OiiOii 易操作） |
| Kling 3.0 | 強 | 強 | Start Frame + Motion Brush 強 | ⭐ 局部運動控制最佳 |
| Sora 2 | 強 | 強 | Cameo | 🔴 平台已停運，勿用 |
| Vidu Q3 | 中 | 中 | Multi-ref 強 | 中（動漫強） |

**結論：複雜物理/流體 → Runway Gen-4.5 或 Veo 3.1；要精準局部運動（產品不動只動水花）→ Kling Motion Brush；要快速好操作 → OiiOii Seedance 2.0 pro + i2v 鎖形狀。**

---

## 連動

- 負面詞完整庫 → [negative-bank.md](../templates/negative-bank.md)
- 質感 token 層 → [cinematic-direction.md](cinematic-direction.md) / [commercial-direction.md](commercial-direction.md)
- 物理/大氣特效 → [vfx-effects.md](vfx-effects.md)
- 運鏡/轉場 → [camera-language.md](camera-language.md) / [editing-transitions.md](editing-transitions.md)
- 產品 i2v 鎖形狀流程 → [image-to-video-workflow.md](image-to-video-workflow.md)
