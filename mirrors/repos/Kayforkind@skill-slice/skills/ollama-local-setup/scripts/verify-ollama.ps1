# verify-ollama.ps1 — deterministic local Ollama health probe (Windows, no external deps)
# Run:  powershell -NoProfile -File scripts/verify-ollama.ps1
$ErrorActionPreference = 'Stop'
$base = 'http://localhost:11434'

function Get-Json($url) {
    try { return (Invoke-RestMethod -Uri $url -TimeoutSec 5) }
    catch { return $null }
}

Write-Host "=== Ollama local check ($base) ===" -ForegroundColor Cyan

# 1. Native endpoint
$tags = Get-Json "$base/api/tags"
$tagNames = if ($tags -and $tags.models) { $tags.models.name } else { @() }
Write-Host "api/tags models: $($tagNames.Count)"
$tagNames | ForEach-Object { Write-Host "  - $_" }

# 2. OpenAI-compatible endpoint
$vm = Get-Json "$base/v1/models"
$vmIds = if ($vm -and $vm.data) { $vm.data.id } else { @() }
Write-Host "v1/models ids:   $($vmIds.Count)"
$vmIds | ForEach-Object { Write-Host "  - $_" }

# 3. Env var (Windows: must be backslashes)
$envVar = $env:OLLAMA_MODELS
$envOk = $false
if ($envVar) {
    $envOk = -not $envVar.Contains('/')   # forward slash => bad
    Write-Host "OLLAMA_MODELS: $envVar  $(if($envOk){'[backslash OK]'}else{'[BAD: use backslashes]'})"
} else {
    Write-Host "OLLAMA_MODELS: (unset)"
}

# 4. Default path vs junction target
$default = Join-Path $env:USERPROFILE '.ollama\models'
$isLink = Test-Path "$default" -PathType Container
$rep = try { (cmd /c fsutil reparsepoint query "$default" 2>$null) } catch { $null }
$linkOk = ($null -ne $rep) -and ($rep -match 'Mount Point|Junction')
Write-Host "default path: $default  $(if($linkOk){'[junction -> '+($envVar)+']'}elseif($isLink){'[dir]'}else{'[missing]'})"

# 5. Verdict
$pass = ($tagNames.Count -gt 0) -and ($vmIds.Count -gt 0)
Write-Host "----------------------------------------" -ForegroundColor Cyan
if ($pass) {
    Write-Host "PASS: server serves $($tagNames.Count) model(s) on both endpoints." -ForegroundColor Green
} else {
    Write-Host "FAIL: no models visible. Check OLLAMA_MODELS backslashes + junction + single server on 11434." -ForegroundColor Red
}
exit $(if($pass){0}else{1})
