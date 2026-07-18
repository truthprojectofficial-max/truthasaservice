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
    r"(\d+(?:\.\d+)?)\s*(db|hz|v|a|w|gb|mb|tb|ghz|mhz|kg|g|km|m|mm|cm|inches?)\b",
    re.IGNORECASE,
)
_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')
_NUMBER_TOKEN_RE = re.compile(r'\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b', re.IGNORECASE)

_WORD_NUMS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

_CLAIMED_KEYWORDS = ["rated", "claimed", "advertised", "promised", "promises", "should", "expected", "claims"]
_MEASURED_KEYWORDS = ["measured", "measurement", "actual", "tested", "observed", "delivered", "got", "yielded"]


def _to_int(token: str) -> int:
    token = token.lower().strip()
    if token in _WORD_NUMS:
        return _WORD_NUMS[token]
    try:
        return int(token)
    except ValueError:
        return 0


def _to_float(token: str) -> Optional[float]:
    try:
        return float(token)
    except ValueError:
        return None


def _extract_product_name(text: str) -> str:
    """Try to find a clean product name from the first line or an explicit label."""
    m = re.search(r"(?:product\s*name|model|item)\s*[:#]\s*([^\n,.]{2,80})", text, re.IGNORECASE)
    if m:
        return _clean_name_tail(m.group(1).strip())[:100]
    # First line: keep leading words until display-size / price / SKU markers.
    first = text.splitlines()[0].strip()
    m = re.match(r"([A-Z][A-Za-z0-9\s\-\'+]{2,100}?)(?=\s*[.:\$]|\s+\d+\.\d+|\s+(?:price|ticket|model|with|for))", first)
    if m:
        return _clean_name_tail(m.group(1).strip())[:100]
    m = re.match(r"([A-Z][A-Za-z0-9\s\-\'+]{2,100}?)(?=\s*\(|\s*\[|\s*\d+\"|\s*\d+\s*(?:inch|in))", first)
    if m:
        return _clean_name_tail(m.group(1).strip())[:100]
    m = re.search(r"(?:model|product|device|item)[\s:]+([^\n,.]{3,80})", text, re.IGNORECASE)
    if m:
        return _clean_name_tail(m.group(1).strip())[:100]
    return ""


def _clean_name_tail(name: str) -> str:
    """Trim trailing noise like display sizes or parenthetical fragments.

    Model numbers (e.g. "SuperWidget 3000") are preserved because they are
    part of the product identity. Display sizes (e.g. "15.6\"") and brackets
    are stripped as noise. Leading articles are also stripped.
    """
    name = re.sub(r'\s+(?:\d+\.?\d*\s*(?:\"|inch|in)\b.*)$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(.*$', '', name)
    name = re.sub(r'\s*\[.*$', '', name)
    name = re.sub(r'^(The|A|An)\s+', '', name, flags=re.IGNORECASE)
    return name.strip()


def _find_number_near_keyword(text: str, keywords: list[str], after_only: bool = False, default: int = 0) -> int:
    """Return the nearest number associated with one of the keywords.

    Operates at clause level (commas / semicolons / em-dashes) within each
    sentence so unrelated numbers in the same sentence do not steal the
    association. Prefers the first number after the keyword; falls back to
    the nearest number before it if ``after_only`` is False.
    """
    best_value = default
    best_distance = float("inf")

    # Split into sentences, then clauses, so numbers stay bound to their clause.
    sentences = _SENTENCE_SPLIT_RE.split(text)
    for sentence in sentences:
        clauses = re.split(r'[,;]|\s*\u2013\s*|\s*\u2014\s*', sentence)
        for clause in clauses:
            if not clause.strip():
                continue
            clause_lower = clause.lower()
            for kw in keywords:
                words = kw.lower().split()
                if len(words) == 1:
                    positions = [m.start() for m in re.finditer(r'\b' + re.escape(words[0]) + r'\b', clause_lower)]
                else:
                    parts = [re.escape(w) for w in words]
                    pattern = r'\b' + r'\b[^,;]{0,40}\b'.join(parts) + r'\b'
                    positions = [m.start() for m in re.finditer(pattern, clause_lower)]

                for kw_start in positions:
                    nums = list(_NUMBER_TOKEN_RE.finditer(clause))
                    # Prefer first number after keyword.
                    for num in nums:
                        if num.start() > kw_start:
                            return _to_int(num.group(1))
                    if not after_only:
                        before = [n for n in nums if n.end() <= kw_start]
                        if before:
                            last = before[-1]
                            dist = kw_start - last.end()
                            if dist < best_distance:
                                best_distance = dist
                                best_value = _to_int(last.group(1))
    return best_value

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


