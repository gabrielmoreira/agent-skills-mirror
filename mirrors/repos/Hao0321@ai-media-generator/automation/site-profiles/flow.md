# Site Profile: Google Flow (Veo 3.1 + Gemini Omni)

**URL:** `https://labs.google/fx/tools/flow` (會重導至 `/zh/tools/flow` 或地區別)
**驗證狀態:** ✅ 2026-04-19 實測（Veo 操作流程）；🆕 2026-06-08 大改版知識（WebSearch 官方+社群多源研究，UI 操作待登入後實機驗證）
**平台類型:** Google AI 創作工作室（已從「電影工具」升級為 AI Creative Studio）
**Stack:** Next.js React，prompt textbox 是 contentEditable DIV (form_input 不吃，比照 OiiOii 用 beforeinput 注入)

> ⚠️ **2026-06-08 登入狀態：Flow session 會過期，重進需 Google 帳號選擇 + OAuth 同意。** 登入/授權是安全紅線（Claude 不代做），需用戶親自完成帳號選擇後才能自動化操作。

---

## 0. 🆕🆕 2026 大改版完整地圖（WebSearch 研究，2026-06-08）

### 改版時間軸
| 日期 | 改版 |
|---|---|
| 2026-01-13 | Veo 3.1 更新：更強音訊/prompt 遵從/寫實；**4K 升頻**；音訊帶進 Ingredients/Frames/Extend |
| **2026-02-25** | **三工具合一**：Flow + Whisk + ImageFX 併成單一介面；**Nano Banana** 成 Flow 內建生圖引擎（直接當 ingredients/frames）|
| 2026-04-30 | Whisk 永久關閉（未遷移者資產刪除）|
| **2026-05-19** | **Google I/O 2026**：Flow 升級「AI Creative Studio」；上 **Gemini Omni / Omni Flash**、**Flow Agent**、**Flow Tools**、**Flow Music (Lyria 3 Pro)**、**Flow TV**；**AI Ultra 降價 $250→$100**，新增雙層 |

### 核心功能地圖（功能｜作用｜操作）
| 功能 | 作用 | 操作要點 |
|---|---|---|
| **Text to Video** | 純文字生影片 | model 下拉選 → Video mode → 4/6/8s（10s 限 Omni）|
| **Frames to Video** | 首/尾幀框構圖 + 轉場 + 動畫化靜圖 | 拖圖到 +Add start frame / +Add end frame → prompt 寫兩幀間動作 |
| **Ingredients to Video** ⭐ | 餵參考（角色/物件/風格/產品）鎖跨鏡一致 = **Flow 版鎖形狀**，比 OiiOii i2v 更強 | 拖資產進 prompt box，**最多 3 個**；產品放純色/去背背景 |
| **Extend** | 延長 clip 保一致 | **僅 Veo 生成的影片**；extended clip 不能再套其他編輯 |
| **Scene Builder** | 多 clip 排序剪輯台 | clip「More→Add to Scene」→ 拖曳排序 + 修剪 → 預覽下載；**Jump To**=換場景保外觀 |
| **Camera Controls** | 運鏡（angles/dolly/zoom/tracking）| 透過 prompt 鏡頭語彙下達 |
| **Flow Agent** 🆕 | AI 創作夥伴：brainstorm/劇情建議/批次編輯/整理 collections | 影片拖進 prompt box 描述要改什麼，存進 asset stack 不丟原檔 |
| **Flow Tools** 🆕 | 自然語言「vibe code」自製工具（影片 resizer / 特效產生器）| Flow 內描述需求即建 |
| **Flow Music (Lyria 3 Pro)** 🆕 | AI 音樂，可單獨改某段/生替代版/翻譯歌詞 | 對 agent 用講的導演音樂影片 |
| **Flow TV** 🆕 | 精選 clip 展示牆，**每支可點「Show Prompt」看確切 prompt** = 學 prompt 神器 | labs.google/fx/zh/tools/flow/tv。⚠️ 2026-06-08 實測 feed 可能**空白**（顯示「此處似乎沒有任何內容」）→ 該帳號/地區當下無串流內容，逐片擷取要等有內容時。Show Prompt 是站內互動，爬蟲抓不到 |
| **生圖引擎** | Flow 內生圖 | Nano Banana 2（預設免費）/ Nano Banana Pro（Ultra）/ Imagen 4 |

