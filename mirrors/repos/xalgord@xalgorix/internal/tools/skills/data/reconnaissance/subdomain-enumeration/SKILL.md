---
name: subdomain-enumeration
description: Advanced multi-source subdomain enumeration combining passive, active, brute-force, and certificate transparency techniques
---

# Subdomain Enumeration

## Methodology

### Passive Enumeration (No Target Contact)

```bash
# Certificate Transparency
curl -s "https://crt.sh/?q=%.TARGET&output=json" | jq -r '.[].name_value' | sort -u

# DNS aggregators
subfinder -d TARGET -all -recursive -o subs_subfinder.txt
findomain -t TARGET -q -u subs_findomain.txt
assetfinder --subs-only TARGET > subs_assetfinder.txt

# Archives
curl -s "https://web.archive.org/cdx/search/cdx?url=*.TARGET/*&output=json&fl=original" | jq -r '.[].original' | cut -d/ -f3 | sort -u

# SecurityTrails, VirusTotal, Shodan (API keys required)
```

### Active Enumeration

```bash
# DNS brute-force
shuffledns -d TARGET -w /usr/share/wordlists/subdomains-top1m.txt -r resolvers.txt -o subs_brute.txt

# DNS resolution and probing
cat all_subs.txt | dnsx -silent -a -resp -o resolved.txt
cat all_subs.txt | httpx -silent -status-code -title -tech-detect -follow-redirects -o live.txt
```

### Subdomain Takeover Detection

```bash
# CNAME pointing to deprovisioned services
cat all_subs.txt | while read sub; do
  cname=$(dig CNAME "$sub" +short)
  [ -n "$cname" ] && host "$cname" >/dev/null 2>&1 || echo "[TAKEOVER?] $sub -> $cname"
done
subjack -w all_subs.txt -t 100 -timeout 30 -ssl -o takeovers.txt
```

## Coverage Gaps & Validation

- No single source is complete — union four classes before resolving: passive APIs (crt.sh, subfinder/amass with all keys, SecurityTrails, VirusTotal, Shodan/Censys), historical (Wayback CDX, `gau`, GitHub code search), active (`shuffledns` brute-force + `dnsx` resolution), and permutation (`altdns`, `dnsgen`, `gotator` on discovered names to find `dev-`, `staging-`, `api-internal-` siblings).
- Most-missed assets: certificate SANs (parse every cert for extra hostnames), wildcard-hidden hosts that need brute-forcing, internal-naming permutations, ASN-based discovery (`amass intel -asn`) for sibling IP ranges, and reverse-DNS/PTR sweeps that reveal hosts with no public DNS record.
- Defeat wildcard DNS first: resolve a random `$(openssl rand -hex 8).TARGET`; if it answers, capture the wildcard IP/response and filter it out so brute-force results aren't all false positives.
- Validate live and in-scope: resolve with multiple trusted resolvers from different networks (avoid stale/poisoned answers), then `httpx` to confirm a real service responds — a DNS record alone is not a live asset.
- Confirm scope ownership before reporting: map each resolved IP to its ASN/org and cross-check against the engagement's authorized ranges; shared CDN/SaaS IPs (Cloudflare, AWS, GitHub Pages) are often out of scope even when the hostname matches.
- Re-check CNAMEs for takeover, but verify the dangling claim by actually inspecting the provider's "no such bucket/app" fingerprint, not just an `NXDOMAIN` on the target.

## Pro Tips

1. Merge ALL sources before resolving — passive + active + brute-force
2. Use multiple resolvers from different networks to avoid DNS filtering
3. Test wildcard DNS (`*.TARGET`) — some domains resolve all subdomains to one IP
4. Check for subdomain takeover on EVERY CNAME — dangling CNAMEs are free bounties
5. Use `httpx -tech-detect` to identify technology stack per subdomain
