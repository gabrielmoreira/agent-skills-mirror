# 2026-08-03 实战经验沉淀（全量实测数据）

> 来源：2026-08-03 至 08-04 会话「拆分 Gemma/Qwen 启动脚本 + 27B 深度优化 + 工具调用测试 + CPU 工具调用脚本 + 编码修复」
> 硬件：RTX 5060 Ti 16GB + Intel U7 270K + 48GB DDR5（CPU 场景）
> 本文件为 SKILL.md 的详细数据附录，SKILL.md 保留结论。

## 一、Qwen3.6-27B 深度优化全量实测（64K / KV q8_0 / t 12 / batch 256）

| 模型 | ngl | 加载 | 显存 | tg 速度 | 较前轮 | MTP 接受率 |
|------|-----|------|------|---------|--------|-----------|
| HauhauCS IQ4XS（裸跑） | 52 | 5.1s | 96% | 14.3 t/s | +37% | - |
| MTP Q4_K_S | 48 | 11.1s | 97% | 15.5 t/s | +24% | 98.5% |
| MTP IQ4XS | 48 | 9.6s | 97% | 16.9 t/s | +25% | 94.6% |
| UD-Q4_K_XL（裸跑） | 48 | 9.6s | 90% | 10.9 t/s | - | - |

**关键发现**：
- 原 128K 配置实际 OOM：HauhauCS IQ4XS（ngl28 + q8_0 + 128K）在干净 GPU 下直接崩溃——这就是此前速度上不去的隐形瓶颈
- Qwen3.6-27B 实际 **64 层**（48 Gated DeltaNet + 16 Gated Attention）；ngl40 时 24 层在 CPU 跑
- KV 极小：64K q8_0 仅 ~0.5GB；**权重才是显存大头**
- 27B MTP 终止日志健康度：`draft acceptance = 0.921`、`graphs reused = 15`、`mean len = 2.59`
- Gemma 4 26B-A4B 为 MoE（128 专家/8 活跃/4B active），解码只算 4B → 55+ t/s，无需此优化

## 二、纯 CPU 工具调用脚本实测（start-CPU-Toolcall-Launcher.bat，端口 8086）

全部 `-ngl 0`、128K 上下文：

| 模型 | KV | 实测 tg | 内存 | 工具调用 |
|------|----|---------|------|---------|
| Qwen3.5-2B (+mmproj) | q4_0 | 57.1 t/s | ~4GB | ✅ PASS |
| Phi-4-mini | q4_0 | 38.3 t/s | 7.4GB | ❌ 不支持 |
| gemma-4-E4B (+mmproj) | q8_0 | 29.8 t/s | ~6GB | ✅ PASS |
| gemma-4-12B-QAT (+mmproj) | q8_0 | 13.0 t/s | ~6GB | ✅ PASS |

## 三、工具调用 11/11 模型测试矩阵（b10158）

- 测试方案：Phase 1 能力探测 + Phase 2 两轮工具循环（调用 → 客户端执行 → 回传结果 → 模型续答）
- 测试工具示例：`get_current_weather {"location":"Beijing"}` → 26°C 晴朗 ✅
- 全部 11 个 Gemma/Qwen 12B 以下模型均 PASS
- 结论：llama.cpp 工具调用内置，服务端 `--jinja` + 客户端 OpenAI `tools` API 即可
- **VS Code / Hermes（OpenAI 兼容客户端）无需 `--tools all`**；`--tools all` 仅服务端/Web UI 场景
- ⚠️ Phi-4-mini 实测不支持工具调用

## 四、BAT 脚本编码问题完整记录

**闪退根因**：文件 UTF-8 → 中文 Windows cmd 按 GBK(936) 解码 → 中文乱码 → 残留 ASCII 特殊字符被错误解释：

```
"REM 值: all=启用(默认) | off=关闭" 乱码后
→ "ll=启用(默认) | off=关闭"
→ 被拆成命令 "ll" + 管道符
→ "'ll' is not recognized" → 脚本崩溃闪退
```

**两个被实测排除的误区**：
1. `chcp 65001` 无效——只影响控制台显示，cmd 解析文件内容时不用它
2. UTF-8 BOM 无效——cmd 仍按 GBK 解码

**解决方案对比**：
| 方案 | cmd 双击 | VS Code 打开 | 中文界面 |
|------|:---:|:---:|:---:|
| A. 保持 GBK（转码） | ✅ | ⚠️ 需手动选 GBK | ✅ |
| B. UTF-8 + 全英文界面 | ✅ | ✅ | ❌ 无中文 |

**最终采用**：
- `start-CPU-Toolcall-Launcher.bat` → 方案 B（全英文 UTF-8，两者都正常）
- `start-Gemma4-Launcher.bat`、`start-Qwen-Launcher.bat` → 方案 A（GBK，编辑器手动选 GBK 编码）

## 五、菜单标注规范（用户体验）

- 速度标注到模型标题后：`1) Qwen3.5-2B [57 t/s] 128K [KV q4_0 fast] (multimodal)`
- 破限模型特殊标注区分
- 能力标注：`[!] NO tool calls`（Phi-4-mini）
- Gemma 脚本 Q5/Q8 标注对应 B 参数（如 12B-Q5_K_M），防用户搞混
