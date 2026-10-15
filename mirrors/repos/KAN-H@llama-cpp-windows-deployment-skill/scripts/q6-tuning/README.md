# q6-tuning — Qwen3.8-27B-GSQ-RCO 调优探针集

2026-10-12 Q6 批次（Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp，qwen35 dense 27B，RTX 5060 Ti 16 GiB）的测量工具链：
Phase 0 元数据 → Phase 2 单配置探针 → 长 agent 稳定性 → Phase 3 回写 → 回归闸门。

纯标准库（Python 3.7+），**不含任何本机路径** —— 靠下面的环境变量定位。

```
_q6_metadata.py          Phase 0：GGUF 元数据基线（MTP head / 几何 / 布局完整性）
_q6_probe.py             Phase 2 主力：单配置端到端测量 → _q6_results.json
_q6_multiturn.py         长 agent 代理：3 轮同 slot（前缀缓存 + decode 稳定性）
_q6_apply.py             Phase 3：测量值 → 注册表 / preset-overrides（--check / --go）
_refactor2_body_probe.py cmd.exe 实收 argv vs 文件书写 argv（FND-014 的回归闸门）
_refactor2_regression.py Phase 1 不变量 A–E + --strict / --self-test
```

---

## 1. 环境变量（六脚本共用同一解析链）

