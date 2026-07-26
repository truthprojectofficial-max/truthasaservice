# Value + Business PDF Analysis — Integration with OGIR

> Created 2026-07-24. Sealed to chain.
> Sources: 2 PDFs from AI INTERACTIONS folder
> Sealed to chain: `VALUE_BUSINESS_PDF_ANALYSIS_2026_07_24`

---

## THE TWO PDFs

### 1. Unifying Human Value in BBFB Audits.pdf (16 pages, 473KB)

**What it is:** A research paper proposing a framework that maps OGIR's
raw machine telemetry (LAW/GRACE/FRUIT scores) to human-interpretable
Quality of Life (S-QoL) dimensions using health economics methodology.

**Key concepts:**

- **S-QoL (Systemic Quality of Life)** — a 5-dimension scale that
  translates machine outputs into human value:
  1. Systemic Vitality (is the system alive and running?)
  2. Structural Integrity (is it structurally sound?)
  3. Transactional Execution (does it do what it says?)
  4. Operational Morbidity (how often does it fail?)
  5. Systemic Vulnerability (how exposed is it?)

- **MAPS (MApping onto Preference-based measures reporting Standards)** —
  an auditable mapping from raw math to human-interpretable scores.
  Originally from health economics (clinical trials → patient QoL).

- **MCDA (Multi-Criteria Decision Analysis)** — the methodology for
  weighting multiple dimensions into a single composite.

- **Worth Curves** — econometric mixture models that translate the
  FRUIT composite value score into a "worth" metric humans can
  understand (like a DALY/QALY in health economics, but for systems).

- **Deception connection:** The paper explicitly mentions the
  Deception Gate and how deception scores feed into the lattice
  volatility calculation. "As inputs become more deceptive or
  unstable, the calculated volatility increases."

### 2. business-evaluation-guide.pdf (33 pages, 1.7MB)

**What it is:** CPA Australia's official business evaluation guide.
Covers financial + non-financial evaluation methods for businesses.

**Key concepts:**

- **Financial evaluation:** balance sheet, P&L, cash flow, ratios
- **Non-financial evaluation:** economic factors, competitive market,
  human resources, global events — "likely to have a financial impact"
- **Key drivers:** each business has unique drivers; evaluate against
  those, not a standard template
- **Regular evaluation:** align with reporting requirements (BAS/ATO)
  for "sound empirical evidence"
- **3-part series:** (1) evaluation, (2) improving performance,
  (3) dashboard reporting

---

## THREADS THAT CONNECT TO OGIR

### Thread 1: S-QoL maps FRUIT to human value

The BBFB Audits PDF proposes exactly what OGIR's valuation engine is
missing: a translation layer from the FRUIT composite value score
(0.0005 to 1.0) to a human-interpretable "worth" metric.

Currently, FRUIT returns a number (e.g., 0.847). The operator has to
interpret what that means. The S-QoL framework would translate it:

| FRUIT score | S-QoL level | Human meaning |
|-------------|------------|---------------|
| 0.85-1.0 | Excellent | The product delivers what it claims. High value. |
| 0.70-0.85 | Good | The product mostly delivers. Acceptable value. |
| 0.50-0.70 | Marginal | The product falls short in measurable ways. Review needed. |
| 0.30-0.50 | Poor | The product significantly under-delivers. Risk of harm. |
| 0.00-0.30 | Critical | The product fails to deliver. Economic harm likely. |

**What I can do:** Add a `s_qol_interpretation` field to the BBFB
response that translates the composite value score into a human-
readable verdict. Pure stdlib, no dependencies.

### Thread 2: MAPS provides the auditable mapping standard

The MAPS framework from health economics gives OGIR a proven,
auditable standard for mapping raw math to human scores. The chain
already seals every audit decision; MAPS would be the methodology
layer that says "this is HOW we translate the math, and it's
auditable because it follows a recognized standard."

**What I can do:** Document the MAPS adaptation in the methodology
docs. The mapping is deterministic (same FRUIT score = same S-QoL
level = same human verdict on any host).

### Thread 3: Deception-adjusted valuation connects to S-QoL

The deception-adjusted valuation I just built (block 40903) reduces
the FRUIT performance pillar when deception is detected. The S-QoL
framework would show this as a reduction in "Transactional Execution"
(does it do what it says?) — because if the description is deceptive,
the answer is "probably not."

| Deception probability | S-QoL Transactional Execution |
|-----------------------|-------------------------------|
| 0% (clean) | Full score — trust the claims |
| 50% (review) | Discounted — partial trust |
| 80% (high) | Heavily discounted — don't trust |
| 100% (refused) | Zero — the claims are fabricated |

### Thread 4: CPA guide adds non-financial drivers

The CPA business evaluation guide says: "The process should not be
limited to a financial review. Non-financial drivers (economic factors,
competitive market, human resources, global events) likely have a
financial impact."

OGIR's FRUIT currently uses 4 pillars: cost, performance, reliability,
compliance. The CPA guide suggests adding:
- **Market position** (competitive context)
- **Human resources** (operator capability, team)
- **Economic factors** (macro conditions)
- **Global events** (supply chain, regulatory changes)

These are NOT product-specific (like cost/performance/reliability/
compliance) — they're business-context-specific. They would be a
new layer ABOVE FRUIT: the Business Context Score (BCS).

**What I can do:** Add an optional `business_context` parameter to
the BBFB engine that, when provided, adds a 5th pillar to FRUIT:
"context_fit" (how well the product fits the business context).
This is NOT a veto (LAW), NOT a penalty (GRACE), but a modifier
on the composite value (FRUIT).

### Thread 5: The deception-adjusted valuation IS the "human value" layer

The BBFB Audits PDF's core argument: "translate raw mathematical
variables into structured dimensions of Systemic Quality of Life."
The deception-adjusted valuation does exactly this:
- Raw math: deception probability (0.0-1.0) + FRUIT score (0.0-1.0)
- Human dimension: "can you trust this product?" (the S-QoL
  Transactional Execution dimension)
- The discount IS the human value translation

---

## WHAT I CAN DO NOW

1. **Add S-QoL interpretation to BBFB response** — translate the
   FRUIT composite score into a human-readable 5-level verdict
   (Excellent/Good/Marginal/Poor/Critical). Pure stdlib.

2. **Add deception-adjusted S-QoL** — show how deception reduces
   the S-QoL Transactional Execution dimension specifically.

3. **Add optional Business Context Score** — a 5th FRUIT pillar
   for market position, human resources, economic factors, global
   events. Optional (not required for the core pipeline).

4. **Document the MAPS adaptation** — in the methodology docs, so
   the mapping from math to human value is auditable and follows
   a recognized standard.

5. **Add worth curves** — the econometric mixture model that
   translates FRUIT into a "worth" metric. This is the ultimate
   output: not "0.847" but "this product is worth $X to this
   business, given the deception risk and the business context."

---

**These 2 PDFs provide the bridge between OGIR's raw math and
human-interpretable value. The S-QoL framework is the translation
layer. The CPA guide adds the business context. The deception-
adjusted valuation IS the human value discount. Together they make
OGIR's output not just a deception score but a worth assessment.**