# Vidu — 生數科技 (ShengShu Tech) AI 影片

官網 `https://www.vidu.com/` (國際) / `https://www.vidu.studio/` (中國)。生數科技主打 **Reference-to-Video (多主體參考一致性)** 與 **動漫 / 二次元**，是這兩條賽道目前最強的開放模型之一。

**2026 時點版本地圖：**
- **Vidu Q3** (2026-01-30 發布) — 主力。業界首個「16s 單次原生音視訊同步」(對話 / 旁白 / 音效 / 配樂 / 多人對白 + lip-sync)。Artificial Analysis Video Arena ELO ~1220–1244，全球**第 2** (僅次 Sora 2)。
- **Vidu Q2** (2025-10-21 發布) / **Q2 Reference Pro** — 多主體一致性主力，最多 7 張參考、最長 10s，Turbo / Pro / Pro Fast 三檔。
- **Vidu Q1** — **動漫 / 2D 專家**（訓練資料含大量 anime+manga），角色情緒表情最自然。

> ⚠️ **校正紀錄**：舊版本檔曾寫「Q3 = 2026-04 發布、Artificial Analysis 全球第 1」。實際 Q3 約 **2026-01-30** 上線，排名**全球第 2（次於 Sora 2）**。本檔已修正。

---

## 1. 模型能力矩陣

| 版本 | 定位 | 最長時長 | 原生音訊 | 參考圖 | 解析度 | 特別強 |
|---|---|---|---|---|---|---|
| **Q3** | 旗艦 · 一鏡到底敘事 | **16s** | ✅ 對話/旁白/SFX/音樂/多人 + lip-sync | 多張 (待驗證上限) | 1080p | 帶聲音的完整故事段、多語對白 |
| **Q2 / Q2 Ref Pro** | 多主體一致性 | 10s | ❌ (Q2 純畫面) | **最多 7 張** | 1080p | 多角色同框、商品 360° 展示、短劇 |
| **Q1** | 動漫 / 2D 專家 | 4–8s | ❌ | 最多 7 張 | 1080p | 二次元、角色情緒表情、cel-style |
| Vidu 2.0 | 上一代通用 | 8s | ❌ | 多張 | 1080p | 流暢度 |
| Vidu 1.5 | 首代 Ref2V | 4s | ❌ | 多張 | 上一代 | 首個 reference-to-video |

**選版速查：**
- 要**聲音 / 對白 / 完整故事段** → **Q3**
- 要**多角色 / 多主體一致 / 商品展示 / 純畫面** → **Q2 (Pro 檔)**
- 要**動漫 / 二次元 / 卡通角色動起來** → **Q1**

> ⚠️ Q3 的參考圖上限官網未明列數字（待驗證）。Q1 / Q2 確認為「**最多 7 張**」（臉 / 手勢 / 場景 / 道具任意組合）。舊檔曾寫「Q3 縮到 1–4 張更穩」屬未證實，已降級為待驗證。

---

## 2. 五大模式

| 模式 | 說明 | 最佳場景 |
|---|---|---|
| **T2V** | 純文字生影片 | 概念快速試 |
| **I2V** | 單張首幀 + prompt | 已有定裝圖要它動 |
| **Reference-to-Video (Ref2V)** | 多張參考 (Q1/Q2 最多 7)，6 類參考 | **Vidu 的招牌** — 多主體一致 |
| **Start-End Frame (首尾幀)** | 給首幀 + 尾幀，模型補中間過渡 | 變身 / 轉場 / 史詩揭示 |
| **T2V + Audio** | Q3 原生同步音訊 | 帶聲音的成片 |

### Ref2V 的 6 類參考 (Q2)
1. 角色 (characters) — 臉 / 全身定裝
2. 物件 / 道具 (props / textures) — 商品、配件、材質
3. 場景 (scenes) — 背景、地點
4. 動作 (actions) — 把某段動作 transfer 到主體
5. 表情 (expressions) — 指定情緒
6. 特效 (special effects) — 風格化視覺

---

## 3. Prompt 公式

把自己想成導演，分層描述：

```
Subject + Action + Environment + Camera + (Lighting + Style)
```

**官方示範：**
```
Cinematic low-angle shot of a fantasy warrior leaping over a chasm,
high-fidelity motion, sunset lighting, 1080p.
```

**長度甜蜜點：** T2V/I2V 約 40–80 字；Ref2V/Q3 多主體 80–150 字（要描述每個 entity 在做什麼 + 怎麼組合）。

