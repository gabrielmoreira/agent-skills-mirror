# solve Skill 质量门禁

发布或刷新 `solve` 前逐项检查；任何关键项失败都停止发布。

## 激活可靠性

- [ ] `SKILL.md` 的 `name` 与目录同为 `solve`，符合小写命名规则。
- [ ] `description` 同时写清能力和触发词：问题求解、分解、证明、证伪、调试、验证、复盘。
- [ ] `When to Use This Skill` 是具体任务，不把“所有思考”当作触发器。
- [ ] `Not For / Boundaries` 明确事实查询、运行时权限、高风险事项和缺失输入的处理方式。

## 可用性和证据

- [ ] Quick Reference 是短步骤，不复制完整领域教材。
- [ ] 至少三个示例包含 Input、Steps、Expected/Acceptance。
- [ ] 结果区分 `succeeded`、`failed`、`inconclusive`、`not_applicable`。
- [ ] 计算实验、模型推断和外部观察不会被混写成证明。
- [ ] 形式证明场景把声明、候选、结果分开，并按 required capability set 逐项接纳，不能证据跳级。

## 包完整性

- [ ] `references/index.md` 覆盖每个 Markdown 参考文件。
- [ ] catalog、taxonomy、inventory、schema 和全部 pack 的相对路径在包内解析。
- [ ] 包内保持 56 个 pack、417 个 source、60 个 derived、477 个总条目。
- [ ] 内容副本与 `operators/` 一致；内容变更只能从源库刷新。

## 安全和维护

- [ ] 算子不自授予工具、权限或结果批准权。
- [ ] 高风险场景明确 `escalate` 和人工/专业审查。
- [ ] `VERSION`、`CHANGELOG.md`、压力场景和回滚路径已同步。

## 验证命令

```bash
bash <codex-home>/skills/workflow/modules/skill-authoring/scripts/validate-skill.sh skills/solve --strict
uv run --locked --script scripts/validate_harness.py --operator-library operators/catalog.json
uv run --locked --script scripts/validate_harness.py --operator-library skills/solve/references/catalog.json
```

本清单是发布前检查，不替代具体 Harness 的权限、执行、Verifier 或生产评估。
