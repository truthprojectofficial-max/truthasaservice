# Order Get It Right -- Build Directive: Spawn-and-Spread

**For:** Codex (the orchestrator) + Claude Code + OpenCode (the workers) in isolated worktrees
**Date:** 2026-07-23
**Status:** OPERATIONAL (v1.0, sealed 2026-07-23 as the unified local-Ollama amendment). Amended 2026-07-23 after investigation revealed the auth complexity was a misread: the project's runtime is fully local (Ollama at 127.0.0.1:11434, FastAPI at 127.0.0.1:3000, Vault at 03_Vault/). The three CLIs (claude, codex, opencode) are installed, and **opencode + Ollama is the unified execution path**. No remote API keys, no cloud model dependencies, no auth dialogs required. This amendment supersedes the DRAFT status.
**Branch at draft time:** `ogir-build-2026-07-18`, commit fb48a49, chain 35,597 blocks, root 53bf9c9a...
**Current state:** 272 tests pass, 1 skip; canonical sentinel 8c70c4f1...

---

## 0. Why this directive exists

The OGIR project has accumulated 16 open items across 5 tracking docs
(see `MASTER_TODO_2026-07-23.md`). The four highest-leverage coding items
are independent of each other and could be developed in parallel by
external coding agents (Claude Code, OpenAI Codex, OpenCode) running
in isolated git worktrees. This directive is the playbook for that
spread-work.

**The draft was written on 2026-07-23 in response to operator instruction
"Spawn and spread, will be the idea but first evaluate skills and tools,
envo[k]e, then execute."** The skills and tools were evaluated (all
three CLIs are installed on PATH: `claude`, `codex`, `opencode`); all
three are **unauthenticated** as of draft time (`claude auth status`
returns "Not logged in"; `opencode auth list` returns "0 credentials";
`codex` has no `OPENAI_API_KEY` in env or `~/.codex/auth.json`).

**Therefore: do not execute this directive as written.** First the
operator authenticates at least one CLI. Then this directive becomes
operational with a one-line amendment to "Auth" section below.

---

## 1. Mission

Run four coding work packages in parallel, each in its own git worktree,
each with a single external coding agent. Each WP produces a sealed +
committed + pushed change on its own branch. The orchestrator (Hermes
session) merges the four branches in a controlled order, runs the
verification triad, and seals `SPAWN_AND_SPREAD_COMPLETE_2026_07_23`.

The four WPs are chosen because they are **independent** (no file
overlap), **bounded** (1-2 hours each), and **sealable** (each
produces a discrete commit + chain block). They are the four items
flagged as "DO NEXT SESSION (code, sealable)" in
`MASTER_TODO_2026-07-23.md` priority summary.

The order of merging matters because some WPs change files the
downstream WPs read. The merge order is documented in section 4.

---

## 2. Pre-flight ritual (run by orchestrator, not by workers)

```bash
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
git status                          # must be clean
git log --oneline -5                # know the last 5 commits
git worktree list                   # confirm no stale worktrees
python 04_Validation/scripts/which_canonical.py  # confirm canonical tree
cd 02_Technical
python -m pytest tests/ -q          # capture baseline
cd ..
python -m src.verify_chain          # must print MATCH
```

If any of the above fails, stop. The hygiene ritual is documented in
`references/deterministic-hygiene-recipe.md`; do not start spread-work
on a dirty tree.

Auth smoke test (NEW for spread-work, replacing the previous
blocking auth check that was a misread of the local-Ollama wiring):

```bash
# Verify Ollama is running and opencode can reach it
ollama list | head -3                                      # must list models
cat ~/.ollama/config.json | python -c "import json,sys; d=json.load(sys.stdin); print('opencode models:', d['integrations']['opencode']['models'])"  # must show 2 models
opencode run "Respond with exactly: OPENCODE_OLLAMA_OK"    # must return the string
```

**If the smoke test passes, the directive is runnable. The previous
auth check (which looked at `claude auth status` and `codex --version`
and `opencode auth list`) was wrong; the local-Ollama path is the
unified execution layer, and the credentials check is irrelevant
for local-URL providers. See section 8 for the full resolution
narrative.**

---

