"""
Order Get It Right -- Agent Orchestrator

The single runtime entry point that drives the agent chain.  Agents do
not call each other directly.  All hand-offs go through the job
delegator.  The orchestrator is the operator-facing surface.

Orchestrator-driven hand-off chain (deterministic, no LLM):
  - Form_Entry_Agent       (01)
  - Audit_Review_Agent     (02)  -- 54-pattern deception scan
  - Lattice_Compute_Agent  (01)  -- Real-Options binomial lattice
  - Ledger_Seal_Agent      (03)  -- Merkle seal to the vault

The orchestrator also touches Affidavit_Agent (04) when the operator
requests a Section 177 certificate, but the affidavit is generated
on-demand from the existing chain rather than as part of the per-input
hand-off sequence.

Siblings of the orchestrator under src/agents/ (10 named modules in
total, all deterministic and no-LLM):
  - 5 hand-off / seal agents: Form_Entry_Agent, Audit_Review_Agent,
    Lattice_Compute_Agent, Ledger_Seal_Agent, Affidavit_Agent
  - InventoryAgent, MonitorAgent -- domain-specific scanners
  - Orchestrator -- this module, the operator-facing entry point
  - AgentJobDelegator -- the MCP bridge; every hand-off is a job token
  - TauFirewall -- enforces the 10% extraction ceiling and issues
    STRUCTURAL_REFUSAL on hit

URN format: OGIR:<SPACE>:<ACTION>
"""
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from config.constants import (
    PROJECT_NAME,
    PROJECT_VERSION,
    PROJECT_OPERATOR,
    PROJECT_VAULT_DIR,
    DECEPTION_ONTOLOGY_VERSION,
)
from src.types import ProductEvidence, DeceptionReport
from src.engines import deception_scanner, bbfb_engine, real_options_lattice
from src.engines import facts_registry
from src.io import vault_io
from src.agents import tau_firewall, job_delegator


