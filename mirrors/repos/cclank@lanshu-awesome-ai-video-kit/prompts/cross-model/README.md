# Cross-Model Prompt Matrix · 跨模型对照矩阵

> **10 个核心场景 × 11 个主流模型 = 110 条精心撰写的对照 prompt**。每条都严格遵循对应模型的官方公式与最佳实践，便于横向对比各模型的 prompt 风格差异，也作为 [`prompt-translator` skill](../../skills/prompt-translator/SKILL.md) 的基准查表数据。

## 这是什么 / 为什么有用

普通的提示词库（如 [prompts/](../README.md) 里的 269 条）是**按模型分散**的 — 每个模型独立的最佳样例。但**没法直接对比"同一个想法在不同模型上的最佳写法到底差在哪"**。

这个矩阵恰好补这一块：

- 🎬 你想做一个"奢华香水广告" → 一眼看到 11 个模型各自最妙的写法
- ⚠️ Sora 2 即将停止 → 看 Sora 写法 → 直接看同一场景在 Veo / Kling / Runway 上怎么改
- 📊 想理解模型差异 → 横向看就懂"哦,Wan 的 lip-sync 体现在 Sound 段写法上"
- 🤖 未来 prompt-translator skill → 这就是它需要的基准数据

## 数据结构

数据源：[`prompts/data/cross-model-matrix.json`](../data/cross-model-matrix.json)

每个场景含：
- `core_anchor`：所有模型共享的视觉/叙事元素（保证"同一场景"）
- `by_model`：11 个模型各自的最佳 prompt + 用了什么方法

## 5 个核心场景

