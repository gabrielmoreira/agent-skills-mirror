# Site Profile: Midjourney v7

**URL:** `https://www.midjourney.com/imagine` (Web UI) / Discord `#newbies-N` 頻道
**驗證狀態:** ⏳ 未驗證 (等使用者實際操作補)
**平台類型:** AI 圖像生成 (2026-04 主力 v7)
**Stack:** Web React / Discord bot

---

## 1. 兩種使用模式

| 模式 | URL / 位置 | 優勢 |
|---|---|---|
| **Web UI** | `https://www.midjourney.com/imagine` | 現代介面、操作直覺 |
| **Discord** | Discord 頻道內 `/imagine prompt: XXX` | 老派、社群感、有些進階功能先在 Discord 上 |

**Web UI 是首選** — Auto-Pilot 預設走 Web。

## 2. 登入

- 需要 **Midjourney 訂閱** ($10/月起 Basic Plan)
- Discord 帳號連結 (即使用 Web 也要)
- **免費額度：** 沒有 (V5 時代過後取消了)

## 3. 預期 UI (Web 版)

### 主頁 `/imagine`
- 頂部大 prompt 輸入框 (placeholder「What do you want to see?」)
- 右側參數面板：
  - **Version** (v7 / v6 / Niji 7)
  - **Stylize** (`--s`)
  - **Aspect Ratio** (`--ar`)
  - **Weird** (`--weird`)
  - **Raw Mode** (toggle `--raw`)
  - **Personalization** (`--p` 若已 unlock)
  - **Style Reference** (`--sref`) 上傳或輸入 code
  - **Omni Reference** (`--oref`) 上傳角色圖
- 下方網格顯示生成結果
- 每個生成可 Upscale (U1/U2/U3/U4) / Vary (V1/V2/V3/V4) / Re-roll

## 4. Phase-by-phase (TBD)

### Phase 1 — 登入
⏳ Google / Discord / Apple

### Phase 2 — prompt 輸入
⏳ 大 prompt 框，text-based (可能支援 markdown)
**格式** (from [../../references/midjourney.md](../../references/midjourney.md))：
```
[Subject], [environment], [style], [composition], [lighting], [mood/detail]
--ar 16:9 --s 250 --v 7
```

### Phase 3 — 進階 refs 欄位
⏳ 需點某按鈕展開
- `--sref` 圖或 code
- `--oref` 圖 + `--ow` 強度
- `--profile` (personalization)

### Phase 4 — 送出
⏳ Enter 或某 button

### Phase 5 — 網格結果 (4 張)
⏳ v7 預設輸出 4 張
- Upscale / Vary / Re-roll 選項

### Phase 6 — 下載 / 儲存
⏳ 單張點擊開全尺寸，右鍵 / 下載按鈕

---

## 5. v7 專屬注意 (重要)

- `--cref` **v7 已失效** — 要用 `--oref` 替代角色一致性
- `--oref` 預設 `--ow 100` 通常不夠，調 **300-600**
- **Personalization (`--p`)** 需先到 `https://midjourney.com/rank-v7` 評 ~200 張解鎖
- 多重 `--sref` 加權：`--sref 111 222 333`

---

## 6. 預期陷阱

- 還在用 `--cref` 做 v7 角色 → 無效，改 `--oref`
- Stylize 拉到 1000 做寫實 → 矛盾，寫實走 `--raw --s 50`
- 多個衝突參數 (`--niji 7 --raw`) → raw 和 niji 設計衝突，選一個
- prompt 太囉嗦完整句子 → MJ 喜歡堆疊形容詞；句子只要 1-2 個
- `--oref` 不加 `--ow` → 權重 default 100 通常不夠

## 7. Auto-Pilot 進 Midjourney 時

**Intent Parser 特化：**
- 偵測「插畫 / 藝術 / 美感」→ 首選 Midjourney
- 解析角色一致性需求 → 自動加 `--oref URL --ow 400`
- 解析「寫實」→ `--raw --s 50-100`
- 解析「動漫」→ 切 `--niji 7 --s 300`

---

## 8. 版本與更新紀錄

- **2026-04 (stub)：** 建立 profile 架構，等實測補 Phase 2-6 座標

---

## 9. ⚡ Chain Speed Optimization (MJ 多 prompt 批次)

**MJ 強項：可並行送多 prompt，每個 4 張，速度極快。**

### 最佳 chain SOP (每 prompt 3-4 calls，10 prompt = 35 calls)

**前置 (1 次)：** navigate to alpha.midjourney.com/imagine + 1 screenshot

**每 prompt 3-4 calls：**
```
1. left_click <imagine bar>    → focus 頂部 imagine 輸入框
2. key ctrl+a                  → 全選 (清空)
3. type <new prompt --params>  → 一次貼 (含 --niji/--raw/--ar/--s/--oref)
4. key Enter                   → 送出 (MJ 用 Enter 觸發)
```

**禁忌：**
- ❌ 中間 screenshot — MJ UI 極穩
- ❌ TodoWrite 每 prompt
- ❌ 用 Draft Mode 然後再 upgrade — chain 應一次到位用 Quality

**並行優勢：** MJ Pro/Mega 支援 12 jobs 並行 — 連送 12 個 prompt 後再 batch screenshot 看結果。

**驗證點 (2 次)：**
- 全部送完 1 screenshot 確認佇列
- 完成後 1 screenshot 抓圖

**內容長度：** MJ prompt 是 keyword stack 不是句子，30-50 字 token-stack 最佳，超過會稀釋。

**預期效能：** 10 prompts (40 張圖) < 3 分鐘送出 + < 1.2k token
