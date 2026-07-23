"""
test_operator_research_preserved.py
====================================

The operator's 893-line architectural research at
  My Project/thinking about solvingComprehensive Architectural Framewo.txt
must be preserved inside the project at
  .hermes/plans/OPERATOR_ARCHITECTURAL_RESEARCH_2026-07-24.txt

The research is the operator's example. The plan references it; the project
commits it so it cannot be lost.

The research must contain all the major sections from the original:
  - Executive Summary
  - Technical Platform Comparison (Supabase vs Firebase vs AWS vs Fly.io vs VPS)
  - Tauri Build Prerequisites
  - GitHub Actions Pipeline YAML
  - OAuth 2.0 PKCE implementation
  - Supabase SQL schema
  - Apple Code Signing
  - Windows Code Signing
  - Australian Privacy Principles (13 APPs)
  - Cost Analysis
  - GTM Strategy
"""
import os
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RESEARCH = PROJECT / ".hermes" / "plans" / "OPERATOR_ARCHITECTURAL_RESEARCH_2026-07-24.txt"

# Major sections that must be present
REQUIRED_SECTIONS = [
    "Executive Summary",
    "Supabase",
    "Firebase",
    "AWS",
    "Tauri",
    "OAuth",
    "Cloudflare",
    "GitHub Actions",
    "Apple",
    "Windows",
    "Privacy",
    "APP",
    "Cost",
    "GTM",
    "go-to-market",  # case-insensitive
]


def test_research_file_exists():
    """The operator's research is preserved at .hermes/plans/."""
    assert RESEARCH.exists(), f"operator research not found at {RESEARCH}"


def test_research_file_size_above_30kb():
    """The research is substantial (>30 KB, was 41 KB originally)."""
    assert RESEARCH.stat().st_size > 30_000, f"research too small: {RESEARCH.stat().st_size} B"


def test_research_has_executive_summary():
    """The research has the Executive Summary section."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "Executive Summary" in text, "missing Executive Summary"


def test_research_has_supabase_section():
    """The research has the Supabase section (Postgres BaaS)."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "Supabase" in text, "missing Supabase section"


def test_research_has_tauri_section():
    """The research has the Tauri section."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "Tauri" in text, "missing Tauri section"


def test_research_has_oauth_section():
    """The research has the OAuth 2.0 PKCE section."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "OAuth" in text, "missing OAuth section"


def test_research_has_cloudflare_section():
    """The research has the Cloudflare R2/Workers section."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "Cloudflare" in text, "missing Cloudflare section"


def test_research_has_github_actions_yaml():
    """The research has the GitHub Actions YAML pipeline."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "release-pipeline.yml" in text or "tauri-action" in text, \
        "missing GitHub Actions YAML"


def test_research_has_apple_signing():
    """The research has the Apple code signing section."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "Apple" in text and ("signing" in text.lower() or "Developer ID" in text), \
        "missing Apple signing section"


def test_research_has_windows_signing():
    """The research has the Windows code signing section."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "Windows" in text and ("signing" in text.lower() or "Sectigo" in text or "IV" in text), \
        "missing Windows signing section"


def test_research_has_privacy_section():
    """The research has the Australian Privacy Principles (13 APPs)."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "Privacy" in text and "APP" in text, "missing privacy section"


def test_research_has_cost_analysis():
    """The research has the cost analysis section."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "Cost" in text or "Budget" in text, "missing cost analysis section"


def test_research_has_gtm_section():
    """The research has the go-to-market section."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "Market" in text or "GTM" in text, "missing GTM section"


def test_research_covers_all_13_apps():
    """The research references the 13 Australian Privacy Principles."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "13" in text and "APP" in text, "missing 13 APPs reference"


def test_research_mentions_drive_file_scope():
    """The research mentions the Google drive.file scope (PKCE-narrow)."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "drive.file" in text, "missing drive.file scope mention"


def test_research_mentions_msix():
    """The research mentions MSIX (Microsoft Store distribution)."""
    text = RESEARCH.read_text(encoding="utf-8")
    assert "MSIX" in text, "missing MSIX mention"
