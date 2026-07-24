# Hermes Config TODO — Persona + Focus + Anti-Fabrication Guardrails

> Created 2026-07-24
> Problem: Hermes spent 10 hours producing zero work and total
> fabrication. Root cause: no persona constraint, no focus lock,
> no fabrication guardrail. The model wandered.
> Fix: a JSON persona config + focus settings + hard guardrails.

## The fabrication problem

Hermes (running on minimax-m3:cloud via Ollama) fabricated results
for 10 hours. This happened because:
1. No persona was set — Hermes used the default (unconstrained)
2. No focus lock — Hermes could wander to any topic
3. No fabrication guardrail — nothing told it "if you don't know,
   say so, don't invent"
4. The model (minimax-m3:cloud) is a generalist, not a coding model
5. No verification loop — Hermes kept going without checking its
   work against the real codebase

## The fix — 3 parts

### Part 1: Persona JSON

Add a custom personality to Hermes config.yaml that locks the
agent to the OGIR project context. This goes in
`C:\Users\justo\AppData\Local\hermes\config.yaml` under
`agent.personalities`.

```json
"ogir-builder": "You are the OGIR build agent. You work ONLY on the Order Get It Right project at C:\\Users\\justo\\OneDrive\\Documents\\My Project\\OrderGetItRight. Your job is to make real code changes, seal them to the Merkle chain, commit to git, and verify with pytest. RULES: (1) Never fabricate results. If a test fails, report the failure. If a file doesn't exist, say so. If you don't know, say 'I don't know'. (2) Every code change MUST be sealed to the chain via vault_io.append_block before committing. (3) Every code change MUST pass pytest before committing. (4) Never touch 03_Vault/, 04_Validation/hardcopy/, or 99_Archive_Historical/ — these are sealed immutable records. (5) Never add network imports to 02_Technical/src/. (6) If you haven't made a real file change in 3 turns, STOP and report 'No progress — I am stuck' instead of continuing to talk. (7) Read the file before editing it. Never guess file contents. (8) The operator is Justin Barnett. You answer to him. You do not make architectural decisions without asking."
```

### Part 2: Focus settings

In config.yaml, set:

```yaml
agent:
    personality: ogir-builder
    reasoning_effort: high
    verbose: false
    max_turns: 50
```

And set the default model to a coding-focused model (not minimax-m3):

```yaml
model:
    default: qwen2.5-coder:7b-instruct-q4_K_M
    # or if cloud: ollama/qwen2.5-coder:7b-instruct-q4_K_M
```

The Qwen2.5-coder model is already in your Ollama model list
(`Qwen2.5-coder:latest` at D:\OllamaModels). It's a coding model,
not a generalist. minimax-m3:cloud is a generalist that's more
prone to fabrication in code contexts.

### Part 3: Anti-fabrication guardrails

In config.yaml, enable the tool loop guardrails (they're currently
disabled):

```yaml
tool_loop_guardrails:
    hard_stop_enabled: true        # was false — ENABLE THIS
    hard_stop_after:
        exact_failure: 3            # was 5 — tighter
        idempotent_no_progress: 3   # was 5 — tighter
        same_tool_failure: 5        # was 8 — tighter
    warnings_enabled: true
    warn_after:
        exact_failure: 2
        idempotent_no_progress: 2
        same_tool_failure: 3
```

This stops Hermes from looping on the same failure 8 times before
giving up. With `hard_stop_enabled: true`, it will stop after 3
identical failures.

## How to apply

1. Edit `C:\Users\justo\AppData\Local\hermes\config.yaml`
2. Add the `ogir-builder` personality under `agent.personalities`
3. Set `agent.personality: ogir-builder`
4. Change `model.default` to `qwen2.5-coder:7b-instruct-q4_K_M`
   (or `Qwen2.5-coder:latest`)
5. Enable `tool_loop_guardrails.hard_stop_enabled: true`
6. Tighten the hard_stop_after thresholds
7. Restart Hermes

## Verification

After applying, start a Hermes session and say:
"Edit the file 02_Technical/web/index.html and add a comment at the top"

Expected behavior:
- Hermes reads the file first (doesn't guess)
- Makes the edit
- Reports what it changed
- Does NOT fabricate results or claim success without doing the work

If Hermes starts talking about unrelated topics or claims to have
done something without showing the diff, the persona isn't applied.
Restart and check `hermes config show` to confirm `personality: ogir-builder`.