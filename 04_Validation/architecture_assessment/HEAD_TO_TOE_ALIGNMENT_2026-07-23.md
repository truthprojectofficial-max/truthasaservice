================================================================================
ORDER GET IT RIGHT -- HEAD-TO-TOE ALIGNMENT
Generated: 2026-07-23 by Hermes (one-view orientation document)
================================================================================

PURPOSE

This is the single document a new operator or new AI session reads first.
It maps the project from the top of the directory tree to the bottom in
one pass, with one-line purpose per file and no rabbit holes. The goal
is 10-15 minutes to full orientation.

If this doc is out of date, run `python 04_Validation/scripts/derive_fingerprints.py --json-only`
to refresh the chain / test / file counts, then re-seal the doc.

================================================================================
LIVE STATE (2026-07-23)
================================================================================

  Merkle chain:        35,594 blocks, root 9256d8cc..., MATCH
  Tests:               272 passed, 1 skipped, 0 failed
  Source .py:          53 under 02_Technical/src/, 35 total under
                       02_Technical/ (src + tools + top-level)
  Test files:          29 under tests/ (HTTP-only boundary)
  HTTP endpoints:      32 under 02_Technical/src/server/app.py
  Ontology:            3.10 (55 patterns, R1-R6)
  Tagline:             "Verified Processor" (rebranded 2026-07-21)
  Operator:            OGIR-OPERATOR (chain) / Justin Barnett (legal docs)
  Jurisdiction:        Commonwealth of Australia / ACL / Evidence Act 1995
  Canonical path:      C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight
  Sentinel:            8c70c4f12edbd35d9e05d4d1fded91d4162d7004007a3e29b722f8b7fa9c1225
  Git remote:          usb -> D:/OrderGetItRight.git
  Last session:        2026-07-23 (this session)
  Open items:          04_Validation/MASTER_TODO_2026-07-23.md (16 items)

================================================================================
TOP-LEVEL TREE (the one-view map)
================================================================================

  OrderGetItRight/
    AGENTS.md                      # operator-ritual command card (30s read)
    CANONICAL.sentinel             # SHA-256 stamp of canonical path
    README.md                      # project elevator pitch
    pyproject.toml                 # pytest + project config
    conftest.py                    # pytest fixtures
    requirements.txt               # stdlib-only promise (no third-party)
    00_Strategy/                   # governance + non-negotiables (16 KB)
    01_Methodology/                # math + ontology docs (21 KB)
    02_Technical/                  # THE PROGRAM (1.9 GB; src + tools + deploy)
    03_Vault/                      # LIVE MERKLE CHAIN (47 MB; append-only)
    04_Validation/                 # test, governance, runbooks, scripts (23 MB)
    99_Archive_Historical/         # frozen snapshots and messy-session archives
    data/                          # intake + outbox for batch audits
    deploy/                        # deploy.ps1 clean-host script
    launchers/                     # bat files (Windows shortcuts)
    tests/                         # HTTP-only test suite (936 KB, 29 files)
    v/                             # vendor / vendored runtime?

================================================================================
00_Strategy/  (governance)
================================================================================

  STRATEGY.md                      # axioms, trust anchors, design
  GOVERNANCE.md                    # operator rules + non-negotiables
  01-AX, 02-SB, ...                # numbered strategy components

  PURPOSE: read STRATEGY.md and GOVERNANCE.md before touching code.

================================================================================
01_Methodology/  (math + ontology documentation)
================================================================================

  REAL_OPTIONS_LATTICE.md          # how S0/K1/sigma lattice works
  F7_SPEC_TAGUCHI.md               # the symmetric value curve V(x)
  DECEPTION_ONTOLOGY.md            # 55 patterns, R1-R6 gates
  ...                              # (each engine has a doc twin)

  PURPOSE: the math and ontology are documented in prose here, then
  implemented in 02_Technical/src/engines/. Read this BEFORE reading
  the engine source.

