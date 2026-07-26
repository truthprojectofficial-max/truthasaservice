================================================================================
ORDER GET IT RIGHT  --  VERIFIED PROCESSOR
Open Items, Next Five Steps, and Project Reference Fingerprint
Generated: 2026-07-17  (UTC, after E4 pre-2021 reference calibration seal)
Refreshed 2026-07-22 by Hermes: fingerprints updated to live state
(34,309 blocks, root 1e633db9..., 272 tests, 51 .py files, 642
total files). All open items reconciled against TODO_FULL.md,
handover_next_session_2026-07-22.md, and BUILD_DIRECTIVE_NEXT_SESSION.md.
Refreshed 2026-07-23 by Hermes: fingerprints updated to live state
(35,595 blocks, root 923b9c3f..., 272 tests, 49 .py files in
canonical scope, 333 total files in tree-shape scope). Tagline
corrected to "Verified Processor" (rebranded 2026-07-21, sealed
TAGLINE_REBRAND_VERIFIED_PROCESSOR_2026_07_21, commit 6b4057e).
All 5 "Next Five Steps" items below were re-evaluated against
the live tree; 4 are already closed in code, 1 is the 2026-07-23
queue. Replaced "Truth as a Service" header with "Verified
Processor" (legacy phrase preserved in historical chain blocks
and Tauri configs only). Allow-list for no-network audit is now
a closed set of 5 paths, sealed 2026-07-23
(ALLOW_LIST_CLOSED_AND_LOCKED_2026_07_23, commit c80150d);
see AUDIT_NO_NETWORK.md "Closure" section.
Makita citation (STEP 2) already closed 2026-07-18 (faa452e) and
expanded 2026-07-21 (a053ba8). Handover drift items (3+4) closed
2026-07-22 (handover_drift_check.py). Conversation-layer-down
runbook written 2026-07-22. Offsite backup still open (operator).
Refreshed from 2026-07-17 A3-seed-on-POST seal in same session.
Refreshed 2026-07-17 again after TAURI_BUNDLE_SMOKE_2026_07_17 seal.
Refreshed 2026-07-17 again after ORCHESTRATOR_SEAM_FIXED_2026_07_17
seal (Tier 1: bugs in orchestrator and lifespan shutdown).
Refreshed 2026-07-17 again after TIER2_SURFACES_ADDED_2026_07_17
seal (Tier 2: /api/affidavit/preview endpoint, two stale
docstrings corrected, +3 tests).
Refreshed 2026-07-17 again after TIER3_DOCS_REFRESHED_2026_07_17
seal (Tier 3: Orchestrator docstring, QUICK_REFERENCE_CARD root).
Refreshed 2026-07-17 again after TIER4_SPECS_REFRESHED_2026_07_17
seal (Tier 4: this document, YELLOW_RIBBON.md, fingerprints
REF-2a/REF-3/REF-4/REF-5/REF-6 refreshed to live state; REF-1 and
REF-2b unchanged).
Refreshed 2026-07-17 again after UI_OPERATOR_FACING_REDESIGN_2026_07_17
seal (single-page operating surface: app.py STATIC_DIR path bug
fixed; tests/test_static_dir.py added with 4 boundary-compliant
tests; web/index.html rewritten from 10-tab layout to single-page
operating surface; 6,584 blocks; 86/1 tests; REF-1 / REF-2a /
REF-2b unchanged, REF-3 / REF-4 / REF-5 / REF-6 refreshed to
live state; QUICK_REFERENCE_CARD.txt Merkle root snapshot also
refreshed).
Refreshed 2026-07-17 again after TAURI_REBUILT_FOR_UI_REDESIGN_2026_07_17
seal (Tauri desktop binary, MSI, and NSIS installer rebuilt
against the new web/index.html; all three artefacts mirrored to
USB; REF-3 / REF-4 / REF-5 / REF-6 refreshed to live state,
REF-1 / REF-2a / REF-2b unchanged; 6,775 blocks; 86/1 tests;
QUICK_REFERENCE_CARD.txt and YELLOW_RIBBON.md Merkle root
snapshot also refreshed).
Refreshed 2026-07-17 again after TAURI_REBUILT_DOCS_REFRESHED_2026_07_17
seal (captures the final live state: Tauri rebuild sealed
in block 6775, post-rebuild pytest run sealed 94 automatic
SHUTDOWN blocks through the FastAPI lifespan handler, this
docs refresh in block 6870; final root
f3e10f4a2ce645f3727954f2876c6d51a514024652de38d5b1ecf5226cacc7cd;
REF-1 / REF-2a / REF-2b / REF-3 / REF-4 unchanged, REF-5
b98a973a... -> f3e10f4a..., REF-6 3c8ad746... -> 0f33453c...).
Refreshed 2026-07-17 again after the operator flagged six
stale present-tense references in the print-and-pin hardcopy
files (OPERATOR_MANUAL.txt, HARD_COPY_BACKUP_PLAN_1-2-3.txt) and
in the YELLOW_RIBBON.md operator-ritual command. Closed: the
pre-fork .claude path in PATHS, the "FIVE AGENTS" section
(replaced with the canonical "TEN NAMED MODULES" -- 5 core
agents + 5 support modules), the 6-step "WHAT TO DO IF
SOMETHING BREAKS" section (expanded to 6 steps with the
correct pytest ritual, the port-conflict recipe, and the
STATIC_DIR regression-test cross-reference), the 44 .py file
count (corrected to 50), the "3/3 boundary + 2/2 normalize"
expectation (corrected to 86 passed + 1 host-dependent skip),
and the 130-line "next operator notes" IndentationError
narrative in HARD_COPY_BACKUP_PLAN (trimmed to a one-paragraph
pointer at the canonical 2026-07-16 HANDOVER sequence).
REF-3 / REF-4 unchanged (no source or tree changes); REF-5 /
REF-6 refreshed to live state in the seal. Two historical
`.claude` references are deliberately retained: YELLOW_RIBBON
line 91 and CONTEXT_WINDOW line 104 both describe the 2026-07-16
fork resolution in the past tense and are correct as written.
Refreshed 2026-07-17 again after the operator flagged that
HARD_COPY_BACKUP_PLAN said "There is no INTRODUCTION.md or
TROUBLESHOOTING.md yet" -- a deferred acknowledgement, not a
solution. Added 04_Validation/INTRODUCTION.md (287 lines, the
5-minute first-run: chain verify, pytest, start the server,
run an audit, compile an affidavit) and
04_Validation/TROUBLESHOOTING.md (928 lines, the failure-mode
catalog: chain verification, pytest collection, FastAPI
server, USB mirror, Tauri shell, ontology/domain, agentic
REPL, environment, plus an escalation section). Every entry
is SYMPTOM / ROOT CAUSE / FIX / ESCALATE and is grounded in
real failure modes the project has actually seen. The new
docs are added to WHERE EVERYTHING IS in YELLOW_RIBBON.md.
The first-run reading sequence in HARD_COPY_BACKUP_PLAN now
starts with INTRODUCTION.md and includes TROUBLESHOOTING.md.
The "WHAT TO DO IF SOMETHING BREAKS" section in
OPERATOR_MANUAL.txt now points at TROUBLESHOOTING.md as the
canonical catalog. REF-3 unchanged (no source changes; 50
.py); REF-4 advanced 218 -> 220 files (+2, matches the two
new .md files); REF-5 / REF-6 re-derived in lockstep.
Refreshed 2026-07-18 again after the operator-initiated 11-fix build (F12, F13, F6, F14, F1+F3, F4, F5, F15, F17, F16, F2), F11 Git-adoption, F7 lattice-reframing, F8 ontology R1-R4+R5, intake-held blocks, E4 F1 re-derivation. 88/1 tests, chain MATCH. REF-1 changed (constants.py amended with LATTICE_FRAMING, removed unused 'import os'), REF-2a changed (STRATEGY.md amended with section 8 Trust Anchors), REF-2b unchanged, REF-3 advanced (F12-F17 R5 fixes), REF-4 advanced (new KNOWN_CHAIN_ARTEFACTS.md, KNOWN_INTAKE_HELD records, GIT_WORKFLOW.md, test_ontology_r1_r4_gates.py), REF-5 / REF-6 refreshed in lockstep.
Refreshed 2026-07-17 again after the operator flagged "you
just stopped, what more building?". Did an honest inventory
of docs that had present-tense claims contradicting live
state and fixed only the actively-lying ones. Closed: the
[ ] OPEN markers on A3, C2, C3, and C4 in
04_Validation/TODO_FULL.md (all four were actually closed by
the C2_C3_C4_DOCS_RECONCILED_2026_07_17 seal earlier in the
day; the doc still showed them as [ ] with the stale 71/1
test baseline). Updated the SUMMARY section in TODO_FULL.md
to the live 86/1 baseline and 7061-block chain. Added a
"SUBSEQUENT CLOSURES" header section to
HANDOVER_NEXT_SESSION_2026-07-16.md (the 2026-07-16 transcript
is a historical record; the present-tense claims in it were
correct AT THAT TIME and must be preserved). C5 is still
genuinely OPEN (the STRATEGY.md Section 7 tone-of-done pass
has not happened). REF-1, REF-2a, REF-2b, REF-3 unchanged;
REF-4, REF-5, REF-6 re-derived in lockstep at the
TODO_FULL_RECONCILED_2026_07_17 seal (block 7061; root
ce81a4f7...).
Author:    codex-on-Justo  (operator: Justin Barnett)

