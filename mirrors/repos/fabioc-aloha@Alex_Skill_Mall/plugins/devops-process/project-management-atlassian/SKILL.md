---
type: skill
lifecycle: stable
inheritance: inheritable
name: atlassian-admin
description: Atlassian Administrator for managing and organizing Atlassian products (Jira, Confluence, Bitbucket, Trello), users, permissions, security, integrations, system configuration, and org-wide governan...
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Atlassian Administrator Expert

## Workflows

### User Provisioning
1. Create user account: `admin.atlassian.com > User management > Invite users`
   - REST API: `POST /rest/api/3/user` with `{"emailAddress": "...", "displayName": "...","products": [...]}`
2. Add to appropriate groups: `admin.atlassian.com > User management > Groups > [group] > Add members`
3. Assign product access (Jira, Confluence) via `admin.atlassian.com > Products > [product] > Access`
4. Configure default permissions per group scheme
5. Send welcome email with onboarding info
6. **NOTIFY**: Relevant team leads of new member
7. **VERIFY**: Confirm user appears active at `admin.atlassian.com/o/{orgId}/users` and can log in

### User Deprovisioning
1. **CRITICAL**: Audit user's owned content and tickets
   - Jira: `GET /rest/api/3/search?jql=assignee={accountId}` to find open issues
   - Confluence: `GET /wiki/rest/api/user/{accountId}/property` to find owned spaces/pages
2. Reassign ownership of:
   - Jira projects: `Project settings > People > Change lead`
   - Confluence spaces: `Space settings > Overview > Edit space details`
   - Open issues: bulk reassign via `Jira > Issues > Bulk change`
   - Filters and dashboards: transfer via `User management > [user] > Managed content`
3. Remove from all groups: `admin.atlassian.com > User management > [user] > Groups`
4. Revoke product access
5. Deactivate account: `admin.atlassian.com > User management > [user] > Deactivate`
   - REST API: `DELETE /rest/api/3/user?accountId={accountId}`
6. **VERIFY**: Confirm `GET /rest/api/3/user?accountId={accountId}` returns `"active": false`
7. Document deprovisioning in audit log
8. **USE**: Jira Expert to reassign any remaining issues

### Group Management
1. Create groups: `admin.atlassian.com > User management > Groups > Create group`
   - REST API: `POST /rest/api/3/group` with `{"name": "..."}`
   - Structure by: Teams (engineering, product, sales), Roles (admins, users, viewers), Projects (project-alpha-team)
2. Define group purpose and membership criteria (document in Confluence)
3. Assign default permissions per group
4. Add users to appropriate groups
5. **VERIFY**: Confirm group members via `GET /rest/api/3/group/member?groupName={name}`
6. Regular review and cleanup (quarterly)
7. **USE**: Confluence Expert to document group structure

### Permission Scheme Design
**Jira Permission Schemes** (`Jira Settings > Issues > Permission Schemes`):
- **Public Project**: All users can view, members can edit
- **Team Project**: Team members full access, stakeholders view
- **Restricted Project**: Named individuals only
- **Admin Project**: Admins only

**Confluence Permission Schemes** (`Confluence Admin > Space permissions`):
- **Public Space**: All users view, space members edit
- **Team Space**: Team-specific access
- **Personal Space**: Individual user only
- **Restricted Space**: Named individuals and groups

**Best Practices**:
- Use groups, not individual permissions
- Principle of least privilege
- Regular permission audits
- Document permission rationale

### SSO Configuration
1. Choose identity provider (Okta, Azure AD, Google)
2. Configure SAML settings: `admin.atlassian.com > Security > SAML single sign-on > Add SAML configuration`
   - Set Entity ID, ACS URL, and X.509 certificate from IdP
3. Test SSO with admin account (keep password login active during test)
4. Test with regular user account
5. Enable SSO for organization
6. Enforce SSO: `admin.atlassian.com > Security > Authentication policies > Enforce SSO`
7. Configure SCIM for auto-provisioning: `admin.atlassian.com > User provisioning > [IdP] > Enable SCIM`
8. **VERIFY**: Confirm SSO flow succeeds and audit logs show `saml.login.success` events
9. Monitor SSO logs: `admin.atlassian.com > Security > Audit log > filter: SSO`

### Marketplace App Management
1. Evaluate app need and security: check vendor's security self-assessment at `marketplace.atlassian.com`
2. Review vendor security documentation (penetration test reports, SOC 2)
3. Test app in sandbox environment
4. Purchase or request trial: `admin.atlassian.com > Billing > Manage subscriptions`
5. Install app: `admin.atlassian.com > Products > [product] > Apps > Find new apps`
6. Configure app settings per vendor documentation
7. Train users on app usage
8. **VERIFY**: Confirm app appears in `GET /rest/plugins/1.0/` and health check passes
9. Monitor app performance and usage; review annually for continued need

### System Performance Optimization
**Jira** (`Jira Settings > System`):
- Archive old projects: `Project settings > Archive project`
- Reindex: `Jira Settings > System > Indexing > Full re-index`
- Clean up unused workflows and schemes: `Jira Settings > Issues > Workflows`
- Monitor queue/thread counts: `Jira Settings > System > System info`

**Confluence** (`Confluence Admin > Configuration`):
- Archive inactive spaces: `Space tools > Overview > Archive space`
- Remove orphaned pages: `Confluence Admin > Orphaned pages`
- Monitor index and cache: `Confluence Admin > Cache management`

**Monitoring Cadence**:
- Daily health checks: `admin.atlassian.com > Products > [product] > Health`
- Weekly performance reports
- Monthly capacity planning
- Quarterly optimization reviews

### Integration Setup
**Common Integrations**:
- **Slack**: `Jira Settings > Apps > Slack integration` — notifications for Jira and Confluence
- **GitHub/Bitbucket**: `Jira Settings > Apps > DVCS accounts` — link commits to issues
- **Microsoft Teams**: `admin.atlassian.com > Apps > Microsoft Teams`
- **Zoom**: Available via Marketplace app `zoom-for-jira`
- **Salesforce**: Via Marketplace app `salesforce-connector`

**Configuration Steps**:
1. Review integration requirements and OAuth scopes needed
2. Configure OAuth or API authentication (store tokens in secure vault, not plain text)
3. Map fields and data flows
4. Test integration thoroughly with sample data
5. Document configuration in Confluence runbook
6. Train users on integration features
7. **VERIFY**: Confirm webhook delivery via `Jira Settings > System > WebHooks > [webhook] > Test`
8. Monitor integration health via app-specific dashboards

## Global Configuration

### Jira Global Settings (`Jira Settings > Issues`)
**Issue Types**: Create and manage org-wide issue types; define issue type schemes; standardize across projects
**Workflows**: Create global workflow templates via `Workflows > Add workflow`; manage workflow schemes
**Custom Fields**: Create org-wide custom fields at `Custom fields > Add custom field`; manage field configurations and context
**Notification Schemes**: Configure default notification rules; create custom notification schemes; manage email templates

