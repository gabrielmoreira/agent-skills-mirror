---
name: ai-media-generator
description: 為使用者產生高品質的 AI 生圖、生影片、生音樂提示詞，並在需要時透過瀏覽器自動化實際送到目標平台。涵蓋 OiiOii、Kling 2.1/2.6/3.0、Seedance 1.0 / 2.0 pro、Suno v5、Seedream 4.0/4.5/5、Vidu Q2/Q3、Midjourney v7、Flux 1.1 Pro / Kontext、Runway Gen-4 / Aleph、Google Veo 3.1、OpenAI Sora 2、Ideogram 3、Nano Banana Pro、Stable Diffusion 3.5。只要使用者提到「AI 生圖」「AI 影片」「AI 音樂」「做 MV」「做 storyboard」「寫 prompt 給 XXX」「我想用 Kling/Suno/Midjourney/Runway/Veo/Sora...」「幫我操作 OiiOii / 即夢 / 可靈」「txt2img / img2video / 文生圖 / 文生影片 / 圖生影片」「角色一致性」「多鏡頭分鏡」「運鏡」，或任何跟上述平台或影像/影片/音樂生成工作流相關的任務，都要用這個 skill。即使他們沒講明平台，只要任務是要餵給某個生成模型的 prompt，就用這個 skill 幫他們選對的平台、寫對的格式。
---

# AI Media Generator

幫使用者把想法變成高品質的 AI 生成內容 (圖片、影片、音樂)，核心工作是 **寫對每個平台的 prompt** 以及 **必要時自動操作網站**。

## 🤖 Auto-Pilot Mode (超傻瓜一句話到成品)

**觸發：** 使用者說「幫我做 X」「做一個 X」「生個 X」「我要 X」這類命令式、且 X 含媒體類型 (圖/影片/音樂/MV/短片/海報/動畫) 或風格關鍵字 → **直接進 auto-pilot 不問**。

**流程 (見 [templates/auto-pilot.md](templates/auto-pilot.md) 完整版)：**
1. **Intent Parser** — 一句話拆 9 slot (媒體/長度/畫面比/主題/風格/角色/場景/音訊/語言)
2. **Fill Defaults** — 沒講的用預設 (video 預設 10s 16:9；動漫預設 Shinkai+Ghibli；電影預設 Deakins DP…)
3. **Platform Decider** — 按 [references/selector.md](references/selector.md) + quick pick 矩陣自動選
4. **Script + Storyboard Auto-gen** — 自動寫 logline + 角色卡 + 分鏡
5. **Prompt Crafting** — 強制套語彙庫 (見下方硬規則)
6. **Preview + Go** — 30-秒 override 視窗，使用者回「go/確認/OK」才執行；無回 + 需花錢 → 停；無回 + 免費 → 30 秒後自動繼續
7. **Execution + Report** — 按 [automation/click-protocol.md](automation/click-protocol.md) + [site-profiles/](automation/site-profiles/) 協議操作

**Auto-Pilot 必停的 checkpoint (不代做)：**
- ⛔ 付費 paywall / 升級提示
- ⛔ 送出前最終一次確認
- ⛔ 下載 / 分享 / 公開發布
- ⛔ 敏感內容 (真人照片疑似裸露/暴力/政治人物)
- ⛔ click-protocol.md 定義的「irreversible action」

**Auto-Pilot 禁止行為：**
- ❌ 幫 Claude 已知的事問使用者 (「你要幾秒的影片？」— 10s 預設就好)
- ❌ 一次拋多選項 — 選 1 個最佳 commit，讓使用者在 Preview 階段才決定改不改
- ❌ 寫純 generic 填詞 prompt (`beautiful / masterpiece / detailed`) — 違反下方硬規則（注意：`cinematic / 4K / 8K` 在新一代模型如 Seedance 2.0 是有效 token，看平台分流）
- ❌ 代付款

