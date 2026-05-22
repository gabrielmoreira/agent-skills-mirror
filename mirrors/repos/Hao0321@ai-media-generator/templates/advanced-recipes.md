# Advanced Recipes — 多步驟進階工作流食譜

**定位：** 單次生成不夠時的「chain workflow」— 把多個進階功能串起來完成大任務。Auto-Pilot 偵測到使用者需求複雜，就來這找 recipe。

**使用方式：** 使用者說「做個 X」，Auto-Pilot 先查這個檔看有無對應 recipe。有 → 直接 chain；無 → 退回單平台單次生成。

---

## ⚡ Chain Workflow 鐵則 (跑任何 recipe 前先讀)

**所有 recipe 都是 chain，2026-04-20 慘痛教訓：5 task chain 不照辦會浪費 70% token + 3 倍時間。**

| 鐵則 | 違反代價 |
|---|---|
| 中間禁 screenshot (只首尾各 1 張) | 1.5k token / 張 × N |
| 中間禁 TodoWrite (chain 完成後一次更新) | 300 token × N |
| Clear field 用 1-click (trash icon / ctrl+a) 不要 3 步 | 3 calls × N |
| 標準長度，不超寫 (Suno 25 行 / Veo 80 字 / MJ 30-50 字 / Seedream 80-120 字) | 2x type 量 |
| **平台有內建批次 → 優先用** (Suno Persona / Kling Multi-Shot / Seedream Series / MJ omni-ref / Vidu Q3) | 比 N 次 chain 省 60-80% |

**預算檢測：** N task chain 應 ≤ 7N tool calls + ≤ 1.5k token + < N 分鐘。違反任一就要修。

完整論述見 [token-efficient-mode.md §策略 8](token-efficient-mode.md) + [click-protocol.md §「Token + 時間最佳化」](../automation/click-protocol.md)。

---

## 🎬 影片類 Recipe

### R1: 30 秒對白短劇 (超越單平台 8-15s 限制)

**使用者需求：** 「做一個 30 秒的對白場景」「兩個人的對話戲」

**Chain：**
1. **Veo 3.1 Fast** 生第 1 段 8s (hook 建立人物 + 開場對白)
2. **Veo 3.1 Extend** × 3 次 (每次基於前段最後 1 秒續，累積到 30s+)
3. 每次 Extend 的 prompt：`Continue from previous scene, camera [新運鏡], [新對白], [延續 continuity anchors]`
4. 最後一段 Extend 切 Veo 3.1 Lite 省 credits
5. 輸出 → 自動拼接 (或下載手動剪)

**預估成本：** ~200 Flow credits (若全 Quality) / ~80 credits (Fast + Lite 混搭)

### R2: 一整部角色故事 (保持角色一致 + 多場景)

**使用者需求：** 「做我兒子在 5 個不同場景的短片」「同角色系列」

**Chain 選項 A (Kling 3.0 Omni Series Mode)：**
1. Image 3.0 Omni → 5 張角色一致的靜態場景圖
2. 每張 → Kling 3.0 Video I2V 生 5s 動畫
3. 自動拼接或 Extend 連貫

**Chain 選項 B (Nano Banana Pro + Runway Gen-4 Refs)：**
1. Nano Banana Pro 角色一致性 → 5 張 storyboard 圖
2. Runway Gen-4 References (3 張一次) × 2 回合 → 影片
3. 後期剪接

**Chain 選項 C (Vidu Q3 Reference-to-Video)：**
1. 1-4 張 reference (角色 + 場景 + 風格)
2. 單次 16s 多鏡 video 含原生音訊
3. 全部在 Vidu 內完成

---

### R3: 把自己的照片變動漫風跑步影片

**使用者需求：** 「把我兒子照片做成動漫風奔跑」

**Chain：**
1. **Flux Kontext** 或 **Nano Banana** → 照片轉動漫風 (靜態)
2. **Runway Act-Two** 或 **Kling Motion Control 3.0** → 你拍一段自己奔跑的手機影片作為 mocap source
3. 靜態動漫角色 + mocap source → 生動畫短片
4. 輸出：動漫版本的角色執行你的動作

