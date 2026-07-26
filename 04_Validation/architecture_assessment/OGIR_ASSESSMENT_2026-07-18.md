# Order Get It Right -- Comprehensive Software Development Assessment

**Reviewer:** Hermes Agent (cloud model, glm-5.2:cloud) on behalf of operator Justin Barnett
**Date:** 2026-07-18 (UTC)
**Subject:** `C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight`
**Method:** Read-only review. No files were modified by the reviewer. The architecture diagram
`04_Validation/OGIR_ARCHITECTURE_DIAGRAM.html` was generated as a deliverable.
**Companion artefacts:**
- `04_Validation/OGIR_ARCHITECTURE_DIAGRAM.html` -- dark-themed SVG architecture diagram
- `04_Validation/OGIR_ASSESSMENT_NOTES_2026-07-18.md` -- short-form record-keeping note

This assessment was requested after the previous attempt (logged in
`Windows PowerShell 5.1.txt`) failed: local Ollama models (qwen3.5:9b, llama3.1:8b,
gemma4:12b) repeatedly hit `finish_reason='length'` truncation and could not complete
the analysis. The current run uses a cloud model with a larger output budget.

---

## 1. Executive Summary

Order Get It Right (OGIR, "Truth as a Service") is a single-operator, deterministic,
air-gapped business audit and valuation engine written in pure-stdlib Python 3.12+.
It ingests business documents, runs a 4-gate pipeline (Deception -> BBFB -> Real-Options
Lattice -> Decision), seals every state change to a SHA-256 Merkle chain, and emits
Markdown/PDF/DOCX reports plus drafted legal instruments (s.177 Affidavit, ACL s.56
demand letter). It ships as three delivery shapes that share one engine: a Python
install, a CLI audit tool, and a Tauri desktop binary.

The project is **operationally coherent and unusually well-disciplined for a solo
build**: a documented 00-99 spatial hierarchy, an AST-enforced boundary test, a
no-network import audit, a canonical-JSON rule, a fixed-constants discipline, a
named-operator constant, a maintenance rhythm, and a paper-card trust anchor. The
Merkle chain (7,156 blocks, ~4 MB) is the project's version control and tamper
evidence. The architecture diagram is in the companion HTML file.

The project is **not production-ready as a commercial product** and does not claim
to be. Its own STRATEGY.md states "operational, not finished ... maintained, not
shipped." The most material findings are:

1. **Documentation drift is pervasive and acknowledged.** Constants count, test
   count, ontology version, and layout diagrams disagree across AGENTS.md, README,
   STRATEGY.md, MATHEMATICS.md, and OPEN_ITEMS. Some are fixed in chain seals; some
   are not. (See Finding F1.)
2. **The Merkle chain contains a permanent data-quality artefact.** Blocks #1 and
   #4 both carry `"id": 1` with the same statement text -- the re-seeding foot-gun
   (OPEN_ITEMS A3, reported closed) left duplicate seed facts baked into an
   append-only ledger. The chain still verifies, but the duplicate is forever.
   (Finding F4.)
3. **The "NIZK proof" is a placeholder, not a proof.** It is a SHA-256 digest of
   the payload plus an operator identity constant. MATHEMATICS.md is honest about
   this; downstream legal-output language is not. (Finding F6.)
4. **The real-options valuation is driven by hard-coded defaults** (S0=55.0,
   K1=18.0, K2=10.0) that do not derive from the audited business's actual
   financials. The lattice is deterministic and reproducible, but it prices a
   stylised compound option, not the business. (Finding F7.)
5. **The 54-pattern deception ontology is hand-curated and validated against only
   8 EVAL cases.** F1 was 0.909 after the v3.9 bump; the EVAL-002 and EVAL-007
   failures are still open. The ontology is the heart of the audit verdict, and
   its empirical base is thin. (Finding F8.)
6. **Single-operator dependency.** PROJECT_OPERATOR = "Justin Barnett" is
   boundary-enforced. The hard-copy 1-2-3 backup plan and handover docs mitigate
   this, but the bus factor is one. (Finding F9.)
7. **Changelog pollution from the test suite.** Dozens of synthetic
   `"Test incident from pytest"` entries are written to
   `04_Validation/changelog.log` on every pytest run. The changelog is the
   human-facing counterpart to the Merkle ledger; this noise degrades its
   signal. (Finding F5.)
8. **`.bak-pre-*` files and stale directories.** `app.py` has 4 backups,
   `inventory_agent.py` 2, `third_party_assistant.py` 1, `web/test_smoke.py` 2.
   `docs/` is empty. `02_Technical/03_Vault/` is empty (live vault is at
   project-root `03_Vault/`). README's layout lists `document_engine/`,
   `middleware/`, `services/` directories that do not exist in the tree.
   (Findings F2, F3.)

Overall: the project is a **credible solo engineering artefact with a strong
internal governance story and a clear set of known weaknesses**, most of which
are already documented in `OPEN_ITEMS_AND_REFERENCE.md`. It is fit for the
operator's stated use (a maintained, auditable personal audit tool) and unfit
for a broader commercial rollout without addressing F4, F6, F7, F8, and the
single-operator dependency.

---

## 2. Project Identity (one paragraph)

Order Get It Right -- Truth as a Service. A deterministic business audit and
valuation program. Version 1.0.0, build 2026-07-12, operator Justin Barnett.
Jurisdiction: Commonwealth of Australia (ACL, Evidence Act 1995 s.79/s.177,
Corporations Act, Privacy Act). Canonical source at
`C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight`. USB/SDXC backup at
`D:\OrderGetItRight`. No network, no LLM in the audit loop. Every decision sealed
to a SHA-256 Merkle chain at `03_Vault/facts_registry.json`. Six reference
fingerprints (REF-1..REF-6) uniquely identify the build; a third party can
re-derive all six in under 10 seconds.

---

## 3. Architecture

