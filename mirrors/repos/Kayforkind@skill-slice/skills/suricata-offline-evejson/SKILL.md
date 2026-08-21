---
name: suricata-offline-evejson
version: 1.1.1
description: "Runs Suricata offline against PCAPs (-r) and validates alerts in eve.json with jq — syntax check, positive/negative captures, rule regression. Use when testing Suricata rules, forensic PCAP review, or eve.json alert counts. Not for live IDS/IPS on a network interface, general jq tutorials (jq), or Suricata versions older than 6."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
---

## When to Use

Use this skill when you need to test Suricata rules against captured traffic (PCAP files) in a non-live environment, perform forensic analysis on network captures, or validate rule accuracy using positive and negative test sets. Trigger keywords: **suricata offline**, **pcap analysis**, **eve.json**, **rule testing**, **forensic pcap**, **suricata -r**, **alert validation**.

Ideal scenarios:

1. **Rule Development and Testing** — Rapidly iterate on Suricata rules by testing them against a controlled set of PCAPs.
2. **Forensic Analysis** — Analyze suspicious network traffic captures to identify malicious activity using a comprehensive set of Suricata rules.
3. **Regression Testing** — Ensure new rule updates or Suricata version upgrades do not introduce false positives or negatives by re-running against a baseline of PCAPs.
4. **Performance Benchmarking** — Evaluate the performance impact of rule sets or Suricata configurations on specific traffic patterns.

### Do NOT use for

- **Real-time network intrusion detection** or monitoring live traffic interfaces. Offline processing introduces latency.
- **High-Performance Live IDS/IPS** — Not designed for real-time threat detection and prevention.
- **Direct Network Interface Monitoring** — This skill focuses on PCAP analysis only.
- **Large-Scale Production Deployment** — Manual offline PCAP processing is not scalable for continuous monitoring.
- **Sensitive Data Handling** — Be cautious with PCAPs containing sensitive information; ensure proper anonymization or secure environments.
- **Outdated Suricata Versions** — Avoid Suricata versions older than 6.0.0 (ideally 7.0.0+). They may lack critical features, performance improvements, and security patches.

## Prerequisites

| Requirement | Minimum | Preferred |
|---|---|---|
| **Suricata** | 6.0.0 | 7.0.0+ (enhanced performance, EVE JSON schema improvements, new rule keywords) |
| **jq** | Any recent stable | Latest stable |
| **PCAP files** | At least one test capture | Positive + negative test sets |
| **suricata.yaml** | Minimal config with EVE output | Full config tuned for offline use |
| **local.rules** | At least one test rule | Curated rule set with positive/negative coverage |

**Windows host note:** This skill's commands are written for Linux/bash environments (common in Suricata deployment contexts such as WSL, Docker, or remote Linux hosts). If running on a Windows PowerShell host, adapt path separators (`/root/` → your equivalent path) and use `Remove-Item` / `New-Item -ItemType Directory` in place of `rm` / `mkdir -p`. The Suricata and jq CLI flags remain identical across platforms.

## Procedure

### Step 1 — Validate rule syntax (ALWAYS first)

Before any PCAP run, validate that your rules parse correctly. This catches syntax errors, rule conflicts, and configuration issues.

```bash
suricata -T -c /root/suricata.yaml -S /root/local.rules
```

**HARD RULE:** If this exits non-zero, stop. Fix errors in `local.rules` before proceeding. Do not attempt a PCAP run with invalid rules.

### Step 2 — Prepare a clean output directory

Always use a fresh log directory per run to avoid mixing logs from different executions.

```bash
mkdir -p /tmp/suri-output
rm -f /tmp/suri-output/*
```

### Step 3 — Run Suricata on a PCAP

```bash
suricata -c /root/suricata.yaml \
  -S /root/local.rules \
  --runmode autofp \
  -k none \
  -r /root/sample.pcap \
  -l /tmp/suri-output \
  --set eve.outputs.0.filetype=regular \
  --set eve.outputs.0.filename=eve.json
```

**Flag reference:**

