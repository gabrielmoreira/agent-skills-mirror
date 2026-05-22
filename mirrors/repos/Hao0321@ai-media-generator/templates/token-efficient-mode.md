# Token-Efficient Mode — 大專案省 token 策略

**問題：** skill 現在 30+ 檔，7000+ 行。每次 auto-pilot 若讀全部 reference + template，會燒 50-100k tokens 在 context，主代理很快炸掉。

**解決：** 7 層 token 優化策略，按需觸發。

---

## 策略 1 — Lazy Load (按需讀檔)

### 原則
**只讀當前任務真的需要的檔**。Auto-Pilot 各 Stage 讀的 reference 不同：

| Stage | 必讀 | 按需讀 |
|---|---|---|
| 1 Intent Parser | SKILL.md (已在 context) | — |
| 2 Defaults | (templates/auto-pilot.md) | [user-flags.md](user-flags.md) 若使用者帶 flag |
| 3 Platform Decider | [selector.md](../references/selector.md) | — |
| 4 Storyboard | [storyboard.md](storyboard.md) 若多鏡 | [music-video.md](music-video.md) 若 MV |
| 5 Prompt Crafting | **只讀選定平台的 reference** (kling.md / flow 沒有 / veo.md 等) | **只讀對應的 preset** |
| 6 Preview | — | — |
| 7 Execution | **只讀對應的 site-profile** ([flow.md](../automation/site-profiles/flow.md) 或 [kling.md](../automation/site-profiles/kling.md) 或 [oiioii.md](../automation/site-profiles/oiioii.md)) | [click-protocol.md](../automation/click-protocol.md) |

### 具體做法
```
❌ 別這樣：Read 所有 references/* (10+ 檔, ~4000 行)
✅ 這樣：先 Read selector.md → 挑好平台 → 只 Read 該平台 reference
```

---

## 策略 2 — Grep 取代 Read 整檔

大檔用 Grep 只抓需要的 section，省 10-50x tokens。

### 範例

**❌ 讀整個 cinematic-direction.md (381 行) 只為找 Roger Deakins 風格：**
```
Read("references/cinematic-direction.md")  # 4000 tokens
```

**✅ Grep 只抓 Deakins 相關：**
```
Grep "Deakins" references/cinematic-direction.md -C 3
# 回 ~200 tokens
```

### 什麼時候用 Grep
- 找特定導演/DP/底片 token → Grep
- 找特定 preset → Grep preset name
- 找特定 site-profile section → Grep "Phase N"

### 什麼時候用 Read
- 需要整體 UI 地圖或流程概覽
- 第一次學一個 reference

---

## 策略 3 — 子代理 parallel 讀

### 原則
**主代理不讀大檔，委派給子代理讀 + 濃縮**。子代理可以處理大量原始資料並只回 summary，主代理 context 不受影響。

### 範例：設計 Apple × Nike 廣告
```
❌ 主代理讀：
Read(cinematic-direction.md)  # 4000 tokens
Read(commercial-direction.md)  # 3500 tokens
Read(preset-packs.md)  # 9000 tokens
→ 主代理吃 16500 tokens

✅ 主代理委派：
Agent("Research Apple aesthetic tokens for TVC", subagent=Explore, 
      prompt="Read commercial-direction.md and preset-packs #11 (Apple Hero). 
              Return the 8 most relevant tokens for an Apple-style product 
              hero shot. <100 words.")
Agent("Research Nike heroic tokens for TVC", subagent=Explore, ...)
→ 主代理只吃 2 × 100 words = ~400 tokens (40x 省)
```

### 子代理用例
- **多平台比較** — 1 個子代理 research 1 個平台
- **深度 research** — 查某個導演的完整簽名
- **prompt 組裝** — 委派子代理從 references 挑 token 組 prompt，回傳成品
- **比對驗證** — 子代理對照 benchmark 結果

---

## 策略 4 — SKILL.md 本體精簡

### 原則
SKILL.md 是「**永遠在 context**」的檔。它越短，每次啟動越省 token。

### 目標
- **SKILL.md ≤ 200 行** (當前 160+)
- **只放路由 + 硬規則 + auto-pilot + 觸發**
- **所有「how-to」內容下沉到 reference 或 template**

### 怎麼做
當 SKILL.md 超過 250 行時，把「詳細教學」抽到新 reference，SKILL.md 只留 link 和一行描述。

---

## 策略 5 — Preset 跳過進階檔

### 原則
**preset-packs.md 已經把 cinematic + commercial + vfx + sound 的最佳組合打包成 30 個食譜。** 用 preset = 不用讀原始 references。

### 做法
```
❌ 做 Wes Anderson 風的海報：
Read(cinematic-direction.md) 找 Wes Anderson section
Read(camera-language.md) 找對稱構圖
Read(vfx-effects.md) 找粉彩色調
組 prompt

✅ 
Grep "Wes Anderson" templates/preset-packs.md -C 25
# 回 Preset #2 完整 prompt，直接改占位符
```

**preset 替換 → 80% 任務直接搞定**，只剩少數特殊需求才翻原始 references。

---

## 策略 6 — Cache-aware Polling

### 原則
Monitor 長任務 (OiiOii / Kling / Flow 生成) 時的 ScheduleWakeup 要挑對節奏，讓 prompt cache 存活。

### Cache TTL 是 5 分鐘 (300s)
- **< 300s 的 wakeup** → cache 熱，便宜
- **> 300s 的 wakeup** → cache miss，貴

