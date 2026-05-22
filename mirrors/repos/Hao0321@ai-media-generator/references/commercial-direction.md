# 廣告 / 時尚 / MV 導演級別的 Prompt 設計

**定位：** 當使用者要的是「廣告片級」、「時尚編輯級」、「MV 精美」—— 與敘事電影不同的視覺語言。廣告講求 **30 秒說完一個情緒**、**商品/品牌必須存在感強**、**每個鏡頭都要能當 stills 用**。

見 [cinematic-direction.md](cinematic-direction.md) 取得共用的 DP / 燈光 / 底片 / 構圖語彙 — 本檔聚焦 **商業項目獨有的範式**。

---

## Part 1 — 廣告片 (TVC / Commercial) 範式

### 主要類型

| 範式 | 特徵 | 代表品牌 |
|---|---|---|
| **Product Hero** | 商品佔主畫面、靜物級光、慢推 | Apple、Rolex、Hermès |
| **Lifestyle Vignette** | 使用者情境、快剪、面部特寫 | Coca-Cola、Starbucks |
| **Manifesto / Epic** | 大景 + 排比 + 激勵旁白 | Nike、Adidas、Apple "Think Different" |
| **Director's Film** | 電影導演拍短片 + 品牌輕置入 | Prada、Chanel、Gucci |
| **Demo / Tech** | 科技感、UI 合成、未來感 | Samsung、Google、Tesla |
| **Emotional Story** | 30 秒微短片、淚點 | 保險、家電、醫療 |

---

### Apple 美學

- **極簡、白底、負空間**
- 商品慢慢推近、360° 旋轉
- **無遮擋** 的神級產品光
- 音效淨化、無背景音樂只有商品聲
- **絕不出現競品 / 多餘元素**

**Prompt token：**
```
Apple product commercial aesthetic, pure white cyclorama background,
product hero shot, slow dolly-in on the subject, clean geometric negative
space, seamless light gradient, no visible light source, 50mm macro,
impossibly clean, Phase One IQ4, commercial product photography, minimal
color story
```

---

### Nike / Adidas 運動英雄美學

- **低角度英雄鏡**
- 汗水、氣息、慢動作 120fps+
- 高對比肌肉、筋脈特寫
- 激勵文字大字卡、黑底白字
- Phantom 高速攝影機

**Prompt token：**
```
Nike commercial heroic aesthetic, low-angle athlete hero shot, 200fps
Phantom slow motion, sweat droplets mid-air, muscle tension close-up,
backlit silhouette against stadium lights, high contrast bleach bypass
grade, industrial concrete textures, bold white sans-serif typography
overlay
```

### 運動廣告特殊 token
- `Phantom Flex 4K 1000fps slow motion`
- `sweat spray against stadium backlight`
- `muscle tendon vein detail macro`
- `stadium arc lamp silhouette backlit`
- `concrete, rubber track, sports floor texture`

---

### 奢侈品 / 時尚品牌

- **極慢節奏、長靜物鏡**
- 自然光、金色調、天鵝絨陰影
- 模特若有若無、模糊臉、氣質優先
- 音樂：鋼琴 / ambient / 無人聲

**Prompt token (Chanel / Dior / Hermès)：**
```
Luxury fashion commercial, Chanel-inspired, 35mm film grain, natural window
light, golden hour, slow static macro of silk fabric, model's neck and
collarbone only (face out of frame), Phase One medium format, Kodak Portra
400, refined elegance, muted gold and ivory palette, no visible branding
```

### 珠寶/手錶
```
Haute horlogerie macro, 100mm macro at f/8 focus stacked, studio seamless
black velvet background, 3-point softbox + edge rim, watch dial crystal-
clear engravings, mechanical movement visible, sub-pixel sharp, deep
obsidian shadows
```

---

### 美妝 / 保養

- **皮膚無孔、柔光、肌理但無瑕**
- 產品放在皮膚旁 / 倒映在眼睛
- 粉紅/米白/金色調
- 超廣角慢推

**Prompt token：**
```
Beauty campaign aesthetic, clamshell beauty lighting (top and bottom
softbox), perfectly diffused skin texture, no harsh shadows, 85mm macro on
lips and cheek, product reflected in subject's eye, peach and cream color
palette, shot on Phase One XF, editorial no-retouch feel
```

---

### 汽車廣告

- **低機位 + tracking**
- Drone 環繞
- 沙漠/山路/空曠公路
- 車身倒映天空 / 霓虹

