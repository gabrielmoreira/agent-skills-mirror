# 鏡頭語言 Cheatsheet (跨平台通用)

本檔適用所有影片模型 (Kling、Seedance、Vidu、Runway、Veo、Sora)。每家支援度略有差異，下方有標註。

**想要更深入？** 本檔是「基礎詞彙表」。要到「電影導演級別」請進階讀：
- [cinematic-direction.md](cinematic-direction.md) — 導演簽名 + DP + 底片 + 燈光分類 + meta token stack
- [commercial-direction.md](commercial-direction.md) — 廣告/時尚/MV 特殊視覺語言
- [vfx-effects.md](vfx-effects.md) — 大氣/物理/光效/VFX 完整詞庫

## 基本運鏡 (Camera Movement)

| 英文術語 | 中文 | 說明 | 支援度 |
|---|---|---|---|
| **static shot** / locked camera | 固定鏡頭 | 相機不動 | 全部 |
| **pan left / pan right** | 左搖 / 右搖 | 相機水平旋轉 (不位移) | 全部 |
| **tilt up / tilt down** | 仰搖 / 俯搖 | 相機垂直旋轉 | 全部 |
| **dolly in / dolly out** | 推軌 / 拉軌 | 相機沿光軸前進或後退 | 全部，Kling 2.1+ 最準 |
| **push in / pull out** | 推進 / 拉出 | 與 dolly 近似，強調情緒 | Sora 偏好；其他也懂 |
| **truck left / truck right** | 橫移左 / 右 | 相機側向位移 | 全部 |
| **pedestal up / pedestal down** | 升降 | 相機垂直位移 | Runway, Veo 較懂 |
| **zoom in / zoom out** | 變焦 | 焦距變 (非物理位移) | 全部；效果不如 dolly |
| **crane up / crane down** | 升降 crane | 大幅度垂直位移 | Kling, Seedance, Veo |
| **tracking shot** | 跟拍 | 相機跟隨主體 | 全部 |
| **orbit / arc shot** | 環繞 | 繞主體 360° 或弧形 | Kling 2.1+, Veo 強 |
| **handheld** | 手持 | 輕微晃動 | 全部；加 "subtle" 控制強度 |
| **aerial / drone shot** | 空拍 | 高空俯視 + 移動 | Seedance, Veo, Vidu 最穩 |
| **overhead / top-down** | 垂直俯拍 | 正上方視角 | 全部 |
| **POV shot** | 主觀鏡頭 | 第一人稱 | 全部 |
| **whip pan** | 急搖 | 快速橫向轉切 | Kling, Sora |

## 景別 (Shot Size)

| 英文 | 中文 | 用途 |
|---|---|---|
| extreme close-up (ECU) | 大特寫 | 眼睛、嘴唇、細節 |
| close-up (CU) | 特寫 | 臉部 |
| medium close-up (MCU) | 中特寫 | 胸以上 |
| medium shot (MS) | 中景 | 腰以上 |
| medium long shot / cowboy | 中遠景 | 大腿以上 |
| long shot / full shot | 全景 | 全身 |
| wide shot | 遠景 | 人 + 一點環境 |
| establishing shot / extreme wide | 大遠景 | 地點感 |

## 角度 (Angle)

| 英文 | 中文 | 語意 |
|---|---|---|
| eye-level | 平視 | 中性 |
| low angle | 仰角 | 權威、英勇 |
| high angle | 俯角 | 脆弱、被觀察 |
| Dutch angle / canted | 荷蘭角 | 不安、失衡 |
| bird's-eye view | 鳥瞰 | 全局感 |
| worm's-eye view | 蟲視角 | 誇張尺度 |
| over-the-shoulder (OTS) | 過肩 | 對話戲 |
| two-shot | 雙人鏡 | 兩主體並置 |

## 鏡頭焦段 (Lens)

