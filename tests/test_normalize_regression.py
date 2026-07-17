"""
Order Get It Right -- normalize_real_world_claim regression test.

The third party (any operator, any future agent) needs the
Form_Entry_Agent.normalize_real_world_claim output to be
deterministic and correct on a known, real-world shaped input.

This test runs the assistant as a subprocess and feeds the
canonical line through the REPL. The boundary test in
test_00_99_boundary.py forbids tests from importing src/, so we
go through the same public surface the third party uses: the
REPL.

The test passes when the parsed product evidence has the
exact fields the third party expects from the canonical line.
"""
import json
import subprocess
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TECHNICAL = PROJECT_ROOT / "02_Technical"
PYTHON_EXE = Path(r"C:\Users\justo\OneDrive\Documents\to the spoils go\Python314\python.exe")

CANONICAL = (
    "Audio Pro W-Gen $599 paid 599 measured 94 dB rated 106 dB "
    "warranty 24 months failed 18 months "
    "3 issues 12 features 1 violation 4 requirements"
)

EXPECTED = {
    "productName": "Audio Pro W-Gen",
    "pricePaid": 599.0,
    "priceAdvertised": 599.0,
    "specClaimed": 106.0,
    "specClaimedUnit": "db",
    "specMeasured": 94.0,
    "warrantyMonths": 24.0,
    "monthsToFailure": 18.0,
    "knownIssues": 3.0,
    "totalFeaturesOrParts": 12.0,
    "regulatoryRequirements": 4.0,
    "violationsFound": 1.0,
}


def _run_assistant(commands):
    proc = subprocess.run(
        [str(PYTHON_EXE), "-m", "src.third_party_assistant"],
        cwd=str(TECHNICAL),
        input="\n".join(commands) + "\n",
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc.stdout, proc.stderr, proc.returncode


def _slice_normalize_json(out):
    """Extract the JSON object that starts with {\n  \"productName\" from the assistant output."""
    idx = out.find("{\n  \"productName\"")
    if idx < 0:
        return ""
    depth = 0
    end = idx
    for i, ch in enumerate(out[idx:], start=idx):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return out[idx:end]


class NormalizeRegression(unittest.TestCase):
    """Regression tests for FormEntryAgent.normalize_real_world_claim."""

    def test_01_normalize_canonical_line(self):
        """The canonical Audio Pro W-Gen line must parse to the expected fields."""
        out, err, rc = _run_assistant([f"normalize {CANONICAL}", "quit"])
        self.assertEqual(rc, 0, f"assistant exited non-zero: {err}")
        slice_ = _slice_normalize_json(out)
        self.assertTrue(slice_, f"normalize JSON not found in output:\n{out}")
        parsed = json.loads(slice_)
        for key, expected_value in EXPECTED.items():
            self.assertEqual(
                parsed.get(key),
                expected_value,
                f"normalize field {key!r} expected {expected_value!r} got {parsed.get(key)!r}",
            )

    def test_02_normalize_determinism(self):
        """Same input twice = same output twice. Bit-for-bit deterministic."""
        out1, _, _ = _run_assistant([f"normalize {CANONICAL}", "quit"])
        out2, _, _ = _run_assistant([f"normalize {CANONICAL}", "quit"])
        self.assertEqual(_slice_normalize_json(out1), _slice_normalize_json(out2))


if __name__ == "__main__":
    unittest.main()
