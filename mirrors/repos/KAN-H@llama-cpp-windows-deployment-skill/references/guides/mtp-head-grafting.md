# 内建 MTP head 嫁接手册（GGUF 张量级手术）

> **适用**: 想给一个**没有 MTP head 的微调模型**（尤其社区无审查微调）加上投机解码能力，
> 而官方同基座量化版**自带 head**。
> **实测结果**: 解码 **64.28 → 86.51 t/s（+34.6%）**，acceptance **0.736**（16 GiB 卡，Qwen3.6-35B-A3B 系）
> **首次验证**: 2026-09-13 | llama.cpp build 10713 | 参考实现 [`../../scripts/mtp_graft.py`](../../scripts/mtp_graft.py)

---

## 0. 先理解：这是 **merge**，不是 adapter

| 形态 | 依赖关系 |
|---|---|
| LoRA / 适配器 | ❌ 依赖基座，自己不能跑 |
| 外挂 draft GGUF（`--model-draft`） | ❌ 依赖主模型 |
| **本手册的嫁接** | ✅ **零依赖的完整独立文件** |

嫁接产物 = **原模型全部权重逐字节复制** + **追加 20 个 head 张量**。
删掉原模型，嫁接版照常运行；两者完全平级、互不引用。

> ⚠️ **执行前必须先讲清三件事**，否则用户会以为你在无意义地拷 22 GB：
> ① 产物是什么（同一个东西 + 补丁）② 是否互相依赖 ③ 删掉原文件会怎样。
> **mmproj 是独立附件**：靠 `--mmproj` 传参，不被任何 gguf 包含，可被多个模型共用。

---

## 1. 适用判定（3 分钟，零成本）

```python
import update_launchers as U
meta = U.read_gguf_meta("<donor.gguf>")
t    = U.read_gguf_tensors("<donor.gguf>")
print(meta["arch"], meta["layers"], t["n_tensors"])
print([i for i in t["layer_ids"] if i >= meta["layers"] - 1])   # head 所在层
```

| 看什么 | 期望 |
|---|---|
| `arch`（donor 与 target） | **必须相同**（如都是 `qwen35moe`） |
| `block_count` | donor **比 target 多 1**（多出的那层就是 head） |
| `layer_ids` 的最大值 | donor = `block_count-1`（如 `blk.40`），target 止于 `block_count-1` |
| head 张量数 | Qwen3.6 系 = **恰好 20 个** |
| target 是否已有 head 张量 | **必须为 0**，否则拒绝（防重复添加） |

**head 长什么样**（Qwen3.6-35B-A3B 实例）：`blk.40.nextn.eh_proj` / `nextn.enorm` /
`nextn.hnorm` / `nextn.shared_head_norm` + 一整套 attn 块 + FFN（含 MoE 专家）。
看到 `nextn.*` 就是它。

---

## 2. GGUF 布局与必须改的 4 处

```
[header 24B][KV 区][张量表][pad ≤31B][数据区 = 21.82 GiB]
```

| # | 改动 | 说明 |
|---|---|---|
| 1 | `qwen35moe.block_count` **40 → 41** | **原地改**，u32 宽度不变 ⇒ KV 区长度不变 |
| 2 | **追加** `qwen35moe.nextn_predict_layers = 1` | ★ **见 §3.3，最关键** |
| 3 | 张量表 **+20 条** | 数据区整体后移，但 GGUF 的 tensor offset **相对数据区起点**，不是相对文件 |
| 4 | 数据区 **追加** head 字节 | **现有张量数据逐字节原样复制，offset 一个都不动** |

> **关键安全性质**：offset 是相对数据区起点的 ⇒ 数据区平移不影响任何现有张量。
> 这也是为什么必须**整份重写**（张量表变长 ⇒ 数据区起点变）——
> 数据区前面只剩 ≤31 字节对齐空隙，塞不下 1.2 KB 的张量表。

---

## 3. 四个会咬人的地方

