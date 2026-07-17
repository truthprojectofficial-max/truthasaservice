"""Runtime config: vault path, logs path, etc."""
import os
from pathlib import Path

from config.constants import (
    PROJECT_ROOT,
    PROJECT_VAULT_DIR,
    PROJECT_OUTBOX_DIR,
    PROJECT_LOGS_DIR,
    PROJECT_SQUEAL_DIR,
    PROJECT_CHANGELOG_DIR,
)

# Working folders
VAULT_DIR = Path(os.environ.get("OGIR_VAULT", PROJECT_VAULT_DIR))
OUTBOX_DIR = Path(os.environ.get("OGIR_OUTBOX", PROJECT_OUTBOX_DIR))
LOGS_DIR = Path(os.environ.get("OGIR_LOGS", PROJECT_LOGS_DIR))
SQUEAL_DIR = Path(os.environ.get("OGIR_SQUEAL", PROJECT_SQUEAL_DIR))
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"
DISCOVERY_DIR = PROJECT_ROOT / "01_Methodology"
DOCS_DIR = PROJECT_ROOT / "docs"
TECHNICAL_DIR = PROJECT_ROOT / "02_Technical"

for _dir in (VAULT_DIR, OUTBOX_DIR, LOGS_DIR, SQUEAL_DIR, SAMPLES_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

ledger_path = lambda: VAULT_DIR / "facts_registry.json"
changelog_path = lambda: PROJECT_CHANGELOG_DIR
