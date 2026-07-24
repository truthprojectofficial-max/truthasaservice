# Repo Move Runbook — OneDrive to C:\OrderGetItRight

> Created 2026-07-24. Do this when you have 1 hour and can verify after.
> The vault in OneDrive is a corruption risk (already happened once).

## Why

The live repo + 19MB Merkle chain is in a OneDrive-synced folder.
OneDrive can and will:
- Lock the file during a seal write → `append_block` fails
- Upload partial writes → corrupt the chain
- Trigger re-downloads that clobber local changes
- Hold upload conflicts

This already happened once (SESSION_LOG_2026-07-24.md section 1A).
Moving the repo out of OneDrive is the permanent fix.

## Current location
```
C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\
```

## Target location
```
C:\OrderGetItRight\
```
(Plain C: drive. Not OneDrive-synced. Not a junction to D:.)

## Prerequisites
- C: has 1689 GB free (plenty)
- The D: junctions at C:\OrderGetItRight and C:\TestJunctionOGIR
  point to D:\OrderGetItRight — these need to be removed first

## Step-by-step

### 1. Remove the existing junction (5 min)
```powershell
# Check what's there
dir C:\OrderGetItRight

# It's a junction to D:\OrderGetItRight. Remove the junction (NOT the D: data):
rmdir C:\OrderGetItRight
rmdir C:\TestJunctionOGIR

# Verify they're gone
Test-Path C:\OrderGetItRight  # should be False
```

### 2. Copy the repo (10 min)
```powershell
robocopy "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight" "C:\OrderGetItRight" /E /COPYALL /R:0 /W:0 /XD ".git" 

# Copy .git separately (robocopy can struggle with .git internals)
robocopy "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\.git" "C:\OrderGetItRight\.git" /E /R:0 /W:0
```

### 3. Verify the copy (10 min)
```powershell
cd C:\OrderGetItRight

# Chain must be MATCH
$env:PYTHONPATH="02_Technical"
python -m src.verify_chain
# Expected: RESULT: MATCH -- chain is intact.

# Tests must pass
python -m pytest tests/ -q
# Expected: 400 passed, 4 skipped

# Block count must match
python -m src.verify_chain | Select-String "Block count"
# Expected: same as the OneDrive copy
```

### 4. Update git remote paths (if needed)
```powershell
cd C:\OrderGetItRight
git remote -v
# origin should still point to GitHub (URL-based, no change needed)
# usb should still point to /d/OrderGetItRight.git (no change needed)
```

### 5. Exclude the old path from OneDrive sync (5 min)
- Open OneDrive settings → Choose folders
- Uncheck "My Project" (or the OrderGetItRight subfolder)
- This stops OneDrive from syncing the old copy

### 6. Keep the old copy for 1 week (safety)
- Don't delete the OneDrive copy yet
- Use C:\OrderGetItRight as the active repo
- After 1 week of clean operation, delete the OneDrive copy

### 7. Update any scripts/shortcuts that reference the old path
Check:
- `launchers/*.bat` — may hardcode the OneDrive path
- `AGENTS.md` — references the path in the run commands
- `INDEX.md` — references the path
- Hermes config — may reference the path
- VS Code workspace settings — may reference the path

### 8. Update PYTHONPATH (if set as a system env var)
```powershell
# Check if PYTHONPATH is set system-wide
[System.Environment]::GetEnvironmentVariable("PYTHONPATH", "User")

# If it references the OneDrive path, update it:
[System.Environment]::SetEnvironmentVariable("PYTHONPATH", "C:\OrderGetItRight\02_Technical", "User")
```

### 9. Verify the temp-vault test fixture still works
```powershell
cd C:\OrderGetItRight
python -m pytest tests/ -q
# The conftest.py fixture uses a tmp_path, so it works regardless of repo location
```

## What NOT to do

- Don't `git mv` — this is a filesystem move, not a git operation
- Don't delete the OneDrive copy until the new location is verified for 1 week
- Don't move during a test run or chain seal
- Don't leave both copies active — pick one and use it

## After the move

- All `python -m` commands run from `C:\OrderGetItRight`
- The vault at `C:\OrderGetItRight\03_Vault\` is local-only (no sync)
- The D: junctions are gone (no confusion about which copy is live)
- OneDrive no longer touches the chain