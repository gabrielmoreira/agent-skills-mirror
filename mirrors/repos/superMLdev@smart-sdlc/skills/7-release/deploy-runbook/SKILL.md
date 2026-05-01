# Skill: Deploy Runbook

> **Activation**: `#file:_superml/skills/7-release/deploy-runbook/SKILL.md`

---

## Purpose

Create a step-by-step deployment runbook that any engineer can follow to deploy the release safely. Must include a validated rollback plan.

---

## Inputs

Load before starting:
- Release checklist: `{output_path}/release/release-checklist.md`
- Architecture doc: `{output_path}/planning/architecture.md`
- Deployment reference in `_superml/reference/release/`

---

## Deliverable

**`{output_path}/release/deploy-runbook.md`**

---

## Deploy Runbook Structure

```markdown
# Deploy Runbook — {project_name} v{version}

**Date**: {date}
**Release Manager**: {release_name}
**Estimated deployment duration**: {N} minutes
**Rollback duration**: {N} minutes

---

## Pre-Deployment Checklist

Run immediately before starting:
- [ ] Release checklist approved (GO decision)
- [ ] On-call engineer standing by
- [ ] Rollback procedure reviewed
- [ ] Maintenance window communicated (if applicable)

---

## Deployment Steps

### Phase 1: Preparation
| Step | Action | Command / Link | Owner | Expected Result |
|------|--------|----------------|-------|----------------|
| 1.1 | Take database backup | `{command}` | DevOps | Backup confirmed |
| 1.2 | Check environment health | `{command}` | DevOps | All services green |

### Phase 2: Deploy
| Step | Action | Command / Link | Owner | Expected Result |
|------|--------|----------------|-------|----------------|
| 2.1 | Deploy release tag | `{command}` | DevOps | Deployment complete |
| 2.2 | Run database migrations | `{command}` | DevOps | Migrations applied |
| 2.3 | Restart services | `{command}` | DevOps | Services healthy |

### Phase 3: Smoke Tests
| Step | Test | URL / Command | Expected Result |
|------|------|---------------|-----------------|
| 3.1 | Health check | `{url}/health` | 200 OK |
| 3.2 | Core user flow | {describe} | Success |

### Phase 4: Post-Deploy Monitoring
- Watch error rate in {monitoring tool} for {N} minutes
- Confirm no alerts firing
- Check logs for unexpected errors

---

## Rollback Procedure

Trigger rollback if any rollback criteria from the Release Checklist are met.

| Step | Action | Command / Link | Expected Result |
|------|--------|----------------|----------------|
| R1 | Revert deployment | `{command}` | Previous version live |
| R2 | Restore database (if needed) | `{command}` | Data restored |
| R3 | Verify rollback | `{url}/health` | 200 OK on previous version |
| R4 | Notify stakeholders | Email / Slack | Team informed |

---

## Communication Plan

| Event | Who to notify | Channel | Template |
|-------|--------------|---------|---------|
| Deployment started | Engineering team | Slack #deployments | "Deploying v{version} now..." |
| Deployment complete | Stakeholders | Email | "v{version} is live" |
| Rollback triggered | All | Slack #incidents | "Rolling back v{version}..." |

---

## Sign-off

| Role | Name | Date |
|------|------|------|
| Release Manager | {release_name} | {date} |
```

---

## Validation Checklist

- [ ] All deployment steps have commands and expected results
- [ ] Rollback procedure is complete and tested (at least on staging)
- [ ] Rollback duration estimate is realistic
- [ ] Communication plan filled in

---

## Next Skill

After deployment complete → **Release Notes** (`#file:_superml/skills/7-release/release-notes/SKILL.md`)
