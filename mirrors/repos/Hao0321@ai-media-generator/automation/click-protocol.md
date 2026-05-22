# 可靠 Click 協議 (Reliable Click Protocol)

**定位：** 瀏覽器自動化的 ≈ 80% 問題都是 **click 沒中** 或 **誤判狀態**。這份檔案是把 OiiOii demo 裡踩到的所有坑整合成可重複使用的 SOP。每個網站都套得上。

**核心原則：** 每個 irreversible action (click 生成按鈕、送出表單、確認付費) 都要 **先驗證 → 再執行 → 後驗證**。不要相信你以為的狀態，要相信 screenshot。

---

## Part 1 — Click 決策樹 (Decision Tree)

遇到「我需要點一個元素」時，依這個順序：

```
1. 是否有確定性連結 (href)？
   ├── 是 → 直接 navigate (最可靠，一步到位)
   └── 否 → 2

2. 是否有穩定 accessibility tree?
   ├── 是 (find 能穩定找到 + ref 短期有效)
   │   └── find → 立刻 left_click ref (中間不插螢幕截圖)
   └── 否 → 3

3. 是否能用座標？
   ├── screenshot → 目視定位元素中心 (x, y)
   │   → left_click coordinate → screenshot 驗證
   └── 坐標打不中 → 4

4. Fallback 連鎖：
   a. hover (x, y) 確認 cursor 在元素上 → left_click
   b. 改用 scroll_to ref 先把元素捲到 viewport 中心 → 再 click
   c. 用 keyboard Tab 跳到元素 → Enter
   d. 若都失敗 → **停下來問使用者** (不要亂戳)
```

---

## Part 2 — ref (accessibility reference) 的正確用法

### ref 的特性

- `find` / `read_page` 回傳的 `ref_N` 是 **該次查詢的短期快照**
- 多數網站 ref 有效 30 秒~幾分鐘；**React / Vue / tldraw 等動態渲染站** (如 OiiOii) ref 可能 **下一秒就失效**
- ref 失效的訊號：`"No element found with reference: 'ref_N'. The element may have been removed from the page."`

### ref 使用 SOP

**✅ 對：**
```
find "送出按鈕" → ref_42
left_click ref_42        # 立刻點
```

**❌ 錯：**
```
find "送出按鈕" → ref_42
screenshot               # ← 這一步可能讓頁面 re-render，ref_42 失效
zoom ...                 # ← 這一步也會
left_click ref_42        # 💥 "Element may have been removed"
```

### 原則
- **find → click** 中間 **不插螢幕截圖/zoom/read_page 以外的動作**
- 如果需要先看才能決定 click 哪個 → 用 screenshot 決定後 **用座標**，不要先 find 再拖延
- 如果一定要 read_page 拿結構 → read_page 回來後立刻 click，**不 screenshot 再 click**

---

## Part 3 — 座標 click 的精準技巧

### 座標系統

`computer.left_click coordinate=[x, y]` 使用的是 **viewport 座標**，而 screenshot 回傳常見 1568×751 或 1568×708。**多數環境中座標 ≈ screenshot 像素座標** (不需要手動 1920/1568 縮放)。實測：OiiOii 在 1568×708 的 (290, 410) 打中「中文」按鈕。

### 定位精度提升

**❌ 粗暴取中心：**
```
看起來按鈕在 (190, 205) → click (190, 205)  # 可能打到邊緣或 padding
```

**✅ 先 zoom 看清 hit area：**
```
zoom region=[x0, y0, x1, y1]  # 把按鈕放大
# zoomed image 顯示：按鈕視覺範圍 y 175-230，中心 y=203
# 按鈕實際可能有 4px 內距，實際 hit area 是 y 179-226
# 安全 click 在正中 y=203，x 同理
```

### 按鈕 hit area 經驗值

| 按鈕視覺大小 | 安全 click 區 |
|---|---|
| 40×40 px 小圖示 | 取視覺中心，誤差容忍 ±3 px |
| 100×40 px 文字按鈕 | 取中心，誤差 ±5 px |
| 大 CTA (400×50 px) | 中心 ±10 px 都 OK，但**避開按鈕邊界 5 px** |
| 卡片整塊可點 | 取卡片中心，不要點在卡片內文字上 |

### click 失敗的診斷

若 click 沒反應，**先排查這三件事再重點**：

| 症狀 | 原因 | 對策 |
|---|---|---|
| 點了毫無反應、UI 沒變化 | 座標在 padding 或透明 overlay | zoom 看實際 hit area，往中心挪 |
| 出現紅色錯誤 toast (如「選項暫不支援重選」) | 這個 action 已經送出過 | 不要再點，UI 已在下一階段 |
| 按鈕視覺變粉框但送不出 | 這是 selected state，不是 activated | 找真正的「送出/確認」按鈕再點 |
| 出現 paywall / modal 遮罩 | 有彈窗擋在按鈕上 | 先處理彈窗 (關閉或互動)，再回來 |
| 頁面在滾動中 | 元素位置漂移 | 先 `wait 1 秒` 或滾到停，再取 screenshot → click |

