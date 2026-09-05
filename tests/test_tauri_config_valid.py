"""
test_tauri_config_valid.py
============================

The Tauri v2 config at 02_Technical/src-tauri/tauri.conf.json must be
valid JSON and must contain all the production-grade fields the operator's
research specifies (signing, MSI, DMG, AppImage, updater endpoints).
"""
import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
TAURI_CONF = PROJECT / "02_Technical" / "src-tauri" / "tauri.conf.json"
CARGO_TOML = PROJECT / "02_Technical" / "src-tauri" / "Cargo.toml"
CAPABILITIES = PROJECT / "02_Technical" / "src-tauri" / "capabilities" / "default.json"


def test_tauri_conf_is_valid_json():
    """tauri.conf.json is valid JSON."""
    obj = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
    assert isinstance(obj, dict)


def test_tauri_conf_has_product_name():
    """tauri.conf.json has a productName field."""
    obj = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
    assert obj.get("productName") == "OrderGetItRight"


def test_tauri_conf_has_version():
    """tauri.conf.json has a version field."""
    obj = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
    assert obj.get("version") == "0.1.0"


def test_tauri_conf_has_identifier():
    """tauri.conf.json has a non-default identifier."""
    obj = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
    ident = obj.get("identifier", "")
    assert ident != "com.tauri.dev", f"identifier is the placeholder default: {ident}"
    assert "ordergetitright" in ident.lower(), f"identifier does not reference ordergetitright: {ident}"


def test_tauri_conf_frontend_dist_exists():
    """tauri.conf.json's frontendDist points to a directory that exists."""
    obj = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
    frontend_dist = PROJECT / "02_Technical" / "src-tauri" / obj["build"]["frontendDist"]
    assert frontend_dist.exists(), f"frontendDist does not exist: {frontend_dist}"


def test_tauri_conf_bundle_has_targets():
    """tauri.conf.json's bundle.targets is 'all' (cross-platform)."""
    obj = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
    assert obj["bundle"]["targets"] == "all"


def test_tauri_conf_bundle_has_windows_signing():
    """tauri.conf.json's bundle.windows has signing config (the Sectigo IV cert)."""
    obj = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
    assert "windows" in obj["bundle"], "bundle.windows missing"
    win = obj["bundle"]["windows"]
    assert "certificateThumbprint" in win, "windows.certificateThumbprint missing"
    assert "timestampUrl" in win, "windows.timestampUrl missing"
    assert "wix" in win, "windows.wix missing (MSI config)"


def test_tauri_conf_bundle_has_macos_signing():
    """tauri.conf.json's bundle.macOS has signing config (the Apple Developer ID)."""
    obj = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
    assert "macOS" in obj["bundle"], "bundle.macOS missing"
    mac = obj["bundle"]["macOS"]
    assert "signingIdentity" in mac, "macOS.signingIdentity missing"
    assert "minimumSystemVersion" in mac, "macOS.minimumSystemVersion missing"


def test_tauri_conf_bundle_has_linux_targets():
    """tauri.conf.json's bundle.linux has deb + appimage + rpm config."""
    obj = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
    assert "linux" in obj["bundle"], "bundle.linux missing"
    linux = obj["bundle"]["linux"]
    assert "deb" in linux, "linux.deb missing"
    assert "appimage" in linux, "linux.appimage missing"
    assert "rpm" in linux, "linux.rpm missing"


def test_tauri_conf_has_updater_config():
    """tauri.conf.json has plugins.updater config (the Tauri updater plugin)."""
    obj = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
    assert "plugins" in obj, "plugins missing"
    assert "updater" in obj["plugins"], "plugins.updater missing"
    updater = obj["plugins"]["updater"]
    assert "endpoints" in updater, "updater.endpoints missing"
    assert len(updater["endpoints"]) > 0, "updater.endpoints is empty"
    assert "pubkey" in updater, "updater.pubkey missing"


def test_tauri_conf_updater_endpoints_point_to_cloudflare():
    """The updater endpoints point to update.ordergetitright.com (the Cloudflare Worker)."""
    obj = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
    endpoints = obj["plugins"]["updater"]["endpoints"]
    for ep in endpoints:
        assert "ordergetitright.com" in ep, f"updater endpoint does not reference ordergetitright.com: {ep}"


def test_tauri_conf_bundle_publisher():
    """tauri.conf.json's bundle has publisher and publisherName."""
    obj = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
    assert obj["bundle"].get("publisher") is not None
    assert obj["bundle"].get("publisherName") is not None


def test_cargo_toml_has_all_research_deps():
    """Cargo.toml has all 6 deps the research specifies (lines 262-271)."""
    text = CARGO_TOML.read_text(encoding="utf-8")
    for dep in ("tauri", "tauri-plugin-updater", "tauri-plugin-dialog",
                 "tauri-plugin-process", "tauri-plugin-store", "tauri-plugin-http"):
        assert dep in text, f"Cargo.toml missing {dep}"


