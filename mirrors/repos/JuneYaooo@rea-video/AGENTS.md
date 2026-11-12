# rea-video：给 Agent 的说明

- 第一次使用：运行 `bash scripts/install_skill.sh`（安装 CLI 并把 skill 链接到常见 agent 目录；需要 ffmpeg、Python ≥ 3.10），再 `rea-video --help` 确认。
- 用户要拆解视频、判断制作方式、标真实素材、拆音乐音效、复刻时，**先读 `skills/rea-video/SKILL.md`**，按里面的流程做，并复核低置信镜头。
- 仓库分工：
  - `skills/rea-video/`：给 agent 用的 skill（流程 + references），只写怎么用，不放开发文档
  - `rea_video/`：CLI 和拆解逻辑；模型能力地图在 `rea_video/capabilities/`，capsule-cinema 对接脚本在 `rea_video/integrations/`
  - `docs/`：给人看的文档；`docs/dev/` 是开发文档（扩充评测集、加拍法维度）
  - `eval/`、`tests/`：评测集和测试
- 开发约定：
  - 开发环境：`pip install -e ".[ocr,dev]"`（dev 带 pytest 和 jsonschema，测试和能力地图校验要用）
  - 规则改动后跑 `python3 -m pytest -q` 和 `rea-video eval eval/labels.yaml` / `eval/holdout*.yaml`，结果更新到 `eval/RESULTS.md`
  - 能力地图改完跑 `python3 scripts/validate_capabilities.py --matrix`
- 不要提交任何密钥；VLM 配置通过 `--env-file` 读取。
