---
name: todo-full-2026-07-16
description: Complete detailed todo list for Order Get It Right as of 2026-07-16.
metadata:
  type: project
  originSessionId: 9c4425d6-35b6-4a10-b34c-b8bd31829254
---

================================================================================
ORDER GET IT RIGHT -- FULL DETAILED TODO LIST
Generated: 2026-07-16  (UTC)
Author:    codex-on-Justo  (operator: Justin Barnett)
================================================================================

This is the master action list. Items are grouped by category, then sorted by
priority within each group. Each item has a status, severity, effort estimate,
files touched, acceptance criteria, and the Merkle seal event type to use when
closing it.

Legend:
  [ ]  open
  [x]  closed
  [-]  not applicable / deferred / blocked on operator action
  !    high severity
  ~    medium severity
  .    low severity

================================================================================
A. CODE FIXES
================================================================================

[A1] Migrate FastAPI startup from @app.on_event("startup") to lifespan handler
  Status:  [x]  CLOSED (chain block 1683)
  Severity: !
  Effort:  30 minutes
  Files:    02_Technical/src/server/app.py
  Acceptance:
    - No DeprecationWarning about on_event("startup") during pytest.
    - TestClient still triggers seeding via /api/facts belt-and-suspenders.
    - 71/1 pytest still passes.
  Seal:     LIFESPAN_MIGRATED_2026_07_12

[A2] Fix v3.8/v3.9 hardcoded strings in startup seed facts
  Status:  [x]  CLOSED (chain blocks 228, 889)
  Severity: !
  Effort:  30 minutes
  Files:    02_Technical/src/server/app.py, 02_Technical/src/agents/orchestrator.py
  Acceptance:
    - _seed_facts_once() and orchestrator seed fact use DECEPTION_ONTOLOGY_VERSION.
    - Regression test asserts seeded facts contain live version string.
    - 71/1 pytest still passes.
  Seal:     ONTOLOGY_VERSION_DRIFT_CLOSED

[A3] Fix _seed_facts_once() startup reset foot-gun
  Status:  [x]  CLOSED (2026-07-17 -- C2_C3_C4_DOCS_RECONCILED_2026_07_17
          seal; the conditional-on-empty-vault fix and a regression test
          were added during the 2026-07-17 session)
  Severity: !
  Effort:  1 hour
  Files:    02_Technical/src/server/app.py, tests/test_smoke.py (or new test)
  Acceptance:
    - _seed_facts_once() only resets if vault has zero facts, OR reset is moved
      to a dedicated init CLI.
    - Regression test starts the app, adds an operator fact, restarts the app,
      and asserts the operator fact survives.
    - 71/1 pytest still passes (or 72/0 if Ollama model is present).
  Seal:     SEED_RESET_FOOTGUN_CLOSED
  Notes:    Closed during the 2026-07-17 session. The 71/1 acceptance
          criterion was superseded by the new 86/1 baseline (4 new
          static-dir tests added at the UI_OPERATOR_FACING_REDESIGN
          seal).

[A4] Build Tauri desktop shell
  Status:  [x]  CLOSED (chain block 1979)
  Severity: !
  Effort:  4 hours
  Files:    02_Technical/tauri-shell/
  Acceptance:
    - Raw .exe, MSI, NSIS installer produced.
    - .exe launches and shows correct window title.
    - 71/1 pytest still passes.
  Seal:     TAURI_SHELL_BUILT_2026_07_12
  Notes:    Binary exists on disk; operator follow-up is replace placeholder
            icons and run interactive smoke tests if desired.

[A5] Validate deploy.ps1 on clean host / dry-run
  Status:  [x]  CLOSED (chain block 2504, verified this session on real D: deploy)
  Severity: !
  Effort:  2 hours
  Files:    deploy/deploy.ps1, tests/test_a5_deploy_dry_run.py
  Acceptance:
    - `deploy/deploy.ps1 -DryRun` produces valid JSON report.
    - Dry-run catches the C:\OrderGetItRight junction foot-gun.
    - Real deploy to D:\OrderGetItRight succeeds and pytest/verify_chain pass.
    - 71/1 pytest still passes.
  Seal:     OPEN_ITEMS_A5_CLOSED_2026_07_12

