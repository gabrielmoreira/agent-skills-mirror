# Google Veo 3 / 3.1 — 原生同步音訊王者

官方 DeepMind `https://deepmind.google/models/veo/`。**市場第一個原生生成同步音訊** (對話、環境音、音效、配樂) 的影片模型。2026 時點主力 **Veo 3.1**。

在 Google Flow UI、Gemini App、Vertex AI 上可用；Replicate、fal.ai 有第三方代理。

---

## 🆕🆕 2026-06 重大：Google 影片變「雙旗艦」— Veo 3.1 + Gemini Omni

**Google I/O 2026（2026-05-19）發表 Gemini Omni** —— any-to-any 多模態影片模型，官方定位「**影片版 Nano Banana**」。**不是取代 Veo，是並存分工**：

| | **Veo 3.1** | **Gemini Omni** 🆕 |
|---|---|---|
| 定位 | 4K 畫質線、長片主力 | 對話編輯線、多模態輸入 |
| 強項 | 最高畫質、48kHz 同步對白、Scene Extension 長片、Ingredients(4 圖鎖形) | 吃任意組合輸入（圖/音/影/文）、**對話式逐輪編輯**、物理感知、世界知識 |
| 何時選 | 要 4K 成品 / 對白配音 / 直式 / 拼長片 | 要多輪改 / 餵語音圖影生影片 / 聊天式換背景換物件改鏡位 |

**Gemini Omni 關鍵（驗證 2026-06-05）：**
- 單一架構融合圖/音/影生成於 one forward pass（消除模型交接的品質損失）
- **對話式編輯殺手鐧**：每個編輯指令都在「之前所有步驟脈絡」下理解 —— 第 3 步改機位，模型記得第 1-2 步的角色/光線/場景
- **Gemini Omni Flash 已上線**：Flow PRO / Gemini app / YouTube Shorts/Create，發布期 **10s 上限**（Google 明說是部署選擇非模型限制）
- 給所有 Google AI Plus/Pro/Ultra 訂閱者
- 官方 prompt guide：六維框架（鏡頭框取/風格/光線/地點/動作/文字渲染）；**心法克制 —— 一回合只改一件事**；別逐像素描述（它會推理世界）；運鏡語彙都吃（`push in`/`dolly zoom`/`locked off`/`oner`）；丟角色圖當 reference 逐輪鎖造型

**⚠️ 同名地雷：Gemini Omni（Google）≠ Kling 3.0 Omni（快手）。** 兩個不同公司同名模型，別搞混。

**對 Hao 的意義：** Flow PRO 同時有 Veo 3.1 + Omni Flash。Omni 的「reference 鎖造型 + 對話改場景」**原生**解掉 OiiOii「加入對話≠i2v」的坑 —— 要乾淨的 i2v 鎖形狀工作流，Flow Omni 比 OiiOii Slate 注入乾淨。

**Google 視覺全家桶現況：** 影片雙旗艦 Veo 3.1 + Gemini Omni；圖像 Nano Banana Pro（4K 旗艦/文字）+ Imagen 4（量產）；世界模型 Genie 3（可走動 3D，非影片）。完整選模型見 [model-picker.md](model-picker.md)。