| Flag | Purpose |
|---|---|
| `-r <pcap>` | Replay a PCAP offline |
| `-S <rules>` | Load only the specified rules file (repeatable for multiple files) |
| `-l <dir>` | Log directory (will contain `eve.json`) |
| `--runmode autofp` | Auto-selects best runmode; often `pcap-file` for offline processing (recommended for Suricata 6.x/7.x) |
| `-k none` | Ignore checksum issues — useful for malformed or intentionally crafted packets |
| `--set eve.outputs.0.filetype=regular` | Override config to ensure regular file output |
| `--set eve.outputs.0.filename=eve.json` | Explicitly set EVE JSON filename in the log directory |

### Step 4 — Inspect alerts in EVE JSON

**Count alerts:**

```bash
jq -r 'select(.event_type=="alert") | .alert.signature_id' /tmp/suri-output/eve.json | wc -l
```

**List alert IDs and messages:**

```bash
jq -r 'select(.event_type=="alert") | [.alert.signature_id,.alert.signature] | @tsv' /tmp/suri-output/eve.json
```

**Pretty-print full alert details:**

```bash
jq 'select(.event_type=="alert")' /tmp/suri-output/eve.json | less -R
```

**Filter by specific signature ID (e.g., 2000001):**

```bash
jq 'select(.event_type=="alert" and .alert.signature_id == 2000001)' /tmp/suri-output/eve.json
```

### Step 5 — Tight feedback loop (recommended for rule iteration)

When iterating on `/root/local.rules`, validate syntax, then test against known good and bad traffic:

```bash
# 1) Validate rule syntax
echo "--- Validating rule syntax ---"
suricata -T -c /root/suricata.yaml -S /root/local.rules
if [ $? -ne 0 ]; then
    echo "Suricata rule syntax validation failed. Fix errors in local.rules."
    exit 1
fi
echo "Rule syntax is valid."

# 2) Run on known-positive traffic (should generate alerts)
echo "--- Running on known-positive traffic ---"
mkdir -p /tmp/suri-pos
rm -f /tmp/suri-pos/*
suricata -c /root/suricata.yaml -S /root/local.rules --runmode autofp -k none \
  -r /root/pcaps/train_pos.pcap -l /tmp/suri-pos \
  --set eve.outputs.0.filetype=regular --set eve.outputs.0.filename=eve.json
echo "Alerts from positive traffic:"
jq -r 'select(.event_type=="alert") | .alert.signature_id' /tmp/suri-pos/eve.json | sort -n | uniq -c

# 3) Run on known-negative traffic (should NOT generate alerts, or only expected ones)
echo "--- Running on known-negative traffic ---"
mkdir -p /tmp/suri-neg
rm -f /tmp/suri-neg/*
suricata -c /root/suricata.yaml -S /root/local.rules --runmode autofp -k none \
  -r /root/pcaps/train_neg.pcap -l /tmp/suri-neg \
  --set eve.outputs.0.filetype=regular --set eve.outputs.0.filename=eve.json
echo "Alerts from negative traffic (should ideally be 0 or expected benign alerts):"
jq -r 'select(.event_type=="alert") | .alert.signature_id' /tmp/suri-neg/eve.json | sort -n | uniq -c

echo "--- Analysis Complete ---"
```

**Reference:** For a one-command encapsulation of this loop, see `scripts/run_suricata_offline.sh` in this skill folder. Load and review that script when you need repeatable automated runs or want to integrate this workflow into CI.

### Minimal `suricata.yaml` for offline use

For offline analysis, a minimal config is often sufficient. Place at `/root/suricata.yaml`:

```yaml
default-log-dir: /tmp/suri-output
outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: eve.json
      # types:
      #   - alert
      #   - http
      #   - dns
      #   - tls
      #   - flow
```

### Example `local.rules`

```suricata
# Detect HTTP GET request for /evil.php
alert http any any -> any any (msg:"ET WEB_SERVER Possible Malicious PHP Request - evil.php"; flow:to_server,established; http.method; content:"GET"; http.uri; content:"/evil.php"; nocase; classtype:web-application-attack; sid:2000001; rev:1;)

# Detect specific DNS query for example.com
alert dns any any -> any any (msg:"ET DNS Query for example.com"; flow:to_server; dns.query; content:"example.com"; nocase; classtype:misc-activity; sid:2000002; rev:1;)
```

