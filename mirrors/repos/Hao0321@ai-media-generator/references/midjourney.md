# Midjourney (V7 default · V8.1 latest · niji 7 · V1 Video)

官網 `https://midjourney.com/`。Discord + Web UI 並行。美感預設值最高的圖像模型。

> **2026-06 版本現況（重要，先讀）**
> - **V7** = 目前**預設**模型（2025-06-17 起）。`--oref` Omni Reference **只在 V7**。
> - **V8.0 Alpha** 2026-03-17 上 `alpha.midjourney.com`；**V8.1** 2026-04-30 上 `midjourney.com` + Discord = **最快、最新**模型。V8 主打 `--hd` 原生 2K、`--q 4`、新 sref 版 `--sv 7`。
> - **niji 7** 2026-01-09 發布（動漫分支），加入 Personalization + Moodboards。
> - **V1 Video** = 獨立影片模型，把任何 MJ 靜圖「Animate」成 5s 影片（可延長至 20s）。V7/V8 本身是**圖像**模型，影片靠 V1。
>
> **選版心法：** 要角色一致性（`--oref`）→ 鎖 **V7**。要最高畫質/速度/2K → **V8.1**。要動漫 → **niji 7**。要動起來 → 先出圖再 **V1 Video Animate**。

---

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

**Token 經濟學：** prompt 是 keyword stack 不是作文。30–60 字 token-stack 最佳，超過會稀釋焦點。每個逗號是一個「美感槽位」，動作句最多 1–2 句。

---

## 核心參數矩陣

| 參數 | 範圍 / 預設 | 說明 | 版本 |
|---|---|---|---|
| `--ar W:H` | — | Aspect ratio，如 16:9, 9:16, 1:1, 21:9, 4:5 | 全 |
| `--s` (stylize) | 0–1000，default 100 | 越高越風格化，越低越貼 prompt | 全 |
| `--c` (chaos) | 0–100 | 4 張之間的變異度（構圖發散） | 全 |
| `--weird` | 0–3000 | 奇異度，比 chaos 更「怪」的非典型美學 | 全 |
| `--exp` | 0–100 | Experimental aesthetics，加電影感/細節密度（會與 oref 競爭） | V7 / V8 |
| `--sref <code/URL>` | — | Style Reference（整體美感，見下） | 全 |
| `--sw` (style weight) | 0–1000，default 100 | `--sref` 的強度。太弱拉 150–300 | 全 |
| `--sv` (sref version) | 1–7 | sref 子版本。V7 default `--sv 6`；**V8 default `--sv 7`**（4x 快/省） | 全 |
| `--oref <URL>` | — | Omni Reference（把特定東西放進圖） | **V7 only** |
| `--ow` (omni weight) | 0–1000，default 100 | `--oref` 強度。換風格用 25，鎖臉/服裝用 400 | **V7 only** |
| `--cref <URL>` | — | Character Reference（舊版角色一致性） | **V6 / niji；V7 失效** |
| `--cw` (char weight) | 0–100，default 100 | `--cref` 強度。100=臉+髮+衣，0=只鎖臉 | V6 / niji |
| `--p` / `--profile <code>` | — | Personalization（需先 rank ~40–200 張解鎖） | 全 |
| `--hd` | flag | 原生 2K 渲染，免 upscale（3x 快、3x 便宜版本） | **V8** |
| `--q` (quality) | .25 / .5 / 1 / 2 / 4 | GPU 用量。`--q 4` 加 coherence（與 oref 不相容） | 全 |
| `--raw` | flag | Raw mode，減少 MJ 自動美化 | 全 |
| `--tile` | flag | 可拼接 tile 圖（紋理/底圖） | 全 |
| `--stop` | 10–100 | 中途停止渲染（朦朧/草稿效果） | 全 |
| `--no <元素>` | — | 負面提示（取代 negative prompt），逗號分隔 | 全 |
| `--seed <num>` | — | 固定 seed（重現/微調同構圖） | 全 |
| `--niji 7` | flag | 切換 niji 動漫分支 | — |
| `--v 7` / `--v 8` | flag | 指定版本（V7 為當前 default） | — |

### 參數順序 & 慣例
參數**永遠放 prompt 最後**。多個 `--no` 用逗號：`--no text, watermark, extra fingers`。
Multi-prompt（`::`）、permutations（`{}`）寫在主體部分。

---

## Style Reference (`--sref` + `--sw`)

抓 **整體美感 / 氛圍**（顏色、質感、光影、媒材），**不複製物件**。這是品牌視覺一致性的主力槓桿。

