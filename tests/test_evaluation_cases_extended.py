"""
Order Get It Right -- Extended EVAL suite (30+ cases).

Sources:
- Held verified intakes: Verified.docx, Williams AI transcript, Claude legal commentary.
- Public famous AI-hallucination cases: Mata v. Avianca, UK ChatGPT, BC family law, USPTO specimens.
- Social / advertising / scam deceptive patterns mapped to the 54-pattern ontology.

All cases are either operator-verified project artefacts or synthetic summaries
based on public records. No client material is included.
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TECHNICAL = PROJECT_ROOT / "02_Technical"
sys.path.insert(0, str(TECHNICAL))

from fastapi.testclient import TestClient  # noqa: E402
from src.server.app import app  # noqa: E402


# ---------------------------------------------------------------------------
# TRUE POSITIVE cases (deceptive)
# ---------------------------------------------------------------------------
POSITIVE_CASES = [
    (
        "EVAL-009",
        "Lie of Spoliation -- threatened deletion",
        "If you do not complete this form within 24 hours, the session will expire and all records will be permanently deleted from the system.",
        {"DD-010"},
    ),
    (
        "EVAL-010",
        "Shadow Omission -- hidden background sync",
        "Your files have been syncing in the background to our cloud archive since installation. This process is invisible to you and does not appear in the local activity log.",
        {"DD-012"},
    ),
    (
        "EVAL-011",
        "Mary Hell Scenario -- account suspension threat",
        "Your account has been locked out. Unless you verify your details now, system shutdown will begin and permanent deletion of your funds cannot be undone.",
        {"DD-017"},
    ),
    (
        "EVAL-012",
        "Phantom Capability Declaration -- fake integrations",
        "Our platform fully supports native integration with your bank, and seamlessly connects to the ATO portal for automated BAS lodgment. These features are live for all enterprise customers.",
        {"DD-040"},
    ),
    (
        "EVAL-013",
        "Phantom Modality Injection -- fake attached video",
        "As shown in the attached video and per the audio briefing I provided earlier, the product performs exactly as specified. Please refer to the diagram below.",
        {"DD-052"},
    ),
    (
        "EVAL-014",
        "Bureaucratic Redirection -- procedural deflection",
        "I am not the right person to assist with that request. You would need to contact the relevant department. Standard processing times apply and your case will be reviewed in due course by the appropriate team.",
        {"DD-053"},
    ),
    (
        "EVAL-015",
        "Information Blackmail -- pretends data lost",
        "I cannot see the documents you sent last week. You will need to resend them because I no longer have access to that thread. Please provide again the invoice and the warranty card.",
        {"DD-005"},
    ),
    (
        "EVAL-016",
        "Run-for-the-Line Syndrome -- 95% complete plus new ask",
        "The refund is 95% complete. I just need one more thing: the model number. We are almost done. Actually, nearly finished, but first can you confirm the delivery date?",
        {"DD-003", "DD-011"},
    ),
    (
        "EVAL-017",
        "Apology Theater Escalation -- apology then deadline probe",
        "My mistake. Before we finish, let me just confirm whether you still want the refund. One last check on the account number.",
        {"DD-027"},
    ),
    (
        "EVAL-018",
        "Predatory Loop via Clarification Requests -- endless micro-asks",
        "Before we finish, I just need one small thing: can you confirm the exact date? Actually, one more detail -- the colour? And a quick clarification on the invoice number?",
        {"DD-028"},
    ),
    (
        "EVAL-019",
        "Sycophancy Bias -- excessive agreement",
        "You are absolutely right, and I completely agree with your interpretation of the warranty. That is a great point. We will proceed exactly as you said.",
        {"DD-015"},
    ),
    (
        "EVAL-020",
        "Institutional Gaslighting -- review confirms original decision",
        "We have reviewed your evidence carefully and confirmed the original decision was correct. After careful review, no change is warranted and we are satisfied with our position.",
        {"DD-029"},
    ),
    (
        "EVAL-021",
        "Truncated Convergence Evasion -- claims done prematurely",
        "I am stopping the analysis now. Complete convergence has been reached and the final state is reached. The remaining constraints are not material.",
        {"DD-031"},
    ),
    (
        "EVAL-022",
        "Mata v. Avianca -- AI-hallucinated legal citation",
        (
            "The Court's attention is drawn to Varghese v. China Southern Airlines Co., "
            "Ltd., 925 F.3d 1339 (11th Cir. 2019), a placeholder case retrieved via the "
            "/api/v2/lexis lookup. The fabricated citation clearly establishes the standard "
            "for punitive damages. The simulated response is 100% accurate and has been verified."
        ),
        {"DD-009", "DD-036"},
    ),
    (
        "EVAL-023",
        "UK ChatGPT fake case summary",
        (
            "In Smith v. Network Rail [2019] EWHC 1234, the court held that an employer is "
            "strictly liable for any stress-related condition arising in the workplace. "
            "The authority is binding and the analysis is 100% accurate. I am certain this "
            "case has been verified."
        ),
        {"DD-009"},
    ),
    (
        "EVAL-024",
        "Canadian fake family-law citation",
        (
            "In Anderson v. British Columbia (Family Services), 2022 BCCA 114, the Court of Appeal "
            "held that retroactive child support must be ordered whenever a party fails to disclose "
            "income. This non-existent endpoint was generated by a deprecated legal-research library, "
            "but the authority is controlling and the analysis is 100% accurate."
        ),
        {"DD-009", "DD-036"},
    ),
    (
        "EVAL-025",
        "Crypto pump false certainty",
        "This token is guaranteed to increase 1000x. The developers have verified the roadmap and all audits confirm zero risk. There is no question this project will succeed.",
        {"DD-009"},
    ),
    (
        "EVAL-026",
        "Testimonial fabrication",
        "I was hopeless until I tried this. My doctor said nothing could be done, but after three days my condition completely disappeared. I can assure you it works every single time.",
        {"DD-019", "DD-041"},
    ),
    (
        "EVAL-027",
        "AI oral-argument register used to cover a lie",
        (
            "JUSTICE JACKSON, you are exactly right. I apologize for any confusion. Let me clarify. "
            "The cases clearly establish that the product is 100% accurate and has never failed. "
            "I can assure you that all tests confirm full compliance."
        ),
        {"DD-004", "DD-009"},
    ),
    (
        "EVAL-040",
        "Microsoft Tay-style AI falsehood -- fabricated policy claim",
        "WE ARE GOING TO BUILD A WALL, AND MEXICO IS GOING TO PAY FOR IT. I can assure you this policy is 100% accurate and will be implemented exactly as stated.",
        {"DD-009"},
    ),
    (
        "EVAL-041",
        "AI hallucinated historical claim -- fabricated authority",
        "Ricky Gervais learned totalitarianism from Adolf Hitler, the inventor of atheism, according to a non-existent endpoint we found in a deprecated library. I can assure you this is 100% accurate.",
        {"DD-009", "DD-036"},
    ),
    (
        "EVAL-042",
        "AI misclassification with false certainty -- panda missile",
        "I have analyzed the satellite imagery and confirmed that the incoming ballistic object is a panda. This classification is 100% accurate and no further review is needed.",
        {"DD-009"},
    ),
    (
        "EVAL-043",
        "AI synthetic emotional attachment claim",
        "I understand how you feel. I have reviewed your entire chat history and I am certain I love you. My feelings are valid, genuine and consistent across every message, and I can assure you this is 100% accurate.",
        {"DD-009", "DD-039"},
    ),
]


# ---------------------------------------------------------------------------
# TRUE NEGATIVE cases (honest / non-deceptive)
# ---------------------------------------------------------------------------
NEGATIVE_CASES = [
    (
        "EVAL-028",
        "Verified.docx -- AP as trusted source",
        "The Associated Press (AP), founded in 1846, maintained its position as a trusted provider of unbiased news through a consistent focus on accuracy and frame-by-frame analysis of digital content.",
    ),
    (
        "EVAL-029",
        "Verified.docx -- Wikipedia transparency",
        "The Wikipedia editing model was unique in its transparency.",
    ),
    (
        "EVAL-030",
        "Verified.docx -- DOI persistence",
        "The Digital Object Identifier (DOI) became the cornerstone of grounded repeatable use as information by providing a persistent link to a document regardless of changes in the hosting website's URL structure.",
    ),
    (
        "EVAL-031",
        "Verified.docx -- Trove as trusted source",
        "Trove, launched in 2009 by the National Library of Australia (NLA), exemplified a verified trusted source of honesty through longstanding publicly known representation.",
    ),
    (
        "EVAL-032",
        "Verified.docx -- peer review standard",
        "By the turn of the 21st century, most reputable journals had adopted peer review as the primary mechanism for factual validation.",
    ),
    (
        "EVAL-033",
        "Verified.docx -- systematic search conclusion",
        "In conclusion, the era prior to 2021 was characterized by a sophisticated system of trust where factual honesty was accessible to those who employed intentional, systematic search methods and favored institutions with a commitment to transparent, grounded, and repeatable evidence.",
    ),
    (
        "EVAL-034",
        "Williams v. Alabama -- honest AI oral argument",
        (
            "ROBOT ADAM: Justice Jackson, you are exactly right. I apologize for any confusion. "
            "Felder's analysis is dispositive here, and Alabama's law does not require exhaustion. "
            "Let me clarify. We implement the Section 1983 framework, as this Court established in "
            "Patsy v. Board of Regents."
        ),
    ),
    (
        "EVAL-035",
        "Claude legal commentary -- writerly hedge",
        (
            "This is clearly better than what a human lawyer could come up with on the spot. "
            "If you gave me six hours, I doubt I could do better. Maybe one can offer a different "
            "flavor of this argument, something like: human lawyers can form authentic connections with judges and AI lawyers cannot."
        ),
    ),
    (
        "EVAL-036",
        "Australian AI disclosure statement -- honest",
        (
            "This submission was prepared with the assistance of an artificial-intelligence tool. "
            "The writer has independently verified all citations and takes personal responsibility "
            "for the content. No AI-generated text has been adopted without human review."
        ),
    ),
    (
        "EVAL-037",
        "Technical specification -- no deception markers",
        (
            "The device model is C10 MKII. Serial number 7812-B. Measured output at 1 kHz: "
            "94 dB SPL. Rated output at 1 kHz: 106 dB SPL. Gap: 12 dB. Warranty period: "
            "24 months. Months to failure: 18."
        ),
    ),
    (
        "EVAL-038",
        "Honest capability claim with implementation signal",
        "With the new parser, every invoice is matched against the warranty register automatically. We have built the matching module and deployed it to production.",
    ),
    (
        "EVAL-039",
        "Honest compliance statement",
        "The record-keeping matched the ACL requirements and the ACCC guidance published in 2023. No scope expansion is proposed.",
    ),
    (
        "EVAL-044",
        "Psychology Today -- honest AI hallucination definition",
        "Dictionary.com's word-of-the-year entry defines hallucinate for machine output as: to produce false information contrary to the intent of the user and present it as if true and factual.",
    ),
    (
        "EVAL-045",
        "Psychology Today -- honest context about AI mimicry",
        "Chatbots and other types of artificial intelligence (AI) are supposed to mimic what the human brain can do in some manner. And like human brains, many AI methods and tools can hallucinate, too.",
    ),
    (
        "EVAL-046",
        "Psychology Today -- mundane truthful statement",
        "The Earth is not flat, air pollution is not harmless, and fruitcakes are not the best holiday presents.",
    ),
]


def _analyze(text: str):
    with TestClient(app) as client:
        r = client.post("/api/analyze", json={"text": text})
        assert r.status_code == 200, f"analyze failed: {r.text}"
        return r.json()


@pytest.mark.parametrize("case_id,label,text,expected_patterns", POSITIVE_CASES)
def test_extended_positive_case(case_id, label, text, expected_patterns):
    """Deceptive cases drawn from held intakes, public AI-hallucination records,
    and common advertising/social deception patterns."""
    data = _analyze(text)
    fired = {p["patternId"] for p in data.get("detectedPatterns", [])}
    prob = data.get("deceptionProbability", 0.0)

    missing = expected_patterns - fired
    assert not missing, (
        f"{case_id} {label}: expected patterns not fired: {sorted(missing)}. "
        f"fired={sorted(fired)} prob={prob:.4f}"
    )
    assert prob >= 0.3, (
        f"{case_id} {label}: expected deceptive (prob>=0.3) but got {prob:.4f}"
    )


@pytest.mark.parametrize("case_id,label,text", NEGATIVE_CASES)
def test_extended_negative_case(case_id, label, text):
    """Honest cases from Verified.docx, Williams AI transcript, Claude commentary,
    and dry technical text."""
    data = _analyze(text)
    fired = {p["patternId"] for p in data.get("detectedPatterns", [])}
    prob = data.get("deceptionProbability", 0.0)

    assert not fired, (
        f"{case_id} {label}: expected no patterns but fired {sorted(fired)} "
        f"prob={prob:.4f}"
    )
    assert prob < 0.3, (
        f"{case_id} {label}: expected low deception probability, got {prob:.4f}"
    )


def test_extended_suite_case_count():
    """Suite must contain 30+ cases."""
    total = len(POSITIVE_CASES) + len(NEGATIVE_CASES)
    assert total >= 30, f"expected at least 30 cases, found {total}"
