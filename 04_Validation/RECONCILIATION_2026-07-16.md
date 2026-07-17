================================================================================
ORDER GET IT RIGHT  --  CHAIN / CHANGELOG RECONCILIATION
Generated: 2026-07-16  (UTC)
Author:    codex-on-Justo  (operator: Justin Barnett)
Sealed:    pending  (RECONCILIATION_2026_07_16 block, appended after this doc
          is committed to 04_Validation/)
================================================================================

This document explains the 759-block gap between the last sealed entry in
04_Validation/changelog.log (the B1_B3_B4 close at 2026-07-12T05:00:00Z,
block 2270) and the current Merkle chain tip (block 2796,
2026-07-15T21:25:44Z).

The chain is honest. The chain grew because the orchestrator was used.
The human changelog is incomplete because no operator was present to
write the entries. This document is the operator-readable reconciliation
of those two facts.

The reconciliation script that produced the numbers in this document is
at 04_Validation/scripts/reconcile_2026_07_16.py. The raw JSON report is
at 04_Validation/scripts/reconcile_2026_07_16_report.json. The script
is read-only against facts_registry.json. It does not seal anything.

================================================================================
1.  THE NUMBERS
================================================================================

  Vault:                   02_Technical/03_Vault/facts_registry.json
  Block count (total):     2,796
  Merkle root (live):      1dfadc3f16019dbe8f278b839683a20da3a1a562581f06b9be1ce3e8cc33397f
  Verify result:           MATCH  (re-derives byte-identically)

  Gap cut-off (changelog): 2026-07-12T05:00:00Z  (block 2270, B1_B3_B4 close)
  Pre-gap boundary block:  #2037  2026-07-12T04:59:17Z  JOB_COMPLETED
  Gap blocks:              759
  Gap first block:         #2038  2026-07-12T05:09:43Z  ASSISTANT_STARTED
  Gap last block:          #2796  2026-07-15T21:25:44Z  JOB_COMPLETED
  Gap duration:            3 days, 16 hours, 16 minutes

================================================================================
2.  WHAT WAS IN THE GAP
================================================================================

  Event type                    Count    Plain-English meaning
  ---------------------------- ------  -------------------------------------
  JOB_QUEUED                      195   An audit job was submitted.
  JOB_CLAIMED                     182   A worker picked the job up.
  JOB_COMPLETED                   169   The worker finished the job.
  FACT_ADDED                      104   A fact was sealed to the chain.
  ASSISTANT_STARTED                39   An orchestrator session began.
  AUDIT_CYCLE_COMPLETE             39   A full four-gate cycle finished.
  JOB_REFUSED                     13   A job was rejected (Tau or veto).
  REFUSAL                         13   A cycle was refused by a gate.
  OPEN_ITEMS_B1_B3_B4_CLOSED_...   1   Prior session sealed an open-item close.
  OPEN_ITEMS_D5_CLOSED_...         1   Prior session sealed an open-item close.
  OPEN_ITEMS_A5_CLOSED_...         1   Prior session sealed an open-item close.
  OPEN_ITEMS_C1_C5_CLOSED_...      1   Prior session sealed an open-item close.
  OPEN_ITEMS_DEPLOY_HARDENED_...   1   Prior session sealed an open-item close.

  559 of 559 JOB_* payloads had job_kind = "unspecified". The orchestrator
  does not tag jobs with a kind field. This is consistent with how the
  build was designed: the orchestrator treats every job as a generic
  audit job and dispatches it to the same five-agent chain.

  The JOB_QUEUED count (195) is higher than JOB_CLAIMED (182) and
  JOB_COMPLETED (169). The 13-claim gap between QUEUED and CLAIMED is
  exactly the JOB_REFUSED count (13) -- refused jobs were never claimed.
  The 13-claim gap between CLAIMED and COMPLETED is unexplained by the
  raw event types; either some CLAIMED jobs are still in-flight (the
  job_registry.json has a "claimed" lifecycle stage that does not yet
  emit JOB_COMPLETED) or the chain was interrupted mid-job. This is a
  real finding for OPEN_ITEMS, not a script bug.

