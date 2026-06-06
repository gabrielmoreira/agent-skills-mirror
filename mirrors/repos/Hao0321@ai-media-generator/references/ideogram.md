# Ideogram 3.0 — 西方模型文字渲染王者

官網 `https://ideogram.ai/`。2026 時點主力 **Ideogram 3.0**（2025-03 發布，全用戶 + iOS App 開放）。**西方模型裡文字渲染最準** 的選擇 — 短文字準確率約 90%、可讀性約 95%（自有 typography 模型），對比 Midjourney 短語約 30%。**英文強、中文弱**。

可用入口：ideogram.ai 網頁、iOS App、API（Pro tier 起）；Replicate / fal.ai / Kie.ai 有第三方代理。

---

## 核心定位

| 場景 | Ideogram 3.0 | Seedream 4.5 | Flux 1.1 Pro | Midjourney v7 |
|---|---|---|---|---|
| 英文海報 / 排版 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Logo / 招牌精準文字 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 中文字渲染 | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| 寫實人像 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 藝術插畫 / 美學 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Style Reference | ✓（≤3 張） | ✓ | 有限 | ✓（sref） |
| 局部編輯 (inpaint) | ✓ Magic Fill | ✓ | 需外掛 | ✓（v7 限定） |
| 角色一致性 | ✓（2025-08 起） | ✓ | 有限 | ✓（cref） |

**一句話選型：** 畫面裡要出現「正確、好看、可讀的文字」→ Ideogram 是西方模型第一順位；中日韓文字 → 轉 Seedream；純美學無文字 → Midjourney / Flux 更強。

---

## 版本能力矩陣 (Ideogram 3.0)

| 能力 | 狀態 | 備註 |
|---|---|---|
| 文字渲染 | ⭐⭐⭐⭐⭐ | 短文字約 90% 準確；文字會吸收場景光影/材質/透視，不再是貼上去的 |
| Style Reference | ✓ | 上傳 ≤3 張參考圖控制美學，補足文字描述不到的風格 |
| Style Code | ✓ | 8 碼代碼，複用 Random 生成過的風格到新 prompt |
| Random Style | ✓ | 號稱 43 億種預設組合，盲抽風格找靈感 |
| Style presets | ✓ | Realistic / Design / 3D / Anime（General/Auto 預設） |
| Magic Prompt | ✓ | On/Off 切換；On 會把短 prompt 擴寫後再生圖 |
| Canvas（無限畫布） | ✓ | 把生成 / 上傳圖放上畫布做局部編輯、合成、擴展 |
| Magic Fill（inpaint） | ✓ | 遮罩選區 → 文字 prompt 替換/新增物件、修瑕、改背景、**改招牌文字** |
| Extend（outpaint） | ✓ | 把圖往外擴展、補滿構圖，風格延續 |
| 角色一致性 | ✓ | 2025-08-06 上線；給角色參考圖跨多張維持樣貌 |
| Describe（圖生 prompt） | ✓ | 上傳圖反推 prompt（逆向工程他人作品用） |
| Upscale | ✓ | 提升解析度；Magic Fill 前先 Upscale → AI 有更多像素可用，修補更穩 |
| Color palette | ✓ | 可指定主色調 |
| API | ✓ | Pro tier 起提供 |
| 中文字 | ⭐ | 偶爾對但不穩；正式中文字一律轉 Seedream |

> (待驗證) 截至 2026-06 主力仍為 **3.0**；2026-01 有「生成速度 +30%」的平台優化，但**未見**官方宣布 3.1/4.0 大版號。若操作時 UI 出現更高版號，以實機為準。

---

## Prompt 寫法

自然語言 + 具體的字體 / 佈局描述。Ideogram 的核心差異化在**文字**，prompt 設計優先把文字內容、字體、位置講清楚。

```
[Scene/Subject] + [Text in "quotes"] + [Typography/Font style] + [Layout/Position] + [Style/Mood]
```

### 文字規則（Ideogram 的護城河）

**1. 引號包字 — 鐵則**
引號內的字 = 要「渲染成文字」；不包引號 → Ideogram 會把字當場景元素畫成圖案（變招牌插畫）。
```
A vintage movie poster with the title "MIDNIGHT DRIVE" in large retro neon letters.
```

