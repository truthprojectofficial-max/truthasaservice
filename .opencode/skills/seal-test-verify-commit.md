---
description: "Use when changing any source file. The mandatory ritual: edit, run tests (must stay green), verify chain (must MATCH), seal a chain block, then git commit (subject = event_type). Seal first, commit second. One seal, one commit."
---

# Seal-Test-Verify-Commit Skill

Every code change goes through this ritual, in this order. No exceptions.

## The ritual (6 steps)

1. **Edit** the source file(s).
2. **Run tests**: `python -m pytest tests/ -q --no-header`
   - MUST be 400+ passed, 0 failed. If tests fail, FIX before proceeding.
3. **Verify the chain**: `$env:PYTHONPATH="02_Technical"; python -m src.verify_chain`
   - MUST print `RESULT: MATCH -- chain is intact.` If BROKEN, stop and
   see the `chain-recovery` skill.
4. **Seal** a chain block:
   ```python
   from src.io.vault_io import append_block
   append_block("EVENT_TYPE_2026_07_XX", { ...payload... })
   ```
   - `event_type` is `SCREAMING_SNAKE_CASE`, ends with the date.
   - Payload records what changed, why, file:line refs, test result.
5. **Commit**: `git add -A && git commit -m "EVENT_TYPE: block NNNNN sealed. <one-line>"`
   - The commit subject IS the chain event_type.
   - One seal = one commit. Do not batch multiple seals into one commit.
6. **Verify again**: `$env:PYTHONPATH="02_Technical"; python -m src.verify_chain`
   - MUST still MATCH after the commit.

## When to seal vs when to commit

| Change type | Chain block | Git commit |
|-------------|-------------|------------|
| Code change (source edit) | YES | YES (subject = event_type) |
| Observation / incident / changelog entry | YES | NO (empty diff, no commit) |
| Merge to main | NO (git-only) | YES, but follow with a `BRANCH_MERGED_<workstream>_<date>` block listing the commit range |

## The mistakes table (do NOT do these)

| Mistake | Why it fails |
|---------|-------------|
| Commit without sealing | The chain is the trust anchor. A commit without a seal is an unwitnessed change. |
| Seal without a source change, then commit | Produces an empty diff commit. Seals are for state changes, not air. |
| Seal after commit | The seal must witness the change BEFORE git records it. Seal first. |
| Multiple seals, one commit | One seal = one commit. Batching loses granularity. |
| Chain and git disagree | The chain wins. If the chain says BROKEN, restore the vault, not the code. |

## The rule

A code change produces BOTH a chain block AND a git commit. The chain is
the trust anchor (the audit-side witness of every state change). Git is
the code management layer (the source-side witness). They are not
interchangeable. The chain is the source of truth for *what the engine
decided*; Git is the source of truth for *what the operator committed*.
If they ever disagree, the chain wins.