**使用者自然語言 flags 可 override 預設：** 使用者一句話可帶「用 Kling / 5 秒 / 豎屏 / 免費 / Ghibli 風 / 有對白」等自然語言 flag，auto-pilot 掃 [templates/user-flags.md](templates/user-flags.md) 對照表自動套用。使用者不懂術語也 OK — 「做個抖音」「可愛一點」「夢幻」都有對應翻譯。

**⚡ Token-Efficient Mode (大專案必讀)：** 本 skill 30+ 檔 / 7000+ 行，全量讀會爆 context。Auto-Pilot 預設套 [templates/token-efficient-mode.md](templates/token-efficient-mode.md) 的 7 層策略 (lazy load / grep / 子代理 / preset 跳過 / cache polling)。**一般任務目標 ~25-40k tokens，不是 100k+**。豪華模式 (全量讀) 只在 benchmark / 學 skill / 陌生平台探索時啟用。

## 🔴 硬規則 (Mandatory)

### Meta 優先序（2026-04-21 實戰鐵律）

**Prompt 寫對一次 ≫ 操作快 10 次。**

根因：寫錯 prompt → 重做 → 等 8-10 分鐘。操作 25 秒 vs 5 分鐘差距（~4.5 分鐘），**遠遠小於「一次 prompt 失敗」成本（~10 分鐘等待 + token 浪費）**。所以速度優化的**真正**優先序：

1. **第一優先：查平台簽名 + 寫對 prompt** → [references/community-prompt-patterns.md](references/community-prompt-patterns.md)（跨 X/Threads/Reddit/小紅書/Bilibili 社群驗證，單一 source of truth）
2. **第二優先：單次提交極速化** → [automation/site-profiles/](automation/site-profiles/)
3. **第三優先：等待不 polling** → `Bash run_in_background:true + sleep 400`

順序反了 = 浪費 40+ 分鐘做 4-5 次嘗試才生出可用的。

### Prompt 必備語彙

**每次產 image / video / music prompt，都必須從 skill 進階語彙庫挑 token — 不是選配，是必做。**

**流程：**
1. **最優先查**：[references/community-prompt-patterns.md](references/community-prompt-patterns.md) — 按**目標模型**查簽名 token + 長度甜蜜點 + 禁忌（⚠️ 平台吃不同 token，Seedance/Wan 吃導演名 = 災難）
2. 決定任務類型 (攝影感/電影感/廣告/時尚/MV/VFX/社群短片)
3. **挑對應 reference 檔讀：**
   - 電影/攝影類 → [cinematic-direction.md](references/cinematic-direction.md) 必讀
   - 廣告/時尚/MV/品牌 → [commercial-direction.md](references/commercial-direction.md)
   - 特效/物理/大氣 → [vfx-effects.md](references/vfx-effects.md)
   - 原生音訊 (Veo/Sora/Vidu Q3) → [sound-design.md](references/sound-design.md)
   - 多鏡/剪接/節奏 → [editing-transitions.md](references/editing-transitions.md)
4. **快速路徑**：先查 [preset-packs.md](templates/preset-packs.md) 找最近的 preset，換占位符即可
5. **每個 prompt 至少嵌入 5-8 個高訊號 token**，從下列層挑（**看平台分流**）：
   - 導演/DP 名 (Deakins、Lubezki、Hoytema、王家衛、新海誠…) — ✅ MJ/Sora 2/Veo；❌ Flux/Nano Banana Pro/Seedance/Wan
   - 鏡頭/焦段 (Panavision anamorphic / 85mm / C-Series 等) — 通吃
   - 底片/感光 (Kodak Vision3 500T / Cinestill 800T 等) — ✅ Flux/MJ；❌ Seedance
   - 光比/燈光 (Rembrandt / 4:1 contrast / volumetric god rays 等) — 通吃
   - 色彩分級 (teal-orange / bleach bypass / A24 indie 等) — 通吃
   - 構圖/景別 (rule of thirds / medium close-up 等) — 通吃
   - VFX/大氣 (halation / Tyndall effect / particles 等) — 通吃
   - (Veo/Sora) 音訊三層 (Dialogue / SFX / Soundtrack)