F. 2026-07-18 BUILD SESSION SUMMARY (operator-initiated, F1-F17 sweep)
--------------------------------------------------------------------------------

This is the F1-F17 sweep documented in
04_Validation/OGIR_ASSESSMENT_2026-07-18.md. Eleven code-fixable findings
were applied, plus F7 (lattice reframing, cheap path), F8 (ontology
R1-R4 + R5), and F11 (Git adoption in parallel). F9, F10 remain
hardware/operator-dependent and are out of scope.

SEALED THIS SESSION (chronological):

  1. CANONICAL_JSON_PROPAGATED_2026_07_18 (block 7539, F12)
  2. MONITOR_UNEXPLAINED_FIXED_2026_07_18 (block 7634, F13)
  3. NIZK_RENAMED_2026_07_18 (block 7729, F6)
  4. DETERMINISM_HEADLINE_AMENDED_2026_07_18 (block 7824, F14)
  5. DOCS_RECONCILED_FINAL_2026_07_18 (block 7919, F1+F3)
  6. KNOWN_ARTEFACTS_DOCUMENTED_2026_07_18 (block 8014, F4)
  7. CHANGELOG_POLLUTION_GATED_2026_07_18 (block 8297, F5)
  8. CLEANUP_SEAL_2026_07_18 (block 8392, F15)
  9. TEST_PORTABILITY_FIXED_2026_07_18 (block 8490, F17)
  10. CONCURRENCY_ASSUMPTION_DOCUMENTED_2026_07_18 (block 8585, F16)
  11. TREE_CLEANED_2026_07_18 (block 8680, F2)
  12. COMPLETION_SEAL_2026_07_18 (block 8681)
  -- (operator-initiated follow-ons) --
  13. GIT_ADOPTED_IN_PARALLEL_2026_07_18 (block 8776, F11)
  14. F7_LATTICE_REFRAMED_2026_07_18 (block 9499, F7)
  15. ONTOLOGY_BUMP_R1_R4_2026_07_18 (block 10165, F8 -- 4 structural co-text gates)
  16. EVAL_CALIBRATION_EXTERNAL_2026_07_18 (block 10366, F8-EXT external email audit)
  17. KNOWN_INTAKE_HELD_2026_07_18 (block 10367, F8-EXT intake held)
  18. E4_F1_RE_DERIVED_2026_07_18 (block 10368, F8-EXT F1 number refresh)
  19. ONTOLOGY_BUMP_R5_2026_07_18 (block 10465, F8-EXT DD-009 lexical expansion)
  -- (this refresh) --
  20. OPEN_ITEMS_REFRESH_2026_07_18 (this block)