### 🎯 Gemini Omni Flash in Flow（殺手鐧 = 對話式編輯）
- **切換：** 設定面板把 video model 切「Gemini Omni Flash」（需 AI Plus/Pro/Ultra；**免費額度只能跑 Veo 3.1**）。
- **Omni 獨家：** 10s clip（Veo 只 4/6/8s）、**Video-to-Video 編輯**、自訂語音、進階角色 reference。
- **對話式編輯流程：** model 設 Omni → 生成 base scene → **在同一 chat 接著講「換背景 / 改機位 / 套 cinematic zoom」** → 它只改不重跑 → **最多 3 輪 refine**。Edit & Refine 可上傳影片（最長 60s，剪到 30s 上限，選最多 10s 片段編輯）。
- **這原生解掉 OiiOii「加入對話≠i2v」的坑** —— Omni 的 reference 鎖造型 + 對話改場景是設計核心。

### Omni vs Veo 3.1 選型（Flow 內）
| 要 | 選 |
|---|---|
| 10s / 影片改影片 / 自訂語音 / 對話式迭代改 | **Gemini Omni Flash** |
| 4K 成品 / 純 t2v / 省 credit / 免費跑 / 拼長片 Extend | **Veo 3.1** |

### 訂閱 + credits（I/O 2026 後，數字待實機確認）
| 層 | 月費 | credits/月 | Omni Flash |
|---|---|---|---|
| Free | $0 | 少量 | ❌（只 Veo 3.1）|
| AI Plus | $7.99 | 200 | ✅ |
| AI Pro | $19.99 | 1,000 | ✅（Hao 持有）|
| AI Ultra | $100 | 10,000 | ✅ + 4K + Nano Banana Pro |
| AI Ultra 高 | $200 | 25,000 | ✅ 全含 |
- 原生 720p；1080p 升頻 Free/Pro 免費；4K 升頻約 50cr (待驗證)。Omni Flash 各時長 credit (15/20/25/30、edit 40) 為第三方數字**待 Flow 介面確認**。

### ✅ Omni Flash 文字渲染：短品牌名「可」渲染（2026-06-08 實測）

一般影片模型對文字 = 鬼畫符（見 quality-control §4），**但 Omni Flash 是例外**：用**引號標注 + 指定載體**（招牌/燈籠）成功渲染出店名「**Hao0321**」清楚可讀（毛筆字風格木招牌）。
- 寫法：`a glowing wooden sign clearly reads "Hao0321"`（引號 + 明確載體）
- 適用：**短英數品牌名/店名**（~7 字內）。長句、段落文字仍不可靠。
- x2 變體中通常至少一支文字到位 → 多生幾版挑。
- 仍不放心 → 走 image-logo（Ideogram/Nano Banana 做對招牌）→ Ingredients/Frames 帶入。但 Omni 一鏡直出短店名已可用。

### ⚠️ x2 可能 1 支成功 1 支被政策擋（2026-06-08 實測）

Omni Flash x2 變體中可能 **1 支正常、1 支跳「失敗：此生成內容可能違反政策」**（遊樂園 prompt 實測，疑似「delighted screams」「screams」等詞觸發）。應對：① 另一支通常 OK 直接用；② 失敗格有 retry/undo/delete 鍵；③ 想兩支都穩 → 移除可能踩線的詞（screams/violence/血腥/裸露/恐懼類）。**安全詞替代**：`delighted screams` → `cheerful laughter`、`excited cheering`。

### Flow 社群 prompt 技巧（X/Reddit/YouTube/官方彙整）
1. **Camera-first**：每個 prompt **開頭先寫鏡頭**（連「static, locked off」也要寫）—— 鏡頭定整支視覺文法。
2. **五要素 + 50-60 字**：Subject&Action / Composition&Camera / Environment&Mood（寫畫面感不只寫地點）/ Visual Style（具體如 stop motion）/ Audio。
3. **`@AssetName` 引用**：打 `@` 接已建資產名引用角色/物件（同 Seedance 概念），保跨鏡一致。
4. **跨鏡一致咒語**：明確叫 Gemini「**repeat all essential details from prior prompts**」複述前鏡關鍵細節。
5. **音訊當 sound designer**：別寫「cinematic score」，寫「a single low cello note building over 5s then cut to silence」。
6. **多輪 surgical 編輯**：每次編輯帶 **preserve 指令** 保留其他部分，把每次生成當草稿逐步改（Omni 原生支援）。
7. ⚠️ **t2v 要寫足視覺細節**（與 OiiOii i2v「不重述視覺」相反 —— 平台差異，分開記！Frames/Ingredients 模式才回到「視覺交給參考圖、prompt 重心運鏡」）。

### ✅ Live 實機驗證（2026-06-08，Hao Flow PRO 登入後實跑 Omni Flash）

**全程自動化跑通：新建專案 → 設定 Omni Flash → 注入 concept-first prompt → 送出 → x2 影片生成。** 實測 SOP：

