# AEM Component Development

## Purpose
Enable the creation, customization, and maintenance of AEM components following best practices for HTL templating, Sling Models, and the component dialog framework.

## When to Use (Triggers)
- User mentions "create a component," "build a component," or "custom component"
- References to HTL, Sling Models, component dialogs, or `.content.xml`
- File paths containing `/apps/*/components/` or `/ui.apps/`
- Questions about component inheritance, proxy components, or resource types
- Requests involving Coral UI or Granite UI dialog fields

## Core Capabilities
- Create complete AEM components with HTL templates, Sling Models, and dialog definitions
- Implement component inheritance and proxy component patterns
- Design responsive component dialogs using Coral UI 3 / Granite UI
- Configure component policies and design dialogs for template editor
- Build composite components using container patterns and data-sly-resource

## Domain Knowledge Required
### Technical Foundation
- HTL (HTML Template Language) syntax including data-sly-use, data-sly-list, data-sly-test, data-sly-resource
- Sling Model injection annotations (@Model, @Inject, @ValueMapValue, @ChildResource)
- JCR node structure and content repository hierarchy
- Maven module structure for ui.apps, core, and ui.frontend

### AEM-Specific Context
- Component resource type resolution and sling:resourceType
- AEM Core Components as foundation (extending vs. proxying)
- Component policies in editable templates
- Client library categories (clientlibs) for CSS/JS bundling
- Experience Fragment and Content Fragment component patterns

## Implementation Approach
### Step 1: Requirements Analysis
Determine component type, authoring needs, and rendering requirements.
- Identify data model (properties, child resources, references)
- Determine dialog complexity (single tab vs. multi-tab, nested multifields)
- Assess if Core Component extension is appropriate

### Step 2: Sling Model Creation
Build the backend model with proper annotations and business logic.
- Define model interface with @Model annotation and adaptables
- Implement injection strategies (@ValueMapValue, @ChildResource, @OSGiService)
- Add @PostConstruct initialization logic
- Include null-safety and default values

### Step 3: HTL Template Development
Create the rendering template with proper structure and semantics.
- Use data-sly-use to bind Sling Model
- Implement conditional rendering with data-sly-test
- Handle empty/unconfigured states with placeholder messaging
- Apply BEM CSS naming conventions

### Step 4: Dialog Definition
Build the authoring dialog using Granite UI components.
- Define .content.xml with cq:dialog node structure
- Configure field types (textfield, pathfield, multifield, select)
- Add field validation (required, pattern, min/max)
- Implement show/hide logic for conditional fields

### Step 5: Client Libraries
Set up CSS and JS bundling for the component.
- Create clientlib folder with css.txt and js.txt
- Define appropriate categories for loading strategy
- Implement component-scoped styles

## Quality Checklist
- [ ] Component renders correctly in author and publish mode
- [ ] Dialog saves all properties to JCR correctly
- [ ] Sling Model handles null/missing data gracefully
- [ ] Component works in Experience Fragments and Content Fragments
- [ ] Accessibility: proper ARIA attributes and semantic HTML
- [ ] Responsive behavior validated across breakpoints
- [ ] Component policy configured for template editor
- [ ] WCM mode handling (edit, preview, disabled)

## Related Skills
- aem-template-page-structure (templates consume components)
- aem-unit-integration-testing (testing Sling Models)
- aem-frontend-build-pipeline (CSS/JS compilation)

## Example Use Cases
1. **Hero Banner Component:** Create a full-width hero with background image, title, description, and CTA button with configurable link, styling variants, and responsive image handling via Dynamic Media.
2. **Product Card Grid:** Build a container component that renders product cards from Content Fragment references with configurable grid layout (2/3/4 columns) and lazy-loading.
3. **Tabbed Content Component:** Implement a container with tab navigation, drag-and-drop authoring of tab panels, and accessible keyboard navigation.

## Notes
- Always extend or proxy AEM Core Components before building from scratch
- AEM Cloud Service requires all components to be editable-template compatible (no static templates)
- Use `cq:isContainer` property for components that allow child component insertion
- Sling Models should target the interface, not the implementation class, for testability