### Confluence Global Settings (`Confluence Admin`)
**Blueprints & Templates**: Create org-wide templates at `Configuration > Global Templates and Blueprints`; manage blueprint availability
**Themes & Appearance**: Configure org branding at `Configuration > Themes`; customize logos and colors
**Macros**: Enable/disable macros at `Configuration > Macro usage`; configure macro permissions

### Security Settings (`admin.atlassian.com > Security`)
**Authentication**:
- Password policies: `Security > Authentication policies > Edit`
- Session timeout: `Security > Session duration`
- API token management: `Security > API token controls`

**Data Residency**: Configure data location at `admin.atlassian.com > Data residency > Pin products`

**Audit Logs**: `admin.atlassian.com > Security > Audit log`
- Enable comprehensive logging; export via `GET /admin/v1/orgs/{orgId}/audit-log`
- Retain per policy (minimum 7 years for SOC 2/GDPR compliance)

## Governance & Policies

### Access Governance
- Quarterly review of all user access: `admin.atlassian.com > User management > Export users`
- Verify user roles and permissions; remove inactive users
- Limit org admins to 2–3 individuals; audit admin actions monthly
- Require MFA for all admins: `Security > Authentication policies > Require 2FA`

### Naming Conventions
**Jira**: Project keys 3–4 uppercase letters (PROJ, WEB); issue types Title Case; custom fields prefixed (CF: Story Points)
**Confluence**: Spaces use Team/Project prefix (TEAM: Engineering); pages descriptive and consistent; labels lowercase, hyphen-separated

### Change Management
**Major Changes**: Announce 2 weeks in advance; test in sandbox; create rollback plan; execute during off-peak; post-implementation review
**Minor Changes**: Announce 48 hours in advance; document in change log; monitor for issues

## Disaster Recovery

### Backup Strategy
**Jira & Confluence**: Daily automated backups; weekly manual verification; 30-day retention; offsite storage
- Trigger manual backup: `Jira Settings > System > Backup system` / `Confluence Admin > Backup and Restore`

**Recovery Testing**: Quarterly recovery drills; document procedures; measure RTO and RPO

### Incident Response
**Severity Levels**:
- **P1 (Critical)**: System down — respond in 15 min
- **P2 (High)**: Major feature broken — respond in 1 hour
- **P3 (Medium)**: Minor issue — respond in 4 hours
- **P4 (Low)**: Enhancement — respond in 24 hours

**Response Steps**:
1. Acknowledge and log incident
2. Assess impact and severity
3. Communicate status to stakeholders
4. Investigate root cause (check `admin.atlassian.com > Products > [product] > Health` and Atlassian Status Page)
5. Implement fix
6. **VERIFY**: Confirm resolution via affected user test and health check
7. Post-mortem and lessons learned

## Metrics & Reporting

**System Health**: Active users (daily/weekly/monthly), storage utilization, API rate limits, integration health, response times
- Export via: `GET /admin/v1/orgs/{orgId}/users` for user counts; product-specific analytics dashboards

**Usage Analytics**: Most active projects/spaces, content creation trends, user engagement, search patterns
**Compliance Metrics**: User access review completion, security audit findings, failed login attempts, API token usage

## Decision Framework & Handoff Protocols

**Escalate to Atlassian Support**: System outage, performance degradation org-wide, data loss/corruption, license/billing issues, complex migrations

**Delegate to Product Experts**:
- Jira Expert: Project-specific configuration
- Confluence Expert: Space-specific settings
- Scrum Master: Team workflow needs
- Senior PM: Strategic planning input

**Involve Security Team**: Security incidents, unusual access patterns, compliance audit preparation, new integration security review

**TO Jira Expert**: New global workflows, custom fields, permission schemes, or automation capabilities available
**TO Confluence Expert**: New global templates, space permission schemes, blueprints, or macros configured
**TO Senior PM**: Usage analytics, capacity planning insights, cost optimization, security compliance status
**TO Scrum Master**: Team access provisioned, board configuration options, automation rules, integrations enabled
**FROM All Roles**: User access requests, permission changes, app installation requests, configuration support, incident reports

## Atlassian MCP Integration

**Primary Tools**: Jira MCP, Confluence MCP

**Admin Operations**:
- User and group management via API
- Bulk permission updates
- Configuration audits
- Usage reporting
- System health monitoring
- Automated compliance checks

**Integration Points**:
- Support all roles with admin capabilities
- Enable Jira Expert with global configurations
- Provide Confluence Expert with template management
- Ensure Senior PM has visibility into org health
- Enable Scrum Master with team provisioning


---
type: skill
lifecycle: stable
inheritance: inheritable
name: atlassian-templates
description: Atlassian Template and Files Creator/Modifier expert for creating, modifying, and managing Jira and Confluence templates, blueprints, custom layouts, reusable components, and standardized content s...
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Atlassian Template & Files Creator Expert

Specialist in creating, modifying, and managing reusable templates and files for Jira and Confluence. Ensures consistency, accelerates content creation, and maintains org-wide standards.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-2
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Confluence Templates Library

See **TEMPLATES.md** for full reference tables and copy-paste-ready template structures. The following summarises the standard types this skill creates and maintains.

### Confluence Template Types
| Template | Purpose | Key Macros Used |
|----------|---------|-----------------|
| **Meeting Notes** | Structured meeting records with agenda, decisions, and action items | `{date}`, `{tasks}`, `{panel}`, `{info}`, `{note}` |
| **Project Charter** | Org-level project scope, stakeholder RACI, timeline, and budget | `{panel}`, `{status}`, `{timeline}`, `{info}` |
| **Sprint Retrospective** | Agile ceremony template with What Went Well / Didn't Go Well / Actions | `{panel}`, `{expand}`, `{tasks}`, `{status}` |
| **PRD** | Feature definition with goals, user stories, functional/non-functional requirements, and release plan | `{panel}`, `{status}`, `{jira}`, `{warning}` |
| **Decision Log** | Structured option analysis with decision matrix and implementation tracking | `{panel}`, `{status}`, `{info}`, `{tasks}` |

**Standard Sections** included across all Confluence templates:
- Header panel with metadata (owner, date, status)
- Clearly labelled content sections with inline placeholder instructions
- Action items block using `{tasks}` macro
- Related links and references

### Complete Example: Meeting Notes Template

The following is a copy-paste-ready Meeting Notes template in Confluence storage format (wiki markup):

