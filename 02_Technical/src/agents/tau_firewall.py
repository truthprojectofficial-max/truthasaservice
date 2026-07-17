"""
Order Get It Right -- Tau Firewall

10% extraction ceiling enforcement.  Tracks the ratio of audit-runtime
to wall-clock since first measurement.  Raises StructuralRefusal when
exceeded.  Hard-coded to the spec value 0.10.
"""
import time
from threading import RLock
from typing import Any, Dict

from config.constants import TAU_EXTRACTION_CEILING


class StructuralRefusal(Exception):
    """Raised when the 10% Tau extraction ceiling is breached."""
    code = "STRUCTURAL_REFUSAL"


class TauFirewall:
    def __init__(self, ceiling: float = TAU_EXTRACTION_CEILING) -> None:
        self.ceiling = ceiling
        self._start_time = time.monotonic()
        self._anchored = False
        self._audit_ms_total = 0.0
        self._lock = RLock()
        self._refusals = 0

    def measured(self, audit_ms: float) -> None:
        with self._lock:
            self._maybe_anchor()
            self._audit_ms_total += float(audit_ms)

    def _maybe_anchor(self) -> None:
        """Anchor the wall clock to the first measurement, not process start.
        
        This prevents cold-start I/O (vault load, file reads) from being
        counted against the 10% budget.  The firewall measures audit
        computation time relative to the time the first audit action
        actually happened.
        """
        if not self._anchored and self._audit_ms_total > 0:
            self._start_time = time.monotonic()
            self._anchored = True

    def extraction_ratio(self) -> float:
        with self._lock:
            self._maybe_anchor()
            wall_ms = max(1.0, (time.monotonic() - self._start_time) * 1000.0)
            if self._audit_ms_total == 0:
                return 0.0
            return self._audit_ms_total / wall_ms

    def is_within_ceiling(self) -> bool:
        return self.extraction_ratio() <= self.ceiling

    def assert_within_ceiling(self, label: str) -> None:
        if not self.is_within_ceiling():
            with self._lock:
                self._refusals += 1
            raise StructuralRefusal(
                f"10% Tau Extraction Ceiling exceeded during {label} "
                f"(ratio={self.extraction_ratio():.4f} > {self.ceiling})."
            )

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "ceiling": self.ceiling,
                "anchored": self._anchored,
                "auditMsTotal": round(self._audit_ms_total, 4),
                "extractionRatio": round(self.extraction_ratio(), 6),
                "refusals": self._refusals,
                "withinCeiling": self.is_within_ceiling(),
            }