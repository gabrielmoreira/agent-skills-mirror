# Site Profile: Ideogram 3

**URL:** `https://ideogram.ai/`
**驗證狀態:** ⏳ 未驗證 (stub — 操作時請邊做邊補)
**平台類型:** 生圖 (主打強文字渲染)
**Stack:** ⏳ 待確認

---

## 1. 整體 UI 地圖 (預期)

```
┌─ Header ──────────────────────────────────────────────┐
│ [Logo] [Generate] [Profile] [Subscribe]               │
├─ Sidebar ─┬───────── Feed / Generator ────┬─ Right ──┤
│ My Images │                                │ Settings │
│ Following │   [prompt + image grid]        │ Style    │
│ Trending  │                                │ Aspect   │
└───────────┴────────────────────────────────┴──────────┘
```

**核心模式：**
- **Generate** — 文生圖，主打強文字渲染 (海報 / 招牌 / Logo 文字準確)
- **Magic Prompt** — AI 自動加細節到你的 prompt
- **Style Reference** — 上傳 ref 圖固定風格
- **Remix** — 從別人的圖改 prompt

---

## 2. 主流程 Phase-by-phase (待實際操作補)

### Phase 0 — 登入 / 首頁
- ⏳ Google SSO / Email
- ⏳ 訂閱層級顯示
- ⏳ 月生成 quota 顯示位置

### Phase 1 — Generate 文生圖
- ⏳ Prompt textbox
- ⏳ Style preset (General / Realistic / Design / 3D / Anime)
- ⏳ Aspect ratio (1:1 / 16:9 / 9:16 / 多種)
- ⏳ Magic Prompt toggle (建議 OFF 給專業 prompt)
- ⏳ 一次出 4 張 (一般 grid)

### Phase 2 — Style Reference
- ⏳ 上傳 ref 圖入口
- ⏳ Reference weight 設定

### Phase 3 — 強文字 prompt
- ⏳ 文字內容用 quotes (`"Sale 50% Off"`)
- ⏳ 字體 / 顏色描述

### Phase 4 — 下載
- ⏳ 下載格式 (PNG / JPG)
- ⏳ Upscale 選項

---

## 3. 付費結構速查 (待補)

| 階段 / 功能 | 成本 | 驗證 |
|---|---|---|
| Free tier 月配額 | 25-100/天 | ⏳ |
| Basic $7/月 | 400 priority | ⏳ |
| Plus $16/月 | 1000 priority | ⏳ |
| Pro $48/月 | 3000 priority | ⏳ |

---

## 4. Click 策略備註 (待補)

- ⏳ ref 穩定度
- ⏳ Selected state 視覺
- ⏳ 文字 prompt 的 quotes 處理

---

## 5. 常見 toast / modal 速查 (待補)

| Toast / Modal | 意義 | 對策 |
|---|---|---|
| ⏳ 配額用完 | Free tier 上限 | 等下天 |
| ⏳ Magic Prompt 改寫提示 | AI 已加細節 | 接受或關掉 |

---

## 6. 快速決策樹

```
打開 Ideogram 要什麼？
├── 海報 / Logo / 招牌 (含文字) → Ideogram 主場
├── 多語言文字 (中文 / 日文) → Ideogram 較強 (vs MJ 弱文字)
├── 一般圖像 → 也行但 MJ / Flux 更美學
└── 同風格批次 → Style Reference + 連發
```

---

## 7. Workspace / 檔案保存機制 (待補)

- ⏳ My Images 永久保存
- ⏳ 公開 / 私人切換 (Free 預設公開)
- ⏳ 下載含浮水印？

---

## 8. 未驗證但值得注意 (下次操作補)

- ⏳ 中文 / 日文 / 韓文文字準確度
- ⏳ 一次出 4 張的 grid 是否能單獨選某一張下載
- ⏳ Free tier 圖是否強制公開
- ⏳ Magic Prompt 對專業 prompt 的影響 (建議 OFF)

---

## 9. ⚡ Chain Speed Optimization

### 通用最佳 SOP

**前置 (1 次)：** navigate + 1 screenshot 確認 UI

**每生成 N calls (理想 ≤ 5)：**
```
1. clear prompt field
2. focus prompt textbox
3. type <new prompt> (含 "quoted text" 若要文字)
4. click Generate (一次出 4 張)
[後續 batch screenshot]
```

**禁忌：**
- ❌ 中間每生成後 screenshot
- ❌ TodoWrite 每生成
- ❌ 開 Magic Prompt — 會改寫專業 prompt 浪費 quota

**驗證點 (僅 2 次)：**
- 第 1 生成後 1 screenshot 確認文字準確
- 全部完成後 1 screenshot

**內容長度建議：** Ideogram prompt 30-80 字 (含 "quoted text" 文字部分)

**並行 / 內建批次替代 chain？**
- **每次 Generate = 4 張同 prompt** → 5 個變體只需 5 次提交不是 20 次
- **Style Reference 一次設定後續同風格** → 跨 prompt 風格穩

**預期效能：** 5 個 prompt × 4 張 = 20 張 < 5 分鐘 + < 1.5k token

---

## 10. 版本與更新紀錄

- 2026-04-20：初始 stub 建立 (待實際操作驗證)
