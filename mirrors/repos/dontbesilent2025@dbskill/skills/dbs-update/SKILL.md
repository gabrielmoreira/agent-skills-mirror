---
name: dbs-update
description: |
  dbskill 更新器。用户说「更新 dbskill」「升级 dbskill」「把 dbskill 更新到最新版」「检查 dbskill 更新」或输入 /dbs-update 时使用。只同步 dontbesilent2025/dbskill，不更新用户安装的其他 Skill，不修改用户的 dbskill 存档。
  Update dbskill when the user asks to update, upgrade, or check updates for dbskill.
---

# dbs-update：更新 dbskill

用户已经明确要求更新 dbskill。直接执行更新，不再做第二次文字确认；宿主若要求 Shell 权限，由用户在宿主的权限窗口中决定。

## 更新范围

- 只更新官方仓库 `dontbesilent2025/dbskill`。
- 保留用户在 `~/.dbs/` 中的存档、报告和决策记录。
- 不更新用户安装的其他 Skill。
- 不创建后台任务、定时任务或 Agent Hook。

## 执行步骤

1. 运行以下命令，同步官方 dbskill 的全部正式 Skill 到已支持的 Agent：

   ```bash
   npx -y skills add dontbesilent2025/dbskill -g --all
   ```

2. 命令成功后，告诉用户更新已完成。当前 Agent 若没有立即重新读取 Skill，提醒用户新建一次对话后再使用新能力。

3. 命令失败时，用一句话说明失败原因和下一步需要用户处理的权限或网络问题。不要把完整终端日志直接贴给用户，除非用户要求。

## 回复格式

成功：

> dbskill 已更新完成。当前对话如果还没有读取到新能力，新建一次对话后即可使用。

失败：

> dbskill 没有更新完成：{简短原因}。处理完 {权限或网络问题} 后，再说一次「更新 dbskill」。

## 边界

- 用户只问版本、更新内容或是否需要更新时，先回答问题，不执行命令。
- 用户明确要求检查更新且希望实际同步时，按本 Skill 更新。
- 不使用 `npx skills update`，该命令可能更新用户安装的其他 Skill。
