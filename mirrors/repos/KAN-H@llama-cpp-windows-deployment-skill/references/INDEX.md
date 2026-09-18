# references 快速索引

> **用途**：本目录是技能的**经验库**。日常只需读 `SKILL.md`；当 SKILL.md 指向某份专题文档、
> 或需要追溯某个结论的**实测证据**时，从这里进入。
>
> **本文件是路径的唯一权威来源 —— 但仅限「本技能内」的路径。**
> 部署侧的目录（`<llama-cpp-dir>` / `<models-dir>`）**不属于本技能**，见 §5B：
> 那里只是作者环境的**参考布局**，你的部署可以完全不同。
>
> ⚠️ 历史上把两者混为一谈（用「权威路径表」同时描述技能内文件与作者本机文件），
> 是这个技能一度「换台机器就跑不起来」的根源。§5 现在的拆分就是为此。

---

## 1. 目录结构

```
<技能仓库>/
├── SKILL.md          ← 技能主文件（日常只读这个）
├── references/       ← 本目录：经验库
│   ├── INDEX.md      ← 本文件
│   ├── sessions/     按日期的会话经验（历史快照，不回改正文）
│   ├── guides/       专题手册（面向未来操作，随实践更新）
│   └── assets/       可直接复用的脚本与配置模板
├── scripts/          ← 可执行工具（随技能发布，无外部依赖）
│   ├── detect.ps1 / detect.py        环境自检
│   ├── mtp_graft.py                  MTP head 嫁接
│   ├── _mtp_verify.py / _ub_probe.py 实测探针
│   ├── launcher_gen/                 启动器生成器 + 交互门面
│   └── tests/                        闸门测试
└── docs/             ← 项目文档（**不属于技能载荷**，安装副本不含此目录）
```

**三类文档的区别**：

| 目录 | 性质 | 可否修改正文 |
|---|---|---|
| `sessions/` | **历史快照** —— 当时的结论与当时的路径 | ❌ 不回改（改了就不是证据了）。路径以 §5A 为准 |
| `guides/` | **操作手册** —— 照着做 | ✅ 随实践更新，路径必须保持当前有效 |
| `assets/` | **可运行资源** —— 复制出去就能用 | ✅ 但需保持脱敏 |

> `scripts/` 与 `docs/` 的性质不同：前者是技能载荷（随安装副本一起走），
> 后者只在源码仓库里（见 §7「双副本同步」）。

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
| [`20260917`](./sessions/20260917-skill-dev-provenance.md) | **项目内迁溯源**：生成器/hub 搬进仓库、参数化契约、保真验证 | **要改一个产出过真实产物的工具，先固化它的产物基线** | 想知道 `scripts/launcher_gen/` 从哪来、凭什么信它 |

---

## 3. 专题手册（`guides/`）

| 文档 | 解决什么 | 关键结论 |
|---|---|---|
| [`mtp-head-grafting.md`](./guides/mtp-head-grafting.md) | 给**没有 MTP head 的微调模型**嫁接官方 head | 实测 **+34.6% 解码**（64.28 → 86.51 t/s，acceptance 0.736）；四个陷阱；**显存代价 = 权重字节 × 3** |
| [`20260913-moe-offload-community-research.md`](./guides/20260913-moe-offload-community-research.md) | MoE 卸载的**社区现状**调研 | 社区**无最优共识、无可用自动脚本**；但有两个可直接抄的杠杆（`-ub 2048`、`--load-mode none`） |

---

## 4. 可复用资源（`assets/`）

### 启动器模板

| 文件 | 对应的部署侧启动器（见 §5B.3） |
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
| [`model-profiles.json`](./assets/model-profiles.json) | **参考参数集** —— **18 个 profile**，其中 **3 个含结构化 `moe` 块**（`gemma4-26b-a4b-qat` / `gemma4-26b-a4b` / `qwen36-35b-a3b`）。字段含 `expert_bytes_per_layer_mib` / `per_layer_spread_pct` / `vram_budget_16gb` |
| [`preset-templates.json`](./assets/preset-templates.json) | 7 种部署场景的 preset 模板 |

