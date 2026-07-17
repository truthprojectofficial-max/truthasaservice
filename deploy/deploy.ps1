<#
.SYNOPSIS
Order Get It Right -- Idempotent Windows installer / launcher.

.DESCRIPTION
Deploys the build to a target install path, installs Python
dependencies, generates convenience launchers, and verifies the
Merkle chain. Designed to be runnable from a USB stick on a clean
Windows host with no human decisions to make.

The script is opinionated about determinism:
  * Refuses to run unless pyproject.toml + 02_Technical\ are in the
    current working directory. A silent misfire is worse than a
    refusal.
  * Refuses to use a Python interpreter older than 3.12. The build
    uses PEP 695 syntax; 3.11 will load the source and crash on
    import.
  * Reports DEGRADED (not COMPLETE) if pip install fails for any
    package. A deploy that reports COMPLETE must be a deploy that
    actually completed.
  * Templated launchers -- every .bat reads the same $InstallPath
    the script was given, so a USB-driven deploy produces
    USB-relative launchers, not C:\OrderGetItRight launchers.
  * Final step re-derives the Merkle chain and prints MATCH or
    BROKEN. A deploy that didn't verify the chain is a deploy that
    didn't deploy.

.PARAMETER DryRun
Walk every step the script would do, log what would happen, and
exit without mutating the filesystem. The dry-run produces a
JSON-shaped report so pytest can parse it and assert each step.

.PARAMETER InstallPath
Where to install. If not specified, defaults to a sibling of the
script's own location. The script is designed to be run from a
USB stick: if it lives at E:\OrderGetItRight\deploy\deploy.ps1,
the default install path is E:\OrderGetItRight. The C:\OrderGetItRight
hardcode from the previous version is gone -- a clean host with no
operator-prepared junction can still deploy, and the deploy lives
where the script lives.

.PARAMETER Yes
Skip the confirmation prompt. Required for unattended operation
(USB stick scenario: a third party double-clicks the script and
walks away). The default is to prompt so a typo'd install path
gets a chance to be caught.

.PARAMETER SkipTauri
Do not invoke build-tauri.ps1 even if OGIR_BUILD_TAURI=1.
Tauri builds take 2-5 minutes and are not part of the runtime
deploy. The default for an unattended USB deploy is to skip
Tauri.

.EXAMPLE
  powershell -File E:\OrderGetItRight\deploy\deploy.ps1 -Yes
  # USB scenario: deploys to E:\OrderGetItRight, runs unattended.

.EXAMPLE
  powershell -File .\deploy\deploy.ps1 -DryRun
  # Reports every step without mutating. Used by the A5 pytest.

.EXAMPLE
  powershell -File .\deploy\deploy.ps1 -InstallPath D:\Recovery -Yes
  # Override the install path; for a third-party recovery operator.
#>

param(
    [switch]$DryRun,
    [string]$InstallPath = "",
    [switch]$Yes,
    [switch]$SkipTauri
)

$ErrorActionPreference = "Stop"
$ProjectName = "Order Get It Right"
$ProjectVersion = "1.0.0"
$ProjectOperator = "Justin Barnett"
$MinPythonMajor = 3
$MinPythonMinor = 12

# ---------------------------------------------------------------------------
# Step 0a -- project root resolution + sanity. Prefer the script's own
# location (so the deploy is USB-launchable: an operator on a clean
# host can double-click the script and it just works). Fall back to
# cwd if $PSScriptRoot is unset (e.g. -File invocation that strips
# it -- PowerShell 5.1 has known quirks here). Refuse to proceed if
# the resolved root has no pyproject.toml AND no 02_Technical\.
# A silent misfire (running from a Downloads folder and copying the
# wrong files) is worse than a hard refusal.
# ---------------------------------------------------------------------------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($ScriptDir -and (Test-Path (Join-Path $ScriptDir "..\pyproject.toml"))) {
    $ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $ScriptDir "..")).Path
} elseif (Test-Path (Join-Path (Get-Location).Path "pyproject.toml")) {
    $ProjectRoot = (Get-Location).Path
} else {
    throw "pyproject.toml not found next to deploy.ps1 (looked in $ScriptDir\..) and not found in cwd ($((Get-Location).Path)). Either run this script from the project root, or keep deploy.ps1 in its original location (deploy/deploy.ps1)."
}
if (-not (Test-Path (Join-Path $ProjectRoot "pyproject.toml"))) {
    throw "pyproject.toml not found in $ProjectRoot. Run this script from the project root (the folder that contains pyproject.toml)."
}
if (-not (Test-Path (Join-Path $ProjectRoot "02_Technical"))) {
    throw "02_Technical\ not found in $ProjectRoot. Run this script from the project root."
}
Write-Host "  -> Project root: $ProjectRoot" -ForegroundColor Green