================================================================================
02_Technical/  (the program -- 1.9 GB)
================================================================================

  Top-level files:
    __init__.py                    # tagline + version (the canonical source)
    requirements.txt               # stdlib-only (no third-party deps)
    DEPLOYMENT.md                  # operator-facing deploy guide
    DEPLOYMENT.Dockerfile          # (not the recommended path; for reference)
    RESOURCING.md                  # the Tauri + vendor Python notes
    B1_B3_B4_SEAL.py               # historical seal-1-of-3 (archive-only)

  config/                          # 41 named constants
    constants.py                   # the 41 constants + ontology version
                                   # the only place a constant lives

  src/                             # THE RUNTIME (zero network, hard-fail)
    audit_cli.py                   # CLI entry: python -m src.audit_cli
    onyx_cli.py                    # CLI entry: onyx> discovery <target>
    third_party_assistant.py       # the onyx> chat shell
    config.py                      # runtime config (not the constants)
    types.py                       # ProductEvidence, etc.
    verify_chain.py                # python -m src.verify_chain

    agents/  (11 files -- the four-gate pipeline + supporting roles)
      orchestrator.py              # wires the 4 gates end-to-end
      form_entry_agent.py          # gate 1: input validation
      audit_review_agent.py        # gate 2: deception scan
      lattice_compute_agent.py     # gate 3: optionality index
      ledger_seal_agent.py         # gate 4: Merkle chain seal
      affidavit_agent.py           # post-pipeline: affidavit
      monitor_agent.py             # health / SLO monitor
      inventory_agent.py           # external artifact intake
      job_delegator.py             # background job dispatch
      tau_firewall.py              # meta/audit ratio guard

    engines/  (12 files -- the actual decision logic)
      deception_ontology_data.py   # the 55 patterns
      deception_scanner.py         # R1-R6 gate implementation
      bbfb_engine.py               # post-purchase lie detector
      real_options_lattice.py      # optionality index (F7-deep wired)
      unified_audit_engine.py      # facade combining all 3 gates
      evaluation_service.py        # runs EVAL cases
      evaluation_cases.py          # base suite (8 cases)
      facts_registry.py            # facts store (governance/tech/forensic)
      legal_affidavit_generator.py # Makita + ACCC v Valve citations
      acl_demand_generator.py      # ACL s 257 demand letter generator
      squeal_protocol.py           # secondary deception tells

    io/  (6 files -- the I/O layer)
      vault_io.py                  # THE ONLY legal interface to the chain
      pipeline.py                  # audit run pipeline
      evidence_parser.py           # auto-parse product statements
      extractors.py                # pull numbers out of free text
      report_writer.py             # .md / .pdf / .docx output

    server/  (4 files -- the HTTP API)
      app.py                       # the 32-endpoint FastAPI surface
      session_tracker.py           # per-request session id
      tracing.py                   # request log

    utils/  (2 files)
      canonical.py                 # canonical-JSON serialiser (for hashing)

  tools/                           # OPERATOR CLI (allow-listed network scope)
    agentic_repl.py                # onyx> chat (Ollama-backed REPL)
    agentic_repl_tools.py          # the 9 tool functions Ollama calls
    discovery_agent.py             # the forward-discovery role

  web/                             # THE WEB UI (single-page, 30s read)
    index.html                     # operating surface (rewritten 2026-07-17)

  tauri-shell/                     # THE WINDOWS DESKTOP BINARY
    src/                           # Rust + Tauri config
    resources/python/              # vendored CPython 3.14 (do not scan)

  04_Validation/                   # historical validation data
                                   # (the live one is at project root)

  data/                            # runtime data: intake, outbox, samples

  scripts/                         # runtime support scripts

================================================================================
03_Vault/  (the live Merkle chain)
================================================================================

  facts_registry.json              # THE CHAIN (47 MB, 35,594 blocks)
  job_registry.json                # background job log
  affidavit_transcript.txt         # sealed affidavit copies

  CONSTRAINT: append-only. Every state change seals a block here.
  Hard-fail on edits. Re-derivation = the source of truth.

================================================================================
04_Validation/  (governance + test + scripts)
================================================================================

  AGENTS.md-equivalents in this dir:
    OPEN_ITEMS_AND_REFERENCE.md    # 5-step roadmap + 6 fingerprints (stale)
    TODO_FULL.md                   # 7 items, all stale (see MASTER_TODO)
    MASTER_TODO_2026-07-22.md      # 2026-07-22 consolidated list
    MASTER_TODO_2026-07-23.md      # 2026-07-23 consolidated list (this session)
    BUILD_DIRECTIVE_NEXT_SESSION.md # 2026-07-18 directive (mostly closed)
    handover_next_session_*.md     # session-by-session state
    AUDIT_NO_NETWORK.md            # 5-allow-list closed-set policy
    AUDIT_BLACK_BOX_TRACE_*.md     # screen-to-function trace
    PAPER_BACKUP_CARD_*.txt        # the operator's fireproof-safe card
    RUNBOOK_*.md                   # operator recovery runbooks
    STRATEGY.md, GOVERNANCE.md     # (mirrors at project root)

  scripts/  (29 files, the build system)
    audit_no_network.py            # 5-allow-list audit (closed set)
    deterministic_hygiene.py       # the GREEN/YELLOW/RED triad runner
    derive_fingerprints.py         # the 6-fingerprint re-deriver
    handover_drift_check.py        # 2-day-stale-handover detector
    which_canonical.py             # sentinel-walk canonical resolver
    append_marker.py               # operator-facing seal helper
    dns_forwarder_health.py        # local Unbound health probe
    audit_cli runners, phase_1..5  # historical seal scripts (archive)
    *.bat                          # Windows mirror scripts

