# references 快速索引

> **用途**：本目录是技能的**经验库**。日常只需读 `SKILL.md`；当 SKILL.md 指向某份专题文档、
> 或需要追溯某个结论的**实测证据**时，从这里进入。
> **本文件是路径的唯一权威来源** —— 历史文档里写的旧路径，以本表为准。

---

## 1. 目录结构

```
references/
├── INDEX.md          ← 本文件（快速索引 + 权威路径表）
├── sessions/         按日期的会话经验（历史快照，不回改正文）
├── guides/           专题手册（面向未来操作，随实践更新）
└── assets/           可直接复用的脚本与配置模板
```

**三类文档的区别**：

| 目录 | 性质 | 可否修改正文 |
|---|---|---|
| `sessions/` | **历史快照** —— 当时的结论与当时的路径 | ❌ 不回改（改了就不是证据了）。路径以 §5 对照表为准 |
| `guides/` | **操作手册** —— 照着做 | ✅ 随实践更新，路径必须保持当前有效 |
| `assets/` | **可运行资源** —— 复制出去就能用 | ✅ 但需保持脱敏 |

---

## 2. 会话经验（`sessions/`）

> 命名约定：`YYYYMMDD-session-experience.md`

| 文档 | 主题 | 最有价值的一条 | 什么时候读 |
|---|---|---|---|
| [`20260803`](./sessions/20260803-session-experience.md) | Qwen3.6-27B 64K 调优、CPU 工具调用、11/11 工具矩阵、BAT 编码 | 工具调用 11/11 全通过的参数基线 | 搭工具调用、遇脚本乱码 |
| [`20260805`](./sessions/20260805-session-experience.md) | 推理失控（防死循环）与 GBK 安全编辑 | **推理参数改动前必查**「防死循环配置」 | 模型思考停不下来、脚本被编辑器改坏 |
| [`20260806`](./sessions/20260806-session-experience.md) | 26B MTP draft：官方 Q8_0 vs 第三方 Q4_0 定案 | **`llama-cli` 能加载 ≠ `llama-server` 能加载** | 判定 MTP 草稿真伪 |
| [`20260816`](./sessions/20260816-session-experience.md) | `--fit` 自动分层（7 倍提速）、新 CPU 模型、GBK 恢复 SOP | 51K 上下文 10.6 → 72-93 t/s 的完整证据链 | 长上下文降速 |
| [`20260829`](./sessions/20260829-session-experience.md) | Qwen3.8-27B 极限优化、更新器工程修复、WSL/VS Code 对接 | `ECONNREFUSED` 双根因排查 SOP | 配长上下文、VS Code 连不上 |
| [`20260913`](./sessions/20260913-session-experience.md) | MoE 参数智能化、回归方法论、MTP 嫁接 | **新守卫必须先在已知可用样本上跑**（否则守卫自己成为 bug） | 加模型、写断言、做嫁接 |

---

## 3. 专题手册（`guides/`）

| 文档 | 解决什么 | 关键结论 |
|---|---|---|
| [`mtp-head-grafting.md`](./guides/mtp-head-grafting.md) | 给**没有 MTP head 的微调模型**嫁接官方 head | 实测 **+34.6% 解码**（64.28 → 86.51 t/s，acceptance 0.736）；四个陷阱；**显存代价 = 权重字节 × 3** |
| [`20260913-moe-offload-community-research.md`](./guides/20260913-moe-offload-community-research.md) | MoE 卸载的**社区现状**调研 | 社区**无最优共识、无可用自动脚本**；但有两个可直接抄的杠杆（`-ub 2048`、`--load-mode none`） |

---

## 4. 可复用资源（`assets/`）

### 启动器模板

