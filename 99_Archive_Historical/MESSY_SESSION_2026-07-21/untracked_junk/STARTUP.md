# STARTUP -- one file, start to finish, no jumping around

**Order Get It Right** -- Truth as a Service.
**This file:** 2026-07-20. **Operator:** Justin Barnett.

If you only read ONE file before running the program, read this one.
It is the single ordered path from "I have the project folder" to "I
just ran an audit and the verdict is sealed." Everything else (README,
INTRODUCTION, TROUBLESHOOTING, handovers) is detail you reach for *after*
something here points you to it.

Canonical project root (everything below assumes you are here):

    C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight

Open a terminal here: hold Shift, right-click the folder,
"Open PowerShell window here" / "Open in Terminal".

> The order is the order. Do not skip a step. Each step takes 30-90 sec.

---

## STEP 1 -- verify the build is intact (chain check)  [30 sec]

The Merkle chain is the proof the project has not been tampered with.
If it verifies, the project is intact. If it is broken, STOP -- do not
run any audit until you understand why.

```powershell
cd 02_Technical
python -m src.verify_chain
```

You want to see, near the end:

```
Claimed root     : <64-hex>
Recomputed root  : <64-hex>
RESULT: MATCH -- chain is intact.
```

**If you see `RESULT: BROKEN at block <N>`:** the chain was edited outside
the program. Stop. Do not run audits. The fix is in
`04_Validation/TROUBLESHOOTING.md` section 1.1 (restore `03_Vault/` from
the USB mirror, re-verify). Do not proceed past Step 1 until MATCH.

> Block count grows by 1 per audit and by SHUTDOWN blocks when the
> server closes; the root changes every seal. What matters is that
> Claimed == Recomputed, not the exact number.

```powershell
cd ..     # back to project root
```

---

## STEP 2 -- run the test suite  [60 sec]

```powershell
python -m pytest tests/ -q --ignore=tauri-shell
```

**Canonical expectation:** all tests pass, a few host-dependent skips.

- The fast suite (`test_vault_journal`, `test_job_journal`,
  `test_vault_reseed_guard`, `test_smoke`, `test_evidence_parser`,
  `test_f7_deep_lattice_wired`, `test_f7_spec_value_curve`) is ~63 tests
  in ~24 sec.
- The **skips** are host-dependent: live tests that need a tool-capable
  Ollama model loaded AND the FastAPI server running are skipped when
  either is absent. That is normal, not a failure. (The agentic REPL
  and its D5 test were removed 2026-07-21 per the operator directive
  "TOOLS/AGENTIC IS OUT" -- the project has no LLM surfaces now.)
- If you see "0 collected" or a very low count: you ran pytest from the
  wrong directory. The real `tests/` is at the PROJECT ROOT.
- If a test ERRORS during collection referencing
  `tauri-shell\resources\python\...`, pytest picked up the bundled Tauri
  Python stdlib. Re-run with `--ignore=tauri-shell` (shown above) or from
  the project root (root `pyproject.toml` scopes `testpaths=["tests"]`).

```powershell
cd 02_Technical   # for Step 3
```

---

## STEP 3 -- confirm the job journal tail agrees with the registry  [15 sec]

Durability check for the journal subsystem. If the tail count drifts
from the registry, a job could be lost on crash.

```powershell
python -c "from src.io import vault_io as v; t=v._read_job_tail(); m=v.read_job_registry(); assert t.get('jobCount')==m['jobCount']==len(m['jobs']), 'DRIFT'; print('OK tail=',t.get('jobCount'))"
```

You want: `OK tail= <N>`. If you see `DRIFT`, see
`04_Validation/TROUBLESHOOTING.md` (journal tail drift).

---

## STEP 4 -- start the web UI (the FastAPI server)  [30-60 sec]

From `02_Technical/`:

```powershell
python -m uvicorn src.server.app:app --port 3000
```

First boot takes 5-10 seconds (lifespan handler initialises the chain).
When ready you will see `Application startup complete.`

Open a browser to <http://127.0.0.1:3000/>. You should see the
single-page operating surface: sticky top bar (STOP/GO/CLEAR), the
four-gate pipeline view, the working-capacity strip, and the call-upon
drawer (top-right) listing the HTTP endpoints.

- If you get JSON `{"status":...}` instead of HTML: the STATIC_DIR path
  bug class (seen 2026-07-17). Fix is `Path(__file__).parent.parent.parent
  / "web"` in `src/server/app.py`. Regression test `test_static_dir.py`.
- If the port is in use: `netstat -an | findstr :3000` to find the owner,
  stop it, or re-run with `--port 3001` and use <http://127.0.0.1:3001/>.
- To stop the server: Ctrl+C. (The lifespan handler seals a SHUTDOWN
  block on clean exit -- this is why the block count grows.)
---

## STEP 5 -- run your first audit (single text)  [30 sec]