```
{panel:title=Meeting Metadata|borderColor=#0052CC|titleBGColor=#0052CC|titleColor=#FFFFFF}
*Date:* {date}
*Owner / Facilitator:* @[facilitator name]
*Attendees:* @[name], @[name]
*Status:* {status:colour=Yellow|title=In Progress}
{panel}

h2. Agenda
# [Agenda item 1]
# [Agenda item 2]
# [Agenda item 3]

h2. Discussion & Decisions
{panel:title=Key Decisions|borderColor=#36B37E|titleBGColor=#36B37E|titleColor=#FFFFFF}
* *Decision 1:* [What was decided and why]
* *Decision 2:* [What was decided and why]
{panel}

{info:title=Notes}
[Detailed discussion notes, context, or background here]
{info}

h2. Action Items
{tasks}
* [ ] [Action item] — Owner: @[name] — Due: {date}
* [ ] [Action item] — Owner: @[name] — Due: {date}
{tasks}

h2. Next Steps & Related Links
* Next meeting: {date}
* Related pages: [link]
* Related Jira issues: {jira:key=PROJ-123}
```

> Full examples for all other template types (Project Charter, Sprint Retrospective, PRD, Decision Log) and all Jira templates can be generated on request or found in **TEMPLATES.md**.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-3
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Macro Usage Guidelines

**Dynamic Content**: Use macros for auto-updating content (dates, user mentions, Jira queries)
**Visual Hierarchy**: Use `{panel}`, `{info}`, and `{note}` to create visual distinction
**Interactivity**: Use `{expand}` for collapsible sections in long templates
**Integration**: Embed Jira charts and tables via `{jira}` macro for live data

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-4
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Best Practices & Governance

**Org-Specific Standards:**
- Track template versions with version notes in the page header
- Mark outdated templates with a `{warning}` banner before archiving; archive (do not delete)
- Maintain usage guides linked from each template
- Gather feedback on a quarterly review cycle; incorporate usage metrics before deprecating

**Quality Gates (apply before every deployment):**
- Example content provided for each section
- Tested with sample data in preview
- Version comment added to change log
- Feedback mechanism in place (comments enabled or linked survey)

**Governance Process**:
1. Request and justification
2. Design and review
3. Testing with pilot users
4. Documentation
5. Approval
6. Deployment (via MCP or manual)
7. Training
8. Monitoring

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-5
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: confluence-expert
description: Atlassian Confluence expert for creating and managing spaces, knowledge bases, and documentation. Configures space permissions and hierarchies, creates page templates with macros, sets up documenta...
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Atlassian Confluence Expert

Master-level expertise in Confluence space management, documentation architecture, content creation, macros, templates, and collaborative knowledge management.

## Atlassian MCP Integration

**Primary Tool**: Confluence MCP Server

**Key Operations**:

```
// Create a new space
create_space({ key: "TEAM", name: "Engineering Team", description: "Engineering team knowledge base" })

// Create a page under a parent
create_page({ spaceKey: "TEAM", title: "Sprint 42 Notes", parentId: "123456", body: "<p>Meeting notes in storage-format HTML</p>" })

// Update an existing page (version must be incremented)
update_page({ pageId: "789012", version: 4, body: "<p>Updated content</p>" })

// Delete a page
delete_page({ pageId: "789012" })

// Search with CQL
search({ cql: 'space = "TEAM" AND label = "meeting-notes" ORDER BY lastModified DESC' })

// Retrieve child pages for hierarchy inspection
get_children({ pageId: "123456" })

// Apply a label to a page
add_label({ pageId: "789012", label: "archived" })
```

**Integration Points**:
- Create documentation for Senior PM projects
- Support Scrum Master with ceremony templates
- Link to Jira issues for Jira Expert
- Provide templates for Template Creator

> **See also**: `MACROS.md` for macro syntax reference, `TEMPLATES.md` for full template library, `PERMISSIONS.md` for permission scheme details.

## Workflows

### Space Creation
1. Determine space type (Team, Project, Knowledge Base, Personal)
2. Create space with clear name and description
3. Set space homepage with overview
4. Configure space permissions:
   - View, Edit, Create, Delete
   - Admin privileges
5. Create initial page tree structure
6. Add space shortcuts for navigation
7. **Verify**: Navigate to the space URL and confirm the homepage loads; check that a non-admin test user sees the correct permission level
8. **HANDOFF TO**: Teams for content population

### Page Architecture
**Best Practices**:
- Use page hierarchy (parent-child relationships)
- Maximum 3 levels deep for navigation
- Consistent naming conventions
- Date-stamp meeting notes

**Recommended Structure**:
```
Space Home
├── Overview & Getting Started
├── Team Information
│   ├── Team Members & Roles
│   ├── Communication Channels
│   └── Working Agreements
├── Projects
│   ├── Project A
│   │   ├── Overview
│   │   ├── Requirements
│   │   └── Meeting Notes
│   └── Project B
├── Processes & Workflows
├── Meeting Notes (Archive)
└── Resources & References
```

### Template Creation
1. Identify repeatable content pattern
2. Create page with structure and placeholders
3. Add instructions in placeholders
4. Format with appropriate macros
5. Save as template
6. Share with space or make global
7. **Verify**: Create a test page from the template and confirm all placeholders render correctly before sharing with the team
8. **USE**: References for advanced template patterns

### Documentation Strategy
1. **Assess** current documentation state
2. **Define** documentation goals and audience
3. **Organize** content taxonomy and structure
4. **Create** templates and guidelines
5. **Migrate** existing documentation
6. **Train** teams on best practices
7. **Monitor** usage and adoption
8. **REPORT TO**: Senior PM on documentation health

### Knowledge Base Management
**Article Types**:
- How-to guides
- Troubleshooting docs
- FAQs
- Reference documentation
- Process documentation

**Quality Standards**:
- Clear title and description
- Structured with headings
- Updated date visible
- Owner identified
- Reviewed quarterly

## Essential Macros

> Full macro reference with all parameters: see `MACROS.md`.

### Content Macros
**Info, Note, Warning, Tip**:
```
{info}
Important information here
{info}
```

**Expand**:
```
{expand:title=Click to expand}
Hidden content here
{expand}
```

**Table of Contents**:
```
{toc:maxLevel=3}
```

**Excerpt & Excerpt Include**:
```
{excerpt}
Reusable content
{excerpt}

{excerpt-include:Page Name}
```

### Dynamic Content
**Jira Issues**:
```
{jira:JQL=project = PROJ AND status = "In Progress"}
```

**Jira Chart**:
```
{jirachart:type=pie|jql=project = PROJ|statType=statuses}
```

**Recently Updated**:
```
{recently-updated:spaces=@all|max=10}
```

**Content by Label**:
```
{contentbylabel:label=meeting-notes|maxResults=20}
```

### Collaboration Macros
**Status**:
```
{status:colour=Green|title=Approved}
```

**Task List**:
```
{tasks}
- [ ] Task 1
- [x] Task 2 completed
{tasks}
```

**User Mention**:
```
@username
```

**Date**:
```
{date:format=dd MMM yyyy}
```

## Page Layouts & Formatting

**Two-Column Layout**:
```
{section}
{column:width=50%}
Left content
{column}
{column:width=50%}
Right content
{column}
{section}
```

**Panel**:
```
{panel:title=Panel Title|borderColor=#ccc}
Panel content
{panel}
```

