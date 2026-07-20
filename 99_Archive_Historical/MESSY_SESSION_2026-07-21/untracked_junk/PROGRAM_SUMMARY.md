# Order Get It Right -- Program Summary

**Date:** 2026-07-20
**Live state:** 26,594 blocks, Merkle root
`22f0809d24610ab98106559f203c1c5ec86c5a3c69fb1faec779daa765a6ec79`,
chain MATCH. 253 tests collected. Operator: Justin Barnett.
**Purpose of this document:** a single-page, plain-English summary of what
the program IS, what it DOES, what state it is in, and what is left to do.
It is the document to hand to a new operator, an auditor, or yourself in
six months. It is NOT the source of truth -- the Merkle chain is. This is
the human-readable map of it.

> Read this first, then `04_Validation/INTRODUCTION.md` for the 5-minute
> first-run, then `04_Validation/INSTRUCTION_AND_CARE_MANUAL_2026-07-20.md`
> for the daily-care and break/fix guide.

---

## 1. What the program is (one paragraph)

**Order Get It Right -- "Truth as a Service"** is a deterministic business
audit and valuation program. You hand it business documents (a supplier
quote, a product spec, an invoice, a contract) and it returns a
legally-grounded verdict -- GO / DEFER / TEST FIRST / REJECT -- backed by a
Section 177 affidavit and a Section 56 ACL demand letter. It has no black
box: every formula lives in `01_Methodology/` as human-readable maths. It
makes no network call and runs no hosted model in the audit loop. Every
decision is sealed to a SHA-256 Merkle chain so the audit trail is
tamper-evident. It runs as a Python web server or a double-clickable Tauri
desktop binary; both run the same engine, so a verdict is identical on
either surface. Operator: Justin Barnett. Jurisdiction: Commonwealth of
Australia. Version 1.0.0.

## 2. What it does (the seven steps)

1. **Ingest** any business document (.txt, .docx, .pdf).
2. **Extract** structured evidence -- price, spec, warranty, compliance --
   via deterministic regex extractors (no ML).
3. **Run the four-gate pipeline:**
   - **Deception Gate** -- 54-pattern ontology v3.9 + Shannon entropy
     (anomaly threshold 4.5 bits/char). A CRITICAL pattern short-circuits
     to REFUSED.
   - **BBFB Gate** -- LAW (multiplicative veto) + GRACE (quadratic
     penalty, coefficient 2.0) + FRUIT (weighted composite) + CVS
     (composite value score, threshold 0.0005).
   - **Real-Options Gate** -- two-stage compound binomial lattice
     producing a deception-adjusted **optionality index** (NOT a business
     valuation -- the inputs are hard-coded defaults; the orchestrator
     surfaces the `LATTICE_FRAMING` string on every response).
   - **Decision Gate** -- GO / DEFER / TEST FIRST / REJECT.
4. **Generate** Markdown, PDF, and DOCX reports.
5. **Draft** a Section 56 ACL demand letter and a Section 177 Affidavit.
6. **Seal** every action to the Merkle truth ledger (`03_Vault/`).
7. **Record** every operator-observed incident/change to a human-readable
   changelog (`04_Validation/changelog.log`).

The ledger proves what the engine decided; the changelog records what the
operator noticed. Both are required.

## 3. The two delivery shapes, one engine

| Surface | What you run | How to build |
|---------|--------------|--------------|
| **Python web server** | `python -m uvicorn src.server.app:app --port 3000` | `deploy\deploy.ps1` |
| **CLI batch audit** | `python -m src.audit_cli --inbox <dir> --outbox <dir>` | `deploy\deploy.ps1` |
| **Tauri desktop** | Double-click `OrderGetItRight.exe` | `deploy\build-tauri.ps1` |

A verdict on the Python install is byte-identical to one in the Tauri shell.

## 4. The directory layout

```
00_Strategy\      Governance charter and operating mandate
01_Methodology\   Human-readable mathematics (no code)
02_Technical\     Python engine + Tauri shell + web UI
   config\        constants.py (named constants), exceptions.py
   src\           runtime: agents/, engines/, io/, server/, utils/
   tauri-shell\   Rust + JS desktop binary
   web\           single-file HTML/JS UI
03_Vault\         facts_registry.json + facts_chain.jsonl (Merkle chain)
                  job_registry.json + job_chain.jsonl (delegator state)
04_Validation\    changelog, audit log, reports, handovers, care manual
99_Archive\       frozen snapshots
data\             sample inboxes, default outbox
deploy\           deploy.ps1, build-tauri.ps1
tests\            pytest suite (253 tests)
```

## 5. The ten named modules

Five core agents (`02_Technical/src/agents/`):
- **Form_Entry_Agent** -- draft a fact from operator input
- **Audit_Review_Agent** -- 54-pattern deception scan (v3.9)
- **Lattice_Compute_Agent** -- real-options binomial lattice
- **Ledger_Seal_Agent** -- Merkle seal to the chain
- **Affidavit_Agent** -- Section 177 certificate

Five support modules:
- **InventoryAgent** -- inbox/outbox tracking
- **MonitorAgent** -- incident briefing
- **Orchestrator** -- the 4-gate pipeline
- **AgentJobDelegator** -- MCP job dispatcher
- **TauFirewall** -- 10% extraction ceiling

## 6. Current state (2026-07-20, live)

| Indicator | Value | Status |
|-----------|-------|--------|
| Chain | 26,594 blocks, root `22f0809d...65a6ec79` | MATCH (intact) |
| Tests collected | 253 | (full suite; ~1 host-dependent skip) |
| Fast suite | 52 passed, 1 warning | green |
| Production job vault | tail 4929 == registry 4929 == 4929 jobs | no drift |
| Last seal | `CODE_REVIEW_SEALED_2026_07_20` (block 26594) | the 2026-07-20 review |
| Network | none in audit loop | `AUDIT_NO_NETWORK.md` proves it |
| 10% promise | tau ceiling enforced | binding per GOVERNANCE s9 |

## 7. The non-negotiables

1. **Determinism** -- same input + same config = same verdict on any host.
2. **No black boxes** -- every formula is in `01_Methodology/`.
3. **Truth ledger** -- every action sealed to a SHA-256 Merkle chain.
4. **Tau firewall** -- 10% extraction ceiling is enforced.
5. **Portable** -- Python install or Tauri binary; same engine.
6. **Human-documentable** -- every change and incident recorded with the
   `bin_id` of the exact binary that was running.

## 8. What is left to do (the honest list)

Carried forward from `TODO_FULL.md` and the 2026-07-19/20 handovers. The
code-doable items are done; what remains is operator-dependent or outward.

| Item | Status | Who |
|------|--------|-----|
| Tauri code-signing ($200-500/yr) | OPEN (operator decision) | operator |
| Second-PC clean-host restore test | OPEN (needs 2nd Windows PC) | operator |
| Gmail .mbox import | OPEN (Google Takeout requested, awaiting delivery) | operator |
| More real-world audit cases (the outward move) | OPEN | operator |
| Job-journal concurrency + tail-count bugs | CLOSED 2026-07-20 (this session) | done |

## 9. The six reference fingerprints (how a third party proves "this is the project")

Re-derive with `python -m src.verify_chain --print-refs` from
`02_Technical/`. The six are: REF-1 constants.py, REF-2a STRATEGY.md,
REF-2b GOVERNANCE.md, REF-3 source tree, REF-4 tree shape, REF-5 live
Merkle root, REF-6 composite. See `OPEN_ITEMS_AND_REFERENCE.md` Part 3.

End of summary. The chain is the source of truth; this is the map of it.