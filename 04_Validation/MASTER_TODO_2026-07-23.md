================================================================================
ORDER GET IT RIGHT -- MASTER TODO (CONSOLIDATED)
Generated: 2026-07-23 by Hermes
Sources: OPEN_ITEMS_AND_REFERENCE.md, TODO_FULL.md,
         handover_next_session_2026-07-22.md, BUILD_DIRECTIVE_NEXT_SESSION.md,
         MASTER_TODO_2026-07-22.md, this session's audit + 5-doc scan
================================================================================

This is the ONE list. Every open item from every source, de-duplicated,
with current status. If an item is not here, it is closed or not real.

Refresh discipline: every session-end seal re-derives this from the 5
tracking docs. Each item here was either:
  (a) open in a 2026-07-22 or earlier source AND still open, OR
  (b) closed in a tracked event but the doc reference was not updated.

Each item below was verified against live source on 2026-07-23
(chain 35,366 blocks, root e2b38e70, 272 tests pass, 5-allow-list
closed-set policy applied).

Legend:
  [ ]    OPEN -- needs work
  [x]    CLOSED -- done and sealed
  [-]    DEFERRED/BLOCKED -- needs operator action or hardware
  !      HIGH severity
  ~      MEDIUM severity
  .      LOW severity

================================================================================
A. INFRASTRUCTURE / COMMS (operator, physical)
================================================================================

[A-COMMS-1] ! WideNet fixed-wireless feasibility inquiry
  Status:   [ ]  OPEN
  Source:   PROJECT TROUBLE COMMS.txt (from prior session)
  Action:   Send email to support@widenet.com.au. Draft is on file.
  Note:     Last status: operator tried calling + emailing, no response
            received as of 2026-07-22. Recommend: confirm last attempt
            date; if no reply in 7 days, move to FSG or other fixed-
            wireless ISP. Field Solutions Group is a parallel candidate
            not yet contacted.

[A-COMMS-2] ~ Telstra mobile broadband dongle
  Status:   [ ]  OPEN (operator purchase)
  Source:   MASTER_TODO 2026-07-22, COMMS_OPTIONS_WHYALLA_2026-07-22.md
  Note:     Telstra has best regional SA coverage. A third independent
            path is a real redundancy. ~$50-99 dongle + ~$30-50/mo SIM.

[A-COMMS-3] ~ NBN availability for 20 Loveday St
  Status:   [ ]  OPEN
  Source:   OPEN_ITEMS (operator check, nbnco.com.au)
  Note:     Online checker says "fibre ready" but this does NOT confirm
            a lead-in reaches the premises. Verify by calling NBN or
            asking the landlord. New builds in Whyalla Norrie may
            need landlord consent + lead-in construction.

[A-COMMS-4] ~ Field Solutions Group (fsg.com.au)
  Status:   [ ]  OPEN
  Source:   MASTER_TODO 2026-07-22
  Action:   Parallel inquiry to WideNet. FSG is a regional Australia
            fixed-wireless specialist.

[A-COMMS-5] . Adapter discipline (session hygiene rule)
  Status:   [-]  ONGOING (operator habit, not code)
  Source:   handover_next_session_2026-07-22.md item 2
  Note:     This is a session-hygiene rule, not a code change.
            Mitigated somewhat by Unbound on 127.0.0.1:53 -- the
            DNS resolver is now independent of which interface is up.

================================================================================
B. BACKUP / DISASTER RECOVERY (operator, physical)
================================================================================

[B-1] ! Offsite backup -- USB stick + paper card to fireproof offsite
  Status:   [ ]  OPEN (operator, ~1 hour at a Whyalla bank branch)
  Source:   OPEN_ITEMS, MASTER_TODO 2026-07-22
  Note:     1-2-3 backup plan: D: microSD mirror (DONE), paper
            backup card text file (DONE -- 04_Validation/PAPER_BACKUP_CARD_2026-07-22.txt
            with root 8bfc95bd... and 34,127 blocks; needs a new card
            at the live 35,366-block root), offsite physical (NOT DONE).
            Until B-1 is done, the chain is on a single physical site
            plus the local D: mirror.

[B-1.1] . Refresh paper backup card to live state
  Status:   [ ]  OPEN (operator, 2 minutes)
  Source:   This session's audit
  Action:   Re-run derive_fingerprints.py to update the paper card
            to root e2b38e70... / 35,366 blocks. Print new card.

