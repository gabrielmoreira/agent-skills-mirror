# Stable Diffusion 3.5 / SDXL / ComfyUI 生態

Stability AI `https://stability.ai/`。開源家族主要版本：
- **SDXL** (1.0 / Turbo) — 成熟，生態最大
- **SD 3 / 3.5** — 新架構，prompt 理解強 (官方)
- **SD 4** (若已推出)

主要用法：本地 / Web UI (A1111, ComfyUI, Forge)、雲端代理 (fal.ai, Replicate, RunDiffusion)、Stability API。

## SDXL vs SD 3.5 — Prompt 寫法的關鍵差異

| 項目 | SDXL | SD 3.5 |
|---|---|---|
| Prompt 風格 | Tag 堆疊 | **自然語言** |
| 權重語法 `(word:1.3)` | ✓ 支援 | ✗ **不支援** |
| `[[word]]` `(((word)))` | ✓ 部分 | ✗ |
| Negative prompt | 重要 | 仍有用但輕 |
| Tokens | 75 tokens | 更長 (T5 encoder) |

## SDXL Prompt 寫法

Tag 堆疊 + 權重。常見用 A1111 / Forge 使用者。

**結構：**
```
[主體], [細節 tags], [style tags], [quality tags], [camera/lens tags]
Negative prompt: [瑕疵 tags], [不想要的 style tags]
```

**範例：**
```
masterpiece, best quality, 1girl, long black hair, red kimono, cherry blossoms,
(standing on wooden bridge:1.2), soft natural light, shallow depth of field,
(photorealistic:1.3), 8k, highly detailed, sharp focus, cinematic lighting

Negative: lowres, bad anatomy, bad hands, text, error, missing fingers,
extra digit, fewer digits, cropped, worst quality, low quality, jpeg artifacts,
watermark, signature
```

### 權重語法 (SDXL)
- `(word:1.2)` — 加權 1.2
- `(word:0.8)` — 降權
- `[word]` — 降一點
- `((word))` — 加一點 (堆疊)
- `word1 AND word2` — 區域拆分 (進階)

### Negative Prompt (SDXL 一定要)
去除手、臉、低品質、浮水印等常見瑕疵。**短而精** 優於長列表 (太長反而稀釋)。

## SD 3.5 Prompt 寫法

**自然語言句子，不用權重語法**。

**範例：**
```
A young woman with long black hair wearing a red silk kimono, standing on a
wooden bridge over a koi pond, surrounded by cherry blossom trees in full
bloom. Soft diffused natural light filters through the petals. Photographic,
shot on 85mm lens with shallow depth of field, sharp focus on her face.

Negative: distorted face, extra fingers, blurry, low quality, watermark
```

### SD 3.5 特色
- **T5 encoder** 讓它懂長句子、邏輯、空間關係
- 文字渲染 比 SDXL 好很多
- 但美感 default 略輸 Flux / Midjourney

### SD 3.5 的 Medium 與 Large
- **SD 3.5 Medium** (2.5B) — 筆電可跑
- **SD 3.5 Large** (8B) — 高階 GPU
- **SD 3.5 Large Turbo** — 蒸餾快速版

## LoRA / Embeddings / ControlNet

SD 生態最大的價值之一：**模型客製化**。

### LoRA 語法 (A1111 / ComfyUI)
```
<lora:filename:weight>
```
**範例：**
```
a knight in armor, cinematic, <lora:my-character:0.8> <lora:sci-fi-armor:0.5>
```

### Textual Inversion / Embedding
```
[embedding:my-style:1]
```
或直接用檔名當 tag。

### ControlNet (ComfyUI / A1111)
讓你用 **骨架 / canny / depth / openpose** 控制構圖，不是 prompt 層級。用圖指姿勢，prompt 寫視覺內容。

## ComfyUI

節點式 UI。工作流是一個 graph：
- Load Checkpoint → Prompt → Sampler → VAE Decode → Save
- 可插 LoRA、ControlNet、IPAdapter、Face Detailer 等

**Prompt 在 ComfyUI 節點 (CLIP Text Encode) 中輸入**，SDXL 分 positive / negative 兩個節點。

## 常見 quality tags (SDXL 專用)

**Positive：**
`masterpiece, best quality, ultra detailed, 8k, sharp focus, professional,
award-winning, photorealistic, cinematic lighting, high dynamic range`

**Negative：**
`lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit,
fewer digits, cropped, worst quality, low quality, normal quality, jpeg
artifacts, signature, watermark, username, blurry, artist name, ugly,
duplicate, mutated, deformed`

## 範例彙整

**1. SDXL 寫實**
```
RAW photo, 1girl, long auburn hair, light freckles, cream wool sweater,
standing by a window, (soft natural light:1.1), warm tones, shallow depth of
field, (shot on Leica M6:1.2), Kodak Portra 400, 85mm, (photorealistic:1.3),
masterpiece, best quality, 8k, highly detailed skin pores

Negative: lowres, bad anatomy, plastic skin, oversaturated, oversharpened,
extra fingers, deformed hands, worst quality, jpeg artifacts, watermark
```

**2. SD 3.5 自然語言**
```
A close-up portrait of a woman in her 30s with auburn hair and light freckles,
wearing a cream wool sweater, standing by a tall window. Soft natural light
from the left illuminates her face, warm tones throughout. Photographic style,
shot on a 85mm lens with shallow depth of field, sharp focus on her eyes.
Subtle skin texture visible, no retouching.

Negative: plastic skin, oversaturated, distorted face, extra fingers
```

**3. ComfyUI + LoRA**
```
(masterpiece, best quality:1.2), fantasy knight in ornate silver armor,
glowing sword, misty battlefield at dawn, cinematic lighting, dramatic
composition, <lora:silver-armor-style:0.7> <lora:fantasy-lighting:0.4>

Negative: text, watermark, worst quality, deformed, extra limbs
```

## 常見錯誤

- **用 SDXL 語法 `(word:1.3)` 餵 SD 3.5** → 不吃，要改自然語言
- **Negative 一長串 50 個 tags** → 稀釋。保持 5–15 個核心瑕疵 tags
- **LoRA 權重都拉 1.0** → 過擬合，角色變形。多數 LoRA 最佳在 0.5–0.8
- **Prompt 寫中文餵 SDXL** → CLIP 對中文差；改英文

## 連結

- Stability AI Learning Hub - SD 3.5 Prompt Guide：https://stability.ai/learning-hub/stable-diffusion-3-5-prompt-guide
- getimg.ai Prompt Weights：https://getimg.ai/guides/guide-to-stable-diffusion-prompt-weights
- MimicPC SD 3.5 Guide：https://www.mimicpc.com/learn/stable-diffusion-3-5-prompt-guide
- Stable Diffusion Art (通用)：https://stable-diffusion-art.com/prompt-guide/
- stable-diffusion-web 通用教學：https://stable-diffusion-web.com/prompt-guide
- stabledifffusion.com Full Guide：https://stabledifffusion.com/guides/sd-3-5-prompt-guide
- HyprLab SD 3.5 Docs：https://docs.hyprlab.io/browse-models/model-list/stability/stable-diffusion-3.5
- VEED SD3 Guide：https://www.veed.io/learn/stable-diffusion-3-prompts
- SeaArt SD 3.5：https://docs.seaart.ai/guide-1/6-permanent-events/high-quality-models-recommendation/stable-diffusion-3.5
- Complete Negative Prompts Guide (imagetoprompt)：https://www.imagetoprompt.dev/blog/negative-prompts-stable-diffusion/
