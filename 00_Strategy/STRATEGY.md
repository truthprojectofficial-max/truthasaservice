# Order Get It Right -- Truth as a Service

**Program Name:** Order Get It Right
**Tagline:** Truth as a Service
**Version:** 1.0.0
**Build Date:** 2026-07-12
**Operator:** Justin Barnett
**Contact:** 0480569941 -- justinbarnett1966@gmail.com
**Hardware Target:** MSI Prestige 16 Studio 13 VF 207AU

---

## 1. Mission Statement

Deliver a single, fully-operational, deterministic business audit and
valuation program that the open market can use to make defensible,
transparent evaluations of any business from its own documents. The
program produces a complete, repeatable, portable and legally grounded
verdict without black boxes.

## 2. Scope

- Ingest any business document (financial statements, contracts, warranties,
  correspondence, invoices, marketing copy, supplier responses, incident
  reports, regulator letters, court filings, evidence packs).
- Extract structured business evidence (price, specifications, warranty,
  compliance, claims, obligations, dates, parties, governing law).
- Run a deterministic, mathematically anchored audit pipeline (Deception
  scan, BBFB engine, Real-Options lattice (reframed F7 2026-07-18 as a deception-adjusted optionality index, NOT a business valuation), Tau ceiling firewall,
  Merkle truth ledger).
- Generate human-readable reports (Markdown, PDF, DOCX).
- Generate legally admissible outputs (Section 177 Affidavit, ACL Section
  56 demand letter, Section 79 supporting bundle).
- Be deployable as either a **local Python install** (via `deploy\deploy.ps1`)
  or a **Tauri desktop binary** (via `deploy\build-tauri.ps1`). Both run
  on the same deterministic Python engine; the Tauri shell only changes
  the wrapping, not the audit.

## 3. The Six Non-Negotiables

1. **Determinism (computation is identical; chain is tamper-evident)**
   -- same input + same config = same verdict, same scores, same decision
   -- on any host. The sealed chain carries ISO-8601 timestamps and is
   tamper-evident, not byte-reproducible across runs. The runtime
   computation is deterministic; the chain payload embeds
   ``datetime.now(timezone.utc)`` so two audits run a second apart
   produce different chains. Both guarantees are needed and they do not
   contradict each other.
2. **No Black Boxes** -- every number on screen is derived from a publicly
   inspectable formula or rule. No probabilistic "model says yes".
3. **Truth Ledger** -- every audit decision is sealed to a SHA-256 Merkle
   chain with an ISO 8601 timestamp. The ledger is portable, tamper-evident,
   and verifiable offline.
4. **Tau Firewall** -- a single input cannot consume more than 10% of the
   system tolerances in any single cycle. The firewall is enforced by
   the runtime, not by the operator.
5. **Portable Deployment** -- runs from a folder, a Tauri desktop binary,
   a Docker image, or a bare Python install. The Python interpreter and
   the project directory are the only hard requirements.
6. **Human-Documentable Change** -- the operator can record every incident,
   change, and rollback in a human-readable changelog without any cloud
   service, and the record is preserved in the same `04_Validation`
   directory as the audit outputs. The runtime, the front-end, and the
   Tauri shell **all share the same changelog file**.

## 4. The 00-99 Spatial Boundary Hierarchy

```
00  Strategy & Governance   -- axioms, mandates, SMART objectives, this document
01  Methodology             -- human-readable formulas, math, no code
02  Technical               -- machine-executable code (this is the program)
03  Vault                   -- durable data, evidence packs, registries
04  Validation              -- immutable audit logs, test outputs, legal outputs
99  Archive                 -- frozen snapshots for archival
```

The hierarchy is enforced on disk. Code lives in 02. Data lives in 03
and 04. Nothing crosses the boundary without an explicit copy through
a deterministic pipeline.

## 5. Operating Jurisdiction

- Commonwealth of Australia, Competition and Consumer Act 2010 (Schedule
  2 -- Australian Consumer Law)
- Evidence Act 1995 (NSW) -- Section 177 expert certificate
- Evidence Act 1995 (Cth) -- Section 79 opinion evidence
- Corporations Act 2001 (Cth) -- director duties, financial records
- Privacy Act 1988 (Cth) -- handling of any personal information

## 6. Build Acceptance Gates

