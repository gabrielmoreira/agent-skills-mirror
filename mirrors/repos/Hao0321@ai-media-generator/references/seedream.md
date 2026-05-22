# Seedream — ByteDance 豆包圖像模型

官方入口：**即夢 (Jimeng) `jimeng.jianying.com`**、**豆包 (Doubao) `doubao.com`**、**Volcengine Ark / BytePlus ModelArk**、第三方 fal.ai、Replicate、Krea。主力版本 **Seedream 4.0 / 4.5 / 5.0**。

## 核心特色

- **4K 原生** — 解析度直上 2048×2048 / 4096×4096
- **最強文字渲染** — 中英雙語，海報 / 標題 / 信封 / 印章 / 招牌都穩
- **統一架構** — 同一模型兼顧生成 + 編輯 + 多圖一致性
- **推理速度** — 4.0 比 3.0 快數倍
- **中國文化元素** — 訓練資料豐富

## Prompt 公式

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

## 文字渲染 (Seedream 的殺手鐧)

### 規則
**要顯示的文字一定用雙引號包起來。**

- ✓ `Generate a poster with the title "Dream Theater" at top center.`
- ✗ `Generate a poster titled Dream Theater.`

### 最佳實踐
- **字數短**：1–10 個字最準。整段文字會分解。
- **位置明指**：`top center`, `bottom right`, `centered`, `diagonal across the image`
- **字型描述**：`bold sans-serif`, `elegant script`, `brush calligraphy`, `neon LED`, `embossed metallic`
- **高解析度**：2048x2048 以上，字才清晰
- **語言明指**：`in English`, `in Traditional Chinese`, `in Japanese kanji`

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

**3. 中文信封**
```
Traditional Chinese envelope design, beige rice paper texture. Vertical
address "北平市西城區" in black brush calligraphy, right side. Red stamp
reading "急" in top-left corner. Subtle ink splatter detail.
```

## 模式

| 模式 | 說明 |
|---|---|
| **T2I** | 純文字生圖 |
| **Image Editing** | 上傳圖 + 編輯指令 (local edit、換背景、換物件) |
| **Multi-Image Reference** | 多圖組合生成 (角色一致性) |
| **Upscale** | 放大到 4K |
| **Variation** | 微調變體 |

## 版本差異

| 版本 | 亮點 |
|---|---|
| Seedream 3.0 | 基礎，中英文字已強 |
| **Seedream 4.0** | 速度↑、4K、統一架構 |
| **Seedream 4.5** | 字體更精、排版更穩、aesthetic↑ |
| Seedream 5.0 | 下一代 (推出時間待確認)，提升複雜場景 + 故事性 |

## 編輯指令 (Image Editing)

用 **簡潔、明確、不含糊代名詞**。

- ✓ `change the sky to a dramatic sunset with pink and orange clouds`
- ✗ `make it more dramatic`
- ✓ `keep the person unchanged, replace the background with a beach at sunset`
- ✗ `change the background` (太模糊)

如果要保留某些元素 → 明確講：`keep the face, hair, and clothing unchanged`。

## 風格模板 (Seedream 原生好的風格)

- `ink wash painting, traditional Chinese aesthetics`
- `cel-shaded anime, Studio Ghibli style`
- `cinematic product photography, soft box lighting`
- `minimalist flat illustration`
- `oil painting, impressionist, Monet-inspired`
- `architectural concept render, Vray`
- `3D claymation`
- `pixel art, 16-bit era`
- `ukiyo-e woodblock print`
- `cyberpunk neon, Blade Runner`

## 參數

- 解析度：512 ~ 4096 (4.0 最大 4K)
- Aspect：任意 (1:1, 16:9, 9:16, 3:4, 4:3, 21:9)
- Negative prompt：支援
- Seed：可固定

## 平台差異

| 平台 | 特色 |
|---|---|
| **即夢 (Jimeng)** | 中文介面，UI 最好用，免費額度 |
| **豆包 (Doubao)** | 整合 chatbot，對話式生成 |
| **Volcengine Ark API** | 企業級，含完整文件 |
| **BytePlus ModelArk** | 國際版 API |
| **fal.ai / Replicate** | 第三方代理，付費快，整合 Python/JS SDK |
| **Krea** | 含 enhancer + real-time 預覽 |

## 負面 Prompt

```
blurry, low quality, watermark, logo, jpeg artifacts, distorted text,
garbled letters, extra limbs, deformed hands, plastic skin, oversaturated
```

## 範例彙整

**1. 寫實人像**
```
Portrait of a 30-year-old woman with shoulder-length auburn hair, freckles,
wearing a cream wool sweater. Natural window light from the left, warm tones.
Shallow depth of field, 85mm lens, Fujifilm Pro 400H film stock. High detail,
pores visible, no retouching. 2048x2048.
```

**2. 動畫角色**
```
Cel-shaded anime character design, teenage boy with spiky silver hair, blue
hoodie, neutral pose, front view. Studio Ghibli style, soft watercolor
background, hand-painted feel. Clean line art.
```

