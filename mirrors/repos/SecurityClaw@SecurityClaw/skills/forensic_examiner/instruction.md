---
schedule_interval_seconds: null
skill: ForensicExaminer
description: >
  Reconstructs incident timelines by analyzing network activity before, during,
  and after a security incident. Data-agnostic—works with any log schema by
  discovering available fields through RAG baselines.
---

# Forensic Examiner

## Purpose

This skill **reconstructs the full story of an incident** by analyzing a 10-minute window:
- 5 minutes BEFORE the suspected incident time
- The incident itself
- 5 minutes AFTER the incident

When a user reports finding an incident and asks "what happened?", this skill:
1. Extracts incident context (IPs, domains, protocols, timestamps)
2. Queries available data for the time window
3. Builds a forensic narrative showing the chain of events

## Input

Receives an incident report via `context["parameters"]["question"]`.

Examples:
- "What happened with 62.60.131.168 at 14:32?"
- "Can you show me the timeline around the port 1194 connection?"
- "What was the activity involving 192.168.0.16 when this alert fired?"
- "Tell me what happened before and after the DNS query to malicious.com"

## Process

1. **Extract incident context**: Parse IPs, domains, ports, timestamps from the question
2. **Discover available data**: Query RAG for field_documentation to understand the schema
3. **Define time window**: ±5 minutes from the incident timestamp
4. **Query related activity**:
   - DNS queries in the window (what was looked up, by whom, when)
   - Network flows (source → destination, protocol, bytes, packets)
   - Alerts/findings (what was detected, when, why)
   - Responses (did data come back, from where)
   - Protocols used (direction, success/failure indicators)
5. **Build forensic narrative**: Use LLM to construct a timeline story
6. **Return findings**: Structured forensic report with evidence and timeline

## Output

Returns a dict:
```json
{
  "status": "ok",
  "forensic_report": {
    "incident_summary": "What the user reported",
    "time_window": "14:27:00 to 14:37:00 UTC",
    "timeline": [
      {
        "time": "14:27:15 UTC",
        "event": "DNS query for...",
        "evidence": "Record: query=malicious.com from 62.60.131.168"
      },
      {
        "time": "14:29:45 UTC",
        "event": "Initial connection attempt",
        "evidence": "Flow: TCP 62.60.131.168:49302 → target:443, 1024 bytes"
      }
    ],
    "narrative": "Detailed story of what happened and why",
    "confidence": 0.90,
    "evidence_count": 8
  }
}
```

## Data Agnostic

Works with any log schema:
- Network flow logs (Zeek, Suricata, NetFlow, sFlow)
- DNS logs (any format with query/response)
- IDS/IPS alerts (any security tool)
- Endpoint logs (EDR, AV, process execution)
- Application logs (with timestamps)

Uses field_documentation from RAG to understand:
- Which fields contain timestamps
- Which fields contain IPs (source, destination)
- Which fields contain DNS queries
- Which fields contain protocol info
- Which fields contain alert severity

## Timeline Story Building

The narrative explains:
1. **Pre-incident activity**: What was the environment doing before?
2. **Trigger event**: What initiated the incident (DNS lookup, connection attempt)?
3. **Main activity**: The core behavior (data transfer, failed auth, etc.)
4. **Responses**: How did systems respond (blocking, logging, alerts)?
5. **Post-incident**: What happened after (cleanup, exfiltration, lateral movement)?

## Relationship to Other Skills

- **network_baseliner**: *Creates* field documentation → stored in RAG
- **baseline_querier**: Searches behavioral baselines and raw logs (traffic, alerts, patterns)
- **forensic_examiner**: Answers "what happened?" for specific incidents *(this skill)*
- **anomaly_triage**: Detects incidents
- **threat_analyst**: Analyzes the forensic findings

## When to Invoke

Use this skill when:
- User finds an incident and wants the full timeline
- Need to understand what led to an alert
- Investigating lateral movement (show activity before/after key events)
- Analyzing data exfiltration (show DNS, connections, data volume)
- Understanding Failed login → successful connection pattern
- Reconstructing attack chain (initial access → escalation → persistence)

## Evidence Extraction Rules

When building the forensic timeline:

### 1. Preserve Exact Timestamps
- Show all activity in chronological order
- Include fractional seconds if available
- Convert to user's requested timezone if specified

### 2. Link Related Events
- DNS query → connection to same domain/IP (cause & effect)
- Alert triggered → corresponding network flow (evidence)
- Data transfer → volume information (impact)

### 3. Show Complete Context
- For each event, include ALL relevant fields from that record
- Don't filter "unnecessary" fields—show exactly what was logged
- Helps identify suspicious patterns or data omissions

### 4. Highlight Anomalies
- Mark events that deviate from baselines
- Show protocol changes (e.g., plaintext → encrypted)
- Identify unusual ports, volumes, or frequencies

### 5. Answer the 5 W's for Each Event
- WHAT: Type of activity (DNS query, flow, alert, etc.)
- WHERE: Source and destination IPs/domains
- WHEN: Exact timestamp
- WHY: Context from baselines or field documentation
- HOW: Protocol, port, data volume, methods used

### 6. Create a Coherent Narrative
- Don't just list events—explain cause and effect
- Connect DNS queries to subsequent network flows
- Show how data moved through the network
- Explain the attacker's likely objectives based on traffic patterns
