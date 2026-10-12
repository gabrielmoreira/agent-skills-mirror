# Development quickstart

Use an existing supported NetClaw with its HUD running. Open its host in VS Code
(local Mac/Linux, WSL distribution or Remote SSH). Install the candidate VSIX,
add the loopback HUD API URL, review identity and bind the installation.

Inspect Overview and RAG before sending work. Chat uses that NetClaw's existing
provider and approvals. Assistant setup is explicit and exposes only the adapter's
bounded tools. Do not replace existing assistant configuration.

Build and verify from extensions/netclaw-vscode using npm ci, npm run check,
npm run build, npm test (unchanged HUD dependencies are required for integration
tests). Packaging requires clean committed source. The exact candidate VSIX and
Windows/WSL commands are in windows-wsl-handoff.md and artifacts/package.json.
