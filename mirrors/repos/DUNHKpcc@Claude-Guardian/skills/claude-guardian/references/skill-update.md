# Skill 更新：每次使用前先查最新

## 1. 什么时候查

- **每个会话开始时查一次**，在回答第一个问题之前。同一个会话里不重复查；会话恢复（`codex resume`）后也不重查，除非用户要求。
- 命令（在 Skill 目录里运行；Windows 用 `py` 或 `python`）：

```
python3 scripts/update_check.py check
```

- 它只读：向 `api.github.com` 发两个 GET 请求，取仓库 main 分支的目录树和最近几条涉及 Skill 的提交，按 git blob 哈希逐个比较本地文件，不下载、不改任何文件。只连 GitHub，不接触 Claude 和 Anthropic，PC0 下照样可以查。属于 A 档，不用问用户。
- 退出码：0 已是最新，1 有更新，2 没查成（连不上、被限流、回复不对），130 被取消。`--json` 输出结构化结果。

## 2. 怎么告诉用户

- **已是最新：**不单独汇报，直接做用户要做的事。
- **有更新：**一句话说有更新，列出远端最近几条更新的日期和标题（脚本输出里有），问用户现在更新还是先用当前版本。用户说先不更新，就用当前版本继续，本会话不再提。
- **没查成：**一句话说没查到、原因（如“连不上 GitHub”），然后用已安装的版本继续，**不阻塞任务**，不反复重试。用户的网络要经代理才能到 GitHub 的，脚本会读取 `HTTPS_PROXY` 等代理变量。
- **本地独有的文件：**脚本会列出本地有、远端没有的文件，可能是用户自己加的，也可能是远端已经删掉的旧文件。更新时逐个问用户留不留，不默认删除。

## 3. 怎么更新

用户同意后由 Agent 执行，属于 B 档（有备份、Agent 自己能撤销）。除了临时克隆和备份目录，不改 Skill 目录以外的东西。

1. **取最新版：**已有仓库克隆的，`git -C <克隆目录> pull --ff-only`；没有的，`git clone https://github.com/DUNHKpcc/Claude-Guardian.git` 到一个新的临时目录。
2. **备份当前 Skill：**把整个已安装的 `claude-guardian` 目录复制到 **Skill 目录之外**（如 `~/.codex/skill-backups/claude-guardian-<日期>`）。不要备份在 `~/.codex/skills/` 里面，否则 Codex 会把备份当成第二个 Skill 加载。
3. **核对用户自己改过的东西：**脚本列出的“不同”里，可能有用户自己改过的文件（二开），“本地独有”里可能有用户自己加的文件。逐个列给用户，问哪些要保留；没有改过的直接用新版。
4. **替换：**删除已安装的 `claude-guardian` 目录，把新版 `skills/claude-guardian` 整个复制过去，再把第 3 步要保留的文件放回原位。保持目录结构，不合并到别的目录里，不嵌套复制。
5. **复查：**再跑一次 `update_check.py check`，应显示已是最新（放回的用户文件会出现在“不同”或“本地独有”里，这是预期）。告诉用户**开一个新会话**，Codex 才会读到新的 SKILL.md。
6. **回滚：**新版有问题，删除新目录，把第 2 步的备份复制回 `~/.codex/skills/claude-guardian`。

Windows 的 Skill 目录通常是 `%USERPROFILE%\.codex\skills`，用 PowerShell 的 `Copy-Item -Recurse` 和 `Remove-Item -Recurse` 做同样的步骤，备份目录同样放在 `skills` 之外。
