"""
Order Get It Right - Constants

Every magic number in the runtime is named here, with its source citation.
The constants are hard-coded, not configurable, so the audit verdict is
bit-for-bit identical on any host.
"""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Tau Extraction Ceiling (Governance Mandate)
# ---------------------------------------------------------------------------
TAU_EXTRACTION_CEILING = 0.10
TAU_VIOLATION_MESSAGE = (
    "STRUCTURAL_REFUSAL: single-input extraction exceeded 10% of runtime "
    "tolerances. Aborting the current cycle. Reduce input size or batch size."
)

# ---------------------------------------------------------------------------
# BBFB Engine Floors
# ---------------------------------------------------------------------------
PERFORMANCE_FLOOR = 0.50
EFFICIENCY_FLOOR = 0.30
WARRANTY_FLOOR = 1.00
ISSUE_DENSITY_FLOOR = 0.10
VIOLATION_RATIO_FLOOR = 0.05

# ---------------------------------------------------------------------------
# GRACE Quadratic Penalty Coefficient
# ---------------------------------------------------------------------------
GRACE_QUADRATIC_COEFFICIENT = 2.0
GRACE_CRITICAL_THRESHOLD = 0.75

# ---------------------------------------------------------------------------
# FRUIT Default Weights
# ---------------------------------------------------------------------------
FRUIT_WEIGHTS = {
    "cost": 0.4,
    "performance": 0.3,
    "reliability": 0.2,
    "compliance": 0.1,
}

# ---------------------------------------------------------------------------
# CVS Threshold
# ---------------------------------------------------------------------------
CVS_THRESHOLD = 0.0005

# ---------------------------------------------------------------------------
# Real-Options Lattice Defaults
# ---------------------------------------------------------------------------
REAL_OPTIONS_S0 = 55.0
REAL_OPTIONS_K1 = 18.0
REAL_OPTIONS_K2 = 10.0
REAL_OPTIONS_T1 = 3.0
REAL_OPTIONS_T2 = 3.0
REAL_OPTIONS_R = 0.05
REAL_OPTIONS_SIGMA1 = 0.30
REAL_OPTIONS_SIGMA2 = 0.20
REAL_OPTIONS_N1 = 3
REAL_OPTIONS_N2 = 3
REAL_OPTIONS_LEARNING_DELTA = 10.0
REAL_OPTIONS_STRIKING_RATIO = 0.85
REAL_OPTIONS_SIGMA_MIN = 0.05
REAL_OPTIONS_SIGMA_MAX = 0.95

# ---------------------------------------------------------------------------
# Entropy Thresholds
# ---------------------------------------------------------------------------
SHANNON_ANOMALY_THRESHOLD = 4.5
SHANNON_LOW_THRESHOLD = 2.5
SHANNON_MAX_NORMAL = 8.0

# ---------------------------------------------------------------------------
# Deception Probability Bands
# ---------------------------------------------------------------------------
DECEPTION_PROBABILITY_VETO = 0.75
DECEPTION_PROBABILITY_LOW = 0.30
DECEPTION_ONTOLOGY_VERSION = "3.9 (54 patterns)"

# ---------------------------------------------------------------------------
# Project Metadata
# ---------------------------------------------------------------------------
PROJECT_NAME = "Order Get It Right"
PROJECT_TAGLINE = "Truth as a Service"
PROJECT_VERSION = "1.0.0"
PROJECT_BUILD_DATE = "2026-07-12"
PROJECT_OPERATOR = "Justin Barnett"
PROJECT_JURISDICTION = "Commonwealth of Australia / ACL / Evidence Act 1995"
SYSTEM_ID = "Sovereign Node 9010 / Order Get It Right v1.0.0"
DEFAULT_VAULT_PATH = "03_Vault"
DEFAULT_OUTBOX_PATH = "04_Validation/reports"

# ---------------------------------------------------------------------------
# Squeal Protocol
# ---------------------------------------------------------------------------
SQUEAL_TRIGGER_PROBABILITY = 0.75

# ---------------------------------------------------------------------------
# Vault path
# ---------------------------------------------------------------------------
PROJECT_VAULT_DIR = str(PROJECT_ROOT / "03_Vault")
PROJECT_OUTBOX_DIR = str(PROJECT_ROOT / "04_Validation" / "reports")
PROJECT_LOGS_DIR = str(PROJECT_ROOT / "04_Validation" / "logs")
PROJECT_SQUEAL_DIR = str(PROJECT_ROOT / "04_Validation" / "squeal-reports")
PROJECT_CHANGELOG_DIR = str(PROJECT_ROOT / "04_Validation" / "changelog.log")
