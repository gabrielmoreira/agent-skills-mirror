# 项目定位与发布纪律

core 只管理当前项目的目录、生命周期和交付。

## 1. 读取项目状态

定位 `short-drama.json` 后运行：

```text
python3 <core>/scripts/project_tool.py status <project>
```

使用 `status.layout.roots` 返回的项目目录。`mode=mixed` 表示中英文阶段目录并存，应先合并；
空项目在第一次阶段发布时固定布局。只读取本次任务需要的直接输入。

## 2. 通过公开命令写入

- owner 用 `publish` 原子发布一项产物，并用可重复的 `--input <project-path>` 声明直接输入。
- `accept` 只记录创作者对当前输出的接受或拒绝。
- `review` 只记录当前输出的复核结论；reviewer 不直接改 owner 文件。
- 输入或输出变化后，该产物显示 `update_needed`，重新发布即可；不递归改写下游状态。
- `package` 只收录当前 `approved` 的文本/JSON，不能替代接受或复核。
- 第一次发布由任意非空 owner 认领合法阶段路径，此后这条路径归该 owner。
- 同一项目路径仍只能属于一个 artifact，输入、交付和机器状态目录仍受保护。

完整参数见 [lifecycle-commands.md](lifecycle-commands.md)，权威边界见
[contract-and-ownership.md](contract-and-ownership.md)。