**2. 字體詞庫**（Ideogram 理解得很好，用「風格描述」而非具體字型名）
- 襯線/無襯線：`bold sans-serif`, `thin elegant serif`, `condensed grotesque`, `slab serif`
- 復古/裝飾：`retro marquee`, `art deco`, `1970s groovy`, `western wood type`, `vintage letterpress`
- 手寫/筆刷：`brush script`, `handwritten`, `calligraphic`, `signature script`
- 街頭/工業：`graffiti`, `stencil`, `spray paint`, `varsity collegiate`
- 質感/特效：`embossed metallic`, `chrome 3D`, `neon glow`, `gold foil`, `glossy plastic`, `pixel font`, `letterpress deboss`

**3. 位置描述**
- `top center`, `bottom left`, `centered vertical`, `diagonal banner`, `arched at the top`, `wrapping around the circle`, `lower third`, `corner badge`

**4. 多行 / 階層文字**（標題 + 副標 + body 分開描述，各給字體/大小/顏色）
```
Title "MIDNIGHT DRIVE" large at top in retro neon. Subtitle "A film by Alex Chen"
small below in thin white serif. Tagline "IN THEATERS THIS FALL" tiny at bottom,
all-caps condensed sans-serif.
```

**5. 字數控制**：單一構圖文字總量 **≤ 20 字** 最穩；超過要分行、分階層、或縮短。長段落文字仍是所有生圖模型的弱項。

### Magic Prompt — on/off 時機（進階）

Magic Prompt = Ideogram 內建「prompt 改寫器」，把你的 prompt 擴寫得更豐富再送去生圖。**On 時 4 張圖全用改寫後的 prompt；Off 時用你的原文。**

| 情境 | Magic Prompt | 理由 |
|---|---|---|
| 短 prompt / 找靈感 / 沒方向 | **On** | prompt 越精簡，Magic Prompt 補越多，幫你破白紙焦慮 |
| 搭配 Random Style 盲抽 | **On** | 短 prompt + 隨機風格 = 最大探索 |
| 精準文字海報 / Logo / 客戶稿 | **Off** | 避免它擅自改寫破壞你指定的字體/排版/文字內容 |
| 已用 Style Reference / Style preset | **Off** | 官方建議：用 style 控制時關掉 Magic Prompt，**並且 prompt 裡不要再塞風格關鍵字**，把美學決定權交給 style 系統，避免雙重風格打架 |
| 長且完整的 brief | **Off** | 你已經寫滿，不需要它加料 |

> 燒 credit 注意：Magic Prompt On 會讓 4 張圖都吃改寫版，若改寫方向歪掉 = 整批 4 張一起報廢。專業稿建議 **Off + 自己寫滿**。

### Style Reference / Style Code / Random（進階風格控制）

- **Style Reference**：上傳 **最多 3 張** 參考圖，讓 Ideogram 模仿那批圖的美學（配色、筆觸、材質、光線）。適合「我講不清楚但我有 mood board」的情況，等同 MJ 的 sref 但介面更友善。**搭配時關 Magic Prompt + prompt 不寫風格詞**。
- **Style Code**：用 Random 生成時，每張圖會得到一組 **8 碼 Style Code**。記下喜歡的那組，貼到新 prompt 即可複用同一種視覺風格 → **跨 prompt 維持品牌一致性的最輕量做法**。
- **Random Style**：盲抽風格（號稱 43 億組合），短 prompt + Random + Magic Prompt On = 靈感發散機。抽到喜歡的就抄它的 Style Code 固定下來。

---

## 進階功能地圖 (Canvas + 編輯)

Ideogram 不只文生圖，**Canvas 是它從「生成」走向「設計工具」的關鍵**。流程通常是：生成 / 上傳 → 放上 Canvas → 局部修。

### 1. Canvas（無限畫布）
把生成圖或上傳圖擺到無限畫布上，做局部編輯、多圖拼合、向外擴展。是 Magic Fill / Extend 的承載環境。