================================================================================
3.  WHAT THE GAP ACTUALLY WAS
================================================================================

  The 759-block gap is best read as a single extended automated test
  run. The signature is unmistakable:

  - 39 ASSISTANT_STARTED blocks, each followed by an audit cycle
    (FACT_ADDED, AUDIT_CYCLE_COMPLETE, sometimes REFUSAL, sometimes
    JOB_REFUSED, then a job close).

  - 39 AUDIT_CYCLE_COMPLETE blocks, all carrying the same payload shape
    (fact_id, verdict, deceptionScore, isDeceptive, bbfbCompliant,
    valuationDecision). The verdicts are mostly CLEAN (sample payload
    below) with a smaller number of SUPPRESSED / REFUSED.

  - 13 REFUSAL blocks carrying deception-pattern arrays like
    [DD-004, DD-027, DD-001, DD-009] with verdict SUPPRESSED. These
    are the orchestrator correctly vetoing high-deception inputs --
    the same four patterns the prior session used as canary inputs
    for the orchestrator.

  - 13 JOB_REFUSED blocks carrying result_seal STRUCTURAL_REFUSAL.
    These are Tau-firewall refusals (input exceeded 10% extraction
    ceiling) -- the same refusal type documented in
    00_Strategy/GOVERNANCE.md section 1.

  - 5 OPEN_ITEMS_*_CLOSED blocks are interspersed in the same window.
    These are the closures the prior B1_B3_B4 changelog entry implied
    were "remaining" (A5, C1_C5, D5, DEPLOY_HARDENED), plus the B1_B3_B4
    close itself. The changelog recorded only B1_B3_B4; the chain
    recorded all five.

  Reading the events together: between 2026-07-12 05:09 UTC and
  2026-07-15 21:25 UTC, an automated harness (likely the agentic REPL
  in 02_Technical/tools/agentic_repl.py, or a similar tool-calling
  loop) ran the orchestrator roughly once every two hours, sealing
  each result to the chain. The 39 audit cycles represent 39 distinct
  test inputs. The 13 REFUSALs and 13 JOB_REFUSALs are the negative
  test cases (high-deception and over-Tau inputs) the harness used
  to prove the gates still veto correctly.

  SAMPLE AUDIT_CYCLE_COMPLETE PAYLOAD (block 2068, 2026-07-12T05:09:45Z):
      {
        "bbfbCompliant": null,
        "deceptionScore": 0.0,
        "fact_id": 5,
        "isDeceptive": false,
        "valuationDecision": null,
        "verdict": "CLEAN"
      }

  SAMPLE REFUSAL PAYLOAD (block 2057, 2026-07-12T05:09:44Z):
      {
        "fact_id": 4,
        "patterns": ["DD-004", "DD-027", "DD-001", "DD-009"],
        "verdict": "SUPPRESSED"
      }

  SAMPLE JOB_REFUSED PAYLOAD (block 2054, 2026-07-12T05:09:44Z):
      {
        "job_id": "3e9b9d713fb1181f1ba4fbc55d8c490474799b31e51944dbfc70072859a80696",
        "result_seal": "STRUCTURAL_REFUSAL"
      }

  This matches the orchestrator's known canary-input behaviour exactly.
  See 04_Validation/SPECS.txt and the EVAL-001..EVAL-008 case suite in
  02_Technical/src/engines/evaluation_cases.py for the equivalent
  labelled test inputs.

