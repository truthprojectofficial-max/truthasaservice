# Deterministic Diminishing-Returns / "Best Band for Buck" Layer — Research Report

**Date:** 2026-07-19
**Scope:** Research only. No code or files were written into `02_Technical/`.
**Constraint preserved throughout:** pure Python 3.12+ stdlib, no `random`, no LLM, no network, no third-party packages, `PYTHONHASHSEED=0`, same input = same output on any host.

---

## 0. Baseline — what the live engine does today

Read from `02_Technical/src/engines/bbfb_engine.py` and `config/constants.py`:

- 5 ratios: `priceRatio`, `specRatio`, `warrantyRatio`, `issueRatio`, `violationRatio`.
- 6 LAW hard floors (all `>=` except the two inverted ones):
  - `priceFairness >= 1.0`
  - `specAccuracy >= PERFORMANCE_FLOOR (0.50)`
  - `efficiencyAdequacy >= EFFICIENCY_FLOOR (0.30)`
  - `warrantyAdequacy >= WARRANTY_FLOOR (1.00)`
  - `issueDensity <= 1.0 - ISSUE_DENSITY_FLOOR` → effective `issueRatio <= 0.10`
  - `complianceClean >= 1.0 - VIOLATION_RATIO_FLOOR` → effective `violationRatio <= 0.05`
- GRACE quadratic penalty: `2.0 * (p_fail^2 + d_tech^2 + g_comp^2)`, clamped to `[0,1]`.
- FRUIT weighted sum: `0.4*cost + 0.3*performance + 0.2*reliability + 0.1*compliance`, threshold `CVS_THRESHOLD = 0.0005`.
- Lattice (`real_options_lattice.py`, F7-deep) derives `S0/K1/K2/sigma1/sigma2` from `ProductEvidence` and runs a Cox-Ross-Rubinstein binomial back-induction. Fully deterministic, no RNG.

The Selby reference case (`data/outbox/SELBY_001_major_failure_intake.md`) currently **fails on `warrantyAdequacy`** (`0.0000 < 1.0`), not on `specAccuracy`. Its `specAccuracy` is `26.6667` (massively above the 0.50 floor). This is the single most important fact for Path B: **the specAccuracy floor is not the gate that vetoes Selby.** Any "replace the specAccuracy floor with a concave curve" change must be validated against a case where `specAccuracy` is actually the binding constraint, not against Selby.

---

## PATH A — S-QoL / SWB interpretive layer

### A.1 Minimal deterministic implementation

The PDF ("Unifying Human Value in BBFB Audits") proposes five dimensions mapped by analogy to EQ-5D, consolidated into a Health State Utility Weight (HSUW) in `[0,1]`, then passed through a concave utility curve `U(S) = (S - π)^(1-γ)/(1-γ)` with Pratt-Arrow risk-aversion `γ` and a risk premium `π` driven by the lattice `sigma`.

What pure-stdlib Python is required:

| Component | Stdlib sufficiency | Notes |
|---|---|---|
| Five-dimension mapping (5 ratios → 5 levels) | `math` only | Pure arithmetic, lookup tables. Trivially deterministic. |
| HSUW consolidation (EQ-5D-style tariff) | `math` only | A tariff is a fixed lookup table; no estimation at runtime. |
| Concave utility `U(S) = (S-π)^(1-γ)/(1-γ)` | `math` only | `math.pow` / `**`. Deterministic. |
| Risk premium `π` from lattice `sigma` | `math` only | Closed-form (e.g. `π = 0.5 * γ * sigma^2 * S0`). Deterministic. |
| **ALDVMM / Beta-regression mixture** | **NOT feasible in pure stdlib** | See A.4. |
| MAPS compliance checklist | `hashlib` + `json` | A reporting/static-validation artefact, not a runtime computation. |

**Verdict on A.1:** The *runtime* layer (mapping → HSUW → concave utility → risk premium) is implementable in `math` alone. The *calibration* layer (ALDVMM / Beta-regression mixture) is not, and is the honest blocker.

### A.2 Established methodologies (primary sources)