**Prompt token：**
```
Automotive commercial, low-angle tracking shot alongside a moving car,
drone orbit around the vehicle in a desert salt flat, golden hour with long
shadows, Arri Alexa LF, Cooke S7/i anamorphic, hyper-polished body paint
reflecting the sky, tire dust catching light, cinematic teal and amber
grade
```

---

## Part 2 — 時尚電影 (Fashion Film) 範式

時尚片與敘事電影的差異：**沒有劇情也成立**、**節奏由音樂與模特動作決定**、**服裝才是主角**。

### 知名時尚導演 / 攝影師風格

| 人物 | 美學 | Prompt token |
|---|---|---|
| **Nick Knight** (SHOWstudio) | 運動+時尚、實驗、流體 | `Nick Knight fashion film, liquid fabric in slow motion, studio high-key white, experimental motion` |
| **Mario Sorrenti** | 自然裸色、親密、柔焦膠片 | `Mario Sorrenti intimate naturalism, natural skin tones, soft film grain, muted beige and ochre, 35mm` |
| **Steven Meisel** | 戲劇化、敘事性時尚 | `Steven Meisel theatrical fashion, editorial storytelling, saturated dramatic lighting` |
| **David Sims** | 極簡強構圖、冷調 | `David Sims minimal strong composition, cool clinical tones, clean studio` |
| **Jonathan Glazer** (Fashion 跨電影) | 恐怖美、冷感、手術級構圖 | `Jonathan Glazer clinical unease, cold palette, static long take, unsettling stillness` |
| **Spike Jonze** (廣告 + 電影) | 夢幻、怪誕溫柔 | `Spike Jonze whimsical surrealism, warm childlike wonder, handheld intimate` |
| **Luca Guadagnino** (Bvlgari, 電影) | 義式肉感、陽光、皮膚 | `Guadagnino sensual Italian sun, tactile skin textures, warm villa interior` |
| **Sofia Coppola** (Dior, Louis Vuitton) | 柔焦、少女感、粉色 | `Sofia Coppola soft pastel femininity, Marie Antoinette aesthetic, dreamy grain` |
| **Harmony Korine** (Gucci) | 粗糙街頭、迷幻 | `Harmony Korine raw street aesthetic, VHS fuzz, psychedelic color shifts` |

### 時尚片結構範本

```
Duration: 60-90 seconds
Structure:
- 0-10s: 環境建立 (場景氛圍，模特未現身或只有局部)
- 10-30s: 模特入鏡，單一慢動作動作
- 30-50s: 服裝特寫 (布料、刺繡、釦子)
- 50-70s: 情緒 close-up
- 70-90s: Logo 靜止或淡出
```

---

## Part 3 — MV (音樂影片) 導演範式

### 知名 MV 導演

| 導演 | 簽名 | Prompt token |
|---|---|---|
| **Hiro Murai** (Childish Gambino, FKA twigs) | 超現實、低光、剪影、緩慢不安 | `Hiro Murai surreal dream logic, silhouette in low light, run-down urban horror atmosphere, slow unsettling pace, one continuous handheld take` |
| **Jonathan Glazer** (Radiohead, Massive Attack) | 冷峻美、嚴謹構圖 | `Jonathan Glazer clinical precision, locked-off camera, cold palette, uncanny stillness` |
| **Chris Cunningham** (Aphex Twin) | 恐怖 + 扭曲人體 + 工業 | `Chris Cunningham industrial horror, distorted figures, bleak institutional lighting` |
| **Michel Gondry** (White Stripes, Björk) | 手工藝、童趣、實拍特效 | `Michel Gondry handmade practical magic, in-camera effect, whimsical craft, cardboard sets` |
| **Spike Jonze** (Weezer, Björk) | 怪誕溫柔、音樂劇感 | `Spike Jonze whimsical narrative, warm suburban americana, handheld intimacy` |
| **Jonas Åkerlund** (Madonna, Rammstein) | 快剪、高對比、暴力美學 | `Jonas Åkerlund rapid cuts, high contrast, provocative imagery, saturated colors` |
| **Cole Bennett** (Lyrical Lemonade) | 動漫/街頭、拼貼特效、VFX 密集 | `Cole Bennett Lyrical Lemonade aesthetic, urban anime cutouts, neon VFX overlays, tight editing to beat` |
| **Hype Williams** (90s hip-hop) | 魚眼、廣角、高光金屬 | `Hype Williams fisheye 8mm, chrome and diamonds, saturated velvet primary colors` |
| **Director X** (Drake, Rihanna) | 乾淨高端、品牌感 | `Director X clean polished hip-hop, luxury modern production, teal and amber` |
| **Dave Meyers** (Missy Elliott, Kendrick Lamar) | 風格混搭、高概念 | `Dave Meyers high-concept stylized world, surreal set design, bold graphic color` |
| **Floria Sigismondi** (Marilyn Manson) | 哥特、扭曲美 | `Floria Sigismondi gothic, twisted painterly figures, baroque darkness` |
| **Romain Gavras** (Justice, M.I.A.) | 壯觀 + 破壞美 | `Romain Gavras epic destruction, large-scale crowds, political imagery, epic tableau` |