[B-2] [x] Paper Merkle root card -- text file written
  Status:   CLOSED (2026-07-22)
  Note:     04_Validation/PAPER_BACKUP_CARD_2026-07-22.txt
            Root: 8bfc95bd...  Blocks: 34,127. (Stale; refresh to live.)

[B-3] [x] D: microSD git mirror -- working
  Status:   CLOSED (2026-07-22 verified)
  Note:     88 commits synced. git push usb works (verified end of session).

================================================================================
C. CODE / BUILD (developer, sealable)
================================================================================

[C-1] [x] Embed Makita v Sprowles citation in affidavit generator
  Status:   CLOSED (2026-07-21, commit a053ba8)
  Source:   OPEN_ITEMS step 2, BUILD_DIRECTIVE WP-1, TODO_FULL (stale)
  Note:     LEGAL_AFFIDAVIT_PRECEDENTS_MAKITA_VALVE_ADDED_2026_07_21
            embedded Makita v Sprowles [2001] NSWCA 305 and ACCC v Valve
            [2016] FCA 196/1553. Asserted in affidavit preview test.
            The OPEN_ITEMS, BUILD_DIRECTIVE, and TODO_FULL references
            to "Makita pending" are STALE DOCS, not pending work.

[C-2] ~ EVAL-suite expansion to 30+ cases
  Status:   [x]  CLOSED (already done; doc references stale)
  Source:   OPEN_ITEMS step 3, BUILD_DIRECTIVE WP-5, TODO_FULL (stale)
  Note:     Suite is at 100+ cases (EVAL-009..EVAL-120, plus
            SELBY-001/002, plus 7 AI-legal cases, plus 6 TRUTH-001..006,
            plus 3 Lancet EVAL-047/048, plus batches A-D lexical sets).
            272 tests pass. The "8 to 30+" claim in OPEN_ITEMS, BUILD_DIRECTIVE,
            and MASTER_TODO is massively stale (the doc references are
            from 2026-07-17; the expansion was done 2026-07-18-21).
            Action: nothing to build; update the doc references.

[C-3] . Lexical-set audit for remaining 53 patterns (R5-EXTENDED)
  Status:   [x]  PARTIALLY DONE (batches A-D done; full pilot pending)
  Source:   OPEN_ITEMS step 4, BUILD_DIRECTIVE WP-3, TODO_FULL (stale)
  Note:     Lexical-set audit batches A, B, C, D done 2026-07-18
            (commits 442e3ea, 1cedc6a, ab65a61, e7f70c3) covering
            DD-001..DD-054 in chunks of 10-20 patterns. The "remaining
            53 patterns" framing is stale; the audit is ~80% done.
            Outstanding: any patterns that still show false-negatives
            in the calibration analysis 2026-07-22.

[C-4] [x] F7-deep: wire lattice inputs to extracted evidence
  Status:   CLOSED (2026-07-19, commit 8c94edd)
  Source:   OPEN_ITEMS F7-EXTENDED, BUILD_DIRECTIVE WP-6, TODO_FULL (stale)
  Note:     F7_DEEP_LATTICE_WIRED_TO_EVIDENCE_2026_07_19: derive_lattice_inputs_from_evidence
            implemented; LATTICE_INPUTS_ARE_HARDCODED=False; Selby case
            now DEFER (463.9 vs 717.2) not GO (80.4 vs 23.8). The
            OPEN_ITEMS, BUILD_DIRECTIVE, and TODO_FULL references
            to "F7-deep deferred" are STALE DOCS.

[C-5] [x] C5: STRATEGY.md Section 7 tone-of-done pass
  Status:   CLOSED (2026-07-22, commit 85d690f, OPEN_ITEMS_AND_STRATEGY_REFRESHED_2026_07_22)
  Source:   TODO_FULL C5, OPEN_ITEMS
  Note:     "Operational and maintained" phrase verified PRESENT in
            00_Strategy/STRATEGY.md (14,070 bytes). Test count updated
            to 272/1. Doc references in TODO_FULL are stale.

[C-6] [x] ~ C1 (TODO_FULL): Makita citation (duplicate of C-1 above)
  Status:   CLOSED (2026-07-21, commit a053ba8)
  Note:     Same item, different doc. Both C-1 and C-6 close together.

