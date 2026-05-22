# Site Profile: Google Flow (Veo 3.1)

**URL:** `https://labs.google/fx/tools/flow` (會重導至 `/zh/tools/flow` 或地區別)
**驗證狀態:** ✅ 2026-04-19 實測
**平台類型:** Google AI 電影製作平台 (Veo 3.1 官方 UI)
**Stack:** Next.js React，ref 相對穩定但 **prompt textbox 是 contentEditable DIV** (一樣 form_input 不吃)

---

## 1. 登入與會員

- 必須 Google 帳號登入
- 有 `PRO` 徽章 (右上) = 付費用戶，有月點數額度 (代碼叫 "點數")
- 每月點數數額依 plan 而定

---

## 2. UI 地圖

### 首頁 `/zh/tools/flow`

```
┌────────────────────────────────────────────────────────┐
│ Flow [logo]            Flow TV  Discord  IG  X  ?  ⋮  PRO │
├────────────────────────────────────────────────────────┤
│ ┌──── 新功能公告 banner (x 可關) ────────────────────┐ │
│ │  "Nano Banana 2 is Here!" / 其他更新               │ │
│ └───────────────────────────────────────────────────┘ │
│                                                         │
│ ┌──── 專案 grid ─────────────────────────────────────┐ │
│ │ [Project 1]   [+ 新建項目]   [Project 2]           │ │
│ │                                                      │ │
│ └───────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

**進首頁常見 modal**：功能公告如「Ingredients to Video with Veo Lite」— 點 "開始使用" 關掉。

### 專案編輯器 `/zh/tools/flow/project/{uuid}`

```
┌────────────────────────────────────────────────────────┐
│ ← [4月19日 下午10:13]  ⋮    [搜尋 🔍][濾鏡 ≡]  + ▣ ⚙ ? ⋮ PRO│
├────────────────────────────────────────────────────────┤
│                                                         │
│ [Generated videos / assets grid]                       │
│                                                         │
│              🌼 開始創建或拖放媒體                       │
│                                                         │
│                                                         │
│ ┌───────── prompt 輸入區 ─────────────────────────┐  │
│ │ [+] 您希望創作什麼內容?        [視頻 □ x2] [→]  │  │
│ └────────────────────────────────────────────────┘  │
│ Flow 的回答未必正確無誤，請注意校查                       │
└────────────────────────────────────────────────────────┘
```

---

## 3. Phase-by-phase 流程

### Phase 1 — 進專案

- 首頁點「+ 新建項目」卡 → 進 `/project/{uuid}`
- 或開既有專案繼續

### Phase 2 — 設定模型 / 格式 (右下角「視頻 □ x2」按鈕)

**點右下角 模型/格式 selector** 展開參數面板：

| 類別 | 選項 | 預設 |
|---|---|---|
| 內容類型 | **視頻** / 圖片 | 視頻 |
| 子類型 | 素材 / 幀 | 素材 |
| 畫面比 | **16:9** / 9:16 | 16:9 (左 9:16, 右 16:9) |
| 數量 | **x2** / x1 / x3 / x4 | x2 |
| 模型 | **Veo 3.1 - Fast** / Veo 3.1 - Lite / Veo 3.1 - Quality | Fast |

**模型下拉展開顯示：**
- 🔊 Veo 3.1 - Lite (最便宜)
- 🔊 **Veo 3.1 - Fast** (預設，中階)
- 🔊 Veo 3.1 - Quality (最貴)

**所有 Veo 3.1 皆支援原生音訊** (🔊 圖示代表)。

### Phase 3 — 點數消耗 (實測)

| 模型 × 數量 | 點數 |
|---|---|
| Fast × 1 | 20 |
| Fast × 2 | 40 |
| Fast × 3 | 60 |
| Fast × 4 | 80 |
| Quality × 1 | 100 |
| Quality × 2 | **200** |

**Quality = 5x Fast 成本**。demo / 比較用 Fast x2；最終版或商業用 Quality x1 或 x2。

### Phase 4 — Prompt 輸入

1. **關掉模型面板** (按 Escape 或點外側)，面板會蓋住 prompt textbox
2. **Click prompt textbox** (底部 "您希望創作什麼內容？" 位置 ≈ y=630-635)
3. **Type 完整 prompt** (Veo 3.1 建議 3-6 句，100-150 字)

**重要 gotcha：**
- Prompt textbox **不是 `<input>` 而是 contentEditable DIV** — `form_input` 回錯
- 要用 `computer.left_click` + `computer.type`
- **不像 OiiOii，Flow 的 Enter 不會觸發送出** (行為較友善)

### Phase 5 — 送出

- 點右下 **→ 送出箭頭** (座標 ≈ (1007, 660))
- 畫布出現 2 個 (或你選的 x 數量) 生成卡片，顯示進度 %
- Fast 通常 2-5 分鐘；Quality 5-10 分鐘

### Phase 6 — 結果 / 編輯器 (2026-04-19 實測補)

生成完成後畫布顯示 1 張縮圖 (代表整個「集合」含 x2 版本)。點進去進到編輯器頁面 (URL `/edit/{uuid}`)：

**編輯器 UI：**
```
┌───────────────────────────────────────────────────────────┐
│ ← [自動抽取標題 e.g. "Girl whispering to kitten"]  ℹ  [下載] [顯示歷史記錄] [完成] │
├───────────────────────────────────────────────────────────┤
│                                                            │
│           [主影片預覽，滑鼠移上會出現播放鍵]                │
│                                                            │
│                                               Veo          │
│                                                            │
├───────────────────────────────────────────────────────────┤
│ 後續步驟                                                   │
│ [prompt 輸入框]                    [Veo 3.1 - Lite ▾] [→]  │
│                                                            │
│ [⏩ 延長] [➕ 插入] [✏️ 移除] [📷 攝像頭]                 │
└───────────────────────────────────────────────────────────┘
```

**4 個後續編輯工具 (類 Runway Aleph)：**
| 按鈕 | 功能 |
|---|---|
| 延長 (Extend) | 接續此片段再生 8 秒 |
| 插入 (Insert) | 片段中間插新內容 |
| 移除 (Remove) | 局部消物件 |
| 攝像頭 (Camera) | 事後改運鏡 |

**重點觀察：**
- **標題是 AI 自動從 prompt 抽取** — "Girl whispering to kitten" 是從原 prompt 萃取的語意
- **延長預設換成 Veo 3.1 Lite** (最便宜，省點數擴充)
- 下載按鈕在右上角，直接存 MP4
- Veo 水印右下角 (輸出含水印，除非特殊 plan)
- **點「完成」** 回到專案 collection 首頁

**音訊驗證：** Claude in Chrome 無法直接聽音訊，要驗證 Veo 3.1 的原生音訊 (對白/SFX/配樂) 要下載 MP4 本機播放。**從視覺看影片有動** (幀與幀不同)，但音訊層次需 user 親自確認。

---

## 4. Click 協議特殊注意

### 設定面板會蓋住 prompt 框
**先關設定面板** (Escape 或 click 面板外側) **才能點 prompt textbox**。否則 click 會打到面板上方空區。

### 座標漂移
Flow 的設定面板用絕對定位在底部偏右，prompt textbox 在底部中央。面板展開時它們**重疊**。

### 「視頻 x1」按鈕 (右下)
這個按鈕顯示當前設定 (如 `視頻 □ x2`)。點它 → 展開完整設定面板。**不要亂點以為是送出**。

### 頂部搜尋框陷阱
頂部中央有 🔍 搜尋框。若焦點跑到那裡 (例如點錯或切 tab 回來焦點丟失)，type 的內容會被當成搜尋 query，觸發 filter (例如顯示 "視頻 ×" 濾鏡 tag)。**送 prompt 前要確認焦點在 prompt textbox**。

---

## 5. Prompt 最佳寫法 (Veo 3.1)

見 [../references/veo.md](../../references/veo.md) + [../references/sound-design.md](../../references/sound-design.md)。**關鍵：**

- **對白：** `[Character] says, "..."` (英文最穩)
- **SFX：** `SFX: 聲源 + 音質`
- **Soundtrack：** `Soundtrack: 風格 + BPM + 動態`
- **Style：** 導演 + DP + 底片 (見 [../references/cinematic-direction.md](../../references/cinematic-direction.md))
- **長度：** 3-6 句話，100-150 字

---

## 6. 實測範例 (2026-04-19，深夜鳥)

**Prompt 輸入：**

```
Interior vignette of a Taipei back alley at 3 AM, light rain streaming.
Medium shot of a 16-year-old girl with long black hair in a cream
oversized cardigan, crouching down beside a flickering vending machine.
An orange tabby kitten with amber eyes peeks out from behind the machine.
The girl softly whispers, "Hey... are you hungry?" and slowly extends
her hand, warm amber light from the vending machine casting a glow on
her face. SFX: gentle rain on wet asphalt, vending machine electrical
hum, soft kitten mew, distant scooter passing by. Soundtrack: sparse
solo piano melody, 70 BPM, melancholic but hopeful. Style: Makoto
Shinkai cinematic anime blended with Hoyte van Hoytema warm-cool
contrast, Kodak Vision3 500T film emulation, shallow depth of field,
volumetric mist under streetlamp, 16:9 widescreen.
```

**設定：** Veo 3.1 Fast, 16:9, x2 = 40 點數

**用到的 skill 語彙：**
- `Makoto Shinkai` (cinematic-direction.md Part 2)
- `Hoyte van Hoytema warm-cool contrast` (cinematic-direction.md Part 3)
- `Kodak Vision3 500T film emulation` (cinematic-direction.md Part 5，Hoytema 招牌底片)
- `volumetric mist under streetlamp` (vfx-effects.md Part 1)
- 對白英文 + SFX 前綴 + Soundtrack + 音訊分層 (veo.md + sound-design.md)

---

## 7. 已知未驗證的行為

下次操作時補進來：

- ✅ ~~生成完成後的 UI (下載路徑、擴展功能)~~ — Phase 6 已補
- ⏳ `Ingredients to Video` (多素材合成) 流程
- ⏳ `Extend` 實測 (有按鈕但沒跑完整流程)
- ⏳ `Insert / Remove / 攝像頭` 四工具實測
- ⏳ `Scene-to-scene` (3.1+ 多場景拼接)
- ⏳ **Nano Banana 圖像模式** — 在模型面板切「圖片」應該會列出 Nano Banana / Nano Banana Pro 等 image model (見 [../../references/nano-banana.md](../../references/nano-banana.md))
- ⏳ 與 Imagen 的整合 (先生圖再動)
- ⏳ 點數歸零後的行為 (是否擋下 / 需充值)
- ⏳ MP4 下載後的檔案規格 (解析度/fps/音訊 codec)
- ⏳ Veo 3.1 對話 lip sync 品質 (英文 vs 中文)
- ⏳ 分享功能 (若有)

---

## 8. 座標速查 (1568×708 viewport)

| 元素 | 座標 |
|---|---|
| 首頁「+ 新建項目」(中間專案) | ~(785, 608) |
| 首頁「+ 新建項目」(其他位置視 grid 而定) | 變動 |
| 專案返回箭頭 | (33, 31) |
| 頂部搜尋框 | (745, 31) — 小心焦點漂移 |
| 右上齒輪 (視圖設定，不是模型) | (1375, 31) |
| 右下模型/格式 selector (視頻 □ x2) | (957, 660) 大概 |
| 設定面板內：16:9 | (937, 530) |
| 設定面板內：9:16 | (830, 530) |
| 設定面板內：x1 | (800, 560) |
| 設定面板內：x2 | (856, 560) |
| 設定面板內：Veo 3.1 下拉 | (880, 591) |
| 下拉展開：Lite | (853, 480) |
| 下拉展開：Fast | (853, 517) |
| 下拉展開：Quality | (862, 553) |
| Prompt textbox 中心 | (780, 635) (要先關設定面板！) |
| 送出 → 箭頭 | (1007, 660) |
| Prompt 框右上 × (關閉/清空) | (1010, 478) 出現時 |

---

## 9. 版本與更新紀錄

- **2026-04-19 實測：** Phase 1-5 完整驗證，生成 Fast x2 共 40 點。prompt textbox 是 contentEditable DIV。Enter 不觸發送出 (跟 OiiOii 不同)。模型面板和 prompt textbox 會重疊，操作前要關面板。
- **未驗證：** Phase 6 下載 + `Ingredients to Video` + `Extend` + `Scene-to-scene`。

---

## 10. ⚡ Chain Speed Optimization (Veo 3.1 多片段)

**痛點：** 連跑多支影片時，每片都 screenshot/TodoWrite 是浪費。

### 最佳 chain SOP (每片 5-6 calls，5 片 = 30 calls)

**前置 (1 次)：** navigate to labs.google/flow + 1 screenshot 確認 UI

**每片 5-6 calls：**
```
1. key Escape                  → 關閉設定面板（避免覆蓋 prompt textbox）
2. left_click (780, 635)       → focus prompt 框
3. key ctrl+a                  → 全選舊內容
4. type <new prompt>            → 一次貼完 (覆寫 + content-editable DIV 沒有 trash)
5. left_click (1007, 660)       → click 送出箭頭
[6. wait 60s 後再 batch screenshot 看進度]
```

**禁忌：**
- ❌ 中間 screenshot — Flow UI 座標穩定
- ❌ TodoWrite 每片 — chain 跑完一次更新即可
- ❌ form_input 給 prompt — Flow textbox 是 contentEditable DIV，**form_input 失敗**
- ❌ Enter 鍵 — Flow 不送出 (跟 OiiOii 不同)，要點箭頭

**驗證點 (僅 2 次)：**
- 第 1 片送出後 → 1 screenshot 確認進度條 + credits 扣
- 全部送完 → 1 screenshot 確認 5 片在 workspace

**clear prompt 法：**
1. **`key ctrl+a`** (全選) → type 直接覆寫 — 最快 1 call
2. ❌ 點 × icon 清空 — 慢，且 × 不一定常駐

**內容長度：** Veo 3.1 prompt 標準 ~80 字 (Subject + Action + Camera + Lighting + Audio)，超過反而模糊。

**預期效能：** 5 片 < 4 分鐘 + < 1.2k token