[A6] Stale .pyc cache / .gitignore
  Status:  [x]  CLOSED (chain block 1800)
  Severity: .
  Effort:  15 minutes
  Files:    .gitignore, deleted __pycache__ directories
  Acceptance:
    - .gitignore excludes __pycache__, .pytest_cache, .pyc, .pyo, .pyd.
    - Existing stale caches removed.
    - 71/1 pytest still passes.
  Seal:     PYC_CACHE_CLEANUP_2026_07_12

================================================================================
B. TESTS / TEST INFRASTRUCTURE
================================================================================

[B1] Delete stale .pytest_cache
  Status:  [x]  CLOSED (chain block 2270)
  Severity: .
  Effort:  15 minutes
  Files:    .gitignore, .pytest_cache/
  Acceptance:
    - Stale nodeids removed.
    - Cache regenerates cleanly on next run.
    - 71/1 pytest still passes.
  Seal:     OPEN_ITEMS_B1_CLOSED_2026_07_12

[B2] Add determinism regression test for evaluation suite
  Status:  [x]  CLOSED (chain block 1392)
  Severity: !
  Effort:  30 minutes
  Files:    tests/test_smoke.py
  Acceptance:
    - Runs run_evaluation_suite() multiple times.
    - Strips volatile fields (runId, timestamp).
    - Asserts byte-identical results across runs.
    - 71/1 pytest still passes.
  Seal:     DETERMINISM_REGRESSION_TEST_ADDED

[B3] Add host-dependent integration tests
  Status:  [x]  CLOSED (chain block 2270)
  Severity: ~
  Effort:  1 hour
  Files:    tests/test_b3_host_dependent.py
  Acceptance:
    - Tests Tauri binary, installers, build env, deploy.ps1 parse, hard-copy
      plan, USB restore placeholder.
    - Every test skip-guarded with clear message naming missing host feature.
    - 71/1 pytest still passes on this host; 72/0 if Tauri built + Ollama model.
  Seal:     OPEN_ITEMS_B3_CLOSED_2026_07_12

[B4] Python 3.12 compatibility / BOM cleanup
  Status:  [x]  CLOSED (chain block 2270)
  Severity: ~
  Effort:  1 hour
  Files:    tests/test_b4_python_312_compat.py, multiple runtime files
  Acceptance:
    - Static analysis finds no PEP 695 syntax or 3.13+ stdlib imports.
    - All runtime files stripped of UTF-8 BOM.
    - 71/1 pytest still passes.
  Seal:     OPEN_ITEMS_B4_CLOSED_2026_07_12

[B5] Ollama tool-calling model test
  Status:  [x]  CLOSED (2026-07-17 -- OLLANMA_MODEL_SWAP_QWEN3_5_9B_2026_07_17)
  Severity: .
  Effort:  5 minutes
  Files:    tests/test_d5_agentic_repl.py, 02_Technical/tools/agentic_repl.py
  Acceptance:
    - Update DEFAULT_MODEL to a model already present that supports tool_calls
      (verified: qwen3.5:9b probed and returns structured tool_calls).
    - Run pytest; the single skip becomes a pass.
    - 73/0 pytest.
  Seal:     OLLANMA_MODEL_SWAP_QWEN3_5_9B_2026_07_17
  Notes:    DEFAULT_MODEL changed from tcoxav/aegis:latest to qwen3.5:9b.
            _ollama_supports_tools() now probes with a real tool and a
            120s timeout (was 10s, which timed out on cold load).
            agentic_repl.py forces UTF-8 stdout so the qwen3.5 U+2713
            reply does not crash on cp1252 Windows consoles; defense in
            depth also added in _format_assistant().

================================================================================
C. DOCUMENTATION AUDITS AND UPDATES
================================================================================

[C1] Refresh QUICK_REFERENCE_CARD and YELLOW_RIBBON Merkle roots
  Status:  [x]  CLOSED (this session, refreshed to root bba6445e...)
  Severity: !
  Effort:  30 minutes
  Files:    04_Validation/YELLOW_RIBBON.md,
            04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt,
            04_Validation/OPEN_ITEMS_AND_REFERENCE.md
  Acceptance:
    - All three docs contain the live Merkle root.
    - Reference fingerprints REF-1..REF-6 re-derived and correct.
    - 71/1 pytest still passes.
  Seal:     DOCS_REFRESH_2026_07_16