### 3.1 KV 必须取 **TARGET** 的，不是 donor 的

| 模型 | `n_kv` |
|---|---:|
| donor（UD 量化版） | **55** |
| target（社区微调） | **45** |

**症状**：产物比预期大 0.495 GiB，`read_gguf_tensors()` 返回 `{}`（张量表解析全崩）。
**根因**：写了 donor 的 KV 字节，却在 header 填了 target 的 `n_kv` ⇒ 解析器**少读 10 条 KV**
就转去读张量表 ⇒ 之后全部错位。
**修复**：KV 取 target 的 —— **目标的 tokenizer / chat template / 命名才该活下来**。

> ⚠️ donor 独有而**不该搬**的键：`license` / `base_model.*` / `quantized_by` / `tags`（出处信息），
> 以及 `tokenizer.ggml.add_bos_token`（**那是目标自己的分词配置，改了会改变分词行为**）。

### 3.2 对齐填充不能写成"整个 head 区域的长度"

**症状**：修好 KV 后仍大 **0.99 GiB**（≈ head 的 2 倍），但**张量表解析完全正常**。
**根因**：把 `cursor - existing_data_len`（**整个 head 区域长度**）当成了对齐填充
⇒ 0.49 GiB 零字节插在 head 数据**前面** ⇒ **每个 head 张量的实际位置比记录的偏移晚 0.98 GiB**，全部指向填充区。
**修复**：只填到**下一个对齐边界**：

```python
w.write(b"\x00" * (align(existing_data_len, alignment) - existing_data_len))   # ≤31 字节
```

### 3.3 ★★★ `nextn_predict_layers` —— 社区帖子没写的那个开关

