---
name: handover-next-session-2026-07-16
description: Handover from the 2026-07-16 session to the next operator or AI session.
metadata:
  type: project
  originSessionId: 9c4425d6-35b6-4a10-b34c-b8bd31829254
---

================================================================================
ORDER GET IT RIGHT -- HANDOVER TO NEXT SESSION
Generated: 2026-07-16  (UTC)
Refreshed: 2026-07-17  (UTC, after INTRO_AND_TROUBLESHOOTING_DOCS_ADDED
seal; subsequent-closures section appended -- do NOT edit the historical
sections below, they are correct as the 2026-07-16 outgoing handover)
Author:    codex-on-Justo  (operator: Justin Barnett)
================================================================================

This file is the first thing the next operator or AI session should read.
It contains the live state, what was done this session, what is still open,
and the exact commands needed to re-establish ground truth.

================================================================================
0. SUBSEQUENT CLOSURES (read this first; the rest of the file is a 2026-07-16
   transcript that is no longer the current state)
================================================================================

The body of this document was written on 2026-07-16 and is a historical
record of THAT session. The test counts, the default model name, and
the "what is still open" list below were all correct on 2026-07-16. They
are not the live state as of 2026-07-17. This section is the live state.

LIVE TEST COUNT (2026-07-17):
  86 passed, 1 skipped, 0 failed   (not 71/1 as in Section 2 below)

LIVE DEFAULT MODEL (2026-07-17):
  qwen3.5:9b   (not tcoxav/aegis:latest as in Section 2 below;
  the swap was sealed in OLLAMA_MODEL_SWAP_QWEN3_5_9B_2026_07_17)

LIVE MERKLE ROOT (2026-07-17, last block 6966):
  21fe18a153877619689322eeaa2f87b998cb9975022e08d3fbbb446f34c70041
  (not 1dfadc3f... as in Section 2 below; the canonical live root
  snapshot is in 04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt)

ITEMS FROM SECTION 4 ("WHAT IS STILL OPEN") THAT HAVE CLOSED SINCE
2026-07-16 (full closure ledger in
04_Validation/OPEN_ITEMS_AND_REFERENCE.md Part 1):

  A3. _seed_facts_once() reset foot-gun            -> CLOSED
       (C2_C3_C4_DOCS_RECONCILED_2026_07_17 seal)
  C2. IP file audit                                 -> CLOSED
       (C2_C3_C4_DOCS_RECONCILED_2026_07_17 seal; 9 -> 10 packages)
  C3. MAINTENANCE_PLAN reconcile                   -> CLOSED
       (C2_C3_C4_DOCS_RECONCILED_2026_07_17 seal)
  C4. New agents in IP file                        -> CLOSED
       (C2_C3_C4_DOCS_RECONCILED_2026_07_17 seal; 10 named modules)
  D2. Full-tree no-network audit                   -> CLOSED
       (D2_NO_NETWORK_AUDIT_FULL_TREE_2026_07_17 seal; 4-test regression)
  D3. Full project-level black-box audit           -> PARTIAL
       (D3_BLACK_BOX_AUDIT_2026_07_17 seal; 14 pillars covered
       by 04_Validation/AUDIT_NO_BLACK_BOX.md)

NEW ITEMS CLOSED IN 2026-07-17 NOT IN THE ORIGINAL SECTION 4:

  A7. STATIC_DIR path bug in src/server/app.py    -> CLOSED
       (UI_OPERATOR_FACING_REDESIGN_2026_07_17 seal; regression
       test tests/test_static_dir.py with 4 tests, all boundary-
       compliant)
  A8. UI does not "speak for itself"              -> CLOSED
       (UI_OPERATOR_FACING_REDESIGN_2026_07_17 seal; 10-tab layout
       rewritten to a 58.7 KB single-page operating surface)
  A9. Tauri desktop binary stale (2026-07-12)     -> CLOSED
       (TAURI_REBUILT_FOR_UI_REDESIGN_2026_07_17 seal; exe + MSI +
       NSIS rebuilt, all three mirrored to USB)
  A10. Stale 02_Technical/tests/ mirror           -> CLOSED
       (PowerShell Remove-Item; REF-3 52 -> 50 .py, REF-4 220 -> 218
       files, no separate seal)

