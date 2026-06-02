# AEM Launch & Campaign Management

## Purpose
Create and manage AEM Launches for staged content preparation, coordinate campaign lifecycles, and implement time-based content promotion strategies.

## When to Use (Triggers)
- User mentions "launch," "campaign," "staged content," or "future publication"
- References to `/content/launches/` paths or launch promotion
- Questions about coordinating content updates across multiple pages simultaneously
- Requests involving seasonal campaigns, product launches, or content freezes
- Discussion of A/B testing content variants or phased rollouts

## Core Capabilities
- Create and manage AEM Launches with multi-level source page selection
- Configure automatic and manual launch promotion schedules
- Implement nested launches for iterative content preparation
- Coordinate multi-site campaign content across regions and brands
- Integrate launches with approval workflows and quality gates

## Domain Knowledge Required
### Technical Foundation
- AEM Launch architecture (source pages, launch pages, promotion, detachment)
- Live Copy relationship handling during launch promotion
- Conflict resolution when source pages change during launch preparation
- Launch scope management (page tree selection, depth control)

### AEM-Specific Context
- Launch console and its management capabilities
- Promotion behavior (promote with sub-pages, promote modified pages only)
- Launch production date and automatic promotion via scheduler
- Integration with MSM blueprints and language copies
- Launch impact on workflow and replication

## Implementation Approach
### Step 1: Campaign Planning
Define the scope and timeline of the content change.
- Identify all pages requiring updates for the campaign
- Determine launch creation date and target promotion date
- Plan review/approval gates before promotion
- Identify dependencies on other launches or content changes

### Step 2: Launch Creation
Set up the launch with proper scope and configuration.
- Create launch with selected source pages and depth
- Configure production date for auto-promotion if applicable
- Set launch title with clear campaign identification
- Define whether to include sub-pages or specific page selection

### Step 3: Content Editing
Coordinate content updates within the launch.
- Authors edit launch pages without affecting live content
- Implement review workflows specific to launch content
- Handle asset updates needed for the campaign
- Manage cross-references between launch pages

### Step 4: Validation & Approval
Ensure launch content meets quality standards.
- Preview launch content in context (timewarp)
- Run content validation checks (links, images, metadata)
- Execute approval workflow with stakeholder sign-off
- Test personalization rules within launch context

### Step 5: Promotion & Cleanup
Execute the promotion and handle post-promotion tasks.
- Promote launch manually or verify auto-promotion
- Validate promoted content on author and publish
- Handle promotion conflicts with source page changes
- Delete launch after successful promotion
- Trigger replication of promoted content

## Quality Checklist
- [ ] Launch scope includes all required pages and assets
- [ ] No live content impacted by launch editing
- [ ] Promotion conflicts identified and resolved before go-live
- [ ] Automatic promotion date configured correctly (timezone-aware)
- [ ] Post-promotion replication verified on all publish instances
- [ ] Nested launches (if used) promote in correct order
- [ ] Campaign content reviewed and approved by all stakeholders
- [ ] Rollback plan documented in case of promotion issues

## Related Skills
- aem-versioning-content-rollback (rollback after failed promotion)
- aem-replication-publishing (content distribution post-promotion)
- aem-msm-multi-site-manager (launches with Live Copies)

## Example Use Cases
1. **Black Friday Campaign:** Prepare 200+ page updates across product, category, and landing pages 6 weeks in advance, with staged review milestones and automatic promotion at midnight on launch day.
2. **Regulatory Compliance Update:** Coordinate simultaneous legal disclaimer changes across 50+ pages with legal team review workflow, mandatory approval, and same-day promotion across all regional sites.
3. **Seasonal Brand Refresh:** Implement nested launches for iterative design updates — first launch for imagery changes, second nested launch for copy updates, sequential promotion with validation between each.

## Notes
- Launches create copies of pages — repository size increases during launch lifecycle
- Promote launches during low-traffic periods to minimize replication impact
- MSM (Live Copy) relationships are maintained through launch promotion
- AEM Cloud Service supports launches but auto-promotion timing depends on pipeline execution