The architecture is captured in `OGIR_ARCHITECTURE_DIAGRAM.html`. The shape is:

```
Operator
  |
  v
[3 delivery surfaces: Web UI | audit_cli | Tauri shell]
  |
  v
[Orchestrator] -- single runtime entry point, process() -> verdict
  |   +-- [Job Delegator] (MCP hand-off, URN OGIR:<SPACE>:<ACTION>)
  |         |
  |         +-- 5 core agents:
  |         |     Form_Entry_Agent    (ingest + extract: txt/docx/pdf -> evidence)
  |         |     Audit_Review_Agent (runs the 4-gate pipeline)
  |         |     Lattice_Compute_Agent (real-options valuation)
  |         |     Ledger_Seal_Agent  (Merkle append + NIZK placeholder)
  |         |     Affidavit_Agent    (s.177 / ACL s.56 / s.79 output)
  |         |
  |         +-- 3 support modules:
  |               TauFirewall     (10% extraction ceiling, enforced)
  |               InventoryAgent  (SHA-256 file walk, operator CLI)
  |               MonitorAgent    (human-in-the-loop oversight)
  |
  +-- 4-gate pipeline (executed by Audit_Review_Agent):
  |     Gate 1: Deception    -- 54-pattern ontology v3.9 + Shannon entropy
  |     Gate 2: BBFB        -- LAW (multiplicative veto) x GRACE (quadratic penalty)
  |     |                       x FRUIT (weighted product) x CVS (composite value)
  |     Gate 3: Real-Options -- 2-stage compound binomial lattice (Cox-Ross-Rubinstein)
  |     Gate 4: Decision    -- GO / DEFER / TEST FIRST / REJECT
  |
  +-- Every state change -> vault_io.append_block -> 03_Vault/facts_registry.json
  |
  +-- verify_chain re-derives Merkle root, prints MATCH / BROKEN
  +-- MonitorAgent reads vault + logs + changelog, emits Incident Briefing
```

### 3.1 The 00-99 spatial hierarchy

```
00_Strategy/      axioms, mission, 6 non-negotiables
01_Methodology/   human-readable math (no code)
02_Technical/     THE PROGRAM (config/, src/, tauri-shell/, web/)
  03_Vault/       (legacy; live vault is at project-root 03_Vault/)
  04_Validation/  (legacy; live validation is at project-root 04_Validation/)
03_Vault/         live Merkle chain (facts_registry.json, job_registry.json)
04_Validation/    changelog.log, deploy.log, reports, hardcopy, scripts, stage papers
99_Archive/       frozen snapshots
99_Archive_Historical/
data/             inbox (5 SEED samples) + outbox + samples
deploy/           deploy.ps1 + build-tauri.ps1
launchers/        4 .bat files
tests/            14 test files, ~86 tests collected
```

The boundary is enforced by `tests/test_00_99_boundary.py` via an AST scan. Code
in `02_Technical/` cannot import from `03_Vault/` or `04_Validation/`. Tests cannot
import from `src/` except `from src.server.app import app` (the one FastAPI
TestClient mount point, whitelisted explicitly).

### 3.2 Delivery shapes

| Surface | What you run | How to build |
|---------|--------------|--------------|
| Python install | `python -m uvicorn src.server:app --port 3000` | `deploy\deploy.ps1` |
| CLI audit | `python -m src.audit_cli --inbox <dir> --outbox <dir>` | `deploy\deploy.ps1` |
| Tauri desktop | Double-click `order-get-it-right.exe` | `deploy\build-tauri.ps1` |
| Agentic REPL | `python -m src.third_party_assistant` (onyx> 12 commands) | optional; Ollama tool-calling |

All three primary shapes run the same Python engine; a verdict produced on a
Python install is byte-identical to one produced in the Tauri shell.

---

## 4. The Runtime Discipline

The project's discipline is its strongest feature. The 6 non-negotiables
(STRATEGY.md section 3) are not marketing -- they are enforced:

1. **Determinism.** No `random`, no `time.time()`, no `datetime.utcnow()`. The
   canonical form is `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`.
   `tests/test_b4_python_312_compat.py` enforces no PEP 695 type aliases in
   runtime.
2. **No black boxes.** Every formula is in `01_Methodology/` in plain math:
   Shannon entropy, BBFB (LAW x GRACE x FRUIT x CVS), Cox-Ross-Rubinstein
   two-stage compound binomial, Merkle chain, NIZK placeholder.
3. **Truth ledger.** Every state-changing operation calls `vault_io.append_block`
   with `event_type` in `SCREAMING_SNAKE_CASE`. The chain is append-only.
4. **Tau firewall.** `TAU_EXTRACTION_CEILING = 0.10` is enforced by
   `TauFirewall.assert_within_ceiling(label)`. Heavy operations must call it.
5. **Portable.** Python 3.12+ (tested on 3.14.6). Runtime is pure stdlib; the 10
   third-party packages in `02_Technical/requirements.txt` (fastapi, uvicorn,
   pydantic, python-multipart, python-dotenv, python-docx, pypdf, reportlab,
   pytest, httpx) are pure-Python and vendorable.
6. **Human-documentable change.** Every change and incident is recorded in
   `04_Validation/changelog.log` (JSONL, one line per cycle) with ISO 8601
   timestamp, type, bin_id, summary, details.

The canonical JSON rule is real: every `json.dumps` that touches the chain goes
through `_canonical_default` (`02_Technical/src/utils/canonical.py`) with
`sort_keys=True, separators=(",", ":")`. No `default=str` band-aids.

The 19-ish named constants (count varies by doc -- see F1) live in
`02_Technical/config/constants.py`. A `CONSTANTS_BUMP` requires a sealed block
recording old value, new value, reason, and test result. The operator identity
`PROJECT_OPERATOR = "Justin Barnett"` is boundary-enforced -- no other identity
can claim to operate the build without forking the source and updating the
constant.

---

## 5. The 4-Gate Pipeline (mathematical detail from 01_Methodology/)

