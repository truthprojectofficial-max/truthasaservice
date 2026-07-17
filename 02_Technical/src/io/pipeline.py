"""
End-to-end deterministic document audit pipeline.

Joins the deception scanner, BBFB engine, and ACL demand generator.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .extractors import extract_text, is_supported_input
from .evidence_parser import extract_product_evidence
from .report_writer import DocumentAuditReport, write_report

from src.engines.deception_scanner import audit_text
from src.engines.bbfb_engine import calculate_bbfb
from src.engines.acl_demand_generator import generate_acl_demand
from src.types import ProductEvidence


@dataclass
class PipelineResult:
    input_path: Path
    output_paths: List[Path] = field(default_factory=list)
    status: str = "pending"
    error: Optional[str] = None
    report: Optional[DocumentAuditReport] = None


# Global eject flag checked between files in a batch
EJECT_REQUESTED = False


def request_eject() -> None:
    """Set the global eject flag; in-flight batches stop after the current file."""
    global EJECT_REQUESTED
    EJECT_REQUESTED = True


def clear_eject() -> None:
    """Clear the global eject flag before a new batch run."""
    global EJECT_REQUESTED
    EJECT_REQUESTED = False


def _to_dict(obj) -> dict:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    return obj


def _base_name(path: Path) -> str:
    name = re.sub(r"[^\w\-]", "_", path.stem)
    return name.strip("_") or "audit_report"


def _has_product_evidence(text: str) -> bool:
    lower = text.lower()
    triggers = ["price", "paid", "warranty", "spec", "measured", "rated", "model", "serial", "failure", "violation"]
    return any(t in lower for t in triggers)


def process_file(
    input_path: Path,
    outbox_dir: Path,
    formats: Optional[List[str]] = None,
) -> PipelineResult:
    """Process a single document through the full audit pipeline."""
    result = PipelineResult(input_path=input_path)
    if not input_path.exists():
        result.status = "error"
        result.error = f"File not found: {input_path}"
        return result

    try:
        text = extract_text(input_path)
    except Exception as exc:
        result.status = "error"
        result.error = f"Extraction failed: {exc}"
        return result

    if len(text.strip()) == 0:
        result.status = "warning"
        result.error = "No extractable text found in document."
        return result

    deception_report = audit_text(text)
    dr_dict = _to_dict(deception_report)
    warnings: List[str] = []

    bbfb_dict = None
    if _has_product_evidence(text):
        parsed = extract_product_evidence(text)
        if parsed and parsed.confidence in ("medium", "high"):
            evidence = ProductEvidence(
                productName=parsed.product_name or input_path.stem,
                pricePaid=parsed.price_paid or 0.0,
                priceAdvertised=parsed.price_advertised or 0.0,
                specClaimed=parsed.spec_claimed or 0.0,
                specClaimedUnit=parsed.spec_claimed_unit or "",
                specMeasured=parsed.spec_measured or 0.0,
                warrantyMonths=parsed.warranty_months or 0.0,
                monthsToFailure=parsed.months_to_failure or 0.0,
                knownIssues=float(parsed.known_issues),
                totalFeaturesOrParts=float(parsed.total_features_or_parts or 1),
                regulatoryRequirements=float(parsed.regulatory_requirements or 1),
                violationsFound=float(parsed.violations_found),
                notes=(
                    f"Heuristic parse confidence: {parsed.confidence}; "
                    f"hits: {', '.join(parsed.raw_hits)}"
                ),
            )
            bbfb_result = calculate_bbfb(evidence)
            bbfb_dict = _to_dict(bbfb_result)
        else:
            warnings.append("Product-like terms found but insufficient structured evidence for BBFB evaluation.")

    acl_demand = None
    deception_prob = dr_dict.get("deceptionProbability", 0.0)
    structural = dr_dict.get("structuralDeceptionFlag", False)
    bbfb_noncompliant = bbfb_dict and not bbfb_dict.get("overallCompliant", True)
    if structural and (bbfb_noncompliant or (bbfb_dict is None and deception_prob > 0.75)):
        acl_demand = generate_acl_demand(
            invoice_spec="Invoice / described specification",
            hardware_id="Delivered / measured specification",
            deception_report=deception_report,
            consumer_name="[Consumer Name]",
            supplier_name="[Supplier Name]",
            bbfb_score=bbfb_dict,
        )

    report = DocumentAuditReport(
        filename=input_path.name,
        extracted_text=text[:1000],
        text_length=len(text),
        deception_report=dr_dict,
        bbfb_report=bbfb_dict,
        acl_demand=acl_demand,
        warnings=warnings,
    )

    base_name = _base_name(input_path)
    out_paths = write_report(report, outbox_dir, base_name, formats)

    result.report = report
    result.output_paths = out_paths
    result.status = "success"
    return result


def process_directory(
    inbox_dir: Path,
    outbox_dir: Path,
    formats: Optional[List[str]] = None,
) -> List[PipelineResult]:
    """Process every supported document in the inbox directory."""
    results: List[PipelineResult] = []
    if not inbox_dir.exists():
        return [PipelineResult(input_path=inbox_dir, status="error", error=f"Inbox not found: {inbox_dir}")]

    files = sorted(p for p in inbox_dir.iterdir() if p.is_file() and is_supported_input(p))
    for file_path in files:
        if EJECT_REQUESTED:
            results.append(PipelineResult(input_path=file_path, status="ejected"))
            break
        results.append(process_file(file_path, outbox_dir, formats))
    return results
