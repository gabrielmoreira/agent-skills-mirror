# BioClaw

AI-powered biology research assistant. Inspired by [NanoClaw](https://github.com/qwibitai/nanoclaw). See [README.md](README.md) for setup.

## Quick Context

Single Node.js process that connects to WhatsApp, routes messages to Claude Agent SDK running in containers pre-loaded with biology research tools. Each group has isolated filesystem and memory.

## Key Files

### Core
| File | Purpose |
|------|---------|
| `src/index.ts` | Orchestrator: channel setup, agent invocation, main() |
| `src/message-loop.ts` | Message polling loop and recovery |
| `src/session-manager.ts` | State management (sessions, groups, timestamps) |
| `src/config.ts` | Trigger pattern, paths, intervals |
| `src/router.ts` | Message formatting and outbound routing |
| `src/group-folder.ts` | Group directory management, IPC dirs, snapshots |
| `src/group-queue.ts` | Per-group job queue with container lifecycle |

### Channels (`src/channels/`)
| File | Purpose |
|------|---------|
| `channels/registry.ts` | Channel factory pattern and lifecycle |
| `channels/whatsapp/channel.ts` | WhatsApp connection, auth, send/receive |
| `channels/whatsapp/auth.ts` | WhatsApp QR code auth flow |
| `channels/local-web/channel.ts` | Local web chat interface |
| `channels/local-web/html-template.ts` | Web UI HTML generation |
| `channels/local-web/vendor-scripts.ts` | Bundled JS libraries for web UI |

### Container
| File | Purpose |
|------|---------|
| `src/container-runner.ts` | Container lifecycle, output parsing, timeouts |
| `src/container-runtime.ts` | Low-level container operations (args, spawn) |
| `src/credential-proxy.ts` | Secret management (stdin injection, never on disk) |
| `container/Dockerfile` | Agent container with bio tools |

### Database (`src/db/`)
| File | Purpose |
|------|---------|
| `db/connection.ts` | SQLite initialization and schema |
| `db/messages.ts` | Chat metadata and message CRUD |
| `db/groups.ts` | Registered group CRUD |
| `db/tasks.ts` | Scheduled task CRUD |
| `db/sessions.ts` | Session CRUD |
| `db/state.ts` | Router state key-value store |
| `db/traces.ts` | Agent trace events |
| `db/migration.ts` | JSON file → SQLite migration |
| `db/index.ts` | Barrel re-exports |

### Other
| File | Purpose |
|------|---------|
| `src/ipc.ts` | IPC watcher and task processing |
| `src/task-scheduler.ts` | Runs scheduled tasks |
| `groups/{name}/CLAUDE.md` | Per-group memory (isolated) |

## Biology Tools Available in Container

### Command-Line Tools
| Tool | Command | Purpose |
|------|---------|---------|
| BLAST+ | `blastn`, `blastp`, `blastx`, `tblastn` | Sequence similarity search |
| SAMtools | `samtools` | SAM/BAM file manipulation |
| BEDTools | `bedtools` | Genome arithmetic |
| BWA | `bwa` | Short-read alignment |
| minimap2 | `minimap2` | Long-read / assembly alignment |
| FastQC | `fastqc` | Sequencing quality control |
| seqtk | `seqtk` | FASTA/FASTQ toolkit |

### Python Libraries
| Library | Import | Purpose |
|---------|--------|---------|
| BioPython | `from Bio import SeqIO, Blast, Entrez` | Sequence I/O, NCBI access, phylogenetics |
| pandas | `import pandas as pd` | Tabular data analysis |
| NumPy/SciPy | `import numpy as np; import scipy` | Numerical/statistical computing |
| matplotlib/seaborn | `import matplotlib.pyplot as plt; import seaborn as sns` | Data visualization |
| scikit-learn | `from sklearn import ...` | Machine learning |
| RDKit | `from rdkit import Chem` | Cheminformatics, molecular structures |
| PyDESeq2 | `from pydeseq2 import ...` | Differential gene expression |
| scanpy | `import scanpy as sc` | Single-cell RNA-seq analysis |
| AnnData | `import anndata as ad` | Annotated data matrices |
| pysam | `import pysam` | SAM/BAM file access from Python |

## Skills

| Skill | When to Use |
|-------|-------------|
| `/setup` | First-time installation, authentication, service configuration |
| `/customize` | Adding channels, integrations, changing behavior |
| `/debug` | Container issues, logs, troubleshooting |

## Development

Run commands directly—don't tell the user to run them.

```bash
npm run dev          # Run with hot reload
npm run build        # Compile TypeScript
./container/build.sh # Rebuild agent container (with bio tools)
```

Service management:
```bash
launchctl load ~/Library/LaunchAgents/com.bioclaw.plist
launchctl unload ~/Library/LaunchAgents/com.bioclaw.plist
```

## Container Build Cache

Apple Container's buildkit caches the build context aggressively. `--no-cache` alone does NOT invalidate COPY steps — the builder's volume retains stale files. To force a truly clean rebuild:

```bash
container builder stop && container builder rm && container builder start
./container/build.sh
```

Always verify after rebuild: `container run -i --rm --entrypoint wc bioclaw-agent:latest -l /app/src/index.ts`