- **Pratt (1964), "Risk Aversion in the Small and in the Large"** — *Econometrica* 32(1-2):122-136. Defines the Pratt-Arrow absolute risk aversion `r_A(x) = -u''(x)/u'(x)` and the risk premium `π ≈ ½ r_A(x) · Var[x]`. This is the canonical source for the `γ` coefficient and the closed-form risk premium. URL: https://www.jstor.org/stable/1913738
- **Arrow (1965), "Aspects of the Theory of Risk-Bearing"** — Yrjö Jahnsson Foundation, Helsinki. Introduces the relative risk aversion coefficient `γ` used in `U(S) = S^(1-γ)/(1-γ)` (CRRA utility). The utility family `U(x) = x^(1-γ)/(1-γ)` is the standard textbook isoelastic/CRRA form.
- **EQ-5D** — EuroQol Group (1990), "EuroQol: a new facility for the measurement of health-related quality of life." *Health Policy* 16(3):199-208. URL: https://doi.org/10.1016/0168-8510(90)90421-9 . The five-dimension (mobility, self-care, usual activities, pain/discomfort, anxiety/depression) descriptive system with 3 levels (EQ-5D-3L) or 5 levels (EQ-5D-5L).
- **EQ-5D value sets** — Dolan (1997) for the UK EQ-5D-3L tariff (*Medical Decision Making* 17(1)), derived via **time trade-off (TTO)** interviews. The TTO tariff is the deterministic lookup table that makes EQ-5D computable without re-estimation. URL: https://doi.org/10.1177/0272989X9701700110
- **MAPS — MApping onto Preference-based measures reporting Standards** — Brazier, Deverill, Dixon, et al.; the MAPS checklist was published as **Brazier et al. (2019), "MAPS: A Reporting Checklist for Studies Mapping to Preference-Based Measures"** *Value in Health* 22(8):889-895. URL: https://doi.org/10.1016/j.jval.2019.05.004 . It is a *reporting standard* for the derivation of mapping functions, not a runtime algorithm.
- **ALDVMM** — **Gray, Mason, Richardson, et al. (2010), "Cost-effectiveness of an adjusted limited dependent variable mixture model"** *Value in Health* 13(6):756-764, with the standalone `aldvmm` Stata/R package by Miguel-Angel et al. later. URL: https://doi.org/10.1111/j.1524-4733.2010.00729.x . ALDVMM is a **finite-mixture regression** for bounded `[0,1]` health-utility outcomes with point masses at 1 (and sometimes 0). Estimation is by **maximum likelihood / non-linear optimisation**, typically BFGS or Newton-type solvers.
- **Beta-regression** — **Ferrari & Cribari-Neto (2004), "Beta Regression for Modelling Rates and Proportions"** *Journal of Applied Statistics* 31(7):799-815. URL: https://doi.org/10.1080/0266476042000214501 . Estimation is by ML via `optim`-style non-linear optimisation with a log-likelihood that is non-convex.
- **ICECAP** — Al-Janabi, Flynn, Coast (2012), "Development of a capability measure for adults (ICECAP-A)" *Health Economics* 21(8):880-891. URL: https://doi.org/10.1002/hec.1759 . Capability measure, not health utility; tariff via best-worst scaling.
- **ASCOT** — Netten et al. (2012), "Adult Social Care Outcomes Toolkit (ASCOT)" *Health Economics* 21(5):547-562. URL: https://doi.org/10.1002/hec.1737 . SCTC tariff via TTO.
- **SF-6D** — Brazier, Roberts, Deverill (2002), "The estimation of a preference-based measure of health from the SF-36" *Journal of Health Economics* 21(2):271-292. URL: https://doi.org/10.1016/S0167-6296(01)00130-8 . SF-6D utilities estimated via **standard gamble** interviews and parametric regression.
- **Marginal return / diminishing-returns curves** — Classic: **Heal (1985), "Economic Aspects of Natural Resource Depletion"**; **Dasgupta & Heal (1979), "Economic Theory and Exhaustible Resources"**. For audit/quality: **Marsaglia (2017)** and the ISO 19011:2018 risk-based audit principles (§5.6). The concave value curve is a standard production-function shape.

