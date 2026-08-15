# Discover local image/video models for /localimage + /localvideo
# Writes models_discovered.json next to this script. ASCII-only.
$ErrorActionPreference = "Continue"
$outDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$now = (Get-Date).ToString("o")

$imageModels = @()
$comfyRoot = if ($env:COMFYUI_ROOT) { $env:COMFYUI_ROOT } else { Join-Path $env:USERPROFILE "ComfyUI" }
$comfyModels = if ($env:COMFYUI_MODELS) { $env:COMFYUI_MODELS } else { Join-Path $comfyRoot "models" }
foreach ($dir in @(
  (Join-Path $comfyRoot "models\checkpoints"),
  (Join-Path $comfyRoot "models\diffusion_models"),
  (Join-Path $comfyRoot "models\unet"),
  (Join-Path $comfyModels "unet"),
  (Join-Path $comfyModels "checkpoints")
)) {
  if (-not (Test-Path $dir)) { continue }
  Get-ChildItem $dir -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -match '\.(safetensors|ckpt|gguf)$' } |
    ForEach-Object {
      $tags = @()
      $n = $_.Name.ToLowerInvariant()
      if ($n -match 'flux') { $tags += @('photoreal','realistic','cinematic','flux') }
      if ($n -match 'krea') { $tags += @('krea','fast','stylized') }
      if ($n -match 'fp8') { $tags += 'fp8' }
      $imageModels += [pscustomobject]@{
        name = $_.Name
        path = $_.FullName
        gb   = [math]::Round($_.Length / 1GB, 2)
        tags = @($tags | Select-Object -Unique)
      }
    }
}

$imageModels = @($imageModels | Group-Object name | ForEach-Object { $_.Group[0] })

$videoRunners = @()
$lc = if ($env:LONGCAT_ROOT) { $env:LONGCAT_ROOT } else { Join-Path $env:USERPROFILE "Apps\LongCat-Video" }
$runnerDefs = @(
  @{ name = "longcat_t2v";  script = "run_sample_windows.py"; notes = "T2V short (~3s / 49f)" },
  @{ name = "longcat_i2v";  script = "run_i2v_windows.py";    notes = "I2V; prefer --no-distill until LoRA+offload fixed" },
  @{ name = "longcat_long"; script = "run_long_windows.py";   notes = "T2V+continuation (~6-10s)" }
)
foreach ($pair in $runnerDefs) {
  $p = Join-Path $lc $pair.script
  if (Test-Path $p) {
    $videoRunners += [pscustomobject]@{
      name = $pair.name
      script = $p
      notes = $pair.notes
    }
  }
}

$styleMap = [ordered]@{
  "realistic|photoreal|photo|cinematic" = @{
    image_model = "flux1-dev-fp8.safetensors"
    workflow = "localimage-stills/workflows/flux_fp8_t2i.json"
    warn = $false
  }
  "krea|fast|stylized" = @{
    image_model = "krea2_turbo_fp8_scaled.safetensors"
    workflow = "krea (export API JSON if missing)"
    warn = $false
  }
  "pixar|disney|3d cartoon|cgi cartoon" = @{
    image_model = $null
    warn = $true
    note = "No Pixar checkpoint installed. ASK user: Flux photoreal or Krea stylized? Never silent substitute."
  }
  "anime|illustration" = @{
    image_model = "krea2_turbo_fp8_scaled.safetensors"
    warn = $false
    note = "Closest installed stylized path is Krea unless a dedicated anime checkpoint is added."
  }
}

$payload = [ordered]@{
  discovered_at = $now
  image_models = @($imageModels)
  video_runners = @($videoRunners)
  style_map = $styleMap
  rules = @(
    "Parse style words from user prompt; match style_map (case-insensitive).",
    "If warn=true (e.g. pixar) STOP and ask - never silent substitute.",
    "People/celebrities: /localimage still -> approve -> /localvideo I2V.",
    "Log model+style+seed+paths in pack manifest.",
    "Never run ComfyUI and LongCat on the same GPU concurrently."
  )
}

$outPath = Join-Path $outDir "models_discovered.json"
$payload | ConvertTo-Json -Depth 8 | Set-Content $outPath -Encoding utf8
Write-Host "Wrote $outPath"
Write-Host ("image_models={0} video_runners={1}" -f $imageModels.Count, $videoRunners.Count)