**三種寫法：**
1. **Code**：`--sref 1234567890`（MJ 內建風格庫，數字碼可收藏/重用）
2. **URL**：`--sref https://...jpg`（自己上傳的圖當風格錨）
3. **Random**：`--sref random`（隨機抽一個，記下喜歡的 code 收藏）

**強度調控（`--sw`）：** default 100。
- 風格沒吃進去 → 拉 `--sw 250`–`--sw 500`
- 風格蓋過主體 → 降 `--sw 50`
- 純粹借色票/光氛、不要構圖味 → `--sw 25`–`--sw 50`

**Style Reference 版本（`--sv`）**
- V7 有多個 sref 子版本，default `--sv 6`。
- **V8 引入 `--sv 7`**：4x 更快、4x 更便宜，支援 `--hd / --p / --stylize / --exp`，對 SREF + Moodboards + HD 銳利度提升。
- 舊 sref code 對應特定 sv；換 sv 同一 code 出來的味道會變。

**多重 sref（混風格）：**
```
--sref 111 222 333
```
三個 sref 加權平均，調出全新混血風格。可搭 `--sw` 統一壓強度。
（進階：個別加權目前需用多 sref 平均近似 — 精細個別權重 **待驗證**。）

---

## Omni Reference (`--oref` + `--ow`) — **V7 限定**

**把特定「東西」放進新圖**（角色、物件、重複元素、產品）。取代已棄用的 `--cref`。

**寫法：**
```
prompt words --oref https://.../character.jpg --ow 400 --v 7
```

**`--ow` 權重邏輯（0–1000，default 100）：**
| 目標 | --ow | 說明 |
|---|---|---|
| 換畫風（照片→動漫） | 25 | 低權重讓風格自由跑，只留輪廓神韻 |
| 一般場景換、保人物 | 100–200 | default 起跳，通常不夠 |
| **鎖臉 / 鎖服裝** | 300–500 | 角色跨圖一致的甜蜜點 |
| 幾乎照搬 ref | 600+ | 構圖也會被綁，慎用 |

**關鍵互動：** `--stylize` 和 `--exp` 會**與 oref 競爭影響力**。stylize/exp 拉高時，`--ow` 要**同步拉高**，否則風格會把角色洗掉。

**多物件：** 把多個角色/物件放在**同一張** ref 圖（並排），prompt 裡分別提到。多 URL 疊加仍**「somewhat untested」**（官方語），效果不穩 → **待驗證**。

**成本與限制：**
- 用 `--oref` 約 **2x GPU 時間**。
- **不相容：** ❌ V8（V7 only）❌ Fast Mode ❌ Draft Mode ❌ Conversational Mode ❌ `--q 4`。
- 實務：要 oref 就鎖 V7、關 Draft/Fast/Conversational、品質用 `--q 1` 或 `--q 2`。

> **v7 重要變更：** `--cref` 在 V7 **已失效**（被忽略或報錯）。V7 角色一律改 `--oref`。
> `--cref` / `--cw` 仍能在 **V6 與 niji** 用。

---

## Personalization (`--p` / `--profile`)

到 `https://midjourney.com/rank-v7` 評圖解鎖個人美感 profile（約 5 分鐘 rating；解鎖門檻官方說法在 ~40–200 張間浮動 — 確切數字 **待驗證**）。

- **V7 起預設啟用** — 解鎖後所有 prompt 自動套你的偏好。
- 約 **85% 使用者偏好** personalization 後的結果（官方數據）。
- **V8 向後相容** V7 的 personalization profiles / moodboards / srefs，免重練。
- 多個 profile 可命名切換；`--p <code>` 指定特定 profile。
- 暫時想看「中性」結果 → 在 prompt 加 `--p 0` 或關掉 profile 開關。

---

## Moodboards（風格板）

上傳**多張圖**組成具名 moodboard，比單張 sref 更全面、穩定的風格 reference。

- 適合**品牌風格固化**：把品牌既有素材丟進一個 moodboard，之後所有 prompt 引用同一板 → 跨圖視覺 DNA 一致。
- V8 `--sv 7` 對 moodboard 銳利度有提升。
- niji 7 也已支援 moodboard。
- Moodboard 與 `--sref` 可疊用，但會互相拉扯味道，建議**擇一主導**、另一個壓低權重。

---

## Draft Mode（快速迭代）

`--draft` 加在任何 prompt 後。

- **約 1/10 成本、5–10x 速度**，畫質較粗 = 「rough concept」非成品。
- 標準流程：**狂出 10–20 張 draft 探方向** → 挑最好的 → promote 成 full-quality standard 重生成。
- **限制：** Draft Mode **不能與 `--oref` 並用**（要角色一致就別用 Draft）。

