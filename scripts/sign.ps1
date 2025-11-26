# File: scripts/sign.ps1
# Put this helper next to your existing scripts; it handles single file or directory signing.
param(
  [Parameter(Mandatory=$true)][string]$TargetPath,
  [Parameter(Mandatory=$true)][string]$PfxPath,
  [Parameter(Mandatory=$true)][string]$Password,
  [Parameter(Mandatory=$true)][string]$SigntoolPath
)

if (-not (Test-Path $PfxPath)) { Write-Error "PFX not found at $PfxPath"; exit 1 }
if (-not (Test-Path $SigntoolPath)) { Write-Error "signtool not found at $SigntoolPath"; exit 1 }

$targets = @()
if (Test-Path $TargetPath -PathType Container) {
  $targets = Get-ChildItem -Path $TargetPath -Recurse -Filter '*.exe' -File
} elseif (Test-Path $TargetPath -PathType Leaf) {
  $targets = @(Get-Item $TargetPath)
} else {
  Write-Error "Target not found: $TargetPath"; exit 1
}

foreach ($t in $targets) {
  Write-Host "Signing $($t.FullName)"
  & "$SigntoolPath" sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 /f "$PfxPath" /p "$Password" "$($t.FullName)"
  if ($LASTEXITCODE -ne 0) {
    Write-Error "SignTool failed for $($t.FullName)"
    exit $LASTEXITCODE
  }
}
Write-Host "Signing completed for $($targets.Count) file(s)."