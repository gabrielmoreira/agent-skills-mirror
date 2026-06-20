# Dedicated Datacenter Proxies

Dedicated IPs assigned to your account. Access via gateway `ddc.oxylabs.io` (Self-Service) or direct IPs (Enterprise). Distinct from shared rotating pool at `dc.oxylabs.io:8000`.

## Self-Service

Purchased via [dashboard](https://dashboard.oxylabs.io/en/). Proxy list: **My Products → Dedicated Datacenter Proxies → Proxy list** (export JSON/CSV).

| Field | Value |
|-------|-------|
| Entry point | `ddc.oxylabs.io` (fixed) |
| Auth prefix | `user-` (required, case-sensitive) |
| Sticky IP port | `8001` and up — one IP per port |
| Rotation port | `8000` — random IP from your list per request |

**Port = access method, not the IP itself.** IPs are mapped to ports automatically; port numbers stay stable across IP replacements.

### Sticky IP (specific proxy)

```bash
curl -x ddc.oxylabs.io:8001 -U "user-USERNAME:PASSWORD" https://ip.oxylabs.io/location
```

Use port from proxy list for other IPs (8002, 8003, …).

### Rotation (random IP from your pool)

```bash
curl -x ddc.oxylabs.io:8000 -U "user-USERNAME:PASSWORD" https://ip.oxylabs.io/location
```

### Country-filtered rotation

Append `-country-XX` to username (ISO 3166-1 alpha-2):

```bash
curl -x ddc.oxylabs.io:8000 -U "user-USERNAME-country-US:PASSWORD" https://ip.oxylabs.io/location
```

### Location targeting

No username params needed — use the port assigned to the desired location's IP in your proxy list.

### Protocols

| Protocol | Example |
|----------|---------|
| HTTP | `http://ddc.oxylabs.io:8001` |
| HTTPS | `https://ddc.oxylabs.io:8001` |
| SOCKS5 (TCP+UDP) | `socks5h://user-USER:PASS@ddc.oxylabs.io:8001` |

SOCKS5 may be detected by some sites — prefer HTTP/HTTPS if blocked.

### Python pattern

```python
import os, requests

user = os.environ["OXY_DC_USERNAME"]
pwd = os.environ["OXY_DC_PASSWORD"]
port = 8000  # 8001+ for sticky

proxies = {
    "http": f"http://user-{user}:{pwd}@ddc.oxylabs.io:{port}",
    "https": f"http://user-{user}:{pwd}@ddc.oxylabs.io:{port}",
}
resp = requests.get("https://ip.oxylabs.io/location", proxies=proxies)
```

### Whitelisting (dashboard)

**Dedicated Datacenter Proxies → Whitelist** — up to 10 IPv4 addresses. Prefer username/password auth on cloud VMs (AWS, etc.).

### Fair usage (concurrent sessions)

Per proxy IP per billing cycle:
- Under 100 GB usage: 100 concurrent sessions per proxy
- Over 100 GB usage: 10 concurrent sessions per proxy (until cycle ends)

Exceeding limit → `429 Too Many Requests`.

---

## Enterprise

Credentials and proxy list URLs provided by Account Manager. Two access modes:

### Direct IP access

| Auth method | Port | Credentials |
|-------------|------|-------------|
| Username/password | `60000` | Required |
| Whitelisted IP | `65432` | None |

```bash
# Username/password
curl -x 1.2.3.4:60000 -U "USERNAME:PASSWORD" https://ip.oxylabs.io/location

# Whitelisted IP
curl -x 1.2.3.4:65432 https://ip.oxylabs.io/location
```

### Proxy list retrieval

```bash
# Browser or API — HTTP Basic Auth
curl -u "USERNAME:PASSWORD" https://proxy.oxylabs.io/all

# With location metadata
curl -u "USERNAME:PASSWORD" "https://proxy.oxylabs.io/all?showCountry"
curl -u "USERNAME:PASSWORD" "https://proxy.oxylabs.io/all?showCity"
```

**REST API** (same credentials):

| Endpoint | Purpose |
|----------|---------|
| `GET https://api.oxylabs.io/v1/proxies/lists` | List all proxy lists |
| `GET https://api.oxylabs.io/v1/proxies/lists/{uuid}` | Get specific list (IP, port, country, city) |

### Proxy Rotator (optional)

Single rotating endpoint instead of per-IP connections. Contact Account Manager for domain (e.g. `vm.oxylabs.io`). **Always port `60000`.**

```bash
curl -x vm.oxylabs.io:60000 -U "USERNAME:PASSWORD" https://ip.oxylabs.io/location
```

**Sticky session** — add `Proxy-Server: s{N}` header (`s10`, `s2541`, etc.):

```bash
curl -x vm.oxylabs.io:60000 -U "USER:PASS" https://ip.oxylabs.io/location \
  --proxy-header "Proxy-Server: s10"
```

Python sticky session with rotator:

```python
import requests

class ProxyAdapter(requests.adapters.HTTPAdapter):
    def proxy_headers(self, proxy):
        headers = super().proxy_headers(proxy)
        headers["Proxy-Server"] = "s10"
        return headers

s = requests.Session()
s.proxies = {"https": "http://USER:PASS@vm.oxylabs.io:60000"}
s.mount("https://", ProxyAdapter())
s.get("https://ip.oxylabs.io/location")
```

### Whitelist REST API

| Method | Endpoint | Notes |
|--------|----------|-------|
| `GET` | `https://api.oxylabs.io/v1/whitelisted_ips` | List IPs + ids (`200`) |
| `POST` | `https://api.oxylabs.io/v1/whitelisted_ips` | Add one — body `{"address": "x.x.x.x"}` (`201`, `422` invalid) |
| `DELETE` | `https://api.oxylabs.io/v1/whitelisted_ips/{id}` | Remove by id (`204`) |
| `POST` | `https://api.oxylabs.io/v1/whitelisted_ips/upload_to_servers` | Apply changes to servers (`202`; 5-min cooldown → `429`) |

Add/delete changes only take effect after calling `upload_to_servers`.

### Proxy management API

OpenAPI spec: https://dc-api-spec.oxylabs.io/ — add/replace subnets, check offline IPs via Subnets endpoint.

### Protocols (Enterprise)

Default: HTTP (port 80), HTTPS (port 443). SOCKS5 requires support activation — use `socks5h://IP:1180`.

---

## Response Codes

| Code | Meaning |
|------|---------|
| `400` | Bad request — malformed request |
| `403` | Forbidden — restricted target |
| `404` | Domain not found / resource unavailable |
| `407` | Missing/wrong credentials or IP not whitelisted |
| `429` | Concurrent session limit reached |
| `500` | Internal server error |
| `502` | Invalid upstream response |
| `503` | DNS failure to target |
| `504` | Gateway timeout (~60s) |

## Restricted Targets

Blocked by default (contact support@oxylabs.io to verify before purchase): streaming (Netflix, Spotify), banking (PayPal, Binance), government sites, gaming (Steam), ticketing (Ticketmaster), mail (Outlook, Yahoo).
