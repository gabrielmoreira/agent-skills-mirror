# AEM Template & Page Structure

## Purpose
Design and implement editable templates, page components, and structural policies that define the authoring experience and content hierarchy in AEM.

## When to Use (Triggers)
- User mentions "create a template," "page template," or "page structure"
- References to editable templates, template policies, or page properties
- File paths containing `/conf/*/settings/wcm/templates/` or `/conf/*/settings/wcm/policies/`
- Questions about page component hierarchy, structural components, or layout containers
- Requests involving initial content, template types, or template thumbnails

## Core Capabilities
- Create editable templates with structure, initial content, and policies
- Define page component hierarchy with proper sling:resourceSuperType chains
- Configure layout container policies and allowed components
- Implement responsive grid configurations and breakpoints
- Set up page properties dialogs with custom tabs

## Domain Knowledge Required
### Technical Foundation
- AEM editable template editor and its three layers (structure, initial content, policies)
- Page component inheritance chain (project page → core page → foundation page)
- Responsive grid system and layout mode configuration
- JCR node types: cq:Template, cq:Page, cq:PageContent

### AEM-Specific Context
- Template types vs. template instances in /conf
- Content policies and their assignment to layout containers
- Allowed component filtering at template, policy, and container levels
- Page property inheritance and `cq:hierarchyNode` behavior
- Locked vs. unlocked components in template structure

## Implementation Approach
### Step 1: Template Type Definition
Define the blueprint that templates are created from.
- Create template type under `/conf/<project>/settings/wcm/template-types/`
- Define structure node with required structural components
- Set thumbnail and description for template picker

### Step 2: Page Component Setup
Create the page-level component with proper inheritance.
- Define page component extending Core Page Component
- Configure `customheaderlibs.html` and `customfooterlibs.html`
- Set up page properties dialog with project-specific tabs
- Define body.html with responsive grid containers

### Step 3: Template Creation
Build the actual template with structure and policies.
- Create template under `/conf/<project>/settings/wcm/templates/`
- Define structural components (header, footer, navigation)
- Configure locked components vs. author-editable areas
- Set initial content for new page instances

### Step 4: Policy Configuration
Assign component policies to define allowed behaviors.
- Create policies under `/conf/<project>/settings/wcm/policies/`
- Map policies to template containers
- Configure allowed components lists per container
- Define style system options per component policy

### Step 5: Responsive Configuration
Set up breakpoints and responsive grid behavior.
- Configure responsive grid columns (default 12)
- Define breakpoints (phone, tablet, desktop)
- Set responsive policy for layout container
- Configure responsive behavior for structural components

## Quality Checklist
- [ ] Template appears in page creation wizard with correct thumbnail
- [ ] All structural components are locked and non-deletable by authors
- [ ] Allowed components properly filtered per content area
- [ ] Page properties dialog includes all required custom tabs
- [ ] Responsive grid functions correctly across breakpoints
- [ ] Template supports all required page types (content, landing, article)
- [ ] Initial content provides sensible defaults for new pages
- [ ] Page component inherits correctly from Core Components page

## Related Skills
- aem-component-development (components used in templates)
- aem-content-strategy-architecture (content model drives templates)
- aem-msm-multi-site-manager (templates across sites)

## Example Use Cases
1. **Multi-Brand Template System:** Create a template hierarchy supporting 5 brands with shared structural components (global header/footer) but brand-specific policy configurations for allowed components and style options.
2. **Article Page Template:** Design a long-form article template with fixed hero area, flexible body content zone with restricted component palette, and structured sidebar for related content.
3. **Landing Page Template:** Build a marketing-focused template with full-width sections, no navigation constraints, and pre-configured initial content blocks for rapid page creation.

## Notes
- Editable templates are stored under `/conf/`, not `/apps/` — they are content, not code
- Always test template changes on a content page before deploying to production
- Template policies are inherited — child pages get parent template policies unless overridden
- AEM Cloud Service does not support static (legacy) templates; always use editable templates
