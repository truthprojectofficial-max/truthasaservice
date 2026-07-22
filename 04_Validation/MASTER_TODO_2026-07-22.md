================================================================================
ORDER GET IT RIGHT -- MASTER TODO (CONSOLIDATED)
Generated: 2026-07-22 by Hermes
Sources: OPEN_ITEMS_AND_REFERENCE.md, TODO_FULL.md,
         handover_next_session_2026-07-22.md, BUILD_DIRECTIVE_NEXT_SESSION.md,
         PROJECT TROUBLE COMMS.txt, this session's work
================================================================================

This is the ONE list. Every open item from every source, de-duplicated,
with current status. If an item is not here, it is closed or not real.

Legend:
  [ ]    OPEN -- needs work
  [x]    CLOSED -- done and sealed
  [-]    DEFERRED/BLOCKED -- needs operator action or hardware
  !      HIGH severity
  ~      MEDIUM severity
  .      LOW severity

================================================================================
A. INFRASTRUCTURE / COMMS (operator, physical, this session)
================================================================================

[A-COMMS-1] ! Send WideNet fixed-wireless feasibility inquiry
  Status:   [ ]  OPEN
  Effort:   5 minutes (email is already drafted)
  Source:   PROJECT TROUBLE COMMS.txt
  Action:   Send the email to support@widenet.com.au
  Note:     The draft requests Fresnel Zone clearance, signal
            integrity, SFOA/SLA docs. Property has no copper or
            NBN lead-in. This is the best comms upgrade path --
            private fixed-wireless with an SLA is a governed
            business relationship, not consumer best-effort.

[A-COMMS-2] ~ Get a Telstra mobile broadband dongle
  Status:   [ ]  OPEN (operator purchase)
  Effort:   ~$50-99 dongle + ~$30-50/mo SIM
  Source:   This session, COMMS_OPTIONS_WHYALLA_2026-07-22.md
  Action:   Buy a prepaid Telstra 4GX/5G dongle for a third
            independent internet path. Telstra has the best
            regional SA coverage.

[A-COMMS-3] ~ Check NBN availability for 20 Loveday St
  Status:   [ ]  OPEN
  Effort:   10 minutes at nbnco.com.au
  Source:   This session
  Action:   Enter the address at nbnco.com.au to determine
            if NBN Fixed Wireless or FTTC is available. If
            yes, this is a viable fixed-line backup.

[A-COMMS-4] ~ Contact Field Solutions Group (fsg.com.au)
  Status:   [ ]  OPEN
  Effort:   10 minutes
  Source:   This session
  Action:   Parallel inquiry to WideNet. FSG is a regional
            Australia fixed-wireless specialist. If WideNet
            can't serve the address, FSG might.

[A-COMMS-5] . Adapter discipline (session hygiene rule)
  Status:   [-]  ONGOING (operator habit, not code)
  Effort:   30 seconds per session
  Source:   handover_next_session_2026-07-22.md item 2
  Action:   Turn off USB tether when on Wi-Fi, and vice versa.
            One path at a time. Prevents DNS resolver conflicts.

================================================================================
B. BACKUP / DISASTER RECOVERY (operator, physical)
================================================================================

[B-1] ! Offsite backup -- USB stick + paper card to fireproof offsite
  Status:   [ ]  OPEN (operator, ~1 hour at a Whyalla bank branch)
  Source:   handover item 1, HARD_COPY_BACKUP_PLAN_1-2-3.txt
  Action:   1. Buy a USB stick (~A$8)
            2. Run the existing mirror scripts (amendments_mirror_to_sdxc.bat)
               OR robocopy the tree to the USB
            3. Print PAPER_BACKUP_CARD_2026-07-22.txt
            4. Put USB + paper card + passphrase in a fireproof
               offsite location (bank safe deposit box in Whyalla)
  Note:     Until this is done, the chain is on a single physical
            site (laptop) plus local D: mirror. Both lost in a
            house fire. This is the #1 gap.

[B-2] [x] Paper Merkle root card -- text file written
  Status:   CLOSED (this session)
  Source:   This session
  Note:     04_Validation/PAPER_BACKUP_CARD_2026-07-22.txt
            Root: 8bfc95bd9b01f8088ea717d1d73cf83fd92a22f6c3ef2f5f386a7d682e84442b
            Blocks: 34,127.  Operator must PRINT it.

[B-3] [x] D: microSD git mirror -- working
  Status:   CLOSED (this session verified)
  Source:   This session
  Note:     85 commits synced. git push usb works.

================================================================================
C. CODE / BUILD (developer, sealable)
================================================================================

