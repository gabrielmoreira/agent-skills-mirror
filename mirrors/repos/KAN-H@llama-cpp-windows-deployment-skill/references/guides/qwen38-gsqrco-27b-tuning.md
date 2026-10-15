# Qwen3.8-27B GSQ-RCO（非均匀量化）+ 内置 MTP：16GB 显存实机调优档案

> 日期：2026-10-12 ｜ 硬件：RTX 5060 Ti 16GB + 48GB DDR5 + Intel U7 270K（24C）
> 平台：Windows 11 + llama.cpp **b10713**（0.3.0-dev, commit 557614e02, CUDA 13.3 构建）
> 模型：[ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF](https://www.modelscope.cn/models/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF) 的 `IQ3_S-mtp` 构建
> 全部数据来自本机实测（探针 `scripts/q6-tuning/_q6_probe.py`，原始记录 `references/sessions/_q6_results.json`）

---

## 0. 一句话结论（TL;DR）

**IQ3_S-mtp + KV q4_0 + 全层 GPU（ngl 64）+ 141K ctx（138K token）** 是该模型在 16GB 卡上的唯一可行全速档：
45K 上下文实测 **decode 27.5 t/s（含 MTP，+31.5%）/ prefill 717 t/s**，代价是余量仅 ~361 MiB。
**任何 CPU 层卸载都会断崖式掉速（-48% 起）**——这与 MoE 模型的经验完全相反（见 §6）。

---

## 1. 模型档案（GGUF 元数据逐项实测，`scripts/q6-tuning/_q6_metadata.py`）

| 项 | 实测值 | 说明 |
|---|---|---|
| 文件 | `Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf` 11.28 GiB（12,109,021,184 B）+ `mmproj-...-BF16.gguf` 0.87 GiB | 大小交叉校验 **delta 0.000%** |
| 架构 | `qwen35`，block_count **65**，nextn_predict_layers **1** | **blk.64 = MTP 块** |
| MTP 头 | **15 张张量 / 332.3 MiB**（Q6_K attn+FFN + F32 的 nextn 机构） | 与官方描述"15 个张量"逐字吻合 |
| 注意力 | GQA 24/4 head、K/V len 256；`full_attention_interval=4` | 16 层 full + 48 层 Gated DeltaNet（SSM） |
| SSM | state_size 128 / inner_size 6144 / conv_kernel 4 / group 16 | 线性层 state **不随 ctx 增长** |
| ctx_train | 262,144 | |
| 量化构成（逐张量） | IQ3_S 3.39 + IQ4_XS 2.81 + IQ3_XXS 1.93 + Q4_K 1.47 + IQ2_S 0.75 + Q6_K 0.32 + … 共 12 种 GiB | GSQ-RCO = 每个张量独立分配类型 |
| 内嵌官方采样 | temp 1.0 / top_p 0.95 / top_k 20 / min_p 0 | 与 unsloth 官方 thinking 参数一致 |

官方解码质量（ModelScope 模型卡）：IQ3_S 在 **AIME25 100.00 / LiveCodeBench 85.71 与 BF16 完全一致**（GPQA-Diamond -0.51），任务平均分 99.8% —— "任务无损"工作点。

**层字节曲线**（写显存预算用）：blk.0 133.3 → blk.63 187.0 MiB（前小后大），均值 158.5 MiB，blk.64（MTP）332.3 MiB。

---

## 2. 上游风险调研（llama.cpp issues，2026-10 现况）

| Issue | 内容 | 对本机的影响 |
|---|---|---|
| **#30302** | 同款 GSQ-RCO-IQ3_S-mtp：Windows + CUDA 开 `--spec-type draft-mtp` **首推理即蓝屏**（HYPERVISOR_ERROR / CLOCK_WATCHDOG）；Vulkan 正常；报告者 RTX 5090M + 616/617 驱动 | ⚠️ 本机 b10713 **冒烟 + 全矩阵未复现**（>10 次 MTP 实跑全部正常）。新驱动/新 build 用户仍需先冒烟 |
| #30307 | qwen4exp (Qwen3.8-Flash) + MTP + mmproj 图像请求 abort（`GGML_ASSERT(ubatch.token)`），b11548+ 引入 | b10713（较旧）不受影响；带图 + MTP 的组合在新 build 上要注意 |
| #30368 | draft-mtp + `--kv-unified` + `-np>1` decode 崩溃 | `-np 1` 不触发 |
| **#30357** | Qwen3.5+/qwen35 系：reasoning/content 空白不可 round-trip → hybrid 模型前缀增量缓存失效 → "forcing full prompt re-processing" 全量 re-prefill（间歇，取决于采样空白） | 90K 单请求实测 `reprefill=0`；长 agent 多轮场景需观察日志此字符串 |

---

## 3. 实测矩阵（45K token 长 prompt，除注明外）

### 3.1 KV cache 类型阶梯（141K ctx，fit 自动分层，无 MTP）

| KV 类型 | decode t/s | VRAM MiB | 余量 MiB | 机制 |
|---|---|---|---|---|
| q8_0 / q8_0 | 14.35 | 14,326 | 1,985 | fit 少放几层 |
| q8_0 / q4_0 | 22.01 | 14,372 | 1,939 | ↑ |
| **q4_0 / q4_0** | **26.30** | 14,390 | 1,921 | fit 已给到**全 64 层** |

⇒ fit 会把 KV 省下的显存自动换成更多 GPU 层；q4_0 档与手工 `-ngl 64` 完全同值（26.2 / 同 VRAM），**fit 不再保守**。

### 3.2 batch/ubatch（反直觉：dense 无收益）

| batch/ub | prefill t/s | decode t/s | VRAM | 备注 |
|---|---|---|---|---|
| 512/512 | 745 | 20.87 | 14,414 | |
| 2048/2048 | 738 | 20.87 | 15,352 (-938 余量) | **dense 无 CPU 专家搬运，MoE 的 `-ub 2048` 杠杆不适用** |

### 3.3 MTP（内置 draft-mtp，n-max 3）

| 上下文 | 无 MTP | 有 MTP | 增益 | acceptance | mean len | MTP 显存代价 |
|---|---|---|---|---|---|---|
| 4K（冒烟） | 28.4 | **48.0** | **+69%** | 0.667 | — | +934 MiB |
| 45K 长文 | 20.87 | **27.45** | **+31.5%** | 0.507 | 2.51 | **+1,536 MiB** |
| 90K 检索（no-think 短输出） | — | 16.4* | — | **1.0** | — | — |

\* 该点为混合配置（ngl61，见 §6），速度被 CPU 断崖拖累；acceptance 1.0 说明**结构化短输出（工具调用/列表）下 MTP 几乎零损耗**。

### 3.4 长 prompt 素材实测（90K token）

- prefill：**586-717 t/s**（45K 与 90K 量级一致）
- 90K token = 130,772 中文/混合字符（≈1.45 字符/token）
- `graphs reused` 稳定、`reprefill=0`
- ⛔ **单发超大 prompt 性能悬崖**：135K（全层+MTP）>10 分钟未完成 prefill；**90K@全层+MTP 也异常缓慢**（>5 分钟，已终止）；而 **90K@ngl61（余 835）与 45K@全层 均正常** ⇒ **性能档舒适单发 ≤45K（保守值）**；**会话累计 KV 到 138K 不受此限**（KV 预分配，逐轮增长没问题）。需要单发大 prompt 时改用无 MTP 配置（视觉档/稳定档）。

---

## 4. 显存方程（16,311 MiB 卡，实测标定）

```
全层 GPU + MTP + b256 + 141K ctx:
  q4_0 KV: 15,756 MiB used / 555 MiB free（b512 时为 15,950/361——b256 省 194 MiB）
无 MTP:            14,414 MiB / 1,897 MiB free
+ mmproj (BF16):   +888 MiB → 15,302 MiB / 1,009 MiB free（视觉档成立，无需卸层）
   ⇒ mmproj 与 MTP 不可叠加（+888+1536=2424 MiB），视觉档固定用无 MTP
```
- 权重（全 65 块含 MTP 头）：11,550 MiB
- 141,312 token KV（q4_0）：≈ 2,500 MiB（其中 full 层线性部分 ~2.1 GiB + SSM 固定部分）
- MTP 路径增量（@141K）：**1,536 MiB** —— 是头部权重（332 MiB）的 **4.6 倍**（draft 自己的 KV / compute / CUDA graph）

---

## 5. 采样与推理参数（官方 + 实机）

```bat
--temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 --presence-penalty 0.0 --repeat-penalty 1.0
--reasoning-preserve --reasoning-budget 8192 --reasoning-format deepseek
--chat-template-kwargs "{\"reasoning_effort\":\"medium\"}"
```
- 思考型模型：客户端 `max_tokens` 太小时 content 会空/截断（≥300 起）
- `--reasoning-format deepseek` 是预算生效的前提（防死循环，历史 FND-069）
- 非思考 / 工具场景：请求级 `enable_thinking:false` 或 `reasoning_effort:none`

---

## 6. ★ CPU 参与断崖（本模型最重要的新事实）

| 配置（45K prompt，均带 MTP） | CPU 参与 | decode t/s | 相对全层 |
|---|---|---|---|
| 全层（ngl 64）b512 | 0 | 27.45 | — |
| 全层（ngl 64）**b256** | 0 | **28.10** | +2.4%（且省 194 MiB） |
| `-ngl 61`（3 层整层 CPU） | 3 层 | 14.39 | **-48%** |
| `-ngl 58`（6 层） | 6 层 | 11.46 | -58% |
| `--n-cpu-ffn 8`（8 层 FFN 上 CPU） | 0.7 层当量 | 19.19 | -30% |

**机制**：dense 模型 + MTP 时，CPU 层在主 forward 与 draft/verify forward 中**各走一遍**；且每 token GPU↔CPU 需同步。
**与 MoE 的对比**：MoE（如 35B-A3B）卸几十层专家仍有 40-70 t/s——其 CPU 专家路径是大矩阵批量搬运、且每 token 只激活少量专家。
**⇒ 部署规则：本模型（及同类 dense + MTP）必须全层 GPU；任何"省显存换层卸载"都会把 27 t/s 打成 11-14 t/s。**
**⇒ 余量不足时，正确动作是换 KV（q4_0 地板）或降 ctx，而不是卸层。**

---

## 7. 最终配置（2026-10-12 实测定型 · 双档）

| 档 | 菜单 | 配置 | 45K 实测 | 余量 |
|---|---|---|---|---|
| **Q6 纯文本 Agent（性能档）** | Qwen 启动器 | `-ngl 64` + KV q4_0 + **MTP**（n-max 3）+ b256/u256 + ctx 141312 | **28.10 t/s**（prefill 690） | **555 MiB** |
| **Q6m 视觉档** | Qwen 启动器 | `-ngl 64` + KV q4_0 + **mmproj** + **无 MTP** + b256/u256 + ctx 141312 | **20.66 t/s**（prefill 744） | **1,009 MiB** |
| （备选）稳定档 | 手动 | 同性能档，去掉 `--spec-type draft-mtp` | 20.87 t/s | 1,897 MiB |

- 落地位置：`launcher/launcher-models.json`（Q6/Q6m 两条目，`RUN_QWEN3_8_27B_GSQ_RCO__MTP` / `__IMG`）→ 生成 `start-Qwen-Launcher.bat`；端口 8084。
- **单发 prompt ≤90K**（135K 单发实测 >10 分钟未完成 prefill，无报错）；**会话累计 KV 到 138K 无限制**（逐轮增长安全，90K 检索 acc=1.0 / reprefill=0）。
- MTP 增益：+31.5%（45K）/ +69%（短上下文）；短结构化输出 draft acc 可达 1.0。
- 禁止与 MTP 叠加：mmproj（+888 MiB 装不下）、任何 CPU 卸载（-30%~-58% 断崖）。
- `--spec-draft-p-min 0.75`：acceptance 升至 0.865 但 decode 反降 7.2% —— **勿用**。
- 5.0 采样 / reasoning 参数见 §5；原始数据 `references/sessions/_q6_results.json`（18 组）+ 报告 `references/sessions/20261012-qwen38-gsqrco-27b-tuning-report.md`。

---

## 8. 复现与探针

- 元数据：`python scripts\q6-tuning\_q6_metadata.py`（基线收录于 `references/sessions/_q6_metadata.json`）
- 单配置测量：`python scripts\q6-tuning\_q6_probe.py`（argv 列表传参、VRAM/health/acceptance 解析、日志落 `logs\`、结果追加 `_q6_results.json`）
  - MTP 冒烟（低风险首测）：`--smoke --mtp --tag smoke`
  - 长 prompt：`--prompt-file logs\q6-long56k.txt`（45K token 实测素材）
  - NIAH：`logs\q6-niah110k.txt`（90K token + 3 针 @25/50/75%）；`--no-think` 防止思考吃光 token
- 启动器落地：`python scripts\q6-tuning\_q6_apply.py`（registry + overrides 一次写入，见 launcher/update_launchers.py 的 FND-070/071 修复注释）
- 六脚本共用环境变量解析（`LLAMA_DIR` / `CHAT_DIR` / `LAUNCHER_DIR`），用法与产物见 `scripts/q6-tuning/README.md`。