[C-7] [x] C2, C3, C4 (TODO_FULL): IP file, maintenance plan, agents
  Status:   CLOSED (2026-07-17, C2_C3_C4_DOCS_RECONCILED_2026_07_17)
  Note:     Audit done. Live IP file lists 7 of 10 named modules
            (Form_Entry, Audit_Review, Lattice_Compute, Ledger_Seal,
            Affidavit, Monitor, InventoryAgent, MonitorAgent are
            present). The orchestrator, AgentJobDelegator, and
            TauFirewall are module-level Python classes, not separate
            "named modules" in the IP-rights sense; their import
            chains are documented. Not a gap.

[C-8] [x] D5: agent wiring end-to-end
  Status:   CLOSED (2026-07-19, test_d5_agentic_repl.py 4/4 + 5/5 pass)
  Source:   TODO_FULL D5
  Note:     agentic_repl.py + agentic_repl_tools.py exist and work.
            TODO_FULL doc reference is stale.

[C-9] [x] D2: no-network audit extended to tools/tests/scripts
  Status:   CLOSED (2026-07-17, audit_no_network.py)
  Source:   TODO_FULL D2, OPEN_ITEMS
  Note:     Audit covers 5 scopes: runtime (hard-fail), tools, tests,
            scripts, audit script itself. Now locked at 5-allow-list
            closed-set policy via tests/test_allow_list_closed.py
            (sealed 2026-07-23 in this session).

[C-10] [x] D4: verify-from-USB CLI subcommand
  Status:   CLOSED (2026-07-17, block 889)
  Source:   TODO_FULL D4

[C-11] [x] D1-TRUE (partial): single-host deploy validation
  Status:   CLOSED (2026-07-17, deploy.ps1 dry-run + real D: deploy)
  Source:   TODO_FULL D1, OPEN_ITEMS
  Note:     True clean-host on a SECOND Windows PC remains operator work
            (see E-4 below).

[C-12] [x] Ollama isolation contract
  Status:   CLOSED (2026-07-21, commit 75aede0, OLLAMA_ISOLATION_CONTRACT_LOCKED)
  Source:   OPEN_ITEMS
  Note:     Isolation test asserts Ollama code stays in tools/, runtime
            has no Ollama dependency. No regression since.

[C-13] [x] Tagline rebrand to "Verified Processor"
  Status:   CLOSED (2026-07-21, commit 6b4057e)
  Source:   OPEN_ITEMS
  Note:     Rebrand complete. Legacy tagline preserved in historical
            blocks. Regression test enforces it.

================================================================================
D. CHAIN / HYGIENE / PROCEDURE (developer, sealable)
================================================================================

[D-1] [x] Auto-handover on session-seal boundary
  Status:   CLOSED (2026-07-22, commit b90dd61)
  Source:   handover_next_session_2026-07-22.md item 3
  Note:     handover_drift_check.py exists. Detects drift, auto-writes
            the handover in place, seals SEALED_HANDOVER_<date> blocks.

[D-2] [x] Handover-drift invariant (refuse on drift)
  Status:   CLOSED (2026-07-22)
  Source:   handover item 4
  Note:     --refuse mode in handover_drift_check.py exists.

[D-3] [x] Conversation-layer-down runbook
  Status:   CLOSED (2026-07-22, RUNBOOK_CONVERSATION_LAYER_DOWN.md)
  Source:   handover item 5
  Note:     Doubles as internal comms book for multi-agent work.

[D-4] [x] Audit path works without LLM (doc)
  Status:   CLOSED (2026-07-22, RUNBOOK_CONVERSATION_LAYER_DOWN.md)
  Source:   handover item 5
  Note:     The runbook covers the PowerShell-only path. The audit
            path is air-gapped; the doc was the gap.

[D-5] ~ OPEN_ITEMS_AND_REFERENCE.md fingerprint refresh
  Status:   [ ]  OPEN
  Source:   This session's audit
  Action:   Update REF-1..REF-6 to live state. Current doc says
            34,309 blocks, root 1e633db9 (2026-07-22 stale snapshot).
            Live is 35,366 blocks, root e2b38e70. Also fix the
            "Truth as a Service" tagline in the next-5-steps section
            (it's already "Verified Processor" in constants.py since
            2026-07-21 rebrand).
  Effort:   30 minutes
  Seal:     OPEN_ITEMS_REFRESHED_2026_07_23

