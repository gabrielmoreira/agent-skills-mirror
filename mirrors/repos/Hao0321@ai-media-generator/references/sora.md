# OpenAI Sora 2

官網 `https://sora.com/`。2026 時點的主力版本是 **Sora 2**。已整合進 ChatGPT Plus (標準功能)。三個核心功能：**Storyboard**、**Remix**、**Blend**。

## 核心哲學

OpenAI 官方指南的核心類比：**把自己當成在對沒看過腳本的攝影指導 (DP) 簡報**。如果你不講清楚，他會自己補 — 結果可能不是你要的。因此：

> **Prompt 要像一張分鏡卡：鏡頭景別、景深、動作節拍、燈光、調色。**

細節 prompt = 高控制；簡短 prompt = 模型發揮 (想要意外美感時好用)。

## Prompt 公式

```
[Framing + Lens] + [Subject + Beats] + [Lighting] + [Palette / Style] +
(可選) [Audio / Dialogue]
```

**範例：**
```
Medium close-up, 50mm, shallow depth of field. A woman in a red raincoat
stands on a wooden pier, slowly raising her hood as the first drops of rain
fall. She looks out over the gray ocean. Overcast soft light, cool
desaturated palette except for her red coat. Melancholic, cinematic, 35mm
film grain. SFX: light rain on wood, distant seagulls.
```

## 功能 1 — Storyboard

在 `sora.com` 的 storyboard 模式，你可以 **秒級** 編排影片：逐秒填入指令，或描述一個場景讓 Sora 自動產 storyboard 後再調整。

**工作流：**
1. 寫一個 1–2 句的總體概念
2. Sora 生成 storyboard (每秒一格的 prompt)
3. 逐格編輯：改運鏡、改角色位置、改光線
4. 生成影片

**每格 prompt 寫法：** 比完整 prompt 短，只描述**那一秒的變化**：
```
0s: Establishing wide shot of the alley.
2s: Camera begins slow push-in.
4s: Cut to medium close-up of the detective's face.
6s: He exhales smoke, turns toward the sound off-screen.
```

## 功能 2 — Remix

已經有一個滿意的生成結果，Remix 讓你 **微調一個變數**，其他保持不變。

**規則：一次只改一件事。** Sora 理解「same X, new Y」。

**範例：**
- `same shot, switch to 85mm` (只改鏡頭)
- `same lighting, new palette: teal, sand, rust` (只改調色)
- `same composition, change character wardrobe to white suit` (只改衣服)

**關鍵：** 先把滿意的結果 **pin as reference**，然後 Remix 只寫「變的部分」。其他不提。

## 功能 3 — Blend

把兩個影片融合。Prompt 描述兩邊各自是什麼 + 要怎麼融合。

```
Blend A with B. A is the location and lighting. B is the subject and motion.
```

## 參數

- **時長**：5s / 10s / 20s (2 的擴展)
- **解析度**：最高 1080p (pro 使用者更高)
- **Aspect**：16:9 / 9:16 / 1:1
- **Style presets**：Cinematic / Animation / Realistic 等

## 運鏡 (Sora 理解特徵)

Sora 對 **電影攝影語彙** 敏銳：
- `medium close-up, 50mm, shallow depth of field`
- `bird's-eye view, slowly rotating`
- `handheld tracking, subject walks through frame`
- `slow push-in toward the subject's eyes`
- `anamorphic 2.39:1, lens flares`

也能理解敘事節拍 (beats)：
- `starts wide, then cuts to medium, ends on close-up`
- `action unfolds in three beats: [A], [B], [C]`

## 音訊 (Sora 2)

Sora 2 也有原生音訊，用法類似 Veo：
- 對白：`"..."` 引號
- SFX：`SFX: ...`
- 音樂：`Soundtrack: ...`

但目前市場共識是 **對白品質 Veo 3.1 仍領先一點**，視覺一致性 Sora 更好。

## 範例

**1. 電影感獨白**
```
Medium close-up, 85mm lens, shallow depth of field. A weary detective sits
in his car, staring at a photograph in his hand. Rain streams down the
windshield behind him. Harsh neon-pink sign reflects on his face. He
whispers, "I should have known." Cinematic noir style, teal and magenta
grade, 35mm film grain. SFX: rain on windshield, distant thunder. Soundtrack:
sparse piano with low synth drone.
```

**2. 動作片 — 三段節拍**
```
Three beats. Beat 1: establishing wide shot of the rooftop at night, city
lights below. Beat 2: medium tracking shot as the runner leaps between
buildings, cape flowing. Beat 3: low-angle close-up landing, dust rising.
Handheld energy, anamorphic lens, cinematic, cool blue palette with orange
city accents.
```