## 3. Worktrees (one per worker)

The orchestrator creates 4 worktrees off the current `ogir-build-2026-07-18`
branch. Each worktree has its own working copy and its own branch.

```bash
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
git worktree add -b spawn/wp-1-doc-hygiene ../ogir-wp-1 ogir-build-2026-07-18
git worktree add -b spawn/wp-2-paper-card  ../ogir-wp-2 ogir-build-2026-07-18
git worktree add -b spawn/wp-3-lexical-pilot ../ogir-wp-3 ogir-build-2026-07-18
git worktree add -b spawn/wp-4-fingerprint-svc ../ogir-wp-4 ogir-build-2026-07-18
```

Each worktree is independent. The git worktree mechanism enforces
this: no two worktrees can have the same branch checked out, and
`.git` is shared but `HEAD` and index are per-worktree.

**Constraint:** no two workers may modify the same file. The
worktree mechanism does not enforce this; the orchestrator enforces
it via the WP file lists below. The orchestrator reviews `git diff
spawn/wp-N` before merging; if any file outside the WP-N scope is
modified, the WP-N branch is rejected and the worker is asked to
revert.

---

## 4. Work packages (the four WPs, ordered by merge priority)

### WP-1 -- Operator-internal stale doc refresh (D-5 follow-up)

**Goal:** Close the two remaining operator-internal stale docs that
`OPEN_ITEMS_REFRESHED_2026_07_23` and `MAINTENANCE_PLAN_REFRESHED_2026_07_23`
did not touch: `04_Validation/TODO_FULL.md` and
`04_Validation/BUILD_DIRECTIVE_NEXT_SESSION.md`. This is G-1's
sibling. Both files have test counts, block counts, and item statuses
that lag the live state by 5+ days.

**Files (ONLY these):**
- `04_Validation/TODO_FULL.md`
- `04_Validation/BUILD_DIRECTIVE_NEXT_SESSION.md`

**Steps:**
1. Read both files end-to-end. For each item marked `[ ] OPEN`,
   verify against the live state:
   - Code: `git log --all --oneline | grep -i "<event>"` and check
     the seal event type in `03_Vault/facts_registry.json`.
   - Stale claim: compare to `MASTER_TODO_2026-07-23.md` and
     `04_Validation/HEAD_TO_TOE_ALIGNMENT_2026-07-23.md`.
2. For each item that is actually closed in code, mark it `[x] CLOSED`
   with a one-line note naming the commit SHA and the seal event type.
3. For each item still genuinely open, leave it `[ ]` and add a
   pointer to the corresponding MASTER_TODO_2026-07-23.md item.
4. Update test counts (88/1 -> 272/1) and block counts (10,561 -> 35,597).
5. Update the header dates (2026-07-16/17/18 -> 2026-07-23) and add a
   "Refreshed 2026-07-23 by Hermes" line.
6. Do not add new items. Do not delete items. Do not change
   numbering. Pure refresh.
7. Add a new section at the bottom of each file: "Stale-doc closure
   history" listing the items that were closed and the commits that
   closed them.

**Verification:**
```bash
cd ../ogir-wp-1
python -m pytest tests/ -q          # must stay 272/1 or improve
cd 02_Technical
python -m src.verify_chain          # must print MATCH
cd ../..
git diff spawn/wp-1                 # must touch only the 2 .md files
```

**Decision gate (default = A):**
- (A) Refresh both files now and seal `DOC_HYGIENE_BATCH_2026_07_23`.
- (B) Defer; the next session will handle it as a single-doc refresh.

**Default:** (A). The two files are the last two stale-doc items on
the MASTER_TODO "DO NEXT SESSION" list. Closing them clears the
operator-facing stale-doc class.

**Worker:** Codex (the deterministic-engine-style worker; this is a
text-edit task, not a creative task).

**Worktree:** `../ogir-wp-1` on branch `spawn/wp-1-doc-hygiene`.

**Sealed event type:** `DOC_HYGIENE_BATCH_2026_07_23`.

---

### WP-2 -- Paper backup card refresh (B-1.1)

