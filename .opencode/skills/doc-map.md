---
description: "Use when searching for a file or navigating the project. The 04_Validation/ folder has 10 named subfolders. 5-file orientation order: CONTEXT_WINDOW, STRATEGY, GOVERNANCE, MAINTENANCE_PLAN, IP_RIGHTS. Always run pytest from project root, not 02_Technical/tests/."
---

# Doc Map Skill

The `04_Validation/` folder was 117 flat files; now sorted into 10
named folders. Use this map instead of searching blindly.

## The folder map

| Folder | What's in it |
|--------|-------------|
| `handovers/` | `HANDOVER_LOG.md` — the agent sign-off log (read at session start) |
| `session_logs/` | Per-session logs (`SESSION_LOG_2026-07-24.md`, `WHY_THIS_FAILED.md`, etc.) |
| `build_directives/` | `MASTER_TICK_LIST_2026-07-24.md` — the operator action list |
| `go_to_market/` | GTM plan, business model, promotional dressing, business handling flow |
| `legal_privacy/` | Privacy policy, NDB response plan, legal handling, engagement letter, CLA |
| `runbooks/` | Setup guides, Supabase, Hermes, repo-move, conversation-layer-down, startup |
| `methodology_calibration/` | Harvesting policy, AI dialects, responsibility split, interaction analysis, calibration rerun |
| `architecture_assessment/` | Project state, process playbook, accreditation brief, gem-doc reconciliation |
| `paper_backup/` | Hard-copy backup plan, Merkle root card |
| `reference_misc/` | Context window, troubleshooting, git workflow, changelog, repo skeleton, agent signoff policy, maintenance plan |

(Plus pre-existing: `hardcopy/`, `logs/`, `pre_2021_intake/`, `reports/`,
`scripts/`, `squeal-reports/`, `operator_completions/`.)

## The 5-file orientation order

If you need to orient in the project, read in this order:
1. `04_Validation/reference_misc/CONTEXT_WINDOW.md`
2. `00_Strategy/STRATEGY.md`
3. `00_Strategy/GOVERNANCE.md`
4. `04_Validation/reference_misc/MAINTENANCE_PLAN.txt`
5. `04_Validation/reference_misc/IP_RIGHTS.md`

## Top-level structure

```
00_Strategy/        axioms, mission, non-negotiables
01_Methodology/     human-readable math (DECEPTION_ONTOLOGY, MATHEMATICS, REAL_OPTIONS_LATTICE)
02_Technical/       THE PROGRAM (config/, src/, tools/, tauri-shell/, web/)
03_Vault/           the live Merkle chain (facts_registry.json)
04_Validation/      logs, docs, scripts (10 named folders)
99_Archive/         frozen snapshots
data/               inbox (samples) + outbox (audit output)
deploy/             deploy.ps1 + build-tauri.ps1
launchers/          4 .bat files
tests/              12+ test files
```

## Where things live (common lookups)

| Looking for | Path |
|-------------|------|
| Handover log | `04_Validation/handovers/HANDOVER_LOG.md` |
| Operator todo | `04_Validation/operator_completions/OPERATOR_TODO_<date>.md` |
| Master tick list | `04_Validation/build_directives/MASTER_TICK_LIST_2026-07-24.md` |
| Constants | `02_Technical/config/constants.py` |
| Vault I/O | `02_Technical/src/io/vault_io.py` |
| Canonical JSON | `02_Technical/src/utils/canonical.py` |
| Deception ontology | `01_Methodology/DECEPTION_ONTOLOGY.md` |
| Lattice methodology | `01_Methodology/REAL_OPTIONS_LATTICE.md` |
| Chain verify | `02_Technical/src/verify_chain.py` |
| Tests | `tests/` (run from project root, NOT `02_Technical/tests/`) |
| Changelog | `04_Validation/reference_misc/changelog.log` |

## The INDEX.md MUST DO

`INDEX.md` at the project root has a "MUST DO" section at the top
that flags critical unaddressed items (e.g. leaked keys to revoke).
Read it at session start. The `priority-check` skill covers the
operator todo; this is the project-level critical-items check.

## The rule

Don't steam off and search files blindly. Use the map. The folder
reorg fixed 13 path references in tests/scripts/hooks when it happened
— if a path is wrong, check the folder map first. Run pytest from the
project root, not from `02_Technical/tests/` (that's a stale mirror,
hard-deleted at A10).