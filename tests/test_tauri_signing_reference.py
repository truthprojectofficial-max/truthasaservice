"""
Order Get It Right -- Tauri Windows signing reference validation.

The project has a Tauri shell under 02_Technical/tauri-shell but no
production signing certificate is committed (the private key must never
live in the repo). This test locks the existence and shape of the signing
reference so it cannot be silently removed or corrupted:

  1. The signing-options reference doc must exist.
  2. The live tauri.conf.json must remain unsigned (no real thumbprint).
  3. A signing example config must exist with the required bundle.windows
     placeholder keys.

These checks are read-only; they do not import or run Tauri.
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TAURI_DIR = PROJECT_ROOT / "02_Technical" / "tauri-shell"
DOC_PATH = PROJECT_ROOT / "04_Validation" / "TAURI_SIGNING_OPTIONS_2026-07-18.md"
LIVE_CONF = TAURI_DIR / "tauri.conf.json"
EXAMPLE_CONF = TAURI_DIR / "tauri.conf.json.signing.example"


def test_tauri_signing_reference_doc_exists():
    assert DOC_PATH.is_file(), f"missing signing options reference: {DOC_PATH}"


def test_tauri_signing_options_doc_covers_all_routes():
    text = DOC_PATH.read_text(encoding="utf-8")
    for route in ["Option A", "Option B", "Option C"]:
        assert route in text, f"reference doc missing route: {route}"
    for key in ["certificateThumbprint", "digestAlgorithm", "timestampUrl"]:
        assert key in text, f"reference doc missing config key: {key}"


def test_live_tauri_conf_remains_unsigned():
    """The committed tauri.conf.json must never contain a real thumbprint.

    A placeholder is fine; a 40-hex-char thumbprint is not.
    """
    assert LIVE_CONF.is_file(), f"missing live Tauri config: {LIVE_CONF}"
    conf = json.loads(LIVE_CONF.read_text(encoding="utf-8"))
    windows = conf.get("bundle", {}).get("windows", {})
    thumbprint = windows.get("certificateThumbprint", "")
    # If a thumbprint is present, it must be a placeholder, not real hex.
    if thumbprint:
        hex_only = all(c in "0123456789abcdefABCDEF" for c in thumbprint)
        assert not (hex_only and len(thumbprint) >= 40), (
            "live tauri.conf.json contains what looks like a real certificate "
            f"thumbprint: {thumbprint}"
        )


def test_tauri_signing_example_exists_and_is_valid():
    assert EXAMPLE_CONF.is_file(), f"missing signing example config: {EXAMPLE_CONF}"
    conf = json.loads(EXAMPLE_CONF.read_text(encoding="utf-8"))
    windows = conf.get("bundle", {}).get("windows", {})
    for key in ("certificateThumbprint", "digestAlgorithm", "timestampUrl"):
        assert key in windows, f"signing example missing bundle.windows.{key}"
    assert windows["digestAlgorithm"] == "sha256", (
        "signing example digestAlgorithm should default to sha256"
    )
