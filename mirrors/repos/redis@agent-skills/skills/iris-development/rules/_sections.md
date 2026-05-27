# Section Definitions

Iris is the umbrella brand for Redis's AI-focused products. The sections below currently cover one product in that family — Redis Agent Memory (RAM) on Redis Cloud. Rules are assigned to sections automatically based on their filename prefix.

---

## 1. Setup & Cloud Service (setup)
**Impact:** HIGH
**Description:** Creating a service on Redis Cloud, authenticating with the official SDKs, and store provisioning.

## 2. Session Memory / Events (session)
**Impact:** HIGH
**Description:** Working-memory conversation history. Appending events, retrieving session memory, and choosing when to use sessions vs long-term memory.

## 3. Long-Term Memory (ltm)
**Impact:** HIGH
**Description:** Persistent, semantically searchable memory records. Bulk create, semantic search with filters, and organizing records with namespace/ownerId/topics/memoryType.

## 4. Memory Promotion (promotion)
**Impact:** MEDIUM
**Description:** Background extraction from session events to long-term memory. Understanding the deduplication window and eventual-consistency semantics.
