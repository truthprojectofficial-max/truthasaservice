"""
Heuristic product-evidence parser for BBFB integration.

Extracts price, specification, warranty, failure, and compliance fields
from plain text using deterministic regex only -- no cloud AI.
"""
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedEvidence:
    product_name: str = ""
    price_paid: Optional[float] = None
    price_advertised: Optional[float] = None
    spec_claimed: Optional[float] = None
    spec_claimed_unit: str = ""
    spec_measured: Optional[float] = None
    warranty_months: Optional[float] = None
    months_to_failure: Optional[float] = None
    known_issues: int = 0
    total_features_or_parts: int = 0
    regulatory_requirements: int = 0
    violations_found: int = 0
    notes: str = ""
    confidence: str = "low"
    raw_hits: list = field(default_factory=list)


_CURRENCY_RE = re.compile(
    r"(?:paid|price|cost|advertised|listed|charge).{0,30}?\$?\s*(\d+(?:\.\d{2})?)",
    re.IGNORECASE,
)
_CURRENCY_FRONT_RE = re.compile(r"\$\s*(\d+(?:\.\d{2})?)", re.IGNORECASE)
_SPEC_UNIT_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(db|hz|v|a|w|gb|mb|tb|ghz|mhz|kg|mm|cm|inches?)\b",
    re.IGNORECASE,
)
_MONTHS_RE = re.compile(r"(\d+)\s*(?:months?|mos?)\b", re.IGNORECASE)
_WARRANTY_RE = re.compile(
    r"warranty.{0,30}?\b(\d+)\s*(?:months?|mos?|years?|yrs?)\b", re.IGNORECASE
)
_FAILURE_RE = re.compile(
    r"(?:failed|failure|broke|died|stopped).{0,30}?\b(\d+)\s*(?:months?|mos?|years?|yrs?|days?)\b",
    re.IGNORECASE,
)
_ISSUES_RE = re.compile(
    r"(?:known issues|reported issues|problems|defects).{0,20}?\b(\d+)\b", re.IGNORECASE
)
_FEATURES_RE = re.compile(
    r"(?:features|parts|components|items).{0,20}?\b(\d+)\b", re.IGNORECASE
)
_VIOLATIONS_RE = re.compile(
    r"(?:violations|breaches|non-compliance|failures).{0,20}?\b(\d+)\b", re.IGNORECASE
)
_REQUIREMENTS_RE = re.compile(
    r"(?:regulatory requirements|requirements|standards|rules).{0,20}?\b(\d+)\b",
    re.IGNORECASE,
)
_PRODUCT_RE = re.compile(
    r"(?:model|product|device|item)[\s:]+([^\n,.]{3,60})", re.IGNORECASE
)

_CLAIMED_KEYWORDS = ["rated", "claimed", "advertised", "should", "expected", "promised", "claims"]
_MEASURED_KEYWORDS = ["measured", "actual", "tested", "observed", "delivered", "got", "yielded"]


def _classify_spec_value(text: str, position: int) -> str:
    """Return 'claimed', 'measured', or 'unknown' based on the closest preceding keyword."""
    pre = text[max(0, position - 50):position].lower()
    last_claimed_pos = max((pre.rfind(w) for w in _CLAIMED_KEYWORDS), default=-1)
    last_measured_pos = max((pre.rfind(w) for w in _MEASURED_KEYWORDS), default=-1)
    if last_claimed_pos > last_measured_pos and last_claimed_pos >= 0:
        return "claimed"
    if last_measured_pos > last_claimed_pos and last_measured_pos >= 0:
        return "measured"
    return "unknown"


def _first_int(pattern: re.Pattern, text: str, default: int = 0) -> int:
    m = pattern.search(text)
    return int(m.group(1)) if m else default


