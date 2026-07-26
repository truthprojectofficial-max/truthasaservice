# Order Get It Right -- Git Workflow (added 2026-07-18, F11)

Git is adopted **in parallel with** the Merkle chain. The chain is the
**trust anchor** (the tamper-evident witness of every audit decision).
Git is the **code management layer** (the diff/branch/remote-backup
ergonomics). They are not interchangeable. The chain is append-only
and is the source of truth for *what the engine decided*. Git is
mutable and is the source of truth for *what the operator changed in
the source tree*.

This document is the day-to-day operator's guide. For the rationale,
see `00_Strategy/STRATEGY.md` and `AGENTS.md` (the Git-adopted-in-
parallel note added 2026-07-18).

---

## 1. The two-track model

| Layer | What it answers | Mutability | Where it lives |
|-------|-----------------|------------|----------------|
| **Merkle chain** | "What did the engine decide, and when, in what order, with what inputs?" | Append-only | `03_Vault/facts_registry.json` |
| **Changelog** (JSONL) | "What did the operator notice and want a human reader to see?" | Append-only | `04_Validation/changelog.log` |
| **Git** | "What does the source tree look like at this point in time?" | Mutable (rebase-able) | `.git/` in the project root |

A code change produces a **Git commit** AND, if the change is
state-affecting at runtime, a **chain block**. The commit is the diff
the operator reviews; the chain block is the proof the engine was
running the version under review. Both are required for the change
to be defensible.

A non-code change (an operator observation, a system incident, a
changelog entry) produces only a chain block and a changelog line.
There is no Git diff because there is no source change.

---

## 2. The day-to-day ritual

### 2.1 Before starting work

```powershell
cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
git status                 # working tree should be clean
git log --oneline -5       # know the last 5 commits
git pull --ff-only         # if a remote exists; otherwise skip
```

If the working tree is dirty, finish the prior work or stash it
(`git stash --include-untracked --keep-index`) before starting a new
change. A dirty working tree is how accidental commits happen.

### 2.2 Making a code change

1. **Edit the source files.** Use your editor of choice. Git does not
   care which editor you use.
2. **Run the tests.** `cd 02_Technical && python -m pytest tests/ -q`.
   The suite must stay at 86 passed, 1 skipped (or improve). If a test
   breaks, revert (`git checkout -- <file>`) before continuing.
3. **Run the chain verifier.** `cd 02_Technical && python -m
   src.verify_chain`. The chain must print `RESULT: MATCH`. If the
   chain is broken, **stop and seal a `CHAIN_BROKEN_RECOVERY` block**
   before continuing -- see `04_Validation/TROUBLESHOOTING.md` for
   the recovery procedure.
4. **Seal a block to the chain** that records the change. Use
   `vault_io.append_block(event_type, payload)`. The block is the
   audit-side witness of the change; the Git commit (next step) is
   the source-side witness.
5. **`git add -A && git commit`.** The commit subject is the
   `event_type` from the chain block. The commit body lists the
   `file:line` references and the test result. One seal, one commit.

### 2.3 Making a non-code change (operator observation, incident)

1. **Append a line to `04_Validation/changelog.log`.** JSONL format,
   one line per cycle. Schema is documented in
   `04_Validation/OPEN_ITEMS_AND_REFERENCE.md`.
2. **Seal a block to the chain.** The event_type is the short
   SCREAMING_SNAKE_CASE label. The payload includes the changelog
   line's `type`, `summary`, and the operator's `binId`.
3. **No Git commit.** The source tree did not change.

### 2.4 Pushing to a remote

This build initialised a **local** Git repository on the branch
`ogir-build-2026-07-18`. There is no remote yet. To add a remote
(an operator decision -- see F11 in `OGIR_ASSESSMENT_2026-07-18.md`):

```powershell
git remote add origin <url>
git push -u origin ogir-build-2026-07-18
```

The remote URL options are out of scope for this build. Three
realistic options:

- **A USB stick that is the 1-2-3 backup**. Push to a `bare` repo on
  the USB. This is the cheapest offsite-compatible remote.
- **A self-hosted Gitea / Gitea-on-a-Pi**. Real branch ergonomics,
  real diffs, real diff history. Air-gap compatible if the Pi is
  inside the air-gap.
