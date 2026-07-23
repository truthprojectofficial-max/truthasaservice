"""
test_privacy_compliance_docs.py
================================

The Privacy Policy (PRIVACY_POLICY_2026-07-24.md) and NDB Response Plan
(NDB_RESPONSE_PLAN_2026-07-24.md) must:
  1. Both files exist at 04_Validation/
  2. The Privacy Policy covers all 13 APPs (Australian Privacy Principles)
  3. The NDB Plan references the 30-day window
  4. The NDB Plan references the OAIC notification
  5. The Privacy Policy references the NDB Plan
  6. The Privacy Policy references the operator name (Justin Barnett)

If any fail, the operator cannot claim APP compliance.
"""
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
PRIVACY = PROJECT / "04_Validation" / "PRIVACY_POLICY_2026-07-24.md"
NDB = PROJECT / "04_Validation" / "NDB_RESPONSE_PLAN_2026-07-24.md"

# The 13 APPs (Australian Privacy Principles)
APP_NUMBERS = list(range(1, 14))


def test_privacy_policy_exists():
    """The Privacy Policy file exists."""
    assert PRIVACY.exists(), f"PRIVACY_POLICY_2026-07-24.md not found at {PRIVACY}"


def test_ndb_response_plan_exists():
    """The NDB Response Plan file exists."""
    assert NDB.exists(), f"NDB_RESPONSE_PLAN_2026-07-24.md not found at {NDB}"


def test_privacy_policy_covers_all_13_apps():
    """The Privacy Policy mentions all 13 Australian Privacy Principles."""
    text = PRIVACY.read_text(encoding="utf-8")
    for app in APP_NUMBERS:
        pattern = rf"APP\s+{app}\b"
        assert re.search(pattern, text), f"Privacy Policy does not reference APP {app}"


def test_privacy_policy_references_oaic():
    """The Privacy Policy references the OAIC for complaints."""
    text = PRIVACY.read_text(encoding="utf-8")
    assert "OAIC" in text, "Privacy Policy does not reference OAIC"


def test_privacy_policy_references_ndb_plan():
    """The Privacy Policy references the NDB Response Plan."""
    text = PRIVACY.read_text(encoding="utf-8")
    assert "NDB_RESPONSE_PLAN" in text, "Privacy Policy does not reference NDB Response Plan"


def test_privacy_policy_references_operator():
    """The Privacy Policy names the operator (Justin Barnett)."""
    text = PRIVACY.read_text(encoding="utf-8")
    assert "Justin Barnett" in text, "Privacy Policy does not name the operator"


def test_privacy_policy_references_privacy_act():
    """The Privacy Policy references the Privacy Act 1988 (Cth)."""
    text = PRIVACY.read_text(encoding="utf-8")
    assert "Privacy Act 1988" in text, "Privacy Policy does not reference Privacy Act 1988"


def test_ndb_plan_references_30_day_window():
    """The NDB Plan references the 30-day assessment window."""
    text = NDB.read_text(encoding="utf-8")
    assert "30 days" in text or "30-day" in text, "NDB Plan does not reference 30-day window"


def test_ndb_plan_references_oaic():
    """The NDB Plan references the OAIC notification."""
    text = NDB.read_text(encoding="utf-8")
    assert "OAIC" in text, "NDB Plan does not reference OAIC"


def test_ndb_plan_references_privacy_policy():
    """The NDB Plan references the Privacy Policy."""
    text = NDB.read_text(encoding="utf-8")
    assert "PRIVACY_POLICY" in text, "NDB Plan does not reference Privacy Policy"


def test_ndb_plan_references_chain_events():
    """The NDB Plan defines the sealed chain events (NDB_SUSPECTED, NDB_ASSESSMENT, etc)."""
    text = NDB.read_text(encoding="utf-8")
    for event in ("NDB_SUSPECTED", "NDB_ASSESSMENT", "NDB_OAIC_NOTIFICATION", "NDB_USER_NOTIFICATION"):
        assert event in text, f"NDB Plan does not define chain event {event}"


def test_ndb_plan_references_13_apps():
    """The NDB Plan references the 13 APPs it implements."""
    text = NDB.read_text(encoding="utf-8")
    assert "13 APPs" in text or "13 Australian Privacy Principles" in text, \
        "NDB Plan does not reference 13 APPs"
