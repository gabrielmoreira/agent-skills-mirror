---
schedule_interval_seconds: null
skill: BaselineQuerier
description: >
  Searches stored behavioral baselines (via vector RAG) and raw logs to answer
  questions about observed network traffic, IP patterns, protocols, ports,
  geographic activity, and alert volumes. Data-agnostic — works with whatever
  baselines network_baseliner has generated.
---

# BaselineQuerier

## Purpose
Search both stored **behavioral baselines** and **raw log records** to answer
user questions about what the network *looks like* and what has *actually happened*.

This skill handles:
- "Show me traffic from Iran last month"
- "What are the top 10 alerts from yesterday?"
- "Any flows to 8.8.8.8?"
- "What protocols are common?"
- "Any traffic on port 1194?"

## What It Does NOT Handle
- **Field schema questions** ("what field holds bytes?") → use `fields_querier`
- **Threat reputation** ("is this IP malicious?") → use `threat_analyst`
- **Creating baselines** → use `network_baseliner`

## Process
1. Retrieve relevant behavioral baseline docs from the vector index
   (network_behavior_baseline, protocol_port_baseline, ip_communication_baseline, dns_baseline)
2. Search raw logs using an LLM-crafted OpenSearch query
3. Combine baseline context with observed records
4. Synthesise a concise, factual answer

## Data Extraction Rules

### 1. Extract Exact Values
- Quote timestamps, IPs, ports, and protocols directly from the data.
- Never paraphrase — show actual values.

### 2. Count Accurately
- Use exact record counts, not vague language ("several", "many").
- If 47 records matched, say 47.

### 3. Timezone Conversions
- Convert UTC timestamps if a user specifies a timezone.

### 4. Be Concise
- Summarise records; do NOT dump raw JSON blocks.
