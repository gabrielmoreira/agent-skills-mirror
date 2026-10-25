# Deployment Spec Kit workspace

Use **NetClaw: Create deployment Spec Kit workspace** after choosing a source and identifying intended homes. Select Codex, Claude or Copilot and a new absolute workspace outside the NetClaw checkout and all claw homes. Native review names the destination and isolated tools directory before downloading pinned Specify 0.7.1 and dependencies. Scaffolding starts neither an assistant nor an installer.

The [NetClaw claw preset](../installer/spec-kit/netclaw-claw/README.md) pins Specify source commit `c12293c3dac84bf20fccb7dfc455a76792d7a6d6`. It renders the selected client's six commands, verifies effective templates and seeds a deployment spec, task file and reference-only plan. Python dependencies are not a fully locked offline distribution. A partial failure retains the workspace for inspection.

Follow **specify → clarify → plan → tasks → analyze → implement** in that deployment project. Resolve all findings before implementation. The plan output must be a canonical secret-free Claw Plan with explicit gaps; templates do not supply provider credentials, target homes or production approval.

The preset's **implement** command submits the exact plan for native review. It cannot authorize unattended setup, invoke a shell installer or fabricate a report. After a run, **NetClaw: Write deployment Claw Report** offers a reviewed write of the structural redacted report to `claw-report.json`. An independently changed existing report is refused. Detailed reports are not written through this route.

The pinned CLI has been exercised in isolated temporary workspaces for all three clients, combined rendering and displaced-template refusal. This does not qualify the installed assistant clients or a real claw installation. See [verification](../specs/153-ide-installer/verification.md).
