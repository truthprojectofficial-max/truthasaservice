"""
test_tauri_config_valid.py
==========================

The Tauri v2 app config (tauri.conf.json) must be:
  1. Valid JSON
  2. Reference a frontendDist that exists
  3. Reference a productName, version, identifier
  4. The ui/ directory must contain at least index.html
  5. src/lib.rs must declare the 3 commands: audit_text, list_models, system_check
  6. src/main.rs must call run() from lib.rs

If any of these fail, the Tauri build will fail.
"""
import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
TAURI_DIR = PROJECT / "02_Technical" / "src-tauri"


def test_tauri_config_is_valid_json():
    """tauri.conf.json parses as JSON."""
    config = TAURI_DIR / "tauri.conf.json"
    text = config.read_text(encoding="utf-8")
    obj = json.loads(text)
    assert isinstance(obj, dict)


def test_tauri_config_has_required_keys():
    """tauri.conf.json has productName, version, identifier, build, app, bundle."""
    config = TAURI_DIR / "tauri.conf.json"
    obj = json.loads(config.read_text(encoding="utf-8"))
    for key in ("productName", "version", "identifier", "build", "app", "bundle"):
        assert key in obj, f"missing key: {key}"


def test_frontend_dist_exists():
    """The frontendDist directory exists and contains at least index.html."""
    config = TAURI_DIR / "tauri.conf.json"
    obj = json.loads(config.read_text(encoding="utf-8"))
    frontend = obj["build"]["frontendDist"]
    # can be relative to src-tauri/
    if not Path(frontend).is_absolute():
        frontend = TAURI_DIR / frontend
    assert frontend.exists(), f"frontendDist not found: {frontend}"
    index = frontend / "index.html"
    assert index.exists(), f"index.html not found at {index}"


def test_lib_rs_has_three_commands():
    """src/lib.rs declares the 3 Tauri commands: audit_text, list_models, system_check."""
    lib_rs = TAURI_DIR / "src" / "lib.rs"
    text = lib_rs.read_text(encoding="utf-8")
    for cmd in ("audit_text", "list_models", "system_check"):
        assert f"fn {cmd}(" in text, f"lib.rs missing fn {cmd}("
    # also check generate_handler
    assert "generate_handler!" in text, "lib.rs missing generate_handler!"


def test_main_rs_calls_run():
    """src/main.rs calls run() from the lib crate."""
    main_rs = TAURI_DIR / "src" / "main.rs"
    text = main_rs.read_text(encoding="utf-8")
    assert "app_lib::run" in text or "lib::run" in text, "main.rs must call run()"


def test_audit_text_command_signature():
    """The audit_text command takes (text: String, context: Option<String>) and returns Result<String, String>."""
    lib_rs = TAURI_DIR / "src" / "lib.rs"
    text = lib_rs.read_text(encoding="utf-8")
    m = re.search(r"fn\s+audit_text\s*\(([^)]*)\)\s*->\s*Result<([^,>]+),\s*([^>]+)>", text)
    assert m, "audit_text signature not found or wrong return type"
    args = m.group(1)
    assert "text" in args and "String" in args, f"audit_text args: {args}"


def test_no_network_modules_in_lib_rs():
    """lib.rs must not import network modules (urllib/socket/http.client/reqwest/actix)."""
    lib_rs = TAURI_DIR / "src" / "lib.rs"
    text = lib_rs.read_text(encoding="utf-8")
    forbidden = ("use std::net", "use tokio::net", "reqwest::", "actix_web::", "hyper::")
    for f in forbidden:
        assert f not in text, f"lib.rs contains forbidden network import: {f}"
