# Real-Options Lattice -- Plain-Math Derivation

The runtime implements a two-stage compound binomial lattice (Cox-Ross-Rubinstein).

**FRAMING (F7, added 2026-07-18):** the output of this lattice is a
**deception-adjusted optionality index**, NOT a business valuation. The
S0, K1, K2 inputs are hard-coded defaults in `config/constants.py`
(`REAL_OPTIONS_S0=55.0`, `REAL_OPTIONS_K1=18.0`, `REAL_OPTIONS_K2=10.0`).
They do NOT derive from the audited business's actual financial
statements. The output value is therefore a stylised compound option
under a stylised volatility regime -- useful for ranking candidates and
for the deception-aware learning-delta story, but defensibly *not* a
number to file as the value of the business. Any consumer of this
lattice (the orchestrator, the affidavit, the audit review agent, the
agentic REPL) MUST surface the `LATTICE_FRAMING` constant in its
output so a third-party reader cannot mistake the optionality index for
a valuation. The lattice is a stylised pricing model, not a forensic
accounting tool. See section 6 below for the operator-facing framing.

## 1. Stage 1: Single-Period Binomial (Cox-Ross-Rubinstein)

`
dt    = T1 / n1
u_1   = exp(sigma_1 * sqrt(dt))
d_1   = 1 / u_1
p_1   = (exp(r * dt) - d_1) / (u_1 - d_1)
S_u   = S0 * u_1
S_d   = S0 * d_1
V_u   = max(S_u - K1, 0)
V_d   = max(S_d - K1, 0)
V_1   = exp(-r * dt) * (p_1 * V_u + (1 - p_1) * V_d)
`

The "up" state represents the upside scenario where the asset value grows by u_1
and the "down" state represents the downside. The risk-neutral probability p_1
ensures the model is arbitrage-free.

## 2. Stage 2: Compound Option

The Stage-2 spot price is the Stage-1 value plus a learning delta:

`
learning_delta = 10.0 * (1 - 0.6 * deception_score)
S0_2           = V_1 + learning_delta
`

deception_score comes from the Deception Scanner. A high deception score reduces
the learning delta — an organisation that signals deception learns less between
Stage 1 and Stage 2.

Stage 2 then applies the same binomial formula with K2, T2, sigma_2 and 
2.

## 3. Total Compound Value

`
V_total = V_1 + V_2
threshold = (K1 + K2) * 0.85
decision  = "GO"  if V_total > threshold
            "DEFER" otherwise
`

## 4. Volatility Adjustments

The runtime clamps the deception-adjusted volatility to [0.05, 0.95] and the
entropy-adjusted volatility to [0.05, 0.90]. This prevents pathological inputs
from producing nonsensical valuations.

## 5. Audit Determinism

The lattice uses no random number generator. The same inputs always produce the
same output. This is required for the audit trail to be reproducible.

## 6. Framing (operator-facing, F7 2026-07-18)

This lattice is **not a business valuation**. It is a deterministic
optionality index under stylised inputs. The two are not the same.

A **business valuation** is a number derived from the audited
business's actual financial statements: revenue, EBITDA, debt,
working capital, comparable transactions, discounted cash flow. It
requires inputs the lattice does not read -- because the lattice is
intentionally decoupled from the audit (a CONSTANTS_BUMP to a
business-valuation calculation would require either a hard-coded
financial model or a parser that extracts the numbers from real
correspondence, neither of which the project has built).

An **optionality index** is a number derived from a stylised pricing
model: a stylised current value (S0=55.0), two stylised exercise
prices (K1=18.0, K2=10.0), stylised volatilities, and a stylised
risk-free rate. The Cox-Ross-Rubinstein binomial lattice prices the
compound option these inputs describe. The output is the lattice
price of *that option*, not the value of the business.

**The deception adjustment** is the part that gives the lattice its
audit value. The 54-pattern deception ontology is run on the input
text, and the resulting `deception_score` raises Stage-1 volatility
(more deception = more uncertainty about whether the option will
pay off) and shrinks the learning-delta (deception reduces what is
learned between Stage 1 and Stage 2). A high-deception input pushes
the optionality index down; a clean input leaves it at the stylised
default. This is the audit's *signal*: a high-deception input
deserves a smaller optionality index, regardless of the lattice's
raw computation.

**What a third-party reader sees in the s.177 affidavit or the audit
output** is the `optionalityGate` block with the framing string
embedded:

```
"optionalityGate": {
    "decision": "GO" | "DEFER" | "TEST FIRST" | "REJECT",
    "totalValue": <number>,
    "threshold": <number>,
    "framing": "deception-adjusted optionality index (not a business valuation)"
}
```

The framing string is mandatory. It is loaded from
`LATTICE_FRAMING` in `config/constants.py` and surfaced on every
lattice output. A future operator who wants to wire the lattice
inputs to extracted evidence (replacing `REAL_OPTIONS_S0=55.0` with
a parser-derived current value) is welcome to do so; the framing
disclaimer can be relaxed at that point via a CONSTANTS_BUMP seal.

**What this lattice CAN say**:
- Whether a given input text has a deception signature that
  warrants raising the volatility adjustment.
- Whether a given input text has a learning-delta profile that
  suggests the Stage-2 investment is or is not justified.
- Whether two candidates differ enough in their deception scores
  that the lattice ranks them differently.

**What this lattice CANNOT say**:
- The market value of the audited business.
- The replacement cost of the audited business's assets.
- The recoverable damages from the audited business's conduct.
- Any number that should appear in a financial report, a tax
  return, or a court affidavit as a "valuation".

The build's `BusinessVerdict` dataclass and the orchestrator's
`optionalityGate` block both carry the framing disclaimer. The
s.177 affidavit, the ACL s.56 demand letter, and the markdown
audit report all surface the framing in their headers. A future
contributor who wants to remove the framing must first wire real
financial inputs to the lattice AND seal a CONSTANTS_BUMP block
recording the change.

