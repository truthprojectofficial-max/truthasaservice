"""
Order Get It Right - Constants

Same input + same config = same verdict, same scores, same decision -- on
any host. The sealed chain carries ISO-8601 timestamps and is tamper-evident,
not byte-reproducible across runs. The runtime computation (deception
probability, entropy, pattern matches, BBFB/FRUIT/GRACE scores, lattice
decision) is deterministic; the sealed payload and the job tokens embed
``datetime.now(timezone.utc)`` so two audits run a second apart produce
different chains. The chain is append-only and verifiable from disk; the
runtime is reproducible from inputs.

Every magic number in the runtime is named here, with its source citation.
The constants are hard-coded, not configurable, so the audit verdict is
identical on any host.
"""
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
DECEPTION_ONTOLOGY_VERSION = "3.10 (55 patterns, R1-R6 applied)"

# ---------------------------------------------------------------------------
# Project Metadata
# ---------------------------------------------------------------------------
PROJECT_NAME = "Order Get It Right"
PROJECT_TAGLINE = "Truth as a Service"
PROJECT_VERSION = "1.0.0"
PROJECT_BUILD_DATE = "2026-07-12"
PROJECT_OPERATOR = "Justin Barnett"
# PRIVACY/PSEUDONYMISATION (2026-07-19):
# The chain is append-only and shareable (USB, remote, auditor). Under
# new privacy laws, personal data sealed into chain blocks is a leak
# risk if the chain is shared. CHAIN_OPERATOR_ID is the pseudonymised
# identity used in chain blocks (vault_io, orchestrator seal payloads).
# PROJECT_OPERATOR remains the real name for legal output documents
# (affidavit generator, ACL demand letter) where the signing party
# must be identified. See VERIFIED_TRUTHS_BANK_2026-07-19.md for the
# indicator-driven decision that produced this split.
CHAIN_OPERATOR_ID = "OGIR-OPERATOR"
PROJECT_JURISDICTION = "Commonwealth of Australia / ACL / Evidence Act 1995"
SYSTEM_ID = "Sovereign Node 9010 / Order Get It Right v1.0.0"
DEFAULT_VAULT_PATH = "03_Vault"
DEFAULT_OUTBOX_PATH = "04_Validation/reports"

# ---------------------------------------------------------------------------
# Squeal Protocol
# ---------------------------------------------------------------------------
SQUEAL_TRIGGER_PROBABILITY = 0.75

# ---------------------------------------------------------------------------
# Lattice Framing (F7, added 2026-07-18)
# ---------------------------------------------------------------------------
# The two-stage compound binomial lattice is deterministic but its inputs
# (S0, K1, K2) are hard-coded defaults, not audited financial statements.
# The output is therefore a **deception-adjusted optionality index**, NOT a
# business valuation. Every place in the code that produces a verdict or
# output string from this lattice carries this framing so a third-party
# reader (or the s.177 affidavit) cannot mistake it for a business
# valuation. See 01_Methodology/REAL_OPTIONS_LATTICE.md "Framing" section.
LATTICE_FRAMING = "deception-adjusted optionality index (not a business valuation) -- F7-deep 2026-07-19 wired to evidence when supplied"
LATTICE_INPUTS_ARE_HARDCODED = False  # F7-deep 2026-07-19: derived from evidence when supplied, else defaults

# ---------------------------------------------------------------------------
# F7-SPEC (2026-07-19): Taguchi-quadratic spec-value curve constants.
# Replaces the hard specAccuracy floor (>= PERFORMANCE_FLOOR) with a concave
# value function that peaks at spec measured == spec claimed and declines
# on BOTH sides (symmetric Taguchi loss). See
# 04_Validation/DIMINISHING_RETURNS_RESEARCH_2026-07-19.md for methodology
# and primary-source citations (Taguchi 1986, Introduction to Quality
# Engineering). V_min is derived from PERFORMANCE_FLOOR so the veto
# boundary is preserved by construction: V(0.5) = 1 - (0.5/1.0)^2 = 0.75.
SPEC_BEST_BAND_X_STAR = 1.0     # peak: spec measured == spec claimed
SPEC_VALUE_WIDTH_W = 1.0        # width: V(0.5) = 0.75, V(1.5) = 0.75
SPEC_VALUE_VETO_FLOOR = 0.75    # V_min = V(PERFORMANCE_FLOOR) -- behaviour-preserving

# ---------------------------------------------------------------------------
# Vault path
# ---------------------------------------------------------------------------
PROJECT_VAULT_DIR = str(PROJECT_ROOT / "03_Vault")
PROJECT_OUTBOX_DIR = str(PROJECT_ROOT / "04_Validation" / "reports")
PROJECT_LOGS_DIR = str(PROJECT_ROOT / "04_Validation" / "logs")
PROJECT_SQUEAL_DIR = str(PROJECT_ROOT / "04_Validation" / "squeal-reports")
PROJECT_CHANGELOG_DIR = str(PROJECT_ROOT / "04_Validation" / "changelog.log")
