# Runway — Gen-4.5 / Gen-4 / Aleph / Act-Two

官網 `https://runwayml.com/` ・ App `https://app.runwayml.com/`。好萊塢等級工作流，定位是 **AI video studio**（生成 + 編輯 + 表演捕捉一條龍），不是單純的 t2v 玩具。

2026 時點主力 **Gen-4.5**（2025-12-01 發布，Artificial Analysis t2v 榜首 1247 Elo，超過 Veo 3 與 Sora 2 Pro）。下面四個核心模組要分清楚用途：

| 模組 | 本質 | 何時用 |
|---|---|---|
| **Gen-4.5 / Gen-4 Video** | 主力 t2v / i2v 生成 | 從零生成新片段 |
| **Gen-4 References** | 最多 3 張參考圖的一致性生成 | 同角色/物件/場景跨鏡頭 |
| **Aleph** | video-to-video 編輯模型 | 改既有影片（加/減/換/重打光/改視角/換風格） |
| **Act-Two** | performance capture / 表情口型驅動 | 讓角色「演」你錄的表演 |
| **Keyframes** | 首/中/尾幀補間 | 轉場、史詩揭示、精確始末狀態 |

> 心智模型：**Gen-4.5 生「主鏡」→ Aleph 做「後期 VFX/改視角」→ Act-Two 補「表演/對口型」→ Keyframes 接「轉場」**。這條 pipeline 才是 Runway 真正的賣點，單看 t2v 它不一定贏 Veo/Kling。

---

## Gen-4.5 / Gen-4 系列能力矩陣

| | **Gen-4 Turbo** | **Gen-4** | **Gen-4.5** |
|---|---|---|---|
| 發布 | 2025-04 | 2025-03 | **2025-12-01** |
| 定位 | 最快最便宜 | 平衡 | **旗艦（最高品質）** |
| 速度 | 10s ≈ 30 秒出片（約 5× Gen-4） | 標準 | 與 Gen-4 相近（無明顯降速） |
| 成本 (video) | **5 credits/s** | **12 credits/s** | **約 25 credits/s** |
| 強項 | 快速迭代、批量、預覽 | 一致性、動作真實感 | 物理準確、prompt 遵循、角色表情、長時序一致性 |
| 時長 | 5s / 10s | 5s / 10s | 最高 10s |
| 模式 | t2v / i2v | t2v / i2v / V2V / Keyframes | t2v 為主；i2v / Keyframes / V2V 陸續開放 (部分待官方確認) |

**架構亮點 (Gen-4.5)：** Autoregressive-to-Diffusion (A2D) — 融合 diffusion 的視覺保真 + autoregressive 的語言/場景理解。實務意義：**複雜多元素 prompt 的遵循度大幅提升**，多角色、多動作的場景比 Gen-4 穩。

**已知短板 (Gen-4.5 官方自承)：** causal reasoning（因果推理）、object permanence（物件恆存）、success bias（高估動作會成功）。→ 對「物件遮擋後再出現」「需要嚴格因果鏈」的鏡頭要多 seed 重試。

**選型決策：**
```
要哪個模型？
├── 快速試 prompt / 跑大量草稿 / 省 credits → Gen-4 Turbo
├── 要最高品質、複雜場景、角色情緒戲 → Gen-4.5
├── 要 V2V 編輯既有影片 → Aleph（不是上面任何一個）
└── 要同角色跨多鏡頭 → 任一生成模型 + Gen-4 References
```

### Prompt 結構

Runway 偏向 **敘事式描述**，不要 tag-heavy（不像 Midjourney 堆關鍵字）：

```
[Subject and context] + [Action] + [Camera] + [Style / Mood]
```

**範例：**
```
A young woman with curly hair sits at a rain-streaked window in a dimly lit
cafe, slowly stirring her coffee as she looks out. Close-up, shallow depth of
field, warm tungsten light from above. Melancholic, cinematic, 35mm film look.
```