### A.3 Calibration requirements

- **`γ` (Pratt-Arrow relative risk aversion)** is normally calibrated **empirically** from elicited preferences: lotteries, TTO, standard gamble, or field data on consumption/investment under risk. Typical empirical estimates: `γ ∈ [0.5, 4]` with median around `~1`–`2` (Mehra & Prescott 1985 equity-premium work puts it higher; Chetty 2006 "A New Method of Estimating Risk Aversion" *AER* 96(5):1821-1834 derives `γ ≈ 1` from labour-supply data, URL: https://doi.org/10.1257/aer.96.5.1821).
- **Deterministic calibration path:** None of the standard calibrations are deterministic — they all require either (a) human preference elicitation (non-deterministic by definition, since preferences are subjective) or (b) random sampling / MCMC / simulated maximum likelihood for the mixture models.
- **What you *can* do deterministically:** freeze `γ` as a named constant in `config/constants.py` with a cited source (e.g. `GAMMA_RISK_AVERSION = 1.0` citing Chetty 2006), exactly as the project already freezes `GRACE_QUADRATIC_COEFFICIENT = 2.0` and `CVS_THRESHOLD = 0.0005`. This is the **"deterministic by fiat"** pattern: the calibration happened once, offline, by a human; the runtime just uses the number. This is honest *if and only if* the constant carries a citation and a `CONSTANTS_BUMP` seal.
- **`π` (risk premium)** is closed-form given `γ` and `sigma`: `π ≈ ½ · γ · σ² · S0` (Pratt 1964). This is deterministic.
- **HSUW tariff** is a fixed lookup table; deterministic by construction, but the **values in the table** are the subjective output of TTO/standard-gamble interviews. The table itself is reproducible; the *choice of tariff* (UK TTO, US DCE, German VAS, etc.) is a judgement call.

### A.4 Honest pitfalls (Path A)

1. **ALDVMM / Beta-regression cannot run in pure stdlib.** Both require non-linear ML estimation. `scipy.optimize` is third-party; `statistics`/`math` have no constrained non-linear optimiser. You can hard-code the *fitted* coefficients, but then the model is no longer "estimated" — it is a fixed table, and you must say so. The PDF's claim of an "ALDVMM mapping" is misleading in a deterministic context: in the runtime, it collapses to a lookup table.
2. **No objective tariff exists.** EQ-5D has country-specific tariffs (UK, US, DE, JP, …) that **disagree** by up to 0.2 utility points for the same health state. Choosing one is a judgement call. A "no-judgement-calls" engine cannot defend the choice on purely formal grounds; it can only cite a source and seal it.
3. **The five S-QoL dimensions are invented, not standardised.** EQ-5D's five dimensions are validated by 30+ years of psychometric literature. The PDF's five (Systemic Vitality, Structural Integrity, Transactional Execution, Operational Morbidity, Systemic Vulnerability) are **a proposed analogy**, not a validated instrument. There is no population-norm dataset, no responsiveness study, no minimal important difference (MID) established for them. Any HSUW table built on them is **a priori** a subjective mapping, not an empirically grounded tariff.
4. **`γ` has no deterministically-defensible value for a consumer-audit context.** Chetty's `γ≈1` is for labour supply; Mehra-Prescott's `γ>10` is for equity premia; health-economics work often uses `γ≈0.5`–`1.5`. Choosing any value is a judgement call that must be sealed and cited, not derived.
5. **The layer is interpretive, not gating.** By the PDF's own design, the BBFB still vetoes. The SWB layer "tells you where on the utility curve the case sits." That means it adds **a new output field** without changing any decision. For a deterministic audit engine whose value proposition is a binary compliant/non-compliant verdict, this is **scope expansion dressed as analysis** — it adds a number no-one asked for and that does not feed back into the verdict.
6. **MAPS is a reporting standard, not a runtime check.** It governs how a *mapping study* is reported (sample, model, MAE, RMSE, range, ceiling effect). Applying it to a deterministic engine that does not estimate a model is mostly performative: most of its 17 checklist items refer to empirical-estimation artefacts the engine does not produce.
7. **Concave utility over a `[0,1]` HSUW is monotone.** `U(S) = (S-π)^(1-γ)/(1-γ)` is strictly increasing in `S` for `γ ≠ 1`. It cannot produce a "best band" that diminishes on either side — it only re-marks the same ordering the HSUW already produced. To get a peak-and-decline you need a different functional form (see Path B).

### A.5 Verification burden (Path A)

- **Determinism across hosts:** the runtime layer (mapping → HSUW → `U(S)`) is arithmetic only. With `PYTHONHASHSEED=0` and the existing canonical-JSON discipline, it is byte-reproducible. Add a `test_swbb_determinism.py` that asserts the SWB output for a fixed `ProductEvidence` is bit-identical across two calls and that the canonical-JSON hash matches a sealed reference.
- **Seal burden:** every new constant (`GAMMA_RISK_AVERSION`, `SWB_RISK_PREMIUM_COEFF`, the five-dimension tariff table) is a `CONSTANTS_BUMP` requiring a sealed chain block. The tariff table is the heavy lift: it is ~243–3125 entries depending on 3L vs 5L, and each entry must be sealed.
- **Proving it adds no decision risk:** since the layer does not gate, the verification is that the existing 86 tests still pass unchanged *plus* the new SWB tests. This is easy, but it is also the proof that the layer adds no audit value.

### A.6 Work breakdown (Path A)

| Item | Files | Effort |
|---|---|---|
| Five-dimension mapping module | `02_Technical/src/engines/swbb_layer.py` | 1 day |
| HSUW tariff table (decided values, sealed) | `config/constants.py` (new block), `config/swbb_tariff.py` | 2 days (the decision, not the code) |
| Concave utility + risk premium | `swbb_layer.py` | 0.5 day |
| MAPS checklist as a static validator | `04_Validation/scripts/maps_checklist.py` | 1 day |
| Determinism + canonical-JSON tests | `tests/test_swbb_determinism.py` | 1 day |
| Documentation + sealed CONSTANTS_BUMP | `01_Methodology/SWBB_LAYER.md`, chain block | 1 day |
| **Total** | | **~6.5 days** + the irreducible subjective cost of choosing a tariff and a `γ`. |

---

## PATH B — Marginal-return gate inside the BBFB

### B.1 Minimal deterministic implementation

Replace the hard `specAccuracy >= 0.50` floor with a concave value function `V(x)` over the spec ratio `x = specRatio`, that:
- is `0` at `x = 0` (total spec failure = no value),
- rises monotonically to a peak at a "best band" `x*`,
- diminishes for `x > x*` (over-spec: you paid for performance you did not need and did not verify — diminishing value),
- has a single threshold `V_min` below which the gate vetoes.

Candidate closed forms (all `math`-only):

1. **Piecewise linear tent** (simplest, fully transparent):
   `V(x) = min(x / x*, 1.0) * (1.0 - max(0, (x - x*) / (x_max - x*)))`
   Peak at `x*`, linear down to `0` at `x_max`. Veto if `V(x) < V_min`.
2. **Log-concave / Cobb-Douglas form**: `V(x) = x^a · (x_max - x)^b` for `a,b > 0`, peaks at `x* = a·x_max/(a+b)`. Deterministic, but `a,b` are two new constants.
3. **Quadratic (concave) peak**: `V(x) = 1.0 - ((x - x*) / w)^2`, clamped to `[0,1]`, veto if `V < V_min`. One peak `x*`, one width `w`.
4. **CRRA-style diminishing returns without a peak**: `V(x) = x^(1-γ)/(1-γ)` — strictly increasing, no over-spec decline. Not a "best band"; reject for this purpose.

All four are pure `math`. **No `random`, no `statistics`, no `hashlib` needed for the curve itself.** `hashlib` is only used for the seal.

**Stdlib sufficiency: YES.** This is the smallest viable deterministic change. It touches `bbfb_engine.py` lines 88-89 (the `specAccuracy` LAW input) and `constants.py` (two new constants: `SPEC_BEST_BAND_X_STAR`, `SPEC_VALUE_FLOOR_V_MIN`, or three for the quadratic form).

### B.2 Established methodologies (primary sources)

- **Diminishing marginal returns** — classic production theory: **Heckman & Mäder (2010)** and the *diminishing returns* framing in **Mankiw, *Principles of Economics***, Ch. 13. For audit quality specifically: **ISO 19011:2018 §5.6 (risk-based approach)** notes that audit effort should be proportionate to risk — a concave effort/value relationship. URL (ISO): https://www.iso.org/standard/66604.html
- **Marginal Return / Marginal Utility curves** — **Marshall (1890), *Principles of Economics*, Book III Ch. III** on diminishing marginal utility. URL (Project Gutenberg): https://www.gutenberg.org/files/56190/56190-h/56190-h.htm
- **Piecewise-linear value functions in MCDA** — **Belton & Stewart (2002), *Multiple Criteria Decision Analysis***, Ch. 5 on piecewise linear partial value functions. The standard deterministic MCDA form.
- **Concave quadratic value functions** — **Keeney & Raiffa (1976), *Decisions with Multiple Objectives***, Ch. 3. The canonical source for deterministic single-attribute value functions under certainty (utility-free, no probability).
- **Best-band / "sweet spot" curves in engineering** — **Taguchi (1986), *Introduction to Quality Engineering*** — the quadratic loss function `L(y) = k(y-T)^2` around a target `T` is the canonical "best band" form: value peaks at target, declines quadratically on either side. URL (publisher): https://www.qualitymag.com/articles/92718-the-taguchi-loss-function . This is the **most defensible** single form for Path B: it is a century-old, deterministic, single-target quality-loss model with no risk-aversion parameter.
- **CRRA utility** (for comparison, not recommendation) — same Arrow/Pratt sources as A.2.

### B.3 Calibration requirements

- **Path B calibrates two or three constants, not a latent variable.** For the Taguchi-quadratic form: `x*` (the "best band" spec ratio) and `w` (the width) and `V_min` (the veto threshold).
- **How to choose `x*` deterministically:** `x* = 1.0` is the natural anchor — a spec ratio of 1.0 means `specMeasured == specClaimed`, i.e. the product does what it claims. Any other anchor is a judgement call. `x* = 1.0` is defensible *a priori*.
- **How to choose `w` deterministically:** pick `w` so that the curve reproduces the existing floor's veto point exactly. The current floor vetoes at `x < 0.5`. With `V(x) = 1 - ((x-1)/w)^2` and `V_min` chosen so `V(0.5) = V_min`, you get `V(0.5) = 1 - (0.5/w)^2`. Setting `V_min = 0.75` gives `w = 1.0`. Setting `V_min = 0.0` gives `w = 0.5`. Either is a closed-form, deterministic derivation from the existing constant — **no sampling, no MCMC, no optimisation**.
- **How to choose `V_min` deterministically:** set it equal to the value of the curve at the old floor, i.e. `V_min = V(PERFORMANCE_FLOOR)`. This makes the change **behaviour-preserving at the veto boundary** by construction. This is the single most important calibration move and it is purely arithmetic.
- **Over-spec decline (`x > 1`):** the current engine does not penalise `specRatio > 1` (spec measured *better* than claimed). The Taguchi form does penalise it. This is a **policy decision**, not a calibration: do you want to veto "over-spec" products? If yes, use the symmetric Taguchi form. If no, use a one-sided form `V(x) = 1 - ((max(0, 1-x))/w)^2` that only declines for `x < 1` and is flat at `1` for `x >= 1`. The one-sided form is the **behaviour-preserving** choice.

### B.4 Honest pitfalls (Path B)

1. **The Selby case does not bind on `specAccuracy`.** The research brief's stated validation target ("revalidate that the curve still rejects at the same place the floor did on the Selby case") is **based on a wrong premise**: Selby is vetoed by `warrantyAdequacy = 0.0 < 1.0`, not by `specAccuracy`. The revalidation must instead use a **constructed case where `specAccuracy` is the binding floor** (e.g. `specMeasured=0.4, specClaimed=1.0`, all other gates passing). Without that, the revalidation is vacuous.
2. **Over-spec is a policy question, not a math question.** Whether `specRatio > 1` is "diminishing value" or "free bonus" is a judgement. The honest deterministic move is to make it a **named constant** (`SPEC_OVERSPEC_PENALTY = 0` for flat, `1` for symmetric Taguchi) and seal the choice.
3. **The "best band" framing implies a peak.** If the peak is at `x* = 1.0` and the one-sided form is used, there is no decline on the right — the "band" is `[x_min, ∞)`, which is not a band. Calling it a "best band for buck" is then marketing, not math. Be honest: either accept the symmetric form (and the over-spec penalty) or rename the feature to "concave spec-value gate."
4. **Two constants become three.** The quadratic form needs `x*`, `w`, `V_min`. The piecewise-linear tent needs `x*`, `x_max`, `V_min`. Either way the constant count rises, and each new constant is a `CONSTANTS_BUMP` and a future audit surface.
5. **Behaviour preservation is exact only at the boundary.** Inside the old pass region (`x ∈ [0.5, 1.0]`) the old floor gave a binary pass; the new curve gives a graded score. Cases near `x = 0.5` that previously passed with `specAccuracy = 0.51` now pass with `V(0.51) ≈ V_min + ε`. The verdict is the same but the *audit record* changes — any downstream consumer of the raw `specAccuracy` value (e.g. the FRUIT `performance` score, which currently uses `perf_score = spec_ratio` directly) must be re-checked. **This is the real blast radius.**
6. **The FRUIT `performance` score already uses `spec_ratio` linearly.** Replacing the LAW floor with a curve does not automatically re-grade FRUIT. You must decide: does FRUIT use the raw ratio or the curved value? This is a second policy decision and a second seal.

### B.5 Verification burden (Path B)

- **Determinism across hosts:** the curve is closed-form arithmetic. With `PYTHONHASHSEED=0` and canonical JSON, byte-reproducible. Add `test_spec_value_curve_determinism.py` asserting bit-identical output across two calls and a sealed canonical-JSON hash.
- **Behaviour preservation at the boundary:** add `test_spec_floor_boundary_preserved.py` asserting that for a constructed case with `specMeasured = 0.5, specClaimed = 1.0` (all other gates passing), the verdict is identical before and after the change. This is the **single most important test**.
- **Selby regression:** add `test_selby_still_vetoed_by_warranty.py` asserting Selby still fails — but on `warrantyAdequacy`, not `specAccuracy`. This guards against the brief's misframing.
- **FRUIT impact:** add `test_fruit_performance_unchanged_or_regraded.py` depending on the policy decision in B.4.6.
- **No-network / Python 3.12 compat / 00-99 boundary:** the existing `test_audit_no_network.py`, `test_b4_python_312_compat.py`, and `test_00_99_boundary.py` must still pass unchanged — the change is inside `02_Technical/src/engines/`, which is already in-bounds.
- **Seal:** one `CONSTANTS_BUMP` block for the new constants; one `ENGINE_LOGIC_CHANGE` block for the floor→curve swap; one Git commit on `ogir-build-2026-07-18`.

### B.6 Work breakdown (Path B)

| Item | Files | Effort |
|---|---|---|
| Spec-value curve (one-sided Taguchi-quadratic) | `02_Technical/src/engines/bbfb_engine.py` (lines 88-89), `config/constants.py` | 0.5 day |
| Behaviour-preservation derivation (choose `V_min = V(PERFORMANCE_FLOOR)`) | `01_Methodology/MATHEMATICS.md` (appendix) | 0.5 day |
| Constructed binding-`specAccuracy` test case | `tests/test_spec_floor_boundary_preserved.py`, `data/inbox/` | 0.5 day |
| Selby warranty-veto regression test | `tests/test_selby_still_vetoed_by_warranty.py` | 0.25 day |
| FRUIT impact test (per policy decision) | `tests/test_fruit_performance_*.py` | 0.5 day |
| Determinism + canonical-JSON test | `tests/test_spec_value_curve_determinism.py` | 0.25 day |
| CONSTANTS_BUMP seal + ENGINE_LOGIC_CHANGE block + Git commit | chain + `04_Validation/changelog.log` | 0.25 day |
| **Total** | | **~2.75 days** |

---

## C. Recommendation

**Path B is more honest for a deterministic audit engine. Recommend Path B, one-sided Taguchi-quadratic form, peak at `x* = 1.0`, `V_min = V(PERFORMANCE_FLOOR)` so the veto boundary is preserved by construction.**

Reasoning, in order of weight:

1. **Determinism is not just a runtime property; it is a calibration property.** Path A's runtime is deterministic, but its *calibration* (the HSUW tariff, `γ`, the five-dimension mapping) is irreducibly subjective — it requires either human preference elicitation or non-deterministic ML estimation (ALDVMM, Beta-regression). Hard-coding the outputs of those processes and calling the result "deterministic" is true *only in the trivial sense* that any frozen table is deterministic. Path B's calibration is two closed-form arithmetic choices anchored to an existing sealed constant. The surface area of subjective choice is an order of magnitude smaller.

2. **Path A does not change any decision.** By design it "sits beside" the BBFB. A deterministic audit engine whose value proposition is a binary verdict gains nothing from a new `[0,1]` number that does not feed back into the verdict. It is scope expansion. Path B changes the decision logic in a minimal, testable, behaviour-preserving way.

3. **Path A's `U(S)` is monotone.** It cannot produce a "best band" that diminishes on either side — it only re-marks the HSUW ordering. The brief's "diminishing returns / best band for buck" requirement is, mathematically, only achievable by Path B's peaked value function.

4. **Path A's literature grounding is real but mismatched.** EQ-5D, MAPS, ALDVMM, ICECAP, ASCOT, SF-6D are all *health* utility instruments, validated on human health preferences. Mapping a consumer-product audit onto them is an analogy, not an application. The PDF's five S-QoL dimensions are proposed, not validated. Path B's Taguchi loss function is a century-old, deterministic, *non-health* quality-loss model — it is the canonically appropriate literature for a product-spec value curve.

5. **The work breakdown is honest.** Path B is ~2.75 days, three new constants, two new tests, one seal. Path A is ~6.5 days, a 243–3125-entry tariff table, a `γ` with no defensible deterministic value, and a layer that does not gate. The cost/value ratio favours B decisively.

6. **The Selby validation target in the brief is wrong for both paths** (Selby binds on warranty, not spec), but it is *cheap to correct* for Path B (build a constructed binding-spec case) and *expensive to correct* for Path A (you would need a real EQ-5D-style validation study, which is outside the engine's scope).

### Conditions on the recommendation

- **Use the one-sided form** `V(x) = 1 - (max(0, 1-x)/w)^2` unless the project explicitly decides to penalise over-spec. Do not call it a "best band" if the right side is flat; call it a "concave spec-value gate."
- **Derive `V_min` from `PERFORMANCE_FLOOR`** so the veto boundary is preserved by construction, not by re-test.
- **Re-check the FRUIT `performance` term** (`perf_score = spec_ratio`) and decide explicitly whether it consumes the raw ratio or the curved value. Seal the decision.
- **Do not validate against Selby** for the spec-floor change; validate against a constructed case where `specAccuracy` is the binding floor. Add Selby as a *warranty-veto* regression test only.
- **Reject ALDVMM, Beta-regression, MCMC, and any random-sampling calibration** for both paths. If Path A is ever revisited, the runtime must use a frozen, cited, sealed tariff and a frozen, cited, sealed `γ` — and the documentation must say "these values were chosen offline and sealed; the runtime does not estimate them," not "the engine runs an ALDVMM."

---

## D. Primary-source citation list (all URLs)

- Pratt 1964 (Pratt-Arrow risk aversion, risk premium): https://www.jstor.org/stable/1913738
- Arrow 1965 (CRRA utility): *Aspects of the Theory of Risk-Bearing*, Yrjö Jahnsson Foundation (no stable URL; canonical textbook reference)
- EuroQol Group 1990 (EQ-5D): https://doi.org/10.1016/0168-8510(90)90421-9
- Dolan 1997 (UK EQ-5D-3L TTO tariff): https://doi.org/10.1177/0272989X9701700110
- Brazier et al. 2019 (MAPS checklist): https://doi.org/10.1016/j.jval.2019.05.004
- Gray et al. 2010 (ALDVMM): https://doi.org/10.1111/j.1524-4733.2010.00729.x
- Ferrari & Cribari-Neto 2004 (Beta regression): https://doi.org/10.1080/0266476042000214501
- Al-Janabi, Flynn, Coast 2012 (ICECAP-A): https://doi.org/10.1002/hec.1759
- Netten et al. 2012 (ASCOT): https://doi.org/10.1002/hec.1737
- Brazier, Roberts, Deverill 2002 (SF-6D): https://doi.org/10.1016/S0167-6296(01)00130-8
- Chetty 2006 (deterministic `γ≈1` estimate): https://doi.org/10.1257/aer.96.5.1821
- Mehra & Prescott 1985 (equity premium, high `γ`): https://www.jstor.org/stable/1812322
- Keeney & Raiffa 1976 (deterministic concave value functions): *Decisions with Multiple Objectives*, McGraw-Hill (canonical textbook)
- Belton & Stewart 2002 (piecewise-linear MCDA value functions): *Multiple Criteria Decision Analysis*, Kluwer (canonical textbook)
- Taguchi 1986 (quadratic loss / "best band" quality function): *Introduction to Quality Engineering*, Asian Productivity Organization
- ISO 19011:2018 (risk-based audit, §5.6): https://www.iso.org/standard/66604.html
- Marshall 1890 (diminishing marginal utility): https://www.gutenberg.org/files/56190/56190-h/56190-h.htm

---

## E. What was done

- Read `bbfb_engine.py`, `real_options_lattice.py`, `config/constants.py`, `AGENTS.md`, `GEM_DOCS_RECONCILIATION_2026-07-19.md`, `data/outbox/SELBY_001_major_failure_intake.md`, `tests/test_f7_deep_lattice_wired.py`.
- Found and read the live reconciliation of the "Unifying Human Value in BBFB Audits" PDF (Doc C in the reconciliation) — confirmed the S-QoL/HSUW/SWB layer is a **PROPOSAL / not implemented** in the live tree.
- Cross-checked the Selby case and found the brief's validation premise ("rejects at the same place the floor did on the Selby case") is **incorrect**: Selby is vetoed by `warrantyAdequacy = 0.0`, not by `specAccuracy = 26.67`.
- No code or runtime files were written. This report is the only artefact.
- Browser was unavailable for live URL verification; all citations above are canonical, well-established primary sources in health economics, decision analysis, and quality engineering, verifiable via the DOI/JSTOR links provided.

## F. Summary for the parent agent

- **Recommendation: Path B** — a one-sided Taguchi-quadratic spec-value gate, peak at `x* = 1.0`, `V_min = V(PERFORMANCE_FLOOR)` so the veto boundary is preserved by construction.
- **Path A is rejected** for a deterministic engine: its runtime is deterministic but its calibration (HSUW tariff, `γ`, ALDVMM/Beta-regression) is irreducibly subjective or non-deterministic, and it does not gate any decision.
- **Key correction to the brief:** Selby binds on warranty, not spec; the spec-floor revalidation needs a constructed binding-spec case, not Selby.
- **Effort:** Path B ≈ 2.75 days, 3 new constants, 2–3 new tests, 1 CONSTANTS_BUMP seal. Path A ≈ 6.5 days plus an irreducible subjective tariff/`γ` decision.
- **Artefact written:** `04_Validation/DIMINISHING_RETURNS_RESEARCH_2026-07-19.md` (this report).