官方來源：[Introducing Gemini Omni (blog.google)](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-omni/) · [Gemini Omni (DeepMind)](https://deepmind.google/models/gemini-omni/) · [Omni prompt guide](https://deepmind.google/models/gemini-omni/prompt-guide/)

## 核心特色

- **原生音訊** — prompt 裡描述什麼聲音，會同步出現
- **對話 (dialogue)** — 支援真實人聲對白
- **電影敘事** — 對敘事結構、角色互動、情緒轉折理解深
- **8s 1080p** 基礎；3.1 可擴展更長
- 與 Imagen 整合：先 Imagen 生圖，再 Veo 動起來

## Prompt 公式

Veo 的最佳 prompt 長度：**3–6 句話，約 100–150 字**。

```
[Scene / Subject] + [Action / Beats] + [Camera] + [Lighting / Style] +
[Dialogue (可選)] + [SFX / Audio (可選)]
```

### 關鍵語法
- **對話**：用雙引號包起來
  `A woman says, "We have to leave now."`
- **音效**：用 `SFX:` 前綴
  `SFX: thunder cracks in the distance.`
- **環境音 / ambient**：直接描述，與畫面並列
  `Rain patters on the tin roof.`
- **音樂**：`Soundtrack: [風格]`
  `Soundtrack: tense orchestral strings.`

## 完整範例

**1. 對話戲**
```
Interior, a dimly lit diner, rain streaming down the window. Two detectives
sit across a booth. Detective A leans forward and says, "You already know
where the body is, don't you?" Detective B stares silently, then slowly
nods. Medium two-shot from the side, shallow depth of field, warm practical
lighting from the pendant lamp above. Cinematic noir style, 35mm film grain.
SFX: distant thunder, coffee cup clinks against saucer. Soundtrack: low,
brooding strings.
```

**2. 純音效 + 環境**
```
A lighthouse atop a stormy cliff, waves crashing against the rocks below,
lightning illuminating the tower intermittently. Wide establishing shot,
slow push in toward the beam of light. Cold blue-green palette, volumetric
light through the rain. SFX: heavy rain, rolling thunder, crashing waves,
distant foghorn. Soundtrack: sparse minimalist piano.
```

**3. 喜劇對白**
```
A golden retriever sits at a dinner table wearing a bow tie. He picks up a
wine glass in his mouth and says with a deep, serious voice, "I believe
it's time we discuss the walk schedule." Medium close-up, centered
composition, warm dining room lighting. Wes Anderson style, symmetrical,
pastel palette.
```

## 模式

| 模式 | 說明 |
|---|---|
| **T2V** | 文字生影片 + 音訊 |
| **I2V** | 首幀 + prompt |
| **I2V from Imagen** | Imagen 產圖 → Veo 動起來 (UI 一條龍) |
| **Extend** | 接續現有片段 |
| **Scene-to-scene** (3.1+) | 多場景拼接 |

## 參數

- 時長：8s (基礎) / 更長 (3.1 extend)
- 解析度：1080p
- Aspect：16:9 / 9:16
- 語言：英文最強；中文可但音訊偏弱

## Veo 特別好的情境

- 需要對白的敘事片
- 廣告 (需要 voiceover + 場景音效)
- 自然紀錄片感 (環境音很重要)
- 短劇 / 獨角戲

## Veo 弱項

- 運鏡精度不如 Kling 2.6 Pro
- 角色跨片段一致性 (沒有 multi-reference 系統)
- 8s 偏短，長片要 extend 多次

## 中文支援

- 視覺理解中文場景 OK (漢字、中式服裝)
- 中文對白也能生成，但 **口型同步和語調** 英文明顯較準
- 建議：場景描述中英皆可，對白優先英文

## 常見錯誤

- **把對白寫進敘述裡** (`she says she has to leave`) — Veo 不會唸出來。要 `She says, "I have to leave."`
- **音樂寫得太具體** (`Beethoven 5th symphony`) — 侵權風險，Veo 會降級處理。寫風格即可 (`dramatic orchestral`)。
- **prompt 太短** — 2 句話出來的東西品質低。盡量 3–6 句。
- **同時疊 SFX + 對話 + 音樂 + 環境 + 旁白** — 會混亂。挑 2–3 個音訊層。

## 連結

- 官方 DeepMind Prompt Guide：https://deepmind.google/models/veo/prompt-guide/
- Google Cloud Ultimate Guide for 3.1：https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1
- Vertex AI 官方文件：https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide
- Replicate Guide：https://replicate.com/blog/using-and-prompting-veo-3
- LTX Studio 範例：https://ltx.studio/blog/veo-prompt-guide
- 100+ 實測範例 (GVN)：https://geekvibesnation.com/google-veo-3-prompts-100-tested-examples-that-actually-work-2026/
- Beginner Guide 2026：https://www.veo3ai.io/blog/veo-3-beginners-guide-2026
- Veo 3.1 on ImagineArt：https://www.imagine.art/blogs/veo-3-1-prompt-guide

---

## 🆕 2026-04 Flow 進階功能完整地圖

### 1. Extend (續拍延長)
- 根據前段**最後 1 秒** 續拍，可串成 1 分鐘+ 影片
- 換回預設 Veo 3.1 Lite 延長 (省 credits)
- **Prompt pattern** (官方):
```
Continue from the previous scene, camera slowly dollies forward, the
character steps into the light, warm sunset tones, soft lens flare.
```
關鍵 4 元素：`action + camera + mood + continuity anchors (角色/場景/燈光)`

### 2. Frames to Video (首尾幀橋接)
- 上傳 **start frame + end frame** 兩張圖
- Flow 自動 bridge 出中間連續動作 (最適合轉場/史詩揭示)

### 3. Ingredients to Video
- 多素材合成 (2026-04 起 Veo Lite 全 tier 開放)
- 上傳素材 (角色 / 場景 / 物件) → Veo 組合進影片
- 比 single image-to-video 更可控的組合生成

### 4. Insert (插入新元素到既有影片)
- 在既有片段內加入新角色/物件/特效
- 原始場景保留，新元素自然融入

### 5. Remove (移除物件)
- 移除既有影片中的物件
- 背景自動重建

### 6. Camera (事後改運鏡)
- 不重生影片，只改運鏡路徑
- 同畫面內容不同 dolly / pan / zoom

### 7. Scene-to-scene (多場景拼接，3.1+)
- 序列多場景 prompt，Veo 串接保持敘事連續
- 每場景獨立 8s，但之間有自然 transition

### 免費 tier 政策 (2026)
- **每月 10 支免費影片** 給**所有 Google 帳號** (Flow 全域)
- PRO 用戶額外配額 + Quality 版
- Veo Lite 是最便宜 tier，所有功能都能用

### 所有功能都支援原生音訊
對白 / SFX / Ambient / Soundtrack 在 Extend / Insert / Frames / Ingredients 皆自動合成。
