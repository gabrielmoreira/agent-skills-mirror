# AEM Multi-Site Manager (MSM)

## Purpose
Implement Multi-Site Manager for content reuse across sites using blueprints, Live Copies, rollout configurations, and synchronization strategies for multi-brand/multi-region architectures.

## When to Use (Triggers)
- User mentions "MSM," "Multi-Site Manager," "Live Copy," "blueprint," or "rollout"
- References to content inheritance, synchronization actions, or relationship status
- Questions about multi-brand sites, regional variations, or content reuse at scale
- Requests involving rollout configurations, conflict resolution, or inheritance cancellation
- File paths containing blueprint or livecopy configuration nodes

## Core Capabilities
- Design blueprint/Live Copy hierarchies for multi-site content reuse
- Configure custom rollout configurations with synchronization actions
- Implement conflict resolution strategies for concurrent edits
- Manage inheritance cancellation and re-attachment at page and component levels
- Set up automated and manual rollout triggers

## Domain Knowledge Required
### Technical Foundation
- MSM architecture (blueprint, Live Copy, rollout configuration, sync actions)
- Content inheritance model (component-level, property-level)
- Rollout triggers (on-modification, on-rollout, manual)
- Conflict handling and relationship status indicators

### AEM-Specific Context
- Blueprint source configuration and blueprint manager
- Live Copy creation wizard and depth control
- Standard rollout configurations and custom action development
- Live Copy overview console for relationship management
- MSM interaction with language copies and launches
- Suspended and detached inheritance states

## Implementation Approach
### Step 1: Multi-Site Architecture Design
Plan the blueprint/Live Copy topology.
- Define master site (blueprint source) and its scope
- Plan Live Copy hierarchy (by region, brand, channel)
- Determine inheritance depth (full tree, partial tree, page-only)
- Identify components/content requiring local override capability

### Step 2: Blueprint Configuration
Set up the source content as a managed blueprint.
- Configure blueprint under `/apps/msm/` with rollout configurations
- Define which rollout configurations apply at which levels
- Set up blueprint chapter structure for modular content management
- Configure notification for blueprint changes

### Step 3: Live Copy Creation
Create Live Copies with appropriate settings.
- Create Live Copies with selected rollout configurations
- Configure initial content deep copy vs. shallow copy
- Set up exclude paths for content that shouldn't be inherited
- Define page name and title transformation rules for copies

### Step 4: Rollout Configuration
Define synchronization behavior.
- Configure standard rollout configs (rolloutPage, pushOnModify)
- Create custom rollout configs for specific sync scenarios
- Implement custom synchronization actions (Java OSGi services)
- Set up triggered vs. manual rollout approaches

### Step 5: Governance & Operations
Establish operational procedures for MSM management.
- Define when authors should cancel inheritance vs. override locally
- Create procedures for re-synchronizing detached content
- Implement monitoring for inheritance status and drift
- Plan for blueprint restructuring and its impact on Live Copies

## Quality Checklist
- [ ] Blueprint changes propagate correctly to all Live Copies
- [ ] Local overrides preserved during rollout (inheritance cancelled correctly)
- [ ] Conflict detection works for concurrent blueprint and Live Copy edits
- [ ] Rollout performance acceptable for large content trees (1000+ pages)
- [ ] Authors understand inheritance status indicators in page editor
- [ ] Detached pages identified and remediation plan in place
- [ ] MSM relationship status reportable for governance
- [ ] Live Copy creation time acceptable for initial sync

## Related Skills
- aem-content-localization-i18n (language copies with MSM)
- aem-template-page-structure (templates across sites)
- aem-replication-publishing (publishing Live Copy content)

## Example Use Cases
1. **Multi-Brand Retail Platform:** Manage 8 brand sites from a single blueprint with brand-specific header/footer overrides, shared product content inheritance, and region-specific pricing components with cancelled inheritance.
2. **Country Site Network:** Roll out corporate website to 25 country sites with automatic content sync for global pages, local override capability for market-specific content, and language-specific translation integration.
3. **Franchise Website System:** Blueprint-driven franchise sites where corporate controls brand elements (locked inheritance) while franchisees customize local content (cancelled inheritance on specific components).

## Notes
- MSM and language copies are orthogonal — you can have Live Copies that are also language copies
- Rollout of large trees is resource-intensive — schedule during low-activity periods
- Inheritance cancellation is at the property level — you can cancel individual dialog fields, not just whole components
- AEM Cloud Service fully supports MSM — no differences from on-premise behavior
