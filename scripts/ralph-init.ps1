param(
  [Parameter(Mandatory = $true)]
  [string]$TargetRepo,
  [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$SourceRoot = Split-Path -Parent $PSScriptRoot
$TargetRoot = (Resolve-Path $TargetRepo).ProviderPath

if (-not (Test-Path (Join-Path $TargetRoot '.git'))) {
  throw "[ralph-init] target is not a git repository: $TargetRoot"
}

$CopyItems = @(
  '.codex',
  '.githooks',
  '.agents',
  'omx_discord_bridge',
  'plugins\stock-omx-loop',
  'scripts\omx_autonomous_loop.py',
  'scripts\omx-loop.ps1',
  'scripts\run-discord-bridge.ps1',
  'scripts\ralph-run.ps1',
  'scripts\ralph-init.ps1',
  'scripts\ralph_runtime.py',
  'scripts\verify_ralph_setup.py'
)

foreach ($RelativePath in $CopyItems) {
  $SourcePath = Join-Path $SourceRoot $RelativePath
  if (-not (Test-Path $SourcePath)) {
    throw "[ralph-init] missing source path: $RelativePath"
  }

  $TargetPath = Join-Path $TargetRoot $RelativePath
  $TargetParent = Split-Path -Parent $TargetPath
  if ($TargetParent) {
    New-Item -ItemType Directory -Force -Path $TargetParent | Out-Null
  }

  if (Test-Path $TargetPath) {
    if (-not $Force) {
      Write-Host "[ralph-init] skip existing: $RelativePath"
      continue
    }
    Remove-Item -LiteralPath $TargetPath -Recurse -Force
  }

  Copy-Item -LiteralPath $SourcePath -Destination $TargetPath -Recurse -Force
  Write-Host "[ralph-init] copied: $RelativePath"
}

$TemplatePath = Join-Path $SourceRoot 'templates\ralph-loop.template.yml'
$TargetConfigPath = Join-Path $TargetRoot '.ralph-loop.yml'
if ((-not (Test-Path $TargetConfigPath)) -or $Force) {
  Copy-Item -LiteralPath $TemplatePath -Destination $TargetConfigPath -Force
  Write-Host "[ralph-init] wrote template: .ralph-loop.yml"
} else {
  Write-Host "[ralph-init] keep existing: .ralph-loop.yml"
}

Push-Location $TargetRoot
try {
  git config core.hooksPath .githooks
} finally {
  Pop-Location
}

Write-Host "[ralph-init] completed for $TargetRoot"
Write-Host "[ralph-init] next: edit .ralph-loop.yml and omx_discord_bridge/.env.discord"
