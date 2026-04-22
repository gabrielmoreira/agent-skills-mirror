# BioClaw Beginner's Guide

This document is for:

- Users who have never touched the command line, Docker, or environment variables
- Users who can boot BioClaw but don't really understand what `.env`, workspace, mounts, or the allowlist are
- Users who want BioClaw to access a specific directory on their host machine but have no idea what to edit
- Users who want to know what BioClaw can actually do and how to run real bioinformatics workflows through it

If all you want is to get BioClaw running, follow **Part 1: 5-minute quickstart** and stop there. The later sections are reference material you can come back to when you hit a specific problem.

---

## Table of Contents

**Part 1: 5-Minute Quickstart**
- [1. Prerequisites checklist (three things)](#1-prerequisites-checklist-three-things)
- [2. First-run command sequence](#2-first-run-command-sequence)
- [3. Make BioClaw do its first real task](#3-make-bioclaw-do-its-first-real-task)

**Part 2: Concepts You Need To Understand**
- [4. BioClaw in one sentence](#4-bioclaw-in-one-sentence)
- [5. What is a terminal / command line / shell](#5-what-is-a-terminal--command-line--shell)
- [6. What is Docker / container / image](#6-what-is-docker--container--image)
- [7. What is an API key / provider / model](#7-what-is-an-api-key--provider--model)
- [8. What is a workspace](#8-what-is-a-workspace)
- [9. What is a skill](#9-what-is-a-skill)
- [10. What is MCP](#10-what-is-mcp)
- [11. What are mounts and the allowlist (the "USB stick" analogy)](#11-what-are-mounts-and-the-allowlist-the-usb-stick-analogy)

**Part 3: Installation & Configuration**
- [12. System requirements and per-OS install steps](#12-system-requirements-and-per-os-install-steps)
- [13. The 4 key locations to remember](#13-the-4-key-locations-to-remember)
- [14. `.env` walkthrough](#14-env-walkthrough)

**Part 4: Day-to-Day Usage**
- [15. Starting and stopping BioClaw](#15-starting-and-stopping-bioclaw)
- [16. Common slash commands inside the chat](#16-common-slash-commands-inside-the-chat)
- [17. Most users don't need extra mounts at all](#17-most-users-dont-need-extra-mounts-at-all)
- [18. Switching provider and model](#18-switching-provider-and-model)
- [19. Workspace details](#19-workspace-details)

**Part 5: Real Bioinformatics Workflows**
- [20. Analyzing an uploaded CSV](#20-analyzing-an-uploaded-csv)
- [21. Running a BLAST homology search](#21-running-a-blast-homology-search)
- [22. Bulk RNA-seq differential expression](#22-bulk-rna-seq-differential-expression)
- [23. Single-cell RNA-seq analysis](#23-single-cell-rna-seq-analysis)
- [24. Querying PDB / UniProt / AlphaFold](#24-querying-pdb--uniprot--alphafold)
- [25. PubMed literature search + review](#25-pubmed-literature-search--review)
- [26. Generating a technical report (Typst / SEC)](#26-generating-a-technical-report-typst--sec)
- [27. Analyzing an SDS-PAGE gel image](#27-analyzing-an-sds-page-gel-image)
- [28. Letting BioClaw SSH to a remote server / HPC](#28-letting-bioclaw-ssh-to-a-remote-server--hpc)

**Part 6: Advanced — Mounting Host Directories**
- [29. When you need an allowlist](#29-when-you-need-an-allowlist)
- [30. Configuring the allowlist for the first time](#30-configuring-the-allowlist-for-the-first-time)
- [31. Where extra mounts actually land inside the container](#31-where-extra-mounts-actually-land-inside-the-container)
- [32. Attaching a host directory to a specific workspace](#32-attaching-a-host-directory-to-a-specific-workspace)
- [33. How to verify a mount worked](#33-how-to-verify-a-mount-worked)
- [34. Minimal working config example](#34-minimal-working-config-example)

**Part 7: Troubleshooting**
- [35. Stuck points new users hit most often](#35-stuck-points-new-users-hit-most-often)
- [36. General troubleshooting checklist](#36-general-troubleshooting-checklist)
- [37. Diagnostic command cheat sheet](#37-diagnostic-command-cheat-sheet)
- [38. Where to get help](#38-where-to-get-help)

**Part 8: Recommended Paths + Related Docs**
- [39. Three recommended paths for new users](#39-three-recommended-paths-for-new-users)
- [40. Related docs](#40-related-docs)

---

# Part 1: 5-Minute Quickstart

## 1. Prerequisites checklist (three things)

Before anything, you need these three things on your machine:

| Requirement | Purpose | Check command |
|---|---|---|
| **Node.js 20+** | Launches BioClaw's channels and web UI | `node -v` shows `v20.x.x` or higher |
| **Docker** | All bioinformatics analysis runs inside a Docker container | `docker -v` shows `Docker version 20.x` or higher |
| **One API key** | Credentials to call the large language model (Anthropic, OpenRouter, etc.) | Get one at [anthropic.com](https://console.anthropic.com/) or [openrouter.ai](https://openrouter.ai/keys) |

If any of these are missing, jump to [Section 12](#12-system-requirements-and-per-os-install-steps) for install steps.

> **Windows users:** see [docs/WINDOWS.md](./WINDOWS.md) first. BioClaw requires WSL2 on Windows — you cannot run it in native PowerShell or cmd.

## 2. First-run command sequence

Open a terminal (macOS/Linux: Terminal app; Windows: the Ubuntu shell inside WSL2) and run these **in order**:

```bash
# 1) Clone the repo into any folder you like
git clone https://github.com/Runchuan-BU/BioClaw.git
cd BioClaw

# 2) Install Node dependencies (takes a few minutes the first time)
npm install

# 3) Make your own copy of the environment file
cp .env.example .env

# 4) Edit .env and fill in your API key (see below)
#    Linux / macOS with nano or vim:
nano .env
#    Or if you have VS Code: code .env
```

In `.env`, find the line `ANTHROPIC_API_KEY=` and replace it with your real key:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-real-key
```

Save and exit (in nano: `Ctrl+O`, `Enter`, `Ctrl+X`).

Keep going:

```bash
# 5) Build the BioClaw container image (5–10 minutes the first time)
docker build -t bioclaw-agent:latest container/

# 6) Launch the local web UI
npm run web
```

When you see output like this, it booted correctly:

```
[bioclaw] Local web UI listening on http://localhost:3000
```

## 3. Make BioClaw do its first real task

1. Open your browser to `http://localhost:3000`
2. Type a greeting in the chat box and make sure the Agent replies
3. Drag a CSV or FASTA file into the chat to upload it
4. Ask BioClaw:

   ```text
   Take a look at this file. What does it contain, and what are the first 10 lines?
   ```

5. Wait for the reply. The Agent will run `head` / `cat` / or a Python snippet inside the container to read your file.

**Congratulations — you've just used BioClaw end-to-end.** You didn't touch allowlists, mounts, or SQL. Those are all advanced features you only need later.

---

# Part 2: Concepts You Need To Understand

## 4. BioClaw in one sentence

> **BioClaw is an AI assistant that "hides" bioinformatics analysis inside a chat window.**
>
> You ask questions or upload files in the chat UI; it runs BLAST, RNA-seq pipelines, BWA, samtools, scanpy, PyMOL, etc. inside a Docker container in the background, then sends plots and reports back to you.

So the correct mental model is not "install another piece of software" — it's "open a window where a bioinformatics-literate assistant does the work behind the scenes."

## 5. What is a terminal / command line / shell

If you've never seen these words, don't panic:

- A **terminal** is a black window where you type commands
- macOS: open Spotlight (`⌘+Space`) and search `Terminal`
- Linux: press `Ctrl+Alt+T`
- Windows: install WSL2, then search `Ubuntu` in the Start menu

Everything in this document that begins with `$` or appears inside a code block is a command you type into a terminal. You do not need to learn bash — **copy, paste, enter** is enough.

The absolute basics:

| Command | Meaning |
|---|---|
| `pwd` | What folder am I in? |
| `ls` | List everything in the current folder |
| `cd path` | Change folder |
| `cd ..` | Go up one folder |
| `cat filename` | Print the contents of a file |
| `Ctrl+C` | Cancel whatever is currently running |

## 6. What is Docker / container / image

An analogy:

- An **image** is a pre-packaged "environment disc" — it contains Python, BLAST, samtools, and a whole bioinformatics toolchain
- A **container** is what you get when you actually boot up that disc. It's isolated and does not pollute your host machine
- **Docker** is the software that manages images and containers

**All** BioClaw bioinformatics analysis happens inside containers. Why:

- Your host doesn't need BLAST, samtools, scanpy, etc. installed
- The analysis environment is isolated from your laptop
- It reproduces consistently on other machines

You only need to remember: `docker build` creates images, `docker run` starts containers. BioClaw starts containers automatically — **you almost never need to touch Docker commands yourself** except for debugging.

## 7. What is an API key / provider / model

- **Provider** = the company that serves the LLM. BioClaw supports four: **Anthropic**, **OpenRouter**, **OpenAI-compatible**, **Codex CLI**
- **API key** = your pass to that provider. Looks like `sk-ant-xxxx` or `sk-or-v1-xxxx`. Goes in `.env`
- **Model** = a specific model from that provider, e.g. `claude-opus-4`, `gemini-2.5-flash`, `deepseek-chat-v3.1`

A chat thread in BioClaw can **switch between providers / models**. Once multiple keys are configured, just type `/provider switch openrouter` and `/model switch google/gemini-2.5-flash` in chat.

**Where to get an API key:**

| Provider | Link | Notes |
|---|---|---|
| Anthropic | [console.anthropic.com](https://console.anthropic.com/) | Native Claude, highest quality; needs an international credit card |
| OpenRouter | [openrouter.ai/keys](https://openrouter.ai/keys) | One key gives access to Claude / Gemini / DeepSeek / GPT and dozens more; supports CN payment methods |
| DeepSeek | [platform.deepseek.com](https://platform.deepseek.com/) | China-based, supports WeChat Pay / Alipay |

## 8. What is a workspace

A **workspace** is a folder that acts as the working directory for "this chat" or "this group".

- Files you upload land in some workspace
- The Agent's default input/output is there
- Different chats / groups can use different workspaces and stay isolated from each other

On your host, the workspace path typically looks like:

```
BioClaw/groups/<workspace-name>/
```

Inside the container, it's mounted at:

```
/workspace/group
```

So when the Agent says "the file is at `/workspace/group/xxx.csv`", that's just `BioClaw/groups/<workspace>/xxx.csv` on your host.

## 9. What is a skill

A **skill** is a pre-built workflow for one class of bioinformatics tasks. Each skill is a `SKILL.md` file that tells the Agent: "when you see X kind of request, use these tools in this order."

BioClaw ships with **40+ bioinformatics skills**, covering:

- **Sequences / databases**: BLAST search, UniProt / PDB / AlphaFold / KEGG / Reactome / ClinVar / GEO / InterPro / Ensembl / OpenTarget lookups
- **Omics analysis**: bulk RNA-seq DE, scRNA-seq, ATAC-seq, ChIP-seq, metagenomics, proteomics
- **Visualization & reports**: publication-quality plots (volcano, heatmap, scatter), automated slide decks, manuscript outlines/drafts, Typst technical reports
- **Wet-lab helpers**: SDS-PAGE gel image review, PubMed search, novelty check
- **Meta / system**: task routing, dataset discovery, human-in-the-loop approvals

**The good news: you don't have to memorize skill names.** The Agent picks the right one based on your question. Your job is to **describe the task clearly**.

Type `/skills` in chat to see every installed skill.

There's also a [**Bioclaw_Skills_Hub**](https://github.com/zongtingwei/Bioclaw_Skills_Hub) with 70+ community skills, pulled dynamically when needed.

## 10. What is MCP

**MCP (Model Context Protocol)** is the protocol BioClaw uses internally to let the Agent call tools.

**You don't need to care about it.** It's pure plumbing — only developers touch it. Using BioClaw does not require understanding MCP any more than using WeChat requires understanding TCP/IP.

The only time you'll see MCP mentioned in passing is around `send_image` / `send_file` (the Agent proactively sends a file or plot) — those use MCP under the hood, but you just ask and they happen.

## 11. What are mounts and the allowlist (the "USB stick" analogy)

This is the one spot that trips up most new users. Analogy:

- The **container** is an isolated, clean machine
- A **mount** is like **plugging a USB stick** into that machine — you attach a folder on your host so the container can see your real files
- The **allowlist** is a **permission form** — before you can plug anything in, you have to fill out the form listing which folders are eligible to be plugged in. Anything not on the form is rejected

Why does the allowlist exist? **Because mounts are dangerous:**
- If you accidentally mount `~/.ssh`, the Agent can read your SSH private keys
- If you mount `/`, the Agent has access to your entire disk

So BioClaw's design is: by default **only folders you've explicitly listed** can be mounted. That's what `~/.config/bioclaw/mount-allowlist.json` is for.

**But here's the thing** — most users don't need mounts. If you're just uploading files in the web UI and letting BioClaw analyze them, you **do not need** an allowlist. See [Section 17](#17-most-users-dont-need-extra-mounts-at-all).

---

# Part 3: Installation & Configuration

## 12. System requirements and per-OS install steps

### 12.1 macOS

**Needs:** macOS 12+, any CPU (M1/M2/M3 or Intel).

```bash
# Install Homebrew (if you don't have it)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js 20
brew install node@20

# Install Docker Desktop
brew install --cask docker

# Launch Docker Desktop from Applications
# First launch will ask you to log in or skip
```

Verify:

```bash
node -v     # should print v20.x.x
docker -v   # should print Docker version 24.x or similar
```

### 12.2 Linux (Ubuntu / Debian)

```bash
# Install Node.js 20 from the official NodeSource repo
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER
# Log out / back in, or temporarily:
newgrp docker
```

Verify the same way.

### 12.3 Windows

You **cannot** run BioClaw natively on Windows. Install WSL2 + Ubuntu, then follow the Linux steps in 12.2.

Full instructions: [docs/WINDOWS.md](./WINDOWS.md).

### 12.4 HPC / cluster (no Docker access)

BioClaw supports **Apptainer/Singularity** as a Docker replacement. See [docs/APPTAINER.md](./APPTAINER.md) and [docs/CLUSTER_DEPLOYMENT.md](./CLUSTER_DEPLOYMENT.md).

## 13. The 4 key locations to remember

Assuming you cloned BioClaw to:

```bash
/path/to/BioClaw
```

The four places you'll touch most often are:

1. **Project root**

   `BioClaw/` itself. Contains `package.json`, `README`, `container/`, `groups/`, `store/`. Almost every command runs from here.

2. **`.env` file**

   ```bash
   /path/to/BioClaw/.env
   ```

   Controls which provider/API you use (Anthropic, OpenRouter, OpenAI-compatible, Codex) and which messaging channels are enabled.

3. **Workspace directory**

   ```bash
   /path/to/BioClaw/groups/<workspace-name>/
   ```

   BioClaw's default working directory, mounted into the container as `/workspace/group`. Files you upload end up here.

4. **Mount allowlist file**

   **Note: this file is NOT in the project — it lives under your home directory:**

   ```bash
   ~/.config/bioclaw/mount-allowlist.json
   ```

   Controls which host directories are **permitted** to be mounted into containers. Without this file you cannot mount any host directory.

## 14. `.env` walkthrough

### 14.1 Minimal working config (pick one)

**Option A: Anthropic (simplest, native Claude)**

```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-key
```

**Option B: OpenRouter (recommended — one key for many models)**

```bash
MODEL_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=google/gemini-2.5-flash
```

**Option C: OpenAI-compatible (DeepSeek / local LLM / proxy services)**

```bash
MODEL_PROVIDER=openai-compatible
OPENAI_COMPATIBLE_API_KEY=your-key
OPENAI_COMPATIBLE_BASE_URL=https://api.deepseek.com/v1
OPENAI_COMPATIBLE_MODEL=deepseek-chat
```

### 14.2 Enable the local web UI

```bash
ENABLE_LOCAL_WEB=true
LOCAL_WEB_PORT=3000
```

With those two lines, `npm run web` will serve the web chat UI at `http://localhost:3000`.

### 14.3 Messaging channels (optional)

BioClaw supports these channels — all opt-in; not enabling them has no effect on core functionality:

| Channel | `.env` switch | Setup difficulty |
|---|---|---|
| WhatsApp | `ENABLE_WHATSAPP=true` | QR login, simplest |
| WeCom (企业微信) | `WECOM_BOT_ID=` + `WECOM_SECRET=` | Needs admin to create a bot |
| Feishu / Lark | `FEISHU_APP_ID=` + `FEISHU_APP_SECRET=` | Needs a custom app |
| Discord | `DISCORD_BOT_TOKEN=` | Needs a Bot application |
| Slack | `SLACK_BOT_TOKEN=` + `SLACK_APP_TOKEN=` | Socket Mode app on api.slack.com |
| QQ official bot | `QQ_APP_ID=` + `QQ_CLIENT_SECRET=` | Application approval required |
| Personal WeChat | `ENABLE_WECHAT=true` | QR login |

Per-channel details: [docs/CHANNELS.md](./CHANNELS.md).

### 14.4 Container runtime (usually leave alone)

```bash
CONTAINER_RUNTIME=docker          # default; on HPC use apptainer
CONTAINER_IMAGE=bioclaw-agent:latest
```

---

# Part 4: Day-to-Day Usage

## 15. Starting and stopping BioClaw

### 15.1 Three ways to start

From the project root:

```bash
# Local web UI only (most common)
npm run web

# Start every configured channel (WhatsApp / Feishu / Discord / web, etc.)
npm run dev

# Run in the background (long-running use)
nohup npm run dev > bioclaw.log 2>&1 &
```

### 15.2 Stopping

- Foreground run: `Ctrl+C` in the terminal
- Background (`nohup`): find the PID via `ps aux | grep bioclaw`, then `kill <pid>`

### 15.3 Restarting

Most config changes (`.env`, allowlist, `container_config`) require a restart:

```bash
# 1) Ctrl+C to stop
# 2) Start again
npm run web     # or npm run dev
```

### 15.4 Cleaning up Docker containers (occasionally needed)

If a container is stuck or in a weird state:

```bash
# See all bioclaw-related containers
docker ps -a | grep bioclaw

# Stop and remove one
docker rm -f <container-id>

# Nuke all containers (only if no other Docker projects!)
docker ps -aq | xargs docker rm -f
```

## 16. Common slash commands inside the chat

BioClaw is **controlled from within the chat window**, not from the terminal. Key commands:

### 16.1 Status

```text
/status       # thread, provider, model, workspace, cwd
/doctor       # health check: provider reachability, container status, etc.
/workspace current
/dir show
```

### 16.2 Switch provider and model

```text
/provider list                          # list configured providers
/provider switch openrouter             # switch to OpenRouter (must be set up in .env)
/model show                             # show current model
/model switch google/gemini-2.5-flash   # switch model (OpenRouter only)
```

### 16.3 Thread management

```text
/threads           # list all threads in this chat
/new               # create a new thread
/use <thread-id>   # switch to a thread
/rename important-project   # rename current thread
/archive           # archive current thread
```

### 16.4 Workspace & working directory

```text
/workspace current
/workspace bind local-web
/dir analysis       # default this thread's working dir to analysis/
/dir reset          # back to workspace root
```

### 16.5 Skills

```text
/skills      # list installed skills, mark preferences
/commands    # save shortcuts for recurring workflows
/alias       # set command aliases
```

### 16.6 SSH / remote

```text
/ssh list    # list host aliases from ~/.ssh/config
```

Combined with SSH, you can let BioClaw run commands on a remote HPC directly — see [Section 28](#28-letting-bioclaw-ssh-to-a-remote-server--hpc).

### 16.7 Agent memory

```text
/memory set I'm a tumor immunology researcher; most of my experiments are in mice
```

Sends this into the Agent's system memory so subsequent replies carry that context.

## 17. Most users don't need extra mounts at all

If your needs are:

- Chat in the local web UI
- Upload images, CSVs, FASTA/FASTQ, PDFs, archives
- Let BioClaw analyze those uploads

then you **don't need** an allowlist and you **don't need** `additionalMounts`.

Uploaded files go into the current workspace automatically — the Agent reads them from `/workspace/group` inside the container.

You only need "extra mounts" when:

- Your data already lives in a big directory on the host and you don't want to copy it into `groups/`
- You want BioClaw to read a shared data disk like `/mnt/lab-data` directly
- You want BioClaw to write results back to a specific host directory

Full mount instructions in [Part 6](#part-6-advanced--mounting-host-directories).

## 18. Switching provider and model

Two flavors of "switch":

### 18.1 Switch per thread (temporary)

Inside the chat:

```text
/provider list
/provider switch openrouter
/model show
/model switch google/gemini-2.5-flash
```

Useful for:

- Switching models on the fly (one is better at code, another at writing)
- Different threads in the same BioClaw instance using different providers
- A/B comparing different models on the same task

Notes:

- Only works if the target provider's API key is configured in `.env`
- `anthropic` does not support per-thread model switching the way OpenRouter does

### 18.2 Switch the whole instance default (permanent)

Edit `.env`, then restart BioClaw:

```bash
# 1) Edit .env: change MODEL_PROVIDER / API_KEY / MODEL
# 2) Ctrl+C
# 3) Start again
npm run web
```

Useful for:

- Making the entire instance default to OpenRouter
- Rotating API keys or base URLs

## 19. Workspace details

Inside the container you'll see these paths:

| Container path | Meaning |
|---|---|
| `/workspace/group` | The current workspace's working directory (most common) |
| `/workspace/project` | The full BioClaw project root; only present for the `main` workspace by default |
| `/workspace/global` | Shared directory across groups, if `groups/global` exists on host |
| `/workspace/ipc` | BioClaw's internal IPC directory (intermediate files) |
| `/workspace/extra/...` | Extra mounted host directories (see Part 6) |

Most important takeaway:

- **Your default working directory is almost always `/workspace/group`**
- Uploaded files typically land there or in a subdirectory

### 19.1 Check current workspace

```text
/workspace current
/status
/dir show
```

### 19.2 Bind a thread to a different workspace

```text
/workspace bind lab-project-2024
```

### 19.3 Change thread default working directory

Work inside `analysis/` by default:

```text
/dir analysis
```

Reset to workspace root:

```text
/dir reset
```

---

# Part 5: Real Bioinformatics Workflows

All examples below assume you finished Part 1 and BioClaw's local web UI is running.

## 20. Analyzing an uploaded CSV

**Scenario:** You have a gene expression matrix as CSV and want an overview.

**Steps:**

1. Drag the CSV into the chat
2. Ask:

   ```text
   This is a gene expression matrix. Please:
   1) Tell me the number of rows/columns and the header
   2) Compute per-column summary stats (mean, std, missing fraction)
   3) Plot a sample-sample correlation heatmap
   ```

**What the Agent does:** reads the file in `pandas` inside the container, draws the heatmap with `seaborn`, and sends the image back into the chat.

## 21. Running a BLAST homology search

**Scenario:** You have an unknown protein sequence and want to find homologs.

**Steps:**

```text
Here is a protein sequence. Please:
1) Run BLAST against NCBI nr (E-value < 1e-10)
2) List the top 5 hits with species source
3) Tell me what class of enzyme this is most likely to be

>my_unknown
MKVLWAALLVTFLAGCQAKVEQAVETEPEPELRQQTEWQSGQRWELALGRFWDYLRWVQTL
SEQVAKKQKEEPALEVVEQE
```

**Skill used:** `blast-search`.

## 22. Bulk RNA-seq differential expression

**Scenario:** Treatment vs control count matrix + metadata.

**Steps:**

1. Upload two files:
   - `counts.tsv` — gene × sample count matrix
   - `coldata.csv` — two columns: sample, condition
2. Ask:

   ```text
   I have bulk RNA-seq counts and sample metadata. Run PyDESeq2 DE analysis,
   compare treated vs control, and give me:
   1) Significant DE genes (adj-p < 0.05, |log2FC| > 1)
   2) Volcano plot
   3) GO enrichment for the top 20 up- and down-regulated genes
   ```

**Skills used:** `differential-expression` + `bio-figure-design`.

## 23. Single-cell RNA-seq analysis

**Scenario:** 10x Genomics `filtered_feature_bc_matrix/` folder.

**Steps:**

1. Zip the folder and upload (or use a mount — see Part 6)
2. Ask:

   ```text
   This is a 10x scRNA-seq dataset. Please run a full scanpy preprocessing:
   1) QC (min_genes=200, min_cells=3, pct_mt<20)
   2) Normalize + log
   3) HVG + PCA + UMAP
   4) Leiden clustering (resolution=0.5)
   5) Cell type auto-annotation
   6) UMAP plot + top marker genes per cluster
   ```

**Skills used:** `scrna-preprocessing-clustering` + `cell-annotation`.

## 24. Querying PDB / UniProt / AlphaFold

**Scenario:** You want structural info about a gene.

**Steps:**

```text
For the TP53 protein:
1) What is its UniProt ID and full sequence length?
2) What PDB structures exist? Recommend 2-3 representative ones
3) How does the AlphaFold prediction score (mean pLDDT)?
4) Mark the DNA-binding and tetramerization domains on the sequence
```

**Skills used:** `query-uniprot` + `query-pdb` + `query-alphafold` in parallel.

## 25. PubMed literature search + review

**Scenario:** Quick literature overview of a field.

**Steps:**

```text
Do a literature review on "CRISPR-Cas13 for RNA editing":
1) Search PubMed 2022-2025, take the 30 most-cited papers
2) Cluster them into: mechanism, therapeutic applications, safety concerns, new variants
3) 200-word summary per cluster with 3-5 representative citations
```

**Skills used:** `pubmed-search` + `bio-manuscript-outline`.

## 26. Generating a technical report (Typst / SEC)

**Scenario:** You just finished an experiment and want a formal report.

**Steps:**

```text
Based on the DE analysis we just did, generate a Typst technical report with:
background, methods, results, discussion, conclusion, and all figures.
Output it as PDF.
```

**Skills used:** `sec-report` + `report-template`. Renders via Typst into a PDF.

## 27. Analyzing an SDS-PAGE gel image

**Scenario:** You took a photo of an SDS-PAGE gel and want the result read.

**Steps:**

1. Upload the gel photo
2. Ask:

   ```text
   This is an SDS-PAGE gel. Please:
   1) Identify the ladder and each sample lane
   2) Estimate the size and abundance of the target band (~55 kDa)
   3) Call out any obvious degradation or non-specific bands
   ```

**Skill used:** `sds-gel-review`.

## 28. Letting BioClaw SSH to a remote server / HPC

**Scenario:** Data is too large to upload locally — let BioClaw work on a remote machine instead.

**Prerequisites:**

1. Configure host aliases in your local `~/.ssh/config`, e.g.:

   ```ssh-config
   Host hpc-login
       HostName 10.0.0.42
       User your-username
       IdentityFile ~/.ssh/id_rsa
   ```

2. Optionally restrict which hosts BioClaw may access via `.env`:

   ```bash
   BIOCLAW_SSH_ALLOWED_HOSTS=hpc-login,lambda-cloud-a100
   ```

**Usage:**

```text
/ssh list
```

Lists available hosts. Then ask:

```text
On hpc-login, run `samtools flagstat /scratch/data/sample.bam`
and report the output back to me
```

The Agent SSHes to the remote machine, runs the command, and brings the output back.

---

# Part 6: Advanced — Mounting Host Directories

This section is **only needed if you actually need to mount host directories**. If you're just uploading files, skip it.

## 29. When you need an allowlist

Only when you want to mount **an extra host directory** into the container.

Example: you have data at

```bash
/home/you/lab-data
```

on your host, and you want BioClaw to see it from inside the container. You cannot just "say mount this." Two steps are required:

1. First, allow this directory's parent root in `~/.config/bioclaw/mount-allowlist.json`
2. Then, declare which directory to mount in a workspace/group's `container_config`

If step 1 is missing, step 2 is rejected.

## 30. Configuring the allowlist for the first time

### 30.1 Create the config directory

```bash
mkdir -p ~/.config/bioclaw
```

### 30.2 Create the allowlist file

```bash
cat > ~/.config/bioclaw/mount-allowlist.json <<'EOF'
{
  "allowedRoots": [
    {
      "path": "~/lab-data",
      "allowReadWrite": false,
      "description": "Experimental data dir, read-only"
    },
    {
      "path": "~/lab-results",
      "allowReadWrite": true,
      "description": "Results output dir, writable"
    }
  ],
  "blockedPatterns": [
    "password",
    "secret",
    "token"
  ],
  "nonMainReadOnly": true
}
EOF
```

Field meanings:

- `allowedRoots`
  The list of host root directories that are allowed to be mounted. Only paths *under* these roots may be attached.

- `allowReadWrite`
  Whether that root is allowed to be writable at all.

- `blockedPatterns`
  Even if a path is under `allowedRoots`, if it matches any of these patterns it's rejected. BioClaw also has hard-coded bans for `.ssh`, `.env`, `credentials`, etc. that cannot be overridden.

- `nonMainReadOnly`
  If `true`, **non-main workspaces** are forced read-only even when they ask for write access.

### 30.3 Critical: restart BioClaw after editing the allowlist

The allowlist is cached in memory. Restart after every edit:

```bash
# Ctrl+C
npm run dev    # or npm run web
```

## 31. Where extra mounts actually land inside the container

Extra mounts don't get attached at your literal host path.

BioClaw always mounts them under:

```bash
/workspace/extra/<containerPath>
```

Example:

```json
{
  "hostPath": "~/lab-data/projectA",
  "containerPath": "projectA-data",
  "readonly": true
}
```

Inside the container, that's seen as:

```bash
/workspace/extra/projectA-data
```

**Not** `/lab-data/projectA`, and **not** `/workspace/group/projectA-data`. This layout intentionally prevents the Agent from confusing mounted directories with the workspace's real files.

## 32. Attaching a host directory to a specific workspace

### 32.1 Identify which workspace to edit

List registered chats/workspaces:

```bash
npm run agents -- chats
```

Or query the database directly:

```bash
sqlite3 store/messages.db "SELECT jid, name, folder, workspace_folder FROM registered_groups;"
```

You'll see something like:

```text
local-web@local.web|Local Web Chat|local-web|local-web
...
```

Typically you'll edit a `folder`, e.g.:

- `main`
- `local-web`
- a specific group's folder

### 32.2 Write `container_config` via SQL

Add two extra mounts to the `local-web` workspace:

```bash
sqlite3 store/messages.db <<'EOF'
UPDATE registered_groups
SET container_config = json('{
  "additionalMounts": [
    {
      "hostPath": "~/lab-data/projectA",
      "containerPath": "projectA-data",
      "readonly": true
    },
    {
      "hostPath": "~/lab-results/projectA",
      "containerPath": "projectA-results",
      "readonly": false
    }
  ]
}')
WHERE folder = 'local-web';

SELECT folder, container_config
FROM registered_groups
WHERE folder = 'local-web';
EOF
```

Field meanings:

- `hostPath` — real directory on the host; supports `~`
- `containerPath` — inside the container this becomes `/workspace/extra/<containerPath>`. Don't use absolute paths or `..`
- `readonly` — `true` for read-only, `false` for read-write. Final writability still depends on the allowlist's `allowReadWrite` and `nonMainReadOnly`

### 32.3 Restart BioClaw again

`registered_groups.container_config` is read at startup, so restart after edits.

## 33. How to verify a mount worked

Recommended check order.

### 33.1 Check BioClaw status

In the chat:

```text
/status
/doctor
```

### 33.2 Have the Agent list the directory

In the chat:

```text
List the contents of /workspace/extra
```

Or:

```text
Show the directory tree of /workspace/extra/projectA-data, up to depth 2
```

### 33.3 Check container logs

BioClaw logs the mount configuration at startup:

```bash
docker ps
docker logs <container-name>
```

## 34. Minimal working config example

### 34.1 `.env`

```bash
MODEL_PROVIDER=openrouter
OPENROUTER_API_KEY=your-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=google/gemini-2.5-flash

ENABLE_LOCAL_WEB=true
LOCAL_WEB_PORT=3000
```

### 34.2 allowlist

```json
{
  "allowedRoots": [
    {
      "path": "~/lab-data",
      "allowReadWrite": false,
      "description": "Read-only data dir"
    },
    {
      "path": "~/lab-results",
      "allowReadWrite": true,
      "description": "Results dir"
    }
  ],
  "blockedPatterns": [
    "password",
    "secret",
    "token"
  ],
  "nonMainReadOnly": true
}
```

### 34.3 `container_config`

```json
{
  "additionalMounts": [
    {
      "hostPath": "~/lab-data/projectA",
      "containerPath": "projectA-data",
      "readonly": true
    },
    {
      "hostPath": "~/lab-results/projectA",
      "containerPath": "projectA-results",
      "readonly": false
    }
  ]
}
```

---

# Part 7: Troubleshooting

## 35. Stuck points new users hit most often

### 35.1 "I added additionalMounts but the container doesn't see them"

Five common causes:

1. You didn't create `~/.config/bioclaw/mount-allowlist.json`
2. `hostPath` doesn't actually exist on the host (typo, or `~` not expanding)
3. `hostPath` isn't under any `allowedRoots` entry
4. You didn't restart BioClaw after editing the allowlist or `container_config`
5. `containerPath` was an absolute path or contained `..`

### 35.2 "I asked for read-write but it's read-only"

Two possibilities:

1. The relevant `allowedRoots` entry has `allowReadWrite: false`
2. `nonMainReadOnly: true` and your current workspace isn't `main`

### 35.3 "Why can't I mount `~/.ssh`, `.env`, or credential folders?"

Intentional security restriction. BioClaw blocks these. The design assumption is: if you genuinely need to SSH somewhere, use `/ssh list` (see [Section 28](#28-letting-bioclaw-ssh-to-a-remote-server--hpc)) rather than exposing your private key to the container.

### 35.4 "I only want BioClaw to process a few files — do I really need mounts?"

**No.** The simplest approach is always:

- Upload the file via the local web UI, or
- Manually drop it into `groups/<workspace>/`

This is the least error-prone and most secure path.

### 35.5 "The Agent froze and isn't responding"

Typical causes:

1. **API key invalid or exhausted** — rotate the key in `.env` and restart
2. **Network unreachable** — `/doctor` will flag the provider as unreachable
3. **Container image missing** — `docker images | grep bioclaw` should show it; if not, rebuild
4. **Container is pulling models or deps** — first-run can take a while; check `docker logs <container>`

### 35.6 "Web UI is blank / won't load"

1. Confirm `.env` has `ENABLE_LOCAL_WEB=true`
2. Confirm `LOCAL_WEB_PORT=3000` isn't used by another process (`lsof -i :3000`)
3. Check the startup log for `Local web UI listening on...`
4. Make sure you're visiting `http://localhost:3000`, not `https`

## 36. General troubleshooting checklist

When you hit "why can't it see my file" / "why doesn't the provider work" / "why is it read-only," run through this in order:

1. Is `.env` correct (API key, `MODEL_PROVIDER`, URL)?
2. Did you restart `npm run dev` / `npm run web` after changes? (Everything requires a restart.)
3. Are `/status` and `/doctor` healthy?
4. Which workspace is active (`/workspace current`)?
5. Should the file have been dropped into `groups/<workspace>/` instead?
6. If using extra mounts:
   - Does the allowlist file exist?
   - Does `hostPath` exist?
   - Is it under `allowedRoots`?
   - Is it being forced read-only (`nonMainReadOnly` + non-main workspace)?
7. Is the container even running: `docker ps | grep bioclaw`?
8. Anything in the container logs: `docker logs <container>`?

## 37. Diagnostic command cheat sheet

### 37.1 Inside chat

```text
/status                  # thread, provider, model, workspace, cwd
/doctor                  # full self-test (provider reachability, container state)
/workspace current
/dir show
/threads
/skills
```

### 37.2 In the terminal

```bash
# See BioClaw processes
ps aux | grep -E "node|bioclaw" | grep -v grep

# See Docker containers
docker ps                        # running
docker ps -a                     # including stopped
docker logs <container-id>       # container logs
docker exec -it <container-id> bash   # shell into the container

# Check the BioClaw image exists
docker images | grep bioclaw

# Query the SQLite DB
sqlite3 store/messages.db "SELECT folder, container_config FROM registered_groups;"

# Port usage
lsof -i :3000                    # Linux / macOS
netstat -ano | findstr :3000     # Windows

# Node / Docker versions
node -v && docker -v
```

### 37.3 Reset to clean state

If you've broken things badly and want to start fresh:

```bash
# Stop BioClaw (Ctrl+C)

# Clear containers
docker ps -aq | xargs docker rm -f

# Rebuild the image
docker build -t bioclaw-agent:latest container/

# (Optional) reset the session DB — WARNING: loses all chat history and workspace bindings
rm -rf store/messages.db

# Restart
npm run web
```

## 38. Where to get help

1. **Official docs** — see `docs/` for [CHANNELS](./CHANNELS.md), [WINDOWS](./WINDOWS.md), [SECURITY](./SECURITY.md), [DASHBOARD](./DASHBOARD.md), [CLUSTER_DEPLOYMENT](./CLUSTER_DEPLOYMENT.md), [CUSTOM_SKILLS](./CUSTOM_SKILLS.md)
2. **GitHub Issues** — [github.com/Runchuan-BU/BioClaw/issues](https://github.com/Runchuan-BU/BioClaw/issues). Before opening an issue, paste the output of `/doctor` and the last ~50 lines of `docker logs`
3. **WeChat group** — scan the QR code on the [homepage](https://ivegotmagicbean.github.io/BioClaw-Page/)
4. **Papers** — architecture details on [bioRxiv](https://www.biorxiv.org/content/10.64898/2026.04.11.716807v1) and [arXiv](https://arxiv.org/abs/2507.02004)

---

# Part 8: Recommended Paths + Related Docs

## 39. Three recommended paths for new users

If this is your first time, pick one:

### Path A: Simplest (99% of new users should take this)

1. Configure `.env` (pick Anthropic or OpenRouter)
2. `docker build -t bioclaw-agent:latest container/`
3. `npm run web`
4. Upload a file in the local web UI
5. Ask BioClaw to analyze it

This path does **not** need an allowlist, SQL, or extra mounts.

### Path B: You already have host data directories (large datasets)

1. Configure `.env`
2. Create `~/.config/bioclaw/mount-allowlist.json`
3. Mount just a single read-only directory first (safer — no accidental writes)
4. Edit `registered_groups.container_config`
5. Restart BioClaw
6. Verify `/workspace/extra/...` is visible in chat

### Path C: You want BioClaw to write results back to a host directory

On top of Path B, add:

1. Set `allowReadWrite: true` for the relevant `allowedRoots` entry
2. Set `readonly: false` in the corresponding `additionalMounts` entry

If it's still read-only, the first thing to check is `nonMainReadOnly: true` on a non-main workspace.

## 40. Related docs

- [README.md](../README.md) — project overview and quick intro
- [docs/CHANNELS.md](./CHANNELS.md) — per-channel setup for WhatsApp / Feishu / WeCom / Discord / Slack / QQ / WeChat
- [docs/WINDOWS.md](./WINDOWS.md) — WSL2 setup for Windows users
- [docs/SECURITY.md](./SECURITY.md) — full trust model and security boundaries
- [docs/DEBUG_CHECKLIST.md](./DEBUG_CHECKLIST.md) — deeper troubleshooting checklist
- [docs/DASHBOARD.md](./DASHBOARD.md) — Lab Trace visualization (what the Agent actually did)
- [docs/CUSTOM_SKILLS.md](./CUSTOM_SKILLS.md) — how to author your own skills
- [docs/CLUSTER_DEPLOYMENT.md](./CLUSTER_DEPLOYMENT.md) — HPC / cluster deployment
- [docs/APPTAINER.md](./APPTAINER.md) — Apptainer/Singularity for environments without Docker

If you're already up and running and just want to explore advanced deployment, security, HPC, or custom skills, those docs are the next step.

If you just wanted to get BioClaw running for real bioinformatics work, **this guide is enough**.
