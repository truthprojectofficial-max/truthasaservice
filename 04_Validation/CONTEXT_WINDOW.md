# CONTEXT WINDOW

**Project:** Order Get It Right — Truth as a Service
**Version:** 1.0.0 (built 2026-07-12, fork-resolved 2026-07-16)
**Operator of record:** Justin Barnett, South Australia
**Generated:** 2026-07-16 (digest; re-derive at the start of every session)
**Purpose:** this is the document a future AI session (or a future
operator) reads first, in full, before doing anything else. It is
the window onto the project as of right now. Re-derive the live
state with the script in `04_Validation/scripts/_rederive_state.py`
or by running the four `python -c` snippets in section 2 below.

---

## 1. Project identity (one paragraph)

Order Get It Right is a deterministic business audit and valuation
program. It ingests business documents (contracts, warranties,
correspondence, evidence packs) and produces a five-pillar audit
verdict (Entropy, Deception Patterns, LAW Gates, GRACE Penalty,
CVS). The runtime is pure Python 3.12+, no network, no LLM in the
audit path. Every audit decision is sealed to a SHA-256 Merkle
chain at `02_Technical/03_Vault/facts_registry.json`. The
methodology is the operator's own: a 54-pattern deception
ontology (v3.9), a BBFB engine (LAW multiplicative veto + GRACE
quadratic penalty + FRUIT weighted product), a two-stage compound
binomial Cox-Ross-Rubinstein real-options lattice, and a 10% tau
extraction firewall. Jurisdiction is the Commonwealth of
Australia. The 00-99 spatial boundary hierarchy is enforced on
disk and by a boundary test in pytest. The build is "operational,
not finished" — it is meant to be maintained, not shipped. The
six non-negotiables are: absolute determinism, no black boxes,
truth ledger, tau firewall, portable deployment, human-documentable
change. The mission, scope, and build acceptance gates are in
`00_Strategy/STRATEGY.md`; the runtime contract is in
`00_Strategy/GOVERNANCE.md`; the IP-rights are in
`04_Validation/INTELLECTUAL_PROPERTY_RIGHTS.txt`; the maintenance
contract is in `04_Validation/MAINTENANCE_PLAN.txt`; the five
operator runbooks are `04_Validation/STAGE_PAPER_{DAILY,WEEKLY,
MONTHLY,QUARTERLY,ANNUAL}.txt`. The two handovers are
`04_Validation/HANDOVER_TO_{NEW_OPERATOR,AUDITOR}.md`. This
document is `04_Validation/CONTEXT_WINDOW.md`.

---

## 2. Live state (re-derive every session)

| Field | Value | How to re-derive |
|---|---|---|
| Block count | **2,797** | `python -c "import json; print(len(json.load(open('02_Technical/03_Vault/facts_registry.json'))['blocks']))"` |
| Merkle root | **3c33d6a18eee0c5935440ff2ebf9a3e675ab2297a2515f454493b1d972d140f5** | `python -c "import json; print(json.load(open('02_Technical/03_Vault/facts_registry.json'))['merkle_root'])"` |
| First block | 2026-07-11T17:15:10Z, #1 | from `merkle_stats()` or chain[0] |
| Last block | 2026-07-15T22:14:17Z, #2,797 (FORK_RESOLVED_2026_07_16) | from `merkle_stats()` or chain[-1] |
| Changelog lines | 25 (sha 2786e7fa53f23201...) | `wc -l 04_Validation/changelog.log` |
| Last changelog entry | "Wrote 2 handover documents..." (P5) | `tail -n 1 04_Validation/changelog.log` |
| Distinct event types | 36 | from `merkle_stats()["eventTypes"]` |
| Top 5 event types | JOB_QUEUED (677), JOB_CLAIMED (627), JOB_COMPLETED (574), FACT_ADDED (487), ASSISTANT_STARTED (174) | from `merkle_stats()["eventTypes"]` |
| Source tree (.py under 02_Technical) | 46 files | `find 02_Technical -name "*.py" -not -path "*__pycache__*" -not -path "*target*" | wc -l` |
| Tree shape (all files, excl. caches) | 186 files | `find . -type f -not -path "*__pycache__*" -not -path "*.pytest_cache*" -not -path "*node_modules*" -not -path "*target*" | wc -l` |

