# @tutti-os/workbench-service

Shared Go Workbench domain service for host daemons.

This package owns:

- typed Workbench snapshot structures
- validation and canonicalization rules
- default empty snapshot behavior
- a narrow `Store` seam for snapshot persistence

This package does not own:

- HTTP handlers
- OpenAPI-generated DTOs
- SQLite schema or SQL
- Electron or preload wiring
- host-specific product identifiers such as `roomId`

Hosts are responsible for:

1. mapping their transport DTOs into `WorkbenchSnapshot`
2. adapting their persistence layer to the `Store` interface
3. translating host-specific persistence errors to package-level sentinels