---

## V1 Video Model（圖生影片）

MJ 第一個影片模型（2026 上線）。工作流叫 **Image-to-Video**：先在 MJ 正常出圖 → 按 **Animate** 讓它動。

- 預設 **5 秒**片段，**可 5 秒一段延長到最長 20 秒**。
- **Auto** vs **Manual** animate：manual 可寫「怎麼動 / 場景如何發展」的動態 prompt。
- **High motion** / **Low motion** 兩檔運動強度。
- 任何 MJ 靜圖（含 V7/V8/niji 出的圖）都能 Animate。
- 定位：對標 Veo / Kling / Sora 的入門級 i2v，勝在跟 MJ 美感無縫接軌。
- 進階運鏡語彙 / extend 細節 **待驗證**（建議實測後補）。

---

## Image Weight — Multi-prompt (`::`)

用 `::` 拆分多個子 prompt，加權：
```
cat::2 dog::1 watercolor::3 --ar 1:1
```
代表貓權重 2、狗 1、水彩風格 3。
（Image prompts + image weights 在 **V8.1** 才回歸支援。）

## Permutations — 一次多版本 (`{}`)

用 `{}` 列舉，MJ 跑所有組合：
```
A {cat, dog, rabbit} in a {forest, desert} --ar 1:1
```
→ 6 張圖。適合批次 A/B 風格/構圖測試（注意吃 GPU 額度）。

---

## Raw Mode (`--raw`)

關掉 MJ 預設「美化偏好」，輸出更貼 prompt 字面。用於：
- 不想要過度飽和 / 電影化
- 模仿真實攝影、product 攝影
- 要對 prompt 有更精準控制時

寫實配方：`--raw --s 50`（低 stylize + raw 是寫實鐵則）。

---

## Niji 7（動漫分支）

`--niji 7` 切到動漫分支（2026-01-09 發布）。

- **更高 coherency**：眼睛、反光、背景小物更清晰。
- **更扁平的 line-art 渲染**，貼近真實動畫產線質感。
- **更字面**的 prompt understanding。
- sref 表現提升，且**已支援 Personalization + Moodboards**。

適合：日系動畫、插畫風角色設計、漫畫分格。
風格 token：`shoujo`, `shonen`, `ghibli`, `scenic`, `cute`, `expressive`。
（niji 角色一致性仍可用 `--cref` + `--cw`，與 V7 主線的 `--oref` 不同 — 別搞混。）

---

## V6 / V7 / V8 / niji 7 能力對照

| 項目 | V6 | V7（default） | V8.1（latest） | niji 7 |
|---|---|---|---|---|
| 角色一致性 | `--cref`/`--cw` | **`--oref`/`--ow`** | ❌ 無 oref（待補） | `--cref`/`--cw` |
| Personalization | 次要 | **預設強化** | 相容 V7 profile | 已支援 |
| Moodboards | 有 | 有 | `--sv 7` 加強 | 已支援 |
| 寫實度 | 中 | 高 | **最高** | （動漫向）|
| 速度 | 中 | 快 | **最快（~5x）** | 快 |
| 2K 原生 | 否 | 否 | **`--hd`** | 否 |
| Text rendering | 差 | 好不少 | **更好** | 好 |
| sref 預設版本 | — | `--sv 6` | **`--sv 7`** | 提升 |
| Draft Mode | 否 | **有** | 有 | 待驗證 |

> **取捨重點：** V8.1 畫質/速度/2K 領先，但 **`--oref` 角色一致性目前仍要回 V7**。做 IP/角色系列 = V7 主力；做單張高質感 keyvisual = V8.1。

---

## 進階 Recipe

### Recipe A — 品牌視覺一致性系列（Moodboard + sref 鎖風格）
目標：同一品牌調性，產出多張一致的行銷圖。
```
Step 1  建一個具名 Moodboard，丟入品牌既有 3–6 張素材（色、光、質感代表作）
Step 2  生一張理想風格圖 → 收藏它的 --sref code（或直接用 moodboard）
Step 3  所有後續 prompt 固定帶同一風格錨：
        <new subject> --sref <code> --sw 150 --ar 4:5 --v 8.1 --hd
Step 4  風格漂移就調 --sw（弱→拉高、太黏→降低），主體只換 keyword
```
產出：跨圖共享色票 / 光氛 / 媒材，但主體自由變 → 品牌 DNA 穩定。