### 做法
| 情境 | 間隔 |
|---|---|
| 等互動 UI (agent 每 1-3 min 問問題) | 60-90s (cache 熱) |
| 等純背後生成 (Flow/Kling 3-5 min) | 120-180s (還在 cache) |
| 等長任務 (OiiOii 10-15 min) | 1200-1800s (一次 miss 買長等) |

**別用 300-600s 中間值** — 那是 worst-of-both (cache miss + 不夠長)。

---

## 策略 7 — 把 Chat 歷史 wrap 起來

### 當 chat 變長 (跨 iteration, 多 demo)
- 主代理 context 累積太多 screenshot + 檔案內容
- **主動用 TodoWrite 濃縮進度**
- **刪除過時的 screenshot references** (每次新 screenshot 覆蓋舊的 image_id)

---

## 策略 8 — Chain Workflow 暴力節省 (2026-04-20 慘痛教訓)

### 痛點
連跑 5 首 Suno 歌花 15 分鐘 + 3.9k token，user 罵「垃圾」。chain 浪費比單任務嚴重 3-5 倍，因為**每 task 都重複犯相同錯**。

### 4 大浪費 (每 N task 放大 N 倍)

| 浪費 | 單次成本 | 5 task 累積 |
|---|---|---|
| 每 task 後 screenshot | 1.5k token | **7.5k 浪費** |
| TodoWrite 每 task 一次 | 300 token | **1.5k 浪費** |
| 多步 clear (triple+ctrl+a+delete) | 3 calls | **15 calls 浪費** |
| 內容超寫 (歌詞 50 行 vs 25 行) | 2x type 量 | **5x type 量** |

### 鐵則 (5 條)

1. **中間禁 screenshot** — 只第 1 task 後 + 全部完成各 1 張。中間相信座標。
2. **中間禁 TodoWrite** — chain 跑完一次性更新；系統 reminder 叫用 TodoWrite 時，若是 chain workflow → **明智地忽略**。
3. **clear 用 1-click** — trash icon / ctrl+a 覆寫。禁 triple-click + Ctrl+A + Delete 三步走。
4. **標準長度** — Suno 歌詞 ~25 行 / Veo prompt ~80 字 / MJ keyword 30-50 字 / Seedream 80-120 字。多寫無加分。
5. **內建批次 > N 次 chain** — 平台有 Series Mode (Seedream / Suno Persona) / Multi-Shot (Kling) / Multi-Reference (Vidu Q3 / MJ omni-ref) → **優先用內建批次**。

### 檢測標準
5 task chain 應 ≤ 36 tool calls + ≤ 1.5k token + < 5 分鐘。違反任一就要修。

### 細節見
- [click-protocol.md §「Token + 時間最佳化」](../automation/click-protocol.md)
- [site-profiles/_template.md §9](../automation/site-profiles/_template.md)
- 各 site profile §「Chain Speed Optimization」

---

## Auto-Pilot Token Budget (參考上限)

| Stage | Budget |
|---|---|
| 1-3 Intent + Defaults + Platform | 2k tokens (讀 selector + auto-pilot) |
| 4 Storyboard | 3k (讀 storyboard template 若多鏡) |
| 5 Prompt Crafting | 5k (Grep 選定平台的 reference) |
| 6 Preview | 1k |
| 7 Execution | 10-30k (screenshots + site-profile + click-protocol) |
| **總計** | **~25-40k tokens** |

**相較不優化：** 讀所有 refs = 100k+ tokens。

---

## 實作層：Auto-Pilot 的 "Lazy Routing"

當使用者說「做個 Ghibli 異世界短片」：

```
Stage 1: SKILL.md 已載 → Parse intent (0 額外 tokens)
Stage 2: Read user-flags.md 若需 flags 對照 (else skip, 省 ~2k)
Stage 3: Read selector.md → 選 Kling 3.0 (~1k)
Stage 4: Grep "Ghibli" templates/preset-packs.md (~200 tokens, 不 Read 整檔)
Stage 5: 用 preset，skip cinematic-direction 深讀 (省 ~4k)
         Read references/kling.md (當前平台 ~150 行, ~2k)
Stage 6: Show preview (0 新 read)
Stage 7: Read site-profiles/kling.md (~300 行, ~4k)
         Read click-protocol.md 首 1-2 章若需 (~1k)
```

**總計：** ~10k tokens (vs 40k naive)

---

## 什麼時候要「豪華模式」不省 token

以下情境全量讀是值得的：
- **學習/研究 skill 本身** — 使用者要看 skill 架構，就應該 Read 全部
- **benchmark / eval 驗證** — 測試 skill 完整能力
- **初次碰到陌生平台** — 建 site-profile 需要探索完整 UI
- **跨平台複合任務** — 做 Apple × Nike TVC 要合併多 references

此時直接 Read 大檔沒關係，token 換品質。

---

## Checklist: Auto-Pilot 啟動前自檢

- [ ] 使用者一句話任務夠明確？若模糊 → 先補問 1-2 個 slot，不要讀檔
- [ ] 任務類型能對應到 preset 嗎？→ 優先 Grep preset-packs
- [ ] 平台已確定？→ 只讀該平台 reference
- [ ] 需要完整語彙庫？→ 委派子代理，自己不讀
- [ ] 長任務監控 → 用對的 wakeup 間隔 (別 300-600s)

---

## 跟 auto-pilot.md 的關係

本檔 = auto-pilot 的「省油版」配置。
- [auto-pilot.md](auto-pilot.md) 是 **7 stage pipeline 架構**
- [token-efficient-mode.md](token-efficient-mode.md) (本檔) 是 **每 stage 的 lazy loading 策略**

Auto-Pilot 跑時自動 apply 這份策略，**使用者不用主動喊**。除非使用者明說「你讀詳細一點沒關係」才進豪華模式。