The items in this section are **standing conditions** the build is held to,
not milestones that were once true and are now in the past. The marker
`[~]` means "operational and maintained": the build is held to this
condition on the rhythm in `04_Validation/MAINTENANCE_PLAN.txt` (daily,
weekly, monthly, quarterly, annual). A `[~]` item that has drifted is
an INCIDENT and is logged in `04_Validation/changelog.log` and
addressed in the next applicable cycle, not deferred.

A marker `[x]` (hard done) does not appear in this section. The build
is not meant to be finished; see section 7.

- [~] All Python source files import cleanly on a clean Python 3.12+
      install. Verified at the start of every quarterly cycle
      (STAGE_PAPER_QUARTERLY.txt part B) and at every deploy.
- [~] `pytest tests/` returns **73 passed + 0 skipped** on a
      fully-provisioned host (with `qwen3.5:9b` loaded in Ollama
      and FastAPI running on 127.0.0.1:3000) and **71 passed +
      2 skip-guard** on a source-only host. The two skip-guards
      are the Tauri junction test (`C:\OrderGetItRight` missing)
      and the Ollama tool-calling model test. The live counts and
      the laptop/SDXC distinction are recorded in
      `MAINTENANCE_PLAN.txt` §2.2 and re-verified on the daily,
      weekly, monthly, quarterly, and annual cycles.
- [~] `python -m src.audit_cli --help` prints a clean help screen.
      The CLI is exercised at least once per weekly cycle against
      the built-in EVAL-001..EVAL-008 cases
      (STAGE_PAPER_WEEKLY.txt step 2).
- [~] `python -m src.server:app` boots the FastAPI server on
      127.0.0.1:3000. The server must come up in under 10 seconds
      on the operator laptop. Boot time is logged in
      `04_Validation/logs/server_boot.log` when configured.
- [~] The web UI loads and all ten tabs function (Dashboard, Deception,
      BBFB, Valuation, Facts, Ledger, Evaluation, Batch, Affidavit,
      Changelog). The full tab walk is part of the smoke-test
      surface (`tests/test_smoke.py`, 28/28 cases).
- [~] The CLI audit run produces a Markdown report under `data/outbox/`.
      The output filename and the on-disk existence are checked
      after every weekly audit.
- [~] The deception ontology loads and the smoke test of every pattern
      passes against the labelled test cases. The pattern count is
      read from `DECEPTION_ONTOLOGY_VERSION` in
      `02_Technical/config/constants.py` (currently
      `3.9 (54 patterns)`). When the constant is bumped, the test
      re-derives the expected count from the version string and
      passes without a code change.
- [~] The Tauri shell (`02_Technical/tauri-shell/`) is wired and
      buildable on a host with Rust + Node.js + WebView2. The
      pre-built artefacts (`.exe`, `.msi`, `.nsis` installer in
      `02_Technical/tauri-shell/target/release/`) are refreshed at
      every release and the build is re-validated in the
      TAURI_BINARY_INVESTIGATION incident response.
- [~] The deployment script (`deploy/deploy.ps1`) provisions the
      runtime on a fresh Windows host without operator intervention
      after the first prompt. The dry-run path is exercised at
      every quarterly cycle
      (`tests/test_a5_deploy_dry_run.py`).

### 6.1 The Tests Boundary Exemption

The 00-99 hierarchy is strict: code in `02_Technical` may not import from
`03_Vault` or `04_Validation`, and tests may not import from `src/`.
Tests go through the HTTP API only, mounted via FastAPI TestClient.

There is **one and only one** legitimate exception to that rule:
`tests/` may import `from src.server.app import app` so the TestClient
can mount the FastAPI app object. The boundary test
`tests/test_00_99_boundary.py` enforces this exception explicitly via
a `TESTS_CAN_IMPORT_FROM = {"src.server.app.app"}` whitelist. Any
other `src.*` import in any test file is a hard failure. The whitelist
is the rule, not the override.

Pytest discovery and Python path are configured at the project root
in `pyproject.toml` and `conftest.py`. Removing either file breaks
`pytest` from the project root. Moving `tests/` out of the project
root breaks the boundary test. The two config files are part of the
build, not optional.

## 7. Status: Operational, Not Finished

