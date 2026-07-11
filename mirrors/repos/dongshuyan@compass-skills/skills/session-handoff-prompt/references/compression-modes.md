# Compression Modes

## balanced

Default. Use when the user has not requested a length. Keep:

- Objective and hard requirements.
- Verified facts and decisions.
- Relevant task-forest state when available.
- Completed work, pending work, and verification gaps.
- Key files, commands, and artifacts.
- Clear next actions.

This mode aims for high task-state fidelity without flooding the next session.

## minimal

Use when the user wants the shortest usable prompt or already understands the background. Keep only:

- Current objective.
- Highest-priority constraints.
- Current state.
- First next actions.

Do not include long decision history, failed attempts, or detailed task-forest timelines unless they directly change the next action.

## full

Use when the task is complex, risky, high-cost, or likely to be audited. Add:

- More decision rationale.
- Failed attempts that should not be repeated.
- Conflicts, uncertainty, and verification gaps.
- More complete file, command, and artifact state.
- More task-forest nodes, todos, dependencies, and timeline summary.

Full mode is still a continuation prompt, not a raw transcript dump.

## Mode Disclosure

Every delivery should state the mode used and offer the other modes. Keep this note outside the paste-ready prompt unless the user asks to include it.