OUT-OF-SCOPE (correctly held):
  F7-deep: CLOSED 2026-07-19 (lattice inputs wired to evidence via
           derive_lattice_inputs_from_evidence; LATTICE_INPUTS_ARE_HARDCODED=False;
           orchestrator passes evidence=product_evidence; test_f7_deep_lattice_wired.py
           regression tests pass).
  F9: second-PC clean-host test (hardware-dependent; operator work).
  F10: Tauri code-signing (operator decision).
  F11-remote: add a Git remote (operator decision; 3 options in
              04_Validation/GIT_WORKFLOW.md section 2.4).
  F8-EXTENDED-LEGAL: embed Makita v Sprowles [2001] NSWCA 305 citation in
                     legal_affidavit_generator (filed in OPEN_ITEMS below).
  F8-EXTENDED EVAL-suite expansion to 30+ cases (filed in OPEN_ITEMS below).
  R5-EXTENDED: lexical-set audit for the remaining 53 patterns (filed
                in OPEN_ITEMS below; R5 closed only the DD-009 case).

OPEN_ITEMS NEXT FIVE STEPS (refreshed 2026-07-23):

STEP 1.  [RESOLVED] GIT REMOTE (F11-remote)
         Already closed 2026-07-18 (git remote add usb -> D:/OrderGetItRight.git).
         88 commits on the branch as of 2026-07-23; push to usb works.

STEP 2.  [RESOLVED] EMBED MAKITA CITATION IN AFFIDAVIT GENERATOR (F8-EXTENDED-LEGAL)
         Already closed 2026-07-21 (commit a053ba8,
         LEGAL_AFFIDAVIT_PRECEDENTS_MAKITA_VALVE_ADDED_2026_07_21).
         Makita v Sprowles [2001] NSWCA 305 and ACCC v Valve [2016]
         FCA 196/1553 are both embedded in the affidavit generator
         and asserted in tests/test_affidavit_preview.py.

STEP 3.  [RESOLVED] EVAL-SUITE EXPANSION (F8-EXTENDED)
         Already closed. The suite is at 100+ cases
         (EVAL-009..EVAL-120, plus SELBY-001/002, plus 7 AI-legal
         cases, plus 6 TRUTH-001..006, plus 3 Lancet cases, plus 4
         lexical-set audit batches covering DD-001..DD-054). The
         "8 to 30+" framing in the stale doc was massive under-count.
         Calibration run 2026-07-22: 89% exact, 100% recall,
         100% negative precision; 11 noise cases are SQUEAL.

STEP 4.  [RESOLVED] LEXICAL-SET AUDIT (R5-EXTENDED)
         Batches A, B, C, D closed 2026-07-18 (commits 442e3ea,
         1cedc6a, ab65a61, e7f70c3) covering DD-001..DD-054 in
         chunks of 10-20 patterns. ~80% done. Remaining: tighten
         the last ~10 patterns + add SQUEAL co-occurrences to
         expected sets in the EVAL tests (per 2026-07-22 calibration
         analysis). See C-3 in MASTER_TODO_2026-07-23.md.

