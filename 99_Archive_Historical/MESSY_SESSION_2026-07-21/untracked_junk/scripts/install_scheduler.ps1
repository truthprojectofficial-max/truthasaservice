<#
.SYNOPSIS
    Installs the Order Get It Right deterministic maintenance scheduler
    as two Windows Task Scheduler tasks: one hourly, one daily.

.DESCRIPTION
    Creates (or replaces) two scheduled tasks:

      OGIR-Maintenance-Hourly
          fires every hour, runs the HOURLY cadence (~0.3 s, no seal).
      OGIR-Maintenance-Daily
          fires daily at 03:00 local, runs the DAILY cadence
          (~10 s post Option B, seals one block).

    Both tasks run whether the user is logged on or not, hidden, with the
    working directory set to 02_Technical so `python -m src.maintenance.*`
    resolves. They run as the CURRENT user (so the vault on OneDrive is
    writable). Exit code 0 == PASS/WARN, 1 == FAIL (Task Scheduler will
    record the failure but does NOT auto-alert; check the report files
    under 04_Validation\maintenance_reports\).

    Deterministic. No LLM. No network. The only writes per run are:
      - one sealed maintenance block to the chain (DAILY only, unless
        --no-seal is passed), and
      - report files under 04_Validation\maintenance_reports\.

.PARAMETER PythonExe
    Path to the Python interpreter. Defaults to `python` on PATH.

.PARAMETER NoSeal
    Pass this to install the DAILY task with --no-seal (run routines and
    write the report, but do NOT seal a block to the chain). Useful for a
    read-only / observation install.

.PARAMETER DailyTime
    The daily fire time as HH:mm (24h). Default 03:00.

.PARAMETER Uninstall
    Remove the two tasks instead of creating them.

.EXAMPLE
    .\install_scheduler.ps1
    .\install_scheduler.ps1 -DailyTime 02:30
    .\install_scheduler.ps1 -NoSeal
    .\install_scheduler.ps1 -Uninstall

.NOTES
    Operator of record: Justin Barnett. Project: Order Get It Right v1.0.0.
#>
[CmdletBinding()]
param(
    [string]$PythonExe = "python",
    [string]$DailyTime  = "03:00",
    [switch]$NoSeal,
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

# --- locate the project root (two levels up from this script) -----------
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$TechDir     = Join-Path $ProjectRoot "02_Technical"

if (-not (Test-Path (Join-Path $TechDir "src\maintenance\scheduler.py"))) {
    throw "Could not find 02_Technical\src\maintenance\scheduler.py under $ProjectRoot. Run this script from <project>\scripts\."
}

$HourlyTask = "OGIR-Maintenance-Hourly"
$DailyTask  = "OGIR-Maintenance-Daily"

if ($Uninstall) {
    foreach ($t in @($HourlyTask, $DailyTask)) {
        try {
            Unregister-ScheduledTask -TaskName $t -Confirm:$false -ErrorAction Stop
            Write-Host "[uninstall] removed $t"
        } catch {
            Write-Host "[uninstall] $t not present (nothing to do)"
        }
    }
    return
}

# --- resolve the python interpreter to an absolute path -----------------
$py = if ($PythonExe -eq "python") {
    (Get-Command python -ErrorAction Stop).Source
} else {
    (Resolve-Path $PythonExe -ErrorAction Stop).Path
}
Write-Host "[install] python  : $py"
Write-Host "[install] tech dir: $TechDir"
Write-Host "[install] daily at: $DailyTime"

# --- build the action arguments -----------------------------------------
$hourlyArgs = '-m src.maintenance.scheduler --once --cadence hourly --no-seal'
$dailyArgs  = '-m src.maintenance.scheduler --once --cadence daily'
if ($NoSeal) { $dailyArgs += ' --no-seal' }

function New-OGIR-Task($Name, $Args, $Trigger) {
    $action    = New-ScheduledTaskAction  -Execute $py -Argument $Args -WorkingDirectory $TechDir
    $settings  = New-ScheduledTaskSettingsSet `
                    -StartWhenAvailable `
                    -DontStopOnIdleEnd `
                    -AllowStartIfOnBatteries `
                    -DontStopIfGoingOnBatteries `
                    -RestartCount 2 -RestartInterval (New-TimeSpan -Minutes 5)
    $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
                    -LogonType Interactive -RunLevel Limited
    Register-ScheduledTask -TaskName $Name -Action $action -Trigger $Trigger `
        -Settings $settings -Principal $principal -Force | Out-Null
    Write-Host "[install] registered $Name"
}

# Hourly: every hour, all day, indefinitely
$hourlyTrig = New-ScheduledTaskTrigger -Once -At ((Get-Date).Date.AddHours(1)) `
    -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 3650)

# Daily: at the chosen time, indefinitely
$h, $m = $DailyTime.Split(':')
$dailyTrig = New-ScheduledTaskTrigger -Daily -At ((Get-Date).Date.AddHours([int]$h).AddMinutes([int]$m))

New-OGIR-Task $HourlyTask $hourlyArgs $hourlyTrig
New-OGIR-Task $DailyTask  $dailyArgs  $dailyTrig

Write-Host ""
Write-Host "[install] DONE."
Write-Host "  Hourly task runs every hour (no seal).       ~0.3 s"
Write-Host "  Daily  task runs at $DailyTime (seals a block). ~10 s"
Write-Host ""
Write-Host "Check status:    Get-ScheduledTask -TaskName OGIR-Maintenance-*"
Write-Host "Run now:         Start-ScheduledTask -TaskName OGIR-Maintenance-Hourly"
Write-Host "See reports:     $ProjectRoot\04_Validation\maintenance_reports\"
Write-Host "Uninstall:        .\install_scheduler.ps1 -Uninstall"