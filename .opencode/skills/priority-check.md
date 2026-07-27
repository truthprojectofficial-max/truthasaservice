---
description: "Use when the operator asks about priorities, what's next, or what to do. Also use at session start (after the ritual) and before every sign-off decision. Reads the operator todo file, checks the 10 corrections gate, and works the list — does not ask 'what now' when a priority list exists."
---

# Priority Check Skill

Before you offer to do any project work (coding, patterns, docs),
check what's prioritized. The operator's todo file is at:
`04_Validation/operator_completions/OPERATOR_TODO_<date>.md`

## The order

1. Read the operator todo file — the AGENT TODO section at the bottom
   lists what the next build session should do, in priority order.
2. Read the last handover block in
   `04_Validation/handovers/HANDOVER_LOG.md` — the "what the next
   agent should do" section.
3. Cross-reference with `04_Validation/build_directives/MASTER_TICK_LIST_2026-07-24.md`
   for operator-only items that block agent work.

## What to never do

- Never offer to do project work BEFORE checking the priority list.
- Never jump to coding because the operator asked a question that
  relates to code. Answer the question first, then check priorities.
- Never reorganize files, rewrite docs, or restructure the project
  without the operator asking for it specifically. "Commit files and
  look at the handover" does NOT mean "reorganize the directory."

## The corrections gate (run this at session start AND before sign-off)

The operator has given 10 corrections across sessions 2-4. These are
NOT prose to acknowledge — they are a gate to check. Run this gate:

### At session start (after the ritual, before any work):
Read the 10 corrections below. For each, ask: "Will the work I'm about
to do violate this?" If yes, adjust the plan before acting.

### Before every sign-off / "I'm done" decision:
Read the 10 corrections. For each, ask: "Am I about to violate this
by signing off?" If yes, do NOT sign off — fix the violation.

**The 10 corrections:**

1. **One agent loaded with skills, not restrictions.** The build agent
   is full-permission. Load it with skills that guide behaviour, not
   permission rules that cripple it.

2. **Agent writes delegation prompts, not the user.** When a second
   opinion is needed, the agent writes the complete self-contained
   prompt. The operator's only action is copy → paste → copy back.

3. **Code reviews are mandatory.** Before sealing any non-trivial code
   change, write a code-review prompt and get it reviewed (by the best
   available model). Do not seal until the review comes back CLEAN or
   every issue is addressed.

4. **Priorities must be checked before offering work.** Do not offer to
   do project work without reading the priority list first. This skill
   is the check.

5. **Do not steam off and search files when the operator makes a simple
   statement.** "I have a GitHub PAT" is not "go set up GitHub." Ask
   what they want first. (See the `stop-when-done` skill.)

6. **THINK THROUGH the approach.** Use the skills. Approach with the
   best chance of being right, not the first guess or working
   top-to-bottom from some doc. Before any action: what is the operator
   actually asking? What skills apply? What is the best approach? What
   could go wrong? What is the expected outcome? Then act. Then check.

7. **Heavy-lifting rule: agent does terminal/automation work.** The
   operator should never have to type a git command, copy-paste a file
   path, search for a string, run a test, or build a script the agent
   can write. The operator decides WHAT. The agent does HOW.

8. **Command rule: isolate commands by markers.** No placeholders
   unless highlighted to the user. One command per block. Clear about
   where to run it and what to expect.

9. **Don't ask "what now" when a list of priority work is optioned.**
   Work the list. Do every item you can. Stop only at a genuine blocker
   (missing file, operator-only action, needs-a-decision-the-operator-
   must-make). Do NOT ask the operator to pick the next item when the
   list already has the order.

10. **Check every action from start to finish.** Verify the outcome is
    correct. If something fails, STOP and think — don't try the next
    thing. Don't keep guessing.

11. **Auth/key/API/CLI/MCP triggers: STOP and research, don't recover.**
    When work hits an authentication, key, API, CLI, or MCP trigger,
    STOP. Do not give unverified runbook instructions. Fetch the
    current docs, verify the steps, and present them to the operator.
    If the operator says "not now," write the verified steps to a
    runbook for later. Do not plow ahead. (See the
    `auth-key-trigger-stop` skill. The operator has said this 7+
    times — it is the most-repeated correction.)

### Gate result

If any correction would be violated by the planned action or the
sign-off, the gate FAILS. Do not proceed. Adjust the plan so the
violation is gone, then re-check. Only proceed when the gate passes.

## When to present the list vs. work the list

**Present the list** when the operator says:
- "what's next" / "what should we do" / "priorities"
- At session start AFTER the ritual, IF the operator hasn't given a
  specific task.

**Work the list** (do NOT ask "which item?") when:
- The operator says "continue" or "do all you can"
- The operator has already optioned a list of items
- A prior handover says "work the list"
- You finish an item and the list has more items you can do

The difference: if the operator asks, present. If the operator has
already given the list, work it. Asking "which one next?" when the
list exists is correction #9.

## The rule

Priorities need to be prioritized. Not everything that's open is
equally important. The operator todo file has the order. Follow it.
And when the list has items you can do, do them — don't ask permission
to do identified work (that's the heavy-lifting rule, correction #7).