---

## Part 4 — 驗證狀態：Selected vs Hover vs Active

OiiOii demo 的關鍵誤判：**把 hover ring 當成 selected**，導致誤以為 click 沒中。

### 視覺狀態辨識

| 狀態 | 常見視覺 |
|---|---|
| **Unselected / default** | 淡色背景、默認邊框 |
| **Hover (focus ring)** | **粉色 / 亮色外圈 ring**，但背景還是默認色 |
| **Selected / committed** | **填底色變深** (或變 brand 色)，邊框也可能變色 |
| **Disabled** | 灰化 + 降透明度 |
| **Active (正在點擊)** | 短暫的按下陰影，1 幀 |

### 驗證選中的 SOP

click 後 **必做**：
```
1. screenshot (或 zoom 該按鈕區域)
2. 看填底色是否變深 / 變 brand 色
3. 若填底沒變 → click 沒中 → 回 Part 3 重試
4. 若填底有變、但下一步 UI 沒出現 → 正常的「agent 背後處理」，等 60-90s 再看
```

### Selected 的其他信號

- 按鈕旁/底部出現「小型確認泡泡」(OiiOii 的粉色氣泡) — 這是系統訊息，強指標
- Checklist 項目加 ✓ (綠勾)
- 右下/左下 toast 提示「已送出」「信息已確認」
- URL 改變 (跳到 `/space/xxx` 之類)

---

## Part 5 — Scroll-aware 座標 (對抗漂移)

### 漂移現象

長對話或動態 panel 裡，同一個按鈕的 (x, y) 會因 scroll 位置變化。實測 OiiOii 的「滿意」按鈕 y 在 385 → 573 → 428 之間來回漂。

### 對策

**Rule of thumb：每次要 click 按鈕，前 5 秒內必須有 screenshot 驗證該按鈕的當前 y 座標。**

```
BAD:
  screenshot -> see button at y=428
  scroll down 10 ticks
  click (290, 428)   # ❌ y 已經變了，打到別處
  
GOOD:
  scroll down 10 ticks
  screenshot           # 必須重照
  see button at y=290 # 位置變了
  click (290, 290)     # ✓
```

### 避免漂移的招

- **不要在 panel 中隨便 scroll** — 只有在要看 above/below 的內容才 scroll
- **click 前不滾動** — 若一定要滾，滾完立刻 screenshot
- **固定位置按鈕**：有些按鈕是 sticky (如底部 submit bar)，這類座標穩定

---

## Part 6 — 文字輸入的陷阱

### 輸入框類型判斷

| HTML 元素 | form_input 支援 | 對策 |
|---|---|---|
| `<input>` / `<textarea>` | ✓ 支援 | 用 form_input |
| `contentEditable DIV` | ✗ 不支援 (回錯: "Element type DIV is not a supported form input") | `computer.left_click` → `computer.type` |
| Rich text editor (Slate, Quill, Lexical, tldraw) | ✗ 不支援 | 同上 |
| 部分 React controlled input | ✗ 可能失敗 | fallback 到 click + type |

### 輸入前後的驗證

```
1. screenshot → 確認輸入框位置 + 目前內容
2. left_click 輸入框中心 → cursor 進入
3. 若要清空先存 → ctrl+a (select all) → Delete
4. type "內容"
5. screenshot 驗證文字已進入
```

### Enter 鍵陷阱 (很重要)

- **很多網站 prompt 框在 contentEditable 模式下，`\n` 會觸發送出** (OiiOii、ChatGPT、Claude.ai 都是這樣)
- 若你 type 的文字含 `\n` → 會在 `\n` 處立刻送出，而且內容可能被截斷
- **對策**：
  - 若要送出：把完整文字一次 type (含 `\n`)，**最後一個 `\n` 就是送出鍵**
  - 若不想送 (只想存草稿)：用 Shift+Enter 或 `<br>` 或拆成多次 type 中間用 arrow key 移動
  - **若不確定**：先試一行短文字、不含 `\n`，觀察 UI 反應

---

## Part 7 — Paywall / Modal / Popup 偵測

### 徵兆

- 原本 active 的按鈕 click 完全沒反應
- 畫面出現新的 overlay、lightbox、彈窗
- 右下或中央冒出 toast: 「模型稍貴」、「升級」、「限制」
- 按鈕周圍出現 $ / 鎖頭 / 皇冠圖示

### SOP

