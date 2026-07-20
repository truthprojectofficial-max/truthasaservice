# PROJECT SPECS & PERFORMANCE — Order Get It Right (v1.0.0)

> Standalone reference: what the project is, how many, per, can-do, best
> purpose, and the measured performance numbers. Operator: Justin Barnett.
> All numbers measured live on the production vault 2026-07-21.

---

## 1. WHAT IT IS

**Order Get It Right (OGIR)** is a *deterministic* business-audit and
valuation engine — "Truth as a Service". It takes any business document
(.txt, .docx, .pdf) and returns a defensible, legally-grounded verdict
**without a black box, without a network call, and without a hosted model**.

Deterministic = same input + same config = same verdict on any host.
Every decision is sealed to a SHA-256 Merkle chain (`03_Vault/`), so the
audit history is **tamper-evident** and re-verifiable offline by any
third party in under 30 seconds.

---

## 2. HOW MANY / PER / CAN-DO (the spec sheet)

### Codebase
| Question | Answer |
|---|---|
| How many source modules? | **45** Python modules under `02_Technical/src/` |
| How many lines of code? | **7,603** LOC (src only) |
| How many agents? | **9** (see below) |
| How many test files? | **23** (`tests/test_*.py`) |
| Python version? | **3.14** (works 3.12+) |
| Platforms? | Windows (Tauri shell) / Python web server / headless CLI |

### The 9 agents
`form_entry` · `evidence_parser` · `affidavit` · `lattice_compute` ·
`audit_review` · `ledger_seal` · `monitor` · `orchestrator` ·
`tau_firewall` (+ `inventory`, `job_delegator` helpers).

### The vault
| Question | Answer |
|---|---|
| How many sealed blocks? | **27,437** (live; grows with use) |
| How big is the vault? | **35.93 MB** total |
| Chain journal | `facts_chain.jsonl`, 0.08 MB |
| Compacted registry | `facts_registry.json`, 13.69 MB |

### Per document — what it does
Ingest -> extract structured evidence -> run **4 gates** -> emit report:

1. **Deception Gate** — 54-pattern ontology v3.9 + Shannon entropy.
2. **BBFB Gate** — LAW (multiplicative veto) + GRACE (quadratic penalty) +
   FRUIT (weighted product).
3. **Optionality Lattice** — two-stage compound binomial lattice ->
   deception-adjusted optionality index (a stylised index, NOT a
   valuation; the orchestrator surfaces `LATTICE_FRAMING` on every
   response).
4. **Decision Gate** — **GO / DEFER / TEST FIRST / REJECT**.

Outputs: Markdown / PDF / DOCX report + a draft Section 56 ACL demand
letter + a draft Section 177 Affidavit.

### Capabilities
| Can it… | Answer |
|---|---|
| run offline? | **Yes** — no LLM, no network, pure Python. |
| be re-verified by a third party? | **Yes** — `python -m src.verify_chain`, offline, <30 s. |
| produce a host-reproducible verdict? | Deterministic verdict/scores/decision; chain is tamper-evident (timestamps differ, so not byte-reproducible). |
| be scheduled to run itself? | **Yes** — Windows Task Scheduler via `scripts\install_scheduler.ps1`. |
| accept third-party/agent calls? | **Yes** — the Onyx CLI (`src.onyx_cli`): audit, seal, verify, affidavit, research, hunt, normalize, compute, compare-to-spec, draft, ledger. |

### Best purpose
Defensible business audit / valuation where **every decision is on a
tamper-evident chain the operator can re-verify offline** — for legal
handoff, compliance, and dispute resolution. Not a hosted SaaS; not an
LLM black box.

---

## 3. PERFORMANCE — the drag strip (measured live)

Production vault: 27,437 blocks / 35.93 MB. Python 3.14 on Windows.
No LLM, no network. Times are wall-clock, single run.

### Launch & throughput (the fast end)
| Segment | Time | Notes |
|---|---:|---|
| Reaction time (module reload of maintenance layer) | **1 ms** | the layer springs to life instantly |
| 60 ft — first block seal (fresh vault) | **5 ms** | + 7 ms to recompute the root after = **12 ms launch** |
| Trap speed — full-chain verify (all 27,437 blocks) | **212 ms** | **129,302 blocks/sec** re-derivation throughput |
| Single block seal into the live journal | ~5 ms | sub-10 ms regardless of chain size |

### Maintenance cadences (the routine passes)
| Pass | Routines | Time | Status |
|---|---:|---:|---|
| **Hourly** | 4 | **306 ms** | PASS (chain_integrity, job_journal_tail, vault_growth, squeal_backlog) |
| **Daily** (the quarter mile) | 7 | **~10.4 s** | PASS |

### Per-routine breakdown (daily, post Options A+B)
```
PASS  chain_integrity       225 ms   chain intact (MATCH)
PASS  job_journal_tail       11 ms   tail=5099 registry=5099 jobs=5099
PASS  vault_growth           64 ms   block count 27437 (delta +0)
PASS  disk_usage              1 ms   vault 35.9 / outbox 20.7 MB
PASS  squeal_backlog          0 ms   0 reports (threshold 50)
PASS  constants_checksum      0 ms   cd918ed8b0b4
PASS  monitor_briefing   10,160 ms   chain OK, 0 hide-pattern hits
                          ----------
                          ~10.4 s   (daily)
```

The only "slow" routine is `monitor_briefing` (~10 s) — a keyword sweep
over the 35 MB vault affidavit. Everything else is sub-quarter-second.

### What changed the numbers (the A/B/C story)
| Option | What | Effect |
|---|---|---|
| **A** (shipped) | Tightened the hide-pattern regexes (`\btamper\b` now excludes "tamper-evident"; descriptive lines skipped). | 28 false hits -> 0. Correctness fix; no speed change. |
| **B** (shipped) | Narrowed the CHANGELOG scan from the whole `04_Validation/` tree to just `changelog.log`. | Daily 16.5 s -> **10.4 s** (~37% faster). |
| **C** (shipped) | Scheduled runner (`scripts\install_scheduler.ps1`) + launcher (`start.py`). | Maintenance runs itself; no LLM, no Ollama timeouts. |

---

## 4. HOW TO START (one line)

```powershell
cd c:\OrderGetItRight
.\start.py
```

Pick a number from the menu, press Enter. That's it. See `START_UP.md`
for the full operator guide and `scripts\install_scheduler.ps1` for the
hands-off scheduled runner.

---

*Deterministic. No LLM. No network. Tamper-evident. Operator: Justin Barnett.*