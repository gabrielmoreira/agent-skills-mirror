# Ideogram 3

官網 `https://ideogram.ai/`。2026 時點主力 **Ideogram 3**。**西方模型裡文字渲染最準** 的選擇 (英文強，中文弱)。

## 定位

| 場景 | Ideogram 3 | Seedream 4.5 | Flux 1.1 Pro |
|---|---|---|---|
| 英文海報 / 排版 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 中文字渲染 | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 寫實人像 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 藝術插畫 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Style reference | ✓ | ✓ | 有限 |

## Prompt 寫法

自然語言 + 具體的字體 / 佈局描述。

```
[Scene/Subject] + [Text with quotes] + [Typography/Layout] + [Style]
```

### 文字規則 (Ideogram 的強項)

**1. 引號包字**
```
A vintage movie poster with the title "MIDNIGHT DRIVE" in large retro neon letters.
```

**2. 字體詞庫** (Ideogram 理解得很好)
- `bold sans-serif`, `thin elegant serif`, `retro marquee`, `brush script`
- `handwritten`, `graffiti`, `stencil`, `embossed metallic`
- `neon glow`, `chrome 3D`, `pixel font`, `art deco`

**3. 位置描述**
- `top center`, `bottom left`, `centered vertical`, `diagonal banner`, `wrapping around the circle`

**4. 多行文字**
```
Title "MIDNIGHT DRIVE" large at top in retro neon. Subtitle "A film by Alex Chen"
small below in thin serif white.
```

## Magic Prompt

Ideogram 有個 **Magic Prompt** 按鈕，會自動擴寫你的短 prompt。用法：
- **寫短 prompt + 開 Magic Prompt** = Ideogram 幫你補細節
- **寫完整 prompt + 關 Magic Prompt** = 照你的來

兩種都有用：短 prompt + Magic Prompt 適合探索；長 prompt + 關 Magic Prompt 適合精準控制。

## Style Reference

上傳 1–N 張圖當風格參考。UI 上的 slider 控制強度。用法類似 Midjourney sref，但介面更友善。

## 範例

**1. 品牌海報**
```
Minimalist gym membership poster, vertical 9:16. Bold headline "UNSTOPPABLE"
in huge black sans-serif, top center. Below it, the body text "JOIN US TODAY
— 30 DAYS FREE" in smaller white sans-serif. A silhouette of a runner against
an orange-to-red gradient background. High contrast, modern editorial style.
```

**2. 菜單**
```
Restaurant menu cover, elegant typography. Title "LA TABLE" in thin golden
serif script, centered top. Subtitle "Season 2026" in small all-caps sans-serif,
below. Cream textured paper background with a single sprig of rosemary in the
corner. Luxurious, minimalist French bistro aesthetic.
```

**3. T-shirt 設計**
```
Retro sunset design for t-shirt print. Large arched text "WAVE RIDER" in
1980s chrome 3D letters, top. Below it, a pixelated sun setting over stylized
purple waves. Palette: magenta, cyan, orange, deep purple. Center composition,
transparent background.
```

## 參數

- Aspect：16:9, 9:16, 1:1, 4:3, 3:4, 等
- Resolution：1024 以上
- Style presets：Realistic, Design, Anime, 3D 等
- Magic Prompt：on/off
- Color palette：可指定主色 (新版支援)
- Negative prompt：有，但輕量

## 常見錯誤

- **用中文** — Ideogram 中文偶爾對，但不穩。中文字請用 Seedream。
- **字太多** (超過 20 字) — 會歪。分行或縮短。
- **指定具體字型 (Arial)** — Ideogram 不保證字體匹配；用風格描述 (`clean modern sans-serif`)。
- **忘記引號** — 字會變成場景元素 (變招牌圖案)。

## 連結

- 官網：https://ideogram.ai/
- (Ideogram 3 沒有官方獨立 prompt guide，參考通用教學 + 實驗)