**3. 簡短 (讓 Sora 發揮)**
```
A paper crane unfolds itself in reverse on a white desk. Soft natural light.
```

## 常見錯誤

- **Remix 一次改太多** — 會變成完全不同的影片。一次一個變數。
- **太少細節**，期待高品質 — Sora 不會讀心。細節 prompt 回報細節輸出。
- **storyboard 每格寫完整 prompt** — 會互相打架。每格只寫「這秒的變化」。
- **同時要求 "handheld" 和 "locked camera"** — 自相矛盾。
- **對白寫成敘述** — 要用引號才會唸出來。

## 連結

- 官方 Sora 2 Prompting Guide (cookbook)：https://cookbook.openai.com/examples/sora/sora2_prompting_guide
- 開發者版 cookbook：https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide
- OpenAI Help - Creating videos with Sora：https://help.openai.com/en/articles/12460853-creating-videos-with-sora
- Sora Release Notes：https://help.openai.com/en/articles/12593142-sora-release-notes
- Generating videos on Sora：https://help.openai.com/en/articles/9957612-generating-videos-on-sora
- Tutorial (DataCamp)：https://www.datacamp.com/tutorial/sora-ai
- Complete Tutorial 2026 (YUV)：https://yuv.ai/learn/sora
- Tips for 2026 (WaveSpeedAI)：https://wavespeed.ai/blog/posts/sora-2-prompting-tips-better-videos-2026/
- 中文站：https://soratoai.com/en/docs/guides/sora-2-prompting-guide/

---

## 🆕 Sora 2 進階功能完整地圖 (2026)

### 1. Storyboard (Beta)

- `sora.com` Storyboard 模式
- **秒級編排**：每秒一格 prompt
- 可從概念自動生 storyboard 草稿，再手動調整每格
- **ChatGPT Pro 先用**

### 2. Remix (一次改一變數)

```
"same shot, switch to 85mm"
"same lighting, new palette: teal, sand, rust"
"same composition, character wardrobe to white suit"
```
規則：**一次改一件**，其他保留。

### 3. Re-cut (重剪)

- 原片段重新剪接順序
- 或切出特定片段 loop

### 4. Blend (融合兩影片)

```
"Blend A with B. A is the location and lighting. 
 B is the subject and motion."
```

### 5. Loop

- 自動把片段變 loopable (首尾無縫)

### 6. Style Presets

- 官方風格預設 (animation / realistic / cinematic / retro / anime)
- Pro 版有更多

### 7. Cameo (Characters) — 殺手級功能

- 錄一次 **video + audio** (5-30 秒，你本人 / 朋友)
- 建 character 存檔
- **以後任何 Sora 場景** 可放進這個 cameo
- **需要該人同意** (Sora 有 consent 機制)
- 實際效果：你可以把朋友放到「宇宙飛船內」「武俠片」任何場景

### 8. Social Features (Sora iOS App)

- **Algorithmic feed** (類 TikTok)
- 社群觀看別人作品
- **Leaderboards** — 最多 remix / 最多 cameo 的作品
- Follow friends
- Remix 別人作品 (需授權)

### 9. 長度擴展

- 新 duration options (超過 Sora 1 的 10s)
- 更長 ideas (電影級片段長度)

### 10. 真人圖片上傳

- 2026 起可上傳真人照片生影片
- **需 consent** — Sora 要求使用者承認有當事人同意
- Deepfake 防範機制 (水印 + 溯源)

### 11. Blend 工作流範例

```
影片 A: 夜晚 Tokyo 街道 (街景、燈光、雨)
影片 B: 角色走路的片段 (動作、表演)

Sora Blend prompt:
"Blend A with B. Take the nighttime Tokyo street from A 
(streets, neon, rain) and overlay the character from B 
walking through that scene. Match rain atmosphere, 
character interacts with puddles."
```

### 12. 進階 Prompt (Storyboard 式)

```
Medium close-up, 50mm, shallow depth of field. A woman 
in a red raincoat stands on a wooden pier, slowly 
raising her hood as the first drops of rain fall. 
She looks out over the gray ocean. Overcast soft light, 
cool desaturated palette except for her red coat. 
Melancholic, cinematic, 35mm film grain. 
SFX: light rain on wood, distant seagulls.
```

關鍵：**寫得像給攝影指導的簡報** (framing + lens + DoF + action beats + lighting + palette + SFX)。
