---
name: web-fetch-advanced
description: Use when webfetch fails, need to bypass bot detection, scrape JS sites, download files, or use custom headers/proxies. Multi-method web content fetching with fallback.
---

# Advanced Web Content Fetching

**PURPOSE**: Multi-method web content retrieval with automatic fallback when primary methods fail.

## When to Use This Skill

Use when:
- webfetch tool fails (rate limits, bot detection)
- Need to bypass simple anti-bot protection
- Scraping sites with JavaScript
- Downloading files
- API calls with custom headers
- Need stealth/anonymity

---

## Fetching Method Arsenal

### Method 1: MCP WebFetch (Default)

**Pros:**
- ✅ Built-in tool
- ✅ Simple to use
- ✅ Format conversion (markdown, text, html)

**Cons:**
- ❌ Rate limited by some sites
- ❌ No JavaScript execution
- ❌ Detected as bot by some sites

**Usage:**
```
Use webfetch tool directly
```

**Best For:**
- Documentation sites
- APIs
- Static content
- Government sites

---

### Method 2: PowerShell Invoke-WebRequest

**Pros:**
- ✅ Always available (Windows)
- ✅ Custom headers support
- ✅ Cookie handling
- ✅ Authentication support
- ✅ File downloads

**Cons:**
- ❌ Slower than curl
- ❌ Windows only

**Implementation:**
```powershell
# Basic GET request
$response = Invoke-WebRequest -Uri "https://example.com" -UseBasicParsing
$content = $response.Content

# With custom headers (bypass basic bot detection)
$headers = @{
    'User-Agent' = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    'Accept' = 'text/html,application/json'
    'Accept-Language' = 'en-US,en;q=0.9'
    'Referer' = 'https://google.com'
}
$response = Invoke-WebRequest -Uri "https://target.com" -Headers $headers -UseBasicParsing

# With timeout
$response = Invoke-WebRequest -Uri "https://target.com" -TimeoutSec 30 -UseBasicParsing

# Download file
Invoke-WebRequest -Uri "https://example.com/file.pdf" -OutFile "output.pdf"

# POST request with JSON
$body = @{
    key1 = "value1"
    key2 = "value2"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "https://api.example.com/endpoint" `
    -Method POST `
    -Body $body `
    -ContentType "application/json" `
    -Headers $headers
```

**Best For:**
- API calls
- File downloads
- Sites requiring specific headers
- Windows-native tasks

---

### Method 3: .NET WebClient (Fast & Lightweight)

**Pros:**
- ✅ Very fast
- ✅ Low memory usage
- ✅ Custom headers
- ✅ Progress tracking for downloads

**Cons:**
- ❌ Less features than Invoke-WebRequest
- ❌ Requires manual disposal

**Implementation:**
```powershell
# Simple GET
$client = New-Object System.Net.WebClient
$client.Headers.Add("User-Agent", "Mozilla/5.0")
$content = $client.DownloadString("https://example.com")
$client.Dispose()

# Download file with progress
$client = New-Object System.Net.WebClient
$client.Headers.Add("User-Agent", "Mozilla/5.0")
Register-ObjectEvent -InputObject $client -EventName DownloadProgressChanged -SourceIdentifier WebClient.DownloadProgressChanged -Action {
    Write-Progress -Activity "Downloading" -Status "$($EventArgs.ProgressPercentage)% complete" -PercentComplete $EventArgs.ProgressPercentage
}
$client.DownloadFileAsync("https://example.com/largefile.zip", "output.zip")
# Wait for download
while ($client.IsBusy) { Start-Sleep -Milliseconds 100 }
$client.Dispose()
Unregister-Event -SourceIdentifier WebClient.DownloadProgressChanged

# POST request
$client = New-Object System.Net.WebClient
$client.Headers.Add("Content-Type", "application/json")
$client.Headers.Add("User-Agent", "Mozilla/5.0")
$response = $client.UploadString("https://api.example.com/endpoint", "POST", '{"key":"value"}')
$client.Dispose()
```

**Best For:**
- Large file downloads
- Quick API calls
- Low-resource environments

---

### Method 4: WSL curl (Most Powerful)

**Pros:**
- ✅ Full curl feature set
- ✅ Best header customization
- ✅ Proxy support
- ✅ SSL/TLS options
- ✅ HTTP/2, HTTP/3 support
- ✅ Rate limiting control

**Cons:**
- ❌ Requires WSL
- ❌ Slightly more complex

