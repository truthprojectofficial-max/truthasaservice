# OGIR Repository Skeleton and Workflow (English)

## What this project is

Order Get It Right (OGIR) — deterministic business audit and deception-detection system.
No cloud AI in the audit loop. Every decision is sealed to a Merkle chain in `03_Vault/facts_registry.json`.

## Repository skeleton

```
C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight
├── 00_Strategy          # Why this exists: governance and strategy
├── 01_Methodology       # How it works: math, ontology, lattice
├── 02_Technical         # The running code
│   ├── config/          # constants.py, exceptions.py
│   ├── data/            # inbox / outbox / samples (audit intake)
│   ├── scripts/         # helper shell scripts
│   ├── src/             # all Python source
│   │   ├── agents/      # 10 named modules (orchestrator, firewall, etc.)
│   │   ├── engines/     # deception scanner, ontology, affidavit, lattice
│   │   ├── io/          # evidence parser, pipeline, report writer
│   │   ├── server/      # FastAPI app.py
│   │   └── utils/       # canonical JSON helpers
│   ├── tools/           # agentic REPL and discovery helpers
│   └── web/             # single-page operator UI (index.html)
├── 03_Vault             # Merkle chain and job registry
└── 04_Validation        # reports, handovers, build directives, fingerprints
    └── hardcopy/        # print-and-pin operator docs
```

## Daily operator workflow

1. **Verify the chain**
   cd 02_Technical
   python -m src.verify_chain

2. **Run the test suite**
   python -m pytest tests/ -q

3. **Start the server (optional)**
   python -m uvicorn src.server.app:app --port 3000

4. **Audit an intake**
   - Browser: http://localhost:3000
   - Or CLI: python -m src.audit_cli --input path/to/intake.txt

5. **Seal every material change**
   - The FastAPI lifespan handler seals SHUTDOWN/TEST events automatically.
   - For manual seals, use the ledger agent or a seal script in 04_Validation/scripts/.

6. **Commit and push**
   git add -A
   git commit -m "DESCRIPTIVE_TAG_YYYY_MM_DD: what changed"
   git push usb ogir-build-2026-07-18

## Key files

- `02_Technical/config/constants.py` — version, operator, ontology version
- `02_Technical/src/engines/deception_ontology_data.py` — 54 deception patterns
- `02_Technical/src/engines/deception_scanner.py` — R1-R5 co-text gates
- `tests/test_evaluation_cases_extended.py` — 111 EVAL cases
- `03_Vault/facts_registry.json` — Merkle chain root
- `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` — authoritative open items
- `04_Validation/YELLOW_RIBBON.md` — operator ritual and where-everything-is

## Git remotes

- local working copy: `C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight`
- bare air-gap backup: `usb` → `D:/OrderGetItRight.git`
- (optional) operator can add GitHub/Codeberg remote if desired.

## Verification commands

| Check | Command | Expected result |
|-------|---------|-----------------|
| Chain | `python -m src.verify_chain` | MATCH |
| Tests | `python -m pytest tests/ -q` | ~207 passed, 1 skipped |
| No network imports | `python 04_Validation/scripts/audit_no_network.py` | CLEAN |
| USB parity | `python -m src.verify_chain` from D:\OrderGetItRight | MATCH |


## Full tree

