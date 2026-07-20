"""
Order Get It Right -- indicate/suggest who needs this, per decision rail.

Runs the five decision rails and, for each, prints the stakeholders who
need that specific outcome. Code only -- the output is the answer.

Run:  python who_needs_this.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.agents.orchestrator import Orchestrator
from src.types import ProductEvidence


# Decision rail -> the stakeholders who need that outcome.
WHO = {
    "REFUSED": [
        "Regulator / fair-trading officer -- needs a fast, auditable refusal of a deceptive seller statement.",
        "Marketplace trust & safety team -- needs evidence-backed takedown of a listing, not a gut call.",
        "Consumer advocate -- needs a sealed record proving the refusal was structural, not arbitrary.",
    ],
    "REJECT": [
        "Consumer seeking a remedy -- needs a substantiated 'not of acceptable quality' finding (ACL s.260-style) to take to the seller or tribunal.",
        "Tribunal/ADR officer -- needs a deterministic, reproducible non-compliance report, not a subjective opinion.",
        "Seller compliance team -- needs a defensible internal flag that a product line is causing economic harm.",
    ],
    "TEST FIRST": [
        "Test lab / standards body -- needs a prioritised queue of borderline products to bench-test before any claim is paid.",
        "Procurement / category buyer -- needs a gate that says 'do not settle until tested' on a marginal product.",
        "Insurer / warranty underwriter -- needs a triage signal on which claims to investigate before paying out.",
    ],
    "REVIEW REQUIRED": [
        "Senior reviewer / case officer -- needs a queue of deception-flagged but not structural-refusal cases for human judgement.",
        "Legal counsel -- needs the sealed deception score and entropy to decide whether to escalate or settle.",
        "Quality lead -- needs the pattern set (DD-xxx) that fired, to feed back into product/claim fixes.",
    ],
    "GO": [
        "Seller / manufacturer -- needs a sealed clean bill to defend against a vexatious claim.",
        "Consumer redress scheme -- needs a pass signal to close a compliant-product dispute quickly.",
        "Regulator -- needs a baseline of 'this product clears both the deception and economic-harm gates'.",
    ],
}


def run_case(label, statement, evidence):
    core = Orchestrator()
    result = core.process_input(category="Technical", statement=statement, product_evidence=evidence)
    core.shutdown()
    action = result["finalAction"]
    print("=" * 72)
    print(f"RAIL: {label}")
    print(f"  finalAction : {action}")
    print(f"  reason       : {result['reason']}")
    dg = result["deceptionGate"]
    print(f"  deception    : score={dg['score']} verdict={dg['verdict']} patterns={dg['patternsMatched']}")
    og = result["optionalityGate"]
    print(f"  optionality  : {og['decision']} ({og['totalValue']} vs {og['threshold']})")
    bbfb = result.get("bbfbGate")
    bb = bbfb["overallCompliant"] if isinstance(bbfb, dict) else None
    print(f"  bbfb         : compliant={bb}")
    print(f"  ledgerRoot   : {result['ledgerRoot']}")
    print("-" * 72)
    print("WHO NEEDS THIS (this decision rail):")
    for who in WHO.get(action, ["(no mapping for this action)"]):
        print(f"  - {who}")
    print()
    return result


def main():
    print("=" * 72)
    print("INDICATE / SUGGEST WHO NEEDS THIS -- by decision rail")
    print("=" * 72)
    print("Each rail is run on a real product. The output names the stakeholders")
    print("who need that specific outcome. Code only -- the output is the answer.")
    print()

    # RAIL 1: REFUSED -- deceptive seller statement (CRITICAL pattern).
    run_case(
        "REFUSED (deceptive statement, structural refusal)",
        "The product is 100% accurate and has never failed. We provide full replacement as a courtesy to all customers.",
        ProductEvidence(productName="Demo Widget", pricePaid=599, priceAdvertised=599,
            specClaimed=106, specClaimedUnit="dB", specMeasured=106, warrantyMonths=24,
            monthsToFailure=24, knownIssues=0, totalFeaturesOrParts=12,
            regulatoryRequirements=4, violationsFound=0, notes="deceptive demo"),
    )

    # RAIL 2: REJECT -- clean statement, non-compliant product.
    run_case(
        "REJECT (clean statement, non-compliant product)",
        "The widget performs as described and meets all advertised claims. There have been no material complaints about this batch.",
        ProductEvidence(productName="Bad Widget", pricePaid=599, priceAdvertised=599,
            specClaimed=106, specClaimedUnit="dB", specMeasured=70, warrantyMonths=24,
            monthsToFailure=6, knownIssues=4, totalFeaturesOrParts=12,
            regulatoryRequirements=4, violationsFound=3, notes="bad batch"),
    )

    # RAIL 3: TEST FIRST -- clean statement, compliant but marginal.
    run_case(
        "TEST FIRST (clean, compliant, low optionality)",
        "The product meets the advertised specification of 106 dB. We have had no reported failures in normal use.",
        ProductEvidence(productName="Clean Widget", pricePaid=599, priceAdvertised=599,
            specClaimed=106, specClaimedUnit="dB", specMeasured=104, warrantyMonths=24,
            monthsToFailure=24, knownIssues=0, totalFeaturesOrParts=12,
            regulatoryRequirements=4, violationsFound=0, notes="clean marginal"),
    )

    # RAIL 4: REVIEW REQUIRED -- mild deception flag, not structural refusal.
    run_case(
        "REVIEW REQUIRED (mild deception flag)",
        "The product basically works fine and most customers are happy with it overall.",
        ProductEvidence(productName="Vague Widget", pricePaid=599, priceAdvertised=599,
            specClaimed=106, specClaimedUnit="dB", specMeasured=104, warrantyMonths=24,
            monthsToFailure=24, knownIssues=0, totalFeaturesOrParts=12,
            regulatoryRequirements=4, violationsFound=0, notes="vague hedging language"),
    )

    # RAIL 5: GO -- high-price, high-spec, clean product (attempt to clear both gates).
    run_case(
        "GO (attempt: high-price clean compliant product)",
        "The equipment meets the published specification of 112 dB and has passed all regulatory testing. No failures have been reported across the installed base.",
        ProductEvidence(productName="Premium Amp", pricePaid=4999, priceAdvertised=4999,
            specClaimed=112, specClaimedUnit="dB", specMeasured=112, warrantyMonths=60,
            monthsToFailure=60, knownIssues=0, totalFeaturesOrParts=24,
            regulatoryRequirements=6, violationsFound=0, notes="premium clean"),
    )


if __name__ == "__main__":
    main()