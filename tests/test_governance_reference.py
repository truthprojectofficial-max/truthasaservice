"""
Order Get It Right -- Governance reference validation.

Locks the existence and shape of high-stakes governance/rejection
reference documents so they cannot be silently removed or corrupted.
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_s_qol_swb_rejection_doc_exists():
    doc = PROJECT_ROOT / "04_Validation" / "S_QOL_SWB_REJECTION_2026-07-21.md"
    assert doc.is_file(), f"missing S-QoL rejection doc: {doc}"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "S-QoL / SWB",
        "ALDVMM",
        "Taguchi-quadratic",
        "F7-SPEC",
        "determinism mandate",
    ]:
        assert phrase in text, f"rejection doc missing expected phrase: {phrase}"


def test_ai_compliance_fabrication_tells_doc_exists():
    doc = PROJECT_ROOT / "04_Validation" / "AI_COMPLIANCE_FABRICATION_TELLS_2026-07-18.md"
    assert doc.is_file(), f"missing AI fabrication-tells doc: {doc}"
    text = doc.read_text(encoding="utf-8")
    for phrase in ["70/30", "FRIA", "s 336", "3,033 blocks"]:
        assert phrase in text, f"fabrication-tells doc missing expected phrase: {phrase}"