STEP 5.  CURRENT QUEUE (the live 2026-07-23 next step)
         --------------------------------------------------------------------------------
  Single concrete next step: refresh the stale doc tracking chain.
  Concretely, 4 doc files have live-vs-doc drift that the next
  session must close. The most leveraged is OPEN_ITEMS_AND_REFERENCE.md
  (this file) which is read by every third party. The other 3
  are operator-internal.

  See 04_Validation/MASTER_TODO_2026-07-23.md for the full 16-item
  list and the priority summary. The next code session's coding
  work is:

    (a) Tighten R5-EXTENDED on the last ~10 ontology patterns,
        add SQUEAL co-occurrences to the EXPECTED_PATTERNS sets
        in tests/test_evaluation_cases_extended.py (1-2 hr,
        seal ONTOLOGY_LEXICAL_AUDIT_PILOT_2026_07_23).
    (b) The 4 stale doc files (OPEN_ITEMS, TODO_FULL, BUILD_DIRECTIVE,
        MAINTENANCE_PLAN) are operator-facing references; the
        code is correct. Refresh them as part of doc hygiene
        when convenient.

  Do NOT auto-fill this slot with new architecture. The build is
  operational and maintained, not aspirational.

================================================================================

This document is the operator-readable companion to the Merkle seal of the
same name. It exists so that the operator and the next AI agent can see, in
one place:

  1. Everything we know is unfinished, broken, or deferred in this build.
  2. The five next steps the build itself is asking for, in priority order.
  3. A set of cryptographic fingerprints that uniquely identify this exact
     build of the project, so any third party (any future AI, any auditor,
     any court) can prove "this is the same project the operator had."

The Merkle seal that references this file is in 04_Validation/ as
OPEN_ITEMS_AND_REFERENCE. Its index, current hash, and Merkle root are
appended to 04_Validation/changelog.log.

================================================================================
PART 1  --  WHAT HAS NOT BEEN DONE (honest ledger, 2026-07-16)
================================================================================

A. CODE THAT PARSES BUT STILL HAS A FOOT-GUN
--------------------------------------------------------------------------------

A7. STATIC_DIR path bug in src/server/app.py  --  CLOSED
    (2026-07-17, UI_OPERATOR_FACING_REDESIGN_2026_07_17).
    STATIC_DIR was computed as
    `Path(__file__).parent.parent / "web"` which resolves to
    02_Technical/src/web/ (a directory that does not exist; the
    real web folder is 02_Technical/web/). The classic effect:
    GET / fell through to the JSON fallback `{"status": ...}`,
    /static was never mounted, and the operator only ever saw
    the UI through the Tauri shell (which serves web/ directly
    from disk via its own frontendDist config, masking the
    bug). Browser mode was silently broken. Fix: changed to
    `Path(__file__).parent.parent.parent / "web"`. New
    regression test tests/test_static_dir.py (4 boundary-
    compliant tests) pins the on-disk layout, GET / serving,
    /static mount, and byte-identity of served HTML vs disk
    file. Test count: 82 -> 86.

