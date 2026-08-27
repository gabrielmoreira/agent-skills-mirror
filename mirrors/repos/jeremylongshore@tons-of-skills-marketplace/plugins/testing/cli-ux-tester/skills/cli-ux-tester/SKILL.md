---
name: cli-ux-tester
description: Expert UX evaluator for CLIs, terminal tools, and developer APIs. Use when reviewing command usability, error messages, help systems, or developer experience.
version: 3.0.0
allowed-tools: Read, Bash, AskUserQuestion, Agent
---

# CLI UX Tester

This skill evaluates the usability of command-line interfaces and developer tools. It identifies the target CLI,
asks clarifying questions if needed, runs three evaluation agents in parallel, then passes the collected results
to a synthesizer agent to produce artifacts.

**Architecture:** The skill spawns all evaluation sub-agents directly (one Explore agent and two test agents in
parallel). This works around the platform constraint that sub-agents cannot spawn further sub-agents. The
`cli-ux-tester:cli-ux-tester` agent acts as a pure synthesizer — it receives the pre-collected test data and
produces the scored report and artifacts.

## Step 1: Detect target CLI

Try to identify the CLI to evaluate from the user's message and current directory context.

**From the user's message:**

- If the user names a specific command or tool (e.g., "review my-tool"), use that as the target.

**From the current directory:**

```bash
# Check for executable entry points
ls -la *.sh bin/ scripts/ 2>/dev/null | head -20

# Check for package.json with a bin field (Node.js CLI)
cat package.json 2>/dev/null | grep -A5 '"bin"'

# Check for Python CLI setup
cat setup.py pyproject.toml 2>/dev/null | grep -A5 'console_scripts\|entry_points' | head -20

# Check for Go main package
ls main.go cmd/ 2>/dev/null

# Check README for CLI name and usage
head -50 README.md 2>/dev/null
```

## Step 2: Ask clarifying questions if needed

Skip this step if the target CLI was already identified from the user's message in Step 1.

Otherwise, ask exactly one AskUserQuestion using the appropriate form below:

**Entry point(s) detected in current directory** → ask which to evaluate:

```text
Question: "Which CLI should I evaluate?"
Options:
  - [Each detected entry point]
  - A different installed command (provide the name)
  - A different path (provide the path)
```

**No entry points detected** → ask the user to specify:

```text
Question: "Which CLI tool should I evaluate?"
Options:
  - An installed command available in $PATH (provide the name)
  - A path to an executable (provide the path)
```

Proceed directly to Step 3 with whatever the user provides.

## Step 3: Run evaluation agents in parallel

Locate the reference files first:

- Use Glob (`**/testing-checklist.md`) to find `testing-checklist.md`; note the path
- Use Glob (`**/test-scenarios.md`) to find `test-scenarios.md`; note the path

Then spawn these three agents simultaneously, substituting the actual `{cli_command}` and `{working_dir}`:

**Explore agent** — codebase mapping:

```text
subagent_type: Explore
prompt: "Map the {cli_command} CLI codebase in {working_dir}. Find: all commands and subcommands,
help text locations, error handling code, version output, README and docs files, entry point(s),
flag/argument parsing. Return a structured summary: command tree, key file locations, patterns
observed."
```

**Test agent A** — discovery and help:

```text
subagent_type: general-purpose
prompt: "Test {cli_command}'s help system and discoverability (run from {working_dir}).
Run: {cli_command} --help, {cli_command} -h, {cli_command} help, {cli_command} (no args),
{cli_command} --version, {cli_command} -v, {cli_command} version, {cli_command} invalid-subcommand,
{cli_command} --invalid-flag. For each subcommand found, also run: {cli_command} subcommand --help.
Capture exact output. Note: what works, what fails, what's missing."
```

**Test agent B** — error handling and consistency:

```text
subagent_type: general-purpose
prompt: "Test {cli_command}'s error handling and consistency (run from {working_dir}).
Run: commands with missing required args, invalid flag values, nonexistent files, wrong syntax.
Check whether flag names are consistent across subcommands (--verbose always means the same thing).
Check exit codes with echo $?. Capture exact outputs. Note every inconsistency."
```

Wait for all three agents to complete and collect their full outputs before proceeding.

## Step 4: Launch synthesizer agent

Once all evaluation results are collected, launch the `cli-ux-tester:cli-ux-tester` agent.

Pass:

- The working directory
- The CLI entry point (command name, script path, or executable)
- Any relevant context from the user's message (e.g., "focus on error messages")
- The full output from all three evaluation agents (Explore, Test A, Test B)
- Path to `testing-checklist.md`
- Path to `test-scenarios.md`

## Step 5: Report results

When the agent completes, inform the user:

```text
✅ Evaluation complete!
📁 Results saved to: {timestamped_directory}
📊 Overall score: {overall_score}/5
🔍 Top issues: {brief_summary}

Clean up with: rm -rf CLI_UX_EVALUATION_*/
```

## Error handling

- **CLI not found**: Ask the user to confirm the command name or path
- **Permission denied**: Note the issue and ask if they want to test a different entry point
- **No CLI in current directory**: Ask the user to specify which tool to evaluate