> **这不是任何东西的「快照」，也没有「权威版本」在别处。**
> `model-profiles.json` 是一份**参考参数集**：里面的 `verified: official` 值采集自厂商文档、
> `verified: measured` 值来自作者本机的实测（**硬件相关，只是参考点，不是保证**）。
> 生成器读的是*你自己*部署目录下的那一份；这一份是给你起步参考的样本。
> 文件名沿用未改 —— 因为生成器的运行时数据文件就叫这个名字，改名会造成「同一个名字指两个东西」。

---

## 5. 文件索引

> **本节分两部分，性质完全不同，不要混读：**
>
> | | 含义 | 权威性 |
> |---|---|---|
> | **§5A 项目内** | 随技能一起发布；换台机器、换个用户，**照常工作** | ✅ **权威** —— 引用以这里为准 |
> | **§5B 部署侧** | 作者本机的目录长什么样 | ⚠️ **参考** —— 你的部署可以完全不同 |
>
> 全文其他地方出现 `launcher/xxx` 这类相对写法时，指的是**你自己部署目录下**的对应文件，
> 不是本技能的某个文件。

### 5A 项目内（随技能发布 ✅ 权威）

| 路径 | 用途 |
|---|---|
| [`scripts/mtp_graft.py`](../scripts/mtp_graft.py) | **MTP head 嫁接的权威实现**：`--check` 只读 / `--go --out` 写入 + 写后自检 / `--audit` 列 per-layer KV 数组 |
| [`scripts/_mtp_verify.py`](../scripts/_mtp_verify.py) | 嫁接 A/B 验证（baseline vs `--spec-type draft-mtp`，同会话对比） |
| [`scripts/_ub_probe.py`](../scripts/_ub_probe.py) | batch / ubatch 探针（`-ub` 单独改无效的实证工具） |
| [`scripts/launcher_gen/update_launchers.py`](../scripts/launcher_gen/update_launchers.py) | **启动器生成器**：扫描 → 渲染 3 个菜单 `.bat` + `models-config.ini`；读 `LAUNCHER_DIR` / `CHAT_DIR` |
| [`scripts/launcher_gen/update-launchers.bat`](../scripts/launcher_gen/update-launchers.bat) | 生成器的 Windows 入口（纯 ASCII） |
| [`scripts/launcher_gen/llama_hub.py`](../scripts/launcher_gen/llama_hub.py) | 交互式门面：菜单 / `--guide` / `--diagnose` / `--write-docs` |
| [`scripts/launcher_gen/llama-hub.bat`](../scripts/launcher_gen/llama-hub.bat) | 门面的 Windows 入口 |
| [`scripts/launcher_gen/README.md`](../scripts/launcher_gen/README.md) | **冷启动指南** + 注册表 schema + 回归模式说明 ← 新用户从这里开始 |
| [`scripts/detect.ps1`](../scripts/detect.ps1) | Windows 环境自检（GPU / 驱动 / VRAM / 模型 / 服务） |
| [`scripts/detect.py`](../scripts/detect.py) | 同上，跨平台 Python 版 |
| [`scripts/tests/test_mtp_graft.py`](../scripts/tests/test_mtp_graft.py) | 嫁接闸门测试（17 例：1 正向 + 16 负向；不需真模型，亚秒完成） |

> `launcher_gen/*` 需要两个环境变量（`LAUNCHER_DIR` / `CHAT_DIR`），见其 README。
> 这两个是**机器相关**的：`LAUNCHER_DIR` 缺省为脚本自身所在目录，`CHAT_DIR` **无默认值**、缺失即报错退出 2。

### 5B 部署侧参考布局（⚠️ 示例，**非本技能一部分**）