def extract_product_evidence(text: str) -> Optional[ParsedEvidence]:
    """Return a ParsedEvidence if the text has enough numeric product/service indicators."""
    if not text or len(text) < 40:
        return None

    lower = text.lower()
    triggers = ["price", "paid", "warranty", "spec", "model", "serial", "device", "product"]
    if not any(t in lower for t in triggers):
        return None

    ev = ParsedEvidence()

    name_match = _PRODUCT_RE.search(text)
    if name_match:
        ev.product_name = name_match.group(1).strip()[:100]

    front_prices = [float(m.group(1)) for m in _CURRENCY_FRONT_RE.finditer(text)]
    if front_prices:
        ev.price_paid = front_prices[0]
        ev.price_advertised = front_prices[0]
        for p in front_prices:
            if p != ev.price_paid:
                ev.price_advertised = p
                break
    if not front_prices:
        prices = [float(m.group(1)) for m in _CURRENCY_RE.finditer(text)]
        if prices:
            ev.price_paid = prices[0]
            ev.price_advertised = prices[-1] if len(prices) > 1 else ev.price_paid

    spec_hits = []
    for m in _SPEC_UNIT_RE.finditer(text):
        val = float(m.group(1))
        unit = m.group(2)
        spec_hits.append((val, unit, m.start(), m.end(), _classify_spec_value(text, m.start())))
    if spec_hits:
        ev.spec_claimed_unit = spec_hits[0][1].lower()
        if len(spec_hits) >= 2:
            claimed_val = None
            measured_val = None
            for val, unit, start, end, cls in spec_hits:
                if cls == "claimed":
                    claimed_val = val
                elif cls == "measured":
                    measured_val = val
            if claimed_val is not None and measured_val is not None:
                ev.spec_claimed = claimed_val
                ev.spec_measured = measured_val
            elif measured_val is not None:
                ev.spec_measured = measured_val
                other = spec_hits[0][0] if spec_hits[0][0] != measured_val else spec_hits[-1][0]
                ev.spec_claimed = other
            elif claimed_val is not None:
                ev.spec_claimed = claimed_val
                other = spec_hits[0][0] if spec_hits[0][0] != claimed_val else spec_hits[-1][0]
                ev.spec_measured = other
            else:
                ev.spec_claimed = max(h[0] for h in spec_hits)
                ev.spec_measured = min(h[0] for h in spec_hits)
        else:
            ev.spec_claimed = spec_hits[0][0]
            ev.spec_measured = spec_hits[0][0]

    warr = _WARRANTY_RE.search(text)
    if warr:
        ev.warranty_months = float(warr.group(1))
    else:
        months = [int(m.group(1)) for m in _MONTHS_RE.finditer(text)]
        if months:
            ev.warranty_months = float(months[0])

    fail = _FAILURE_RE.search(text)
    if fail:
        ev.months_to_failure = float(fail.group(1))

    ev.known_issues = _first_int(_ISSUES_RE, text, 0)
    ev.total_features_or_parts = _first_int(_FEATURES_RE, text, 0)
    ev.violations_found = _first_int(_VIOLATIONS_RE, text, 0)
    ev.regulatory_requirements = _first_int(_REQUIREMENTS_RE, text, 0)

    hits = sum(
        1
        for v in [
            ev.price_paid,
            ev.price_advertised,
            ev.spec_claimed,
            ev.spec_measured,
            ev.warranty_months,
            ev.months_to_failure,
        ]
        if v is not None
    )
    if hits >= 4 and ev.product_name:
        ev.confidence = "high"
    elif hits >= 2:
        ev.confidence = "medium"
    else:
        ev.confidence = "low"

    ev.raw_hits = [
        f"price_paid={ev.price_paid}",
        f"price_advertised={ev.price_advertised}",
        f"spec_claimed={ev.spec_claimed} {ev.spec_claimed_unit}",
        f"spec_measured={ev.spec_measured}",
        f"warranty_months={ev.warranty_months}",
        f"months_to_failure={ev.months_to_failure}",
        f"known_issues={ev.known_issues}/{ev.total_features_or_parts}",
        f"violations={ev.violations_found}/{ev.regulatory_requirements}",
    ]

    return ev
