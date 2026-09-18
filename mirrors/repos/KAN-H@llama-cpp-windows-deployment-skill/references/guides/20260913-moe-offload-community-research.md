# MoE 卸载社区调研（llama.cpp `--n-cpu-moe`）

> **调研日期**: 2026-09-13
> **调研范围**: ggml-org/llama.cpp issues + discussions（GitHub 搜索 `n-cpu-moe`，5 页）
> **本地基准**: RTX 5060 Ti 16GB / Intel U7 270K / 48GB DDR5 / llama.cpp build 10713
> **结论一句话**: **社区没有「最优 n-cpu-moe」共识，也没有可用的自动计算脚本** —— 主流做法仍是静态层切分，前沿方向（专家缓存）**全部未合并**。但有两个**直接可用的实测发现**，见 §4。

---

## 1. 你最初问的 5 个问题，逐条回答

| 问题 | 答案 | 证据 |
|---|---|---|
| **① `--n-cpu-moe` 最优策略共识？** | **无共识，但有方法论共识**：静态层切分（把前 N 层专家放 CPU）是当前唯一生产可用的方案；「专家缓存 / 热专家驻留 VRAM」是研究前沿，RFC 满天飞但一个都没合 | #28248 / #24528 / #28363 / #20757 |
| **② 16GB 卡最佳余量？** | **硬底线 ≈ 1.0 GiB 空闲**（WDDM 分页线），且**是绝对值不是比例**。我们的 3 GB 判据是这条线的宽裕版 | #28363 zhaoyilun 的 WDDM 实测（见 §3） |
| **③ 256 专家 vs 128 专家差异？** | 专家数本身不是关键，**路由偏斜度（routing skew）才是**。256 专家/8 激活的 Qwen3.6-35B-A3B 在 16GB 卡上完全可用 | #28363 / #28248 JigSawPT 的直方图数据 |
| **④ 有没有自动计算脚本？** | **没有已合并的**。存在两个第三方实验仓（§5）。我们的「张量表预算方程 + `--tune-sweep`」在方法上不比它们差 | 搜索全量结果 |
| **⑤ 专家是否按层非均匀分布？** | **是，已用本地 GGUF 张量表证实**（§2）—— 这一条我们自己测出来了，社区没给数据 | 本地 `read_gguf_tensors()` |

---

## 2. 【本地实测】专家字节按层非均匀分布

用 `read_gguf_tensors()` 解析 GGUF 张量表，统计每层 `ffn_*_exps.*` 字节数：

| 模型 | 层数 | 专家字节/层 (均值) | **层间极差** | 模式 |
|---|---:|---:|---:|---|
| `gemma-4-26B-A4B-it-qat-UD-Q4_K_XL` | 30 | 408 MiB | **0%** | 完全均匀 |
| `Gemma4-26B-A4B-...-HauhauCS-Balanced-MTP` | 30 | 481 MiB | **17%** | 257/166 交替 |
| `Qwen3.6-35B-A3B-UD-Q4_K_XL` | 41 | 468 MiB | **17%** | — |
| `Qwen3.6-35B-A3B-Uncensored-HauhauCS-...` | 40 | 518 MiB | **31%** | 中段 432/498 交替，**末 6 层 630** |

**⇒ 结论**：
1. `--n-cpu-moe N` **不是**移除 `N × 平均值` 的显存 —— 移除的是**前 N 层实际字节数**。
2. `N × 均值` 的误差可达**几百 MiB**（Q5 末 6 层比中段大 46%）。
3. **正确做法**：用张量表的**真实累积曲线** `cum(N) = Σ per_layer[0..N-1]`，而不是层数 × 均值。
   已落地在 `estimate_ncpu_moe()`（[`scripts/launcher_gen/update_launchers.py`](../../scripts/launcher_gen/update_launchers.py)）。
4. 生产上「平均 531 MiB/层」的线性模型仍然好用（误差 <2%），因为扫描区间通常落在均匀段。

**两条独立方法互证**（这条最有价值）：
| 来源 | Q5 每层专家字节 |
|---|---|
| GPU 行为反推（`VRAM = 3779 + 13.24·ctx/1024 + (40−n)·531`，由实测阶梯回归） | **531 MiB** |
| GGUF 张量表直算（与 GPU 无关） | **518 MiB** |
| **差** | **2.5%** |

