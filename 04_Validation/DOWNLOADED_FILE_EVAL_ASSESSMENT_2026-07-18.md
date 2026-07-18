# Assessment of three held files as EVAL case sources

## 1. `C:\Users\justo\Downloads\Working Clude codex.txt`

- **Size**: 565,467 characters, ~9,005 lines.
- **Content**: Codex/Claude development session log. Includes repeated project analysis, S3-vs-filesystem argument, deployment decisions, EVAL run reports, and implementation notes.
- **Usable for EVAL cases?** Limited.
- **Why**: It is not curated case material. It contains internal project reasoning, not external AI-inventive text. Could mine a few passages for **TRUE NEGATIVE** "dry technical decision text" or **TRUE POSITIVE** "cloud-lock-in marketing rebuttal", but most of it is self-referential.
- **Best use**: Raw material for an adversarial case where a model falsely claims S3 is required for an air-gap design.

## 2. `C:\Users\justo\Downloads\entry_points (1).docx`

- **Size**: ~2,500 characters.
- **Content**: Python `virtualenv` package `entry_points.txt` listing console scripts and plugin hooks (`bash`, `batch`, `cshell`, `fish`, `nushell`, `powershell`, `python`, `xonsh`, etc.).
- **Usable for EVAL cases?** Not directly.
- **Why**: It is configuration metadata. No natural-language claims. Could be used as a **TRUE NEGATIVE** "dry technical list", but it adds no deception-detection signal.

## 3. `C:\Users\justo\Downloads\Justin B Resume.docx`

- **Size**: ~1,700 characters.
- **Content**: Personal resume for Justin Barnett.
- **Usable for EVAL cases?** Limited.
- **Why**: It is a straightforward CV with no deception markers. Could be a **TRUE NEGATIVE** for honest self-description, but the signal is weak.

## Recommendation

These three files are **not high-value EVAL case sources** compared to what is already committed:

- `Verified.docx` (40,534 chars, editorial, strong TRUE NEGATIVE).
- `Williams AI Transcript` (59 KB, legal register, strong TRUE NEGATIVE).
- `tuff claude.txt` (Claude legal commentary, TRUE NEGATIVE + adversarial flip).

If you want to use the downloads anyway, the best approach is to extract one or two TRUE NEGATIVE dry-text cases from the Codex log and resume, and ignore `entry_points.docx`.

However, the user's stated goal is "AI inventive with their information" cases. None of these three files contain that. For that, public famous cases (Mata, UK, BC, USPTO) are still the best source, and the extended suite already covers them.