**Implementation:**
```bash
# Basic GET
wsl -d kali-linux -- curl -s https://example.com

# With custom User-Agent
wsl -d kali-linux -- curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" https://example.com

# Follow redirects
wsl -d kali-linux -- curl -s -L https://example.com

# With headers
wsl -d kali-linux -- curl -s -H "Accept: application/json" -H "Authorization: Bearer TOKEN" https://api.example.com

# POST request with JSON
wsl -d kali-linux -- curl -s -X POST -H "Content-Type: application/json" -d '{"key":"value"}' https://api.example.com

# Download file
wsl -d kali-linux -- curl -s -L -o output.pdf https://example.com/file.pdf

# With timeout
wsl -d kali-linux -- curl -s --max-time 30 https://example.com

# Through proxy
wsl -d kali-linux -- curl -s -x http://proxy:8080 https://example.com

# With cookies
wsl -d kali-linux -- curl -s -b "session=abc123" https://example.com

# Ignore SSL errors (for testing only!)
wsl -d kali-linux -- curl -s -k https://self-signed.example.com

# Rate limiting (1 request per 2 seconds)
wsl -d kali-linux -- curl -s --limit-rate 50k https://example.com
```

**Best For:**
- API testing
- Bypassing bot detection (with custom headers)
- Proxy usage
- SSL/TLS testing
- Maximum control

---

### Method 5: Playwright Browser (JavaScript Support)

**Pros:**
- ✅ Full browser rendering
- ✅ JavaScript execution
- ✅ Bypasses most bot detection
- ✅ Can interact with page elements
- ✅ Screenshots

**Cons:**
- ❌ Slow (full browser)
- ❌ Resource intensive
- ❌ Complex for simple tasks

**Implementation:**
```
Use playwright_browser_navigate tool
Use playwright_browser_snapshot for content
Use playwright_browser_take_screenshot for visual
```

**Best For:**
- JavaScript-heavy sites (SPAs)
- Sites with bot detection
- Interactive content
- When you need to click/fill forms

---

### Method 6: Python requests (via WSL)

**Pros:**
- ✅ Excellent library ecosystem
- ✅ Session management
- ✅ Beautiful Soup integration
- ✅ Retry logic

**Implementation:**
```bash
# Simple GET
wsl -d kali-linux -- python3 -c "import requests; print(requests.get('https://example.com').text)"

# With headers
wsl -d kali-linux -- python3 -c "
import requests
headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get('https://example.com', headers=headers)
print(r.text)
"

# Session with cookies
wsl -d kali-linux -- python3 << 'EOF'
import requests
s = requests.Session()
s.get('https://example.com/login')  # Get cookies
r = s.get('https://example.com/protected')  # Use cookies
print(r.text)
EOF
```

**Best For:**
- Complex scraping
- Session management
- HTML parsing

---

## Automatic Fallback Strategy

### Smart Fetch Workflow

```markdown
ATTEMPT 1: webfetch (fastest)
    ↓ If fails (429, timeout, error)
    
ATTEMPT 2: WSL curl with headers (stealth)
    ↓ If fails (no WSL, blocked)
    
ATTEMPT 3: PowerShell Invoke-WebRequest (custom headers)
    ↓ If fails (still blocked)
    
ATTEMPT 4: Playwright (full browser)
    ↓ If fails (JavaScript errors)
    
FALLBACK: Report failure with details
```

### Implementation Example

**Scenario:** User asks to fetch https://target.com

```powershell
# Try Method 1: webfetch
Try webfetch tool first (fastest)

# If 429 or timeout:
Try WSL curl with stealth headers:
wsl -d kali-linux -- curl -s -L \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Accept: text/html,application/xhtml+xml" \
  -H "Accept-Language: en-US,en;q=0.9" \
  -H "Referer: https://google.com" \
  https://target.com

# If still fails:
Try PowerShell with full headers:
$headers = @{
    'User-Agent' = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    'Accept' = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    'Accept-Language' = 'en-US,en;q=0.9'
    'Accept-Encoding' = 'gzip, deflate, br'
    'Referer' = 'https://www.google.com/'
    'DNT' = '1'
}
Invoke-WebRequest -Uri "https://target.com" -Headers $headers -UseBasicParsing

# If JavaScript required:
Use playwright_browser_navigate → playwright_browser_snapshot
```

---

## Stealth Techniques

### Bypass Basic Bot Detection

**1. Realistic User-Agent:**
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

