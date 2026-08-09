# 2026-08-07 闭源 Rust cdylib 核心算法差分复现

## 场景分类
二进制分析 / 逆向工程

## 目标概述
对客户自有二进制(闭源 Rust+Python 混合,含 PyO3 算法库 cdylib)做 IP 保护强度评估:逆向核心算法并以 Rust 重写功能等价实现,用同一测试集与原版逐位对拍验证输出一致性。

## Scope 摘要(脱敏)
- auth_basis: written_contract(客户为软件所有权方,书面委托)
- network_profile: lab_only(仅本地回环)
- asset_types: [本地 cdylib, 本地服务器]

## 角色
- lead_role: lead
- specialists: [cre, cie]

## 完整执行链路

1. 勘察多个历史工作目录,确认最新工作区(git log 活跃度判断)
2. 复现核心算法库(6 个 Python API):
   - 搭建差分电池: 同输入分别跑原版/复现版,JSON 序列化输出对比
   - 初始 189/194(5 个 Schneider mdt=0.5 用例失败,段结构一致仅系数差 2-13%)
   - 反汇编导数函数 + 从 Hermite 输出 coeffs 数学反解切向量 → 定位为最小二乘线性拟合
   - 修正后 194/194
3. 线性指派(LSAP): 移植开源 Crouse JV 算法 → 600/600 vs 原版 + 240 golden
4. Cargo workspace 拆分: 纯计算 crate(无 PyO3)+ 薄封装 crate
5. LED 灯光字节码编译器: 黑盒探测(60+120 随机用例)→ 120/120 字节级一致
6. 归档打包器: Python JSON 序列化 + 双重舍入语义 → 120/120 字节级一致
7. 降落/分解 operation: 黑盒反推公式 → 240/240

## Evidence 链摘要(脱敏)
| E-id | source_type | 可复用命令模式 | 关联 Finding |
|------|-------------|----------------|--------------|
| E-001 | 反汇编 | `otool -tV -p <addr> <so>` | F-001 |
| E-002 | 黑盒差分 | runner 同输入双跑 + compare 脚本 | F-002 |
| E-003 | 黑盒探测 | 单变量全组合探测矩阵 | F-003 |

## Finding / Path 摘要
- top_finding: 符号未 strip + 算法全公开 → 核心算法可被完全逐位复现(194/194)
- path_type: solve
- path_one_liner: 反汇编 + 系数反解 + 黑盒差分三路交叉验证

## 踩坑记录

| 问题 | 原因 | 解决方案 | 耗时 |
|------|------|---------|------|
| 导数系数差 2-13% | 误用端点差分,原版是中心化 LS 拟合 | 数学反解 → 匹配 LS 窗口 | 2h |
| round 语义两套 | 坐标用二进制 half-even,派生字段用 CPython 十进制 round | 双函数区分 | 1h |
| 同帧多色规则 | 同帧桶合并保留首桶 min + 末桶 max | 定向探测矩阵 | 1.5h |
| JSON 键序/浮点格式 | Python dict 保序 + repr 科学计数 | 自写序列化器 | 1h |
| 双模式 operation | 同 z 组着色 + 跨 z 累积 | z 分组处理 | 1.5h |

## 工具链发现
- `otool -tV -p <sym>` 反汇编 macOS Mach-O cdylib
- x86_64 CPython venv(Apple Silicon 经 Rosetta)加载 x86_64 .so
- `uv venv --python cpython-3.12.11-macos-x86_64-none` 快速建 x86_64 venv
- 差分对拍模式: CLI 子进程 + JSON 输出对比,稳定可复用

## 关键代码/命令

```bash
# 差分电池(三件套: runner / compare / CLI 桥)
bash run_diff.sh                # 核心算法 194/194
python3 diff_lights.py          # 灯光 120/120
python3 diff_render.py          # 打包 120/120
python3 diff_ops.py             # operations 240/240
# 反汇编
otool -tV -p 0x22660 <orig>.so
# 构建
cargo build --workspace --target x86_64-apple-darwin --release
```

## 对本包的改进建议
- 可补充"闭源 Rust cdylib(PyO3)差分复现"workflow 到 reverse-engineering/references

## 可复用的模式/脚本片段
- 系数反解法: 从插值输出 coeffs 反解切向量,定位导数估计差异
- 黑盒规则解码矩阵: 单变量全组合探测(is_fade×4、同帧×N、舍入边界)
- 差分对拍三件套: runner(载荷)/ compare(容差)/ CLI 桥

## 进化动作
- [x] 新增了 pitfalls 记录(本文件)
- [ ] 更新了路由矩阵
- [ ] 更新了 tool-index
- [ ] 更新了 bootstrap-manifest
- [ ] 更新了子 skill 文档

## 环境信息
- OS: macOS (Darwin), Apple Silicon + Rosetta
- 工具版本: rustc/cargo 1.97, otool, x86_64 CPython 3.10/3.12, graphviz
- 目标平台/版本: 闭源 Rust cdylib(abi3, x86_64)

## 索引同步
已同步 `_index.md`。