[C2] Audit INTELLECTUAL_PROPERTY_RIGHTS.txt against current codebase
  Status:  [x]  CLOSED (2026-07-17 -- C2_C3_C4_DOCS_RECONCILED_2026_07_17
          seal; 17 KB of IP clauses audited against the current codebase;
          the third-party package count was 9 in the document but the
          live requirements.txt has 10; corrected. The default Ollama
          model note was added -- was tcoxav/aegis:latest, now qwen3.5:9b.
          All agent names mentioned in the IP file were cross-checked
          against 02_Technical/src/agents/. The IP file now lists 10
          named modules and 10 third-party packages; the Ollama model
          swap is documented at line 72.)
  Severity: ~
  Effort:  2 hours
  Files:    04_Validation/INTELLECTUAL_PROPERTY_RIGHTS.txt, all .py files
  Acceptance:
    - Walk every .py file; list every third-party symbol/library.
    - Confirm IP file's claims/exclusions match current code.
    - Add missing agent names (InventoryAgent, etc.).
    - 71/1 pytest still passes.
  Seal:     IP_AUDIT_COMPLETE

[C3] Reconcile MAINTENANCE_PLAN.txt with live state
  Status:  [x]  CLOSED (2026-07-17 -- C2_C3_C4_DOCS_RECONCILED_2026_07_17
          seal; MAINTENANCE_PLAN.txt was reconciled with live state;
          the 71/1 test-count baseline was preserved as the historical
          reference, the live state is now 86/1 since the static-dir
          tests were added. NOTE: the test-count acceptance criterion
          "71 pass + 1 skip" is now historical; the live test count is
          86/1. The MAINTENANCE_PLAN.txt file itself has NOT been
          re-reconciled since then -- it still shows the 2026-07-17
          baseline. A future session may wish to update it to 86/1
          if that is required; it is not a chain-affecting change.)
  Severity: ~
  Effort:  1 hour
  Files:    04_Validation/MAINTENANCE_PLAN.txt,
            04_Validation/STAGE_PAPER_*.txt
  Acceptance:
    - Test counts match 71 pass + 1 skip (or 72/0 if Ollama model ready).
    - Vault path recorded as 03_Vault/.
    - SDXC/USB status recorded as D:\OrderGetItRight, current.
    - Stage paper cross-references consistent.
    - 71/1 pytest still passes.
  Seal:     MAINTENANCE_PLAN_RECONCILED

[C4] Add new agents to IP file and maintenance plan
  Status:  [x]  CLOSED (2026-07-17 -- C2_C3_C4_DOCS_RECONCILED_2026_07_17
          seal; InventoryAgent and any other agents added since the
          last audit are now listed in
          04_Validation/INTELLECTUAL_PROPERTY_RIGHTS.txt and
          04_Validation/MAINTENANCE_PLAN.txt; 10 named modules
          cross-checked against 02_Technical/src/agents/.)
  Severity: ~
  Effort:  30 minutes
  Files:    04_Validation/INTELLECTUAL_PROPERTY_RIGHTS.txt,
            04_Validation/MAINTENANCE_PLAN.txt
  Acceptance:
    - InventoryAgent listed.
    - Any other agents added since the last audit listed.
    - 71/1 pytest still passes.
  Seal:     AGENT_LISTS_UPDATED

[C5] Final STRATEGY.md tone-of-done pass
  Status:  [ ]  OPEN
  Severity: .
  Effort:  30 minutes
  Files:    00_Strategy/STRATEGY.md
  Acceptance:
    - Section 7 checkboxes read "operational and maintained" rather than
      "completed".
    - Test-count line matches live state (71/1 or 72/0).
    - 71/1 pytest still passes.
  Seal:     STRATEGY_TONE_OF_DONE_FIXED

================================================================================
D. SECURITY / DETERMINISM / PORTABILITY
================================================================================

[D1] USB clean-host restore test
  Status:  [x]  CLOSED to extent verifiable on this host
            [ ]  TRUE clean-host test still pending
  Severity: !
  Effort:  2-4 hours (operator work)
  Files:    None (hardware test)
  Acceptance (this-host):
    - Fresh deploy to D:\OrderGetItRight succeeds.
    - pytest 71/1 from USB passes.
    - verify_chain MATCH from USB.
    - C:\OrderGetItRight junction correct.
    - audit_cli 5/5 success from USB.
    - Seal: OPEN_ITEMS_D1_CLOSED_2026_07_16 (already sealed).
  Acceptance (true clean-host):
    - On a second Windows PC with NO Python installed, copy the project from
      USB.
    - Run deploy/deploy.ps1; it must install/provision Python and pass.
    - Run pytest; expect 71/1 (or 72/0 with Ollama model).
    - Run verify_chain; expect MATCH.
    - Record host specs, any failures, and whether the Merkle root matches.
    - Seal: D1_TRUE_CLEAN_HOST_VERIFIED
  Notes:    This-host portion is done. True clean-host requires a second PC.

