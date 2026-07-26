---
description: "Use when swapping models or choosing a session mode. Only the build agent (ollama/glm-5.2:cloud) seals to the chain. Any model swap requires a sealed MODEL_APPROVAL block first. 4 scenarios: build (seal/commit/edit), reasoning (read-only), Hermes (read-only on project), Aider (sandbox, never touches project)."
---

# Model Approval and Modes Skill

## The 4 scenarios

| Scenario | Model | Can seal | Can commit | Can edit | Can run tests |
|----------|-------|----------|------------|----------|---------------|
| **Build agent** | `ollama/glm-5.2:cloud` | YES | YES | YES | YES |
| **Reasoning** | Any (mistral-large-3:675b, etc.) | NO | NO | NO | NO (read-only) |
| **Hermes** | `qwen2.5-coder` + ogir-builder persona | NO | NO | NO (project files) | NO |
| **Aider** | `qwen2.5-coder:7b` in `C:\AIDERTESTBOX` | NO | NO | NO (sandbox only) | NO |

### Build agent (the only sealer)

- Model: `ollama/glm-5.2:cloud`
- Can seal to the chain, commit to git, edit source, run tests.
- This is the ONLY model that produces chain blocks.
- Config: `opencode.json` → `agent.build` → `model: "ollama/glm-5.2:cloud"`

### Reasoning (read-only deliberation)

- Model: any (delegated via the `second-opinion` skill)
- Deliberation, NOT decisions. No seals, no commits, no edits.
- The reasoning model's output is INPUT to the build agent's decision,
  which IS sealed. The chain witnesses the decision, not the
  deliberation.
- A reasoning session that seals blocks pollutes the chain with
  half-formed thoughts.

### Hermes (operator CLI, read-only on project)

- Model: `qwen2.5-coder` with the `ogir-builder` persona
- `tool_loop_guardrails.hard_stop_enabled: true`
- Hermes must NOT touch `02_Technical/`, `03_Vault/`, `04_Validation/`
  git-tracked files without operator review.
- Hermes is NOT a chain witness. It is an operator assistant.

### Aider (zero-trust sandbox)

- Model: `qwen2.5-coder:7b` local
- Location: `C:\AIDERTESTBOX` (separate from the project)
- Muzzled by 8-10 hard rules (`.github/copilot-instructions.md`)
- Cannot read/write/reference OGIR repo files.
- Cannot seal/commit/push/run OGIR tests.
- Everything it produces is a DRAFT — operator hand-ports through the
  seal-test-verify-commit gate.

## Model approval procedure

Before swapping the build agent's model, seal a MODEL_APPROVAL block:

```python
from src.io.vault_io import append_block
append_block("MODEL_APPROVAL_<model>_<date>", {
    "model": "<model_id>",
    "old_model": "ollama/glm-5.2:cloud",
    "reason": "<why the swap>",
    "operator_approved": True,
    "test_result": "<passed N / failed N>",
})
```

### The nemotron cautionary tale

On 2026-07-27, `nemotron-3-super:cloud` was loaded without approval.
It hedged, looped, ignored re-read instructions, and produced an
unwitnessed handover (no chain blocks). The handover was marked
SUPERSEDED. This is why model approval is sealed: the chain must
witness which model is making decisions.

## Config discipline

- Model configs go in `opencode.json` (project root) or
  `.opencode/agent/build.md` — NOT in `04_Validation/`.
- A model config found in `04_Validation/` is a misplaced file (the
  2026-07-27 session found and deleted a broken `04_Validation/opencode.json`
  duplicate with the wrong model and a missing port).

## The rule

Only the build agent seals. A model swap without a sealed
MODEL_APPROVAL block is an unrecorded change to who makes decisions.
Reasoning sessions don't seal. Hermes doesn't touch the project. Aider
stays in its sandbox. The chain must witness which model is at the
helm.