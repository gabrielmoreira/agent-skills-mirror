# Site Profile: Kling AI

**URL:** `https://kling.ai/app/` (新版)，舊 URL `https://app.klingai.com/global/` 會 redirect
**驗證狀態:** ✅ 2026-04-20 完整驗證 Phase 1-7 (免費帳號 96 credits 實測，跑 Kling 3.0 720p 5s 扣 45 credits)。✅ 2026-06-05 recon 確認**仍登入可用**，首頁功能列：**Omni / Image Generation / Video Generation / Motion Control / Kling Canvas / Agent / Avatar 2.0**（Agent + Avatar 2.0 為新增，待深測）
**平台類型:** AI 影片/圖像生成 (Kuaishou 快手出品)
**Stack:** React，ref 穩定度待驗證；feature label 多為 icon 非文字 → DOM 文字掃描抓不到，需 screenshot 對座標
**版本：** **Kling 3.0 / 3.0 Omni / Motion Control 3.0 + Agent + Avatar 2.0** (2026-06 首頁。references/kling.md 已於 v1.5.0 升級至 3.0/O-series 完整功能地圖)

---

## 1. 登入

- **未登入就進不了 Generate** — Auto-Pilot checkpoint：不代登入
- 左下角 `Sign In` 按鈕
- 登入後獲得「Kling AI Trial Package」限時免費 credits
- 訂閱方案：**$6.99/月 起**

---

## 2. 整體 UI 地圖 (未登入狀態)

```
┌────────────────────────────────────────────────────────────────┐
│ [logo]                                        [Trial Package 彈窗] │
├────┬──────────────────────────────────────────────────────────┤
│ 🌐 │  ┌─ banner (旋轉): IMAGE 3.0 & 3.0 Omni / Motion Control 3.0 │
│Ex- │  └────────────────────────────────────────────────────────  │
│plore│                                                              │
│ 📦 │  [Omni Does It All]  [Image Gen]  [Video Gen]  [Motion Ctrl]  [Kling Canvas]  [Avatar 2.0] │
│Ass │                                                              │
│ 🌀 │  Recommended | Follows | Events ... Search                   │
│Omni│  For You | Shorts | 3.0 Model | Motion Control | Creatives   │
│ 🎨 │                                                              │
│Gen │  [explore grid - 社群作品]                                    │
│erate│                                                              │
│ 🖼 │                                                              │
│Can │                                                              │
│vas │                                                              │
│ ≡  │                                                              │
│All │                                                              │
│Tools│                                                             │
│    │                                                              │
│ API │                                                              │
│Sign│                                                              │
│ In │                                                              │
│$6.99│                                                             │
└────┴──────────────────────────────────────────────────────────┘
```

---

## 3. 左側 Sidebar 功能 (底層入口)

| 圖示 | 名稱 | 用途 |
|---|---|---|
| 🌐 Explore | Explore | 社群作品 browse |
| 📦 | Assets | 我的素材 |
| 🌀 | **Omni** | ⭐ **Image 3.0 Omni** 新功能 — Storytelling 模式、4K 原生 |
| 🎨 | **Generate** | 傳統 Video + Image 生成入口 |
| 🖼 | Canvas | Kling Canvas (畫布式編輯) |
| ≡ | All Tools | 所有工具列表 |
| API | API | 開發者 API |

---

## 4. 主要功能入口 (中央 grid)

1. **Omni Does It All** (Experience Now 按鈕) — 最新 Omni 綜合模式
2. **Image Generation** — Image 3.0 / Image 3.0 Omni
3. **Video Generation** — 視頻生成 (預計包含 Video 3.0 Pro / Standard)
4. **Motion Control** — **Motion Control 3.0**，專業動作捕捉
5. **Kling Canvas** — 畫布編輯
6. **Avatar 2.0** — 虛擬角色

---

## 5. Kling 3.0 速查 (2026-04 首頁觀察)

### Image 3.0 & 3.0 Omni
- **Series Mode Storytelling** — 系列式敘事 (可能類似 Nano Banana Pro 的角色一致性？)
- **Native 4K Output** — 原生 4K
- **Cinematic-Grade Fidelity** — 電影等級保真度

### Motion Control 3.0
- **Professional Motion Capture, Reimagined**
- 預計是從示範影片驅動角色表情/動作 (類似 Runway Act-Two)

### 這對 Auto-Pilot 的意義

