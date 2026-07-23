"""
Order Get It Right -- Google OAuth client ID test.

Closes Block C of the GTM plan. Verifies the OAuth client ID in
02_Technical/src-tauri/src/commands.rs is a real Google-registered
Desktop app client ID, NOT the OPERATOR_SET_IN_TAURI_CONFIG placeholder.
The code in commands.rs implements the full PKCE S256 flow; this test
confirms the ID is wired so the flow can actually talk to Google.
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COMMANDS_RS = PROJECT_ROOT / "02_Technical" / "src-tauri" / "src" / "commands.rs"


def test_oauth_client_id_is_not_placeholder():
    """The CLIENT_ID const must not be the placeholder string."""
    content = COMMANDS_RS.read_text(encoding="utf-8")
    assert "OPERATOR_SET_IN_TAURI_CONFIG" not in content, (
        "commands.rs still has the OPERATOR_SET_IN_TAURI_CONFIG placeholder. "
        "Register a Desktop app OAuth client at console.cloud.google.com and "
        "paste the Client ID. See GTM_OPERATOR_DIRECTIVES Block C."
    )


def test_oauth_client_id_is_real_google_format():
    """The CLIENT_ID must match the Google OAuth client ID format:
    <digits>-<44chars>.apps.googleusercontent.com"""
    content = COMMANDS_RS.read_text(encoding="utf-8")
    m = re.search(r'const CLIENT_ID:\s*&str\s*=\s*"([^"]+)"', content)
    assert m, "could not find CLIENT_ID const in commands.rs"
    client_id = m.group(1)
    # Google Desktop app client IDs look like:
    # 123456789-abc...apps.googleusercontent.com
    assert ".apps.googleusercontent.com" in client_id, (
        f"CLIENT_ID does not look like a Google OAuth client ID: {client_id}"
    )
    assert re.match(r"^\d+-[a-z0-9]+\.apps\.googleusercontent\.com$", client_id), (
        f"CLIENT_ID format mismatch (expected <digits>-<chars>.apps.googleusercontent.com): {client_id}"
    )


def test_oauth_uses_drive_file_scope():
    """The scope must be drive.file (narrow), not drive (full) -- the
    narrow scope bypasses Google's 100-user brand verification audit."""
    content = COMMANDS_RS.read_text(encoding="utf-8")
    assert "drive.file" in content, (
        "commands.rs must use the drive.file scope (narrow), not drive (full)"
    )
    assert '"/auth/drive "' not in content and '"/auth/drive"' not in content, (
        "commands.rs must NOT use the full drive scope"
    )


def test_oauth_uses_pkce_s256():
    """The PKCE code_challenge_method must be S256 (SHA-256), not plain."""
    content = COMMANDS_RS.read_text(encoding="utf-8")
    assert "code_challenge_method=S256" in content, (
        "commands.rs must use PKCE S256 (SHA-256), not plain"
    )