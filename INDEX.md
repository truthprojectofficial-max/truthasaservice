# Order Get It Right -- Project Index

> **One-page entry point. Read this first.**
> Last refreshed 2026-07-23. Source of truth: the chain (03_Vault/facts_registry.json, 35,662 blocks, root e66d86d4..., MATCH). This index is the operator-readable layer on top of the chain; the chain drives the canonical numbers.

---

## What this is (60-second read)

**Order Get It Right -- Verified Processor.**
A deterministic business audit and valuation engine written in pure-stdlib Python 3.12+. Takes intake documents (PDFs, emails, contracts) and produces court-grade forensic audit output: affidavits, deception-tell reports, calibration against evaluation cases. Every action is sealed to a Merkle chain; the chain is the tamper-evident witness.

**Operator:** Justin Barnett. **Jurisdiction:** Commonwealth of Australia (ACL + Evidence Act 1995). **Tagline:** "Verified Processor."

**Live state (2026-07-23):**
- Chain: 35,662 blocks, root e66d86d4..., MATCH
- Tests: 272 pass + 1 skip
- Source: 49 .py in 02_Technical/, ontology v3.10 with 55 patterns
- Allow-list: 5 files (closed-set, sealed 2026-07-23)
- Last commit: 9fcae15 (BUILD_DIRECTIVE_SPAWN_AND_SPREAD_OPERATIONAL)

---

## How to read this project (5-minute read)

1. **`00_Strategy/`** -- the WHY. Mission, scope, six non-negotiables, four-gate pipeline, paths A and B.
2. **`01_Methodology/`** -- the WHAT. BBFB (band-for-buck forensic), four-pillar FRUIT formula, deception ontology.
3. **`02_Technical/`** -- the HOW. Pure-stdlib Python engine. Run `python -m src.audit_cli --inbox data/inbox --outbox data/outbox` to process a case.
4. **`03_Vault/`** -- the WITNESS. facts_registry.json is the Merkle chain; every action since 2026-07-12 is sealed here. 47MB, append-only.
5. **`04_Validation/`** -- the PROOF. EVAL cases, calibration reports, the chain's human-readable documentation layer.

---

## The 8 documents you actually need to read

In priority order (each later doc references the earlier ones):

### 1. `README.md` (project root, 5.7KB)
The 60-second project summary. Read this first if you have 0 context.

### 2. `AGENTS.md` (project root, 9.3KB)
The rules every external agent (Claude Code, OpenCode, Codex, onyx) must follow. Includes the seal-test-verify-commit ritual, the 5-allow-list policy, and the canonical 8 non-negotiables.

### 3. `04_Validation/HEAD_TO_TOE_ALIGNMENT_2026-07-23.md` (24KB, refreshed 2026-07-23)
The one-view orientation document. New operator/agent reads this in 10-15 minutes and understands the whole project. Includes the full .py inventory, 32 HTTP endpoints, 41 constants, the 4-gate pipeline diagram, and common tasks.

### 4. `04_Validation/MASTER_TODO_2026-07-23.md` (19.5KB, refreshed 2026-07-23)
The one list of work items. 16 items: 8 closed, 8 open. Tells you "what's been done" and "what's next" in one document.

### 5. `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` (37KB, refreshed 2026-07-23)
The historical record + the live fingerprint (REF-1..REF-6 hashes). The place to look up "what is the current Merkle root?" or "is item X still open?"

### 6. `04_Validation/BUILD_DIRECTIVE_SPAWN_AND_SPREAD_2026-07-23.md` (27.6KB, refreshed 2026-07-23)
The 4-WP parallel spread-work playbook. The execution roadmap for the next 2-3 hours. **OPERATIONAL** as of 2026-07-23 (auth resolved; unified local-Ollama path).

### 7. `04_Validation/AUDIT_NO_NETWORK.md` (11.8KB, refreshed 2026-07-23)
The closed-set network policy. 5 files in the allow-list, all loopback-only. The closed-set test `tests/test_allow_list_closed.py` locks the policy.

### 8. `04_Validation/MAINTENANCE_PLAN.txt` (22.1KB, refreshed 2026-07-23)
The 5-cycle maintenance contract (daily/weekly/monthly/quarterly/annual). Tells you "what to do when" and "what to look for."

---

## How to run the project (commands)

```bash
# Verify the chain
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical"
python -m src.verify_chain                    # must print MATCH

# Run the test suite
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
python -m pytest tests/ -q                     # expected: 272 pass, 1 skip

# Process an audit case
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical"
python -m src.audit_cli --inbox data/inbox --outbox data/outbox

# Confirm canonical tree
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
python 04_Validation/scripts/which_canonical.py

# Refresh the live fingerprint (REF-1..REF-6)
python 04_Validation/scripts/derive_fingerprints.py
```

The full FastAPI server is at `02_Technical/src/server/app.py` (32 endpoints); see `04_Validation/HEAD_TO_TOE_ALIGNMENT_2026-07-23.md` for the endpoint inventory.

---

## How to start a new session (operator ritual)

```bash
# 1. Read the project state (3 docs, 5 minutes)
cat 04_Validation/MASTER_TODO_2026-07-23.md          # what's open
cat 04_Validation/BUILD_DIRECTIVE_SPAWN_AND_SPREAD_2026-07-23.md  # what's planned
cat 04_Validation/HEAD_TO_TOE_ALIGNMENT_2026-07-23.md  # the project map

# 2. Verify the chain (10 seconds)
cd 02_Technical
python -m src.verify_chain
cd ..

# 3. Run the targeted tests (15 seconds)
python -m pytest tests/test_tagline_rebrand.py tests/test_allow_list_closed.py tests/test_audit_no_network.py tests/test_which_canonical.py -q

# 4. If any of the above fails, STOP. Do not add features to a broken build.
#    Seal a BUILD_BASELINE_BROKEN_2026_07_XX block and end the session.
```

