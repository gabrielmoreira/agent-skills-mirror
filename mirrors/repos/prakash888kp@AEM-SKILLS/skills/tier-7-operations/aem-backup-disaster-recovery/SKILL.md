# AEM Backup & Disaster Recovery

## Purpose
Design and implement backup strategies, disaster recovery plans, and business continuity procedures for AEM environments including repository backup, content recovery, and failover architecture.

## When to Use (Triggers)
- User mentions "backup," "disaster recovery," "DR," "failover," or "business continuity"
- References to repository backup, restore procedures, or data protection
- Questions about RTO/RPO requirements, backup scheduling, or recovery testing
- Requests involving high availability, geographic redundancy, or failover configuration
- Discussion of data loss prevention, backup validation, or restore procedures

## Core Capabilities
- Design backup strategies for all AEM data (repository, datastore, configurations)
- Implement automated backup scheduling with retention policies
- Configure high availability and failover architectures
- Build and document disaster recovery runbooks
- Test and validate recovery procedures with measurable RTO/RPO

## Domain Knowledge Required
### Technical Foundation
- Backup types: full, incremental, differential, snapshot-based
- Recovery objectives: RTO (Recovery Time Objective), RPO (Recovery Point Objective)
- High availability patterns: active-active, active-passive, cold standby
- Data consistency during backup (quiescing, point-in-time snapshots)

### AEM-Specific Context
- Oak TarMK online backup (FileDataStore + SegmentNodeStore backup)
- AEM Cold Standby (TarMK standby sync)
- Document store (MongoDB) backup patterns for DocumentMK
- Backup of external datastore (S3, Azure Blob, shared filesystem)
- AEM Cloud Service managed backup vs. on-premise manual backup
- Restore procedures and data consistency verification

## Implementation Approach
### Step 1: Requirements Analysis
Define recovery objectives and scope.
- Establish RTO and RPO for each environment (author, publish)
- Identify critical data: repository content, configurations, datastore binaries
- Determine compliance requirements (retention periods, geographic restrictions)
- Assess acceptable data loss and downtime per tier

### Step 2: Backup Architecture Design
Plan the backup approach for each data component.
- Configure Oak online backup for repository segments
- Set up datastore backup (filesystem copy, S3 versioning, or snapshots)
- Plan configuration backup (OSGi configs, dispatcher, infrastructure-as-code)
- Design backup storage location (offsite, different region, different provider)

### Step 3: Automation & Scheduling
Implement automated backup execution.
- Schedule Oak online backup via cron/maintenance window
- Automate datastore backup aligned with repository backup timing
- Implement backup rotation and retention (daily, weekly, monthly)
- Configure backup monitoring and failure alerting

### Step 4: High Availability Configuration
Set up failover capabilities.
- Configure TarMK Cold Standby for author instance failover
- Set up publish farm with load balancer health checks
- Implement dispatcher-level failover for publish tier
- Design cross-region failover for geographic disaster scenarios

### Step 5: Recovery Testing
Validate recovery procedures regularly.
- Schedule quarterly DR drills with documented runbooks
- Test full restore to isolated environment
- Measure actual RTO/RPO against targets
- Document and remediate gaps found during testing

## Quality Checklist
- [ ] Backup covers all data components (repository, datastore, config)
- [ ] Backup consistency verified (no corrupt or partial backups)
- [ ] RTO/RPO measured and within business requirements
- [ ] Backup retention meets compliance requirements
- [ ] Automated alerting on backup failures
- [ ] Recovery procedures documented in runbook format
- [ ] DR tested quarterly with documented results
- [ ] Backup storage in separate failure domain from production

## Related Skills
- aem-monitoring-alerting (backup monitoring)
- aem-versioning-content-rollback (content-level recovery)
- aem-upgrade-patch-management (safe upgrade with backup)

## Example Use Cases
1. **Enterprise DR Strategy:** Design a multi-region disaster recovery architecture for a critical AEM author instance with 4-hour RTO, 1-hour RPO, automated failover, and documented recovery runbooks tested quarterly.
2. **Cloud-to-On-Premise Backup:** Implement backup strategy for AEM Cloud Service content with nightly exports to on-premise storage for compliance requirements, including content package extraction and verification.
3. **Ransomware Recovery Plan:** Create an air-gapped backup architecture with immutable backups, integrity verification, and a tested recovery procedure that can restore a clean AEM instance within 8 hours.

## Notes
- AEM Cloud Service manages backups automatically — focus DR planning on content recovery, not infrastructure
- Oak online backup creates a consistent snapshot — do NOT use filesystem copy while AEM is running
- Cold Standby provides near-real-time replication but requires dedicated standby instance
- Test restores are critical — a backup that hasn't been tested is not a backup
