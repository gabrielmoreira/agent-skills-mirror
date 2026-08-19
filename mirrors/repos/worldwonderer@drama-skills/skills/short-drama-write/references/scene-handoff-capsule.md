# 单集分批续写交接胶囊

长单集跨多轮写作、上下文即将切换或中断恢复时，用一张短胶囊把“接下来必须记住的变化”
交给下一轮。胶囊是从当前剧本派生的临时工作记忆，**不是第二份权威**；任何冲突都以
已接受的 `screenplay.md`、单集契约和连续性来源为准。

## 何时建立

- 当前轮无法安全完成整集，但已经写完一个有明确退出状态的场景或场景组；
- 下一轮只需续写，不值得重新加载整份上游与全部已完成正文；
- 会话压缩或恢复需要准确找到最后一个已接受块。

短场景、一次完成的单集或只做局部改字时不建立。不要按固定场景数或字数强制分批。

## 最小字段

```yaml
scene_handoff_capsule:
  authority: derived
  sources:
    screenplay: {owner: short-drama-write, artifact: 剧集/<EP>/screenplay.md}
  screenplay_ref: {src: screenplay}
  current_scene:
    scene_id: EPxxx-SCxxx
    agenda: 当前人物正在争取什么
    opposition: 谁/什么正在反制
    turn: 刚发生的方向变化
    exit_state: 场景结束后谁能做什么、不能做什么
  changed_state:
    story: [知识/关系/权力/风险/决定的变化]
    physical: [位置/持物/伤势/造型/环境的变化]
  setup_debt: [仍待兑现或明确放弃的 setup ID/ref]
  information_permissions: [谁知道/误信/怀疑什么，观众此刻能知道什么]
  next_scene_pressure: 下一场由哪个已发生结果发动
  tail_locator: {block_id: <last-accepted-block>}
  unresolved: [不得由续写者自行补齐的选择]
```

只记录变化和下一步依赖，不复制整段正文、角色小传、资产 设定集 或所有旧节拍。`tail_locator`
必须指向当前已接受剧本尾部；如果只完成 candidate，明确保留 candidate authority，不能写成
accepted。

## 恢复步骤

1. 先确认 `sources.screenplay` 指的还是当前剧本；剧本已经改过就丢弃胶囊，重新从当前剧本恢复。
2. 用 `tail_locator` 读最后一个块及其相邻上下文，确认语气、动作和状态确实对得上。
3. 读取下一场直接依赖的单集契约、setup/payoff 与连续性引用；不预加载无关 reference。
4. 写下一场前重新回答 agenda、opposition、turn、exit_state，不能把胶囊里的候选当既定剧情。
5. 场景发布后重建或删除胶囊：重新从当前剧本派生 `sources` 与 `tail_locator`。

胶囊帮助恢复注意力，不替代创作者接受、稳定索引或审查。
