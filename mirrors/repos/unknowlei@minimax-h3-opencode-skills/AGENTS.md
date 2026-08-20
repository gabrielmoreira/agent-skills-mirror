# AI Installation Contract

When a user gives you this repository URL and asks you to install it, perform the installation instead of only explaining commands.

## Install Target

Install globally for OpenCode unless the user explicitly requests project-local installation.

- Windows global target: `$HOME\.config\opencode\skills`
- Linux/macOS global target: `$HOME/.config/opencode/skills`
- Project-local target: `<project>/.opencode/skills`

## Required Installation

1. Clone or download this repository to a temporary directory.
2. Locate every directory under `skills/` that contains `SKILL.md`.
3. Before replacing an existing same-name skill, create a timestamped backup beside it. Do not delete unrelated skills.
4. Copy all six bundled skill directories into the selected OpenCode skills target.
5. Install the official `h3-prompt-writing` dependency from:
   `https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing`
6. Prefer a shallow sparse clone of `https://github.com/MiniMax-AI/MiniMax-H3.git` restricted to `skills/h3-prompt-writing`, then copy that directory to `<target>/h3-prompt-writing`.
7. Confirm that these seven files exist:
   - `<target>/h3-prompt-writing/SKILL.md`
   - `<target>/minimax-h3-creative-director/SKILL.md`
   - `<target>/minimax-h3-multishot-planner/SKILL.md`
   - `<target>/minimax-h3-text-video-prompt/SKILL.md`
   - `<target>/minimax-h3-reference-video-prompt/SKILL.md`
   - `<target>/minimax-h3-keyframe-video-prompt/SKILL.md`
   - `<target>/minimax-h3-prompt-reviewer/SKILL.md`
8. If `opencode` is available, run `opencode debug skill` and verify that all seven names are discovered.
9. Report the exact target directory, installed skill names, backup paths, and validation result.
10. Tell the user to start a new OpenCode session so previously loaded skill content is not reused.

## Safety

- Preserve unrelated files and skills.
- Never recursively delete the complete OpenCode skills directory.
- Treat the official dependency as upstream content; fetch it from the MiniMax repository rather than substituting a reconstructed copy.
- If network access prevents fetching the official dependency, install the six bundled skills, clearly report the missing dependency, and provide the exact retry step.
