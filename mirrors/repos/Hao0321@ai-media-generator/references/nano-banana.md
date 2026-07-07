# Nano Banana — Google Gemini Flash Image 家族

**定位：** Google 的原生多模態圖像生成/編輯模型，**「Nano Banana」是代號**。2026 時點主要版本：
- **Nano Banana** = Gemini 2.5 Flash Image (2025-08 發布)
- **Nano Banana 2** = Gemini 3.1 Flash Image (2026-02-26 發布)
- **Nano Banana Pro** = Gemini 3 Pro Image (旗艦)

**為什麼值得一個獨立 reference：** 它在 **文字渲染** 和 **角色一致性 (最多 5 人不用 fine-tune)** 這兩項目前領先市場，並且是 Flow 官方 UI、Gemini App、Google Search、Vertex AI 裡可直接呼叫的唯一 Google 原生圖像模型。

---

## 核心特色

- **角色一致性** — 一個 prompt 內最多 5 個角色在不同 generation 保持一致 (**儲存格敘事、storyboarding 神器**)
- **文字渲染** — Pro 版本目前業界最準：短標、長段、多語混排都能 legible
- **多圖融合 (blend)** — 合併多張參考圖
- **自然語言編輯** — 「模糊背景」「移除物件」「換姿勢」「黑白上色」…直接用中/英文指令
- **整合 Gemini 世界知識** — 不只是貼圖生成，懂「這個物件在什麼情境會是什麼樣子」
- **低延遲** — 比 Imagen 快很多，對話式編輯流暢

---

## 平台入口

| 平台 | URL | 用途 |
|---|---|---|
| **Gemini App** | `https://gemini.google.com/` | 對話中生圖/編輯 |
| **Google Search AI Mode** | 搜尋列 | 搜尋式觸發 |
| **Google Lens** | 手機 app | 圖像分析 + 衍生 |
| **Flow** | `https://labs.google/fx/tools/flow` | 切到「圖片」模式 (搭配 Veo 3.1 生影片) |
| **Google AI Studio** | `https://aistudio.google.com/` | 開發者測試 |
| **Vertex AI** | Google Cloud Console | 企業 API |
| **fal.ai / Replicate** | 第三方 | 代理 API (可能有 latency 差) |

---

## 定價 (Gemini 2.5 Flash Image，2026 起參考)

- Input + output tokens billed separately
- **每張圖 = 1,290 output tokens**
- Output pricing: **$30 / 1M tokens**
- **每張圖約 $0.039 美金** (比 Midjourney 便宜，比 Flux Schnell 貴)

Nano Banana 2 / Pro 的具體定價見 Google AI docs，隨版本調整。

---

## Prompt 公式 (官方推薦)

**結構化 brief，按重要性由高到低排序：**

```
[Subject] + [Action / relationships] + [Setting] + [Style / medium] +
[Composition / camera]
```

### 5 個核心元素

| 元素 | 說明 | 範例 |
|---|---|---|
| **Subject** | 誰/什麼，**具體** | `a stoic robot barista with glowing blue optics` |
| **Action & relationships** | 在做什麼，與誰/物件互動 | `carefully pouring espresso into a glass mug` |
| **Setting** | 地點、時間、天氣 | `in a cozy rain-streaked cafe at dusk` |
| **Style & medium** | 攝影/插畫/3D/油畫 | `studio photography, soft box lighting` |
| **Composition / camera** | 構圖、焦段、景深 | `close-up 85mm shallow DoF, eye-level` |

### Prompt 寫法要點

1. **從最重要到最不重要排序** — 前面 tokens 權重高
2. **具體 > 模糊** — "a fluffy calico cat wearing a tiny wizard hat" > "a cat"
3. **生成 vs 編輯是不同 mindset：**
   - 生成：描述所有元素
   - 編輯：只寫 **what is changing + what is staying** (以圖為底)

---

## 文字渲染 (Nano Banana 強項)

### 規則

- **要顯示的文字用引號包：** `a poster with the headline "MIDNIGHT DRIVE" in bold retro letters`
- **字體描述詞**：
  - `bold sans-serif`, `elegant serif`, `handwritten script`, `chrome 3D letters`, `neon glow tube`, `embossed metallic`, `pixelated 8-bit font`
- **位置描述**：`top center`, `bottom left`, `wrapping around a circle`, `diagonal banner`
- **多行 / 多語混排 (Pro 版強)**：Nano Banana Pro 可同時準確渲染英+中/日，短標+長段混合

### 範例

```
A vintage film poster, vertical format. Main title "LUNA VIDE" in huge
retro neon tube letters at top center, saturated magenta glow. Subtitle
"A Film by Yuki Tanaka" in small white elegant serif below. A silhouette
of a motorcycle rider against a deep purple twilight sky. Grain texture,
1980s aesthetic.
```

---

## 角色一致性 (5 人以內)

### 為什麼重要

