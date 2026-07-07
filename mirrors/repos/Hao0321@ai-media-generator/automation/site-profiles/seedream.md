# Site Profile: Seedream (即夢 / 豆包)

**URL:** 
- **即夢 AI:** `https://jimeng.jianying.com/ai-tool/home`
- **豆包:** `https://www.doubao.com/chat/`
- **Volcengine Ark API:** 企業級
- **fal.ai / Replicate:** 第三方代理

**驗證狀態:** ⏳ 未驗證
**平台類型:** AI 圖像生成 (ByteDance Seedream 4.0 / 4.5 / 5)
**Stack:** 中國區服務，需手機號/微信登入

---

## 1. 三個主要入口

| 入口 | URL | 特色 |
|---|---|---|
| **即夢 (Jimeng)** | `jimeng.jianying.com` | 中文 UI，UI 最好，免費額度 |
| **豆包 (Doubao)** | `doubao.com` | 對話式整合，chatbot 模式 |
| **Volcengine Ark API** | `platform.volcengine.com` | 企業 API，含完整文件 |

**首選即夢** (UI 友善 + 免費額度)。

## 2. 登入

- 中國區：手機號碼 + 簡訊驗證碼，或微信掃碼
- 國際區：有時需 VPN；BytePlus ModelArk 是國際版 API
- **不支援 Google / Apple / Email 登入** (這點跟西方平台不一樣)

⚠️ 若使用者無中國手機號，可能需走 fal.ai / Replicate 代理。

## 3. 預期 UI (即夢)

### 主頁
- 左側 sidebar：首頁 / 圖片生成 / 視頻生成 / 畫布 / 我的作品
- 中央 prompt 框
- 右側參數：
  - 模型選擇 (Seedream 3.0 / 4.0 / 4.5 / 5)
  - 畫面比
  - 解析度 (到 4K 原生)
  - 生成數量

### Seedream 特色功能
- **文字渲染** (殺手級) — 中英雙語都強
- **圖像編輯** (同模型一鍵切換)
- **多圖 reference** (角色一致性)
- **4K 原生輸出** (4.0 起)

## 4. Phase-by-phase (TBD)

### Phase 1 — 登入 (手機號)
⏳ Auto-Pilot 停在此，不代登入

### Phase 2 — 進圖片生成
⏳ 左側 sidebar 點「圖片生成」

### Phase 3 — Prompt 輸入
⏳ 中央大 prompt 框 (猜測 `<textarea>`)
**格式** (from [../../references/seedream.md](../../references/seedream.md))：
```
[主體 + 細節] + [風格/媒材] + [構圖] + [光影] + [細節加強]
```

**文字渲染的殺手級技巧：**
- **要顯示的文字用雙引號包** — `"Cloud Nine"` 不是 `Cloud Nine`
- 位置明指 — `top center`, `diagonal banner`
- 字型描述 — `brush calligraphy`, `neon LED`
- 短字數 (1-10 字最準)
- **高解析 (2048+)** 字才清晰

### Phase 4 — 編輯模式 (Image Editing)
⏳ 上傳圖 + 編輯指令

### Phase 5 — 送出 + 監控
⏳ 生成時間與 credit 消耗待測

### Phase 6 — 下載 + Upscale
⏳ 支援 4K

---

## 5. Auto-Pilot 進 Seedream 時

**Intent Parser 特化：**
- 偵測「中文海報 / 中文字」→ 強制 Seedream (市場第一的中文渲染)
- 偵測「編輯既有圖」→ Seedream 4.0+ Image Editing
- 偵測「水墨 / 漢服 / 中式」→ Seedream 對中國文化元素訓練最多
- 英文海報 → 可能改 Nano Banana Pro / Ideogram 3

## 6. 預期陷阱 (from references)

- 要文字卻不加引號 → 會變場景元素
- 一張圖塞太多文字 → 超過 10 字歪
- Image Editing 用含糊代名詞 (`make it better`) → 沒用
- 寫 `(word:1.3)` 權重 → 不吃 (自然語言即可)

## 7. 版本與更新紀錄

- **2026-04 (stub)：** 建立 profile 架構，等實測補

---

## 8. ⚡ Chain Speed Optimization (Seedream 多圖)

### 最佳 chain SOP (每圖 4-5 calls，5 圖 = 25 calls)

**前置 (1 次)：** navigate 到 即夢/豆包/Krea/fal.ai (看 user 偏好) + 1 screenshot

**每圖 4-5 calls：**
```
1. left_click <prompt textbox>
2. key ctrl+a
3. type <new prompt with "雙引號文字">
4. left_click <Generate>
[5. batch screenshot 後續]
```

**禁忌：**
- ❌ 中間 screenshot
- ❌ TodoWrite 每圖
- ❌ 引號內文字寫超過 10 字 — 會歪

**Series Mode 替代 chain：** 若是「同風格 5 張」需求，**直接用 Seedream 4.5 Image Series Mode 一次出 5 張**，比 5 次獨立 chain 省時間 + 自動保持 theme consistency。

**Multi-Reference 替代 chain：** 13 元素商品海報可 14 refs 一次出，不要 chain 多次。

**驗證點 (2 次)：**
- 第 1 圖出來後 1 screenshot 校準
- 全部完成 1 screenshot

**內容長度：** Seedream prompt 標準 ~80-120 字 (主體 + 風格 + 構圖 + 光影 + 細節)，文字渲染必加雙引號。

**預期效能：** 5 圖 < 3 分鐘 + < 1.0k token
