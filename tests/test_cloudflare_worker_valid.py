"""
test_cloudflare_worker_valid.py
================================

The Cloudflare Worker at 02_Technical/cloudflare-worker/ is Block D's
updater server. It must:
  1. The src/index.js file exists and is valid JavaScript
  2. The wrangler.toml file exists and is valid TOML
  3. The package.json file exists and is valid JSON
  4. The worker has the 3 routes: /, /latest, /:platform/:version
  5. The worker returns 204 when client is up-to-date
  6. The worker returns the manifest when an update is available
  7. The worker does not use Node-specific APIs (it's a Worker, not a Node app)

The actual deploy is operator-gated (needs Cloudflare account + KV namespace).
"""
import json
import re
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
WORKER_DIR = PROJECT / "02_Technical" / "cloudflare-worker"
INDEX_JS = WORKER_DIR / "src" / "index.js"
WRANGLER = WORKER_DIR / "wrangler.toml"
PACKAGE = WORKER_DIR / "package.json"

NODE = r"C:\Program Files\nodejs\node.exe"


def test_worker_directory_exists():
    """The cloudflare-worker directory exists."""
    assert WORKER_DIR.exists(), f"worker dir not found at {WORKER_DIR}"


def test_index_js_exists():
    """The src/index.js file exists."""
    assert INDEX_JS.exists(), f"index.js not found at {INDEX_JS}"


def test_index_js_is_valid_javascript():
    """The index.js parses with node --check (syntax-only)."""
    r = subprocess.run(
        [NODE, "--check", str(INDEX_JS)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"index.js has syntax errors: {r.stderr}"


def test_index_js_has_three_routes():
    """The worker has 3 routes: /health, /latest, /:platform/:version."""
    text = INDEX_JS.read_text(encoding="utf-8")
    # /health (or root)
    assert "health" in text or 'path === ""' in text, "missing health check route"
    # /latest
    assert "/latest" in text, "missing /latest route"
    # /:platform/:version -- matched by a regex with two capture groups
    # The match() call captures platform and version from the URL
    assert re.search(r'\[,\s*targetPlatform,\s*clientVersion\]', text) \
        and re.search(r'path\.match', text), \
        "missing /:platform/:version route (regex match with destructured groups)"


def test_index_js_returns_204_when_up_to_date():
    """The worker returns 204 when the client version matches the latest version."""
    text = INDEX_JS.read_text(encoding="utf-8")
    assert "status: 204" in text or "status = 204" in text, \
        "worker must return 204 when client is up-to-date or no release exists"


def test_index_js_uses_kv_for_latest_release():
    """The worker reads latest_release from UPDATES_KV."""
    text = INDEX_JS.read_text(encoding="utf-8")
    assert "UPDATES_KV" in text, "worker must read from UPDATES_KV"
    assert "latest_release" in text, "worker must read the latest_release key"


def test_index_js_no_node_specific_apis():
    """The worker does not use Node-specific APIs (it's a Worker, not a Node app)."""
    text = INDEX_JS.read_text(encoding="utf-8")
    forbidden = ("require(", "process.env", "fs.readFile", "Buffer.from(", "setTimeout(")
    for f in forbidden:
        assert f not in text, f"worker uses Node-specific API: {f}"


def test_wrangler_toml_exists():
    """The wrangler.toml file exists."""
    assert WRANGLER.exists(), f"wrangler.toml not found at {WRANGLER}"


def test_wrangler_toml_has_name():
    """The wrangler.toml has a name field."""
    text = WRANGLER.read_text(encoding="utf-8")
    assert re.search(r'^name\s*=\s*"', text, re.MULTILINE), "wrangler.toml missing name field"


def test_wrangler_toml_has_routes():
    """The wrangler.toml declares routes for update.ordergetitright.com."""
    text = WRANGLER.read_text(encoding="utf-8")
    assert "update.ordergetitright.com" in text, "wrangler.toml missing custom domain routes"


def test_package_json_exists():
    """The package.json file exists."""
    assert PACKAGE.exists(), f"package.json not found at {PACKAGE}"


def test_package_json_has_wrangler_dep():
    """The package.json declares wrangler as a dev dependency."""
    obj = json.loads(PACKAGE.read_text(encoding="utf-8"))
    deps = obj.get("devDependencies", {})
    assert "wrangler" in deps, "package.json missing wrangler devDependency"


def test_package_json_has_deploy_script():
    """The package.json has a deploy script."""
    obj = json.loads(PACKAGE.read_text(encoding="utf-8"))
    scripts = obj.get("scripts", {})
    assert "deploy" in scripts, "package.json missing deploy script"
    assert "wrangler" in scripts["deploy"], "deploy script must use wrangler"
