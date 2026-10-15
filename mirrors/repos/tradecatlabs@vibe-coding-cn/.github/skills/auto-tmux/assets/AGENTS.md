# .github/skills/auto-tmux/assets Agent 指南

本目录只承载 auto-tmux 的外部资源入口。

## 规则

- 只允许保存指向仓库内 `.github/tools/external/` 的相对软链接。
- 不要复制 `tmux` 或 `oh-my-tmux` 源码到本目录。
- 上游内容更新必须通过 `.github/tools/external/` 下的 Git submodule 指针完成。
- 修改软链接后，运行 `find .github/skills/auto-tmux/assets -maxdepth 1 -type l -printf '%p -> %l\n'` 核对目标。

## 当前已知偏差

法器登记固定的父仓库来源修订 `0a7fdf4ca54d2bb327dcdfc13e816da57ee9c4c2` 中，`oh-my-tmux` 和 `tmux-src` 实际是 0 字节普通文件，不是软链接；“只允许软链接”仍是目标契约，不代表当前路径已满足。不得仅凭预期目标就原地替换；修复须通过法器登记追加可追溯来源修订并保留旧字节摘要。`git submodule update` 只更新目标仓库，不会转换这两个占位文件；`auto-tmux doctor`只检查路径存在，可能对占位文件通过，不能证明链接可用。该说明在新修订通过来源校验且两条入口确为软链接后再退役。

历史核对显示，偏差早于 `.github` 目录迁移：迁移提交 `99adc940a5660763a780c3abc6b4b77465600264` 的父提交中旧路径已是 0 字节普通文件，迁移前README虽要求软链接，实际Git blob仍为空。目录迁移不是这两个入口失效的根因；该历史也不证明更早曾存在有效链接。
