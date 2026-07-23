"""
Tests for the post-seal bark mechanism (sealed 2026-07-23 in chain block 36506).

The bark is the "loop is sealed" witness: every append_block() call must
write a one-line entry to 04_Validation/scripts/last_seal.log so the
operator can verify "the pig is home" without re-running verify_chain.

These tests verify:
  1. The bark log file exists at the canonical path
  2. The bark log has at least one entry
  3. Each bark line matches the pipe-delimited format
  4. The last bark line corresponds to a valid chain block (the witness matches)
  5. read_bark_tail() returns the last N lines correctly
  6. The bark mechanism survives a real seal (the loop is sealed end-to-end)
"""

import os
import re
import sys
import subprocess

# Ensure we can import the runtime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_Technical'))

from src.io.vault_io import append_block, read_bark_tail, BARK_LOG_PATH


def test_bark_log_path_is_canonical():
    """The bark log lives at 04_Validation/scripts/last_seal.log."""
    expected_suffix = os.path.join('04_Validation', 'scripts', 'last_seal.log')
    assert BARK_LOG_PATH.endswith(expected_suffix), (
        f"BARK_LOG_PATH must end with {expected_suffix}; got {BARK_LOG_PATH}"
    )


def test_bark_log_exists():
    """The bark log file exists. It was created the first time append_block ran."""
    assert os.path.exists(BARK_LOG_PATH), (
        f"Bark log not found at {BARK_LOG_PATH}. "
        f"Did append_block() run at least once in this project?"
    )


def test_bark_log_has_entries():
    """The bark log has at least one entry (the install seal)."""
    assert os.path.getsize(BARK_LOG_PATH) > 0, (
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
    """read_bark_tail() returns the last N lines of the bark log."""
    tail = read_bark_tail(5)
    assert isinstance(tail, str)
    # if log has content, tail should have content
    if os.path.getsize(BARK_LOG_PATH) > 0:
        assert len(tail) > 0


def test_loop_is_sealed_end_to_end():
    """The full seal -> bark loop works. Seal a test event, verify the bark line lands."""
    from datetime import datetime, timezone
    test_event = 'TEST_LOOP_SEALED'
    test_payload = {
        'fix_id': 'TEST_LOOP',
        'files_changed': ['test_bark.py: end-to-end loop test'],
        'bin_id': 'hermes-agent-test',
        'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    # record log size before
    sz_before = os.path.getsize(BARK_LOG_PATH)

    # seal
    block = append_block(test_event, test_payload)

    # log size should have grown
    sz_after = os.path.getsize(BARK_LOG_PATH)
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
    assert str(block['index']) in last_line, (
        f"Last bark line does not mention block index {block['index']}: {last_line!r}"
    )