[D2] Full-tree no-network import audit
  Status:  [x]  CLOSED for 02_Technical/src/
            [ ]  OPEN for full tree (tools, tests, bundled runtime)
  Severity: ~
  Effort:  1 hour
  Files:    04_Validation/scripts/audit_no_network.py (extend),
            04_Validation/AUDIT_NO_NETWORK.md (extend)
  Acceptance:
    - Script walks 02_Technical/tools/, tests/, and relevant bundled runtime
      files (excluding legitimate vendored libraries like pip).
    - Flags any urllib/requests/http.client/socket/asyncio-network imports.
    - Exits 0 if clean; non-zero if any import found.
    - Document lists exactly which files are allowed to touch the network and
      why.
    - 71/1 pytest still passes.
  Seal:     FULL_TREE_NO_NETWORK_AUDIT_COMPLETE

[D3] Full project-level black-box audit
  Status:  [x]  PARTIAL (AUDIT_NO_BLACK_BOX.md covers 14 pillars)
            [ ]  OPEN for complete screen-to-function trace
  Severity: ~
  Effort:  2 hours
  Files:    04_Validation/AUDIT_NO_BLACK_BOX.md
  Acceptance:
    - For every number shown in CLI output, web UI, PDF, and Markdown reports,
      list the Python file, function, and line that computed it.
    - No number appears without a traceable source.
    - 71/1 pytest still passes.
  Seal:     FULL_BLACK_BOX_TRACE_COMPLETE

[D4] Verify-from-USB CLI subcommand
  Status:  [x]  CLOSED (chain block 889)
  Severity: !
  Effort:  1 hour
  Files:    02_Technical/src/verify_chain.py
  Acceptance:
    - `python -m src.verify_chain` re-derives Merkle root and prints MATCH/BROKEN.
    - Optional --vault and --print-refs flags work.
    - 71/1 pytest still passes.
  Seal:     VERIFY_CHAIN_CLI_ADDED

[D5] Agent wiring end-to-end
  Status:  [x]  CLOSED (chain block 2387)
            [ ]  RUNTIME exercise pending Ollama tool-calling model
  Severity: ~
  Effort:  30 minutes
  Files:    02_Technical/tools/agentic_repl.py
  Acceptance:
    - Static tests pass (tool schemas, dispatch, etc.).
    - With Ollama + tool-calling model + FastAPI server, the REPL answers a
      prompt by calling at least one tool.
    - 72/0 pytest if model present; 71/1 otherwise.
  Seal:     D5_RUNTIME_EXERCISED
  Notes:    Block 2387 sealed the wiring. The runtime exercise needs the model.

================================================================================
E. OPERATOR-SUPPLIED INPUTS
================================================================================

[E1] Gmail export for InventoryAgent
  Status:  [ ]  OPEN (operator action)
  Severity: ~
  Effort:  30 minutes (operator side)
  Files:    OneDrive\Documents\to the spoils go\inbox\
  Acceptance:
    - Export truthproject.official@gmail.com to .mbox format.
    - Drop .mbox into OneDrive\Documents\to the spoils go\inbox\.
    - Run InventoryAgent or a future EmailReader agent against it.
    - Seal: GMAIL_CORPUS_INGESTED
  Notes:    Network egress is not granted to the AI. Operator must export.

[E2] OpenClaw assistant
  Status:  [-]  NOT APPLICABLE
  Severity: .
  Effort:  N/A
  Files:    N/A
  Acceptance:
    - third_party_assistant.py implements the equivalent local-assistant pattern.
  Seal:     N/A

[E3] via_app_data.py / rewrite.py hints
  Status:  [-]  FALSE LEADS (recorded in docs)
  Severity: .
  Effort:  N/A
  Files:    N/A
  Acceptance:
    - These files were library noise, not relevant.
  Seal:     N/A

[E4] Pre-2020 reference corpus
  Status:  [ ]  OPEN (operator action)
  Severity: ~
  Effort:  varies (operator side)
  Files:    OneDrive\Documents\to the spoils go\pre_2020_corpus\
  Acceptance:
    - Operator drops pre-2020 reference files into the folder.
    - Re-run audit_cli against them.
    - Seal: PRE_2020_CORPUS_INGESTED
  Notes:    verified_prior_2021.txt is the closest sample currently on disk.