### 參數
- 時長：5s / 10s
- 解析度：720p 預設；付費可 **upscale 到 4K**
- Aspect：16:9 / 9:16 / 1:1 / 4:3 / 3:4（21:9 部分模型，待確認）
- FPS：24
- Seed：可固定（重現/微調用）
- Camera Control：UI 預設（pan / tilt / dolly / zoom / roll）+ 強度 slider，比純文字運鏡精準

---

## 進階 Prompt 技巧（Runway 專屬）

### 1. Runway 沒有原生 negative prompt — 三種替代法

Runway **沒有** 獨立 negative 欄位。要排除東西：

1. **句尾 avoid 法**（最常用）：prompt 結尾加 `Avoid: text overlays, warped hands, extra limbs.`
2. **正向改寫**（更有效）：把「不要模糊」→ 寫「sharp focus, crisp detail」。Runway 對**正向描述**的反應遠好於否定句。
3. **換 seed / 重生**：某些 artifact（多指、鬼影）靠語言壓不掉，直接換 seed 比堆 avoid 有用。

> 黃金律：**描述你要的畫面，而不是列舉你不要的東西。** 否定詞在 diffusion 模型常被忽略甚至反效果。

### 2. Gen-4 References 一致性策略

上傳最多 3 張圖當 **character / style / environment** 參考，**用 `@tag` 引用**：

- **打 `@` 會自動補全** reference 名稱 → 直接 `@John is playing guitar`
- **存成跨 session 可複用**：hover 圖片 → 點 tag → 命名 → Enter（之後跨專案都能叫）
- 多 ref 時用一致 label：`image_1` / `image_2` / `image_3`，讓模型知道哪張影響哪裡
- 強化一致性可加片語：`same character`、`maintaining appearance`、`exact features`

**寫法要點（關鍵）：**
- 標記角色：`@hero is the main character, @cafe is the location`
- **描述「動作 + 新元素」，不要重述 ref 的外觀** ← 最常見錯誤
- 一張 ref 圖就能跨不同打光/場景/處理保持角色一致

```
@hero walks into @cafe, sits by the window, and opens a leather journal.
Medium shot, soft window light, warm tones, shallow depth of field.
```

### 3. Aleph 編輯指令寫法

Aleph = 把影片丟進去 + 文字編輯指令 → 輸出改過的影片（V2V，不是 t2v）。

**核心公式：**
```
[動作動詞 add/remove/change/replace/relight/restyle/generate] + [對象] + [新內容/新狀態]
```

**進階寫法（從實測歸納，效果差很多）：**

- **描述「環境如何行為」，不只是「環境是什麼」。**
  弱：`change background to desert`
  強：`make it feel like they're in the middle of a desert sandstorm, with wind and sand whipping around them, dust softening the light`
- **明確鎖定「不要動的東西」**（極重要，減少漂移）：
  `Don't change the subject — keep the face, mouth, and motion exactly the same. Just add...`
- **指定材質 + 氛圍**：`velvet armchair`、`matte finish`、`low-slung fog`、`moody high-contrast`
- **有目標 look 就附 reference 圖**錨定 Aleph 的決策（V2V 也能吃 ref）
- **一次一個改動**，評估後再疊下一個 → 比一次塞多個指令乾淨
- **運鏡先從「接地」的要求開始**：`move the camera two feet to the left` 再進階到大視差

---

## 進階功能地圖

### A. Gen-4 References — 一致性引擎

- **用途**：同一角色/物件/場景跨多個鏡頭保持一致
- **何時用**：做有連續性的故事、角色廣告、系列鏡頭
- **上限**：一次最多 3 張 ref
- **省力點**：1 次 3-ref 生成 比 3 次單獨 chain 省約 60%

### B. Aleph — V2V 編輯（2025-07 發布）

把「拍好/生成好的影片」當素材後製。支援的編輯類別：