```
📁 00_Strategy
        GOVERNANCE.md
        STRATEGY.md
📁 01_Methodology
        DECEPTION_ONTOLOGY.md
        MATHEMATICS.md
        REAL_OPTIONS_LATTICE.md
📁 02_Technical
    📁 04_Validation
        📁 logs
        📁 reports
        📁 squeal-reports
        __init__.py
        B1_B3_B4_SEAL.py
    📁 config
            __init__.py
            constants.py
            exceptions.py
    📁 data
        📁 inbox
                README.md
                SEED_001_sample_audit_intake.txt
                SEED_002_warranty_claim.txt
                SEED_003_prior_2021_reference.txt
                SEED_004_drive_inventory_pointer.txt
                SEED_MANIFEST.txt
        📁 outbox
                SEED_001_sample_audit_intake.docx
                SEED_001_sample_audit_intake.md
                SEED_001_sample_audit_intake.pdf
                SEED_002_warranty_claim.docx
                SEED_002_warranty_claim.md
                SEED_002_warranty_claim.pdf
                SEED_003_prior_2021_reference.docx
                SEED_003_prior_2021_reference.md
                SEED_003_prior_2021_reference.pdf
                SEED_004_drive_inventory_pointer.docx
                SEED_004_drive_inventory_pointer.md
                SEED_004_drive_inventory_pointer.pdf
                SEED_MANIFEST.docx
                SEED_MANIFEST.md
                SEED_MANIFEST.pdf
        📁 samples
        DEPLOYMENT.Dockerfile
        DEPLOYMENT.md
        requirements.txt
        RESOURCING.md
    📁 scripts
            run_eval_suite.sh
    📁 src
            __init__.py
        📁 agents
                __init__.py
                affidavit_agent.py
                audit_review_agent.py
                form_entry_agent.py
                inventory_agent.py
                job_delegator.py
                lattice_compute_agent.py
                ledger_seal_agent.py
                monitor_agent.py
                orchestrator.py
                tau_firewall.py
            audit_cli.py
            config.py
        📁 data
        📁 engines
                __init__.py
                acl_demand_generator.py
                bbfb_engine.py
                deception_ontology_data.py
                deception_scanner.py
                evaluation_cases.py
                evaluation_service.py
                facts_registry.py
                legal_affidavit_generator.py
                real_options_lattice.py
                squeal_protocol.py
        📁 io
                __init__.py
                evidence_parser.py
                extractors.py
                pipeline.py
                report_writer.py
                vault_io.py
            onyx_cli.py
        📁 server
                __init__.py
                app.py
                session_tracker.py
                tracing.py
            third_party_assistant.py
            types.py
        📁 utils
                __init__.py
                canonical.py
            verify_chain.py
    📁 tools
            __init__.py
            agentic_repl.py
            agentic_repl_tools.py
            discovery_agent.py
    📁 web
            index.html
📁 03_Vault
        affidavit_transcript.txt
        facts_registry.json
        job_registry.json
📁 04_Validation
        AI_COMPLIANCE_FABRICATION_TELLS_2026-07-18.md
        AUDIT_BLACK_BOX_TRACE_2026-07-17.md
        AUDIT_NO_BLACK_BOX.md
        AUDIT_NO_NETWORK.md
        BBFB_INTEGRATION_PLANNING_2026-07-17.md
        BUILD_DIRECTIVE_2026-07-18.md
        BUILD_DIRECTIVE_NEXT_SESSION.md
        changelog.log
        COMPLIANCE_WORD_DENSITY_HEURISTIC_2026-07-18.md
        CONTEXT_WINDOW.md
        deploy.log
        DOWNLOADED_FILE_EVAL_ASSESSMENT_2026-07-18.md
        EVAL_CASE_REFERENCE_INDEX_2026-07-18.md
        GEM_DOCUMENTS_RECONCILED_2026-07-18.md
        GEM_DOCUMENTS_WRONG_CLAIM_ANALYSIS_2026-07-18.md
        GIT_WORKFLOW.md
        HALLUCINATION_PSYCHOLOGY_TODAY_EVAL_PROPOSALS_2026-07-18.md
        HANDOVER_NEXT_SESSION_2026-07-16.md
        HANDOVER_NEXT_SESSION_2026-07-18.md
        HANDOVER_TO_AUDITOR.md
        HANDOVER_TO_NEW_OPERATOR.md
    📁 hardcopy
            HARD_COPY_BACKUP_PLAN_1-2-3.txt
            OPERATOR_MANUAL.txt
            QUICK_REFERENCE_CARD.txt
        INTELLECTUAL_PROPERTY_RIGHTS.txt
        INTRODUCTION.md
        KNOWN_CHAIN_ARTEFACTS.md
        LANCET_FABRICATED_CITATIONS_STAT_2026-07-18.md
        LEXICAL_SET_AUDIT_HELPER_PLAN_2026-07-18.md
    📁 logs
        MAINTENANCE_PLAN.txt
        OGIR_ARCHITECTURE_DIAGRAM.html
        OGIR_ASSESSMENT_2026-07-18.md
        OGIR_ASSESSMENT_NOTES_2026-07-18.md
        OPEN_ITEMS_AND_REFERENCE.md
    📁 pre_2021_intake
            pre_2021_reference_audit_intake.txt
        pre_2021_reference_audit_intake.txt
        PRE_2021_REFERENCE_CALIBRATION_2026-07-17.md
        RECONCILIATION_2026-07-16.md
    📁 reports
        RESEARCH_COMPATIBILITY_2026-07-12.md
    📁 scripts
            amendments_mirror_chain_to_sdxc.bat
            amendments_mirror_paper_to_sdxc.bat
            amendments_mirror_to_sdxc.bat
            amendments_verify_mirror.py
            audit_no_network.py
            phase_1_preflight.py
            phase_2_copy_from_a_to_b.py
            phase_2_copy_report.json
            phase_3_changelog_append.py
            phase_3_changelog_report.json
            phase_4_fingerprints.json
            phase_4_refresh_fingerprints.py
            phase_5_seal_fork_resolved.py
            phase_5_seal_report.json
            precision_final_verify.py
            precision_mirror_all_to_sdxc.bat
            reconcile_2026_07_16.py
            reconcile_2026_07_16_report.json
            sdxc_reburn_step1_backup.bat
            sdxc_reburn_step2_mirror.bat
            seal_amendment_close.py
            seal_precision_followup.py
            seal_strategy_amended.py
        SESSION_REPORT_2026-07-18.md
        SPECS.txt
    📁 squeal-reports
        STAGE_PAPER_ANNUAL.txt
        STAGE_PAPER_DAILY.txt
        STAGE_PAPER_MONTHLY.txt
        STAGE_PAPER_QUARTERLY.txt
        STAGE_PAPER_WEEKLY.txt
        TAURI_BINARY_INVESTIGATION_2026-07-16.md
        TAURI_SIGNING_OPTIONS_2026-07-18.md
        tauri_smoke_fastapi.log
        TODO_FULL.md
        TROUBLESHOOTING.md
        VERIFIED_INTAKE_SOURCE_ELEVATION_2026-07-18.md
        YELLOW_RIBBON.md
📁 99_Archive
        README.md
📁 99_Archive_Historical
        _drift_blueprint.txt
        _drift_consolidated.txt
        _drift_framework.txt
        _drift_production.txt
        _drift_release_notes.txt
        _drift_requirements.txt
        _drift_transition - Copy.txt
        _drift_transition.txt
        _drift_zerotouch.txt
        _review_extra_docs.txt
        _review_sovereign_docs.txt
        claude 1.txt
        clude 3.txt
        clude part 2.txt
        github_pat_[REDACTED].md
        grounded-verify.md
        INDEX.md
        Is A bit of a update. We are close.txt
        now what.txt
        The message.thinking in reasoning tasks. FYI.txt
        Tool calling.txt
        What’s Missing for Real-World Funct.txt
    A5_SEAL.py
    AGENTS.md
    C1_C5_SEAL.py
    CACHEDIR.TAG
    CANONICAL_JSON_SEAL.py
    conftest.py
    D1_USB_SEAL.py
    D5_SEAL.py
📁 data
    📁 discovery
    📁 inbox
            HALLUCINATION_PSYCHOLOGY_TODAY_2023-12.txt
            LANCET_FABRICATED_CITATIONS_2026-05.txt
            README.md
            SEED_001_sample_audit_intake.txt
            SEED_002_warranty_claim.txt
            SEED_003_prior_2021_reference.txt
            SEED_004_drive_inventory_pointer.txt
            SEED_MANIFEST.txt
            Williams_Ai_Transcript.txt
    📁 outbox
            DRIVE_INVENTORY_20260711T221839Z.md
            DRIVE_INVENTORY_20260711T221839Z.records.json
            E4_F1_RE_DERIVED_2026-07-18.json
            EMAIL_CALIBRATION_2026-07-18.json
            EMAIL_CALIBRATION_SUMMARY_2026-07-18.json
            EVAL_SUITE_DEFAULT_RUN_2026-07-18.json
            INTAKE_HELD_AUDITED_2026-07-18_AVEPOINT.json
            INTAKE_HELD_AUDITED_2026-07-18_CLAUDE_LEGAL.json
            INTAKE_HELD_AUDITED_2026-07-18_WILLIAMS_AI_TRANSCRIPT.json
            LIVE_REFS_2026-07-18.json
            pre_2021_reference_audit_intake.md
            SEED_001_sample_audit_intake.docx
            SEED_001_sample_audit_intake.md
            SEED_001_sample_audit_intake.pdf
            SEED_002_warranty_claim.docx
            SEED_002_warranty_claim.md
            SEED_002_warranty_claim.pdf
            SEED_003_prior_2021_reference.docx
            SEED_003_prior_2021_reference.md
            SEED_003_prior_2021_reference.pdf
            SEED_004_drive_inventory_pointer.docx
            SEED_004_drive_inventory_pointer.md
            SEED_004_drive_inventory_pointer.pdf
            SEED_MANIFEST.docx
            SEED_MANIFEST.md
            SEED_MANIFEST.pdf
            SESSION_END_REFS_2026-07-18.json
            Williams_Ai_Transcript.md
    📁 samples
            cli_sample.txt
            deceptive_warranty.txt
            eject_test_1.txt
            eject_test_2.txt
            notes.xls
            verified_prior_2021.certainty.jsonl
            verified_prior_2021.txt
            warranty.txt
📁 deploy
        deploy.ps1
    DEPLOY_HARDENED_SEAL.py
📁 launchers
        Build-Tauri-Desktop.bat
        Run-AuditCli.bat
        Start-Server.bat
        Verify-Chain.bat
        Verify-Tests.bat
    MODEL_SWAP_REVERT_SEAL.py
    pyproject.toml
    README.md
    RESEARCH_QUICK_WINS_SEAL.py
📁 tests
        __init__.py
        test_00_99_boundary.py
        test_a5_deploy_dry_run.py
        test_affidavit_preview.py
        test_audit_no_network.py
        test_b3_host_dependent.py
        test_c14_canonical_json_hardening.py
        test_d5_agentic_repl.py
        test_evaluation_cases_ai_legal.py
        test_evaluation_cases_extended.py
        test_normalize_regression.py
        test_ontology_r1_r4_gates.py
        test_orchestrator_seam.py
        test_smoke.py
        test_static_dir.py
📁 v
    📁 cache
            lastfailed
            nodeids
```