The numbers in this table are the values as of 2026-07-16. The
column "How to re-derive" gives the command. If a re-derivation
returns a different number, the project has changed since this
document was written; either the chain has grown (expected; the
number should be larger) or the project has drifted (the number
should be the same; if it isn't, the build is in a different
state than this document says).

### Six reference fingerprints (re-derived 2026-07-16)

| Ref | What | Value | Source |
|---|---|---|---|
| REF-1 | `02_Technical/config/constants.py` SHA-256 | `1f3879de1ae95521f732fc21754b0b73a5ef13b8083bb7cd88654d02ecbdb470` | constants |
| REF-2a | `00_Strategy/STRATEGY.md` SHA-256 | `b9850dd7655adfbf78cf07f7d1a6e2958a310c3d6b73b4d2d7a3be67787f10e3` | strategy |
| REF-2b | `00_Strategy/GOVERNANCE.md` SHA-256 | `0c2335de7e3e1962f30cacc3d12fe2921e8565287190c04d2dec01328f8f028d` | governance |
| REF-3 | source tree SHA-256 (46 .py files under 02_Technical, sorted, concatenated, hashed) | `4101295942b6d902a4cbe666171420ae3e7b9ffa0ef67b1452de1ff418013886` | code |
| REF-4 | tree shape SHA-256 (186 files, sorted relative paths joined by '\n') | `25cc89aef73419c8820493b8594c9cccb5266a52eafdbf5346d66d2c19aad852` | tree |
| REF-5 | Merkle root (live) | `3c33d6a18eee0c5935440ff2ebf9a3e675ab2297a2515f454493b1d972d140f5` | chain |
| REF-6 | composite (sha256 of REF-1..REF-5 concatenated) | `0354947d2ca0450970dae7090962ae19a0e5a1d8f0c775e05a8bbd9e0283351c` | composite |

The script `04_Validation/scripts/phase_4_refresh_fingerprints.py`
re-derives all six and writes the result to
`04_Validation/scripts/phase_4_fingerprints.json`.

> **Drift note:** the values in the chain payload of block 2,797
> (FORK_RESOLVED_2026_07_16) for REF-3 and REF-4 are from the time
> of that seal. They are stale by the count of .py and tree files
> added since. The current REF-3/REF-4 are the live values. This is
> expected: the chain records what was true at seal time; the live
> values are what is true now.

---

## 3. What changed in this session (2026-07-16)

The session that produced this document worked through a 5-phase
fork resolution, plus 4 priority tasks (P3-P6) that were on the
operator's list. Total: 25 files written. 2 chain seals. 4
changelog entries.

### Phase 1-5: Fork resolution (sealed)

The project had silently forked into two working copies: Copy A
(`C:\Users\justo\.claude\OrderGetItRight`, 2,977 blocks, root
`98a0b3aa...`) and Copy B (`C:\Users\justo\OneDrive\Documents\My
Project\OrderGetItRight`, 2,796 blocks, root `1dfadc3f...`). The
"missing" Tauri binary was in Copy A, not deleted. Resolution:

1. **P1 / Phase 1**: read 759-block chain/changelog gap.
   `04_Validation/RECONCILIATION_2026-07-16.md` (24,770 bytes).
   5 named OPEN_ITEMS_*_CLOSED blocks identified that the
   changelog missed.
2. **P2 / Phase 1**: traced Tauri binary to Copy A.
   `04_Validation/TAURI_BINARY_INVESTIGATION_2026-07-16.md`
   (17,769 bytes).
3. **Phase 2**: copied 8 files (8,864,089 bytes) from Copy A to
   Copy B. 3 Tauri artefacts re-hashed against block 1979 — all
   matched byte-for-byte. 5 SEAL/doc files copied.
4. **Phase 3**: appended `type: "fork_resolved"` entry to
   `changelog.log` (line 22 → 23, 1,797 bytes).
5. **Phase 4**: re-derived 6 reference fingerprints against Copy
   B. Refreshed `04_Validation/YELLOW_RIBBON.md` (2 occurrences
   of the Merkle root line updated).
6. **Phase 5**: **chain seal at block 2,797** with
   `FORK_RESOLVED_2026_07_16` event_type. Payload is the full
   machine-readable summary of phases 1-4 (8 files copied, 3
   Tauri matched block 1979, 6 fingerprints, D1 outstanding).
   New root: `3c33d6a18eee0c59...`. `verify_chain: MATCH`.