| 類別 | 範例指令 |
|---|---|
| 移除 | `remove the car in the background`（自動補背景 + 修陰影/反射） |
| 加入 | `add gently falling snow throughout the scene` |
| 改變/替換 | `change the shirt to navy`、`replace the sky with a stormy sunset` |
| 變材質 | `transform the wooden chair into marble` |
| 重打光 | `relight the scene with warm golden hour light`、`change to midnight, neon purple and cyan` |
| 換天氣/季節 | `turn summer into winter with light snow` |
| 換環境 | `replace the room with an outdoor garden` |
| **生成新視角** | `create a reverse shot showing the opposite angle`（保持光線/背景連續） |
| **生成下一鏡** | `generate the next shot continuing the action` |
| 換風格 | `restyle in Studio Ghibli animation, hand-painted backgrounds` |

- **何時用**：要 VFX 但不想開 After Effects、要補拍對話的反打、要改天氣/打光救素材
- **最佳輸入**：乾淨打光（避免混色溫/閃爍）、前景背景分離清楚的素材，編輯成功率高
- **5s 片段 + 4K upscale** 是常見 VFX 工作流

### C. Act-Two — Performance Capture（2025-07 發布）

- **用途**：免 mocap 設備，用手機錄自己表演（臉、頭、身體、手），驅動任意角色
- **輸入**：driving performance video（任何相機，含手機）+ character reference（**圖** 或 **影片**）
- **追蹤**：head / face / body / hands
- **關鍵限制 — gesture（身體姿態）控制：**
  - **character 是「圖」→ gesture toggle 可開**（身體動作來自你的表演）
  - **character 是「影片」→ gesture 不可用**（身體動作由該影片本身決定，Act-Two 只套臉部+環境動態）
  - toggle 關閉時 → 只加臉部 + 環境動態
- **多角色對話**：支援（見官方 Multi-Character Dialogues 文件）
- **何時用**：對口型、角色獨白、把真人演技轉到動畫/虛擬角色上
- **Prompt 角色次要**：輸出由 driver 影片主導，prompt 只描述場景 + 燈光

### D. Keyframes — 首/中/尾幀補間

- **用途**：給定 **起始幀 / 中間幀 / 結束幀**，模型補出之間的平滑過渡
- **何時用**：轉場、變身/揭示、需要精確控制始末狀態的鏡頭
- **訣竅**：首尾差異大 → 選 **10s**（給模型更多時間平滑過渡）；選 5s 會比較突兀（也可故意用來做 abrupt cut）
- 註：Keyframes 文件目前多掛在 Gen-3 Alpha Turbo 下，Gen-4/4.5 的 Keyframes 支援陸續開放 (待官方確認完整對應)

---

## 進階 Recipe

### Recipe 1 — 角色一致的故事短片（References → 生成 → Aleph 補鏡）

```
Step 1. Gen-4 References：上傳 @hero（角色圖）+ @lab（場景圖）
        Prompt: "@hero walks through @lab, examining glowing vials.
        Tracking shot, cool clinical lighting, shallow depth of field."
        → 出 10s 主鏡
Step 2. Aleph（餵 Step 1 影片）：
        "generate a reverse shot showing @hero's face reacting,
         keep lighting and background consistent."
        → 出反打
Step 3.（若要對白）Act-Two：手機錄自己唸台詞 + 用 @hero 當 character image
        gesture toggle 開 → 角色完整演出
```
這條 = 好萊塢等級工作流：一致角色 + 多視角 + 表演，全程不開傳統剪輯軟體。

### Recipe 2 — 單素材 VFX 變形（i2v → Aleph 疊環境）

