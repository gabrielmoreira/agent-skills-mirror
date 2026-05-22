# Midjourney v7

官網 `https://midjourney.com/`。Discord + Web UI 並行。2026 時點主力 **v7 / v7.1**。美感預設值最高的模型。

## Prompt 結構

Midjourney 喜歡 **密集的形容詞堆疊 + 參數**，而非完整句子。

```
[Subject], [environment], [style], [composition], [lighting], [mood/detail]
--參數
```

**範例：**
```
An elderly fisherman mending nets on a weathered wooden dock at dawn,
coastal village with tiled roofs in the background, golden hour light,
shot on Kodak Portra 400, 35mm, shallow depth of field, warm earthy tones,
slight film grain, cinematic --ar 16:9 --s 250 --v 7
```

## 核心參數 (v7 相容)

| 參數 | 說明 |
|---|---|
| `--ar W:H` | Aspect ratio，如 16:9, 9:16, 1:1, 21:9 |
| `--s 0-1000` | Stylize，default 100。越高越風格化，越低越接近 prompt |
| `--c 0-100` | Chaos，變異度 |
| `--weird 0-3000` | 奇異度，下一層的不尋常 |
| `--sref <code or URL>` | Style reference (見下) |
| `--oref <URL>` | Omni Reference (v7 新增，取代 --cref) |
| `--ow 0-1000` | Omni Weight，--oref 的強度 |
| `--profile <code>` | 個人化 (需 rank 200 張) |
| `--p <code>` | Personalization profile |
| `--raw` | Raw mode，減少 MJ 自動美化 |
| `--tile` | 可拼接 tile 圖 |
| `--niji 7` | 切換到 niji (動漫分支) |
| `--v 7` | 版本 (v7 為預設) |
| `--stop 10-100` | 中途停止 (創意效果) |
| `--no <元素>` | 負面提示 (取代 negative prompt) |
| `--seed <num>` | 固定 seed |

### 參數順序 & 慣例
參數放 prompt 最後。多個 --no 可用逗號分隔：`--no text, watermark, extra fingers`

## Style Reference (`--sref`)

抓 **整體美感 / 氛圍** (顏色、質感、光影、媒材)，不複製物件。

**三種寫法：**
1. **Code**：`--sref 1234567890` (MJ 內建庫)
2. **URL**：`--sref https://...jpg` (自己上傳的圖)
3. **Random**：`--sref random` (隨機抽一個)

**Style Reference 版本 (--sv)**
v7 下有 6 個 sref 子版本，預設 `--sv 6`。舊 sref 碼用 `--sv 1`–`--sv 6` 指定。

**多重 sref**：
```
--sref 111 222 333
```
三個 sref 加權平均。

## Omni Reference (`--oref`) — v7 標配

**把特定「東西」放進新圖** (角色、物件、重複元素)。取代已棄用的 `--cref`。

**寫法：**
```
prompt words --oref https://.../character.jpg --ow 400
```

- `--ow 0-1000`，default 100。越高越像 ref。
- 多個 oref 疊加：`--oref A.jpg B.jpg --ow 400`

**v7 重要變更：**
> `--cref` 在 v7 **已失效**，會被忽略或報錯。改用 `--oref`。

## Personalization (`--p` / `--profile`)

需先到 `https://midjourney.com/rank-v7` 評 ~200 張圖，解鎖個人美感 profile。解鎖後 `--p` 自動套用你的偏好。

## Image Weight — Multi-prompt

用 `::` 拆分多個子 prompt，加權：

```
cat::2 dog::1 watercolor::3 --ar 1:1
```

代表貓權重 2、狗 1、水彩風格 3。

## Permutations — 一次多個版本

用 `{}` 列舉，MJ 會跑所有組合：
```
A {cat, dog, rabbit} in a {forest, desert} --ar 1:1
```
→ 6 張圖。

## Raw Mode

`--raw` 關掉 MJ 預設的「美化偏好」，輸出更接近 prompt 的字面意思。用於：
- 不想要過度飽和/電影化
- 模仿真實攝影
- Product 攝影

## Niji

`--niji 7` 切到動漫分支。適合：
- 日系動畫
- 插畫風角色設計
- 漫畫分格

Niji 有自己的風格 token (`shoujo`, `shonen`, `ghibli`, `scenic`)。

## v6 vs v7 差異

| 項目 | v6 | v7 |
|---|---|---|
| Personalization | 次要 | 預設強化 |
| --cref | 支援 | **失效** (用 --oref) |
| --oref | 無 | **新增** |
| 寫實度 | 中 | 高 |
| 速度 | 中 | 快 |
| Text rendering | 差 | 好不少 |
| Sref 版本 | 單一 | 6 個 sv |

## 範例

**1. 攝影寫實**
```
Portrait of a weather-beaten sailor in his 60s, deep wrinkles, piercing blue
eyes, wearing a knit wool sweater, against a foggy harbor background, shot on
Leica M6, Kodak Portra 400, soft natural window light, 85mm lens, shallow
depth of field --ar 4:5 --s 150 --raw --v 7
```