## Pitfalls

- **Never skip syntax validation** — Running Suricata with invalid rules produces misleading or no results. Always run `suricata -T` first.
- **Never reuse a log directory across runs** — Mixing logs from different executions leads to incorrect analysis. Always `rm -f` the output directory before each run.
- **Checksum failures on crafted PCAPs** — Use `-k none` to bypass checksum validation; otherwise Suricata may silently drop packets with bad checksums, producing false negatives.
- **Suricata version too old** — Versions < 6.0.0 lack critical features. Prefer 7.0.0+ for EVE JSON schema improvements and new rule keywords.
- **Memory consumption with large rule sets** — Suricata can consume significant memory. Monitor usage during runs, especially with large PCAPs.
- **Large PCAP performance** — For very large PCAPs, consider `--runmode workers` with `-q <num_queues>` on multi-core systems, or split the PCAP into smaller chunks with `editcap`.
- **Security context** — When running in automated environments, ensure Suricata runs with appropriate permissions (non-root if possible, or minimal capabilities).
- **`-S` overrides `suricata.yaml` rule paths** — When you pass `-S`, only the specified file(s) are loaded. Rules referenced in `suricata.yaml` are NOT included unless you also pass them via additional `-S` flags.
- **EVE JSON is line-delimited JSON (JSONL)** — Each line is a separate JSON object. Do not attempt to parse the entire file as a single JSON document. `jq` handles this naturally when reading from a file.

## Verification

Run through each checkpoint to confirm successful execution:

1. **Suricata installed and version ≥ 6.0.0:**
   ```bash
   suricata --version
   ```

2. **jq installed:**
   ```bash
   jq --version
   ```

3. **Config and rule files exist:**
   ```bash
   ls -l /root/suricata.yaml /root/local.rules
   ```

4. **PCAP file exists:**
   ```bash
   ls -l /root/sample.pcap
   ```

5. **Rule syntax validation passes (exit code 0):**
   ```bash
   suricata -T -c /root/suricata.yaml -S /root/local.rules
   echo "Exit code: $?"
   ```

6. **Offline run executes successfully:**
   ```bash
   mkdir -p /tmp/suri-output && rm -f /tmp/suri-output/*
   suricata -c /root/suricata.yaml -S /root/local.rules --runmode autofp -k none \
     -r /root/sample.pcap -l /tmp/suri-output \
     --set eve.outputs.0.filetype=regular --set eve.outputs.0.filename=eve.json
   ```

7. **`eve.json` created and non-empty:**
   ```bash
   ls -l /tmp/suri-output/eve.json
   head -n 5 /tmp/suri-output/eve.json
   ```

8. **Alert count matches expectations:**
   ```bash
   jq -r 'select(.event_type=="alert") | .alert.signature_id' /tmp/suri-output/eve.json | wc -l
   ```
   Count should be > 0 if `sample.pcap` contains traffic matching your `local.rules`.

9. **Specific alert verification (e.g., sid 2000001):**
   ```bash
   jq 'select(.event_type=="alert" and .alert.signature_id == 2000001)' /tmp/suri-output/eve.json
   ```
   Should return JSON output if the alert was triggered.

## Related Skills

- **Network Traffic Analysis** — Understanding network protocols and traffic patterns is fundamental to effective rule writing and PCAP analysis.
- **Suricata Rule Writing** — Crafting effective and efficient rules: keywords, performance considerations, and common pitfalls.
- **PCAP Manipulation (tcpdump/wireshark/editcap)** — Capturing, filtering, and editing PCAP files for targeted test cases.
- **JSON Processing (jq)** — Proficiency with `jq` is vital for efficiently parsing, filtering, and analyzing `eve.json` output.
- **Containerization (Docker/Podman)** — For reproducible and isolated testing environments, encapsulate Suricata and its dependencies in a container.
