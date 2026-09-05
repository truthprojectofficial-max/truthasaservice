"""
Order Get It Right -- Tauri Supabase shell integration.

Closes the Tauri-side shell wiring gap for Block B by verifying the
desktop app exposes Supabase config to the frontend and that the plain
HTML UI contains the auth + persistence flow for customers, orders,
order_files, and scans.
"""
from pathlib import Path


PROJECT = Path(__file__).resolve().parent.parent
LIB_RS = PROJECT / "02_Technical" / "src-tauri" / "src" / "lib.rs"
UI_HTML = PROJECT / "02_Technical" / "src-tauri" / "ui" / "index.html"


def test_lib_rs_exposes_supabase_config_command():
    """The Tauri invoke handler exposes supabase_config to the frontend."""
    text = LIB_RS.read_text(encoding="utf-8")
    assert "fn supabase_config()" in text, "lib.rs missing supabase_config command"
    assert "supabase_config," in text, "generate_handler! does not register supabase_config"


def test_lib_rs_reads_supabase_environment_variables():
    """The Supabase shell config comes from environment variables, not hardcoded secrets."""
    text = LIB_RS.read_text(encoding="utf-8")
    assert "OGIR_SUPABASE_URL" in text, "lib.rs must read OGIR_SUPABASE_URL"
    assert "OGIR_SUPABASE_ANON_KEY" in text, "lib.rs must read OGIR_SUPABASE_ANON_KEY"
    assert "project_ref" in text, "lib.rs should expose the Supabase project ref"


def test_ui_has_supabase_auth_controls():
    """The plain HTML UI exposes sign-up/sign-in/sign-out controls."""
    text = UI_HTML.read_text(encoding="utf-8")
    for token in (
        "btn-supabase-sign-up",
        "btn-supabase-sign-in",
        "btn-supabase-sign-out",
        "supabase-email",
        "supabase-password",
        "supabase-business-name",
    ):
        assert token in text, f"UI missing Supabase auth control: {token}"


def test_ui_has_audit_persistence_controls():
    """The UI exposes order/file metadata inputs and a save-scan action."""
    text = UI_HTML.read_text(encoding="utf-8")
    for token in (
        "order-external-id",
        "order-source",
        "file-name",
        "mime-type",
        "file-size",
        "btn-save-scan",
        "btn-load-scans",
        "scans-output",
    ):
        assert token in text, f"UI missing audit persistence control: {token}"


def test_ui_talks_to_supabase_auth_and_rest_endpoints():
    """The frontend hits Supabase auth plus orders/order_files/scans REST endpoints."""
    text = UI_HTML.read_text(encoding="utf-8")
    for token in (
        "/auth/v1/signup",
        "/auth/v1/token?grant_type=password",
        "/rest/v1/customers",
        "/rest/v1/orders",
        "/rest/v1/order_files",
        "/rest/v1/scans",
    ):
        assert token in text, f"UI missing Supabase endpoint: {token}"


def test_ui_persists_and_restores_session_locally():
    """The frontend keeps the Supabase session across restarts."""
    text = UI_HTML.read_text(encoding="utf-8")
    assert "localStorage.setItem('ogir.supabase.session'" in text
    assert "localStorage.getItem('ogir.supabase.session')" in text
    assert "loadSupabaseConfig().catch" in text, "UI should load Supabase config on startup"


def test_ui_does_not_hardcode_supabase_project_values():
    """The UI should not embed a fixed project URL or anon key."""
    text = UI_HTML.read_text(encoding="utf-8")
    assert "https://qqbrpqdbxhypkvvsjble.supabase.co" not in text
    assert "eyJ" not in text, "UI appears to embed a JWT-like Supabase key"