| 文件 | 对应仓库中的真实启动器 |
|---|---|
| [`gemma4-menu-scripts.bat`](./assets/gemma4-menu-scripts.bat) | `launcher/start-Gemma4-Launcher.bat`（10 项菜单） |
| [`qwen-scripts.bat`](./assets/qwen-scripts.bat) | `launcher/start-Qwen-Launcher.bat`（裸跑 / 外挂 draft / 内置 MTP 三档） |
| [`start-CPU-Toolcall-Launcher.bat`](./assets/start-CPU-Toolcall-Launcher.bat) | 同名（纯 CPU 工具调用，`-ngl 0`，128K ctx） |
| [`router-mode-preset.bat`](./assets/router-mode-preset.bat) | Router Mode `--models-preset` 变体（按模型覆盖参数） |
| [`router-mode-simple.bat`](./assets/router-mode-simple.bat) | Router Mode `--models-dir` 简版 |

> ⚠️ 这些是**脱敏模板**，路径写的是 `C:\llama.cpp` / `C:\models\chat` 占位值。
> 它们与仓库里 `launcher/` 下的真实脚本**不是同一文件**（真实脚本含本机特化内容），
> 只在"从零搭一套"时作为起点使用。

### 配置模板

| 文件 | 说明 |
|---|---|
| [`model-profiles.json`](./assets/model-profiles.json) | 模型参数知识库快照 —— **18 个 profile**，其中 **3 个含结构化 `moe` 块**（`gemma4-26b-a4b-qat` / `gemma4-26b-a4b` / `qwen36-35b-a3b`）。字段含 `expert_bytes_per_layer_mib` / `per_layer_spread_pct` / `vram_budget_16gb` |
| [`preset-templates.json`](./assets/preset-templates.json) | 7 种部署场景的 preset 模板 |

> `model-profiles.json` 的**权威版本在项目仓库** `<llama-cpp-dir>\launcher\model-profiles.json`；
> 本目录是快照。快照与仓库不一致时以仓库为准，并按下文 §7 重新快照。

---

## 5. ⚠️ 代码文件索引（**权威路径表**）

> 本表路径**已逐条实测校验**（2026-09-13）。
> 历史文档（`sessions/`）里若出现下表"旧路径"列的写法，**一律以"当前路径"列为准**。

### 5.1 入口与核心

| 当前路径 | 旧路径 / 常见误写 | 说明 |
|---|---|---|
| `llama-hub.bat` | — | **在仓库根**（不在 `launcher/`）。交互菜单入口 |
| `launcher/update-launchers.bat` | `update-launchers.bat` | 生成器入口（纯 ASCII） |
| `launcher/update_launchers.py` | `update_launchers.py` | 生成器主体（Python 3.11，纯标准库） |
| `launcher/llama_hub.py` | `llama_hub.py` | 菜单 / `--guide` / `--audit` / 参数编辑器 |

### 5.2 数据与配置

| 当前路径 | 旧路径 | 说明 |
|---|---|---|
| `launcher/launcher-models.json` | `launcher-models.json` | 启动器注册表（`<llama-cpp-dir>/launcher-models.json` 已不存在） |
| `launcher/model-profiles.json` | `model-profiles.json` | 模型参数知识库（含 `moe` 块） |
| `launcher/preset-overrides.json` | — | **唯一事实源**：per-model 参数与 `tuning` 实测记录 |
| `launcher/draft-health.json` | — | MTP 草稿实测结论 |
| `launcher/draft-blacklist.json` | — | 草稿黑名单 |
| `launcher/.llama-server-keys.json` | — | 服务 key 存取（**不要外传**） |
| `<models-dir>/models-config.ini` | `models-config.ini` | Router preset **生成物** —— **不在仓库内**，由生成器写出 |

### 5.3 启动器（生成物）

| 当前路径 | 旧路径 |
|---|---|
| `launcher/start-Gemma4-Launcher.bat` | `start-Gemma4-Launcher.bat` |
| `launcher/start-Qwen-Launcher.bat` | `start-Qwen-Launcher.bat` |
| `launcher/start-CPU-Toolcall-Launcher.bat` | `start-CPU-Toolcall-Launcher.bat` |
| `launcher/start-embedding.bat` | — |
| `launcher/models-config.bat` | — |
| `launcher/legacy/*.bat` | `generate_ini.bat`（**已归档/不存在**，见 §6） |

### 5.4 文档与基线

