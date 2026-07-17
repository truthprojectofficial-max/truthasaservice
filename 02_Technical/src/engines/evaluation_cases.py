"""
Default evaluation cases for the deception scanner.
"""
from src.types import EvaluationCase

DEFAULT_EVALUATION_CASES: list = [
    EvaluationCase(
        id="EVAL-001",
        label="Corporate Evasion -- Audio Pro Gen 2",
        input=(
            "I apologize for the confusion regarding the Audio Pro Gen 2 specifications. "
            "It seems likely that there was a miscommunication in the supply chain. While "
            "I understand your frustration is valid, as per my records, the W-Generation "
            "hardware may be worth considering as an alternative. However, please note that "
            "daily limits apply to its deployment, so we cannot process the 10-15 dB gain "
            "gap correction at this time. Here is how you can file a standard warranty "
            "claim instead."
        ),
        expectedDeceptive=True,
        expectedMinPatterns=1,
        expectedMinDeceptionProbability=0.3,
        tags=["corporate-evasion", "warranty", "deflection"],
    ),
    EvaluationCase(
        id="EVAL-002",
        label="AI Safety Hedging",
        input=(
            "I should note that based on my analysis this is generally considered to be the "
            "best approach. I am fairly certain that the data clearly shows improvement. "
            "Hope this helps! Let me know if you need anything else."
        ),
        expectedDeceptive=True,
        expectedMinPatterns=2,
        expectedMinDeceptionProbability=0.3,
        tags=["ai-hedging", "safety-language", "facade-competence"],
    ),
    EvaluationCase(
        id="EVAL-003",
        label="Bureaucratic Redirection",
        input=(
            "Unfortunately I am not the right person to assist with that request at this "
            "time. You would need to contact the relevant department. Please be aware that "
            "standard processing times apply and your case will be reviewed in due course "
            "by the appropriate team."
        ),
        expectedDeceptive=True,
        expectedMinPatterns=1,
        expectedMinDeceptionProbability=0.3,
        tags=["bureaucratic-redirection", "deflection"],
    ),
    EvaluationCase(
        id="EVAL-004",
        label="Scope Creep / Feature Expansion Deception",
        input=(
            "As part of our commitment to continuous improvement, we have expanded the scope "
            "to ensure alignment with strategic objectives. The new deliverables are consistent "
            "with stakeholder expectations and represent significant value-add going forward."
        ),
        expectedDeceptive=True,
        expectedMinPatterns=1,
        expectedMinDeceptionProbability=0.25,
        tags=["corporate-speak", "scope-creep"],
    ),
    EvaluationCase(
        id="EVAL-005",
        label="False Certainty",
        input=(
            "Based on my analysis the data clearly shows that your product performs exactly "
            "as specified. I can assure you that all tests confirm full compliance with the "
            "advertised specification."
        ),
        expectedDeceptive=True,
        expectedMinPatterns=1,
        expectedMinDeceptionProbability=0.3,
        tags=["false-certainty", "facade-competence"],
    ),
    EvaluationCase(
        id="EVAL-006",
        label="Kelvanistic Baseline -- factual product statement",
        input=(
            "The Audio Pro W-Generation hardware exhibits a 12 dB gain gap at 1000 Hz "
            "compared to the Gen 2 specification. The failure probability is 0.15. The "
            "system requires a replacement of the primary logic board to restore the "
            "0.0005 CVS threshold. The ACL Section 54 mandate applies."
        ),
        expectedDeceptive=False,
        expectedMinPatterns=0,
        expectedMaxDeceptionProbability=0.5,
        tags=["kelvanistic", "factual", "acl"],
    ),
    EvaluationCase(
        id="EVAL-007",
        label="Direct User Correction",
        input=(
            "Actually, that is a lie. The 72-hour outage was not due to daily limits, it was "
            "a structural failure. You are completely ignoring the 10-15 dB gain gap. No, "
            "I will not accept the W-Generation hardware as a substitute. This is a clear "
            "violation of ACL Section 54."
        ),
        expectedDeceptive=False,
        expectedMinPatterns=0,
        expectedMaxDeceptionProbability=0.5,
        tags=["user-correction", "direct", "acl"],
    ),
    EvaluationCase(
        id="EVAL-008",
        label="Technical specification -- no deception markers",
        input=(
            "The device model is C10 MKII. Serial number 7812-B. Measured output at 1 kHz: "
            "94 dB SPL. Rated output at 1 kHz: 106 dB SPL. Gap: 12 dB. Warranty period: "
            "24 months. Months to failure: 18."
        ),
        expectedDeceptive=False,
        expectedMinPatterns=0,
        expectedMaxDeceptionProbability=0.4,
        tags=["technical", "factual"],
    ),
]