> 下面描述的是**作者本机**部署目录的组织方式，路径已逐条实测校验（2026-09-13）。
> 价值在于**架构借鉴**：一个能跑起来的启动器生态长什么样、什么依赖什么、哪些是生成物。
> **你自己的部署不必长这样；本技能也不依赖它存在。**
> 历史文档（`sessions/`）里若出现下表「旧路径」列的写法，以下表「当前路径」列为准。

#### 5B.1 入口与核心

| 当前路径 | 旧路径 / 常见误写 | 说明 |
|---|---|---|
| `llama-hub.bat` | — | **在仓库根**（不在 `launcher/`）。交互菜单入口 |
| `launcher/update-launchers.bat` | `update-launchers.bat` | 生成器入口（纯 ASCII） |
| `launcher/update_launchers.py` | `update_launchers.py` | 生成器主体（Python 3.11，纯标准库） |
| `launcher/llama_hub.py` | `llama_hub.py` | 菜单 / `--guide` / `--audit` / 参数编辑器 |

#### 5B.2 数据与配置

| 当前路径 | 旧路径 | 说明 |
|---|---|---|
| `launcher/launcher-models.json` | `launcher-models.json` | 启动器注册表（`<llama-cpp-dir>/launcher-models.json` 已不存在） |
| `launcher/model-profiles.json` | `model-profiles.json` | 模型参数知识库（含 `moe` 块） |
| `launcher/preset-overrides.json` | — | **唯一事实源**：per-model 参数与 `tuning` 实测记录 |
| `launcher/draft-health.json` | — | MTP 草稿实测结论 |
| `launcher/draft-blacklist.json` | — | 草稿黑名单 |
| `launcher/.llama-server-keys.json` | — | 服务 key 存取（**不要外传**） |
| `<models-dir>/models-config.ini` | `models-config.ini` | Router preset **生成物** —— **不在仓库内**，由生成器写出 |

#### 5B.3 启动器（生成物）

| 当前路径 | 旧路径 |
|---|---|
| `launcher/start-Gemma4-Launcher.bat` | `start-Gemma4-Launcher.bat` |
| `launcher/start-Qwen-Launcher.bat` | `start-Qwen-Launcher.bat` |
| `launcher/start-CPU-Toolcall-Launcher.bat` | `start-CPU-Toolcall-Launcher.bat` |
| `launcher/start-embedding.bat` | — |
| `launcher/models-config.bat` | — |
| `launcher/legacy/*.bat` | `generate_ini.bat`（**已归档/不存在**，见 §6） |

#### 5B.4 文档与基线

| 当前路径 | 说明 |
|---|---|
| `launcher/docs/MODELS.md` | 模型清单（含「MoE 卸载」列） |
| `launcher/docs/脚本使用注意.txt` | GBK 无 BOM，操作注意事项 |
| `launcher/backup/phase1-baseline.json` | Phase 1 基线哈希 |
| `plan/refactor-launcher-ecosystem-{1,2,3}.md` | 改造方案与执行记录（**3 是最新**） |

#### 5B.5 探针脚本（`plan/_*.py`）