================================================================================
tests/  (HTTP-only, 29 files, ~280KB)
================================================================================

  CORE (always run):
    test_smoke.py                  # baseline (200+ tests)
    test_00_99_boundary.py         # the 00-99 boundary rule
    test_audit_no_network.py       # the 5-allow-list audit
    test_allow_list_closed.py      # 5-allow-list closed-set lock (NEW 2026-07-23)
    test_which_canonical.py        # sentinel resolver
    test_static_dir.py             # /static mount + GET /

  EVAL CASES (the 100+ calibration):
    test_evaluation_cases_ai_legal.py      # 7 cases
    test_evaluation_cases_extended.py      # 100+ cases
    test_evaluation_cases_selby.py         # 2 cases (real evidence)

  ENGINE-SPECIFIC:
    test_bbfb_engine.py            # BBFB LAW gates
    test_f7_spec_value_curve.py    # Taguchi quadratic
    test_f7_deep_lattice_wired.py  # LATTICE_INPUTS_ARE_HARDCODED=False
    test_evidence_parser.py        # auto-parse product statements
    test_orchestrator_seam.py      # 4-gate pipeline integration
    test_unified_audit_engine.py   # facade + HTTP-only contract
    test_affidavit_preview.py      # Makita + Valve citations present
    test_normalize_regression.py   # numerical determinism

  GOVERNANCE:
    test_governance_reference.py   # S-QoL/SWB/ALDVMR rejected
    test_vault_reseed_guard.py     # re-seed foot-gun
    test_c14_canonical_json_hardening.py  # canonical-JSON
    test_tagline_rebrand.py        # "Verified Processor" only
    test_tauri_signing_reference.py # Windows signing config
    test_ollama_isolation.py       # runtime has no Ollama dep
    test_faults_rebuttal.py        # FRUIT four-pillar, no drift

  DEPLOY + INFRA:
    test_a5_deploy_dry_run.py      # deploy.ps1 -DryRun
    test_b3_host_dependent.py      # host-portable tests
    test_b4_python_312_compat.py   # Python 3.12+ compat
    test_handover_drift_check.py   # handover auto-write
    test_d5_agentic_repl.py        # Ollama REPL end-to-end (skip-guarded)

================================================================================
THE FOUR-GATE PIPELINE (what the engine actually does)
================================================================================

  Operator input
       |
       v
  Gate 1: Form_Entry           validates category + statement
       |
       v
  Gate 2: Audit_Review         runs /api/analyze (55-pattern scan, R1-R6)
                                   fires 0..N patterns
                                   computes deceptionProbability
                                   emits SQUEAL if layered
       |
       v
  Gate 3: Lattice_Compute      runs real_options_lattice
                                   S0/K1/K2 derived from ProductEvidence
                                   (F7-deep 2026-07-19)
                                   returns optionality index (not valuation)
       |
       v
  Gate 4: Ledger_Seal          append_block to 03_Vault/facts_registry.json
                                   finalAction: GO / REVIEW_REQUIRED /
                                                REJECT / REFUSED
                                   sealed block carries the verdict

  POST-PIPELINE: Affidavit      optional, on Forensic or REJECT cases
                                   embeds Makita + Valve citations
                                   writes to affidavit_transcript.txt

