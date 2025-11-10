param(
  [string]$ProjectRoot = ".",
  [string]$ReleaseDir = ".\LatestReleaseMulti",
  [string]$VersionFile = "pyproject.toml"
)

set -e

# === helper functions ===
function Get-VersionFromPyproject {
  param([string]$path)
  if (-not (Test-Path $path)) { return $null }
  $content = Get-Content $path -Raw
  $m = [regex]::Match($content, 'version\s*=\s*["''](?<v>[^"'']+)["'']')
  if ($m.Success) { return $m.Groups['v'].Value }
  return $null
}

# === compute variables ===
$version = Get-VersionFromPyproject (Join-Path $ProjectRoot $VersionFile)
if (-not $version) {
  Write-Host "Could not determine version from $VersionFile, using 'dev'" -ForegroundColor Yellow
  $version = "dev"
}

$exeFolder = Join-Path $ReleaseDir "OTL_Wizard_2"
$exeName = "OTL Wizard 2.exe"
$exePath = Join-Path $exeFolder $exeName

if (-not (Test-Path $exePath)) {
  # try original name with spaces (pyinstaller creates "OTL Wizard 2")
  $altPath = Join-Path $ReleaseDir "OTL Wizard 2\$exeName"
  if (Test-Path $altPath) {
    New-Item -ItemType Directory -Path $exeFolder -Force | Out-Null
    Move-Item -Path $altPath -Destination $exePath -Force
    # move data folder too if exists
    $altData = Join-Path $ReleaseDir "OTL Wizard 2\data"
    if (Test-Path $altData) {
      Move-Item -Path $altData -Destination (Join-Path $exeFolder "data") -Force
    }
  } else {
    Write-Error "Executable not found at expected locations: $exePath or $altPath"
    exit 1
  }
}

# === Step: Optionally sign the EXE (placeholder) ===
# You must supply a PFX certificate and password as secrets and configure here.
# Example (uncomment and set env variables or secrets):
# $certPath = $env:SIGNING_CERT_PATH
# $certPass = $env:SIGNING_CERT_PASSWORD
# if ($certPath -and (Test-Path $certPath)) {
#   $signtool = "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe"
#   & $signtool sign /f $certPath /p $certPass /fd SHA256 $exePath
#   if ($LASTEXITCODE -ne 0) { Write-Error "signtool failed"; exit 1 }
# } else {
#   Write-Host "Signing skipped: SIGNING_CERT_PATH not provided or file missing" -ForegroundColor Yellow
# }

# === Step: Compile Inno Setup script ===
# Expect the repository to contain LatestReleaseMulti\inno_setup_installer_setup_script.iss
$issPath = Join-Path $ReleaseDir "inno_setup_installer_setup_script.iss"
if (-not (Test-Path $issPath)) {
  Write-Error "Inno script not found at $issPath"
  exit 1
}

# Replace MyAppDevRoot and version macro in the .iss (producer expects absolute project root)
$issText = Get-Content $issPath -Raw
$issText = $issText -replace 'MyAppDevRoot\s*=\s*".*?"', "MyAppDevRoot=""$ProjectRoot"""
$issText = $issText -replace '#define\s+MyAppVersion\s+".*?"', "#define MyAppVersion `"$version`""
$tmpIss = Join-Path $env:TEMP "inno_build_$(Get-Random).iss"
Set-Content -Path $tmpIss -Value $issText -Encoding UTF8

# Ensure Inno Setup is available. If not, try to install via chocolatey (runner already may have Inno).
if (-not (Get-Command "ISCC.exe" -ErrorAction SilentlyContinue)) {
  Write-Host "ISCC.exe not found. Installing Inno Setup via chocolatey (requires admin)..." -ForegroundColor Yellow
  choco install innosetup -y
  if ($LASTEXITCODE -ne 0) { Write-Error "choco install innosetup failed"; exit 1 }
}

$ISCC = (Get-Command "ISCC.exe").Source
Write-Host "Using ISCC at $ISCC"
& $ISCC /Q $tmpIss
if ($LASTEXITCODE -ne 0) { Write-Error "Inno Setup compilation failed"; exit 1 }

# Inno creates an installer in LatestReleaseMulti folder, with name like "OTL wizard 2 installer V<version>.exe"
# Find the newest exe in the ReleaseDir
$installer = Get-ChildItem -Path $ReleaseDir -Filter "*.exe" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $installer) { Write-Error "Installer .exe not found in $ReleaseDir after Inno compile"; exit 1 }

# Rename/move installer to normalized name
$installerDest = Join-Path $ReleaseDir ("OTL_Wizard_2_installer_V" + $version + ".exe")
Move-Item -Path $installer.FullName -Destination $installerDest -Force

# === Step: Optionally sign the installer (placeholder) ===
# Use the same signtool call as above if you want to sign the installer
# Example:
# & $signtool sign /f $certPath /p $certPass /fd SHA256 $installerDest

# === Step: Create zip distribution (no installer) ===
$zipName = Join-Path $ReleaseDir ("OTL_Wizard_2_V" + $version + ".zip")
if (Test-Path $zipName) { Remove-Item $zipName -Force }
Compress-Archive -Path (Join-Path $exeFolder "*") -DestinationPath $zipName -Force

Write-Host "Packaging complete."
Write-Host "Executable: $exePath"
Write-Host "Installer: $installerDest"
Write-Host "Zip: $zipName"
