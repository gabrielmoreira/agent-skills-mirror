# 多鏡頭分鏡模板 (跨平台通用)

把一個故事拆成 3–8 個鏡頭，每鏡寫獨立 prompt。適用 Kling、Seedance、Vidu、Runway、Sora、Veo；Seedance 原生支援單 prompt 多鏡 (`Cut to`)，其他平台要分次生成再剪輯。

## 工作流

### Step 1 — 寫故事大綱 (中文即可)

4-6 句話，從頭到尾：
- **情境 (setup)** — 誰、在哪、什麼氛圍
- **引入 (inciting)** — 發生了什麼
- **衝突/發展 (escalation)** — 主角做什麼
- **高潮 (climax)** — 關鍵動作/揭露
- **尾聲 (resolution)** — 收在哪

### Step 2 — 定義主角與場景的「視覺錨」

每個角色寫 3+ 個固定外觀特徵：
- 頭髮顏色/長度、膚色、年紀、體型、服裝、特殊標記

每個場景寫 2–3 個視覺錨：
- 時間、天氣、主要元素、色調

### Step 3 — 拆分鏡頭

依節奏決定鏡頭數：
- **10-15s 短片** → 2–3 鏡
- **30s 短片** → 4–6 鏡
- **1 分鐘** → 6–10 鏡 (接剪)
- **MV** → 10+ 鏡

每個鏡頭的 prompt 包含：
- **景別** (wide / medium / close-up / ECU)
- **角度** (eye-level / low / high / OTS)
- **運鏡** (static / dolly / pan / track / orbit)
- **主體動作** (一句話描述本鏡發生什麼)
- **光影與風格** (跟整片一致)

### Step 4 — 檢查一致性

- 所有角色的視覺錨在每鏡都有複述 (至少 1-2 個關鍵錨)
- 色調、光影、風格描述用 **同一組字** (不要一鏡寫 "golden hour"、另一鏡寫 "sunset")
- 時間線合理 (除非是跳接)
- 情感節奏有起伏 (不要所有鏡都靜態)

## 範本 (填空式)

```markdown
# Storyboard：[片名]

## 設定
- **目標平台**：[Kling 2.1 / Seedance 1.0 Pro / Runway Gen-4 ...]
- **總長**：[30s / 1 min]
- **畫面比**：[16:9 / 9:16]
- **整體風格錨**：[e.g., cinematic, Wong Kar-wai style, teal and orange grade, 35mm film]

## 角色
- **角色 A**：[年齡、髮色/長度、膚色、服裝、特徵]
- **角色 B**：[...]

## 場景
- **場景 1**：[地點、時間、天氣、主要元素]
- **場景 2**：[...]

## 鏡頭

### Shot 1 — [標題]
- 景別：[wide establishing]
- 角度：[eye-level]
- 運鏡：[static / slow pan right]
- 動作：[角色 A 走進畫面從左邊]
- 光影：[soft morning light from the right]

**Prompt：**
```
[填入完整 prompt]
```

### Shot 2 — [標題]
...

## 轉場與剪接提示
- Shot 1 → Shot 2：[cut / dissolve / match cut on action]
- Shot 2 → Shot 3：[...]

## 配樂指示 (若有)
- 整片配樂走向：[upbeat synth pop, gradual build]
- 或走 Suno 生成：[link to suno prompt]
```

## 範例：30 秒短片「咖啡師」

**設定：**
- 目標平台：Seedance 1.0 Pro (用 `Cut to` 原生多鏡)
- 總長：30s
- 畫面比：16:9
- 風格錨：warm cinematic, soft natural window light, shallow depth of field, muted earthy palette, 35mm film grain

**角色：**
- 咖啡師 Aya：女性 20 代後半，短黑髮俐落馬尾，白色立領襯衫加褐色圍裙，左手戴細銀戒

**場景：**
- 場景 1：獨立咖啡店，早晨，窗外晨霧，木質吧檯，黃銅咖啡機

**鏡頭：**

**Shot 1 — 店內空景**
```
Wide static shot of a cozy independent cafe at dawn. Warm window light spills
across wooden counter with a brass espresso machine. Morning mist visible
outside the window. Muted earthy palette, 35mm film grain, cinematic.
```

**Shot 2 — 咖啡師入鏡**
```
Cut to medium shot. A young woman with short black hair in a ponytail, wearing
a white collared shirt and brown apron, walks behind the counter and ties her
apron strings. Soft morning light from the right. Cinematic, shallow depth of
field, warm tones.
```

**Shot 3 — 動作特寫**
```
Cut to close-up of hands (silver ring on left hand) operating a brass espresso
machine, dark coffee streaming into a white ceramic cup. Steam rising. Soft
directional light, shallow depth of field, 35mm film.
```

**Shot 4 — 情感收尾**
```
Cut to medium shot of the same young woman placing the coffee cup on the
counter, looking out the window with a small contented smile. Warm morning
light on her face. Cinematic, muted earthy palette, shallow depth of field.
```

**轉場：**
- Shot 1 → 2：cut
- Shot 2 → 3：match cut on hand movement
- Shot 3 → 4：cut

**配樂 (Suno prompt)：**
```
Style: intimate lo-fi jazz, warm upright piano, brushed drums, double bass,
muted trumpet, 72 BPM, nostalgic Sunday morning

Lyrics:
[Instrumental]
```

## 針對不同平台的調整

### Seedance 1.0 Pro (原生多鏡)
把所有 shots 合成一個 prompt，用 `Cut to:` 分段，一次生成整片。

### Kling / Vidu / Runway / Sora / Veo
每個 shot 獨立生成，後期在剪接軟體拼接。保持角色描述完全一致 (逐字複製)。

### OiiOii (multi-agent)
把 shots 轉成敘事 brief 格式 (見 `references/oiioii.md`)，讓 multi-agent 自己分鏡。

## 一致性技巧

1. **把「角色卡」當函式呼叫** — 開一個變數：
   ```
   CHAR_A = "a 20s woman with short black hair in a low ponytail,
            wearing a crisp white collared shirt and brown apron"
   ```
   每個 prompt 貼一次。

2. **固定 seed** (若平台支援) — 同一 seed 增加角色/場景延續性。

3. **先生成最難的鏡** — 通常是 close-up 人臉。確認後再做其他鏡。

4. **Midjourney --oref / Vidu ref2v / Runway Gen-4 Refs** — 都是跨鏡一致的工具，值得為角色投資一張「主照」。

5. **Flux Kontext / Seedream editing** — 修正個別鏡的小問題比重生整鏡快。
