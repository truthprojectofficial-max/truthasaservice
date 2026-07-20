# HOW TO RUN IT — a first-timer's walk-through (OGIR v1.0.0)

> Read this like a story. It walks you, one step at a time, through the
> exact thing you do: open the program, pick 3, pick 1, loop. At every
> step it tells you **what each named thing is**, **what it does**, and
> **what happens next**. No assumed knowledge. Written so a high-school
> kid opening the manual for the first time can follow it.
>
> Time to read: ~10 minutes. Time to do: ~2 minutes once you've read it.

---

## BEFORE YOU START — the three named things you'll meet

There are only three named things in this whole walk-through. Learn them
now and the rest makes sense.

### 1. `start.py` — "the launcher" (the front door)
`start.py` is a small Python file that sits in the **project root** (the
top folder of the whole project). It is not the project itself — it's a
**menu**. When you run it, it prints a numbered list of jobs the project
can do, you type a number, and it runs that job for you. Think of it as
a remote control with 10 buttons. You only ever press button 3 and
button 1.

### 2. `02_Technical` — "the engine room"
`02_Technical` is a folder inside the project. It holds **all the actual
code** — the 45 Python modules, the 9 agents, the audit pipeline, the
chain. You almost never go in there yourself. The launcher goes in there
for you. When the launcher runs a job, it sets its "working directory" to
`02_Technical` so the job can find its own code.

### 3. `03_Vault` — "the safe" (the record of every decision)
`03_Vault` is a folder that holds the **audit chain** — a tamper-evident
list of every decision the project has ever made, sealed with
cryptography so nobody can secretly change an old decision. Right now it
holds **27,437 sealed blocks**. Every time the project decides something,
it seals a new block in here. Job 3 (verify) checks this safe is intact;
job 1 (audit) adds new blocks to it.

That's the whole cast. Now the story.

---

## STEP 0 — open a terminal (the screen you type into)

A "terminal" is the black-or-blue window where you type commands. On
Windows it's called **PowerShell** or **Command Prompt**. You can find
it by pressing the Windows key and typing "powershell" and hitting Enter.

When it opens you'll see a line that ends with `>` or `PS` and a flashing
cursor. That's where you type.

**What happens next:** nothing yet. You need to get to the project folder.

---

## STEP 1 — get to the project root (`cd`)

Your terminal opens in some random folder (usually your user folder).
You need to move it to the project root — the folder that contains
`start.py`. The command to "move" is `cd` (change directory).

Type this exactly, then press Enter:

```
cd c:\OrderGetItRight
```

**What `cd` is:** it's not part of the project. It's a built-in terminal
command meaning "go to this folder." The quote marks are there because
the path has spaces in it ("My Project").

**What `OrderGetItRight` is:** the project root. The top folder. It
holds `start.py`, `02_Technical`, `03_Vault`, and a few others.

**What happens next:** the terminal's prompt changes to show you're now
in `OrderGetItRight`. You won't see any message — the prompt line itself
just updates. You're now standing at the front door.

---

## STEP 2 — run the launcher (`.\start.py`)

Now type this and press Enter:

```
.\start.py
```

