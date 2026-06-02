# AEM Debugging & Log Analysis

## Purpose
Systematically diagnose and resolve AEM issues using log analysis, debugging tools, error pattern recognition, and structured troubleshooting methodologies.

## When to Use (Triggers)
- User mentions "debug," "error," "exception," "log analysis," or "troubleshoot"
- References to error.log, request.log, stack traces, or AEM error pages
- Questions about diagnosing specific exceptions, null pointers, or bundle issues
- Requests involving log configuration, log aggregation, or error patterns
- Discussion of AEM health problems, startup failures, or runtime errors

## Core Capabilities
- Analyze AEM log files (error.log, request.log, access.log) for issue diagnosis
- Configure logging levels and custom loggers for targeted debugging
- Interpret common AEM exception patterns and their root causes
- Use debugging tools (remote debug, CRXDE Lite, OSGi console)
- Implement structured troubleshooting for complex multi-component issues

## Domain Knowledge Required
### Technical Foundation
- Log4j/SLF4J logging framework configuration and MDC context
- Java exception hierarchy and stack trace interpretation
- Remote debugging with JDWP (Java Debug Wire Protocol)
- Log aggregation patterns (ELK stack, Splunk, Azure Monitor)

### AEM-Specific Context
- AEM log file locations and their purposes (error.log, request.log, stdout.log)
- Sling Log Support configuration via OSGi
- Common AEM exceptions and their meanings (ResourceNotFoundException, LoginException, etc.)
- OSGi bundle lifecycle states and troubleshooting (Installed, Resolved, Active)
- AEM Developer Tools (browser extension, CRXDE, System Console)

## Implementation Approach
### Step 1: Issue Classification
Categorize the problem for targeted investigation.
- Determine error type: startup failure, runtime exception, performance, data corruption
- Identify affected layer: OSGi, Sling, JCR, AEM application, dispatcher
- Check if issue is intermittent or consistent
- Establish timeline: when did the issue start, what changed

### Step 2: Log Collection
Gather relevant log data for analysis.
- Collect error.log entries around issue timestamp
- Review request.log for associated HTTP requests and timing
- Check stdout.log for JVM-level issues (GC, OOM, native errors)
- Examine bundle startup logs for dependency resolution failures

### Step 3: Log Analysis
Interpret log entries to identify root cause.
- Parse stack traces for originating code and nested exceptions
- Identify error patterns (frequency, correlation with user actions)
- Trace request flow through log correlation (request ID, session)
- Check for resource exhaustion (threads, connections, memory)

### Step 4: Active Debugging
Use debugging tools for real-time investigation.
- Attach remote debugger to AEM JVM (port 5005 by default)
- Use CRXDE Lite for content inspection and quick fixes
- Check OSGi console for bundle states and service availability
- Inspect Sling Resource Resolution via Sling console

### Step 5: Resolution & Prevention
Fix the issue and prevent recurrence.
- Implement fix based on identified root cause
- Add targeted logging for future diagnosis of similar issues
- Create monitoring/alerting for the failure condition
- Document the issue pattern and resolution for knowledge base

## Quality Checklist
- [ ] Root cause identified with evidence (not just symptom addressed)
- [ ] Log entries clearly point to the issue origin
- [ ] Custom loggers configured for affected code paths
- [ ] Fix validated in test environment before production
- [ ] Monitoring added to detect recurrence
- [ ] Knowledge base updated with issue pattern
- [ ] Log levels restored to production-appropriate settings after debugging
- [ ] No sensitive data exposed in log output

## Related Skills
- aem-monitoring-alerting (proactive issue detection)
- aem-performance-tuning-profiling (performance-related debugging)
- aem-custom-osgi-services (service-level debugging)

## Example Use Cases
1. **Bundle Resolution Failure:** Diagnose an OSGi bundle stuck in "Installed" state by analyzing dependency resolution errors, identifying missing imports, and resolving version conflicts in Maven dependencies.
2. **Intermittent 500 Errors:** Track down sporadic Internal Server Errors on publish using request.log correlation, error.log stack traces, and thread dump analysis revealing connection pool exhaustion.
3. **Post-Deployment Regression:** Investigate functionality broken after deployment by comparing bundle versions, analyzing Sling Model registration errors, and identifying service ranking conflicts.

## Notes
- Remote debugging on production is extremely risky — it pauses JVM threads. Use only as last resort.
- AEM Cloud Service logs are accessed via Cloud Manager or Adobe Experience League tools
- Configure custom loggers per package (not per class) to balance detail vs. log volume
- Request.log TIMER entries are AEM's built-in profiler — learn to read them