### Gate 1 -- Deception (54 patterns v3.9 + Shannon entropy)

```
H(X) = -sum_i p_i * log2(p_i)         (Shannon entropy, bits/char)
```
- H > 4.5 -> anomalous (possible non-human origin)
- H < 2.5 -> suspiciously coherent (possible scripted content)

54 patterns DD-001..DD-054, each with severity (CRITICAL/HIGH/MEDIUM/LOW),
indicator substrings, and a confidence threshold. Categories: legacy (30),
advanced evasion (6), context & capability (4), cross-lingual (6), multimodal (6),
procedural & scope (2). 15 CRITICAL, 35 HIGH, 4 MEDIUM. The runtime flags a
pattern when its indicators match and confidence exceeds threshold.

### Gate 2 -- BBFB (Barnett Binary Faith-Basis)

```
LAW = I(P>=0.50) * I(E>=0.30) * I(W>=1.00) * I(I<=0.10) * I(V<=0.05)   (multiplicative veto)
Penalty_GRACE = 2.0 * (F^2 + D^2 + G^2)                                 (quadratic, bounded [0,1])
FRUIT = 0.4*cost + 0.3*performance + 0.2*reliability + 0.1*compliance
CVS = LAW * (FRUIT - Penalty_GRACE)
```
- Penalty_GRACE > 0.75 -> CRITICAL (veto)
- CVS < 0.0005 -> NON-COMPLIANT

### Gate 3 -- Real-Options Lattice (Cox-Ross-Rubinstein, 2-stage compound)

```
dt = T/n ; u = exp(sigma*sqrt(dt)) ; d = 1/u
p  = (exp(r*dt) - d) / (u - d)
V1 = exp(-r*dt) * (p*max(S0*u - K1, 0) + (1-p)*max(S0*d - K1, 0))
S0_2 = V1 + 10.0*(1 - 0.6*deception_score)        (learning delta)
V2 = ... (same formula with K2, T2, sigma2, n2)
V_total = V1 + V2
decision = "GO" if V_total > 0.85*(K1+K2) else "DEFER"
sigma_adjusted = clamp(sigma*(1 + deception*0.35), 0.05, 0.95)
```

Defaults (constants.py): S0=55.0, K1=18.0, K2=10.0, T1=T2=3.0, r=0.05,
sigma1=0.30, sigma2=0.20, n1=n2=3, learning_delta=10.0, striking_ratio=0.85.

### Gate 4 -- Decision

`GO / DEFER / TEST FIRST / REJECT`. Striking gate: if the hard-coded real-options
valuation falls below 60% of the striking gate, the runtime force-exits with
`STRIKING_GATE_VIOLATION` (GOVERNANCE.md section 6).

---

## 6. Findings (F1..F11)

### F1 -- Documentation drift (MEDIUM, acknowledged)
Multiple docs disagree on numbers that should be stable.

| Topic | AGENTS.md | README | STRATEGY | MATHEMATICS | OPEN_ITEMS | constants.py (truth) |
|-------|-----------|--------|---------|-------------|------------|----------------------|
| Constants count | "19" | -- | -- | -- | -- | 35 named constants |
| Ontology version | v3.9 (54) | v3.9 (54) | -- | "52 Patterns" (section 4) | v3.9 (54) | `3.9 (54 patterns)` |
| Tests pass/skip | "70 pass + 2 skip-guard" | "70 passed + 2 skipped" | "73 passed + 0 skipped" (provisioned) / "71 passed + 2 skip-guard" (source) | -- | "86/1" | -- |
| .py file count | -- | -- | -- | -- | 50 | 50 under 02_Technical (excl. bundled runtime) |
| Block count | -- | -- | -- | -- | 7,156 (REF-5) | 7,156 in facts_registry.json |
| Layout dirs | `02_Technical/03_Vault/` "legacy" | `02_Technical/03_Vault/` listed as live | -- | -- | live vault at `03_Vault/` | live vault at `03_Vault/` |
| README layout dirs | -- | lists `document_engine/`, `middleware/`, `services/` | -- | -- | -- | these dirs do not exist; actual layout is `src/agents`, `src/engines`, `src/io`, `src/server`, `src/utils` |

Several of these are already fixed in chain seals (e.g. STRATEGY.md line 88
"28/28" -> "50/50" was sealed at STRATEGY_AMENDED_2026_07_16 block 2798; OPEN_ITEMS
was refreshed through TODO_FULL_RECONCILED_2026_07_17). The drift that remains:
MATHEMATICS.md section 4 still says "52 Patterns" (should be 54); AGENTS.md still
says "19 named constants" (actual count is 35); README layout lists directories
that don't exist. None of these affect runtime behaviour; all of them degrade
the project's own "no black boxes / verifiable from the docs" promise.

Recommendation: a single "DOCS_RECONCILED_FINAL" seal that amends AGENTS.md
constants count, MATHEMATICS.md section 4 pattern count, and README layout to
match the live tree.

### F2 -- `.bak-pre-*` files and stale directories (LOW)
- `02_Technical/src/server/app.py` has 4 backups (`.bak-pre-fix1`, `-fix2`,
  `-fix4-app`, `-patch`)
- `02_Technical/src/agents/inventory_agent.py` has 2 (`.bak-pre-boundary`,
  `.bak-pre-outbox-path`)
- `02_Technical/src/third_party_assistant.py` has 1 (`.bak-pre-fix3`)
- `tests/test_smoke.py` has 2 (`.bak-pre-fix4`, `.bak-pre-fix5`)
- `02_Technical/src/server/app.py.bak-pre-patch`
- `00_Strategy/STRATEGY.md.bak-pre-docfix`

The `.gitignore` excludes `__pycache__/`, `*.pyc`, `.pytest_cache/`, etc. but
does **not** exclude `.bak-pre-*`. These accumulate. The boundary test excludes
`.bak-pre-*` from the REF-4 tree-shape hash (per OPEN_ITEMS PART 3 note), so they
don't break the fingerprint, but they are noise in the tree.

