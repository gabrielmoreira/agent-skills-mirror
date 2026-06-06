# Seedream — ByteDance 豆包 / 字節跳動 圖像模型

官方入口：**即夢 (Jimeng) `jimeng.jianying.com`**、**豆包 (Doubao) `doubao.com`**、**Volcengine Ark / BytePlus ModelArk** (官方 API)；第三方 **fal.ai / Replicate / Krea / WaveSpeedAI**。主力版本 **Seedream 4.0 / 4.5 / 5.0 Lite**。

**一句話定位：** 市場最強「中英文字渲染 + 生成/編輯統一架構 + 4K 原生 + 多圖參考」的圖像模型。要中文海報、要精準排版、要多圖一致性 → 預設選 Seedream。

---

## 0. 版本能力矩陣 (2026-06)

| 能力 | 3.0 | **4.0** | **4.5** | **5.0 Lite** |
|---|---|---|---|---|
| 最大解析度 | 2K | **4K (4096)** | **4K** | **4K (~3s 出圖)** |
| 推理速度 | 基準 | **比 3.0 快 10×+** | 比 4.0 再快 30–40% | 同級快 |
| 文字渲染 (中英) | 已強 | 強 | **更精 + dense text 版面穩** | **雙語再強** |
| 生成 + 編輯統一架構 | 部分 | ✅ | ✅ | ✅ (native edit) |
| 多圖參考上限 | 少 | 多圖 + batch | **up to 14 refs** | **up to 14 refs** |
| Sequential / batch 系列圖 | ✗ | ✅ batch | ✅ 主題一致系列 | ✅ |
| Chain-of-Thought 視覺推理 | ✗ | ✗ | ✗ | **✅ (新)** |
| 內建 live web search | ✗ | ✗ | ✗ | **✅ (新)** |
| 約略單張價 (官方/第三方) | — | ~$0.03–0.04 | **~$0.035–0.04** | **~$0.035 (比 4.5 省 ~22%)** |

**選版建議：**
- **要排版/品牌字/人像編輯** → **4.5**（官方推薦的 typography / branded / portrait edit 首選）。
- **要「懂世界」的複雜 prompt**（仿某風格海報、需引用真實視覺、語意推理）→ **5.0 Lite**（CoT + web search）。
- **純大量出圖、成本敏感** → 4.0 / 5.0 Lite（速度與單價最佳）。
- 5.0 目前為 **Lite** 版（2026-02 發布）；完整 5.0 推出時點 **(待驗證)**。

---

## 1. 核心特色

- **4K 原生** — 直上 2048×2048 / 4096×4096，文字在高解析下才清晰。
- **最強文字渲染** — 中英雙語，海報 / 標題 / 信封 / 印章 / 招牌 / 包裝標籤都穩。
- **統一架構** — 同一模型兼顧 T2I 生成 + 圖像編輯 + 多圖一致性，免切換系統。
- **推理速度** — 4.0 經蒸餾加速，DiT 比 3.0 快 **10 倍以上**。
- **中國文化元素** — 訓練資料豐富（水墨、漢服、書法、節慶、中式建築）。
- **Seedream → Seedance 影片管線** — 用 Seedream 出圖，再用 **Seedance** 動起來（字節同門影片模型，一條龍：text → image → moving scene）。**(待驗證 UI 串接細節)**

---

## 2. Prompt 公式

```
[主體 + 具體細節] + [風格/媒材] + [構圖] + [光影] + [細節加強]
```

```
A young woman in a hanfu dress holding a folding fan (subject)
ink wash painting style, traditional Chinese aesthetics (style/medium)
centered composition, pale silk background (composition)
soft diffused light, morning mist (lighting)
delicate brush strokes, visible paper texture, 2048x2048 (detail)
```

**4.5 / 5.0 黃金原則（vs 4.0）：** **concise + precise 勝過堆砌華麗詞彙。**
> 以前疊一堆 ornate vocabulary 容易亂；4.5 起 prompt adherence 大幅提升，簡潔精確的指令反而更聽話。先寫清楚「主體 + 動作 + 關鍵 3–4 個視覺錨」，再加風格，不要前面塞 20 個形容詞。

---

## 3. 進階技巧 A — 文字渲染 (Seedream 的殺手鐧)