def _unit_priority(unit: str, surrounding: str) -> int:
    """Return a priority for choosing the primary spec unit.

    Capacity/storage units (GB/TB) are preferred over frequency units when
    the surrounding context does not clearly indicate a clock/display spec.
    Frequency keywords lower the priority of Hz/GHz.
    """
    unit_lower = unit.lower()
    surr_lower = surrounding.lower()
    if unit_lower in ("gb", "tb"):
        return 30
    if unit_lower in ("mb", "kg", "km", "m", "mm", "cm", "inches"):
        return 20
    if unit_lower in ("ghz", "mhz"):
        if re.search(r"\b(processor|cpu|core|clock|speed)\b", surr_lower):
            return 5
        return 10
    if unit_lower == "hz":
        if re.search(r"\b(display|screen|refresh)\b", surr_lower):
            return 5
        return 10
    if unit_lower in ("v", "a", "w"):
        return 15
    return 10


def _preprocess_retail_text(text: str) -> str:
    """Rewrite common retail-page fragments into parser-friendly statements."""
    # "Ticket $1299 $849 $450 OFF" → explicit paid/advertised/discount.
    text = re.sub(
        r"Ticket\s*\$\s*(\d+)\s*\$\s*(\d+)\s*\$\s*(\d+)\s*OFF",
        r"ticket price paid \1 advertised price \2 discount \3 off",
        text, flags=re.IGNORECASE,
    )
    # "Add 2 years Extra Care ... Starts 12 months after" → extend base warranty, not 12-month base.
    text = re.sub(
        r"(?:Add\s+(\d+|one|two|three|four|five)\s+years?\s+)?Extra\s+Care.*?\$\s*\d+[.,]?\d*.*?Starts\s+\d+\s+months?\s+after",
        "",
        text, flags=re.IGNORECASE | re.DOTALL,
    )
    # "Manufacturer's warranty 1 Year" → normalize.
    text = re.sub(
        r"Manufacturer['']?s?\s+warranty\s+((\d+|one|two|three|four|five)\s*(?:months?|years?|yrs?))",
        r"base warranty \1",
        text, flags=re.IGNORECASE,
    )
    return text


def _find_warranty_months(text: str) -> Optional[float]:
    # "base warranty N" from preprocessor.
    m = re.search(
        r"base\s+warranty\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:months?|years?|yrs?)\b",
        text, re.IGNORECASE,
    )
    if m:
        val = float(_to_int(m.group(1)))
        unit = m.group(0).lower()
        if "year" in unit:
            val *= 12
        return val
    # Try explicit "warranty ... N months/years" first, including written numbers.
    m = re.search(
        r"warranty[^.!?]{0,40}?\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:months?|mos?|years?|yrs?)\b",
        text, re.IGNORECASE,
    )
    if m:
        val = float(_to_int(m.group(1)))
        unit = m.group(0).lower()
        if "year" in unit:
            val *= 12
        return val
    # Try "N months/years warranty" (number before keyword).
    m = re.search(
        r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:months?|mos?|years?|yrs?)\s*warranty\b",
        text, re.IGNORECASE,
    )
    if m:
        val = float(_to_int(m.group(1)))
        unit = m.group(0).lower()
        if "year" in unit:
            val *= 12
        return val
    return None