---

## 4. 進階技巧 A — Reference-to-Video 多主體一致性 (Vidu 最強招)

這是 Vidu 區別於 Veo / Sora 的核心。Veo 沒有 multi-reference 系統，Runway Gen-4 Refs 上限更少。用好它，「同一角色跨鏡一致」幾乎免費。

**規則 1 — 明確指涉每個 ref，別讓模型猜**
用 `the character from reference 1` / `the object in image 2` / `the scene in video 1`。
Vidu UI 內以 **`[@image 1]` `[@image 2]`** 標籤對應上傳順序；多角色同框時依序放標籤：`[@image 1][@image 2]`。

**規則 2 — 不要重述參考圖已有的外觀**
ref1 已是金髮紅洋裝女孩，prompt 就**別**再寫 `a blond girl in a red dress`——會與 ref 打架、稀釋一致性。模型看得到長相，你只需給「**做什麼 + 怎麼組合**」。

**規則 3 — 重點放動作與組合關係**
模型理解每張 ref 之間的關係，能在「不把它們塞進同一張圖」的前提下合成有層次的場景。

**規則 4 — 多角度提升穩定度**
要角色超穩（轉頭 / 大動作不崩），餵 **3–7 張**良好打光、不同姿勢/角度的 ref。單張只夠簡單設計。

**範例 — 角色 + 場景 + 物件三 ref 組合：**
```
(Ref 1: 主角臉部, Ref 2: 中世紀市集, Ref 3: 紅色絲巾)
The character from reference 1 walks through the market from reference 2,
wraps the red scarf from reference 3 around her neck as she passes a flower
stall. Medium tracking shot, natural morning light.
```

**範例 — 動作 transfer：**
```
The subject (ref 1) performs the dance from reference video 1, in the setting
of ref 2, dynamic tracking shot, stage lighting.
```

---

## 5. 進階技巧 B — 動漫 / 二次元最佳化 (Q1 專長)

Q1 訓練資料含大量 anime + manga，會依該風格詮釋「這角色會怎麼笑 / 怎麼生氣」，情緒表情自然且不破壞角色辨識度。這是寫實模型做不到的。

**官方 Q1 動漫 prompt 模組（依序組）：**
```
Camera work + Location + Emotion + Action + [@character ref]
```

**關鍵字策略：**
- 用 **`flat, cel-style coloring`**（平塗賽璐珞上色）。Vidu 對細膩漸層 / 微妙陰影較難精準複製，**純色 / 平塗反而穩**。
- 情緒用**強度形容詞**：`burning competitive spirit`、`maximum curiosity`。
- 運鏡用**比喻 + 強度**：`F1-style whip pan`、`lightspeed zoom`、`slow pan → sudden stop zoom`。

**參考圖準備（動漫專用）：**
- 背景盡量**單純 / 純色**，讓模型專注角色。
- 高解析、平塗無漸層。
- 簡單設計**單張即可**；複雜角色再補正/側/背三視圖。

**範例 — 熱血戰鬥動漫：**
```
[@image 1] A spiky-haired shonen protagonist, flat cel-style coloring,
burning competitive spirit in his eyes. Rooftop at dusk, orange sky.
He clenches his fist and lunges forward. Camera: slow pan then sudden
whip-pan zoom-in on his face, F1-style speed lines.
```

---

## 6. 進階技巧 C — 首尾幀 (Start-End Frame)

Vidu 在首尾幀過渡特別穩，適合**變身 / 時光流逝 / 史詩揭示 / 商品變形**。上傳起始幀 + 結束幀，模型補中間連續動作。

**重點：** prompt 寫**過程描述**（怎麼變），不要重述兩端外觀。

**範例 — 花開縮時：**
```
(Start: 花苞, End: 盛開紅玫瑰)
Time-lapse of the flower bud slowly opening into full bloom, macro shot,
soft natural light, seamless transition.
```

---

## 7. 進階技巧 D — Q3 原生音訊（對話 / 音效 / 配樂）

Q3 是 Vidu 唯一會出聲音的版本，且**一個 model 同時出音訊 + 影像**，免後期對齊。支援**對話 / 旁白 / 音效 / 配樂 / 多人對白 + 自動 lip-sync**，多國語言（英 / 日 / 中）。