### Recipe B — 角色多場景（V7 Omni Reference 角色聖經）
目標：同一角色出現在不同場景 / 姿勢 / 鏡頭（漫畫、分鏡、廣告 campaign）。
```
Step 1  出一張乾淨的角色定裝照（正面、清楚臉+服裝）→ 拿到 i.mj.run URL
Step 2  鎖 V7（oref V7 only），關 Draft/Fast/Conversational
Step 3  每個場景同一 oref，只換場景描述：
        <角色> in <場景A>, <鏡頭/光>
        --oref https://i.mj.run/CHAR.jpg --ow 400 --ar 16:9 --s 200 --v 7
Step 4  臉跑掉→--ow 拉到 450–500；風格被洗掉→stylize/ow 同步調
Step 5  要動 → 把最佳幀丟 V1 Video Animate（low motion 保臉）
```
產出：角色跨圖一致，場景隨 prompt 變。stylize 高就記得同步抬 `--ow`。

### Recipe C — 風格探索 → 量產（Draft 省錢漏斗）
目標：低成本找對方向，再高質感量產。
```
Step 1  Draft Mode 狂掃 15–20 版探構圖/風格（~1/10 成本）
        <concept variants> --draft --ar 16:9
Step 2  挑最佳方向 → 記下其 seed / sref
Step 3  關 Draft，用 V8.1 重生成高質感：
        <winner prompt> --sref <code> --sw 150 --hd --ar 16:9 --v 8.1
Step 4  要 4K 級 → --hd 已原生 2K，再走 upscale
```
注意：Draft **不能**跟 `--oref` 並用 → 角色系列改走 Recipe B。

### Recipe D — 寫實產品攝影（Raw 低 stylize）
```
A minimalist ceramic coffee mug on a light oak table, morning sunlight
streaming from the left, soft shadows, clean white background, product
photography, shot on Phase One, 50mm
--ar 1:1 --s 50 --raw --hd --v 8.1
```
鐵則：`--raw --s 50` + 攝影器材/鏡頭 token（Phase One / 50mm / softbox）。

---

## 速查範例

**1. 攝影寫實（V8.1 + hd）**
```
Portrait of a weather-beaten sailor in his 60s, deep wrinkles, piercing blue
eyes, wearing a knit wool sweater, against a foggy harbor background, shot on
Leica M6, Kodak Portra 400, soft natural window light, 85mm lens, shallow
depth of field --ar 4:5 --s 150 --raw --hd --v 8.1
```

**2. 概念插畫（niji 7）**
```
A young witch riding a flying broomstick over a seaside cliff town at
sunset, long coat trailing in the wind, whimsical, soft watercolor wash,
scenic --ar 16:9 --niji 7 --s 300
```

**3. 角色一致性（V7 Omni Reference）**
```
the character, standing in a bustling Tokyo night market, neon signs
reflecting on wet pavement, handheld candid shot, cinematic
--oref https://i.mj.run/my-character.jpg --ow 450 --ar 16:9 --s 200 --v 7
```

**4. 產品（Raw）**
```
A minimalist ceramic coffee mug on a light oak table, morning sunlight
streaming from the left, soft shadows, clean white background, product
photography, shot on Phase One, 50mm --ar 1:1 --s 50 --raw --v 8.1
```

---

## 常見失敗 + 修法

| 症狀 | 原因 | 修法 |
|---|---|---|
| `--cref` 在 V7 無效 | V7 已棄用 cref | 改 `--oref` + `--ow`；或回 V6/niji 才用 cref |
| `--oref` 在 V8 沒反應 | **oref 是 V7-only** | 加 `--v 7` 鎖 V7；要 V8 畫質就別用 oref 做角色 |
| 角色每張臉都跑掉 | `--ow` 太低（default 100 不夠） | 拉 `--ow 350–500`，鎖臉/服裝 |
| stylize 拉高後角色被洗掉 | stylize/exp 與 oref 競爭 | `--ow` 與 `--s`/`--exp` **同步拉高** |
| `--oref` 怎樣都不出 | 跟 Draft/Fast/Conversational/`--q 4` 衝突 | 關掉這些模式，`--q 1`/`--q 2` |
| Draft 出不來角色系列 | Draft 不相容 oref | 角色系列別用 Draft，走 V7 標準（Recipe B） |
| sref 風格吃不進去 | `--sw` 太低 | 拉 `--sw 250–500` |
| 換了 `--sv` 同 code 變味 | sref code 綁特定 sv 版本 | 固定一個 `--sv`（V7→6，V8→7）再比較 |
| Stylize 1000 做寫實但很假 | 高 stylize 與寫實矛盾 | 寫實走 `--raw --s 50` |
| `--niji 7 --raw` 結果怪 | raw 與 niji 美學設計衝突 | 二選一，別混 |
| prompt 寫成長句卻很糊 | MJ 要 keyword stack 非作文 | 改逗號分隔形容詞堆疊，動作句 ≤1–2 |
| 想要 2K 卻一直要 upscale | 沒開 `--hd` | V8 加 `--hd` 原生 2K |

