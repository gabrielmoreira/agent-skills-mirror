---
name: cambium_codec_cheshire
description: JSON codec for Cambium structured logging.
---

# Cambium Codec Cheshire

A JSON encoder for Cambium that encodes log data as JSON using Cheshire.

## Overview

cambium.codec-cheshire provides a codec that encodes log messages and context data as JSON, making logs machine-parseable and suitable for log aggregation systems.

## Core Concepts

**JSON Encoding**: Convert log data to JSON.

```clojure
(require '[cambium.core :as log]
         '[cambium.codec-cheshire])

; Configure Cambium with Cheshire codec
; When logs are output, they will be in JSON format:
; {"timestamp":"2024-01-15T10:30:45.123Z","level":"INFO","message":"User created","user-id":1}
```

**Integration with Logback**: Works with Logback JSON layout.

```clojure
; Configuration in logback.xml:
; <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
;   <encoder class="net.logstash.logback.encoder.LogstashEncoder"/>
; </appender>
```

## Key Features

- JSON output for logs
- Compatible with log aggregation
- Structured data preservation
- Performance optimized
- Works with Logback

## When to Use

- Production environments with log aggregation
- ELK stack, Splunk, or other log collectors
- Debugging with structured log analysis

## When NOT to Use

- Development environments (human-readable text better)
- Simple applications without log aggregation

## Common Patterns

```clojure
; Logging with JSON output (when properly configured)
(require '[cambium.core :as log]
         '[cambium.codec-cheshire])

(log/info "User action" {:user-id 123 :action "login" :timestamp (java.time.Instant/now)})

; Output (JSON):
; {"timestamp":"2024-01-15T10:30:45Z","level":"INFO","logger":"app.handler","message":"User action","user_id":123,"action":"login"}
```

## Related Libraries

- cambium/cambium.core - Core logging library
- cambium/cambium.logback.json - Logback JSON layout

## Resources

- Official Documentation: https://github.com/cambium-clojure/cambium
- API Documentation: https://cljdoc.org/d/cambium/cambium.codec-cheshire

## Notes

This project uses Cambium Codec Cheshire for JSON-formatted logs when configured with Logback.