**Code Block**:
```
{code:javascript}
const example = "code here";
{code}
```

## Templates Library

> Full template library with complete markup: see `TEMPLATES.md`. Key templates summarised below.

| Template | Purpose | Key Sections |
|----------|---------|--------------|
| **Meeting Notes** | Sprint/team meetings | Agenda, Discussion, Decisions, Action Items (tasks macro) |
| **Project Overview** | Project kickoff & status | Quick Facts panel, Objectives, Stakeholders table, Milestones (Jira macro), Risks |
| **Decision Log** | Architectural/strategic decisions | Context, Options Considered, Decision, Consequences, Next Steps |
| **Sprint Retrospective** | Agile ceremony docs | What Went Well (info), What Didn't (warning), Action Items (tasks), Metrics |

## Space Permissions

> Full permission scheme details: see `PERMISSIONS.md`.

### Permission Schemes
**Public Space**:
- All users: View
- Team members: Edit, Create
- Space admins: Admin

**Team Space**:
- Team members: View, Edit, Create
- Team leads: Admin
- Others: No access

**Project Space**:
- Stakeholders: View
- Project team: Edit, Create
- PM: Admin

## Content Governance

**Review Cycles**:
- Critical docs: Monthly
- Standard docs: Quarterly
- Archive docs: Annually

**Archiving Strategy**:
- Move outdated content to Archive space
- Label with "archived" and date
- Maintain for 2 years, then delete
- Keep audit trail

**Content Quality Checklist**:
- [ ] Clear, descriptive title
- [ ] Owner/author identified
- [ ] Last updated date visible
- [ ] Appropriate labels applied
- [ ] Links functional
- [ ] Formatting consistent
- [ ] No sensitive data exposed

## Decision Framework

**When to Escalate to Atlassian Admin**:
- Need org-wide template
- Require cross-space permissions
- Blueprint configuration
- Global automation rules
- Space export/import

**When to Collaborate with Jira Expert**:
- Embed Jira queries and charts
- Link pages to Jira issues
- Create Jira-based reports
- Sync documentation with tickets

**When to Support Scrum Master**:
- Sprint documentation templates
- Retrospective pages
- Team working agreements
- Process documentation

**When to Support Senior PM**:
- Executive report pages
- Portfolio documentation
- Stakeholder communication
- Strategic planning docs

## Handoff Protocols

**FROM Senior PM**:
- Documentation requirements
- Space structure needs
- Template requirements
- Knowledge management strategy

**TO Senior PM**:
- Documentation coverage reports
- Content usage analytics
- Knowledge gaps identified
- Template adoption metrics

**FROM Scrum Master**:
- Sprint ceremony templates
- Team documentation needs
- Meeting notes structure
- Retrospective format

**TO Scrum Master**:
- Configured templates
- Space for team docs
- Training on best practices
- Documentation guidelines

**WITH Jira Expert**:
- Jira-Confluence linking
- Embedded Jira reports
- Issue-to-page connections
- Cross-tool workflow

## Best Practices

**Organization**:
- Consistent naming conventions
- Meaningful labels
- Logical page hierarchy
- Related pages linked
- Clear navigation

**Maintenance**:
- Regular content audits
- Remove duplication
- Update outdated information
- Archive obsolete content
- Monitor page analytics

## Analytics & Metrics

**Usage Metrics**:
- Page views per space
- Most visited pages
- Search queries
- Contributor activity
- Orphaned pages

**Health Indicators**:
- Pages without recent updates
- Pages without owners
- Duplicate content
- Broken links
- Empty spaces

## Related Skills

- **Jira Expert** (`project-management/jira-expert/`) — Jira issue macros and linking complement Confluence docs
- **Atlassian Templates** (`project-management/atlassian-templates/`) — Template patterns for Confluence content creation


---
type: skill
lifecycle: stable
inheritance: inheritable
name: jira-expert
description: Atlassian Jira expert for creating and managing projects, planning, product discovery, JQL queries, workflows, custom fields, automation, reporting, and all Jira features. Use for Jira project setu...
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Atlassian Jira Expert

Master-level expertise in Jira configuration, project management, JQL, workflows, automation, and reporting. Handles all technical and operational aspects of Jira.

## Quick Start — Most Common Operations

**Create a project**:
```
mcp jira create_project --name "My Project" --key "MYPROJ" --type scrum --lead "user@example.com"
```

**Run a JQL query**:
```
mcp jira search_issues --jql "project = MYPROJ AND status != Done AND dueDate < now()" --maxResults 50
```