ITEMS STILL OPEN AS OF 2026-07-17 (carried forward from Section 4):

  C5. STRATEGY.md Section 7 tone-of-done pass      -> OPEN
  D1-TRUE. Real clean-host restore on a second PC  -> OPEN
       (operator work; D1 is "closed to extent verifiable on this
        host" -- the single-machine boundary is documented)
  E1. Gmail .mbox import                           -> OPEN
       (operator-supplied input)
  E4. Pre-2020 reference corpus                    -> OPEN
       (E4_PRE_2021_REFERENCE_CALIBRATION sealed the pre-2021
        calibration on 2026-07-17; the pre-2020 corpus (E4 in the
        2026-07-16 nomenclature) is a separate ask -- the operator
        has supplied neither; the pre-2021 corpus was already on
        disk at data/samples/verified_prior_2021.txt)

FOR THE LIVE STATE AND THE LIVE OPEN-ITEMS LIST, READ IN THIS ORDER:
  1. 04_Validation/INTRODUCTION.md (added 2026-07-17; 5-min first run)
  2. 04_Validation/TROUBLESHOOTING.md (added 2026-07-17; failure catalog)
  3. 04_Validation/YELLOW_RIBBON.md (current root in WHERE EVERYTHING IS)
  4. 04_Validation/OPEN_ITEMS_AND_REFERENCE.md Part 1 (live open items)
  5. 04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt (live root snapshot)
  6. This file (the 2026-07-16 historical transcript, beginning below)
  7. 04_Validation/CONTEXT_WINDOW.md (long-form digest, also 2026-07-16)

The remainder of this document is the original 2026-07-16 outgoing
handover. It is correct as a record of that session. Do not treat
it as a current-state document.

================================================================================
0.5. EVENING SESSION 2026-07-17  (added by the docs-reconciliation session)
================================================================================

This section captures what happened in the evening session of 2026-07-17,
sealed as HANDOVER_2026_07_17_EVENING_DOCS_RECONCILIATION. The session
was docs-only; no source code changed. The 86/1 test baseline held the
entire time. The 32-endpoint surface and 10 named modules are unchanged.

WHAT THIS SESSION DID:
  (a) Fixed six present-tense stale references in the three print-and-pin
      hardcopy files (OPERATOR_MANUAL.txt, HARD_COPY_BACKUP_PLAN_1-2-3.txt,
      YELLOW_RIBBON.md operator-ritual command). Sealed
      HARDCOPY_DOC_CORRECTIONS_2026_07_17 at block 6965.
  (b) Created the two missing operator-facing docs: 04_Validation/INTRODUCTION.md
      (287 lines, the 5-minute first-run) and 04_Validation/TROUBLESHOOTING.md
      (928 lines, the failure-mode catalog). Sealed
      INTRO_AND_TROUBLESHOOTING_DOCS_ADDED_2026_07_17 at block 6966;
      REF-4 advanced 218 -> 220 files.
  (c) Flipped A3, C2, C3, C4 from [ ] OPEN to [x] CLOSED in
      04_Validation/TODO_FULL.md (all four were actually closed by the
      C2_C3_C4_DOCS_RECONCILED_2026_07_17 seal earlier in the day; the
      doc still showed them as [ ]). Updated the SUMMARY section to the
      live 86/1 baseline. Sealed TODO_FULL_RECONCILED_2026_07_17 at
      block 7061.
  (d) Added a "0. SUBSEQUENT CLOSURES" header to this file (the
      2026-07-16 transcript is a historical record; the present-tense
      claims in it were correct AT THAT TIME and are preserved verbatim).
  (e) Did an honest inventory of operator-supplied input status. The
      operator's Verified.docx at C:\Users\justo\OneDrive\Documents\My
      Project\Verified.docx is the source for the already-completed
      E4 pre-2021 calibration (data/samples/verified_prior_2021.txt,
      04_Validation/PRE_2021_REFERENCE_CALIBRATION_2026-07-17.md). E4
      pre-2020 is a separate ask and remains open. No .mbox file is on
      disk for E1; the to the spoils go\inbox\ subdirectory does not
      exist; E1 remains open.

LIVE STATE AT HANDOVER SEAL (2026-07-17 evening):
  Tests:                86 passed, 1 skipped, 0 failed
  Chain root:           0fe4872733fb402bbe8dc14e6543a702f901118e6130549304de156bf48ac7c7
  Block count:          7156
  REF-1:                7654ddf6... (unchanged)
  REF-2a:               e4b2ff19... (unchanged)
  REF-2b:               0c2335de... (unchanged)
  REF-3:                7962bf61... (50 .py files, unchanged)
  REF-4:                b85f4cb7... (220 files; path-list rotated between seals)
  REF-5:                0fe48727... (chain above)
  REF-6:                ec72d1f2... (composite of REF-1..REF-5)
  USB:                  D:\OrderGetItRight\ mirrored; chain MATCH at 7156

STILL OPEN AT HANDOVER (for the next session):
  C5.   STRATEGY.md Section 7 tone-of-done pass (genuinely open;
        lowest-priority remaining doc fix)
  D1-true-clean-host.  Real clean-host restore on a second Windows PC
        with no Python installed. Operator work.
  E1.   Gmail .mbox into OneDrive\Documents\to the spoils go\inbox\.
        Operator work; not done. No .mbox file on disk.
  E4.   Pre-2020 reference corpus into OneDrive\Documents\to the
        spoils go\pre_2020_corpus\. Operator work; not done.
        Note: the operator's Verified.docx is the source for the
        already-completed E4 pre-2021 calibration -- a different
        corpus.

FIRST ACTIONS FOR THE NEXT SESSION:
  1. cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical"
     python -m src.verify_chain
     -> expect RESULT: MATCH; root should start 0fe48727...
  2. cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
     python -m pytest tests/ -q
     -> expect 86 passed, 1 skipped
  3. If either fails, STOP and read 04_Validation/TROUBLESHOOTING.md
     (failure-mode catalog) before changing anything.
  4. If both pass, read 04_Validation/INTRODUCTION.md for the
     5-minute first-run orientation.

================================================================================
1. PROJECT IDENTITY (one paragraph)
================================================================================

Order Get It Right -- Truth as a Service. A deterministic business audit and
valuation program. Version 1.0.0. Operator: Justin Barnett. Jurisdiction:
Commonwealth of Australia / ACL / Evidence Act 1995. Canonical source lives at
C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight. USB/SDXC backup
at D:\OrderGetItRight (also reachable via C:\OrderGetItRight junction). No
network in the audit loop. No LLM in the audit loop. Every decision sealed to
a Merkle chain at 03_Vault\facts_registry.json.

================================================================================
2. LIVE STATE (re-derive these numbers before doing anything)
================================================================================

Canonical source:
  cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical"
  python -m src.verify_chain
  cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
  python -m pytest tests/ -q

USB/SDXC backup:
  cd "D:\OrderGetItRight\02_Technical"
  python -m src.verify_chain
  cd "D:\OrderGetItRight"
  python -m pytest tests/ -q

Expected results:
  verify_chain  -> RESULT: MATCH
  pytest        -> 71 passed, 1 skipped, 0 failed
  audit_cli     -> 5/5 success
  The single skip is the Ollama tool-calling end-to-end test, which requires
  a tool-capable Ollama model. The model list on this host currently shows:
    qwen3.5:9b
    Qwen2.5-coder:latest
  The default hard-coded model is `tcoxav/aegis:latest`. If you want the
  D5 test to pass, either (a) pull aegis with `ollama pull tcoxav/aegis`, or
  (b) confirm one of the installed models supports Ollama tool_calls and
  update `DEFAULT_MODEL` in `02_Technical/tools/agentic_repl.py` and the
  `OGIR_AGENT_MODEL` env var in `tests/test_d5_agentic_repl.py`.

================================================================================
3. WHAT THIS SESSION DID (2026-07-16)
================================================================================

(a) Resolved the project fork. The OneDrive copy
    (C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight) is now
    canonical. The older .claude copy was frozen as a snapshot.

(b) Fixed remaining runtime bugs:
    - `PROJECT_ROOT` in `config/constants.py` now resolves to the project root
      (was pointing at `02_Technical`).
    - `src/config.py` imports `PROJECT_CHANGELOG_DIR`.
    - `src/server/app.py` `_read_changelog()` returns `[]` on missing file.
    - `Orchestrator.shutdown()` uses `vault_io.append_block()` correctly.
    - `src/server/__init__.py` exports `app` for `uvicorn src.server:app`.
    - Added `POST /api/canonical/dump` route.
    - All five launchers rewritten to relative paths and PATH Python.

(c) Refreshed 52-pattern references to 54-pattern v3.9 across README,
    methodology, tests, and docs.

(d) Deployed a fresh full copy to `D:\OrderGetItRight` via
    `deploy/deploy.ps1 -InstallPath "D:/OrderGetItRight" -Yes`.

(e) Fixed the `C:\OrderGetItRight` junction to point to `D:\OrderGetItRight`
    (was a broken junction to a non-existent .claude path).

(f) Verified portable operation:
    - pytest 71/1 from canonical source
    - pytest 71/1 from USB copy
    - verify_chain MATCH from both
    - audit_cli 5/5 success from USB copy
    - A5 redirect-detection test passes

(g) Refreshed reference docs:
    - `04_Validation/OPEN_ITEMS_AND_REFERENCE.md`
    - `04_Validation/YELLOW_RIBBON.md`
    - `04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt`

(h) Sealed two Merkle blocks:
    - `OPEN_ITEMS_D1_CLOSED_2026_07_16`
    - `DOCS_REFRESH_2026_07_16`

(i) Mirrored final canonical state to USB `D:\OrderGetItRight`.

(j) Updated project memory at
    `C:\Users\justo\.claude\projects\C--Users-justo\memory\order-get-it-right-state.md`.

================================================================================
4. WHAT IS STILL OPEN
================================================================================

Code fixes:
  A3. _seed_facts_once() in app.py calls reset_registry() unconditionally on
      startup. A server restart will wipe operator-added facts that were not
      sealed through the orchestrator. Make the reset conditional on an empty
      vault and add a regression test.

Documentation audits:
  C2. Audit `INTELLECTUAL_PROPERTY_RIGHTS.txt` against the current codebase.
  C3. Reconcile `MAINTENANCE_PLAN.txt` numbers with live state.
  C4. Add any missing agents to IP file and maintenance plan.
  C5. Final tone-of-done pass on `00_Strategy/STRATEGY.md` Section 7.

Determinism / portability:
  D2. Run the no-network import audit over the full tree (not just
      `02_Technical/src/`).
  D3. Complete a project-level black-box trace for every CLI/web output field.
  D1-TRUE. A real clean-host restore test on a second Windows PC with no
      Python installed remains operator work.

Operator-supplied inputs:
  E1. Gmail export to `.mbox` into `OneDrive\Documents\to the spoils go\inbox\`.
  E4. Pre-2020 reference corpus into
      `OneDrive\Documents\to the spoils go\pre_2020_corpus\`.

Optional:
  - Pull `tcoxav/aegis` (or another tool-calling model) to remove the single
    pytest skip and get 72/72.
  - Rebuild the Tauri shell if the operator wants a fresh binary bundle.

================================================================================
5. FIRST FIVE FILES TO READ
================================================================================

  1. This file (HANDOVER_NEXT_SESSION_2026-07-16.md).
  2. 04_Validation/OPEN_ITEMS_AND_REFERENCE.md (open items + fingerprints).
  3. 04_Validation/YELLOW_RIBBON.md (the ribbon: what the project is).
  4. 00_Strategy/STRATEGY.md (the contract with the world).
  5. 04_Validation/CONTEXT_WINDOW.md (the long-form digest).

================================================================================
6. NON-NEGOTIABLE CONSTANTS
================================================================================

Before changing any of these, run the CONSTANTS_BUMP procedure documented in
HANDOVER_TO_NEW_OPERATOR.md:

  - TAU_EXTRACTION_CEILING (see config/constants.py)
  - DECEPTION_ONTOLOGY_VERSION = 3.9 (54 patterns)
  - PROJECT_OPERATOR = "Justin Barnett"
  - PROJECT_JURISDICTION = "Commonwealth of Australia"

================================================================================
7. STANDARD OPENING RITUAL
================================================================================

Every session must start with:

  cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical"
  python -m src.verify_chain
  cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
  python -m pytest tests/ -q

If either command does not produce the expected result, stop and fix the state
before making any new changes.

================================================================================
8. HOW TO CLOSE A TODO ITEM
================================================================================

For each item you close:
  1. Make the code/doc change.
  2. Add or update a regression test if it touches code.
  3. Run the standard opening ritual; it must still pass.
  4. Update this handover or `04_Validation/TODO_FULL.md` to mark it done.
  5. Seal a Merkle block describing the closure.
  6. Refresh `OPEN_ITEMS_AND_REFERENCE.md`, `YELLOW_RIBBON.md`, and
     `QUICK_REFERENCE_CARD.txt` with the new root.
  7. Mirror the canonical source to `D:\OrderGetItRight` with robocopy /MIR.
  8. Re-run verify_chain on the USB copy to confirm MATCH.

================================================================================
END OF HANDOVER
================================================================================
