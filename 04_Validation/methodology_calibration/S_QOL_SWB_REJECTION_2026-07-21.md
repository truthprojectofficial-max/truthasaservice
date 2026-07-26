# Why S-QoL / SWB / ALDVMM mapping was rejected for OGIR

## Source proposal

`files for inspiration and code/High-Assurance Sovereign Audit fix bbfb Arch.txt` proposes a non-invasive mapping harness that translates BBFB telemetry into five Systemic Quality of Life (S-QoL) dimensions, then into a Systemic Well-Being (SWB) utility via a risk-aversion curve, estimated with an Adjusted Limited Dependent Variable Mixture Model (ALDVMM) or Beta-regression mixture model under the MAPS reporting standard.

## Decision

**Rejected.** The S-QoL/SWB path is not implemented in Order Get It Right and will not be merged into the live engine.

## Reasons

1. **Subjective preference elicitation is required.**
   EQ-5D-style utility weights are derived from population preference studies (time-trade-off, standard gamble). There is no canonical population preference set for "systemic vitality" or "structural integrity." Any weights we invent would be arbitrary and non-reproducible across hosts, violating the determinism mandate.

2. **ALDVMM / Beta-regression are not in the Python standard library.**
   The project runs on a zero-dependency, pure Python stdlib runtime. Implementing a mixture model from scratch would be error-prone and unverifiable; importing `statsmodels`, `scipy`, or similar would break the air-gap / supply-chain contract.

3. **The mapping adds no gate.**
   BBFB already produces a deterministic verdict (GO / DEFER / TEST FIRST / REJECT) through LAW, GRACE, FRUIT, and the optionality lattice. Wrapping the same numbers in a 0-to-1 SWB score would be a second, redundant verdict layer with no decision authority.

4. **It conflicts with the chosen value curve.**
   On 2026-07-19 the project adopted the symmetric Taguchi-quadratic spec-value curve (F7-SPEC) as the live best-band-for-buck gate. That curve is deterministic, has a closed-form formula, and penalises both under- and over-specification symmetrically. S-QoL/SWB would introduce a competing, preference-laden value framework.

5. **Diminishing-returns framing is preserved without SWB.**
   The F7-SPEC curve already encodes the intuition that exceeding a spec is not a bonus and that deviations on either side reduce value. No separate risk-aversion coefficient or certainty-equivalent calculation is required.

## What was kept from the proposal

- The five domain labels (Systemic Vitality, Structural Integrity, Transactional Execution, Operational Morbidity, Systemic Vulnerability) are useful narrative anchors and may be used in reports, but they are **not** scored or weighted.
- The 90/10 Tau extraction ceiling, thermodynamic-sovereignty language, and spatial 00-99 hierarchy were already part of the live design before this proposal.

## Live alternative

The current engine uses:

- `PERFORMANCE_FLOOR` and `EFFICIENCY_FLOOR` as hard binary gates (LAW).
- `GRACE_QUADRATIC_COEFFICIENT` and `GRACE_CRITICAL_THRESHOLD` for compound-failure penalties.
- `FRUIT_WEIGHTS` for geometric utility across cost/performance/reliability/compliance.
- `SPEC_BEST_BAND_X_STAR`, `SPEC_VALUE_WIDTH_W`, `SPEC_VALUE_VETO_FLOOR` for the Taguchi-quadratic spec-value curve (F7-SPEC).
- `REAL_OPTIONS_*` constants for the deception-adjusted optionality index (F7-deep).

These are all hard-coded, named, and reproducible on any host.

## Conclusion

S-QoL/SWB is a clinically valid methodology for health economics, but it is the wrong tool for a deterministic legal-admissibility engine. The project records this rejection in the chain so the idea cannot be silently reintroduced later as a "missing feature."
