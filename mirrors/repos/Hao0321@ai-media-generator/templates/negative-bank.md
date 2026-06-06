# 負面提示詞庫 (Negative Prompt Bank)

針對不同模型與不同任務的常用「要避免」詞組。**短而精** 比長列表有效。多數模型 5–15 個 tag 是甜蜜點。

## 按模型支援度

| 模型 | Negative Prompt 支援 | 備註 |
|---|---|---|
| Kling 3.0 | ✓ 原生獨立欄位 | 效果明顯；別塞 >15 詞 |
| Seedance 2.0 | ✓ | 效果中等 |
| Seedream 5.0 / 4.0 | ✓ | 明顯 |
| Vidu Q3 | ✓ | 中等 |
| Runway Gen-4.5 | ✗ 官方無 | 用 "avoid..." 寫進 prompt 尾，或正向改寫 |
| ~~Sora 2~~ | 🔴 平台已停運 (2026-04) | 勿用 |
| Veo 3.1 | 輕 | 寫進 prompt 尾 |
| Midjourney V8.1 | `--no X, Y` | 官方方式 |
| Flux 1.1 Pro | 輕支援 | 重寫 prompt 更有效 |
| Flux Kontext | 不需要 | 直接講保留什麼 |
| Ideogram 3 | ✓ 輕量 | |
| SDXL | ✓ **核心機制** | 長 list 有效 |
| SD 3.5 | ✓ | 仍有用但短即可 |
| Suno v5.5 | ✓ Style 欄尾 / Exclude styles slider | `no auto-tune, no rap` |

## 人物類 (影片 + 圖像通用)

### 臉/手/身體瑕疵
```
deformed face, distorted face, asymmetrical eyes, crossed eyes, extra eye,
warped facial features, uncanny valley, plastic skin, overly smooth skin,
airbrushed, extra limbs, extra arms, extra legs, missing limbs, extra fingers,
six fingers, seven fingers, fused fingers, distorted hands, mutated hands,
malformed limbs, bad anatomy, warped anatomy, disproportionate body
```

### 視覺瑕疵
```
blurry, out of focus (除非你要), low resolution, pixelated, jpeg artifacts,
compression artifacts, noise, grainy (除非你要), oversaturated, overexposed,
underexposed, washed out, flat lighting
```

### 介面/元素
```
watermark, signature, text overlay, logo, subtitle, timestamp, timecode,
UI elements, HUD, caption, copyright, username
```

## 影片類專屬

### 動態問題
```
jittery camera, erratic motion, camera shake (除非你要 handheld),
frame stutter, frame drop, choppy motion, unstable footage, motion jitter,
stuttering animation, ghosting, motion trails (若不要)
```

### 物理不合理
```
objects floating unnaturally, clipping through walls, impossible physics,
melting geometry, morphing body parts, inconsistent shadows
```

## 圖像類專屬

### 構圖
```
cropped, cut off, out of frame, poorly framed, centered boring composition
(若要藝術構圖), tilted horizon (若不要 Dutch angle)
```

### 品質 tag (SDXL 傳統)
```
lowres, worst quality, low quality, normal quality, sketchy (若不要素描),
unfinished, draft, doodle
```

## 按任務類型

### 寫實人像 (要避免「AI 臉」)
```
plastic skin, overly smooth skin, airbrushed, waxy appearance, uncanny valley,
symmetrical face (人臉本來微不對稱), oversharpened, beauty filter look,
unrealistic eye shine, glossy lips (若不要)
```

### 產品攝影（圖像）
```
blurry, low quality, watermark, background clutter, distracting reflections,
fingerprints, dust, shadows on label, warped text, bad reflection,
plastic look, oversaturated, harsh flat lighting, distorted product shape
```

### 產品廣告（影片）⭐ 最致命：主體變形

產品在動畫中變形是廣告級 killer。**先看 [quality-control.md §1 主體完整性](../references/quality-control.md)**，這裡是配套 negative：
```
deformed product, morphing shape, warping geometry, melting object,
inconsistent label, distorted logo, shape-shifting, structural collapse,
garbled text, flickering, texture boiling, plastic look, CGI render,
jittery camera, warped reflection
```
**根治法不是堆 negative，是切 i2v**：先用 Ideogram/Seedream/MJ 定死 hero 圖 → i2v 只動畫化，形狀被圖鎖死。

### 藝術插畫
```
photorealistic (若要插畫感), 3D render (若要 2D), muddy colors,
oversaturated, lack of detail, flat shading (若要 shading),
inconsistent line weight
```

### 動畫 / 卡通
```
photorealistic, 3D render, blurred, distorted proportions, inconsistent style,
realistic skin texture, photographic lighting
```

### 食物
```
plastic looking, fake, inedible appearance, cgi look, oversaturated colors,
bad composition, cluttered background, dirty plate
```

### 建築 / 風景
```
people (若不要人), cars (若不要車), power lines (若不要),
crooked verticals, perspective distortion, warped windows
```

## Midjourney `--no` 用法

```
prompt here --no text, watermark, signature, extra fingers, plastic skin
```

多個用逗號分隔，放在參數後。

## Suno Style 欄負面用法

放最後，用清楚動詞：

```
...existing style tags..., no auto-tune, no rap, no male vocals, exclude dubstep
```

## 「不要動的元素」(Flux Kontext 風格)

Kontext 不吃 negative prompt，直接用肯定句：

- `keep the face, hair, and clothing unchanged`
- `preserve the original lighting`
- `only change the background`
- `maintain the existing composition`

## 整組 Ready-to-use Negative (按模型)

### 針對 Kling / Seedance / Vidu (影片)
```
deformed face, extra fingers, extra limbs, distorted hands, plastic skin,
blurry, jittery camera, frame stutter, low quality, watermark, text overlay,
logo, subtitle, oversaturated, artifacts
```

### 針對 SDXL (寫實人像)
```
lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit,
fewer digits, cropped, worst quality, low quality, normal quality, jpeg
artifacts, signature, watermark, username, blurry, plastic skin, oversaturated,
overexposed, deformed face, asymmetrical eyes, ugly, duplicate, mutated hands
```

### 針對 SD 3.5 (精簡)
```
distorted face, extra fingers, blurry, low quality, watermark
```

### 針對 Seedream (圖像)
```
blurry, low quality, watermark, logo, jpeg artifacts, distorted text,
garbled letters, extra limbs, deformed hands, plastic skin, oversaturated
```

### 針對 Suno (音樂，一般流行/電影)
```
no auto-tune (若不要), no distorted vocals, no harsh clipping,
exclude lo-fi artifacts (若不要)
```

## 反模式：不要放的東西

- **太多同義詞** (`blurry, fuzzy, out of focus, unfocused, soft focus`) — 只選一個
- **與 prompt 衝突** (prompt 寫 "watercolor painting" + negative "painting") — 互相打架
- **抽象概念** (`bad art, ugly style`) — 模型不懂
- **過度小心** (負向列 50 個) — 稀釋訊號
- **在 Midjourney 同時用 `--no` 又用 `negative prompt:`** — MJ 只吃 `--no`

## 快速選擇法

**90% 的情境用這個「通用保底 12 句」** (影片 + 真實人像圖)：

```
deformed face, extra fingers, extra limbs, distorted hands, plastic skin,
blurry, low quality, watermark, logo, subtitle, oversaturated, artifacts
```

若是插畫/動畫，替換為：

```
photorealistic, 3D render, blurry, muddy colors, inconsistent style,
flat lighting, low quality, watermark, text overlay, deformed proportions
```
