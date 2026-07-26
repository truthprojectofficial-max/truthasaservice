---
description: "Use when python -m src.verify_chain prints BROKEN or a JSONDecodeError. STOP immediately. Do not run audits, do not write code. Restore the vault from git HEAD, re-verify, seal a recovery block. The vault is the trust anchor — corrupted vault invalidates every trust claim."
---

# Chain Recovery Skill

When `python -m src.verify_chain` prints anything other than
`RESULT: MATCH -- chain is intact.`, STOP. The trust anchor is broken.

## Step 1: STOP

Do not run audits. Do not write code. Do not seal blocks. Do not
commit. The chain is the trust anchor — if it is broken, every sealed
decision is in question until it is restored.

## Step 2: Restore from git HEAD

```powershell
git checkout HEAD -- 03_Vault/facts_registry.json 03_Vault/job_registry.json
```

This restores the vault to the last committed state. Git is the
code-side witness; the last commit's vault is the known-good state.

If git HEAD is also corrupt (unlikely, but possible if OneDrive
synced garbage into the commit), restore from the USB mirror:
```powershell
git checkout usb/ogir-build-2026-07-18 -- 03_Vault/facts_registry.json 03_Vault/job_registry.json
```

If the USB mirror is also corrupt, restore from the paper card:
the Merkle root on the paper card in `04_Validation/hardcopy/` is the
last-resort recovery anchor. Contact the operator.

## Step 3: Re-verify

```powershell
$env:PYTHONPATH="02_Technical"; python -m src.verify_chain
```

MUST print `RESULT: MATCH -- chain is intact.` If it still says
BROKEN, the corruption is deeper. STOP and report to the operator.

## Step 4: Seal a recovery block

```python
from src.io.vault_io import append_block
append_block("CHAIN_BROKEN_RECOVERY_<date>", {
    "broken_at_block": <N>,
    "root_broken": "<hash>",
    "root_restored": "<hash>",
    "recovery_source": "git HEAD" | "USB mirror" | "paper card",
    "tests_after_recovery": "<passed N / failed N>",
})
```

## Step 5: Run the tests

```powershell
python -m pytest tests/ -q --no-header
```

MUST be 400+ passed, 0 failed. If tests fail after recovery, the
corruption affected source too. STOP and report.

## Known corruption vector: OneDrive sync

The repo lives in an OneDrive-synced folder. OneDrive has already
corrupted the vault once (2026-07-24: trailing garbage appended to
`facts_registry.json`). The fix is to move the repo to
`C:\OrderGetItRight` (runbook at
`04_Validation/runbooks/REPO_MOVE_RUNBOOK_2026-07-24.md`). Until the
move is done, this skill is the recovery path.

## The rule

A broken chain is a stop-the-world event. Nothing else matters until
the trust anchor is restored and re-verified. No audits, no code, no
commits, no seals — until `verify_chain` says MATCH.