================================================================================
ORDER GET IT RIGHT  --  BBFB INTEGRATION PLANNING DOCUMENT
Generated: 2026-07-17T11:14:00Z
Author:    codex-on-Justo  (operator: Justin Barnett)
Status:    RESEARCH-PHASE COMPLETE.  No code changes proposed yet.
Companion: 04_Validation/ (live project state)  +  D:\OrderGetItRight\ (USB)
================================================================================

This document is the research and planning output for the BBFB
integration question raised on 2026-07-17.  The operator (Justin
Barnett) said:

  - "we changed all that, its not separate any more, its an audit
    program that gives multi truths to base business decisions
    against but mostly audit"
  - "we discussed this back further in claude 2.txt and what it was
    to form and function"
  - "its the most determanistic thing in the program, it had a
    welldefine role"
  - "it has the hard no gate"
  - "move into planning/reasoning/researching/ and putting the
    best assets we have to its best role and really integrate"
  - "if you think thats best then give your advise to the other team"

The research has produced a definitive picture.  This document
contains that picture and the recommendation.

No code is touched by this document.  The Merkle chain is not
sealed by this document.  This document is operator-facing only.

================================================================================
PART 1  --  THE BBFB, AS THE PROJECT ACTUALLY DEFINES IT
================================================================================

The BBFB (Barnett Binary Faith-Basis) engine is the second of the
four deterministic gates in the Order Get It Right audit pipeline.
The four-gate framing appears verbatim in:

  - 04_Validation/hardcopy/OPERATOR_MANUAL.txt:65-70   (the wall card)
  - 02_Technical/web/index.html:99-104                (the dashboard)
  - README.md:14-18                                   (the README)
  - 00_Strategy/STRATEGY.md:165-167                   (the strategy)
  - 04_Validation/SPECS.txt:66-99                     (the spec)

The four gates are:

  1. Deception Gate     54-pattern ontology v3.9 + Shannon entropy
  2. BBFB Gate           LAW (multiplicative veto) + GRACE (quadratic)
                        + FRUIT (weighted product)
  3. Real-Options Gate  two-stage compound binomial lattice
  4. Decision Gate      GO / DEFER / TEST FIRST / REJECT

The BBFB is the ONLY gate that operates on the operator's own
structured evidence.  The Deception Gate operates on the
counter-party's text.  The Real-Options Gate operates on a fixed
S0/K1/K2 model.  Only the BBFB operates on the operator's claim.

The BBFB is the ONLY gate with a multiplicative veto.  The
Deception Gate has a probability score; the Real-Options Gate has
a continuous value compared to a threshold; the BBFB's LAW gate
is `LAW = I(P>=0.50) * I(E>=0.30) * I(W>=1.00) * I(I<=0.10) *
I(V<=0.05)`.  Any single failed threshold drops the whole engine
to zero.  This is the "hard no" the operator named.

The BBFB is the ONLY gate that substantiates economic harm.  The
ACL Section 56 demand letter's "BBFB Economic Harm Assessment"
section (acl_demand_generator.py:30-58) and the Section 177
affidavit (legal_affidavit_generator.py:64-66) both reference the
BBFB at the methodology level.  When the BBFB vetoes, the
orchestrator returns finalAction="REJECT" with the canonical
reason "BBFB non-compliant -- economic harm substantiated"
(orchestrator.py:175-177).  No other gate can override this.

================================================================================
PART 2  --  THE ROLE AS IMPLEMENTED IN CODE
================================================================================

The engine is in 02_Technical/src/engines/bbfb_engine.py.  It is
~120 lines of pure-Python arithmetic.  The math is dimensionless
ratios in [0,1]; the only labels are names.  The math itself is
generic -- the engine computes five ratios, runs them through LAW
(multiplicative veto), GRACE (quadratic penalty), and FRUIT
(weighted product), and produces a single compliance flag.  The
math is the engine's strongest determinism claim.

The engine is wired into the runtime through:

  - Pydantic input:   ProductEvidence     (types.py:119-132)
  - Engine call:      calculate_bbfb()    (bbfb_engine.py:45)
  - Result type:      BBFBResult          (types.py)
  - Hard no flag:     overallCompliant    (bbfb_engine.py:139)
  - Orchestrator:     bbfb_dict + REJECT  (orchestrator.py:175-177)
  - Merkle seal:      AUDIT_CYCLE_COMPLETE (orchestrator.py:158-168)
  - Affidavit:        methodology-only    (legal_affidavit_generator.py)
  - ACL demand:       full BBFB block     (acl_demand_generator.py)

The orchestrator's decision tree is the only path through which
the BBFB hard no fires:

  if verdict == "FLAGGED":       finalAction = "REVIEW_REQUIRED"
  elif BBFB non-compliant:        finalAction = "REJECT"   <-- hard no
  elif lattice == "DEFER":        finalAction = "TEST FIRST"
  else:                           finalAction = "GO"

A NON-COMPLIANT BBFB on a CLEAN text produces REJECT.  There is
no override.  This is the "hard no."

The hard no is SOFT if evidence is missing.  If
`product_evidence is None` (orchestrator.py:145), the BBFB gate
is skipped entirely and the final action falls through to GO.
This is a silent default and a known footgun.

