---
name: huashu-skill-updater
description: 检查并更新花叔系 skills。用户说「检查skill更新」「更新花叔的skill」「skill是不是最新的」时触发。按各仓库的版本标签判断有没有新版本，只提示，是否更新由用户决定。
---

# huashu-skill-updater — 花叔系 Skill 更新检查

花叔的 skill 都在持续迭代（修 bug、补方法论、加能力）。这个 skill 负责让用户装过的版本不掉队。

## 全量检查（首选）

```bash
python3 ~/.claude/skills/huashu-skill-updater/scripts/check_updates.py
```

脚本会扫描 skills 目录下所有花叔系 skill（识别标准：目录带 `.git` 且 origin 指向 alchaincyf，或存在 `.huashu-skill-meta.json`），输出「已最新 / 有更新 / 无法判断」三态报告。有更新时 exit code 为 1，方便接 cron。

怎么算「有新版本」：git 安装的 skill，比较 SKILL.md 开头 `metadata.version` 和远程仓库最大的 `vX.Y.Z` 标签。作者只在实质更新（新能力、行为变化、修 bug）时打标签，改错字、改 README 不打，所以不会因为小改动反复提醒。检查只读取远程标签，不下载文件、不上传数据。复制安装的 skill 没有版本号，仍按来源仓库的 commit 比较。

加 `--mark-checked` 会在联网成功后刷新各 skill 的检查日期（联网失败不刷新）：

```bash
python3 ~/.claude/skills/huashu-skill-updater/scripts/check_updates.py --mark-checked
```

## 执行更新

- git 安装的 skill（独立仓库）：`git -C ~/.claude/skills/<名字> pull --ff-only`
- 复制安装的 skill（huashu-skills 内置，或 dukou）：重新 clone 来源仓库到临时目录，把对应子目录覆盖复制回去，然后更新 `.huashu-skill-meta.json` 里的 `commit` 和 `installed_at`：

```bash
git clone --depth 1 https://github.com/alchaincyf/huashu-skills.git /tmp/huashu-skills-update
rm -rf ~/.claude/skills/<名字> && cp -r /tmp/huashu-skills-update/<名字> ~/.claude/skills/
```

更新前如果用户对该 skill 做过本地改动（`git status` 有未提交修改，或复制安装的目录 mtime 晚于 installed_at），先提醒用户会被覆盖，让用户确认。

## 元数据约定

复制安装的 skill 必须在其目录里带一个 `.huashu-skill-meta.json`（安装它的 agent 负责写入）：

```json
{
  "name": "huashu-slides",
  "repo": "alchaincyf/huashu-skills",
  "subdir": "huashu-slides",
  "commit": "安装时来源仓库的 HEAD sha（git rev-parse HEAD）",
  "installed_at": "YYYY-MM-DD",
  "last_checked": "YYYY-MM-DD"
}
```

git clone 安装的 skill 不需要这个文件，`.git` 本身就是元数据。另外每个独立仓库 skill 的 SKILL.md 末尾自带「版本检查」段：agent 使用该 skill 时读目录里的 `.last-update-check`（一行日期加结果，如 `2026-10-13 ok`），上次成功不足 30 天、上次失败不足 7 天就跳过，到期才读一次远程版本标签；用户把内容改成 `off` 就永久不检查。`check_updates.py --mark-checked` 联网成功后会同时刷新这个文件，避免刚全量检查完又被单个 skill 重复提醒。

## 每月定期检查

推荐用户任选其一：

- 每月对 agent 说一句「检查花叔skill更新」
- 挂 cron，每月 1 号早上跑一次：

```
0 9 1 * * python3 ~/.claude/skills/huashu-skill-updater/scripts/check_updates.py --mark-checked
```

## 给 agent 的行为规则

1. 触发本 skill 后先跑 `check_updates.py`，把报告翻译成人话给用户：哪些最新、哪些落后几个 commit、更新命令是什么。
2. 不要不问就更新——列出有更新的 skill，让用户决定更新哪些（用户明确说「全部更新」除外）。
3. 单个 skill 的到期检查由它自己的「版本检查」段负责，本 skill 不重复提醒。
4. skills 目录不在 `~/.claude/skills/` 时（项目级安装、其他 agent），用 `--skills-dir` 指定。
