# WEB-Resume - Resume Service Module AI Instructions  
  
**Scope**: Authoritative for web-resume module  
**Last Updated**: 2026-05-12  
  
> **Authority**: DEEP - Authoritative for all work inside `web-resume/`  
> See `.github/copilot-instructions.md` for how the AI-INSTRUCT hierarchy works. 
  
---  
  
## Contents  
  
| Section | What's here |  
|---------|-------------|  
| [Deployment Modes](#deployment-modes) | Four project-wide deployment modes |
| [Project Overview](#project-overview) | What this module is and does |
| [Workspace Layout](#workspace-layout) | Directory structure |
| [Critical Constraints](#critical-constraints) | Safety rules for data protection |
| [Technology Stack](#technology-stack) | Frontend, backend, database, LLM |
| [Naming Conventions](#naming-conventions) | File and code naming patterns |

---

## Deployment Modes

This module (WEB-Resume) is deployed as part of **PDS-Master-001's four deployment modes**. Your working instructions come from the active mode, following the depth-priority hierarchy.

**Active mode instructions:**

→ **[`.deployment/dev-local/.ai/instruct.md`](../../.deployment/dev-local/.ai/instruct.md)** — Local development (http only, no TLS)

→ **[`.deployment/dev-lan/.ai/instruct.md`](../../.deployment/dev-lan/.ai/instruct.md)** — LAN sharing (self-signed HTTPS)

→ **[`.deployment/prod-self-serve/.ai/instruct.md`](../../.deployment/prod-self-serve/.ai/instruct.md)** — Production self-serve (DDNS + Let's Encrypt)

→ **[`.deployment/prod-railway/.ai/instruct.md`](../../.deployment/prod-railway/.ai/instruct.md)** — Railway cloud hosting

**When working in WEB-Resume**: The active deployment mode's instructions override this file. If you're in `dev-local` mode, follow `.deployment/dev-local/.ai/instruct.md`. If in `prod-self-serve`, follow that mode's file.

**Quick start:**
```powershell
./ResumeServer/start-dev-modes.ps1 -Mode dev-local
./ResumeServer/start-dev-modes.ps1 -Mode dev-lan
./ResumeServer/start-dev-modes.ps1 -Mode prod-self-serve
./ResumeServer/start-dev-modes.ps1 -Mode prod-railway
```
  
**Resume-Suite** is a self-hosted multi-user resume drafting service powered by a local LLM (LLM Studio). It serves a small number of invited users over a local network and provides a full pipeline: job description capture (via Chrome extension), AI-driven analysis and resume generation, ATS scoring, and final DOCX/PDF export. The pipeline mirrors the existing `K:\Resume` workflow but operates as a web service with per-user workspaces. 
  
---  
  
## Workspace Layout  
  
```  
WEB-Resume/  
��� .github/  
�   ��� copilot-instructions.md     META: explains the AI-INSTRUCT hierarchy  
�   ��� prompts/                    AI slash-command prompt files  
��� AI-INSTRUCT/                    Global shared reference instructions  
�   ��� AI-CONVENTIONS.md           Naming, file organization  
�   ��� AI-MAINTENANCE.md           .old, .archive, .dev.md patterns  
��� AI-INSTRUCT.md                  This file (legacy - see .ai/instruct.md)  
��� Resume/                         READ-ONLY reference copy (do not edit)  
��� ResumeServer/                   The full server application  
��� UserData/                       Per-user file workspaces (managed by server)  
    ��� <username>/  
        ��� Parts/                  Resume building blocks (uploaded by user)  
        ��� Listings/               Job descriptions  
        ��� Current/                Generated artifacts (NNNN-listing-name/)  
``` 
  
---  
  
## Critical Constraints  
  
### Do Not Modify Source References  
  
`Resume/` is a read-only reference copy. Never edit files inside it. Copy content into the appropriate layer if needed.  
  
### UserData Is Not Source Code  
  
`UserData/` is runtime data owned by the server. Never commit it to git. It must be in `.gitignore`.  
  
### All AI Work Goes Through the Server  
  
No component should call LLM Studio directly except `ResumeServer/server/services/llm-client.js`. 
  
### The Database Is Never Reset or Dropped  
  
**CRITICAL - do not override under any circumstances.**  
  
The PostgreSQL database contains live user data (listings, workflow jobs, artifacts, accounts). Never run `DROP TABLE`, `DROP DATABASE`, `TRUNCATE`, `DELETE FROM` without a `WHERE` clause, or any migration that destroys rows, unless the user has explicitly confirmed they want specific data permanently deleted and understands it is irreversible.  
  
If schema changes are needed, use `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` or additive migrations only. `init-database.js` must never drop or truncate existing tables.  
  
> ** [Never Reset Databases](../../.ai/maintenance.md#never-reset-databases)** - complete policy on database safety rules. 
  
---  
  
## Technology Stack  
  
| Layer | Technology |  
|-------|------------|  
| Frontend | React 18 + Vite |  
| Backend | Node.js + Express (ESM) |  
| Database | PostgreSQL |  
| Auth | JWT + bcryptjs |  
| LLM | LLM Studio OpenAI-compatible API (localhost:1234) |  
| LLM Model | qwen3.6-27b |  
| ATS Scoring | Python subprocess (ats_multi_score.py) |  
| Document Build | Pandoc subprocess (MD  DOCX  PDF) |  
| File Storage | Local filesystem (`UserData/`) via abstract `file-store.js` service |  
| Server Port | 38291 |  
  
> ** [Port Registry](../../.ai/ports.md)** - complete port allocation for all PDS services. 
  
---  
  
## Naming Conventions  
  
> ** [Canonical source](AI-INSTRUCT/AI-CONVENTIONS.md)** - comprehensive naming rules.  
  
| Type | Convention | Example |  
|------|-----------|---------|  
| Files | kebab-case | `user-auth.js`, `llm-client.js` |  
| Directories | kebab-case | `api-routes`, `user-management` |  
| Variables | camelCase | `userData`, `listingId` |  
| Classes / Types | PascalCase | `UserManager`, `LlmClient` |  
| Constants | UPPER_SNAKE_CASE | `LLM_API_URL`, `MAX_UPLOAD_SIZE` | 
  
---  
  
## Code Comment Convention  
  
- Comment on **why**, not what  
- One line preferred; no rambling  
- Do not add comments to code you did not touch in the current change  
- If a line implements a non-obvious architectural constraint, reference the governing `AI-INSTRUCT.md`  
  
> ** [Code Comment Style](../.github/copilot-instructions.md#code-comment-convention)** - full comment convention.  
  
---  
  
## AI-INSTRUCT Maintenance Rule  
  
Whenever an architectural change is made, update the relevant `AI-INSTRUCT.md` file(s) in the same operation. Never defer. 