```
Step 1. Gen-4 Turbo i2v：一張人像 → 生 5s 自然動態（省 credits 先試）
Step 2. Aleph 第一層（鎖主體）：
        "Don't change the subject — keep face, mouth, motion exactly.
         Add a desert sandstorm: wind and sand whipping around them,
         dust softening the light, hair reacting to wind."
Step 3. Aleph 第二層（評估後再疊）：
        "relight with warm low-angle sun breaking through the dust."
Step 4. 4K upscale 輸出
```
重點：**Aleph 一次一層**，鎖死「subject 不變」是減少漂移的關鍵句。

### Recipe 3 — Keyframes 史詩揭示轉場

```
First frame:  緊閉的巨大石門特寫（你用 Gen-4 Image 生）
Last frame:   門後神殿全景，光束灑落
Prompt:       "The massive stone doors slowly grind open, revealing the
              temple beyond, dramatic god rays piercing through dust.
              Slow dolly-in, epic, cinematic."
Duration:     10s（首尾差異大，給足過渡時間）
```

---

## 模式速查

| 模式 | 說明 | 主力模型 |
|---|---|---|
| **T2V** | 文字生影片 | Gen-4.5 / Gen-4 / Turbo |
| **I2V** | 首幀 + prompt | Gen-4 / Turbo（4.5 陸續） |
| **References** | 1-3 張 ref 一致性 | Gen-4 References |
| **V2V (Aleph)** | 影片 → 編輯後影片 | Aleph |
| **Act-Two** | 表演驅動角色 | Act-Two |
| **Keyframes** | 首/中/尾幀補間 | Gen-3 Turbo（Gen-4 陸續） |

---

## 付費結構（2026）

| Plan | 月費 | 月 credits | 適用 |
|---|---|---|---|
| Free | $0 | 125（一次性） | 試水溫 |
| **Standard** | $12 / 人 | 625 | 輕量個人 |
| **Pro** | $28 / 人 | 2,250 | 主力創作者 |
| **Unlimited** | $76 / 人 | 2,250（express 快線）+ 無限「relaxed」慢線 + Explore Mode | 重度量產 |
| Enterprise | 客製 | — | 團隊 |

**credits 換算（影片）：** Gen-4 Turbo 5cr/s ・ Gen-4 12cr/s ・ Gen-4.5 約 25cr/s。
- 625 credits ≈ 25s Gen-4.5 ／ 52s Gen-4 ／ 125s Gen-4 Turbo
- 2,250 credits ≈ 90s Gen-4.5 ／ 187s Gen-4

> **Unlimited 的真相**：2,250 是「快線」配額，用完後仍可無限生成但走 **relaxed（慢佇列）**；Explore Mode 是無限慢線專供試錯迭代。重度迭代選 Unlimited，但別期待都跑快線。

---

## 中文支援

- 視覺理解中式場景 OK（漢字招牌、中式服裝、建築）
- **prompt 建議用英文**：Runway 的 prompt 遵循、運鏡詞、風格詞都以英文最準
- 無原生音訊 → 中文對白問題不存在（要對白走 Veo 3 / Kling）

---

## 常見失敗 + 修法

| 症狀 | 原因 | 修法 |
|---|---|---|
| **Aleph 改動很亂/主體跑掉** | 一次塞太多指令、沒鎖主體 | 一次一個改動；加 `Don't change the subject — keep face/motion exactly` |
| **Aleph 換環境很空洞** | 只寫「change to X」 | 描述「環境如何行為」（風、粒子、光、與主體互動） |
| **Gen-4 Refs 角色不像** | prompt 又長篇重述外觀，跟 ref 打架 | 只寫動作+新元素，外觀交給 ref；加 `same character` |
| **負面詞無效（還是出現不要的東西）** | Runway 無 negative 欄位，否定句被忽略 | 改正向描述；或換 seed 重生 |
| **物件遮擋後消失/變形** | Gen-4.5 object permanence 短板 | 換 seed 多試；避免複雜遮擋編排 |
| **Act-Two 身體不動只有臉** | 用了 character「影片」→ gesture 不可用 | 改用 character「圖」並開 gesture toggle |
| **Keyframes 轉場太突兀** | 首尾差異大卻選 5s | 改 10s 給足過渡時間 |
| **用 Midjourney 參數（--ar --s --v）** | Runway 吃不到 | 全用 UI 欄位設定 |
| **期待原生音訊** | Runway 無原生音訊 | 走 Veo 3 / Kling，或後期配音 |
| **複雜因果劇情演不出** | causal reasoning 短板 | 拆成多個簡單鏡頭分別生，再 Aleph 接 |