### 2. Magic Fill（inpaint 局部重繪）
遮罩選區 + 文字 prompt，用來：**替換物件、新增元素、修瑕疵、換背景**。
- **Ideogram 的殺手鐧：改招牌/標籤上的文字** — 一般 inpaint 工具改文字會糊，Ideogram 因為文字模型強，**常常一次就把招牌文字換對**。
- 操作三步：① 遮罩要改的區域 → ② 調整 generation window 位置/大小（**務必框入足夠的周邊原圖當 context**）→ ③ prompt 描述「畫面裡有什麼 + 你要改成什麼」。
- 一次出多個候選，下方箭頭切換 4 個版本選最好。
- **進階訣竅**：動手 Magic Fill 前先對該圖 **Upscale**，AI 拿到約 2 倍像素，修補細節（尤其小字）成功率明顯提高。

### 3. Extend（outpaint 向外擴展）
把圖往邊界外延伸、補滿更大構圖（例如 1:1 → 16:9 banner），風格與內容自動延續。改版面比例 / 補留白給文字時很好用。

### 4. 角色一致性 (Character Consistency)
2025-08 上線。提供角色參考圖，跨多張生成維持同一張臉/造型。適合：系列海報主角、品牌吉祥物、漫畫分鏡同一人物。(待驗證) 介面入口與 weight 細節以實機為準。

### 5. Describe（圖反推 prompt）
上傳圖 → Ideogram 吐出推測 prompt。用來逆向學習喜歡的作品怎麼下 prompt。

---

## 進階 Recipe

### Recipe A — Logo / 海報精準文字（客戶交付級）
**目標：** 文字 100% 正確 + 排版可控。**設定：** Magic Prompt **Off**、Style preset = `Design`、字數 ≤ 8。
```
Minimalist gym membership poster, vertical 9:16. Bold headline "UNSTOPPABLE"
in huge black condensed sans-serif, top center. Below it, body text "JOIN US
TODAY — 30 DAYS FREE" in smaller white sans-serif. A silhouette of a runner
against an orange-to-red gradient background. High contrast, modern editorial
style, generous negative space.
```
**收尾：** 若某字母歪 → 不要重生整張，用 **Magic Fill 只遮那塊文字**重繪（先 Upscale）。

### Recipe B — 品牌 Typography 系統（跨圖一致）
**目標：** 一整套同風格 banner / 貼文，視覺統一。**做法：** 先 Random 抽風格 → 拿到滿意那張的 **8 碼 Style Code** → 套到後續每一張 prompt。Magic Prompt **Off**，prompt 不寫風格詞（風格交給 Style Code）。
```
[Style Code: XXXXXXXX]
Social media banner, square 1:1. Centered logotype "AURORA" in elegant
high-contrast serif, soft gold foil texture. Subtitle "skincare" below in
tiny tracked-out all-caps sans-serif. Cream studio background, single soft
shadow, premium beauty aesthetic.
```
→ 換 "AURORA" / 換 subtitle / 換產品，其餘不動，整套視覺自動同調。

### Recipe C — 既有圖換字（Magic Fill 編輯流）
**情境：** 海報已生成好，但要把標題 "SUMMER SALE" 改成 "WINTER SALE"，其餘不動。
1. 圖放上 **Canvas** → 先 **Upscale**。
2. **Magic Fill** 遮罩原標題區域，generation window 框入周邊背景當 context。
3. Prompt：`A bold red sale banner that reads "WINTER SALE" in the same thick sans-serif style as the surrounding design.`（描述要的文字 + 沿用周邊字體風格）
4. 切 4 個候選選最對的。文字模型強 → 通常 1-2 輪就換對。

### Recipe D — T-shirt / 商品印花（透明底 + 弧形字）
**設定：** Style preset = `Design`，Magic Prompt Off。
```
Retro sunset design for t-shirt print. Large arched text "WAVE RIDER" in
1980s chrome 3D letters at the top. Below it, a pixelated sun setting over
stylized purple waves. Palette: magenta, cyan, orange, deep purple. Centered
composition, isolated on transparent background, sticker-style.
```

---

## 範例（基礎參考）

**菜單封面**
```
Restaurant menu cover, elegant typography. Title "LA TABLE" in thin golden
serif script, centered top. Subtitle "Season 2026" in small all-caps sans-serif
below. Cream textured paper background with a single sprig of rosemary in the
corner. Luxurious, minimalist French bistro aesthetic.
```

---

## 參數

