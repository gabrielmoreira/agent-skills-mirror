# Site Profile: Vidu

**URL:** `https://www.vidu.com/` (國際) / `https://www.vidu.studio/` (中國)
**驗證狀態:** ⏳ 未驗證 (stub — 操作時請邊做邊補)
**平台類型:** 生影片 (生數科技 ShengShu，多 reference 強)
**Stack:** ⏳ 待確認 (可能 React + 中國區優化)

---

## 1. 整體 UI 地圖 (預期)

```
┌─ Sidebar ─┬───── Editor / Library ─────┬─ Settings ─┐
│ Q3 (新)   │                             │ Style       │
│ 1.5       │   [video / prompt panel]    │ Duration    │
│ Templates │                             │ Aspect      │
│ Library   │                             │             │
└───────────┴─────────────────────────────┴─────────────┘
```

**核心模式：**
- **Vidu Q3** — 最新主力，Reference-to-Video，1-7 張 reference 一次出 16s 多鏡含原生音訊
- **Vidu 1.5** — T2V / I2V，4-8s
- **Q3 Multi-Entity** — 多角色同框 (主打點)
- **Templates** — 預設模板 (跳舞 / 變身 / 表情)

---

## 2. 主流程 Phase-by-phase (待實際操作補)

### Phase 0 — 登入 / 首頁
- ⏳ 國際版 vs 中國版 (vidu.com / vidu.studio)
- ⏳ 中國區登入可能需手機號 + 簡訊
- ⏳ 代幣顯示位置

### Phase 1 — Q3 Reference-to-Video
- ⏳ 上傳 1-7 張 ref (角色 / 場景 / 物件 / 風格)
- ⏳ 每張 ref 是否能 tag 角色 (`@A` / `@B`)
- ⏳ Prompt textbox 位置
- ⏳ Duration: 16s 固定？還是可選

### Phase 2 — Q3 Multi-Entity
- ⏳ 多 character 一起入鏡的設定
- ⏳ 角色互動描述

### Phase 3 — 等待 + 下載
- ⏳ 16s 含音訊的 generation 時長
- ⏳ 結果預覽 + 下載
- ⏳ 是否能 Extend

---

## 3. 付費結構速查 (待補)

| 階段 / 功能 | 成本 | 驗證 |
|---|---|---|
| Q3 16s 含音 | ? credits | ⏳ |
| Q3 Multi-Entity | ? credits | ⏳ |
| 1.5 短片 | ? credits | ⏳ |
| 月訂閱 | ? | ⏳ |

---

## 4. Click 策略備註 (待補)

- ⏳ ref 穩定度
- ⏳ 中國區 UI 可能不同
- ⏳ Selected state 視覺

---

## 5. 常見 toast / modal 速查 (待補)

| Toast / Modal | 意義 | 對策 |
|---|---|---|
| ⏳ 配額用完 | 付費牆 | 停手提示 |
| ⏳ Ref 圖太多 (>7) | 上限 | 減少 |
| ⏳ Content moderation | 中國區 | 改 prompt |

---

## 6. 快速決策樹

```
打開 Vidu 要什麼？
├── 多角色多場景一致影片 → Q3 Reference-to-Video (1-7 張 ref)
├── 多人同框 → Q3 Multi-Entity
├── 單一動作短片 → 1.5 T2V / I2V
└── 跳舞 / 變身效果 → Templates
```

---

## 7. Workspace / 檔案保存機制 (待補)

- ⏳ Library 永久保存？
- ⏳ 公開 / 私人切換
- ⏳ 下載格式

---

## 8. 未驗證但值得注意 (下次操作補)

- ⏳ Q3 16s 是否真含原生音訊 (對話 / 音效 / BGM)
- ⏳ Multi-Entity 上限幾人
- ⏳ Reference 圖是否能控制每張的影響權重
- ⏳ 中國區與國際區帳號是否互通

---

## 9. ⚡ Chain Speed Optimization

### 通用最佳 SOP

**前置 (1 次)：** navigate + 1 screenshot 確認 UI

**每生成 N calls (理想 ≤ 8 含 ref 上傳)：**
```
1. clear prompt field
2. (若新場景) 上傳 1-7 張 ref 圖
3. focus prompt textbox
4. type <new prompt>
5. click Generate
[後續 batch screenshot]
```

**禁忌：**
- ❌ 中間每生成後 screenshot
- ❌ TodoWrite 每生成
- ❌ 重複上傳同一張 ref (Library 應可重用)

**驗證點 (僅 2 次)：**
- 第 1 生成後 1 screenshot 校準
- 全部完成後 1 screenshot 確認

**內容長度建議：** Q3 prompt 80-150 字 (因含多 character + scene)

**並行 / 內建批次替代 chain？**
- **Q3 1-7 張 ref + 16s 多鏡含音訊 = 一次出整個故事段** → 比 4 次 Veo chain (4×8s) 強 100%
- **這是 Vidu 最大 selling point — 不要 chain，直接 Q3 一次到位**

**預期效能：** 1 次 Q3 16s = 1 次 chain，5 次故事 < 30 分鐘 (Q3 較慢)

---

## 10. 版本與更新紀錄

- 2026-04-20：初始 stub 建立 (待實際操作驗證)
