# Vidu — 生數科技 (ShengShu Tech) AI 影片

官網 `https://www.vidu.com/` / `https://www.vidu.studio/`。主力版本 **Vidu Q2** (2025-10 發表) / **Q2 Reference Pro** (2026-01-27 全球發布) / **Q3** (16s 原生音視訊)。**殺手鐧是 Reference-to-Video**：一次可餵 2 段參考影片 + 4 張參考圖 (共 7 個 references)，模型保持多實體一致。

## 核心模式

| 模式 | 說明 |
|---|---|
| **T2V** | 純文字生影片 |
| **I2V** | 單張首幀 + prompt |
| **Reference-to-Video (Ref2V)** | 1–7 張參考 (Q2 起擴到 2 videos + 4 images)，6 類參考 |
| **Start-End Frame** | 首尾幀之間生成過渡 (Vidu 在此項特別穩) |
| **T2V + Audio** | Q3 起原生同步音效/環境音 |

### 6 類參考 (Q2)
1. 角色 (characters)
2. 物件 / 道具 (props / textures)
3. 場景 (scenes)
4. 動作 (actions)
5. 表情 (expressions)
6. 特效 (special effects)

## Prompt 公式

把自己想成導演，四段式：

```
Subject + Action + Environment + Camera Angle + (Lighting + Style)
```

**範例 (官方示範)：**
```
Cinematic low-angle shot of a fantasy warrior leaping over a chasm,
high-fidelity motion, sunset lighting, 1080p.
```

## Reference-to-Video 的關鍵規則

**1. 明確指涉每個 ref**
用 "the character from reference 1"、"the object in image 2"、"the scene in video 1"、"the red car"、"the boy in ref 1"。

**2. 不要重複描述參考圖已有的外觀**
如果 ref1 已經是金髮女孩穿紅洋裝，prompt 就不要再寫 "a blond girl in a red dress"，會跟 ref 打架。

**3. 重點放「動作」與「組合」**
模型看得到外型，你要告訴它「要做什麼」+「怎麼組合」。

**範例 1 — 角色 + 場景組合：**
```
The character from reference 1 walks into the cafe from reference 2,
sits at the window seat, warm afternoon light, slow dolly in, cinematic.
```

**範例 2 — 角色 + 物件 + 另一角色：**
```
The girl (ref 1) picks up the vintage camera (ref 2) and smiles at the dog
(ref 3), shallow depth of field, handheld, golden hour.
```

**範例 3 — 以動作 ref 指引：**
```
The subject (ref 1) performs the dance from reference video 1, in the setting
of ref 2, dynamic tracking shot, stage lighting.
```

## 音效 Prompt (Q2 後期 / Q3)

Vidu 支援環境音 + 物件音效 (**不做音樂**)。結構：`聲源 + 音質 + 環境音`。

```
Audio: heavy rain, rolling thunder, waves crashing against rocks,
distant foghorn, wind howling.
```

**避免：**
- 音樂性描述 (「悲傷的旋律」) — Vidu 不是 music model
- 人聲/對話 — 目前還不穩，要對話去 Veo 3.1

## 運鏡詞

支援全套標準：
- `zoom in / out`
- `pan left / right`
- `tilt up / down`
- `tracking shot / dolly / follow`
- `orbit / arc`
- `static`
- `handheld`
- `aerial / drone`

## 參數

- **時長**：Q2 約 4–8s；**Q3 原生 16s**
- **解析度**：1080p
- **Aspect**：16:9 / 9:16 / 1:1
- **中英文 prompt** 皆原生支援

## 版本差異

| 版本 | 亮點 |
|---|---|
| Vidu 1.5 | 首個 reference-to-video |
| Vidu 2.0 | 流暢度↑、1080p、8s |
| Vidu Q1 | 高品質輸出，物理合理性↑ |
| **Vidu Q2** | 2 videos + 4 images refs、6 類 |
| Vidu Q2 Reference Pro | 2026-01 全球，提升一致性 |
| **Vidu Q3** | 原生 16s 音視訊同步 |

## 中英混寫

- 中國文化元素 → 中文
- 電影術語 / 運鏡 / 風格 → 英文

```
一位漢服少女在竹林中舞劍，cinematic low-angle tracking shot,
Wong Kar-wai style, slow motion moments, golden hour lighting.
```

## 範例

**1. T2V — 電影感奇幻**
```
A hooded wanderer trudges through knee-deep snow toward a distant glowing
doorway in the mountainside. Low-angle tracking shot from behind. Cold blue
palette, volumetric light spilling from the door, cinematic, Lord of the Rings
inspired.
```

**2. Ref2V — 角色旅程 (給 Vidu 3 張圖)**
```
(Ref 1: 主角臉部, Ref 2: 中世紀市集, Ref 3: 紅色絲巾)
The character from reference 1 walks through the market from reference 2,
wraps the red scarf from reference 3 around her neck as she passes a flower
stall. Medium tracking shot, natural morning light.
```

