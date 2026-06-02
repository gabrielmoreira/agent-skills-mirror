# AEM Upgrade & Patch Management

## Purpose
Plan and execute AEM version upgrades, service pack installations, cumulative fix pack applications, and hotfix deployments with minimal downtime and risk.

## When to Use (Triggers)
- User mentions "upgrade," "patch," "service pack," "hotfix," or "version migration"
- References to AEM version numbers, compatibility matrices, or release notes
- Questions about upgrade paths, deprecated features, or migration tools
- Requests involving upgrade planning, pre-upgrade checks, or rollback procedures
- Discussion of AEM Cloud Service continuous updates vs. on-premise upgrades

## Core Capabilities
- Plan upgrade paths across AEM major/minor versions with dependency analysis
- Execute pre-upgrade validation including compatibility checks and content analysis
- Manage service pack and CFP installations with proper testing cycles
- Design rollback procedures for failed upgrades
- Migrate custom code for API compatibility with new AEM versions

## Domain Knowledge Required
### Technical Foundation
- Software upgrade methodologies (blue-green, rolling, in-place)
- Dependency management and API compatibility assessment
- Database migration patterns and data transformation
- Change management processes and risk assessment

### AEM-Specific Context
- AEM version naming (6.5.x, Service Packs, CFPs, hotfixes)
- AEM upgrade paths and prerequisite versions
- Pattern Detector tool for code compatibility analysis
- Repository restructuring requirements between versions
- AEM Cloud Service continuous delivery model vs. on-premise upgrades
- Deprecated API detection and migration (Sling, Oak, Granite)

## Implementation Approach
### Step 1: Upgrade Assessment
Evaluate the upgrade scope and prepare for execution.
- Identify current version and target version
- Map upgrade path (direct or multi-hop through intermediate versions)
- Run Pattern Detector to identify incompatibilities in custom code
- Review release notes for breaking changes and deprecated features
- Assess third-party dependency compatibility

### Step 2: Code Migration
Update custom code for target version compatibility.
- Address Pattern Detector findings (deprecated APIs, removed features)
- Update Maven dependencies to target version BOMs
- Migrate deprecated OSGi annotations or APIs
- Update content structure for repository restructuring requirements
- Run unit/integration tests against new version APIs

### Step 3: Pre-Upgrade Preparation
Set up the environment and validate readiness.
- Execute pre-upgrade maintenance tasks (compaction, version purge, consistency check)
- Backup all environments completely (repository, datastore, configs)
- Prepare rollback procedure with tested restore
- Set up upgrade monitoring and success criteria
- Communicate maintenance window and stakeholder notification

### Step 4: Upgrade Execution
Perform the version upgrade.
- Apply upgrade following Adobe's documented procedure
- Monitor upgrade progress and error logs
- Execute post-upgrade tasks (reindexing, workflow migration, config updates)
- Validate Oak index health and repository integrity
- Verify all bundles reach ACTIVE state

### Step 5: Post-Upgrade Validation
Verify system health after upgrade.
- Run smoke tests covering critical user journeys
- Validate all integrations (commerce, analytics, translation)
- Check performance baselines against pre-upgrade metrics
- Verify replication and dispatcher functionality
- Execute full regression test suite
- Sign off with stakeholders and close maintenance window

## Quality Checklist
- [ ] Pattern Detector reports zero critical findings
- [ ] All custom bundles active after upgrade
- [ ] No traversal queries or index warnings post-upgrade
- [ ] Performance within 10% of pre-upgrade baselines
- [ ] All integrations functional and verified
- [ ] Rollback procedure tested before upgrade execution
- [ ] Content integrity verified post-upgrade
- [ ] Documentation updated with new version details

## Related Skills
- aem-backup-disaster-recovery (pre-upgrade backup)
- aem-monitoring-alerting (post-upgrade monitoring)
- aem-debugging-log-analysis (upgrade troubleshooting)

## Example Use Cases
1. **Major Version Upgrade:** Migrate from AEM 6.4 to 6.5 with 500+ custom components, requiring repository restructuring, API migration from JSP to HTL, and workflow model migration over a 3-month project.
2. **Service Pack Rolling Update:** Apply quarterly service pack to production AEM cluster with zero-downtime using rolling upgrade across publish instances and scheduled author maintenance window.
3. **Cloud Service Migration:** Migrate on-premise AEM 6.5 deployment to AEM Cloud Service, addressing all Cloud Readiness Analyzer findings, migrating to asset microservices, and adapting to CI/CD deployment model.

## Notes
- AEM Cloud Service manages upgrades automatically — focus on keeping code Cloud-Ready
- Never skip service packs — cumulative fix packs (CFPs) require specific SP base versions
- Pattern Detector should be run early in planning — not at upgrade time
- Repository restructuring (/etc → /conf, /content) is often the most time-consuming migration task