> 社区实测帖（[#28363](https://github.com/ggml-org/llama.cpp/discussions/28363)）只说
> 「`block_count` 必须改写 40→41」。**它没提这个键。**

对比两边 KV 键集发现：**`qwen35moe.nextn_predict_layers = 1` 只存在于 donor。**

它是告诉加载器**「多出来的那一层是 NextN/MTP head 而不是普通层」**的开关。

| | 有它 | 没它 |
|---|---|---|
| 模型加载 | ✅ | ✅ **照样成功** |
| 20 个张量 | 生效 | **死重量** |
| 投机解码 | ✅ +34.6% | ❌ **永远不触发，且不报错** |

**⇒ 没有它，就是一个 22 GiB 的成功 vs 一个 22 GiB 的空转。**

实现：追加一条 u32 键值，并把 header 的 `n_kv` +1。

```python
def enc_kv_u32(key, val):                      # GGUF type 4 = UINT32
    b = key.encode("utf-8")
    return struct.pack("<Q", len(b)) + b + struct.pack("<I", 4) + struct.pack("<I", val)

kv_raw += enc_kv_u32("qwen35moe.nextn_predict_layers", 1)   # donor 的值
n_kv_out = target.n_kv + 1
```

**若 donor 里没有这个键 → 直接报错退出，不要猜。**

### 3.4 ★★★★ 「能解析」≠「正确」—— 写入器必须自带写后自检

第二个产物：`block_count=41` ✓、`nextn_predict_layers=1` ✓、张量表 **753 条全解析** ✓、
`blk.40` 全在 ✓ —— **每一项检查都过**，但 head 张量指向的是**零字节**。

**唯一抓到它的是文件大小交叉校验**：

```python
v = U.read_gguf_tensors(str(out))          # 把全部张量字节求和，与真实文件长度比对
if not v or not v.get("size_ok"):
    print("[X] SELF-CHECK FAILED - 不要使用，删掉重跑"); return 1
```

它验的**不是**"能不能读"，而是"**所有偏移加起来是否等于文件长度**"。

> **★ 通用铁律：「实际大小 ≠ 预期大小」是布局出错的第一个信号**，比任何解析结果都更早、更可靠。
> 两次都靠它定位：第一次 +0.495 GiB（KV 错位），第二次 +0.99 GiB（填充错位）。

---

## 4. 验证协议（缺一不可）

| # | 检查 | 通过标准 |
|---|---|---|
| 1 | **产物大小 vs 预期** | 差 < 4 KB（仅对齐填充） |
| 2 | `n_kv` | `target.n_kv + 1` |
| 3 | `block_count` | 41 |
| 4 | `nextn_predict_layers` | **1** |
| 5 | **张量表交叉校验** | **delta 0.0000%，`size_ok=True`** ← 唯一能验"所有偏移都对"的检查 |
| 6 | **加载日志的 `max blk.N`** | 应为 40（多出来的 block 真的建起来了） |
| 7 | **`acceptance` 计数器** | **非 null 且 > 0.3** |

> ⚠️ 第 7 项是**铁证**：接受率接近 0 或 null 意味着 head 在跑但预测不出有用的东西 ——
> 那是**嫁接做坏了**的签名，而不是想法不对。
> 第 6 项对第 5 项是补充：文件可以解析完美却指向错的字节（见 §3.4）。

**A/B 必须同会话实测**，不能拿社区绝对值比：

```powershell
# arm A 基线 / arm B 投机
llama-server -m <grafted.gguf> ... --spec-type draft-mtp --spec-draft-n-max 2
```

---

## 5. ★ 显存代价 = 权重字节的 **3 倍**

| | 值 |
|---|---|
| head 权重字节 | **0.49 GiB** |
| **实测 MTP 路径总开销** | **1,652 MiB** |

漏算的三块：
1. **`blk.40` 的专家张量不被 `--n-cpu-moe` 覆盖**（该参数只作用于 `blk.0..N-1`，而 N < 40）⇒ 留在 GPU
2. draft 路径**自己的 KV cache**
3. draft 的 **compute buffer + CUDA graph**

**⇒ 决不允许按文件大小估算嫁接开销。** 实测值：
- n=27：VRAM 11,872 → **13,524 MiB**，余量 4,439 → **2,787 MiB**
- 每升 1 层 `n-cpu-moe` 释放 ~518 MiB ⇒ **n=28 恢复 3 GB 判据**（~3,305 MiB）

---

## 6. 落地：新开目录，不要塞进同一个模型目录

模型扫描器**每个目录只暴露一个主 gguf**（取第一个）。同一目录放两个主 gguf
⇒ **扫描器会静默选一个**。

```
<models-dir>/<原模型目录>/            ← 保持不动
<models-dir>/<新目录>/                ← 嫁接版
    <新名字>.gguf
    <mmproj>.gguf                     ← 必须【复制】一份进来
```

⚠️ **mmproj 必须复制到新目录**：扫描器只在模型目录**内**找它，否则新条目会丢掉识图能力。

⚠️ **文件名要带量化分隔符**（如 `-Q4_K_P.gguf`），否则量化识别失败，
菜单标签出现 `?`、配置分区名退化成文件名。

---

## 7. 参考实现

**权威实现已在项目内：`scripts/mtp_graft.py`** —— 纯标准库、单文件、可直接运行
（实测：只带一个 Python 3.8+ 即可工作，**无任何外部模块依赖**）。

> 此前这里是「实现位于 `<llama-cpp-dir>\plan\_mtp_graft.py`（纯标准库，可独立运行）」。
> **那句话是错的** —— 该脚本 `import update_launchers as U`（用了它的 `GGML_TYPE_BYTES`
> 与 `read_gguf_tensors`），脱离 `<llama-cpp-dir>\launcher\` 就 `ModuleNotFoundError`。
> 两个符号现已**内联**进 `scripts/mtp_graft.py`，它才真正可独立运行。

- `--check`（默认）：只读，报告 head 张量清单与字节数、磁盘空间、**结构性兼容性结论**
- `--go --out <path>`：写入 + **写后自检**；必须带 `--out`，且**拒绝覆盖已存在的输出**
- `--audit`：只打印目标模型里所有 per-layer KV 数组（见下）
- `--donor/--target` 直接给文件；或 `--preset qwen36-35b-a3b --models-dir <models-dir>`
- `--json` 机器可读摘要 ｜ `--check`/`--go`/`--audit` 互斥

### 兼容性是一道闸门，不是一份报告

任一条不满足即**拒绝写入**（退出码 1，什么都不落盘，无需清理）。

**结构性（硬性，全部由两份文件当场推导）**

| # | 条件 |
|---:|---|
| 1 | 两份都是可解析的 GGUF v2/v3 |
| 2 | `general.architecture` 一致 |
| 3 | `block_count(donor) == block_count(target) + nextn` |
| 4 | target 的**每一个**张量都在 donor 中，且 **dims 完全一致** |
| 5 | donor 多出的张量**恰好**是 head 块区间内的那些 |
| 6 | target **不得**已自带 head（含已声明 `nextn_predict_layers`） |
| 7 | donor **必须**声明可用的 `nextn_predict_layers` —— 缺了就拒，不猜 |
| 8 | `block_count` 是 **u32**（否则不能原地改写） |
| 9 | head 块区间内**确实有张量** |
| 10 | head 的每个量化类型都在尺寸表内（否则无法算布局） |
| 11 | **per-layer 数组 KV 不会失配**（见下） |
| 12 | 磁盘空间足够 |

**架构建议层（来自上游调研，2026-09）**

- 头张量**会被加载但永不执行**的架构（`glm4` `exaone4` `exaone_moe` `bailingmoe2` `dots3note`）
  ⇒ **只警告，不拒绝** —— 上游名单在变，用过期表拒绝会挡掉本来可用的嫁接
- `granite-switch` **复用** `n_layer_nextn` 作 router 层 ⇒ **拒绝**（写它是语义污染）
- `gemma4-assistant` 的头在 `blk.N.*` **之外**（顶层 `nextn.pre_projection`）⇒ **拒绝**（本写入器搬不动）
- 多块头用在**断言单块**的架构上 ⇒ **拒绝**（加载会 `GGML_ASSERT`）

> ⚠️ **量化类型差异不是拒绝条件。** 同一基座的两种量化配方（如 `UD-Q4_K_XL` vs `Q4_K_P`）
> 本来就对不同张量用不同类型；GGUF 每张量自带类型，嫁接不受影响 —— 只作为提示输出。
> （第一版把这个当硬条件，**误拒了已知可用的真实组合**：381/733 个张量类型不同但 shape 全一致。）

### ★ 头必须按 **block index 区间** 识别，不能按名字

`bailingmoe3` 的头张量用**普通后缀**命名（`blk.%d.layer_out_norm`），名字里根本没有 `nextn`。
按名字过滤会漏掉这个架构。区间算法是纯算术：头 = `[block_count - nextn, block_count)`。

### ★ per-layer 数组 KV 陷阱

加块会让任何「长度恰好等于 `block_count`」的 KV 数组与新层数不一致：有的加载器按下标访问会越界，
有的会静默用到错误的条目。**写之前必须审计**，`--audit` 会列出全部候选：

```
python scripts/mtp_graft.py --audit --donor <head.gguf> --target <base.gguf>
```

已知会按层索引的键（不限于此 —— 工具还会按「长度恰好等于 `block_count`」兜底发现）：
`compress_ratios` / `shared_kv_layers` / `recurrent_layers` / `deepstack_layers` / `layer_types`。

### 等价性已实测

用本工具对 2026-09-13 那次嫁接的**同一对模型**重跑，产物与原工具**SHA-256 完全相同**
（22.31 GiB，`5AF97A49…72D272`）。即改写是**保真等价**，不是「看起来能用」。

**磁盘**：need ≈ 原模型 + head 字节（实例：22.37 GiB）。
**可逆**：原模型不动，产物直接删即可。