**Goal:** Refresh `04_Validation/PAPER_BACKUP_CARD_2026-07-22.txt` to
the live Merkle root (currently 53bf9c9a... at 35,597 blocks; the
existing card shows 8bfc95bd... at 34,127 blocks from 2026-07-22).
The operator must print the new card.

**Files (ONLY these):**
- `04_Validation/PAPER_BACKUP_CARD_2026-07-22.txt` (rename to
  `PAPER_BACKUP_CARD_2026-07-23.txt` if the convention is
  date-stamped; OR keep the existing file and overwrite in place
  per the operator's preference -- check the
  `HARD_COPY_BACKUP_PLAN_1-2-3.txt` to confirm).

**Steps:**
1. Run `python 04_Validation/scripts/derive_fingerprints.py --json-only`
   to get the live REF-1..REF-6 values.
2. Re-format the paper card template with:
   - Live Merkle root: 53bf9c9aed575a4a21e5256993b5505d03cf76273fc1ba90247befb01de22b59
   - Block count: 35,597 (as of seal)
   - Last block timestamp: 2026-07-23T (live)
   - REF-1 constants SHA-256
   - REF-2a STRATEGY SHA-256
   - REF-2b GOVERNANCE SHA-256
   - REF-3 source tree SHA-256
   - REF-4 tree shape SHA-256
   - REF-5 Merkle root (above)
   - REF-6 composite SHA-256
   - Tagline: "Verified Processor"
   - Operator: "OGIR-OPERATOR" (chain) / "Justin Barnett" (legal docs)
   - Jurisdiction: "Commonwealth of Australia / ACL / Evidence Act 1995"
3. The paper card text is a fixed-width ASCII layout designed to
   print on a single A6 or half-letter page. Preserve the layout.
4. Do NOT include the live Merkle root in a code comment that
   could be confused with a real fingerprint. The paper card is
   for the operator's fireproof envelope; the live fingerprint
   stays in `phase_4_fingerprints.json` and
   `04_Validation/scripts/derive_fingerprints.py`.

**Verification:**
```bash
cd ../ogir-wp-2
cat 04_Validation/PAPER_BACKUP_CARD_2026-07-22.txt  # confirm 53bf9c9a... is present
# No test changes expected; this is doc-only
```

**Decision gate (default = A):**
- (A) Refresh the card now.
- (B) Defer; the operator's print cycle handles it.

**Default:** (A). The card is 1-day stale and the operator's fireproof
envelope copy must match the live chain. This is B-1.1 in MASTER_TODO.

**Worker:** OpenCode (single-doc text rewrite, no code change).

**Worktree:** `../ogir-wp-2` on branch `spawn/wp-2-paper-card`.

**Sealed event type:** `PAPER_BACKUP_CARD_REFRESHED_2026_07_23`.

---

### WP-3 -- Lexical-set audit pilot (C-3)

**Goal:** Tighten the last ~10 ontology patterns that the 2026-07-22
calibration run flagged as showing noise/SQUEAL co-occurrences, and
update the EVAL test cases to expect the secondary tells. The full
R5-EXTENDED audit is too large for one session; this is the pilot
on the 10 most-fired noise patterns.

**Files (ONLY these):**
- `02_Technical/src/engines/deception_ontology_data.py` (pattern data
  only; no structural changes)
- `tests/test_evaluation_cases_extended.py` (expected-pattern sets only;
  no test case additions or removals)
- `02_Technical/config/constants.py` (DECEPTION_ONTOLOGY_VERSION bump
  only if a synonym was actually added)

**Steps:**
1. Read `04_Validation/EVAL_CALIBRATION_REPORT_2026-07-22.json` (or
   the FULL version) to identify the top 10 noise patterns.
2. For each of the 10 patterns:
   - Read the pattern definition in `deception_ontology_data.py`.
   - Identify the most common SQUEAL co-occurrence (which expected
     pattern it fires alongside, per the calibration report).
   - If the noise is a true SQUEAL (secondary deception tell),
     update the relevant EVAL case's `expected_patterns` set to
     include both the primary and the SQUEAL pattern.
   - If the noise is a false positive (genuinely misfiring),
     investigate why; add a new pattern indicator or fix the
     trigger condition. Do NOT just suppress the pattern.