### MV 鏡頭節奏與音樂對齊

**核心技巧：把音樂結構寫進 prompt**

```
A 60-second music video segment timed to a 95 BPM track.

0-4s (Intro, filter sweep): [視覺 A]
4-20s (Verse 1, sparse beat): [視覺 B, slower pace, one shot per 4 beats]
20-28s (Pre-Chorus, build): [cuts accelerate, 1 shot per 2 beats]
28-44s (Chorus, drop): [high-energy montage, 1 shot per beat, wide shots]
44-60s (Verse 2 + Outro): [return to character, slow resolution]

Style: [挑一個 MV 導演] aesthetic
Lighting: [對應風格]
```

### MV 特有視覺語彙

- `beat-matched editing, one cut per kick drum`
- `performance shot with artist lip-syncing to camera`
- `visualizer aesthetic, abstract reactive motion graphics`
- `one-take music video, continuous oner choreography`
- `handheld energy matching the song's energy level`
- `smoke bomb saturation, colored smoke grenade`
- `backlight rim only, silhouette performance`

---

## Part 4 — 社群短影音 (TikTok / Reel / Shorts)

### 核心差異

- **9:16 豎版**，頭部構圖 (頭部在上三分之一)
- **前 3 秒要抓住** — 強視覺 hook
- **快節奏** (< 2 秒 / 鏡)
- **中央主體**，兩側要留字幕空間
- 讀唇感：人物對著鏡頭說話直接

### TikTok UGC 感 (Ugly good)
```
Handheld selfie-style vertical 9:16, iPhone 15 Pro front camera, natural
room lighting, messy background, no filter, slight motion blur, authentic
bedroom aesthetic, 4K/30fps
```

### 美食 ASMR / Food Porn
```
Overhead 90° top-down vertical shot, macro 100mm on plate, steam rising
lit by side light, close-up fork lifting cheese pull, glistening oil,
saturated but natural food colors, 240fps slow motion for the splash,
shallow depth of field, 9:16
```

### 科技開箱 (Tech Unboxing)
```
Overhead vertical 9:16, crisp studio lighting, black table, hands entering
from bottom slowly revealing product, clean macro on logos and ports,
seamless white gradient background option, 50mm macro
```

### Fitness / Motion
```
Vertical 9:16, low-angle athletic shot, 120fps slow motion on movement,
practical gym lighting, high contrast, saturated red/black/white brand
palette, text overlay safe zones top and bottom
```

### Beauty / Makeup Tutorial
```
Vertical 9:16 front-facing, ring light soft shadowless, 85mm equivalent,
subject centered with blurred background, natural skin but polished,
studio cyclorama wall, 4K/60fps
```

---

## Part 5 — 品牌調性 (Brand Tone) 對應

幫使用者選 prompt 語彙前，先問「這是哪一類品牌？」

| 品牌類別 | 調性 | Prompt 優先 token |
|---|---|---|
| **Apple / 科技奢華** | 極簡、冷靜、精確 | `minimal, precise, cool white, seamless, no clutter` |
| **Nike / 運動激勵** | 熱血、肌肉、勝利 | `heroic, low-angle, slow motion sweat, bold typography` |
| **Chanel / 時尚奢侈** | 冷豔、黑白、復古 | `Paris Vogue 1960s, monochrome, haute couture stillness` |
| **Coca-Cola / 快消** | 溫暖、家庭、亮色 | `warm sunset, multicultural friendship, saturated brand red` |
| **Tesla / 未來科技** | 冷感、極客、流體 | `futuristic minimal, cool blue-white, aerospace precision` |
| **IKEA / 生活實用** | 北歐、溫暖、家 | `Scandinavian warmth, soft daylight, living room warmth` |
| **Airbnb / 旅遊** | 故事、真實、人情 | `travel diary, natural light, authentic local moment` |
| **Netflix / 影集** | 電影級、戲劇性 | `cinematic drama, teal-orange, key art composition` |
| **Spotify / 音樂** | 高飽和、圖像感、漸層 | `saturated poster-like color blocks, gradient backgrounds, bold graphic` |
| **Rolex / 奢侈錶** | 靜止、金色、權威 | `static authoritative, gold and jade green, macro on craftsmanship` |
| **Supreme / 街牌** | 粗糙、紅白、叛逆 | `gritty skate culture, red and white, urban raw` |
| **Patagonia / 戶外** | 紀實、粗粒、山 | `documentary grain, mountain wilderness, earth tones, 16mm film feel` |

