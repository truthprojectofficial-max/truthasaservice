# AUDIT_BLACK_BOX_TRACE

**Date:** 2026-07-17
**Status:** COMPLETE — every user gesture is traced from screen to file:line
**Closes:** OPEN_ITEMS_AND_REFERENCE.md D3
**Companion to:** AUDIT_NO_BLACK_BOX.md (the pillar-level table)

## What this document proves

The build's "no black boxes" promise has two halves:

- **The pillar-level half** (AUDIT_NO_BLACK_BOX.md, sealed 2026-07-12) lists every number the UI shows and the file:line that computed it. Pillar by pillar, the audit can be traced.
- **The flow-level half** (this document, sealed 2026-07-17) walks a *real* audit end-to-end and names every hop from the operator's first click to the JSON that comes back. The pillar table says "this is the function"; this doc says "this is the user's gesture, this is the HTTP request, this is the agent hop, this is the engine, this is the constant, this is the line that puts the number on the screen."

A third party reading both halves together has a complete receipt for the audit.

## How to use this document

Pick one of the flows below. For each step, the table has four columns:

- **Operator gesture** — what the user does on the screen (or in the REPL).
- **HTTP request** — the verb, path, and payload. (For the REPL flows, this is the Ollama tool call.)
- **Server hop** — the file:line in `02_Technical/src/server/app.py` (or `02_Technical/tools/agentic_repl.py` for REPL flows) that handles the request.
- **Engine hop** — the file:line in the engine / agent that produces the value.
- **Constants** — the file:line in `02_Technical/config/constants.py` (or the engine file itself) that names the threshold / coefficient.
- **Render line** — the file:line in `02_Technical/web/index.html` (or stdout for REPL) that puts the value on the screen.

A flow with a missing row is incomplete; push back. A flow with a row that does not match the code is broken; push back.

---

## Flow 1 — Deception scan (the operator's most-used flow)

**Scenario:** The operator opens the web UI, clicks the "Deception Scanner" tab, types a sentence about a supplier claim, and clicks "Audit". The page shows the verdict (CLEAN / FLAGGED / REFUSAL), the detected patterns, the Shannon entropy, and the deception probability.

| Step | Operator gesture | HTTP request | Server hop | Engine hop | Constants | Render line |
|---|---|---|---|---|---|---|
| 1.1 | Click "Deception Scanner" tab | (DOM only) `data-tab="deception"` | n/a | n/a | n/a | `02_Technical/web/index.html:64` (tab nav), `:106` (`#tab-deception` shown) |
| 1.2 | Type text into the textarea, click "Audit" | `POST /api/analyze` `{text: <typed>, context: <opt>, prioritizedPatterns: <opt>}` | `02_Technical/src/server/app.py:146` (`analyze()`) | calls `audit_text()` from `src.engines.deception_scanner` | n/a (passed through) | `02_Technical/web/index.html:307` (the `api("POST", "/analyze", {text})` call) |
| 1.3 | (inside `analyze()`) | n/a — in-process | `02_Technical/src/server/app.py:148` | `src/engines/deception_scanner.py:audit_text()` (line numbers per AUDIT_NO_BLACK_BOX.md) | n/a | n/a |
| 1.4 | (inside `audit_text()`) Shannon entropy | n/a | n/a | `src/engines/deception_scanner.py:25` (`shannon_entropy()`) | `SHANNON_ANOMALY_THRESHOLD`, `SHANNON_LOW_THRESHOLD` (`02_Technical/config/constants.py:73-75`) | n/a |
| 1.5 | (inside `audit_text()`) Pattern match | n/a | n/a | `src/engines/deception_scanner.py:56` (`detect_patterns_with_confidence()`) | 54 patterns in `src/engines/deception_ontology_data.py`; version in `02_Technical/config/constants.py:82` | n/a |
| 1.6 | (inside `audit_text()`) Probability & verdict | n/a | n/a | `src/engines/deception_scanner.py:104` (`calculate_deception_probability()`) + `:167` (`audit_text()` top-level) | `DECEPTION_PROBABILITY_VETO = 0.75`, `DECEPTION_PROBABILITY_LOW = 0.30` (`02_Technical/config/constants.py:80-81`) | n/a |
| 1.7 | (return) JSON `AuditReport` | n/a | `02_Technical/src/server/app.py:149` (`return report.model_dump()`) | n/a | n/a | n/a |
| 1.8 | Page renders verdict + pattern list | (browser JS) | n/a | n/a | n/a | `02_Technical/web/index.html:339` (the LAW gate table — note: this template is shared; the Deception tab uses the verdict box at `:106-114`) |
| 1.9 | (optional) Operator clicks "View in BBFB" — but BBFB is a separate tab, not a follow-up; the audit report is the final value for the Deception tab. | n/a | n/a | n/a | n/a | n/a |

