"""
Order Get It Right - Exception Hierarchy

Every exception the runtime can raise is defined here, with a stable
string name that is also written to the audit ledger.
"""


class SovereignException(Exception):
    """Root of the Order Get It Right exception hierarchy."""
    code: str = "SOVEREIGN_EXCEPTION"


class StructuralRefusal(SovereignException):
    code = "STRUCTURAL_REFUSAL"


class UserExhaustion(SovereignException):
    code = "USER_EXHAUSTION"


class SpoliationDetected(SovereignException):
    code = "SPOLIATION_DETECTED"


class DeterminismViolation(SovereignException):
    code = "DETERMINISM_VIOLATION"


class TauCeilingExceeded(StructuralRefusal):
    code = "TAU_CEILING_EXCEEDED"


class StrikingGateViolation(StructuralRefusal):
    code = "STRIKING_GATE_VIOLATION"


class ExtractionError(SovereignException):
    code = "EXTRACTION_ERROR"


class UnsupportedFormat(SovereignException):
    code = "UNSUPPORTED_FORMAT"


class OntologyIntegrityError(SovereignException):
    code = "ONTOLOGY_INTEGRITY_ERROR"
