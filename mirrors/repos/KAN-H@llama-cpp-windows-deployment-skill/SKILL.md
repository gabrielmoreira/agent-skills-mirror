---
name: llama-cpp-windows-deployment
description: 'llama.cpp Windows 平台多模型部署与优化。涵盖：Router Mode 多模型管理、Gemma 4/Qwen/Phi-4 模型部署、QAT–MTP 推理优化、RTX 5060 Ti 16GB 显存调优、CPU 内存受限场景适配、预编译包快速部署、Preset 差异化配置、WSL2 通路配置、Agent/API 接入、Tool Calling 工具调用测试、纯 CPU 工具调用脚本、BAT 脚本编码修复。Use when: 部署 llama.cpp 服务、配置多模型路由、优化推理性能、排查显存/内存溢出、配置 MTP 投机解码、迁移 Qwen/Gemma 模型、测试模型工具调用、搭建纯 CPU 推理、修复 .bat 闪退/乱码。English: deploying llama.cpp on Windows, configuring Router Mode, optimizing GPU/CPU inference, troubleshooting OOM, setting up MTP speculative decoding, migrating between Gemma 4 and Qwen models, testing tool calling, running CPU-only inference, fixing .bat encoding crashes.'
argument-hint: '描述你的部署场景：硬件配置、目标模型、显存大小、是否使用 Router Mode / MTP'
user-invocable: true
---

# llama.cpp Windows 多模型部署与优化集成技能

> **版本**: v3.2 | **基准硬件**: RTX 5060 Ti 16GB + Intel U7 270K / CPU-only (48GB DDR5) | **平台**: Windows 10/11 + WSL2 | **llama.cpp 版本**: b10056 – b10158+ | **更新**: 2026-08-16（新增 `--fit` 自动显存分层实测、CPU 工具调用新模型、参数知识库与启动脚本自动同步方法论、Router Mode 参考脚本）

## 一、When to Use（触发词）

| 场景 | 触发词 |
|------|--------|
| 多模型路由部署 | "Router Mode", "多模型管理", "单端口多模型" |
| Gemma 4 部署 | "Gemma-4", "QAT", "12B", "26B-A4B", "mmproj" |
| Qwen 系列迁移 | "Qwen3", "Qwen3.6", "30B-A3B", "35B-A3B-MTP" |
| Phi-4 CPU 推理 | "Phi-4-mini", "CPU推理", "9GB内存", "纯CPU" |
| MTP 投机解码 | "MTP", "draft-mtp", "spec-draft", "投机解码", "draft acceptance" |
| 显存优化 | "16GB显存", "显存溢出", "OOM", "KV Cache量化" |
| 环境搭建 | "预编译包", "Blackwell", "sm_120", "首次部署" |
| WSL2 连接 | "WSL2", "宿主机访问", "NAT" |
| Agent 对接 | "Hermes", "Claude Code", "Codex CLI", "LangChain" |
| 工具调用 | "工具调用", "tool calling", "function calling", "--tools all", "--jinja" |
| 纯 CPU 推理 | "CPU工具调用", "纯CPU", "CPU-only", "不占GPU", "128K" |
| BAT 脚本 | "脚本闪退", "乱码", "GBK", "UTF-8", "编码" |

## 二、Prerequisites（前置条件）

### 2.1 硬件要求
| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| GPU | RTX 5060 Ti 8GB | RTX 5060 Ti 16GB |
| 驱动 | NVIDIA ≥ 610.47 | ≥ 610.62 |
| 内存 | 9GB（CPU-only） | 32GB+ |
| CPU | 8 核 | Intel U7 270K（20核） |
| OS | Windows 10 64-bit | Windows 11 24H2 |

### 2.2 软件要求
- `llama.cpp` 预编译包（`llama-b10056+-bin-win-cuda-13.3-x64.zip`，Blackwell sm_120 原生支持）
- 模型文件：GGUF 格式（标准 / QAT-UD / MTP）
- NVIDIA 驱动正常，`nvidia-smi` 可运行（GPU 场景）
- PowerShell + CMD（BAT 脚本兼容）

### 2.3 目录规范
```
C:\models\
├─ chat\                          # Router Mode 扫描的对话模型目录
│  ├─ gemma-4-12b-it-Q5_K_M\     # 无 preset.json → 继承全局参数
│  │  └── model.gguf
│  ├─ gemma-4-12B-it-qat-UD-Q4_K_XL\
│  │  ├── model.gguf
│  │  └── mmproj-F16.gguf        # 多模态投影文件
│  ├─ Qwen3.5-2B-Q4_K_M\
│  │  ├── model.gguf
│  │  └── preset.json            # ctx_size: 32768
│  └── Qwen3.6-35B-A3B-MTP-GGUF\
│     ├── model.gguf
│     └── preset.json
├─ embedding\                     # Embedding 模型独立目录
└─ gemma4_mtp\                    # MTP Draft 模型集中存放
   ├── mtp-gemma-4-12b-it-Q8_0.gguf
   └── mtp-gemma-4-26B-A4B-it-Q8_0.gguf
```

## 三、Core Concepts（核心概念）

