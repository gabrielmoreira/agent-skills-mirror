# Baseline Performance Expectations

## Table of Contents

- [Expected Latency Ranges](#expected-latency-ranges)
- [Token Acquisition](#token-acquisition)
- [CRUD Operations](#crud-operations)
- [Paginated Operations](#paginated-operations)
- [LRO Operations](#lro-operations)
- [Interpreting Results](#interpreting-results)
- [Environmental Factors](#environmental-factors)

---

## Expected Latency Ranges

These ranges represent typical performance for Fabric REST API calls from a well-connected Azure or corporate network. Your results may vary based on geographic proximity to the Fabric service, network quality, and capacity SKU.

| Operation | Good (ms) | Acceptable (ms) | Degraded (ms) | Investigate |
|-----------|-----------|-----------------|----------------|------------|
| Token acquisition (client credentials) | <400 | 400-800 | 800-1500 | >1500 |
| Token acquisition (interactive) | <1000 | 1000-2000 | 2000-4000 | >4000 |
| GET single workspace | <200 | 200-400 | 400-800 | >800 |
| GET workspace items (first page) | <300 | 300-600 | 600-1000 | >1000 |
| POST create item (sync) | <500 | 500-1000 | 1000-2000 | >2000 |
| POST create item (LRO initial) | <800 | 800-1500 | 1500-3000 | >3000 |
| GET operation state (poll) | <200 | 200-400 | 400-600 | >600 |
| List workspaces (first page) | <400 | 400-800 | 800-1500 | >1500 |

---

## Token Acquisition

Token acquisition latency depends on the authentication method:

| Method | Typical Range | Notes |
|--------|--------------|-------|
| Client credentials (secret) | 200-600ms | Fastest for automation |
| Client credentials (certificate) | 150-500ms | Slightly faster than secret |
| Interactive browser | 1-3s | Includes user interaction |
| Managed identity (Azure VM) | 100-300ms | Uses local IMDS endpoint |
| Managed identity (App Service) | 150-400ms | Slightly higher due to proxy |

**Red Flags:**

- Token acquisition consistently >2s for client credentials indicates DNS, network, or Entra ID service issues.
- Tokens being acquired on every API call instead of cached adds cumulative latency.

---

## CRUD Operations

Single-item CRUD operations on `api.fabric.microsoft.com`:

| Operation | Expected P50 | Expected P95 |
|-----------|-------------|-------------|
| Get item by ID | 100-250ms | 400-600ms |
| List items (no pagination) | 150-350ms | 500-800ms |
| Create item (synchronous) | 300-700ms | 1000-1500ms |
| Update item | 200-500ms | 600-1000ms |
| Delete item | 200-400ms | 500-800ms |

---

## Paginated Operations

Performance for paginated endpoints depends on total result count:

| Result Count | Expected Total Time | Pages |
|-------------|-------------------|-------|
| <50 items | <500ms | 1 |
| 50-200 items | 500ms-2s | 2-4 |
| 200-1000 items | 2-8s | 4-20 |
| 1000+ items | 8-30s | 20+ |

**Performance Tips:**

- Each page request is a separate HTTP round-trip.
- Sequential pagination is the only option (no parallel page fetching).
- Cache paginated results if the data doesn't change frequently.

---

## LRO Operations

LRO timing varies significantly by operation type:

| Operation Type | Typical Duration | Notes |
|---------------|-----------------|-------|
| Notebook creation | 5-30s | Usually completes in one poll cycle |
| Lakehouse creation | 10-60s | Includes SQL analytics endpoint provisioning |
| Environment publish | 1-5 min | Depends on library/compute changes |
| Large data table load | 1-30 min | Depends on data volume |
| Capacity operations | 5-15 min | Create, resume, suspend |

**Polling Overhead Budget:**

- Aim for <10 poll requests per LRO.
- Each poll should be <300ms network time.
- Total polling overhead should be <5% of total LRO duration.

---

## Interpreting Results

### Green (All Within Range)

Your API integration is performing normally. Document current baselines for future comparison.

### Yellow (Some Degraded)

One or two metrics are in the degraded range. Investigate:

1. Run tests from a different network to rule out local issues
2. Check Azure service health for Fabric
3. Verify token caching is working
4. Review if capacity SKU is under load

### Red (Investigate)

Multiple metrics exceed thresholds. Systematic investigation needed:

1. Isolate the layer: network, auth, or API
2. Test token acquisition independently
3. Test with minimal API calls (single GET)
4. Compare against a different workspace or capacity
5. Check Fabric admin center for capacity health

---

## Environmental Factors

| Factor | Impact | Mitigation |
|--------|--------|------------|
| Geographic distance | +50-200ms per hop | Use regions close to Fabric capacity |
| VPN/proxy | +50-300ms | Test with/without VPN |
| DNS resolution | +10-100ms first call | Use DNS caching |
| TLS handshake | +50-150ms first call | Keep connections alive |
| Capacity under load | +100-500ms | Test during off-peak hours |
| Shared capacity (Trial) | Unpredictable | Use dedicated F SKU for benchmarking |