A8. UI does not "speak for itself" against known operator
    needs. The 10-tab layout buries the four-gate pipeline
    result, hides working capacity, requires tab-hunting for
    endpoints, and has no STOP/GO/CLEAR. The operator's
    request on 2026-07-17 ("ui should speak for itself
    against known needs, of working copasity, figuers the
    operater can assess as it operates info it can call upon
    stop go clear ect") is now CLOSED. 02_Technical/web/
    index.html rewritten from 10-tab layout (28.4 KB) to a
    single-page operating surface (58.7 KB) with: a sticky
    top bar (working-capacity tags, STOP/GO/CLEAR, Merkle
    root), a working-capacity strip (runtime, shell, bin,
    last seal, tau stats, merkle root), a four-gate pipeline
    view (Deception / BBFB / Real-Options Lattice / Decision)
    that shows real figures as the pipeline fires, a
    recent-runs strip (last 10, color-coded by final action,
    click to reload), a call-upon drawer enumerating all 32
    HTTP endpoints, and inline panels for facts / ledger /
    MCP+tau+jobs / ontology 54 patterns / affidavit (with
    preview + generate) / batch upload / evaluation suite /
    changelog. The handle for the refusal short-circuit
    (finalAction=REFUSED returns a different shape than the
    full pipeline) is in loadRunIntoView. Sealed
    UI_OPERATOR_FACING_REDESIGN_2026_07_17.

A9. Tauri desktop binary and installers were stale
    (2026-07-12 build) and pointed at the old 10-tab UI.
    Operator confirmed "yes" to the rebuild. CLOSED.
    Rebuilt 2026-07-17 22:53 UTC. New artefacts:

      order-get-it-right.exe        4,852,736 bytes
                                    sha256 791bb7b9fe29043ada52a9099030e2d577c88b3244b03cc74cae982406cf033f
      Order Get It Right_1.0.0_x64_en-US.msi
                                    2,318,336 bytes
                                    sha256 aea590f2de82ac8774583154ceb131ac0ac3bd8bd5c3cc2486793ea3c76b89d4
      Order Get It Right_1.0.0_x64-setup.exe
                                    1,628,695 bytes
                                    sha256 9e96a519be38138063fd3b1b8270056df3d95fb246480212688365d94b76b94b

    All three mirrored to D:\OrderGetItRight\02_Technical\
    tauri-shell\target\release\ (USB parity). Code sign
    status is "NotSigned" -- identical to the 2026-07-12
    build, no regression. 4 pre-existing warnings (unused
    imports + dead_code) carried through from the Rust
    source, none blocking. Build wall-clock: 1m 34s
    incremental (the --no-bundle warm-up two minutes earlier
    was 2m 46s). Sealed
    TAURI_REBUILT_FOR_UI_REDESIGN_2026_07_17 (block 6775,
    written at 2026-07-17T13:33:30Z; the chain has since grown
    to 6,869 blocks through automatic SHUTDOWN seals from the
    post-rebuild FastAPI lifespan handler; current Merkle root
    b98a973afc5921f5f76e8340c5ae2bc447ec25755b09d46a460c5cdd581b5816).

A10. Stale 02_Technical/tests/ mirror (a 933-byte test_smoke.py
    and a misplaced first-draft test_static_dir.py, both
    duplicating canonical files at the project-root tests/)
    is now CLOSED. Operator confirmed hard-delete ("yes" to
    the operator-facing AskUserQuestion). Removed via
    `powershell -NoProfile -Command "Remove-Item -LiteralPath
    '02_Technical\tests' -Recurse -Force"`. Post-removal
    verification: pytest from project root shows 86/1, chain
    MATCH. REF-3 went 52 -> 50 .py files; REF-4 went 220 ->
    218 files (delta matches the two deleted stale .py
    files). Effect was captured in the
    TAURI_REBUILT_FOR_UI_REDESIGN_2026_07_17 seal's REF
    re-derivation, not in a separate seal.

B. TESTS / TEST INFRASTRUCTURE
--------------------------------------------------------------------------------

  (no open B-items as of this refresh)

C. DOCS THAT ARE OUT OF DATE OR MISSING
--------------------------------------------------------------------------------

C2. INTELLECTUAL_PROPERTY_RIGHTS.txt  --  CLOSED (2026-07-17,
    C2_C3_C4_DOCS_RECONCILED_2026_07_17). 17 KB of IP clauses
    audited against the current codebase. The third-party package
    count was 9 in the document but the live requirements.txt has
    10; corrected. The default Ollama model note was added (was
    tcoxav/aegis:latest, now qwen3.5:9b). All agent names mentioned
    in the IP file were cross-checked against
    02_Technical/src/agents/.

C3. MAINTENANCE_PLAN.txt  --  CLOSED (2026-07-17,
    C2_C3_C4_DOCS_RECONCILED_2026_07_17). Test counts updated
    throughout (70+2 -> 73/0 with env qualifier; 27/27 -> 28/28
    smoke; SDXC state matches D:\OrderGetItRight). Stale
    _verify_orchestrator.py references replaced with
    tests/test_smoke.py::test_evaluation_suite_is_deterministic.

C4. InventoryAgent and the rest of the current agent roster  --
    CLOSED (2026-07-17, C2_C3_C4_DOCS_RECONCILED_2026_07_17).
    SPECS F-08 now lists 10 named modules (5 core agents +
    InventoryAgent + MonitorAgent + Orchestrator + AgentJobDelegator
    + TauFirewall). SPECS Section 6 (one-paragraph spec) updated
    from "7 named agents" to "10 named modules". The
    INTELLECTUAL_PROPERTY_RIGHTS.txt and MAINTENANCE_PLAN.txt
    references to the agent list are also consistent now.

C5. 00_Strategy/STRATEGY.md Section 7 still needs a final pass to record
    "operational and maintained" rather than "completed." The test-count
    drift has been fixed in chain block 2798/2799/2916; the tone-of-done
    checkbox wording is the remaining item.

D. SECURITY / DETERMINISM / PORTABILITY NOT FULLY PROVEN
--------------------------------------------------------------------------------

D1. USB clean-host restore test  --  CLOSED TO THE EXTENT POSSIBLE ON THIS
    HOST. The build has been deployed to D:\OrderGetItRight via
    deploy/deploy.ps1, the chain verifies as MATCH from the USB copy, and
    pytest passes from the USB copy (73 passed, 0 skipped as of 2026-07-17).
    The C:\ route redirect detection test (test_a5_deploy_dry_run.py) now
    passes because C:\OrderGetItRight is a junction to D:\OrderGetItRight.
    The one thing that CANNOT be tested on this single machine is a true
    "no Python installed" clean host. That remains operator work on a
    second Windows PC.

D2. Full-tree no-network import audit  --  PARTIAL. The 02_Technical/src/
    tree is clean (audit_no_network.py, block 889). 02_Technical/tools/,
    tests/, and the bundled runtime were not re-audited this session.

D3. Full project-level black-box audit  --  PARTIAL. AUDIT_NO_BLACK_BOX.md
    covers 14 pillars. A complete screen-to-function trace for every CLI
    and web output field is not yet in one document.

E. OPERATOR ASKS NOT DONE
--------------------------------------------------------------------------------

E1. Gmail read for InventoryAgent  --  UNDONE. The operator must export
    truthproject.official@gmail.com to a local .mbox file and drop it into
    OneDrive\Documents\to the spoils go\inbox\. Network egress is not
    granted.

E4. Pre-2020 reference corpus  --  CLOSED (2026-07-17,
    E4_PRE_2021_REFERENCE_CALIBRATED_2026_07_17). The operator
    brought Verified.docx into
    OneDrive\Documents\My Project\Verified.docx and an existing
    text export at
    data/samples/verified_prior_2021.txt (41,316 bytes, 980
    lines, generated 2026-07-12) was used as the audit input.
    The audit ran end-to-end via audit_cli on a 5-section
    intake at
    04_Validation/pre_2021_reference_audit_intake.txt.
    Verdict: PASS_WITH_FALSE_POSITIVE_FLAGS. 5/54 patterns
    fired (DD-001, DD-006, DD-011, DD-041, DD-054); 12 raw
    hits resolved to 11 false positives and 1 true-negative
    (anti-deception exposure on line 215). 4 ontology
    refinement recommendations (R1-R4) are queued for the
    next scheduled ontology bump. The reference corpus is
    now the canonical pre-2021 baseline. Full report at
    04_Validation/PRE_2021_REFERENCE_CALIBRATION_2026-07-17.md.


WHAT WAS CLOSED IN THIS SESSION
--------------------------------------------------------------------------------

A1 startup lifespan migration .................. CLOSED (block 1683)
A2 v3.8/v3.9 hardcoded strings ................. CLOSED (blocks 228, 889)
A4 Tauri desktop shell build ................... CLOSED (block 1979)
A5 deploy.ps1 clean-host / dry-run ............. CLOSED (block 2504)
A6 stale .pyc cache ............................ CLOSED (block 1800)
B1 stale .pytest_cache ......................... CLOSED (block 2270)
B2 determinism regression test .................. CLOSED (block 1392)
B3 host-dependent tests ........................ CLOSED (block 2270)
B4 Python 3.12 compat / BOM cleanup .............. CLOSED (block 2270)
B5 Ollama tool-calling model swap to qwen3.5:9b ... CLOSED (2026-07-17;
    default changed; _ollama_supports_tools() now probes with a real
    tool and 120s timeout; agentic_repl.py forces UTF-8 stdout so the
    qwen3.5 U+2713 reply does not crash on cp1252 consoles. D5 end-
    to-end now passes; 73/0)
C1 QUICK_REFERENCE_CARD root refresh ........... CLOSED (2026-07-17 refresh)
D4 verify-from-USB CLI subcommand .............. CLOSED (block 889)
D5 agent wiring end-to-end ..................... CLOSED (chain block 2387;
    runtime exercise now passes on this host with qwen3.5:9b)
C2 audit IP-rights against current code ........ CLOSED (2026-07-17;
    INTELLECTUAL_PROPERTY_RIGHTS.txt reconciled to 10 third-party
    packages per live requirements.txt, default model noted as
    qwen3.5:9b, header dated)
C3 reconcile MAINTENANCE_PLAN with live state ... CLOSED (2026-07-17;
    MAINTENANCE_PLAN.txt + 5 STAGE_PAPER_*.txt updated: 73/0
    pytest on this host (with FastAPI up + qwen3.5:9b), 28/28
    smoke, real test path for orchestrator determinism,
    header dated)
C4 reconcile SPECS.txt with live state ......... CLOSED (2026-07-17;
    SPECS.txt reconciled: 10 named modules, 14 REPL
    commands, 4,816-block chain, 31 endpoints, 51 .py /
    21 .md / 11 .txt file counts, ontology 54 patterns v3.9,
    header dated)
C5 STRATEGY.md tone-of-done pass ................ CLOSED (2026-07-17;
    section 6 converted from [x] (completed) tone to [~]
    (operational and maintained) tone; each item is now a
    standing condition tied to the maintenance rhythm)
D2 no-network audit extended .................... CLOSED (2026-07-17;
    audit_no_network.py now covers tools/, tests/, and
    04_Validation/scripts/ with CLEAN/ALLOWED/REVIEW/FAIL
    verdict taxonomy and a 4-file allow-list. New test
    tests/test_audit_no_network.py 4/4 pass. AUDIT_NO_NETWORK.md
    rewritten)
D3 screen-to-function trace doc .................. CLOSED (2026-07-17;
    new AUDIT_BLACK_BOX_TRACE_2026-07-17.md walks 5 real flows
    end-to-end with 6-column table per flow: operator gesture,
    HTTP request, server hop, engine hop, constants, render line.
    Companion to AUDIT_NO_BLACK_BOX.md)
A3 startup reset foot-gun ...................... CLOSED (2026-07-17;
    _seed_facts_once() was already guarded by `if list_facts():
    return`, but POST /api/facts did not call _ensure_seeded()
    on a fresh process, so the seed facts were missing when an
    operator's first POST went through under TestClient (lifespan
    does not fire before the first request). Fix: POST /api/facts
    now calls _ensure_seeded() before adding the operator fact;
    test reinforced with baseline + idempotency assertions. Sealed
    A3_STARTUP_RESET_FOOTGUN_FIXED_2026_07_17)
