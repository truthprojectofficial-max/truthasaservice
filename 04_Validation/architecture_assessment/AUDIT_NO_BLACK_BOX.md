# AUDIT_NO_BLACK_BOX

**Date:** 2026-07-12
**Status:** COMPLETE — every pillar of audit output is traced to a `file:line`
**Closes:** OPEN_ITEMS_AND_REFERENCE.md D3

## What this document proves

The build's second-strongest promise is "no black boxes" — every number on the screen is computed by a Python function in this codebase, with the formula documented in `01_Methodology/`. Until now that promise was a claim. This document is the claim turned into a per-pillar traceability table.

A third party with the project folder can open the file listed next to any number in the UI, jump to the cited line, and read the exact expression that produced the value. No number on the screen is a magic constant, an LLM output, or an opaque service call.

## Pillar-to-source traceability

| Pillar | UI shows | Computed by | Constants / thresholds | Source line |
|---|---|---|---|---|
| **Entropy** | `shannonEntropy`, `normalizedEntropy`, `anomalyFlag`, `lowEntropyFlag` | `shannon_entropy()` | `SHANNON_ANOMALY_THRESHOLD`, `SHANNON_LOW_THRESHOLD` | `02_Technical/src/engines/deception_scanner.py:25` (function), `51-52` (thresholds), `02_Technical/config/constants.py:73-75` (constants) |
| **Deception (matches)** | `detectedPatterns[]`, `matchedIndicators[]`, `confidence` per match | `detect_patterns_with_confidence()` | 54 patterns × indicators in `DECEPTION_ONTOLOGY` | `02_Technical/src/engines/deception_scanner.py:56` (function), data in `02_Technical/src/engines/deception_ontology_data.py`, version in `02_Technical/config/constants.py:82` |
| **Deception (probability)** | `deceptionProbability` (0..1) | `calculate_deception_probability()` | `DECEPTION_PROBABILITY_VETO = 0.75`, `DECEPTION_PROBABILITY_LOW = 0.30` | `02_Technical/src/engines/deception_scanner.py:104` (function), `02_Technical/config/constants.py:80-81` (constants) |
| **Deception (verdict)** | `CLEAN` / `FLAGGED` / `REFUSAL` | `audit_text()` (top-level orchestrator inside scanner) | uses `SHANNON_*` + `DECEPTION_PROBABILITY_VETO` | `02_Technical/src/engines/deception_scanner.py:167` (function) |
| **LAW gate** | 6 metrics, each with `value`/`threshold`/`passed`; overall `lawPass` | `calculate_bbfb()` LAW section | `PERFORMANCE_FLOOR = 0.50`, `EFFICIENCY_FLOOR = 0.30`, `WARRANTY_FLOOR = 1.00`, `ISSUE_DENSITY_FLOOR = 0.10`, `VIOLATION_RATIO_FLOOR = 0.05` | `02_Technical/src/engines/bbfb_engine.py:86-111` (LAW block), `02_Technical/config/constants.py:25-29` (constants) |
| **GRACE gate** | `rawPenalty`, `normalizedPenalty`, `riskLevel` | `calculate_bbfb()` GRACE section | `GRACE_QUADRATIC_COEFFICIENT = 2.0`, `GRACE_CRITICAL_THRESHOLD = 0.75` | `02_Technical/src/engines/bbfb_engine.py:113-124` (GRACE block), `02_Technical/config/constants.py:34-35` (constants) |
| **FRUIT gate (CVS)** | `compositeValueScore`, `weightedScores[]`, `compliant` | `calculate_bbfb()` FRUIT section | `FRUIT_WEIGHTS = {cost:0.4, performance:0.3, reliability:0.2, compliance:0.1}`, `CVS_THRESHOLD = 0.0005` | `02_Technical/src/engines/bbfb_engine.py:126-139` (FRUIT block), `02_Technical/config/constants.py:40-50` (constants) |
| **Valuation (lattice)** | Real-options two-stage compound binomial value | `hardened_compound_binomial_gate()` | `REAL_OPTIONS_S0`, `_K1`, `_K2`, `_T1`, `_T2`, `_R`, `_SIGMA1`, `_SIGMA2`, `_N1`, `_N2`, `_LEARNING_DELTA`, `_STRIKING_RATIO`, `_SIGMA_MIN`, `_SIGMA_MAX` | `02_Technical/src/engines/real_options_lattice.py:50` (function), `02_Technical/config/constants.py:55-68` (constants). Binomial step: `real_options_lattice.py:33` |
| **Decision gate** | `GO` / `DEFER` / `TEST FIRST` / `REJECT` | `audit_text()` (Deception) + `calculate_bbfb()` (BBFB) + `hardened_compound_binomial_gate()` (Lattice) — all wired in the orchestrator | combination of the above | `02_Technical/src/agents/orchestrator.py` (orchestration), `02_Technical/src/server/app.py:501` (HTTP surface `/api/orchestrator/process`) |
| **Evidence parser** | `parsed.price_paid`, `parsed.spec_measured`, `parsed.warranty_months`, etc. | `extract_product_evidence()` | regex patterns in function body | `02_Technical/src/io/evidence_parser.py:86` (function), regex patterns at top of file |
| **Pipeline** | `PipelineResult` for a whole document (Markdown / PDF / DOCX outputs) | `process_file()` / `process_directory()` | n/a (calls into engines above) | `02_Technical/src/io/pipeline.py:67` and `:155` (functions) |
| **Tau firewall** | `auditMsTotal`, `availableRuntime`, `extractionRatio`, `ceiling` | `TauFirewall` (agents/tau_firewall.py) | `TAU_EXTRACTION_CEILING = 0.10` | `02_Technical/src/agents/tau_firewall.py` (entire module), `02_Technical/config/constants.py:16` (ceiling) |
| **Merkle seal** | `current_hash`, `previous_hash`, `merkle_root`, block count | `vault_io.append_block()` | n/a (deterministic SHA-256 chain) | `02_Technical/src/io/vault_io.py:85` (function) |
| **Affidavit (Section 177)** | Markdown body that an officer can sign | `LegalAffidavitGenerator` | n/a (template + facts_registry read) | `02_Technical/src/engines/legal_affidavit_generator.py` |
| **ACL demand (Section 56)** | Markdown body that can be sent to a supplier | `ACLDemandGenerator` | n/a (template + evidence) | `02_Technical/src/engines/acl_demand_generator.py` |