Stale/empty directories:
- `docs/` is empty
- `02_Technical/03_Vault/` is empty (live vault is at project-root `03_Vault/`)
- `02_Technical/04_Validation/` empty (live is at project-root)

Recommendation: add `.bak-pre-*` and the empty `docs/` and
`02_Technical/03_Vault/` to `.gitignore` or hard-delete them in a cleanup seal.

### F3 -- README layout is stale (LOW)
README's "Layout" section lists:
```
02_Technical\document_engine\ extractors, parser, report writer, pipeline
02_Technical\middleware\    tracing, session tracking
02_Technical\services\      audit, BBFB, lattice, ledger, facts, squeal, ACL,
                            affidavit, evaluation
```
None of these directories exist. The actual layout is:
```
02_Technical\src\agents\    orchestrator, job_delegator, 5 agents, tau_firewall,
                            inventory_agent, monitor_agent
02_Technical\src\engines\   deception_scanner, bbfb_engine, real_options_lattice,
                            evaluation_service, acl_demand_generator,
                            legal_affidavit_generator, facts_registry,
                            squeal_protocol, deception_ontology_data,
                            evaluation_cases
02_Technical\src\io\        vault_io, evidence_parser, extractors, pipeline,
                            report_writer
02_Technical\src\server\   app, session_tracker, tracing
02_Technical\src\utils\     canonical
02_Technical\config\        constants, exceptions
02_Technical\tools\        agentic_repl, agentic_repl_tools, discovery_agent
02_Technical\web\           index.html (single-file UI)
02_Technical\tauri-shell\   Rust + JS desktop binary
```
Recommendation: rewrite README layout to match the live tree in the
DOCS_RECONCILED_FINAL seal.

### F4 -- Duplicate seed facts baked into the Merkle chain (MEDIUM)
The first blocks of `03_Vault/facts_registry.json` show:
- Block #1: `id: 1`, statement "Order Get It Right enforces the agent chain via the
  job delegator."
- Block #2: `id: 2`, "All deception detections use the deterministic 52-pattern
  ontology v3.8."
- Block #3: `id: 3`, "BBFB engine uses LAW/GRACE/FRUIT decomposition..."
- Block #4: `id: 1`, statement "Order Get It Right enforces the agent chain via
  the job delegator." (same as block #1)
- Block #5: `id: ...` (continues with re-seeded facts)

Block #2 also still says "52-pattern ontology v3.8" while the live
`DECEPTION_ONTOLOGY_VERSION` constant is "3.9 (54 patterns)" -- a stale seeded
fact that was reportedly fixed at OPEN_ITEMS A2 ("v3.8/v3.9 hardcoded strings")
but remains in the chain because the chain is append-only. The fix sealed new
facts but did not -- and cannot -- edit the old ones.

The A3 fix ("startup reset foot-gun") reportedly guarded `_seed_facts_once()`
with `if list_facts(): return` and made `POST /api/facts` call `_ensure_seeded()`
before adding. That prevents new duplicates on a fresh process. It does not
remove the existing duplicates.

Source-level confirmation (subagent digest, `facts_registry.py:118`):
`add_fact` does dedup-check on `(statement, source)` and raises `ValueError` on
duplicate -- so new duplicates via the live API are blocked. The chain
artefact is historical, not a live regression.

Impact: the chain still verifies (the hashes chain correctly), but the
facts registry has a permanent `id: 1` collision in its first 5 blocks. Any
third-party auditor who reads the chain head will see the duplicate. This is
a data-quality smell, not a security hole.

Recommendation: accept the historical duplicate as a permanent record (the chain
is append-only by design), but add a `KNOWN_CHAIN_ARTEFACTS` note to
`04_Validation/` listing the duplicate id:1 blocks and the stale "v3.8" seed
fact, so the next operator or auditor sees the explanation in one place rather
than discovering it.

### F5 -- Changelog pollution from the test suite (MEDIUM)
`04_Validation/changelog.log` contains dozens of entries like:
```json
{"binId": "test-runner", "details": "Synthetic incident to verify the changelog is wired.", "summary": "Test incident from pytest", "timestamp": "...", "type": "incident"}
```
These appear at the head of the changelog (2026-07-11 onwards) and continue
through 2026-07-17. They are written by the test suite, not by the operator.
They are not sealed to the Merkle chain (they are changelog-only, not
vault-only), so they don't corrupt the chain -- but they corrupt the changelog,
which is the human-facing counterpart to the chain.

Recommendation: in the test that emits these, gate the write behind an
environment variable (e.g. `OGIR_TEST_WRITE_CHANGELOG=1`) that the operator sets
only when explicitly testing the changelog wiring, or write to a temp file
instead of the live changelog.

### F6 -- "NIZK proof" is a placeholder, not a proof (MEDIUM, acknowledged in math doc)
Each block has a `nizk_proof` field that is a SHA-256 digest of the payload plus
the operator identity constant (per MATHEMATICS.md section 6):
```
c = SHA256(g || V || Y || user_id) mod q
s = (v - c * x) mod q
proof = (c, s, V)
```
The math doc is explicit: "The runtime ships with a fully functional placeholder
that can be replaced with a production-grade Schnorr implementation without
changing the public API." The implementation is a SHA-256 hash, not a Schnorr
signature. There is no discrete-log hard problem in play, no public/private
keypair, no verifier challenge.

The risk is downstream: the affidavit generator and legal output language lean
on the integrity of the ledger. A court that reads "NIZK proof" in an affidavit
and discovers it is a hash of the payload plus a constant will not be impressed.
The chain's tamper-evidence is real (it's a Merkle chain); the "NIZK proof" name
is overselling what the field actually is.

Recommendation: rename the field `nizk_proof` -> `integrity_digest` (or
`payload_commitment`) in the next `CONSTANTS_BUMP`-class seal, and update the
legal output language to describe it accurately. Keep the placeholder; just
don't call it a proof.