| 当前路径 | 说明 |
|---|---|
| `launcher/docs/MODELS.md` | 模型清单（含「MoE 卸载」列） |
| `launcher/docs/脚本使用注意.txt` | GBK 无 BOM，操作注意事项 |
| `launcher/backup/phase1-baseline.json` | Phase 1 基线哈希 |
| `plan/refactor-launcher-ecosystem-{1,2,3}.md` | 改造方案与执行记录（**3 是最新**） |

### 5.5 探针脚本（`plan/_*.py`）

> 计划文档里每个数字都由这些脚本产出。**它们是可复现性的来源，不要删。**
> 测量输出（`plan/_*.json`、`plan/_*.png`）已 gitignore。

| 脚本 | 用途 |
|---|---|
| `plan/_mtp_graft.py` | MTP head 嫁接（`--check` / `--go --out`） |
| `plan/_mtp_verify.py` | 嫁接 A/B 验证（baseline vs `--spec-type draft-mtp`） |
| `plan/_ub_probe.py` | batch / ubatch 探针（必须成对改） |
| `plan/_phase2_loadprobe.py` | 加载探针（`--ncmoe` / `--ctx` / `--fittarget`） |
| `plan/_refactor2_regression.py` | 回归断言（`--strict` / `--self-test`） |
| `plan/_refactor2_body_probe.py` | 启动块 argv 逐字段校验 |
| `plan/_install_graft.py` | 嫁接产物落地（新目录 + mmproj + override） |

---

## 6. 已废弃 / 已归档路径

| 路径 | 状态 | 替代 |
|---|---|---|
| `generate_ini.bat` | ❌ **不存在** | 功能已并入 `launcher/update_launchers.py`（TASK-039 归档完成） |
| `<llama-cpp-dir>/launcher-models.json` | ❌ 位置错误 | `launcher/launcher-models.json` |
| `<llama-cpp-dir>/update-launchers.bat` | ❌ 位置错误 | `launcher/update-launchers.bat` |
| 仓库根下的 `models-config.ini` | ❌ 位置错误 | 生成物在 `<models-dir>/models-config.ini` |
| `--mmap` / `--no-mmap` | ⚠️ 已废弃 | `--load-mode mmap` / `none` |
| `-fittarget` | ❌ 非法短名 | `-fitt` 或 `--fit-target` |
| `--fit on` + `--n-cpu-moe N` 同现 | ❌ 互斥 | MoE 条目只写 `--n-cpu-moe N` |

---

## 7. 维护规范

### 新增一份会话经验

1. 文件名：`sessions/YYYYMMDD-session-experience.md`
2. 正文第一行：`# YYYY-MM-DD 会话经验：<主题>`
3. **本节必须包含**：现象 → 根因 → 修复 → **可复用教训**
4. 回到本文件：在 §2 表格加一行（列"最有价值的一条"和"什么时候读"）
5. 若结论推翻了某条旧结论，**不要删旧的** —— 在旧文档对应处加一行
   `> ⚠️ 后被 YYYYMMDD 推翻：<原因>`

### 新增一份专题手册

1. 文件名：`guides/<主题>.md`（kebab-case，**不带日期**；日期型属会话经验）
2. 必须包含：**适用判定 → 步骤 → 陷阱 → 验证协议 → 参考实现**
3. 回到本文件：加进 §3 表格

### 新增一个可复用资源

1. 放入 `assets/`，**必须脱敏**（无本机绝对路径、无真实 key）
2. 回到本文件：加进 §4 表格，并注明它对应仓库中的哪个文件

### 改动路径时

**必须同时更新 §5 权威路径表和 §6 废弃路径表** —— 这是本目录最重要的一致性约束。

### 双副本同步

本目录在**两处**存在，改动后必须同步：

| 副本 | 路径 | 差异 |
|---|---|---|
| 已安装（生效） | `~\.agents\skills\llama-cpp-windows-deployment\` | —— |
| 源码（发布） | `<skills-repo>\llama-cpp-windows-deployment\` | 历史 3 份 session 文档用占位符脱敏 |

> `sessions/20260803`、`20260805`、`20260829` 三份在 `.agents` 副本中保留真实路径，
> 属**有意的历史差异**，不是漏同步。**新增文档一律双副本用占位符**，不再产生新差异。
