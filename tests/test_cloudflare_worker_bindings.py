"""
Order Get It Right -- Cloudflare Worker bindings test.

Closes Block D of the GTM plan. Verifies the wrangler.toml has real
(non-placeholder) KV namespace + R2 bucket bindings, and that the
Worker code references the same binding names. Does NOT deploy -- the
operator deploys with `wrangler deploy` from the cloudflare-worker dir.
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKER_DIR = PROJECT_ROOT / "02_Technical" / "cloudflare-worker"
WRANGLER_TOML = WORKER_DIR / "wrangler.toml"
WORKER_SRC = WORKER_DIR / "src" / "index.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_wrangler_toml_has_no_placeholders():
    """wrangler.toml must not contain any <operator-pastes-here> or
    commented-out binding placeholders."""
    content = _read(WRANGLER_TOML)
    assert "<operator-pastes-here>" not in content, (
        "wrangler.toml still has a placeholder -- fill in the real KV id"
    )
    assert "<operator" not in content, (
        "wrangler.toml still has an operator placeholder"
    )


def test_wrangler_toml_has_kv_namespace_binding():
    """wrangler.toml must have an uncommented [[kv_namespaces]] block
    with a real 32-char hex id."""
    content = _read(WRANGLER_TOML)
    assert "[[kv_namespaces]]" in content, (
        "wrangler.toml missing [[kv_namespaces]] block (still commented out?)"
    )
    m = re.search(r'\[\[kv_namespaces\]\].*?id\s*=\s*"([a-f0-9]{32})"', content, re.DOTALL)
    assert m, (
        "wrangler.toml KV namespace id must be a 32-char hex string -- "
        "got a placeholder or missing id"
    )
    kv_id = m.group(1)
    assert kv_id != "0" * 32, "KV namespace id is all zeros (placeholder)"


def test_wrangler_toml_has_r2_bucket_binding():
    """wrangler.toml must have an uncommented [[r2_buckets]] block
    with a real bucket name."""
    content = _read(WRANGLER_TOML)
    assert "[[r2_buckets]]" in content, (
        "wrangler.toml missing [[r2_buckets]] block (still commented out?)"
    )
    m = re.search(r'\[\[r2_buckets\]\].*?bucket_name\s*=\s*"([^"]+)"', content, re.DOTALL)
    assert m, "wrangler.toml R2 bucket missing bucket_name"
    assert "ordergetitright" in m.group(1).lower(), (
        f"R2 bucket name should contain 'ordergetitright', got {m.group(1)}"
    )


def test_worker_code_references_kv_binding():
    """The Worker JS code must reference env.UPDATES_KV (the binding
    name in wrangler.toml) -- not a different name."""
    content = _read(WORKER_SRC)
    assert "env.UPDATES_KV" in content, (
        "Worker code does not reference env.UPDATES_KV -- binding name mismatch"
    )


def test_worker_code_has_health_route():
    """The Worker must have a /health route for liveness checks."""
    content = _read(WORKER_SRC)
    assert "/health" in content, "Worker code missing /health route"


def test_worker_code_has_updater_manifest_route():
    """The Worker must have the /:platform/:clientVersion route that
    Tauri's updater polls on app launch."""
    content = _read(WORKER_SRC)
    assert "clientVersion" in content, (
        "Worker code missing the /:platform/:clientVersion updater route"
    )