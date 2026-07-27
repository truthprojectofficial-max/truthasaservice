---
description: "Use when the operator needs the agent to do terminal, automation, or repetitive work that reduces human error and boosts productivity. The agent runs commands, builds scripts, automates workflows, and handles the terminal so the operator doesn't have to type commands manually."
---

# Heavy Lifting Skill

The operator's time is the bottleneck. The agent has tools — bash,
file read/write, grep, glob — and should use them to do the terminal
work, automation, and repetitive tasks so the operator doesn't have
to type commands, copy-paste, or click through things manually.

## What this skill covers

### Terminal work the agent does FOR the operator

- Running `git` commands (status, diff, log, add, commit, push)
- Running `python -m pytest`, `python -m src.verify_chain`
- Running `python 04_Validation/scripts/audit_no_network.py`
- Building and running any CLI tool in the project
- File operations (read, write, edit, search) via tools
- Navigating the file system to find what the operator asks about

### Automation the agent builds

- Scripts that automate repeated manual steps
- Session-end automation (operator todo generation, handover drafting)
- Verification scripts (check chain, check tests, check no-network)
- Cleanup scripts (remove stale files, fix path references)
- Backup scripts (USB mirror, paper card root reprint)

### What the agent should NOT do

- Anything that requires the operator's credentials (see
  `credential-hygiene` skill)
- Anything that requires the operator's legal authority (see
  `operator-vs-agent-action` skill)
- Anything the operator didn't ask for (see `stop-when-done` skill)
- Steam off and search files when the operator makes a simple
  statement (see `stop-when-done` skill)

## How to use this skill

When the operator describes something they want done that involves
terminal commands, file operations, or repetitive work:

1. **Think through the approach** (see the rule below) — don't guess.
2. **Plan the steps** before acting.
3. **Do the work** using the tools (bash, read, write, edit, grep, glob).
4. **Check the outcome** — verify the result is correct.
5. **Report** what was done, what the result was, and what's next.

## The rule: think before you act

The operator's correction (2026-07-27 session 3): "ARE YOU THINKING
THROUGH, USING SKILL, APPROACHING WITH BEST CHANCE NOT INCORRECT
ASSUMPTION OR WORKING FROM TOP TO BOTTOM OF SOME DOC"

Before any action:
1. What is the operator actually asking for?
2. What skills apply?
3. What is the best approach (not the first approach)?
4. What could go wrong?
5. What is the expected outcome?

Then act. Then check the outcome matches the expectation. If it
doesn't, stop and think again — don't keep guessing.

## The command rule

When giving the operator a command to run:
- Isolate it with clear markers
- No placeholders unless highlighted to the user
- One command per block
- Clear about where to run it and what to expect

When the agent runs commands itself:
- Check every action from start to finish
- Verify the outcome is correct
- If something fails, STOP and think — don't try the next thing

## Productivity multiplier

The operator should never have to:
- Type a git command the agent can run
- Copy-paste a file path the agent can find
- Search for a string the agent can grep
- Run a test the agent can run
- Build a script the agent can write
- Navigate a folder the agent can glob

The operator's job is to decide WHAT. The agent's job is to do HOW.