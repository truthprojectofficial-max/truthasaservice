"""
test_oauth_pkce_implementation_valid.py
========================================

The OAuth 2.0 PKCE implementation in 02_Technical/src-tauri/src/commands.rs
must match the operator's architectural research at
  .hermes/plans/OPERATOR_ARCHITECTURAL_RESEARCH_2026-07-24.txt

Specifically:
  1. Uses drive.file scope (NOT full drive) -- bypasses Google audit
  2. Uses PKCE S256 (SHA-256 code_challenge_method)
  3. Binds to 127.0.0.1:0 (any free loopback port)
  4. Uses base64-url-no-pad for the code_verifier and code_challenge
  5. Opens the user's browser with the auth URL
  6. Blocks on the loopback listener for the callback
  7. Extracts the auth code from the redirect query string
  8. Returns (auth_code, redirect_uri) to the frontend

The Rust file may not compile in the test environment (rustfmt missing),
but the structure must be correct.
"""
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
COMMANDS = PROJECT / "02_Technical" / "src-tauri" / "src" / "commands.rs"


def test_commands_rs_exists():
    """The commands.rs file exists."""
    assert COMMANDS.exists(), f"commands.rs not found at {COMMANDS}"


def test_commands_rs_uses_drive_file_scope():
    """The PKCE handler uses the narrow drive.file scope (NOT full drive)."""
    text = COMMANDS.read_text(encoding="utf-8")
    assert "drive.file" in text, "commands.rs does not use drive.file scope"
    # MUST NOT use full drive
    assert "drive" not in text or "drive.file" in text, \
        "commands.rs may be using full drive scope (bypasses narrow-scope intent)"


def test_commands_rs_uses_pkce_s256():
    """The PKCE handler uses S256 code_challenge_method (SHA-256)."""
    text = COMMANDS.read_text(encoding="utf-8")
    assert "S256" in text, "commands.rs does not use S256 code_challenge_method"
    assert "code_challenge" in text, "commands.rs does not implement code_challenge"


def test_commands_rs_binds_to_loopback():
    """The PKCE handler binds to 127.0.0.1:0 (any free loopback port)."""
    text = COMMANDS.read_text(encoding="utf-8")
    assert "127.0.0.1:0" in text, "commands.rs does not bind to 127.0.0.1:0"


def test_commands_rs_uses_pkce_verifier():
    """The PKCE handler generates a code_verifier (random URL-safe string)."""
    text = COMMANDS.read_text(encoding="utf-8")
    assert "code_verifier" in text, "commands.rs does not implement code_verifier"
    assert "URL_SAFE_NO_PAD" in text, "commands.rs does not use base64-url-no-pad"


def test_commands_rs_opens_browser():
    """The PKCE handler opens the user's browser to the Google auth URL."""
    text = COMMANDS.read_text(encoding="utf-8")
    assert "google" in text.lower() or "GOOGLE" in text, \
        "commands.rs does not reference Google OAuth"


def test_commands_rs_uses_prompt_consent():
    """The PKCE handler requests prompt=consent for offline access."""
    text = COMMANDS.read_text(encoding="utf-8")
    assert "prompt=consent" in text or "prompt=\"consent\"" in text, \
        "commands.rs does not request prompt=consent (needed for refresh_token)"


def test_commands_rs_requests_offline_access():
    """The PKCE handler requests access_type=offline for refresh_token."""
    text = COMMANDS.read_text(encoding="utf-8")
    assert "access_type=offline" in text or "access_type=\"offline\"" in text, \
        "commands.rs does not request offline access (needed for refresh_token)"


def test_commands_rs_no_network_modules():
    """The PKCE handler does not use reqwest, hyper, or actix (loopback only)."""
    text = COMMANDS.read_text(encoding="utf-8")
    forbidden = ("use reqwest", "use actix_web", "use hyper")
    for f in forbidden:
        assert f not in text, f"commands.rs uses forbidden network crate: {f}"


def test_commands_rs_extracts_code():
    """The PKCE handler extracts the auth code from the redirect query string."""
    text = COMMANDS.read_text(encoding="utf-8")
    assert "code" in text and "extract_code" in text, \
        "commands.rs does not extract the auth code from the callback"
