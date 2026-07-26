---
description: "Use when a shortcut or expedient is proposed. Checks if a right-first way exists. If not, seals the workaround to the chain with the full record. Workarounds unrecorded lead to project death downstream."
---

# Workaround Discipline Skill

When you (the agent) or the operator proposes a shortcut, an expedient,
a "just do it for now" — before acting, check:

## 1. Is there a right-first way?

Ask: "Is there a way to do this correctly right now, without the
workaround?" Search the codebase, the docs, the chain. If a right-first
way exists and is feasible, do that instead.

## 2. If no right-first way exists

The workaround is allowed ONLY if:

- The operator confirms there is no other way, OR
- Stopping to find the right-first way would kill the project (and
  the operator says so), OR
- The workaround was already done (retroactive recording)

## 3. Seal it (mandatory)

Before (or immediately after, if retroactive) taking the workaround,
seal a block to the chain:

```
event_type: WORKAROUND_TAKEN_<date>_<short_name>
payload:
  workaround: <what the workaround is>
  why_necessary: <why it was needed>
  right_first_alternative: <what the correct way would be>
  why_not_used: <why the correct way couldn't be used at the time>
  cost: <what technical debt or risk this introduces>
  cleanup_path: <how to fix it later>
  operator_confirmed: true
```

## 4. Log it

Append to `04_Validation/reference_misc/changelog.log` with type
`incident` and a one-line summary.

## 5. Track it

Add to `04_Validation/operator_completions/OPERATOR_TODO_<date>.md`
as an open item with a cleanup path.

## The rule

A workaround that is not sealed, logged, and tracked is a silent
failure. The project does not accept silent failures. Workarounds
unrecorded lead to project death downstream, mostly at deployment.

## When to trigger

- The operator says "just do it for now" or "I'll fix it later"
- You (the agent) are about to take a shortcut in code
- You see a pattern that doesn't match the conventions because
  "there wasn't time"
- The operator describes something they did previously that was
  a workaround and wasn't recorded (retroactive — seal it now)