def test_cargo_toml_tauri_dependency_is_resolvable():
    """Cargo.toml keeps the tauri dependency in a resolvable 2.x form."""
    text = CARGO_TOML.read_text(encoding="utf-8")
    m = re.search(r'tauri\s*=\s*\{([^}]+)\}', text)
    assert m is not None, "Cargo.toml missing tauri dependency block"
    block = m.group(1)
    assert 'version = "2.' in block, f"expected a Tauri 2.x dependency, got: {block}"
    assert 'features = ["all"]' not in block, "invalid Tauri 2.x feature 'all' breaks cargo resolution"


def test_cargo_toml_has_pkce_primitives():
    """Cargo.toml has sha2, base64, rand (used by the PKCE handler in commands.rs)."""
    text = CARGO_TOML.read_text(encoding="utf-8")
    for dep in ("sha2", "base64", "rand"):
        assert dep in text, f"Cargo.toml missing PKCE primitive {dep}"


def test_capabilities_default_json_is_valid_json():
    """capabilities/default.json is valid JSON."""
    obj = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
    assert isinstance(obj, dict)


def test_capabilities_includes_plugin_permissions():
    """capabilities/default.json has permissions for the 5 research plugins."""
    obj = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
    perms = obj.get("permissions", [])
    perms_text = " ".join(perms).lower()
    for plugin in ("core", "dialog", "store", "http", "process", "updater"):
        assert plugin in perms_text, f"capabilities missing {plugin} permission"


def test_no_network_modules_in_src_tauri_src():
    """The src-tauri/src/ directory has no Python network modules (it's Rust)."""
    src_dir = PROJECT / "02_Technical" / "src-tauri" / "src"
    assert src_dir.exists()
    py_files = list(src_dir.glob("*.py"))
    assert len(py_files) == 0, f"src-tauri/src/ has Python files: {[f.name for f in py_files]}"


def test_lib_rs_has_tauri_commands():
    """src-tauri/src/lib.rs declares Tauri commands (audit_text, list_models, system_check)."""
    lib_rs = PROJECT / "02_Technical" / "src-tauri" / "src" / "lib.rs"
    text = lib_rs.read_text(encoding="utf-8")
    for cmd in ("audit_text", "list_models", "system_check"):
        assert cmd in text, f"lib.rs missing command {cmd}"


def test_commands_rs_has_oauth_pkce():
    """src-tauri/src/commands.rs has the OAuth PKCE handler."""
    commands_rs = PROJECT / "02_Technical" / "src-tauri" / "src" / "commands.rs"
    text = commands_rs.read_text(encoding="utf-8")
    assert "drive.file" in text
    assert "S256" in text
    assert "127.0.0.1:0" in text


def test_commands_rs_cross_platform_browser_launch():
    """src-tauri/src/commands.rs opens the browser on Windows, macOS, and Linux.

    Per the subagent's audit, the original code had a `#[cfg(target_os = "windows")]`
    block with no `else` for non-Windows builds. This would silently no-op the
    browser launch on macOS/Linux and then block for 120s. Fixed by adding
    explicit `#[cfg]` blocks for each platform.
    """
    commands_rs = PROJECT / "02_Technical" / "src-tauri" / "src" / "commands.rs"
    text = commands_rs.read_text(encoding="utf-8")
    # All 3 platforms must have an explicit cfg block
    assert 'target_os = "windows"' in text, "missing Windows browser launch"
    assert 'target_os = "macos"' in text, "missing macOS browser launch (subagent audit)"
    assert "xdg-open" in text, "missing Linux browser launch (subagent audit)"
    assert "open" in text, "missing macOS `open` command"


def test_lib_rs_registers_google_handshake():
    """src-tauri/src/lib.rs registers google_handshake in generate_handler!.

    Per the subagent's audit, the OAuth PKCE handler was defined in commands.rs
    but NOT registered in lib.rs's generate_handler! macro, making it unreachable
    from the WebView2 frontend. Fixed.
    """
    lib_rs = PROJECT / "02_Technical" / "src-tauri" / "src" / "lib.rs"
    text = lib_rs.read_text(encoding="utf-8")
    assert "google_handshake" in text, \
        "lib.rs does not register google_handshake in generate_handler!"
    # The generate_handler! block must include it
    m = re.search(r"generate_handler!\[(.+?)\]", text, re.DOTALL)
    assert m is not None, "no generate_handler! macro found"
    block = m.group(1)
    assert "google_handshake" in block, \
        "google_handshake not in generate_handler! block"


def test_lib_rs_registers_all_5_research_plugins():
    """src-tauri/src/lib.rs registers all 5 research plugins (updater, dialog, process, store, http)."""
    lib_rs = PROJECT / "02_Technical" / "src-tauri" / "src" / "lib.rs"
    text = lib_rs.read_text(encoding="utf-8")
    for plugin in ("updater", "dialog", "process", "store", "http"):
        assert f"tauri_plugin_{plugin}" in text, f"lib.rs missing {plugin} plugin registration"