⇒ 两个彼此独立的测量互相确认，VRAM 模型和解析器都可信。

---

## 3. 【社区实测】16GB 卡的余量硬线（#28363）

zhaoyilun 的实验台：**RTX 4080 Super 16 GiB** + i9-14900KF + 96GB DDR5，**Qwen3.8-Flash-Next 176.94B**（另有 Qwen3.6-35B-A3B 对照组）。

### 3.1 余量是「绝对线」且有悬崖

| 空闲显存 | 后果 |
|---:|---|
| **858 MiB** | 解码 **−1%**（几乎无感） |
| **775 MiB** | 解码 **−11%**，TTFT **×2.3** |
| 536 MiB（262K staging） | **NO-GO** —— 降级为 WDDM 共享内存爬行，40 分钟后终止 |
| 453 MiB（`--n-cpu-moe 12`） | **病态降级** |
| 323 MiB（ubatch 4096） | **病态降级** |
| **~1.0 GiB**（260K 跑满 4 分钟） | ✅ 不崩 |

> 原文：**"83 MiB separate 'unnoticeable' from 'broken'"**
> 且**不确定**："whether you collapse depends on residency"

**⇒ 对本地判据的意义**：用户的 **3 GB 余量**把这条 1 GiB 硬线留出了 3 倍安全系数，
而且是在「视觉请求吃 ~500 MiB 不可回收 CUDA graph 缓存」之后仍成立。**判据偏保守是正确方向。**

### 3.2 同款模型的实测数字（可直接对照）

**Qwen3.6-35B-A3B（Q4_K_M, 21.2 GB, 40 层 = 10 full attention + 30 linear, 256 专家/8 激活, 262K）**
在 **未修改的 llama.cpp b10666** 上，`--n-cpu-moe 24`，q8_0 KV，**`-ub 2048`**：

| 指标 | 数值 |
|---|---|
| 63K 冷 prefill | 184.6 → **1,460 tok/s（7.9×）**，仅靠把 physical ubatch 128 → 2048，**解码不变** |
| 260K 冷 prefill | 238 s = **1,091 tok/s** |
| 260K 处 512-token 解码 | **34.3 tok/s** |
| 解码 2.4K → 260K 衰减 | 57.5 → 34.3 tok/s（因为 40 层里只有 10 层是 full attention） |

**⇒ 两个可以直接抄的结论**：
1. **`-ub 2048`（ubatch）是 prefill 的免费杠杆** —— CPU 侧专家张量**每层每个 ubatch 搬一次，
   与 ubatch 大小无关**，所以 ubatch 越大摊得越薄。**解码不受影响。**
   ⚠️ 注意 ubatch 会影响 compute buffer 大小（显存），需在余量预算里留位置。
2. 我们的 Q5 在 262144 ctx / n=30 实测 **32.3 t/s**，与他们的 n=24 / 260K / **34.3 t/s** 同档 ——
   说明我们还有 n 下探空间（他们的 24 vs 我们的 30），但 16GB 卡 + 21.8GB 模型已接近极限。

**另一组数据（#28248 MichaelDietzel）** —— Qwen3.6-35B-A3B-UD-**Q6_K_XL**，2080 Ti 22 GiB：
| n-cpu-moe | t/s |
|---:|---:|
| 40 | 38.20 ± 1.75 |
| 30 | 44.34 ± 1.44 |
| 20 | 49.57 ± 3.62 |
| **13** | **54.25 ± 3.29** ← "pretty much the limit before the GPU goes OOM" |

### 3.3 ⚠️ **`--n-cpu-moe` + mmap = prefill 掉 60%**（#28363，原文）

> "on current master, `--n-cpu-moe` + mmap costs ~60% of prefill unless `--load-mode none`
> is set (the server warns about tensor overrides with mmap; measured **1,293 → 2,145 t/s at 22.7K**
> on the same binary). Might be worth making that combination warn louder or default differently."

**⇒ 这直接验证了本地 A 组刚完成的 X5 迁移**（`--no-mmap` → `--load-mode none`，14 处）。
社区独立实测给出了机制：`--n-cpu-moe` 产生 tensor overrides，与 mmap 组合会拖垮 prefill。
**我们不是「顺手换个新写法」，而是修掉了一个 60% prefill 的性能洞。**
（`--load-mode none` 也正是 #28248 里各家的标准命令写法。）

