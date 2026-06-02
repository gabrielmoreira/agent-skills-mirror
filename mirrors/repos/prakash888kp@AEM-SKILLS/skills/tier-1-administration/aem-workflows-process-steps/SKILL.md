# AEM Workflows & Process Steps

## Purpose
Design, implement, and manage AEM workflows including custom process steps, workflow launchers, and approval processes for content governance and automation.

## When to Use (Triggers)
- User mentions "workflow," "process step," "workflow launcher," or "approval process"
- References to `com.adobe.granite.workflow` or `WorkflowProcess` interface
- File paths containing `/conf/*/settings/workflow/` or workflow model definitions
- Questions about DAM asset processing, content approval, or automated actions
- Requests involving workflow participants, inbox, or task management

## Core Capabilities
- Create custom workflow process steps (Java-based and ECMA)
- Design workflow models with branching, splits, and joins
- Configure workflow launchers with path and event-type triggers
- Implement participant steps with dynamic participant selection
- Build custom inbox actions and notification handlers

## Domain Knowledge Required
### Technical Foundation
- Granite Workflow engine architecture (models, instances, items)
- Java WorkflowProcess interface and MetaDataMap
- OSGi service registration for workflow steps
- Workflow session and payload handling (JCR paths, DAM assets)

### AEM-Specific Context
- DAM Asset Update workflow and its customization points
- Workflow purge configuration and instance management
- Transient workflows for high-volume processing
- Workflow consoles: Models, Instances, Archive, Failures
- AEM Cloud Service workflow limitations vs. on-premise

## Implementation Approach
### Step 1: Workflow Model Design
Plan the workflow structure and decision points.
- Define start/end states and transitions
- Identify OR/AND splits and join conditions
- Determine participant assignment strategy
- Plan timeout and escalation handling

### Step 2: Custom Process Step Development
Implement Java-based process steps.
- Create OSGi component implementing `WorkflowProcess`
- Define `@Component` annotations with process.label property
- Implement `execute()` method with WorkItem and WorkflowSession
- Handle payload extraction (page path, asset path, or JCR path)
- Implement proper error handling and workflow advancement

### Step 3: Workflow Model Configuration
Build the model in AEM workflow editor or via code.
- Define model nodes and transitions in `/var/workflow/models/`
- Configure step titles, descriptions, and dialog arguments
- Set up OR-split conditions using ECMA expressions
- Configure timeout handlers for participant steps

### Step 4: Launcher Configuration
Set up automatic workflow triggering.
- Define launcher conditions (path glob, node type, event type)
- Configure launcher for created, modified, or deleted events
- Set excludes to prevent recursive triggering
- Handle launcher ordering for multiple workflows on same path

### Step 5: Testing and Monitoring
Validate workflow execution and handle failures.
- Test with various payload types (pages, assets, folders)
- Verify failure handling and retry behavior
- Configure workflow purge for completed/failed instances
- Set up monitoring for stalled workflow instances

## Quality Checklist
- [ ] Process step handles all payload types gracefully
- [ ] Error handling prevents workflow from getting stuck
- [ ] Launcher conditions are specific enough to avoid unwanted triggers
- [ ] Workflow model has proper termination conditions
- [ ] Participant selection works for all user scenarios
- [ ] Transient workflow used where instance persistence isn't needed
- [ ] Workflow purge configured to prevent repository growth
- [ ] Custom steps registered with clear process.label values

## Related Skills
- aem-dam-organization-metadata (DAM workflows)
- aem-custom-osgi-services (service integration in steps)
- aem-monitoring-alerting (workflow failure monitoring)

## Example Use Cases
1. **Content Approval Workflow:** Multi-stage approval with author → reviewer → publisher chain, deadline escalation, and automatic rejection notification with comments.
2. **DAM Processing Pipeline:** Custom asset processing workflow that generates renditions, extracts metadata, applies smart tags, and triggers CDN cache invalidation upon approval.
3. **Page Publication Governance:** Workflow triggered by page activation request that validates SEO metadata completeness, accessibility compliance score, and legal disclaimer presence before allowing publish.

## Notes
- Transient workflows don't persist intermediate steps — use for high-volume, non-auditable processes
- AEM Cloud Service restricts custom workflow model deployment — use runtime configuration
- Always implement `WorkflowProcess` with the `@Component` annotation, not the legacy `@Service`
- Workflow instances accumulate and can degrade performance — configure aggressive purging