| 概念 | 说明 |
|------|------|
| **Router Mode** | 单端口多模型动态加载，请求时指定 `model` 参数自动加载对应 GGUF |
| **Preset (preset.json)** | 模型目录下的独立配置，覆盖 Router 全局参数。**优先级：preset.json > 启动脚本全局参数** |
| **MTP (Multi-Token Prediction)** | 投机解码技术，每步预测多个 token。Gemma 4 用外挂 draft 模型；Qwen3.6 用内置 MTP heads |
| **QAT (Quantization-Aware Training)** | 训练时感知量化的模型，对 KV Cache 精度敏感，推荐 `q8_0/q8_0` |
| **UD (Uniform Decomposition)** | 均匀分解量化，在 XL 级别保留更高比特给敏感层 |
| **KV Cache** | 上下文 Key-Value 缓存，是显存/内存占用的主要变量。公式：`≈ 2 × ctx × layers × hidden_dim × precision_bytes` |
| **Blackwell (sm_120)** | RTX 50 系架构，需 CUDA 13.3+ 驱动 ≥ 610.47 |
| **子命令架构** | 新版 llama.cpp 用 `llama <子命令>` 结构，`llama-server` / `llama-cli` / `llama-embed` |
| **Tool Calling 双层机制** | ①客户端 tools API（VS Code/Hermes 用，需 `--jinja`）②服务端内置 agent 工具 `--tools all`（Web UI 用）。**内置功能，无需安装** |
| **Qwen3.6-27B 架构** | 64 层混合架构：48 层 Gated DeltaNet（线性注意力，KV 极小）+ 16 层 Gated Attention。权重是显存大头，KV 占比很小 |
| **BAT 编码** | 中文 Windows cmd 按 GBK(936) 解码 .bat。UTF-8 中文会乱码→语法错误→闪退；`chcp 65001` 与 BOM 均无法修复解析问题 |

## 四、Deployment Workflow（部署工作流）

### Step 1：环境校验与版本指纹

**每次换 build 或换模型族前必做**，防止参数 silent fail：

```powershell
# PowerShell（llama.cpp 目录下）
.\llama-server.exe --help | Select-String "spec-draft-n-max"
.\llama-server.exe --help | Select-String "spec-type"
.\llama-server.exe --help | Select-String "draft-"
```

| 指纹特征 | 含义 | 后续操作 |
|---------|------|---------|
| `--spec-draft-n-max` + `draft-mtp` 存在 | b10056 标准版，用 `--spec-*` 命名 | 按本技能 MTP 参数 |
| `--draft-model` / `--draft-mtp-n` 出现 | build 已迁移到 `--draft-*` 命名 | 切换 MTP 参数命名 |
| `--spec-draft-buffer` 不存在 | b10056 已摘除，正常 | 不要写此参数 |
| 模型名含 `MTP` 后缀 | 内置 MTP heads（Qwen3.6 系） | **不需要** `--model-draft` |

### Step 2：选择部署模式

#### 模式 A：Router Mode（多模型热切换）⭐ 推荐

```bat
@echo off
chcp 65001 >nul
title llama.cpp Router - RTX 5060 Ti
cd /d C:\llama.cpp

llama-server.exe ^
  --models-dir C:\models\chat ^
  --host 0.0.0.0 ^
  --port 8080 ^
  -fa on ^
  -c 8192 ^           :: 全局默认，保护 12B+ 模型
  -np 1 ^
  -t 16 ^
  --cache-type-k q8_0 ^
  --cache-type-v q8_0 ^
  --metrics ^
  --timeout 600

pause
```

**关键规则**：
- 不要在 Router 全局参数中设置 `-ngl` / `-t` 等硬件参数→在单个模型 `preset.json` 中定义
- 小模型（≤3B）通过 `preset.json` 覆盖 `ctx_size` 释放长文本潜力
- 大模型（≥12B）不设 `preset.json`→自动继承全局 `-c 8192` 保显存

#### Preset 模板（放入模型目录）

**小模型（0.8B–3B）长文本配置**：`C:\models\chat\<model-dir>\preset.json`
```json
{
    "ctx_size": 32768,
    "n_gpu_layers": 99,
    "n_threads": 16,
    "flash_attn": true
}
```

**大模型（≥12B）无需创建 preset.json**，继承全局参数。

> 📎 **Router Mode 参考脚本**：[`./references/router-mode-preset.bat`](./references/router-mode-preset.bat)（`--models-preset` 版，最贴合 preset 优先级设计）、[`./references/router-mode-simple.bat`](./references/router-mode-simple.bat)（`--models-dir` 简单版）。两者均为 ASCII 通用模板，改顶部 `LLAMA_DIR`/`MODELS_DIR`/`PORT` 即可。

#### 模式 B：单模型实例（专用端口）

适用于需要独占 GPU 资源的高负载场景，每个模型开独立端口。

### Step 3：模型族专项配置

#### 3A：Gemma 4 系列（含 QAT + MTP）

**硬件匹配矩阵（RTX 5060 Ti 16GB）**