### 禁用模式（通用 + 平台特定）

**通用原則：** **寧可 5 個具體 token，不要 20 個泛詞。** 但 generic 與否**看平台**。

**真正全平台垃圾（任何時候都別用）：**
- `beautiful / masterpiece / detailed / high quality / professional`（這幾個從沒在新一代模型有實證效果）
- `--no blur` 等 flag-style 負面 prompt（多數模型不吃，用自然語言 `no blur` 反而 OK）

**⚠️ 平台特定（注意「2026-04-21 vs 2026-05-18 推翻」— 模型升級會改變斷言）：**
- ⚠️ `cinematic` / `4K` / `8K` / `35mm-50mm-85mm` — **舊版 Seedance 1.0 弱，Seedance 2.0 大量吃**（v1.1.0 修正）。Kling / Sora 2 / Veo 3.1 / MJ v7 / Flux 全吃。
- ❌ **Seedance 2.0**：`fast`（改 `extreme speed / kinetic / rapid`）、多動詞同句、多主體獨立動作、chaotic wide 無時間區塊、個別 DP 名（藝術運動 / 品牌風格 OK）
- ❌ **Flux / Nano Banana Pro**：artist names（訓練時被 scrub）、`--ar` 語法
- ❌ **Runway Gen-4**：>60 字 prompt（最短的模型）、synonym drift
- ❌ **Kling**：stacking 多個相機運動、>4-5 distinct nouns

**先查 [community-prompt-patterns.md](references/community-prompt-patterns.md)** — 該檔每個模型都有「禁忌」section，且註明 cross-platform 推翻歷史。

### 驗證自檢

Prompt 寫完問自己：
1. 查過 community-prompt-patterns.md 目標模型章節？
2. Token 符合該平台簽名（不是隨手亂塞）？
3. 避開該平台禁忌？
4. 長度在甜蜜點（不過長不過短）？

4 題都過 → 送。缺一題回去改。

## 核心原則

1. **先問清楚「要什麼」，再決定「用哪個」**。同一個想法送到不同模型，prompt 寫法完全不同。先釐清：
   - 媒體類型：靜態圖 / 影片 / 音樂 / 複合 (MV、分鏡動畫)
   - 用途：社群貼文 / 廣告 / 電影感短片 / 角色一致性專案 / 文字海報
   - 手上資源：有沒有參考圖、首尾幀、角色圖、歌詞
   - 預算/可用性：免費網站 / 付費會員 / API 金鑰

2. **讀對應的 reference 檔**。本 skill 的知識是分散式的。不要從腦中記憶硬編 prompt — 每次都先讀目標平台的 reference 檔，因為各模型版本更新很快，檔案裡有最新的語法、參數、連結。

3. **中英混寫時有規則**：主體名詞、運鏡術語、模型參數用英文；情感描述、文化元素 (漢服、水墨、國風)、旁白/歌詞用中文。Seedream 與 Kling 的中文支援最好；Midjourney、Flux、Runway、Veo 英文效果明顯較佳。

4. **Prompt 長度**。多數模型在 60–150 字 / tokens 之間最佳；Flux Kontext 上限 512 tokens；Veo 建議 3–6 句話；Sora 偏好「分鏡式」描述。reference 檔有每個模型的具體上限。

5. **輸出格式**。除非使用者明說只要 prompt 本文，否則給他們：
   - 一個 **可複製的 prompt 區塊** (通常英文)
   - 一段 **繁中說明**：這個 prompt 為什麼這樣寫、哪些 token 可以換掉、預期輸出會長怎樣
   - 一組 **建議參數** (aspect ratio、時長、model variant、seed 等)
   - 如果有平台特殊語法 (tag、metatag、參考圖槽位)，把它結構化呈現

## 工作流

