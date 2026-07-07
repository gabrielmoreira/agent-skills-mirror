# Site Profile: Runway

**URL:** `https://app.runwayml.com/`
**驗證狀態:** ⏳ 未驗證 (stub — 操作時請邊做邊補)
**平台類型:** 生影片 + 編輯 (多功能 AI video studio)
**Stack:** React-based studio，左 panel + 中央 canvas + 右屬性

---

## 1. 整體 UI 地圖 (預期)

```
┌─ Sidebar ──┬─────── Canvas / Timeline ──────┬─ Properties ─┐
│ - Gen-4    │                                │              │
│ - Aleph    │      [video preview]           │ Gen-4: refs  │
│ - Act-Two  │                                │ duration     │
│ - Frames   │                                │ camera       │
│ - Assets   │                                │              │
└────────────┴────────────────────────────────┴──────────────┘
```

**核心模式：**
- **Gen-4 Turbo** — 文生影片 / I2V，5-10s
- **Gen-4 References** — 上傳 1-3 張 ref 圖保持角色/物件一致 (3 張一次)
- **Aleph** — 影片轉影片 (V2V)，加效果/換風格/換背景
- **Act-Two** — Motion capture：上傳你的人物影片作為動作 source，套到任何角色上
- **Frames** — 影片內畫面編輯 (類似 Photoshop for video frames)

---

## 2. 主流程 Phase-by-phase (待實際操作補)

### Phase 0 — 登入 / 首頁
- ⏳ 確認 SSO 入口
- ⏳ 代幣顯示位置
- ⏳ 各模式入口 (Gen-4 / Aleph / Act-Two)

### Phase 1 — Gen-4 文生影片
- ⏳ Prompt textbox 位置
- ⏳ Duration 選項 (5s / 10s)
- ⏳ Aspect ratio 選項
- ⏳ Generate 按鈕

### Phase 2 — Gen-4 References (一致性)
- ⏳ 上傳 3 張 reference 圖入口
- ⏳ 每張 ref 的 weight / role 設定
- ⏳ Prompt 怎麼引用 ref (`@ref1`?)

### Phase 3 — Act-Two (Motion Capture)
- ⏳ 上傳 driver video (你的動作)
- ⏳ 上傳 character (要套動作的角色)
- ⏳ 是否需 face mesh / body pose 校準
- ⏳ 輸出長度上限

### Phase 4 — 等待 + 下載
- ⏳ Generation 時長 (Gen-4 Turbo ~30s? Aleph ~2 min?)
- ⏳ 結果預覽位置
- ⏳ 下載格式選項 (MP4 / ProRes?)

---

## 3. 付費結構速查 (待補)

| 階段 / 功能 | 成本 | 驗證 |
|---|---|---|
| Gen-4 Turbo 5s | ? credits | ⏳ |
| Gen-4 References | ? credits | ⏳ |
| Aleph V2V | ? credits | ⏳ |
| Act-Two (高級) | ? credits | ⏳ |
| 月訂閱 Pro | $35? | ⏳ |
| 月訂閱 Unlimited | $95? | ⏳ |

---

## 4. Click 策略備註 (待補)

- ⏳ ref 穩定度
- ⏳ Selected state 視覺
- ⏳ 已知 hit area 小的按鈕

---

## 5. 常見 toast / modal 速查 (待補)

| Toast / Modal | 意義 | 對策 |
|---|---|---|
| ⏳ Out of credits | 付費牆 | 停手提示用戶 |
| ⏳ Generation queued | 排隊 | 等待 |

---

## 6. 快速決策樹

```
打開 Runway 要什麼？
├── 文生影片短片 → Gen-4 Turbo
├── 同角色多場景 → Gen-4 References (3 圖一次)
├── 影片加特效 / 換風格 → Aleph
├── 套動作到角色 → Act-Two (mocap)
└── 編輯影片內畫面 → Frames
```

---

## 7. Workspace / 檔案保存機制 (待補)

- ⏳ Generations 是否永久保存？
- ⏳ 下載格式
- ⏳ 是否能從 URL 直接返回某個生成

---

## 8. 未驗證但值得注意 (下次操作補)

- ⏳ Gen-4 References 的 3 張 ref 上限 (Vidu Q3 是 4 張)
- ⏳ Act-Two 是否需 consent 流程
- ⏳ Aleph 結果是否能餵回 Gen-4 做下游處理
- ⏳ 是否有 Multi-Shot 一次出多鏡 (節省 chain)

---

## 9. ⚡ Chain Speed Optimization

### 通用最佳 SOP

**前置 (1 次)：** navigate + 1 screenshot 確認 UI

**每生成 N calls (理想 ≤ 7)：**
```
1. clear prompt field (1-click 用 trash icon / 或 ctrl+a 覆寫)
2. focus prompt textbox
3. type <new prompt>
4. (若 References 模式) 上傳 ref 圖
5. click Generate
[後續 batch screenshot]
```

**禁忌：**
- ❌ 中間每生成後 screenshot — 浪費 1.5k token/張
- ❌ TodoWrite 每生成 — chain 完成後一次性更新
- ❌ 多步 clear — 用 1 步

**驗證點 (僅 2 次)：**
- 第 1 生成後 1 screenshot 校準
- 全部完成後 1 screenshot 確認

**內容長度建議：** Gen-4 prompt 60-100 字 (含 cinematic tokens)

**並行 / 內建批次替代 chain？**
- **Gen-4 References 一次 3 張 ref** → 比 3 次 chain 省 60%
- ⏳ 是否有 batch generate 多個 prompt 一次 (待驗證)

**預期效能：** 5 生成 < 5 分鐘 + < 1.5k token

---

## 10. 版本與更新紀錄

- 2026-04-20：初始 stub 建立 (待實際操作驗證)