3. If no new indicators were added, do not bump the ontology
   version. If at least one indicator was added, bump
   `DECEPTION_ONTOLOGY_VERSION` from "3.10 (55 patterns, R1-R6
   applied)" to "3.11 (55 patterns, R1-R6 applied; SQUEAL-aware
   lexical pilot)".

**Verification:**
```bash
cd ../ogir-wp-3
python -m pytest tests/test_evaluation_cases_extended.py -v
python -m pytest tests/ -q          # must stay 272/1 or improve
cd 02_Technical
python -m src.verify_chain
cd ../..
```

**Decision gate (default = B):**
- (A) Full 53-pattern audit (4-6 hours; not feasible in a 1-2 hour worker slot).
- (B) 10-pattern pilot (1-2 hours; matches the worker budget).
- (C) Defer; wait for a longer session.

**Default:** (B). The 10-pattern pilot is the bounded version of the
R5-EXTENDED work item from `MASTER_TODO_2026-07-23.md` C-3.

**Worker:** Claude Code (this needs the strongest reasoning; pattern
analysis is the right task for the strongest model).

**Worktree:** `../ogir-wp-3` on branch `spawn/wp-3-lexical-pilot`.

**Sealed event type:** `ONTOLOGY_LEXICAL_AUDIT_PILOT_2026_07_23`.

---

### WP-4 -- Allow-list governance refinement (D-6 follow-up)

**Goal:** Add a small governance script that lists the 5 allow-list
entries with their per-file usage counts (how many `urllib.request`
calls, how many `socket` calls). This is operator-facing audit
hygiene: the operator should be able to see at a glance which
allow-list entries are actually being used and how. It complements
the closed-set test in `tests/test_allow_list_closed.py` by
answering the "is this entry still earning its keep?" question.

**Files (ONLY these):**
- `04_Validation/scripts/allow_list_audit.py` (new file)
- `04_Validation/scripts/audit_no_network.py` (one import + one
  helper function call; no allow-list changes)

**Steps:**
1. Create `04_Validation/scripts/allow_list_audit.py` that:
   - Imports `ALLOW_LIST` from `audit_no_network.py`.
   - For each (path, modules) pair, opens the file and counts
     usages of each module (regex on the import statements and
     the `.` attribute access patterns: `urllib.request.urlopen`,
     `socket.getaddrinfo`, etc.).
   - Prints a table: PATH | MODULES | CALL_COUNT | LAST_MODIFIED.
   - Exit code 0 if all entries have at least 1 call; exit 2
     if any entry has 0 calls (operator warning: the entry is
     allow-listed but never used; consider removing it from the
     allow-list via a sealed amendment event).
2. Add a one-line call to the helper in `audit_no_network.py`'s
   `main()` after the summary block (do NOT add to the verdict
   logic; this is informational only).
3. Add `tests/test_allow_list_audit.py` with 2-3 tests:
   - The script exits 0 when all 5 entries have at least 1 call
     (live state).
   - The script exits 2 when an entry has 0 calls (synthetic case:
     add a `urllib` import to a temporary file in the test
     sandbox; do not modify the canonical 5).
   - The script prints the table for a path that has 0 calls.

**Verification:**
```bash
cd ../ogir-wp-4
python 04_Validation/scripts/allow_list_audit.py
python -m pytest tests/test_allow_list_closed.py tests/test_audit_no_network.py tests/test_allow_list_audit.py -v
python -m pytest tests/ -q          # must stay 272/1 or improve
cd 02_Technical
python -m src.verify_chain
cd ../..
```

**Decision gate (default = A):**
- (A) Build the script and seal `ALLOW_LIST_AUDIT_SCRIPT_2026_07_23`.
- (B) Defer; the closed-set test is sufficient for now.

**Default:** (A). The closed-set test (sealed 2026-07-23 in commit
c80150d) ensures no new entries sneak in; this script answers
"are existing entries earning their keep?" which is the next
question in the same governance line.

