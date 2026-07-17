# INTRODUCTION

A 5-minute first-run for a fresh operator of the **Order Get It Right**
("Truth as a Service") audit/valuation program. If you have the project
folder and a working Python, you can verify the build is intact in
under sixty seconds, run your first audit, and read your first
affidavit in under five minutes. Nothing in this document requires
the network, a vendor, a cloud account, or any AI subscription.

This document is read at human speed. Read it in order. Do not skip
steps. The order is the order.

---

## STEP 1 (30 sec) -- confirm you have the project

You should be in a directory that contains this file, the
`02_Technical/`, `03_Vault/`, `04_Validation/`, `01_Methodology/`,
and `00_Strategy/` subdirectories, and a `tests/` directory at
the top level. The canonical project root is:

    C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight

The USB mirror is at:

    D:\OrderGetItRight

(also reachable through the `C:\OrderGetItRight` junction, which
is a one-way shortcut to the USB). If you are not at one of these
paths, stop. The rest of this document assumes you are.

Open a terminal in this directory. On Windows: hold Shift, right-
click the folder, "Open PowerShell window here" or "Open in
Terminal".

---

## STEP 2 (30 sec) -- re-derive the Merkle root

The chain is the proof that the project has not been tampered with.
If the chain is intact, the project is intact. If the chain is
broken, something is wrong and you should not run any audit until
you understand why.

From the project root, run:

    cd 02_Technical
    python -m src.verify_chain

The script prints, near the end, two lines:

    Claimed root     : <64-hex>
    Recomputed root  : <64-hex>

If the two strings are **identical**, you will see the line
`RESULT: MATCH -- chain is intact.` If they differ, you will see
`RESULT: BROKEN ...` with the first broken block index. Do not
run any further audit. Roll back to the last printed Merkle root
(from `04_Validation/hardcopy/QUICK_REFERENCE_CARD.txt`) and
re-burn the build from the USB mirror.

If the script itself errors, the most common cause is a stale
`__pycache__` from a prior Python version. Wipe it and retry:

    cd 02_Technical
    python -m compileall -f src/

then run `python -m src.verify_chain` again.

---

## STEP 3 (60 sec) -- run the test suite

From the project root (NOT from `02_Technical/`), run:

    cd ..
    python -m pytest tests/ -q

The canonical expectation is:

    86 passed, 1 skipped, 0 failed

The single skip is the host-dependent Ollama tool-calling
end-to-end test, `tests/test_d5_agentic_repl.py`, which requires
both a tool-capable model loaded in Ollama and the FastAPI
server running on `127.0.0.1:3000`. It is skipped when either
of those is absent. That is normal. A "0 collected" result
means an import error -- read the traceback's first line; the
file and line number it names is the regression.

If you see a count significantly lower than 86 -- e.g. "6 passed"
-- you are running pytest from the wrong directory. The canonical
`tests/` lives at the project root, not at `02_Technical/tests/`.
There is a stale mirror under `02_Technical/tests/` with only
2-3 test files; do not run from there.

---

## STEP 4 (60 sec) -- start the FastAPI server

From the project root, run:

    python -m uvicorn src.server.app:app --port 3000

The first run can take 5-10 seconds while the lifespan handler
initialises. When ready, you will see a line ending in
`Application startup complete.` Open a browser to
<http://127.0.0.1:3000/>. The single-page operating surface
(sticky top bar with STOP/GO/CLEAR; four-gate pipeline view;
working-capacity strip; call-upon drawer enumerating 32 HTTP
endpoints) should appear.

If you see a JSON response like `{"status": ...}` instead of the
HTML, the bug class is the one previously seen on 2026-07-17:
a path bug in `02_Technical/src/server/app.py` STATIC_DIR.
The fix is `Path(__file__).parent.parent.parent / "web"`. The
regression test `tests/test_static_dir.py` catches this.

If the port is already in use, find the owner with
`netstat -an | findstr :3000` (Windows) or `lsof -i :3000`
(POSIX), then either stop that process or use a different port
with `--port 3001` and adjust the browser URL.

---

## STEP 5 (60 sec) -- run your first audit

Open the web UI, paste a single line of text into the input
panel (a warranty response, a contract clause, a support email),
and press Ctrl+Enter (or click GO). Within 2-5 seconds the
four-gate pipeline view will populate:

  - **Deception Gate** -- which of the 54 patterns fired
    (DD-001 through DD-054) and the deception score
  - **BBFB Gate** -- LAW (multiplicative veto) + GRACE
    (quadratic penalty) + FRUIT (weighted composite)
  - **Real-Options Lattice** -- the two-stage compound
    binomial lattice value
  - **Decision** -- GO / DEFER / TEST FIRST / REJECT

A `REFUSED` final action (no full pipeline shown) means a
CRITICAL pattern fired and the orchestrator short-circuited.
This is by design and is handled in the UI's `loadRunIntoView`.

The audit is now sealed to the Merkle chain. The block count
went up by one. Re-run Step 2 to confirm.

---

## STEP 6 (60 sec) -- compile a Section 177 affidavit

