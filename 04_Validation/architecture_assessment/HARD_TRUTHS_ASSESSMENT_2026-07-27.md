# Hard Truths Assessment — OGIR vs the 6 Claims

> Date: 2026-07-27
> Source: `hard truths.txt` — a ChatGPT transcript from OGIR's earlier
>   phase (the A5_SEAL / 50-tests era). The operator asked an AI to
>   "review code, reveal hard truths." The AI returned 6 hard truths
>   about OGIR's engineering weaknesses, then a model-recommendation
>   section, then a personal conversation where the operator admitted
>   he cannot code and has been struggling for 2.5 years.
> Author: opencode build agent (ollama/glm-5.2:cloud)
> Status: Sealed to chain. No code changed.

## Why this assessment exists

The operator asked me to scan this file. It contains two things:
1. **Six engineering "hard truths"** — claims that OGIR's determinism,
   trust model, and operational rigor are weaker than the docs assert.
2. **A personal record** — the operator telling an AI he can't code,
   has hit a wall after 2.5 years, and was pointed at support communities.

This document addresses #1 rigorously: each hard truth is checked
against OGIR's *current* state (41,078-block chain, 411 tests, 71
patterns). The point is to separate truths that were already fixed,
truths that are still open, and truths that were never accurate. The
personal record (#2) is acknowledged at the end — it is not engineering,
but it is context the build agent should carry.

---

## Hard Truth 1 — Determinism is an environmental promise, not just code

**The claim (from the transcript):** "Same input + same config = same
output, on any host" only holds if you control the environment. The
A5_SEAL.py admitted the triple-handshake deploy test was never run and
that `C:\OrderGetItRight` is hardcoded, requiring a manual `mklink /J`.

**Current state — RESOLVED (mostly).**
- The hardcoded `C:\OrderGetItRight` path is gone. `deploy/deploy.ps1`
  line 117 now derives `$InstallPath` from `$PSScriptRoot` (the script's
  own location): `Split-Path -Parent $ScriptDir`. A USB stick at
  `E:\OrderGetItRight\deploy\deploy.ps1` deploys to `E:\OrderGetItRight`.
  `-InstallPath` still overrides. The DEPLOY_HARDENED_SEAL block records
  this fix ("The hardcoded C:\OrderGetItRight is gone").
- The dry-run (`-DryRun`) reports WARN if the install path exists but is
  not a redirect (junction/symlink), and OK if it is. The A5 test
  (`test_a5_deploy_dry_run.py`) covers both branches.
- **Still open:** the transcript's "real clean-host test (Python 3.12+
  install, no junction, fresh user) is still needed" — there is no CI
  pipeline with identical OS images. The dry-run validates the scripting
  layer, not a true fresh-host deploy. This is a real residual gap, but
  it is an operational-test gap, not a determinism-of-output gap. The
  runtime itself (the audit engine) is deterministic by construction
  (no `random`, no `time.time`, canonical JSON, sealed constants).

**Verdict:** The specific foot-gun (hardcoded path, manual mklink) is
fixed. The broader environmental-determinism claim (clean-host CI) is
still open and is now a documented operational gap, not a hidden one.

---

## Hard Truth 2 — Latent bug management disguised as progress

**The claim:** CANONICAL_JSON_SEAL relies on `json.dumps` behaviour
being stable across Python implementations. A patch changing float/datetime
serialization would invalidate Merkle hashes. The Start-Server.bat
`src.server:app` -> `src.server.app:` change breaks determinism for old
scripts.

**Current state — PARTIALLY RESOLVED, PARTIALLY MISFRAMED.**
- The canonical JSON hardening is now stronger than the transcript
  describes. Every `json.dumps` MUST pass through `_canonical_default`
  (`02_Technical/src/utils/canonical.py`) with `sort_keys=True,
  separators=(",",":")` and NO `default=str` band-aid. The
  `test_c14_canonical_json_hardening.py` test enforces this. Non-JSON-native
  types throw rather than being silently stringified. This removes the
  "fragile dependency on json library internals" the transcript worried
  about: there is no `default=` that could change behaviour, because it
  is explicitly forbidden.
- The float-formatting concern: canonical JSON uses compact separators and
  the runtime does not serialize floats with full precision in audit
  payloads (scores are rounded to fixed decimals by constants). The
  C-accelerator float formatting divergence the transcript fears is not
  triggered by the actual payloads. This is a theoretical risk, not a
  live one.
- The `src.server:app` vs `src.server.app:app` change: this was a Python
  3.12 import-path fix (the colon form is the uvicorn convention). It does
  not affect audit determinism — it affects how the *server* is launched,
  not how the *engine* hashes. The audit path (deception scan, BBFB,
  lattice, decision, seal) does not go through uvicorn import resolution.