5 phase scripts written to `04_Validation/scripts/phase_{1..5}_*.py`.
3 phase reports: `phase_2_copy_report.json`,
`phase_3_changelog_report.json`, `phase_4_fingerprints.json`,
`phase_5_seal_report.json`.

### P3: data/inbox recreated

`data/inbox/` was missing from Copy B; the CLI would have failed
with the default `--inbox data/inbox` argument. Recreated with
6 files: `README.md` (folder contract), 4 `SEED_*.txt` templates
(template / warranty / reference / self-audit), `SEED_MANIFEST.txt`.
CLI test: 5/5 success, 0 errors, 0 warnings. Engine produced real
verdicts: SEED_001 flagged DD-009 "Lie of Certainty" at 85%
confidence, BBFB Compliant: NO. `changelog.log` line 23, 2,314
bytes.

### P4: 5 stage papers

`STAGE_PAPER_{DAILY,WEEKLY,MONTHLY,QUARTERLY,ANNUAL}.txt` (5 files,
38,839 bytes, 837 lines total). Each is a one-page operator runbook
companion to `MAINTENANCE_PLAN.txt`. They do not duplicate the
maintenance contract; they are the scannable checklist version.
`changelog.log` line 24, 1,730 bytes.

### P5: 2 handover documents

`HANDOVER_TO_NEW_OPERATOR.md` (10,981 bytes): orientation for the
heir. 5 steps — read the project from above, verify the chain,
re-derive the 6 fingerprints, seal an `OPERATOR_HANDOVER` block,
run the first daily cycle. The 4 non-negotiable constants and the
`CONSTANTS_BUMP` procedure are spelled out. The
if-the-previous-operator-has-died branch points at
`HARD_COPY_BACKUP_PLAN_1-2-3.txt` section 3 and the offsite
envelope.

`HANDOVER_TO_AUDITOR.md` (14,545 bytes): verification script for a
stranger. 30-minute basic check (chain match, 6 fingerprints,
changelog walk, pytest, IP-rights read) plus 4-hour full audit
(every doc, every constant, no-network claim, no-black-box claim).
Authority is `INTELLECTUAL_PROPERTY_RIGHTS.txt` clauses c, d, e.
The report is a single paragraph if everything passes.

`changelog.log` line 25, 2,706 bytes.

### P6: this document

`CONTEXT_WINDOW.md` — the window onto the project. Future AI
sessions start by reading this, then re-derive section 2, then
go.

---

## 4. What is open (the real list)

The honest list, ordered by severity.

### Documentation drift (low severity, fix in next session)

**STATUS: this drift is fixed in the same session that
wrote this section. The fix was sealed to the chain as
`STRATEGY_AMENDED_2026_07_16` + `MAINTENANCE_PLAN_AMENDED_2026_07_16`
at blocks 2798 + 2799, then refined at block 2800+
as `DOCS_PRECISION_FOLLOWUP_2026_07_16` to add the
laptop/SDXC distinction. The historical record below is kept
for traceability.**

- `00_Strategy/STRATEGY.md` §6 line 88 said "pytest tests/
  passes (28/28)". The test count moved 28→50→48→70 over the
  window between block 416 (2026-07-11 21:49, VERIFICATION_PASS)
  and the current session. STRATEGY.md and MAINTENANCE_PLAN.txt
  did not get the update. Live state (this session): 70 pass +
  2 skip-guard on a source-only host. The 2 skips are the Tauri
  junction test (C:\OrderGetItRight not present) and the Ollama
  tool-calling model skip (no tool-capable model loaded). On a
  fully-provisioned host with the junction present and a tool-
  capable Ollama model loaded, the suite passes 72/72. Fixed in
  this session: STRATEGY.md §6, MAINTENANCE_PLAN.txt §2.2/2.4/2.5,
  the 5 STAGE_PAPER_*.txt files, the 2 HANDOVER_*.md files,
  YELLOW_RIBBON.md, and the user-facing source strings in
  report_writer.py, deception_scanner.py, legal_affidavit_generator.py,
  onyx_cli.py, third_party_assistant.py, audit_review_agent.py,
  orchestrator.py, web/index.html, and RESOURCING.md.

