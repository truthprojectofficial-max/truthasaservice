---
description: "Use when changing any constant in 02_Technical/config/constants.py. A CONSTANTS_BUMP requires a sealed block recording the old value, new value, reason, and test result. Changing constants without a seal breaks the trust anchor."
---

# Constants Bump Skill

The 41 named constants in `02_Technical/config/constants.py` ARE the
runtime — 19 numeric decision thresholds plus metadata/paths/version
strings (including `LATTICE_FRAMING` for the optionality gate). Changing
any of them is a `CONSTANTS_BUMP`.

## The procedure (5 steps)

1. **Record the old value** before editing. Copy the exact line.
2. **Edit** the constant in `config/constants.py`.
3. **Run tests**: `python -m pytest tests/ -q --no-header` — must pass.
4. **Seal a CONSTANTS_BUMP block**:
   ```python
   from src.io.vault_io import append_block
   append_block("CONSTANTS_BUMP_<date>_<constant_name>", {
       "constant": "<CONSTANT_NAME>",
       "old_value": <old>,
       "new_value": <new>,
       "reason": "<why the change is justified>",
       "test_result": "<passed N / skipped N / failed N>",
   })
   ```
5. **Commit** with subject `CONSTANTS_BUMP_<date>_<constant>: block NNNNN sealed.`

## When this triggers

- Any edit to `02_Technical/config/constants.py`, no matter how small.
- A threshold change, a path change, a version string change, a framing
  string change. All are CONSTANTS_BUMPs.
- Adding a NEW constant to the file.

## What requires a CONSTANTS_BUMP

| Change | CONSTANTS_BUMP? |
|--------|-----------------|
| Change a numeric threshold | YES |
| Change a path string | YES |
| Change a version string | YES |
| Change LATTICE_FRAMING text | YES |
| Add a new constant | YES |
| Rename a constant | YES (record old + new name) |
| Remove a constant | YES (record removal + why) |

## What does NOT require a CONSTANTS_BUMP

- Editing a comment in the file (not a state change).
- Reformatting whitespace (not a state change).
- Editing any file OTHER than `config/constants.py`.

## The rule

The 19 numeric thresholds are the entire audit decision. A change
without a seal is an unrecorded shift in what the engine decides. The
chain must witness every shift. No silent threshold changes.