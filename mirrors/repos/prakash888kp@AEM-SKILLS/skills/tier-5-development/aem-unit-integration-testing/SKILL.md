# AEM Unit & Integration Testing

## Purpose
Implement comprehensive testing strategies for AEM projects including Sling Model unit tests, integration tests with AEM Mocks, UI tests with Selenium/Cypress, and CI pipeline test automation.

## When to Use (Triggers)
- User mentions "testing," "unit test," "integration test," "AEM Mocks," or "test coverage"
- References to JUnit, Mockito, wcm.io testing, or AEM testing frameworks
- Questions about testing Sling Models, servlets, OSGi services, or workflows
- Requests involving test automation, CI/CD testing, or test-driven development
- Discussion of testing strategies for AEM components or custom code

## Core Capabilities
- Write unit tests for Sling Models using AEM Mocks (io.wcm.testing)
- Implement integration tests with AEM context and repository state
- Configure UI testing with Selenium, Cypress, or Playwright for AEM pages
- Set up test fixtures using JCR content loading and mock resources
- Integrate testing into Maven build lifecycle and CI/CD pipelines

## Domain Knowledge Required
### Technical Foundation
- JUnit 5 architecture (extensions, parameterized tests, lifecycle)
- Mockito mocking framework (when/then, verify, argument captors)
- Test patterns (arrange-act-assert, test fixtures, test doubles)
- Code coverage tools (JaCoCo) and quality gates

### AEM-Specific Context
- AEM Mocks (wcm.io) for in-memory AEM context simulation
- Sling Testing Mocks (ResourceResolver, SlingHttpServletRequest mocks)
- AEM Context JUnit extension for test resource loading
- Content loading from JSON fixtures for test data
- OSGi mock context for service testing
- AEM Cloud Service testing pipeline (unit, integration, UI tiers)

## Implementation Approach
### Step 1: Test Strategy Definition
Plan the testing approach for the project.
- Define test pyramid: unit (70%), integration (20%), UI (10%)
- Identify critical paths requiring integration/UI tests
- Establish code coverage targets (>80% for core bundle)
- Plan test data management strategy

### Step 2: Unit Test Setup
Configure testing framework and write model tests.
- Add AEM Mocks dependencies to core module pom.xml
- Configure AemContext with required resource types and services
- Write tests for Sling Models (property injection, business logic)
- Test servlets with mock request/response objects
- Test OSGi services with mock dependencies

### Step 3: Integration Testing
Implement tests requiring AEM context.
- Load test content from JSON fixtures into AemContext
- Test component rendering with HTL compilation (if applicable)
- Validate workflow execution with mock payloads
- Test query execution against loaded test content
- Verify ACL-dependent behavior with mock users

### Step 4: UI Testing
Implement end-to-end browser testing.
- Configure Selenium/Cypress for AEM author and publish testing
- Create page objects for AEM editing interfaces
- Test component authoring workflow (add, configure, preview)
- Validate publish-side rendering and interaction
- Test responsive behavior across viewports

### Step 5: CI/CD Integration
Automate test execution in build pipeline.
- Configure Maven Surefire/Failsafe for unit/integration separation
- Set up JaCoCo for code coverage reporting and enforcement
- Configure Cloud Manager quality gates for test results
- Implement test parallelization for faster feedback

## Quality Checklist
- [ ] Unit tests cover all Sling Model business logic
- [ ] Integration tests validate critical content operations
- [ ] UI tests cover happy-path user journeys
- [ ] Code coverage meets minimum threshold (>80% core)
- [ ] Tests run reliably in CI without flakiness
- [ ] Test execution time acceptable (unit < 2min, integration < 5min)
- [ ] Test data managed independently (no shared mutable state)
- [ ] Failed tests produce clear, actionable error messages

## Related Skills
- aem-component-development (testing components)
- aem-custom-osgi-services (testing services)
- aem-debugging-log-analysis (debugging test failures)

## Example Use Cases
1. **Sling Model Testing:** Write comprehensive unit tests for a product detail Sling Model verifying property injection, computed fields, null handling, and multi-value property processing using AEM Mocks.
2. **Workflow Process Step Testing:** Test a custom workflow process step that validates page metadata completeness, using AemContext with loaded test content and mock WorkflowSession.
3. **Author Experience Testing:** Implement Cypress tests validating the complete authoring workflow: create page, add component, configure dialog, preview, and publish.

## Notes
- AEM Mocks simulate most AEM functionality in-memory — but not Oak queries or full OSGi container
- Use `@ExtendWith(AemContextExtension.class)` for JUnit 5 AEM test context
- For Cloud Service: unit and integration tests run pre-deploy; UI tests run post-deploy on stage
- Keep unit tests fast (< 100ms each) — move slower tests to integration tier