- `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` PART 3 says
  constants SHA-256 is `d6f75ca89c5da4f93ec5c098a35d36c7...`
  and source tree is 43 .py files. The live REF-1 is
  `1f3879de1ae95521...` and live source tree is 46 .py files. Both
  drifted when the A5 seal bumped constants. PART 3 was sealed
  2026-07-11 (574 blocks); the live state is 2,797 blocks. PART 3
  is the snapshot at seal time; the live REF-1/REF-3 are the
  current values.

### Hardware-dependent (D1, OPEN_ITEMS_AND_REFERENCE.md §D)

- **D1** — USB clean-host restore test. The hard-copy backup plan
  has not been tested on a fresh Windows host. Requires a real USB
  stick + a Windows VM or second laptop. Cannot be done in a
  session; this is operator work. The first quarterly cycle that
  runs after a clean-host test exists closes D1.

### Operator-dependent (resourcing, the build's own list)

- The build is "operational, not finished" (`STRATEGY.md` §7). It
  is not a defect list; it is the design. Maintenance is the
  product. The 5 cycles are the contract.

### Items that have closed in this session

- The 759-block chain/changelog gap (P1). The 5 missed
  `OPEN_ITEMS_*_CLOSED` blocks are now documented in
  `RECONCILIATION_2026-07-16.md`.
- The "missing" Tauri binary (P2). It was in Copy A, not deleted.
  3 Tauri artefacts copied to Copy B; all 3 re-hashed against
  block 1979 and matched.
- `data/inbox/` recreated (P3). CLI re-runnable.
- 5 stage papers written (P4).
- 2 handover documents written (P5).
- CONTEXT_WINDOW written (P6, this document).

---

## 5. Where to read first (5-file orientation, in order)

A future AI session reads these five files, in this order, before
doing anything else. Total reading time: ~30 minutes.

1. `04_Validation/CONTEXT_WINDOW.md` — this document. The window
   onto the project.
2. `00_Strategy/STRATEGY.md` — the mission, scope, six
   non-negotiables, build acceptance gates, status. ~190 lines.
3. `00_Strategy/GOVERNANCE.md` — the runtime contract. Tau
   firewall, LAW gates, GRACE penalty, FRUIT, CVS, striking gate,
   five pillars, truth ledger, 10% promise. ~85 lines.
4. `04_Validation/MAINTENANCE_PLAN.txt` — the maintenance
   contract. 5 cycles, costs, incident response, the one-paragraph
   maintenance story. ~385 lines.
5. `04_Validation/INTELLECTUAL_PROPERTY_RIGHTS.txt` — the
   operator's reservations and the third party's rights. ~324
   lines.

After these five, the orientation is complete. The next reads
depend on the work in front of you:

- For audit work: `04_Validation/STAGE_PAPER_DAILY.txt` +
  `STAGE_PAPER_WEEKLY.txt`. Run the daily cycle; queue the audits
  for the weekly cycle.
- For a fork/inconsistency investigation: `RECONCILIATION_2026-07-16.md`
  + `TAURI_BINARY_INVESTIGATION_2026-07-16.md` are the templates.
- For an audit by a third party: `HANDOVER_TO_AUDITOR.md` is the
  verification script.
- For a successor taking over the project:
  `HANDOVER_TO_NEW_OPERATOR.md` is the orientation packet.

The build is portable. The orientation packet fits in the
session. The chain is the source of truth.

---

## 6. The 10-second summary

- **What:** deterministic business audit, no network, no LLM in
  the path, 5 pillars, 4 gates, 54 deception patterns, 10% tau
  firewall, Merkle chain, 00-99 boundary, ACL + Evidence Act 1995.
- **Where:** `C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\`.
- **Who:** Justin Barnett, sole operator, South Australia.
- **When:** built 2026-07-12, fork-resolved 2026-07-16.
- **State:** 2,797 blocks, root `3c33d6a18eee0c59...`, 25
  changelog lines, 46 source .py files, 186 tree files, 36
  distinct event types.
- **Open:** STRATEGY.md test-count drift was fixed in this
  session and sealed; D1 USB test (operator work) and the
  build's own design intent that it is maintained, not finished.
- **Next session:** re-derive section 2, then read whichever of
  the orientation files matches the work in front of you.
