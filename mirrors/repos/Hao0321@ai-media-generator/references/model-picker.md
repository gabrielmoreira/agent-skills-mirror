# 模型選擇大全 — OiiOii 全模型 + 各平台「選誰 / 招牌技巧」

**用途：** 任何生成任務先來這裡「選對模型」。每個模型一張卡：**廠商 / 最強情境 / 招牌 prompt 技巧 / 何時選**。2026-06 WebSearch 多源研究，平台特定數字標 (待驗證)，落 SOP 前須在站內實測。

> ⚠️ **OiiOii 是第三方聚合器**：站內 STAR/盒飯 消耗、時長上限可能 ≠ 各家原生 API 數字。下面的「最強情境/技巧」可直接用，但「價格/時長」以 OiiOii UI 實測為準（呼應 `feedback_verify_before_documenting`）。

---

## 0. 30 秒決策樹

```
影片？
├─ 產品/品牌廣告，要鎖形狀 → 先生 hero 圖 → i2v（Seedance 2.0 pro / Kling Start Frame）
├─ 多鏡頭敘事 + 有機運動（髮/布/水）+ 性價比 → ⭐ Seedance 2.0 pro（OiiOii 預設首選）
├─ 角色情緒戲 / 微表情 / 動作打鬥 → Hailuo 2.3 Pro
├─ 動漫 / 二次元 / 多角色一致 → Vidu Q3（@tag 多參）
├─ 複雜多主體場景 / 要畫面內文字招牌 / 首尾幀精控 → Wan 2.7
├─ 角色對白 / 15s 多場景音畫 → Wan 2.6 / HappyHorse
├─ 要對話式反覆改 + 餵語音/圖/影生影片 → Gemini Omni（Flow PRO）
├─ 要最高 4K 畫質 + 原生對白 + 長片 → Veo 3.1（Flow）
└─ 最強局部運動控制（產品不動只動水花）→ Kling Motion Brush
　 ❌ Sora 2 已停運（2026-04），勿選

圖片？
├─ 要圖內精準文字（海報/包裝/logo）→ Ideogram 3 / Nano Banana Pro / GPT-4o
├─ 旗艦寫實 + 4K + 世界知識 → Nano Banana Pro（OiiOii = Oii Nano Pro）
├─ 亞洲人美學 / 中文理解 → Seedream 5.0
├─ 動漫 / 插畫 → MJ niji7 / NovelAI（Danbooru tag）
├─ 大量低成本 API → Imagen 4
└─ 寫實 + 圖編輯 + 指令跟隨 → GPT-4o 生圖
```

---

## 🎬 影片模型卡

### ⭐ Seedance 2.0（字節跳動）— OiiOii 影片旗艦，預設首選
- **最強：** 多鏡頭敘事 + 有機運動（髮絲/布料/水波最自然）+ 時尚美妝/生活氛圍 + 性價比。Artificial Analysis Elo ~1269 居首（勝 Veo 3/Sora 2/Runway Gen-4.5，2026-06）。
- **招牌技巧：** `@AssetName` 資產標記 —— `@Image1` 鎖角色臉/產品形狀、`@Video1` 控運鏡走位、`@Audio1` 定配樂節拍。**明確分派每個 reference 的職責**，別只丟檔。
- **心法：** 少即是多 —— 1 張強主體圖 + 1 段乾淨運鏡 clip + 1 條聚焦 prompt > 一堆鬆散資產。
- **何時選：** 大多數 OiiOii 影片任務的預設。OiiOii 預設時長 10s，要 15s 手動拉 slider。

### Hailuo 2.3（MiniMax 海螺）— 角色表演旗艦
- **最強：** 人物表演 + 微表情 + 動作戲（武打/旋踢）+ 變形特效 + 最電影感。
- **招牌技巧：** 「導演的 AI」，**要劇本不要清單**。用現在式動詞**只寫變化的部分**；主體用簡短引用接具體動作（防換臉）；拿掉 `8k/masterpiece` quality booster，改自然敘事 + `slowly/gently` 收斂動態。
- **雷區：** input 是 close-up 別 prompt wide shot（會逼模型瞎掰場景致解剖錯誤）。
- **何時選：** 人像情緒戲、角色動作。Pro 限 5s、Std 可 6/10s（長鏡走 Std，待驗證 OiiOii 是否同）。

### Vidu Q3（生數 ShengShu）— 動漫 + 多角色一致旗艦
- **版本：** Q3 Mix（智能轉場敘事）/ Q3 Ref（多機位切換）/ Q3 Pro（畫質精度）/ Q2（品牌/Logo 控制最硬）。
- **最強：** 動漫/二次元（保 cel animation 不融化）+ 多角色跨鏡一致 + 16s 長片 + 原生音畫同出。
- **招牌技巧：**
  - `@tag` 多參點名，**順序即優先級**（核心主體放最前）：`@SCENE_BG @Akari_front enters left sprinting, dolly-in`
  - **HEX 鎖色**：`#C8A2FF` ≫「淺紫」（防跨幀色漂）
  - 每主體備 3 張參考圖（正/側/動），多角度防變形
  - 音訊當劇本：`Dialogue:` / `SFX:`（加時間錨點 `at 0.5s`）/ `Ambience:` / `BGM:` 分段 + 一句 `No music` 防亂加