### 3.4 MTP head 可跨微调移植（+28% 解码）

zhaoyilun 把官方 Qwen3.6-35B-A3B 的 MTP head **在张量层面嫁接到社区无审查微调上**
（微调版不带 head，无法用 `draft-mtp`）：

- head = **恰好 20 个 `blk.40.*` 张量**（纯新增）
- **必须把 `qwen35moe.block_count` 从 40 改写成 41**，否则加载器找不到 `blk.39.nextn.*` 而失败
- 实测（同 16 GiB 机器，b10819，`--n-cpu-moe 24`，q8_0 KV，`-ub 2048`，128K）：
  **解码 62.2 → 79.4–79.7 tok/s（+28%）**，draft acceptance **0.851–0.891** / mean 2.70–2.77
- 关键结论：**"the MTP head tolerates substantial weight drift in the target,
  so heads are portable across fine-tunes of the same base"**
  （投机解码本身无损；head 不匹配只降低接受率）

**⇒ 对我们直接可用**：`Q5 Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive` 是同基座微调且**没有 MTP head**。
嫁接官方 head 后理论 **+28% 解码**，且 `draft-mtp` 不占额外显存（内置 head）。
**这是目前已知最大的单点收益机会**（待验证，需张量级移植）。

---

## 4. 专家缓存：前沿状态（**全部未合并**）

有人多次尝试把「热专家留在 VRAM」做进上游，**全部被关闭**：

| PR/Issue | 内容 | 状态 |
|---|---|---|
| #20757 | Feature Request: Two-tier GPU+RAM expert cache | **open**（feature request） |
| #21614 | ggml: persistent expert cache for `--n-cpu-moe` | **closed** |
| #21620 | ggml: dedup expert cache for MoE CPU offload | **closed** |
| #24524 | cuda: MoE expert cache, adaptive VRAM caching | **closed**（scope） |
| #27861 | GPU-resident LRU cache for host-offloaded MoE expert weights | **open**（PR） |
| #28248 | RFC: Persistent expert slot pool (`--moe-expert-cache`) | **open**（RFC，非主线） |
| #24528 | RFC: MoE expert cache, VRAM caching of hot experts | **open**（RFC，69 评论） |
| #28363 | Experiment: fixed GPU expert working set | **open**（实验，非 PR） |

**⇒ 结论：不要等上游，也不要自己打补丁**（Windows + CUDA 上已有多人报告崩溃/无收益）。

### 4.1 缓存收益的**先验判据**（很实用）

**闭式 breakeven**（#28248，MichaelDietzel）：

$$\text{需要命中率} \geq 1 - \frac{\text{PCIe 带宽}}{\text{RAM 带宽}}$$

- PCIe 3.0 / DDR4-136GB/s → 需 **≈91%** 命中率
- PCIe 5.0 / DDR5-99GB/s → 需 **≈36%**
- 实测 N=16 vs N=160 分别落在该线两侧，方向吻合

**路由偏斜度判据**（JigSawPT 直方图）：
| 模型 | 命中集中度 | 缓存收益 |
|---|---|---|
| Coder-Next | ~80% 命中落在 ~28% 专家 | 高（接近线性） |
| gpt-oss / Step-3.7 | 平坦 | +2% / +5–12% |
| DeepSeek-V4-Flash | 每层熵 6.3–7.9 / 8.0 bit | **~0**（静态热表 +3%，噪声内） |

**⇒ 实操**：**先跑一次路由直方图，再决定要不要花一晚上扫 N。**
（`llama.cpp` 新 `moe-trace` example 可导出原始路由决策。）

### 4.2 静态切分 vs 动态 LRU（同模型同槽数实测）

Step-3.7，61k 文档：**深度处 LRU ≈ 静态**（+13% vs +12%），**512-token 生成 LRU 胜出**（+20% vs +13%）。
⇒ 动态策略在浅层/生成场景确实多赚，但**深度处不再有优势**。

---

## 5. 第三方工具（无官方等价物）

| 仓库 | 内容 |
|---|---|
| `github.com/JigSawPT/moe-autopilot` | **VRAM-cliff 探针**、batch-1 drift harness、static-vs-dynamic harness |
| `github.com/zhaoyilun/moe-working-set-16gb` | #28363 的完整证据包（patch、runner、~1150 证据文件、build/repro 文档） |