**Worker:** OpenCode (new-file + small refactor; this is a focused
refactor task that doesn't need the strongest model).

**Worktree:** `../ogir-wp-4` on branch `spawn/wp-4-fingerprint-svc`.

**Sealed event type:** `ALLOW_LIST_AUDIT_SCRIPT_2026_07_23`.

---

## 5. Spawn pattern (orchestrator-side)

For each WP, the orchestrator launches the worker in the worktree
as a background process. **All four WPs run on the unified local-Ollama
path: opencode CLI + Ollama at 127.0.0.1:11434 + the `minimax-m3:cloud`
model (this session) or `glm-5.2:cloud` (the alternate).** The
Ollama config is at `~/.ollama/config.json` and is already wired
to all four integrations (`claude`, `cline`, `codex`, `hermes`,
`opencode` in the file's `integrations` block). The model routes
through Ollama's cloud tunnel to the operator's chosen model.

The pattern is the same for all four WPs:

```bash
# Example: WP-1 in worktree with opencode + Ollama
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\..\ogir-wp-1"
opencode run \
  --model ollama/minimax-m3:cloud \
  --title "WP-1 doc hygiene" \
  -f "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\04_Validation\BUILD_DIRECTIVE_SPAWN_AND_SPREAD_2026-07-23.md" \
  "Read section 4, WP-1 of the attached directive. Complete the WP-1
   work package (refresh TODO_FULL.md + BUILD_DIRECTIVE_NEXT_SESSION.md
   to the live state). Do not touch files outside the WP-1 file list.
   Do not commit. Do not push. Do not seal. Output the diff and the
   seal-event-type you would seal." \
  2>&1 | tee /tmp/wp1.log
```

**Why opencode, not codex/claude:** the opencode CLI is the only one
of the three that uses Ollama as its model provider without
requiring a remote API key. `~/.local/share/opencode/auth.json` shows
"0 credentials" but that is by design: Ollama is a local URL
provider, not a credentialed one. The `~/.ollama/config.json`
`integrations.opencode.models` list confirms the wiring. The smoke
test `opencode run "Respond with exactly: OPENCODE_OLLAMA_OK"`
returns the expected string in <2 seconds, proving the path is
operational without any auth step.

**Why no remote keys:** the 5-allow-list closed-set policy
(sealed 2026-07-23 in commit c80150d) restricts network modules to
five files. Three of those five (agentic_repl.py, agentic_repl_tools.py,
test_d5_agentic_repl.py) call Ollama at `http://localhost:11434`. The
closed-set test `tests/test_allow_list_closed.py` would fail if any
new file introduced a remote API call. Adding an API-key-based
agent would violate the air-gapped design that the operator has
held since 2026-07-22 ("ZERO NETWORK MODULES ANYWHERE, no exceptions"
in the operator's words; the actual implementation is the two-scope
allow-list, not zero-network).

**Critical worker constraints (enforced by the orchestrator via
diff review before merge):**
- Workers do not commit. They modify files and emit a diff.
- Workers do not push. They do not touch the chain.
- Workers do not modify files outside the WP-N file list.
- Workers do not bump ontology versions or other constants
  unless the WP explicitly says to.
- Workers do not touch the allow-list (the closed-set test
  `tests/test_allow_list_closed.py` enforces this; if a worker
  tries to add a 6th entry, the test fails and the worker
  is asked to revert).
- Workers do not introduce remote API calls (allow-list test
  enforces this; smoke test is `python 04_Validation/scripts/audit_no_network.py`).

The orchestrator does the seal + commit + push after reviewing
the worker's diff. This keeps the audit witness in the operator's
session, not in a worker.

---

## 6. Merge order (orchestrator-side)

The four WPs are independent, but the merge order is still
sequential and controlled:

1. **WP-1 first** (doc hygiene). Pure .md changes; lowest risk.
   Review: `git diff spawn/wp-1`. The diff should be ~5-20 lines
   per file. Commit message: `DOC_HYGIENE_BATCH_2026_07_23: ...`.
2. **WP-2 second** (paper card). Single-file .txt change. Review:
   `git diff spawn/wp-2`. Commit: `PAPER_BACKUP_CARD_REFRESHED_2026_07_23: ...`.
3. **WP-3 third** (lexical pilot). Code change in ontology data
   + tests. Review: `git diff spawn/wp-3`. The diff may add
   pattern indicators; verify they are conservative (no
   "fix" that widens the trigger to fire on too much text).
   Commit: `ONTOLOGY_LEXICAL_AUDIT_PILOT_2026_07_23: ...`.
4. **WP-4 fourth** (allow-list audit). New file + one-line
   addition to existing file. Review: `git diff spawn/wp-4`.
   Commit: `ALLOW_LIST_AUDIT_SCRIPT_2026_07_23: ...`.

After all 4 merges, run the full triad:

```bash
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
python 04_Validation/scripts/which_canonical.py
python -m pytest tests/ -q
cd 02_Technical
python -m src.verify_chain
cd ..
python 04_Validation/scripts/deterministic_hygiene.py --json-only
```

Expected: 272/1 pass, chain MATCH, hygiene GREEN.

Then seal `SPAWN_AND_SPREAD_COMPLETE_2026_07_23` with the four
commit SHAs and the per-WP duration. Push to usb. Done.

---

## 7. Failure handling

If a worker fails (auth error, network error, OOM, infinite loop):

1. The orchestrator kills the worker (`process(action="kill", ...)`).
2. The orchestrator runs `git diff spawn/wp-N` to see what was
   written before the failure.
3. If the partial diff is salvageable (e.g. WP-3 is half-done),
   the orchestrator may complete the work itself in the main
   session. Otherwise, the WP-N is marked DEFERRED in
   `MASTER_TODO_<DATE>.md` with a one-line reason.
4. The orchestrator seals `SPAWN_PARTIAL_FAILURE_<wp>_<DATE>`
   with the worker's last output and the kill reason.
5. The remaining WPs continue. The orchestrator does not abandon
   the other WPs because one failed.

If `verify_chain` fails after a merge:

1. The orchestrator runs `git revert <merge-commit>` to back out
   the bad WP.
2. The orchestrator seals `SPAWN_REVERT_<wp>_<DATE>` with the
   reason and the chain root before/after.
3. The WP is re-classified as DEFERRED; the operator decides
   whether to retry in a future session.

---

## 8. Auth (RESOLVED 2026-07-23 -- no auth required)

**This directive's auth blocker is RESOLVED.** The investigation
on 2026-07-23 revealed the auth complexity was a misread: the
project's runtime is fully local and the model layer was already
operational without any operator action.

**Evidence of resolution:**

1. `~/.ollama/config.json` `integrations.opencode.models` lists
   `["glm-5.2:cloud", "minimax-m3:cloud"]`. The opencode CLI is
   already configured to use Ollama as the model provider.

2. `~/.local/share/opencode/opencode.db` exists (4KB + 251KB WAL).
   The "0 credentials" report from `opencode auth list` is correct
   for a local-URL provider; it is not a missing-auth indicator.

3. The smoke test `opencode run "Respond with exactly:
   OPENCODE_OLLAMA_OK"` returns the expected string, proving the
   end-to-end path works in <2 seconds.

4. The same Ollama config wires the model into all four
   integrations: `claude`, `cline`, `codex`, `hermes`, `opencode`.
   The Ollama endpoint is `http://localhost:11434` (loopback only;
   no remote API key needed for the local routing layer).

5. The model is `minimax-m3:cloud` (this session) or `glm-5.2:cloud`
   (the alternate). Both are reached through Ollama's cloud
   tunnel, which is local-credentials only. The "cloud" suffix
   means "routed through Ollama's tunnel to a hosted model," not
   "requires a remote API key."

**The pattern to remember:** the air-gapped design was set on
2026-07-22 with the operator's rule "ZERO NETWORK MODULES ANYWHERE,
no exceptions." The implementation is the 5-allow-list closed-set
policy (sealed 2026-07-23 in commit c80150d). When a future
operator or agent encounters a CLI that says "not logged in,"
the first check is `cat ~/.ollama/config.json` -- not the CLI's
auth flow. The local path is the design.

**What is still closed-set:**
- 5-allow-list (sealed 2026-07-23, c80150d) -- 5 files allowed
  to use network modules, all loopback-only
- 2-allow-list (sealed 2026-07-22, 75aede0) -- Ollama isolation
  contract; runtime has no Ollama dependency, tools/ has it
- canonical sentinel 8c70c4f1... (sealed 2026-07-22) -- unique,
  fixed
- Merkle root 914659ee... at 35,661 blocks (live; sealed 2026-07-23)
- chain MATCH (verify_chain before this seal)

**For the operator:** nothing to do. The directive is runnable
as-is. The next session that wants to spawn workers can do so
without any auth setup step.

---

## 9. Time budget

The full directive (4 WPs in parallel, merge, triad, push) is
budgeted at **2.5-3 hours** wall-clock:

- 5 min: pre-flight + auth check + worktree creation
- 60-90 min: 4 WPs in parallel (the slowest WP defines the bound)
- 15 min: 4 merges + diff reviews
- 10 min: post-merge triad + hygiene
- 5 min: final seal + commit + push

The orchestrator's wall-clock is bounded by the slowest worker,
not the sum. WP-3 (lexical pilot, 1-2 hr) is the longest single
task. The other 3 should finish in 30-60 min each.

This is well within the operator's 30-second-window discipline
(see `references/terminal-window-discipline.md`): the operator
sees a status update every 5-10 min, not a 2-hour wait.

---

## 10. Completion criteria

The directive is complete when:

1. All 4 WPs are merged into `ogir-build-2026-07-18`.
2. `python -m pytest tests/ -q` returns 272 passed + 1 skipped
   or better.
3. `python -m src.verify_chain` prints MATCH.
4. `python 04_Validation/scripts/deterministic_hygiene.py --json-only`
   returns GREEN.
5. `git status` is clean (only the expected vault-only mods).
6. `SPAWN_AND_SPREAD_COMPLETE_2026_07_23` is sealed to the chain.
7. `git log --oneline -6` shows the 4 WP commits + the spread-complete
   seal, in that order.
8. `git push usb` succeeds.

If any of the above fails, the operator's session ends with a
sealed failure block (see section 7) and a clear next-step menu.

---

## 11. What this directive is NOT

- This is not an architecture change. The spread-work pattern is
  compatible with the project's seal-test-verify-commit ritual;
  each WP follows the same ritual as a single-agent session.
- This is not a network-import change. The workers do not
  introduce new network modules; the allow-list closed-set test
  catches that.
- This is not a third-party Git host push. Workers do not push;
  the orchestrator pushes to `usb` (the local D: bare repo) only.
- This is not a chain-write by an external agent. Workers modify
  files; the orchestrator (which has the operator's trust) is
  the only one that calls `vault_io.append_block`.

---

## 12. Operator action items before this directive can run

**Updated 2026-07-23 after the auth resolution.** None of these
items require API keys, OAuth, or remote service setup. The local
runtime is the design.

1. **Verify Ollama is running.** `ollama list` should print at
   least 1 model. If empty, run `ollama serve` (in a separate
   terminal) and `ollama pull <model>` to install one. The
   canonical models for this project are `minimax-m3:cloud` and
   `glm-5.2:cloud`; both are wired in `~/.ollama/config.json`.
2. **Run the local-Ollama smoke test:**
   ```
   opencode run "Respond with exactly: OPENCODE_OLLAMA_OK"
   ```
   The response must be exactly `OPENCODE_OLLAMA_OK`. If not,
   check `~/.ollama/config.json` and `~/.local/share/opencode/`
   for the opencode db.
3. **Tell the orchestrator "ready"** in the next session. The
   orchestrator will:
   - Re-run the pre-flight ritual (section 2).
   - Confirm the local-Ollama smoke test passes.
   - Seal `SPAWN_READY_<DATE>` with the smoke-test output.
   - Begin WP-1 in worktree `../ogir-wp-1`.

---

## 13. One-line project identity (preserved across all four WPs)

```
Order Get It Right -- Verified Processor.
A deterministic business audit engine written in pure-stdlib Python 3.12+.
Chain: 35,597 blocks, root 53bf9c9a... 272 tests, MATCH.
Operator: Justin Barnett. Jurisdiction: Commonwealth of Australia.
Ontology: 3.10, 55 patterns, R1-R6. Tagline: "Verified Processor".
```

End of directive. **Not yet executed.** Awaiting operator auth.
