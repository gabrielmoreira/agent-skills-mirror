# 分镜诊断目录：可机器判定的那一部分

## 目录

- [这份目录只收什么](#这份目录只收什么)
- [诊断目录](#诊断目录)
- [不进这份目录的东西](#不进这份目录的东西)

## 这份目录只收什么

本文只登记**不需要读懂戏就能判定**的分镜缺陷：时长账目的算术、关键帧声明的边界是否
与它绑定的字段一致、边界条目有没有写成常见的回指说法、每条引用是否解析得到一个上游快照。它们由
[storyboard_check.py](../scripts/storyboard_check.py) 执行，`enforcer` 一律是 `validator`。
脚本读引用时先取文件的 `sources` 声明，再按每条引用的 `src` 取回 `owner` 与 `artifact`。

分成脚本与审查两条路的理由很实际：账目类错误由人来核对既慢又不可靠——覆盖里少写一个
镜头 ID，肉眼看过去和写全了完全一样。把这类工作交给脚本，审查者的注意力才能留给
真正需要判断的东西。

## 诊断目录

| code | classification | enforcer | 默认 severity | owner | 含义 |
|---|---|---|---|---|---|
| REF_SRC_IS_NOT_DECLARED | structural_invariant | validator | error | storyboard | 引用的 `src` 在本文件 `sources` 里没有声明 |
| REF_HAS_NO_UPSTREAM_BINDING | structural_invariant | validator | error | storyboard | 引用既没有 `src`，也没有完整的 `owner`/`artifact` |
| REF_IS_NOT_AN_OBJECT | structural_invariant | validator | error | storyboard | 引用位置上不是一个对象 |
| SOURCE_ENTRY_IS_INCOMPLETE | structural_invariant | validator | error | storyboard | `sources` 条目缺少 `owner` 或 `artifact` |
| SHT05_BOUNDARY_ENTRY_IS_A_BACK_REFERENCE | structural_invariant | validator | error | storyboard | 边界条目整条是「同上」「位置不变」这类回指，没有写出绝对事实 |
| SHT16_RECORD_MISSING | structural_invariant | validator | error | storyboard | 覆盖记录没有 `episode_duration` |
| SHT16_RECORD_INCOMPLETE | structural_invariant | validator | error | storyboard | `episode_duration` 缺少 `counted_shot_ids` 或 `unresolved_durations` |
| SHT16_SHOT_LEFT_THE_TOTAL | structural_invariant | validator | error | storyboard | 覆盖列出的镜头既不计入总和也没被挂起 |
| SHT16_SHOT_COUNTED_AND_UNRESOLVED | structural_invariant | validator | error | storyboard | 同一镜头既算进总和又列为未定 |
| SHT16_SHOT_UNRESOLVABLE | structural_invariant | validator | error | storyboard | 时长记录点名的镜头不在镜头文件里 |
| SHT16_COUNTED_SHOT_HAS_NO_DURATION | structural_invariant | validator | error | storyboard | 计入总和的镜头没有数值 `duration_seconds` |
| SHT16_SUSPENDED_SHOT_HAS_A_DURATION | structural_invariant | validator | error | storyboard | 挂起为未定的镜头其实已有时长 |
| SHT16_TOTAL_MISSING | structural_invariant | validator | error | storyboard | `shot_seconds_total` 不是数值 |
| SHT16_TOTAL_IS_NOT_THE_SUM | structural_invariant | validator | error | storyboard | 总和不等于各计入镜头时长之和 |
| SHT16_DELTA_MISSING | structural_invariant | validator | error | storyboard | 声明了目标却没有带符号差值 |
| SHT16_DELTA_IS_WRONG | structural_invariant | validator | error | storyboard | 差值不等于总和减目标 |
| SHT16_SHOT_LISTED_TWICE | structural_invariant | validator | error | storyboard | 同一镜头在时长记录里出现多次，会被加两次 |
| SHT16_EPISODE_SHOT_LEFT_THE_TOTAL | structural_invariant | validator | error | storyboard | `shots.jsonl` 里的镜头既不计入总和也没被挂起 |
| SHT16_DISPOSITION_MISSING | structural_invariant | validator | error | storyboard | 声明了目标却没有对差值的处置 |
| SHT16_DISPOSITION_CLAIMS_A_TARGET | structural_invariant | validator | error | storyboard | 没有目标却给出了判断目标的处置 |
| SHT17_KEYFRAME_HAS_NO_ID | structural_invariant | validator | error | storyboard | 关键帧记录没有 `keyframe_id` |
| SHT17_BOUNDARY_ROLE_MISSING | structural_invariant | validator | error | storyboard | 关键帧没声明它冻结的是哪一端 |
| SHT17_BOUNDARY_REF_MISSING | structural_invariant | validator | error | storyboard | 关键帧没有绑定它投影的边界 |
| SHT17_BOUNDARY_REF_DISAGREES_WITH_ROLE | structural_invariant | validator | error | storyboard | 声明的角色与绑定的边界字段不一致 |
| SHT17_BOUNDARY_REF_UNRESOLVABLE | structural_invariant | validator | error | storyboard | 关键帧绑定的镜头不在镜头文件里 |
| SHT17_DUPLICATE_BOUNDARY_KEYFRAME | structural_invariant | validator | error | storyboard | 同一镜头的同一端有两张关键帧 |
| SHT01_BLOCK_UNCLAIMED | structural_invariant | validator | error | storyboard | 处理为 `covered`/`intentional_repeat` 的块没有镜头认领 |
| SHT01_BLOCK_CLAIMED_TWICE | structural_invariant | validator | error | storyboard | 非 `intentional_repeat` 的块被多个镜头认领 |
| SHT01_BLOCK_IS_ON_SCREEN_ANYWAY | structural_invariant | validator | error | storyboard | 记为不拍的块却有镜头认领 |
| SHT01_BLOCK_NOT_IN_SCREENPLAY | structural_invariant | validator | error | storyboard | 镜头认领的块不在剧本索引里 |
| SHT01_BLOCK_HAS_NO_DISPOSITION | structural_invariant | validator | error | storyboard | 有制作相关的块没有写处理 |
| SHT01_DISPOSITIONS_MISSING | structural_invariant | validator | error | storyboard | 覆盖表没有 `dispositions` |
| SHT01_DISPOSITION_MALFORMED | structural_invariant | validator | error | storyboard | 处理行不是对象或没点名块 |
| SHT01_DISPOSITION_UNKNOWN | structural_invariant | validator | error | storyboard | 处理不是工作流定义的四种之一 |
| SHT01_DISPOSITION_REPEATED | structural_invariant | validator | error | storyboard | 同一个块写了多行处理 |
| SHT01_DISPOSITION_NOT_IN_SCREENPLAY | structural_invariant | validator | error | storyboard | 处理点名的块不在剧本索引里 |
| SHT01_DISPOSITION_HAS_NO_REASON | structural_invariant | validator | error | storyboard | 重复或省略是决定，必须写理由 |
| SHT01_SCREENPLAY_IS_NOT_FULLY_INDEXED | structural_invariant | validator | error | storyboard | 剧本索引里还有没归类的行，覆盖检查看不到剧本的全部 |

## 不进这份目录的东西

- **目标时长的差值本身**：`SHT-16` 只让脚本核对差值算得对不对。差值多大是创作者的判断，
  目标时长是计划而不是质量门槛，脚本不因为差值大小报错。
- **关键帧数量**：默认一张首帧，只在交付工作流真的消费尾帧时才有第二张。缺尾帧不是缺陷，
  脚本也不检查"是否该有尾帧"。
- **镜头拆得对不对、景别选得对不对、构图好不好**：这些需要读懂本场在做什么，属于审查者，
  判据在本技能的工艺参考里，不在这份目录。
