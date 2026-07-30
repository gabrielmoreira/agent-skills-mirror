# `voice-record-sheet.jsonl` 填写模板

每行一条待录台词。这份表是**剧本的投影，不是第二份台词权威**：`line_text` 必须逐字
等于 `source_ref` 指向的剧本块，需要改词就改剧本再重新投影，不在这里改。示例值不是
默认答案；不适用的字段删掉，不要添加媒体任务、供应商或接口。

录音的顺序几乎从不是剧情顺序——通常按人物集中录，所以**配音者失去的正是上下文**。
本表存在的理由就是把上下文补回去：他此刻知道什么、对谁说、上一句是谁说的、这一句要
达成什么。缺了这些，剩下的只是一串没有处境的句子。

```json
{
  "line_id": "VLINE-EP001-SC001-003",
  "episode_id": "EP001",
  "scene_id": "EP001-SC001",
  "speaker": "CHAR-<id>",
  "speaker_display": "<剧本里逐字写的那个名字>",
  "line_text": "<逐字等于剧本块原文的冒号之后部分>",
  "source_ref": {
    "owner": "short-drama-write",
    "artifact": "episodes/EP001/screenplay-index.jsonl",
    "hash": "<sha256>",
    "record_id": "BLK-EP001-SC001-D03"
  },
  "channel": "sync | dubbed | VO | OS",
  "lip_sync_constrained": true,
  "addressed_to": ["CHAR-<id>"],
  "preceding_line_id": "VLINE-EP001-SC001-002",
  "speaker_knows_now": "<此刻他知道什么、还不知道什么>",
  "tactic": "<质问 | 试探 | 收回 | 交换 | 拖延……：这一句要达成什么>",
  "pronunciation_notes": [
    {
      "surface": "<多音字、生僻字、专名或数字>",
      "reading": "<确定读法>",
      "decided_by": "creator | <role>:<stable-id>"
    }
  ],
  "target_seconds": null,
  "unresolved": []
}
```

## 字段为什么是这些

| 字段 | 不写会怎样 |
|---|---|
| `source_ref` | 剧本改一句而表没跟上，录出来的是旧词；有 `hash` 才能被标 `stale` |
| `speaker` 与 `speaker_display` | 前者是资产身份用于绑定，后者是剧本里逐字写的名字；只留一个就必然有一处对不上 |
| `channel` 与 `lip_sync_constrained` | 同期与配音、画内与 VO 的可改余地完全不同，混在一起就只能按最严的来 |
| `addressed_to` / `preceding_line_id` | 集中录制时配音者不知道在对谁说、接谁的话，语气只能靠猜 |
| `speaker_knows_now` | 同一句话在"已经知道"和"还不知道"下是两种读法，这是最常见的重录原因 |
| `tactic` | 情绪词（"愤怒"）不可执行；策略可执行。见对白工艺的策略库 |
| `pronunciation_notes` | 专名与多音字在录音棚里是最贵的中断；决定要在进棚前做完并留痕 |
| `target_seconds` | 有画面时长约束的行要提前知道，不要在混录时才发现塞不下 |

## 边界

- **本表不拥有台词文字、说话人和信息权限**，它们属于剧本；本表也不拥有逐镜的音频实现
  （空间化、层级、与画面的对位），那属于视频提示词环节，本表只引用不复制。
- 表里出现与剧本不一致的文字时，**剧本为准**，把差异作为 `unresolved` 记下来交给
  负责人，不要就地"顺一下"。
- 本套件不生成音频、不调用任何语音服务，也不从这份文本判断成品音质。