### F7 -- Real-options valuation uses hard-coded business inputs (HIGH)
The lattice is mathematically correct and deterministic. But the defaults in
`constants.py` are:
```
REAL_OPTIONS_S0 = 55.0      current asset value
REAL_OPTIONS_K1 = 18.0     stage-1 exercise price
REAL_OPTIONS_K2 = 10.0     stage-2 exercise price
REAL_OPTIONS_T1 = 3.0      stage-1 horizon (years)
REAL_OPTIONS_T2 = 3.0      stage-2 horizon
REAL_OPTIONS_R  = 0.05      risk-free rate
REAL_OPTIONS_SIGMA1 = 0.30 stage-1 volatility
REAL_OPTIONS_SIGMA2 = 0.20 stage-2 volatility
REAL_OPTIONS_LEARNING_DELTA = 10.0
```
These are **the same for every audit**. The audited business's own financials
do not feed the lattice. Only the deception score (from Gate 1) and the entropy
(from Gate 1) feed it, via the sigma adjustment
`clamp(sigma*(1 + deception*0.35), 0.05, 0.95)` and the learning delta
`10.0*(1 - 0.6*deception_score)`. So the "valuation" is a function of the
audit text's deception score against a fixed option, not a valuation of the
business.

This is fine as a relative signal (more deception -> lower value) but it is
not a business valuation in any ordinary sense. The legal output language
should not imply otherwise.

Recommendation: either (a) document the lattice as a "deception-adjusted
optionality index" rather than a valuation, or (b) wire the lattice inputs to
extracted evidence (price, spec, warranty) so the valuation reflects the
audited business. Option (b) is a real change; option (a) is a doc fix.

### F8 -- 54-pattern ontology validated against only 8 EVAL cases (HIGH)
The deception ontology is the heart of the audit verdict. Its empirical
validation surface is the 8-case evaluation suite (EVAL-001..EVAL-008):
- corporate-evasion, AI safety hedging, bureaucratic redirection, scope creep,
  false certainty, kelvanistic baseline, direct user correction, technical spec.
- After the v3.9 bump (which added DD-053 Bureaucratic Redirection and DD-054
  Scope Creep): 6/8 strict pass, accuracy 0.875, precision 0.833, recall 1.00,
  F1 0.909, 0 false negatives, 1 false positive.
- Two cases still fail: EVAL-002 (wants patternCount>=2, threshold tuning) and
  EVAL-007 (false positive on direct user correction language, needs a DD-034
  discriminator).
- The E4 pre-2021 reference calibration (2026-07-17) ran a real 5-section intake
  and got 5/54 patterns firing, 12 raw hits, 11 false positives, 1 true
  negative. Four refinement recommendations R1-R4 are queued.

8 cases is a thin base for a 54-pattern ontology that drives legal output.
The ontology is hand-curated from the operator's experience; the EVAL cases are
synthetic. The R1-R4 refinements (DD-001 "clearly", DD-006 "could"/"to clarify",
DD-041 rename, DD-054 "consistent with") are open.

Recommendation: before any commercial use, expand the EVAL suite to at least
30-50 cases with real (anonymised) correspondence, and run a proper
precision/recall sweep per pattern. The OPEN_ITEMS STEP 3 (ontology bump R1-R4)
is the right next move; consider expanding it to include the EVAL suite
expansion.

### F9 -- Single-operator dependency (HIGH, structural)
- `PROJECT_OPERATOR = "Justin Barnett"` is boundary-enforced. No other identity
  can operate the build.
- The hard-copy 1-2-3 backup plan, the handover docs, the maintenance rhythm,
  and the paper-card trust anchor all mitigate this. But the bus factor is one.
- The changelog is full of `binId: "codex-on-Justo"` -- the build was largely
  developed with an AI assistant (Codex) under the operator's identity.
- If the operator is unavailable, the next operator must fork the source,
  update `PROJECT_OPERATOR`, and seal an `OPERATOR_HANDOVER` block. The
  handover docs (`HANDOVER_TO_NEW_OPERATOR.md`) walk this path. It is
  documented; it is not tested.

Recommendation: the OPEN_ITEMS D1-true-clean-host step (the only remaining
hardware-dependent verification) should be run on a second Windows PC with a
second operator (a trusted third party, not Justin) acting as the "next
operator". This tests both the portability claim and the handover procedure
in one move.

### F10 -- Tauri binary is unsigned (LOW, acknowledged)
The Tauri build artefacts (`order-get-it-right.exe`,
`Order Get It Right_1.0.0_x64_en-US.msi`, `Order Get It Right_1.0.0_x64-setup.exe`)
have code-sign status "NotSigned" (per OPEN_ITEMS A9, 2026-07-17 rebuild).
This is acknowledged and treated as "no regression" since the 2026-07-12 build
was also unsigned. For a personal audit tool this is fine; for any
distribution beyond the operator it will trigger SmartScreen warnings on
Windows and undermine the "defensible" claim.

Recommendation: no action for the operator's personal use. Flag as a blocker
for any broader distribution.

### F11 -- No Git (LOW, by design)
The project is explicit: "This project does not currently use Git (the chain is
the version control)." There is no `.git/`. This is a deliberate choice -- the
Merkle chain is the version control and the changelog is the human-readable
counterpart. The `.gitignore` exists anyway (to keep `__pycache__/`,
`.pytest_cache/`, etc. out of a future Git adoption).

The cost: no branches, no merges, no bisect, no cheap diffs, no remote backup
via push. The 1-2-3 backup plan (USB + paper card + offsite) is the backup. The
SDXC at `D:\OrderGetItRight` is a robocopy mirror, not a Git clone. The chain
verifies the mirror is a prefix of the laptop chain (per changelog 2026-07-16
D1 probe), which is a real tamper-evidence story -- but it is not a
version-control story in the collaborative sense.