**3. 廣告構圖 + 文字**
```
Minimalist skincare ad, top-down flat lay. Glass bottle labeled "HYDRA
BLOOM" in thin elegant serif, centered. Surrounded by fresh peonies and
dewdrops on marble surface. Soft morning light, pastel palette, high-end
commercial photography. 2048x2048.
```

## 常見錯誤

- **要文字卻不加引號** — Seedream 會當描述，文字會混進場景元素
- **一張圖塞太多文字** — 超過 10 字、多段落會歪
- **Image Editing 用含糊代名詞** (`make it better`) — 沒用；要明確講改什麼
- **Seedream 4 寫 `(word:1.3)` 權重** — 不吃；自然語言即可

## 連結

- 官方 Seedream 4.0 頁面：https://seed.bytedance.com/en/seedream4_0
- 官方 Seedream 4.5 頁面：https://seed.bytedance.com/en/seedream4_5
- BytePlus Prompt Guide (官方)：https://docs.byteplus.com/en/docs/ModelArk/1829186
- WaveSpeedAI 4.5 完整指南：https://wavespeed.ai/blog/posts/seedream-4-5-complete-guide-2026/
- WaveSpeedAI 4→5 Tutorial：https://wavespeed.ai/blog/posts/seedream-4-0-to-5-0-complete-tutorial-image-generation-editing/
- fal.ai Seedream 4.5 Guide：https://fal.ai/learn/devs/seedream-v4-5-prompt-guide
- Atlabs Prompting Guide：https://www.atlabs.ai/blog/seedream-4o-prompting-guide
- Krea Seedream 4 Guide：https://www.krea.ai/articles/seedream-4-guide
- getimg.ai Full Guide：https://getimg.ai/blog/guide-to-bytedance-seedream-4-ai-image-model

---

## 🆕 Seedream 4.5 / 5.0 進階功能 (2026 更新)

### Seedream 4.5 核心升級 (全面 scaling)

- Prompt adherence ↑
- Alignment ↑
- Aesthetics ↑
- 主體識別 (multi-image editing 更準)
- **Typography + dense text rendering** ↑ (複雜版面更穩)

### Multi-Reference Editing (更正！最多 **14 張** 不是 7 張)

- Edit mode 上傳 **up to 14 reference images**
- Prompt 用 `the [entity] from ref N` 指涉
- Strictly preserve details (嚴格保留 ref 細節)
- **用例：** 複雜商品海報 (model + 產品 + 背景 + 配件 + logo + 字型範本 + 色票 + ...)

### 3 種輸入模式

1. **Text only** → text-to-image
2. **Single image + text** → image editing
3. **Multiple images + text** → multi-image fusion / sequential batch

### Sequential Batch Generation (Image Series Mode)

- 一次 prompt 生多張**主題一致**系列圖
- 適合：繪本分鏡 / 系列廣告 / 品牌視覺包
- Theme consistency 自動維持 (不用 prompt 重複描述錨)

### Seedream 5.0 (2026-02 發布，Lite 版)

- **Chain-of-Thought reasoning** 整合 (推理更強)
- **Live web search** 內建 (可 search 參考最新視覺)
- **Multi-modal reference understanding** 統一架構
- 最適合：需要「懂世界」的複雜 prompt (如「做一個 2026 奧斯卡海報的仿品」)

### Prompt 原則升級 (vs 4.0)

**以前：** 疊很多 ornate vocabulary 容易亂
**現在 4.5 / 5.0：** **簡潔 + 精確** 好過堆砌
> "使用 concise 和 precise prompts 通常比 repeatedly stacking 華麗詞彙更好"

### 進階工作流：13 元素商品海報

```
Ref 1: 主 model 肖像
Ref 2: 產品包裝
Ref 3: 品牌 logo
Ref 4-5: 色票 reference 圖
Ref 6: 背景場景
Ref 7-8: 配件 (耳環 / 手錶)
Ref 9: 字型 reference
Ref 10-14: 其他視覺元素

Prompt: "Create a luxury fashion campaign poster. Main model 
from ref 1 wearing the product from ref 2, brand logo in 
top right as in ref 3. Color palette from refs 4-5. Setting 
from ref 6 (with bokeh). Accessories from refs 7-8 visible. 
Headline '秋冬 2026' in the typography style of ref 9, 
positioned bottom center."
```

Seedream 4.5 能把所有 14 個 refs 融合進一張圖。

### 新連結

- [Seedream 4.5 官方](https://seed.bytedance.com/en/seedream4_5)
- [4.0-5.0 Complete Tutorial](https://wavespeed.ai/blog/posts/seedream-4-0-to-5-0-complete-tutorial-image-generation-editing/)
- [5.0 Lite Guide](https://scholarviz.com/blog/seedream-5-0-lite-complete-model-guide)
- [Seedream 4.5 Prompt Tests](https://docs.mew.design/blog/seedream-4-5-test/)
- [Seedream Best Practices 2026](https://evolink.ai/blog/seedream-prompt-guide-best-practices-2026)
