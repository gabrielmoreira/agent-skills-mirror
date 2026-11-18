# capsule-cinema

开源的本地生成流程：https://github.com/JuneYaooo/capsule-cinema

## 能做什么

按拆解结果逐镜生成 AI 镜头，拼回原时间线；`rea-video remake-plan` / `remake-run` 直接对接。

## 费用

- capsule-cinema 本身免费开源，本地部署。
- 模型和密钥用户自己配，按模型调用计费，费用付给模型平台。
- 生成前先 `--dry-run` 给用户看调用次数和费用，用户同意再跑。

## 用户要用时：帮他装好接上

由你帮用户装好、接上，做到用户能直接开始。装之前说清装什么、从哪装；花钱的事由用户决定。已经知道的（参考视频、报告、要换成什么）不要再问。

1. 没装（`rea-video remake-plan` 报找不到仓库）：读 https://raw.githubusercontent.com/JuneYaooo/capsule-cinema/main/docs/install.md 照着装；装好后 `rea-video prefs capsule_root <安装目录>` 记下，`remake-run` 用装了它依赖的那个 Python（`--python`）。
2. 密钥让用户自己填进安装目录的 `.env`，只告诉用户要填哪几个变量名，不要让用户把密钥贴进对话。
3. 按 SKILL.md「复刻」问模型、要换什么，`rea-video plan` 出方案，再按下面出任务、dry-run、跑、拼回原时间线。

## 怎么跑

`remake-plan` 照报告第二部分的方案出任务（一个单元的每次调用一个任务，用 `remake/prompts.json` 里的最终提示词），方案检查有 ❌ 时不出任务；`remake-run` 交给 capsule-cinema 跑完，`remake` 按原片切点拆回各镜头。方案不迁就执行端：capsule-cinema 还没接的模型会在 `remake-run` 时报错，这时把提示词和 `remake/refs/` 里的参考交给用户在模型自己的平台上生成。

生成要用 capsule-cinema 自己的 Python 环境。`rea-video remake-run` / `capsule-draft` 会自动找 `$CAPSULE_CINEMA_PYTHON` 或 `<capsule-root>/.venv/bin/python`，也可以用 `--python` 指定。

```bash
CC=$CAPSULE_CINEMA_ROOT   # capsule-cinema 仓库路径
rea-video remake-plan out/ref/breakdown.json --capsule-root $CC   # 照报告第二部分的方案出任务
rea-video remake-run out/ref/remake/jobs.json --dry-run      # 先给用户看任务和费用；--only G2 只跑一个单元
rea-video remake-run out/ref/remake/jobs.json                # 用户确认后再跑
rea-video assemble out/ref/breakdown.json out/ref/remake/results.json                   # 拼回原时间线 + compare.mp4
rea-video capsule-draft out/ref/breakdown.json --capsule-root $CC --capsule-name xxx [--write-capsule]
```

- jobs.json 里每个任务的 `executor` 取值：
  - `capsule_cinema`：调模型生成
  - `local_ffmpeg`：静态图本地重建
  - `keep_original`：保留原片，比如代码渲染、录屏、真实素材
- `user_assets`：这个镜头需要用户提供的真实素材。生成结果只是近似，要提醒用户。
- `capsule-draft`：通过 capsule-cinema 自带的 `tool_factory` 注入拆解结果，不改 capsule-cinema 代码，生成的配方草稿默认是 `review_required`。