The build is **operational**. The runtime engine works. The 54-pattern
deception ontology scans text deterministically. The BBFB engine
classifies facts under the four gates. The Optionality Lattice (formerly called the Real-Options binomial
lattice prices a fact under uncertainty. The Merkle truth ledger
seals every decision. The boundary test enforces the 00-99 spatial
hierarchy. The no-network audit enforces the air-gap constraint.
The no-black-box audit traces every output number to a file and
line. The five agents chain end-to-end. The Tauri shell wraps the
engine as a single double-clickable desktop binary. The agentic REPL
(Ollama tool calling) gives a third party a natural-language
interface to the same engine. The deploy script provisions a fresh
Windows host.

The build is **not finished**. It is not the goal that the build be
finished. The build is meant to be **maintained**, not shipped.

What "finished" would have meant, historically: every code path is
locked, every constant is final, every contract is fixed, every
test passes for a year, no more commits. That is a frozen artefact.
A frozen artefact decays: the laws change, the patterns evolve, the
third-party libraries age out, the operator's circumstances change,
the methodology itself improves. A frozen artefact is a liability.

What "operational, not finished" means:

- The build is **good enough to use today**. A third party can clone
  the source tree, run `python -m pytest tests/`, see 70 pass
  + 2 skip-guard on a source-only host (the Tauri junction test
  and the Ollama tool-calling model test; both are
  environment-dependent), and trust the engine. A third party can
  run `python -m src.verify_chain` and confirm the Merkle root
  matches the printed paper card.
- The build is **not promised to be good enough tomorrow**. The
  methodology is evolving. The constants can be bumped. The patterns
  can be added. The agents can be re-shaped. The Merkle chain
  records every change.
- The build is **maintained by a single operator on a defined
  rhythm** (see 04_Validation/MAINTENANCE_PLAN.txt: 15 minutes/day,
  2 hours/week, 4 hours/month, 8 hours/quarter, 16 hours/year). The
  rhythm is the contract. The chain is the proof.
- The build is **not promised to be perfect**. The agentic REPL uses
  a 1.5B parameter model. A larger model would answer better. The
  deploy script has a dry-run mode but a real clean-host test is
  still OPEN_ITEMS D1. The 1-2-3 backup plan has a paper card but
  the offsite test trip is a manual step.
- The build is **open to being wrong**. OPEN_ITEMS_AND_REFERENCE.md
  is the live list. The list is honest about what is unproven. The
  list is sealed to the chain so the next operator knows what the
  previous operator was uncertain about.

The build is a **living artefact**. It is the operator's working
notebook, audit log, and methodology. The chain is the operator's
proof that the artefact is what the operator says it is. The
printed paper card is the operator's last-resort recovery anchor.
The 1-2-3 backup plan is the operator's bet that the artefact
survives them.

The build is meant to be **used**, not displayed. The build is meant
to be **maintained**, not frozen. The build is meant to be **audited
by a third party**, not trusted on the operator's word alone. Every
claim in this document is verifiable from the source tree, the
constants file, the chain, and the chain re-derivation script.

## 8. Trust Anchors (added 2026-07-18, F11)

The project maintains **two trust anchors in parallel**:

1. **The Merkle chain** at `03_Vault/facts_registry.json` is the
   **audit-side trust anchor**. It is the tamper-evident witness of
   every state change the engine made. It is append-only. It is
   re-derivable by `python -m src.verify_chain`. The chain is the
   source of truth for *what the engine decided*.

2. **The Git repository** at the project root `.git/` is the
   **code-side trust anchor**. It records every committed change to
   the source tree. It is mutable (rebase-able). It is the source
   of truth for *what the operator committed*.

A defensible record requires BOTH. A source change in Git with no
chain block leaves the audit witness missing. A chain block with no
Git commit leaves the source diff unreviewed. The day-to-day
workflow in `04_Validation/GIT_WORKFLOW.md` enforces both.

The Merkle chain is the project-invariant. Git is a productivity

**Note on lattice framing (F7, 2026-07-18):** the 4th gate of the audit
pipeline is the *optionality* gate, not a valuation gate. The Cox-
Ross-Rubinstein binomial lattice is a stylised pricing model whose
inputs (S0=55.0, K1=18.0, K2=10.0) are hard-coded defaults in
`02_Technical/config/constants.py`. The orchestrator, the affidavit,
and the audit output all surface the `LATTICE_FRAMING` string so a
third-party reader cannot mistake the optionality index for a
business valuation. See `01_Methodology/REAL_OPTIONS_LATTICE.md`
section 6 for the operator-facing framing.

layer on top. If the two ever disagree (a commit-seal mismatch, a
rebase that re-orders the chain), the chain wins. The 1-2-3 backup
plan mirrors the source tree, not the chain -- the chain is
re-derivable from any clone that contains the unbroken tail.