- **弱項：** 複雜物理、嚴格 prompt 遵循（Smart Cuts 會自作主張加鏡頭）、photoreal 頂點非其強項。

### Wan 2.7 / 2.6（阿里 通義萬相）— 複雜場景 + 精控
- **Wan 2.7 最強：** 複雜多主體 + 首尾幀雙端精控 + **畫面內文字渲染（招牌/typography）**。招牌技巧：**啟用 Thinking Mode**（先規劃構圖/光線/敘事節拍再生成 → 刻意導演感）。
- **Wan 2.6 最強：** 角色扮演對白（中國首個）+ 多鏡頭故事板 + 15s 音畫同步。簡單 prompt 自動擴展成多鏡頭腳本；可從參考影片複製角色外觀+音色。
- **何時選：** 要畫面內中文招牌、複雜場景、首尾幀精控 → 2.7；要角色對白短劇 → 2.6。

### HappyHorse 1.0（阿里 ATH Innovation Unit）
- **最強：** 多鏡頭敘事 + 原生 1080p + 對白/環境音/Foley 同生（單流 transformer，文圖影音 token 同序列）。曾居 Artificial Analysis Video Arena #1。支援 7 語言對白（含中/粵/日/韓）。
- **何時選：** 要一次出好「敘事短片 + 完整音軌」。

### Gemini Omni（Google）🆕 I/O 2026（2026-05-19）
- **本質：** any-to-any 多模態影片模型，「**影片版 Nano Banana**」。單一架構融合 圖/音/影 生成，吃任意組合輸入。**Gemini Omni Flash 已上線**（Flow PRO / Gemini app / YouTube Shorts，發布期 10s 上限）。
- **殺手鐧：** **對話式編輯** —— 每個編輯指令都在「之前所有步驟的脈絡」下理解（第 3 步改機位，模型記得第 1-2 步的角色/光線/場景）。物理感知。
- **何時選：** 要**多輪迭代改**、餵語音/圖/影生影片、聊天式換背景/換物件/改鏡位。**直接解 OiiOii「加入對話≠i2v」的痛點 —— Omni 的 reference 鎖造型 + 對話改場景是原生功能。**
- **⚠️ 同名地雷：** Gemini Omni（Google）≠ Kling 3.0 Omni（快手）。兩個不同公司同名。

### Veo 3.1（Google）— 4K 畫質 + 原生音訊
- **最強：** 最高 4K 電影級畫質、48kHz 同步對白、原生 9:16 直式、Scene Extension 串長片。
- **招牌：** **Ingredients to Video**（上傳最多 4 張參考圖鎖角色/物件/產品 = i2v 鎖形狀正規武器）；對白寫進 prompt 自動對嘴；`SFX:` / `Soundtrack:` 前綴。
- **何時選：** 要 4K 成品、對白配音、直式短影音、拼長片廣告。

### Kling 3.0 / O-series（快手）— 人物動作 + 一致性 + 局部控制
- **版本釐清（重要）：**
  - **V3（3.0）** = 純 prompt 畫質旗艦，CoT 推理拆 prompt，單 clip 最多 6 鏡。
  - **Omni（V3 Omni / O3）** = 參考驅動，**唯一吃 video reference input** + Elements 3.0 鎖角色+聲音；迭代更快。
  - **O1** = 統一生成+編輯引擎，**首幀→尾幀**生成 + swap/replace/add/remove 編輯。
  - **2.6** = 首度原生音訊 + Motion Control；**2.5 Turbo** = 速度/CP 值檔（無音訊/無首尾幀）。
- **招牌功能：** Motion Brush（區域運動筆刷，最多 6 元素各自軌跡）+ Static Brush（鎖死像素）+ Elements（1-4 圖鎖角色，90%+ 一致）+ Start/End Frame + Motion Control（ref video 動作轉移）+ Camera Control + Avatar 2.0。
- **招牌技巧：**
  - 物理寫「事件」不寫「狀態」：`a glass falls and shatters` ≫ `a broken glass`
  - 防 hang 給動作收尾：`hair gently moves, then settles back` + `returning to stillness`
  - 一 shot 一運鏡 + 宣告機構+數字：`Camera on tripod, 5% zoom-in over 2s`
  - 序列動作（First…then…finally）比同時動作穩
  - 過濾雷區：身體裸露詞/特定接觸詞 → 改「描述穿什麼」取代「描述沒穿什麼」
- **最強：** 人物動作/對嘴/皮膚質感天花板、CP 值+迭代速度、角色一致性、**局部運動控制（產品不動只動背景/水花 = Motion Brush 不刷產品）**。
- **弱項：** 複雜物理互動不及 Sora 2 真實感。
- **⚠️ Kling i2v prompt 偏好 15-40 字（比 OiiOii 80-150 字短）—— 不同平台不互抄。**