```
1. 看到 click 無效 → screenshot → 辨識是否有 modal
2. 若有 paywall modal → 立刻停下，向使用者報告
3. 不要試圖繞過 paywall (安全規則)
4. 寫進 site profile 的 "已知付費點" 清單
```

### 常見付費點 (見 site profile)

- OiiOii: 分鏡師 → 影片生成 = $7
- Suno: 分段 stem 下載 = Pro
- Runway: 4K 輸出 = 訂閱升級
- Midjourney: 所有生成 = 訂閱 (無免費)

---

## Part 8 — 等待策略 (Polling)

### 正確的等待節奏

| 情境 | 建議節奏 | 為什麼 |
|---|---|---|
| 互動 UI 會出現 (agent 問問題) | **60 秒** 一次 screenshot | 不要錯過互動時機 |
| Agent 背後處理 (沒 UI 變動期) | 每 3-5 分鐘 一次 | 省 token，快來早也沒用 |
| 上傳 / 下載中 | 每 30 秒 | 變化較快 |
| 影片生成中 (5-15 min 長任務) | 每 3 分鐘 | 適度 |

### ScheduleWakeup 最小 60 秒

runtime hard clamp：`[60, 3600]` 秒。**10 秒 polling 不可能**，使用者若要求這麼快，解釋限制並使用 60s。

### 「不動 ≠ 卡住」的辨識

**看起來卡住但沒卡：**
- UI 靜止 + 「工作中...」spinner 還在轉 → 正常，agent 在背後跑
- Checklist 沒加新項目 → 可能跑慢，再等 3-5 分鐘
- 代幣沒扣 → 可能前期階段不計費

**真的卡住：**
- Checklist 倒退 / 變灰
- 紅色錯誤 toast (非「選項暫不支援重選」這種正常提示)
- 「工作中」消失但沒新內容
- 15 分鐘+ 完全沒進度

真卡住的對策：
1. screenshot 記錄狀態
2. 保留 URL (site profile 下次繼續用)
3. 考慮 reload 頁面 (有些網站 reload 會從最後狀態恢復)
4. 告訴使用者，別硬 retry

---

## Part 9 — 驗證循環 (Verification Loop)

**這是 reliability 的核心模式**：

```
for each irreversible action:
    1. BEFORE screenshot    # 記下起始狀態
    2. Execute action       # click / type / navigate
    3. AFTER screenshot     # 記下結束狀態
    4. Diff:
       - UI 有變化？(selected 色改變、toast 出現、URL 變) → ✓
       - UI 無變化？→ action 沒生效，回 Part 3 debug
    5. 若 ✓ → 下一步
    6. 若 ✗ → fallback chain，最多 2 次，還不行停下問使用者
```

這個 pattern 防止兩種常見失敗：
- **Silent failure** (click 沒中但不報錯)
- **Double commit** (看 UI 沒變就再點，結果兩次都中，導致重複操作)

---

## Part 10 — 速度優化 (Speed)

### 合併可平行的操作

**慢 (串行)：**
```
click A → screenshot → click B → screenshot → click C
```

**快 (批次)：**
```
click A
click B         # (同一 tool_use block)
click C
screenshot      # 一次看結果
```

**但注意：** 只有 **互不影響** 的 click 能平行。依序 click 3 個 radio (要前一個完成才能點下一個) 則不能平行。

### 減少 screenshot 次數

每次 screenshot 消耗 tokens 且花時間 (~1-2 秒)。原則：
- 一組連續 click 只在**最後**驗證一次
- 長等待中每 60-90 秒一次就夠
- zoom 比 full screenshot 省 tokens (看小範圍)

### 平行 tool call

一個 message 多個 tool call = 平行執行。特別適合：
- 「同時讀檔 + 截圖」
- 「同時 edit 兩個不同檔案」
- 「同時 find + navigate」

不適合：
- 「先 find ref 再 click ref」(必須串行)

---

## Part 11 — 常見失敗 Pattern 速查表

| 症狀 | 最可能原因 | 立即對策 |
|---|---|---|
| "Element may have been removed" | ref 已失效 | 重 find，立刻 click |
| click 毫無回應 | 座標偏、paywall、disabled | screenshot 檢查狀態 + 重 zoom |
| 按鈕變粉色但下一頁沒來 | 是 hover 不是 selected | 看填底色變化 |
| UI 靜止 > 5 分鐘 | 可能真卡住 | reload 或問使用者 |
| 紅 toast「選項暫不支援重選」 | action 已送出過 | 停點、UI 已在下階段 |
| 打字被截斷送出 | `\n` 觸發送出 | 避免換行或用 Shift+Enter |
| 跑出 paywall / 升級彈窗 | 碰到付費牆 | 停下問使用者 |
| click 座標偏了幾 px 就不中 | hit area 小於視覺 | zoom 看實際範圍 |
| 連續點兩次錯開位置 | scroll 造成漂移 | 每次 click 前 screenshot |