傳統 AI 模型每次生成都是獨立 — 同一個角色在第 2 張圖就變臉。Nano Banana Pro 解了這個：**同一段對話中可保持最多 5 個角色的視覺一致性**。適用：
- 繪本敘事 (同一角色多場景)
- 社群 campaign (同一角色多姿勢)
- 分鏡故事板 (角色跨鏡頭一致)

### 實作方式

**方式 A — 純文字描述 (ad-hoc)：**

在 prompt 內為每個角色定義具體視覺錨 (髮色、眼睛、服裝、記號)，之後所有 prompt 重複這些描述：

```
PROMPT 1:
The main character Aya — a 25-year-old Japanese woman with chin-length
black hair, a small mole under her left eye, wearing a mustard yellow
trench coat over a cream blouse — stands at a Tokyo subway platform at
night, waiting.

PROMPT 2 (同一對話中):
Aya (same character as before) now sits at a small ramen shop counter,
same outfit, warm interior light, close-up shallow DoF.
```

**方式 B — 上傳參考圖 (最強)：**

在 Gemini App 或 Flow 裡上傳角色的 main portrait，然後後續 prompt 引用 "the person in the reference"。Nano Banana Pro 會在 **5 人以內** 保持一致。

### Storyboard 工作流範例

1. 先產 5 張角色定妝照 (每個角色一張 main reference)
2. 把 5 張同時 blend 進一個 prompt：「In this scene, characters A and C stand in a park while B watches from behind a tree...」
3. 系列鏡頭維持一致性

---

## 自然語言編輯 (Nano Banana 殺手級功能)

傳統圖像模型只能重生成；Nano Banana 可以 **對一張既有圖做局部/全局編輯**，指令用自然語言。

### 編輯指令範例

| 任務 | 自然語言 prompt |
|---|---|
| 換背景 | `change the background to a tropical beach at sunset, keep the subject unchanged` |
| 移除物件 | `remove the telephone pole behind the person` |
| 換姿勢 | `keep the same person and outfit, change the pose to seated with legs crossed` |
| 加物件 | `add a pair of round wire-frame glasses on her face` |
| 改天氣 | `make it raining heavily, keep everything else the same` |
| 黑白上色 | `colorize this black and white photo with natural skin tones and warm ambient light` |
| 風格轉換 | `convert to Studio Ghibli animation style, keep composition and subject identical` |
| 文字修改 | `change the text on the sign from "OPEN" to "CLOSED", same font and color` |

### 編輯 mindset

**核心：講清楚「改什麼 + 保留什麼」**

```
❌ 不明確：
"make it better"
"change the look"

✅ 明確：
"keep the subject's face, hair, and clothing unchanged. Change only the
background from a plain studio to a sunlit meadow with wildflowers."
```

---

## 多圖融合 (Blend)

餵多張參考圖，讓 Nano Banana 把元素合成進一張：

```
Reference image 1: A person's portrait.
Reference image 2: A vintage leather jacket.
Reference image 3: A rainy Tokyo street photograph.

Task: Create an image where the person from reference 1 is wearing the
jacket from reference 2, walking through the scene from reference 3.
Same lighting tone as reference 3.
```

這比 Midjourney 的 `--oref` 更靈活 — 不只是「套一個角色」，是「從多張圖取不同元素 blend」。

---

## 與競品速查

| 能力 | Nano Banana Pro | Seedream 4.5/5 | Flux 1.1 Pro | Midjourney v7 |
|---|---|---|---|---|
| 文字渲染 | ⭐⭐⭐⭐⭐ 業界第一 | ⭐⭐⭐⭐⭐ 中英文雙強 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 角色一致性 | ⭐⭐⭐⭐⭐ (5 人) | ⭐⭐⭐ 需要 reference | ⭐⭐⭐ Kontext | ⭐⭐⭐⭐ --oref |
| 自然語言編輯 | ⭐⭐⭐⭐⭐ 對話式 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ Kontext | ⭐⭐ |
| 寫實攝影 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ 最寫實 | ⭐⭐⭐⭐ |
| 藝術插畫 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ 美感最高 |
| 中文文化 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ 中式最強 | ⭐⭐ | ⭐⭐⭐ |
| 多圖融合 | ⭐⭐⭐⭐⭐ 原生 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ Kontext | ⭐⭐⭐ |
| 定價 | $0.039/image | 中低 | 中 | 訂閱 $10+/月 |
| 商業授權 | ✓ Google 授權 | ✓ | ✓ Pro | ✓ Basic+ |

**什麼時候選 Nano Banana：**
- 做 **海報/貼文/文字為主的設計**，要英文 legibility
- **角色一致性** 的 storyboarding 或敘事 campaign
- 要 **對話式編輯** (Gemini App 自然流)
- 要 Google 生態整合 (Flow → Veo 3.1 i2v，搭配 Gemini 上下文)