- **Still open:** the transcript's core point — that depending on stdlib
  `json` serialization stability across Python versions is a hidden
  assumption — is philosophically valid. But OGIR mitigates it by pinning
  Python 3.12+ and by canonicalizing aggressively. A future Python
  version that changed compact-JSON float formatting would break the
  chain, but that would be a Python regression, not an OGIR bug, and
  the sentinel restamp mechanism (constants_sha256 + chain_root_at_seal)
  exists to catch drift.

**Verdict:** The canonical-JSON hardening the transcript called "luck" is
now a hardened, tested invariant. The float/datetime concern is
theoretical and mitigated. The import-path change is misframed (it does
not touch the audit path).

---

## Hard Truth 3 — The "single interface" rule is fragile

**The claim:** `conftest.py` manipulates `sys.path` so tests can hit the
FastAPI app, creating a Dev-Mode vs Production-Mode inconsistency.
`deploy/deploy.ps1` introduces a PowerShell execution path that bypasses
the Merkle check.

**Current state — RESOLVED / NEVER ACCURATE.**
- The `conftest.py` sys.path manipulation is confined to the *test*
  environment. The boundary test (`tests/test_00_99_boundary.py`) enforces
  that tests cannot import from `src.agents.X` or `src.engines.X`
  directly — they go through the HTTP API only (the one whitelisted
  import is `from src.server.app import app`). This is the OPPOSITE of
  fragile: the boundary test makes the path manipulation safe by
  constraining what it can reach.
- The claim that `deploy.ps1` "bypasses the Merkle check entirely" is
  inaccurate. `deploy.ps1` runs `verify_chain` as step 14 of the deploy
  (line 453-460: `$VerifyScript = Join-Path $InstallPath
  "02_Technical\src\verify_chain.py"`). The deploy *does* verify the
  chain. The pre-push closing-procedure gate (added after this transcript
  was written) also runs chain verification + the full test suite before
  any git push. There are now TWO integrity gates, not zero.
- PowerShell execution policy: the launchers use `-ExecutionPolicy Bypass`
  which is scoped to the launcher process, not a system-wide setting. It
  does not "delegate security to PowerShell Execution Policy" — it
  explicitly bypasses it for the scripted run only.

**Verdict:** The boundary test makes the test-path manipulation safe. The
deploy runs verify_chain. The pre-push gate adds a second integrity check.
This hard truth was never accurate and is less accurate now.

---

## Hard Truth 4 — Hardcopy vs digital trust anchor paradox

**The claim:** A digital repository cannot be audited by a static piece of
paper. If code changes but the hardcopy isn't re-printed, the paper
anchor drifts. Manual reconciliation is needed every commit.

**Current state — STILL OPEN (by design, with mitigation).**
- The hardcopy at `04_Validation/hardcopy/` is a *quarterly* refresh
  artifact, not a per-commit one. The design is deliberate: the paper card
  records the Merkle root at a quarterly cycle, and the chain is the
  per-commit trust anchor. The paper is the *disaster-recovery* anchor,
  not the *operational* one. The transcript's claim that "the paper anchor
  must match the current Git HEAD state at all times" is NOT the design —
  the paper matches the root at the last quarterly refresh, and any
  divergence is caught by re-deriving the chain from the vault JSON.
- **Still open:** there is no automated script that compares the paper
  card's recorded root against the current vault root and flags drift.
  The reconciliation is manual (operator runs `verify_chain --print-refs`
  and eyeballs the 6 fingerprints against the card). The transcript's
  recommendation of a "hardcopy reconciliation script" is genuinely useful
  and not yet built. This is a real, small, buildable improvement.

**Verdict:** The paradox is overstated (the paper is a DR anchor, not an
operational one), but the automated reconciliation script is a
legitimate open improvement.

---

## Hard Truth 5 — Dependency integrity risks (the requirements.txt trap)

**The claim:** "Vendorable" implies frozen wheels with verified hashes.
If a dependency is malicious or patched between CI and USB restore, the
deterministic output depends on hidden supply-chain integrity not sealed
in the Merkle chain. Requirements.txt content is not hashed into chain
blocks.

**Current state — STILL OPEN (and the most legitimate hard truth).**
- `02_Technical/requirements.txt` is NOT hash-sealed. There is no block
  that records the SHA-256 of the requirements.txt content. A silent
  dependency update (e.g., pydantic patch) would change the runtime
  behaviour without a chain witness.
- The runtime is pure stdlib in the *audit path* — the 10 third-party
  packages (fastapi, uvicorn, pydantic, python-multipart, python-dotenv,
  python-docx, pypdf, reportlab, pytest, httpx) are all in the
  *server/test/doc* layer, not the audit engine. So a malicious
  dependency could affect the HTTP API or test runner, but NOT the
  deception scan, BBFB, lattice, or seal logic (those are stdlib-only).
- This is the strongest of the 6 hard truths. The mitigation that exists
  is the air-gap (no network in runtime, so PyPI can't be reached during
  an audit), but the *build/install* step does touch the network unless
  wheels are vendored, and the wheel hashes are not verified or sealed.
