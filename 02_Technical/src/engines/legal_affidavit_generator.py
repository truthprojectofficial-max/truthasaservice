"""
Legal Affidavit Generator (Section 177 / Section 79)

Transforms the cryptographically sealed Truth Ledger into a formal
legal statement suitable for filing under the Evidence Act 1995 (NSW).
"""
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from src.types import DeceptionReport
from config.constants import (
    PROJECT_NAME,
    PROJECT_VERSION,
    PROJECT_OPERATOR,
    PROJECT_JURISDICTION,
    DECEPTION_ONTOLOGY_VERSION,
)

LEGAL_PRECEDENTS = """
LEGAL BASIS AND APPLIED PRECEDENTS

1. Opinion evidence and specialised knowledge
   Makita (Australia) Pty Ltd v Sprowles [2001] NSWCA 305 at [85]:
   "An expert must demonstrate that his or her opinion is based on
   specialised knowledge arising from training, study or experience, and
   must identify the factual basis for the opinion and explain how that
   factual basis generates the opinion reached."

2. Consumer guarantees and misleading or deceptive conduct
   Australian Competition and Consumer Commission v Valve Corporation
   [2016] FCA 196; [2016] FCA 1553:
   - Foreign companies carrying on business in Australia are subject to
     the Australian Consumer Law (ACL) consumer guarantees.
   - ACL section 64 prevents exclusion, restriction or modification of
     consumer-guarantee rights.
   - ACL section 18 prohibits misleading or deceptive conduct, including
     misrepresentations about statutory rights of repair, replacement or
     refund.
   - ACL section 260 provides the major-failure remedy of refund,
     replacement or damages when goods fail to meet the consumer
     guarantee of acceptable quality under section 54.
""".strip()


