# 运行时预检与发布纪律

无论从主技能还是子技能进入，都先完成同一套轻量预检。它只检查安装完整性、项目事务状态和已记录的精确引用，不评价创作内容。

## 1. 验证当前安装

从 `suite-ref.json` 解析到逻辑安装路径中的 core 后，用当前可用的 Python 3 解释器运行：

```bash
python3 <core>/scripts/suite_verify.py <core>
```

若环境的 Python 3 命令名不同，使用该环境已经提供的等价解释器。验证器必须沿逻辑安装路径逐一检查清单中的八个技能；混装、缺件、额外可执行文件或 hash 不一致时停止写入。不要退回源码检出目录“借用”通过验证的兄弟技能。

## 2. 恢复事务，再读状态

定位项目根目录后，先运行：

```bash
python3 <core>/scripts/project_tool.py recover <project>
python3 <core>/scripts/project_tool.py status <project>
```

`recover` 可重复执行。若它报告 blocked，保持创作者文件原样并先处理冲突；不要绕过 WAL、手改状态文件或假定上次写入成功。`status` 中的 accepted/candidate 指针和阻断项是后续工作的当前事实。

## 3. 只通过公开生命周期写入

- 负责人用 `publish` 原子发布候选，并给每个外部结构化引用提供精确 input hash。
- 上游接受引用不继承候选状态；`authority:candidate` 只用于同次发布的目标或明确的
  候选预览链，后者在接受前必须已由同 hash 的上游接受快照闭合。
- 创作者接受、独立审查和内容修订是不同动作；审查者发布 finding/verdict，不改负责人的来源。
- 每次修订后重新运行适用的结构校验，并让下游刷新旧 hash。
- `package` 是最终文本/JSON 交付闸门，不是接受或审查命令；任何阻断项仍在时不打包。

完整命令参数见 [lifecycle-commands.md](lifecycle-commands.md)，权威边界见 [contract-and-ownership.md](contract-and-ownership.md)。