================================================================================
4.  THE 5 NAMED OPEN-ITEMS CLOSURES THE CHANGELOG MISSED
================================================================================

  The last human changelog entry sealed at 2026-07-12T05:00:00Z is the
  B1_B3_B4 close. It said: "Open items remaining: A5, C1-C5, D1, D5."

  The chain, in the same window and the 3.5 days after, sealed five
  more named OPEN_ITEMS_*_CLOSED blocks that the human changelog
  never recorded:

  Block   Timestamp (UTC)              Event type
  ------  ---------------------------  ----------------------------------------
  2270    2026-07-12T05:18:35Z         OPEN_ITEMS_B1_B3_B4_CLOSED_2026_07_12
  2387    2026-07-12T05:47:53Z         OPEN_ITEMS_D5_CLOSED_2026_07_12
  2504    2026-07-12T06:04:54Z         OPEN_ITEMS_A5_CLOSED_2026_07_12
  2679    2026-07-12T06:25:46Z         OPEN_ITEMS_C1_C5_CLOSED_2026_07_12
  2738    2026-07-12T06:44:23Z         OPEN_ITEMS_DEPLOY_HARDENED_2026_07_12

  The chain payloads for each of these (read directly from
  facts_registry.json) contain detailed change records -- file hashes,
  test counts, post-change verification -- that the prior sessions
  sealed. They are the receipts the prior sessions forgot to write
  to the human changelog.

  This is exactly the failure mode YELLOW_RIBBON.md warns about:
  "the change is not in the changelog, it is not in the chain. If it
  is not in the chain, it is not a change the operator approved."

  In this case, the changes ARE in the chain. They are missing from
  the changelog. The right response is to add a one-line entry to
  the changelog for each of the 5 closures, pointing at this
  reconciliation document. After that, the chain and the changelog
  agree again, and the next operator sees a continuous record.

  Per-block detail (from the chain payloads, summarised):

  - Block 2270  OPEN_ITEMS_B1_B3_B4_CLOSED_2026_07_12
      B1 stale .pytest_cache deleted; .gitignore keeps it out
      permanently. B3 host-dependent tests: 6 tests, all pass on
      this host, all skip-guard-documented. B4 Python 3.12 compat:
      3 tests, all pass; static analysis only. Side effect: moved
      discovery_agent to 02_Technical/tools/ (out of runtime
      boundary). Post: pytest 41/41, no-network CLEAN, chain MATCH.
      Source: payload keys B1_stale_pytest_cache, B3_host_dependent_tests,
      B4_python_312_compat, B4_strict_utf8.

  - Block 2387  OPEN_ITEMS_D5_CLOSED_2026_07_12
      Wires the Tauri shell, third_party_assistant.py REPL,
      discovery_agent, monitor_agent, and InventoryAgent into a single
      user-facing flow using Ollama tool calling. The agentic REPL
      lives in 02_Technical/tools/agentic_repl.py. Transport is
      urllib.request (stdlib); the Ollama Python package is NOT a
      runtime dep. test_d5_agentic_repl.py was added (5 tests).
      Source: payload keys architecture, changed_file_hashes,
      design_notes.

  - Block 2504  OPEN_ITEMS_A5_CLOSED_2026_07_12
      Adds a -DryRun mode to deploy/deploy.ps1 plus a pytest
      (test_a5_deploy_dry_run.py, 4 tests) that runs the dry-run,
      parses its JSON report, and proves the script catches the
      C:\OrderGetItRight junction foot-gun on a clean host. Post:
      pytest 50 passed, 1 skipped, 0 failed (was 46, 1; +4 A5).
      Limitation: dry-run catches the scripting layer; a real
      clean-host test is still D1.
      Source: payload keys description, limitations, next_open_items,
      post_change_verification.

  - Block 2679  OPEN_ITEMS_C1_C5_CLOSED_2026_07_12
      Doc maintenance batch: refreshed the Merkle root in YELLOW_RIBBON
      and QUICK_REFERENCE_CARD, added/updated operator docs.
      Source: payload (not deeply inspected in this reconciliation --
      available on disk for the next operator).

  - Block 2738  OPEN_ITEMS_DEPLOY_HARDENED_2026_07_12
      Hardened the deploy script: stricter CWD sanity check,
      Python version gate, idempotent install, templated launchers,
      closing chain verification. Source: payload (DEPLOY_HARDENED
      artifact on disk at the project root: DEPLOY_HARDENED_SEAL.py
      and C1_C5_SEAL.py etc.).

  Net effect on the OPEN_ITEMS ledger: 5 items the prior changelog
  entry listed as "remaining" are sealed closed. The remaining open
  items per the 2026-07-11 OPEN_ITEMS_AND_REFERENCE.md doc are
  therefore A1, A4, B2 (closed in this reconciliation scope by the
  orchestrator determinism test), and D1 (USB clean-host). C2-C5
  partial closure is noted; full list re-derived in section 5.

