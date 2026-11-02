# Plugin Scanner

Run an LLM-guided security review of third-party Agent Zero plugins from a Git repository.

## What It Does

This plugin builds a structured scanning prompt from a selectable checklist, runs that prompt in a temporary agent context, and returns a markdown report describing the plugin's security posture.

## Main Behavior

- **Prompt-driven scan**
  - Loads scan checks and a markdown prompt template from the plugin's `webui/` assets.
- **Temporary scan context**
  - Creates a temporary chat context, logs the generated prompt into it, starts the agent immediately, and waits for the model result.
- **Parallel-friendly execution**
  - Each scan runs in its own chat context; the plugin does not serialize scans behind a "wait for another scan" queue.
- **Selectable checks**
  - Supports scanning all checks by default or only the subset selected by the caller.
- **UI integration**
  - Includes API endpoints and web UI files for logging the prompt, starting the scan, and running scans synchronously.

## Key Files

- **Scan runner**
  - `api/plugin_scan_run.py` performs a synchronous end-to-end scan and returns the report.
- **Prompt builder**
  - `helpers/prompt.py` loads check definitions and renders the final scan prompt.
- **Additional APIs**
  - `api/plugin_scan_queue.py` logs the prompt into the temporary chat.
  - `api/plugin_scan_start.py` starts the agent in that chat.

## Configuration Scope

- **Settings sections**: none
- **Per-project config**: `false`
- **Per-agent config**: `false`

## Plugin Metadata

- **Name**: `_plugin_scan`
- **Title**: `Plugin Scanner`
- **Description**: Security scanner for third-party A0 plugins.
