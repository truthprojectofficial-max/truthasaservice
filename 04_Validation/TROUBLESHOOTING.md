# TROUBLESHOOTING

A catalog of failure modes the project has actually encountered,
with symptom / root cause / fix recipes. Each recipe ends with
"if this doesn't fix it, stop and check [doc]". This document
assumes you have already read `INTRODUCTION.md` and have
the build running on your machine. If you have not, start there.

This is a lossless catalog. Every entry below has a chain
reference or a file:line reference so a future operator can
verify the diagnosis. New failure modes should be added
following the same pattern (SYMPTOM / ROOT CAUSE / FIX / ESCALATE).

---

## HOW TO USE THIS DOCUMENT

Look up the SYMPTOM. Each entry is structured:

  - **SYMPTOM** -- the visible failure (error message, wrong
    output, missing file, blank UI, port refusal, etc.)
  - **ROOT CAUSE** -- the actual cause in the code, the path,
    the env var, or the data file
  - **FIX** -- the minimal, lossless recipe to recover
  - **ESCALATE** -- where to look if the fix does not work
    (a doc, a file:line, a Merkle seal, a contact)

If your failure is not listed, run the standard opening
ritual first (see INTRODUCTION.md Step 2 and Step 3), and
if the build is still green, the issue is in your input data
or your environment, not the program. If the build is red,
write down the exact error message, the exact command, and
the Python and OS versions, then escalate per the last entry
in this document.

---

## 1. CHAIN VERIFICATION

