# Flux — Black Forest Labs

官網 `https://bfl.ai/`。2026 時點主力 **FLUX 1.1 Pro**、**FLUX.1 Kontext (Pro/Max/Dev)**、**Flux Schnell** (快速開源) / **Flux Dev** (開源進階) / **Flux Pro** (API 付費版)。**最強的自然語言 + 寫實 + 文字渲染** 影像模型之一。

## 核心模型

| 模型 | 特色 | 授權 |
|---|---|---|
| **Flux Schnell** | 快速蒸餾版 (4 步) | 開源 Apache 2.0 |
| **Flux Dev** | 中階品質、可 fine-tune | 開源非商用 |
| **Flux Pro** | 旗艦品質 API | 閉源商用 |
| **Flux 1.1 Pro** | Pro 的強化版 | API 商用 |
| **Flux 1.1 Pro [ultra]** | 4MP 原生 | API 商用 |
| **FLUX.1 Kontext [pro]** | **圖像編輯** 專用 (in-context) | API 商用 |
| **FLUX.1 Kontext [max]** | Kontext 旗艦 | API 商用 |
| **FLUX.1 Kontext [dev]** | 開源版 | 開源 |

## Prompt 風格

Flux **最愛自然語言完整句子**，不要 tag 式。**直接描述你想看到什麼，像在跟人講故事**。

```
A photograph of a young woman sitting at a vintage cafe, reading a leather-bound
book, with steam rising from her coffee cup. Soft morning light streams through
the window behind her, creating a warm backlit glow. Shot on a 50mm lens with
shallow depth of field, the background bokeh is gentle. The scene has a quiet,
contemplative atmosphere.
```

### 規則
- **使用完整句子**，描述如同攝影師解釋作品
- **細節優先具體** — 不是 `a woman`，是 `a woman in her 30s with chin-length auburn hair`
- **最多 512 tokens**，Kontext 上限相同
- **不要權重語法** `(word:1.3)` — Flux 不吃；想強調就用更具體的形容詞或重述

## 文字渲染 (Flux 1.1 Pro 與 Kontext 都強)

Flux 生成文字很準。規則：
- 用引號包要顯示的字：`with the text "BREAKFAST" written in bold sans-serif`
- 描述字型 + 位置：`a neon sign at the top of the image saying "OPEN"`
- 字少為宜 (< 10 字)
- 字體可指 `Helvetica`, `handwritten script`, `retro marquee letters`, `embossed metal`

## FLUX.1 Kontext — 圖像編輯殺手

Kontext 是 **in-context image generation + editing** — 你 **同時給它一張圖 + 文字指令**，它回傳編輯過的圖。用於：

- Change the X to Y
- Remove / add 物件
- 換背景、換光線、換風格
- 角色一致性 (同角色多姿勢)
- 換人 / 換衣 / 換髮型

### Kontext Prompt 最佳實踐 (官方)
1. **直接講要改什麼** — 不需重複描述圖裡已有的細節
2. **明確程度越高越好** (只要指令不過於複雜)
3. **保留未提及的元素** — Kontext 預設保留，寫「只改 X」會更穩
4. **連續編輯** — 可以把輸出丟回去再改一次，但累積失真

### Kontext 範例

**1. 加物件**
```
Add a pair of aviator sunglasses to the person.
```

**2. 換背景**
```
Change the background to a tropical beach at sunset, keep the subject and
lighting direction unchanged.
```

**3. Restyle**
```
Transform this photo into a Studio Ghibli animated film still, hand-painted
watercolor backgrounds, soft pastel palette, while keeping the subject's
face recognizable.
```

**4. 文字編輯**
```
Change the text on the coffee cup from "MONDAY" to "FRIDAY", same font and
color.
```

**5. 角色一致性 (同人不同場景)**
```
(Input: 某角色的參考圖) The same person, now standing in a snowy mountain
village at dusk, wearing a red winter coat, candid medium shot, soft
practical lighting.
```

## Flux 1.1 Pro 範例

**1. 寫實攝影**
```
A professional portrait of a Japanese elderly man with weathered skin, deep
wrinkles, and silver hair, wearing a traditional indigo-dyed kimono. He is
seated in a tatami room with soft natural light filtering through a rice
paper screen behind him. The image is shot with a medium-format camera,
85mm lens, shallow depth of field, rich tonal range. Muted earth tones,
soft shadows, photographic realism.
```

**2. 插畫 + 文字**
```
A minimalist flat illustration of a rocket launching from a green hill into
a starry sky. The sun is rising on the horizon in pastel pink and orange.
At the top of the image, in a clean geometric sans-serif font, the text
"LAUNCH DAY" is displayed in bold yellow. The overall style is modern
editorial illustration, limited palette, high contrast.
```

**3. 商品**
```
A luxury perfume bottle on a polished black marble surface. The bottle is
clear glass with golden accents and a minimalist label reading "NOIR". Soft
side lighting creates elegant reflections on the marble. Clean, editorial
fashion photography aesthetic, 50mm macro, high detail.
```

## 參數

- **Aspect / resolution**：API 可指 1024–4MP (ultra 支援 4MP 原生)
- **Steps**：Schnell 4 / Dev 30 / Pro API 自動
- **Guidance**：2–5 預設；高會僵
- **Seed**：可指定
- **Safety tolerance**：API 專用

## 平台差異

| 平台 | 型號可用 | 備註 |
|---|---|---|
| **BFL API** (`api.bfl.ml`) | 全系列 | 官方首選 |
| **fal.ai** | 幾乎全系列 | 快，文件好 |
| **Replicate** | 全系列 | Python/JS SDK 完備 |
| **Azure AI Foundry** | Pro + Kontext | 企業 |
| **Krea / Freepik / getimg** | Pro | 有 UI |
| **ComfyUI** | Schnell / Dev | 本地跑 |

## 常見錯誤

- **用 MJ 的 `--ar --s` 參數** → 無效。Flux 在 API 是欄位。
- **寫 tag 式 prompt** (`beautiful, cinematic, 8k, masterpiece`) → Flux 吃不到；會被當雜訊。寫句子。
- **`(word:1.3)` 權重** → 不吃。自然語言重述即可。
- **Kontext 講模糊指令** (`make it better`) → 它不知道你要什麼。具體講 (`increase contrast and saturate the reds`)。
- **一個 Kontext 指令要改 5 件事** → 品質下降。一次 1–2 件事。

## 連結

- BFL 官網：https://bfl.ai/
- FLUX.1 Kontext 介紹：https://bfl.ai/models/flux-kontext
- Kontext 官方 Prompt Guide (image-to-image)：https://docs.bfl.ml/guides/prompting_guide_kontext_i2i
- Hugging Face Kontext dev：https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev
- Replicate Kontext Pro：https://replicate.com/black-forest-labs/flux-kontext-pro
- Flux 1 Quickstart (Civitai Edu)：https://education.civitai.com/quickstart-guide-to-flux-1/
- Azure AI Foundry 整合公告：https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/black-forest-labs-flux-1-kontext-pro-and-flux1-1-pro-now-available-in-azure-ai-f/4434659
- Skywork Ultimate Guide：https://skywork.ai/blog/flux-prompting-ultimate-guide-flux1-dev-schnell/
- giz.ai FLUX.1 Prompt Guide：https://www.giz.ai/flux-1-prompt-guide/
- getimg.ai Pro Tips：https://getimg.ai/blog/flux-1-prompt-guide-pro-tips-and-common-mistakes-to-avoid