| 变量 | 含义 | 解析顺序 |
|---|---|---|
| `LLAMA_DIR` | **llama.cpp 部署目录**（`llama-server.exe`、`logs/`） | 环境变量 → 脚本上一级（默认；即脚本位于 `<llama-cpp-dir>\plan\` 的旧布局） |
| `LAUNCHER_DIR` | **launcher 数据目录**（`launcher-models.json`、`preset-overrides.json`、`backup/`） | 环境变量 → `<LLAMA_DIR>\launcher` |
| `CHAT_DIR` | **模型根目录** | 环境变量 → 注册表 `launcher-models.json` 里记的 `chat_dir` → 占位符 `<models-dir>` + 报错提示 |
| `LLAMA_API_KEY` | 探针请求用的 key | 环境变量 → `sk-local-001` |

```powershell
$env:LLAMA_DIR = '<llama-cpp-dir>'
$env:CHAT_DIR  = '<models-dir>'
python _q6_probe.py --dry --mtp --tag dry
```

> 不设任何环境变量时：脚本放在 `<llama-cpp-dir>\plan\` 内即可按旧行为运行；
> 放在别处（如技能仓 `scripts/q6-tuning/`）时给 `LLAMA_DIR`。
> 模型根优先 `CHAT_DIR`，否则读注册表记住的值 —— **全新机器上没有注册表就必须给 `CHAT_DIR`**。

---

## 2. 脚本说明

### `_q6_metadata.py` — Phase 0（零 GPU 消耗）
回答三个"上卡之前"的问题：MTP head 是否真的在（`nextn_predict_layers` KV + `blk.<N>.*` 张量）、
几何参数是什么（`block_count` / `head_count_kv` / KV 长度 / sliding window）、文件布局是否完好
（张量表字节和 vs `文件大小 − data_offset`）。布局校验是嫁接时代的最早告警信号：
**解析成功不等于布局正确**（偏移错的文件照样解析），先查它、最信它。
另输出逐层字节曲线 + 逐张量量型直方图（GSQ-RCO 的量型是逐张量分配的，"IQ3_S" 只是预算标签）。

```powershell
python _q6_metadata.py [model_dir]     # 默认 <chat root>/Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp
```
产物：`_q6_metadata.json`（写在脚本旁；仓库收录副本见 §4）。

### `_q6_probe.py` — Phase 2 主力（需要 GPU）
单配置端到端，顺序：GPU 忙则拒绝运行 → 以 LIST argv 启动（不经 shell 引号）→ 等 `/health`（同时盯进程早死）
→ 1-token 暖机 → 真实解码测量 → 读 VRAM、解析日志（draft 接受率 / 层拆分 / `n_ctx_slot` / 警告）→ 写日志 + JSON 记录
→ 关服并等 VRAM 回落。

测量约定（各测臂一致，保证可比）：decode t/s 取服务端 `predicted_per_second`；提示词为固定英文段落、温度 0；
首请求做暖机不计入；VRAM 取测量请求刚结束时的 `nvidia-smi memory.used`。

```powershell
python _q6_probe.py --smoke --mtp --tag mtp-smoke        # 冒烟（见 §5 BSOD 警告）
python _q6_probe.py --ctx 141312 --mtp --tag a1-141k     # 正式测量
python _q6_probe.py --dry --mtp --tag dry1               # 只打印 argv 不启动
```
常用参数：`--tag`（必填，命名日志 + JSON 记录）、`--ctx`、`--ngl`、`--kv-k/--kv-v`、`--batch/--ub`、
`--mtp`、`--mmproj`、`--spec-n-max`、`--prompt-file`、`--long-extra`、`--load-mode`、`--n-predict`、`--threads`。
产物：日志进 `<LLAMA_DIR>\logs\`；测量记录**追加**进 `_q6_results.json`（脚本旁）。

### `_q6_multiturn.py` — 长 agent 稳定性（需要 GPU）
一次加载、同一 slot 三连问：45K 铺底 + "总结" → 追加 "展开中段" → 追加 "一句英文总结"。
验证：第 2/3 轮**前缀缓存复用**（`n_prompt_tokens_cache` 接近上轮总量、prefill 缩到增量）、
decode 稳定性（45K→46K 上下文）、日志**不得**出现 `forcing full prompt re-processing`
（#30357：Gated DeltaNet 状态无法回滚，任何偏离 = 全文重预填）。

```powershell
python _q6_multiturn.py [--ctx 141312] [--ngl 64] [--mtp] [--nmax 3] [--threads 12]
```
前置：铺底文本 `<LLAMA_DIR>\logs\q6-long56k.txt` 必须已存在。

### `_q6_apply.py` — Phase 3 回写（--check / --go 二选一必填）
把测量得到的最终参数写回 launcher 生态：
1. `launcher-models.json`：补发 `AUTO_QWEN3_8_27B_GSQ_RCO__MM` 变量（FND-070）；
2. 重写 Q6 纯文本 Agent 块为实测值（含 `no_mmproj` 标记）；3. 紧随其后插入 Q6 视觉块（同目录 + mmproj）；
4. `preset-overrides.json`：Q6 params/tuning。

两次写入前都会把原文件备份进 `launcher/backup/`。

```powershell
python _q6_apply.py --check      # 只说将改什么
python _q6_apply.py --go         # 真写；随后按提示跑生成器渲染：
python launcher\update_launchers.py --yes
```
> `--go` 后**不要**用 `update-launchers.bat`（末尾 `pause` 会卡住自动化）。

测量数据来源（自动按序找）：脚本旁 → `<LLAMA_DIR>\plan\` → 技能仓 `references/sessions\`。

### `_refactor2_body_probe.py` — 启动块存活验证
从生成的启动器里抽出每个 `:RUN_*` 块，把 `llama-server.exe` 换成 argv 回显桩，用 cmd.exe 实跑，
对比**实际收到**的 argv 与**文件里书写**的 argv。这是能抓住 FND-014 的回归
（`^` 续行里出现空行 → cmd.exe 静默丢弃其后全部参数）。

```powershell
python _refactor2_body_probe.py                    # 默认 --dir = LAUNCHER_DIR / <llama-cpp-dir>\launcher
python _refactor2_body_probe.py --dir <备份副本>    # 反向对照（应 FAIL）
```
退出码 0 = 全部块存活，1 = 有块丢参。

### `_refactor2_regression.py` — Phase 1 不变量闸门
A：续行内无空行（FND-014）；B：`goto` 标签唯一；C：启动体必带 `--port`/`--api-key`；
D（`--strict`）：`models-config.bat` 的 `--models-max` 恰好一次；
E：MoE/`--fit` 历史回归（FND-064 `--n-cpu-moe` 与 overrides 不符、FND-066 `--fit`+`--n-cpu-moe`、FND-033 显式 `-ngl`、FND-063 `-fittarget`、TASK-080 `--no-mmap`）。

```powershell
python _refactor2_regression.py            # 常规
python _refactor2_regression.py --strict   # 提交前（含 D 组 + 共享 key 动态校验）
python _refactor2_regression.py --self-test  # 自证：E 组检查在故意破坏的样本上必须失败
```

---

## 3. 典型流程（Q6 批次实测顺序）

```powershell
python _q6_metadata.py                                   # 0) 元数据基线（无 GPU）
python _q6_probe.py --smoke --mtp --tag mtp-smoke        # 1) 冒烟优先
python _q6_probe.py --ctx 141312 --mtp --tag <tag>       # 2) 阶梯测量（逐臂追加记录）
python _q6_multiturn.py --ngl 64 --mtp                   # 3) 长 agent 稳定性
python _q6_apply.py --check                              # 4) 回写（先 check）
python _q6_apply.py --go                                 #    → 再生成器渲染
python _refactor2_body_probe.py                          # 5) 提交前闸门
python _refactor2_regression.py --strict
```

## 4. 产物与收录

| 产物 | 位置 | 说明 |
|---|---|---|
| `_q6_metadata.json` | 脚本旁；仓库收录 `references/sessions/`（已脱敏） | GGUF 元数据基线 |
| `_q6_results.json` | 脚本旁 → `<LLAMA_DIR>\plan\` → 仓库 `references/sessions/` | probe 逐臂追加；仓库收录副本 18 条 |
| 服务器日志 | `<LLAMA_DIR>\logs\` | probe / multiturn 原始日志 |
| 注册表 / overrides | `<LAUNCHER_DIR>\launcher-models.json` 等 | `--go` 写入；写前备份在 `backup/` |

## 5. 注意事项（踩过的坑）

- ⚠️ **先 `--smoke` 再放大**：#30302（GSQ-RCO + draft-mtp + Windows CUDA）有蓝屏报告；
  冒烟用小 `--ctx` / 小 `--n-predict`，活着再逐级放大。
- ⚠️ **`_q6_apply.py --check` 的 `[check]` 行是静态日志**（无条件打印"将会做的编辑"），
  **不是漂移信号** —— 判断漂移看生成物实际内容或跑 `update_launchers.py --check`。
- ⚠️ probe 在 **GPU 忙时拒绝运行**（混测的数字比没有数字更糟）。
- ⚠️ `--strict` 含 `models-config.bat` 共享 key 断言：**改完启动器先跑它**
  （曾抓到 key 从 `-001` 被回退成 `-abc` 的回归）。
- `_q6_probe.py --dry` 也会做"模型是否存在"检查；缺 `CHAT_DIR` 且无注册表时会给出 `<models-dir>` 提示而非崩溃。

## 6. 血缘

本批脚本产自 2026-10-12 Q6 调优批次（实验现场 `<llama-cpp-dir>\plan\`），是技能
"带探针的调优方法"的完整实例。完整叙事见
[references/guides/qwen38-gsqrco-27b-tuning.md](../../references/guides/qwen38-gsqrco-27b-tuning.md) 与
[references/sessions/20261012-qwen38-gsqrco-27b-tuning-report.md](../../references/sessions/20261012-qwen38-gsqrco-27b-tuning-report.md)。