# ---------------------------------------------------------------------------
# Step 0b -- install-path resolution. Default is "sibling of this script",
# not a hardcoded Windows path. The script is the source of truth for
# where the install should live.
# ---------------------------------------------------------------------------
if ([string]::IsNullOrEmpty($InstallPath)) {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    # The script is at <root>\deploy\deploy.ps1. The install path is
    # the parent of the deploy folder -- the project root itself, or
    # whatever the operator copied the build to.
    $InstallPath = Split-Path -Parent $ScriptDir
    Write-Host "  -> Install path (defaulted from script location): $InstallPath" -ForegroundColor Green
}

$InstallPath = (Resolve-Path -LiteralPath $InstallPath -ErrorAction SilentlyContinue).Path
if (-not $InstallPath) {
    # Path doesn't exist yet. Resolve to absolute form using the cwd.
    $InstallPath = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot $InstallPath))
}

$LauncherDir = Join-Path $InstallPath "launchers"
$LogFile = Join-Path $InstallPath "04_Validation\deploy.log"
$LocalPython = Join-Path $ProjectRoot "02_Technical\python"

# Dry-run report accumulator. The end of the script emits this as a
# machine-readable block so pytest can parse it via ConvertFrom-Json.
$DryRunReport = New-Object System.Collections.Generic.List[object]
$DeployDegraded = $false

function Write-Deploy-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    if (-not $DryRun) {
        Add-Content -Path $LogFile -Value $entry -ErrorAction SilentlyContinue
    }
    if ($Level -eq "WARN") {
        Write-Host "  !! $entry" -ForegroundColor Yellow
    } elseif ($Level -eq "ERROR") {
        Write-Host "  XX $entry" -ForegroundColor Red
    } else {
        Write-Host "  -> $entry" -ForegroundColor Green
    }
}

function Add-DryRun-Step {
    param(
        [string]$Name,
        [string]$Action,
        [string]$Status,    # OK / WARN / FAIL
        [string]$Detail = ""
    )
    $DryRunReport.Add([pscustomobject]@{
        name   = $Name
        action = $Action
        status = $Status
        detail = $Detail
    }) | Out-Null
}

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "          $ProjectName  --  WINDOWS DEPLOYMENT                              " -ForegroundColor Cyan
Write-Host "          Version $ProjectVersion                                            " -ForegroundColor Cyan
Write-Host "          Operator: $ProjectOperator                                          " -ForegroundColor Cyan
Write-Host "          Project root:    $ProjectRoot" -ForegroundColor Cyan
Write-Host "          Install path:    $InstallPath" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "          MODE: DRY RUN (no filesystem mutations)                             " -ForegroundColor Yellow
}
if ($SkipTauri) {
    Write-Host "          Tauri build: SKIPPED (-SkipTauri)                                   " -ForegroundColor Yellow
}
Write-Host "================================================================================" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# Step 0c -- install-path sanity. Catches the A5 foot-gun: a real
# directory at the install path that the script would silently write
# into. A junction or symlink is OK (the operator's own redirect).
#
# The RESEARCH_COMPATIBILITY_2026-07-12.md report (Area 2, finding
# 2.1) noted that .LinkType can be $null on OneDrive Files On-Demand
# cloud-only paths and UNC reparse points. The guard checks for $null
# before the -in comparison so a misleading WARN is not emitted.
# ---------------------------------------------------------------------------
$InstallPathExists = Test-Path $InstallPath
$IsRedirect = $false
$LinkType = ""
$LinkTarget = ""
if ($InstallPathExists) {
    $item = Get-Item $InstallPath -Force -ErrorAction SilentlyContinue
    # Guard: .LinkType may be $null (OneDrive cloud-only, UNC reparse).
    # Use a separate variable so the -in check does not raise on $null.
    $DetectedLinkType = if ($item) { $item.LinkType } else { $null }
    if ($DetectedLinkType -and $DetectedLinkType -in @("SymbolicLink", "Junction")) {
        $IsRedirect = $true
        $LinkType = $DetectedLinkType
        $LinkTarget = $item.Target
    }
}
if ($InstallPathExists) {
    if ($IsRedirect) {
        $msg = "Install path is a redirect ($LinkType): $InstallPath -> $LinkTarget"
        Write-Deploy-Log $msg
        Add-DryRun-Step -Name "install_path" -Action "use $InstallPath" -Status "OK" -Detail "$LinkType -> $LinkTarget"
    } else {
        $msg = "Install path $InstallPath exists and is a real directory. The deploy will write into it. If this is your USB stick, this is what you want. If this is a host folder, override with -InstallPath."
        Write-Deploy-Log $msg "WARN"
        Add-DryRun-Step -Name "install_path" -Action "use $InstallPath" -Status "WARN" -Detail "exists but not a redirect"
    }
} else {
    Write-Deploy-Log "Install path $InstallPath does not exist; will be created"
    Add-DryRun-Step -Name "install_path" -Action "create $InstallPath" -Status "OK" -Detail "will be created"
    if (-not $DryRun) {
        New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
    }
}