```
1. 首頁 click「+ 新建項目」(~783,605) → URL 變 /project/{uuid}
2. 底部 prompt 框右側 click「視頻·10s·x2」設定 chip → 彈出設定面板：
   - 圖片/視頻 tab、幀/素材 子模式、9:16 / 16:9、x1-x4 輸出數
   - model dropdown（**Omni Flash 預設已選**，10s 預設）、4/6/8/10s 時長
   - 底部即時顯示「生成將消耗 N 個點數」
3. ✅ **Omni Flash 16:9 10s x2 = 30 點數**（live 確認，原研究待驗證數字解除）
   ⚠️ 此期間有「Omni Flash 半價 credits 限時優惠（~6/8）」，30 可能含折扣
4. Esc 關設定面板
5. ⚠️⚠️ **Flow prompt 框是 Slate，注入用「純 JS 完整聚焦序列」最可靠**（2026-06-08 二次驗證）：
   computer.left_click 座標**對不上**（見下 §座標陷阱），改用 JS：
   ```js
   const div = [...document.querySelectorAll('[contenteditable="true"]')].find(d=>d.getBoundingClientRect().width>100);
   div.dispatchEvent(new FocusEvent('focusin', {bubbles:true}));  // ← 關鍵，少這個會聚焦到 BODY
   div.focus();
   const target = div.querySelector('p, span, [data-slate-node]') || div;  // 選 inner node 不是 div
   const range = document.createRange(); range.selectNodeContents(target); range.collapse(false);
   const sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);
   // 等 150ms → 驗 document.activeElement 的 contenteditable==='true' → 再 beforeinput insertFromPaste
   ```
   驗證 `focusedAfterJS===true` + domLen 大增（實測 773）才算成功。
   ⚠️ **send 後必驗「生成真的啟動」**（2026-06-08 實測）：偶爾第一次 send 是 **no-op**（prompt 框清空了 domLen→13，但 canvas 沒出現 video placeholder、無 generating）= React state 沒登記。**應對：截圖/查 `videoEls` 確認有 placeholder；沒有就「重新注入 + 再 send」**（第二次通常成功）。別只看「框清空」就當送出成功。
   ⚠️⚠️ **2026-06-11 重要修正：新版 Flow 生成顯示在「所有媒體內容」gallery 的 tile（不是 canvas video placeholder），且 `videoEls`/body 文字關鍵字（生成/Generating/排队）偵測都抓不到** → **唯一可靠驗證 = 截圖看 gallery 出現新 tile**（生成中=灰漸層 shimmer tile，完成=縮圖）。多次「框清空但 JS 說沒 generating」其實**生成有 queue**（只是文字偵測失效）。**別因 JS 偵測失敗就重送**（會疊生成燒點數）—— 先截圖看 gallery tile。
   ⚠️ **注入用 `insertText`（模擬打字）比 `insertFromPaste` 對 Flow Slate 更穩**；注入後補一個 `input` event 推 React onChange。送出箭頭用 computer 真實 click（isTrusted）最穩。
6. send button：prompt 框右下，`aria-disabled="false"` 的 button（class 是 styled-components
   亂碼 sc-xxx，用「box 右緣 + 框內 y 範圍 + not disabled」定位，別靠 class）
7. 送出後 prompt 框清空 + canvas 出現 x2 影片佔位（shimmer loading）+ 左欄加「視頻」
8. Omni Flash 10s 生成約 1-3 分鐘
```

**Flow Slate 注入關鍵差異（vs OiiOii）：**
| | OiiOii | Flow |
|---|---|---|
| beforeinput 前需先 click 聚焦？ | 否（直接注入即可）| **是（必須先 computer.left_click 框）** |
| send button 定位 | `_send-button_`/`_credit-cost_` | styled-components 亂碼 class → 用位置+aria-disabled |
| 設定面板 | 底部 toolbar icon | prompt 框右側「視頻·10s·x2」chip |

**⚠️ 座標陷阱（2026-06-08 實測）：** Flow 頁面 **CSS 視窗 = 1920×919（dpr=1）**，但 Chrome MCP 截圖 = **1568×705** → x 縮放 1.224×、y 縮放 1.304×。**computer.left_click 用截圖座標會點錯位**（點 prompt 框結果聚焦 BODY）。生成後 prompt 框降到 CSS y≈809（截圖外）。**結論：Flow 的框互動一律走 JS（querySelector + 上面的聚焦序列），不要靠 computer.left_click 座標。** send button 也用 JS（位置 + aria-disabled）。

**生成後點到既有 clip 會開 /edit/{uuid} 編輯視圖**（有 timeline + Omni Flash「描述編輯需求」對話框 = 對話式編輯入口）；回專案點左上返回鍵。

**登入：** Flow session 會過期，重進停在 `accounts.google.com` 帳號選擇 → 用戶親自完成（Claude 不代登入）。登入後 URL = `labs.google/fx/zh/tools/flow`，首頁有「+ 新建項目」+ Flow TV/Discord/IG/X 頂欄連結 + PRO badge。

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