| 模型 | GGUF 类型 | 权重 VRAM | 推荐 ctx | MTP 可行性 | 备注 |
|------|----------|----------|---------|-----------|------|
| 12B Q5_K_M | 标准 | ~8.5 GB | 64K ✅ | 32K ✅ | 日常首选 |
| 12B UD-Q8_K_XL | UD imatrix | ~13 GB | 64K ✅ | ❌ 16GB 扛不住 | 高质量基线 |
| 12B qat-UD-Q4_K_XL | QAT+UD | ~6.7 GB | 128K ✅ | ❌ arch 不对齐 | 多模态 + mmproj |
| 26B-A4B qat-UD-Q4_K_XL | MoE A4B | ~10.5 GB | 128K ✅（官方甜点，SWA 小 KV） | 需专用 A4B draft（官方 Q8_0） | 16GB 下优先 `--fit on` |

**核心参数（所有 Gemma 4 共用）**：
```bat
-ngl 99 -fa on -np 1 -t 10 --batch-size 1024
--cache-type-k q8_0 --cache-type-v q8_0  :: QAT 对 KV 精度敏感，不要降 q4
--no-mmap --host 0.0.0.0
```

**MTP 专有参数（Gemma 4 外挂 draft）**：
```bat
--model-draft <path_to_mtp_draft.gguf>
--spec-type draft-mtp
--spec-draft-n-max 2-3    :: 5060Ti 保守给 2-3，Unsloth 官方给 4
--gpu-layers-draft 60     :: Q5 主模型时给 60，Q8 时给 50
```

> ⚠️ **QAT-UD 与 MTP 不推荐同开**：QAT-UD 是多模态主（带 mmproj），MTP draft 是纯文本 arch，b10056 会因 arch 不对齐 silent skip。QAT-UD 走裸跑 + `--mmproj`。
> 参考脚本 `gemma4-menu-scripts.bat` 菜单 7/9 保留 QAT+MTP 组合仅作实验入口（菜单已标注 `[!] QAT+MTP 不推荐`），正常使用请选 QAT 裸跑项（5/6）或非 QAT 的 MTP 项（1/2）。

**26B-A4B MoE 特殊处理（2026-08-16 更新）**：
- ⭐ **优先用 `--fit on --fit-ctx <ctx>` 让 llama.cpp 自动分层**（本 build fit 默认 on，但 `-ngl` 被显式设置时会 abort）。实测：16GB 下 51K 上下文从硬编码 ngl 的 10.6 t/s 提升到 72-93 t/s（~7 倍），根因是显存临界导致 CUDA graph 回退（详见 `references/20260816-session-experience.md`）
- 手工 `-ngld`（40-50）作为 fit 不可用时的后备方案
- MTP draft 必须用 **A4B 专用** GGUF（不可复用 12B draft），且只认官方 Q8_0（第三方 Q4_0 在 server 加载路径必崩）
- Context：**128K 是官方甜点**（ctx_train=262144、MRCR 128K=44.1%）；SWA 使 KV 随 ctx 增长极小（128K 仅 ~1.0GB）

#### 3B：Qwen 系列迁移

**三档路线速查**：

| 模型 | MTP 方式 | 参数形态 |
|------|---------|---------|
| Qwen3-30B-A3B | 无（可外挂小 draft） | `--spec-type draft` + `--model-draft` |
| Qwen3.6-35B-A3B-MTP | 内置 heads | `--spec-type draft-mtp`，**无** `--model-draft` |
| Qwen3.5-2B/0.8B | 无 | 裸跑，通过 preset.json 扩 ctx |

> ⚠️ 拿 30B-A3B 硬开 `draft-mtp` 会报 `model does not support MTP`；拿 35B-A3B-MTP 还写 `--model-draft` 会多占显存。

**采样参数（区别于 Gemma 4 的默认值）**：
```bat
--temp 0.7 --top-p 0.8 --top-k 20 --repeat-penalty 1.05
--chat-template-kwargs "{\"enable_thinking\":false}"
```

**Qwen3.6-35B-A3B-MTP 脚本要点**：
- **删除** `--model-draft`、`--gpu-layers-draft`
- `--spec-draft-n-max 3`（5060Ti 16GB 推荐，可试 4）
- context 上限 32K（拉 64K 需降 KV 到 q4_0）

#### 3C：Phi-4-mini CPU 推理（9GB 内存受限场景）

```bat
@echo off
chcp 65001 >nul
title Phi-4-mini (CPU - 9GB Safe Mode)
cd /d C:\llama.cpp

set "MODEL_DIR=C:\models\chat\Phi-4-mini-instruct-Q4_K_M"
set "CTX_SIZE=32768"       :: 从 32K 起测，稳定后试 48K/64K
set "BATCH_SIZE=256"
set "THREADS=16"

llama-server.exe ^
  --model "%MODEL_DIR%\Phi-4-mini-instruct-Q4_K_M.gguf" ^
  --ctx-size %CTX_SIZE% ^
  --batch-size %BATCH_SIZE% ^
  --threads %THREADS% ^
  --cache-type-k q4_0 ^     :: CPU 场景降 KV 精度保内存
  --host 0.0.0.0 ^
  --port 8083 ^
  --cors-origins localhost ^
  --no-mmap ^
  --no-metrics

pause
```