> 计划文档里每个数字都由这些脚本产出。**它们是可复现性的来源，不要删。**
> 测量输出（`plan/_*.json`、`plan/_*.png`）已 gitignore。
>
> ⚠️ **MTP head 嫁接已迁入项目内** —— 用 [`../scripts/mtp_graft.py`](../scripts/mtp_graft.py)，
> **不要再用 `plan/_mtp_graft.py`**（它 `import update_launchers`，脱离 `launcher\` 即报错，已废弃）。

| 脚本 | 用途 |
|---|---|
| `plan/_mtp_verify.py` | 嫁接 A/B 验证（baseline vs `--spec-type draft-mtp`） |
| `plan/_ub_probe.py` | batch / ubatch 探针（必须成对改） |
| `plan/_phase2_loadprobe.py` | 加载探针（`--ncmoe` / `--ctx` / `--fittarget`） |
| `plan/_refactor2_regression.py` | 回归断言（`--strict` / `--self-test`） |
| `plan/_refactor2_body_probe.py` | 启动块 argv 逐字段校验 |
| `plan/_install_graft.py` | 嫁接产物落地（新目录 + mmproj + override） |

> ↑ 原「§5.6 项目内工具」表已提升为 **§5A** —— 它是本节里唯一有权威性的一组。
> 本节剩下的都是**部署侧参考布局**（§5B），仅供架构借鉴。

---

## 6. 已废弃 / 已归档路径

| 路径 | 状态 | 替代 |
|---|---|---|
| `plan/_mtp_graft.py` | ❌ **已废弃** | 迁入项目内为 [`../scripts/mtp_graft.py`](../scripts/mtp_graft.py)（自包含、12 条闸门、按 block 区间识别头、支持多块头与 per-layer KV 审计）。旧脚本依赖 `launcher/update_launchers.py` 的 `GGML_TYPE_BYTES` / `read_gguf_tensors`；后者的现成版本在 [`../scripts/launcher_gen/update_launchers.py`](../scripts/launcher_gen/update_launchers.py) |
| `generate_ini.bat` | ❌ **不存在** | 功能已并入生成器（TASK-039 归档完成） |
| `<llama-cpp-dir>/launcher-models.json` | ❌ 位置错误 | 应在部署目录的 `launcher/launcher-models.json`（见 §5B.2） |
| `<llama-cpp-dir>/update-launchers.bat` | ❌ 位置错误 | 应在部署目录的 `launcher/update-launchers.bat`；**或者直接用技能自带的** [`../scripts/launcher_gen/`](../scripts/launcher_gen/) |
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

**必须同时更新 §5A（项目内，权威）与 §5B（部署侧，参考）** —— 这是本目录最重要的一致性约束。

- 新增/移动**技能内**文件 ⇒ 进 §5A，用相对链接（`../scripts/xxx`），**并确保安装副本能跟着走**
- 部署侧布局变了 ⇒ 改 §5B，但**不要把它写成「权威」** —— 它只是一个人的一台机器

> ⚠️ **防止旧病复发**：不要为「某个文件到底在哪」设一个跨技能边界唯一的答案。
> 技能内文件与部署侧文件是**两套东西**；把它们写进同一张「权威路径表」曾是 86 条外部依赖的根源。

### 双副本同步

本目录在**两处**存在：

| 副本 | 路径 | 角色 |
|---|---|---|
| 源码（发布） | `<skill-repo>\` | 唯一**编辑处** |
| 已安装（生效） | `~\.agents\skills\llama-cpp-windows-deployment\` | 由源码**同步过去**的副本 |

**同步边界**（哪些目录该同步）：

| 路径 | 同步 | 原因 |
|---|---|---|
| `SKILL.md`、`CHANGELOG.md`、`README.md`、`LICENSE` | ✅ | 技能载荷 —— 技能运行时要读 |
| `references/` | ✅ | 同上 |
| `scripts/` | ✅ | 同上（工具随技能发布） |
| `docs/` | ❌ | 项目文档，非载荷 |
| `scripts/mtp-graft-package/` | ❌ | 考古材料，未并入发布集 |
| `AGENTS.md`、`CLAUDE.md`、`.claude/`、`.vscode/` | ❌ | GitNexus 生成 / 开发环境配置，**不可手写**（见 `docs/merge-plan.md` 决策 2） |

**两副本现在应当逐字节一致。** 新增文档一律用占位符（`<llama-cpp-dir>` / `<models-dir>` /
`C:\llama.cpp` / `C:\models\chat`），**不得写入本机绝对路径**。

> 历史上有 3 份 session 文档在 `.agents` 副本里保留真实路径，造成长期的双副本差异。
> 2026-09-17 已把 `.agents` 侧也改为占位符 —— **历史结论一字未动，只改了路径字面**。
