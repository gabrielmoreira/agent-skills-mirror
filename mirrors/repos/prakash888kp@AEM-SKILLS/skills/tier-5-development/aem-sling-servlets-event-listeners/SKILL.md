# AEM Sling Servlets & Event Listeners

## Purpose
Implement Sling servlets for custom HTTP endpoints and event listeners for reactive content processing in AEM, following Sling framework best practices.

## When to Use (Triggers)
- User mentions "servlet," "endpoint," "event listener," "Sling servlet," or "request handler"
- References to @SlingServletResourceTypes, SlingHttpServletRequest, or resource type binding
- Questions about custom API endpoints, form handlers, or AJAX endpoints in AEM
- Requests involving JCR observation, Sling events, or resource change listeners
- Discussion of custom POST handlers, GET endpoints, or content export servlets

## Core Capabilities
- Implement resource-type-bound Sling servlets with proper method handling
- Create path-bound servlets for system endpoints (with security considerations)
- Build Sling event handlers for content change reactions
- Implement JCR observation listeners for fine-grained content monitoring
- Design Sling jobs for reliable asynchronous processing

## Domain Knowledge Required
### Technical Foundation
- HTTP method semantics (GET, POST, PUT, DELETE) and proper response coding
- Servlet lifecycle and thread safety considerations
- Event handling patterns (synchronous vs. asynchronous, ordered vs. unordered)
- Job scheduling and reliable execution patterns

### AEM-Specific Context
- Sling servlet resolution algorithm (resource type, selectors, extensions, methods)
- @SlingServletResourceTypes vs. @SlingServletPaths annotations
- Sling Event Handling (EventHandler OSGi service with event.topics)
- Sling Jobs API (JobManager, JobConsumer) for reliable async processing
- Resource change listeners (ResourceChangeListener interface)
- CSRF protection for POST endpoints

## Implementation Approach
### Step 1: Endpoint Design
Plan the servlet's contract and integration.
- Define URL pattern: resource-type-based (preferred) or path-based
- Determine HTTP methods to support and response formats (JSON, HTML, binary)
- Plan authentication/authorization requirements
- Design request parameters and validation rules

### Step 2: Servlet Implementation
Build the servlet with proper Sling annotations.
- Annotate with @SlingServletResourceTypes (selectors, extensions, methods)
- Override doGet/doPost/etc. with proper request parsing
- Implement response writing with correct Content-Type headers
- Handle errors with appropriate HTTP status codes
- Add CSRF token validation for mutating operations

### Step 3: Event Listener Development
Implement reactive content processing.
- Create @Component implementing EventHandler with event.topics property
- Define event topic filter for targeted event reception
- Implement handleEvent() with fast execution (offload heavy work)
- Use Sling Jobs for work that must be reliable and retryable

### Step 4: Job-Based Processing
Build reliable async handlers using Sling Jobs.
- Implement JobConsumer for the processing logic
- Create job via JobManager with appropriate topic and payload
- Configure retry behavior and max retries
- Handle job cleanup and failure reporting

### Step 5: Security & Testing
Secure endpoints and validate behavior.
- Ensure resource-type servlets only serve appropriate content
- Add permission checks for sensitive operations
- Configure dispatcher to allow/block servlet paths as needed
- Write unit tests with mock request/response objects

## Quality Checklist
- [ ] Servlets bound to resource types (not paths) where possible
- [ ] CSRF protection enabled for all POST/PUT/DELETE endpoints
- [ ] Response includes proper Content-Type and status codes
- [ ] Event listeners execute quickly and offload heavy work to jobs
- [ ] Sling Jobs handle failures and retry gracefully
- [ ] Servlets are thread-safe (no instance state)
- [ ] Dispatcher configured to route requests to servlets correctly
- [ ] Unit tests cover happy path and error scenarios

## Related Skills
- aem-custom-osgi-services (services used by servlets)
- aem-security-access-control (servlet security)
- aem-webhook-event-driven-architecture (event patterns)

## Example Use Cases
1. **Form Submission Handler:** Implement a Sling servlet handling multi-step form submissions with CSRF validation, input sanitization, persistence to JCR, and email notification triggering via Sling Jobs.
2. **Content Export API:** Build a resource-type-bound servlet that exports page content as JSON with configurable depth, property filtering, and pagination support for headless consumption.
3. **Real-Time Content Sync:** Implement a ResourceChangeListener that detects content changes in a specific path, transforms them into events, and queues Sling Jobs to sync changes to an external search index.

## Notes
- Resource-type-bound servlets are preferred over path-bound — they participate in Sling's resource resolution
- Path-bound servlets require explicit dispatcher allow rules and don't benefit from ACL protection automatically
- Sling Event Handlers are synchronous by default — long-running handlers block the event thread
- Sling Jobs survive instance restarts — use them for work that must not be lost