**2. Full Header Set:**
```powershell
$headers = @{
    'User-Agent' = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    'Accept' = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    'Accept-Language' = 'en-US,en;q=0.9'
    'Accept-Encoding' = 'gzip, deflate, br'
    'DNT' = '1'
    'Connection' = 'keep-alive'
    'Upgrade-Insecure-Requests' = '1'
    'Sec-Fetch-Dest' = 'document'
    'Sec-Fetch-Mode' = 'navigate'
    'Sec-Fetch-Site' = 'none'
    'Cache-Control' = 'max-age=0'
}
```

**3. Random Delays:**
```powershell
# Between requests
Start-Sleep -Milliseconds (Get-Random -Minimum 1000 -Maximum 3000)
```

**4. Referer Spoofing:**
```powershell
$headers['Referer'] = 'https://www.google.com/search?q=target+site'
```

---

## Special Use Cases

### Case 1: Download Large Files

**Best Method:** .NET WebClient with progress

```powershell
$url = "https://example.com/largefile.zip"
$output = "C:\Downloads\file.zip"

$client = New-Object System.Net.WebClient
Register-ObjectEvent -InputObject $client -EventName DownloadProgressChanged -SourceIdentifier Download -Action {
    $percent = $EventArgs.ProgressPercentage
    Write-Host "`rProgress: $percent%" -NoNewline
}

$client.DownloadFile($url, $output)
$client.Dispose()
Unregister-Event -SourceIdentifier Download
Write-Host "`nDownload complete!"
```

### Case 2: Scrape API with Pagination

**Best Method:** WSL curl in loop

```bash
for page in {1..10}; do
  wsl -d kali-linux -- curl -s \
    -H "Authorization: Bearer TOKEN" \
    "https://api.example.com/items?page=$page" >> data.json
  sleep 2  # Rate limiting
done
```

### Case 3: Bypass Cloudflare Basic Protection

**Best Method:** Playwright browser

```
1. playwright_browser_navigate to target
2. playwright_browser_wait_for (wait for challenge)
3. playwright_browser_snapshot (get content after JS loads)
```

### Case 4: Get Data Behind Login

**Best Method:** Python requests with session

```python
import requests

s = requests.Session()

# Login
login_data = {'username': 'user', 'password': 'pass'}
s.post('https://example.com/login', data=login_data)

# Now authenticated
r = s.get('https://example.com/protected/data')
print(r.text)
```

---

## Performance Comparison

| Method | Speed | Stealth | JS Support | Resource Usage |
|--------|-------|---------|------------|----------------|
| webfetch | ⚡⚡⚡ Fast | 🥷 Low | ❌ No | 💻 Low |
| WSL curl | ⚡⚡⚡ Fast | 🥷🥷 Medium | ❌ No | 💻 Low |
| PowerShell | ⚡⚡ Medium | 🥷 Low | ❌ No | 💻 Medium |
| .NET WebClient | ⚡⚡⚡ Fast | 🥷 Low | ❌ No | 💻 Very Low |
| Python requests | ⚡⚡ Medium | 🥷🥷 Medium | ❌ No | 💻 Medium |
| Playwright | ⚡ Slow | 🥷🥷🥷 High | ✅ Yes | 💻💻💻 High |

---

## Troubleshooting

### Error: 429 Too Many Requests

**Solution:**
1. Add delays between requests
2. Use different User-Agent
3. Try through proxy
4. Use Playwright (appears as real browser)

### Error: SSL Certificate Error

**Solution:**
```bash
# curl: Ignore SSL (testing only!)
wsl -d kali-linux -- curl -k https://target.com

# PowerShell: Ignore SSL (testing only!)
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
Invoke-WebRequest -Uri https://target.com
```

### Error: Timeout

**Solution:**
```powershell
# Increase timeout
Invoke-WebRequest -Uri https://slow-site.com -TimeoutSec 60

# Or curl
wsl -d kali-linux -- curl --max-time 60 https://slow-site.com
```

### Error: Blocked by Cloudflare/Bot Detection

**Solution:**
1. Use Playwright (full browser)
2. Add realistic headers
3. Use proxy/VPN
4. Add cookies from real browser session

---

## Summary

**Quick Decision Tree:**

```
Need JavaScript? → Playwright
Need speed? → WSL curl or WebClient
Need stealth? → Playwright or curl with headers
Need file download? → WebClient with progress
Need API call? → WSL curl or PowerShell
Site blocking you? → Try fallback chain
```

**Always Available Methods:**
1. ✅ webfetch (MCP tool)
2. ✅ PowerShell Invoke-WebRequest
3. ✅ .NET WebClient
4. ✅ WSL curl (if WSL installed)
5. ✅ Playwright (if MCP enabled)

**Never rely on single method - always have fallbacks!** 🎯