Recommendation: keep the chain as the trust anchor. Consider adopting Git **in
parallel** (not as a replacement) for the diff/branch/remote-backup ergonomics,
with the chain still the source of truth for audit decisions. The `.gitignore`
is already in place.

---

## 6A. Source-level findings (F12-F17)

These findings were surfaced by a background subagent that read the full Python
source tree (agents, engines, io, server, utils, tauri-shell, all 12 test
files). They are concrete code-level issues that the documentation-only review
above could not see. The subagent's full digest is at
`C:\Users\justo\AppData\Local\hermes\cache\delegation\subagent-summary-0-20260718_020523_170684.txt`
(81 KB, 536 lines).

### F12 -- Two chain verifiers use non-canonical JSON (MEDIUM, latent bug)
The C14 canonical-JSON hardening fix was applied to `vault_io._canonical_json`
(the sealer) and `verify_chain._recompute_root` (the standalone CLI verifier).
It was **not** propagated to two other verifiers:
- `src/agents/ledger_seal_agent.py:45` -- uses plain
  `json.dumps(sort_keys=True, separators=(",", ":"))` with no `default=` callable
- `src/agents/monitor_agent.py:81` -- same non-canonical form

These will `TypeError` if a block payload ever contains a `datetime`, `UUID`,
`Decimal`, `set`, `-0.0`, or NFD-normalised string -- exactly the cases C14 was
written to handle. Currently all sealed payloads are JSON-native (dicts of
str/float/int/bool/list), so the divergence is **latent, not active**. But
`monitor_agent` is the human-in-the-loop oversight module; if it ever silently
hashes differently from `verify_chain`, the operator's briefing will disagree
with the canonical verifier on the same chain. Maintenance hazard.

Recommendation: replace both with `canonical_dumps` calls, or delegate to
`verify_chain.verify()`. One-line fix each.

### F13 -- `monitor_agent` "unexplained_verdicts" is a stub (MEDIUM, misleading)
`src/agents/monitor_agent.py:244-247` -- the "unexplained verdicts" loop
appends **every** `SUPPRESSED` block as unexplained. The comment says "The
orchestrator seals REFUSAL alongside every SUPPRESSED" but the code never
actually checks for a matching `REFUSAL` block or Squeal report. The result:
the operator's Incident Briefing will always list every SUPPRESSED block as
"unexplained," regardless of whether a REFUSAL was sealed. The check is a stub
masquerading as a check.

Recommendation: either implement the actual cross-check (scan the chain for a
matching `REFUSAL` block referencing the same `fact_id` / `job_id` within a
window), or rename the field to `all_suppressed_blocks` and drop the
"unexplained" framing. As-is, it misleads the operator.

### F14 -- Determinism claim is narrower than marketed (MEDIUM, acknowledged in tests)
The headline in `constants.py:5-6` and `STRATEGY.md` non-negotiable #1 is
"same input + same config = same output, on any host" / "bit-for-bit
identical." The source shows this is true for the **computation** (deception
probability, entropy, pattern matches, BBFB/FRUIT/GRACE scores, lattice
decision) but **not for the sealed chain**, because every block carries
`timestamp = datetime.now(timezone.utc).strftime(...)` and the job tokens
embed `datetime.now()` in the `job_block` that gets hashed into `job_id`.
Re-running the same audit at a different moment produces a different chain.

The project's own tests acknowledge this: `test_evaluation_suite_is_deterministic`
strips `runId` and `timestamp` before comparing; `test_affidavit_preview_matches_post_output`
strips the `DATE OF AFFIDAVIT:` line. So the non-determinism is honest and
documented at the test layer -- but the headline "bit-for-bit identical"
overstates what the chain delivers. The chain is tamper-evident and
reproducible **within a run**, not reproducible **from scratch**.

Recommendation: amend the headline to "same input + same config = same verdict,
same scores, same decision -- on any host. The sealed chain carries
ISO-8601 timestamps and is tamper-evident, not byte-reproducible across runs."
This is honest and still strong.

### F15 -- Code smells and dead code (LOW)
A cluster of smaller issues the subagent flagged:
- `tau_firewall.StructuralRefusal` is re-declared locally rather than imported
  from `config/exceptions.py` (which defines its own `StructuralRefusal` that
  the runtime never uses). Two classes, same name, same `code`. Divergence.
- `inventory_agent._classify` has a dead branch (lines 349-354): both arms of
  `if size <= STREAM_HASH_THRESHOLD: ... else: ...` call `_safe_stream_hash`
  identically. The "very large files" comment is aspirational; the code is
  identical.
- `form_entry_agent.draft_fact` truncates statements to 1000 chars
  (`statement[:1000]`), while the orchestrator deliberately seals the full
  statement (regression-tested by `test_orchestrator_seam.py`). Two truncation
  policies in the same project, depending on entry point. The `draft_fact`
  truncation is dormant for the audit path but live for the Onyx CLI `draft`.
- `real_options_lattice.py:79` hard-codes sigma2 upper clamp to `0.90` instead
  of using `REAL_OPTIONS_SIGMA_MAX=0.95`. Minor constant/use divergence.
- `vault_io.append_block:126` hard-codes `"Justin Barnett"` for the NIZK seed
  instead of importing `PROJECT_OPERATOR` from constants. Duplicates the
  single source of truth.
- `config/constants.py:8` imports `os` but never uses it.
- `config/exceptions.py` defines `OntologyIntegrityError`, `UserExhaustion`,
  `SpoliationDetected`, `DeterminismViolation`, `StrikingGateViolation`,
  `ExtractionError`, `UnsupportedFormat` -- none raised anywhere in the
  runtime. Future-proofing or dead code.
- `SHANNON_MAX_NORMAL`, `SYSTEM_ID`, `SQUEAL_TRIGGER_PROBABILITY` defined in
  constants but not referenced in the runtime. (`SQUEAL_TRIGGER_PROBABILITY=0.75`
  duplicates `DECEPTION_PROBABILITY_VETO=0.75`; the scanner uses the latter.)