### 1.1 `verify_chain` prints BROKEN with a first broken block index

  - **SYMPTOM**
    ```
    RESULT: BROKEN at block <N>
    ```
    where `<N>` is the index of the first block whose hash
    no longer matches the recomputed hash.

  - **ROOT CAUSE**
    A file under `03_Vault/` (the chain registry) was
    modified, deleted, or truncated outside the
    `vault_io.append_block` API. The chain is content-
    addressed; any byte change cascades forward.

  - **FIX**
    Do not run any further audit. The chain is the proof;
    the proof is broken.
    1. Stop the server (Ctrl+C). Stop any test run.
    2. Find the last printed Merkle root in
       `04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt`.
    3. Restore `03_Vault/facts_registry.json` from the USB
       mirror (`D:\OrderGetItRight\03_Vault\`).
    4. Re-run `python -m src.verify_chain` and confirm
       `RESULT: MATCH`.
    5. Re-mirror the canonical source back to the USB.

  - **ESCALATE**
    If the USB mirror is also broken or out of date, see
    `04_Validation/hardcopy/HARD_COPY_BACKUP_PLAN_1-2-3.txt`
    Step 3.4 (offsite restore).

### 1.2 `verify_chain` errors with `FileNotFoundError` on `constants.py`

  - **SYMPTOM**
    ```
    FileNotFoundError: [Errno 2] No such file or directory:
    'C:\\...\\02_Technical\\config\\constants.py'
    ```
    or similar, when running `python -m src.verify_chain
    --print-refs`. The bare `verify_chain` (without
    `--print-refs`) still prints MATCH.

  - **ROOT CAUSE**
    The `--print-refs` code path in `src/verify_chain.py`
    uses a path-computation that drops the
    `OrderGetItRight` segment when the project root
    contains a space (e.g. the OneDrive path
    `Documents\My Project\OrderGetItRight`). This is a
    long-standing bug in the print-refs helper, not in
    the chain.

  - **FIX**
    Use the bare `python -m src.verify_chain` to check
    chain integrity. To re-derive the six reference
    fingerprints, run the recipes in
    `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` PART 3
    directly (they use a `Path('.')`-relative glob that
    handles the space correctly).

  - **ESCALATE**
    This is tracked as a known issue. The fix is to
    change `verify_chain.py` to use a more robust path
    computation; that is a code change requiring a
    sealed SOURCE_TREE_BUMP block.

### 1.3 `verify_chain` reports a block count that does not match the docs

  - **SYMPTOM**
    `Block count: 6870` (live) but the printed
    QUICK_REFERENCE_CARD says 6585. Or any other
    mismatch.

  - **ROOT CAUSE**
    The chain grows with every `vault_io.append_block`
    call. Automatic SHUTDOWN seals from the FastAPI
    lifespan handler add 1-3 blocks per pytest run.
    A mismatch is normal and means the docs are stale,
    not that the chain is broken.

  - **FIX**
    Refresh the docs (YELLOW_RIBBON.md, OPEN_ITEMS, and
    QUICK_REFERENCE_CARD) against the live root. The
    refresh recipe is in
    `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` PART 3
    and the chain refresh ritual in
    `HANDOVER_NEXT_SESSION_2026-07-16.md` Section 8.

  - **ESCALATE**
    If the docs say e.g. 6965 and the chain says 6870,
    the chain went BACKWARDS. That is impossible by
    construction. Investigate before any further
    action; the USB mirror may have a stale copy.

---

## 2. PYTEST COLLECTION

### 2.1 `pytest` reports `0 collected` or `errors during collection`

  - **SYMPTOM**
    `pytest` exits with `0 collected, X errors` and the
    traceback names a specific file:line.

  - **ROOT CAUSE**
    An import error or syntax error in that named file.
    The first line of the traceback is the regression.

  - **FIX**
    1. Read the file:line in the traceback.
    2. Open the file at that line. Confirm the syntax
       or import is intact.
    3. If the file is `src/server/app.py` and the
       error is `IndentationError: unexpected indent`
       around the Changelog & Incident Audit section,
       see entry 2.2 below.
    4. If the error is `ModuleNotFoundError: No module
       named 'X'`, install the missing dependency per
       `02_Technical/requirements.txt`:
       `pip install -r 02_Technical/requirements.txt`.

  - **ESCALATE**
    If the import error is for a stdlib module (e.g.
    `json`, `pathlib`, `hashlib`), the Python
    interpreter is broken. Reinstall Python 3.12+ or
    use the operator's local copy at
    `C:\Users\justo\OneDrive\Documents\to the spoils
    go\Python314\python.exe`.

### 2.2 The 2026-07-12 IndentationError in `src/server/app.py`

  - **SYMPTOM**
    `pytest` reports
    ```
    File ".../src/server/app.py", line 314
        _CHANGELOG_PATH = Path(os.environ.get("OGIR_CHANGELOG", PROJECT_CHANGELOG_DIR))
    IndentationError: unexpected indent
    ```
    All tests in `tests/` silently fail to collect. Pytest
    reports `0 collected`. The web UI works for static
    pages, but the changelog and every endpoint that
    touches the audit cycle are dead.

  - **ROOT CAUSE**
    The Changelog & Incident Audit helpers
    (`_read_changelog`, `_write_changelog_entry`) had
    their bodies half-deleted. Sealed at block 416 on
    2026-07-12. The fix is in the chain. If you are
    seeing this again, the patch was reverted or
    partially overwritten.

  - **FIX**
    Compare `02_Technical/src/server/app.py` against
    the chain's sealed version (the `previous_hash` of
    the next block after 416 is the SHA-256 of the
    post-fix `app.py`). The full byte-for-byte
    recovery recipe is in the long-form session
    transcript (JSON line at the chain block 416
    payload). Re-apply the patch, re-run pytest,
    expect 86/1.

  - **ESCALATE**
    If the chain itself has been reset, this fix
    recipe is no longer recoverable from the chain.
    The complete patch is in
    `04_Validation/hardcopy/HARD_COPY_BACKUP_PLAN_1-2-3.txt`
    (older versions) and was also included in the
    2026-07-12 seal payload (block 416).

### 2.3 Pytest reports a count significantly lower than 86

  - **SYMPTOM**
    `pytest` reports e.g. "6 passed" when the expected
    count is 86.

  - **ROOT CAUSE**
    You are running pytest from the wrong directory.
    The canonical `tests/` lives at the project root
    (`OrderGetItRight/tests/`), not at
    `02_Technical/tests/`. The `02_Technical/tests/`
    directory is a stale mirror that was hard-deleted
    in the TAURI_REBUILT_FOR_UI_REDESIGN_2026_07_17
    seal (block 6775, A10 in OPEN_ITEMS). If it has
    reappeared, the rebuild was incomplete.

  - **FIX**
    Always run pytest from the project root:
    ```
    cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
    python -m pytest tests/ -q
    ```
    If you see `02_Technical/tests/` reappear, the
    checkout was restored from a backup that pre-dates
    the A10 closure. Re-apply the TAURI_REBUILT seal
    steps from the chain.

  - **ESCALATE**
    This rule is also captured in
    `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` Part 1
    (A10, closed 2026-07-17).

### 2.4 The boundary test fails

  - **SYMPTOM**
    `tests/test_00_99_boundary.py` fails with a
    message that names a forbidden import path.

  - **ROOT CAUSE**
    The 00-99 spatial boundary restricts which modules
    `tests/` can import. The allow-list is exactly
    two symbols:
      - `from src.server.app import app`
      - `from src.utils.canonical.canonical_dumps`
    Any other `from src.X` import in `tests/` fails the
    boundary. The constraint enforces that the test
    surface exercises the HTTP and public-API endpoints
    only -- it must not reach into internal state.

  - **FIX**
    1. Identify the import named in the failure.
    2. Refactor the test to use the HTTP surface
       (FastAPI TestClient against the named endpoint)
       instead of importing the internal module.
    3. If the test genuinely needs internal state,
       write it as a behavioural test that drives the
       same code path through the public API.

  - **ESCALATE**
    The boundary test docstring is in
    `tests/test_00_99_boundary.py`. The architectural
    rationale is in
    `04_Validation/INTELLECTUAL_PROPERTY_RIGHTS.txt`
    Section "(e) Right to extend" and the on-disk
    history is in
    `04_Validation/AUDIT_BLACK_BOX_TRACE_2026-07-17.md`.

### 2.5 Pytest reports 1 failed at `test_d5_agentic_repl.py`

  - **SYMPTOM**
    ```
    FAILED tests/test_d5_agentic_repl.py::...
    ```
    The test requires a tool-capable Ollama model and
    the FastAPI server running on `127.0.0.1:3000`.

  - **ROOT CAUSE**
    Either the Ollama model is not loaded, the FastAPI
    server is not running, or the default model is not
    tool-capable. The default model is `qwen3.5:9b`
    (changed from `tcoxav/aegis:latest` on 2026-07-17
    during the C2_C3_C4 reconciliation; the aegis
    reference is a legacy note in
    `HANDOVER_NEXT_SESSION_2026-07-16.md` line 56-59).

  - **FIX**
    1. Start the FastAPI server in another terminal:
       `python -m uvicorn src.server.app:app --port 3000`
    2. Confirm the Ollama model is loaded:
       `ollama list` -- look for `qwen3.5:9b`.
    3. If absent, pull it: `ollama pull qwen3.5:9b`.
    4. Re-run the test.

  - **ESCALATE**
    If the test fails consistently even with the
    server up and the model loaded, the test is
    host-dependent and is allowed to be skipped
    (the canonical expectation is 86 passed + 1
    skipped, not 87 passed). Mark it as
    `@pytest.mark.skip(...)` with a clear reason.

---

## 3. FASTAPI SERVER

### 3.1 Server starts but the browser shows JSON instead of HTML

  - **SYMPTOM**
    `GET http://127.0.0.1:3000/` returns
    `{"status": ...}` (a 50-100 byte JSON body) instead
    of the single-page operating surface (a 58 KB HTML
    body).

  - **ROOT CAUSE**
    The `STATIC_DIR` path in
    `02_Technical/src/server/app.py` is computed with
    the wrong number of `.parent` calls. The correct
    path is
    `Path(__file__).parent.parent.parent / "web"`
    (three levels up: `app.py` -> `server/` -> `src/`
    -> `02_Technical/`), resolving to
    `02_Technical/web/`. A common regression is
    `.parent.parent` (two levels), which lands on
    `02_Technical/src/web/` -- a directory that does
    not exist. The `if STATIC_DIR.exists():` guard
    fails silently and the JSON fallback wins.

  - **FIX**
    1. Open `02_Technical/src/server/app.py` around
       the `STATIC_DIR` constant.
    2. Confirm the path has THREE `.parent` calls
       before the `/ "web"` join.
    3. Confirm `02_Technical/web/index.html` exists
       (it should be a 58 KB file).
    4. Re-run `python -m pytest tests/test_static_dir.py -v`
       to confirm the regression test passes.

  - **ESCALATE**
    This bug class was fixed at the
    UI_OPERATOR_FACING_REDESIGN_2026_07_17 seal
    (block 6584, A7 in OPEN_ITEMS). The regression
    test is `tests/test_static_dir.py` (4 tests, all
    boundary-compliant). If the test passes but the
    bug is still visible, the issue is in the Tauri
    shell's `frontendDist` config -- see entry 6.1.

### 3.2 Server refuses to start with `Address already in use`

  - **SYMPTOM**
    ```
    OSError: [WinError 10048] Only one usage of each
    socket address (protocol/network address/port) is
    normally permitted
    ```
    or
    ```
    ERROR: [Errno 98] Address already in use
    ```

  - **ROOT CAUSE**
    Another process owns port 3000. Common culprits:
    a prior uvicorn that was not killed cleanly, the
    Tauri shell's embedded server, a long-running
    pytest that started a server fixture without
    stopping it, or a previous session that was
    killed with Task Manager instead of Ctrl+C.

  - **FIX**
    Windows:
    ```
    netstat -an | findstr :3000
    ```
    Find the row in `LISTENING` state. Note the PID
    in the last column. Kill the process:
    ```
    taskkill /F /PID <pid>
    ```
    POSIX:
    ```
    lsof -i :3000
    kill <pid>
    ```
    If you cannot kill the process (e.g. it is a
    system service), start uvicorn on a different
    port and adjust the browser URL:
    ```
    python -m uvicorn src.server.app:app --port 3001
    ```
    and open `http://127.0.0.1:3001/`.

  - **ESCALATE**
    If the port is held by a service you do not own
    (e.g. IIS on Windows Server), change the default
    port in the launcher and the documentation.
    The default port is 3000 throughout the project;
    changing it requires a sealed CONSTANTS_BUMP.

### 3.3 Server starts but no audit appears in the web UI

  - **SYMPTOM**
    The UI loads, the four-gate pipeline view is
    visible, but pressing GO returns an error or
    the pipeline never populates. The browser
    console (F12) shows a network error or a 500
    from `/api/orchestrator/process`.

  - **ROOT CAUSE**
    The orchestrator short-circuits if a CRITICAL
    deception pattern fires. The response shape is
    different from the full pipeline shape: it
    contains `finalAction: "REFUSED"`, `reason`,
    `deceptionScore`, `patternsFired`, and
    `ledgerRoot` -- but no `deceptionGate`,
    `bbfbGate`, or `valuationGate` keys. An older
    version of the UI assumed the full-pipeline
    shape and crashed silently on REFUSED.

  - **FIX**
    1. Open `02_Technical/web/index.html`.
    2. Find the `loadRunIntoView` function (around
       the bottom of the inline `<script>`).
    3. Confirm it handles BOTH response shapes
       (the full pipeline AND the refusal short-
       circuit). The pattern to look for is
       `if (run.finalAction === "REFUSED") { ... }
       else { /* full pipeline render */ }`.
    4. The behaviour is sealed at the
       UI_OPERATOR_FACING_REDESIGN_2026_07_17 seal
       (block 6584).

  - **ESCALATE**
    If the refusal is unexpected (you do not see
    a CRITICAL pattern in the input text), it may
    be a false positive. Run the same input through
    the REPL:
    ```
    python -m src.third_party_assistant
    onyx> audit <text>
    ```
    The REPL prints the full pattern list with
    confidence scores. If a pattern is firing with
    high confidence on innocent text, this is an
    ontology refinement candidate (R1-R4 from the
    E4 pre-2021 reference calibration, sealed at
    block 6,584).

---

## 4. USB MIRROR

### 4.1 USB chain verify returns a different root than source

  - **SYMPTOM**
    ```
    cd D:\OrderGetItRight\02_Technical
    python -m src.verify_chain
    ```
    returns a different Merkle root than the source
    canonical. The source chain says MATCH and the
    USB chain says MATCH, but the two roots are
    different.

  - **ROOT CAUSE**
    The USB mirror is stale. It was last copied
    before the source chain was updated. The mirror
    must be re-synced with the canonical source.

  - **FIX**
    From the project root, run:
    ```
    robocopy . D:\OrderGetItRight /MIR /XD __pycache__ target node_modules .pytest_cache
    ```
    or for a one-off re-sync, the recipes in
    `02_Technical/DEPLOYMENT.md`. After the copy,
    re-run the USB chain verify and confirm the
    two roots match.

  - **ESCALATE**
    If the chain roots still differ after a clean
    re-mirror, the file system is doing something
    unexpected (NTFS alternate data streams, symlink
    vs junction, OneDrive hydration). Re-burn the
    USB from scratch per
    `04_Validation/hardcopy/HARD_COPY_BACKUP_PLAN_1-2-3.txt`
    Step 1.

### 4.2 The `C:\OrderGetItRight` junction is broken

  - **SYMPTOM**
    ```
    cd C:\OrderGetItRight
    The system cannot find the path specified.
    ```
    or the junction resolves to a non-existent
    directory.

  - **ROOT CAUSE**
    The junction was a stale shortcut to the
    pre-fork `.claude/OrderGetItRight` path. The
    2026-07-16 fork resolution moved the canonical
    project to the OneDrive path. The junction was
    fixed at the FORK_RESOLVED_2026_07_16 seal.

  - **FIX**
    As administrator, in an elevated PowerShell:
    ```
    Remove-Item C:\OrderGetItRight -Force
    New-Item -ItemType Junction -Path C:\OrderGetItRight -Target D:\OrderGetItRight
    ```
    Confirm with:
    ```
    Get-Item C:\OrderGetItRight | Select-Object Name,Target,LinkType
    ```
    Expected: `LinkType: Junction` and
    `Target: D:\OrderGetItRight`.

  - **ESCALATE**
    If the junction target also does not exist
    (`D:\OrderGetItRight`), the USB itself is
    missing. Restore from the offsite backup per
    `04_Validation/hardcopy/HARD_COPY_BACKUP_PLAN_1-2-3.txt`
    Step 3.

### 4.3 `robocopy /MIR` deletes files the operator wanted to keep

  - **SYMPTOM**
    Files present on the USB are deleted by the
    mirror because they are not on the source.

  - **ROOT CAUSE**
    `robocopy /MIR` is a true mirror -- it deletes
    destination files that are not on the source.
    This is intentional and is the correct behaviour
    for canonical mirrors, but it is dangerous if
    the USB has operator-created files (e.g. a
    backup of a draft affidavit) that are not on
    the source.

  - **FIX**
    1. Stop the mirror immediately.
    2. Check the destination: any files the mirror
       is about to delete are listed in the robocopy
       output. If those are files you want to keep,
       move them to a folder the mirror does not
       touch (e.g. `D:\OrderGetItRight\notes\`).
    3. Re-run the mirror. The mirror deletes only
       files inside its scope.

  - **ESCALATE**
    The mirror scope is the entire project root.
    Operator files MUST live outside the project
    tree (e.g. `D:\OrderGetItRight\notes\` or
    `OneDrive\Documents\to the spoils go\`).

---

## 5. TAURI SHELL

### 5.1 The Tauri shell opens but the page is blank

  - **SYMPTOM**
    `order-get-it-right.exe` launches, the window
    appears, but the content area is white or
    shows a `tauri://localhost/` error.

  - **ROOT CAUSE**
    The `tauri.conf.json` `frontendDist` setting
    points at a directory that no longer matches
    the current `02_Technical/web/`. The default
    in the project is `"../web"` (relative to
    `tauri-shell/src-tauri/`), which resolves to
    `02_Technical/web/`. If the web folder was
    moved or renamed, the path breaks.

  - **FIX**
    1. Confirm `02_Technical/web/index.html` exists
       and is non-empty.
    2. Open `02_Technical/tauri-shell/src-tauri/
       tauri.conf.json`. Confirm `frontendDist:
       "../web"`.
    3. If the Tauri shell has a Cargo build cache
       pointing at a previous path, rebuild:
       ```
       cd 02_Technical/tauri-shell
       cargo clean
       npx tauri build
       ```
       (a 1-2 minute incremental build; 4-5 minutes
       for a full bundle).

  - **ESCALATE**
    The Tauri shell serves `02_Technical/web/`
    directly from disk on every launch, so HTML-only
    changes do NOT require a rebuild. If the page
    is blank after an HTML change, the issue is
    the path, not the cache.

### 5.2 Tauri build fails with `error: linker 'link.exe' not found`

  - **SYMPTOM**
    ```
    error: linker 'link.exe' not found
    note: please ensure that Visual Studio 2017 or
    later, or Build Tools for Visual Studio, is
    installed
    ```

  - **ROOT CAUSE**
    The MSVC toolchain is not installed. The Tauri
    build links against the Microsoft C++ toolchain,
    which is not part of the standard `rustc`
    install. This was an operator-known block
    during the 2026-07-12 Tauri build prep
    (sealed in OPEN_ITEMS A4).

  - **FIX**
    Install the Visual Studio Build Tools with the
    "Desktop development with C++" workload. This
    is a multi-GB download and requires an
    elevated installer. Once installed, the next
    `npx tauri build` will succeed.

  - **ESCALATE**
    If MSVC cannot be installed (e.g. the operator
    is on a non-admin machine), the project can be
    used without the Tauri shell -- the FastAPI
    server + browser is functionally equivalent
    and is the primary surface the operator
    actually uses (per
    `04_Validation/AUDIT_NO_BLACK_BOX.md`).

---

## 6. ONTOLOGY AND DOMAIN

### 6.1 The 54-pattern deception ontology fires on innocent text

  - **SYMPTOM**
    An audit of an obviously innocent input returns
    a high deception score and REFUSED. The REPL
    lists the patterns with their confidence scores.

  - **ROOT CAUSE**
    The 54 patterns are tuned for editorial register
    and warranty / contract / support email text.
    They over-fire on common English connectives in
    other registers (the E4 pre-2021 reference
    calibration sealed at block 6584 documented 11
    such false positives on the pre-2021 corpus).

  - **FIX**
    1. Identify the pattern(s) firing: the REPL
       prints `DD-NNN` IDs and confidence scores.
    2. Read the pattern definition in
       `01_Methodology/DECEPTION_ONTOLOGY.md`.
    3. If the pattern is firing on a single-word
       lexical match that does not reflect the
       pattern's intent, queue an ontology
       refinement (R1-R4 from the E4 calibration
       recommendation list).
    4. Re-bump the ontology in a sealed
       `ONTOLOGY_BUMP_<date>` block.

  - **ESCALATE**
    The ontology version is pinned in
    `02_Technical/config/constants.py` as
    `DECEPTION_ONTOLOGY_VERSION`. Any bump
    requires a sealed CONSTANTS_BUMP block; see
    the constants bump procedure in
    `HANDOVER_TO_NEW_OPERATOR.md`.

### 6.2 The Real-Options lattice returns zero

  - **SYMPTOM**
    The Real-Options gate returns `0.0` even on
    inputs that should produce a non-zero lattice
    value.

  - **ROOT CAUSE**
    The LAW multiplicative veto has fired. At least
    one metric (performance, efficiency, warranty,
    issue density, violation ratio) is below its
    floor. The product is non-compliant and the
    lattice value is vetoed to zero by construction.

  - **FIX**
    1. Inspect the BBFB gate output. The failing
       metric(s) are named in the panel.
    2. Cross-reference with the floor in
       `00_Strategy/GOVERNANCE.md` Section 2.
    3. Either improve the input (better evidence
       for the failing metric) or accept the
       REJECT decision as correct.

  - **ESCALATE**
    If you believe the veto is wrong (the input
    has evidence for the metric but the engine
    does not see it), the issue is in the evidence
    parser. Check `src/agents/form_entry_agent.py`
    and `src/engines/normalize.py` and confirm the
    `ProductEvidence` extraction is correct for
    your input.

---

## 7. AGENTIC REPL (OLLAMA TOOL CALLING)

### 7.1 The REPL says `model not found` when invoking `chat`

  - **SYMPTOM**
    The third-party assistant's `chat` command
    (which hands off to the agentic REPL) errors
    with `model 'X' not found`.

  - **ROOT CAUSE**
    The default Ollama model (`qwen3.5:9b`) is
    not loaded. The previous default
    (`tcoxav/aegis:latest`) was changed during
    the C2_C3_C4 reconciliation. The REPL tool
    reads `OGIR_AGENT_MODEL` env var first, then
    `DEFAULT_MODEL` in
    `02_Technical/tools/agentic_repl.py`, then
    falls back to the hard-coded default.

  - **FIX**
    1. Confirm Ollama is running: `ollama list`.
    2. Confirm `qwen3.5:9b` is loaded; if not,
       `ollama pull qwen3.5:9b`.
    3. To use a different model, set
       `OGIR_AGENT_MODEL=<name>` in the
       environment and re-launch the REPL.

  - **ESCALATE**
    The agentic REPL is OPTIONAL. The deterministic
    audit path (REPL `audit <text>`, FastAPI
    `/api/orchestrator/process`) does not use
    Ollama and works without it. If Ollama is
    unavailable, skip the `chat` command and use
    the deterministic path.

### 7.2 The REPL mangles a JSON payload passed to `seal`

  - **SYMPTOM**
    `onyx> seal MY_EVENT {"key": "value with spaces"}`
    silently drops the braces, the value, or the
    entire payload.

  - **ROOT CAUSE**
    The REPL uses Python's `shlex` to tokenise
    input from stdin. `shlex` does not understand
    JSON: unquoted braces, unquoted colons, and
    embedded spaces are split on whitespace, not
    treated as a JSON object.

  - **FIX**
    For a one-off seal from the REPL, use single
    quotes around the JSON and avoid spaces inside
    the JSON values:
    ```
    onyx> seal MY_EVENT '{"key":"value"}'
    ```
    For any non-trivial payload, seal from
    Python, not from the REPL:
    ```
    python -c "from src.io.vault_io import append_block; print(append_block('EVENT_NAME', {'key': 'value with spaces'}))"
    ```

  - **ESCALATE**
    This is a long-standing REPL limitation. The
    canonical recipes for sealing custom events
    are in
    `HANDOVER_NEXT_SESSION_2026-07-16.md`
    Section 8 and in
    `04_Validation/OPEN_ITEMS_AND_REFERENCE.md`
    Part 1 (the per-item seal pattern).

---

## 8. ENVIRONMENT

### 8.1 `python` is not recognised

  - **SYMPTOM**
    `python : The term 'python' is not recognized
    as the name of a cmdlet, function, script file,
    or operable program.`

  - **ROOT CAUSE**
    Python is not in the PATH. The operator's
    local copy is at
    `C:\Users\justo\OneDrive\Documents\to the
    spoils go\Python314\python.exe` (per the
    CONSTANTS_BUMP recipe); the system Python is
    in `C:\Users\justo\AppData\Local\Programs\
    Python\Python312\python.exe` or similar.

  - **FIX**
    1. Find the Python interpreter:
       `where python` (Windows) or `which python`
       (POSIX).
    2. If absent, install Python 3.12+ and
       ensure "Add to PATH" is checked.
    3. To use the operator's local copy without
       installing: prepend the interpreter
       directory to PATH for the current
       PowerShell session:
       ```
       $env:Path = "C:\Users\justo\OneDrive\Documents\to the spoils go\Python314;$env:Path"
       ```
    4. Verify: `python --version` should print
       `Python 3.12.x` or `Python 3.14.x`.

  - **ESCALATE**
    The project requires Python 3.12+; 3.14 is
    also tested. Older 3.x versions may work but
    are not part of the canonical build.

### 8.2 The OneDrive folder is not syncing

  - **SYMPTOM**
    Files saved to `C:\Users\justo\OneDrive\
    Documents\My Project\OrderGetItRight` do not
    appear in the OneDrive web view, or vice
    versa. Status icons show a red X or a yellow
    exclamation.

  - **ROOT CAUSE**
    OneDrive is paused, offline, or the path
    has been re-hydrated. This affects the
    canonical project root -- if the project
    is not syncing, neither is the chain.

  - **FIX**
    1. Open the OneDrive system tray icon.
    2. Confirm the account is signed in and
       "Files On-Demand" is enabled.
    3. Right-click the project folder,
       "Always keep on this device".
    4. Wait for the green checkmark to appear.

  - **ESCALATE**
    If the project lives in a OneDrive path
    that is not syncing, the operator is
    working on a local-only copy. Re-sign in
    to OneDrive or re-create the canonical
    path on a different host and re-mirror.

---

## 9. ESCALATION

If a failure is not in this catalog, the recovery is in
one of these documents, in order:

  1. The error message itself -- the first line of
     any Python traceback is the regression.
  2. `04_Validation/changelog.log` -- the most
     recent entry names the file that was last
     touched.
  3. `04_Validation/OPEN_ITEMS_AND_REFERENCE.md`
     -- the open-items ledger, the closed-items
     ledger, and the canonical re-derivation
     recipes for REF-1 through REF-6.
  4. `04_Validation/YELLOW_RIBBON.md` -- the
     project identity and the "if someone cuts
     the ribbon" section.
  5. `04_Validation/hardcopy/OPERATOR_MANUAL.txt`
     -- the print-and-laminate reference.
  6. The chain itself -- every seal has a payload
     that names the file:line and the before/after
     SHA-256.

If the failure is not in any of these, write down:
  - the exact error message
  - the exact command
  - the Python and OS versions
  - the current Merkle root
  - the current REF-3 and REF-4 (source tree and
    tree shape hashes)
  - whether the source chain and USB chain both
    return MATCH

Then re-derive REF-1 through REF-6 from disk and
compare with the values in
`04_Validation/YELLOW_RIBBON.md`. If REF-1, REF-2a,
REF-2b, REF-3, and REF-4 all match, the project
source is intact. If only REF-5 and REF-6 differ,
the chain has grown since the docs were last
refreshed -- that is normal. If a different REF-3
or REF-4 appears, a file under `02_Technical/`
has been changed without a sealed
SOURCE_TREE_BUMP / CONSTANTS_BUMP block. Stop and
investigate before any further audit.

---

## HOW TO ADD A NEW ENTRY TO THIS DOCUMENT

When a future operator encounters a new failure mode
that is not listed here, the correct action is to
add a new entry following the SYMPTOM / ROOT CAUSE /
FIX / ESCALATE template. Then:

  1. Run the standard opening ritual to confirm the
     build is still green.
  2. Update the chain by sealing a
     `TROUBLESHOOTING_ENTRY_ADDED_<date>` block via
     `vault_io.append_block`. The payload should
     name the failure mode, the fix recipe, and the
     file:line in `TROUBLESHOOTING.md` where the
     entry was added.
  3. Refresh `04_Validation/OPEN_ITEMS_AND_REFERENCE.md`
     and `04_Validation/YELLOW_RIBBON.md` with the
     new chain root.
  4. Mirror the docs to the USB.

This keeps the troubleshooting catalog honest: every
entry is anchored to a real failure the project
actually saw, and every update is sealed to the
chain.