================================================================================
THE HTTP API SURFACE (32 endpoints, 02_Technical/src/server/app.py)
================================================================================

  GET  /                              # serve web/index.html
  GET  /api/status                    # project name, version, ontology
  GET  /api/verify-chain              # re-derive Merkle root
  GET  /api/ontology                  # full 55-pattern ontology
  GET  /api/eval/run                  # run the EVAL suite
  GET  /api/facts                     # list facts registry
  POST /api/facts                     # add fact (seals block)
  GET  /api/changelog                 # list chain events
  POST /api/changelog                 # seal custom event
  GET  /api/ledger                    # list sealed blocks
  POST /api/analyze                   # 55-pattern scan (text only)
  POST /api/calculate                 # BBFB + Lattice with evidence
  POST /api/parse/evidence            # auto-parse product statement
  POST /api/orchestrator/process      # FULL 4-GATE PIPELINE
  POST /api/affidavit                 # generate affidavit
  GET  /api/affidavit/preview         # preview affidavit
  POST /api/acl-demand                # ACL s 257 demand letter
  GET  /api/squeal                    # SQUEAL co-occurrences
  POST /api/canonical/dump            # canonical-JSON dump
  POST /api/batch/upload              # batch audit intake
  POST /api/batch/process             # batch run
  POST /api/batch/eject               # batch outbox eject
  GET  /api/batch/job/{job_id}        # batch job status
  GET  /api/batch/download/{job_id}/{filename}
  GET  /api/mcp/jobs                  # list jobs
  GET  /api/mcp/jobs/pending          # pending jobs
  POST /api/mcp/jobs                  # create job
  POST /api/mcp/jobs/{job_id}/claim   # claim job
  POST /api/mcp/jobs/{job_id}/close   # close job
  GET  /api/mcp/stats                 # job stats
  GET  /api/mcp/tau                   # meta/audit ratio
  GET  /health                        # liveness probe

