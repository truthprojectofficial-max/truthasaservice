"""
Form_Entry_Agent -- the intake + research role.

The third party hands the agent a payload. The agent's job is to:
  1. Take whatever was handed in (text, document, question) and
     turn it into a DraftFact with a URN.
  2. If the payload is a research request, hunt through the build
     folder and the reference folder for the relevant material.
  3. If the payload is a test request, prepare the test harness.
  4. If the payload is a real-world business deal, normalize the
     numbers into ProductEvidence so the Lattice_Compute_Agent can
     run.

The agent does not call any LLM. It uses deterministic string
matching, file walking, and the URN bus. The "research" is a
filesystem search with a clear inclusion/exclusion rule.
"""
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.constants import PROJECT_ROOT, PROJECT_OPERATOR


@dataclass
class DraftFact:
    fact_id: Optional[int]
    category: str
    statement: str
    source: str
    urn: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class FormEntryAgent:
    """The third-party intake role. Deterministic. No LLM."""
    VALID_CATEGORIES = {"Technical", "Governance", "Forensic"}

    def __init__(self, root: Path = PROJECT_ROOT) -> None:
        self.root = Path(root)
        self.operator = PROJECT_OPERATOR

    def draft_fact(self, category: str, statement: str, source: str = "operator") -> DraftFact:
        if category not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category {category!r}. Must be one of: {sorted(self.VALID_CATEGORIES)}")
        if not statement or not statement.strip():
            raise ValueError("statement cannot be empty")
        return DraftFact(
            fact_id=None,
            category=category,
            statement=statement[:1000],
            source=source,
            urn="OGIR:02:FORM_ENTRY",
        )

    DEFAULT_RESEARCH_ROOTS = ["00_Strategy", "01_Methodology", "02_Technical", "docs"]

    def research(self, query: str, roots: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []
        roots = roots or self.DEFAULT_RESEARCH_ROOTS
        terms = [t.lower() for t in re.split(r"\s+", query.strip()) if t]
        if not terms:
            return []
        hits: List[Dict[str, Any]] = []
        for root_name in roots:
            root_path = self.root / root_name
            if not root_path.exists():
                continue
            for path in root_path.rglob("*"):
                if not path.is_file():
                    continue
                if path.suffix not in {".py", ".md", ".txt", ".json", ".yml", ".yaml", ".ps1", ".sh"}:
                    continue
                if "__pycache__" in path.parts or ".pytest_cache" in path.parts:
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except (OSError, UnicodeDecodeError):
                    continue
                for lineno, line in enumerate(text.splitlines(), start=1):
                    lowered = line.lower()
                    if all(t in lowered for t in terms):
                        hits.append({
                            "file": str(path.relative_to(self.root)),
                            "line": lineno,
                            "text": line.strip()[:300],
                        })
                        if len(hits) >= 200:
                            return hits
        return hits

    def normalize_real_world_claim(self, raw: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "productName": "",
            "pricePaid": 0.0,
            "priceAdvertised": 0.0,
            "specClaimed": 0.0,
            "specClaimedUnit": "",
            "specMeasured": 0.0,
            "warrantyMonths": 0.0,
            "monthsToFailure": 0.0,
            "knownIssues": 0.0,
            "totalFeaturesOrParts": 0.0,
            "regulatoryRequirements": 0.0,
            "violationsFound": 0.0,
            "notes": raw[:1000],
            "gaps": [],
        }

        # --- productName --------------------------------------------------
        # Prefer an explicit "model|product|device|item" prefix. Fall back
        # to the leading 1-4 word run before the first $ or numeric field
        # -- the deterministic, opinion-free version of "look at the
        # start of the line" the third party asked for.
        m = re.search(
            r"(?:model|product|device|item)[\s:]+([^\n,.$\d][^\n,.$\d][^\n,.$]{0,58})",
            raw,
            re.IGNORECASE,
        )
        if m:
            result["productName"] = m.group(1).strip()
        else:
            head = re.match(
                r"\s*((?:[A-Za-z][A-Za-z0-9\-]*\s+){0,3}[A-Za-z][A-Za-z0-9\-]*)",
                raw,
            )
            if head:
                candidate = head.group(1).strip()
                if candidate.lower() not in {"the", "a", "an", "we", "i", "it", "this", "that"}:
                    result["productName"] = candidate
        if not result["productName"]:
            result["gaps"].append("no product name found")

        # --- prices -------------------------------------------------------
        # Accept "$599" or "paid 599" / "advertised 599" syntax.
        prices = [float(x) for x in re.findall(r"\$\s*(\d+(?:\.\d{2})?)", raw)]
        if not prices:
            paid = re.search(r"\bpaid\s+(\d+(?:\.\d{2})?)", raw, re.IGNORECASE)
            advertised = re.search(
                r"\b(?:advertised|listed|msrp|rrp|asking)\s+(\d+(?:\.\d{2})?)",
                raw,
                re.IGNORECASE,
            )
            if paid:
                result["pricePaid"] = float(paid.group(1))
            if advertised:
                result["priceAdvertised"] = float(advertised.group(1))
            elif paid and not advertised:
                result["priceAdvertised"] = result["pricePaid"]
        else:
            result["pricePaid"] = prices[0]
            result["priceAdvertised"] = prices[-1] if len(prices) > 1 else prices[0]
        if result["pricePaid"] == 0.0 and result["priceAdvertised"] == 0.0:
            result["gaps"].append("no price found")

        # --- specs --------------------------------------------------------
        # "rated X" is the *claimed* spec, "measured X" is the measured
        # spec. The keyword disambiguates, which is what the third party
        # found missing in the prior build.
        spec_unit = r"(dB|hz|v|w|gb|mb|ghz|kg|mm|cm)"
        measured = re.search(
            r"measured\s+(\d+(?:\.\d+)?)\s*" + spec_unit,
            raw,
            re.IGNORECASE,
        )
        rated = re.search(
            r"\brated\s+(\d+(?:\.\d+)?)\s*" + spec_unit,
            raw,
            re.IGNORECASE,
        )
        if not rated:
            rated = re.search(
                r"\b(?:advertised|claimed|stated|promised|nominal)\s+(\d+(?:\.\d+)?)\s*"
                + spec_unit,
                raw,
                re.IGNORECASE,
            )
        unit_used = ""
        if measured:
            result["specMeasured"] = float(measured.group(1))
            unit_used = measured.group(2).lower()
        if rated:
            result["specClaimed"] = float(rated.group(1))
            unit_used = rated.group(2).lower()
        elif measured and not rated:
            # No explicit "rated" claim: measured value is also the claim.
            result["specClaimed"] = result["specMeasured"]
        if unit_used:
            result["specClaimedUnit"] = unit_used
        else:
            spec_match = re.search(r"(\d+(?:\.\d+)?)\s*" + spec_unit, raw, re.IGNORECASE)
            if spec_match:
                result["specMeasured"] = float(spec_match.group(1))
                result["specClaimed"] = result["specMeasured"]
                result["specClaimedUnit"] = spec_match.group(2).lower()
            else:
                result["gaps"].append("no spec found")

        # --- warranty -----------------------------------------------------
        warr = re.search(
            r"warranty[^\d]*(\d+)\s*(months?|mos?|years?|yrs?)",
            raw,
            re.IGNORECASE,
        )
        if warr:
            n = float(warr.group(1))
            unit = warr.group(2).lower()
            if unit.startswith("y"):
                n *= 12.0
            result["warrantyMonths"] = n
        else:
            result["gaps"].append("no warranty found")

        # --- months to failure -------------------------------------------
        fail = re.search(
            r"(?:failed|broke|died|stopped|conked)[^\d]*(\d+)\s*(months?|days?)",
            raw,
            re.IGNORECASE,
        )
        if fail:
            n = float(fail.group(1))
            unit = fail.group(2).lower()
            if unit.startswith("d"):
                n /= 30.0
            result["monthsToFailure"] = n
        else:
            result["gaps"].append("no failure time found")

        # --- count fields -------------------------------------------------
        # "3 issues", "12 features", "1 violation", "4 requirements".
        # "out of N" syntax splits the numerator from the denominator
        # cleanly when both appear in the same sentence.
        issues = re.search(r"(\d+)\s+(?:known\s+)?issues?\b", raw, re.IGNORECASE)
        if issues:
            result["knownIssues"] = float(issues.group(1))
        else:
            result["gaps"].append("no known issues found")

        feat = re.search(
            r"(\d+)\s+(?:of\s+\d+\s+)?features?(?:\s+or\s+parts?)?",
            raw,
            re.IGNORECASE,
        )
        if feat:
            result["totalFeaturesOrParts"] = float(feat.group(1))

        vio = re.search(r"(\d+)\s+violations?\b", raw, re.IGNORECASE)
        if vio:
            result["violationsFound"] = float(vio.group(1))

        req = re.search(
            r"(\d+)\s+(?:regulatory\s+)?requirements?\b",
            raw,
            re.IGNORECASE,
        )
        if req:
            result["regulatoryRequirements"] = float(req.group(1))

        # De-duplicate gaps while preserving insertion order.
        seen = set()
        deduped: List[str] = []
        for g in result["gaps"]:
            if g not in seen:
                deduped.append(g)
                seen.add(g)
        result["gaps"] = deduped
        return result

