# 安装与 VLM 配置

## 安装（一次性）

```bash
pip install "rea-video[ocr] @ git+https://github.com/JuneYaooo/rea-video"   # 需要 ffmpeg；Python ≥ 3.10
# 或在仓库里：bash scripts/install_skill.sh（装 CLI 并把 skill 链接到各 agent 目录）
rea-video --help
```

pip 报 `externally-managed-environment`（Homebrew / 新版 Ubuntu 的系统 Python）时，不要加 `--break-system-packages`，改用
`pipx install "rea-video[ocr] @ git+https://github.com/JuneYaooo/rea-video"`，或直接跑 `install_skill.sh`（会自动改用 pipx 或仓库内 `.venv`）。

手动装了 `[ocr]` 时，OCR 依赖会再装一套 `opencv-python`，和 rea-video 用的 `opencv-python-headless` 抢同一个 `cv2` 目录。装完跑一次：
`pip uninstall -y opencv-python && pip install --force-reinstall --no-deps "opencv-python-headless>=4.8,<5"`（`install_skill.sh` 会自动做）。

## VLM 配置（建议，不强制）

**VLM（建议配置，不强制）**：VLM 是能看图/看视频的多模态大模型（Gemini、GPT-4o、豆包、Qwen-VL 等）。不开 VLM，工具只靠像素统计、帧率、OCR、元数据判断，照样能跑完、出报告，但**实拍 / AI / 3D 的区分明显变弱**，音效清单也只有信号层的低置信候选。开了 VLM，工具会把每个镜头的短片段和关键帧发给它，再和确定性结果融合。

配置走 OpenAI 兼容接口，按以下顺序读取：

1. `REA_VLM_BASE_URL` / `REA_VLM_API_KEY` / `REA_VLM_MODEL`（`REA_VLM_MODEL` 可写多个模型、逗号分隔，前一个失败自动换下一个）
2. 如果没有，回落到 capsule-cinema 的 `VIDEO_ANALYSIS_*` 或 `GEMINI3_*`

用 `--env-file <某个 .env>` 读取配置（例如复用 capsule-cinema 的）。**不要把密钥写进对话、仓库或报告，也不要打开 .env 看内容。**

用户没配 VLM 时：照常不加 `--vlm` 跑，不要因此中止任务。

- **你自己能看图（多模态 agent）**：你就是这次的"VLM"，不需要建议用户另配。按 SKILL.md 第 1 节的「看图复核并入」做：`rea-video review` → 逐镜看图填答案 → `rea-video apply-review`，你的判断会并入工具结论和报告。结论里写"未开 VLM，由 agent 看图复核"。
- **你看不了图**：遵守 `review.md` 的「看不了图时的规则」，并在回复末尾用一句话建议配置 VLM（说明能提升实拍/AI/3D 的区分和音效识别）。
- 实测（2026-10-30，仓库 eval/RESULTS.md）：agent 看图复核并入比单开 Gemini VLM 更准；Gemini 容易把卡通 3D 风格的 AI 视频判成 3D 渲染、把画进画面的游戏界面判成录屏。所以能看图时**一定要做看图复核**，开了 VLM 也要做，并且独立判断，不要照抄 VLM。
- 外部 VLM 仍有你替代不了的部分：它能直接看视频片段的运动、听音轨。你只能看静帧、听不了声音时，音效和人声来源照样标"待确认"。

**VLM 是否真的生效，以 `rea-video summary` 的 `VLM:` 一行为准**（也在 `breakdown.json` 的 `analysis.vlm.status`）：`ok` 已生效、`partial` 部分镜头有结果、`failed` 请求了但全部调用失败（例如服务端 503）、`not_configured` 请求了但没找到配置、`off` 没请求。`failed` / `not_configured` 等同没开 VLM，报告里要如实写，不能写"已开 VLM"。