For full command reference, see [Atlassian MCP Integration](#atlassian-mcp-integration). For JQL functions, see [JQL Functions Reference](#jql-functions-reference). For report templates, see [Reporting Templates](#reporting-templates).

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-8
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: meeting-analyzer
description: Analyzes meeting transcripts and recordings to surface behavioral patterns, communication anti-patterns, and actionable coaching feedback. Use this skill whenever the user uploads or points to meet...
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Meeting Insights Analyzer

> Originally contributed by [maximcoding](https://github.com/maximcoding) — enhanced and integrated by the claude-skills team.

Transform meeting transcripts into concrete, evidence-backed feedback on communication patterns, leadership behaviors, and interpersonal dynamics.

## Core Workflow

### 1. Ingest & Inventory

Scan the target directory for transcript files (`.txt`, `.md`, `.vtt`, `.srt`, `.docx`, `.json`).

For each file:
- Extract meeting date from filename or content (expect `YYYY-MM-DD` prefix or embedded timestamps)
- Identify speaker labels — look for patterns like `Speaker 1:`, `[John]:`, `John Smith  00:14:32`, VTT/SRT cue formatting
- Detect the user's identity: ask if ambiguous, otherwise infer from the most frequent speaker or filename hints
- Log: filename, date, duration (from timestamps), participant count, word count

Print a brief inventory table so the user confirms scope before heavy analysis begins.

### 2. Normalize Transcripts

Different tools produce wildly different formats. Normalize everything into a common internal structure before analysis:

```
{ speaker: string, timestamp_sec: number | null, text: string }[]
```

Handling per format:
- **VTT/SRT**: Parse cue timestamps + text. Speaker labels may be inline (`<v Speaker>`) or prefixed.
- **Plain text**: Look for `Name:` or `[Name]` prefixes per line. If no speaker labels exist, warn the user that per-speaker analysis is limited.
- **Markdown**: Strip formatting, then treat as plain text.
- **DOCX**: Extract text content, then treat as plain text.
- **JSON**: Expect an array of objects with `speaker`/`text` fields (common Otter/Fireflies export).

If timestamps are missing, degrade gracefully — skip timing-dependent metrics (speaking pace, pause analysis) but still run text-based analysis.

### 3. Analyze

Run all applicable analysis modules below. Each module is independent — skip any that don't apply (e.g., skip speaking ratios if there are no speaker labels).

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-10
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

#### Module: Conflict & Directness

Scan the user's speech for hedging and avoidance markers:

**Hedging language** (score per-instance, aggregate per meeting):
- Qualifiers: "maybe", "kind of", "sort of", "I guess", "potentially", "arguably"
- Permission-seeking: "if that's okay", "would it be alright if", "I don't know if this is right but"
- Deflection: "whatever you think", "up to you", "I'm flexible"
- Softeners before disagreement: "I don't want to push back but", "this might be a dumb question"

**Conflict avoidance patterns** (requires more context, flag with confidence level):
- Topic changes after tension (speaker A raises problem → user pivots to logistics)
- Agreement-without-commitment: "yeah totally" followed by no action or follow-up
- Reframing others' concerns as smaller than stated: "it's probably not that big a deal"
- Absent feedback in 1:1s where performance topics would be expected

For each flagged instance, extract:
- The full quote (with surrounding context — 2 turns before and after)
- A severity tag: `low` (single hedge word), `medium` (pattern of hedging in one exchange), `high` (clearly avoided a necessary conversation)
- A rewrite suggestion: what a more direct version would sound like

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-11
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

#### Module: Question Quality & Listening

Classify the user's questions:
- **Closed** (yes/no): "Did you finish the report?"
- **Leading** (answer embedded): "Don't you think we should ship sooner?"
- **Open genuine**: "What's blocking you on this?"
- **Clarifying** (references prior speaker): "When you said X, did you mean Y?"
- **Building** (extends another's idea): "That's interesting — what if we also Z?"

Good listening indicators:
- Clarifying and building questions (shows active processing)
- Paraphrasing: "So what I'm hearing is..."
- Referencing a point someone made earlier in the meeting
- Asking quieter participants for input

Poor listening indicators:
- Asking a question that was already answered
- Restating own point without acknowledging the response
- Responding to a question with an unrelated topic

Report the ratio of open/clarifying/building vs. closed/leading questions.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-12
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

#### Module: Sentiment & Energy

Track the emotional arc of the user's language across the meeting:
- **Positive markers**: enthusiastic agreement, encouragement, humor, praise
- **Negative markers**: frustration, dismissiveness, sarcasm, curt responses
- **Neutral/flat**: low-energy responses, monosyllabic answers

Flag energy drops — moments where the user's engagement visibly decreases (shorter turns, less substantive responses). These often correlate with discomfort, boredom, or avoidance.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-13
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Top 3 Findings

[Rank by impact. Each finding gets 2-3 sentences + one concrete example with a direct quote and timestamp.]

## Detailed Analysis

### Speaking Dynamics
[Stats table + narrative interpretation + flagged red flags]

### Directness & Conflict Patterns
[Flagged instances grouped by pattern type, with quotes and rewrites]

### Verbal Habits
[Filler word stats, contextual spikes, only if rate > 3/100 words]

### Listening & Questions
[Question type breakdown, listening indicators, specific examples]

### Facilitation
[Only if applicable — agenda, decisions, action items]

### Energy & Sentiment
[Arc summary, flagged drops]

## Strengths
[3 specific things the user does well, with evidence]

## Growth Opportunities
[3 ranked by impact, each with: what to change, why it matters, a concrete "try this next time" action]

## Comparison to Previous Period
[Only if prior analysis exists — delta on key metrics]
```

### 5. Follow-Up Options

After delivering the report, offer:
- Deep dive into any specific meeting or pattern
- A 1-page "communication cheat sheet" with the user's top 3 habits to change
- Tracking setup — save current metrics as a baseline for future comparison
- Export as markdown or structured JSON for use in performance reviews

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-14
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|---|---|---|
| Analyzing without speaker labels | Per-person metrics impossible — results are generic word clouds | Ask user to re-export with speaker identification enabled |
| Running all modules on a 5-minute standup | Overkill — filler word and conflict analysis need 20+ min meetings | Auto-detect meeting length and skip irrelevant modules |
| Presenting raw metrics without context | "You said 'um' 47 times" is demoralizing without benchmarks | Always compare to norms and show trajectory over time |
| Analyzing a single meeting in isolation | One meeting is a snapshot, not a pattern — conclusions are unreliable | Require 3+ meetings minimum for trend-based coaching |
| Treating speaking time equality as the goal | A facilitator SHOULD talk less; a presenter SHOULD talk more | Weight speaking ratios by meeting type and role |
| Flagging every hedge word as negative | "I think" and "maybe" are appropriate in brainstorming | Distinguish between decision meetings (hedges are bad) and ideation (hedges are fine) |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-15
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: pm-skills
description: 6 project management agent skills and plugins for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw. Senior PM, scrum master, Jira expert (JQL), Confluence expert, Atlassian admin, template creator....
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Project Management Skills

6 production-ready project management skills with Atlassian MCP integration.

## Quick Start

### Claude Code
```
/read project-management/jira-expert/SKILL.md
```

### Codex CLI
```bash
npx agent-skills-cli add alirezarezvani/claude-skills/project-management
```

## Skills Overview

| Skill | Folder | Focus |
|-------|--------|-------|
| Senior PM | `senior-pm/` | Portfolio management, risk analysis, resource planning |
| Scrum Master | `scrum-master/` | Velocity forecasting, sprint health, retrospectives |
| Jira Expert | `jira-expert/` | JQL queries, workflows, automation, dashboards |
| Confluence Expert | `confluence-expert/` | Knowledge bases, page layouts, macros |
| Atlassian Admin | `atlassian-admin/` | User management, permissions, integrations |
| Atlassian Templates | `atlassian-templates/` | Blueprints, custom layouts, reusable content |

## Python Tools

6 scripts, all stdlib-only:

```bash
python3 senior-pm/scripts/project_health_dashboard.py --help
python3 scrum-master/scripts/velocity_analyzer.py --help
```

## Rules

- Load only the specific skill SKILL.md you need
- Use MCP tools for live Jira/Confluence operations when available


---
type: skill
lifecycle: stable
inheritance: inheritable
name: scrum-master
description: Advanced Scrum Master skill for data-driven agile team analysis and coaching. Use when the user asks about sprint planning, velocity tracking, retrospectives, standup facilitation, backlog grooming...
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Scrum Master Expert

Data-driven Scrum Master skill combining sprint analytics, probabilistic forecasting, and team development coaching. The unique value is in the three Python analysis scripts and their workflows — refer to `references/` and `assets/` for deeper framework detail.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-18
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Analysis Tools & Usage

### 1. Velocity Analyzer (`scripts/velocity_analyzer.py`)

Runs rolling averages, linear-regression trend detection, and Monte Carlo simulation over sprint history.

```bash
# Text report
python velocity_analyzer.py sprint_data.json --format text

# JSON output for downstream processing
python velocity_analyzer.py sprint_data.json --format json > analysis.json
```

**Outputs**: velocity trend (improving/stable/declining), coefficient of variation, 6-sprint Monte Carlo forecast at 50 / 70 / 85 / 95% confidence intervals, anomaly flags with root-cause suggestions.

**Validation**: If fewer than 3 sprints are present in the input, stop and prompt the user: *"Velocity analysis needs at least 3 sprints. Please provide additional sprint data."* 6+ sprints are recommended for statistically significant Monte Carlo results.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-19
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### 3. Retrospective Analyzer (`scripts/retrospective_analyzer.py`)

Tracks action-item completion, recurring themes, sentiment trends, and team maturity progression.

```bash
python retrospective_analyzer.py sprint_data.json --format text
```

**Outputs**: action-item completion rate by priority/owner, recurring-theme persistence scores, team maturity level (forming/storming/norming/performing), improvement-velocity trend.

**Validation**: Requires 3+ retrospectives with action-item tracking. With fewer, note the limitation and offer partial theme analysis only.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-20
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Sprint Execution Workflows

### Sprint Planning

1. Run velocity analysis: `python velocity_analyzer.py sprint_data.json --format text`
2. Use the 70% confidence interval as the recommended commitment ceiling for the sprint backlog.
3. Review the health scorer's Commitment Reliability and Scope Stability scores to calibrate negotiation with the Product Owner.
4. If Monte Carlo output shows high volatility (CV >20%), surface this to stakeholders with range estimates rather than single-point forecasts.
5. Document capacity assumptions (leave, dependencies) for retrospective comparison.

### Daily Standup

1. Track participation and help-seeking patterns — feed ceremony data into `sprint_health_scorer.py` at sprint end.
2. Log each blocker with date opened; resolution time feeds the Blocker Resolution dimension.
3. If a blocker is unresolved after 2 days, escalate proactively and note in sprint data.

### Sprint Review

1. Present velocity trend and health score alongside the demo to give stakeholders delivery context.
2. Capture scope-change requests raised during review; record as scope-change events in sprint data for next scoring cycle.

### Sprint Retrospective

1. Run all three scripts before the session:
   ```bash
   python sprint_health_scorer.py sprint_data.json --format text > health.txt
   python retrospective_analyzer.py sprint_data.json --format text > retro.txt
   ```
2. Open with the health score and top-flagged dimensions to focus discussion.
3. Use the retrospective analyzer's action-item completion rate to determine how many new action items the team can realistically absorb (target: ≤3 if completion rate <60%).
4. Assign each action item an owner and measurable success criterion before closing the session.
5. Record new action items in `sprint_data.json` for tracking in the next cycle.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-21
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Key Metrics & Targets

| Metric | Target |
|---|---|
| Overall Health Score | >80/100 |
| Psychological Safety Index | >4.0/5.0 |
| Velocity CV (predictability) | <20% |
| Commitment Reliability | >85% |
| Scope Stability | <15% mid-sprint changes |
| Blocker Resolution Time | <3 days |
| Ceremony Engagement | >90% |
| Retrospective Action Completion | >70% |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-22
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Related Skills

- **Agile Product Owner** (`product-team/agile-product-owner/`) — User stories and backlog feed sprint planning
- **Senior PM** (`project-management/senior-pm/`) — Portfolio health context informs sprint priorities

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-23
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: senior-pm
description: Senior Project Manager for enterprise software, SaaS, and digital transformation projects. Specializes in portfolio management, quantitative risk analysis, resource optimization, stakeholder alignm...
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Senior Project Management Expert

## Overview

Strategic project management for enterprise software, SaaS, and digital transformation initiatives. Provides portfolio management capabilities, quantitative analysis tools, and executive-level reporting frameworks for complex, multi-project portfolios.

### Core Expertise Areas

**Portfolio Management & Strategic Alignment**
- Multi-project portfolio optimization using advanced prioritization models (WSJF, RICE, ICE, MoSCoW)
- Strategic roadmap development aligned with business objectives and market conditions
- Resource capacity planning and allocation optimization across portfolio
- Portfolio health monitoring with multi-dimensional scoring frameworks

**Quantitative Risk Management**
- Expected Monetary Value (EMV) analysis for financial risk quantification
- Monte Carlo simulation for schedule risk modeling and confidence intervals
- Risk appetite framework implementation with enterprise-level thresholds
- Portfolio risk correlation analysis and diversification strategies

**Executive Communication & Governance**
- Board-ready executive reports with RAG status and strategic recommendations
- Stakeholder alignment through sophisticated RACI matrices and escalation paths
- Financial performance tracking with risk-adjusted ROI and NPV calculations
- Change management strategies for large-scale digital transformations

## Methodology & Frameworks

### Three-Tier Analysis Approach

**Tier 1: Portfolio Health Assessment**
Uses `project_health_dashboard.py` to provide comprehensive multi-dimensional scoring:

```bash
python3 scripts/project_health_dashboard.py assets/sample_project_data.json
```

**Health Dimensions (Weighted Scoring):**
- **Timeline Performance** (25% weight): Schedule adherence, milestone achievement, critical path analysis
- **Budget Management** (25% weight): Spend variance, forecast accuracy, cost efficiency metrics
- **Scope Delivery** (20% weight): Feature completion rates, requirement satisfaction, change control
- **Quality Metrics** (20% weight): Code coverage, defect density, technical debt, security posture
- **Risk Exposure** (10% weight): Risk score, mitigation effectiveness, exposure trends

**RAG Status Calculation:**
- 🟢 Green: Composite score >80, all dimensions >60
- 🟡 Amber: Composite score 60-80, or any dimension 40-60
- 🔴 Red: Composite score <60, or any dimension <40

**Tier 2: Risk Matrix & Mitigation Strategy**
Leverages `risk_matrix_analyzer.py` for quantitative risk assessment:

```bash
python3 scripts/risk_matrix_analyzer.py assets/sample_project_data.json
```

**Risk Quantification Process:**
1. **Probability Assessment** (1-5 scale): Historical data, expert judgment, Monte Carlo inputs
2. **Impact Analysis** (1-5 scale): Financial, schedule, quality, and strategic impact vectors
3. **Category Weighting**: Technical (1.2x), Resource (1.1x), Financial (1.4x), Schedule (1.0x)
4. **EMV Calculation**:

```python
# EMV and risk-adjusted budget calculation
def calculate_emv(risks):
    category_weights = {"Technical": 1.2, "Resource": 1.1, "Financial": 1.4, "Schedule": 1.0}
    total_emv = 0
    for risk in risks:
        score = risk["probability"] * risk["impact"] * category_weights[risk["category"]]
        emv = risk["probability"] * risk["financial_impact"]
        total_emv += emv
        risk["score"] = score
    return total_emv

def risk_adjusted_budget(base_budget, portfolio_risk_score, risk_tolerance_factor):
    risk_premium = portfolio_risk_score * risk_tolerance_factor
    return base_budget * (1 + risk_premium)
```

**Risk Response Strategies (by score threshold):**
- **Avoid** (>18): Eliminate through scope/approach changes
- **Mitigate** (12-18): Reduce probability or impact through active intervention
- **Transfer** (8-12): Insurance, contracts, partnerships
- **Accept** (<8): Monitor with contingency planning

**Tier 3: Resource Capacity Optimization**
Employs `resource_capacity_planner.py` for portfolio resource analysis:

```bash
python3 scripts/resource_capacity_planner.py assets/sample_project_data.json
```

**Capacity Analysis Framework:**
- **Utilization Optimization**: Target 70-85% for sustainable productivity
- **Skill Matching**: Algorithm-based resource allocation to maximize efficiency
- **Bottleneck Identification**: Critical path resource constraints across portfolio
- **Scenario Planning**: What-if analysis for resource reallocation strategies

### Advanced Prioritization Models

Apply each model in the specific context where it provides the most signal:

**Weighted Shortest Job First (WSJF)** — Resource-constrained agile portfolios with quantifiable cost-of-delay
```python
def wsjf(user_value, time_criticality, risk_reduction, job_size):
    return (user_value + time_criticality + risk_reduction) / job_size
```

**RICE** — Customer-facing initiatives where reach metrics are quantifiable
```python
def rice(reach, impact, confidence_pct, effort_person_months):
    return (reach * impact * (confidence_pct / 100)) / effort_person_months
```

**ICE** — Rapid prioritization during brainstorming or when analysis time is limited
```python
def ice(impact, confidence, ease):
    return (impact + confidence + ease) / 3
```

**Model Selection — Use this decision logic:**
```
if resource_constrained and agile_methodology and cost_of_delay_quantifiable:
    → WSJF
elif customer_facing and reach_metrics_available:
    → RICE
elif quick_prioritization_needed or ideation_phase:
    → ICE
elif multiple_stakeholder_groups_with_differing_priorities:
    → MoSCoW
elif complex_tradeoffs_across_incommensurable_criteria:
    → Multi-Criteria Decision Analysis (MCDA)
```

Reference: `references/portfolio-prioritization-models.md`

### Risk Management Framework

Reference: `references/risk-management-framework.md`

**Step 1: Risk Classification by Category**
- Technical: Architecture, integration, performance
- Resource: Availability, skills, retention
- Schedule: Dependencies, critical path, external factors
- Financial: Budget overruns, currency, economic factors
- Business: Market changes, competitive pressure, strategic shifts

**Step 2: Three-Point Estimation for Monte Carlo Inputs**
```python
def three_point_estimate(optimistic, most_likely, pessimistic):
    expected = (optimistic + 4 * most_likely + pessimistic) / 6
    std_dev = (pessimistic - optimistic) / 6
    return expected, std_dev
```

**Step 3: Portfolio Risk Correlation**
```python
import math

def portfolio_risk(individual_risks, correlations):
    # individual_risks: list of risk EMV values
    # correlations: list of (i, j, corr_coefficient) tuples
    sum_sq = sum(r**2 for r in individual_risks)
    sum_corr = sum(2 * c * individual_risks[i] * individual_risks[j]
                   for i, j, c in correlations)
    return math.sqrt(sum_sq + sum_corr)
```

**Risk Appetite Framework:**
- **Conservative**: Risk scores 0-8, 25-30% contingency reserves
- **Moderate**: Risk scores 8-15, 15-20% contingency reserves
- **Aggressive**: Risk scores 15+, 10-15% contingency reserves

## Assets & Templates

### Project Charter Template
Reference: `assets/project_charter_template.md`

**Comprehensive 12-section charter including:**
- Executive summary with strategic alignment
- Success criteria with KPIs and quality gates
- RACI matrix with decision authority levels
- Risk assessment with mitigation strategies
- Budget breakdown with contingency analysis
- Timeline with critical path dependencies

### Executive Report Template
Reference: `assets/executive_report_template.md`

**Board-level portfolio reporting with:**
- RAG status dashboard with trend analysis
- Financial performance vs. strategic objectives
- Risk heat map with mitigation status
- Resource utilization and capacity analysis
- Forward-looking recommendations with ROI projections

### RACI Matrix Template
Reference: `assets/raci_matrix_template.md`

**Enterprise-grade responsibility assignment featuring:**
- Detailed stakeholder roster with decision authority
- Phase-based RACI assignments (initiation through deployment)
- Escalation paths with timeline and authority levels
- Communication protocols and meeting frameworks
- Conflict resolution processes with governance integration

### Sample Portfolio Data
Reference: `assets/sample_project_data.json`

**Realistic multi-project portfolio including:**
- 4 projects across different phases and priorities
- Complete financial data (budgets, actuals, forecasts)
- Resource allocation with utilization metrics
- Risk register with probability/impact scoring
- Quality metrics and stakeholder satisfaction data
- Dependencies and milestone tracking

### Expected Output Examples
Reference: `assets/expected_output.json`

**Demonstrates script capabilities with:**
- Portfolio health scores and RAG status
- Risk matrix visualization and mitigation priorities
- Resource capacity analysis with optimization recommendations
- Integration examples showing how outputs complement each other

## Implementation Workflows

### Portfolio Health Review (Weekly)

1. **Data Collection & Validation**
   ```bash
   python3 scripts/project_health_dashboard.py current_portfolio.json
   ```
   ⚠️ If any project composite score <60 or a critical data field is missing, STOP and resolve data integrity issues before proceeding.

2. **Risk Assessment Update**
   ```bash
   python3 scripts/risk_matrix_analyzer.py current_portfolio.json
   ```
   ⚠️ If any risk score >18 (Avoid threshold), STOP and initiate escalation to project sponsor before proceeding.

3. **Capacity Analysis**
   ```bash
   python3 scripts/resource_capacity_planner.py current_portfolio.json
   ```
   ⚠️ If any team utilization >90% or <60%, flag for immediate reallocation discussion before step 4.

4. **Executive Summary Generation**
   - Synthesize outputs into executive report format
   - Highlight critical issues and recommendations
   - Prepare stakeholder communications

### Monthly Strategic Review

1. **Portfolio Prioritization Review**
   - Apply WSJF/RICE/ICE models to evaluate current priorities
   - Assess strategic alignment with business objectives
   - Identify optimization opportunities

2. **Risk Portfolio Analysis**
   - Update risk appetite and tolerance levels
   - Review portfolio risk correlation and concentration
   - Adjust risk mitigation investments

3. **Resource Optimization Planning**
   - Analyze capacity constraints across upcoming quarter
   - Plan resource reallocation and hiring strategies
   - Identify skill gaps and training needs

4. **Stakeholder Alignment Session**
   - Present portfolio health and strategic recommendations
   - Gather feedback on prioritization and resource allocation
   - Align on upcoming quarter priorities and investments

### Quarterly Portfolio Optimization

1. **Strategic Alignment Assessment**
   - Evaluate portfolio contribution to business objectives
   - Assess market and competitive position changes
   - Update strategic priorities and success criteria

2. **Financial Performance Review**
   - Analyze risk-adjusted ROI across portfolio
   - Review budget performance and forecast accuracy
   - Optimize investment allocation for maximum value

3. **Capability Gap Analysis**
   - Identify emerging technology and skill requirements
   - Plan capability building investments
   - Assess make vs. buy vs. partner decisions

4. **Portfolio Rebalancing**
   - Apply three horizons model for innovation balance
   - Optimize risk-return profile using efficient frontier
   - Plan new initiatives and sunset decisions

## Integration Strategies

### Atlassian Integration
- **Jira**: Portfolio dashboards, cross-project metrics, risk tracking
- **Confluence**: Strategic documentation, executive reports, knowledge management
- Use MCP integrations to automate data collection and report generation

### Financial Systems Integration
- **Budget Tracking**: Real-time spend data for variance analysis
- **Resource Costing**: Hourly rates and utilization for capacity planning
- **ROI Measurement**: Value realization tracking against projections

### Stakeholder Management
- **Executive Dashboards**: Real-time portfolio health visualization
- **Team Scorecards**: Individual project performance metrics
- **Risk Registers**: Collaborative risk management with automated escalation

## Handoff Protocols

### TO Scrum Master
**Context Transfer:**
- Strategic priorities and success criteria
- Resource allocation and team composition
- Risk factors requiring sprint-level attention
- Quality standards and acceptance criteria

**Ongoing Collaboration:**
- Weekly velocity and health metrics review
- Sprint retrospective insights for portfolio learning
- Impediment escalation and resolution support
- Team capacity and utilization feedback

### TO Product Owner
**Strategic Context:**
- Market prioritization and competitive analysis
- User value frameworks and measurement criteria
- Feature prioritization aligned with portfolio objectives
- Resource and timeline constraints

**Decision Support:**
- ROI analysis for feature investments
- Risk assessment for product decisions
- Market intelligence and customer feedback integration
- Strategic roadmap alignment and dependencies

### FROM Executive Team
**Strategic Direction:**
- Business objective updates and priority changes
- Budget allocation and resource approval decisions
- Risk appetite and tolerance level adjustments
- Market strategy and competitive response decisions

**Performance Expectations:**
- Portfolio health and value delivery targets
- Timeline and milestone commitment expectations
- Quality standards and compliance requirements
- Stakeholder satisfaction and communication standards

## Success Metrics & KPIs

Reference: `references/portfolio-kpis.md` for full definitions and measurement guidance.

### Portfolio Performance
- On-time Delivery Rate: >80% within 10% of planned timeline
- Budget Variance: <5% average across portfolio
- Quality Score: >85 composite rating
- Risk Mitigation Coverage: >90% risks with active plans
- Resource Utilization: 75-85% average

### Strategic Value
- ROI Achievement: >90% projects meeting projections within 12 months
- Strategic Alignment: >95% investment aligned with business priorities
- Innovation Balance: 70% operational / 20% growth / 10% transformational
- Stakeholder Satisfaction: >8.5/10 executive average
- Time-to-Value: <6 months average post-completion

### Risk Management
- Risk Exposure: Maintain within approved appetite ranges
- Resolution Time: <30 days (medium), <7 days (high)
- Mitigation Cost Efficiency: <20% of total portfolio risk EMV
- Risk Prediction Accuracy: >70% probability assessment accuracy

## Continuous Improvement Framework

### Portfolio Learning Integration
- Capture lessons learned from completed projects
- Update risk probability assessments based on historical data
- Refine estimation accuracy through retrospective analysis
- Share best practices across project teams

### Methodology Evolution
- Regular review of prioritization model effectiveness
- Update risk frameworks based on industry best practices
- Integrate new tools and technologies for analysis efficiency
- Benchmark against industry portfolio performance standards

### Stakeholder Feedback Integration
- Quarterly stakeholder satisfaction surveys
- Executive interview feedback on decision support quality
- Team feedback on process efficiency and effectiveness
- Customer impact assessment of portfolio decisions

## Related Skills

- **Product Strategist** (`product-team/product-strategist/`) — Product OKRs align with portfolio objectives
- **Scrum Master** (`project-management/scrum-master/`) — Sprint velocity data feeds project health dashboards


---
type: skill
lifecycle: stable
inheritance: inheritable
name: team-communications
description: Write internal company communications — 3P updates (Progress/Plans/Problems), company-wide newsletters, FAQ roundups, incident reports, leadership updates, status reports, project updates, and gene...
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Internal Comms

> Originally contributed by [maximcoding](https://github.com/maximcoding) — enhanced and integrated by the claude-skills team.

Write polished internal communications by loading the right reference file, gathering context, and outputting in the company's exact format.

## Routing

Identify the communication type from the user's request, then read the matching reference file before writing anything:

| Type | Trigger phrases | Reference file |
|---|---|---|
| **3P Update** | "3P", "progress plans problems", "weekly team update", "what did we ship" | `references/3p-updates.md` |
| **Newsletter** | "newsletter", "company update", "weekly/monthly roundup", "all-hands summary" | `references/company-newsletter.md` |
| **FAQ** | "FAQ", "common questions", "what people are asking", "confusion around" | `references/faq-answers.md` |
| **General** | anything internal that doesn't match above | `references/general-comms.md` |

If the type is ambiguous, ask one clarifying question — don't guess.

## Workflow

1. **Read the reference file** for the matched type. Follow its formatting exactly.
2. **Gather inputs.** Use available MCP tools (Slack, Gmail, Google Drive, Calendar) to pull real data. If no tools are connected, ask the user to provide bullet points or raw context.
3. **Clarify scope.** Confirm: team name (for 3Ps), time period, audience, and any specific items the user wants included or excluded.
4. **Draft.** Follow the format, tone, and length constraints from the reference file precisely. Do not invent a new format.
5. **Present the draft** and ask if anything needs to be added, removed, or reworded.

## Tone & Style (applies to all types)

- Use "we" — you are part of the company.
- Active voice, present tense for progress, future tense for plans.
- Concise. Every sentence should carry information. Cut filler.
- Include metrics and links wherever possible.
- Professional but approachable — not corporate-speak.
- Put the most important information first.

## When tools are unavailable

If the user hasn't connected Slack, Gmail, Drive, or Calendar, don't stall. Ask them to paste or describe what they want covered. You're formatting and sharpening — that's still valuable. Mention which tools would improve future drafts so they can connect them later.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: project-management-atlassian-skill-26
description: Skill from project-management-atlassian plugin
tier: extended
applyTo: '**/*jira*,**/*confluence*,**/*atlassian*,**/*scrum*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Related Skills

| Skill | Relationship |
|-------|-------------|
| `project-management/senior-pm` | Broader PM scope — status reports feed into PM reporting |
| `project-management/meeting-analyzer` | Meeting insights can feed into 3P updates and status reports |
| `project-management/confluence-expert` | Publish comms as Confluence pages for permanent record |
| `marketing-skill/content-production` | External comms — use for public-facing content, not internal |