若使用者的需求含：
- **多張連貫敘事** (storyboard) → Image 3.0 Omni Series Mode 可能贏過 Nano Banana Pro，待驗證
- **精準演員驅動** → Motion Control 3.0 (vs Runway Act-Two)
- **4K 輸出** → Kling 3.0 原生，免後期 upscale

---

## 6. Phase-by-phase 流程 (2026-04-20 實測完整)

### Phase 1 — 登入 (手動，使用者)
- 左下 `Sign In` → Google / email
- **Auto-Pilot 停在此** — 不代登入
- 登入後左下顯示 credits (免費實測 30→96 動態，可能 daily 補發或依活動)
- `Upgrade subscription` 按鈕在 credits 下方

### Phase 2 — 進 Video Generation

從首頁 `https://kling.ai/app/` 任一入口進：
- **中央 main grid** 點 `Video Generation` (座標 ~790, 256)
- **或頂部 tab** `Video Generation` (座標 ~237, 22)，**預設進入後這個 tab 就是 active**
- URL 變 `https://kling.ai/app/video/new`

### Phase 3 — 模型選擇 (左上)

**預設選中：`VIDEO 3.0 NEW` (含 Native Audio, Enhanced Element Consistency)**，左上有個 3.0 圖示 + 名稱 + NEW 標籤 + 描述，右側有下拉箭頭 `▾`。

**點下拉** (座標 ~480, 87) 展開列出所有可用 Kling video 模型：
- Kling 1.6 / 2.0 / 2.1 Standard / 2.1 Master / 2.6 Pro / **3.0** / **3.0 Omni** / **3.0 Lite** (列表待下次拉開驗證)
- 免費 tier 能用哪些需實測 (Fast-Track 給免費也有，但 Quality 版可能要訂閱)

### Phase 4 — Prompt 輸入 (textbox ref_17)

**位置：** 左側編輯面板中央空白區
**類型：** `<textbox>` — `form_input` 不會成功 (回 `Element type DIV is not supported`)
**SOP：** `find "prompt textbox"` → `left_click ref` → `type`

Kling 3.0 支援多語言對白、引號包 spoken content：
```
Host says, "welcome to today's release."
```
支援多口音 + dialects (3.0 unique)。

### Phase 5 — 參數設定 (左下)

左下參數列：`720p · 5s · 16:9 · 1` 點任一欄會展開可選項 (座標 ~145, 715)。
- **解析度：** 720p / 1080p (免費可能鎖 720p)
- **時長：** 5s / 10s (3.0 Omni 可到 15s 但耗 credits 多)
- **畫面比：** 16:9 / 9:16 / 1:1
- **數量：** 1 / 2 / 3 / 4

旁邊：
- **Native Audio** toggle (預設 ON) — 3.0 招牌，含 SFX/配樂/對白
- **Multi-Shot** toggle (在 prompt 框下方座標 ~230, 529) — 3.0 多鏡 storyboarding

### Phase 6 — Generate (送出 + Credits)

**Generate 按鈕** (綠色，座標 ~438, 715) 會顯示 **🔥 需要的 credits** (如 `🔥 45 Generate`)。實測：
- Video 3.0 / 720p / 5s / 16:9 / x1 / Native Audio ON = **45 credits**
- 上限：免費每日/月配額依活動 (實測 96 credits 起)

按下後右側大預覽區顯示：
- `Video | Video 3.0 | 720p` 標題 + prompt 內容
- **Queueing → Creating** 狀態文字
- `Congrats! You're having Fast-Track Generation. 2 hours saved from waiting in the queue` (免費也有 Fast-Track！)
- `Estimated wait: 1 minute`
- 左下 credits 立即扣款

### Phase 7 — 完成 + 播放/下載

**1 分鐘內完成** (Fast-Track)。右側預覽區自動顯示影片播放器：
- 播放圖示 ▶ (左下)
- **00:00 / 00:05** 時間顯示
- 右下 KlingAI 3.0 水印
- **🔊 音訊圖示** (右下角，代表有音軌)
- **全螢幕** 按鈕 (右下角末)

影片下方動作列：
- `Create in Omni` — 發送到 Omni 做後續延伸
- `Lip Sync` — 對口型 (Motion Control 3.0 功能)
- `Extract Frame` — 抽幀作為新生成的首/尾幀
- 右側 icons：👍 👎 📤 (分享) 📥 (下載) ⋯ ⭐

右側縮圖列 (Assets) 列出今天的產出。

---

## 7. 已觀察到的 UI 特性