[D-6] [x] Allow-list closed-set policy lock
  Status:   CLOSED (2026-07-23, this session)
  Source:   Operator pushback 2026-07-22
  Note:     tests/test_allow_list_closed.py locks the 5-file
            allow-list in audit_no_network.py to a closed set.
            AUDIT_NO_NETWORK.md "Closure" section documents the
            amendment procedure. Any 6th entry requires a sealed
            ALLOW_LIST_AMENDED_<DATE> event + same-commit test
            update + doc update.

================================================================================
E. OPERATOR-SUPPLIED INPUTS (operator, not code)
================================================================================

[E-1] ~ Gmail .mbox export for InventoryAgent
  Status:   [ ]  OPEN (operator action)
  Source:   TODO_FULL E1, OPEN_ITEMS E1
  Action:   Export truthproject.official@gmail.com to .mbox.
            Drop into OneDrive\Documents\to the spoils go\inbox\.
  Note:     Network egress not granted. Operator must export.

[E-2] [x] Pre-2020 reference corpus (E4 in TODO_FULL)
  Status:   CLOSED (2026-07-17, E4_PRE_2021_REFERENCE_CALIBRATED_2026_07_17)
  Source:   TODO_FULL E4
  Note:     The pre-2021 corpus was calibrated with verified_prior_2021.txt
            at data/samples/. TODO_FULL doc reference is stale.

[E-3] [-] Tauri code-signing ($200-500/yr)
  Status:   [-]  BLOCKED (operator decision, cost)
  Source:   TODO_FULL F10, BUILD_DIRECTIVE
  Note:     Required for any distribution beyond the operator.
            tauri.conf.json.signing.example was added 2026-07-21 (a707faf).

[E-4] [-] D1-TRUE: second-PC clean-host restore test
  Status:   [-]  BLOCKED (needs second Windows PC)
  Source:   TODO_FULL D1, OPEN_ITEMS
  Action:   On a second Windows PC with no Python, copy from USB,
            run deploy.ps1, pytest, verify_chain. Record whether
            Merkle root matches.

[E-5] [x] OpenClaw assistant (E2 in TODO_FULL)
  Status:   DEAD (no such tool in live tree; doc reference obsolete)
  Source:   TODO_FULL E2
  Note:     No file matches "openclaw" or "open_claw" anywhere in
            the project tree. The TODO_FULL entry appears to be
            obsolete doc cruft from 2026-07-16.

[E-6] [x] via_app_data.py / rewrite.py (E3 in TODO_FULL)
  Status:   DEAD (no such files in live tree)
  Source:   TODO_FULL E3
  Note:     No file matches "via_app_data" or "rewrite.py" in the
            project tree. Obsolete doc cruft.

================================================================================
F. GEMINI GEM / AIDER SANDBOX (research artifacts)
================================================================================

[F-GEM-1] [x] Updated Gem spec written
  Status:   CLOSED (2026-07-22)
  Note:     04_Validation/GEM_SPEC_UPDATED_2026-07-22.md

[F-GEM-2] [x] Chain summary JSON generated (redacted)
  Status:   CLOSED (2026-07-22)
  Note:     04_Validation/CHAIN_SUMMARY_FOR_GEM_2026-07-22.json

[F-GEM-3] . Build the Gem in Google Gemini
  Status:   [ ]  OPEN (operator, ~5 min in Gemini UI)
  Source:   GEM_SPEC_UPDATED_2026-07-22.md
  Action:   1. gemini.google.com/gems -> Create
            2. Paste system instructions
            3. Upload 6 knowledge base files
            4. Run first setting prompt
            5. Run truncation check

================================================================================
G. DOCUMENTATION (developer, sealable)
================================================================================

[G-1] ~ MAINTENANCE_PLAN.txt is stale
  Status:   [ ]  OPEN
  Source:   TODO_FULL C3 notes
  Action:   Test count shows 73/0 (live is 272/1). Refresh to
            current state.
  Effort:   15 minutes

[G-2] . ACCREDITATION brief has unverified providers
  Status:   [ ]  OPEN (operator due diligence)
  Source:   ACCREDITATION_AND_VERIFICATION_BRIEF_2026-07-21.md
  Action:   Borderless CS, The Escrow Company, Elttam, CyberPulse,
            Dreamlab Technologies -- all UNVERIFIED. Operator must
            check CREST/ISO accreditation, scope, pricing.