**什麼時候選別的：**
- 中文藝術 → Seedream
- 極限寫實 → Flux 1.1 Pro
- 美感藝術插畫 → Midjourney v7
- 本地/開源 → SDXL / Flux Dev / Flux Schnell

---

## 完整範例

### 1. 海報 (文字渲染強項)

```
A minimalist movie poster, vertical 2:3 aspect. Main title "NEON HARBOR"
in large chrome 3D letters at top center, subtle pink-cyan glow edge.
Subtitle "A Film by Alex Chen" in thin white serif below. A silhouette
of a ship against a magenta-to-purple gradient sky, distant city lights.
Clean composition, grain texture, late 1980s Drive aesthetic.
```

### 2. 角色一致性 (多張 storyboard)

```
Scene 1: Hana (25, short black hair, green cardigan over white blouse,
round wire glasses) reads at a window seat in a cafe, morning light.

Scene 2: Hana (same person, same outfit) looks up as a stray cat jumps
onto the windowsill outside.

Scene 3: Hana smiles and slowly opens the window, reaches out.

All three scenes in the same illustrated style, warm color palette,
Studio Ghibli inspired, consistent character appearance.
```

### 3. 編輯 (既有圖 + 指令)

```
[Input image: a photo of a man in a blue shirt standing in an office]

Prompt: Keep the man, his shirt, and his pose identical. Change only the
background to a tropical beach at golden hour, with soft bokeh palm
trees. Adjust his shirt lighting to match warm sunset tones, but don't
change the shirt color itself.
```

### 4. 多圖 blend

```
Reference 1: [A person's headshot]
Reference 2: [A vintage motorcycle]
Reference 3: [A desert highway at sunset]

Create: The person from ref 1 riding the motorcycle from ref 2 down the
highway in ref 3. Maintain the person's face exactly. Warm golden hour
lighting matching ref 3. Dynamic low-angle tracking shot composition.
```

---

## 中文支援

- **視覺理解中文場景：** 良好 (廟宇、漢服、毛筆書法、節慶元素)
- **中文字渲染：** 英文 > Nano Banana Pro > Seedream 5 (2026-04 印象，Seedream 對繁中書法偏好度仍有優勢)。Pro 版中文可用但複雜字體 (明體/隸書等) 仍偶有錯字
- **中文 prompt：** Nano Banana 原生支援中文 prompt (Gemini 本來就多語)；但習慣寫英文 prompt 的使用者可留 prompt 英文，文字內容(要顯示的字) 用中文引號包

---

## 常見錯誤

- **Prompt 太抽象** (`a cool scene`) → 輸出 generic。務必具體
- **要顯示的字不加引號** → 字變成場景元素 (變招牌圖)
- **編輯模式寫得像生成** — 忘記講「保留什麼」，結果 AI 重畫整張
- **角色一致性超過 5 人** — 模型上限，6+ 人會開始跑掉
- **塞太多元素進一張** — 5 個以上主要元素會相互干擾；盡量一圖一主題

---

## Flow 裡的 Nano Banana (2026-04 觀察)

在 [Flow](../automation/site-profiles/flow.md) 編輯器的模型選擇面板：
- 內容類型切 **「圖片」** (預設是「視頻」)
- 下拉會顯示可用的 image 模型，包含 **Nano Banana / Nano Banana Pro** 變體
- 生成完的圖可作為 Veo 3.1 的 **首幀 (I2V)** — 這是 Google 生態最強的 image-to-video 工作流

實測待補 (下次操作 Flow image mode 時更新此檔和 site-profile)。

---

## 連結

- 官方 DeepMind Prompt Guide：https://deepmind.google/models/gemini-image/prompt-guide/
- Google Cloud Ultimate Prompting Guide：https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana
- Google Developers Blog 發布公告：https://developers.googleblog.com/en/introducing-gemini-2-5-flash-image/
- Google AI 官方文檔：https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash-image
- Vertex AI 整合：https://cloud.google.com/blog/products/ai-machine-learning/gemini-2-5-flash-image-on-vertex-ai
- Nano Banana Pro (Gemini 3 Pro Image) 發布：https://blog.google/innovation-and-ai/products/nano-banana-pro/
- Nano Banana Pro Tips (Google Blog)：https://blog.google/products/gemini/prompting-tips-nano-banana-pro/
- Leonardo.Ai Prompt Guide：https://leonardo.ai/news/nano-banana-prompt-guide/
- 75 Prompts + Pro Guide (ImagineArt)：https://www.imagine.art/blogs/nano-banana-pro-prompt-guide
- Travis Nicholson Style List (Medium)：https://travisnicholson.medium.com/complete-list-of-prompts-styles-for-nano-banana-ai-images-ee2229f1c48c
- Nano Banana vs Seedream vs Flux 2 (WaveSpeedAI)：https://wavespeed.ai/blog/posts/seedream-5-0-vs-nano-banana-pro-gpt-image-flux-klein-qwen-image-comparison-2026/