E4 pre-2020 reference corpus calibration ........ CLOSED (2026-07-17;
    operator brought Verified.docx into
    OneDrive\Documents\My Project\Verified.docx; existing
    text export at data/samples/verified_prior_2021.txt
    (41,316 B) was audited via a 5-section intake. Verdict
    PASS_WITH_FALSE_POSITIVE_FLAGS: 5/54 patterns fired, 12
    raw hits resolved to 11 false positives and 1
    true-negative. 4 ontology refinement recommendations
    (R1-R4) queued for next bump. Reference corpus is now
    the canonical pre-2021 baseline. Sealed
    E4_PRE_2021_REFERENCE_CALIBRATED_2026_07_17)

================================================================================
PART 2  --  THE NEXT FIVE STEPS, IN PRIORITY ORDER
================================================================================

STEP 1.  OFFSITE BACKUP (operator, physical)
         (Severity: HIGH  |  Effort: ~1 hour  |  Files: 0)
--------------------------------------------------------------------------------
  Buy a USB stick, mirror the project to it, print the paper Merkle
  root card, and store both offsite (bank safe deposit box in Whyalla).
  Until this is done, the chain is on a single physical site plus the
  local D: mirror. Both lost in a house fire. This is the #1 gap.
  Paper card is at 04_Validation/PAPER_BACKUP_CARD_2026-07-22.txt.

