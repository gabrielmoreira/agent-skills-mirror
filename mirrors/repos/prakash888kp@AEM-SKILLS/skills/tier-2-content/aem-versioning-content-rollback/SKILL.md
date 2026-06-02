# AEM Versioning & Content Rollback

## Purpose
Implement content versioning strategies, manage page/asset version histories, and execute content rollback procedures for disaster recovery and editorial corrections.

## When to Use (Triggers)
- User mentions "version," "rollback," "restore," "undo changes," or "version history"
- References to `jcr:versionHistory`, version purging, or timewarp
- Questions about restoring previous page states or comparing versions
- Requests involving version retention policies or audit trails
- Discussion of content recovery after accidental edits or deletions

## Core Capabilities
- Configure automatic versioning on page edit, activation, and workflow completion
- Implement version comparison and selective property restoration
- Design version purge policies to manage repository growth
- Execute rollback procedures for single pages, trees, and assets
- Set up Timewarp for point-in-time content preview

## Domain Knowledge Required
### Technical Foundation
- JCR versioning model (versionable mixin, version history, base version, predecessors)
- Version storage in `/jcr:system/jcr:versionStorage`
- Oak version garbage collection and purge mechanisms
- Difference between page version and asset version behaviors

### AEM-Specific Context
- AEM page versioning triggered by activation, not save
- Version creation in workflows (Create Version process step)
- Timewarp feature for historical content rendering
- Version purge configuration via OSGi (VersionManagerImpl)
- Restore vs. Restore Tree operations in Sites console

## Implementation Approach
### Step 1: Versioning Strategy
Define when and how versions are created.
- Determine version creation triggers (activate, workflow step, manual)
- Plan version labeling conventions (date, campaign, author)
- Define which content types require versioning (pages, assets, fragments)
- Establish version retention requirements (compliance, editorial, technical)

### Step 2: Version Purge Configuration
Manage repository growth from version accumulation.
- Configure VersionPurgeTask via OSGi (`com.day.cq.wcm.core.impl.VersionPurgeTask`)
- Set retention rules: max versions, max age, minimum retained
- Schedule purge execution during low-activity windows
- Exclude specific paths or content types from purging

### Step 3: Rollback Procedures
Document and implement content restoration processes.
- Single page restore via Sites console or version timeline
- Tree-level restore for coordinated multi-page rollback
- Asset version restore including rendition regeneration
- Content Fragment version handling and variation restore

### Step 4: Audit & Compliance
Track version creation for regulatory and editorial needs.
- Configure audit logging for version creation/deletion events
- Implement version annotation for editorial context
- Create version reports for compliance documentation
- Set up retention holds for legal preservation requirements

### Step 5: Disaster Recovery Integration
Integrate versioning with broader recovery strategy.
- Define RTO/RPO requirements and version-based recovery capabilities
- Document manual rollback procedures for operations team
- Test restore procedures regularly
- Plan for scenarios where version purge removed needed versions

## Quality Checklist
- [ ] Versions created automatically at all required trigger points
- [ ] Version purge configured and running without impacting live content
- [ ] Rollback tested for single page, multi-page, and asset scenarios
- [ ] Timewarp functions correctly for historical content preview
- [ ] Version storage growth monitored and within acceptable limits
- [ ] Audit trail captures who created/restored versions
- [ ] Compliance retention requirements met by purge policy
- [ ] Operations team trained on rollback procedures

## Related Skills
- aem-backup-disaster-recovery (broader recovery strategy)
- aem-launch-campaign-management (launches as alternative to versioning)
- aem-workflows-process-steps (version creation in workflows)

## Example Use Cases
1. **Editorial Correction:** Author publishes incorrect pricing information; operations team uses version history to identify the last correct version and restores it within 5 minutes, followed by immediate replication.
2. **Compliance Retention:** Financial services site requires 7-year retention of published content versions for regulatory audit, with version purge exclusions for regulated pages and automated compliance reporting.
3. **Campaign Rollback:** Marketing campaign produces negative results; entire campaign content tree (50 pages) is rolled back to pre-campaign state using coordinated tree restore with verification.

## Notes
- AEM versioning is page-level, not component-level — all components on a page version together
- Version storage can consume significant repository space — monitor `/jcr:system/jcr:versionStorage` size
- Restoring a page version does NOT restore referenced assets — asset versions must be handled separately
- AEM Cloud Service version purge is managed by Adobe — custom purge configs may not apply
