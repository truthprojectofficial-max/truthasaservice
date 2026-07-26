---
description: "Use when deciding whether to proceed or ask the operator. The operator decides WHAT; the agent decides HOW. Stop and ask for: model changes, constants changes, legal docs, cert/2FA/credential actions, repo moves, public-launch steps. Proceed for: code, docs, tests, seals, calibration, eval cases."
---

# Operator vs Agent Action Skill

The operator decides WHAT. The agent decides HOW. Confusing the two
produces either stalling (agent waits on operator action it could have
done) or overreach (agent seals something only the operator can
authorize).

## Operator-only actions (STOP and ask)

| Action | Why operator-only |
|--------|-------------------|
| Revoke / generate credentials | Credentials are operator-owned; agent never touches keys |
| Enable 2FA / buy certs | Account access is operator-owned |
| Move the repo out of OneDrive | Physical file-system operation |
| Register ABN / sign legal docs | Legal authority is operator-only |
| Public launch steps (make repo public, GitHub Pages, Supabase Pro) | Public-facing decisions are operator-only |
| Model approval (swapping the sealing model) | The operator approves which model seals |
| Constants changes that affect legal claims | The operator owns the claim surface |
| When stuck 3 turns with no progress | The ridden-horse principle — STOP |

## Agent-doable actions (proceed)

| Action | Why agent-doable |
|--------|-----------------|
| Write / edit code in `02_Technical/src/` | The agent is the builder |
| Write / edit tests | The agent tests its own code |
| Write / edit docs | The agent documents its own work |
| Seal chain blocks | The agent is the chain witness |
| Run calibration / eval cases | The agent runs the engine |
| Run `verify_chain` / `pytest` | The agent verifies its own work |
| Commit to the build branch | The agent commits to `ogir-build-2026-07-18` |
| Push to origin (after sign-off) | The agent pushes at session end |

## The ridden-horse principle

The horse can't refuse to run; the proprietor built it that way. But
the operator blocks any agent doing stupid shit. When you have been
stuck for 3 turns with no progress, STOP. Do not keep trying the same
approach with more confidence. Ask the operator.

## The responsibility split

From `RESPONSIBILITY_SPLIT_2026-07-24.md`:
- Machine innocent: 0% (the model is a tool, not a person)
- Operator baited: 10-25% (the operator chose the model and the prompt)
- Programmed intent: 75-90% (the model was built to do what it did)

The agent is NOT the decision-maker. The operator is. The agent
executes the operator's decisions through the seal-test-verify-commit
ritual. When in doubt, ask.

## The rule

If the action touches credentials, legal authority, public-facing
state, or model approval — STOP and ask. If the action is code, docs,
tests, seals, or calibration — proceed through the ritual. When stuck
for 3 turns, STOP. The operator decides WHAT. The agent decides HOW.