**CPU 优化黄金法则**：
- KV Cache 必须量化（`q4_0` 或 `q2_k`），否则 64K = 12.8GB 超 9GB 内存
- `--batch-size 256`，降低瞬时内存峰值
- 支持 `--no-metrics` 节省少量内存
- 不支持参数：`--memory-limit`、`--max-batch-size`、`--numa`

> ⚠️ **BAT 注释提示**：行末 `::` 注释在 `if() (...)` 括号块内可能导致解析错误，如需在括号块内注释请改用 `REM` 语句。

> 📎 **完整脚本参考**：[`./references/gemma4-menu-scripts.bat`](./references/gemma4-menu-scripts.bat)（Gemma 4 10 选项菜单）、[`./references/qwen-scripts.bat`](./references/qwen-scripts.bat)（Qwen 三档部署脚本）、[`./references/preset-templates.json`](./references/preset-templates.json)（各场景 Preset 模板集合）、[`./references/20260803-session-experience.md`](./references/20260803-session-experience.md)（全量实测数据与经验沉淀）

#### 3D：Qwen3.6-27B 稠密模型专项（64K + 高 ngl 提速）⭐ 2026-08-03 实测

**架构关键**：Qwen3.6-27B 实际是 **64 层**（48 层 Gated DeltaNet 线性注意力 + 16 层 Gated Attention）。KV 缓存极小（64K q8_0 仅 ~0.5GB），**权重才是显存大头**。

**核心结论**：128K 配置在 16GB 显存下**必 OOM**；改 **64K + 更高 ngl** 反而更快：

| 模型 | 旧配置 | 新配置 | 实测 tg | MTP 接受率 |
|------|--------|--------|---------|-----------|
| HauhauCS IQ4XS（裸跑） | ngl40/128K | **ngl52/64K** | **14.3 t/s** (+37%) | - |
| MTP Q4_K_S | ngl40/128K | **ngl48/64K** + MTP | **15.5 t/s** (+24%) | 98.5% |
| MTP IQ4XS | ngl40/128K | **ngl48/64K** + MTP | **16.9 t/s** (+25%) | 94.6% |
| UD-Q4_K_XL（裸跑） | ngl40/128K | **ngl48/64K** | 10.9 t/s | - |

**要点**：
- ngl40 时 24 层在 CPU → 提升到 ngl48-52 后仅 12 层在 CPU，速度显著提升
- 统一参数：`-c 65536 --cache-type-k/v q8_0 -t 12 --batch-size 256`
- 27B MTP 实测健康度：`draft acceptance = 0.921` / `graphs reused = 15` / `mean len = 2.59` ✅
- 对比：**Gemma 4 26B-A4B 是 MoE**（128 专家/8 活跃/4B active），解码每 token 只算 4B → 天然快 3-4 倍（55+ t/s），无需此优化

#### 3E：纯 CPU 工具调用脚本（12B 以下，不占 GPU）

菜单式一键脚本 `start-CPU-Toolcall-Launcher.bat`（端口 8086，脚本顶部 `PORT` 变量可改；[参考脚本](./references/start-CPU-Toolcall-Launcher.bat)），全部 `-ngl 0`、128K 上下文：

| 模型 | KV | 实测 tg | 内存 | 工具调用 |
|------|----|---------|------|---------|
| Qwen3.5-2B (+mmproj) | q4_0 | **57.1 t/s** | ~4GB | ✅ |
| Phi-4-mini | q4_0 | 38.3 t/s | 7.4GB | ❌ 不支持 |
| gemma-4-E4B (+mmproj) | q8_0 | 29.8 t/s | ~6GB | ✅ |
| gemma-4-12B-QAT (+mmproj) | q8_0 | 13.0 t/s | ~6GB | ✅ |
| Qwen3.5-4B-UD (+mmproj) | q8_0 | 13.46 t/s | ~7GB | ✅ |
| QwenPaw-Flash-9B-heretic-MTP | q8_0 | 27.3 t/s（CPU 上 MTP +74%） | ~2GB KV | ✅ |
| QwenPaw-Flash-9B | q8_0 | 15.7 t/s | ~2GB KV | ✅ |
| LFM2.5-8B-A1B-UD (MoE) | q8_0 | 44.1 t/s（同档最快） | ~0.8GB KV | ✅ |

**CPU 参数要点**：
- `-ngl 0` 强制不占 GPU（可用 `nvidia-smi` 验证无 llama 进程）
- `--cache-type-k/v q4_0`（fast 档）或 `q8_0`（quality 档）
- `-t <物理核数>`、`--batch-size 256` 降低内存峰值
- 菜单标题直接标注实测速度（`[57 t/s]`）与能力（`[!] NO tool calls`），便于用户选型