================================================================================
THE 41 CONSTANTS (02_Technical/config/constants.py)
================================================================================

  Identity:
    PROJECT_NAME = "Order Get It Right"
    PROJECT_VERSION = "1.0.0"
    PROJECT_OPERATOR = "Justin Barnett"   # legal docs only
    CHAIN_OPERATOR_ID = "OGIR-OPERATOR"   # chain blocks
    PROJECT_ROOT, PROJECT_VAULT_DIR
    __tagline__ = "Verified Processor"   # (in src/__init__.py)
    __jurisdiction__ = "Commonwealth of Australia / ACL / Evidence Act 1995"

  Deception ontology:
    DECEPTION_ONTOLOGY_VERSION = "3.10 (55 patterns, R1-R6 applied)"

  Probabilities + thresholds:
    DECEPTION_PROBABILITY_LOW = 0.30
    DECEPTION_PROBABILITY_VETO = 0.75
    PERFORMANCE_FLOOR = 0.50
    EFFICIENCY_FLOOR = 0.30
    ISSUE_DENSITY_FLOOR = 0.10
    CVS_THRESHOLD = 0.0005

  GRACE:
    GRACE_CRITICAL_THRESHOLD = 0.75
    GRACE_QUADRATIC_COEFFICIENT = 2.0

  FRUIT:
    FRUIT_WEIGHTS = {...}   # 4 pillars: quality, efficiency, completeness, durability

  Lattice:
    LATTICE_FRAMING = "deception-adjusted optionality index (not a business valuation)"
    LATTICE_INPUTS_ARE_HARDCODED = False  # F7-deep 2026-07-19
    STRIKING_RATIO = ...
    DEFAULT_S0, DEFAULT_K1, DEFAULT_K2, DEFAULT_SIGMA1, DEFAULT_SIGMA2
    PERFORMANCE_FLOOR used in V(x) = 1 - ((x-1)/w)^2

  Pipeline + storage:
    DEFAULT_VAULT_PATH = "03_Vault"
    DEFAULT_OUTBOX_PATH = "04_Validation/reports"
    BATCH_INTAKE_DIR, BATCH_OUTBOX_DIR

  Meta:
    TAU_EXTRACTION_CEILING = 0.10
    META_AUDIT_RATIO_GUARD = 5.0

  (Read the file for the rest. It's 41 constants, all in one place.)

================================================================================
THE SEAL-TEST-VERIFY-COMMIT RITUAL
================================================================================

Every source change follows:

  1. PROBE: python -c "from src.engines.X import Y; ..."
     Confirm the change is what you think it is.
  2. EDIT: write_file or patch (the only edit primitives).
  3. TEST: python -m pytest tests/ -q (from project root)
     Must pass with 272+/1+ count or better.
  4. VERIFY: cd 02_Technical && python -m src.verify_chain
     Must print MATCH with non-decreasing block count.
  5. SEAL: append_block to vault_io (the only legal interface)
     event_type in SCREAMING_SNAKE_CASE, e.g. FOO_BAR_BAZED_2026_07_23.
  6. COMMIT: git add -A && git commit -m "<event_type>: <one-line>"
     One block per commit. No mega-commits.
  7. RE-VERIFY: verify_chain again. Chain is now +1 block.
  8. PUSH (if remote): git push usb.

DO NOT seal first, commit second -- the witness must lead the git record.
DO NOT skip any step. DO NOT rewrite history. DO NOT edit chain blocks.

================================================================================
NON-NEGOTIABLES (the project promises)
================================================================================

  1. Runtime is zero-network. Hard-fail. No exceptions.
  2. Operator tools may use network, but only via the 5-allow-list
     closed set (Ollama local, FastAPI local, DiscoveryAgent socket,
     DNS health probe). Adding a 6th requires a sealed governance event.
  3. Chain is append-only. No edits. No re-seeds. No rewrites.
  4. One block per source change. One commit per block.
  5. The 00-99 boundary is enforced by an AST test. Tests cannot
     import from src/ except src.server.app. The audit cannot import
     from tools/, deploy/, or web/.
  6. The audit path works without Ollama, without internet, without
     LLM in the loop. The conversation layer is not the audit path.
  7. The engine is a lie detector, not a business valuation. The
     lattice returns an optionality index, not a price. The
     LATTICE_FRAMING string is the reminder; never use "valuation"
     in user-facing language.
  8. The tag is "Verified Processor". The prior branding is the
     legacy phrase, preserved in historical chain blocks and Tauri
     configs only.

================================================================================
COMMON TASKS (where to start)
================================================================================

  Add a new deception pattern:
    1. tests/test_evaluation_cases_extended.py  -- add EVAL-NNN
    2. 02_Technical/src/engines/deception_ontology_data.py  -- add DD-NNN
    3. 02_Technical/config/constants.py  -- bump DECEPTION_ONTOLOGY_VERSION
    4. 02_Technical/src/engines/deception_scanner.py  -- if R-gate needed
    5. seal ONTOLOGY_BUMP_DDxxx_<date>, commit, push

  Audit a real document:
    1. Copy document to data/inbox/<casename>/
    2. cd 02_Technical && python -m src.audit_cli --inbox ../data/inbox/<casename> --outbox ../data/outbox
    3. Read data/outbox/*.md
    4. Translate engine verdict to operator-facing language

  Add a new engine:
    1. 01_Methodology/<engine>.md  -- math + ontology doc
    2. 02_Technical/src/engines/<engine>.py  -- implementation
    3. tests/test_<engine>.py  -- regression tests via HTTP API
    4. 02_Technical/src/agents/orchestrator.py  -- wire into pipeline
    5. 02_Technical/config/constants.py  -- add constants
    6. 04_Validation/scripts/derive_fingerprints.py  -- bump REF-3 count
    7. seal ENGINE_<NAME>_ADDED_<date>, commit, push

  Seal a one-off event:
    python 04_Validation/scripts/append_marker.py \
      --event-type INCIDENT_xyz_2026_07_23 \
      --note "what happened and what changed"

  Verify the chain is intact:
    cd 02_Technical && python -m src.verify_chain
    Expected: RESULT: MATCH -- chain is intact.

  Run the full hygiene triad:
    python 04_Validation/scripts/deterministic_hygiene.py --json-only
    Expected: GREEN verdict, seal+push eligible.

================================================================================
STALE DOCS TO REFRESH (next session)
================================================================================

  1. OPEN_ITEMS_AND_REFERENCE.md
     - REF-3/4/5/6 stale (34,309 blocks, root 1e633db9, 2026-07-22)
     - Tagline (prior branding) in next-5-steps (should be
       "Verified Processor")
     - 5 of 5 next-5-steps already closed in code
  2. TODO_FULL.md
     - All 7 "open" items are stale (C5, D5, E2, E3 done; E4 stale)
     - Test count 88/1 (live 272/1)
     - Block count 10,561 (live 35,594)
  3. BUILD_DIRECTIVE_NEXT_SESSION.md
     - 5 of 7 WPs already done
     - Default decision gates no longer apply
     - Action: archive as historical; supersede with this file
  4. MAINTENANCE_PLAN.txt
     - Test count 73/0 (live 272/1)

================================================================================
THE ONE-LINE PROJECT IDENTITY
================================================================================

  Order Get It Right -- "Verified Processor".
  A deterministic business audit engine written in pure-stdlib Python 3.12+.
  Reads text, asks "is this deceptive?", scores evidence under BBFB LAW
  gates, computes an optionality index, and seals the verdict to an
  append-only Merkle chain at 03_Vault/facts_registry.json. The runtime
  is zero-network. The operator tools are allow-list scoped. The audit
  path works without Ollama, without internet, without LLM. Every
  decision is sealed; every seal is committed; every commit is pushed
  to the USB bare repo at D:/OrderGetItRight.git. Operator: Justin
  Barnett. Jurisdiction: Commonwealth of Australia / ACL / Evidence
  Act 1995. Tagline: "Verified Processor". Ontology: 3.10, 55 patterns,
  R1-R6. Live: 35,594 blocks, 272 tests pass, chain MATCH.

================================================================================
END OF HEAD-TO-TOE ALIGNMENT
================================================================================
