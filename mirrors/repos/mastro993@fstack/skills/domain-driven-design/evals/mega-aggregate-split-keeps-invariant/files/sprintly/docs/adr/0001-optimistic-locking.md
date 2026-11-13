# Optimistic locking on every aggregate

Two people editing the same thing must never silently overwrite each other. Each aggregate carries a
version; a save whose version is stale fails with ConcurrencyError and the user reloads.

Considered: last write wins (lost edits in planning sessions); pessimistic locks (people left tabs
open and blocked the team).
