# 首次部署指南：从零到第一次成功推理

> 适用：**全新机器**、第一次部署 llama.cpp，或换新 GPU 后重建环境。
> 范围：获取并验证 llama.cpp 预编译包 → 获取并落位模型 → 环境自检 → **首次冒烟**。
> 之后的模式选择/调优（Router Mode、模型族专项、MTP）见 `SKILL.md` §四 与各专题手册。
> 路径占位符：`<llama-cpp-dir>` = 你放 llama.cpp 的目录；`<models-dir>` = 你的模型根目录。

---

## 1. 适用判定

| 你的情况 | 读这份？ | 去哪 |
|---|---|---|
| 全新机器 / 第一次部署 | ✅ 从头读 | — |
| 环境能跑，只想加模型 | ❌ | `SKILL.md` §2.3 目录规范 + §四 Step 3 |
| 环境能跑，只是慢 / 爆显存 | ❌ | [`qwen38-gsqrco-27b-tuning.md`](./qwen38-gsqrco-27b-tuning.md) / `SKILL.md` §五 |
| 想从零搭菜单启动器生态 | 读完本文接着读 | [`../../scripts/launcher_gen/README.md`](../../scripts/launcher_gen/README.md) |

## 2. 获取 llama.cpp 预编译包

**入口**：<https://github.com/ggml-org/llama.cpp/releases> —— 选最新的 `bXXXX` 版本（**≥ b10056**，本技能基线）。

### 2.1 选哪个资产（asset）

| 你的硬件 | 选这个资产 | 说明 |
|---|---|---|
| RTX 50 系（Blackwell / sm_120） | `llama-b<BUILD>-bin-win-cuda-13.3-x64.zip` | 技能基准组合；驱动需 ≥ 610.47 |
| RTX 30/40 系（驱动较新） | 同上（cuda-13.3） | 驱动够新就统一 13.3，避免两套环境 |
| RTX 30/40 系（驱动较旧） | `llama-b<BUILD>-bin-win-cuda-12.4-x64.zip` | ⚠️ 老构建**不含 sm_120 内核**，50 系会报 `no kernel image is available` |
| 无 NVIDIA / 先跑通 CPU | `llama-b<BUILD>-bin-win-cpu-x64.zip` | 对应技能的「纯 CPU」章节 |

> ⚠️ **CUDA 运行时包**：release 页若同时提供 `cudart-llama-bin-win-cuda-13.3-x64.zip`
> （CUDA runtime DLL），**一并下载**，把里面的 DLL 解压进同一目录 —— 否则
> `llama-server.exe` 启动即退（报缺 `cudart64_*.dll`）。

### 2.2 解压与验证

解压到 `<llama-cpp-dir>`（例如 `C:\llama.cpp`），确认目录内有 `llama-server.exe`：

```powershell
cd <llama-cpp-dir>
.\llama-server.exe --version     # 打印 version/build/commit 即解压成功（或用 --help 看首行）
```

> 报「不是内部或外部命令 / 缺少 DLL」→ 解压层级错了（zip 里常多套一层目录），或 cudart 未解压。
> 拿到 build 号后，按 `SKILL.md` §四 Step 1 做**参数指纹检查**（`--spec-*` vs `--draft-*` 命名）。

## 3. 获取模型（GGUF）

**来源**（二选一）：

| 来源 | 适合 | 入口 |
|---|---|---|
| HuggingFace | 国际网络 | <https://huggingface.co>（搜 `<模型名> GGUF`） |
| ModelScope | 国内网络更稳 | <https://www.modelscope.cn>（例：`ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF`） |

**选型三步**：
1. 认准 **GGUF** 格式（不是 safetensors / 原始权重）；
2. 按显存挑量化档：16GB 卡约 **Q4–Q5 档**（`Q4_K_M` / `UD-Q4_K_XL` / `IQ3_S`，视模型大小）；
3. 看文件数：大模型常分片（`xxx-00001-of-00003.gguf`），**必须全部下载到同一目录**；
   多模态另下 `mmproj-*.gguf`；外挂 MTP 另下 draft 模型（仅该类模型需要）。

