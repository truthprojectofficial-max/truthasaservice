<#
.SYNOPSIS
Order Get It Right -- Build the Tauri desktop binary on Windows.
.DESCRIPTION
This script is intentionally small. It performs only the steps required
to produce a signed-ready Tauri MSI/NSIS bundle on a clean Windows host
that already has Node.js, Rust, and the WebView2 runtime installed.

The Python runtime source is configurable. On a clean host with no
bundled interpreter, the script falls back to the first python.exe on
PATH instead of crashing.
#>

param(
    [string]$PythonSource = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Derive the project root from the script's own location. This keeps the
# script usable when invoked through a launcher that already cd'd into the
# project root, and also when called directly by absolute path.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) {
    $ScriptDir = (Get-Location).Path
}
$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $ScriptDir "..")).Path
$TauriDir = Join-Path $ProjectRoot "02_Technical\tauri-shell"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Order Get It Right -- Tauri build harness" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Project root:  $ProjectRoot"
Write-Host "  Tauri dir:     $TauriDir"
Write-Host "================================================================================" -ForegroundColor Cyan

# 1. Pre-flight: rust, node, webview2
foreach ($tool in @("rustc", "cargo", "node", "npm")) {
    $cmd = Get-Command $tool -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "Required tool not found: $tool. Install Rust + Node.js before running."
    }
}

# 2. Resolve the Python runtime source. Preference order:
#    a) An explicitly provided -PythonSource directory.
#    b) A bundled runtime under 02_Technical\python.
#    c) C:\Python314 (common system-wide install for this project).
#    d) The directory containing the first python.exe on PATH.
function Resolve-PythonSource {
    param([string]$Explicit)

    if ($Explicit) {
        if (Test-Path (Join-Path $Explicit "python.exe")) {
            return $Explicit
        }
        Write-Host "  !! Explicit -PythonSource $Explicit does not contain python.exe; trying defaults" -ForegroundColor DarkYellow
    }

    $bundled = Join-Path $ProjectRoot "02_Technical\python"
    if (Test-Path (Join-Path $bundled "python.exe")) {
        return $bundled
    }

    if (Test-Path "C:\Python314\python.exe") {
        return "C:\Python314"
    }

    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) {
        return Split-Path -Parent $cmd.Source
    }

    return $null
}

$ResolvedPythonSource = Resolve-PythonSource $PythonSource
$ResourceDir = Join-Path $TauriDir "resources"
if (-not $DryRun) {
    New-Item -ItemType Directory -Force -Path $ResourceDir | Out-Null
}

if ($ResolvedPythonSource) {
    Write-Host "[1/3] Bundling Python runtime from $ResolvedPythonSource" -ForegroundColor Yellow
    if ($DryRun) {
        Write-Host "  DRY: would copy $ResolvedPythonSource -> $(Join-Path $ResourceDir "python")" -ForegroundColor DarkYellow
    } else {
        Copy-Item -Path $ResolvedPythonSource -Destination (Join-Path $ResourceDir "python") -Recurse -Force
    }
} else {
    Write-Host "[1/3] No local Python runtime found; bundle will assume the user has Python 3.12+ on PATH" -ForegroundColor DarkYellow
}

# 3. Install npm deps
Write-Host "[2/3] Installing Tauri npm dependencies" -ForegroundColor Yellow
Set-Location $TauriDir
if (-not (Test-Path "node_modules")) {
    if ($DryRun) {
        Write-Host "  DRY: would run npm install in $TauriDir" -ForegroundColor DarkYellow
    } else {
        npm install
    }
}

# 4. Build
Write-Host "[3/3] Running tauri build" -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "  DRY: would run npx tauri build in $TauriDir" -ForegroundColor DarkYellow
} else {
    npx tauri build
}
Set-Location $ProjectRoot
Write-Host "Tauri build complete. Artifacts under $TauriDir\target\release\bundle" -ForegroundColor Green
