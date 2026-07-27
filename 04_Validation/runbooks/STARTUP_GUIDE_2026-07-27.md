# OGIR Startup Guide — one page

> Last refreshed 2026-07-27. Read this before you open any tool.

## The golden rule

**Only the build agent (opencode + `glm-5.2:cloud`) seals to the chain,
commits, or edits source.** Everything else is read-only on the project.

## Which tool for which job

| Job | Tool | Model | Seals? | Commits? |
|-----|------|-------|--------|----------|
| Change project code/docs (witnessed) | opencode (build agent) | `glm-5.2:cloud` | YES | YES |
| Think / review / reason (no changes) | opencode (tell it "read-only") | `glm-5.2:cloud` | NO | NO |
| Long research with browser | Hermes | `minimax-m3:cloud` | NO | NO |
| Draft code in a sandbox | Aider | `qwen2.5-coder` (local) | NO | NO (sandbox) |

## Start the build agent

1. Terminal in `C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight`
2. Launch opencode — it auto-loads `.opencode/agent/build.md`
3. The agent's FIRST action must be the 5-check ritual:
   `verify_chain` → MATCH → read handover → read INDEX → `pytest` →
   seal `AGENT_SIGN_ON_OPENCODE`. If it skips this, stop.
4. At session end the agent runs the SIGN-OFF ritual: verify chain,
   tests, append handover, push, seal `AGENT_SIGN_OFF_OPENCODE`.

## Read-only reasoning session

Same tool, tell it: **"Read-only. Do not seal, commit, or edit files."**
It can read, search, and run `verify_chain` / `pytest`. No sign-off
needed — nothing was sealed.

## Models

**Approved:**
- `glm-5.2:cloud` — build agent + reasoning (the project default)
- `minimax-m3:cloud` — Hermes default
- `qwen2.5-coder` (cloud or local 7B) — Aider code drafting

**Not approved:** `nemotron-3-super:cloud` (hedged + looped on
2026-07-27, produced an unwitnessed handover). Any model change for the
build agent requires a sealed `MODEL_APPROVAL_<model>_<date>` block.

Local models on `D:\OllamaModels`: `Qwen2.5-coder`, `qwen3.5:9b`,
`llama3.1:8b`, `DeepSeek-R1-Distill-Qwen-7B`, `gemma3`, `Llama3.2`, +
reasoning variants. Use for offline work; none are approved to seal.

## Hard rules

- Never put model configs in `04_Validation/` (the broken duplicate is
  deleted; the only opencode config is at the repo root).
- Never use `nemotron-3-super:cloud` for OGIR work.
- Only the build agent seals. Hermes and Aider are not chain witnesses.
- Aider works in `C:\AIDERTESTBOX` (sandbox) — never in the live tree.

## Where things are

- Chain + handover + INDEX: see `INDEX.md` (the project map).
- Folder map of `04_Validation/`: see §9 of INDEX.md.
- Operator action list: `04_Validation/operator_completions/OPERATOR_TODO_2026-07-27.md`.