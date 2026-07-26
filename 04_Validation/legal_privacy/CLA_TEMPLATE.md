# Contributor License Agreement (CLA) — OGIR

> **DRAFT — not legally binding until reviewed by a lawyer.**
> Created 2026-07-24. For any contributor who submits code to OGIR.

---

## Contributor License Agreement

Thank you for contributing to Order Get It Right (OGIR). This
agreement ensures that the project can use your contribution while
you retain ownership of your work.

### 1. Definitions

- **"Project"** means Order Get It Right, operated by Justin Barnett
- **"Contribution"** means any code, documentation, or other work you submit
- **"You"** means the contributor
- **"Licensor"** means Justin Barnett (the project operator)

### 2. Copyright License

You grant Justin Barnett a perpetual, worldwide, non-exclusive,
royalty-free license to use, copy, modify, distribute, and
sublicense your Contribution under the MIT License.

You retain copyright in your Contribution.

### 3. Patent License

You grant Justin Barnett a perpetual, worldwide, non-exclusive,
royalty-free patent license to make, use, sell, and distribute your
Contribution where your Contribution is covered by a patent you own
or control.

### 4. Original Work

You represent that your Contribution is your original work and that
you have the right to submit it under this agreement.

### 5. No Warranty

You provide your Contribution "AS IS" without warranty of any kind.

### 6. Third-Party Content

If your Contribution includes third-party content, you must disclose
the source and license of that content.

### 7. Determinism Acknowledgement

You acknowledge that OGIR is a deterministic, air-gapped forensic
tool. Your Contribution must not:
- Add network imports to `02_Technical/src/`
- Introduce non-deterministic code (`random`, `time.time()`)
- Modify files in `03_Vault/` or `04_Validation/hardcopy/`

### 8. Acceptance

By submitting a pull request, you agree to the terms of this CLA.

---

> **This is a DRAFT.** Must be reviewed by a qualified Australian
> lawyer before use. Template based on standard OSS CLA patterns
> (Apache CLA, GitHub CLA Assistant).