================================================================================
F. SESSION HYGIENE (do this every session)
================================================================================

[F1] Start-of-session ritual
  - Run verify_chain on source and USB.
  - Run pytest on source.
  - Confirm expected counts before making changes.

[F2] End-of-session ritual
  - Run pytest; confirm 71/1 (or 72/0).
  - Run verify_chain; confirm MATCH.
  - If any chain seal was added, refresh OPEN_ITEMS_AND_REFERENCE.md,
    YELLOW_RIBBON.md, and QUICK_REFERENCE_CARD.txt.
  - Mirror canonical source to D:\OrderGetItRight with robocopy /MIR.
  - Run verify_chain on D:\OrderGetItRight; confirm MATCH.
  - Update project memory at
    C:\Users\justo\.claude\projects\C--Users-justo\memory\order-get-it-right-state.md.

[F3] Robocopy mirror command template
      robocopy "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight" \
               "D:\OrderGetItRight" /MIR /XD __pycache__ .pytest_cache target node_modules \
               /XF *.bak-pre-* /R:2 /W:2
      (Use //MIR //XD ... //XF ... in Git Bash to avoid argument parsing issues.)

================================================================================
SUMMARY
================================================================================

Closed this session or earlier:  A1, A2, A3, A4, A5, A6, B1, B2, B3, B4, B5,
                                  C1, C2, C3, C4, D1-this-host, D4, D5-wiring,
                                  A7, A8, A9, A10 (UI/Tauri refresh, 2026-07-17).

Closed 2026-07-18 (this build):   F1+F3 (docs reconciliation),
                                  F2 (tree cleanup; 11 .bak-pre-* removed,
                                       2 empty dirs, .gitignore rules),
                                  F4 (KNOWN_CHAIN_ARTEFACTS.md),
                                  F5 (changelog pollution gated),
                                  F6 (nizk_proof -> integrity_digest),
                                  F7 (lattice reframed to optionality index
                                       with LATTICE_FRAMING),
                                  F8 (ontology R1-R4 applied; 4 structural
                                       co-text gates; 3.9 -> 3.10),
                                  F8-EXT-R5 (DD-009 lexical set expansion
                                            covering 100% correct,
                                            100% success, 100% complete),
                                  F11 (Git adopted in parallel),
                                  F12 (canonical_dumps propagated),
                                  F13 (monitor_agent REFUSAL/Squeal
                                       cross-check; unexplained=0 on live chain),
                                  F14 (determinism headline amended),
                                  F15 (cleanup seal; 6 sub-fixes),
                                  F16 (single-worker assumption documented),
                                  F17 (test portability fixed).

Still open / next actions:       C5 (STRATEGY.md Section 7 tone-of-done pass),
                                  D1-true-clean-host (operator work,
                                       needs a second PC),
                                  E1 (operator; Gmail .mbox into
                                       OneDrive\Documents\to the spoils
                                       go\inbox\ -- not done yet),
                                  E4 (operator; pre-2020 reference
                                       corpus into
                                       OneDrive\Documents\to the spoils
                                       go\pre_2020_corpus\ -- not done
                                       yet),
                                  F7-deep (lattice inputs hard-coded --
                                          OPEN; F7 cheap path closed the
                                          language but not the inputs),
                                  F8-EXTENDED-LEGAL (embed Makita citation
                                          in legal_affidavit_generator),
                                  F8-EXTENDED EVAL-suite expansion
                                          (8 -> 30+ cases),
                                  R5-EXTENDED (lexical-set audit for
                                          remaining 53 patterns),
                                  F11-remote (operator decision: pick a
                                          Git remote; 3 options in
                                          GIT_WORKFLOW.md section 2.4).

Expected test count:             88 passed, 1 skipped, 0 failed
                                 (was 86 before the F8 R1-R4 regression test
                                  was added in this build)

Live chain:                      10561 blocks, root 5b66058e8d322f00a724a9f4b36cdf3f3f9a6d7a01dc147c9ebf843bf05b71f3
                                 (the FastAPI lifespan handler writes
                                 additional SHUTDOWN blocks during
                                 every verify_chain / pytest run;
                                 this number advances with each run)

================================================================================
END OF TODO LIST
================================================================================
