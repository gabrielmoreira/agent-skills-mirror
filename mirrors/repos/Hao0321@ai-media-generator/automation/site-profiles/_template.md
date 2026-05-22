# Site Profile: [網站名]

**URL:** `https://...`
**驗證狀態:** ⏳ 未驗證 / ✅ 已驗證 YYYY-MM-DD / ⚠️ 部分驗證
**平台類型:** (生圖 / 生影片 / 生音樂 / 多功能 / 編輯)
**Stack:** (若已知：React / Vue / plain / canvas-based 等，影響 ref 穩定度)

> 這是一個 site profile 的模板。複製一份改名為 `<platform>.md`，填入實際觀察。未驗證的區塊寫 `⏳ TBD`。

---

## 1. 整體 UI 地圖

(截圖描述 + ASCII 示意)

```
┌─ 描述主要區塊 ─┐
│                │
└────────────────┘
```

**關鍵：** (這個站的 UI 核心概念，如「左 chat 右畫布」/「頂部模式切換」等)

---

## 2. 主流程 Phase-by-phase

### Phase 0 — 首頁 / 登入狀態

- URL: `...`
- 關鍵元素：
  - 登入按鈕 / 用戶頭像 (確認已登入的 indicator)
  - 代幣/計費顯示位置
  - 主 CTA 按鈕

### Phase 1 — (第一個互動動作)

**步驟：**
1. (第一步)
2. ...

**互動元素：**
| 元素 | 座標 (1568×?) 或 ref 慣例 | 備註 |
|---|---|---|
| | | |

**陷阱：**
- (該站特有的坑)

### Phase 2 — ...

(同上格式)

---

## 3. 付費結構速查

| 階段 / 功能 | 成本 | 驗證 |
|---|---|---|
| 生成一張圖 | ? | ⏳ |
| 生成一段影片 | ? | ⏳ |
| 訂閱 / 月費 | ? | ⏳ |

---

## 4. Click 策略備註

- ref 穩定度：(高/中/低)
- 座標系：(screenshot = viewport ≈ 1:1 / 需要縮放)
- Selected state 視覺：(填底 / 粉色 ring / 勾選 icon)
- 已知 hit area 小的按鈕：(列出)

---

## 5. 常見 toast / modal 速查

| Toast / Modal | 意義 | 對策 |
|---|---|---|
| | | |

---

## 6. 快速決策樹

```
打開這個站要什麼？
├── 任務 A → 流程 A
├── 任務 B → 流程 B
└── 任務 C → 流程 C
```

---

## 7. Workspace / 檔案保存機制

- 生成結果是否永久保存？
- 有無 URL 固定可返回？
- 下載格式與管道？

---

## 8. 未驗證但值得注意的行為

(下次操作時檢查並補進來)

- ⏳ ...
- ⏳ ...

---

## 9. ⚡ Chain Speed Optimization (必填)

> **強制：** 所有 site profile 都必須有這節。chain workflow (連跑多任務) 不照辦會浪費 70% token。

### 通用最佳 SOP (改成本站專屬)

**前置 (1 次)：** navigate + 1 screenshot 確認 UI

**每任務 N calls (理想 ≤ 7)：**
```
1. clear field (1-click 用 trash icon / 或 ctrl+a 覆寫)
2. focus prompt textbox
3. type <new prompt>
4. click 送出按鈕
[後續 batch screenshot]
```

**禁忌：**
- ❌ 中間每 task 後 screenshot — 浪費 1.5k token/張
- ❌ TodoWrite 每 task — chain 完成後一次性更新即可
- ❌ 多步 clear (triple_click + Ctrl+A + Delete) — 用 1 步

**驗證點 (僅 2 次)：**
- 第 1 task 後 1 screenshot 校準
- 全部完成後 1 screenshot 確認

**內容長度建議：** (本站 prompt 標準長度，多寫無加分)

**並行 / Series 替代 chain？** (若本站有 Series Mode / Multi-Shot / Multi-Reference 一次出多個，**優先用內建批次** 而非 N 次 chain)

**預期效能：** N task < X 分鐘 + < Y token

---

## 10. 版本與更新紀錄

- YYYY-MM-DD：(操作紀錄，更新了什麼)