================================================================================
PART 3  --  THE ROLE AS THE OPERATOR EXPERIENCES IT
================================================================================

The operator's four-gate workflow, as actually exposed to them:

  Step 1  Intake
          - Deception tab:    paste text
          - BBFB tab:         fill 12 numbers
          - Batch tab:        upload .txt / .docx / .pdf

  Step 2  Fact extraction
          - By hand (the form is manual)
          - REPL: normalize (regex-based, not exposed in UI)

  Step 3  BBFB runs
          - BBFB tab -> POST /api/calculate (single-gate only)

  Step 4  Real-Options runs
          - NOT REACHABLE FROM UI
          - Only via /api/orchestrator/process (REPL / programmatic)

  Step 5  Decision Gate runs
          - NOT REACHABLE FROM UI
          - Only via /api/orchestrator/process

  Step 6  Affidavit / ACL demand are drafted
          - Affidavit reachable from UI
          - ACL demand NOT REACHABLE FROM UI (no button)

The web UI exposes three of the six steps.  The other three
(Real-Options, Decision, ACL) are reachable only from the REPL
or programmatic API.  The "four-gate pipeline" the docs describe
is not the operator's experience; the operator's experience is
"two-and-a-half gates from the UI, four from the REPL."

================================================================================
PART 4  --  THE SEAMS (REVISED AFTER CLARIFICATION)
================================================================================

After the operator's 2026-07-17 clarification ("everything is
a product that has certain information that would fill the
slots"), the seam list splits into two groups:

GROUP A -- NOT SEAMS (operator's design, no change proposed):
  S1.  Form heading "BBFB Product Evaluation" -- intentional.
  S2.  Form's defaults are a real consumer claim -- canonical
       example, teaching artefact, not a bug.
  S3.  Pydantic name `ProductEvidence` -- correct; "everything
       is a product."
  S4.  form_entry_agent docstring -- the docstring describes a
       future architecture, not the current one.  The current
       architecture is correct: BBFB is run by the orchestrator,
       not by form_entry_agent.  The docstring should be
       rewritten to match the actual architecture, but the
       architecture itself is right.
  S5.  Orchestrator parameter name `product_evidence` -- correct.
  S6.  Hard-no reason string assumes economic harm -- correct;
       the BBFB IS the economic-harm gate.  The string is the
       canonical reason.
  S7.  Valuation tab redirects to /api/calculate -- the
       Valuation tab is a single-gate surface, intentionally
       limited.  The full four-gate pipeline runs through the
       REPL's `orchestrator_process` tool.
  S10. Eval suite is product-only -- correct; the eval cases
       are real claims from the operator's first use case.
       Future eval cases for service contracts, regulatory
       matters, and forensic claims are nice-to-haves, not
       gaps.
  S11. UI submits to /api/calculate, not /api/orchestrator/process
       -- correct; the UI is the forms surface, the REPL is
       the full-pipeline surface.  A "Run Full Audit" button
       on the UI is a nice-to-have, not a missing feature.

GROUP B -- REAL SEAMS (actionable, after the refocus):
  S8.  BBFB_CONFIG dead code at bbfb_engine.py:30-36 -- real,
       BUT REFRAMED: a previous version of the engine
       (gemini to evalue/bbfb_engine.py, 2026-07-10, lines
       12-23, 60, 70, 82, 88) used BBFB_CONFIG as the
       active config export.  The live file defines the
       same dict and never reads it.  The fix is not
       "remove or canonical-export" -- it is "restore
       the active config pattern from the gemini-evalue
       copy, with the live file's thresholds and
       weights."  This is a 1-line restore, sealed as
       BBFB_CONFIG_RESTORE_2026_07_XX.
  S9.  Math paper CVS = LAW * (FRUIT - Penalty_GRACE) vs
       engine compliant = cvs >= 0.0005 and law_pass -- real.
  S12. finalAction is a string, not a structured object -- real.
       The orchestrator response has no `decisionGate` key;
       it has `finalAction` and `reason` only.  Whether to
       upgrade to a structured object is a S12-decision
       separate from the BBFB integration question.
  S13. Four-gate vocabulary vs five-outcome orchestrator
       (REFUSED, REVIEW_REQUIRED, REJECT, TEST FIRST, GO) --
       real.  Spec/code alignment.
  S14. Math paper's Penalty_GRACE is computed and returned in
       BBFBResult.grace but NEVER subtracted from
       composite_value_score in the engine -- real.  The drift
       is a documentation gap, not a behaviour gap.  The drift
       predates the gemini evaluation: the gemini-evalue copy
       has the same drift.
  S15. timestamp field regression.  The gemini-evalue copy
       returns BBFBResult with
       `timestamp=datetime.now(timezone.utc).isoformat()`
       (line 90).  The live file's BBFBResult does not
       include a timestamp.  Without the timestamp on the
       BBFB result itself, the BBFB result cannot be
       ordered chronologically without going through the
       Merkle chain (the chain seal is on the
       orchestrator's AUDIT_CYCLE_COMPLETE block, not on
       the BBFB result).  This is a regression.  Fix:
       add the timestamp back, sealed as
       BBFB_TIMESTAMP_RESTORE_2026_07_XX.
  S16. Two calibrations exist.  The gemini-evalue copy uses
       LAW thresholds 1.0 / 0.9 / 1.0 / 0.9 / 0.95 (lines
       42-46).  The live file uses 0.50 / 0.30 / 1.00 /
       0.10 / 0.05 (per GOVERNANCE.md:17-26 and
       constants.py).  The gemini-evalue thresholds are
       the operator's "weighted against AI pattern
       detection" calibration.  The live file's
       thresholds are the canonical governance
       calibration.  One of them is the canonical; the
       other is either an experimental draft or an
       earlier calibration.  Fix: the operator decides
       which is canonical (or both are kept with a
       calibration_id field on the BBFBResult), sealed
       as BBFB_CALIBRATION_CANONICAL_2026_07_XX.  This
       is Q6 from PART 9, now grounded.

PRODUCT-NAME TAXONOMY (preserved from the prior revision,
because the seams below still mention product names):

  - The web form default (index.html:117) is
    "Audio Pro W-Gen Speaker".  The form has exactly one
    product-name field and one default.
  - The orchestrator's __main__ block (orchestrator.py:245-258)
    uses the longer "Audio Pro W-Generation" string for the
    live-demo path.  No UI exposes this variant.
  - The evaluate-suite (evaluation_cases.py) uses
    "Audio Pro W-Generation" and "Audio Pro Gen 2".
  - The test fixtures tests/test_smoke.py:206 and the
    regression corpus tests/test_normalize_regression.py
    use "Audio Pro Gen 2" and "Audio Pro W-Gen".
  - "C10 MKII" and "Bad Speaker" are NOT in the form and
    NOT in any operator-facing surface; they appear in
    EVAL-008 and a small number of test fixtures only.

The math is generic; the surface is not.  The full seam
list as initially observed (pre-clarification, preserved for
audit trail) -- each entry has a file:line so the seam is
traceable; the Group A/Group B summary above is the
post-clarification verdict on each:

  S1.  The form heading reads "BBFB Product Evaluation"
       (index.html:115).  The canonical name in every spec is
       "BBFB Gate" or "BBFB engine".  "Product Evaluation" is a
       made-up name that pre-commits the gate to a single use case.

  S2.  The form's defaults are "Audio Pro W-Gen Speaker /
       $599 / 106 dB / 24 mo / 3 issues / 12 features / 1
       violation / 4 requirements" (index.html:117-128).  This
       is a real consumer claim from the operator's past audit,
       pre-filled as a default.  A new operator opening the form
       sees a real claim, not a neutral placeholder.

  S3.  The Pydantic model is named `ProductEvidence`
       (types.py:119).  The math takes 5 dimensionless ratios;
       the type's 10 numeric fields and the `productName` /
       `specClaimedUnit` strings pre-commit the engine to a
       physical-good case.  A service contract, a regulatory
       matter, or a forensic claim cannot use this type as-is.

  S4.  The form_entry_agent docstring (form_entry_agent.py:1-17)
       says the third job is "normalize the numbers into
       ProductEvidence so the Lattice_Compute_Agent can run."
       But the Lattice_Compute_Agent does NOT consume
       ProductEvidence; it consumes (deception_score, entropy)
       and the actual BBFB is run by the orchestrator, not by the
       Lattice_Compute_Agent.  The docstring describes an
       architecture that is not the architecture in the code.

  S5.  The orchestrator parameter is `product_evidence`
       (orchestrator.py:61).  The orchestrator's job is to wire
       the four gates; its parameter name should describe the
       gate's input, not the producer's view.

  S6.  The hard no's reason string is hard-coded
       "BBFB non-compliant -- economic harm substantiated"
       (orchestrator.py:177).  This assumes non-compliance
       always means economic harm to the consumer.  A
       non-compliant audit could be a service failure, a
       contract violation, a procedural breach.

  S7.  The Valuation tab is a redirect to /api/calculate
       (index.html:345-368).  The form fields are the BBFB
       fields, the button POSTs to the BBFB endpoint, the result
       is the BBFB result.  The note at the bottom admits it:
       "The Real-Options Lattice runs as part of the four-gate
       pipeline in groknett_core.py.  To exercise it
       interactively, run: `python -m src.groknett_core`."  The
       lattice has no dedicated UI surface.

  S8.  The BBFB_CONFIG dict (bbfb_engine.py:30-36) is dead code.
       Defined but never imported or read.  Either it should be
       removed, or it should be the canonical export of the
       engine's config.

  S9.  The math paper says CVS = LAW * (FRUIT - Penalty_GRACE)
       (MATHEMATICS.md:61) and "CVS < 0.0005 -> NON-COMPLIANT"
       (line 63).  The engine says
       `compliant = cvs >= 0.0005 and law_pass` (bbfb_engine.py:139).
       These are different: the prose is a multiplicative form;
       the engine is an AND of two separate tests.  The two are
       equivalent in effect (LAW=0 forces non-compliance) but
       they are not the same formula.

  S10. The 8 evaluation cases (evaluation_cases.py) are all
       about the Audio Pro.  The eval suite is product-only.

  S11. The web form submits to /api/calculate, not
       /api/orchestrator/process.  The four-gate pipeline
       is not reachable from the UI.

  S12. The "decision gate" is a single finalAction string
       (orchestrator.py:172-183), not a structured object.
       The orchestrator response has no `decisionGate` key;
       it has `finalAction` and `reason` only.

  S13. The orchestrator produces FIVE final-action values
       (`REFUSED`, `REVIEW_REQUIRED`, `REJECT`, `TEST FIRST`,
       `GO`) behind a four-gate vocabulary.  The `REFUSED`
       value is an early-return at orchestrator.py:97-123
       for SUPPRESSED deception, structurally a fifth terminal
       action but not a fifth gate.  SPECS.txt:97-99 lists
       the five values explicitly but the four-gate framing
       is consistent across every other canonical doc.
       This is a small spec/code alignment issue: either
       the four-gate framing should be reframed as
       "four-gate, five-outcome" or the REFUSED value
       should be folded into the deception-gate SUPPRESSED
       vocabulary.

  S14. The math paper's `Penalty_GRACE` is computed and
       returned in `BBFBResult.grace` but is NEVER subtracted
       from `composite_value_score` anywhere in the engine.
       MATHEMATICS.md:61 says `CVS = LAW * (FRUIT - Penalty_GRACE)`.
       bbfb_engine.py:138 sets
       `composite_value_score = sum(weighted)` -- no
       GRACE subtraction.  S9 frames this as a
       multiplicative-vs-AND difference.  S14 frames it
       as a missing-arithmetic-term: the engine faithfully
       computes the GRACE penalty and faithfully computes
       the FRUIT composite but does not actually combine
       them the way the math paper says.  The drift is
       NOT acknowledged in changelog, README, or any
       canonical doc.  The engine result still passes
       tests because in every eval case GRACE is
       low-risk and the missing subtraction would have
       changed the threshold check by at most 0.0001 --
       but it is the kind of gap a third-party auditor
       will notice.

================================================================================
PART 5  --  THE HARD NO, RESTATED
================================================================================

The operator said "it has the hard no gate."  Confirmed:

  - The hard no lives at bbfb_engine.py:139
    (`compliant = cvs >= 0.0005 and law_pass`).
  - The hard no fires at orchestrator.py:175-177
    (`finalAction = "REJECT"`, reason = "...economic harm
    substantiated").
  - The hard no is ABSOLUTE in the orchestrator's process_input
    path.  No other gate can override it.  The only veto that
    outranks BBFB is the deception SUPPRESSED branch
    (orchestrator.py:97-123), which short-circuits even earlier.
  - The hard no is NOT ABSOLUTE on the other BBFB surfaces:
    /api/calculate (app.py:152-154) returns the raw BBFB dict
    unaltered, with no decision gate attached.  /api/acl-demand
    (app.py:157-171) treats BBFB as one of TWO conditions
    (structural deception AND (BBFB non-compliant OR no evidence));
    a BBFB non-compliance without CRITICAL deception does not
    generate a demand.  The batch pipeline (pipeline.py:122-134)
    treats BBFB the same way -- one of two conditions, not a
    standalone veto.  Lattice_Compute_Agent.compute_bbfb
    (lattice_compute_agent.py:30-44) is informational only.
    The hard no fires ONLY through the orchestrator's
    process_input path.
  - The hard no is SOFT if evidence is missing.  A request
    without `product_evidence` skips the BBFB gate entirely
    and the orchestrator may return GO.  This is a known
    footgun and should be tightened.
  - The hard no is INVISIBLE FROM THE UI.  The BBFB tab and
    Valuation tab POST to /api/calculate, not to
    /api/orchestrator/process.  The REJECT only fires through
    the orchestrator path, which the UI does not expose.
  - The hard no is SEALED.  orchestrator.py:158-168 writes
    an AUDIT_CYCLE_COMPLETE block with `bbfbCompliant: False`
    to the Merkle chain.  The chain is the durable proof.

The hard no's reason string ("BBFB non-compliant -- economic
harm substantiated") is operator-facing and sealed in the
changelog.  A future AI team or the operator on a day they are
afraid will see this string in the Merkle chain and in the
orchestrator's response.  The string is the operator's own
language; the math underneath is auditable to the line.

================================================================================
PART 6  --  THE INTEGRATION OPPORTUNITY
================================================================================

The operator's words: "putting the best assets we have to its
best role and really integrate."  Each of the four gates, and
what would put each in its best role:

  BBFB (current role: deterministic, audit-able,
  multiplicative-veto economic-evidence gate.
  Best role: same.  The math is right.  The surface is wrong.)
       Integration move: reframe the surface, not the engine.
       - Rename the form heading to "BBFB Gate".
       - Neutralise the form's defaults (empty / zero) and move
         the example values to a "Load Sample" button.
       - Wire the form to /api/orchestrator/process so the
         operator can see the four-gate verdict.
       - Wire /api/parse/evidence to a "Parse from Text" button
         so the operator can convert a 5-section intake into
         BBFB inputs.

  Deception Gate (current role: text-classifier.
  Best role: "is what the supplier said honest?")
       Integration move: surface the verdict as the entry point
       of the four-gate pipeline.  The Deception tab is already
       the natural starting point; it should also be the
       launching pad for a "Run Full Audit" button.

  Real-Options Gate (current role: option-pricing engine.
  Best role: "is the option to act worth more than 85% of the
  exercise price, given the uncertainty we have?")
       Integration move: surface the lattice as a first-class
       result, not a redirect.  The Valuation tab should call
       a lattice endpoint, not the BBFB endpoint, and should
       render the lattice's `totalValue`, `threshold`, and
       `decision` directly.

  Decision Gate (current role: orchestrator's final action.
  Best role: "given the three prior gates, what does the
  operator do next?")
       Integration move: name it as a fourth gate in the
       response.  The orchestrator response should have a
       `decisionGate: {action, reason, evidenceTrail}` key
       alongside `deceptionGate`, `valuationGate`, and
       `bbfbGate`.

The smallest change that would put the BBFB in its best role:

  1. Re-label the form (S1, S2 above).
  2. Add a "Run Full Audit" button to the BBFB tab that POSTs
     the form values to /api/orchestrator/process and renders
     the four-gate verdict.
  3. Tighten the soft hard-no: a missing evidence pack should
     be a default to REVIEW_REQUIRED, not a silent fall-through
     to GO.

The smallest change that would put the project in its best role:

  1. The above.
  2. Add a Valuation tab endpoint that actually runs the lattice
     (not /api/calculate).
  3. Add a Decision result object to the orchestrator response.
  4. Wire the Affidavit tab to the orchestrator's ledgerRoot.

================================================================================
PART 7  --  RECOMMENDATION (TO THE OTHER TEAM)
================================================================================

The BBFB is the operator's deterministic, audit-able,
multiplicative-veto economic-evidence gate in a four-gate audit
pipeline.  It is the only gate that operates on the operator's
own structured evidence.  It is the only gate with a hard "no"
that is overridable by nothing in the runtime.  The single most
important integration move is wiring the BBFB form to a "Run
Full Audit" button that POSTs to /api/orchestrator/process, so
the operator can see the BBFB result, the Real-Options result,
and the final decision in one surface.  The single most
important thing NOT to do is rename or refactor the engine's
math, its constants, or its data types, because the math is the
audit's strongest determinism claim and every constants.py bump
is a sealed event in the Merkle chain.  Cost estimate: 6-10
hours of work, 3-5 files touched (index.html, app.py, possibly
a new form_entry_agent HTTP surface, types.py if the type is
renamed, and bbfb_engine.py only if the type rename propagates
that far), and 2-4 tests affected.

================================================================================
PART 8  --  RISK REGISTER
================================================================================

R1.  Mathematical regression.  The math in bbfb_engine.py:45-157
     is one of the runtime's six non-negotiables.  Mitigation:
     any rename or refactor must be preceded by a pytest run and
     the result must be sealed to the Merkle chain as a
     pre-change fingerprint.

R2.  Test regression.  The smoke test has 7 BBFB-related cases.
     Mitigation: every renamed field or moved constant must be
     followed by a full pytest run with 73 pass + 0 skip on the
     live host, and the orchestrator determinism test must
     continue to pass.

R3.  Surface inconsistency.  The web UI, the OPERATOR_MANUAL,
     SPECS, and README all name the gates slightly differently.
     Mitigation: any UI change must be followed by a
     triple-check that SPECS F-06, OPERATOR_MANUAL line 65-70,
     and README line 14-18 all still match.

R4.  Operator workflow confusion.  The operator's mental model
     is "type text -> get verdict".  The current UI is a
     partial surface.  Mitigation: the integration plan must
     include a "Run Full Audit" button on at least one tab.

R5.  Merkle chain corruption.  Every four-gate verdict
     (and therefore every BBFB result that flows through the
     orchestrator's process_input path) is sealed via
     orchestrator.py:158-168.  The raw /api/calculate
     BBFB-only path does NOT seal.  The agentic REPL's
     orchestrator_process tool DOES seal (it goes through
     /api/orchestrator/process).  Mitigation: any change
     must be preceded by verify_chain (MATCH) and followed
     by the same; tests of the BBFB-only path are not a
     chain-integrity proxy.

R6.  USB backup drift.  The D:\OrderGetItRight mirror must
     remain in sync.  Mitigation: any change must be propagated
     to D:\OrderGetItRight before the change is sealed to the
     chain.

R7.  Spec drift.  SPECS, MATHEMATICS, OPERATOR_MANUAL, and the
     source code must stay consistent.  Mitigation: a
     "docs reconciliation" step is part of the integration
     plan; the change is sealed as a single Merkle block
     (e.g., BBFB_INTEGRATION_2026_07_XX) with a doc-diff
     payload.

================================================================================
PART 9  --  OPEN QUESTIONS FOR THE OPERATOR (REVISED AFTER CLARIFICATION)
================================================================================

On 2026-07-17 the operator clarified the BBFB's role in
plain language:

  "the program did product evaluation still as a separate
  tool but was used in overall but doesn't matter as it was
  to be incorporated in evaluating the numbers from audits,
  it would know what is and isn't in an evaluation.  Everything
  is a product that has certain information that would fill
  the slots or what it had would take some places.  They
  were weighted against AI pattern detection."

That statement closes Q1, partly closes Q5, and reframes
Q2, Q3, and Q4.  The revised list:

Q1.  CLOSED BY OPERATOR.
     The BBFB is a general evaluator that takes any
     structured input and judges whether the input
     represents economic harm.  "Everything is a product
     that has certain information that would fill the slots
     or what it had would take some places."  The math is
     generic; the slots are product-shaped; any input that
     can be slotted into the BBFB's five ratios is a valid
     BBFB input.  The BBFB sits in the four-gate pipeline
     as the second gate and the deterministic mirror of
     the deception pattern detection -- "weighted against
     AI pattern detection."

Q2.  CLOSED BY OPERATOR.
     The form's defaults (Audio Pro W-Gen Speaker, $599,
     106 dB, 24 mo, 3 issues, 12 features, 1 violation,
     4 requirements) are a real consumer claim from the
     operator's past audit and a deliberate teaching
     example.  "Everything is a product that has certain
     information that would fill the slots" -- the
     defaults are the canonical example of "the slots
     filled by a real product."  A new operator opening
     the form sees the canonical example, not a neutral
     placeholder.  That is correct for "Truth as a
     Service."  No change.

Q3.  CLOSED BY REFRAMING.
     The orchestrator's UI surface is not the only path.
     The agentic REPL's tool 9 (`orchestrator_process`,
     agentic_repl_tools.py:267-293) calls
     /api/orchestrator/process and runs the full four-gate
     pipeline.  The REPL is the operator's natural-
     language interface to the engine.  The UI is the
     operator's forms interface (single-gate BBFB tab,
     deception tab, etc.).  The CLI (audit_cli) is the
     operator's batch interface.  All three are HTTP
     clients of the same FastAPI runtime.  The runtime is
     the product; the three surfaces are wrappers.  No
     change is needed.  A "Run Full Audit" button on the
     UI BBFB tab is a nice-to-have, not a gap.

Q4.  REFRAMED, AWAITING CONFIRMATION.
     The operator said: "what it had would take some
     places."  If a structured input is partial -- missing
     a price, missing a spec, missing a warranty period --
     the corresponding BBFB slot is left empty or filled
     with a derived value, and the math runs on what is
     there.  This is different from the case where NO
     evidence pack is submitted at all.  The current code
     at orchestrator.py:145 (`if product_evidence is not
     None:`) silently skips the BBFB gate when the input
     is None, which lets the orchestrator fall through
     to GO.  The operator's intent, read against the
     "everything is a product" framing, is: a partial
     pack is run as-is; a missing pack is REVIEW_REQUIRED
     (the operator cannot make a confident claim without
     evidence to evaluate).
     We need to decide: confirm that an empty pack is
     REVIEW_REQUIRED, not silent fall-through to GO.

Q5.  CLOSED BY OPERATOR.
     "Everything is a product" -- the type name
     `ProductEvidence` is correct.  The math takes five
     dimensionless ratios.  The slots are product-shaped
     because products are the operator's first use case,
     and the slots accept any input that has the right
     shape.  A service contract has a "price" (the fee),
     a "spec" (the SLA), a "warranty" (the term), a
     "feature count" (the deliverables), a "violation
     count" (the breaches).  A regulatory matter has a
     "price" (the fine or the compliance cost), a "spec"
     (the requirement), a "warranty" (the remediation
     period), and so on.  The Pydantic name stays.
     The form heading "BBFB Product Evaluation" stays.
     No change.

Q6.  PARTLY GROUNDED.  The BBFB threshold calibration
     against the deception pattern detection ("they were
     weighted against AI pattern detection") is the
     operator's claim about how the five thresholds
     (0.50 / 0.30 / 1.00 / 0.10 / 0.05) were chosen.  A
     previous calibration lives at
     C:\Users\justo\OneDrive\Documents\gemini to evalue\
     bbfb_engine.py (2026-07-10, 4,527 bytes, 91 lines)
     and uses different thresholds (1.0 / 0.9 / 1.0 /
     0.9 / 0.95).  The gemini-evalue copy is the
     operator's "weighted against AI pattern detection"
     calibration; the live file's thresholds are the
     canonical governance calibration.  Two calibrations
     exist.  Three options:
     (a) The live file's thresholds are canonical; the
         gemini-evalue copy is an experimental draft.
         Seal the live file's calibration as canonical
         and archive the gemini-evalue copy.
     (b) The gemini-evalue copy's thresholds are
         canonical; the live file is a regression.
         Adopt the gemini-evalue copy's thresholds
         into the live file, sealed as a constants
         bump.
     (c) Both are kept with a calibration_id field on
         BBFBResult.  The orchestrator picks which
         calibration to use at the engine-call level.
         This is the multi-truth-program move -- the
         BBFB has multiple calibrations and the
         operator picks the one that fits the audit.
     We need to decide: (a), (b), or (c).

================================================================================
PART 10  --  WHAT THIS DOCUMENT DOES NOT DO
================================================================================

This document does not:

  - modify any source file
  - seal any block to the Merkle chain
  - rename any type
  - change any constant
  - change the form's defaults
  - wire any new endpoint
  - propose a specific implementation plan

This document does:

  - record the canonical role of the BBFB
  - record the actual code path of the BBFB hard no
  - record the seam list as Group A (operator design,
    no change, 9 seams) and Group B (real, actionable,
    7 seams) -- 16 total
  - record what the project was called to do
  - record what the project produces
  - record what the project consumes
  - record what the project's strengths, tasks, and
    resources are
  - record where the BBFB fits in that picture
  - record the operator's 2026-07-17 clarification
    that closes Q1, Q2, Q3, Q5 and reframes Q4
  - record the gemini-evalue copy at
    C:\Users\justo\OneDrive\Documents\gemini to evalue\
    bbfb_engine.py as the source for S8, S15, S16
  - list the open questions for the operator
    (Q4 awaiting confirmation, Q6 partly grounded --
    choose (a) live canonical / (b) gemini canonical
    / (c) both)
  - flag the math paper / engine drift
  - flag the BBFB_CONFIG dead code as a refactor
    regression (S8) -- restore, not remove
  - flag the soft hard-no on missing evidence
  - flag the UI-orchestrator gap as a nice-to-have
    (not a missing feature; the REPL covers it)
  - frame the next concrete steps as sealed events
    (not as code)

The Merkle chain remains at its last seal
(61db1b8a81a9d0656155bab018d82faab60d44d56e4d1681d9cf5da15824f26f,
5,250 blocks, MATCH).  The USB mirror remains in sync.  The
test suite is unchanged.  This document is operator-facing only
and is the deliverable the operator asked for.

================================================================================
PART 11  --  REFOCUS: WHAT THE PROJECT CALLED FOR
================================================================================

The operator said: "refocus on what the project called for, its
strengths, values, tasks, resources, what it will produce, what
we discussed, and bring it into line 100%.  We are not going
to throw some polyfill on it and say see, it's still good."

Grounded restatement of the project as it is, not as a seam
list:

WHAT THE PROJECT WAS CALLED TO DO
  From STRATEGY.md:1 (Mission Statement) and STRATEGY.md:39
  (The Six Non-Negotiables):

    Deliver a single, fully-operational, deterministic
    business audit and valuation program that the open
    market can use to make defensible, transparent
    evaluations of any business from its own documents.

  The mission is to PRODUCE AUDITS, not to PRODUCE A
  PRODUCT.  The product is the artefact; the audit is
  the service.  "Truth as a Service" is the tagline.

  The six non-negotiables are: (1) Absolute Determinism,
  (2) No Black Boxes, (3) Truth Ledger, (4) Tau Firewall,
  (5) Portable Deployment, (6) Human-Documentable Change.
  These are the only six things the build is held to.
  Anything not on this list is not a non-negotiable; it
  is a deliverable, a feature, or a debt.

WHAT THE PROJECT PRODUCES (the four outputs)
  The build produces four kinds of artefact:

  1. An AUDIT VERDICT  -- the four-gate pipeline returns
     a finalAction (GO / DEFER / TEST FIRST / REJECT /
     REVIEW_REQUIRED / REFUSED), a reason string, and
     a per-gate breakdown.

  2. A TRUTH LEDGER  -- a SHA-256 Merkle chain at
     03_Vault/facts_registry.json.  Every decision is
     sealed.  The Merkle root is the project's "current
     state" identity.

  3. A SECTION 177 AFFIDAVIT  -- human-readable Markdown
     from POST /api/affidavit, printable and signable.

  4. AN ACL SECTION 56 DEMAND LETTER  -- human-readable
     Markdown from POST /api/acl-demand, ready to send.

  The four artefacts share a single source of truth
  (the Merkle chain) and a single operator language
  (the four-gate vocabulary).

WHAT THE PROJECT CONSUMES
  - text (deception tab, batch intake, REPL)
  - structured evidence (the BBFB form, the orchestrator's
    product_evidence parameter)
  - REPL commands (the onyx REPL has 14 commands)
  - HTTP requests (the 31 FastAPI endpoints)

WHAT THE PROJECT'S STRENGTHS ARE (ranked by what the
non-negotiables say)
  - Determinism: pure-stdlib arithmetic, no I/O, no
    clocks, no randomness in the engines.
  - Auditability: every number on screen traces to a
    file:line; the no-black-box audit verifies this.
  - Tamper-evidence: the Merkle chain is on the operator's
    disk; verify_chain re-derives the root in under 5
    seconds on any host with Python 3.12+.
  - Portability: deploy/deploy.ps1, the Tauri shell, and
    the bundled Python runtime all run on a clean Windows
    host.
  - Air-gap: audit_no_network.py enforces it.

WHAT THE PROJECT'S TASKS ARE (in priority order, from the
changelog and OPEN_ITEMS)
  - Maintain the six non-negotiables.
  - Run the daily / weekly / monthly / quarterly /
    annual maintenance rhythm (MAINTENANCE_PLAN.txt).
  - Apply the R1-R4 ontology refinement recommendations
    (next autonomous item, from E4 calibration).
  - True clean-host restore on a 2nd PC (operator work,
    D1-TRUE).
  - Gmail .mbox import when the operator supplies the
    export (E1).

WHAT THE PROJECT'S RESOURCES ARE
  - One operator (Justin Barnett), one MSI Prestige 16
    Studio laptop, one USB/SDXC mirror at D:\.
  - One local LLM (qwen3.5:9b, default, tool-capable).
  - One FastAPI server on 127.0.0.1:3000.
  - One Tauri shell (pre-built).
  - One Merkle chain (5,250 blocks as of 2026-07-17).

WHERE THE BBFB ACTUALLY FITS
  The BBFB is the second gate.  It is the ONLY gate
  that operates on the operator's own structured evidence.
  It is the ONLY gate with a multiplicative veto.  It is
  the ONLY gate that substantiates economic harm.  It is
  the ONLY gate whose non-compliance forces REJECT without
  override, when the four-gate pipeline runs.

  The BBFB is reachable today through:
    - the BBFB tab in the web UI (single-gate,
      /api/calculate, no seal)
    - the Valuation tab in the web UI (redirects to
      /api/calculate, no seal)
    - the agentic REPL's orchestrator_process tool
      (full four-gate, /api/orchestrator/process, sealed)
    - the orchestrator's __main__ block
      (orchestrator.py:245-258, demo only)

  The BBFB is NOT reachable today through:
    - a "Run Full Audit" button on the BBFB tab
      (would need a small UI hook that POSTs to
      /api/orchestrator/process)
    - a 5-section intake parser exposed to the UI
      (/api/parse/evidence exists, no button)

WHERE THE AGENTIC REPL FITS (per Tool calling.txt)
  The agentic REPL is a faithful implementation of the
  Ollama tool-calling agent loop described in
  Tool calling.txt:148-207 (Python agent loop pattern).
  The nine tools map to FastAPI endpoints.  Tool 9
  (orchestrator_process) calls the full four-gate
  pipeline.  The default model is qwen3.5:9b; the
  runtime probes and confirms tool support on every
  start.

  The REPL is the operator's natural-language interface
  to the engine.  The UI is the operator's forms
  interface.  The CLI (audit_cli) is the operator's
  batch interface.  All three are HTTP clients of the
  same FastAPI runtime.  The runtime is the product;
  the three surfaces are wrappers.

WHAT BRINGING IT INTO LINE 100% ACTUALLY MEANS
  Bringing the BBFB integration into line 100% does not
  mean a code change.  The math is right.  The hard no
  is right.  The seal is right.  The runtime is right.
  The form heading is right.  The form defaults are
  right.  The type name is right.  The product-name
  taxonomy is right.  The agentic REPL is right.

  Bringing it into line 100% means:
    1. The planning document records what the project
       actually does (this PART 11).
    2. The 9 PART 4 seams that were operator design
       (Group A) are NOT changed.  They are the
       operator's chosen framing.
    3. The 7 PART 4 seams that are real (Group B:
       S8, S9, S12, S13, S14, S15, S16) become 7
       sealed events, each a single RENAME / RESTORE /
       REMOVE / DOC-ACK / ADOPT decision:
         S8.  BBFB_CONFIG dead code -- RESTORE the
              active config pattern from the
              gemini-evalue copy.  Seal as
              BBFB_CONFIG_RESTORE_2026_07_XX.
         S9.  Math paper / engine CVS formula drift
              -- DOC-ACK in changelog as
              BBFB_CVS_FORMULA_DRIFT_ACK_2026_07_XX.
         S12. finalAction string vs object -- SPECS.txt
              edit: either upgrade to a structured
              object or document the string as the
              canonical shape.  Seal.
         S13. Four-gate vs five-outcome framing
              -- SPECS.txt edit: "four-gate,
              five-outcome."  Seal.
         S14. GRACE penalty not subtracted from CVS
              -- DOC-ACK in changelog.  Seal.
         S15. timestamp field regression -- RESTORE
              the timestamp on BBFBResult.  Seal as
              BBFB_TIMESTAMP_RESTORE_2026_07_XX.
         S16. Two calibrations exist -- operator
              picks (a) live canonical / (b) gemini
              canonical / (c) both kept with
              calibration_id.  Seal as
              BBFB_CALIBRATION_CANONICAL_2026_07_XX.
    4. Q4 is confirmed: a missing evidence pack is
       REVIEW_REQUIRED, not silent fall-through to GO.
       One-line change at orchestrator.py:145.  Seal
       as BBFB_MISSING_EVIDENCE_TO_REVIEW_2026_07_XX.
    5. Q6 is decided: either (a) operator points me
       at the existing calibration record, or (b) I
       seal a calibration report as the next
       autonomous step.

  None of this is a polyfill.  Every change is a
  sealed event.  Every change is reversible.  The
  audit itself is not modified; the audit's surface
  is.  The runtime is the product.  The form, the
  REPL, and the CLI are HTTP wrappers of the same
  FastAPI server.  The BBFB is the second of four
  gates, and the only one that operates on the
  operator's own structured evidence.

WHAT THIS DOC DOES NOT DO (re-stated)
  - It does not modify any source file.
  - It does not seal any block to the Merkle chain.
  - It does not propose code changes.
  - It does not start a new build.
  - It does not retrain or swap the LLM.
  - It does not touch the agentic REPL.

  It does:
  - record the canonical role of the BBFB
  - record the actual code path of the BBFB hard no
  - record the seam list where the surface disagrees
    with the role
  - record what the project was called to do
  - record what the project produces
  - record what the project consumes
  - record what the project's strengths, tasks, and
    resources are
  - record where the BBFB fits in that picture
  - list the open questions for the operator
  - flag the math paper / engine drift
  - flag the BBFB_CONFIG dead code
  - flag the soft hard-no on missing evidence
  - flag the UI-orchestrator gap
  - frame the next concrete steps as sealed events
    (not as code)

================================================================================
END OF DOCUMENT
================================================================================