**What `.\start.py` is:** the launcher — the remote control from step 0.
You don't need to type `python` first; Windows knows `.py` files run with
Python (it's set up on your machine). The `.\` part means "the file in
this folder" — i.e. `start.py` right here in the project root.

**What happens next:** the screen fills with a banner and a numbered
menu. It looks like this:

```
========================================================================
   ORDER GET IT RIGHT  --  v1.0.0
   Deterministic business audit & valuation engine
   Operator of record: Justin Barnett
========================================================================
  No LLM. No network. Tamper-evident chain. Same input -> same verdict.
------------------------------------------------------------------------
  CHOOSE A TASK:

    1. Run a document audit (inbox -> outbox)
    2. Run the end-to-end demo job (sample evidence)
    3. Verify the whole audit chain (MATCH / BROKEN)
    4. Run HOURLY maintenance health check
    5. Run DAILY maintenance health check (seals a block)
    6. Onyx CLI (third-party surface: audit, verify, affidavit, ledger...)
    7. Monitor agent oversight briefing
    8. Run the test suite (pytest)
    9. Install the Windows Task Scheduler (hands-off maintenance)
   10. Quit

  Enter number (or q to quit):
```

The cursor is blinking after the colon. It's waiting for you.

---

## STEP 3 — PICK 3 (verify the chain — the "is the safe intact?" check)

Type `3` and press Enter.

**What you just picked:** "Verify the whole audit chain."

**What this does, in plain English:** the project goes into `03_Vault`
(the safe), reads **every single sealed block** (all 27,437 of them),
re-does the cryptography from the very first block to the very last, and
checks that the answer matches the answer recorded on the outside of the
safe. If they match, nobody has tampered with the history. If they don't
match, somebody changed something and you'd need to investigate.

**Why you do this first, before anything else:** it's the trust check.
You don't want to add new decisions to a safe that's already been
tampered with. So you check the safe is clean *before* you use it. It
takes about a fifth of a second (212 ms) — basically instant.

**What the screen shows after you press Enter:**
The launcher first prints a description of what's about to happen, then
asks:

```
  >> Verify the whole audit chain (MATCH / BROKEN)
     Re-derives the Merkle root from every sealed block and compares it to
    the recorded root. ~212 ms for 27,437 blocks. The trust anchor.

  Press Enter to launch (Ctrl+C to cancel)...
```

This is the launcher's **two-step safety**: it tells you what you picked
and waits for you to confirm. Press Enter to go, or Ctrl+C to back out.

**Press Enter.**

**What happens next:** the launcher prints a box showing the exact
command it's running and where, then the verifier runs and prints:

```
==============================================================================
ORDER GET IT RIGHT -- CHAIN VERIFICATION
==============================================================================
Vault path       : C:\...\03_Vault
Block count      : 27437
...
Claimed root     : 9b1af15468bea96cfb6e2a4b750ee0583fee9c46db11f268fdcfc060f4abbb66
Recomputed root  : 9b1af15468bea96cfb6e2a4b750ee0583fee9c46db11f268fdcfc060f4abbb66
------------------------------------------------------------------------------
RESULT: MATCH -- chain is intact.
Every block in the vault re-derives to the same Merkle root that
is recorded in the registry. The audit history is unchanged.
==============================================================================
```

**What "MATCH" means:** the safe is intact. The 27,437 decisions in
there are exactly as they were sealed. You're good to go.

**What "BROKEN" would mean (you won't see this today):** somebody
altered the vault. Stop, don't run an audit, and investigate. (This
has never happened on this project.)

After the result prints, the launcher says:

```
  Done. Press Enter to return to the menu (Ctrl+C to quit)...
```

**Press Enter.** You're back at the menu. The safe is verified. Now the
real work.

---

## STEP 4 — PICK 1 (run a document audit — the main job)

Type `1` and press Enter.

**What you just picked:** "Run a document audit (inbox -> outbox)."

**What this does, in plain English:** the project looks in a folder
called `02_Technical\data\inbox`. Any business document in there — a
`.txt`, a `.docx`, or a `.pdf` — gets read, picked apart for the
facts (price, spec, warranty, compliance claims), run through the
**4 gates** (see below), given a verdict (GO / DEFER / TEST FIRST /
REJECT), and a report is written to `02_Technical\data\outbox` in
Markdown, PDF, and Word. It also seals a block to `03_Vault` recording
that it did this.

**The 4 gates, in plain English** (this is what "happens" to each
document):
1. **Deception Gate** -- reads the words for the 54 known lying patterns
   (the "I apologize for the confusion" kind of thing) and measures how
   much real information is in the text.
2. **BBFB Gate** -- checks the facts against the law (LAW = one violation
   kills it), gives grace for small slips (GRACE), and scores the whole
   basket (FRUIT).
3. **Optionality Lattice** -- turns the deception score into an
   "optionality index" -- how much room you have to act. (This is a
   stylised index, not a dollar valuation; the project always says so.)
4. **Decision Gate** -- combines everything into one of four verdicts:
   **GO** (do it), **DEFER** (wait), **TEST FIRST** (check before you
   act), or **REJECT** (don't).

**What the screen shows after you press Enter on the menu:**

```
  >> Run a document audit (inbox -> outbox)
     Processes every .txt/.docx/.pdf in 02_Technical/data/inbox and writes
    Markdown/PDF/DOCX reports to 02_Technical/data/outbox. Main use.

  Press Enter to launch (Ctrl+C to cancel)...
```

**Press Enter.**

**What happens next:** the launcher runs the audit. For each document
in the inbox it prints progress and a verdict. When it's done, the
reports are sitting in the outbox folder. You can open that folder in
Windows Explorer and read them.

> **If the inbox is empty:** the audit runs instantly and reports
> nothing to do. To actually run a real audit, drop a `.txt`/`.docx`/
> `.pdf` business document into `02_Technical\data\inbox` first, then
> pick 1 again. There are also sample documents already in the outbox
> (`SEED_001` ... `SEED_004`) you can look at to see what a report
> looks like.

After it finishes:

```
  Done. Press Enter to return to the menu (Ctrl+C to quit)...
```

**Press Enter.** You're back at the menu. One audit done. A new block
is sealed in the safe.

---

## STEP 5 — LOOP (do it again)

That's the whole loop:

```
pick 3  ->  verify the safe is intact
pick 1  ->  run an audit on whatever's in the inbox
(press Enter to come back to the menu)
pick 3 again  ->  re-verify (the new block you just sealed now checks out too)
pick 1 again  ->  run the next audit
... and so on
```

You can do this as many times as you like. Every `pick 1` adds a block;
every `pick 3` confirms all the blocks (old and new) still match. That's
the rhythm: **check, work, check, work.**

---

## STEP 6 — quit

When you're done, type `q` (or `10`) and press Enter. The launcher
closes. Your terminal is still open — you can close it like any window.

Nothing you did is lost. The audits you ran are sealed in `03_Vault`
forever (or until someone deliberately and visibly changes them, which
would break the chain and show up as BROKEN on the next `pick 3`).

---

## THE WHOLE LOOP ON ONE LINE (the thing you asked for)

```
cd <project root>  ->  .\start.py  ->  pick 3 (verify)  ->  pick 1 (audit)  ->  loop
```

Or, copy-paste the first part:

```
cd c:\OrderGetItRight
.\start.py
```
…then type `3`, Enter, Enter, …then type `1`, Enter, Enter, …repeat.

---

## IF SOMETHING GOES WRONG

| What you see | What it means | What to do |
|---|---|---|
| `python : The term 'python' is not recognized` | Python isn't installed or isn't on your PATH. | Install Python 3.12+ from python.org, tick "Add Python to PATH". |
| `ERROR: could not find 02_Technical/...` | You ran `start.py` from the wrong folder. | `cd` to the project root (Step 1) and try again. |
| `RESULT: BROKEN` | The vault chain doesn't re-derive. Someone changed a sealed block. | **Stop.** Don't run any audits. Investigate `03_Vault` or restore from backup. (Has never happened here.) |
| The audit says "no documents found" | The inbox folder is empty. | Put a `.txt`/`.docx`/`.pdf` in `02_Technical\data\inbox` and pick 1 again. |
| A `squeal-*` file appears in `04_Validation\squeal-reports\` | A maintenance routine failed. | Open it and read it — it says what went wrong. |

---

## THE OTHER MENU NUMBERS (you don't need these for the loop, but here's what they are)

- **2** -- runs the audit pipeline on a built-in fake document (good for a quick "is the project alive?" test; you don't need to put anything in the inbox).
- **4** -- runs the 4 fast health checks (the ones a scheduled task would run every hour). ~0.3 seconds. Doesn't seal a block.
- **5** -- runs all 7 health checks AND seals one maintenance block. ~10 seconds. This is what the daily scheduled task does.
- **6** -- prints the help for the "Onyx CLI", which is the set of commands a *third party* (another company, another program) would use to talk to your project. Not for you day-to-day.
- **7** -- runs the "Monitor agent", which is the project's own watchdog. It double-checks the chain and looks for anything suspicious. Read its output before you use a verdict for anything legal.
- **8** -- runs the 23 built-in tests. Green = the project still works the way it was built to. Run this if you changed any code.
- **9** -- installs the two Windows scheduled tasks so the health checks run by themselves every hour and every day, even when you're not at the computer. Run once, then forget it.
- **10** (or `q`) -- quit.

---

## THE ONE-SENTENCE VERSION

Open a terminal, `cd c:\OrderGetItRight`, run `.\start.py`, type
`3` and Enter and Enter to check the safe, type `1` and Enter and Enter
to run an audit on whatever's in the inbox, then keep going — that's the
whole job.

---

*Deterministic. No LLM. No network. Tamper-evident. Operator: Justin Barnett.*