### 唯一硬規則
**要顯示的文字一定用雙引號包起來。**
- ✓ `Generate a poster with the title "Dream Theater" at top center.`
- ✗ `Generate a poster titled Dream Theater.` ← 會被當描述，文字混進場景。

### 最佳實踐
- **字數短**：1–10 個字最準。整段長文字會被拆解、出錯。要長文 → 拆成標題 / 副標 / 註腳多個短引號串。
- **位置明指**：`top center`, `bottom right`, `centered`, `diagonal banner across the image`, `right vertical column`。
- **字型描述**：`bold sans-serif`, `elegant script`, `brush calligraphy`, `neon LED`, `embossed metallic`, `thin serif`。
- **語言明指**：`in English`, `in Traditional Chinese`, `in Simplified Chinese`, `in Japanese kanji`。
- **高解析度**：2048×2048 以上，小字才不糊。
- **4.5 專屬：dense text** — 多段落 / 表格 / 菜單式密集排版比 4.0 更穩，但仍建議每塊文字獨立引號 + 標位置。

### 範例

**1. 雙語海報**
```
Movie poster, centered vertical composition. Title "時光迴廊" in elegant
brush calligraphy, top center. Subtitle "Corridor of Time" in thin
sans-serif, bottom center. A lone figure walks through an ancient Chinese
archway at sunset, ink wash aesthetic with a cinematic color grade. 2048x2048.
```

**2. 產品標籤**
```
Minimalist coffee bag design, white background. Logo "MOONBREW" in bold
sans-serif, top center. Subtext "Single Origin · Ethiopia · 250g" in small
thin letters, bottom center. Illustration of a crescent moon above the logo.
High contrast, premium packaging photography.
```

**3. 中文信封 / 印章**
```
Traditional Chinese envelope design, beige rice paper texture. Vertical
address "北平市西城區" in black brush calligraphy, right side. Red square
seal stamp reading "急" in top-left corner. Subtle ink splatter detail.
```

---

## 4. 進階技巧 B — 多圖參考 (up to 14 refs)

Edit / multi-image 模式可上傳 **最多 14 張參考圖**，Seedream 融合進一張輸出。

- **指涉語法**：`the [entity] from ref N`（例：`the model from ref 1`, `the logo from ref 3`）。
- **嚴格保留**：要 ref 細節不變 → `strictly preserve the details of the product from ref 2`。
- **用例**：複雜商品海報（model + 產品 + 背景 + 配件 + logo + 色票 + 字型範本…）、角色跨圖一致性、把多素材合成單張視覺。

### 三種輸入模式
1. **Text only** → text-to-image。
2. **Single image + text** → image editing。
3. **Multiple images + text** → multi-image fusion / sequential batch。

### Sequential Batch / 系列圖模式
- 一次 prompt 生多張**主題一致**系列圖（繪本分鏡 / 系列廣告 / 品牌視覺包）。
- Theme consistency 自動維持，**不必每張重述視覺錨**。
- ⚡ 若需求是「同風格 N 張」，**用系列/batch 一次出**，比 N 次獨立生成省時且更一致（見 site-profile chain SOP）。

---

## 5. 進階技巧 C — 圖像編輯指令 (Image Editing)

用 **簡潔、明確、不含糊代名詞** 的指令。支援 **新增 / 刪除 / 替換 / 修改**。

- ✓ `change the sky to a dramatic sunset with pink and orange clouds`
- ✗ `make it more dramatic`（沒用，太模糊）
- ✓ `keep the person unchanged, replace the background with a beach at sunset`
- ✗ `change the background`（沒指明改成什麼）

**保留元素就明講**：`keep the face, hair, and clothing unchanged`。

**進階：視覺標記引導 (visual cues)** — 在輸入圖上畫 **箭頭 / bounding box / 塗鴉** 標出要編輯的區域，Seedream 4.5 會據此定位編輯目標，比純文字描述位置更準。適合「只改這一塊」的精修。

**鏈式編輯 (chained edit)**：T2I 出底圖 → edit 端點做定點修改 → 再 edit 微調，逐步逼近，每步只改一件事，可控度最高。

---

## 6. 進階技巧 D — 4K 與輸出控制