- **Aspect**：1:1, 16:9, 9:16, 4:3, 3:4, 10:16, 3:2 等多種
- **Resolution**：1024+；可 Upscale 放大
- **Style presets**：General(Auto) / Realistic / Design / 3D / Anime
- **Magic Prompt**：On / Off（專業稿建議 Off）
- **Style Reference**：≤3 張參考圖
- **Style Code**：8 碼，複用風格
- **Color palette**：可指定主色
- **Negative prompt**：有，但輕量（不像 SD 那麼吃重；主要靠正向描述）

---

## 付費結構速查 (2026)

> (待驗證) 各來源金額略有出入，以官網 `ideogram.ai/pricing` 實機為準。下表為多源彙整。

| 方案 | 月費 | 額度 | 重點 |
|---|---|---|---|
| **Free** | $0 | ~10 slow credits/週（週六 00:00 UTC 重置），最省設定約 40 張/週 | 圖預設公開、無 priority |
| **Basic** | ~$8/月 | ~400 priority credits/月 | 入門 priority |
| **Plus** | ~$20/月（年繳 ~$15，省 25%） | ~1,000 priority credits/月 | 私人生成 |
| **Pro** | ~$48/月（年繳 ~$42，省 ~30%） | ~3,200 credits + **API** | 最高量 + API |

**Credit 規則：**
- **Priority credits**（即時生成）只能靠訂閱 / 加購取得；**訂閱的 priority credit 每個計費週期末歸零、不滾存**。
- **Top-up（加購）credits** 在訂閱額度用完後才動用，**未用會滾存到下期**。
- Free tier 是 slow queue（排隊），且**圖預設公開**。

---

## 常見失敗 + 修法

| 症狀 | 原因 | 修法 |
|---|---|---|
| 文字變成招牌圖案 / 沒有文字 | 忘了用引號 | 要渲染的字一律 `"包引號"` |
| 拼字錯 / 字母歪 | 字太多（>20）或太小 | 縮短、分行、分階層；或先 Upscale 再 **Magic Fill** 只重繪那塊 |
| 整批 4 張風格被改歪 | Magic Prompt On 擅自改寫 | 專業稿 **關 Magic Prompt**、自己寫滿 |
| 指定 `Arial` 沒生效 | Ideogram 不保證具體字型匹配 | 改用**風格描述**（`clean modern sans-serif`） |
| Style Reference 沒效果 / 風格打架 | prompt 裡又塞了風格詞 | 用 style 系統時**關 Magic Prompt + prompt 不寫風格詞** |
| 中文字糊 / 錯 | Ideogram 中文不穩 | 中日韓文字一律轉 **Seedream** |
| Magic Fill 改完糊掉 | context 不足 / 像素太少 | generation window 框入更多周邊原圖；先 **Upscale** |
| 跨多張風格不一致 | 沒固定風格 | Random 抽風格 → 記 **8 碼 Style Code** → 套用到每張 |
| Free tier 圖被別人看到 | Free 預設公開 | 需私人生成請升級付費方案 |
| priority credit 月底突然歸零 | 訂閱 priority 不滾存 | 量大臨時需求改買 **top-up**（會滾存） |

---

## 連結

- 官網：https://ideogram.ai/
- 官方文件總站：https://docs.ideogram.ai/
- Magic Prompt 文件：https://docs.ideogram.ai/using-ideogram/generation-settings/magic-prompt
- Style & Style Reference 文件：https://docs.ideogram.ai/using-ideogram/generation-settings/style-and-style-reference
- Canvas / Magic Fill 文件：https://docs.ideogram.ai/canvas-and-editing/canvas/magic-fill
- Canvas 功能頁：https://ideogram.ai/features/canvas/
- Prompting Guide（官方）：https://docs.ideogram.ai/using-ideogram/prompting-guide/2-prompting-fundamentals
- 定價：https://ideogram.ai/pricing ／ https://docs.ideogram.ai/plans-and-pricing/available-plans
- API：https://ideogram.ai/features/api-pricing
- Ideogram 3.0 發布說明（LearnPrompting）：https://learnprompting.org/blog/ideogram-3-0
- 角色一致性（Scenario 第三方教學）：https://help.scenario.com/en/articles/ideogram-character-single-image-character-consistency/
