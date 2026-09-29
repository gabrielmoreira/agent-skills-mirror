---
name: subdomain-enumeration
description: Multi-source subdomain discovery combining passive (CT, aggregators) and active (DNS brute-force) techniques with takeover assessment
---

# Subdomain Enumeration

## When to Use
When the target is a domain (not a raw IP) and the scan methodology includes subdomain discovery. Skip when explicitly targeting a single host or when the scan mode says subdomain enumeration is not required.

## Methodology

### Passive Discovery (No Target Contact)
```bash
# Certificate Transparency
curl -s "https://crt.sh/?q=%25.TARGET&output=json" | jq -r '.[].name_value' | sort -u > tmp/ct_subs.txt

# DNS aggregators (passive, no rate impact on target)
subfinder -d TARGET -all -recursive -o tmp/subs_subfinder.txt 2>/dev/null
assetfinder --subs-only TARGET > tmp/subs_assetfinder.txt 2>/dev/null
```

### Active Verification
```bash
# Verify each subdomain is live (resolve + HTTP probe)
while read sub; do
  ip=$(dig +short "$sub" | head -1)
  if [ -n "$ip" ]; then
    code=$(curl -sk -o /dev/null -w "%{http_code}" --max-time 5 "https://$sub/" 2>/dev/null)
    echo "[LIVE] $sub ($ip) HTTP $code" >> tmp/verified_subs.txt
  else
    echo "[DEAD] $sub" >> tmp/dead_subs.txt
  fi
done < tmp/all_subs.txt
```

### Takeover Assessment
For each CNAME record, check if the destination is unclaimed:
```bash
while read sub; do
  cname=$(dig +short CNAME "$sub" | head -1)
  if [ -n "$cname" ]; then
    # Explicit branching (never chain && || — false positives)
    # Check if the CNAME destination resolves
    dest_ip=$(dig +short "$cname" | head -1)
    if [ -z "$dest_ip" ]; then
      # Destination doesn't resolve — potential takeover
      # Verify: does the provider return NXDOMAIN or a provisioning error?
      ns_status=$(dig +short "$cname" | wc -l)
      if [ "$ns_status" -eq 0 ]; then
        echo "[TAKEOVER?] $sub -> $cname (destination unclaimed)"
      fi
    else
      echo "[OK] $sub -> $cname ($dest_ip)"
    fi
  fi
done < tmp/verified_subs.txt
```

**IMPORTANT**: Takeover assessment requires ALL of:
1. A CNAME record exists
2. The destination does not resolve
3. The provider fingerprint matches a known takeover pattern

Never treat generic NXDOMAIN alone as proof of takeover.

## Scope Note

For hostname-scoped engagements, CDN/SaaS-backed infrastructure (AWS, Cloudflare, Fastly, Azure, GitHub Pages) is common and does NOT make a hostname out of scope. The hostname scope is authoritative. IP ownership informs classification only.

## Stopping Criteria
- Primary passive sources queried (CT + at least one aggregator)
- Each discovered subdomain verified live or dead
- Takeover candidates assessed with CNAME + non-resolution + provider fingerprint

## Common Misses
- Wildcard DNS: check with a random subdomain first (`random123.TARGET`)
- Subdomains that resolve but don't serve HTTP (try other protocols)
- Sub-subdomains (api.staging.TARGET)
- Subdomains only in internal DNS
