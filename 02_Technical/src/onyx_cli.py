"""
Order Get It Right -- Onyx CLI

The third-party Onyx surface. Another agent can call this CLI to
submit a URN, poll for completion, and re-derive the verdict.

Usage:
    python -m src.onyx_cli audit --text "I apologize for the confusion."
    python -m src.onyx_cli seal --event JOB_QUEUED --data '{"agent": "A"}'
    python -m src.onyx_cli verify
    python -m src.onyx_cli affidavit
    python -m src.onyx_cli research --query "Tau firewall"
    python -m src.onyx_cli hunt --statement "We are air-gapped."
    python -m src.onyx_cli normalize --text "Audio Pro W-Gen $599..."
    python -m src.onyx_cli compute --evidence '{"productName": ...}'
    python -m src.onyx_cli compare-to-spec
    python -m src.onyx_cli draft --category Governance --statement "..."
    python -m src.onyx_cli ledger

The Onyx CLI is the only thing a third party needs to know about.
The internal agents are implementation detail.
"""
import argparse
import json
import sys

from src.agents.form_entry_agent import FormEntryAgent
from src.agents.audit_review_agent import AuditReviewAgent
from src.agents.lattice_compute_agent import LatticeComputeAgent
from src.agents.ledger_seal_agent import LedgerSealAgent
from src.agents.affidavit_agent import AffidavitAgent


def cmd_audit(args) -> int:
    agent = AuditReviewAgent()
    verdict = agent.audit(args.text, context=args.context)
    print(json.dumps({
        "state": verdict.state,
        "reason": verdict.reason,
        "deceptionProbability": verdict.deception_probability,
        "patternsFired": verdict.patterns_fired,
        "timestamp": verdict.timestamp,
    }, indent=2))
    return 0


def cmd_seal(args) -> int:
    agent = LedgerSealAgent()
    data = json.loads(args.data)
    block = agent.seal_fact(args.event, data)
    print(json.dumps(block, indent=2))
    return 0


def cmd_verify(args) -> int:
    agent = LedgerSealAgent()
    result = agent.verify_root()
    print(json.dumps(result, indent=2))
    return 0 if result["matches"] else 1


def cmd_affidavit(args) -> int:
    agent = AffidavitAgent()
    print(agent.compile_affidavit())
    return 0


def cmd_research(args) -> int:
    agent = FormEntryAgent()
    hits = agent.research(args.query)
    print(json.dumps(hits, indent=2))
    return 0


def cmd_hunt(args) -> int:
    agent = AuditReviewAgent()
    contradictions = agent.hunt(args.statement)
    print(json.dumps(contradictions, indent=2))
    return 0


def cmd_normalize(args) -> int:
    agent = FormEntryAgent()
    result = agent.normalize_real_world_claim(args.text)
    print(json.dumps(result, indent=2))
    return 0


def cmd_compute(args) -> int:
    from src.types import ProductEvidence
    agent = LatticeComputeAgent()
    data = json.loads(args.evidence)
    evidence = ProductEvidence(**data)
    verdict = agent.compute_bbfb(evidence)
    print(json.dumps({
        "bbfbCompliant": verdict.bbfb_compliant,
        "bbfbCvs": verdict.bbfb_cvs,
        "bbfbGraceRisk": verdict.bbfb_grace_risk,
        "valuationDecision": verdict.valuation_decision,
        "valuationTotal": verdict.valuation_total,
        "summary": verdict.summary,
        "timestamp": verdict.timestamp,
    }, indent=2))
    return 0


def cmd_compare_to_spec(args) -> int:
    agent = AffidavitAgent()
    disagreements = agent.compare_to_spec()
    print(json.dumps(disagreements, indent=2))
    return 0


def cmd_draft(args) -> int:
    agent = FormEntryAgent()
    fact = agent.draft_fact(args.category, args.statement, args.source)
    print(json.dumps({
        "category": fact.category,
        "statement": fact.statement,
        "source": fact.source,
        "urn": fact.urn,
        "timestamp": fact.timestamp,
    }, indent=2))
    return 0


def cmd_ledger(args) -> int:
    agent = LedgerSealAgent()
    stats = agent.stats()
    print(json.dumps(stats, indent=2))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="onyx",
        description="Order Get It Right -- Onyx third-party surface",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("audit", help="Run the 54-pattern deception scan")
    p.add_argument("--text", required=True)
    p.add_argument("--context")

    p = sub.add_parser("seal", help="Seal a fact to the Merkle chain")
    p.add_argument("--event", required=True)
    p.add_argument("--data", required=True, help="JSON string")

    p = sub.add_parser("verify", help="Re-derive the Merkle root")

    p = sub.add_parser("affidavit", help="Compile a Section 177 certificate")

    p = sub.add_parser("research", help="Walk the build folder for a query")
    p.add_argument("--query", required=True)

    p = sub.add_parser("hunt", help="Hunt for code that contradicts a statement")
    p.add_argument("--statement", required=True)

    p = sub.add_parser("normalize", help="Normalize a real-world business claim")
    p.add_argument("--text", required=True)

    p = sub.add_parser("compute", help="Run the BBFB engine on product evidence")
    p.add_argument("--evidence", required=True, help="JSON string")

    p = sub.add_parser("compare-to-spec", help="Find code/spec disagreements")

    p = sub.add_parser("draft", help="Draft a fact from an operator input")
    p.add_argument("--category", required=True)
    p.add_argument("--statement", required=True)
    p.add_argument("--source", default="operator")

    p = sub.add_parser("ledger", help="Show Merkle chain stats")

    args = parser.parse_args(argv)
    dispatch = {
        "audit": cmd_audit,
        "seal": cmd_seal,
        "verify": cmd_verify,
        "affidavit": cmd_affidavit,
        "research": cmd_research,
        "hunt": cmd_hunt,
        "normalize": cmd_normalize,
        "compute": cmd_compute,
        "compare-to-spec": cmd_compare_to_spec,
        "draft": cmd_draft,
        "ledger": cmd_ledger,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
