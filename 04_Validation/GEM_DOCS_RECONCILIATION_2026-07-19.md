# Gem Documents Reconciliation — 2026-07-19

Operator: Justin Barnett
Build agent: hermes-glm-5.2-cloud
Branch: `ogir-build-2026-07-18`

Subject files reviewed (operator-supplied external drafts, FYI context,
and one held PDF):

  A. `C:\Users\justo\OneDrive\Documents\My Project\Gemini Gem Knowledge Base Configuration.txt`
  B. `C:\Users\justo\OneDrive\Documents\My Project\Gem Senior AUDIT RESULTS..txt`
  C. `C:\Users\justo\Downloads\Unifying Human Value in BBFB Audits.pdf`  (FYI)
  D. `C:\Users\justo\OneDrive\Documents\er Get It Right Deterministic Audit.txt`  (FYI, NotebookLM export of an OGIR audit chat)

---

## 0. Live project state at assessment (re-derived this session)

- Tests: **213 passed, 1 skipped, 1 warning** (115.56s) on Python 3.14.6.
- Chain verify: **MATCH** (against the working-tree vault — see §6 caveat).
- Branch: `ogir-build-2026-07-18`; last commit `2faa4b2`
  (HANDOVER_REFRESHED_2026_07_19).
- Git remote: `usb` → `/d/OrderGetItRight.git` (bare repo, push works).
- Canonical committed vault (git HEAD): **16,475 blocks**, root
  `f39a1cc144f71f19f71fe1cd3764ee8f0576add8dfdeeb876a242ad37f26514a`,
  first block 2026-07-11T17:15:10Z, last 2026-07-18T15:03:15Z.
- Working-tree vault (OneDrive): **383 blocks**, root
  `b93bfdafefffdc2819dcba9bb99030632088027c2fa16d475804b24ce4f523e1`
  — re-seeded at 2026-07-18T15:09:16Z (see §6; the only material
  integrity issue surfaced this session).