**落位**（与 `SKILL.md` §2.3 目录规范一致）：

```
<models-dir>\
└─ <模型目录名>\
   ├── <模型名>.gguf          # 分片则多文件同目录
   └── mmproj-*.gguf          # 可选：多模态投影
```

**下载校验**：文件大小应与模型卡标注一致（中断下载会留 `.part` 残留或明显偏小）。
（可选）GGUF 布局自检：`python scripts/q6-tuning/_q6_metadata.py "<models-dir>\<模型目录>"` —— 会核对张量表与文件大小并写一份 JSON。

## 4. 环境自检

```powershell
# 技能仓内（Windows）
.\scripts\detect.ps1 -llamaDir "<llama-cpp-dir>" -modelsDir "<models-dir>"

# 跨平台 Python 版
python scripts/detect.py --llama-dir "<llama-cpp-dir>" --models-dir "<models-dir>"
```

按输出逐项处理：模型计数、驱动/显存、MTP 参数指纹、服务端口连通性。

## 5. 首次冒烟

**目标只有一个：证明「exe + 模型 + 显卡」三者能出一句话。** 不追性能 —— 小 ctx、小输出、保守 ngl。

```powershell
cd <llama-cpp-dir>

# 窗口 1：启动（-ngl 先给保守值；新版也会自动分层，首测求稳不求快）
.\llama-server.exe -m "<models-dir>\<模型目录>\<模型名>.gguf" --host 127.0.0.1 --port 8080 -c 8192 -ngl 20

# 窗口 2：等窗口 1 出现 "server is listening ..." 后：
curl.exe http://127.0.0.1:8080/health
#   → {"status":"ok"}

curl.exe http://127.0.0.1:8080/v1/chat/completions -H "Content-Type: application/json" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":32}"
#   → choices[0].message.content 非空 = 冒烟通过（测试问句随意替换）
```

冒烟通过后：回到窗口 1 按 `Ctrl+C` 关闭；GPU 场景用 `nvidia-smi` 确认显存已回落。

## 6. 陷阱（第一次最容易踩的）

| 症状 | 根因 | 处置 |
|---|---|---|
| exe 启动即退，日志缺 `cudart64_*.dll` | cudart 运行时包未下载 / 未解压到同目录 | 见 §2.1 注 |
| `no kernel image is available for execution on the device` | 50 系（sm_120）用了老 CUDA 构建 | 换 cuda-13.3（或 ≥12.8）构建 |
| `CUDA error: ... driver ...` | 驱动 < 610.47（13.3 构建要求） | 升级 NVIDIA 驱动 |
| 端口 8080 被占 | 其它服务 / 旧实例 | 换 `--port`；先关旧 `llama-server` |
| 加载报 `tensor ... not found` / `unexpected EOF` | 分片不全或下载损坏 | 补下缺失分片 / 重新下载 |
| 中文/空格路径下 bat 脚本异常 | cmd 按 GBK 解析 + 路径引号 | 目录尽量纯 ASCII；bat 内路径加引号（见 `SKILL.md` §七） |

## 7. 验证协议（全过才算「首次部署完成」）

- [ ] `llama-server.exe --version` 打印构建号（≥ b10056）
- [ ] `detect.ps1` / `detect.py` 跑完无 ERROR（模型计数 > 0、驱动/显存正常）
- [ ] 冒烟 server `/health` 返回 `{"status":"ok"}`
- [ ] 一次 `/v1/chat/completions` 返回非空内容
- [ ] 关服后显存回落（GPU 场景）

## 8. 接下来

- 多模型热切换 / 菜单脚本 / 生成器：[`../../scripts/launcher_gen/README.md`](../../scripts/launcher_gen/README.md)（冷启动指南）
- 部署模式选择（Router vs 单实例）与模型族专项：`SKILL.md` §四 Step 2 / Step 3
- 一个完整的 16GB 调优实例（GSQ-RCO + MTP）：[`qwen38-gsqrco-27b-tuning.md`](./qwen38-gsqrco-27b-tuning.md)