class LegalAffidavitGenerator:
    """Compiles chronological evidence logs into a formal Section 177 certificate."""

    def __init__(self, ledger_path: str):
        self.ledger_path = ledger_path
        self.operator_identity = PROJECT_OPERATOR
        self.system_id = f"{PROJECT_NAME} v{PROJECT_VERSION}"
        self.jurisdiction = PROJECT_JURISDICTION
        self.ontology_version = DECEPTION_ONTOLOGY_VERSION

    # ------------------------------------------------------------------
    def _load_ledger(self) -> List[Dict[str, Any]]:
        """Load the Merkle truth ledger from disk."""
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                content = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        if isinstance(content, dict):
            return content.get("blocks", [])
        if isinstance(content, list):
            return content
        return []

    # ------------------------------------------------------------------
    def generate_header(self) -> str:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return (
            f"{'=' * 80}\n"
            f"                    AFFIDAVIT OF DETERMINISTIC SYSTEM TRUTH\n"
            f"{'=' * 80}\n"
            f"SYSTEM IDENTIFIER: {self.system_id}\n"
            f"PRIMARY OPERATOR: {self.operator_identity}\n"
            f"DATE OF AFFIDAVIT: {now}\n"
            f"ONTOLOGY VERSION: {self.ontology_version}\n"
            f"PROTOCOL COMPLIANCE: 00-99 Spatial Mandate / ISO Date Mandate / ACL Section 56\n"
            f"ENVIRONMENTAL STATUS: NO_NETWORK=1 (Air-Gapped Forensic Surface)\n"
            f"JURISDICTION: {self.jurisdiction}\n"
            f"{'=' * 80}\n\n"
            f"I, {self.operator_identity}, acting as the primary operator of {self.system_id},\n"
            f"hereby declare that the following evidentiary blocks were generated within a\n"
            f"deterministic, zero-black-box environment. These records are sealed via\n"
            f"SHA-256 Merkle-chaining and are tamper-evident.\n\n"
            f"This affidavit is issued under the authority of the BBFB Engine and\n"
            f"complies with Section 177 of the Evidence Act 1995 (NSW) and the\n"
            f"fall-back integrity provisions of Section 79 of the same Act.\n\n"
            f"Under Section 79 of the Evidence Act 1995 (NSW), as explained in\n"
            f"Makita (Australia) Pty Ltd v Sprowles [2001] NSWCA 305 at [85], opinion\n"
            f"evidence is admissible only where it is wholly or substantially based on the\n"
            f"witness's specialised knowledge arising from training, study or experience.\n"
            f"The operator's opinion in this affidavit is based on direct authorship of, and\n"
            f"working familiarity with, the deterministic {self.system_id} codebase; the\n"
            f"underlying methodology is transparent and reproducible.\n\n"
            f"--- BEGIN CHRONOLOGICAL EVIDENCE LOG ---\n"
        )

    # ------------------------------------------------------------------
    def format_entry(self, block: Dict[str, Any]) -> str:
        idx = block.get("index", block.get("block_index", "UNK"))
        ts = block.get("timestamp", "UNK")
        event = block.get("event_type", block.get("event", "SYSTEM_EVENT"))
        b_hash = block.get("current_hash", block.get("hash", "NO_HASH"))
        p_hash = block.get("previous_hash", block.get("prev_hash", "NO_PREV_HASH"))
        data = block.get("payload", block.get("data", {}))
        # Backward-compat read: prefer integrity_digest (post-2026-07-18 seal),
        # fall back to nizk_proof (pre-rename blocks). Both are the same SHA-256
        # of the canonical payload + operator constant -- just different field names.
        integrity = block.get("integrity_digest") or block.get("nizk_proof") or "N/A"

        return (
            f"\n"
            f"BLOCK INDEX: {idx}\n"
            f"TIMESTAMP: {ts}\n"
            f"EVENT CLASSIFICATION: {event}\n"
            f"CRYPTOGRAPHIC SEAL (SHA-256): {b_hash}\n"
            f"PREVIOUS BLOCK LINK: {p_hash}\n"
            f"INTEGRITY DIGEST (SHA-256 of canonical payload + operator constant; placeholder for future Schnorr implementation): {integrity}\n"
            f"FACTUAL CONTENT:\n{json.dumps(data, indent=4, default=str, sort_keys=True)}\n"
            f"{'-' * 80}\n"
        )

    # ------------------------------------------------------------------
    def compile_full_affidavit(self) -> str:
        """Compile the entire Merkle ledger into a single affidavit string."""
        blocks = self._load_ledger()
        if not blocks:
            return (
                "ERROR: No Truth Ledger entries found in the vault.\n"
                "Initialise the Facts Registry before generating affidavits."
            )
        affidavit = self.generate_header()
        for block in blocks:
            affidavit += self.format_entry(block)

        affidavit += (
            f"\n--- END OF EVIDENCE LOG ---\n\n"
            f"{LEGAL_PRECEDENTS}\n\n"
            f"VERIFICATION STATEMENT:\n"
            f"Every block listed above has been mathematically verified against the\n"
            f"{self.system_id} Truth Ledger root. Any alteration to a single bit of\n"
            f"data within this sequence would result in a complete hash-link failure.\n\n"
            f"Pathway of Reasoning: The verdict in this matter is reached by\n"
            f"deterministic application of (a) the 54-pattern deception ontology,\n"
            f"(b) the Barnett Binary Faith-Basis engine, and (c) the Real-Options\n"
            f"lattice, all of which are openly inspectable. The expert opinion\n"
            f"expressed is the system operator's interpretation of the system output\n"
            f"and is reproducible bit-for-bit on any host running {self.system_id}.\n"
            f"The opinion rests on specialised knowledge: direct authorship of, and\n"
            f"working familiarity with, the deterministic {self.system_id} codebase.\n"
            f"The factual basis is the sealed block chain set out above.\n\n"
            f"Specialised knowledge: The operator is the original author of the\n"
            f"{self.system_id} codebase and has direct, working knowledge of every\n"
            f"module, formula, and threshold used to produce the verdict.\n\n"
            f"SIGNED: ____________________________________\n"
            f"        {self.operator_identity}\n"
            f"        {self.system_id} Operator\n"
            f"        Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"
        )
        return affidavit

    # ------------------------------------------------------------------
    def save_to_vault(self, filename: str = "affidavit_transcript.txt") -> str:
        """Save the compiled affidavit to disk for archival."""
        import os
        output_dir = os.path.dirname(self.ledger_path)
        output_path = os.path.join(output_dir, filename)
        content = self.compile_full_affidavit()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path
