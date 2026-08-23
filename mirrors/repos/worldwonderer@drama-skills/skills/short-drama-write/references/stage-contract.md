# 剧本阶段契约

本阶段只拥有 `剧集/<EP>/剧本.md`：场景、动作、对白、画外音、声音事实、画面文字、连续性提示与转场。
它继承项目/分集决定，但不决定人物视觉身份、镜头构图、提示词或媒体生产。

所有来源都用文档中可见的集号与场景 ID 定位；不建立第二份节拍、block、审批或状态文件。格式标签
只负责区分生产语义，不借格式补造剧情。

## 本阶段规则

### `SCR`

| ID | Class | Knowledge |
|---|---|---|
| SCR-01 | reviewed_invariant | Every scene has a current agenda, opposing force, directional turn, and exit state. |
| SCR-02 | craft_default | Prefer choices and consequences over coincidence for major turns. |
| SCR-03 | reviewed_invariant | Private thought is expressed through behavior, evidence, or deliberate VO/OS. |
| SCR-04 | craft_default | Dialogue carries agenda, relationship, subtext, and a change—not only information. |
| SCR-05 | structural_invariant | Existing production tags use supported, closed syntax and resolvable references. |
| SCR-06 | taste_option | Silence, slang, interruption, narration, and sentence rhythm remain character/style choices. |
| SCR-07 | reviewed_invariant | Story-critical text, VO/OS, SFX, transition, and continuity requirements are not left indistinguishable from ordinary prose. |
| SCR-08 | craft_default | When abstract emotion obscures performance, translate it into character-specific behavior, object handling, distance, silence, or delivery. Dialogue turn length and tactic follow the scene agenda rather than a universal attack-defense cadence. |
| SCR-09 | craft_default | Break a long speech with a visible action beat that changes the speaker's tactic, giving downstream a sourced cut point and the performance a breath; a speech with no internal turn is shortened rather than split. |
| SCR-10 | reviewed_invariant | When the creator marks a beat's realization as replaceable under later pressure, the record separates the dramatic function from the current depiction and names a fallback depiction that delivers the same function: same person proven or changed, downstream payoff refs and next-episode entry state still satisfied, cost not erased, no new setup required. Deleting the beat is never a fallback. An unmarked beat leaves the rule inactive—the suite carries no platform standard, predicts no outcome, and pre-emptive sanding is the more expensive mistake. |
| SCR-11 | craft_default | When sound carries story information, spatial pressure, off-screen presence, a deliberate silence, or a scene bridge, the screenplay identifies the necessary source/event and its dramatic target; it does not prescribe per-shot mixing, add decorative sound to every scene, or use music to replace performance. |
| SCR-12 | craft_default | A crowded scene first makes clear who is contending with whom—by cutting non-essential presence, staggering entrances, splitting the scene so one opponent holds the focus at a time, or handing attention from one character to the next—rather than naming every present character in action paragraphs. Deliberately chaotic ritual, siege, or farce may override this once the disorder is a visible choice and one followable thread remains. |
| SCR-13 | reviewed_invariant | A consequential choice keeps at least two live values in conflict until the character acts, and the screenplay itself makes their immediate stakes and closing cost perceptible. The action closes what is actually incompatible without inventing the sacrifice of an independent benefit; it does not rely on upstream notes or first declare one option useless, costless, or already lost and then present the remainder as a choice. |
| SCR-14 | reviewed_invariant | Evidence is tested on screen against the strongest live mundane counter-explanation as a counterfactual: if that explanation were true, a named visible result would differ, and the test makes it fail. The evidence changes only the claim it supports and produces a proportionate response; when the counter-explanation remains open, the conclusion narrows rather than jumping across identity, motive, cause, or full truth. |
| SCR-15 | craft_default | A local payoff visibly changes an object, repeated action, relationship, or available next move while retaining residue from the cost; the ending does not replace that consequence with a slogan explaining the theme. |
| SCR-16 | reviewed_invariant | A deadline action chain fits its stated time and available tools, and exact time markers correspond to completed work rather than decorative jumps. When it cannot fit, the character narrows the objective, changes method, recruits an established resource, or accepts a visible failure/cost instead of receiving unexplained speed. |

规则分级由高到低：`structural_invariant`（结构缺陷，阻断）、
`reviewed_invariant`（需证据判断）、`craft_default`（常用做法，可覆盖）、
`taste_option`（创作者选择，不作缺陷）。创作者已接受的事实优先于本表。