### Runway 不支援什麼
- 原生音訊（要走 Veo / Kling / Sora，或後期）
- 原生 negative prompt 欄位（句尾 avoid 或正向改寫）
- 預設直出 4K（720p 預設 → upscale）
- 嚴格因果/物件恆存（Gen-4.5 自承短板）

---

## 連結

**官方：**
- 官網：https://runwayml.com/
- App：https://app.runwayml.com/
- 定價：https://runwayml.com/pricing
- Changelog：https://runwayml.com/changelog
- Research / Gen-4.5：https://runwayml.com/research/introducing-runway-gen-4.5
- Research / Gen-4：https://runwayml.com/research/introducing-runway-gen-4
- Research 總覽：https://runwayml.com/research

**官方教學（Help Center / Academy）：**
- Creating with Gen-4 Video：https://help.runwayml.com/hc/en-us/articles/37327109429011-Creating-with-Gen-4-Video
- Creating with Gen-4 Image References：https://help.runwayml.com/hc/en-us/articles/40042718905875-Creating-with-Gen-4-Image-References
- Aleph Prompting Guide：https://help.runwayml.com/hc/en-us/articles/43277392678803-Aleph-Prompting-Guide
- Creating with Aleph：https://help.runwayml.com/hc/en-us/articles/43176400374419-Creating-with-Aleph
- Aleph + Reference Image：https://help.runwayml.com/hc/en-us/articles/44609246167059-Controlling-Aleph-edits-with-a-Reference-Image
- Performance Capture with Act-Two：https://help.runwayml.com/hc/en-us/articles/42311337895827-Performance-Capture-with-Act-Two
- Act-Two 多角色對話：https://help.runwayml.com/hc/en-us/articles/41748090660499-Creating-Multi-Character-Dialogues-with-Act-Two
- Creating with Keyframes：https://help.runwayml.com/hc/en-us/articles/34170748696595-Creating-with-Keyframes
- How do credits work：https://help.runwayml.com/hc/en-us/articles/15124877443219-How-do-credits-work
- Gen-4 section 總覽：https://help.runwayml.com/hc/en-us/sections/39888423025683-Gen-4
- Runway Academy：https://academy.runwayml.com/ways-to-use-runway
- Academy / Aleph 影片轉換：https://academy.runwayml.com/tutorial/how-to-transform-videos

---

## 版本與更新紀錄

- 2025-03：Gen-4 發布（一致性、動作真實感大躍進）
- 2025-04：Gen-4 Turbo（約 5× 速度、最低 credit 成本）
- 2025-07：Aleph（V2V 編輯）+ Act-Two（performance capture）發布
- **2025-12-01：Gen-4.5 發布** — A2D 架構，Artificial Analysis t2v 榜首 1247 Elo（超越 Veo 3 / Sora 2 Pro）
- 2026-06-05：本檔升級到進階水準（加入 Gen-4.5、能力矩陣、Aleph/References 進階寫法、功能地圖、3 recipe、失敗修法表、2026 定價）

> 註：標 **(待確認)** 的項目（Gen-4.5 各模式逐步開放狀態、21:9 支援、Keyframes 對 Gen-4 的完整對應）以實際操作 app 或官方 changelog 為準。早前版本提到的「Motion Brush 3.0 / 原生 3D Asset Integration」缺乏官方一手來源佐證，本次升級暫不納入正文，待 app 實測或官方文件確認後再補。