- USB working copy vault (`D:\OrderGetItRight\03_Vault\`): **7,156 blocks**,
  root `0fe4872733fb402bbe8dc14e6543a702f901118e6130549304de156bf48ac7c7`,
  last 2026-07-17 — stale relative to Git HEAD; the bare remote
  `usb` is the air-gap-correct backup, not the USB working copy.
- Ontology: 3.10, 54 patterns, R1-R4 + R5 applied.
- EVAL suite: 109 extended cases + AI-legal + legacy = 214 collected
  (213 pass + 1 host-dependent skip on the live server guard).
- All four of the "STEP 1-4" items in OPEN_ITEMS_AND_REFERENCE.md
  were already CLOSED on 2026-07-18 (Makita citation, R5-EXTENDED-2
  legal register gate, lexical-set audit/EVAL expansion, Git remote).

## 1. What each document is

**A. Gemini Gem Knowledge Base Configuration.txt** — a Gemini "Gem"
configuration spec. It defines a `PM Source Architect: Deterministic
Edition` Gem that converts local OGIR files into RAG-optimized
Markdown for NotebookLM. It bundles: a directory overview, a
data-tier comparison table, a 54-pattern ontology excerpt, Gem
rules 1-9, a Stackelberg signaling utility, a MarkItDown comparison
table, and a first-time initialization prompt. Marked "Project
name OderGetitRight.txt" as the source citation, with NotebookLM
guide and aibuilderclub blog references dated 2026-07-18.

**B. Gem Senior AUDIT RESULTS..txt** — a Gemini "Gem Senior"
conversation. The first half is a statutory/algorithmic mapping
(ASQM/ASA/ISO 19011/IIA/ISO 42001/NIST AI RMF/Corporations Act
s 336). The second half is a "Zero-AI Spatial Architecture
Mandate" audit of a Google Drive `PROJECT 2` folder, concluding
that folder is "non-compliant" and prescribing a 00-99 numerical
hierarchy + ISO-date filename protocol.

**C. Unifying Human Value in BBFB Audits.pdf** (16 pages) —
"High-Assurance Sovereign Audit Architecture: Unifying
Mathematical Telemetry with Human-Centric Quality of Life Worth
Curves." Maps the BBFB/Lattice telemetry onto a five-dimension
Systemic Quality of Life (S-QoL) harness derived from EQ-5D +
MCDA + MAPS. Includes a law.json parameter table, Landauer's
Principle framing, the 10% Tau extraction ceiling, the
2,679-block ledger claim, and a Health State Utility Weight /
Systemic Well-Being utility curve.

**D. er Get It Right Deterministic Audit.txt** — a NotebookLM
export of an OGIR audit Q&A. 794 lines covering: top-3 critical
areas (persistence "memory hole", placeholder NIZK proofs, thin
EVAL base), Schnorr/Fiat-Shamir requirements, Truth Ledger
integration, "one common auditor?" framing, the 4-gate
pipeline, case uses (Nissan D40, Audio ACL §56, Selby), unified
engine status, BBFB/CVS math, governance audit, S-QoL dimensions,
Shannon entropy, a "research prompt," and a "Master Build
Directive: Production Sovereignty Phase."

## 2. Compliance-word-density screening

Heuristic from `references/compliance-word-density-detector.md`
(high obligation/softener ratio >10, framework density >1.5%,
sentences >18 words/sentence predict fabricated/stale compliance
language):

| Doc | words/sent | obligation % | frameworks % | ob/soft ratio | verdict |
|---|---|---|---|---|---|
| A. Gem Config | 15.2 | 0.86% | 0.00% | 6.0 | borderline-dense, low framework |
| B. Gem Senior | 20.9 | 1.53% | 3.61% | 31.0 | **fires all four signals** |
| D. Deterministic Audit (NotebookLM) | 13.4 | 0.62% | 0.00% | 7.8 | moderate; section-by-section review needed |

Doc B is a repeat offender — same 31.0 ob/soft ratio and 2.79-3.61%
framework density band it had on 2026-07-18 (per
COMPLIANCE_WORD_DENSITY_HEURISTIC_2026-07-18.md). Treat as a
draft external claim, not authoritative project state.

## 3. Claims vs live state — reconciliation table

### A. Gemini Gem Knowledge Base Configuration.txt

| Claim in doc | Live state | Status |
|---|---|---|
| "exactly 3,033 blocks" Merkle ledger | Git HEAD has 16,475; USB working copy 7,156; working tree 383 (re-seeded) | **STALE** — 3,033 traces to the older `phase_4_fingerprints.json` snapshot, not the live vault |
| Merkle root `26501872d1a9d419...` | Live root `f39a1cc1...` (HEAD); `b93bfdafe...` (working tree) | **STALE** — root does not match any current vault copy |
| `facts_registry.json` loaded "entirely into the memory stack on startup" | Confirmed: `vault_io` reads/writes the whole JSON file per block; O(N); single-worker only | **ACCURATE** — known scaling bottleneck (documented OPEN_ITEM, F1) |
| SQLite migration roadmap via `better-sqlite3` | Not implemented; vault remains a flat JSON file. `better-sqlite3` is a Node.js library, not pure-Python | **ASPIRATIONAL** — and the `better-sqlite3` choice conflicts with OGIR's pure-stdlib-python discipline (Pitfall 9: storage durability ≠ determinism) |
| Azure Files `validation-vault-share` in `australiaeast` | No Azure integration exists in the tree; OGIR is air-gapped by design | **ASPIRATIONAL / contra air-gap** — see `references/azure-independent-node-analysis.md` |
| "54-pattern Deception Ontology (v3.9)" | Live: v3.10, 54 patterns | **STALE** (version only) |
| DD-001 through DD-008 as the "8-rule core" | Live ontology has 54 patterns; the 8 listed are real but a small subset | **PARTIAL** — doc itself later says "54-pattern"; the "8-rule core" framing is misleading |
| Shannon entropy human baseline 3.8-4.3 bpc, anomaly H>4.5 triggers VETO | Matches `deception_scanner.py` and the PDF (Doc C) | **ACCURATE** |
| `deception_scanner.py` location "or within groknett_core.py" | No `groknett_core.py` exists in the live tree; the scanner is at `02_Technical/src/engines/deception_scanner.py` | **STALE / phantom file** |
| Knowledge base file list includes `validation_vault_share` under `04_Validation\` | No such file exists; `04_Validation/` contains docs and `scripts/`, no Azure share config | **FABRICATED** |
| Gem Rule 8 "Causal Graph Modeling... collider graph (CBN logic)" and Rule 9 "Failure First Planner" | These are Gem-behavior rules, not OGIR engine features | **Non-claim** — describes the Gem, not the project |
| MarkItDown F1 82%, 12s/100pp, no GPU | Plausible external benchmarks; not verifiable from OGIR sources | **External claim, unverified** — within scope of the Gem doc, not OGIR |

### B. Gem Senior AUDIT RESULTS..txt

| Claim in doc | Live state | Status |
|---|---|---|
| s 336 Corporations Act 2001 anchors ASQM 1/2, ASA 102, etc. | s 336 is real (auditor obligations) but does not directly "anchor" ASQM 1/2; ASQM is AUASB-standard-based, not statute-anchored | **LEGALLY IMPRECISE** — same finding as 2026-07-18 GEMINI_WRONG_CLAIM_ANALYSIS |
| ISO 19011 "seven core tenets" (Integrity, Fair Presentation, Due Professional Care, Confidentiality, Independence, Evidence-based, Risk-based) | ISO 19011:2018 §5 lists these as audit principles (§5.2); the count and names are broadly right | **ACCURATE** — but verify against the standard before citing in a sealed doc |
| IIA "4 C's: Competence, Confidentiality, Communication, Credibility" | The IIA Global Internal Audit Standards use different framing; the "4 C's" is not a canonical IIA taxonomy | **UNVERIFIED / likely fabricated taxonomy** |
| NIST AI RMF four functions: Govern, Map, Measure, Manage | Matches NIST AI RMF 1.0 Core | **ACCURATE** |
| "70/30 rule of AI development" | No such rule exists in NIST AI RMF, ISO/IEC 42001, or AUASB guidance | **FABRICATED** — appears invented to add authority |
| ISO/IEC 42001 PDCA lifecycle | ISO/IEC 42001:2023 §10.1-10.2 references continual improvement; PDCA is the AI management system's framing | **ACCURATE** |
| "Promptfoo" as TEVV tool | Promptfoo is a real LLM eval framework | **ACCURATE** |
| "audit of PROJECT 2 directory shows naked `__pycache__, requests, rich, util, commands` folders" | Those folders are not part of OGIR's `02_Technical/` layout; OGIR has no `requests`/`rich`/`commands`/`util` at its root | **NON-SEQUITUR** — the audit target is a different (Google Drive) project, not OGIR; the doc conflates them |
| Prescribes "00-09 / 10-19 / 20-29 / 30-39 / 40-49" five-tier scheme | OGIR uses `00_Strategy / 01_Methodology / 02_Technical / 03_Vault / 04_Validation` — a four-tier scheme, not the five-tier `00-09...40-49` banding the doc prescribes | **PRESCRIPTION MISMATCH** — OGIR's hierarchy is not "non-compliant" with the doc's invented standard; the doc's standard is not the project's standard |
| "ISO Date Mandate: every filename begins YYYY-MM-DD" | OGIR does not use this convention (e.g. `OPEN_ITEMS_AND_REFERENCE.md`, `AGENTS.md`) and is not bound to | **PRESCRIPTION not grounded in any cited standard** |

### C. Unifying Human Value in BBFB Audits.pdf (FYI)

| Claim in doc | Live state | Status |
|---|---|---|
| "2,679-block persistent ledger" | Git HEAD: 16,475; USB working: 7,156; working tree: 383 | **STALE** — older than any live copy |
| S-QoL five dimensions (Systemic Vitality, Structural Integrity, Transactional Execution, Operational Morbidity, Systemic Vulnerability) mapped to EQ-5D | The five dimensions are defined in the PDF itself and in Doc D; OGIR's `GOVERNANCE.md` / `STRATEGY.md` do not implement an S-QoL harness — this is a proposed interpretive layer, not an engine feature | **PROPOSAL / not implemented** |
| `03_Vault/law.json` holds striking gate variables | `03_Vault/law.json` exists (per project layout) | **ACCURATE** for the file; values would need re-derivation to confirm |
| Landauer's Principle, 86 kcal/page "somatic backpressure", Tau extraction ceiling ≤0.10 | The Tau ceiling is a real OGIR invariant (constants.py); the 86 kcal figure and Landauer framing are interpretive additions in the PDF, not engine code | **MIXED** — Tau ceiling is real; kcal/Landauer is narrative |
| Health State Utility Weight + concave SWB utility curve with risk aversion γ | Proposed in the PDF; not in `01_Methodology/MATHEMATICS.md` or `02_Technical/src/engines/` as implemented math | **PROPOSAL** |

### D. er Get It Right Deterministic Audit.txt (FYI NotebookLM export)

| Claim in doc | Live state | Status |
|---|---|---|
| "8 EVAL cases" / "thin empirical base" | Live: 109 extended cases + AI-legal + legacy = 214 collected; 53 of 54 patterns covered | **STALE** — closed by LEXICAL_SET_AUDIT batches A-D + EVAL_SUITE_EXTENDED on 2026-07-18 |
| "54-pattern ontology v3.9" | v3.10 (R1-R4 + R5 applied) | **STALE** (version only) |
| "Placeholder NIZK proofs; SHA-256 integrity_digest only" | Confirmed — `vault_io.append_block` writes `integrity_digest` as SHA-256 of canonical payload + PROJECT_OPERATOR; no Schnorr/Fiat-Shamir | **ACCURATE** — and the project position is that the SHA-256 digest is the deterministic witness, not a placeholder for NIZK (F6 renamed the field for accuracy in commit 76297ee's lineage) |
| "v3.10 with structural co-text gates" | Confirmed — R1-R4 + R5-EXTENDED-2 gates live in `deception_scanner.py` | **ACCURATE** |
| "static regex is computationally weak; AST parsing required" | OGIR uses case-insensitive substring + co-text gates; no AST parsing of ingested text is implemented. The OGIR position is that the R-gates handle lexical near-misses and that AST parsing is not a current requirement for the audit-text use case | **PARTIALLY ACCURATE** — describes the doc's target spec, not the live engine; the engine's position is documented |
| "facts_registry.json is an in-memory ephemeral sql.js footprint" | **Wrong on two counts**: (a) it is a flat JSON file, not `sql.js`; (b) it is durable on disk, not ephemeral. The scaling bottleneck is real, the medium is mis-described | **INACCURATE** — `sql.js` does not appear anywhere in OGIR |
| "Composite prime failure — candidate prime q is composite, fails Fermat/Miller-Rabin" | The OGIR integrity_digest is a SHA-256 hash, not a discrete-log signature; there is no prime `q` to test. This finding appears to be about a *different* proposed NIZK implementation, not the live code | **NON-SEQUITUR** — applies to a hypothetical Schnorr implementation, not the shipped digest |
| "19 hardcoded constants claimed vs 35+ in constants.py" | Live: **41 named constants** (per AGENTS.md and `config/constants.py`); both the "19" and "35+" figures are stale | **STALE** on both sides |
| "65% Visual Echo" / legacy UI strings | UI was rewritten 2026-07-17 (single-page operating surface); the "65%" strings were already purged in that seal | **STALE** — closed |
| Tauri binary `order-get-it-right.exe` exists, NotSigned | Confirmed — built 2026-07-17, sha256 `791bb7b9...`, unsigned (F10 OPEN, operator decision) | **ACCURATE** |
| "Master Build Directive: Production Sovereignty Phase" prescribing `better-sqlite3`, Schnorr, AST parsing, Tauri rebuild | This directive is **aspirational** — none of those four items is on the current OPEN_ITEMS list as a code change; the live position is F7-deep (wire lattice to evidence), hardcopy refresh, Tauri signing, clean-host test, Gmail .mbox | **ASPIRATIONAL** — would re-open closed decisions |
| `02_Technical/src/engines/sovereign_core_v3.py`, `01_Core_Engine/deterministic_decision_layer.py`, `03_Domain_Modules/d40_forensics/`, `03_Domain_Modules/selby_forensics/` | None of these paths exist in the live tree; the engine lives at `02_Technical/src/engines/bbfb_engine.py`, `02_Technical/src/engines/real_options_lattice.py`, etc. There is no `01_Core_Engine/` or `03_Domain_Modules/` directory | **FABRICATED paths** — the audit describes a different file layout than the live tree |
| "Makita v Sprowles [2001] NSWCA 305" must be embedded in affidavit generator | **CLOSED 2026-07-18** — citation embedded in `legal_affidavit_generator.py`; the doc's "remediation step" is already done | **STALE / closed** |
| "EVAL suite expansion to 30+ cases" | **CLOSED 2026-07-18** — 109 extended cases | **STALE / closed** |

## 4. Fabricated-compliance tells in Doc B (Gem Senior)

Beyond the density score, Doc B exhibits the structural tells
from `AI_COMPLIANCE_FABRICATION_TELLS_2026-07-18.md`:

1. **Invented authority**: the "70/30 rule of AI development" and the
   IIA "4 C's" (Competence, Confidentiality, Communication,
   Credibility) do not appear in the cited frameworks. They are
   presented with the same binding tone as real NIST/ISO clauses.
2. **Scope drift**: it audits a Google Drive `PROJECT 2` folder
   (`__pycache__`, `requests`, `rich`, `util`, `commands`) and
   then prescribes a 00-99 hierarchy as if that prescription
   applied to OGIR — but OGIR already uses a 00-99 hierarchy of a
   different (four-tier) shape, and the audited folder is not OGIR.
3. **Obligation without section**: "must implement", "must deploy",
   "must enforce" appear throughout without pinning a clause of
   ASQM 1, ISO 19011, or ISO/IEC 42001. When a section is named
   (s 336), the anchoring claim is imprecise.
4. **Status inflation**: "FULLY COMPLYING" is presented as a binary
   the project can reach by following the roadmap. OGIR's position
   (AGENTS.md, GOVERNANCE.md) is that it is an auditable
   deterministic tool, not a system that "fully complies" with
   statutory audit standards — that framing overclaims.

## 5. What is actually not done (per live OPEN_ITEMS + handover)

The only genuinely OPEN items on the live project (from
`HANDOVER_NEXT_SESSION_2026-07-18.md` and the 2026-07-19 commit):

1. **F7-deep**: wire lattice inputs to extracted evidence (defer; LOW).
2. **Hard-copy reference card refresh**: update QUICK_REFERENCE_CARD
   Merkle root + test count (LOW, 15 min).
3. **Tauri code-signing**: $200-500/yr, operator decision (LOW).
4. **Second-PC clean-host restore test (D1-TRUE)**: needs a second
   Windows PC (MEDIUM).
5. **Gmail .mbox import (E1)**: operator must export
   truthproject.official@gmail.com to a local .mbox (LOW).

Everything else in the supplied drafts (Schnorr NIZK, AST parsing,
SQLite migration, Azure Files, 2,679/3,033/16,475 block counts
except the live Git HEAD figure, "65% visual echo", "8 EVAL
cases", Makita citation, R5 legal register gate, EVAL expansion,
Git remote) is either STALE, ASPIRATIONAL, FABRICATED, or already
CLOSED.

## 6. Integrity anomaly discovered during reconciliation (ACTION NEEDED)

While running the verification triad I found that the working-tree
`03_Vault/facts_registry.json` does NOT match the canonical vault
committed at git HEAD:

| Copy | Blocks | Root | First block | Last block |
|---|---|---|---|---|
| Git HEAD (committed) | 16,475 | `f39a1cc144f71f19...` | 2026-07-11T17:15:10Z FACT_ADDED | 2026-07-18T15:03:15Z SHUTDOWN |
| USB bare remote (`usb`) | 16,475 | `f39a1cc144f71f19...` | same | same |
| USB working copy (`D:\OrderGetItRight`) | 7,156 | `0fe4872733fb402b...` | 2026-07-11 | 2026-07-17 |
| **Working tree (OneDrive)** | **383** | `b93bfdafefffdc28...` | 2026-07-18T15:09:16Z SHUTDOWN (re-seeded, index=1, prev=0000) | 2026-07-19T11:08:57Z SHUTDOWN |

The working-tree vault was **re-seeded** at 2026-07-18T15:09:16Z —
four minutes after the last committed block. Block 1 is a SHUTDOWN
with `previous_hash = 0000...`, i.e. a fresh chain. The 383
blocks now in the working tree are SHUTDOWN/seed blocks produced
by pytest/server runs since the re-seed. `verify_chain` reports
MATCH because it verifies the (truncated, re-seeded) chain
against itself — the canonical 16,475-block history is NOT in
the working tree.

**The canonical chain is not lost**: it is preserved in git HEAD
and pushed to the `usb` bare remote. The USB working copy is
stale (2026-07-17) but intact.

**Most likely cause**: a test or server start on a clean working
tree (after `git checkout` or a OneDrive sync event) ran
`_seed_facts_once()` on an empty/missing vault and re-seeded
from block 1, instead of loading the existing 16,475-block file.
The `_atomic_write_json` resilience patch
(UI_API_PATH_FIX_AND_VAULT_LOCK_RESILIENCE_2026_07_18) may have
masked a write failure by writing to a fresh file.

**Impact**: any seal applied to the working tree right now would
append to a 383-block chain, not the canonical 16,475-block
chain. That would fork the audit history. Do NOT seal anything
until the working-tree vault is restored.

**Recommended fix** (one command, no seal yet):
```
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
git checkout HEAD -- 03_Vault/facts_registry.json 03_Vault/job_registry.json 03_Vault/affidavit_transcript.txt
cd 02_Technical
python -m src.verify_chain
```
Expected: 16,475 blocks, root `f39a1cc1...`, MATCH. Then the
working tree is back on the canonical chain and sealing can
resume. The 383 SHUTDOWN blocks produced since the re-seed are
test artefacts, not audit decisions, and do not need to be
preserved.

**Root-cause follow-up** (separately, after restore): add a
guard to `_seed_facts_once()` / `vault_io.append_block` that
refuses to seed block 1 if a `facts_registry.json` exists in
git HEAD with a non-zero block count, and/or refuse to
over-write a non-empty vault file with a seed block. This
prevents the same re-seed from happening again.

## 7. Recommendations

1. **Restore the working-tree vault** from git HEAD before any
   build work (§6). This is the only blocking action.
2. **Do not action any of the four drafts' "remediation steps"
   as build directives.** They are external claims about OGIR,
   not OGIR's own backlog. The live OPEN_ITEMS list (§5) is the
   backlog.
3. **File the drafts under `04_Validation/external_drafts/`**
   (or leave them where they are) with a pointer to this
   reconciliation. They are useful as historical context for the
   Gem/NotebookLM workflow, not as authoritative state.
4. **Keep the project position on NIZK/Schnorr**: the
   `integrity_digest` is the deterministic witness (SHA-256 of
   canonical payload + operator identity), not a placeholder
   for a discrete-log NIZK. Do not re-open F6. If a real Schnorr
   proof is ever wanted, it must be a fresh OPEN_ITEM with a
   pure-Python constraint — not a "remediation" of a "missing"
   feature.
5. **Keep the project position on storage**: SQLite/Azure Files
   are durability features, not determinism features. The
   air-gap guarantee precludes Azure Files by design. Any
   storage change must preserve pure-stdlib-Python and the
   no-network invariant.
6. **For the Gem config (Doc A)**: if the operator still wants
   a RAG Gem for NotebookLM, update the block count and root to
   the live figures (16,475 / `f39a1cc1...`), drop the
   `groknett_core.py` reference, drop the `validation_vault_share`
   knowledge-base row, and mark SQLite/Azure as "aspirational,
   not implemented" before ingestion. Otherwise NotebookLM will
   ingest stale state as if it were current.

## 8. Verification

This document was produced by re-deriving every project-state
claim from the live tree. The compliance-word-density detector
script was run on all three text drafts. The PDF was extracted
with PyMuPDF (system Python 3.14.6). The vault anomaly in §6
was found by comparing the working-tree, git-HEAD, USB-bare,
and USB-working vaults.

No source change, no chain seal. This is a reconciliation
report. The operator should restore the working-tree vault
(§6) before any seal is applied to the next change.

---

End of reconciliation.