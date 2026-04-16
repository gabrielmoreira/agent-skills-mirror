# Seedance Viral Forge

本仓库名为 Seedance Viral Forge，是一个 Seedance 专用脚本仓库，现在只维护一套生产版 skills，不再保留平行目录。

## Canonical Paths

- `skills/通用场景/SKILL.md`
- `skills/跳舞/SKILL.md`
- `skills/热梗/SKILL.md`
- `shared/SEEDANCE_BASELINE.md`

## Repo Rules

- 生产版 skill 只放 `skills/` 目录下三个文件夹
- 历史草稿、旧快照、实验版统一放 `archive/`
- 默认行为是“先在对话输出”，不是“自动写文件”
- 只有用户明确要求保存时，才落 `.md`
- 改共通规则先改 `shared/SEEDANCE_BASELINE.md`

## Skill Design Standard

每个生产版 `SKILL.md` 都必须回答清楚：

1. 这个 skill 解决什么问题
2. 最小输入是什么
3. 缺字段时怎么补
4. 默认模式怎么走
5. 批量模式何时启用
6. 最终输出长什么样
7. 什么时候不该硬生成

## Don’t Regress

- 不要再写第二套目录结构
- 不要把“默认输出”和“默认保存”混在一起
- 不要把历史实验 prompt 直接塞回生产版
- 不要让 invocation、别名、正文触发词互相打架