**新增模型已知问题（2026-08-16）**：
- ⚠️ **LFM2.5 工具调用**：llama.cpp issue #26658——工具参数含引号/转义可能解析失败（规避：要求双引号无转义）
- ⚠️ **llama-cli 单次测试必须加 `-st`（--single-turn）**：`-no-cnv` 在 b10158 仍进交互模式等 stdin，用管道/`Select-Object` 时看似卡死（实为等输入），勿误判为 hang
- ✅ **MTP 在 CPU 上实测生效**：QwenPaw-heretic-MTP 27.3 vs 非 MTP 15.7 t/s（+74%），`draft acceptance = 0.725`；内置 MTP head 模型**不要**传 `--model-draft`
- 完整实测见 [`./references/20260816-session-experience.md`](./references/20260816-session-experience.md)

### Step 4：安全配置（WSL2 + Agent 对接）

```bat
set "API_KEY=sk-local-001"
set "CORS_ORIGINS=http://localhost:* https://localhost:*"
```

| `--host` 值 | WSL2 连通性 | 说明 |
|-------------|------------|------|
| `127.0.0.1` | ❌ 不通 | WSL2 NAT 下 localhost 隔离 |
| `0.0.0.0` + `--api-key` | ✅ 通 | WSL2 用宿主机 vEthernet IP 访问 |
| `.wslconfig` 开 `networkingMode=mirrored` | ✅ 通 | Win11 22H2+ 方案 |