[C-1] ~ Embed Makita v Sprowles citation in affidavit generator
  Status:   [ ]  OPEN
  Effort:   1 hour
  Source:   OPEN_ITEMS step 2, BUILD_DIRECTIVE WP-1
  Files:    02_Technical/src/engines/legal_affidavit_generator.py
  Action:   Add citation Makita (Australia) Pty Ltd v Sprowles
            [2001] NSWCA 305 to the VERIFICATION STATEMENT block.
            The affidavit makes a s 79 specialised-knowledge claim
            without citing the foundational authority.
  Seal:     F8_EXTENDED_LEGAL_MAKITA_CITED_2026_07_XX
  Held:     Supreme Court of NSW -.txt is on file at
            C:\Users\justo\OneDrive\Documents\Supreme Court of
            New South Wales -.txt (KNOWN_INTAKE_HELD)

[C-2] ~ EVAL-suite expansion to 30+ cases
  Status:   [ ]  OPEN
  Effort:   1-2 days
  Source:   OPEN_ITEMS step 3, BUILD_DIRECTIVE WP-5
  Files:    tests/test_evaluation_cases_extended.py (new)
  Action:   Expand from 8 to 30+ cases with real anonymised
            correspondence. R1-R4 gates are stable; next move
            is empirical coverage.
  Seal:     F8_EXTENDED_EVAL_SUITE_GROWN_2026_07_XX

[C-3] . Lexical-set audit for remaining 53 patterns (R5-EXTENDED)
  Status:   [ ]  OPEN
  Effort:   4-6 hours (or 1 hour for 10-pattern pilot)
  Source:   OPEN_ITEMS step 4, BUILD_DIRECTIVE WP-3
  Files:    02_Technical/src/engines/deception_ontology_data.py,
            tests/test_evaluation_cases_extended.py,
            02_Technical/config/constants.py
  Action:   For each pattern DD-001..DD-054, write a probe with
            a synonym/near-miss. If it fails to fire, add the
            synonym. Bump ontology version to 3.11.
  Default:  10-pattern pilot first.
  Seal:     ONTOLOGY_LEXICAL_AUDIT_2026_07_XX

[C-4] ~ F7-deep: wire lattice inputs to extracted evidence
  Status:   [-]  DEFERRED (methodology change, needs own session)
  Effort:   ~4 hours + calibration plan
  Source:   OPEN_ITEMS F7-EXTENDED, BUILD_DIRECTIVE WP-6
  Files:    02_Technical/src/engines/real_options_lattice.py,
            02_Technical/src/io/extractors.py,
            02_Technical/config/constants.py
  Note:     LATTICE_INPUTS_ARE_HARDCODED = False is already set
            (wired to evidence when supplied, falls back to
            defaults). The deep work is the mapping calibration.
  Seal:     F7_DEEP_LATTICE_WIRED_2026_07_XX

[C-5] . C5: STRATEGY.md Section 7 tone-of-done pass
  Status:   [ ]  OPEN
  Effort:   30 minutes
  Source:   TODO_FULL.md C5, OPEN_ITEMS
  Files:    00_Strategy/STRATEGY.md
  Action:   Section 7 checkboxes read "operational and maintained"
            not "completed". Test-count line to match live state
            (272 pass + 1 skip, not 71/1).
  Seal:     STRATEGY_TONE_OF_DONE_FIXED

================================================================================
D. CHAIN / HYGIENE / PROCEDURE (developer, sealable)
================================================================================

[D-1] ~ Auto-handover on session-seal boundary
  Status:   [x]  CLOSED (2026-07-22)
  Source:   handover item 3
  Note:     handover_drift_check.py exists and works. It detects
            drift, auto-writes the handover in place, and seals
            SEALED_HANDOVER_<date> blocks. Detected 3747-block
            drift between handover (30380) and live (34127) on
            this session's run.

[D-2] ~ Handover-drift invariant (refuse on drift)
  Status:   [x]  CLOSED (2026-07-22)
  Source:   handover item 4
  Note:     handover_drift_check.py --refuse mode exists.

[D-3] [x] Conversation-layer-down runbook
  Status:   CLOSED (this session)
  Source:   handover item 5
  Note:     04_Validation/RUNBOOK_CONVERSATION_LAYER_DOWN.md
            Doubles as internal comms book for multi-agent work.

[D-4] . Audit path works without LLM (doc needed)
  Status:   [x]  CLOSED (this session)
  Source:   handover item 5
  Note:     The runbook covers the PowerShell-only path. The
            audit path is already air-gapped; the doc was the gap.

[D-5] ~ OPEN_ITEMS_AND_REFERENCE.md is stale (last refreshed 2026-07-18)
  Status:   [ ]  OPEN
  Effort:   30 minutes
  Source:   This session's audit
  Action:   Refresh all 6 fingerprints to live state (34,127
            blocks, root 8bfc95bd...). The doc still shows 10,561
            blocks and root 5b66058e... from 2026-07-17.
  Seal:     OPEN_ITEMS_REFRESH_2026_07_22

[D-6] ~ TODO_FULL.md is stale (last refreshed 2026-07-17)
  Status:   [ ]  OPEN
  Effort:   30 minutes
  Source:   This session's audit
  Action:   Test count shows 88/1 (live is 272/1). Block count
            shows 10,561 (live is 34,127). Many items marked [ ]
            are actually closed. Needs full reconciliation.