- `commands.rs::ping` is defined in the Tauri shell but not registered in
  `invoke_handler!` in `lib.rs` -- unreachable from the front-end. Dead code.
- Two parallel regex evidence parsers: `form_entry_agent.normalize_real_world_claim`
  (276 lines, used by Onyx CLI/REPL) and `io/evidence_parser.extract_product_evidence`
  (196 lines, used by the pipeline/server). Overlapping but not identical
  logic. Maintenance hazard.
- Two Squeal surfaces: `deception_scanner.trigger_squeal_protocol` writes to an
  in-memory `SQUEAL_LOG` list (never persisted); `squeal_protocol.write_squeal_report`
  writes to disk but is not called from the audit path. The disk writer is
  effectively dead code.
- `session_tracker._sessions` grows unbounded between POSTs (purge runs only
  on each POST, never on a timer). Long idle + many clients -> memory growth.
- `BATCH_JOBS: dict = {}` and `facts_registry._registry` are in-memory only;
  batch job metadata and operator-added facts are lost on server restart.

Recommendation: none of these individually blocks anything. A cleanup seal
that (a) propagates `canonical_dumps` to the two verifiers (F12), (b) fixes
the `monitor_agent` stub (F13), (c) imports `PROJECT_OPERATOR` in
`vault_io.append_block`, and (d) deletes the dead Tauri `ping` command would
address the highest-value items in one pass.

### F16 -- `vault_io.append_block` is not concurrency-safe (LOW, latent)
The append path is `read_facts_registry -> mutate blocks -> write_facts_registry`,
with no lock around the read-modify-write. The `AgentJobDelegator` holds an
`RLock` for its own calls, but the orchestrator's direct
`vault_io.append_block` calls for `REFUSAL` / `AUDIT_CYCLE_COMPLETE` /
`SHUTDOWN` are unguarded. Under uvicorn with a single worker (the default) this
is fine. Under multi-worker it would race and could lose a block. The
single-worker assumption is undocumented.

Recommendation: document the single-worker assumption in `app.py` and
`deploy/deploy.ps1`, or wrap `append_block` in a process-wide lock. The air-gap
single-tenant model makes multi-worker unlikely, so documentation is the
proportionate fix.

### F17 -- `test_normalize_regression.py` hardcodes a host-specific Python path (LOW)
The test hardcodes
`PYTHON_EXE = C:\Users\justo\OneDrive\Documents\to the spoils go\Python314\python.exe`.
This will break on any other host (including the second PC for D1-true-clean-host,
F9). It's a portability bug in the test suite itself, which is otherwise
host-agnostic.

Recommendation: replace with `sys.executable` or `shutil.which("python")`.

---

## 7. What the project does well

- The 00-99 spatial hierarchy with AST-enforced boundary test is a genuinely
  strong architectural discipline. Most solo projects don't have this.
- The canonical JSON rule (every seal goes through `_canonical_default` with
  `sort_keys=True, separators=(",", ":")`) is correctly applied and tested
  (`test_c14_canonical_json_hardening.py`).
- The no-network claim is not just a claim -- `audit_no_network.py` verifies
  it with a CLEAN/ALLOWED/REVIEW/FAIL taxonomy and a 4-file allow-list, and
  `tests/test_audit_no_network.py` pins it (4/4).
- The determinism rule is enforced by code review and by
  `test_b4_python_312_compat.py` (no PEP 695 type aliases in runtime).
- The 6 reference fingerprints (REF-1..REF-6) are a clever third-party
  verification mechanism: any auditor can re-derive all six in under 10 seconds
  and prove "this is the same project."
- The maintenance rhythm (daily 15 min, weekly 2 hr, monthly 4 hr, quarterly
  8 hr, annual 16 hr, via 5 STAGE_PAPER_*.txt files) is a real commitment, not
  aspirational text.
- The handover documents (HANDOVER_TO_AUDITOR.md, HANDOVER_TO_NEW_OPERATOR.md)
  are written for two distinct audiences and ground the project's continuity
  claim.
- The TROUBLESHOOTING.md (928 lines, SYMPTOM/ROOT CAUSE/FIX/ESCALATE) is
  unusually thorough for a solo project.
- The changelog is a JSONL append-only log with structured fields; the chain
  is the tamper-evidence layer, the changelog is the human-readable layer.
- The operator's honesty about what is open (OPEN_ITEMS_AND_REFERENCE.md) is
  the best single feature of the project's documentation culture. The list is
  sealed to the chain so the next operator knows what the previous operator was
  uncertain about.

---

## 8. Recommendations (priority order)

1. **F8 (ontology validation):** Expand the EVAL suite from 8 to >=30 cases
   with real correspondence. Run a per-pattern precision/recall sweep. Apply
   the R1-R4 refinements already queued in OPEN_ITEMS STEP 3. This is the
   single biggest lever on the audit verdict's credibility.
2. **F7 (lattice inputs):** Either reframe the lattice output as a
   "deception-adjusted optionality index" in all legal output language, or
   wire S0/K1/K2 to extracted evidence. The current state is a fixed-option
   valuation dressed as a business valuation.
3. **F13 (monitor stub):** Fix `monitor_agent` "unexplained_verdicts" -- it
   currently lists every SUPPRESSED block as unexplained without checking for
   a matching REFUSAL. Either implement the cross-check or rename the field.
   The operator's Incident Briefing is misleading as-is.
4. **F12 (canonical JSON propagation):** Replace the non-canonical
   `json.dumps` in `ledger_seal_agent.verify_root:45` and
   `monitor_agent._recompute_chain_root:81` with `canonical_dumps`. One-line
   fix each; prevents a latent TypeError and a silent hash divergence if a
   non-JSON-native payload ever enters the chain.
