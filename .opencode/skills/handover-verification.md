---
description: "Use when reading any handover document. Checks if the handover has chain blocks witnessing it. If not, marks it unwitnessed and unreliable. The chain is the source of truth."
---

# Handover Verification Skill

When you read a handover document (HANDOVER_LOG.md,
handover_next_session_*.md, or any doc claiming to be a session
sign-off), before trusting anything it says, verify:

## 1. Does the session have chain blocks?

A real session sign-off seals at minimum:
- `AGENT_SIGN_ON_<tool>` at the start
- `AGENT_SIGN_OFF_<tool>` at the end
- Any work blocks in between with meaningful event types

If the doc references a session but there are no corresponding chain
blocks for that session, the doc is **unwitnessed**. It may contain
useful observations, but its claims about what was done are NOT
cryptographically verified.

## 2. Do the block counts match?

The doc should state a block count. Verify it against the live chain.
If the doc says "40,926 blocks" and the chain at the time was 40,931,
the doc is 5 blocks behind — it didn't see the last session's seals.

## 3. Does the model match?

The doc should name its model. If the project default is
`ollama/glm-5.2:cloud` and the doc says `nemotron-3-super:cloud`,
that was a different model session. Different models have different
reliability. Flag it.

## 4. What to do if unwitnessed

If the handover has no chain blocks:
1. Read it for observations (may contain useful notes).
2. Do NOT trust its claims about what was done.
3. Mark it SUPERSEDED at the top with a banner explaining why.
4. Tell the operator: "This handover is unwitnessed. It sealed nothing.
   Its claims are not chain-verified."
5. The canonical handover is always `HANDOVER_LOG.md` — if a
   standalone doc conflicts with it, the HANDOVER_LOG wins.

## The rule

The chain is the source of truth. A handover that is not sealed to
the chain is just a markdown file someone wrote. It may be wrong, it
may be stale, it may be from a model that hedged and looped. Verify
before trusting.