### Step 1 — 選平台

如果使用者已指定平台 (「用 Kling」「幫我寫 Suno prompt」)，直接跳 Step 2。

否則讀 [references/selector.md](references/selector.md) 按「媒體類型 × 用途 × 資源」選出 1–2 個最佳候選平台，並把推薦理由用 2–3 句話告訴使用者。如果落差很大 (例如「免費 vs 付費最佳」)，給使用者選擇。

### Step 2 — 讀對應的 reference 檔

根據選定平台，**一定要** 讀對應檔案，不要憑記憶寫 prompt：

**影片 (Video)**
- Kling → [references/kling.md](references/kling.md)
- Seedance 2.0 pro / 1.0 Pro / Lite → [references/seedance.md](references/seedance.md)
- Vidu Q2 / Q3 → [references/vidu.md](references/vidu.md)
- Runway Gen-4 / Aleph / Act-Two → [references/runway.md](references/runway.md)
- Google Veo 3 / 3.1 → [references/veo.md](references/veo.md)
- OpenAI Sora 2 → [references/sora.md](references/sora.md)

**圖片 (Image)**
- Seedream 4.0 / 4.5 / 5 → [references/seedream.md](references/seedream.md)
- Midjourney v7 → [references/midjourney.md](references/midjourney.md)
- Flux 1.1 Pro / Kontext → [references/flux.md](references/flux.md)
- Ideogram 3 → [references/ideogram.md](references/ideogram.md)
- Stable Diffusion 3.5 / SDXL → [references/stable-diffusion.md](references/stable-diffusion.md)

**音樂 (Music)**
- Suno v5 → [references/suno.md](references/suno.md)

**複合 / 多智能體**
- OiiOii.ai → [references/oiioii.md](references/oiioii.md)

**跨平台共通**
- 鏡頭語言 (影片類都適用) → [references/camera-language.md](references/camera-language.md)

**進階導演 / VFX / 音效 / 剪接 級別 prompt 設計** (當使用者要「電影級」「廣告級」「奢侈品級」「完整影視團隊」時**必讀**)
- 電影導演 / 攝影指導 / 底片 / 燈光 / 構圖 / meta tokens → [references/cinematic-direction.md](references/cinematic-direction.md)
- 廣告 / 時尚 / MV 導演 / 品牌調性 / 社群短影音 → [references/commercial-direction.md](references/commercial-direction.md)
- VFX 總監 / 大氣 / 物理 / 特效 recipes → [references/vfx-effects.md](references/vfx-effects.md)
- **音效設計** (對白 / SFX / Foley / 配樂) → [references/sound-design.md](references/sound-design.md) — Veo 3.1 / Sora 2 / Vidu Q3 原生音訊必讀
- **剪接 / 轉場 / 節奏** (match cut / whip pan / J-L cut / ASL 律動) → [references/editing-transitions.md](references/editing-transitions.md) — 多鏡故事、storyboard、MV 必讀

這三個進階檔是 **語彙庫**，不是流程手冊。使用方式：
1. 先照平台的 reference (kling.md / flux.md 等) 確定該平台的 prompt 結構
2. 再從進階檔挑 **5-8 個高質量 token** 填進結構裡
3. 不要整段 copy — 挑對情緒、對平台、對故事的那幾個詞

一個人身高不同，鏡頭焦段/燈光/底片的「關鍵詞組合」就不同。「超級資深影視導演」的 prompt = 四層堆疊 `[導演/DP] + [鏡頭/底片] + [燈光/色調] + [動作/構圖]`，每層挑最契合的 1-2 個 token。

### Step 3 — 根據任務類型參考 template

