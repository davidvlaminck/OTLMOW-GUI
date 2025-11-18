param(
  [string]$ProjectRoot = ".",
  [string]$ReleaseDir = ".\LatestReleaseMulti",
  [string]$VersionFile = "pyproject.toml"
)

# =====
# First install Inno setup only if missing
# =====

# --- helper: common possible ISCC locations ---
# --- ensure ISCC is available, install only if missing ---
# possible disk locations to check (use proper env var syntax)
$possibleIsccPaths = @(
  "${Env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
  "${Env:ProgramFiles}\Inno Setup 6\ISCC.exe",
  "${Env:ProgramFiles(x86)}\Inno Setup 5\ISCC.exe",
  "${Env:ProgramFiles}\Inno Setup 5\ISCC.exe"
)

# helper to find ISCC on disk or in PATH
function Find-ISCC {
  # try PATH first
  $cmd = Get-Command ISCC.exe -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }

  # try common disk locations
  foreach ($p in $possibleIsccPaths) {
    if (Test-Path $p) { return (Resolve-Path $p).Path }
  }

  return $null
}

$ISCC = Find-ISCC
if ($ISCC) {
  Write-Host "ISCC found at $ISCC. Skipping installer." -ForegroundColor Green
} else {
  Write-Host "ISCC not found. Installing Inno Setup..." -ForegroundColor Yellow

  # installer variables
  $downloadUrl   = 'https://www.jrsoftware.org/download.php/is.exe'
  $installerPath = Join-Path $env:TEMP 'InnoSetupInstaller.exe'
  $installDir    = 'C:\Program Files (x86)\Inno Setup 6'
  $maxRetries    = 3
  $retryDelaySec = 3

  # elevation helper (relaunch elevated if needed)
  function Ensure-Elevated {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) {
      Write-Host "Not running as Administrator. Relaunching elevated..." -ForegroundColor Yellow
      $pwsh = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
      if (-not $pwsh) { $pwsh = (Get-Command powershell).Source }
      $args = "-NoProfile -NoLogo -ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Path)`""
      $psi = New-Object System.Diagnostics.ProcessStartInfo($pwsh,$args)
      $psi.Verb = "runas"
      try { [System.Diagnostics.Process]::Start($psi) > $null; exit } catch { Write-Error "Elevation declined. Aborting."; exit 1 }
    }
  }

  Ensure-Elevated

  # download with retries
  $attempt = 0
  while ($attempt -lt $maxRetries) {
    $attempt++
    try {
      Write-Host "Downloading Inno Setup installer (attempt $attempt) to $installerPath ..."
      Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing -TimeoutSec 60
      if (Test-Path $installerPath) { break }
    } catch {
      Write-Warning "Download attempt $attempt failed: $($_.Exception.Message)"
      if ($attempt -lt $maxRetries) { Start-Sleep -Seconds $retryDelaySec } else { Throw "Failed to download installer after $maxRetries attempts" }
    }
  }

  # run silent installer
  Unblock-File -Path $installerPath -ErrorAction SilentlyContinue
  $dirArg = "/DIR=`"$installDir`""
  $arguments = "/VERYSILENT","/SP-","/NORESTART",$dirArg
  Write-Host "Running silent installer ..."
  $proc = Start-Process -FilePath $installerPath -ArgumentList $arguments -Wait -PassThru -NoNewWindow
  if ($proc.ExitCode -ne 0) {
    Remove-Item -Force $installerPath -ErrorAction SilentlyContinue
    Throw "Inno Setup installer exited with code $($proc.ExitCode)"
  }

  # refresh PATH from registry for current session (best-effort)
  try {
    $machinePath = [System.Environment]::GetEnvironmentVariable('Path','Machine')
    $userPath    = [System.Environment]::GetEnvironmentVariable('Path','User')
    if ($machinePath -or $userPath) { $env:Path = ($machinePath + ';' + $userPath).Trim(';') }
  } catch { }

  # find ISCC after install (do not rely solely on PATH)
  $ISCC = Find-ISCC
  if (-not $ISCC) {
    # last-resort search under Program Files roots (use correct env var syntax)
    $searchRoots = @($Env:ProgramFiles, ${Env:ProgramFiles(x86)})
    $search = Get-ChildItem -Path $searchRoots -Filter ISCC.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($search) { $ISCC = $search.FullName }
  }

  Remove-Item -Force $installerPath -ErrorAction SilentlyContinue

  if (-not $ISCC) { Throw "ISCC.exe not found after install. Check installer logs." }

  Write-Host "ISCC discovered at $ISCC" -ForegroundColor Green
}

# export $ISCC for the remainder of the script
Set-Variable -Name ISCC -Value $ISCC -Scope Script -Force

# =====
# After ensuring Inno setup is available, try using it
# =====

$ProjectRoot = (Resolve-Path $ProjectRoot).Path

if (-not $script:ISCC) {
  $script:ISCC = Find-ISCC
}
if (-not $script:ISCC) {
  Write-Error "ISCC.exe not found. Please install Inno Setup or ensure ISCC is discoverable."
  exit 1
}
$ISCC = $script:ISCC
Write-Host "Using ISCC at $ISCC"

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

# Compile with ISCC
& $ISCC /Q /DMyAppDevRoot="$ProjectRoot" /DMyAppVersion="$version" $issPath
if ($LASTEXITCODE -ne 0) {
  Write-Error "Inno Setup compilation failed"
  exit 1
}
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