| 術語 | 效果 |
|---|---|
| wide lens / 24mm / 35mm | 場景張力，輕微變形 |
| standard lens / 50mm | 最像人眼 |
| portrait lens / 85mm | 人像散景 |
| telephoto / 135mm / 200mm | 壓縮空間，放大遠景 |
| anamorphic lens | 寬銀幕 + 橢圓光斑 (電影感) |
| macro lens | 極近 / 微距 |
| fisheye | 魚眼 |
| tilt-shift | 小人國感 |

## 光影 (Lighting)

| 英文 | 中文 | 效果 |
|---|---|---|
| golden hour | 黃金時刻 | 日出/日落柔金光 |
| blue hour | 藍色時刻 | 日落後藍紫 |
| rim light / backlight | 輪廓光 / 逆光 | 邊緣發光 |
| key light from left | 主光左側 | 經典人像 |
| Rembrandt lighting | 林布蘭光 | 鼻影三角 |
| volumetric light / god rays | 體積光 / 耶穌光 | 光束可見 |
| cinematic lighting | 電影感照明 | 高對比、色彩分層 |
| soft natural light | 柔和自然光 | 陰天或擴散光 |
| hard shadows | 硬陰影 | 直射強光 |
| neon lighting | 霓虹 | 賽博龐克 |
| practical lights | 場景實光 | 畫面內的燈泡、螢幕 |
| chiaroscuro | 明暗對比 | 油畫感 |

## 時序 / 速度 (Time)

| 英文 | 說明 |
|---|---|
| slow motion / slo-mo | 慢動作 |
| high speed / fast motion | 快動作 |
| time-lapse | 縮時 |
| real-time | 實時 (基準) |
| freeze frame | 定格 |
| ramping speed | 速度變化 (需要支援的模型) |

## 風格錨 (Style Anchors)

### 電影 / 導演
- `Wes Anderson style` — 對稱、粉彩
- `Christopher Nolan style` — 冷色、IMAX 感
- `Kurosawa-inspired` — 黑澤明、武士、深景深
- `Wong Kar-wai style` — 王家衛、霓虹、慢動作
- `Roger Deakins cinematography` — 自然光、質感
- `Blade Runner 2049` — 賽博朋克、橙藍配色
- `Studio Ghibli animation` — 吉卜力
- `Pixar 3D animation` — 皮克斯 3D
- `anime cel-shaded` — 動畫賽璐珞
- `shot on 35mm film, Kodak Portra 400` — 底片感

### 色彩分級 (color grade)
- `teal and orange grade`
- `bleach bypass`
- `muted earth tones`
- `high contrast black and white`
- `pastel colors, desaturated`

## 一次一到兩個運鏡 (重要)

疊太多會壞掉。**好的組合：**
- `slow dolly-in + slight tilt down` ✓
- `tracking shot following the subject, handheld` ✓
- `static wide shot, subject walks from left to right` ✓

**壞的組合：**
- `zoom in while panning right, then crane up, then orbit` ✗
- `handheld and dolly and orbit simultaneously` ✗

## 跨模型翻譯表

同一個意圖在不同模型的最佳寫法：

| 意圖 | Kling | Seedance | Veo 3.1 | Sora 2 |
|---|---|---|---|---|
| 鏡頭慢慢推近主角 | `slow dolly-in` | `push in slowly` | `slow camera push-in toward subject` | `the camera slowly pushes in` |
| 繞主角轉一圈 | `360 orbit` | `orbit shot around subject` | `camera orbits the subject` | `camera arcs around the subject` |
| 跟著人走 | `tracking shot` | `follow shot` | `tracking shot following the subject` | `the camera tracks alongside` |
| 空拍下降 | `drone shot descending` | `aerial descent` | `drone shot, descending` | `bird's-eye view descending` |

## 負面鏡頭詞 (常見要避免的)

放在 negative prompt (如模型支援)：
- `jittery camera, erratic motion`
- `camera shake, motion blur (若不想要)`
- `unstable footage`
- `repeated zoom`
- `frame jump, stutter`