- **右上 Trial Package 彈窗**：未登入狀態顯示，促銷登入。關閉按鈕在彈窗右上
- **"Claude is active in this tab group"** 提示會出現在底部中央，不影響操作
- **Top banner 旋轉** (自動輪播不同公告)
- **Explore grid**：可見其他使用者的作品，有 Like 數、時長、Pet Vlogger 等 category

---

## 8. 待驗證項目

- ✅ ~~Video Generation 進入後：模型下拉、prompt textbox type、參數欄位~~ Phase 2-7 已驗證
- ✅ ~~Credit 顯示位置~~ 左下角
- ✅ ~~輸出下載流程~~ 播放器下方 icons
- ✅ ~~Enter 鍵是否觸發送出~~ (Kling prompt textbox 不觸發 — 較友善)
- ⏳ Image 3.0 Omni Series Mode 實測 (多圖 storytelling)
- ⏳ Motion Control 3.0 完整 UI (角色圖 + 動作 video → 映射)
- ⏳ 設定 panel 是否蓋住 prompt textbox (目前觀察不會，比 OiiOii/Flow 友善)
- ⏳ Model 下拉展開的完整可選列表 (Lite/Fast/Quality/1.6/2.1/2.6/3.0/3.0 Omni)
- ⏳ 免費 tier 哪些模型可用，哪些鎖住

## 9. 座標速查 (1568×751 viewport, 2026-04-20 實測)

| 元素 | 座標 |
|---|---|
| 頂部 Video Generation tab | (237, 22) |
| 左上模型選擇器 + 下拉 | (290, 87) / 箭頭 (480, 87) |
| Prompt textbox (ref_17 穩定) | 左側編輯面板中央 |
| Multi-Shot toggle | (230, 529) |
| 左下參數列 `720p · 5s · 16:9 · 1` | (145, 715) |
| Native Audio toggle | (267, 715) |
| **Generate** 按鈕 (綠) | (438, 715) |
| Credits 顯示 | 左下 (30, 637) |
| Sign In / Upgrade | 左下 Sign In 區 |

---

## 9. 跟 skill references/kling.md 的同步

**references/kling.md 目前寫到 Kling 2.6 Pro，需更新到 3.0。**

待 WebSearch 拉最新資料後同步更新：
- 3.0 的 prompt 公式
- 3.0 Omni 的 Series Mode 用法
- Motion Control 3.0 的 prompt 寫法
- 新參數 (若有)

---

## 10. 版本與更新紀錄

- **2026-04-20 首頁觀察 (未登入)：**
  - 發現 Kling 3.0 / 3.0 Omni / Motion Control 3.0 是當前主力
  - URL 從 `klingai.com` 遷到 `kling.ai/app/`
  - 左側 sidebar 改版：Explore / Assets / Omni / Generate / Canvas / All Tools
  - 訂閱起價 $6.99/月

---

## 11. ⚡ Chain Speed Optimization (Kling 3.0 多影片)

**最佳 chain SOP (每影片 5-6 calls，5 片 = 30 calls)**

**前置 (1 次)：** navigate to kling.ai/app/generate + 1 screenshot 確認登入 + UI

**每影片 5-6 calls：**
```
1. left_click <prompt textbox>  → focus
2. key ctrl+a                   → 全選舊內容
3. type <new prompt>             → 覆寫
4. left_click <Generate 按鈕>   → 送出
[5. 一次性 batch screenshot 確認進度]
```

**禁忌：**
- ❌ 中間 screenshot — Kling UI 穩定
- ❌ TodoWrite 每片
- ❌ 同時開多 sub-tab — Kling 免費並行限制 1-2 個
- ❌ 模型 / aspect / 時長每片重設 — 預設沿用上一次設定

**驗證點 (2 次)：**
- 第 1 片進佇列後 1 screenshot 確認
- 全部跑完 1 screenshot 確認 5 片完成

**Multi-Shot Mode 替代 chain：** 若是「同主題 6 鏡」需求，**直接用 Kling 3.0 Custom Multi-Shot 一次出 6 鏡** (8s × 6 = 48s)，比 6 次獨立 chain 省 2/3 時間 + credits。Recipe R4。

**內容長度：** Kling 3.0 prompt 標準 ~100 字，多鏡語法用 `Shot 1: ... Shot 2: ...` 換行。

**預期效能：** 5 片 < 5 分鐘 + < 1.5k token
- **Phase 1-7 待登入後補完整。**