5. **F6 (NIZK rename):** Rename `nizk_proof` -> `integrity_digest` in the next
   CONSTANTS_BUMP seal. Update affidavit language to describe it accurately.
   Keep the placeholder; stop calling it a proof.
6. **F14 (determinism claim):** Amend the "bit-for-bit identical" headline to
   "same verdict, same scores, same decision -- on any host. The sealed chain
   is tamper-evident, not byte-reproducible across runs." Honest and still
   strong.
7. **F1 + F3 (docs reconciliation):** A single `DOCS_RECONCILED_FINAL` seal
   that amends AGENTS.md constants count, MATHEMATICS.md section 4 pattern
   count, README layout to match the live tree. One pass, one seal.
8. **F4 (chain artefacts note):** Add `04_Validation/KNOWN_CHAIN_ARTEFACTS.md`
   listing the duplicate id:1 blocks and the stale "v3.8" seed fact, with
   explanation. The chain is append-only; the explanation is the fix.
9. **F5 (changelog pollution):** Gate the test-suite changelog writes behind
   `OGIR_TEST_WRITE_CHANGELOG=1` or redirect them to a temp file. Run a
   one-time cleanup of the existing "Test incident from pytest" entries (or
   accept them as historical and add a note to KNOWN_CHAIN_ARTEFACTS.md).
10. **F9 (single-operator):** Run D1-true-clean-host on a second Windows PC
    with a trusted third party acting as the "next operator." This tests
    portability and the handover procedure in one move. (Note: F17 -- the
    test suite hardcodes a host-specific Python path that will need fixing
    before this test can run on a second host.)
11. **F15 (cleanup seal):** A single cleanup seal that (a) imports
    `PROJECT_OPERATOR` in `vault_io.append_block` instead of hard-coding
    "Justin Barnett", (b) deletes the dead Tauri `ping` command, (c) removes
    the `inventory_agent._classify` dead branch, (d) fixes the
    `real_options_lattice` sigma2 clamp to use `REAL_OPTIONS_SIGMA_MAX`, (e)
    removes the unused `os` import in `constants.py`, (f) either wires or
    deletes `squeal_protocol.write_squeal_report` (currently dead).
12. **F17 (test portability):** Replace the hardcoded Python path in
    `test_normalize_regression.py` with `sys.executable`. Prerequisite for
    F9 (the second-host test).
13. **F16 (concurrency):** Document the single-uvicorn-worker assumption in
    `app.py` and `deploy/deploy.ps1`, or wrap `vault_io.append_block` in a
    process-wide lock.
14. **F2 (cleanup):** Add `.bak-pre-*` to `.gitignore` or hard-delete the
    backups in a cleanup seal. Delete the empty `docs/` and
    `02_Technical/03_Vault/` directories.
15. **F10 (code signing):** No action for personal use. Blocker for any
    broader distribution.
16. **F11 (Git):** Optional. Consider adopting Git in parallel with the chain
    for diff/branch/remote-backup ergonomics. The chain stays the trust anchor.

---

## 9. Reference fingerprints (live state at review time)

From `OPEN_ITEMS_AND_REFERENCE.md` (sealed 2026-07-17, refreshed through the
TODO_FULL_RECONCILED_2026_07_17 seal at block 7061, root ce81a4f7...):

| Fingerprint | Value |
|-------------|-------|
| REF-1 constants.py SHA-256 | 7654ddf6fffd79c618d1899b6703121d99b742e8d37793e2ea1a023bb70bedea |
| REF-2a STRATEGY.md SHA-256 | e4b2ff1928e2b8e4d253cf7a2feaf66457df6df4c01b49793a499286023aa75d |
| REF-2b GOVERNANCE.md SHA-256 | 0c2335de7e3e1962f30cacc3d12fe2921e8565287190c04d2dec01328f8f028d |
| REF-3 source tree SHA-256 | 7962bf6116445f46296ac97f43ffaf01ce8ca68e111cfc3f565d4c7a5b659087 |
| REF-4 tree shape SHA-256 | b85f4cb7c7c4bbcd202cdde014219d5d6820137f0bb714a519e5403e7915e0af |
| REF-5 Merkle root | 0fe4872733fb402bbe8dc14e6543a702f901118e6130549304de156bf48ac7c7 |
| REF-6 composite SHA-256 | ec72d1f273f9c6e52385bd39dffe41a2a52d7d47fe267dca40a9188a1a34cda6 |
| Block count | 7,156 |
| First block | 2026-07-11T17:15:10Z |
| Last block (approx) | 2026-07-17T14:14:00Z |

Re-derive with: `cd 02_Technical && python -m src.verify_chain` (and
`--print-refs` for the six fingerprints).

Note: the facts_registry.json I inspected on 2026-07-18 has a tail block with
timestamp `2026-07-17T14:30:29Z` and the same root as REF-5, so the live state
matches the sealed reference within the expected drift window.

---

## 10. Conclusion

Order Get It Right is a **credible, disciplined solo engineering project** with
a strong internal governance story (spatial hierarchy, boundary test,
canonical JSON, no-network audit, named operator, maintenance rhythm, paper
trust anchor, six reference fingerprints). It is **fit for the operator's
stated use** as a maintained, auditable personal audit tool.

It is **not fit for broader commercial rollout** without addressing:
- the thin empirical base of the deception ontology (F8),
- the hard-coded business inputs to the real-options lattice (F7),
- the "NIZK proof" naming (F6),
- the single-operator dependency (F9), and
- the documentation drift (F1, F3).

Most of these are already in OPEN_ITEMS_AND_REFERENCE.md. The project's
culture of honestly recording what is unfinished is its strongest feature
and the reason a review like this can be specific rather than speculative.

The architecture diagram (`04_Validation/OGIR_ARCHITECTURE_DIAGRAM.html`) and
the short-form notes (`04_Validation/OGIR_ASSESSMENT_NOTES_2026-07-18.md`)
are the companion deliverables.

---

End of assessment.