**2. 概念插畫 (Niji)**
```
A young witch riding a flying broomstick over a seaside cliff town at
sunset, long coat trailing in the wind, whimsical, soft watercolor wash,
Studio Ghibli inspired --ar 16:9 --niji 7 --s 300
```

**3. 角色一致性 (Omni Reference)**
```
the character, standing in a bustling Tokyo night market, neon signs
reflecting on wet pavement, handheld candid shot, cinematic
--oref https://i.mj.run/my-character.jpg --ow 500 --ar 16:9 --s 200 --v 7
```

**4. 產品 (--raw)**
```
A minimalist ceramic coffee mug on a light oak table, morning sunlight
streaming from the left, soft shadows, clean white background, product
photography, shot on Phase One, 50mm --ar 1:1 --s 50 --raw --v 7
```

## 常見錯誤

- **還在用 --cref 做 v7 角色** → 無效。用 --oref。
- **Stylize 拉到 1000 做寫實** → 矛盾。寫實走 `--raw --s 50`。
- **多個衝突參數** (`--niji 7 --raw`) → raw 和 niji 設計衝突，選一個。
- **prompt 太囉嗦的完整句子** → MJ 喜歡堆疊形容詞；句子只要 1–2 個帶動作。
- **--oref 不加 --ow** → 權重 default 100 通常不夠，角色跑掉。調 300–600。

## 連結

- Style Reference 官方：https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference
- Parameter List 官方：https://docs.midjourney.com/hc/en-us/articles/32859204029709-Parameter-List
- Character Reference 官方 (注意 v7 狀態)：https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference
- Omni Reference 指南 (TitanXT)：https://www.titanxt.io/post/control-your-midjourney-creations-a-guide-to-the-new-omnireference-v7
- V7 完整評測 (promptsref)：https://promptsref.com/guide/In-Depth-Review-of-MidJourney-V7
- 2026 Prompt 指南 (Printify)：https://printify.com/blog/midjourney-prompts/
- Cheatsheet：https://sref-midjourney.com/cheatsheet
- Sref Codes Library：https://midjourneysref.com/
- Sref v7 Deep-dive (geeky curiosity)：https://geekycuriosity.substack.com/p/midjourney-complete-overview-of-the
- --cref 指南 (prompting.systems)：https://prompting.systems/blog/how-to-use-midjourney-cref-for-consistent-characters

---

## 🆕 Midjourney v7 進階功能完整地圖 (2026)

### V7 發布里程碑
- **2025-04-03** v7 alpha release
- **2025-06-17** v7 成為 default
- V7 第一個把 **model personalization 預設開啟** 的版本

### 1. Draft Mode (快速迭代)

- **半價成本 + 10x 速度**
- 適合早期 ideation 快速看方向
- 限制：**Omni Reference (--oref) 不能與 Draft Mode 並用**

### 2. Personalization (`--p` / `--profile`)

- V7 起預設啟用
- 需先解鎖 (約 5 分鐘 rating 過程)：`https://midjourney.com/rank-v7`
- **85% 使用者偏好** personalization 結果
- 解鎖後所有 prompt 自動套個人美感 profile

### 3. Moodboards (新)

- 上傳多張圖組成 moodboard
- 比單張 sref 更全面的風格 reference
- V7 新 sref 演算法精度提升

### 4. Omni Reference (`--oref`) 完整限制

Omni Reference 把特定「東西」放進新圖。但 **不相容：**
- ❌ Fast Mode
- ❌ Draft Mode
- ❌ Conversational Mode
- ❌ `--q 4`

實務：要用 --oref 記得關 Draft/Fast/Conversational，品質參數用 `--q 1` 或 `--q 2`。

### 5. V7 Web UI Alpha (新介面)

- 右側 panel：settings / image references / Personalization profiles / moodboards / grid view
- 比 V6 更快
- Imagine bar 上方即時 preview

### 6. Multi-sref 加權組合

```
prompt words --sref 1234567890 9876543210 5555555555
```
三個 sref 平均權重 (組合新風格)。

### 7. 進階工作流範例

**Storyboard 角色一致性：**
```
Step 1: --oref CHARACTER.jpg --ow 500 (主角一張 reference)
Step 2: 每個 prompt 用同 --oref 生不同場景/姿勢
Step 3: 角色跨圖一致，場景隨 prompt 變
```

**風格探索：**
```
Step 1: Draft Mode 快速 brainstorm 20 版 (省錢)
Step 2: 挑最好的 → 升級 Standard 重生成
Step 3: 用該版 sref code 當風格錨
```

### 8. 新 API (V7)

V7 支援 API 存取 (需訂閱 Pro +)。可以程式化批次：
- `POST /imagine` 提交 prompt
- `GET /status` 查進度
- 批次大規模生成適合廣告 / 素材庫