**Agent 接入示例**：
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    base_url="http://<宿主机IP>:8080/v1",
    api_key="sk-local-001",
    model="Qwen3.5-2B-Q4_K_M",
)
```

### Step 5：Tool Calling 工具调用（内置，无需安装）⭐ 2026-08-03 实测

**llama.cpp 工具调用是内置功能，无需安装任何额外 tools**。存在两套完全独立的机制：

| | **客户端 tools API**（VS Code / Hermes 用） | **服务端内置工具 `--tools all`**（Web UI 用） |
|---|---|---|
| 谁定义工具 | 客户端在请求体 `tools` 数组定义 | 服务端内置 read_file/grep_search/exec_shell_command/write_file/edit_file/get_datetime |
| 谁执行工具 | 客户端执行后回传 tool 消息 | 服务端 `/tools` REST 端点执行 |
| 前置条件 | 服务端 `--jinja` + 模型支持 | 启动参数 `--tools all`（需配合 `--jinja`） |
| 依赖关系 | **不依赖** `--tools all` | 独立 |

**关键结论（实测验证）**：
- 通过 **OpenAI API 连 VS Code 或 WSL2 Hermes：不需要 `--tools all`**，工具由客户端自己驱动，无需额外参数
- `--tools all` 仅给 Web UI / 服务端 agent 场景使用
- 脚本配置方式：
```bat
set "AGENT_TOOLS=off"   :: off=关闭(默认) | all=启用全部内置工具
if "%AGENT_TOOLS%"=="all" ( set "TOOLS_ARG=--tools all" ) else ( set "TOOLS_ARG=" )
```

**工具调用测试方案（11/11 模型全部 PASS，b10158）**：
- Phase 1 能力探测：发带 `tools` 的请求，确认模型返回 tool_call
- Phase 2 两轮工具循环：调用 → 客户端执行 → 回传结果 → 模型基于结果继续作答
- 测试工具示例：`get_current_weather {"location":"Beijing"}` → 26°C 晴朗 ✅
- ⚠️ **Phi-4-mini 不支持工具调用**（实测确认）

### Step 6：启动脚本工程化经验（2026-08-03/04 实战沉淀）

- **备份先行**：任何脚本修改前先复制到 `backup\`（如 `start-Gemma4-Launcher-WSL.bat.bak-20260803`），确认字节数一致再改动，可随时回滚
- **按模型族拆分脚本**：Gemma 专用 / Qwen 专用 / CPU 工具调用专用，端口独立（默认 8080 / 8083 / 8086，脚本顶部 `PORT` 变量可改，与现有服务冲突时调整）
- **菜单标注**：实测速度标注到标题后（`[57 t/s]`）、破限模型特殊标注、不同 B 参数量化版写清（如 12B-Q5_K_M）
- **编码选择**：见 Troubleshooting「脚本闪退」——新脚本推荐 UTF-8 + 全英文；既有 GBK 脚本保留并在编辑器中手动选 GBK

#### 6A：模型清单自动同步器 `update-launchers`（2026-08-16 新增）

- **位置**：`D:\dev\projects\llama.cpp\` 下 `update-launchers.bat`（纯 ASCII 入口）+ `update_launchers.py`（Python 3.11 纯标准库，用现成 `.venv\Scripts\python.exe`）+ `launcher-models.json`（注册表，UTF-8）
- **作用**：扫描 `D:\dev\models\chat`，自动同步 4 个工件——`start-CPU-Toolcall-Launcher.bat` / `start-Gemma4-Launcher.bat` / `start-Qwen-Launcher.bat` / `models-config.ini`（Router preset）
  - 模型目录被删 → 自动移除对应变量/菜单/启动块并重编号菜单；ini 僵尸段同步清除
  - 新模型目录出现 → 按家族自动生成默认参数条目（菜单标 [NEW]）：gemma→Gemma4 启动器（自动配对 gemma4_mtp draft 生成 +MTP 条目）/ qwen→Qwen / lfm→CPU / 其他→Qwen
  - 每次写入前自动备份 `backup\<名>.bak-YYYYMMDD-HHMMSS`
- **用法**：双击（报告+确认）| `--check` 干跑（预览写 `backup\preview\`）| `--yes` 全自动 | `--extract` 从 3 脚本重建注册表 | `--no-scan` 按注册表原样渲染（回归）
- **要点**：手工调参改注册表 JSON 而非直接改 3 个启动脚本（会被覆盖）；生成器严格按各脚本编码写出（Gemma4/Qwen=GBK 无 BOM、CPU/ini=ASCII、CRLF）；ini 相比旧 generate_ini.bat 修复了「文件名含 mtp 即被排除」的 bug（内置 MTP heads 模型现在也能进 Router）

#### 6B：参数知识库 + 26B 长会话降速实测修复（2026-08-16）

**参数知识库（三源治理）**：
- `model-profiles.json`：官方/实测参数卡片（Gemma4 全系含 QAT、Qwen3.6/3.5、GLM、Devstral、LFM、Phi 等，含采样/ctx/KV/MTP 规则/来源 URL/verified 级别）。官方 Gemma4：temp 1.0/top-p 0.95/top-k 64、256K ctx、QAT 唯一官方量化 UD-Q4_K_XL、MTP n-max 2 起步+2GB 内存；Qwen3.6 精确编码 temp 0.6/通用 1.0
> 📎 **知识库参考**：[`./references/model-profiles.json`](./references/model-profiles.json)（脱敏通用版）。⚠️ 其中 `verified: official` 的来源 URL 是在采集时从厂商文档记录，本技能未逐一复核，使用前请自行核实可达性。
- 新模型自动条目三源合并：家族模板 → 知识库匹配覆盖 → 用户注册表最终覆盖；报告标注 profile 来源
- `update-launchers.bat --audit`：GGUF 头解析（arch/层数/SWA/KV 维度）+ KV 内存估算 + 采样对比 + 16GB 显存红绿灯，只读

**26B-A4B QAT 长会话降速根因（实测，2026-08-16）**：
- 真相：Gemma 4 是 SWA 混合注意力（30 层中 28 层滑动窗口 1024）→ **KV 极小（64K 仅 ~0.4GB），KV 膨胀论不成立**；瓶颈是 14.25GB 权重 + draft + mmproj 使 16GB 极度临界
- 实测基准（51K 上下文 tg t/s）：旧基线（ngl 硬编码+draft 层 24）**10.6**；draft 全 CPU **26.9**；`--fit on --fit-ctx 65536`（权重留 ~2.4GB 在 host）+ draft 层 8 **72-93**（~7 倍）
- 关键证据：S1 日志 `offloaded 31/31 layers to GPU`（13,573 MiB）+ KV 839MiB + draft 425MiB + mmproj ≈ 超过 16GB → CUDA graph 回退 → 解码阶梯下降；`--fit` 自动分层后恢复
- 修复已写入启动脚本：菜单 6/8/17 与新增菜单 9「纯文本 Agent」：移除硬编码 -ngl（fit 自动分层；本 build fit 默认 on 但 ngl 被用户设置时会 abort）+ `--fit-ctx 65536` + `--gpu-layers-draft 8` + `--keep 8192` + `--metrics`；agent 变体块内预算 2048
- **带 mmproj 时 ctx_shift 被自动禁用（源码）**；纯文本 + `--context-shift` 仅对 **n_predict=-1 无限生成**生效（b10158 实测：有限 n_predict 仍在 64K 截断）。纯文本项核心收益是**前缀缓存复用**（实测第二轮 prompt_n=7，不再全量重算历史）
- **128K 上探可行**：26B-A4B ctx_train=262144；SWA 使 KV 随 ctx 增长极小（128K 仅 ~1.0GB）；128K 是官方甜点（MRCR 128K 八针 26B=44.1%，256K 质量衰减）。实测 100K 上下文 pp=1480/tg=45.5 无 OOM 无截断。已新增菜单 9「26B-QAT + MTP 128K 多模态」并将纯文本 Agent 项升 128K（`-c 131072 --fit-ctx 131072 --timeout 300`）；26B 破限版菜单 14/15 已 fit 化（删硬 ngl + gld 8 + metrics，实测 tg=70）

| 参数 | 推荐值 | 适用场景 | 理由 |
|------|--------|---------|------|
| `-ngl` | 99 | GPU 全卸载 | 16GB 显存全量利用 |
| `-fa` | on | 所有模型 | FlashAttention 降显存 |
| `-np` | 1 | 单卡单用户 | 防多批次显存叠加 |
| `-t` | 10-16 | 全场景 | 物理核数，防 Windows oversubscribe |
| `--batch-size` | 1024 (GPU) / 256 (CPU) | 分场景 | GPU 用大 batch 提吞吐，CPU 用小 batch 保内存 |
| `--cache-type-k/v` | q8_0 (GPU) / q4_0 (CPU) | 分场景 | QAT 模型必须 q8_0；CPU 场景可降 |
| `--no-mmap` | 置尾 | Windows | 大 GGUF 长时运行防偶发卡顿 |
| `--host 0.0.0.0` | 必设 | 服务部署 | WSL2 + 局域网访问 |

## 六、MTP Health Diagnostics（健康诊断）

服务启动后，从 `slot print_timing` 日志提取三维度：

| 指标 | 健康阈值 | 处置 |
|------|---------|------|
| `draft acceptance` (A) | > 0.5 ✅ | 0.3-0.5 ⚠️ 检查 draft 对齐；< 0.3 ❌ 换 draft |
| `mean len` (L) | 接近 `spec-draft-n-max` | 显著低于 n-max → 可试提 n-max |
| `graphs reused` (R) | > 0 ✅ | = 0 → draft 被跳过，查 arch/显存 |

**实测参考**（Q5 + Q8 draft）：`A=0.549 / L=2.10 / n-max=2 / R=283` → ✅ 全线绿。

> 🔧 **自动化诊断**：运行 [`./scripts/detect.ps1`](./scripts/detect.ps1)（Windows 原生 PowerShell）或 [`./scripts/detect.py`](./scripts/detect.py)（跨平台 Python，Windows/Linux/macOS 通用，Python 3.7+）一键检测 CUDA 架构、MTP 指纹、驱动版本、模型文件和显存状态。两者功能一致，改动时需同步。

<details>
<summary>🔀 跨模型族迁移检查清单（点击展开）</summary>

| 检查项 | Gemma 4 (外挂 draft) | Qwen3-30B-A3B (无 MTP) | Qwen3.6-35B-A3B-MTP (内置 heads) |
|--------|---------------------|------------------------|----------------------------------|
| `--model-draft` | ✅ 必写 | 外挂时才写 | ❌ 删除 |
| `--gpu-layers-draft` | ✅ 写（控显存） | 外挂时才写 | ❌ 删除 |
| `--spec-type` | `draft-mtp` | `draft` | `draft-mtp` |
| 采样参数 | temp=0.7 / top_p=0.9 | temp=0.7 / top_p=0.8 / top_k=20 | temp=0.7 / top_p=0.8 / top_k=20 |
| `--chat-template-kwargs` | 不需要 | `{"enable_thinking":false}` | `{"enable_thinking":false}` |
| KV Cache | q8_0/q8_0（QAT 敏感） | q8_0/q8_0 | q8_0/q8_0（拉 64K 可降 q4_0） |
| ctx 上限 (16GB) | 12B=64K / 26B-A4B=32K | 48K–64K | 32K |
| MTP 诊断解读 | 读外挂 draft 的 A/L/R | 读外挂 draft 的 A/L/R | 读内置 heads 产出（R 含义不同） |

</details>

## 七、Troubleshooting（常见故障排查）

| 现象 | 根因 | 解决方案 |
|------|------|----------|
| 脚本闪退无输出 | 不支持参数 / 中文注释 | 移除非支持参数，删除中文符号 |
| `invalid argument: --verbose-prefill` | b10066 不支持 | 删除参数，升级 b10070+ 后可加回 |
| `CORS is set to allow all origins ('*')` | 未设 `--api-key` | 添加 `--api-key <自定义值>` |
| WSL2 无法连接 | `--host 127.0.0.1` | 改为 `--host 0.0.0.0` |
| 小模型 ctx 被限制在 8K | 全局 `-c` 一刀切 | 在小模型目录创建 `preset.json` 覆盖 |
| `unknown command '-m'` | 新版子命令架构 | 改用 `llama-cli -m` 或 `llama-server --model` |
| `sm_89` 而非 `sm_120` | 下载了 CUDA 12.4 版 | 下载 CUDA 13.3 版预编译包 |
| MoE 模型 `draft-mtp` 报错 | 模型未训练 MTP heads | 确认模型是否支持（30B-A3B 不支持）|
| 26B 加载 OOM / 长会话阶梯降速 | 显存临界致 CUDA graph 回退（非 KV 膨胀，见 20260816 经验） | **优先 `--fit on --fit-ctx <ctx>` 自动分层**；手工 `-ngld` 40-50 仅作后备 |
| 26B MTP `acceptance` 极低 | 用了 12B 的 draft | 换 A4B 专用 MTP GGUF |
| 26B MTP 加载报 `invalid vector subscript` | 用了第三方 Q4_0 draft。官方 MTP 只有 Q8_0/BF16/F16，**从未有 Q4_0**；第三方 Q4_0 在 llama-server 的 draft 加载路径解析崩溃（**llama-cli 单独加载正常**，易误判为文件没问题） | 用官方 Q8_0 draft（`mtp-gemma-4-26B-A4B-it-Q8_0.gguf`），或以官方 Q8_0 用 `llama-quantize` 自量化 Q4_0 |
| Phi-4 64K OOM | KV Cache 超 9GB | 降 KV 到 q4_0，从 32K 逐步测试 |
| 脚本双击闪退（中文乱码） | UTF-8 中文被 cmd 按 GBK 解码，残留 ASCII 特殊字符被误解释（如 `ll=启用(默认) | off=关闭` 被拆成命令） | 方案 A：转 GBK 编码 + 删 `chcp 65001` + 去 emoji；方案 B（推荐新脚本）：UTF-8 + 全英文界面 |
| `chcp 65001` / UTF-8 BOM 无法修复闪退 | 只影响控制台显示，cmd 解析文件内容时不用它 | 不要依赖，直接改文件编码 |
| `nvidia-smi ... --format=csv,noheader` 报 noheader 不被识别 | cmd 中**逗号是参数分隔符**，`--format=csv,noheader` 被拆成 3 个参数（PowerShell 调用则无此问题） | bat 中加引号：`--format="csv,noheader,nounits"` |
| GBK 文件在 VS Code 显示乱码 | VS Code 默认按 UTF-8 打开 | 编辑器右下角手动选 GBK；或改用方案 B 全英文 UTF-8 |
| BAT `for` 循环内用 `goto` 导致只处理首文件/死循环 | `goto` 跳出会终止 `for` 循环（generate_ini.bat 踩坑） | 循环内改用 `call :子程序` 并 `exit /b` 返回循环体 |
| 含中文 GBK 脚本被外部工具转 UTF-8 损坏（U+FFFD） | 编辑器/工具按 UTF-8 重存 | 用 skeleton+LCS 合并法从 backup 恢复中文（见 `references/20260816-session-experience.md` 六节） |
| 128K 上下文加载崩溃 | 16GB 显存下权重 + 128K KV 超限 | 降 64K + 提 ngl（27B 实测反而更快） |
| 模型不支持工具调用 | 模型能力限制（如 Phi-4-mini） | 换支持模型；菜单标注 `[!] NO tool calls` |

**参考脚本编码现状说明（2026-08-05 修订）**：`references/gemma4-menu-scripts.bat`、`qwen-scripts.bat`、`start-CPU-Toolcall-Launcher.bat` 已统一为 **UTF-8 + 全英文（纯 ASCII）+ 无 chcp**，任意 Windows cmd 可直接运行无乱码（方案 B）。实测教训：UTF-8 中文注释 + `chcp 65001` 的混合脚本在中文 Windows cmd 下会被 GBK 误解析导致命令错乱（如 `llama-server.exe` 被截断成 `erver.exe` 报错），因此参考脚本不再使用中文。用户自建脚本若需中文界面，请用方案 A（GBK 编码 + 删 chcp + 去 emoji）。

## 八、Version Upgrade Notes（版本升级说明）

| 目标版本 | 恢复/调整的参数 | 说明 |
|---------|---------------|------|
| b10070+ | `--verbose-prefill` | 验证 MTP Prefill 生效 |
| b10070+ | `--defrag-thresh 0.1` | 优化长对话 KV Cache 碎片 |
| 迁移到 `--draft-*` 命名 | 见下方「spec→draft 映射表」 | 参考脚本默认按 b10056 `--spec-*` 编写；新版 build 检测到 `--draft-*` 后按映射表切换 |
| b10158+ | `--jinja` / `--tools all` | 工具调用内置功能；`--tools all` 需配合 `--jinja` |

#### spec→draft 参数映射表（build 迁移到 `--draft-*` 命名时）

| 当前（b10056 `--spec-*`） | 新版（`--draft-*`） | 说明 |
|---|---|---|
| `--spec-type draft-mtp` | `--draft-type mtp` | 投机解码类型 |
| `--spec-draft-n-max N` | `--draft-mtp-n N` | 最大预测 token 数 |
| `--gpu-layers-draft L` | `--draft-mtp-ngl L` | Draft 层数 |
| `--model-draft <path>` | `--draft-model <path>` | 外挂 Draft 模型 |

> 迁移后用 `llama-server.exe --help` 验证新参数存在（Step 1 指纹检测），并在日志确认 `draft acceptance` 健康。

## 九、Verification Checklist（验证清单）

部署完成后，Agent 自动校验以下八项：

- [ ] **ctx 数值验证**：日志 `n_ctx_slot = <目标值>`（128K→`131072` / 64K→`65536` / 32K→`32768`）
- [ ] **推理速度**：`tg ≥ 60 t/s`（12B 标准）/ `tg ≥ 85 t/s`（12B QAT 128K）/ `tg ≥ 1500 t/s prompt`（26B）
- [ ] **MTP 健康**：`draft acceptance > 0.5`（如适用）
- [ ] **WSL2 连通**：`curl http://<宿主机IP>:<port>/health` → `{"status":"ok"}`
- [ ] **安全配置**：无 API Key → `401`；跨域仅允许配置来源
- [ ] **工具调用**：Phase 1 探测 + Phase 2 两轮工具循环（如适用；Phi-4-mini 预期不支持）
- [ ] **脚本可启动**：双击 .bat 不闪退（中文 Windows 注意编码，见 Troubleshooting）
- [ ] **CPU 模式**：`-ngl 0` 时 `nvidia-smi` 无 llama 进程（确认不占 GPU）

---

**Skill End**
Agent 执行完成后应输出《部署验证报告》，包含以上八项指标及模型加载状态。