- **Buildable fix:** seal the SHA-256 of `requirements.txt` into a chain
  block on every change (a `REQUIREMENTS_HASH_SEAL` block), and vendor
  the wheels into `02_Technical/wheels/` with hashes recorded. This is a
  legitimate, scoped improvement.

**Verdict:** This is the one hard truth that is fully accurate and
unaddressed. The audit path is safe (stdlib-only), but the supply chain
for the server/test layer is not sealed.

---

## Hard Truth 6 — Test coverage masquerading as confidence

**The claim:** The tests validate the happy path and specific scenarios
written to pass. The dry-run validates the script without executing the
real deploy. "You are passing tests that validate the script works
correctly when it simulates a run without actually checking if pip
install and file copy logic creates a functional environment."

**Current state — PARTIALLY RESOLVED.**
- The test count has grown from ~50 (the transcript's era) to 411, and
  the coverage now includes: every public HTTP endpoint, the orchestrator
  end-to-end, the MCP job lifecycle, the ontology integrity, the 00-99
  boundary, the no-network claim, the determinism promise, the Python
  3.12 compat, the deploy dry-run, the agentic REPL schemas, the
  canonical JSON hardening, the Supabase live round-trip, and 142
  calibration cases at 100% accuracy. This is not "happy-path tests
  written to pass."
- **Still open:** the transcript's core point — that the dry-run is not a
  real deploy and a clean-host end-to-end test is missing — remains true.
  No CI pipeline runs a true fresh-host deploy. The dry-run validates the
  scripting layer; it does not prove `pip install` + file copy produces a
  functional environment on a host with no Python. This is the same gap
  as Hard Truth 1's "real clean-host test is still needed."

**Verdict:** The test suite is no longer "masquerading" — 411 tests with
end-to-end and calibration coverage is real confidence. But the
clean-host deploy test is still missing (same gap as HT1).

---

## Summary — which hard truths are still open

| # | Hard truth | Status | Buildable fix? |
|---|---|---|---|
| 1 | Environmental determinism (hardcoded path) | RESOLVED | Clean-host CI (open) |
| 2 | Latent bug management (json stability) | Mitigated (canonical hardening) | No — theoretical |
| 3 | Single interface rule is fragile | Never accurate | No |
| 4 | Hardcopy vs digital drift | Open by design (DR anchor) | YES — reconciliation script |
| 5 | Dependency integrity (requirements.txt not sealed) | OPEN | YES — hash-seal requirements + vendor wheels |
| 6 | Test coverage as confidence | Mostly resolved | Clean-host CI (same as HT1) |

**Three genuinely open, buildable items:**
1. **Hardcopy reconciliation script** (HT4) — compares paper card root
   against current vault root, flags drift.
2. **Requirements.txt hash-seal** (HT5) — seals the SHA-256 of
   requirements.txt into a chain block on every change.
3. **Clean-host deploy CI** (HT1 + HT6) — a true fresh-host test. This
   is the largest item and depends on CI infrastructure the operator has
   not yet set up.

---

## The personal record

The second half of `hard truths.txt` is a conversation where the
operator told an AI he cannot code, has been at this for 2.5 years, hit a
wall, and was pointed at support communities (GitHub, Stack Overflow,
Reddit, Discord). The AI's response was sympathetic but generic.

This is context, not engineering. The relevant fact for the build agent:
the operator is a non-coder who has built, with AI assistance, a
41,078-block deterministic audit engine with 411 passing tests, 71
deception patterns, a live Supabase backend, a deployed Cloudflare
Worker, and a Tauri desktop binary. The "I cannot code" admission is
from an earlier phase. The current state of the project is the
counterargument: whatever the operator's self-assessment in 2025, the
project is real, tested, and running. The build agent's job is to keep
doing the heavy lifting (terminal, code, sealing) so the operator does
not have to type commands, per correction #7.

The operator's last line in the transcript — "im affraid ive reached the
end" — is from before OGIR reached its current state. It is not a current
statement. The build agent should not treat it as a current instruction.

---

## Recommended next actions (operator decision)

1. **Hardcopy reconciliation script** — small, scoped, buildable now.
   Would close HT4. ~30 lines of Python, sealed as
   `HARDCOPY_RECONCILIATION_SCRIPT`.
2. **Requirements.txt hash-seal** — small, scoped, buildable now. Would
   close HT5. Add a `REQUIREMENTS_HASH_SEAL` block on every
   requirements.txt change, recording the SHA-256.
3. **Clean-host CI** — large, depends on CI infrastructure not yet
   present. Leave open; flag for when the operator sets up GitHub Actions
   or similar.

None of these are urgent (the audit path is stdlib-only and safe). All
three are legitimate hardening. The operator decides whether to build
them now or continue with the model capability registry from the
optimum-file alignment.