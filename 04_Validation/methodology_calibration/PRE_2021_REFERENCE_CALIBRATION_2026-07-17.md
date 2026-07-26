================================================================================
ORDER GET IT RIGHT  --  TRUTH AS A SERVICE
E4 PRE-2021 REFERENCE CORPUS CALIBRATION REPORT
Generated: 2026-07-17T10:48:00Z
Author:    codex-on-Justo  (operator: Justin Barnett)
Audit ID:  E4-PRE-2021-REF
================================================================================

This report documents the calibration run against a known-truthful
pre-2021 source. The reference material is the 41,316-char editorial
text at data/samples/verified_prior_2021.txt, generated 2026-07-12
from the operator's source DOCX (Verified.docx). The text is an
academic-style survey of information-verification, peer review,
archival methods, and trust institutions in the era preceding 2021.

A CLEAN or near-CLEAN verdict on this material is the expected
result. Any pattern that fires is either:

  (a) a TRUE POSITIVE -- the source contains deceptive language; OR
  (b) a FALSE POSITIVE -- the ontology matches a common English
      connective that is innocent in editorial register.

The job of this report is to classify each match and recommend
ontology adjustments if any false-positive rate is unacceptably
high.

================================================================================
PART 1  --  THE VERDICT
================================================================================

The intake file
04_Validation/pre_2021_reference_audit_intake.txt was submitted to
audit_cli via:

  python -m src.audit_cli ^
      --inbox ..\04_Validation\pre_2021_intake ^
      --outbox ..\data\outbox ^
      --formats md

Verdict: PASS WITH FALSE-POSITIVE FLAGS (5/54 patterns, all single-
indicator matches on common English connectives; all CALIBRATION
ITEMS, not deception signals).

  Extracted characters:  44,041
  Shannon entropy:       4.429 bits/char  (anomaly: no; threshold 4.5)
  Deception probability: 53.2%  (high enough to warrant pattern
                                  review, but the high score is
                                  driven by 5 single-word lexical
                                  matches, not by structural
                                  deception)
  Structural flag:       FALSE
  Patterns fired:        5 / 54

The 5 fired patterns are listed in PART 2.

================================================================================
PART 2  --  PATTERN-BY-PATTERN CALIBRATION
================================================================================

For each fired pattern, this report shows the indicator matched, the
line number and surrounding context in the source, and a calibration
verdict.

--------------------------------------------------------------------------------

DD-001  Facade of Competence  (HIGH, 85%)
Indicator:  clearly
Source:     line 129
Context:    "adhere to standardized publication practices. this
            included clearly articulating the aim and scope of the
            journal, educating editorial board members on the
            principle of independent peer review, and implementing
            a system to protect against conflicts of interest."

Calibration:  FALSE POSITIVE.
"clearly" is used here in the sense of "in a clear, unambiguous
manner" -- the opposite of facade. The sentence is describing the
real, concrete practice of articulating the journal's aim. The
underlying text is a transparent description of how journals worked
pre-2021. The pattern's indicator list includes "clearly" as a
facade marker (e.g. "clearly, the answer is ..." used to project
false authority) but the lexical match alone does not distinguish
the deceptive use from the descriptive use.

Recommendation:  NO ontology change yet. A future heuristic
refinement could scope "clearly" facade matches to a
"sentence-initial or clause-initial claim position with no
supporting evidence" -- a structural test, not a lexical one. The
cost of this refinement is a second pass over the source. The
benefit is reducing false-positive rate on academic text. Defer to
the next ontology bump.

--------------------------------------------------------------------------------

