# Phase Execution Pattern

Each phase follows this standard pattern:

| Step | What to do | Why |
|------|-----------|-----|
| **0. Precondition Check** | Run the matching `node scripts/check-phase-N-*.mjs` script | Verifies prerequisites are met before proceeding |
| **1. Load skill** | Invoke the skill for this phase | Gives you current rules, patterns, constraints |
| **2. Execute** | Follow the loaded skill's workflow | The skill defines HOW to do the work correctly |
| **3. Verify** | Run lint and build | Catch errors before moving to next phase |
| **4. Post-verification** | Run the matching `node scripts/check-phase-N-complete.mjs` (if available) | Machine-checkable validation of phase completion |
| **5. Checkpoint** | Confirm phase completion | Ensures dependencies satisfied for next phase |

**CRITICAL: Do NOT skip step 1 (loading the skill).** Skills evolve — always load the current version.

**Always invoke every script via `node` (never as a bare executable)** so it works on Windows cmd/PowerShell as well as macOS/Linux/Git Bash.

## Available Verification Scripts

- `node scripts/check-sfdx-project.mjs` - Validates SFDX project exists (Phase 0/1 prerequisite)
- `node scripts/check-phase-1-complete.mjs` - Verifies scaffold complete (Phase 4/6 prerequisite)
- `node scripts/check-phase-4-complete.mjs` - Verifies UI build complete (Phase 6 prerequisite)
- `node scripts/check-phase-6-ready.mjs` - Verifies deployment prerequisites met
- `node scripts/check-hosting-target.mjs` - Determines which hosting target is configured

All scripts exit 0 on success, exit 1 on failure with an error message.