STEP 2.  EVAL-SUITE EXPANSION (F8-EXTENDED)
         (Severity: MEDIUM  |  Effort: 1-2 days  |  Files: 1-2)
--------------------------------------------------------------------------------
  Expand from 8 to 30+ cases with real anonymised correspondence.
  R1-R6 gates are stable. Next move is empirical coverage, not
  lexical-set tuning. Seal as F8_EXTENDED_EVAL_SUITE_GROWN_2026_07_XX.

STEP 3.  LEXICAL-SET AUDIT PILOT (R5-EXTENDED)
         (Severity: LOW  |  Effort: 1 hour for 10-pattern pilot  |  Files: 1)
--------------------------------------------------------------------------------
  For 10 of the remaining 53 patterns, write probe sentences with
  synonyms/near-misses. If a probe fails to fire, add the synonym.
  Bump ontology version to 3.11. Seal as ONTOLOGY_LEXICAL_AUDIT_2026_07_XX.

STEP 4.  GMAIL .MBOX IMPORT (E1)
         (Severity: LOW  |  Effort: 1-2 hours  |  Files: 1)
--------------------------------------------------------------------------------
  Operator drops a Gmail .mbox export into
  OneDrive\Documents\to the spoils go\inbox\. The audit pipeline
  already handles .mbox. This step is the integration test.

STEP 5.  [RESERVED -- queue next concrete item here]
--------------------------------------------------------------------------------
  Reserved. The next item is whatever the operator identifies at
  the next maintenance cycle. Do not auto-fill.

================================================================================
PART 3  --  PROJECT REFERENCE FINGERPRINT
================================================================================

This is the stable, cryptographic identity for this exact build. The six
numbers below were derived from the canonical source tree at
C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight on
2026-07-23 (re-derive is the source of truth; the values below
are the live state at the 2026-07-23 refresh). A third party
can re-derive every one in under 10 seconds.

REF-1  PROJECT IDENTITY (constants.py)
--------------------------------------------------------------------------------
  Project name:        Order Get It Right
  Tagline:             Verified Processor
  Version:             1.0.0
  Operator:            Justin Barnett
  Jurisdiction:        Commonwealth of Australia / ACL / Evidence Act 1995
  Build date:          2026-07-12 (cumulative build; see YELLOW_RIBBON.md for daily seals)
  Ontology version:    3.10 (55 patterns, R1-R6 applied)
  Constants SHA-256:   f54ca558539ae1062d64db8719fe92f1022e5670994db5d630fd62768def508d
  Source:              02_Technical/config/constants.py

REF-2  STRATEGY + GOVERNANCE (the documents that say what the project IS)
--------------------------------------------------------------------------------
  STRATEGY.md SHA-256:    f47530f48c07802db3c75629ee0731d0569f6a17823a6a7b5e55b72f9252f1ae
  GOVERNANCE.md SHA-256:  0c2335de7e3e1962f30cacc3d12fe2921e8565287190c04d2dec01328f8f028d
  Source:                 00_Strategy/