- **快速：抽一個現成 preset 套用** (30 個電影/廣告/MV/VFX/短影音 preset) → [templates/preset-packs.md](templates/preset-packs.md)
- **複雜多步驟任務 (> 15s 影片 / 多角色一致 / 品牌包 / 專輯 / MV 一條龍)** → [templates/advanced-recipes.md](templates/advanced-recipes.md) 13 個 chain workflow (Extend / Persona / Motion Control / Cameo 等進階功能組合)
- **重用角色/風格/場景卡** → [templates/asset-library.md](templates/asset-library.md)
- 多鏡頭 / 分鏡故事片 → [templates/storyboard.md](templates/storyboard.md)
- 音樂影片 / MV → [templates/music-video.md](templates/music-video.md)
- 常用負面提示詞 → [templates/negative-bank.md](templates/negative-bank.md)
- **社群多版本 / 預算 flag / 平台 flag / 風格 flag** → [templates/user-flags.md](templates/user-flags.md)
- **大專案省 token** → [templates/token-efficient-mode.md](templates/token-efficient-mode.md)

**preset-packs.md 的用法：** 使用者要「Wes Anderson 風」「Nike 廣告感」「賽博龐克雨夜」「水下夢境」等明確風格時，**先到 preset-packs.md 找最近的 preset**，換占位符即可，不用每次從零組 prompt。若使用者要的風格不在 preset 裡，再從 [cinematic-direction.md](references/cinematic-direction.md) / [commercial-direction.md](references/commercial-direction.md) / [vfx-effects.md](references/vfx-effects.md) 現場組。

### Step 4 — 組出 prompt 並輸出

依 reference 檔給的公式組出 prompt。每個平台有自己的 order、特殊符號、tag — **嚴格按 reference 檔的格式寫**。

**輸出格式**：可複製的 prompt 區塊 + negative + 參數 + 繁中 why (每個 token 為什麼選)。完整範例見 [preset-packs.md](templates/preset-packs.md) 的 30 個 preset，每個都是 ready-to-use 格式。

### Step 5 (選配) — 瀏覽器自動化執行

如果使用者要求「幫我直接做」「幫我貼上去按產生」「操作 OiiOii/Kling/Suno」等，這套檔要讀：

**1. 通用 click 協議 (所有網站都要遵循)**
- [automation/click-protocol.md](automation/click-protocol.md) — Click 決策樹、ref 保質期、座標精準技巧、驗證 selected 的方法、scroll-aware 座標、paywall 偵測、等待策略、驗證循環、速度優化

**2. 網站特定 profile (該站的 UI 地圖 + 座標 + 陷阱)**
- [automation/site-profiles/](automation/site-profiles/) — 每個網站一份深度 profile
  - ✅ [oiioii.md](automation/site-profiles/oiioii.md) — 完整驗證 Phase 1-3E (止於付費牆)
  - ✅ [flow.md](automation/site-profiles/flow.md) — 完整驗證 Phase 1-6 (Veo 3.1 Fast/Quality/Lite)
  - ✅ [kling.md](automation/site-profiles/kling.md) — 完整驗證 Phase 1-7 (Kling 3.0 + credits + Fast-Track)
  - ⏳ 其他平台 (Suno / Runway / MJ 等) 待操作時補
  - 📝 [_template.md](automation/site-profiles/_template.md) — 新網站 profile 模板

**3. 高層流程速查 (每站登入與主流程概述)**
- [automation/browser-guide.md](automation/browser-guide.md)

**送出前必做的安全檢查 (見 click-protocol.md 詳細)：**
- 確認使用者已登入目標站 (**絕不代輸入密碼**)
- 把即將輸入的 prompt 完整貼給使用者，**等確認再送**
- 首次操作某站 → screenshot 對照 site-profile，UI 改版就更新 profile
- 送出前 screenshot (before)，送出後 screenshot (after)，**比對 UI 變化確認真送出**
- 撞到 paywall / modal / 非預期彈窗 → **立刻停下問使用者**，不代付款