- 解析度：512 ~ 4096（4.0 起支援 4K；5.0 Lite ~3s 出 4K）。
- Aspect：任意（1:1, 16:9, 9:16, 3:4, 4:3, 21:9）。
- **小字 / 細節密集** → 直接生 2048+ 或 4K，不要先小圖再放大（原生高解析的文字邊緣更乾淨）。
- Negative prompt：支援；Seed：可固定（系列圖鎖 seed 維持一致）。
- ⚠️ **4.0+ 不吃 `(word:1.3)` 權重語法** — 自然語言描述即可，寫權重無效。

---

## 7. 進階功能地圖

| 功能 | 說明 | 適用版本 |
|---|---|---|
| **T2I** | 純文字生圖 | 全版本 |
| **Image Editing** | 上傳圖 + 指令（local edit / 換背景 / 換物件 / 增刪改）| 4.0+ |
| **Multi-Image Reference (≤14)** | 多圖融合 / 角色一致性 | 4.0+（4.5/5.0 最穩）|
| **Sequential Batch / 系列圖** | 一次出多張主題一致 | 4.0+ |
| **Visual-cue Editing** | 箭頭/框/塗鴉指定編輯區 | 4.5+ |
| **Chain-of-Thought 推理** | 語意推理理解複雜 prompt | **5.0 Lite** |
| **Live Web Search** | 內建檢索參考最新視覺 | **5.0 Lite** |
| **Seedream → Seedance 影片** | 出圖後一鍵動畫化 | 影片走 Seedance |
| **Upscale / Variation** | 放大到 4K / 微調變體 | 平台側功能 |

---

## 8. 進階 Recipe

### Recipe 1 — 品牌海報含精準中文字 (4.5)
```
Premium tea brand poster, vertical 9:16. Background: misty mountain tea
terraces at dawn, soft ink-wash gradient. Brand name "雲頂茶事" in elegant
black brush calligraphy, top center, large. Tagline "高山·手採·春摘" in thin
modern sans-serif, directly below, smaller. Bottom strip: a single tea leaf
icon centered. Muted green and cream palette, refined negative space,
high-end commercial photography. 4K.
```
要點：標題與副標各自雙引號 + 各自標位置 + 各自字型；版面留白；4K 讓書法邊緣清晰。

### Recipe 2 — 產品多角度 / 多圖合成商品海報 (≤14 refs)
```
Ref 1: model portrait   Ref 2: product packaging   Ref 3: brand logo
Ref 4–5: color swatch references   Ref 6: background scene
Ref 7–8: accessories (earrings / watch)   Ref 9: typography sample

Prompt: "Create a luxury fashion campaign poster. The model from ref 1
wearing the product from ref 2; brand logo from ref 3 in the top-right.
Color palette strictly from refs 4–5. Setting from ref 6 with soft bokeh.
Accessories from refs 7–8 visible. Headline '秋冬 2026' in the typography
style of ref 9, positioned bottom center. Strictly preserve product and
logo details. 4K."
```
要點：每元素用 `from ref N` 點名；色票/logo 用 `strictly preserve`；文字仍走雙引號規則。

### Recipe 3 — 同主題系列廣告 (Sequential Batch)
```
Generate a 4-image series of the same minimalist sneaker on a pastel
podium, consistent product and lighting across all frames. Frame 1: front
view. Frame 2: 3/4 side view. Frame 3: top-down. Frame 4: close-up of the
sole texture. Soft studio lighting, seamless gradient background, premium
e-commerce product photography. 4K.
```
要點：明列每張差異（角度），共用主體/光線靠 batch 自動維持，不必每張重寫風格。

---

## 9. 風格模板 (Seedream 原生好的風格)

- `ink wash painting, traditional Chinese aesthetics`
- `cel-shaded anime, hand-painted watercolor background`
- `cinematic product photography, soft box lighting`
- `minimalist flat illustration`
- `oil painting, impressionist, loose brushwork`
- `architectural concept render, physically based`
- `3D claymation`
- `pixel art, 16-bit era`
- `ukiyo-e woodblock print`
- `cyberpunk neon, rain-soaked street`

> 風格詞可保留具名美術流派（impressionist / ukiyo-e），但**避免具名在世藝術家或商標 IP**（侵權與攔截風險）。

---

