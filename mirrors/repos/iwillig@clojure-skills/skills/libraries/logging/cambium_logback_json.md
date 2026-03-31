---
name: cambium_logback_json_layout
description: JSON layout for Logback to structure log output.
---

# Cambium Logback JSON

A Logback JSON layout configuration for structured JSON logging.

## Overview

cambium.logback.json provides a Logback layout that formats logs as JSON, making them suitable for structured log analysis and aggregation systems.

## Core Concepts

**JSON Layout Configuration**: Configure Logback to output JSON.

```clojure
; In logback.xml or logback-spring.xml:
; <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
;   <encoder class="cambium.logback.core.util.JsonPatternLayout">
;     <pattern>{"level":"%level","timestamp":"%date","logger":"%logger","message":"%message"}</pattern>
;   </encoder>
; </appender>
```

**Structured Log Output**: Logs are emitted as JSON.

```clojure
; With proper Logback configuration:
; {"level":"INFO","timestamp":"2024-01-15T10:30:45Z","logger":"app.handler","message":"Request processed"}
```

## Key Features

- JSON formatted logs
- Customizable layout
- Compatible with log aggregation
- Logback integration
- MDC field inclusion
- Performance optimized

## When to Use

- Production logging to JSON files
- Log aggregation and analysis
- Integration with ELK, Splunk, or similar
- Structured logging requirements

## When NOT to Use

- Local development (text logs more readable)
- Systems without log aggregation

## Common Patterns

```clojure
; Typical logback.xml configuration
; <?xml version="1.0" encoding="UTF-8"?>
; <configuration>
;   <appender name="JSON_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
;     <file>logs/app.json</file>
;     <encoder class="cambium.logback.core.JsonEncoder"/>
;   </appender>
;
;   <logger name="app" level="INFO">
;     <appender-ref ref="JSON_FILE"/>
;   </logger>
; </configuration>
```

## Related Libraries

- cambium/cambium.core - Logging API
- cambium/cambium.codec-cheshire - JSON codec

## Resources

- Official Documentation: https://github.com/cambium-clojure/cambium
- Logback Documentation: http://logback.qos.ch/

## Notes

This project uses Cambium Logback JSON for structured JSON logging in production.
