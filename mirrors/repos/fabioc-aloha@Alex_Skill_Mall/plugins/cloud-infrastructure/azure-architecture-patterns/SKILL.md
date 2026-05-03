---
type: skill
lifecycle: stable
inheritance: inheritable
name: azure-architecture-patterns
description: Well-Architected Framework principles and Azure best practices
tier: standard
applyTo: '**/*azure*,**/*architecture*,**/*patterns*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Azure Architecture Patterns


> Well-Architected Framework principles, reference architectures, and Azure best practices.

## The Five Pillars

| Pillar | Focus | Key Question |
|--------|-------|--------------|
| Reliability | Resiliency, availability | Will it stay up? |
| Security | Protection, compliance | Is it safe? |
| Cost Optimization | Efficiency, value | Is it worth it? |
| Operational Excellence | Manageability, observability | Can we run it? |
| Performance Efficiency | Scalability, responsiveness | Is it fast enough? |

## Reliability Patterns

### Key Patterns

- **Circuit Breaker**: Fail fast when downstream unhealthy (Polly)
- **Retry with Backoff**: Handle transient failures with exponential delays
- **Availability Zones**: Distribute across datacenters

### Reliability Checklist

- [ ] Single points of failure identified and mitigated
- [ ] Health endpoints implemented (`/health`, `/ready`)
- [ ] Retry policies with backoff
- [ ] Circuit breakers for external dependencies
- [ ] Availability zones utilized
- [ ] RTO/RPO defined and tested

## Security Patterns

### Zero Trust

| Principle | Implementation |
|-----------|----------------|
| Verify explicitly | Always authenticate/authorize |
| Least privilege | Minimal necessary permissions |
| Assume breach | Segment, encrypt, detect |

### Identity

- **Managed Identity**: Eliminate credential management
- **RBAC**: Built-in roles, scope to resource group, use groups

### Network

- **Private Endpoints**: Keep traffic on Azure backbone
- **NSG**: Default deny, explicit allow (priority 100-4096)

### Security Checklist

- [ ] Managed identities (no stored credentials)
- [ ] Key Vault for secrets/certificates
- [ ] Private endpoints for PaaS services
- [ ] NSG rules deny-by-default
- [ ] TLS 1.2+ enforced
- [ ] Microsoft Defender enabled

## Cost Optimization

| Strategy | Impact |
|----------|--------|
| Right-size | Match SKU to workload |
| Reserved Instances | 40-72% savings |
| Spot VMs | 90% discount (interruptible) |
| Auto-shutdown | Dev/test off at night |
| Serverless | Pay per execution |

### Compute Selection

| Workload | Recommended |
|----------|-------------|
| Steady-state web | App Service Premium |
| Event-driven | Azure Functions |
| Batch processing | Container Apps + KEDA |
| Big compute | Spot VMs + Batch |
| Dev/test | B-series VMs |

### Storage Tiers

| Tier | Use Case | Cost |
|------|----------|------|
| Hot | Frequent access | ~$0.02/GB |
| Cool | Infrequent (30+ days) | ~$0.01/GB |
| Archive | Rarely accessed | ~$0.002/GB |

### Cost Checklist

- [ ] Azure Advisor recommendations reviewed
- [ ] Reserved Instances for predictable workloads
- [ ] Auto-shutdown for non-prod
- [ ] Right-sized based on utilization
- [ ] Storage lifecycle policies
- [ ] Cost alerts and budgets set

## Operational Excellence

### IaC Tools

| Tool | Best For |
|------|----------|
| Bicep | Azure-native, declarative |
| Terraform | Multi-cloud, state management |
| ARM | Legacy (avoid for new) |

### Observability Stack

| Layer | Service |
|-------|---------|
| Logs | Log Analytics |
| Metrics | Azure Monitor |
| Traces | Application Insights |
| Alerts | Azure Alerts |
| Dashboards | Azure Workbooks |

### Operational Checklist

- [ ] IaC for all resources (Bicep/Terraform)
- [ ] CI/CD pipelines for deployment
- [ ] Diagnostic settings to Log Analytics
- [ ] Application Insights integrated
- [ ] Alerts for critical metrics

## Performance Efficiency

### Scalability

| Service | Mechanism |
|---------|-----------|
| App Service | Autoscale rules |
| Azure Functions | Event-driven automatic |
| AKS | HPA + Cluster Autoscaler |
| VMSS | Autoscale rules |

### Caching Strategy

| Type | Use Case | Service |
|------|----------|---------|
| CDN | Static content | Azure Front Door |
| Distributed | Session, computed | Redis Cache |
| Local | Hot data | In-memory |

### Performance Checklist

- [ ] Autoscaling configured and tested
- [ ] CDN for static content
- [ ] Redis cache for hot data
- [ ] Database indexes reviewed
- [ ] Load testing completed

## Reference Architectures

### Web Application

```
Internet → Front Door → App Service → Azure SQL + Redis
```

### Microservices

```
Internet → API Management → AKS → Cosmos DB + Service Bus
```

### Serverless

```
Events → Event Grid → Functions → Cosmos DB + Storage
```

## SKU Selection

| Series | Use Case |
|--------|----------|
| B-series | Dev/test (burstable) |
| D-series | Most production |
| E-series | Memory-optimized |
| F-series | Compute-optimized |

## Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Monolithic deployment | Microservices or modular |
| Hardcoded config | App Configuration, Key Vault |
| Single region | Multi-region + Traffic Manager |
| Over-provisioned | Right-size + autoscale |
| No IaC | Bicep/Terraform everything |

## MCP Tools Available

| Tool | Use Case |
|------|----------|
| `mcp_azure_mcp_cloudarchitect` | Interactive architecture design |
| `mcp_azure_mcp_documentation` | Search Azure docs |
| `mcp_azure_mcp_get_bestpractices` | Code gen, deployment patterns |
| Service-specific tools | AKS, App Service, Functions, Cosmos, SQL |