================================================================================
E. OPERATOR-SUPPLIED INPUTS (operator, not code)
================================================================================

[E-1] ~ Gmail .mbox export for InventoryAgent
  Status:   [ ]  OPEN (operator action)
  Effort:   30 minutes operator side
  Source:   TODO_FULL.md E1, OPEN_ITEMS E1
  Action:   Export truthproject.official@gmail.com to .mbox.
            Drop into OneDrive\Documents\to the spoils go\inbox\.
  Seal:     GMAIL_CORPUS_INGESTED
  Note:     Network egress not granted. Operator must export.

[E-2] [-] Pre-2020 reference corpus
  Status:   [-]  PARTIALLY DONE (verified_prior_2021.txt exists)
  Source:   TODO_FULL.md E4
  Note:     E4 was CLOSED 2026-07-17 for the pre-2021 corpus.
            True pre-2020 corpus still needs operator files.

[E-3] [-] Tauri code-signing ($200-500/yr)
  Status:   [-]  BLOCKED (operator decision, cost)
  Source:   TODO_FULL.md F10, BUILD_DIRECTIVE
  Note:     Required for any distribution beyond the operator.

[E-4] [-] D1-TRUE: second-PC clean-host restore test
  Status:   [-]  BLOCKED (needs second Windows PC)
  Source:   TODO_FULL.md D1, OPEN_ITEMS
  Action:   On a second Windows PC with no Python, copy from
            USB, run deploy.ps1, pytest, verify_chain. Record
            whether Merkle root matches.

================================================================================
F. GEMINI GEM / AIDER SANDBOX (this session's work)
================================================================================

[F-GEM-1] [x] Updated Gem spec written
  Status:   CLOSED (this session)
  Note:     04_Validation/GEM_SPEC_UPDATED_2026-07-22.md
            All live numbers, redacted identity, 9 rules,
            Aider sandbox integration template.

[F-GEM-2] [x] Chain summary JSON generated (redacted)
  Status:   CLOSED (this session)
  Note:     04_Validation/CHAIN_SUMMARY_FOR_GEM_2026-07-22.json
            Root, block count, event distribution, fingerprints.

[F-GEM-3] . Build the Gem in Google Gemini
  Status:   [ ]  OPEN (operator, 5 minutes in Gemini UI)
  Source:   GEM_SPEC_UPDATED_2026-07-22.md
  Action:   1. Go to gemini.google.com/gems -> Create
            2. Paste system instructions from the spec
            3. Upload 6 knowledge base files
            4. Run first setting prompt to verify
            5. Run truncation check

================================================================================
G. DOCUMENTATION (developer, sealable)
================================================================================

[G-1] ~ MAINTENANCE_PLAN.txt is stale
  Status:   [ ]  OPEN
  Source:   TODO_FULL.md C3 notes
  Action:   Test count shows 73/0 (live is 272/1). Needs
            refresh to current state.

[G-2] . ACCREDITATION brief has unverified providers
  Status:   [ ]  OPEN (operator due diligence)
  Source:   ACCREDITATION_AND_VERIFICATION_BRIEF_2026-07-21.md
  Action:   Borderless CS, The Escrow Company, Elttam, CyberPulse,
            Dreamlab Technologies -- all UNVERIFIED. Operator
            must check CREST/ISO accreditation, scope, pricing.

================================================================================
PRIORITY SUMMARY (by urgency)
================================================================================

DO NOW (operator, minutes):
  1. Send WideNet email (draft is ready, 5 min)
  2. Print PAPER_BACKUP_CARD_2026-07-22.txt (2 min)
  3. Check nbnco.com.au for 20 Loveday St (10 min)

DO THIS WEEK (operator, hours):
  4. Buy USB stick + set up offsite backup at Whyalla bank (~1 hr)
  5. Build the Gemini Gem (~5 min in UI, then test)
  6. Buy Telstra dongle (~$50-99)

DO NEXT SESSION (code, sealable):
  7. C-1: Makita citation in affidavit generator (1 hr)
  8. D-5: Refresh OPEN_ITEMS_AND_REFERENCE.md (30 min)
  9. D-6: Reconcile TODO_FULL.md (30 min)
  10. C-5: STRATEGY.md tone-of-done (30 min)

DO WHEN TIME PERMITS:
  11. C-2: EVAL-suite expansion (1-2 days)
  12. C-3: Lexical-set audit pilot (1 hr for 10 patterns)
  13. C-4: F7-deep lattice wiring (own session)
  14. E-1: Gmail .mbox export (operator, 30 min)
  15. E-4: D1-TRUE clean-host test (needs 2nd PC)
  16. E-3: Tauri code-signing ($200-500/yr)
  17. G-2: Due diligence on accreditation providers

================================================================================
END OF MASTER TODO
================================================================================