**對比：**
- Act-Two (Runway)：好萊塢級，大場面
- Motion Control 3.0 (Kling 3.0 Omni)：整合式，同平台，中文場景強

---

### R4: 電影感分鏡 60 秒片段

**使用者需求：** 「做一個 60 秒電影級廣告 / MV 開場」

**Chain：**
1. 寫完整 storyboard (`templates/storyboard.md`) 6-8 shots
2. **Kling 3.0 Custom Multi-Shot** → 一次生 6 shots × 15s = 90s
3. 或 **Seedance 1.0 Pro** `Cut to:` 多鏡 + 後期剪
4. 套完整 cinematic-direction.md 語彙 (Deakins / Vision3 500T / anamorphic / god rays)
5. 後期：配 Suno 音樂

---

## 🎨 靜態圖類 Recipe

### R5: 品牌識別包 (Brand Kit)

**使用者需求：** 「幫我做 [品牌] 的完整視覺包 — logo / 海報 / 社群貼文」

**Chain：**
1. **Midjourney v7 Draft Mode** → 快速 20-30 個 logo 方向
2. 挑最好的 sref code → 固定風格
3. **Nano Banana Pro** → logo 精修 + 加入品牌文字
4. **Seedream 4.5** Multi-Reference (14 張) → 用 sref + logo + 色票 → 生 5-10 個社群貼文格式
5. **Ideogram 3** → 強文字海報 (如廣告 hero shot)

---

### R6: 繪本/漫畫分鏡 (角色一致的 10 張圖)

**使用者需求：** 「做一本有 10 頁的繪本」「漫畫 10 格」

**Chain：**
1. **Nano Banana Pro** Series Mode → 主角一致性 10 張圖 (最多 5 人同時)
2. 每張不同場景 / 情緒 / 動作
3. **Seedream 4.5 Image Series Mode** → 若要中文字幕貼圖，再加工
4. 輸出：10 張高解析 PDF 合輯

**Nano Banana Pro 優勢：** 5 人內保持一致不用 fine-tune，Seedream 主導中文。

---

### R7: 產品攝影 Campaign

**使用者需求：** 「一個產品，5 種不同場景 / 角度」

**Chain：**
1. 第 1 張用 **Flux 1.1 Pro** or **Nano Banana Pro** → 產品精修靜態
2. Flux Kontext 或 Nano Banana 編輯 → 換背景 × 5
3. 每張再 Seedream 4.5 加標語 / 雙語文字

---

## 🎵 音樂類 Recipe

### R8: 完整專輯 5 首歌 (一致聲線)

**使用者需求：** 「做一張 EP，5 首歌風格類似」

**⚠️ 強制走 Persona，不要 5 次完整 chain：**
- 5 次完整 chain (每次重打 style + lyrics) = 50+ tool calls + 15 分鐘 (2026-04-20 親身驗證浪費)
- Persona chain (style 一次定，4 次只重打 lyrics) = 30 tool calls + 6 分鐘

**Chain (Suno Persona 版)：**
1. 第 1 首 → 用完整專業 prompt 生 2 版 (10 credits)
2. 挑最好版本 → **Create Persona** (存聲線, 0 credits)
3. Persona + 第 2-5 首：**只換 lyrics**，style 自動繼承 → 各 10 credits = 40 credits
4. (可選) 每首 **Extend** 到 3-4 分鐘
5. v5 Pro → **Stems 下載** (vocal / drums / bass / other)

**預估：** 50 credits + ≤ 30 tool calls + ≤ 1.5k token + < 6 分鐘
**詳細 SOP：** [site-profiles/suno.md §6 Speed Optimization](../automation/site-profiles/suno.md)

---

### R9: 廣告 30 秒 Hook

**使用者需求：** 「做個 30 秒廣告音樂 + MV」

**Chain：**
1. **Suno +Hooks** → 30 秒 punchy hook (不是 full song)
2. 同時 Flow Veo 3.1 or Kling 3.0 → 30 秒 MV
3. 後期：合 MV + hook 音訊

---

### R10: 翻唱 (Cover) 跨 5 種風格

**使用者需求：** 「把這首歌做成 lo-fi / rock / 爵士 / EDM / folk 5 版」

