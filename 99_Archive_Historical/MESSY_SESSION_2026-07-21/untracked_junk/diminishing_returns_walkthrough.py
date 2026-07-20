"""
Order Get It Right -- diminishing-returns sweep + end-to-end run + walkthrough.

Single script that:
  1. Sweeps specMeasured to find the point of diminished return (the last
     spec that still clears the lattice strike line = GO, vs the first that
     falls under it = DEFER).
  2. Runs the full agent chain as one on a realistic case built at the
     failure-point spec.
  3. Prints a plain-English walkthrough of the naming/procedure and the
     sealed trail.

Run:  python diminishing_returns_walkthrough.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.agents.orchestrator import Orchestrator
from src.engines import real_options_lattice as rol
from src.types import ProductEvidence


def main() -> None:
    PRICE = 599
    NAME = "Audio Pro W-Generation"
    BASE = dict(
        productName=NAME, pricePaid=PRICE, priceAdvertised=PRICE,
        specClaimed=106, specClaimedUnit="dB", warrantyMonths=24,
        monthsToFailure=24, knownIssues=0, totalFeaturesOrParts=12,
        regulatoryRequirements=4, violationsFound=0, notes="",
    )

    print("=" * 72)
    print("PHASE 1 - POINT OF DIMINISHED RETURNS SWEEP")
    print("=" * 72)
    print(f"Product: {NAME} | pricePaid={PRICE} | specClaimed=106 dB")
    print("Sweep specMeasured 106 -> 80, deception=0, entropy=4.0 (clean text).")
    print("The threshold is the lattice strike line. The point where the")
    print("optionality index crosses BELOW threshold is the point of diminished return.")
    print("-" * 72)

    for spec in (106, 100, 95, 90, 88, 86, 85, 84, 83, 80):
        ev = ProductEvidence(specMeasured=spec, **BASE)
        d = rol.derive_lattice_inputs_from_evidence(ev)
        val = rol.hardened_compound_binomial_gate(0.0, 4.0, evidence=ev)
        print(
            f"specMeasured={spec:3d} dB | s0={d['s0']:.2f} k1={d['k1']:.2f} "
            f"sig1={d['sigma1']:.4f} | optionality={val.totalValue:7.4f} "
            f"threshold={val.threshold:7.4f} -> {val.decision}"
        )

    print("-" * 72)
    boundary = None
    for spec in range(106, 80, -1):
        ev = ProductEvidence(specMeasured=spec, **BASE)
        val = rol.hardened_compound_binomial_gate(0.0, 4.0, evidence=ev)
        if val.decision == "DEFER":
            boundary = spec + 1
            break
    print(f"FINE SWEEP: last GO at specMeasured={boundary} dB; first DEFER at {boundary - 1} dB.")
    print(f"POINT OF DIMINISHED RETURN = {boundary} dB.")
    print("Above this, more spec buys more optionality (GO). Below it, the")
    print("compound option falls under the strike line (DEFER) -- the marginal")
    print("return on pursuing the claim has gone negative.")
    print()
    _phase_two(BASE, boundary)


def _phase_two(BASE, boundary):
    CASE_SPEC = boundary - 1
    print("=" * 72)
    print("PHASE 2 - RUN AS ONE (full agent chain on the failure-point product)")
    print("=" * 72)
    print(f"Case product: {BASE['productName']}, specMeasured={CASE_SPEC} dB (under claim),")
    print("failed at 18 mo, 2 known issues, 1 regulatory violation.")
    print("Statement: a clean, factual buyer complaint (no deception patterns).")
    print("-" * 72)

    core = Orchestrator()
    case_ev = ProductEvidence(
        productName=BASE["productName"], pricePaid=BASE["pricePaid"],
        priceAdvertised=BASE["priceAdvertised"], specClaimed=BASE["specClaimed"],
        specClaimedUnit=BASE["specClaimedUnit"], specMeasured=CASE_SPEC,
        warrantyMonths=24, monthsToFailure=18, knownIssues=2,
        totalFeaturesOrParts=12, regulatoryRequirements=4, violationsFound=1,
        notes="Buyer reports speaker under spec, failed early, issues present.",
    )
    STATEMENT = (
        "I purchased the Audio Pro W-Generation speaker advertised at 106 dB. "
        "After eighteen months the unit stopped outputting sound. My measurement "
        f"shows {CASE_SPEC} dB, not 106 dB. Two features do not work and one "
        "regulatory marking is missing. I am seeking a remedy under the consumer guarantee."
    )
    result = core.process_input(category="Technical", statement=STATEMENT, product_evidence=case_ev)
    core.shutdown()
    _print_result(result)
    _walkthrough(result)


def _print_result(result):
    bbfb = result.get("bbfbGate")
    bbfb_compliant = bbfb["overallCompliant"] if isinstance(bbfb, dict) else None
    print("Full chain result (key fields):")
    print(json.dumps({
        "factId": result.get("factId"),
        "systemId": result.get("systemId"),
        "operator": result.get("operator"),
        "deceptionGate": result.get("deceptionGate"),
        "optionalityGate": result.get("optionalityGate"),
        "bbfbCompliant": bbfb_compliant,
        "finalAction": result.get("finalAction"),
        "reason": result.get("reason"),
        "ledgerRoot": result.get("ledgerRoot"),
    }, indent=2, default=str))
    print()


def _walkthrough(result):
    dg = result["deceptionGate"]
    og = result["optionalityGate"]
    bbfb = result.get("bbfbGate")
    bbfb_compliant = bbfb["overallCompliant"] if isinstance(bbfb, dict) else None
    bbfb_word = "compliant" if bbfb_compliant else "NON-compliant"
    print("=" * 72)
    print("PHASE 3 - PLAIN-ENGLISH WALKTHROUGH: naming + procedure on this product")
    print("=" * 72)
    print(
        f"\n1. NAMING THE PRODUCT (URN + fact id)\n"
        f"   - System: {result['systemId']}\n"
        f"   - Operator on the chain: {result['operator']}\n"
        f"   - The product enters the ledger under a fact id. For this case the\n"
        f"     fact id is {result['factId']}. That id is the name the chain will\n"
        f"     use for this dispute from here on -- every later block that\n"
        f"     references it cites this id, not the product description.\n"
        f"   - The work the agents do is labelled by URN, format OGIR:<SPACE>:<ACTION>.\n"
        f"     The spaces are 01 (lattice/compute), 02 (form + audit), 03 (seal),\n"
        f"     04 (affidavit). So the hand-offs in this run were:\n"
        f"       * OGIR:02:FORM_ENTRY      -- Form_Entry_Agent drafted the fact\n"
        f"       * OGIR:02:AUDIT_TEXT      -- Audit_Review_Agent scanned the statement\n"
        f"       * OGIR:01:COMPUTE_LATTICE -- Lattice_Compute_Agent priced the option\n"
        f"       * OGIR:03:SEAL_FACT       -- Ledger_Seal_Agent sealed the cycle\n"
        f"\n2. WHAT EACH GATE SAID ABOUT THIS PRODUCT\n"
        f"   - Deception gate: score {dg['score']}, verdict {dg['verdict']},\n"
        f"     {dg['patternsMatched']} pattern(s) fired. The buyer's statement was\n"
        f"     straight, so the cycle was allowed to proceed (no structural refusal).\n"
        f"   - Optionality gate (the diminishing-return engine): the compound\n"
        f"     optionality index came out {og['totalValue']} against a strike\n"
        f"     threshold of {og['threshold']}. Decision: {og['decision']}.\n"
        f"     That number is the real-options value of pursuing/escalating the\n"
        f"     claim, with volatility pushed up by any deception and entropy in the\n"
        f"     statement. It is NOT a business valuation -- it is a deception-adjusted\n"
        f"     optionality index (the framing line baked into every output).\n"
        f"   - BBFB gate: {bbfb_word}.\n"
        f"\n3. THE FINAL ACTION THE CHAIN TOOK\n"
        f"   - finalAction: {result['finalAction']}\n"
        f"   - reason: {result['reason']}\n"
        f"   - This is the decision an operator would act on: GO, TEST FIRST,\n"
        f"     REVIEW_REQUIRED, REJECT, or REFUSED. For this product the chain\n"
        f"     landed on {result['finalAction']}.\n"
        f"\n4. THE TRAIL (why the decision is provable later)\n"
        f"   - The whole cycle was sealed to the Merkle chain. The current ledger\n"
        f"     root after this run is:\n"
        f"       {result['ledgerRoot']}\n"
        f"   - Every block in the vault re-derives to that root. The fact id, the\n"
        f"     deception score, the verdict, the BBFB flag, and the optionality\n"
        f"     decision are all in the sealed AUDIT_CYCLE_COMPLETE block. Nothing\n"
        f"     about this decision can be changed silently after the fact.\n"
        f"   - If this ever goes to a Section 177 affidavit, the Affidavit_Agent\n"
        f"     (space 04) compiles the exhibit from this exact chain -- the root\n"
        f"     and the block hashes become the sworn anchors.\n"
    )
    print("=" * 72)
    print("END TO END: diminishing return found -> case run -> trail sealed.")
    print("=" * 72)


if __name__ == "__main__":
    main()