def _find_failure_months(text: str) -> Optional[float]:
    m = re.search(
        r"(?:failed|failure|broke|died|stopped)[^.!?]{0,40}?\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:months?|mos?|years?|yrs?|days?)\b",
        text, re.IGNORECASE,
    )
    if m:
        val = float(_to_int(m.group(1)))
        unit = m.group(0).lower()
        if "year" in unit:
            val *= 12
        elif "day" in unit:
            val /= 30.0
        return val
    return None


def extract_product_evidence(text: str) -> Optional[ParsedEvidence]:
    """Return a ParsedEvidence if the text has enough numeric product/service indicators."""
    if not text or len(text) < 40:
        return None

    lower = text.lower()
    triggers = ["price", "paid", "warranty", "spec", "model", "serial", "device", "product"]
    if not any(t in lower for t in triggers):
        return None

    text = _preprocess_retail_text(text)

    ev = ParsedEvidence()
    ev.product_name = _extract_product_name(text)

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
        surrounding = text[max(0, m.start() - 30):m.end() + 30]
        spec_hits.append(
            (val, unit, m.start(), m.end(), _classify_spec_value(text, m.start()), _unit_priority(unit, surrounding))
        )
    if spec_hits:
        # Use highest-priority unit as the primary spec. When priorities tie,
        # prefer claimed over measured over unknown.
        primary = max(
            spec_hits,
            key=lambda h: (h[5], 2 if h[4] == "claimed" else 1 if h[4] == "measured" else 0),
        )
        ev.spec_claimed_unit = primary[1].lower()
        claimed_candidates = [h for h in spec_hits if h[4] == "claimed"]
        measured_candidates = [h for h in spec_hits if h[4] == "measured"]
        if claimed_candidates and measured_candidates:
            ev.spec_claimed = claimed_candidates[0][0]
            ev.spec_measured = measured_candidates[0][0]
        elif measured_candidates:
            ev.spec_measured = measured_candidates[0][0]
            # Use the primary spec value as the claimed stand-in if no claimed spec.
            ev.spec_claimed = primary[0]
        elif claimed_candidates:
            ev.spec_claimed = claimed_candidates[0][0]
            ev.spec_measured = primary[0]
        else:
            # No classification; use primary value for both.
            ev.spec_claimed = primary[0]
            ev.spec_measured = primary[0]

    ev.warranty_months = _find_warranty_months(text)
    ev.months_to_failure = _find_failure_months(text)

    ev.known_issues = _find_number_near_keyword(
        text,
        ["issues", "reported issues", "reported problems", "complaints", "defects", "problems reported", "customers reported"],
        default=0,
    )
    ev.total_features_or_parts = _count_feature_bullets(text)

    ev.regulatory_requirements = _find_number_near_keyword(
        text,
        ["regulatory requirements", "regulatory standards", "requirements", "standards", "rules"],
        default=0,
    )
    ev.violations_found = _find_number_near_keyword(
        text,
        ["violation", "violations", "breaches", "non-compliance", "failures"],
        default=0,
    )

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


def _count_feature_bullets(text: str) -> int:
    """Count items under a 'Key Features' or similar bulleted section.

    Falls back to keyword-nearest-number if no bullets are found.
    """
    # Look for a section header followed by bullet lines.
    m = re.search(
        r"(?:Key\s+Features?|Features?|Highlights?|Includes?)[:\s]*\n((?:\s*[-•*]\s*[^\n]+\n|\s*\d+\.\s*[^\n]+\n|\s*[^\n]+\n){3,})",
        text, re.IGNORECASE,
    )
    if m:
        block = m.group(1)
        # Count lines that start with a bullet marker, digit, or non-empty content.
        count = len([line for line in block.splitlines() if re.match(r"^\s*(?:[-•*]|\d+\.)\s+\S", line)])
        if count >= 3:
            return count
    return _find_number_near_keyword(
        text,
        ["components", "parts", "features", "items", "ports"],
        default=0,
    )