**Files a third party reads to verify Flow 1 end-to-end:**

1. `02_Technical/web/index.html` lines 106-114 (the Deception tab markup), lines 244-255 (the `api()` helper), line 307 (the audit call).
2. `02_Technical/src/server/app.py` lines 146-150 (the `analyze()` endpoint).
3. `02_Technical/src/engines/deception_scanner.py` lines 25 (entropy), 56 (patterns), 104 (probability), 167 (top-level).
4. `02_Technical/src/engines/deception_ontology_data.py` (the 54 patterns).
5. `02_Technical/config/constants.py` lines 73-75 (Shannon), 80-82 (deception).

**Six files. Six line ranges. Every number on the Deception tab is in those six files.**

---

## Flow 2 — BBFB + Lattice (the decision gate)

**Scenario:** The operator has product evidence (price, warranty, spec, supplier) and wants the full decision: GO / DEFER / TEST FIRST / REJECT. They fill in the BBFB tab and click "Calculate".

| Step | Operator gesture | HTTP request | Server hop | Engine hop | Constants | Render line |
|---|---|---|---|---|---|---|
| 2.1 | Click "BBFB Engine" tab | (DOM only) `data-tab="bbfb"` | n/a | n/a | n/a | `02_Technical/web/index.html:65` (nav), `:114` (tab shown) |
| 2.2 | Fill the LAW/GRACE/FRUIT fields, click "Calculate" | `POST /api/calculate` `{evidence: {...}}` | `02_Technical/src/server/app.py:152` (`calculate()`) | `src/engines/bbfb_engine.py:calculate_bbfb()` | per-flow (LAW, GRACE, FRUIT) | `02_Technical/web/index.html:334` (the BBFB call) |
| 2.3 | LAW section: 6 metrics, each `value`/`threshold`/`passed` | n/a | n/a | `src/engines/bbfb_engine.py:86-111` (LAW block) | `PERFORMANCE_FLOOR=0.50`, `EFFICIENCY_FLOOR=0.30`, `WARRANTY_FLOOR=1.00`, `ISSUE_DENSITY_FLOOR=0.10`, `VIOLATION_RATIO_FLOOR=0.05` (`02_Technical/config/constants.py:25-29`) | n/a |
| 2.4 | GRACE section: `rawPenalty`, `normalizedPenalty`, `riskLevel` | n/a | n/a | `src/engines/bbfb_engine.py:113-124` (GRACE block) | `GRACE_QUADRATIC_COEFFICIENT=2.0`, `GRACE_CRITICAL_THRESHOLD=0.75` (`02_Technical/config/constants.py:34-35`) | n/a |
| 2.5 | FRUIT section: `compositeValueScore`, `weightedScores[]`, `compliant` | n/a | n/a | `src/engines/bbfb_engine.py:126-139` (FRUIT block) | `FRUIT_WEIGHTS = {cost:0.4, performance:0.3, reliability:0.2, compliance:0.1}`, `CVS_THRESHOLD=0.0005` (`02_Technical/config/constants.py:40-50`) | n/a |
| 2.6 | Click "Run Lattice" on the Valuation tab | `POST /api/calculate` (same endpoint, different evidence shape) | `02_Technical/src/server/app.py:152` | `src/engines/real_options_lattice.py:hardened_compound_binomial_gate()` (line 50); binomial step at line 33 | `REAL_OPTIONS_S0`, `_K1`, `_K2`, `_T1`, `_T2`, `_R`, `_SIGMA1`, `_SIGMA2`, `_N1`, `_N2`, `_LEARNING_DELTA`, `_STRIKING_RATIO`, `_SIGMA_MIN`, `_SIGMA_MAX` (`02_Technical/config/constants.py:55-68`) | `02_Technical/web/index.html:361` (the lattice call) |
| 2.7 | Decision: GO / DEFER / TEST FIRST / REJECT | (combined — see Flow 3) | n/a | n/a | n/a | n/a |

**For the full decision gate, Flow 2 is wired together with Flow 3 (the orchestrator). The `BBFB Engine` tab by itself shows the four gates. The decision is a higher-level combination of the four.**

---

## Flow 3 — Orchestrator end-to-end (the audit cycle)