In the web UI, open the call-upon drawer (top-right), then the
**Affidavit** section. Click "Preview" to get the markdown
without writing to disk, or "Generate" to write it. Both
return the same markdown -- the difference is whether a file
appears under `04_Validation/`. The Merkle root is embedded
in the document body. Print the page, sign, and date. The
printed Merkle root is the trust anchor: any third party with
the project folder can re-derive it in under 5 seconds and
compare to the value in the printed page.

---

## STEP 7 (5 sec) -- shut down cleanly

Press Ctrl+C in the terminal where the server is running. The
FastAPI lifespan handler seals a SHUTDOWN block to the chain
on clean exit. This is automatic. If the server is killed
without a clean shutdown (Task Manager / SIGKILL), the SHUTDOWN
seal is not written. The next clean run will write one.

The first time you install on a fresh machine, this is also a
good moment to set up the USB mirror if you have not already.
See `04_Validation/hardcopy/HARD_COPY_BACKUP_PLAN_1-2-3.txt`.

---

## WHAT TO READ NEXT

You have just verified the build and run an audit end to end.
The next five files to read, in order, are:

  1. This file (INTRODUCTION.md) -- the first-run orientation.
  2. `04_Validation/OPEN_ITEMS_AND_REFERENCE.md` -- what is
     open, what is closed, the six reference fingerprints.
  3. `04_Validation/YELLOW_RIBBON.md` -- the project identity
     in one document; "if someone cuts the ribbon".
  4. `00_Strategy/STRATEGY.md` -- the contract with the world.
  5. `04_Validation/CONTEXT_WINDOW.md` -- the long-form digest
     and the on-disk history of every recent change.

If something has gone wrong, see `TROUBLESHOOTING.md` (this
folder) before debugging by hand.

---

## THE 10% PROMISE

The runtime will never take more than 10% of your time, your
disk, or your network in a single cycle. It will not phone
home. It will not phone an LLM. It will not transmit any
artefact off-host unless you explicitly invoke a network-
enabled action. This is the 10% promise in `00_Strategy/
GOVERNANCE.md` Section 9. It is binding. The network audit
that proves it is in `04_Validation/AUDIT_NO_NETWORK.md`.

---

## THE 10 NAMED MODULES

You do not need to memorise these to operate the build. They
are listed here so you know what the project is built from.
Five core agents (under `02_Technical/src/agents/`):

  - Form_Entry_Agent       -- draft a fact from operator input
  - Audit_Review_Agent     -- 54-pattern deception scan (v3.9)
  - Lattice_Compute_Agent  -- real-options binomial lattice
  - Ledger_Seal_Agent      -- Merkle seal to the chain
  - Affidavit_Agent        -- Section 177 certificate

Five support modules (under `02_Technical/src/agents/` and
`tools/`):

  - InventoryAgent         -- inbox/outbox tracking
  - MonitorAgent           -- incident briefing
  - Orchestrator           -- 4-gate pipeline
  - AgentJobDelegator      -- MCP job dispatcher
  - TauFirewall            -- 10% extraction ceiling

The URN map and the discovery process are in
`04_Validation/INTELLECTUAL_PROPERTY_RIGHTS.txt`.

---

## THE FOUR GATES

Every audit decision passes through the same four gates, in
order:

  1. **Deception Gate**   -- 54-pattern ontology v3.9
                             + Shannon entropy (anomaly
                             threshold 4.5 bits/char)
  2. **BBFB Gate**        -- LAW (multiplicative veto)
                             + GRACE (quadratic penalty,
                               coefficient 2.0)
                             + FRUIT (weighted composite)
                             + CVS (composite value score,
                               threshold 0.0005)
  3. **Real-Options Gate**-- two-stage compound binomial
                             lattice (S0=55, K1=18, K2=10,
                             T1=T2=3, R=0.05, sigma1=0.30,
                             sigma2=0.20, N1=N2=3)
  4. **Decision Gate**    -- GO / DEFER / TEST FIRST / REJECT
                             (also: REFUSED if a CRITICAL
                             pattern fires -- the refusal
                             short-circuit)

If any gate fails (LAW multiplicative veto, GRACE penalty
above 0.75, deception veto above 0.75, striking gate
violation, tau above 0.10), the cycle aborts with a specific
verdict. The decision gate then either defers, tests first,
or rejects. Only a clean pass through all four gates
produces a GO.

---

## WHAT THIS PROJECT IS, IN ONE SENTENCE

> Order Get It Right -- Truth as a Service.
> A deterministic business audit and valuation program.
> Version 1.0.0. Operator: Justin Barnett.
> Jurisdiction: Commonwealth of Australia.
> Operates from `C:\Users\justo\OneDrive\Documents\My
> Project\OrderGetItRight`. USB/SDXC backup at
> `D:\OrderGetItRight`. No network. No LLM in the audit
> loop. Every decision sealed to a Merkle chain at
> `03_Vault/facts_registry.json`.

That sentence plus the six reference fingerprints is the
entire project identity. The fingerprints are in
`04_Validation/YELLOW_RIBBON.md` Section "THE SIX
FINGERPRINTS".

---

If you have read this far and the steps above worked, the
project is running on your machine. Welcome home.