If all 4 pass, you are operational. Continue with the work in the current MASTER_TODO.

---

## How to seal a change (the audit ritual)

```python
# The seal-test-verify-commit ritual
# 1. Make the change
# 2. Run the targeted tests
python -m pytest tests/test_allow_list_closed.py tests/test_audit_no_network.py -q
# 3. Verify the chain
cd 02_Technical && python -m src.verify_chain && cd ..
# 4. Seal the change
python -c "
import sys; sys.path.insert(0, '02_Technical')
from src.io.vault_io import append_block
from datetime import datetime, timezone
block = append_block('YOUR_EVENT_TYPE_2026_07_XX', {'details': '...'})
print(f'Sealed block {block[\"index\"]}, hash {block.get(\"hash\", \"\")[:16]}...')
"
# 5. Commit (commit message MUST reference the block index)
git add -A
git commit -m "YOUR_EVENT_TYPE_2026_07_XX: ... (chain block NNNNN)"
git push usb
# 6. Verify the chain again
cd 02_Technical && python -m src.verify_chain
```

The commit message is the human-readable summary; the chain block is the tamper-evident witness. Both are required; neither alone is sufficient.

---

## The 8 non-negotiables (from AGENTS.md)

1. **Order Get It Right**: deterministic, sealed, audit-driven. No untracked changes.
2. **Seal every action**: every state change produces a `facts_registry.json` block.
3. **Merkle root is sacred**: `e66d86d4...` is the live root; if it changes without a seal, that's a tamper event.
4. **Canonical tree is one**: `OrderGetItRight/` at `C:\Users\justo\OneDrive\Documents\My Project\`. No branches, no copies, no symlinks.
5. **5-allow-list is closed**: only 5 files may use network modules. Adding a 6th requires `ALLOW_LIST_AMENDED_2026_07_XX` event.
6. **Pure stdlib Python 3.12+**: no pip dependencies in 02_Technical/src/. The chain and the engine are stdlib-only.
7. **Commonwealth of Australia jurisdiction**: ACL + Evidence Act 1995 (NSW) + Privacy Act 1988. The audit is court-grade.
8. **Operator is Justin Barnett**: every seal block records the operator; no anonymous changes.

---

## Where to look for what (quick reference)

| If you want to know... | Read this |
|------------------------|-----------|
| What this project is (60 sec) | `README.md` |
| The rules every agent must follow | `AGENTS.md` |
| One-view project map (15 min) | `04_Validation/HEAD_TO_TOE_ALIGNMENT_2026-07-23.md` |
| What's open / what's next | `04_Validation/MASTER_TODO_2026-07-23.md` |
| The current Merkle root + REFs | `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` |
| The 4-WP execution roadmap | `04_Validation/BUILD_DIRECTIVE_SPAWN_AND_SPREAD_2026-07-23.md` |
| The network allow-list policy | `04_Validation/AUDIT_NO_NETWORK.md` |
| The maintenance cycles | `04_Validation/MAINTENANCE_PLAN.txt` |
| The chain witness (machine) | `03_Vault/facts_registry.json` (47MB, 35,662 blocks) |
| Git history (94 commits) | `git log --oneline` |
| The 5-stage paper backup plan | `04_Validation/STAGE_PAPER_*.txt` |
| Operator's everyday comms context | `04_Validation/COMMS_OPTIONS_WHYALLA_2026-07-22.md` |
| What to do if the build breaks | `04_Validation/TROUBLESHOOTING.md` |
| The full 32-endpoint API | `04_Validation/HEAD_TO_TOE_ALIGNMENT_2026-07-23.md` section "HTTP endpoints" |
| The 41 constants | `04_Validation/HEAD_TO_TOE_ALIGNMENT_2026-07-23.md` section "Constants" |
| The chain's known artefacts | `04_Validation/KNOWN_CHAIN_ARTEFACTS.md` |
| The handover to the next session | `04_Validation/handover_next_session_2026-07-22.md` (stale; refresh next session) |
| The 5-cycle audit / ont / eval pipeline | `01_Methodology/` |
| Why this is the design (mission) | `00_Strategy/` |

---

## What this project is NOT

- Not a cloud service. The runtime is fully local; no remote APIs are used at runtime.
- Not a multi-tenant system. One operator, one machine, one canonical tree.
- Not a Python package. The `02_Technical/src/` is a flat module tree, not a pip installable.
- Not a research project. The ontology, methodology, and audit rules are all sealed and locked.
- Not a work-in-progress. The chain has 35,662 blocks; every state change since 2026-07-12 is recorded.

---

## Versioning and refresh notes

- This index: 2026-07-23 (v1.0, created by Hermes; addresses 4 of the 5 recurring patterns this session).
- Prior pattern: the discoverability question ("where has all that information gone") was asked three times in 2026-07-23 alone. The previous answer was "read the 5 docs + the chain + git log" -- 6+ items to check. This INDEX.md reduces that to 1.
- Refresh cadence: when the next 5-doc consolidation happens, append a "Refreshed YYYY-MM-DD" line. Do not delete the prior content; it is the audit trail.

---

## One-line identity (preserved verbatim)

```
Order Get It Right -- Verified Processor.
A deterministic business audit engine written in pure-stdlib Python 3.12+.
Chain: 35,662 blocks, root e66d86d4..., 272 tests, MATCH.
Operator: Justin Barnett. Jurisdiction: Commonwealth of Australia.
Ontology: 3.10, 55 patterns, R1-R6. Tagline: "Verified Processor".
```