**Scenario:** The operator wants the full agent chain — Form Entry → Audit Review → Lattice Compute → Ledger Seal — on a single input. They POST to `/api/orchestrator/process` (or use the `third_party_assistant.py` REPL's `audit` command, which routes through the same path).

| Step | Operator gesture | HTTP request | Server hop | Engine hop | Constants | Render line |
|---|---|---|---|---|---|---|
| 3.1 | POST to `/api/orchestrator/process` with `{category, statement, product_evidence?}` | `POST /api/orchestrator/process` | `02_Technical/src/server/app.py:567` (`orchestrator_process()`) | `src/agents/orchestrator.py:Orchestrator.process_input()` (line 57) | n/a | (REPL stdout, or no UI) |
| 3.2 | Orchestrator instantiates | n/a | `02_Technical/src/server/app.py:571` (`core = Orchestrator()`) | `src/agents/orchestrator.py:38-45` (`__init__`, attaches `TauFirewall` and `AgentJobDelegator`) | n/a | n/a |
| 3.3 | `Form_Entry_Agent` records the input as a job token | n/a | n/a | `src/agents/orchestrator.py` (delegates to `form_entry_agent.py`) | n/a | n/a |
| 3.4 | `Audit_Review_Agent` runs Deception + BBFB | n/a | n/a | `src/agents/audit_review_agent.py` (calls `audit_text()` and `calculate_bbfb()`) | per Flow 1 + 2 | n/a |
| 3.5 | `Lattice_Compute_Agent` runs the real-options lattice | n/a | n/a | `src/agents/lattice_compute_agent.py` (calls `hardened_compound_binomial_gate()`) | per Flow 2 | n/a |
| 3.6 | `Ledger_Seal_Agent` writes a `AUDIT_CYCLE_COMPLETE` block to the Merkle chain | n/a | n/a | `src/agents/ledger_seal_agent.py` → `src/io/vault_io.py:append_block()` (line 105) | n/a (deterministic SHA-256 chain) | n/a |
| 3.7 | (return) Decision JSON `{finalAction, summary, ...}` | n/a | `02_Technical/src/server/app.py:580` (`return result`) | n/a | n/a | (REPL stdout) |

**The `TauFirewall` (`src/agents/tau_firewall.py`) wraps the whole thing: it enforces `audit_runtime / available_runtime < 0.10` (`02_Technical/config/constants.py:16`).**

---

## Flow 4 — Merkle seal verification (the audit's "is the chain intact?" check)

**Scenario:** The operator wants to confirm the chain on disk has not been edited. They run `python -m src.verify_chain` from `02_Technical` (or visit the Ledger tab in the UI, which calls the same path through HTTP).

| Step | Operator gesture | HTTP request | Server hop | Engine hop | Constants | Render line |
|---|---|---|---|---|---|---|
| 4.1 | Standalone: `python -m src.verify_chain` (or click "Ledger" tab → "Verify" button) | n/a (CLI) or `GET /api/verify-chain` | `02_Technical/src/verify_chain.py:VERIFY()` → `02_Technical/src/server/app.py:203` (`verify_chain()`) | n/a | n/a | stdout (CLI) or `02_Technical/web/index.html:399` (the ledger table) |
| 4.2 | Read `facts_registry.json` blocks | n/a | n/a | `02_Technical/src/io/vault_io.py:read_facts_registry()` (line ~30) | n/a | n/a |
| 4.3 | Re-derive each block's `current_hash` | n/a | n/a | `02_Technical/src/io/vault_io.py:append_block()` line 124 (the SHA-256 chain formula) | n/a | n/a |
| 4.4 | Compare re-derived `merkle_root` to stored `data["merkle_root"]` | n/a | n/a | `02_Technical/src/io/vault_io.py:merkle_stats()` (line 166) | n/a | n/a |
| 4.5 | Print MATCH or BROKEN | n/a | n/a | n/a | n/a | stdout: `RESULT: MATCH -- chain is intact.` |

**Five files. Every number on the Ledger tab is in those five files. The chain re-derivation is the proof of audit integrity.**

---

## Flow 5 — Agentic REPL tool-call round trip (Ollama local)

**Scenario:** The operator launches `python -m tools.agentic_repl` and asks "is the chain intact?" The REPL loops with Ollama (local, `127.0.0.1:11434`) until Ollama returns a plain assistant message.

| Step | Operator gesture | HTTP request (Ollama) | REPL hop | Engine hop | Constants | Render line |
|---|---|---|---|---|---|---|
| 5.1 | Run `python -m tools.agentic_repl` | n/a (startup) | n/a | n/a | n/a | (REPL banner) |
| 5.2 | Type the question, press enter | n/a (in-process prompt) | n/a | n/a | n/a | (REPL prompt) |
| 5.3 | REPL sends messages + tools to Ollama | `POST http://127.0.0.1:11434/api/chat` with `{model, messages, tools}` | `02_Technical/tools/agentic_repl.py` (the `urllib.request.Request` call) | n/a (Ollama is local, not a project module) | n/a | n/a |
| 5.4 | Ollama returns `tool_calls: [{name, args}]` | n/a | n/a | n/a | n/a | n/a |
| 5.5 | REPL executes the tool — typically `http POST http://127.0.0.1:3000/api/verify-chain` | `POST /api/verify-chain` (local) | `02_Technical/tools/agentic_repl_tools.py` (the `audit_text` / `verify_root` / etc. wrappers) | `02_Technical/src/server/app.py:203` (`verify_chain()`) → `02_Technical/src/io/vault_io.py:merkle_stats()` | n/a | n/a |
| 5.6 | REPL sends the tool result back to Ollama as `{role: "tool"}` | `POST http://127.0.0.1:11434/api/chat` | `02_Technical/tools/agentic_repl.py` (loop) | n/a | n/a | n/a |
| 5.7 | Ollama returns a plain assistant message | n/a | n/a | n/a | n/a | n/a |
| 5.8 | REPL prints the assistant message | n/a | n/a | n/a | n/a | stdout |

**The REPL is a thin Ollama client. It does NOT call into `src/engines` or `src/agents` directly. Every tool call is a normal HTTP request to `127.0.0.1:3000` — the same surface the web UI uses. The boundary rule that tests/ follows (`tests/` may not import from `src/`) is the same rule the REPL follows: cross the boundary through HTTP, not through Python imports.**

---

## How the flows fit together

- **Flow 1 (Deception)** is the operator's primary input — the human-readable text scan. A text-only audit goes no further than this.
- **Flow 2 (BBFB + Lattice)** is the structured-evidence audit. The operator must supply ProductEvidence. A BBFB-only audit goes no further than the four gates.
- **Flow 3 (Orchestrator)** is the end-to-end audit. It runs Flow 1 and Flow 2 under the orchestrator, then seals the result to the chain.
- **Flow 4 (Verify)** is the integrity check. It is orthogonal to the audit direction: it confirms the chain on disk has not been edited.
- **Flow 5 (REPL)** is the operator's natural-language interface. It routes through the same HTTP surface as the web UI. The boundary is `127.0.0.1:3000` for both.

Every flow is in the source tree. Every number on the screen is in those files. The constants are in `02_Technical/config/constants.py`. The chain is at `03_Vault/facts_registry.json`. The chain re-derivation is at `02_Technical/src/verify_chain.py`. The receipts are in the chain.

---

## What this document does NOT cover

- **The 54 patterns themselves.** The pattern list is in `02_Technical/src/engines/deception_ontology_data.py` and `01_Methodology/DECEPTION_ONTOLOGY.md`. This document traces where the patterns are USED, not the patterns themselves.
- **The boundary test.** The 00-99 spatial boundary is enforced by `tests/test_00_99_boundary.py`, which is itself described in STRATEGY.md §6.1. This document is downstream of that rule.
- **The Tauri shell.** The Tauri wrapper changes the wrapping (a desktop binary vs a browser), not the audit. The shell invokes the same FastAPI surface; the audit path is the same.
- **The 1-2-3 backup plan.** The recovery procedure is in `04_Validation/hardcopy/HARD_COPY_BACKUP_PLAN_1-2-3.txt`. This document assumes the project tree is intact.

---

## How to extend

If a new flow is added to the UI:

1. Add a new section to this document with the same six-column table.
2. Add a new row to AUDIT_NO_BLACK_BOX.md if the flow introduces a new pillar.
3. Re-run `python 04_Validation/scripts/audit_no_network.py` and confirm PASS.
4. Re-run `python -m pytest tests/` and confirm 73+/0.
5. Seal the change to the Merkle chain.

If a flow's server hop moves (a refactor that changes the line number), update the table. If a constant is renamed, update both this document and the pillar table. The two documents are living indexes, not one-time writes.

---

## When in doubt

If a number on the screen does not have a row in either this document or AUDIT_NO_BLACK_BOX.md, the value is undocumented at the source level. That does not mean the value is wrong — it means a third party cannot verify it from the docs alone. Open the source and find the function. If you cannot find the function, push back.

The default is: **every number on the screen has a file:line in either this document or AUDIT_NO_BLACK_BOX.md. If it does not, the number is a black box until proved otherwise.**

---

*This document is sealed to the Merkle chain. To prove it has not been edited, re-derive the Merkle root and compare it to the value in `YELLOW_RIBBON.md` REF-5.*
