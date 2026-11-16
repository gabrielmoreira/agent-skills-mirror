# 版本升级与显存余量预算（Upgrade & VRAM headroom）

> 适用对象：Windows + 单卡 16GB（或同级）跑 20GB+ MoE 模型、用 Router / 启动器管理多模型。
> 实测来源：[`../sessions/20261115-v1-upgrade-moe-cache-report.md`](../sessions/20261115-v1-upgrade-moe-cache-report.md)

---

## 1. 适用判定（先回答这 5 个问题）

| 你的诉求 | 本文是否适用 | 第一动作 |
|---|---|---|
| 「驱动 / 新版本说能快 2 倍，我要不要加参数？」 | ✅ | 读 §2，先算余量，再决定要不要动 |
| 换 build / 换 CUDA 运行时包 | ✅ | 走 §3 升级流程 + §6 验收 |
| 想开 `--moe-cache-mib` | ✅ | 先过 §4 的三条前提，大概率不该开 |
| 想调 `n-cpu-moe` / 开 `-np >1` | ✅ | 先过 §2 余量体检，再按 §5 做交错 A/B |
| 只是想首次部署 | ❌ | 转 [`first-time-setup.md`](./first-time-setup.md) |

**一句话判据**：本类卡上的"提速空间"几乎全部由 **显存余量**决定，而不是由某个新参数决定。
先量余量，再谈参数。

---

## 2. 显存余量体检（做任何改动之前）

### 2.1 读 fit 判决行

带 `--fit on` 启动一次（哪怕你平时不加这个参数），在日志里找这三行：

```
| CUDA0 (…) | 16283 = 15172 + ( 7325 = 5628 + 512 + 1185) + -6213 |
projected to use 12236 MiB of device memory vs. 15172 MiB of free device memory
will leave 2935 >= 2129 MiB of free device memory, no changes needed
```

| 字段 | 含义 | 怎么用 |
|---|---|---|
| `free 15172` | 启动时程序看到的空闲显存 | 与 `nvidia-smi` 常有几百 MiB 差异（WDDM），**以程序看到的为准** |
| `model 5628 / context 512 / compute 1185` | GPU 侧权重 / KV / 计算缓冲 | 想加缓存就砍 `compute`（降 batch）或 `context`（降 ctx） |
| `will leave X >= Y` | 投影余量 X，程序最低要求 Y（本机实测 Y=2129，随显存规模变化） | **X − Y 就是你的真实富余** |
| `no changes needed` | fit 认为无需调整 | ⚠️ 只表示"当前够了"，**不表示余量充足** |

### 2.2 三档判定

| 真实富余（X − Y） | 判定 | 允许的动作 |
|---|---|---|
| < 200 MiB | 🔴 红线 | 什么都别加；连"多开一个桌面程序占显存"都要避免 |
| 200–800 MiB | 🟡 紧 | 只允许**减少**占用（提 `n-cpu-moe`、降 batch、降 ctx） |
| > 800 MiB | 🟢 有余量 | 才可以考虑缓存 / 并发 / 更大 mmproj |

实测参考：262K + 34 层 CPU 专家 + MTP + mmproj 的组合落在 **204 MiB**（🔴），
同配置换成 36 层可回到 **>1 GiB**（🟢），代价是 prefill 慢 2%–5% 与多 ~1 GiB RAM。

> ⚠️ `--fit` **不是安全网**：投影不足时它是否真的会下调，尚未验证（没有零风险探针）。
> 余量必须自己算，不能"开了 fit 就敢加参数"。

---

## 3. 升级 build 的步骤

1. **备份整套二进制**（不要只备份 exe）：
   `llama-server.exe`、`llama-server-impl.dll`、`llama.dll`、`llama-common.dll`、`mtmd.dll`、`ggml*.dll`、`cudart64_*.dll`、`cublas*64_*.dll`。
2. **确认 CUDA 运行时是否要换**：若新旧包都是同一 CUDA 主版本（如 13.5），
   `cudart64_13.dll` / `cublas64_13.dll` / `cublasLt64_13.dll` 常逐文件相同 ⇒ 不必替换。
   用 `Get-FileHash` 对比再决定。
3. **整套覆盖**到 `<llama-cpp-dir>`，不要混装（旧 `ggml-cuda.dll` + 新 `llama.dll` 会崩）。
4. **不要改 ini / preset**：先证明"只换二进制"能跑，再谈调参。
5. `llama-server.exe --version` 记录 build 与 commit；`--help` 确认脚本里用到的参数仍在。

### 3.1 换版本时的参数考古（按需）

- 全新 `--spec-*` 命名 ↔ `--draft-*` 命名：见 SKILL.md §八 映射表。
- 已废弃：`--no-mmap`（→ `--load-mode none`）、`--defrag-thold`。
- 新版可能"静默改变行为"：本次实测同一 prompt 下新 build 思考更长，**客户端输出上限要留够**。

---

## 4. `--moe-cache-mib` 该不该开（三条前提）

| # | 前提 | 怎么验证 |
|---|---|---|
| 1 | 模型专家体量 ≫ 显存，且显存能空出 **≥ 10% 专家总量** | §2 的余量 ≥ 0.1 × 专家总字节 |
| 2 | 负载以小批量解码为主（≤ 32 token/批） | 看实际用途：Agent 单流 ✅ / 批量离线 ❌ |
| 3 | 能观测命中率与传输开销 | 日志/指标拿不到 ⇒ 变慢也无法归因，先别开 |