> 重要差異：**Q3 已支援音樂 (music)**。舊檔「Vidu 不做音樂」只適用 Q2 及更早版本。Q3 描述配樂風格即可（避免具體曲名 / 侵權）。

**音訊分層建議（挑 2–3 層，不要全疊）：**
- 環境音 / SFX：`Audio: heavy rain, rolling thunder, waves crashing against rocks, distant foghorn.`
- 對白：角色名 + 引號（接近 Veo 寫法）。
- 配樂：寫**風格 + BPM + 情緒走向**，不要寫具體曲名。

**避免：**
- 具體版權曲名（侵權風險，會降級處理）→ 改寫風格 `melancholic synth pad, 60 BPM`。
- 同時疊 對白 + SFX + 配樂 + 環境 + 旁白 → 混亂。

---

## 8. 運鏡詞

支援全套標準（Q3 為 frame-level 精準執行）：
- `zoom in / out`、`pan left / right`、`tilt up / down`
- `tracking shot / dolly / follow`、`orbit / arc`
- `static`、`handheld`、`aerial / drone`
- `whip pan`、`slow push in`、`crash zoom`

---

## 9. 參數

- **時長**：Q1 4–8s · Q2 最長 10s · **Q3 最長 16s**
- **解析度**：1080p（部分代理可選 540p / 720p 省 credits）
- **Aspect**：16:9 / 9:16 / 1:1
- **語言**：中英原生；Q3 音訊支援 英 / 日 / 中
- **Q2 品質檔**：Turbo（快、簡單短片）/ Pro（電影級細節）/ Pro Fast（折衷）

### 中英混寫策略
- 中國文化元素（漢服、竹林、水墨）→ 中文
- 電影術語 / 運鏡 / 風格 → 英文

```
一位漢服少女在竹林中舞劍，cinematic low-angle tracking shot,
slow motion moments, golden hour lighting, ink-wash aesthetic.
```

---

## 10. 價格速查 (待驗證 — 官網 vidu.com/pricing 為準)

訂閱分 **Free / Standard / Premium / Ultimate** 四檔（年付約）：

| 方案 | 月費 (年付) | Credits/月 |
|---|---|---|
| Standard | ~$8 | 800 |
| Premium | ~$28 | 4,000 |
| Ultimate | ~$79 | 8,000 |

> 部分頁面列月付為 $10 / $35 / $99（與年付不同）。以官網即時為準。

**Ref2V credit 消耗（依代理 API 公開值，官 UI 可能不同）：**

| 解析度 | 5s | 10s |
|---|---|---|
| 540p | 12 credits (~$0.06) | 20 credits (~$0.1) |
| 720p | 24 credits (~$0.12) | 42 credits (~$0.21) |
| 1080p | 42 credits (~$0.21) | 76 credits (~$0.38) |

消耗三因子：**時長**（越長越貴）×**品質檔**（高檔 1.5–2.5×）×**功能**（physics / style lock 加成）。Pro 方案有 **50% credit rollover**。

---

## 11. 進階 Recipe

### Recipe A — 多主體短劇一鏡（Q2 Ref Pro，招牌用法）
不用 chain，一次出多角色同框。
```
(Ref 1: 女主臉, Ref 2: 男主臉, Ref 3: 雨夜街道場景)
The woman from reference 1 stands under a streetlight in the scene from
reference 3, the man from reference 2 walks toward her from the shadows.
She turns, recognition on her face. Slow dolly-in, rain-soaked neon
reflections, shallow depth of field, cinematic.
```
要點：兩張臉 ref 各自指涉，**不重述長相**，只寫互動 + 運鏡。

### Recipe B — 帶對白的完整情緒段（Q3 16s 一鏡到底）
取代 Veo 多次 8s extend。
```
(Ref 1: 角色A, Ref 2: 角色B, Ref 3: 黃昏天台)
Rooftop at sunset (ref 3). Character A (ref 1) walks in from the left;
Character B (ref 2) already stands at the edge. Medium two-shot, he turns
toward her. Camera slow push-in to her face as her expression shifts to
recognition.
Dialogue —
A: "I wasn't sure you'd come."
B: "I almost didn't."
Soundtrack: melancholic synth pad, ~60 BPM, building on the close-up.
Style: cinematic anime warmth, anamorphic, soft neon bokeh.
```
要點：對白用角色名 + 引號；配樂寫風格 + BPM；16s 內**自帶起承轉**。