---

## 連結

**官方文件（authoritative）**
- Version（各版本現況）：https://docs.midjourney.com/hc/en-us/articles/32199405667853-Version
- Parameter List：https://docs.midjourney.com/hc/en-us/articles/32859204029709-Parameter-List
- Style Reference：https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference
- Omni Reference：https://docs.midjourney.com/hc/en-us/articles/36285124473997-Omni-Reference
- Character Reference（注意 V7 失效）：https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference
- Video（V1）：https://docs.midjourney.com/hc/en-us/articles/37460773864589-Video

**官方更新公告（primary）**
- V8 Alpha：https://updates.midjourney.com/v8-alpha/
- Omni-Reference --oref：https://updates.midjourney.com/omni-reference-oref/
- niji V7：https://updates.midjourney.com/niji-v7/
- V1 Video Model：https://updates.midjourney.com/introducing-our-v1-video-model/
- 更新總頁：https://www.midjourney.com/updates

**社群指南 / 深度評測**
- Omni Reference 指南（TitanXT）：https://www.titanxt.io/post/control-your-midjourney-creations-a-guide-to-the-new-omnireference-v7
- V8 vs V7 比較（MindStudio）：https://www.mindstudio.ai/blog/midjourney-v8-vs-v7-comparison
- V8 prompting（Blake Crosley）：https://blakecrosley.com/blog/midjourney-v8-prompting
- V8 alpha sref v7 實測（geeky curiosity）：https://geekycuriosity.substack.com/p/midjourney-v8-alpha-the-new-style
- Draft Mode 指南（promptsref）：https://promptsref.com/guide/Exploring-MidJourney-Draft-Mode
- 角色一致性 2026（Medium / Pijush Saha）：https://medium.com/@impijushsaha/how-to-create-consistent-characters-in-midjourney-the-complete-guide-for-2026-405c3bfbb4e1
- niji 7 動畫工作流（DomoAI）：https://domoai.app/blog/niji-7-guide-animate-ai-anime
- Sref Codes Library：https://midjourneysref.com/
- Cheatsheet：https://sref-midjourney.com/cheatsheet
- 2026 Prompt 指南（Printify）：https://printify.com/blog/midjourney-prompts/

---

## 🆕 V7 / V8 進階功能地圖（2026）

### 發布里程碑
- **2025-04-03** V7 alpha
- **2025-06-17** V7 成為 default（第一個 model personalization 預設開啟的版本）
- **2026-01-09** niji 7
- **2026-03-17** V8.0 Alpha（alpha.midjourney.com）
- **2026-04-30** V8.1（midjourney.com + Discord）= 最快模型
- **2026 Q2** V1 Video（Image-to-Video Animate）

### V8 重點（為何升級）
- `--hd`：原生 2K，免 upscale（HD 模式 3x 快、3x 便宜）；標準解析度也 50% 快、25% 便宜。
- `--q 4`：額外 coherence 模式。
- `--sv 7`：新 sref/moodboard 預設版本，4x 快/省，支援 `--hd / --p / --stylize / --exp`，SREF + Moodboards + HD 銳利度提升。
- 向後相容 V7 的 personalization / moodboards / srefs。
- 多 aspect ratio、`--chaos / --weird / --exp / --raw` 支援；**image prompts + image weights 在 V8.1 回歸**。
- 初期 **Relax 模式尚未支援**（之後可能補 — **待驗證**）。
- ⚠️ **V8 目前不支援 `--oref`**：角色一致性仍須回 V7。

### V7 仍不可取代之處
- **Omni Reference（`--oref` / `--ow`）= V7 獨佔**，角色/物件跨圖一致性的最強工具。
- **Draft Mode** 省錢漏斗（V8 也有，但 oref 系列只能 V7 標準）。

### Web UI（Alpha 介面）
- 右側 panel：settings / image references / Personalization profiles / moodboards / grid view。
- Imagine bar 上方即時 preview。比舊版快。

### API（V7+）
需訂閱 Pro+。可程式化批次：`POST /imagine` 提交、`GET /status` 查進度。適合廣告 / 素材庫大規模生成。
（V8 的 API 開放時程 / 端點差異 **待驗證**。）