### 🔴 Sora 2（OpenAI）— 已停運
- app/web 2026-04-26 已關、API 2026-09-24 關。**勿選**。OiiOii dropdown 可能仍列（API 代理），但別用。要 bodycam 寫實 → Runway Gen-4.5；要敘事 → Veo/Seedance。

### Runway Gen-4.5
- **最強：** 物理頂級、References/Act-Two（角色表演）/Aleph（video-to-video 編輯）、電影製作控制面。不自動產音訊。
- **何時選：** 複雜物理/流體、需要精密控制的電影工作流。

---

## 🖼 圖片模型卡

### Nano Banana Pro（Google，= OiiOii「Oii Nano Pro」）— 圖像旗艦
- **最強：** 4K + **文字渲染冠軍** + 世界知識（grounding Google Search）+ 圖編輯。
- **招牌技巧：** 拒絕「tag 湯」，用完整句像創意總監下指令（Subject/Composition/Action/Location/Style）；目標文字用**引號**包 + 指定字型（`"URBAN EXPLORER" in bold white sans-serif`）；可當升頻器（小圖 + `Upscale to 4K`）；80% 對了用對話改別重生。
- **何時選：** 海報/廣告 KV、含正確文字的設計、產品渲染、要真實地理/光線。
- **⚠️** OiiOii「Oii Nano Pro」≈ Nano Banana Pro 為平台內品牌名，底層實際版本須站內實測（待驗證）。

### Seedream 5.0（字節跳動）
- **最強：** 亞洲人美學 + 中文理解 + CoT 視覺推理 + 內建 web search + ≤14 張多圖參考 + 4K。
- **何時選：** 亞洲臉孔人像、中文場景、產品 hero 圖（本 skill i2v 流程已驗用 Seedream 5.0 生 hero）。

### Ideogram 3.0
- **最強：** 文字渲染王（~90% 準確）+ Style Code（8 碼複用畫風）+ Magic Prompt + Canvas。
- **何時選：** logo/海報/包裝要精準文字。

### Midjourney V8.1 / niji 7
- **最強：** 美學天花板、moodboards、`--sref`（畫風）。⚠️ `--oref` Omni Reference 是 **V7-only**，V8 改用 `--sref`。
- **niji 7：** 動漫美學最佳。
- **何時選：** 要最美的藝術感成圖、風格化。

### NovelAI Diffusion V4.5
- **最強：** 動漫/插畫，乾淨線稿 + 準確解剖 + 多角色。
- **招牌技巧：** **Danbooru tag 體系** —— 角色用 Danbooru 標記名（`yorha no. 2 type b` ✓ / `2b` ✗）；尾綴 quality tag（`masterpiece, no text, rating:general`）；Curated（穩）vs Full（廣）。
- **何時選：** 同人/動漫角色，要 tag 精準控制。

### GPT-4o 生圖（OpenAI，OiiOii「Gpt 4o」）
- **最強：** 照片寫實 + **可靠文字嵌入** + 指令跟隨 + 圖轉圖（最多 ~20 物件）。
- **弱項：** 局部編輯有副作用（可能動到其他區域）；物件 >20 會崩。
- **何時選：** 寫實 + 圖內要文字 + 複雜指令。

### Imagen 4（Google）
- **最強：** 大量低成本 API 量產（Fast $0.02/張）、多語系文字。
- **何時選：** 行銷素材批次、product render 量產。

---

## 🧩 命名混淆對照（背起來免出糗）

| 名字 | 真身 | 廠商 |
|---|---|---|
| Gemini Omni / Google Omni | any-to-any 影片模型（I/O 2026）| Google |
| Kling 3.0 Omni / O3 | 參考驅動影片（吃 video ref）| 快手 |
| Kling O1 | 統一生成+編輯引擎（首尾幀）| 快手 |
| GPT-4o（o=omni）| 多模態 LLM（非影片生成器）| OpenAI |
| Nano Banana Pro | 旗艦圖像（4K/文字）| Google |
| Oii Nano Pro | OiiOii 對 Nano Banana Pro 的介面名 | OiiOii 聚合 |
| Genie 3 | 互動世界模型（可走動，非影片）| Google |
| Seedance | 影片（字節）| ByteDance |
| Seedream | 圖像（字節）| ByteDance |

---

## 連動

- 概念/敘事先行 → [concept-first-prompting.md](concept-first-prompting.md)
- 反瑕疵技術面 → [quality-control.md](quality-control.md)
- 各模型完整 reference → 同目錄 `kling.md` / `vidu.md` / `veo.md` / `seedance.md` / `runway.md` / `seedream.md` / `midjourney.md` / `ideogram.md` / `suno.md`
- OiiOii 站內操作 → [../automation/site-profiles/oiioii.md](../automation/site-profiles/oiioii.md)
- 平台現況（含 Sora 停運）→ memory `reference_platform_status_2026_06.md`