**3. Start-End Frame — 變身/過場**
```
(Start Frame: 花苞, End Frame: 盛開紅玫瑰)
Time-lapse of the flower bud slowly opening into full bloom, macro shot,
soft natural light, seamless transition.
```

**4. Q3 原生音訊**
```
A lighthouse during a thunderstorm, waves crashing against the rocks below,
lightning illuminating the clifftop. Wide establishing shot, slow push in.
Audio: heavy rain, rolling thunder, crashing waves, distant foghorn.
```

## 連結

- 官網：https://www.vidu.com/
- Q2 發布新聞 (PRNewswire)：https://www.prnewswire.com/news-releases/vidu-launches-q2-reference-to-video-pioneering-a-new-era-of-high-consistency-and-creative-control-302590002.html
- Q2 總覽 (SuperMaker)：https://supermaker.ai/blog/vidu-q2-overview-next-gen-video-ai-that-brings-details-and-camera-moves-to-life/
- Q3 解析 (promeai)：https://www.promeai.pro/blog/what-is-vidu-q3/
- WaveSpeedAI Vidu 集合：https://wavespeed.ai/collections/vidu
- 302.AI 實測：https://medium.com/@302.AI/vidu-q2-test-actors-leading-the-new-direction-in-ai-video-innovation-bcea34de7e4c
- Scenario 指南：https://help.scenario.com/en/articles/vidu-models-the-essentials/
- SCMP 報導：https://www.scmp.com/tech/tech-trends/article/3329800/chinese-ai-start-shengshu-unveils-vidu-q2-challenge-openais-sora

---

## 🆕 Vidu Q3 (2026-04-13 全球發布) — 完整更新

**Vidu Q3 Reference-to-Video** 是 2026-04 最大升級，ShengShu Tech 官方。

### 業界第一: 16 秒 single-pass synchronized audio+video

- **16 秒 一次生成** audio + video 同步
- 包含 ambient sound / dialogue lip-sync / atmospheric audio
- **比 Veo 3.1 (8s) + Kling 3.0 (15s) 更長**
- **同一 model 出音訊 + 影像**，不需後期對齊

### Multi-Entity Consistency (Vidu Q3 核心)

- **1-4 張 reference images** (比 Q2 減少但更穩)
- 結合多個不同來源 (不同角色 / 角度 / 風格) 進單一場景
- 每個 entity 維持 distinct identity
- **比 Runway Gen-4 Refs (最多 3 張) 更靈活**

### 6 類原生電影級 VFX

Vidu Q3 內建：
1. **Particle systems** (雨 / 雪 / 沙 / 魔法粒子)
2. **Fluid simulation** (水 / 液體 / 煙霧)
3. **Dynamic motion** (真實物理)
4. **Camera movement** (精準運鏡)
5. **Transitions** (自然場景切換)
6. **Lighting** (動態光影)

**意義：** 不需後期 VFX，原生包含。

### 多鏡 Composition + Camera Control

- 單次 prompt 內多鏡
- 每鏡獨立 camera control

### 多語言 Dialogue + Lip Sync

- 支援多國語言對白
- 自動 lip sync
- 品質接近 Veo 3.1 (評測中 Vidu 在多國語言上有優勢)

### Benchmark 成績

- **Artificial Analysis benchmark 全球第 1** (發布時)
- 綜合分數勝過 Veo 3.1 / Kling 3.0 / Sora 2 (在某些類別)

### 進階 Prompt (Q3 格式)

```
Multi-entity scene at a Tokyo rooftop at sunset:
- Character A (from ref 1): young woman in red jacket, 
  walks onto rooftop from left
- Character B (from ref 2): man in black suit, 
  already standing at edge looking out
- Setting (from ref 3): cyberpunk Tokyo skyline

Shots (16s total):
Shot 1 (0-5s): Wide establishing of rooftop, both characters 
  visible, dynamic motion of her walking.
Shot 2 (5-10s): Medium two-shot from side, he turns 
  toward her, her expression shows recognition.
Shot 3 (10-16s): Close-up on her face, she smiles, 
  tear rolls down. Bokeh neon background.

VFX: particle system for distant neon glow drift, 
fluid simulation on scattered rain, dynamic wind on 
her hair/jacket.

Dialogue:
Character A: "I wasn't sure you'd come."
Character B: "I almost didn't."

Soundtrack: melancholic synth pad with subtle piano, 
60 BPM, building to emotional swell on close-up.

Style: Makoto Shinkai cinematic anime meets Blade Runner 
2049 neon atmosphere, 2.39:1 anamorphic, 16-bit HDR.
```

### 新連結

- [Vidu Q3 Launch (PR Newswire)](https://www.prnewswire.com/news-releases/shengshu-launches-vidu-q3-reference-to-video-with-expanded-visual-and-audio-capabilities-302740489.html)
- [Vidu Q3 on WaveSpeedAI](https://wavespeed.ai/blog/posts/introducing-vidu-q3-reference-to-video-on-wavespeedai/)
- [What Is Vidu Q3? (promeai)](https://www.promeai.pro/blog/2026/02/05/what-is-vidu-q3/)