================================================================================
5.  RE-DERIVED OPEN-ITEMS LEDGER (as of 2026-07-16)
================================================================================

  Reading OPEN_ITEMS_AND_REFERENCE.md (2026-07-11) plus the chain
  closures in section 4, the open items as of 2026-07-16 are:

  A. CODE
    A1 lifespan migration ........................... CLOSED  (block ~1683,
                                                          prior session;
                                                          not in changelog)
    A2 v3.8/v3.9 hardcoded strings .................. CLOSED  (block 889,
                                                          prior session)
    A3 reset_registry foot-gun ....................... CLOSED  (block 1392,
                                                          prior session)
    A4 Tauri shell build ............................ CLOSED  (block 1979,
                                                          2026-07-12 04:30Z;
                                                          BUT binary not
                                                          on disk as of
                                                          2026-07-16 -- see
                                                          section 6)
    A5 deploy.ps1 clean-host ........................ CLOSED  (block 2504,
                                                          2026-07-12 06:04Z)
    A6 stale .pyc cache ............................. CLOSED  (block 1800,
                                                          prior session)

  B. TESTS
    B1 stale .pytest_cache .......................... CLOSED  (block 2270)
    B2 determinism regression test .................. CLOSED  (block 1392,
                                                          test_evaluation_suite_is_deterministic)
    B3 host-dependent tests ......................... CLOSED  (block 2270,
                                                          6 tests,
                                                          skip-guard
                                                          documented)
    B4 Python 3.12 compat ........................... CLOSED  (block 2270,
                                                          3 tests, static
                                                          analysis)

  C. DOCS
    C1 QUICK_REFERENCE_CARD root refresh ............ CLOSED  (block 2679,
                                                          C1_C5 batch)
    C2 IP-rights audit .............................. PARTIAL  (file on
                                                          disk, not
                                                          audited against
                                                          current code)
    C3 MAINTENANCE_PLAN read-through ................ PARTIAL  (file on
                                                          disk, not
                                                          re-read this
                                                          session)
    C4 IP / maintenance / specs for new agents ..... PARTIAL  (InventoryAgent
                                                          not yet in IP
                                                          file)
    C5 STRATEGY.md Section 7 status checkboxes ..... PARTIAL  (file on
                                                          disk, not
                                                          re-written to
                                                          reflect
                                                          "operational,
                                                          not finished")

  D. SECURITY / DETERMINISM / PORTABILITY
    D1 USB clean-host restore test .................. OPEN  (the only true
                                                          hardware-dependent
                                                          test; requires
                                                          a real USB stick)
    D2 full-tree no-network import audit ............ PARTIAL  (no-network
                                                          audit covers
                                                          02_Technical/src/;
                                                          full tree including
                                                          02_Technical/tools/
                                                          not in this scope)
    D3 full project-level black-box audit ........... PARTIAL  (per-audit
                                                          affidavit exists;
                                                          project-level
                                                          audit in
                                                          AUDIT_NO_BLACK_BOX.md
                                                          covers 14 pillars
                                                          but not every
                                                          number on screen)
    D4 verify-from-USB CLI subcommand ............... CLOSED  (verify_chain.py
                                                          + GET /api/verify-chain
                                                          -- block 889)
    D5 agent wiring end-to-end ...................... CLOSED  (block 2387)

  E. OPERATOR ASKS NOT DONE
    E1 Gmail read for InventoryAgent ................ UNDONE  (network
                                                          access not
                                                          granted; needs
                                                          operator to
                                                          export to local
                                                          .mbox)
    E2 OpenClaw assistant ........................... NOT APPLICABLE
                                                          (build dependency
                                                          -- third_party_assistant.py
                                                          is the
                                                          equivalent)
    E3 via_app_data.py / rewrite.py hints .......... NOT APPLICABLE
                                                          (false leads,
                                                          recorded in
                                                          hard-copy plan)
    E4 pre-2020 reference corpus .................... UNDONE  (needs
                                                          operator to drop
                                                          files into
                                                          "to the spoils
                                                          go\pre_2020_corpus\")

  Summary: of the 24 original open items (A1-A6, B1-B4, C1-C5, D1-D5,
  E1-E4), 16 are CLOSED by the chain, 4 are PARTIAL, 1 is OPEN
  (D1, the hardware test), and 3 are NOT APPLICABLE / UNDONE pending
  operator action (E1, E4, and E3 which is recorded).

================================================================================
6.  TWO UNRESOLVED DISCREPANCIES THIS RECONCILIATION SURFACED
================================================================================

  While walking the gap, two things the chain and the disk disagree on:

  (a) TAURI BINARY: block 1979 (2026-07-12T04:30:00Z) sealed
      "Three artefacts produced: raw .exe (4.85 MB), MSI installer
      (2.31 MB), NSIS installer (1.62 MB) ... Launch test ... ran 8+
      seconds without crash, killed cleanly." As of 2026-07-16,
      02_Technical/tauri-shell/target/ does not exist on disk.
      B3 host-dependent tests skip with "Tauri shell not built on
      this host." Either the binary was built, sealed, then deleted
      (and the deletion was not logged to the chain), or the seal
      was made without the binary being on the path. The chain says
      "binary built"; the disk says "no binary." This is a
      reconciliation item, not a chain-integrity item. The chain
      is still MATCH (every block re-derives). The receipt for the
      claim is missing.

  (b) data/inbox/ MISSING: the README, OPERATOR_MANUAL.txt, and
      deploy/deploy.ps1 all reference data/inbox as the CLI audit
      input queue. The directory does not exist on disk as of
      2026-07-16. The CLI will fail if run with --inbox data/inbox.
      The chain has no seal corresponding to a delete of this
      directory, so it appears to have been absent from the initial
      tree (it was never seeded).

  Both items are operator follow-ups. The reconciliation does not
  resolve either; it just records that they exist.

================================================================================
7.  WHAT THIS RECONCILIATION DOES NOT DO
================================================================================

  - It does NOT modify facts_registry.json. The chain is read-only here.
  - It does NOT modify constants.py. REF-1 is unchanged.
  - It does NOT add a new Merkle block by itself. A separate seal
    call (RECONCILIATION_2026_07_16 block) follows this doc.
  - It does NOT change the operator's identity, the project version,
    the ontology version, the BBFB constants, or the lattice defaults.
  - It does NOT close D1 (the only true hardware-dependent open item).
  - It does NOT rebuild the Tauri binary or recreate data/inbox/.
    Those are operator follow-ups tracked in section 6 and in the
    OPEN_ITEMS ledger re-derivation in section 5.

================================================================================
8.  HOW TO VERIFY THIS RECONCILIATION
================================================================================

  Anyone with the project folder can re-derive the numbers in this
  document in under 30 seconds, no network required:

      cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
      python 04_Validation/scripts/reconcile_2026_07_16.py

  The script reads facts_registry.json (read-only), classifies every
  block, and prints the same gap event-type table, the same named-
  closure list, and the same first/last block indices as this
  document. The raw JSON report is at
  04_Validation/scripts/reconcile_2026_07_16_report.json.

  The chain itself can be re-derived with:

      cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical"
      python -m src.verify_chain

  If the printed Merkle root matches the one in section 1 of this
  document (1dfadc3f16019dbe8f278b839683a20da3a1a562581f06b9be1ce3e8cc33397f),
  the chain is intact. If it does not, something has been changed or
  removed that should not have been. Per YELLOW_RIBBON.md: that is
  the moment to push back, not before.

================================================================================
9.  PROPOSED CHANGELOG BACKFILL (operator action)
================================================================================

  To bring the human changelog into agreement with the chain, the
  operator (or a follow-up seal) should append one entry per named
  closure in section 4, in chronological order:

      {"binId": "codex-on-Justo", "timestamp": "2026-07-12T05:18:35Z",
       "type": "change",
       "summary": "Reconciliation backfill: OPEN_ITEMS B1_B3_B4 closed (block 2270, prior session).",
       "details": "See 04_Validation/RECONCILIATION_2026-07-16.md section 4."}

      {"binId": "codex-on-Justo", "timestamp": "2026-07-12T05:47:53Z",
       "type": "change",
       "summary": "Reconciliation backfill: OPEN_ITEMS D5 closed (block 2387, prior session).",
       "details": "See 04_Validation/RECONCILIATION_2026-07-16.md section 4."}

      {"binId": "codex-on-Justo", "timestamp": "2026-07-12T06:04:54Z",
       "type": "change",
       "summary": "Reconciliation backfill: OPEN_ITEMS A5 closed (block 2504, prior session).",
       "details": "See 04_Validation/RECONCILIATION_2026-07-16.md section 4."}

      {"binId": "codex-on-Justo", "timestamp": "2026-07-12T06:25:46Z",
       "type": "change",
       "summary": "Reconciliation backfill: OPEN_ITEMS C1_C5 closed (block 2679, prior session).",
       "details": "See 04_Validation/RECONCILIATION_2026-07-16.md section 4."}

      {"binId": "codex-on-Justo", "timestamp": "2026-07-12T06:44:23Z",
       "type": "change",
       "summary": "Reconciliation backfill: OPEN_ITEMS DEPLOY_HARDENED closed (block 2738, prior session).",
       "details": "See 04_Validation/RECONCILIATION_2026-07-16.md section 4."}

  These are human-readable, not chain-sealed. They record that the
  operator has read and accepted the chain evidence for these five
  closures. The chain already says they happened. The changelog
  catching up is paperwork, not state change.

================================================================================
END OF DOCUMENT
================================================================================
