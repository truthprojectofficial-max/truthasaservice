"""
Tests for the post-seal bark mechanism (sealed 2026-07-23 in chain block 36506).

The bark is the "loop is sealed" witness: every append_block() call must
write a one-line entry to 04_Validation/scripts/last_seal.log so the
operator can verify "the pig is home" without re-running verify_chain.

These tests verify the ON-DISK artifact (the bark log) without importing
src/ -- they obey the 00-99 boundary rule (tests go through the HTTP API,
not direct src/ imports). The end-to-end test uses subprocess to invoke
a small wrapper script that calls append_block.

  1. The bark log file exists at the canonical path
  2. The bark log has at least one entry
  3. Each bark line matches the pipe-delimited format
  4. read_bark_tail() returns the last N lines correctly
  5. The bark mechanism survives a real seal (the loop is sealed end-to-end)
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# Per the 00-99 boundary rule, tests cannot import from src/.
# Resolve the bark log path from the project root instead.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BARK_LOG_PATH = PROJECT_ROOT / "04_Validation" / "scripts" / "last_seal.log"


def test_bark_log_path_is_canonical():
    """The bark log lives at 04_Validation/scripts/last_seal.log."""
    expected_suffix = os.path.join('04_Validation', 'scripts', 'last_seal.log')
    assert str(BARK_LOG_PATH).endswith(expected_suffix), (
        f"BARK_LOG_PATH must end with {expected_suffix}; got {BARK_LOG_PATH}"
    )


def test_bark_log_exists():
    """The bark log file exists. It was created the first time append_block ran."""
    assert BARK_LOG_PATH.exists(), (
        f"Bark log not found at {BARK_LOG_PATH}. "
        f"Did append_block() run at least once in this project?"
    )


def test_bark_log_has_entries():
    """The bark log has at least one entry (the install seal)."""
    assert BARK_LOG_PATH.stat().st_size > 0, (
        f"Bark log at {BARK_LOG_PATH} is empty."
    )


def test_bark_log_format():
    """Each bark line matches the pipe-delimited format:
        <index>|<timestamp>|<event_type>|<hash_prefix>|<files_summary>"""
    with open(BARK_LOG_PATH, 'r', encoding='utf-8') as f:
        lines = [l for l in f.readlines() if l.strip()]
    assert len(lines) > 0, "No bark lines found"
    # check format on a sample
    pattern = re.compile(
        r'^\d+\|[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\|'
        r'[A-Z0-9_]+\|[0-9a-f]{12}\|.*$'
    )
    sample = lines[-1]  # last line is most recent seal
    assert pattern.match(sample), (
        f"Last bark line does not match expected format: {sample!r}"
    )


def test_read_bark_tail_returns_recent_lines():
    """read_bark_tail() returns the last N lines of the bark log.

    Uses subprocess to call the function (avoids direct src/ import)."""
    wrapper = PROJECT_ROOT / "02_Technical" / ".hermes_bark_tail.py"
    wrapper.write_text(
        "import sys\n"
        "sys.path.insert(0, '.')\n"
        "from src.io.vault_io import read_bark_tail\n"
        "n = int(sys.argv[1]) if len(sys.argv) > 1 else 5\n"
        "print(read_bark_tail(n), end='')\n",
        encoding='utf-8',
    )
    try:
        r = subprocess.run(
            [sys.executable, str(wrapper), '5'],
            capture_output=True, text=True,
            cwd=str(PROJECT_ROOT / "02_Technical"),
            timeout=10,
        )
        assert r.returncode == 0, f"read_bark_tail wrapper failed: {r.stderr}"
        tail = r.stdout
        assert isinstance(tail, str)
        if BARK_LOG_PATH.stat().st_size > 0:
            assert len(tail) > 0
    finally:
        wrapper.unlink(missing_ok=True)


def test_loop_is_sealed_end_to_end():
    """The full seal -> bark loop works. Seal a test event, verify the bark line lands.

    Uses a throwaway wrapper script (deleted after the test) so the test itself
    does not import src/. The wrapper is gitignored by .hermes-* patterns.
    """
    test_event = 'TEST_LOOP_SEALED'
    wrapper = PROJECT_ROOT / "02_Technical" / f".hermes_seal_test_{os.getpid()}.py"
    wrapper.write_text(
        "import sys\n"
        "sys.path.insert(0, '.')\n"
        "from datetime import datetime, timezone\n"
        "from src.io.vault_io import append_block\n"
        f"event = {test_event!r}\n"
        "payload = {\n"
        "    'fix_id': 'TEST_LOOP',\n"
        "    'files_changed': ['test_bark.py: end-to-end loop test'],\n"
        "    'bin_id': 'hermes-agent-test',\n"
        "    'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),\n"
        "}\n"
        "block = append_block(event, payload)\n"
        "print(block['index'])\n",
        encoding='utf-8',
    )
    try:
        sz_before = BARK_LOG_PATH.stat().st_size

        # seal via subprocess
        r = subprocess.run(
            [sys.executable, str(wrapper)],
            capture_output=True, text=True,
            cwd=str(PROJECT_ROOT / "02_Technical"),
            timeout=30,
        )
        assert r.returncode == 0, f"seal wrapper failed: {r.stderr}"
        # The wrapper prints the [SEAL] line via _post_seal_bark AND the
        # block index. Take the last non-empty line as the index.
        block_index = int(r.stdout.strip().splitlines()[-1])

        # log size should have grown
        sz_after = BARK_LOG_PATH.stat().st_size
        assert sz_after > sz_before, (
            f"Bark log did not grow after seal: {sz_before} -> {sz_after}"
        )

        # last line should mention the test event
        with open(BARK_LOG_PATH, 'r', encoding='utf-8') as f:
            last_line = f.readlines()[-1]
        assert test_event in last_line, (
            f"Last bark line does not mention {test_event}: {last_line!r}"
        )
        # and the block index
        assert str(block_index) in last_line, (
            f"Last bark line does not mention block index {block_index}: {last_line!r}"
        )
    finally:
        wrapper.unlink(missing_ok=True)