## 10. 負面 Prompt

```
blurry, low quality, watermark, logo, jpeg artifacts, distorted text,
garbled letters, misspelled text, extra limbs, deformed hands, plastic skin,
oversaturated, overexposed
```

---

## 11. 範例彙整 (T2I 基礎)

**1. 寫實人像**
```
Portrait of a 30-year-old woman with shoulder-length auburn hair, freckles,
wearing a cream wool sweater. Natural window light from the left, warm tones.
Shallow depth of field, 85mm lens, fine film grain. High detail, pores
visible, no retouching. 2048x2048.
```

**2. 動畫角色**
```
Cel-shaded anime character design, teenage boy with spiky silver hair, blue
hoodie, neutral pose, front view. Soft watercolor background, hand-painted
feel. Clean line art.
```

**3. 廣告構圖 + 文字**
```
Minimalist skincare ad, top-down flat lay. Glass bottle labeled "HYDRA
BLOOM" in thin elegant serif, centered. Surrounded by fresh peonies and
dewdrops on a marble surface. Soft morning light, pastel palette, high-end
commercial photography. 2048x2048.
```

---

## 12. 常見失敗 + 修法

| 症狀 | 原因 | 修法 |
|---|---|---|
| 想要的字變成場景元素 | 文字沒加雙引號 | 所有要顯示的字一律 `"..."` |
| 文字歪斜 / 拼錯 / 缺字 | 一張塞太多字、解析度太低 | 字數壓 1–10、拆多個短引號、生 2048+/4K |
| Image Editing 無反應 | 含糊指令 (`make it better`) | 明確講改什麼、改成什麼；保留項明列 |
| 編輯改錯地方 | 沒指定區域 | 在圖上畫箭頭/框 (visual cue) 或文字標位置 |
| 多圖參考亂融合 | 沒點名 ref / 沒鎖細節 | 用 `the X from ref N` + `strictly preserve` |
| 寫了 `(word:1.3)` 沒效果 | 4.0+ 不吃權重語法 | 改自然語言；重要元素往句首放、講具體 |
| 堆一堆形容詞反而亂 | 4.5/5.0 ornate stacking | 改 concise + precise，先錨主體再加風格 |
| 系列圖風格不一致 | 逐張獨立生成 | 改用 sequential batch / 系列模式 + 鎖 seed |
| 出現商標/IP 被攔或扭曲 | prompt 寫具名品牌/IP | 改描述特徵，不寫品牌名（見 §9 註） |

---

## 連結

### 官方
- Seedream 4.0：https://seed.bytedance.com/en/seedream4_0
- Seedream 4.5：https://seed.bytedance.com/en/seedream4_5
- Seedream 5.0 Lite：https://seed.bytedance.com/en/seedream5_0_lite
- Seedream 4.0 發布公告：https://seed.bytedance.com/en/blog/seedream-4-0-officially-released-beyond-drawing-into-imagination
- BytePlus / ModelArk 官方 Prompt Guide (4.0–4.5)：https://docs.byteplus.com/en/docs/ModelArk/1829186

### Prompt / 教學指南
- fal.ai Seedream v4.5 Prompt Guide：https://fal.ai/learn/devs/seedream-v4-5-prompt-guide
- WaveSpeedAI 4.5 完整指南：https://wavespeed.ai/blog/posts/seedream-4-5-complete-guide-2026/
- WaveSpeedAI 4.0→5.0 Complete Tutorial：https://wavespeed.ai/blog/posts/seedream-4-0-to-5-0-complete-tutorial-image-generation-editing/
- magichour 4.0 Reference/Editing Guide：https://magichour.ai/blog/seedream-edit-guide
- Seedream Best Practices 2026：https://evolink.ai/blog/seedream-prompt-guide-best-practices-2026
- 5.0 Lite Guide (scholarviz)：https://scholarviz.com/blog/seedream-5-0-lite-complete-model-guide

### 價格
- Seedream Pricing Guide 2026 (evolink)：https://evolink.ai/blog/seedream-pricing-guide-2026
- Seedream Pricing Guide (ImagineArt)：https://www.imagine.art/blogs/seedream-pricing-guide
- Price Per Token — Seedream 4.5：https://pricepertoken.com/image/model/bytedance-seedream-4-5
