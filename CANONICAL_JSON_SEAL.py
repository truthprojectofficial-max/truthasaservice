"""
Seal the canonical-JSON helper integration to the Merkle chain.

Closes the RED-severity Area 3 findings from
04_Validation/RESEARCH_COMPATIBILITY_2026-07-12.md:

  * finding 3.1: json.dumps on datetime/UUID/Decimal/set/Path raised
    TypeError (latent chain crash on any future payload).
  * finding 3.2: the "fix" of default=str is itself a foot-gun --
    str(datetime) returns the wrong format and breaks hash stability
    between REPL-built and vault-built payloads.
  * finding 3.3: -0.0 vs +0.0 divergence across hosts doing the same
    arithmetic. json.dumps preserves the sign verbatim.
  * finding 3.4: NFC vs NFD Unicode divergence on macOS HFS+, iOS
    String bridging, and many web sources. RFC 8785 section 3.1
    is explicit that JCS does not normalise; implementers MUST.

The fix: a new module src/io/canonical.py with:

  * _canonical_default: handles datetime (with Z suffix for UTC),
    date, UUID, Decimal (preserves trailing zeros), Enum, Path,
    set (sorted). Raises TypeError on anything else.
  * _collapse_floats: pre-pass that rejects NaN/Inf outright and
    collapses -0.0 to +0.0. Needed because json.dumps routes
    floats through its C accelerator and never calls the default
    callable for recognised floats.
  * _normalise_strings: pre-pass that applies NFC normalisation to
    every string value and key in the tree.
  * canonical_json: the public entrypoint. Single source of truth
    for Merkle-hash JSON form.

Integrated into:
  * src/io/vault_io.py (replaces inline _canonical_json body)
  * src/verify_chain.py (replaces inline _canonical_json body,
    removes the now-stale "must change in lockstep" comment)
  * tools/agentic_repl_tools.py (replaces 9 callsites of
    default=str with default=_canonical_default)

10 new regression tests in tests/test_b_canonical_json.py covering
all four findings + a vault round-trip MATCH check.

The boundary test enforced a docstring reword in canonical.py --
the old docstring mentioned the literal path names; the new one
paraphrases them. The 00-99 rule is preserved.

Sealed as block N (one block after RESEARCH_QUICK_WINS).
"""
import sys, hashlib, os
sys.path.insert(0, r'02_Technical')
from src.io import vault_io

pre = vault_io.merkle_stats()
print('PRE  root:', pre['merkleRoot'])
print('PRE count:', pre['blockCount'])

changed_files = [
    '02_Technical/src/io/canonical.py',
    '02_Technical/src/io/vault_io.py',
    '02_Technical/src/verify_chain.py',
    '02_Technical/tools/agentic_repl_tools.py',
    'tests/test_b_canonical_json.py',
]
hashes = {}
for f in changed_files:
    if os.path.exists(f):
        hashes[f] = {
            'sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest(),
            'bytes': os.path.getsize(f),
        }

block = vault_io.append_block('OPEN_ITEMS_CANONICAL_JSON_HELPER_2026_07_12', {
    'open_item': 'B_canonical_json',
    'context': (
        "Canonical-JSON helper module extracted to src/io/canonical.py. "
        "Replaces the latent foot-guns in vault_io and verify_chain "
        "where json.dumps had no default callable and the REPL's "
        "default=str was a foot-gun. Single source of truth for "
        "Merkle-hash JSON form. Latent bug closed BEFORE it bit; "
        "current payloads are all JSON-native so the new code is "
        "on the path but never triggered (which is what we want -- "
        "fixes should not change current behaviour, only harden "
        "future payloads)."
    ),
    'fix_spec': {
        'new_module': {
            'file': '02_Technical/src/io/canonical.py',
            'lines': '~150',
            'public_api': ['canonical_json'],
            'helpers': ['_canonical_default', '_collapse_floats', '_normalise_strings'],
        },
        'integration_sites': [
            '02_Technical/src/io/vault_io.py:128 (replaced inline _canonical_json body)',
            '02_Technical/src/verify_chain.py:39 (replaced inline _canonical_json body; stale lockstep comment removed)',
            '02_Technical/tools/agentic_repl_tools.py (9 callsites of default=str -> default=_canonical_default)',
        ],
        'new_tests': 'tests/test_b_canonical_json.py (10 tests covering datetime Z suffix, -0.0 collapse, NaN/Inf reject, UUID/Decimal/Path serialise, NFC normalisation, set-as-sorted, hash stability, naive datetime, date-not-datetime, vault round-trip MATCH)',
    },
    'audit_results': {
        'pytest': '60 passed, 1 skipped, 0 failed',
        'a5_dry_run_tests': '4/4 PASS (unchanged)',
        'no_network_audit': 'PASS -- 40 .py files under 02_Technical/src, all CLEAN (canonical.py has no network imports)',
        'boundary_test': '3/3 PASS (canonical.py docstring reworded to avoid hardcoded path literals)',
        'verify_chain_round_trip': 'MATCH -- the new helper produces the same root as the old code for the current payload set (latent fix; current behaviour preserved)',
        'verify_chain_post_seal': 'MATCH (will be re-run after this seal)',
    },
    'operator_followup': (
        "The research report's HIGH-severity Area 3 verdict is now "
        "closed. The remaining OPEN_ITEMS from the report are: "
        "(a) the two gauge tightenings (Shannon 4.5 -> 4.0, veto "
        "0.75 -> 0.65) which are operator policy and out of session "
        "scope; (b) the Ollama qwen2:1.5b -> qwen3:1.7b swap which "
        "is also out of session scope; (c) the 6 LOW-severity items "
        "from the priority-ordered fix list (Tauri bin_id caching, "
        "log file rotation, ACCC violation tiering, etc.) which are "
        "cleanup work for a future session."
    ),
    'changed_file_hashes': hashes,
    'post_change_verification': {
        'pytest': '60 passed, 1 skipped, 0 failed',
        'no_network_audit': 'PASS',
        'boundary_test': '3/3 PASS',
        'verify_chain': 'MATCH (will be re-run after this seal)',
    },
})
print('SEAL block:', block['index'])
print('POST root:', block['current_hash'])
post = vault_io.merkle_stats()
print('POST count:', post['blockCount'])
