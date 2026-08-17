# 2026-08-16 实战经验沉淀（26B-A4B `--fit` 自动显存分层 + 启动脚本自动化方法论）

> 来源：2026-08-09 / 08-16 多个会话 | 硬件：RTX 5060 Ti 16GB + Intel U7 270K + 48GB DDR5 | llama.cpp b10158+
> 一句话：**16GB 显存跑 26B-A4B 别再手写 `-ngl`/`-ngld` 试错——用 `--fit on --fit-ctx <ctx>` 让 llama.cpp 自动分层，实测 7 倍提速；长会话降速的根因是"显存临界导致 CUDA graph 回退"，不是 KV 膨胀。**

## 一、26B-A4B QAT 长会话降速根因（实测）
- **KV 膨胀论不成立**：Gemma 4 是 SWA 混合注意力（30 层中 28 层滑动窗口 1024）→ 64K q8_0 KV 仅 ~0.4GB。瓶颈 = 14.25GB 权重 + draft 425MiB + mmproj ~0.75GB ≈ 16GB 临界 → CUDA graph 回退 → 解码阶梯降速。
- 实测基准（51K 上下文 tg t/s）：
  - 旧基线（硬 ngl36 + gld24）：**10.6**
  - draft 全 CPU（gld0）：**26.9**
  - `--fit on --fit-ctx 65536`（自动留 ~2.4GB 权重在 host）+ gld8：**72-93**（~7 倍）
- 关键证据：S1 日志 `offloaded 31/31 layers to GPU`（13,573 MiB）+ KV 839MiB + draft 425MiB + mmproj ≈ 超 16GB → CUDA graph 回退。
- **本 build fit 默认 on，但 `-ngl` 被用户显式设置时会 abort**（日志 `n_gpu_layers already set by user`）→ 硬编码 `-ngl` 是降速帮凶。修复：26B 条目删 `-ngl` + 显式 `--fit on --fit-ctx 65536`。

## 二、ctx-shift 与 mmproj 的互斥（重要）
- 带 mmproj 时 **ctx_shift 被自动禁用**（源码 `server-context.cpp`）。
- `--context-shift` 仅对 **n_predict=-1 无限生成**生效（b10158 实测 0.6B 探测 14 次 shift；有限 n_predict 仍在 64K truncated）。
- 纯文本无 mmproj 的核心收益是**前缀缓存复用**（实测第二轮 prompt_n=7，不再全量重算历史）。

## 三、128K 是 26B-A4B 官方甜点
- ctx_train=262144（GGUF 元数据）；SWA 使 KV 随 ctx 增长极小（64K 0.84G → 128K ~1.0G）。
- MRCR 128K 八针 26B=44.1%（256K 质量衰减）→ 128K 是官方甜点。
- 实测：纯文本 128K @100K prompt `pp=1480 / tg=45.5` 无 OOM 无截断 ✅。
- 落地：菜单 9→10「128K 纯文本Agent」、新增菜单 9「128K 多模态」（`-c 131072 --fit-ctx 131072 --timeout 300`）；26B 破限版菜单 14/15 fit 化（删硬 ngl + gld 8 + metrics，实测 tg=70，label 改 `[fit]`，删除过期 `[!]已知失败`）。

## 四、CPU Toolcall 新模型实测（2026-08-09）
- **QwenPaw-Flash-9B**：arch=`qwen35`（Qwen3.5 混合：24 Gated DeltaNet + 8 Gated Attention），ctx 原生 256K，KV 极小（128K q8_0 ~2GB）。工具调用✅（Qwen3 XML 解析器）。官方采样 temp 1.0/top-p 0.95/top-k 20。非 MTP 版 32 块，heretic-MTP 版 33 块（**内置 MTP head，无需 --model-draft**，用 `--spec-type draft-mtp --spec-draft-n-max 2`）。
- **MTP 在 CPU 上实测生效（b10158）**：MTP 版 27.3 t/s vs 非 MTP 15.7 t/s（**+74%**）；日志 `draft acceptance = 0.725` / mean len 2.42 / graphs reused 25 ✅。
- **LFM2.5-8B-A1B-UD**：arch=`lfm2moe`（MoE 32 专家/4 活跃，24 层，18 gated conv+6 GQA），ctx 128K。44.1 t/s（CPU，同档最快）。工具调用✅（LFM2 专用解析器，b10158 含 #23856 修复）。⚠️ llama.cpp issue #26658：工具参数含引号/转义可能解析失败（规避：要求双引号无转义）。官方采样 temp 0.2/top-k 80/repeat-penalty 1.05。
- **踩坑：llama-cli 单次测试必须用 `-st`（--single-turn）**；`-no-cnv` 在 b10158 仍进交互模式等 stdin，用 `Select-Object` 管道时看似卡死（实际等输入），勿误判为 hang。

