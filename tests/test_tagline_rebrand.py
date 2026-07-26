"""
Order Get It Right -- Tagline rebrand validation.

Locks the change from "Truth as a Service" to "Verified Processor"
and rejects reintroduction of the legacy absolute-sounding tagline
in new source files.
"""
import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TECHNICAL = PROJECT_ROOT / "02_Technical"

LEGACY_TAGLINE = "Truth as a Service"
NEW_TAGLINE = "Verified Processor"

# Historical / archive / build-artefact files that legitimately contain
# the legacy tagline and must not be touched by this rebrand.
WHITELIST = {
    "04_Validation/changelog.log",
    "04_Validation/hardcopy/HARD_COPY_BACKUP_PLAN_1-2-3.txt",
    "04_Validation/hardcopy/OPERATOR_MANUAL.txt",
    "04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt",
    "04_Validation/legal_privacy/INTELLECTUAL_PROPERTY_RIGHTS.txt",
    "04_Validation/architecture_assessment/BBFB_INTEGRATION_PLANNING_2026-07-17.md",
    "04_Validation/reference_misc/CONTEXT_WINDOW.md",
    "04_Validation/handovers/HANDOVER_NEXT_SESSION_2026-07-16.md",
    "04_Validation/handovers/HANDOVER_TO_AUDITOR.md",
    "04_Validation/handovers/HANDOVER_TO_NEW_OPERATOR.md",
    "04_Validation/methodology_calibration/AI_COMPLIANCE_FABRICATION_TELLS_2026-07-18.md",
    "04_Validation/architecture_assessment/ACCREDITATION_AND_VERIFICATION_BRIEF_2026-07-21.md",
    "04_Validation/go_to_market/TAGLINE_REBRAND_VERIFIED_PROCESSOR_2026-07-21.md",
    "04_Validation/reference_misc/INTRODUCTION.md",
    "04_Validation/architecture_assessment/OGIR_ASSESSMENT_2026-07-18.md",
    "04_Validation/build_directives/OPEN_ITEMS_AND_REFERENCE.md",
    "04_Validation/reference_misc/TAURI_BINARY_INVESTIGATION_2026-07-16.md",

    "02_Technical/DEPLOYMENT.md",
    "02_Technical/RESOURCING.md",
    "02_Technical/requirements.txt",
    "02_Technical/tauri-shell/Cargo.toml",
    "02_Technical/tauri-shell/tauri.conf.json",
    "02_Technical/tauri-shell/tauri.conf.json.signing.example",
    "02_Technical/tauri-shell/A4_SEAL_COMPLETE.py",
    "02_Technical/tools/agentic_repl.py",
}


def _relative(p: Path) -> str:
    return p.relative_to(PROJECT_ROOT).as_posix()


def test_constants_tagline_is_verified_processor():
    text = (TECHNICAL / "config" / "constants.py").read_text(encoding="utf-8")
    assert f'PROJECT_TAGLINE = "{NEW_TAGLINE}"' in text, (
        "constants.py tagline not updated"
    )
    assert LEGACY_TAGLINE not in text, "constants.py still contains legacy tagline"


def test_src_init_tagline_is_verified_processor():
    text = (TECHNICAL / "src" / "__init__.py").read_text(encoding="utf-8")
    assert f'__tagline__ = "{NEW_TAGLINE}"' in text, (
        "src/__init__.py tagline not updated"
    )
    assert LEGACY_TAGLINE not in text, "src/__init__.py still contains legacy tagline"


def test_web_index_title_is_verified_processor():
    html = (TECHNICAL / "web" / "index.html").read_text(encoding="utf-8")
    assert NEW_TAGLINE in html, "web/index.html does not contain new tagline"
    assert LEGACY_TAGLINE not in html, "web/index.html still contains legacy tagline"


def test_readme_heading_is_verified_processor():
    readme = PROJECT_ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    assert f"# Order Get It Right — {NEW_TAGLINE}" in text, (
        "README heading not updated"
    )
    assert LEGACY_TAGLINE not in text, "README still contains legacy tagline"


def test_no_new_source_contains_legacy_tagline():
    """The legacy tagline must not appear in any non-whitelisted file."""
    offenders = []
    for py_file in TECHNICAL.rglob("*.py"):
        rel = _relative(py_file)
        if rel in WHITELIST:
            continue
        try:
            text = py_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if LEGACY_TAGLINE in text:
            offenders.append(rel)

    for md_file in (PROJECT_ROOT / "04_Validation").rglob("*.md"):
        rel = _relative(md_file)
        if rel in WHITELIST:
            continue
        try:
            text = md_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if LEGACY_TAGLINE in text:
            offenders.append(rel)

    assert not offenders, (
        f"legacy tagline found in non-whitelisted files: {offenders}"
    )
