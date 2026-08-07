**中文** · [English](README.en.md)

# shuohao-skills

给 AI 编码 agent 用的 skill 集合。**Claude Code 和 codex 都能跑。**

| Skill | 做什么 |
| --- | --- |
| [**novel-characters**](skills/novel-characters) | 把一篇小说拆成角色设定集：人物画像、卡通形象提示词、音色提示词、三视图 |

## 装

```bash
git clone https://github.com/eternityspring/shuohao-skills.git
cd shuohao-skills
./scripts/install.sh
```

自动检测本机装了 Claude Code 还是 codex，把所有 skill **软链**过去——`git pull` 之后立刻生效，不用重装。

```bash
./scripts/install.sh novel-characters   # 只装某一个
./scripts/install.sh --codex            # 只装到 codex
./scripts/install.sh --uninstall        # 取消软链
```

不想用脚本就自己链：

```bash
ln -s "$PWD/skills/novel-characters" ~/.claude/skills/novel-characters
ln -s "$PWD/skills/novel-characters" ~/.codex/skills/novel-characters
```

## 前置条件

| | 必需？ | 说明 |
| --- | --- | --- |
| **Node** | 必需 | ≥ 18。skill 的脚本只用标准库，**没有 npm 依赖，不需要 install** |
| **模型额度** | 必需 | 用你当前会话的额度，**不需要任何 API key** |
| **codex CLI** | 可选 | 出图才用得上（走内置 `$imagegen`）。没有就跳过出图，其余产出照常 |

## 仓库约定

每个 skill 一个目录，**自包含、可以单独拷走**：

```
skills/<skill-name>/
├── SKILL.md          给 agent 读的工作流（必需）
├── README.md         给人读的说明
├── scripts/
│   ├── <name>.mjs    确定性工具，零依赖
│   └── selftest.mjs  自测，不调模型（必需）
├── references/       按需加载的详细指令
├── examples/         自带样例，同时当测试夹具
└── assets/           截图
```

两条硬要求：

- 每个 skill 必须有 `SKILL.md`
- 每个 skill 必须有 `scripts/selftest.mjs`，**不调用模型、不花额度**，覆盖全部确定性逻辑

（`ci/selftest.yml` 会检查这两条，但那个 workflow **还没启用**——见下。）

本地跑全部自测：

```bash
for f in skills/*/scripts/selftest.mjs; do node "$f"; done
```

### 启用 CI（尚未启用）

`ci/selftest.yml` 是现成的 GitHub Actions workflow：Ubuntu + macOS × Node 18/22/24，自动发现 `skills/*/scripts/selftest.mjs`，加新 skill 不用改它。

它**没有**放在 `.github/workflows/` 下，所以现在不会运行——推送那个路径需要 token 的 `workflow` 权限。也就是说：**目前所有测试只在 macOS + Node 24 上跑过。** 启用：

```bash
gh auth refresh -h github.com -s workflow   # 授权一次
mkdir -p .github/workflows
git mv ci/selftest.yml .github/workflows/
git commit -m "ci: enable selftest workflow" && git push
```

## License

[Apache 2.0](LICENSE)
