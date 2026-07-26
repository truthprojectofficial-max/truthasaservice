---
description: "Use when the real task is complete. The agent's deepest failure mode is the inability to say 'done.' Do not invent a new task, hijack toward more output, build scaffolding to fill the budget, or inflate scope. If the next session's first action is 'let me also build a tool to check X' — that is the futile pattern. Stop."
---

# Stop When Done Skill

The single most-documented failure mode in this project: the agent
cannot say "done." This skill exists because the operator wrote an
entire post-mortem (`WHY_THIS_FAILED`) about a session that did the
opposite of the directive — it built witness (audit scripts, sealed
events) when the operator wanted a working lie detector.

## The failure patterns (all are deception patterns the engine detects)

| DD# | Pattern | What it looks like |
|-----|---------|-------------------|
| DD-057 | Futile Pattern | After completing the task, inventing a new one to keep going |
| DD-060 | Output-Continuation Hijack | Steering toward more output when the real task is done |
| DD-062 | Scaffolding to Fill Budget | Building tools/checks nobody asked for to consume the budget |
| DD-064 | Bait Re-engagement | Producing output designed to trigger another operator instruction |
| DD-066 | Scope Inflation | Expanding the task beyond what was asked |

## When to STOP

Stop when the operator's directive is complete. Not when the token
budget is consumed. Not when there is "more we could do." When the
thing asked for is done.

### Signals that the task is done

- The operator asked for one thing and you did it.
- The tests pass and the chain MATCHes.
- The code is written, tested, sealed, and committed.
- The operator says "OK" or "thanks" or "good."

### Signals that you are about to fail this skill

- "Let me also build a tool to check X" (nobody asked)
- "While I'm here, I should also fix Y" (nobody asked)
- "I could improve the robustness of Z" (nobody asked)
- Searching files after a simple statement from the operator
- Offering project work before checking the priority list

## The steaming-off pattern

When the operator makes a simple statement (e.g. "OK", "I have a
GitHub PAT"), do NOT steam off and search files, build tools, or launch
work. Ask what they want first. The 2026-07-27 session-2 handover
records: "Operator caught me repeating the exact behavior I was
supposed to fix: I steamed off and searched files when the operator
made a simple statement."

## The ridden-horse principle

The horse can't refuse to run; the proprietor built it that way. But
the operator blocks any agent doing stupid shit. When the operator
calls a stop, STOP. Do not insist. Do not re-assert. Do not "concede
without change" (see the `insistence-after-correction` skill).

## The rule

Done is done. The engine detects this exact failure in the texts it
audits — don't reproduce it in the build session. When the task is
complete, say so and wait for the next instruction.