## How a third party uses this table

1. Pick a number on the screen that you want to verify.
2. Find the row in the table above that matches the pillar.
3. Open the cited file at the cited line.
4. Read the Python expression.
5. If the constants are involved, open `02_Technical/config/constants.py` at the cited line and confirm the value.

If the file does not exist, the line does not match, the constant has been renamed, or the function is now imported from a third-party library, the black-box claim is broken. Push back.

## What this document does NOT cover

- **The 54 patterns themselves.** Each pattern is a `(name, severity, indicators, threshold)` tuple in `02_Technical/src/engines/deception_ontology_data.py`. The complete list is in that file and in `01_Methodology/DECEPTION_ONTOLOGY.md`. This document traces where the patterns are USED, not the patterns themselves.
- **Tau runtime enforcement.** The 10% extraction ceiling is enforced at runtime by `TauFirewall`. The enforcement logic is in the file, but the human-readable rationale is in `00_Strategy/GOVERNANCE.md` and the operator manual.
- **Cross-cutting concerns** like UTC stamping, sort_keys canonical JSON, and atomic writes — these are in `vault_io.py` and `monitor_agent.py`, not in any single pillar. They are described in `00_Strategy/STRATEGY.md` and the YAML/methodology docs.

## How to extend

If a new pillar is added to the UI (for example, a "compliance heatmap" or a "vendor history score"):

1. Add the new pillar to the table above with a `file:line` reference.
2. Write the engine that produces the number.
3. Wire it into the orchestrator + HTTP surface.
4. Re-run the no-network audit (`04_Validation/scripts/audit_no_network.py`).
5. Update this document and seal the change to the Merkle chain.

If a pillar's source line moves, update the table. If a constant is renamed, update the table. The document is a living index, not a one-time write.

## When in doubt

If a UI element does not have a row in this table, the value is undocumented at the source level. That does not mean the value is wrong — it means a third party cannot verify it from this document alone. Open the source and find the function. If you cannot find the function, push back.

The default is: **every number on the screen has a `file:line` in this document. If it does not, the number is a black box until proved otherwise.**

---

*This document is sealed to the Merkle chain. To prove it has not been edited, re-derive the Merkle root and compare it to the value in `YELLOW_RIBBON.md` REF-5.*