## 五、启动脚本自动同步方法论（update-launchers）
- 三源合并：家族模板 → profile 覆盖 → 用户注册表最终；`--audit` 做 GGUF 头解析（arch/层数/SWA/KV 维度）+ KV 内存估算 + 采样对比 + 显存红绿灯。
- 删除语义：条目 dirs 缺失→移除条目+变量组（含注释）+重编号菜单；agent 变体条目通过 `goto RUN_X` 继承目标 dirs。
- 新增语义：家族规则（gemma→gemma4 / qwen→qwen / lfm→cpu / 其他→qwen）自动生成默认条目（菜单标 [NEW]），gemma 自动配对 gemma4_mtp draft 生成 +MTP 条目。
- ini 改进：去掉 generate_ini 的"文件名含 mtp/draft 即排除"过滤→内置 MTP heads 模型（Qwen3.6 MTP 系、QwenPaw-heretic）现在也进 Router 配置。
- 每次写入前自动备份 `backup\<名>.bak-YYYYMMDD-HHMMSS`；注册表每次保存也备份。
- 生成器 GBK strict 写出（Gemma4/Qwen）、ASCII（CPU/ini）、CRLF、无 BOM、保留每个菜单行的 echo 前缀空格（1-9 两空格/10+ 一空格的原始差异）。
- 回归验证方法：`--no-scan` 渲染 + 与 `backup\` 中 .bak 或原文件 difflib 逐字节比对，应零差异。
- **手工调整参数的入口改为编辑注册表 JSON（label/body 均可改），改完重跑更新器；不要直接手改 3 个启动脚本（下次运行会被覆盖）。**

## 六、BAT 灾难恢复 SOP：GBK 中文乱码合并（skeleton+LCS）
- 背景：`start-Gemma4-Launcher.bat` 多次被外部工具重新保存为 UTF-8 产生 U+FFFD 乱码（已发生 3 次）。
- 恢复方案（成功）：以损坏文件为基准（ASCII/最新配置完整），中文用 `backup\` 中干净 GBK 版补齐。
- 合并算法：**skeleton 对齐（保留全部 ASCII、连续非 ASCII 折叠为单个 §）+ LCS**，**不能用「非 ASCII 字符数」对齐**（U+FFFD 会把多字节折叠，导致对不上）。
- 输出：GBK 无 BOM 无 chcp。损坏文件备份 `backup\<名>.utf8corrupt-YYYYMMDD`。

## 七、MTP draft 官方来源判定法
- **官方 `unsloth/gemma-4-26B-A4B-it-GGUF` 的 MTP 只有 Q8_0/BF16/F16，从未有 Q4_0**。文件名含 Q4_0 的一律第三方。
- 第三方 Q4_0 draft 在 **llama-server** 的 draft 加载路径报 `invalid vector subscript` 崩溃；**llama-cli 单独加载却正常** → 测试必须用真实 server 命令（查 `/health`），llama-cli 会误判。
- 判据：`Get-Item <draft>.gguf | Select Name,Length`（440MB=官方 Q8_0, 240MB=Q4_0）。
- 修复：`DRAFT_TYPE=q8`，`D26_Q4`/`D26_UNCENS` 都指 `mtp-gemma-4-26B-A4B-it-Q8_0.gguf`；坏 Q4_0 移入 `gemma4_mtp\_unused_thirdparty_Q4_0\`。
