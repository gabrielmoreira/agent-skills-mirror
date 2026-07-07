# Site Profile: Sora 2

> 🔴 **平台已停運（2026-06）— 此 profile 僅供歷史參考，勿用於自動化。**
> OpenAI 宣布退役 Sora：**Web/App 2026-04-26 關閉**、**API 2026-09-24 關閉**。
> `sora.com` + iOS/Android App 已無法操作 → **不要嘗試導航/登入/click**。
> 要用 Sora 只剩第三方代理 API（fal.ai / Replicate / Azure AI Foundry），時效到 2026-09-24。
> 新專案請改用現役模型。完整說明見 `references/sora.md` §平台狀態警告。

**URL:** `https://sora.com/` (或 `https://chat.openai.com/sora`) — ⛔ 已關閉
**驗證狀態:** 🔴 平台停運，stub 不再續補
**平台類型:** 生影片 (OpenAI 文生影片)
**Stack:** OpenAI 自建 React，曾需 ChatGPT Plus / Pro 訂閱

---

## 1. 整體 UI 地圖 (預期)

```
┌─ Sidebar ─┬──────── Feed / Editor ────────┬─ Inspector ─┐
│ Explore   │                                │ Style       │
│ Library   │   [video preview / prompt]     │ Cameo       │
│ Cameos    │                                │ Duration    │
│ Drafts    │                                │ Aspect      │
└───────────┴────────────────────────────────┴─────────────┘
```

**核心模式：**
- **Sora 2** — 文生影片，up to ~20s (Pro 可能更長)
- **Cameo** — 上傳一次 5-30 秒自己的 video + audio，存成 character，未來可入鏡任何 prompt
- **Remix** — 從別人 / 自己的 generation 改 prompt 變奏
- **Storyboard** (?) — 多 shot 規劃

---

## 2. 主流程 Phase-by-phase (待實際操作補)

### Phase 0 — 登入 / 首頁
- ⏳ ChatGPT Plus / Pro 帳號入口
- ⏳ Plus = ? 月、Pro = ? 月
- ⏳ Plus 月生成上限、Pro 月生成上限

### Phase 1 — 文生影片
- ⏳ Prompt textbox 位置
- ⏳ Style preset (cinematic / anime / photoreal?)
- ⏳ Duration 選項 (5 / 10 / 20s?)
- ⏳ Aspect ratio (16:9 / 9:16 / 1:1)

### Phase 2 — Cameo 建立 / 使用
- ⏳ 建立 Cameo: 上傳 video 5-30s + 你的聲音
- ⏳ Sora consent flow (深偽防範)
- ⏳ 自動加水印確認
- ⏳ Cameo 怎麼引用入 prompt (`with @MyCameo as protagonist`?)

### Phase 3 — 等待 + 下載
- ⏳ Generation 時長
- ⏳ 結果在 Library / Drafts 哪裡
- ⏳ 下載格式 (MP4 / 包含水印的版本)

---

## 3. 付費結構速查 (待補)

| 階段 / 功能 | 成本 | 驗證 |
|---|---|---|
| Plus 月費 | $20 | ⏳ |
| Pro 月費 | $200 | ⏳ |
| Plus 月生成 limit | ? 個 | ⏳ |
| Pro 月生成 limit | unlimited? | ⏳ |
| Cameo 建立 | 包含 | ⏳ |
| 高解析下載 | Pro only? | ⏳ |

---

## 4. Click 策略備註 (待補)

- ⏳ ref 穩定度
- ⏳ Selected state 視覺
- ⏳ OpenAI UI 一致性，可能 ref 比較穩

---

## 5. 常見 toast / modal 速查 (待補)

| Toast / Modal | 意義 | 對策 |
|---|---|---|
| ⏳ 月配額用完 | 等下月或升級 | 停手提示用戶 |
| ⏳ Cameo consent 跳出 | 安全機制 | 必須使用者本人確認 |
| ⏳ 內容違規 | OpenAI 審查 | 改 prompt |

---

## 6. 快速決策樹

```
打開 Sora 2 要什麼？
├── 短影片 (<20s)，文字 → 直接 Sora 2
├── 把自己拍進場景 → 先建 Cameo → 引用
├── 改別人的 generation → Remix
└── 多鏡故事 → Storyboard 模式 (待驗證)
```

---

## 7. Workspace / 檔案保存機制 (待補)

- ⏳ Library 是否永久保存
- ⏳ Cameo 永久保存
- ⏳ 公開 / 私人 generation 切換

---

## 8. 未驗證但值得注意 (下次操作補)

- ⏳ Cameo 建立 一次 vs 多次 (能否更新 / 刪除)
- ⏳ 安全水印是否影響使用 (商業可用?)
- ⏳ 是否有 API (OpenAI 是否開放 Sora API)
- ⏳ Pro 是否解鎖更長影片 / 高解析

---

## 9. ⚡ Chain Speed Optimization

### 通用最佳 SOP

**前置 (1 次)：** navigate + 1 screenshot 確認 UI

**每生成 N calls (理想 ≤ 6)：**
```
1. clear prompt field (1-click 用 trash icon / 或 ctrl+a 覆寫)
2. focus prompt textbox
3. type <new prompt>
4. (若用 Cameo) 確認 cameo 已選
5. click Generate
[後續 batch screenshot]
```

**禁忌：**
- ❌ 中間每生成後 screenshot — 浪費 1.5k token/張
- ❌ TodoWrite 每生成 — chain 完成後一次性更新
- ❌ Cameo 重複建立 — 一次建好重用

**驗證點 (僅 2 次)：**
- 第 1 生成後 1 screenshot 校準
- 全部完成後 1 screenshot 確認

**內容長度建議：** Sora prompt 60-120 字 (含 cinematic tokens)

**並行 / 內建批次替代 chain？**
- **Cameo 一次建立永久重用** → 100% 省同角色 chain
- **Storyboard 模式 (若有) 一次出多鏡** → 待驗證

**預期效能：** 5 生成 < 8 分鐘 (Sora 較慢) + < 1.5k token

---

## 10. 版本與更新紀錄

- 2026-04-20：初始 stub 建立 (待實際操作驗證)