三条全满足才对拍；**任何一条不满足，保持默认 `0`**。

实测（16GB + 35B-A3B + 34 层 CPU 专家）：8K 上下文下 256/512/1024 MiB 缓存让解码 **下降 31%–41%**；
262K 上下文连 256 MiB 都放不进去（余量只剩 204 MiB）。

---

## 5. 交错 A/B 测速协议（想改参数时照做）

1. **固定一切**：同一模型、同一 ctx、同一 batch/ubatch、同一 KV、同一线程与 CPU range、同一 seed。
2. **交错顺序**，不要"先测 A 再测 B 各 10 次"：`A,B | B,A | A,B`，至少 3 对。
3. 每组**丢弃首个请求**（冷启动、页面未热），取后 2 个稳态样本。
4. **记录四个数**：服务端 `predicted_per_second`、`prompt_per_second`、`draft acceptance`、最低空闲显存。
5. 只在**两版都完成**后比较；`finish_reason=length` 的样本只能比吞吐，不能比质量。
6. ⚠️ 客户端墙钟包含轮询/HTTP 开销，**不要当端到端延迟**；要延迟就看服务端 `prompt eval time`。

### 5.1 必须先排除的三个混淆

| 混淆 | 现象 | 处理 |
|---|---|---|
| MTP 接受率随配置变 | 换 `n-cpu-moe` 后接受率 0.486→0.532，速度跟着变 | 把接受率一起记录，别把"接受率变了"当成"kernel 变快了" |
| 上下文长度 | 短 prompt 56 t/s、长上下文 68–77 t/s，同一模型 | 结论必须绑定 ctx 与负载形态 |
| 生成长度不同 | 新版多思考几十 token，整段耗时更长 | 比较 decode t/s，不要只比总时长 |

---

## 6. 验收协议（升级后 3 条 + 回滚条件）

| # | 检查 | 期望 |
|---|---|---|
| 1 | `curl http://127.0.0.1:<port>/health` | `{"status":"ok"}` |
| 2 | 一次小请求（如 `max_tokens 2048`，要求输出 `FINAL: <n>`） | 有**可见**答案且正确 |
| 3 | 一次 ~12K 上下文请求 | prefill 与升级前同量级（本机参考 1600–1700 t/s），答案正确 |
| 4 | 观察 1–2 天真实 Agent 回合 | 无空答案、无 OOM、无退化 |

**回滚条件**（任一即回滚整套备份）：可见答案变空/被思考吃掉、prefill 掉 >15%、启动日志出现新的警告、
显存余量比升级前低 >500 MiB、出现 CUDA error / 系统级不稳定。

---

## 7. 陷阱清单（本专题踩过的）

| 陷阱 | 真相 |
|---|---|
| ini 里写 `parallel = 3`，以为生效 | **Router 用 CLI 覆盖 preset** ⇒ `-np 1` 时就是 1 槽；要用 `router_args_probe.ps1` 看渲染结果 |
| 把「34 层 + 3 槽」当生产配置测 | 这条组合在 Router（34/1 槽）与菜单（37/3 槽）里都不存在，测出来的越界是无意义的混合体 |
| 用短 prompt 判断"模型变慢了" | 短 prompt 的 MTP 接受率低（~0.49），长上下文反而 68–77 t/s |
| 看到"2.2 倍"就想加缓存 | 前提是显存能空出十几 GiB；16GB 卡上不成立 |
| 以为 `--fit on` 能兜底 | 它只报判决；救命要靠自己的余量预算 |
| 只看总耗时判断版本 | 生成长度不同会污染结论，要看 decode t/s + 接受率 |
| 升级时顺带改缓存/并发/层数 | 一次只动一个变量，否则无法归因、无法回滚 |
| 把客户端墙钟当首字延迟 | 用服务端 `prompt eval time` |

---

## 8. 参考实现

| 脚本 | 用途 | 示例（占位符） |
|---|---|---|
| [`../../scripts/moe_bench.ps1`](../../scripts/moe_bench.ps1) | 按生产参数起隔离实例 → 发固定负载 → 记录 t/s、接受率、显存/内存低谷、fit 判决 | `.\moe_bench.ps1 -LlamaDir <llama-cpp-dir> -Model <model.gguf> -Mmproj <mmproj.gguf> -Context 262144 -CpuExperts 34 -Fit -Mode short` |
| [`../../scripts/router_args_probe.ps1`](../../scripts/router_args_probe.ps1) | 从运行中的 Router 反查**实际生效**的子进程参数（自动脱敏 api key） | `.\router_args_probe.ps1 -Url http://127.0.0.1:8082 -ApiKey <key>` |

`moe_bench.ps1` 内置护栏：启动前要求空闲显存 ≥ `-MinFreeGpuStartMiB`、可用内存 ≥ `-MinFreeRamStartMiB`、
提交余量 ≥ 46 GiB；运行中低于 `-GpuFloorMiB`（默认 3072）或内存/提交 < 4096 MiB 立即终止**本次测试进程**。
把它调低（例如 2048）时，请在结论里**明示**这一偏离——生产本身可能就跑在 2.1–2.3 GiB 余量上。