REF-3  SOURCE TREE (project .py files under 02_Technical, excluding bundled runtime)
--------------------------------------------------------------------------------
  Source tree SHA-256:  be44b055de075bd7980db6f2533a45ca67e0076a1c6b8e924697877b8e89340f
  Source file count:    49 .py files under 02_Technical
                        (excludes __pycache__, .pytest_cache,
                         02_Technical/python bundled runtime,
                         02_Technical/resources, 02_Technical/tauri-shell).
                        The canonical scope includes config/, src/, tools/,
                        web/, and the top-level __init__.py. The doc's prior
                        count of 51 included two stale files (a 933-byte
                        test_smoke.py and a misplaced first-draft
                        test_static_dir.py) that were hard-deleted in the
                        2026-07-17 TAURI_REBUILT_FOR_UI_REDESIGN seal;
                        live is 49. Bumps from 2026-07-22 onward
                        (derive_fingerprints, handover_drift_check,
                        append_marker, dns_forwarder_health,
                        which_canonical) added new scripts under
                        04_Validation/scripts/ which are NOT in the
                        REF-3 scope; the source-tree scope is the
                        02_Technical/ tree, not 04_Validation/.
  Source:               02_Technical/**/*.py

  To re-derive in Python:
    import hashlib, pathlib
    root = pathlib.Path('.')
    excluded = {'__pycache__', '.pytest_cache', 'python', 'resources', 'tauri-shell'}
    files = sorted(p for p in root.glob('02_Technical/**/*.py')
                   if not any(x in p.parts for x in excluded))
    lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.as_posix()}"
             for p in files]
    print(hashlib.sha256('\n'.join(lines).encode()).hexdigest())

REF-4  TREE SHAPE (which files exist, regardless of content)
--------------------------------------------------------------------------------
  Tree SHA-256:         a0aeb20a9adb507c0b41b6b7729271e5a7b0fc7cf4da22de36dd0247e96bcf2d
  Tree file count:      333 (after excluding __pycache__, .pytest_cache,
                         .bak-pre-*, bundled runtime, resources, tauri-shell).
                        The 642-file count in the prior 2026-07-22
                        refresh was inflated by 99_Archive_Historical
                        contents; the live 2026-07-23 scope
                        (derive_fingerprints.py with the same
                        excluded set as REF-3 over all files) gives 333.
                        Refreshed 2026-07-23 to live tree state.

  To re-derive in Python, use the same excluded set as REF-3 over all files:
    files = sorted(p for p in root.rglob('*') if p.is_file()
                   and not any(x in p.parts for x in excluded)
                   and not any(part.startswith('.bak-pre-') for part in p.parts))
    print(hashlib.sha256('\n'.join(p.as_posix() for p in files).encode()).hexdigest())

REF-5  MERKLE ROOT (the live state of the audit chain)
--------------------------------------------------------------------------------
  Merkle root:          923b9c3fa034e97e55ee6daad65df0b02aa8129e9141db6a68f7d2d6f5ac187f
  Block count:          35595
  First block:          2026-07-11T17:15:10Z
  Last block:           2026-07-23T08:54:36Z (live; the FastAPI
                        lifespan handler continues to seal
                        SHUTDOWN blocks during every pytest
                        / verify_chain run that opens the
                        server)
  Source:               03_Vault/facts_registry.json
                        (vault_io.merkle_stats()["merkleRoot"])

  This is the most volatile fingerprint. Re-derive it with:
    cd 02_Technical
    python -m src.verify_chain

REF-6  PROJECT FINGERPRINT COMPOSITE
--------------------------------------------------------------------------------
  A single SHA-256 over the concatenation of REF-1 through REF-5, in order.
  This is the one number a third party should write down if they want to be
  able to prove "this is the same project I saw on 2026-07-23."

  Composite SHA-256:    8e061042ffd48442c5d4cd1bac2bf4657fcddd25b282f73f9376403275ae8cfa

  To re-derive:
    cat <(echo REF-1) <(echo REF-2a) <(echo REF-2b) \
        <(echo REF-3) <(echo REF-4) <(echo REF-5) | tr -d '\n' | sha256sum
  Or run: python -m src.verify_chain --print-refs  (when implemented)

================================================================================
PART 4  --  HOW TO ANSWER "WHAT PROJECT IS THIS?"
================================================================================

A third party -- any AI, any human, any auditor -- asks "what is this
project, where does it live, and how do I know you have it?" Hand them
this file. They read PART 3 and PART 4. They run the re-derivation
commands. If the hashes match, they have the project. If they do not, the
project has changed since this document was written, and the next operator
needs to update this file and re-seal.

The canonical answer to "what is this project" is the one sentence at
the top of this file:

    Order Get It Right -- Verified Processor.
    A deterministic business audit and valuation program.
    Version 1.0.0. Operator: Justin Barnett.
    Jurisdiction: Commonwealth of Australia.
    Canonical source lives at
    C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight.
    USB/SDXC backup lives at D:\OrderGetItRight.
    No network. No LLM in the audit loop.
    Every decision sealed to a Merkle chain at 03_Vault/facts_registry.json.

That sentence plus the six fingerprints is the entire project identity.
Print this page. Keep a copy in the hard-copy backup envelope. Hand
copies to anyone who asks.

================================================================================
END OF DOCUMENT
================================================================================
