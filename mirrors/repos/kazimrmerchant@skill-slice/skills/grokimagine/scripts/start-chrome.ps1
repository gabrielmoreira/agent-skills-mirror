# Launch owned Relocate-and-Own Chrome with CDP for Grok Imagine.
# Delegates to browser-hub — never invent a second --user-data-dir.
# Usage: pwsh -File start-chrome.ps1

$ErrorActionPreference = "Stop"
$hubRoot = if ($env:BROWSER_HUB) { $env:BROWSER_HUB } else { Join-Path $env:USERPROFILE ".cursor\browser-hub" }
$hub = Join-Path $hubRoot "scripts\start.ps1"
if (-not (Test-Path $hub)) { throw "browser-hub start.ps1 missing: $hub (set BROWSER_HUB)" }
& powershell -NoProfile -ExecutionPolicy Bypass -File $hub -Url "https://grok.com/imagine"
exit $LASTEXITCODE
