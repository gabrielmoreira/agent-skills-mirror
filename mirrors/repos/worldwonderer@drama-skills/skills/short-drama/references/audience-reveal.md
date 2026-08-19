# 观众此刻可以知道什么

背影、腿部入画、门缝、画外声、浅景深和遮挡不只是画面风格。它们同时决定观众**何时**
知道一个人是谁、看见那张字条、或者发现门后有人。

这件事容易被当成构图偏好处理，于是出两种错，而且两种都不会被"这镜好看吗"抓到：

- 本镜本来要交代证据，却被一个漂亮的遮挡挡住了——**该给的没给**；
- 剧本只允许观众先看到鞋和停步位置，结果正脸提前露出来——**不该给的给了**。

所以每个镜头要按**事实**分开记录可见性，而不是给整镜写一句"稍后揭示"。

## 一条记录只管一个事实

这些记录写在镜头的 `audience_visibility[]` 里（字段属于 storyboard 的 shot 记录）。

同一个镜头里，"这人是谁"和"他手里有什么"是两件独立的事，可以有完全不同的揭示条件。
揉成一句，下游就只能一起放或一起收——所以 `audience_visibility` **按事实分条**，
不是每镜一条。

每条记录写清五项：

| 字段 | 回答什么 |
|---|---|
| `fact` | 这条管的是哪一个具体事实 |
| `source_ref` | 这个揭示义务来自剧本的哪一段 |
| `permission` | 现在就给（`show_now`）还是先扣住（`withhold_now`） |
| `carrier` | 观众此刻能看见或听见的是什么 |
| `reveal_trigger` / `protection_method` / `rationale` | 什么时候放、靠什么扣住、为什么 |

### 合成示例

一个镜头里，观众要听见有人叫出主角的旧称呼（说明来者认识他），但**不能**看到来者的脸。

`audience_visibility` 所在的 `shots.jsonl` 在第一行声明本文件引用到的上游快照：

```json
{"record_type":"sources","schema_version":"1.0.0","sources":{"screenplay":{"owner":"short-drama-write","artifact":"剧集/EP001/screenplay.md"}}}
```

数组里每条只写快照键和记录 ID：

```json
[
  {
    "fact": "来者认识主角的旧身份",
    "source_ref": {"src": "screenplay", "record_id": "BLK-EP001-SC003-A02"},
    "permission": "show_now",
    "carrier": "画外一声旧称呼，主角闻声停手",
    "reveal_trigger": "对方开口",
    "rationale": "本镜必须让观众意识到主角被认出来了"
  },
  {
    "fact": "来者是谁",
    "source_ref": {"src": "screenplay", "record_id": "BLK-EP001-SC003-A05"},
    "permission": "withhold_now",
    "carrier": "只有门框边的一只手和影子",
    "protection_method": "来者留在景深之外，不进正面光",
    "reveal_trigger": "下一场推门进屋时",
    "rationale": "身份揭示是场末的转折，提前露脸会让那一下失效"
  }
]
```

两条各有各的条件：**声音放，脸扣住**。写成一条就做不到这件事。

## 不是"神秘感越多越好"

扣住信息本身没有价值，它只在为后面某个具体时刻服务时才有价值。所以
`withhold_now` 必须写出 `reveal_trigger`——说不出什么时候放，就说明这不是设计，
只是没想清楚。

审查时同时核对两侧：原文此刻**允许**透露什么，以及本镜**必须**传达什么。
只评价构图是否漂亮的审查，抓不到这类缺陷。