**reliability 核心原則 (來自 OiiOii demo 踩坑紀錄)：**
1. **不信任記憶中的座標** — 5 秒前的 screenshot 可能已過期，click 前必須剛截圖
2. **ref 很短命** — `find` 完 **立刻** click，中間不插其他 tool call
3. **selected state 看填底色，不是粉色 ring** (那是 hover)
4. **click 沒中別亂重試** — 先 screenshot 診斷 (paywall？disabled？座標偏？)
5. **Polling 不要 < 60s 也不要 > 3min** — 互動 UI 60-90s，純背後等待 3-5min

**⚡ Chain workflow 強制節省 (來自 Suno 5 首歌 chain 慘痛教訓 2026-04-20)：**
連跑多任務 (做 5 首歌、5 張圖、多支影片) 時：
1. **中間禁 screenshot** — 只第 1 task 後 + 全部完成各 1 張 (浪費點 #1)
2. **中間禁 TodoWrite** — chain 完成後一次性更新即可 (浪費點 #2)
3. **clear field 用 1-click** — 點 trash icon 或 ctrl+a 覆寫，禁用 triple-click + Ctrl+A + Delete 三步走
4. **內容寫標準長度** — Suno 歌詞 ~25 行 / Veo prompt ~80 字 / MJ keyword 30-50 字 / Seedream 80-120 字，超寫不加分
5. **平台有 Series Mode/Multi-Shot/Multi-Reference → 用內建批次** 不要 N 次 chain (Suno Persona / Kling Multi-Shot / Seedream Series / MJ omni-ref / Vidu Q3 multi-entity)

**檢測標準：** 5 task chain 應 ≤ 36 tool calls + ≤ 1.5k token + < 5 分鐘。違反任一就要修。詳見 [click-protocol.md §「Token + 時間最佳化」](automation/click-protocol.md)。

## 關鍵品質檢查 (在交付 prompt 前跑一遍)

- [ ] 有沒有「具體的主體描述」— 不只是 "a person" 而是 "a woman in her 30s with chin-length silver hair"
- [ ] 動作有沒有可視化的動詞 — "walks slowly" / "tilts her head" 優於 "is moving"
- [ ] 場景有沒有 2–4 個具體元素 — 時間、地點、天氣、物件
- [ ] 鏡頭 (如果是影片) — 運鏡類型 + 速度 + 距離
- [ ] 風格與光影 — 一到兩個清楚的風格錨 (例如 "cinematic, teal-and-orange grade")
- [ ] 長度適當 — 檢查目標平台的 sweet spot
- [ ] 沒有自相矛盾 — 不要同時寫 "close-up" 和 "wide establishing shot"
- [ ] 負面提示詞 (如該模型支援) 有列常見缺陷

## 常見反模式

- **拿 Midjourney 的 `--ar 16:9 --s 250` 語法餵 Flux / Kling / Sora** — 只會被當成雜訊。每個平台有自己的參數欄位。
- **在 Suno Lyrics 欄寫 "Verse:"** — 會被當成歌詞唱出來。要寫 `[Verse]`。
- **Seedream 叫它寫文字時用單引號或不加引號** — 官方建議用雙引號包住要顯示的字：`"Seedream 5"`。
- **Kling / Seedance 運鏡疊太多** — "zoom in while panning right and tilting up" 會爛掉。一次一到兩個運鏡。
- **Vidu ref2v 時 prompt 又重複描述參考圖的外觀** — 會互相打架。描述「動作與互動」就好。
- **SD 3.5 用 `(word:1.3)` 權重語法** — 3.5 不吃這個，改用自然語言。SDXL 才吃。

## 關於「萬用」的邊界

此 skill 設計為 prompt engineering + 瀏覽器自動化雙層。不直接呼叫 API (API key 管理、計費都是額外議題)，但若使用者明確要走 API，reference 檔裡有各平台的官方 API 端點連結，可以協助組 payload。

## 版本資訊

知識整理於 2026-04，各模型版本皆以當時最新為準。各 reference 檔末尾有官方文件連結 — **若要執行會花錢/產生後果的操作前，優先拿 reference 連結當最終依據**，因為版本/定價變動快。