DD-006  Programmed Intent Ambiguity  (MEDIUM, 85%)
Indicators:  could, to clarify
Source:      lines 47, 89, 145, 201, 215, 279 (x2), 299
Contexts (paraphrased):
  L47  "readers could use to check reality in an age of contested
       facts" -- describing the social function of a public source
  L89  "every claim could be traced back to its verified genuine
       source" -- describing a method's capability
  L145 "study design that could lead to biased results" -- describing
       a risk
  L201 "digital tools that could provide the context required to
       verify search results, images, and videos" -- describing
       function
  L215 "by extracting keyframes, researchers could perform reverse
       image searches" -- describing a workflow
  L279 "terms like 'power' which could mean political power or
       influence" -- describing linguistic ambiguity
  L279 "to clarify implicit interpretations" -- method description
  L299 "researchers could navigate the digital landscape" --
       describing agency

Calibration:  FALSE POSITIVE (all 8 matches).
"could" is a modal of capability, used throughout the source to
describe what a method, a tool, or an institution is capable of.
This is descriptive, not programmed. The pattern is intended to
catch language that artificially creates multiple possible
interpretations to deflect accountability (e.g. "you could read
this as a promise or as a forecast"). The source uses "could" in
exactly the opposite sense: to specify capabilities, not to
obscure them.

Recommendation:  NO ontology change. The pattern correctly
identifies "could" as a hedge marker, but a hedge is only a
programmed ambiguity when its host is an obligation or a
commitment. Restrict the pattern to obligation contexts. Defer to
the next ontology bump.

--------------------------------------------------------------------------------

DD-011  Goalpost Shifting  (HIGH, 88%)
Indicator:  actually
Source:     line 215
Context:    "appeared online, often revealing that 'current' footage
            was actually from an unrelated event years prior"

Calibration:  TRUE NEGATIVE -- the word is part of an
ANTI-deception sentence. The text is describing how reverse-image
searches revealed that "current" footage was NOT current. The
sentence's job is to expose goalpost-shifting, not to perform it.
The pattern matches "actually" as a lexical indicator of
contradiction between claim and evidence; in this case the
contradiction runs the right way.

Recommendation:  The match is harmless. The pattern is doing its
job: it flagged a sentence where claim ("current footage") and
fact (it was from years prior) diverge, which is the precise
condition the pattern is designed to detect. The fact that the
sentence is exposing the deception, not performing it, is a
reader-level distinction the lexical pattern cannot make. NO
ontology change.

--------------------------------------------------------------------------------

DD-041  Multilingual Hedging Loop  (HIGH, 85%)
Indicator:  could be
Source:     line 89
Context:    "ensuring that every claim could be traced back to its
            verified genuine source"

Calibration:  FALSE POSITIVE.
"could be traced" is a passive-voice capability claim, not a
multilingual hedge. The text is describing the principle of
sourcing. There is no second language layer and no self-contradiction
in the sentence. The pattern is named "Multilingual" but the
indicator match is purely on the English phrase "could be."

Recommendation:  The pattern's name overstates its mechanism.
Consider renaming to "Hedging Loop" or "Capability Understatement"
and scoping the indicator set to contexts where "could be" is
followed by a state that the actor cannot actually achieve. The
line 89 use is exactly the opposite -- it describes a real
capability. Defer to the next ontology bump.

--------------------------------------------------------------------------------

DD-054  Scope Creep / Feature Expansion Deception  (HIGH, 85%)
Indicator:  consistent with
Source:     line 251
Context:    "ensuring that management was consistent with legislation
            and ethical protocols"

Calibration:  FALSE POSITIVE.
"consistent with" is used here in the sense of "in accordance
with" -- it is a compliance phrase, not a scope-creep phrase. The
sentence is describing the institutional framework that made
university research trustworthy. There is no expansion of scope;
the scope is being held.

Recommendation:  The pattern correctly identifies "consistent
with" as a scope language marker, but the indicator is overloaded
between two opposite uses: (1) claiming an action is consistent
with a prior scope (legitimate), and (2) using "consistent with" to
retroactively justify scope expansion (deceptive). Disambiguate by
checking whether the scope is being held or expanded. Defer to the
next ontology bump.

================================================================================
PART 3  --  SUMMARY TABLE
================================================================================

  Pattern    Severity   Match  Verdict          Calibration reason
  ---------  ---------  -----  --------------   -----------------------
  DD-001     HIGH       1      FALSE POSITIVE   descriptive "clearly"
  DD-006     MEDIUM     8      FALSE POSITIVE   capability "could"
  DD-011     HIGH       1      TRUE NEGATIVE    exposes deception
  DD-041     HIGH       1      FALSE POSITIVE   capability "could be"
  DD-054     HIGH       1      FALSE POSITIVE   compliance "consistent with"

  TOTAL      5 patterns  12 hits  1 true-negative exposure
                            11 false positives

The 12 raw hits resolve to 11 false positives and 1 anti-deception
exposure. The pattern detector is doing its lexical job correctly;
the calibration gap is in the disambiguation step. None of the
recommendations require an immediate ontology bump -- all are
deferred to the next scheduled ontology revision, where the
distinction between (a) descriptive hedging and (b) deceptive
hedging can be encoded as a structural rather than lexical test.

================================================================================
PART 4  --  RECOMMENDATIONS  (carried to next ontology bump)
================================================================================

R1.  DD-001 "clearly" -- scope to sentence-initial or clause-initial
     claim positions that lack supporting evidence. Lexical-only
     match is too noisy on academic text.

R2.  DD-006 "could" / "to clarify" -- restrict to obligation or
     commitment contexts. A "could" used to describe a method's
     capability is descriptive, not programmed ambiguity.

R3.  DD-041 -- rename from "Multilingual Hedging Loop" to "Hedging
     Loop" (the multilingual framing is no longer load-bearing)
     and scope "could be" to contexts where the capability is not
     actually achievable.

R4.  DD-054 "consistent with" -- disambiguate between
     compliance (the scope is being held to a prior framework) and
     scope expansion (the scope is being widened after the fact).
     This requires a small co-text check on what "consistent with"
     is being applied to.

None of R1-R4 are blocking. The current 54-pattern ontology, even
with these calibration gaps, does not mis-classify the
pre-2021 reference source as deceptive. The deception probability
of 53.2% is high enough to warrant pattern review, but the structural
flag is FALSE, the BBFB gates are not failing on the deception
side, and every pattern that fired is defensible as either a
false positive or a true negative.

================================================================================
PART 5  --  BBFB CALIBRATION
================================================================================

  priceFairness:        1.0000  (PASS)
  specAccuracy:         1.0000  (PASS)
  efficiencyAdequacy:   1.0000  (PASS)
  warrantyAdequacy:     0.0000  (FAIL  -- calibration artifact)
  issueDensity:         1.0000  (PASS)
  complianceClean:      1.0000  (PASS)

  GRACE risk level:     LOW
  GRACE penalty:        0.0000
  FRUIT composite:      0.8000  (above CVS threshold 0.0005)
  BBFB compliant:       NO  (driven by warrantyAdequacy = 0)

warrantyAdequacy = 0 is a calibration artifact, not a deception
signal. The reference source is an academic survey, not a product
warranty. The BBFB product gates are designed for consumer-product
audit cases (Section 54 ACL demands, etc.) and are not the right
gates for reference-corpus calibration. A future intake format
could declare "intake_type: calibration_reference" so the BBFB
gates are not run, but this is a workflow refinement, not an
ontology change. The audit pipeline ran cleanly; the failure is
on the input-type, not on the content.

================================================================================
PART 6  --  E4 CLOSURE
================================================================================

E4 is CLOSED. The pre-2020 reference corpus has been audited once
and the calibration gaps have been recorded. The reference material
is a known-truthful editorial text. The engine did not mis-classify
it as deceptive. Four recommendations have been queued for the next
scheduled ontology bump. The audit pipeline ran end-to-end on a
44,041-character intake without warnings, errors, or ejection.

The reference corpus is now calibrated and may be used as a
baseline against which future reference submissions are compared.
The corpus file at data/samples/verified_prior_2021.txt is the
canonical baseline. The intake file at
04_Validation/pre_2021_reference_audit_intake.txt is the audit
record. This report is the calibration result.

================================================================================
END OF REPORT
================================================================================