| # | 场景 | 维度覆盖 | 适用 |
|---|---|---|---|
| 1 | [奢华香水旋转广告](#1-奢华香水旋转广告) | 商业 / 产品 / 静态主体 / 慢镜旋转 | 电商 / 品牌广告 / 时尚视频 |
| 2 | [金色时刻情侣重逢](#2-金色时刻情侣重逢) | 叙事 / 双人对话 / 情感 / 原生音频 | 短剧 / 情感广告 / 影视片段 |
| 3 | [滑板 Kickflip 慢动作](#3-滑板-kickflip-慢动作) | 动作 / 物理仿真 / 慢镜 / 户外光 | 运动品牌 / 短视频爆款 |
| 4 | [图生视频:咖啡馆肖像](#4-图生视频咖啡馆肖像) | 图生视频 / 只描述运动 / 微表情 | 静态海报转动态短视频 |
| 5 | [办公室会议三人讨论](#5-办公室会议三人讨论) | 多角色 / 多人对话 / 唇同步 / 室内 | 企业宣传 / SaaS 演示 |

## 怎么用

**3 种方式**：

1. **Web 矩阵专页**（推荐）→ [tools/cross-model/index.html](../../tools/cross-model/index.html) — 表格式横向对比 + 一键复制
2. **直接看数据** → [data/cross-model-matrix.json](../data/cross-model-matrix.json)
3. **下面浏览** → 按场景展开看每个模型的写法

---

## 1. 奢华香水旋转广告

**核心元素**：透明矩形玻璃香水瓶 + 琥珀金色液体 / 黑色大理石台面 / 侧光 + 镜面反射 / 缓慢 360° 旋转 / 喷雾慢动作

| 模型 | 方法 | 一句话亮点 |
|---|---|---|
| **Seedance 2.0** | 8 要素工程指令 | 全套细节 + 约束词收紧 |
| **HappyHorse 1.0** | 30-55 词紧凑 + audio | 单镜头紧凑展示 |
| **Kling 3.0** | 5 层进阶 | Scene/Characters/Action/Camera/Audio 结构化 |
| **Sora 2** | Shot List 分层 | Style 段锚定 35mm 胶片美学 |
| **Veo 3.1** | 8 元素 + Dialogue:/Audio: | 双层音频标记 |
| **Runway Gen-4.5** | subject+action+setting+camera | 紧凑实用 |
| **Pika 2.5** | 短聚焦 + no morphing | "no morphing" 防形变 |
| **Hailuo 02** | Director's AI + 物理细节 | 强调"accurate fluid dynamics" |
| **Hunyuan 1.5** | Master 模式重写 | 强调构图/光照/运镜 |
| **Wan 2.7** | Entity+Scene+Motion+Sound | Sound 段含 voiceover |
| **即梦 AI** | 8 维度中文 + 中式美学 | 中文配音"时间,会沉淀真正的美" |

→ 完整 11 条 prompt 见 [JSON](../data/cross-model-matrix.json) 中 `scene-1-perfume`

---

## 2. 金色时刻情侣重逢

**核心元素**：两位 30 岁初男性 / 公园长椅黄金时刻 / 落叶飘落 / 一坐一识 / 共笑 / 简短对白

| 模型 | 方法亮点 |
|---|---|
| **Seedance** | 分镜时序写 3 个镜头(走近/识别/共笑) |
| **HappyHorse** | 8s 时序节拍(First 4s/Final 4s) |
| **Kling** | 5 层全开 + 中文对白角色定向发声 |
| **Sora** | Style 锚定 2010s 美国 indie drama + 35mm halation |
| **Veo** | Dialogue: 多人对白专项(强项) |
| **Runway** | 提示后续可用 Aleph re-light 调情绪 |
| **Pika** | 改成单一聚焦时刻(避开多人对白短板) |
| **Hailuo** | 强调"breath visible in cool air"等物理细节 |
| **Hunyuan** | Master 模式 + 写实人物刻画 |
| **Wan** | lip-sync 唇同步 + 多人对白同步 |
| **即梦** | 8 维度中文 + 中式情感叙事 |

→ 完整 11 条 prompt 见 [JSON](../data/cross-model-matrix.json) 中 `scene-2-reunion`

---

## 3. 滑板 Kickflip 慢动作

**核心元素**：20 岁滑板少年 / 城市傍晚停车场 / 湿润沥青反光 / 起跳→板飞旋→接板落地 / 物理感

| 模型 | 方法亮点 |
|---|---|
| **Seedance** | 8 要素 + 动作细化(具体到"后脚 pop tail / 前脚 drag diagonally") |
| **HappyHorse** | 30-55 词 + 时序节拍 + audio |
| **Kling** | 5 层 + 物理动作细节描述 |
| **Sora** | Style: Urban skate cinematography 锚定 + Actions 拆 beats |
| **Veo** | Audio: 多层(tail pop / wheels / deck slap / knee absorption) |
| **Runway** | 紧凑 + "preserve clean body proportion" 约束 |
| **Pika** | 单一动作时刻聚焦 + no morphing |
| **Hailuo** | ★★★★★ 物理之王 — "accurate angular momentum" / "weight transfer" |
| **Hunyuan** | Master 模式 + "photorealistic motion blur on grip tape" |
| **Wan** | Entity+Scene+Motion+Sound + 滑板音效精彩 |
| **即梦** | 中文 8 维度 + 国内潮酷美学 |

→ 完整 11 条 prompt 见 [JSON](../data/cross-model-matrix.json) 中 `scene-3-kickflip`

---

## 4. 图生视频:咖啡馆肖像

**核心元素**：雨夜咖啡馆窗边女子(参考图) / 抬头微笑望镜头 / 雨势加大 / 霓虹闪烁 / 只描述运动

**铁律**：图生视频**只描述运动,不重复图中已有视觉**。这条规则在 11 个模型里高度共通。

| 模型 | 方法亮点 |
|---|---|
| **Seedance** | 「参考@图片1」语法 + 中文运动描述 |
| **HappyHorse** | 30-55 词紧凑 + audio + "the woman in the reference image" |
| **Kling** | ★★★★★ Motion Brush 强项 — 只描述运动 |
| **Sora** | Style 段 "preserve all visual details exactly" 锚定连续性 |
| **Veo** | "Continuation of the reference image" + Audio: 多层 |
| **Runway** | "preserve all original visual details exactly" + Gen-4.5 / Aleph 编辑可选 |
| **Pika** | 简短 + "preserve original image style exactly" |
| **Hailuo** | 强调"realistic weight" / "natural neck muscle tension" 等物理 |
| **Hunyuan** | I2V + 微动作("subtle hair drift") |
| **Wan** | I2V + Sound 含咖啡杯触托盘声 |
| **即梦** | 中文图生视频 + 风格连续性约束 |

→ 完整 11 条 prompt 见 [JSON](../data/cross-model-matrix.json) 中 `scene-4-i2v-cafe`

---

## 5. 办公室会议三人讨论

**核心元素**：3 位专业人士(2 男 1 女)圆桌 / 现代极简会议室 / 依次发言 / 多人对白 / 唇同步

**这场景能区分模型的多人对话能力**：Veo / Wan / Kling 是这类场景的最优解,Pika / HappyHorse 多人对白短板明显。

| 模型 | 方法亮点 |
|---|---|
| **Seedance** | 分镜时序 + 多主体标签锁定(经理 M/设计师 D/工程师 E) |
| **HappyHorse** | 改成女经理单镜头(避开多人对白短板) |
| **Kling** | 5 层 + 中文对白 + 角色定向发声 |
| **Sora** | 分层 Shot List + 多 dialogue beats |
| **Veo** | ★★★★★ Dialogue: 多人专项 — 看家场景 |
| **Runway** | Gen-4.5 多镜头 + 可后续 Aleph re-light |
| **Pika** | 单一聚焦 — 改成女经理白板时刻 |
| **Hailuo** | 强调"clasping table edge" / "marker tap" 物理细节 |
| **Hunyuan** | Master 模式 + 多角色描述 |
| **Wan** | ★★★★★ lip-sync 多人 — 看家场景 |
| **即梦** | 中文 8 维度 + 国内职场美学 |

→ 完整 11 条 prompt 见 [JSON](../data/cross-model-matrix.json) 中 `scene-5-meeting`

---

## 路线图

| 版本 | 内容 |
|---|---|
| **v1（当前）** | 5 场景 × 11 模型 = 55 条 |
| v2（计划） | 加 5 场景：恐怖悬疑 / 自然延时 / 抽象艺术 / 武侠决斗 / 萌宠 |
| v3（计划） | 每条 prompt 附实测效果截图 / 视频对比 |
| v4（计划） | 基于此数据训练 `prompt-translator` skill |

## 贡献

发现某条 prompt 不符合该模型的最佳实践？欢迎 PR：
- 编辑 [data/cross-model-matrix.json](../data/cross-model-matrix.json)
- 在 commit message 说明实测对比效果
- 优先收录有**实测截图**或**生成视频**的提交