**⇒ 我们自己的工具已经覆盖了同类能力**：
`plan/_phase2_loadprobe.py` ≈ VRAM-cliff 探针；`--tune-sweep` ≈ N 扫描；
本文件的 §2 张量表解析**社区没有等价物**。

---

## 6. 其它值得记的小结论

| 结论 | 来源 |
|---|---|
| `N = top-k` 是**满miss最坏情况**，比不用缓存还慢；**从 2–4 × top-k 起步再扫** | #28248 |
| 缓存 flag **不做自动定尺寸**（"our flag doesn't auto-size N anyway"） | #28248 |
| VRAM rail 应为**绝对值**：`free − 估算的最大上下文 KV − 1.0 GiB reserve`，**按层逐个判断**（每层可用槽数可以不同） | #28248 JigSawPT/MichaelDietzel |
| **PPL 不是验收标准**：池化后 PPL 变化 <1%，但 argmax 翻转 2%/6% —— 必须用 batch-1 KLD / top-1 翻转率 | #28248 JigSawPT |
| `--prefetch-weights`（#21067）对 MoE 反而搬 2.06× 字节、TTFT +47.8% | #28248 |
| WSL2 跑同一个模型有 **−12…−21% 解码税** | #28363 |
| 缓存池会**吃掉 KV 增长的空间**，导致更早撞分页线 —— 「随上下文变慢」的常见误因 | #28248 |

---

## 7. 对本地配置的**可执行建议**（按收益排序）

1. **【高】给无审查 Qwen3.6-35B-A3B 嫁接官方 MTP head** → 预期 **+28% 解码**（§3.4）。
   需：20 个 `blk.40.*` 张量 + `qwen35moe.block_count` 40→41。**未验证，建议在副本上做。**
2. **【高】把 `-ub`（ubatch）提到 2048** → prefill 可达 **7.9×**，解码无损（§3.2）。
   需先确认 compute buffer 增量在 3 GB 余量内。
3. **【已完成】`--load-mode none`** → 已修，社区实测这是 **60% prefill** 的差别（§3.3）。
4. **【中】用张量表累积曲线替代 `N × 均值`** → 已落地（§2）。
5. **【低/不做】专家缓存补丁** → 上游全未合并，Windows+CUDA 有崩溃报告，收益依赖路由偏斜（§4）。

---

## 8. 参考链接（全部为本次实读）

- https://github.com/ggml-org/llama.cpp/discussions/28363
  — *Experiment: fixed GPU expert working set with Native CPU miss execution for Qwen sparse MoE (16 GiB GPU, 16K-262K context)* · zhaoyilun · 2026-09
- https://github.com/ggml-org/llama.cpp/discussions/28248
  — *RFC: Persistent expert slot pool for MoE CPU offload (`--moe-expert-cache`), +84% decode* · memoriaru · 2026-09
- https://github.com/ggml-org/llama.cpp/discussions/24528
  — *RFC: MoE expert cache, VRAM caching of hot CPU-resident experts* · leloch
- https://github.com/ggml-org/llama.cpp/issues/20757
  — *Two-tier GPU+RAM expert cache for MoE offload (pluggable eviction policy)*
- https://github.com/ggml-org/llama.cpp/discussions/27289
  — *Why is a CPU buffer being allocated instead of a CUDA_Host buffer when CPU+GPU MoE offloading*
- https://github.com/ggml-org/llama.cpp/discussions/23324
  — *RFC+PoC: MoE offload to disk with on-demand paging*
- https://github.com/ggml-org/llama.cpp/discussions/27393
  — *Tensor Split for MoE models*
- https://github.com/ggml-org/llama.cpp/discussions/28588
  — *How to stop Qwen 3.8 Flash Next from consuming ALL the system ram?*
- https://github.com/ggml-org/llama.cpp/discussions/27950
  — *Qwen3.8-Flash-Next on Strix Halo (gfx1151): 17 → 47 tok/s*
- https://github.com/ggml-org/llama.cpp/discussions/19890
  — *RTX 5090 (CUDA) vs Radeon AI PRO R9700 (Vulkan) — Qwen3.5-35B-A3B MoE Q4_K_XL llama-bench*
