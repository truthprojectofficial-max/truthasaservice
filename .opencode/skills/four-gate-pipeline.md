---
description: "Use when changing audit-related code. The 4-gate pipeline: Deception (N-pattern ontology + Shannon entropy), BBFB (LAW veto + GRACE penalty + FRUIT product + CVS), Optionality Lattice (deception-adjusted, NOT a valuation), Decision (GO/REVIEW/REFUSED/REJECT). LATTICE_FRAMING must surface on every output."
---

# Four-Gate Pipeline Skill

Every audit input runs through 4 gates, in order. Knowing what each
gate does prevents the two most common mistakes: mis-framing the
lattice as a valuation and misdiagnosing a LAW veto as a bug.

## The 4 gates

### Gate 1: Deception
- **What:** N-pattern deception ontology (v3.12, 69 patterns, 3 tiers)
  + Shannon entropy (anomalies > 4.5 bits flagged).
- **Output:** Which patterns fired, entropy score, deception flag.
- **Tiers:** dialects (DD-001..055) + structural mechanics (DD-056..067)
  + linguistic markers.

### Gate 2: BBFB (Best Behavior For Business)
- **What:** The compliance gate. Four sub-engines:
  - **LAW** — multiplicative veto. One fail = 0. This is the hard veto.
  - **GRACE** — quadratic penalty. Veto fires above 0.75.
  - **FRUIT** — weighted product across pillars.
  - **CVS** — compound verification signal.
- **Output:** Compliance score, veto status, penalty status.
- **Common mistake:** A LAW veto produces a zero lattice value. This is
  NOT a bug — it is the veto working. Do not "fix" a zero lattice value
  caused by a LAW veto.

### Gate 3: Optionality Lattice
- **What:** A deception-adjusted compound binomial lattice (Cox-Ross-
  Rubinstein). NOT a business valuation. The `LATTICE_FRAMING`
  constant must surface on every response that includes a lattice value.
- **Output:** An optionality index, not a dollar valuation.
- **Critical:** The lattice is reframed (F7, 2026-07-18) as a
  deception-adjusted optionality index. If any output presents it as
  a business valuation, the legal disclaimer breaks. The
  `LATTICE_FRAMING` string in `config/constants.py` is the canonical
  text — it must appear verbatim on every lattice-bearing response.

### Gate 4: Decision
- **What:** The final gate combines gates 1-3 into a verdict.
- **Verdicts:** GO / REVIEW_REQUIRED / REFUSED / REJECT
- **Traffic light:** R (REFUSED) / G (GO) / Y (REVIEW_REQUIRED) +
  directional + machine eval (CLEAN/REVIEW/REFUSED)

## The 5 pillars of audit output

Every audit response surfaces these 5 pillars:
1. Entropy (Shannon)
2. Deception Patterns (which fired)
3. LAW Gates (pass/fail per check)
4. GRACE Penalty (quadratic score)
5. CVS (compound verification signal)

## The agents (5 named agents wired by the Orchestrator)

| Agent | Role |
|-------|------|
| Form_Entry | Ingests and validates input |
| Audit_Review | Runs the deception + BBFB gates |
| Lattice_Compute | Runs the optionality lattice |
| Ledger_Seal | Seals the decision to the chain |
| Affidavit | Produces the legal affidavit |

The Orchestrator is the single runtime entry point. It delegates to
agents via `AgentJobDelegator` (MCP hand-off, URN `OGIR:<SPACE>:<ACTION>`).

## The rule

The 4 gates are the audit. Know what each does before changing audit
code. The lattice is optionality, not valuation — surfacing it wrong
breaks the legal disclaimer. A LAW veto producing zero is correct
behavior, not a bug.