# ---------------------------------------------------------------------------
# Confirmation prompt. Default behaviour is to ASK before mutating,
# unless -Yes was given. This is the second-line defence against
# typo'd install paths.
# ---------------------------------------------------------------------------
if (-not $DryRun -and -not $Yes) {
    Write-Host ""
    Write-Host "About to deploy to: $InstallPath" -ForegroundColor Yellow
    $answer = Read-Host "Type 'yes' to proceed, anything else to abort"
    if ($answer -ne "yes") {
        Write-Host "Aborted by operator." -ForegroundColor Red
        exit 1
    }
}

# ---------------------------------------------------------------------------
# Step 1 -- mirror the project tree to the install path
# ---------------------------------------------------------------------------
$Folders = @("00_Strategy", "01_Methodology", "02_Technical", "03_Vault", "04_Validation", "99_Archive", "data", "docs", "tests", "deploy")
foreach ($folder in $Folders) {
    $src = Join-Path $ProjectRoot $folder
    $dst = Join-Path $InstallPath $folder
    if (-not (Test-Path $src)) {
        Write-Host "  -- skipping $folder (not in source tree)" -ForegroundColor DarkGray
        Add-DryRun-Step -Name "mirror_$folder" -Action "skip" -Status "OK" -Detail "source does not exist"
        continue
    }
    # USB-stick case: install path equals project root. Copying the
    # source tree onto itself fails ("Cannot overwrite the item X with
    # itself"). The source IS the destination, so the mirror is a
    # no-op -- skip the copy and report it.
    $SameTree = ((Resolve-Path -LiteralPath $src).Path -eq (Resolve-Path -LiteralPath $dst -ErrorAction SilentlyContinue).Path)
    if ($SameTree) {
        Write-Deploy-Log "Source and destination are the same tree: $src (USB case). Mirror is a no-op."
        Add-DryRun-Step -Name "mirror_$folder" -Action "skip (same tree)" -Status "OK" -Detail "USB case: source = destination"
        continue
    }
    if ($DryRun) {
        $fileCount = (Get-ChildItem -Path $src -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
        Write-Deploy-Log "DRY: would mirror $folder ($fileCount files) -> $dst"
        Add-DryRun-Step -Name "mirror_$folder" -Action "copy $fileCount files" -Status "OK" -Detail "$src -> $dst"
    } else {
        New-Item -ItemType Directory -Force -Path $dst | Out-Null
        # Copy-Item -ErrorAction Stop fails the whole step on the
        # first error. If a single file is locked or unreadable, we
        # want to know.
        Copy-Item -Path (Join-Path $src "*") -Destination $dst -Recurse -Force -ErrorAction Stop
        Write-Deploy-Log "Mirrored $folder to $dst"
    }
}

# Step 1a -- root config files (pyproject.toml, conftest.py) the
# runtime needs to find pytest. These were added this session and
# called out specifically in OPEN_ITEMS A5.
$RootFiles = @("pyproject.toml", "conftest.py")
foreach ($f in $RootFiles) {
    $src = Join-Path $ProjectRoot $f
    $dst = Join-Path $InstallPath $f
    if (Test-Path $src) {
        # USB-stick case: source and destination resolve to the same
        # file. Skip the copy (it's a no-op that Copy-Item refuses to
        # do anyway with "Cannot overwrite the item X with itself").
        $SameFile = ((Resolve-Path -LiteralPath $src).Path -eq (Resolve-Path -LiteralPath $dst -ErrorAction SilentlyContinue).Path)
        if ($SameFile) {
            Add-DryRun-Step -Name "copy_$f" -Action "skip (same file)" -Status "OK" -Detail "USB case: source = destination"
            continue
        }
        if ($DryRun) {
            Write-Deploy-Log "DRY: would copy $f -> $dst"
            Add-DryRun-Step -Name "copy_$f" -Action "copy root file" -Status "OK" -Detail "$src -> $dst"
        } else {
            Copy-Item -Path $src -Destination $dst -Force -ErrorAction Stop
            Write-Deploy-Log "Copied $f -> $dst"
        }
    } else {
        Add-DryRun-Step -Name "copy_$f" -Action "copy root file" -Status "WARN" -Detail "source $src does not exist"
    }
}

# ---------------------------------------------------------------------------
# Step 2 -- Python runtime. Prefer a bundled runtime under the project
# tree; otherwise fall back to the first python.exe on PATH that meets
# the version gate. A clean host with no bundled interpreter must still
# be able to deploy using only a system Python 3.12+ installation.
# ---------------------------------------------------------------------------
function Find-PythonRuntime {
    # Bundled runtime: must contain a usable python.exe.
    $bundled = Join-Path $ProjectRoot "02_Technical\python\python.exe"
    if (Test-Path $bundled) {
        return $bundled
    }
    # No bundled runtime -- use the first python on PATH.
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    return $null
}

$PythonExe = Find-PythonRuntime
if (-not $PythonExe) {
    throw "No Python interpreter found. Install Python $MinPythonMajor.$MinPythonMinor+ and ensure it is on PATH, or place a bundled runtime under 02_Technical\python."
}

# Version gate. PEP 695 syntax (used in the build) requires 3.12+.
$PythonVersion = & $PythonExe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
if (-not $PythonVersion) {
    throw "Could not determine Python version from $PythonExe"
}
$vmajor, $vminor, $vmicro = $PythonVersion.Split('.') | ForEach-Object { [int]$_ }
if (($vmajor -lt $MinPythonMajor) -or ($vmajor -eq $MinPythonMajor -and $vminor -lt $MinPythonMinor)) {
    throw "Python $PythonVersion found at $PythonExe. The build requires Python $MinPythonMajor.$MinPythonMinor or later. Install a newer interpreter and re-run."
}

if (Test-Path (Join-Path $ProjectRoot "02_Technical\python\python.exe")) {
    Write-Deploy-Log "Using bundled Python runtime: $PythonExe (version $PythonVersion)"
    Add-DryRun-Step -Name "python_runtime" -Action "use bundled" -Status "OK" -Detail "$PythonExe (v$PythonVersion)"
} else {
    Write-Deploy-Log "No bundled Python runtime under 02_Technical\python; using PATH Python: $PythonExe (version $PythonVersion)" "WARN"
    Add-DryRun-Step -Name "python_runtime" -Action "use PATH" -Status "OK" -Detail "$PythonExe (v$PythonVersion) [no bundled runtime]"
}

# ---------------------------------------------------------------------------
# Step 3 -- pip install. Best-effort: if a package fails, mark the
# deploy as DEGRADED. The launchers will still be written, but the
# closing banner will say DEGRADED, not COMPLETE.
# ---------------------------------------------------------------------------
$ReqFile = Join-Path $ProjectRoot "02_Technical\requirements.txt"
if ($DryRun) {
    if (Test-Path $ReqFile) {
        $reqLines = (Get-Content $ReqFile | Where-Object { $_ -and -not $_.StartsWith("#") }).Count
        Write-Deploy-Log "DRY: would install $reqLines packages from $ReqFile"
        Add-DryRun-Step -Name "pip_install" -Action "pip install -r requirements.txt" -Status "OK" -Detail "$reqLines packages"
    } else {
        Add-DryRun-Step -Name "pip_install" -Action "pip install -r requirements.txt" -Status "WARN" -Detail "requirements.txt not found at $ReqFile"
    }
} else {
    Write-Deploy-Log "Upgrading pip"
    & $PythonExe -m pip install --upgrade pip --no-warn-script-location 2>&1 | Out-Null
    if (Test-Path $ReqFile) {
        Write-Deploy-Log "Installing Python dependencies from $ReqFile"
        $pipOutput = & $PythonExe -m pip install -r $ReqFile --no-warn-script-location 2>&1
        $pipExit = $LASTEXITCODE
        if ($pipExit -ne 0) {
            $DeployDegraded = $true
            $failed = ($pipOutput | Select-String -Pattern "ERROR:" | Select-Object -First 3) -join "; "
            Write-Deploy-Log ("pip install exited {0}: {1}" -f $pipExit, $failed) "ERROR"
            Add-DryRun-Step -Name "pip_install" -Action "pip install -r requirements.txt" -Status "FAIL" -Detail "exit code $pipExit"
        } else {
            $reqLines = (Get-Content $ReqFile | Where-Object { $_ -and -not $_.StartsWith("#") }).Count
            Add-DryRun-Step -Name "pip_install" -Action "pip install -r requirements.txt" -Status "OK" -Detail "$reqLines packages installed"
        }
    } else {
        Add-DryRun-Step -Name "pip_install" -Action "pip install -r requirements.txt" -Status "WARN" -Detail "requirements.txt not found at $ReqFile"
    }
}

# ---------------------------------------------------------------------------
# Step 4 -- generate convenience launchers. Templated from $InstallPath
# and $PythonExe so they point at the deploy's actual install, not
# the hardcoded C:\OrderGetItRight. The operator can copy the launchers
# to a USB and they still work.
# ---------------------------------------------------------------------------
$Launchers = @(
    # CONCURRENCY ASSUMPTION (F16, 2026-07-18): the Start-Server
    # launcher boots uvicorn with the default single worker. Multi-worker
    # is unsafe: `vault_io.append_block` has no process-wide lock around
    # its read-modify-write of facts_registry.json, and two workers could
    # race to clobber each other. Do NOT add `--workers N` to the
    # launcher without first adding a lock. See DEPLOYMENT.md.
    @{ Name = "Start-Server.bat";
       Body = "@echo off`r`nsetlocal`r`ncd /d `"$InstallPath\02_Technical`"`r`n`"$PythonExe`" -m uvicorn src.server.app:app --host 127.0.0.1 --port 3000`r`n" },
    @{ Name = "Run-AuditCli.bat";
       Body = "@echo off`r`nsetlocal`r`ncd /d `"$InstallPath\02_Technical`"`r`n`"$PythonExe`" -m src.audit_cli %*`r`n" },
    @{ Name = "Verify-Tests.bat";
       Body = "@echo off`r`nsetlocal`r`ncd /d `"$InstallPath`"`r`n`"$PythonExe`" -m pytest tests/ -v`r`n" },
    @{ Name = "Verify-Chain.bat";
       Body = "@echo off`r`nsetlocal`r`ncd /d `"$InstallPath\02_Technical`"`r`n`"$PythonExe`" -m src.verify_chain`r`n" },
    @{ Name = "Build-Tauri-Desktop.bat";
       Body = "@echo off`r`nsetlocal`r`ncd /d `"$InstallPath`"`r`npowershell -ExecutionPolicy Bypass -File deploy\build-tauri.ps1`r`n" }
)
foreach ($L in $Launchers) {
    $launcherPath = Join-Path $LauncherDir $L.Name
    if ($DryRun) {
        Write-Deploy-Log "DRY: would write $launcherPath"
        Add-DryRun-Step -Name "launcher_$($L.Name)" -Action "write" -Status "OK" -Detail $launcherPath
    } else {
        if (-not (Test-Path $LauncherDir)) {
            New-Item -ItemType Directory -Force -Path $LauncherDir | Out-Null
        }
        Set-Content -LiteralPath $launcherPath -Value $L.Body -Encoding ASCII
        Write-Deploy-Log "Wrote $launcherPath"
    }
}

# ---------------------------------------------------------------------------
# Step 5 -- Tauri desktop build. Default: skip. Set OGIR_BUILD_TAURI=1
# (or remove -SkipTauri) to build. Tauri takes 2-5 minutes; not part
# of the runtime path.
# ---------------------------------------------------------------------------
$TauriRequested = ($env:OGIR_BUILD_TAURI -eq "1") -and (-not $SkipTauri)
if ($TauriRequested) {
    if ($DryRun) {
        Write-Deploy-Log "DRY: OGIR_BUILD_TAURI=1 set; would call build-tauri.ps1"
        Add-DryRun-Step -Name "tauri_build" -Action "invoke build-tauri.ps1" -Status "OK" -Detail "OGIR_BUILD_TAURI=1"
    } else {
        Write-Host "Building Tauri desktop binary (OGIR_BUILD_TAURI=1)" -ForegroundColor Cyan
        try {
            & (Join-Path $PSScriptRoot "build-tauri.ps1")
        } catch {
            $DeployDegraded = $true
            Write-Deploy-Log "Tauri build failed: $_" "ERROR"
            Add-DryRun-Step -Name "tauri_build" -Action "invoke build-tauri.ps1" -Status "FAIL" -Detail "$_"
        }
    }
} else {
    $reason = if ($SkipTauri) { "-SkipTauri" } else { "OGIR_BUILD_TAURI not set" }
    Add-DryRun-Step -Name "tauri_build" -Action "skip" -Status "OK" -Detail $reason
}

# ---------------------------------------------------------------------------
# Step 6 -- verify the chain. The build's whole point is that the
# Merkle chain is verifiable. A deploy that doesn't re-verify the
# chain is a deploy that didn't deploy. In dry-run mode we report
# the step; in real mode we run verify_chain.py and inspect the
# output for MATCH.
# ---------------------------------------------------------------------------
if ($DryRun) {
    Add-DryRun-Step -Name "verify_chain" -Action "run src.verify_chain" -Status "OK" -Detail "would run after deploy"
} else {
    $VerifyScript = Join-Path $InstallPath "02_Technical\src\verify_chain.py"
    if (Test-Path $VerifyScript) {
        Write-Deploy-Log "Re-deriving Merkle chain from disk"
        # Run from 02_Technical so that `python -m src.verify_chain`
        # finds the src/ package on sys.path. Without the cd, the
        # script's cwd is wherever the operator launched the deploy
        # from, and Python raises ModuleNotFoundError.
        $VerifyCwd = Join-Path $InstallPath "02_Technical"
        Push-Location -LiteralPath $VerifyCwd
        try {
            $verifyOutput = & $PythonExe -m src.verify_chain 2>&1
        } finally {
            Pop-Location
        }
        $verifyJoined = $verifyOutput -join "`n"
        if ($verifyJoined -match "RESULT: MATCH") {
            Write-Deploy-Log "Chain re-derivation: MATCH"
            Add-DryRun-Step -Name "verify_chain" -Action "run src.verify_chain" -Status "OK" -Detail "MATCH"
        } else {
            $DeployDegraded = $true
            Write-Deploy-Log "Chain re-derivation did NOT return MATCH. See $LogFile for full output." "ERROR"
            Add-DryRun-Step -Name "verify_chain" -Action "run src.verify_chain" -Status "FAIL" -Detail "did not return MATCH"
        }
    } else {
        $DeployDegraded = $true
        Write-Deploy-Log "verify_chain.py not found at $VerifyScript -- cannot verify" "ERROR"
        Add-DryRun-Step -Name "verify_chain" -Action "run src.verify_chain" -Status "FAIL" -Detail "verify_chain.py not found"
    }
}

# ---------------------------------------------------------------------------
# Closing banner. DEGRADED is not COMPLETE. A deploy that did not
# verify the chain is not a deploy that succeeded.
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
if ($DeployDegraded) {
    Write-Host "    DEPLOYMENT DEGRADED -- one or more steps did not complete successfully" -ForegroundColor Yellow
    Write-Host "    Review $LogFile for details. The chain may not verify." -ForegroundColor Yellow
} else {
    Write-Host "    DEPLOYMENT COMPLETE" -ForegroundColor Green
}
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "Project root:        $ProjectRoot"
Write-Host "Install path:        $InstallPath"
Write-Host "Log file:            $LogFile"
Write-Host "Start server:        $LauncherDir\Start-Server.bat"
Write-Host "Run CLI audit:       $LauncherDir\Run-AuditCli.bat"
Write-Host "Run tests:           $LauncherDir\Verify-Tests.bat"
Write-Host "Verify chain:        $LauncherDir\Verify-Chain.bat"
Write-Host "Build Tauri binary:  $LauncherDir\Build-Tauri-Desktop.bat"
if ($DryRun) {
    Write-Host ""
    Write-Host "DRY-RUN REPORT (JSON; pytest parses this):" -ForegroundColor Yellow
    $json = $DryRunReport | ConvertTo-Json -Compress -Depth 4
    Write-Host $json -ForegroundColor Yellow
}
Write-Host ""

if ($DeployDegraded -and -not $DryRun) {
    exit 2
}
exit 0