**Chain：**
1. 現成歌曲 (或 Suno 生的) → 上傳
2. **Covers** 功能 → 指定新 style
3. 5 次 Cover × 10 credits = 50 credits
4. v4.5+ 每 Cover 可 Extend 更長

---

## 🌀 跨類 Recipe (多媒體)

### R11: Music Video 一條龍 (音樂 + 影片 + 剪接)

**使用者需求：** 「我有個 MV 概念，從頭到尾做完」

**⚠️ 影片段強制用 Kling Multi-Shot 一次出 6-8 鏡，不要 N 次 chain：**
- 6 鏡 chain = 50+ tool calls + 20 分鐘 + 浪費 token
- Multi-Shot Mode = 1 次提交 + 等待 + 1 次下載 = ≤ 15 calls + 8 分鐘

**Chain：**
1. **Suno** → 3 分鐘音樂 (lyrics + style，10 credits)
2. 記錄歌曲 BPM + 段落時間點 (Intro 0-8s, Verse 8-32s, Chorus 32-56s...)
3. 用 `templates/music-video.md` 規劃 6-8 shots 對應段落
4. **Kling 3.0 Multi-Shot Mode** → 一次提交 6-8 shots × 8-15s
5. 後期：剪輯軟體 (CapCut / DaVinci / Premiere) 對齊音樂拍點
6. 輸出 MP4

**預估：** 10 credits (Suno) + ~400 credits (Kling Multi-Shot 一次出多鏡) = 大專案成本
**詳細 SOP：** [site-profiles/kling.md §11 Chain Speed](../automation/site-profiles/kling.md)

### R12: Storyboard → 完整影片 (Director workflow)

**使用者需求：** 「我有劇本，做完整短片」

**Chain：**
1. **OiiOii Story Video** 模式 → 劇本進去自動分鏡 + 角色 + 場景 + 多智能體協作
2. 到分鏡師後 $7 升級 → 完整影片輸出
3. **或** OiiOii 只做劇本 + 角色設計 (前期免費)，影片改走 Kling / Flow 手動

### R13: 真實人像 → AI 影片 (Sora Cameo)

**使用者需求：** 「把我拍進異世界影片」

**Chain：**
1. **Sora 2 Cameo**：錄一次 5-30 秒 video + audio (你的臉 + 聲音)
2. 建立 character 存檔
3. 任何 Sora 場景 prompt 可放入這個 cameo
4. Deepfake 防範：Sora 自動加水印 + consent 宣告

---

## 何時需要進階 recipe vs 單次生成

### 單次就夠
- 短於 15s 的影片
- 單張圖
- 單首歌 (< 4 分鐘)
- 不需跨片段一致性

### 要用進階 recipe
- **> 15s 影片** → R1 Extend chain
- **多鏡 / 多場景同角色** → R2 / R4 / R6
- **既有素材整合** → R3 / R7 / R13
- **大量同風格** → R5 / R8 / R10 / R11
- **全流程一條龍** → R11 / R12

---

## Auto-Pilot 整合

**Stage 3.5 (新)：偵測進階需求**

Auto-Pilot 在 Stage 3 (Platform Decider) 後，**檢查 intent 是否 match recipe**：

1. 解析 intent 關鍵字：
   - 時長 `30s+` → R1
   - 角色一致性 + 多場景 → R2 / R4 / R6
   - 真人照片 → R3 / R13
   - 品牌包 / 系列 → R5 / R6 / R7
   - 專輯 / 多首歌 → R8
   - MV / 一條龍 → R11 / R12

2. 若 match recipe → **執行 chain** (告知使用者會跑多步 + 累積預估成本)
3. 若無 match → 退回單次生成

**Preview 要告知：** 「這個任務要跑 X 步 chain，預估 Y credits 總成本，要繼續嗎？」讓使用者知道會比單次貴。

---

## 自我增長機制

使用者的新需求若沒有對應 recipe，**Auto-Pilot 完成後可提議：**

> 「這個 workflow 我設計了 3 步 chain (A → B → C)，要不要存成新 recipe R14？下次類似需求我直接套。」

存成新 recipe 後 skill 越用越聰明。
