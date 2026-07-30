# 分镜诊断目录：可机器判定的那一部分

## 目录

- [这份目录只收什么](#这份目录只收什么)
- [诊断目录](#诊断目录)
- [不进这份目录的东西](#不进这份目录的东西)

## 这份目录只收什么

本文只登记**不需要读懂戏就能判定**的分镜缺陷：时长账目的算术、关键帧声明的边界是否
与它绑定的字段一致。它们由 [storyboard_check.py](../scripts/storyboard_check.py) 执行，
`enforcer` 一律是 `validator`。

分成脚本与审查两条路的理由很实际：账目类错误由人来核对既慢又不可靠——覆盖里少写一个
镜头 ID，肉眼看过去和写全了完全一样。把这类工作交给脚本，审查者的注意力才能留给
真正需要判断的东西。

## 诊断目录

| code | classification | enforcer | 默认 severity | owner | 含义 |
|---|---|---|---|---|---|
| SHT16_RECORD_MISSING | structural_invariant | validator | error | storyboard | 覆盖记录没有 `episode_duration` |
| SHT16_SHOT_LEFT_THE_TOTAL | structural_invariant | validator | error | storyboard | 覆盖列出的镜头既不计入总和也没被挂起 |
| SHT16_SHOT_COUNTED_AND_UNRESOLVED | structural_invariant | validator | error | storyboard | 同一镜头既算进总和又列为未定 |
| SHT16_SHOT_UNRESOLVABLE | structural_invariant | validator | error | storyboard | 时长记录点名的镜头不在镜头文件里 |
| SHT16_COUNTED_SHOT_HAS_NO_DURATION | structural_invariant | validator | error | storyboard | 计入总和的镜头没有数值 `duration_seconds` |
| SHT16_SUSPENDED_SHOT_HAS_A_DURATION | structural_invariant | validator | error | storyboard | 挂起为未定的镜头其实已有时长 |
| SHT16_TOTAL_IS_NOT_THE_SUM | structural_invariant | validator | error | storyboard | 总和不等于各计入镜头时长之和 |
| SHT16_DELTA_IS_WRONG | structural_invariant | validator | error | storyboard | 差值不等于总和减目标 |
| SHT16_DISPOSITION_MISSING | structural_invariant | validator | error | storyboard | 声明了目标却没有对差值的处置 |
| SHT16_DISPOSITION_CLAIMS_A_TARGET | structural_invariant | validator | error | storyboard | 没有目标却给出了判断目标的处置 |
| SHT17_BOUNDARY_ROLE_MISSING | structural_invariant | validator | error | storyboard | 关键帧没声明它冻结的是哪一端 |
| SHT17_BOUNDARY_REF_DISAGREES_WITH_ROLE | structural_invariant | validator | error | storyboard | 声明的角色与绑定的边界字段不一致 |
| SHT17_BOUNDARY_REF_UNRESOLVABLE | structural_invariant | validator | error | storyboard | 关键帧绑定的镜头不在镜头文件里 |
| SHT17_DUPLICATE_BOUNDARY_KEYFRAME | structural_invariant | validator | error | storyboard | 同一镜头的同一端有两张关键帧 |

## 不进这份目录的东西

- **目标时长的差值本身**：`SHT-16` 只让脚本核对差值算得对不对。差值多大是创作者的判断，
  目标时长是计划而不是质量门槛，脚本不因为差值大小报错。
- **关键帧数量**：默认一张首帧，只在交付工作流真的消费尾帧时才有第二张。缺尾帧不是缺陷，
  脚本也不检查"是否该有尾帧"。
- **镜头拆得对不对、景别选得对不对、构图好不好**：这些需要读懂本场在做什么，属于审查者，
  判据在本技能的工艺参考里，不在这份目录。