---

## Part 6 — 典型廣告 / MV 工作流

### 商業拍攝思考順序

1. **Brand brief** — 誰是品牌？賣什麼？情緒？
2. **Key visual** — 一張圖能代表整個廣告 (poster shot)？
3. **30-second arc** — Hook (0-3s) / Build (3-15s) / Product reveal (15-25s) / Tagline (25-30s)
4. **Shot list** — 通常 6-10 鏡 / 30s
5. **Hero shots** — 2-3 個最終用於海報與 still 的構圖
6. **Transitions** — match cut on motion、whip pan、speed ramp

### 案例：運動飲料廣告 (30 秒)

```
CONCEPT: 「在你想停下時，再推一下」

Brand: energy drink, dynamic, hyper-athletic
Duration: 30s, 16:9 master (9:16 cutdown)

Shot list:
0-3s HOOK:
  Extreme close-up of athlete's eye, sweat dripping from brow, reflection
  of finish line in pupil. Shot on Alexa 65 at 120fps Phantom slow motion,
  harsh 1-point rim light from stadium arc lamp, bleach bypass grade.

3-10s BUILD:
  Low-angle tracking shot following athlete's feet pounding track. Dust
  kicks up in slow motion. 200mm telephoto compressed background stadium
  lights bokeh. Practical red/blue LED stadium glow.

10-18s PEAK:
  Hero shot: athlete mid-stride, arms up, backlit silhouette against arc
  lamp, exploding sweat droplets in air, saturated brand red gel light
  from behind. 85mm at f/2.8, 240fps, crushed blacks.

18-25s RELIEF:
  Athlete collapses to knees on finish line, handheld intimate. Warm
  golden hour sun bleeds through stadium. Tear mixing with sweat, close-up.
  Kodak Vision3 500T, natural grain.

25-30s BRAND:
  Product bottle slides across finish line, practical stadium light above.
  Tagline fades in: bold sans-serif white on black. Brand red accent.
```

---

## Part 7 — 廣告/MV 專用陷阱

| 陷阱 | 症狀 | 對策 |
|---|---|---|
| **商品太小** | AI 生出來商品只佔 5% 畫面 | prompt 明講 `product fills center, subject 40% of frame` |
| **品牌 Logo 錯字** | AI 渲染商標錯字 | Seedream + 引號寫 logo；或 後期合成 |
| **臉太完美** | 看起來像 AI 美顏 | 加 `natural skin pore texture, no retouching, freckles visible` |
| **構圖不留字幕位** | 頭頂或底部滿版、無處放標語 | 加 `negative space top 20%` / `lower thirds safe zone` |
| **光線太平** | 廣告看起來像存貨庫 | 明講 `one-point dramatic key light from camera-left, deep shadow fill side` |
| **色彩不統一** | MV 每鏡顏色跳 | 固定 `color palette: [品牌色 A] + [配色 B]` 在每個 shot |

---

## 連結

- [Luxury Fashion Brands with Cinema Directors](https://luxurysociety.com/en/luxury-fashion-brands-using-cinema-directors-in-video/)
- [Hiro Murai Creative Review](https://www.creativereview.co.uk/hiro-murai-director/)
- [Hiro Murai Directors' Library](https://directorslibrary.com/2013/latest/editorial/interviews-and-talks/director-id-hiro-murai/)
- [Fashion Films Business of Fashion](https://www.businessoffashion.com/videos/technology/fashion-2-0-top-10-fashion-films-of-the-season-5/)
- [TeePee Fashion Directors](https://www.teepeefilms.com/fashion-directors)
- [Lights Film School - Fashion Film](https://www.lightsfilmschool.com/blog/fashion-film-new-music-video)
- [Sora 2 Prompts for AI Video](https://www.youngurbanproject.com/sora-prompts-for-ai-video-generation/)