---

## 給 Claude：進入瀏覽器操作時的 Mental Model

1. **不信任「我記得按鈕在 (x, y)」** — 5 秒前的 screenshot 可能已過期
2. **不信任 ref 能活過 2 個 tool call** — find 完立刻 click
3. **不信任「看起來選中了」** — 要看填底色，不是邊框
4. **不信任 click 真送出了** — 一定要 after-screenshot 驗證
5. **不信任廠商 API 永遠穩定** — 網站每週改版，`site-profiles/` 每次用前先驗證

---

## ⚡ Token + 時間最佳化 (2026-04-20 慘痛教訓)

### Meta 優先序（2026-04-21 補充：**比操作手速更重要**）

User 試了 4 次 Seedance 戰鬥生成才出來，抱怨「2:50 花 500 token」。回推根因不是**手速慢**，是**第一次寫錯 prompt 導致重做**。

**速度優化真正的優先序：**

| 優先序 | 優化點 | 省多少時間 |
|---|---|---|
| 🥇 **1. Prompt 寫對一次** | 查 [../references/community-prompt-patterns.md](../references/community-prompt-patterns.md) 目標模型簽名 | 避開 1 次重做 = **10 分鐘** |
| 🥈 **2. 單次提交極速化** | site-profile 座標 + 中間 0 screenshot | 5 min → 25 秒 = **4.5 分鐘** |
| 🥉 **3. 等待不 polling** | `Bash run_in_background:true + sleep 400` | 省 poll 開銷 = **幾百 token** |

**順序反了的代價：** 這次 session 跑 4-5 次 Seedance 才成功 = 浪費 40+ 分鐘 + 數千 token。**寫對 prompt 一次能省 1 小時**。

**下次操作前自檢：**
1. ✅ 查過 community-prompt-patterns.md 對應模型章節？
2. ✅ 避開該模型禁忌（導演名？多動詞？fast？chaotic wide？）
3. ✅ 長度在甜蜜點？
4. ✅ 只 3 個答 yes 都不夠，回去改。

---

### Chain workflow 的浪費點：

### 4 大浪費 + 修法

| 浪費 | 症狀 | 修法 |
|---|---|---|
| 每 action 後 screenshot | 1.5k token/張 × 8+ 張 = 12k+ 浪費 | **chain 中只在第一次 + 最後一次 screenshot**；中間相信座標 |
| TodoWrite 每任務一次 | 300 token × 5 = 1.5k 浪費 | **chain 是線性，跑完一次更新就好** |
| 多步 clear (triple-click + Ctrl+A + Delete) | 3 個 tool call 變 3× | **找垃圾桶 / 重設按鈕，1 個 click 解決** |
| 內容寫太長 (歌詞 50 行 vs 25 行) | type 翻倍 | 抓**標準長度**，多寫無加分 |

### 黃金法則

> **Chain workflow ≠ 連續單任務**。連續單任務每個都 verify；chain 第一個 verify 完，後面相同 UI 就 trust + go。

**驗證頻率：**
- ✅ Chain 第一個 task 後 1 張 screenshot (確認座標 / credits / 提交成功)
- ✅ Paywall 出現時 screenshot (decision point)
- ✅ Chain 全部跑完 1 張 screenshot (final verify)
- ❌ 中間每 task 都 screenshot (浪費)

**clear 欄位優先順序：**
1. **垃圾桶 / Reset / Clear icon** (1 click) — 最快
2. **form_input ref ""** (1 call) — 次快
3. triple_click → type 新內容 (replace) — 中等
4. ❌ triple_click → Ctrl+A → Delete → type — 最慢，**禁用**

**TodoWrite 使用：**
- ✅ 多階段非線性 (research → plan → impl → test) — 用
- ✅ User 給 5+ 不同任務清單 — 用
- ❌ 同一個 chain 跑 N 次 (做 5 首歌、5 張圖) — **不用**，跑完一次更新

---

## 跟 [browser-guide.md](browser-guide.md) 與 site-profiles/ 的關係

- **本檔 (click-protocol.md)**：通用 SOP、decision tree、失敗模式。**所有網站都適用**。
- **browser-guide.md**：平台速查 — 每個站的登入 / 主流程簡述
- **site-profiles/*.md**：特定網站的深度 profile — UI 地圖、已知座標、gotchas

遇到問題查詢順序：
1. 先看 **site-profile** (該站特有的 gotcha 可能直接有答案)
2. 再看 **click-protocol** (通用 SOP)
3. 最後看 **browser-guide** (流程概述)