- **A third-party host (GitHub, GitLab, Codeberg)**. Convenient but
  trusts the third party with the chain (since the chain is in
  source control). Defeats the air-gap guarantee; do not use
  without operator decision.

---

## 3. Branch discipline

The default branch is `ogir-build-2026-07-18` (the build that
introduced Git). A future operator may rename this to `main` (one
command, no chain impact):

```powershell
git branch -m ogir-build-2026-07-18 main
```

Feature work goes on a named branch, not on `main`. The branch name
carries the finding id (F12, F13, F17) or the workstream name:

```powershell
git checkout -b f15-cleanup-seal
```

A feature branch is sealed to the chain the same way as a direct
commit on `main` -- the chain is process-wide, not branch-scoped.
A future bisect over Git will land on the same chain root for both
`main` and the branch, because the chain appends from the working
tree, not from the Git index.

A merge back to `main` is a Git-only event. The chain does not
observe merges. A merge to `main` should be followed by a chain
block with `event_type: BRANCH_MERGED_<workstream>_<date>` and a
payload listing the merged-in commit range. This keeps the chain
aware of which Git history is in effect at any moment.

---

## 4. The .gitignore and .gitattributes

- `.gitignore` excludes runtime artefacts that are not part of the
  trust anchor: `.bak-pre-*` backups, `__pycache__/`, `.pytest_cache/`,
  `04_Validation/logs/`, `04_Validation/reports/`,
  `04_Validation/squeal-reports/`, `data/outbox/`, and
  `03_Vault/affidavit_transcript.txt` (the rendered affidavit,
  which is regenerated by `/api/affidavit`).
- `.gitignore` **does not exclude** `03_Vault/facts_registry.json`
  or `04_Validation/changelog.log`. Both are the trust anchor and
  must be in source control.
- `.gitattributes` pins line-ending policy. Python, Markdown, JSON,
  Rust: LF in repo. PowerShell, batch: CRLF. Binary files: marked
  `binary` so Git never rewrites them. The JSON pin is critical --
  a CRLF rewrite of a chain block file would change the file
  SHA-256 and break the trust anchor.

---

## 5. What Git does NOT do

- Git does **not** verify the chain. `git log` is a diff of the
  source tree; it does not call `verify_chain`. The chain verifier
  is still `python -m src.verify_chain` (or `cd 02_Technical && python
  -m src.verify_chain --print-refs` for the six reference
  fingerprints).
- Git does **not** record operator observations. The changelog does
  that. A Git commit on `changelog.log` would be a metadata diff
  with no source-change meaning; the chain block is the witness.
- Git does **not** replace the chain. A rebased chain is a
  different chain. The chain is append-only; Git is mutable; the
  two are not interchangeable. If the two ever disagree (a
  commit-seal mismatch, a rebase that re-orders the chain), the
  chain is the source of truth.

---

## 6. Common mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| `git commit` without sealing the chain first | The diff is in Git but the audit witness is not. A future auditor sees a source change with no chain entry. | Always seal first, then commit. The commit subject should match the chain `event_type`. |
| `git commit` with the chain unverified | A `MATCH` check is not the same as a `git status` check. The chain may be broken. | Run `python -m src.verify_chain` before each commit. |
| `git push --force` | Rewrites remote history. Chain blocks in the old history are not re-derivable from the new history. | Never force-push to a remote that holds chain-bearing commits. The 1-2-3 backup does not need force. |
| Sealing a block without a source change (operator observation) and then committing | A Git diff for the chain block alone shows nothing. The commit is empty. | Don't commit operator-observation blocks. Append to `changelog.log` and seal only. |

---

## 7. Sealing the F11 decision

The decision to adopt Git in parallel is sealed to the chain as
`GIT_ADOPTED_IN_PARALLEL_2026_07_18`. The block records:

- The decision (adopt / do not adopt)
- The trust-anchor split (chain = audit, Git = code)
- The branch name and the initial commit hash
- The list of Git-side changes that go with the decision
  (`.gitignore`, `.gitattributes`, this file, the AGENTS/STRATEGY
  notes)

The chain is still the source of truth for *what the engine
decided*. Git is the source of truth for *what the operator
committed*. Both are required for a defensible record.

---

**Document generated:** 2026-07-18
**Sealed to chain:** `GIT_ADOPTED_IN_PARALLEL_2026_07_18` (this build)
**Re-derivable:** yes. The workflow is documented in this file and
in `AGENTS.md`.