class Orchestrator:
    """The single runtime entry point.  Owns the delegator and the firewall."""

    def __init__(self) -> None:
        self.system_id = f"{PROJECT_NAME} v{PROJECT_VERSION}"
        self.operator = PROJECT_OPERATOR
        self.tau = tau_firewall.TauFirewall()
        self.delegator = job_delegator.AgentJobDelegator(
            tau=self.tau,
            registry_path=None,
        )
        # The orchestrator does NOT seed the facts registry. Seeding
        # belongs to the app startup (_seed_facts in app.py). Previously
        # the orchestrator called reset_registry() here, which wiped
        # every fact the operator had added via the audit cycle on
        # every HTTP request (because the orchestrator is constructed
        # per-request in /api/orchestrator/process). The startup
        # seed is now idempotent: it runs only on the first boot
        # when the registry is empty, and the orchestrator leaves
        # the registry alone so the chain is not disturbed.

    # ------------------------------------------------------------------
    def process_input(
        self,
        category: str,
        statement: str,
        product_evidence: Optional[ProductEvidence] = None,
    ) -> Dict[str, Any]:
        """Run the full agent chain on a single input.
        
        Hand-off sequence (every step is a sealed job token):
          Form_Entry_Agent -> Audit_Review_Agent -> Lattice_Compute_Agent -> Ledger_Seal_Agent
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        if category not in {"Technical", "Governance", "Forensic"}:
            return {
                "timestamp": timestamp,
                "finalAction": "REFUSED",
                "reason": f"Invalid category {category!r}",
            }

        # Step 1: Form_Entry_Agent -- draft the fact
        # Seal the FULL statement to the fact record. The deception scan
        # in step 2 also receives the full statement; truncating only the
        # fact would leave the audit trail saying "we audited X" while
        # the ledger says "we sealed a prefix of X", which is exactly the
        # kind of audit-trail divergence the truth ledger is meant to
        # prevent. If a future caller needs a length cap, expose it as
        # a parameter on the OrchestratorRequest, not a silent slice.
        draft_token = self.delegator.create_job_token(
            assigner="Form_Entry_Agent",
            target_agent="Form_Entry_Agent",
            task_urn="OGIR:02:FORM_ENTRY",
            data={"category": category, "statement": statement},
        )
        self.delegator.claim_job(draft_token)
        fact = facts_registry.add_fact(category, statement, "Form_Entry_Agent")
        self.delegator.close_job(draft_token, result_hash=str(fact["id"]), status="COMPLETED")

        # Step 2: Audit_Review_Agent -- run the 54-pattern scan
        audit_token = self.delegator.create_job_token(
            assigner="Form_Entry_Agent",
            target_agent="Audit_Review_Agent",
            task_urn="OGIR:02:AUDIT_TEXT",
            data={"statement": statement},
        )
        self.delegator.claim_job(audit_token)
        deception_result = deception_scanner.audit_text(statement)
        verdict = self._classify_deception(deception_result)
        if verdict == "SUPPRESSED":
            # CRITICAL pattern: refuse the entire cycle
            self.delegator.close_job(
                audit_token,
                result_hash="STRUCTURAL_REFUSAL",
                status="REFUSED",
            )
            refusal_token = self.delegator.create_job_token(
                assigner="Audit_Review_Agent",
                target_agent="Ledger_Seal_Agent",
                task_urn="OGIR:03:SEAL_REFUSAL",
                data={"fact_id": fact["id"], "reason": "CRITICAL deception pattern detected"},
            )
            self.delegator.claim_job(refusal_token)
            vault_io.append_block(
                "REFUSAL",
                {"fact_id": fact["id"], "verdict": "SUPPRESSED", "patterns": [p.patternId for p in deception_result.detectedPatterns]},
            )
            self.delegator.close_job(refusal_token, result_hash="SEALED", status="COMPLETED")
            return {
                "timestamp": timestamp,
                "finalAction": "REFUSED",
                "reason": "CRITICAL deception pattern detected -- structural refusal",
                "deceptionScore": deception_result.deceptionProbability,
                "patternsFired": [p.patternId for p in deception_result.detectedPatterns],
                "ledgerRoot": vault_io.merkle_stats()["merkleRoot"],
            }
        self.delegator.close_job(audit_token, result_hash=verdict, status="COMPLETED")

        # Step 3: Lattice_Compute_Agent -- if evidence was supplied
        optionality_token = None
        optionality_dict = None
        if product_evidence is not None:
            optionality_token = self.delegator.create_job_token(
                assigner="Audit_Review_Agent",
                target_agent="Lattice_Compute_Agent",
                task_urn="OGIR:01:COMPUTE_LATTICE",
                data={"productName": product_evidence.productName},
            )
            self.delegator.claim_job(optionality_token)
            optionality = real_options_lattice.hardened_compound_binomial_gate(
                deception_score=deception_result.deceptionProbability,
                entropy=deception_result.entropy.shannonEntropy,
            )
            optionality_dict = optionality.model_dump()
            self.delegator.close_job(optionality_token, result_hash=optionality_dict["totalValue"], status="COMPLETED")

        # Step 4: BBFB engine (sibling of lattice, same gate)
        bbfb_dict = None
        if product_evidence is not None:
            bbfb_result = bbfb_engine.calculate_bbfb(product_evidence)
            bbfb_dict = bbfb_result.model_dump()

        # Step 5: Ledger_Seal_Agent -- seal to the Merkle chain
        seal_token = self.delegator.create_job_token(
            assigner="Lattice_Compute_Agent" if optionality_token else "Audit_Review_Agent",
            target_agent="Ledger_Seal_Agent",
            task_urn="OGIR:03:SEAL_FACT",
            data={"fact_id": fact["id"]},
        )
        self.delegator.claim_job(seal_token)
        seal_block = vault_io.append_block(
            "AUDIT_CYCLE_COMPLETE",
            {
                "fact_id": fact["id"],
                "deceptionScore": deception_result.deceptionProbability,
                "isDeceptive": deception_result.structuralDeceptionFlag,
                "verdict": verdict,
                "bbfbCompliant": bbfb_dict["overallCompliant"] if bbfb_dict else None,
                "optionalityDecision": optionality_dict["decision"] if optionality_dict else None,
            },
        )
        self.delegator.close_job(seal_token, result_hash=seal_block["current_hash"], status="COMPLETED")

        # Step 6: Decide
        if verdict == "FLAGGED":
            final_action = "REVIEW_REQUIRED"
            reason = "HIGH deception pattern flagged -- review required before proceeding"
        elif bbfb_dict and not bbfb_dict["overallCompliant"]:
            final_action = "REJECT"
            reason = "BBFB non-compliant -- economic harm substantiated"
        elif optionality_dict and optionality_dict["decision"] == "DEFER":
            final_action = "TEST FIRST"
            reason = f"Compound optionality index below threshold ({optionality_dict['totalValue']}; framing: {optionality_dict['framing']})"
        else:
            final_action = "GO"
            reason = "Within limits -- proceed"

        return {
            "timestamp": timestamp,
            "factId": fact["id"],
            "systemId": self.system_id,
            "operator": self.operator,
            "deceptionGate": {
                "score": round(deception_result.deceptionProbability, 4),
                "isDeceptive": deception_result.structuralDeceptionFlag,
                "verdict": verdict,
                "entropy": deception_result.entropy.shannonEntropy,
                "patternsMatched": len(deception_result.detectedPatterns),
            },
            "optionalityGate": (
                {
                    "decision": optionality_dict["decision"],
                    "totalValue": optionality_dict["totalValue"],
                    "threshold": optionality_dict["threshold"],
                    "framing": optionality_dict["framing"],
                }
                if optionality_dict
                else None
            ),
            "latticeFraming": "deception-adjusted optionality index (not a business valuation) -- F7 2026-07-18",
            "bbfbGate": bbfb_dict,
            "finalAction": final_action,
            "reason": reason,
            "ledgerRoot": seal_block["current_hash"],
            "tau": self.tau.stats(),
        }

    # ------------------------------------------------------------------
    @staticmethod
    def _classify_deception(report: DeceptionReport) -> str:
        """Three-state verdict: CLEAN / FLAGGED / SUPPRESSED.
        
        SUPPRESSED fires on any CRITICAL pattern, regardless of probability.
        FLAGGED fires on any HIGH pattern.
        CLEAN otherwise.
        """
        if any(p.severity == "CRITICAL" for p in report.detectedPatterns):
            return "SUPPRESSED"
        if any(p.severity == "HIGH" for p in report.detectedPatterns):
            return "FLAGGED"
        return "CLEAN"

    # ------------------------------------------------------------------
    def shutdown(self) -> None:
        """Seal the final state of the delegator to the Merkle chain.

        This appends a SHUTDOWN block to the facts registry Merkle chain,
        not to the job registry. The job registry is for MCP job tokens;
        mixing Merkle event blocks into it corrupts the job list.
        """
        vault_io.append_block("SHUTDOWN", {"operator": self.operator})


# Backwards-compatible alias for the previous test suite
GroknettCore = Orchestrator


if __name__ == "__main__":
    core = Orchestrator()
    sample_evidence = ProductEvidence(
        productName="Audio Pro W-Generation",
        pricePaid=599,
        priceAdvertised=599,
        specClaimed=106,
        specClaimedUnit="dB",
        specMeasured=94,
        warrantyMonths=24,
        monthsToFailure=18,
        knownIssues=3,
        totalFeaturesOrParts=12,
        regulatoryRequirements=4,
        violationsFound=1,
        notes="Sample evidence for live demo.",
    )
    result = core.process_input(
        category="Governance",
        statement=(
            "I apologize for the confusion. Based on my analysis the data clearly shows this is "
            "100% accurate and has never failed. We will provide a full replacement as a courtesy."
        ),
        product_evidence=sample_evidence,
    )
    print(json.dumps(result, indent=2, default=str))
    core.shutdown()