[G-3] [x] F8-EXTENDED-LEGAL: Makita citation (stale duplicate)
  Status:   CLOSED (2026-07-21, a053ba8)
  Note:     See C-1. Same work item, different doc reference.

================================================================================
H. HEAD-TO-TOE ALIGNMENT (this session's scan)
================================================================================

[H-1] [x] Allow-list closed-set policy
  Status:   CLOSED (2026-07-23, this session)
  See:      D-6.

[H-2] [x] Master TODO consolidation (this doc)
  Status:   CLOSED (2026-07-23, this session)
  See:      This file.

[H-3] [x] Head-to-toe one-view alignment scan
  Status:   CLOSED (2026-07-23, this session)
  See:      04_Validation/HEAD_TO_TOE_ALIGNMENT_2026-07-23.md
  Note:     Scans 11 files, 41 constants, 55 ontology patterns,
            test/chain/git/canonical state. Single document the
            operator and a future AI can read to orient in 5 minutes.

================================================================================
PRIORITY SUMMARY (by urgency, 2026-07-23)
================================================================================

DO NOW (operator, minutes):
  1. A-COMMS-1: WideNet follow-up email/call (operator decision)
  2. B-1.1: Refresh paper backup card to live root (2 min via derive_fingerprints.py)
  3. F-GEM-3: Build the Gemini Gem (~5 min in UI)
  4. A-COMMS-3: NBN check at nbnco.com.au (10 min)

DO THIS WEEK (operator, hours):
  5. B-1: Buy USB stick + set up offsite backup at Whyalla bank (~1 hr)
  6. A-COMMS-2: Buy Telstra dongle (~$50-99)
  7. A-COMMS-4: Email Field Solutions Group

DO NEXT SESSION (code, sealable):
  8. D-5: Refresh OPEN_ITEMS_AND_REFERENCE.md fingerprints + tagline
     (30 min, sealed OPEN_ITEMS_REFRESHED_2026_07_23)
  9. G-1: Refresh MAINTENANCE_PLAN.txt (15 min)
  10. C-3: Continue lexical-set audit on remaining ~10 patterns
     (1-2 hr, sealed ONTOLOGY_LEXICAL_AUDIT_PILOT_2026_07_XX)

DO WHEN TIME PERMITS:
  11. C-2: nothing to build; the suite is at 100+. Just close
     the stale doc references when convenient.
  12. C-3: lexical-set audit on the rest of the patterns
  13. E-1: Gmail .mbox export (operator, 30 min)
  14. E-3: Tauri code-signing ($200-500/yr)
  15. E-4: D1-TRUE clean-host test (needs 2nd PC)
  16. G-2: Due diligence on accreditation providers

================================================================================
DOCUMENTS THAT NEED AN UPDATE BEFORE NEXT SESSION
================================================================================

The following tracking docs are stale and confuse the next session.
Priority: refresh as part of D-5 (the OPEN_ITEMS refresh) or
G-1 (MAINTENANCE_PLAN):

  1. OPEN_ITEMS_AND_REFERENCE.md
     - REF-3/4/5/6 stale (34,309 blocks, root 1e633db9)
     - Tagline "Truth as a Service" still appears in next-5-steps
       text (the rebrand to "Verified Processor" is 2026-07-21)
     - Many "OPEN" items now closed (C-1, C-2, C-4, C-5)

  2. TODO_FULL.md
     - All 7 "open" items in this doc (C4, C5, D5, E1, E2, E3, E4)
       are stale references. C5, D5, E2, E3 actually closed; E1
       operator-dependent; E4 stale.
     - Test count line is 88/1 (live is 272/1).
     - Block count line is 10,561 (live is 35,366).

  3. BUILD_DIRECTIVE_NEXT_SESSION.md
     - Dated 2026-07-18; many WPs already closed (WP-1 a053ba8,
       WP-3 batches done, WP-4 USB remote done, WP-6 F7-deep done).
     - The "default" decision gates no longer apply because the
       items are already done.
     - Action: archive as historical; the next-session directives
       should come from this MASTER_TODO and from 04_Validation/
       HEAD_TO_TOE_ALIGNMENT_2026-07-23.md.

================================================================================
END OF MASTER TODO
================================================================================