In the web UI, paste one line of text into the input panel (a warranty
response, a contract clause, a support email) and press **Ctrl+Enter**
(or click GO). Within 2-5 seconds the four-gate pipeline view fills:

- **Deception Gate** -- which of the 54 patterns fired (DD-001..DD-054)
  and the deception probability
- **BBFB Gate** -- LAW (multiplicative veto) + GRACE (quadratic penalty)
  + FRUIT (weighted composite)
- **Real-Options Lattice** -- the two-stage compound binomial value
  (a stylised optionality index, NOT a valuation -- the
  `LATTICE_FRAMING` string is surfaced on every response)
- **Decision** -- GO / DEFER / TEST FIRST / REJECT

A **REFUSED** final action (no full pipeline shown) means a CRITICAL
pattern fired and the orchestrator short-circuited. That is by design.

The audit is now sealed to the Merkle chain -- the block count went up
by one. Re-run Step 1 to confirm (Ctrl+C the server first, or in a
second terminal).

---

## STEP 6 -- run a HEADLESS batch audit (no UI)  [optional]

For auditing a whole inbox folder without the UI. From `02_Technical/`:

```powershell
python -m src.audit_cli --inbox "<folder-of-docs>" --outbox "<output-folder>" --formats md --per-file-timeout 60 --heartbeat 15
```

- `--inbox` = a folder of `.txt` / `.docx` / `.pdf` files (one per file).
- `--outbox` = where the per-file `.md` reports are written.
- `--formats md` (also `pdf`, `docx`, or comma-separated).
- `--per-file-timeout 60` caps each file; `--heartbeat 15` prints progress.
  These prevent the timeout-during-audit problem (see gotcha 2).

End line you want: `Done. Success: N | Errors: 0 | Warnings: 0 |
Ejected: 0 | Timeouts: 0`. The batch audit (audit_cli) NEVER stalls --
a pathological file is marked "timeout" and skipped, not hung on.

---

## STEP 7 -- audit a Gmail Takeout (.mbox)  [optional]

The CLI does not read `.mbox` directly. Split it first, then audit the
split folder. From the project root:

```powershell
# 1. Split the mbox into one .txt per message (decodes MIME, drops
#    operator-sent + noise, keeps business-in only).
python 04_Validation\scripts\split_gmail_takeout_2026_07_20.py

# 2. Audit the split inbox (Step 6 command, inbox = data\gmail_split_inbox).

# 3. Inspect the verdicts.
python 04_Validation\scripts\inspect_gmail_audit_live.py
```

The splitter writes a manifest to
`04_Validation/gmail_split_manifest_2026-07-20.json`. The inspector prints
the deception-probability distribution, top suspects, pattern
frequencies, BBFB and ACL verdicts.

> **Sealed principle (2026-07-20):** the deception scanner receives the
> FULL extracted text including HTML markup. Do NOT add an HTML-stripper
> before the scanner. Inflated markup IS the signal -- a company wrapping
> a trivial message in 180 KB of repetitive banners is the manipulation
> the scanner exists to catch. Stripping it would launder the evidence.
> Sealed as `DESIGN_PRINCIPLE_MARKUP_IS_SIGNAL_2026_07_20`.
---

## STEP 8 -- compile a Section 177 affidavit  [optional]

In the web UI, open the call-upon drawer (top-right), then the
**Affidavit** section. Click **Preview** (markdown only, no file) or
**Generate** (writes a file under `04_Validation/`). Both return the same
markdown. The Merkle root is embedded in the document body. Print the
page, sign, date. The printed Merkle root is the trust anchor: any third
party with the project folder can re-derive it in under 5 seconds and
compare.

---

## STEP 9 -- seal a manual note / fact to the chain  [optional]

To record an incident, a decision, or any fact as immutable history:

```powershell
cd 02_Technical
python -c "import sys; sys.path.insert(0,'.'); from src.agents.ledger_seal_agent import LedgerSealAgent; LedgerSealAgent().seal_fact('YOUR_EVENT_TYPE', {'note':'what happened'}); print('sealed')"
python -m src.verify_chain
```

Use a unique `event_type` string (UPPER_SNAKE_CASE with a date suffix is
the convention, e.g. `OPERATOR_NOTE_2026_07_20`). Every code change in
this project is sealed this way -- the Ollama timeout fix below was
sealed as `OLLAMA_TIMEOUT_FIX_2026_07_20`.

---

## STEP 10 -- talk to the program in plain English (REMOVED)

