# 角色卡结构

`cast.json` 顶层：

```json
{
  "source": "渡口",
  "summary": "民国年间的清晨，一条河的渡口浓雾未散。摆渡四十年的老船夫照常开船，先后上船的是……",
  "characters": [ /* 角色卡 */ ]
}
```

| 顶层字段 | 必填 | 说明 |
| --- | --- | --- |
| `source` | 是 | 书名/篇名，报告标题用 |
| `summary` | 是 | **故事摘要**，中文 3–5 句。交代时空背景、核心情境、人物聚在一起的由头。报告顶部显示，让人不看原文也知道这几个角色是什么关系。不要剧透结局，也不要写成推荐语 |
| `characters` | 是 | 角色卡数组 |

`summary` 缺失会被 `validate` 判为违规——报告顶部会空着。

单张角色卡：

```json
{
  "name": "老周",
  "aliases": ["老伯"],
  "importance": "major",
  "oneLiner": "在渡口摆渡四十年的老船夫，一只眼睛是白的。",

  "persona": {
    "gender": "男",
    "ageRange": "约七十岁（推断）",
    "identity": "渡口船夫",
    "appearance": "背驼得像一张拉满的弓。左眼被风沙磨得只剩一层白翳。……",
    "personality": ["沉默", "耐性", "老练"],
    "temperament": "开口时嗓子里像卡着半口江水，含混、发沉。……",
    "motivation": "把船开过去。雾再厚也照常开船。",
    "arc": "静止。他是这条河的一部分。",
    "relationships": [{ "name": "沈知微", "relation": "向他问路的年轻渡客" }],
    "evidence": ["雾一厚，连自己的手都看不清。"]
  },

  "image": {
    "style": "Flat vector cartoon with ink-wash colouring",
    "prompt": "Character design sheet of an elderly Chinese ferryman ...",
    "promptZh": "角色设定图：约七十岁的中国老船夫……",
    "negativePrompt": "photorealistic, 3d render, young face, ...",
    "tags": ["flat vector", "character sheet", "ink wash palette"],
    "turnaround": "Orthographic character turnaround model sheet: three full-body views ..."
  },

  "voice": {
    "timbre": "沙哑低沉的男中低音，喉音重",
    "pitch": "低",
    "pace": "缓慢，字与字之间拖着气口",
    "accent": "南方水乡口音，尾音含混",
    "emotion": "疲惫而平静",
    "prompt": "An elderly male voice, around seventy-five. Low bass-baritone ...",
    "promptZh": "约七十五岁的老年男声。低音区男中低声部……",
    "referenceHint": "像一个在同一个渡口喊了四十年「开船」的人"
  }
}
```

## 字段约束

| 字段 | 类型 | 语言 | 说明 |
| --- | --- | --- | --- |
| `name` | string | 原文 | 原文里用得最多的称呼 |
| `aliases` | string[] | 原文 | 其他称谓；职业名词（如「货郎」）归 `identity`，不进这里 |
| `importance` | enum | — | `protagonist` / `major` / `supporting` / `minor`，**只能这四个** |
| `oneLiner` | string | 中文 | 一句话抓住这个人 |
| `persona.*` | — | **中文** | 全部中文。`personality` 3–5 个词 |
| `persona.evidence` | string[] | 原文 | **逐字引用**，没有就空数组 |
| `image.style` | string | 英文 | 画风一句话 |
| `image.prompt` | string | **英文** | 卡通角色设定图；**禁止出现人名** |
| `image.promptZh` | string | 中文 | 上面那条的中文版；**同样禁止人名** |
| `image.negativePrompt` | string | **英文** | 逗号分隔 |
| `image.tags` | string[] | **英文** | 4–8 个风格标签 |
| `image.turnaround` | string | **英文** | 正/侧/背三视图；**禁止出现人名** |
| `voice.timbre/pitch/pace/accent/emotion/referenceHint` | string | **中文** | 最容易写成英文的地方，注意 |
| `voice.prompt` | string | **英文** | 给 TTS 音色设计引擎 |
| `voice.promptZh` | string | 中文 | 上面那条的中文版 |

## 校验

`scripts/novel-characters.mjs validate <cast.json> <book.txt>` 会检查：结构完整性、`importance` 枚举、**引文逐字**、**出图提示词不含人名**、**语言分工**。违规逐条列出并 exit 1。
