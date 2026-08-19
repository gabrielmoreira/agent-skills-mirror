# dsh-tongflow

**TongFlow as a [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) (dsh) plugin — a film-crew studio inside your agent.**

Three layers, never mixed up:

| Layer | Owns |
|---|---|
| **dsh** | the harness: sessions, model routing, tools, jobs, web UI |
| **the agent** | creativity: script, characters, shot lists, prompts, review notes — plain files |
| **TongFlow** | deterministic generation: every image / voice / music / video is produced by **running a saved workflow file** (`workflows/*.tongflow.json`) through the TongFlow engine and its plugins |

There is deliberately no "generate an image" tool. The agent writes a workflow, binds its inputs to project assets, runs it, reviews the take, circles the good one. Users open the same `.tongflow.json` on the embedded canvas, tweak it, and re-run.

## Install

```sh
npx @deepseek-ai/dsh@next plugin --profile web add dsh-tongflow      # from npm
# or from a tarball:  pnpm --filter dsh-tongflow pack  →  dsh plugin --profile web add ./dsh-tongflow-x.y.z.tgz
npx @deepseek-ai/dsh@next web
```

Requirements: dsh ≥ 0.1.0-rc.7 (Node ≥ 22.19), **Python ≥ 3.10** on `PATH` (or `pythonPath` in the plugin config), `git`, and `ffmpeg` for video contact sheets. On first use the plugin creates `~/.dsh/tongflow/venv` with the `tongflow` SDK; TongFlow plugins are cloned into `~/.dsh/tongflow/plugins` on demand.

Start a session whose **first message begins with `@tongflow`** — that session becomes a studio session: the conversation view turns into the Studio (chat column · project tree · preview / canvas · drawers for takes, runs and details, all in the UI language of your browser), and the agent gets the `tongflow_*` tools and skills. Any other session is untouched dsh. In the Studio: create a project (template **manga-drama** ships, with English / Chinese starter files), install TongFlow plugins and paste API keys under **Plugins & keys**, then talk to the agent — or click a workflow and use the canvas directly.

### Chat model

Any model dsh can route works. For the agent to *see* generated images (`tongflow_look`) use a vision-capable route, e.g. in `$DSH_HOME/settings.yaml`:

```yaml
llm-pi-ai:
  providers:
    google:
      apiKeyEnv: GEMINI_API_KEY
    my-qwen:                          # a self-hosted Qwen3.8-27B behind vLLM
      apiKeyEnv: QWEN_API_KEY
      api: openai-completions
      baseURL: http://127.0.0.1:8000/v1
      models:
        - id: Qwen/Qwen3.8-27B
          input: [text, image]
```

Video and audio are reviewed through TongFlow's own describe / transcribe slots (`tongflow_perceive`), so they work with any chat model.

## The project (a real crew, on disk)

```
~/.dsh/tongflow/projects/<id>/
  project.json
  story/                treatment.md · outline.md · script.md            ← agent-written text
  world/<ID>/           card.md · consistency.json · REF/ · VO/           ← CHR_ LOC_ PRP_ STY_ entities
  episodes/EP01/        scenes.json (shot breakdown) + MUS/ SFX/ MIX/ CUT/
  shots/<SHOT>/         SB/ KF/ ANI/ DLG/                                 ← numbered takes per pass
  inbox/                user drops
  workflows/            one *.tongflow.json per generated asset; templates/ = starting shapes
  notes/                review notes
  export/               deliverables
```

- Ids: `EP01` · `EP01_SC003` · `EP01_SC003_SH0010` (shots step by 10) · `CHR_MEI` · takes `T01…`. One take per pass is **circled**; every take carries a `provenance.json` (workflow hash, bindings, plugins, duration).
- `tf://` references bind workflows to roles, not paths: `tf://CHR_MEI/REF`, `tf://EP01_SC003_SH0010/KF`, `tf://EP01/ANI`, `tf://EP01_SC003_SH0010/dialogue/2`, `tf://STY_MAIN/prompt`. Prompts compose with `{{tf://…}}` placeholders inside one text.
- The **consistency kit** (`consistency.json`: prompt prefix/suffix, negative prompt, seed, plugin, model, refs) travels with each entity and is what keeps shots on-model.

## Agent tools

`tongflow_project_*` · `tongflow_bible_*` · `tongflow_breakdown_*` · `tongflow_workflow_new / _patch / _read / _list / _validate / _bind / _run` · `tongflow_node_catalog / _describe` · `tongflow_take_list / _circle / _delete` · `tongflow_dailies_note` · `tongflow_ref_resolve` · `tongflow_look` (images / video contact sheets, returned as an image block) · `tongflow_perceive` (video/audio/image understanding via TongFlow slots) · `tongflow_plugins_list / _install / _uninstall` · `tongflow_run_status`. Long runs go through dsh background jobs (`run_in_background`).

Skills shipped: `tongflow-studio` (the working method) and `tongflow-manga-drama` (the pipeline: script → bible → breakdown → SB → KF → DLG → ANI → MUS → CUT).

## HTTP (same origin as dsh)

`/tongflow/projects`, `/tongflow/p/:pid/{tree,status,entities,breakdown,takes,workflows,workflow,runs,files/*,ref}`, `/tongflow/runs/:id[/events|/cancel]`, `/tongflow/plugins`, `/tongflow/env`, `/tongflow/health`, plus the canvas-compat API under `/tongflow/p/:pid/api/*` that `tongflow/canvas` talks to.

## Configuration (cordis row `tongflow`)

| key | default | |
|---|---|---|
| `studioRoot` | `<DSH_HOME>/tongflow` | projects, venv, plugins, data |
| `pythonPath` | auto-detect | Python ≥ 3.10 used to create the venv |
| `sdkSpec` | `tongflow==0.3.0` | pip spec installed into the venv (`-e /path/to/sdk` for development) |
| `pluginOrg` | `https://github.com/tong-io` | where official plugins are cloned from |
| `pluginGitUrls` | `{}` | plugin id → git URL overrides |
| `env` | `{}` | environment for plugin processes (API keys); the Studio's key store (`env.json`) is merged over it |
| `maxConcurrentRuns` | `2` | |
| `httpPrefix` | `/tongflow` | |
| `locale` | `en` | canvas UI locale (`en` / `zh` / `ja` / `ko`) |

## Development

```sh
pnpm install
pnpm --filter dsh-tongflow build          # host lib/index.js + browser lib/client.js
pnpm --filter dsh-tongflow test
npx @deepseek-ai/dsh@next plugin --profile web add ./packages/dsh-tongflow   # link: install for hacking
```

The browser half is a single CJS bundle in dsh's `window.__ModuleLoader__` shape: only dsh's platform modules (react, cordis, slot kits) stay external; `tongflow/canvas`, @xyflow/react, zustand and use-intl are inlined (and deduplicated so React contexts match). See [`docs/design.md`](docs/design.md) and [`docs/naming.md`](docs/naming.md).

License: AGPL-3.0-only (same as TongFlow).