> **Removed 2026-07-21 (operator directive "TOOLS/AGENTIC IS OUT").**
> The agentic REPL (`tools/agentic_repl.py`) and its tool-call layer
> (`agentic_repl_tools.py`) were removed because they were the only
> non-deterministic, LLM-dependent, network-touching surfaces in the
> project, contradicting the build directive ("NO BLACK BOX...
> DETERMINISTIC"), the authoritative `[BEGIN TXT OUTPUT]` spec, and
> OPEN_ITEMS_AND_REFERENCE.md line 670 "No LLM in the audit loop". They
> were moved to `99_Archive_Historical/`. The `chat` command in
> `third_party_assistant.py` (their only entry point) was removed too.
>
> The operator's plain-English interface is now the deterministic
> third-party assistant REPL (`python -m src.third_party_assistant`):
> `audit`, `research`, `hunt`, `normalize`, `compute`, `seal`,
> `verify`, `affidavit`, `ledger`, `compare`, `discovery`. Every command
> is bit-for-bit deterministic and sealed to the Merkle chain. There is
> no Ollama, no model download, and no network in the project after this
> removal (except the operator `discovery` DNS recon tool, which is
> out-of-runtime and on the no-network allow-list).
>
> The historical Ollama-timeout text that was here is retained in the
> `99_Archive_Historical/` copy for audit traceability.
---

## KNOWN GOTCHAS (read once, remember)

1. **Ollama first-call timeout (FIXED 2026-07-20).** See Step 10. The
   agentic REPL now defaults to 180s + 1 retry. If you hit it, raise
   `--ollama-timeout`. The batch audit CLI and web UI never call Ollama.
2. **Timeouts during long batch audits.** Without `--per-file-timeout`
   and `--heartbeat`, a large inbox can hang on one slow file. Always
   pass both for batch runs (Step 6). The CLI never stalls -- it marks
   the file "timeout" and moves on.
3. **Wrong test directory.** `tests/` is at the project root. There is a
   stale 2-3 file mirror under `02_Technical/tests/` -- never run from
   there.
4. **Pytest collects the bundled Tauri Python.** If you see errors
   referencing `tauri-shell\resources\python\Lib\test\...`, add
   `--ignore=tauri-shell` (shown in Step 2) or run from the project root.
5. **Block count grows on its own.** Every clean server shutdown seals a
   SHUTDOWN block via the lifespan handler. So the count at Step 1 may
   already be higher than the last number you wrote down. Normal -- what
   matters is MATCH, not the exact count.
6. **The lattice output is NOT a valuation.** Lattice inputs are hard-
   coded defaults; the output is a stylised optionality index. The
   `LATTICE_FRAMING` string is surfaced on every response so this is
   never misread as a business valuation.
7. **No network, ever.** The engine is pure Python stdlib -- no pip
   installs at runtime, no cloud, no AI subscription, no LLM in the
   loop. The only network surface left in the project is the operator
   `discovery` command in third_party_assistant.py (DNS/socket recon,
   out-of-runtime, on the allow-list). The agentic REPL
   (tools/agentic_repl.py), which previously talked to local Ollama,
   was removed 2026-07-21 per "TOOLS/AGENTIC IS OUT"; the runtime was
   always independent of it.

---

## WHERE EACH THING LIVES (quick map)

```
00_Strategy\      STRATEGY.md, GOVERNANCE.md -- what the project IS
01_Methodology\   the human-readable maths (no code)
02_Technical\     the engine: config\, src\, web\, tools\, tauri-shell\
   config\        constants.py (the named constants), exceptions.py
   src\           runtime: agents\, engines\, io\, server\, utils\
   tools\         operator CLI: discovery_agent (agentic_repl removed
                  2026-07-21 per "TOOLS/AGENTIC IS OUT")
   web\           single-file HTML/JS UI
03_Vault\         facts_registry.json + Merkle chain (the proof)
04_Validation\    ALL docs: this file, handovers, review records,
                  open-items, troubleshooting, care manual, scripts\
data\             gmail_split_inbox\, gmail_audit_outbox\, sample inboxes
deploy\           deploy.ps1, build-tauri.ps1
tests\            the pytest suite (project root)
```

---

## IF SOMETHING BREAKS

Go to `04_Validation/TROUBLESHOOTING.md`. It is a lossless catalog of
every failure mode the project has actually seen, each as
SYMPTOM / ROOT CAUSE / FIX / ESCALATE with a chain or file:line
reference. If your symptom is not there, run Steps 1-3 first; if the
build is green, the issue is in your input data or environment, not the
program.

---

## CURRENT OPEN ITEMS (2026-07-20)

- **Tauri code-signing** -- $200-500/yr, operator decision (not code).
- **Second-PC clean-host restore test** -- needs a second Windows PC;
  this is what the USB full-file copy is FOR.
- **Ontology bump R1-R4** -- the four pattern-scope refinements from the
  pre-2021 calibration report; code-doable, not yet done. See
  `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` STEP 3.
- **Operator review of the 8 structural-flag Gmail files** -- the
  audit found 8 files with structural deception flags and 2 with ACL
  demands. The markup-is-signal principle is sealed; what remains is the
  operator deciding which are actionable.

Gmail .mbox import is **CLOSED** (done this session).
Ollama timeout is **CLOSED** (fixed + sealed this session).

---

End of STARTUP. The chain is the source of truth; this file is the map
to it. God bless.
