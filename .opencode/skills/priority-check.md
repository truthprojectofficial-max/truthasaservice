---
description: "Use when the operator asks about priorities, what's next, or what to do. Reads the operator todo file and the open items, presents a prioritized list. Never offer to do project work before checking the priority list."
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

- Never offer to do the 2 AI-dialect false negatives, the Tauri sync,
  or the automation layer BEFORE checking the priority list. These are
  on the list but may not be the top priority.
- Never jump to coding because the operator asked a question that
  relates to code. Answer the question first, then check priorities.
- Never reorganize files, rewrite docs, or restructure the project
  without the operator asking for it specifically. "Commit files and
  look at the handover" does NOT mean "reorganize the directory."

## When to present the list

When the operator says:
- "what's next"
- "what should we do"
- "priorities"
- "continue"
- Or when a session starts after the ritual and the operator hasn't
  given a specific task

Present the priority list from the operator todo file, and ask which
item to work on. Do NOT start working on item 1 without confirmation.

## The rule

Priorities need to be prioritized. Not everything that's open is
equally important. The operator todo file has the order. Follow it.