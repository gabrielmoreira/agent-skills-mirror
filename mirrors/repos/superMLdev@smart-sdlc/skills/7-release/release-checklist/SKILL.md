# Skill: Release Checklist

> **Activation**: `#file:_superml/skills/7-release/release-checklist/SKILL.md`

---

## Purpose

Generate and verify a comprehensive pre-release checklist. This is the go/no-go gate before deployment. Every item must be checked or explicitly accepted with written justification.

---

## Inputs

Load before starting:
- QA sign-off: `{output_path}/qa/qa-signoff.md`
- PRD: `{output_path}/planning/prd.md`
- Architecture doc: `{output_path}/planning/architecture.md`
- Release reference docs in `_superml/reference/release/`

---

## Deliverable

**`{output_path}/release/release-checklist.md`**

---

## Release Checklist Structure

```markdown
# Release Checklist — {project_name} v{version}

**Date**: {date}
**Release Manager**: {release_name}
**Target environment**: Production / Staging / UAT
**Deployment window**: {date/time}

## Go / No-Go Decision

> ✅ GO  /  ❌ NO-GO — see blockers

---

## 1. Quality Gates
- [ ] QA sign-off confirmed (`artifacts.qa_signed_off: true`)
- [ ] All P1/P2 bugs resolved and verified
- [ ] Regression suite passed on target environment

## 2. Code & Build
- [ ] Feature branches merged to release branch
- [ ] No uncommitted changes in release branch
- [ ] Build passes CI (link: )
- [ ] Dependency audit clean (no known CVEs)
- [ ] Version / tag created: v{version}

## 3. Configuration & Secrets
- [ ] Environment variables / secrets configured in production
- [ ] Feature flags set correctly for target environment
- [ ] Database migrations tested on staging

## 4. Infrastructure
- [ ] Target environment healthy (all services up)
- [ ] Capacity / scaling confirmed for expected load
- [ ] Monitoring and alerting configured
- [ ] Log aggregation working

## 5. Documentation
- [ ] Release notes drafted (`{output_path}/release/release-notes.md`)
- [ ] Deploy runbook ready (`{output_path}/release/deploy-runbook.md`)
- [ ] Rollback plan documented

## 6. Communication
- [ ] Stakeholders notified of deployment window
- [ ] Support team briefed on new features / known issues
- [ ] On-call engineer confirmed for deployment window

## 7. Rollback Criteria
Define exactly when to roll back:
- Any P1 incident within {N} minutes of deployment
- Error rate exceeds {N}% over {N}-minute window
- Specific smoke test failure: {describe}

---

## Approval

| Role | Name | Decision | Date |
|------|------|----------|------|
| Release Manager | {release_name} | GO / NO-GO | {date} |
| Tech Lead | | GO / NO-GO | |
| Product Owner | | GO / NO-GO | |
```

---

## Validation Checklist

- [ ] All items in every section assessed
- [ ] No-Go items documented with owners and resolution plan
- [ ] Go/No-Go decision is explicit
- [ ] Rollback criteria defined

---

## Next Skill

After checklist approved → **Deploy Runbook** (`#file:_superml/skills/7-release/deploy-runbook/SKILL.md`)