### Recipe C — 動漫角色情緒爆發（Q1，二次元最佳化）
```
[@image 1] Flat cel-style coloring. A young swordswoman, calm face cracking
into a fierce grin, eyes burning with resolve. Dojo at night, paper lanterns.
She draws her blade in one swift motion. Camera: static hold then crash-zoom
on her eyes, dramatic speed lines.
```
要點：`flat cel-style coloring` 鎖風格 + 情緒強度詞 + 比喻運鏡。

---

## 12. 常見失敗 + 修法

| 症狀 | 原因 | 修法 |
|---|---|---|
| 多角色長相互相污染 / 變第三人 | prompt 重述了 ref 已有外觀，與 ref 打架 | 刪掉外觀描述，只寫「ref N 做什麼」+ 用 `[@image N]` 標籤 |
| 角色轉頭 / 大動作就崩 | 只給單張 ref | 補到 3–7 張多角度、良好打光的 ref |
| 動漫漸層 / 陰影髒掉 | Vidu 對細膩 shading 較弱 | 改 `flat, cel-style coloring`，背景純色 |
| Q3 出不來聲音 | 用到 Q2/Q1（無音訊） | 確認模型選 **Q3** |
| 對白沒被唸出來 | 寫成敘述 `she says she has to leave` | 改 `A: "..."` 角色名 + 引號 |
| 配樂走鐘 / 被降級 | 寫了具體版權曲名 | 改寫風格 `dramatic orchestral, building` |
| 音訊一團亂 | 同時疊 5 種音層 | 挑 2–3 層（環境 + 對白 或 配樂） |
| 中國區生成被擋 | content moderation（vidu.studio） | 改 prompt，避免敏感題材 |
| 想要 >16s | 單次上限 16s (Q3) | 分段生再剪，或 Ref2V 保角色一致接續 |

---

## 13. 與其他模型分工

- **要多角色跨鏡一致 / 商品 360°** → Vidu **Q2 Ref2V**（Veo 沒有 multi-ref，這是 Vidu 主場）
- **要二次元 / 動漫角色動畫** → Vidu **Q1**（寫實模型做不出 anime 情緒）
- **要帶聲音的完整故事段（16s）** → Vidu **Q3**
- **要超精準運鏡 / 物理** → Kling 2.6 Pro（Vidu 運鏡略遜）
- **要最自然英文對白 / lip-sync** → Veo 3.1（Vidu Q3 多語對白接近但英文略遜）

---

## 連結

**官方：**
- 官網：https://www.vidu.com/
- Vidu Q3 介紹頁：https://www.vidu.com/vidu-q3
- Q1 動漫官方指南：https://www.vidu.com/blog/vidu-q1-ai-2d-anime-guide
- GPT-4o + Vidu 角色動畫教學：https://www.vidu.com/blog/create-and-animate-ai-character-with-gpt4o-and-vidu
- 定價頁：https://www.vidu.com/pricing
- API 定價：https://platform.vidu.com/docs/pricing

**發布新聞：**
- Q2 Ref2V 發布 (PRNewswire)：https://www.prnewswire.com/news-releases/vidu-launches-q2-reference-to-video-pioneering-a-new-era-of-high-consistency-and-creative-control-302590002.html
- Q2 全面升級 / 5 分鐘故事 (aibase)：https://news.aibase.com/news/22138
- SCMP 報導 (challenge Sora)：https://www.scmp.com/tech/tech-trends/article/3329800/chinese-ai-start-shengshu-unveils-vidu-q2-challenge-openais-sora

**第三方解析 / 評測：**
- Q3 是什麼 + 1/30 發布 (Cutout.pro)：https://www.cutout.pro/learn/blog-what-is-vidu-q3/
- Q3 深度 (CometAPI)：https://www.cometapi.com/what-is-vidu-q3/
- Q3 pricing & credits (promeai)：https://www.promeai.pro/blog/vidu-q3-pricing-credits/
- Vidu pricing 2026 拆解 (Flowith)：https://flowith.io/blog/vidu-pricing-2026-free-vs-pro-vs-enterprise-cost/
- Q1 動漫評測 (ReelMind)：https://reelmind.ai/blog/vidu-q1-dynamic-anime-multi-reference-video
- Scenario 模型總覽：https://help.scenario.com/en/articles/vidu-models-the-essentials/
- WaveSpeedAI Vidu 集合：https://wavespeed.ai/collections/vidu
- Z.AI Q1 開發文件：https://docs.z.ai/guides/video/vidu-q1
