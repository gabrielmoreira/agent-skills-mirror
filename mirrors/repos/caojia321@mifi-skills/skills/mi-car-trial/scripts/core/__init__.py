"""mi-car-trial 核心业务逻辑（纯函数 / 无 argparse / 无 print）。

对外暴露的职责层级：

- core.http      —— HTTP GET/POST + envelope 校验，底层只依赖标准库
- core.money     —— 元/万元/比例 → 分 的金额换算
- core.car_models—— /car-models 拉取 + 车型名匹配
- core.terms     —— /supported-terms 拉取
- core.aggregate —— /aggregate POST 试算
- core.evaluate  —— 对 aggregate 响应做首付/期数/过滤/排序评估

CLI 层只做：参数解析 → 调 core → 把返回值 json.dumps 写到 stdout。
Skill 层只做：在 SKILL.md 里指引如何调用 CLI。
"""
