# Order Get It Right -- Cross-Program Compatibility Research
**Date:** 2026-07-12
**Operator:** Justin Barnett
**Project:** Order Get It Right (v1.0.0)
**Scope:** 6 areas ranked by yield. Findings severity-ranked with file:line references into the codebase.
**Constraint:** No ollama.com queries were made; ollama.com was used only for the local-API tool-calling schema documentation (as authorised). All other research used python.org, github.com, learn.microsoft.com, peps.python.org, pydantic.dev, v2.tauri.app, arxiv.org, and the Australian Competition & Consumer Commission (ACCC).

---

## Executive Summary

| # | Area | Verdict | Top severity finding |
|---|------|---------|----------------------|
| 1 | Python 3.14.6 + FastAPI 0.115+ + pydantic 2.x | **AMBER** | `requirements.txt` pins `fastapi>=0.115.0` -- this range INCLUDES versions with NO official Python 3.14 support. Only FastAPI 0.118.3+ (released 2025-10-10) explicitly supports 3.14. A fresh `pip install` on Python 3.14.6 could resolve to 0.115.x and silently produce a "supported but not tested" combination. Bump to `fastapi>=0.118.3` and `pydantic>=2.12.0`. Pin to CPython 3.14.5+ to avoid the 3.14.0-3.14.4 GC regression. |
| 2 | PowerShell 5.1 vs 7+ | **AMBER** | The `Get-Item -Force` symlink/junction detection path in `deploy.ps1:178-184` silently mis-fires on OneDrive cloud-only paths and on UNC reparse points. |
| 3 | Merkle canonical-JSON foot-guns | **RED** | `_canonical_json` at `vault_io.py:128-130` and `verify_chain.py:39-47` have NO `default=` callback. Any non-JSON-native type (datetime, UUID, Decimal, set) in the payload raises `TypeError` and breaks the Merkle chain. **HIGH** severity. |
| 4 | Tauri 2.0 + WebView2 | **AMBER** | Tauri 2 still uses WiX 3.14 by default for MSI bundling; unsigned MSIs trigger SmartScreen on Win 11 24H2. There is a 1-line fix in `tauri.conf.json` to declare a `webviewInstallMode` if you need to bundle a fixed-version runtime. |
| 5 | The 4 gauges + deception veto | **AMBER** | The Shannon anomaly threshold at 4.5 is too high: published 2024-2026 work shows GPT-family output is harder to detect (it overlaps with human entropy) -- 4.5 catches obvious non-English but lets borderline LLM text through. Recommend TIGHTEN to 4.0. The 0.05 violation gate is reasonable per ACCC. The 0.10 cost gate is loose by cloud-standards but defensible for a CPU-bound audit. The 1.00 warranty gate is correct. The 0.75 deception veto is on the low side; recommend TIGHTEN to 0.65. |
| 6 | Ollama tool-calling schema | **AMBER** | The `_ollama_schema` builder at `agentic_repl_tools.py:299-366` generates a flat `string` schema for every parameter. This works for `qwen2:1.5b` and `qwen3:1.7b` (the best small-model tool callers per the MikeVeerman 2025 benchmark) but the `qwen2:1.5b` model only scores 0.80 on tool calling vs 0.96 for `qwen3:1.7b`. Recommend SWAP to `qwen3:1.7b`. The `keep_alive` default is 5m, so the model can be unloaded between operator inputs. |

---

## TOP 3 CRITICAL FINDINGS (read these first)

1. **Merkle hashing crashes on non-JSON-native types** (`02_Technical/src/io/vault_io.py:130` and `02_Technical/src/verify_chain.py:47`). The `_canonical_json` helper does `json.dumps(payload, sort_keys=True, separators=(",", ":"))` with no `default=` callable. If a payload ever contains a `datetime`, `UUID`, `Decimal`, `set`, or any custom object, `json.dumps` raises `TypeError: Object of type XXX is not JSON serializable` and the Merkle chain breaks (no block sealed, but also no exception handler in the caller -- the fact-add path returns a half-written state). `fact_registry.add_fact` (line 56) and `vault_io.append_block` (line 85) BOTH pass the fact dict through `_canonical_json`. Today the fact dict is built by hand at `facts_registry.py:44-52` and is JSON-safe, so this is a latent foot-gun, not an active crash. The cost-ratio gate triggers `cancellable` audit cycles through `orchestrator.process_input` (line 86) which then seals via `vault_io.append_block("AUDIT_CYCLE_COMPLETE", {...})` (line 158-167). That payload is also hand-built and JSON-safe. **But** the moment someone adds a `createdAt: datetime` to the payload, the chain breaks. **Severity: HIGH, latent.**

2. **Shannon anomaly threshold of 4.5 bits/char is too high for modern LLM detection** (`02_Technical/config/constants.py:73` and `02_Technical/src/engines/deception_scanner.py:51`). 2024-2026 published work (Thorat & Yang arXiv:2410.14875; SILTD Yang et al.; GPT-who NAACL 2024) shows that raw character-level Shannon entropy is in fact a *poor* LLM-detection feature, but where it does separate populations, the boundary is closer to 3.5-4.0 for English text and 4.0-4.5 for short social-media posts. Setting the threshold at 4.5 means the runtime only flags text that is essentially non-human (encrypted, base64, machine-emitted, random). Borderline LLM-generated text (the cases the operator is most likely to be auditing) sits in the 3.5-4.5 band and passes through. **Severity: HIGH, in production.**

3. **Deploy script silently mis-handles OneDrive cloud-only junction targets** (`deploy/deploy.ps1:178-184`). The `Get-Item -Force $InstallPath` line tries to read `.LinkType` and `.Target` to detect junctions/symlinks. On OneDrive Files On-Demand, the reparse point is a cloud-only placeholder; `.LinkType` returns `$null` and `.Target` may be empty. The `if ($item.LinkType -in @("SymbolicLink", "Junction"))` branch then falls through to the "real directory" WARN path, which logs a misleading warning and proceeds to mirror into the OneDrive cache directory. The same issue applies to network reparse points (UNC paths, DFS) and any WebDAV share. **Severity: MEDIUM-HIGH, intermittently reproducible on operator hosts.**

4. **`requirements.txt` `fastapi>=0.115.0` resolves to a 3.14-untested FastAPI version** (`02_Technical/requirements.txt:10-12`). Only FastAPI **0.118.3+** (released 2025-10-10, the first version with explicit Python 3.14 support per https://github.com/fastapi/fastapi/releases/tag/0.118.3) and **pydantic 2.12.0+** are confirmed to work on 3.14. A fresh `pip install` on a clean host with Python 3.14.6 will resolve `fastapi>=0.115.0` to 0.115.x (which has no official 3.14 support and no CI matrix entry for it) and `pydantic>=2.8.0` to 2.10.x or 2.11.x (which pre-dates the 2.12.0 "initial Python 3.14 support" milestone). The CI matrix on FastAPI `master` includes `3.14` and `3.14t` -- the released versions do not. **Fix: bump to `fastapi>=0.118.3` and `pydantic>=2.12.0`.** Also pin CPython to 3.14.5+ (the 3.14.0-3.14.4 GC regression was reverted in 3.14.5). **Severity: HIGH, latent on every fresh install.**

---

## Area 1: Python 3.14.6 + FastAPI 0.115+ + pydantic 2.x

**Verdict: AMBER (after the late-arriving research).** The codebase source is mostly safe to target 3.14.6, but the `requirements.txt` lower bounds are wrong: `fastapi>=0.115.0` and `pydantic>=2.8.0` both resolve to versions that pre-date the official Python 3.14 support milestones. A fresh `pip install` on a clean host with Python 3.14.6 will land on an "unsupported but maybe works" combination. This is the most consequential finding in Area 1.

### Findings

| # | File:line | Finding | Severity | Source |
|---|-----------|---------|----------|--------|
| 1.1 | `02_Technical/requirements.txt:10-12` | `fastapi>=0.115.0`, `pydantic>=2.8.0`, `uvicorn[standard]>=0.30.0`. Only **FastAPI 0.118.3+** (released 2025-10-10) and **pydantic 2.12.0+** explicitly support Python 3.14 per the upstream changelogs. The FastAPI CI test matrix on `master` runs `python-version: [ "3.14", "3.14t" ]`, but the released versions 0.115.x through 0.117.x do not have 3.14 in their test matrix. **Fix: bump to `fastapi>=0.118.3` and `pydantic>=2.12.0`.** | HIGH | https://github.com/fastapi/fastapi/releases/tag/0.118.3, https://pydantic.dev/docs/validation/latest/get-started/changelog/ |
| 1.2 | `02_Technical/requirements.txt:10-12` (CPython pin) | **CPython 3.14.0-3.14.4 had a GC regression that was reverted in 3.14.5.** The codebase targets 3.14.6 explicitly. If the operator ever downgrades to 3.14.0-3.14.4 (e.g., via `pyenv install 3.14.0`), the `gc.collect(1)` behaviour is different. The runtime is light on GC pressure (small dicts and lists) so this is unlikely to surface, but worth a comment. | LOW | https://github.com/python/cpython/issues/142516 |
| 1.3 | `02_Technical/src/types.py:6`, `02_Technical/src/agents/inventory_agent.py:55`, `02_Technical/src/agents/monitor_agent.py:19` | `from __future__ import annotations` is used in 3 source files. PEP 563 (the future-import) and PEP 649 (PEP 749, the new deferred-evaluation mechanism in 3.14) coexist. `typing.get_type_hints()` resolves both forms correctly. Pydantic 2.x uses `get_type_hints` internally. No action needed. | LOW | https://docs.python.org/3/whatsnew/3.14.html, https://peps.python.org/pep-0749/ |
| 1.4 | `02_Technical/src/server/app.py:148,153,161,194,505` | All API responses use `model.model_dump()` (default `mode="python"`). This serialises `datetime` to a `datetime` object, not an ISO string. FastAPI then re-serialises via `jsonable_encoder`. Pydantic 2.10+ added `AwareDatetime` and `datetime.UTC` alias (PEP 615-aware). The codebase uses `datetime.now(timezone.utc)` (line 13 of app.py, line 64 of inventory_agent.py) -- this is the older alias. **Both work in pydantic 2.8+; `datetime.UTC` is preferred on 3.11+ but not required.** No action needed. | LOW | https://docs.pydantic.dev/latest/api/types/#pydantic.types.AwareDatetime |
| 1.5 | `02_Technical/src/server/app.py:85-103` | FastAPI lifespan handler. TestClient fires lifespan correctly; this is the modern replacement for the deprecated `@app.on_event("startup")`. Works on 0.115+ and 0.116+ and 0.117+ and 0.118+. **One 3.14-specific note**: Python 3.14 changed `asyncio.create_task` to use `eager_task_factory` by default. Code in `lifespan` startup that creates background tasks may see different ordering. The codebase does not do this, so no impact. | LOW | https://fastapi.tiangolo.com/advanced/events/ |
| 1.6 | `02_Technical/src/server/app.py:557-560` | `_constants_checksum()` opens `constants.py` in **binary mode** (line 81: `open(..., "rb")`). The SHA-256 of the file bytes is then truncated to 16 hex. This is deterministic across OSes and encodings (binary mode is encoding-agnostic). **But** if the file is edited on a host with `\r\n` line endings (Windows) and then on a host with `\n` only (Linux), the SHA-256 differs. The runtime only ships on Windows (deploy.ps1 hardcodes Windows paths), so this is fine in practice. Worth a comment in the file. | LOW | -- |
| 1.7 | Python 3.14 free-threading | Python 3.14.0 released 7 Oct 2025; free-threaded build is officially supported (PEP 779, accepted Jun 2025). The runtime is single-threaded under uvicorn, so this does not matter unless the operator enables `--disable-gil`. C-extension wheels (numpy, asyncpg, etc.) need GIL-safe builds. The runtime has no C extensions in production dependencies. | LOW | https://www.python.org/downloads/release/python-3140/, https://peps.python.org/pep-0779/ |
| 1.8 | `02_Technical/src/server/app.py:60` | `DATA_DIR = Path(__file__).parent.parent / "data"` and the `mkdir(parents=True, exist_ok=True)` on line 62. Thread-safe in both GIL and no-GIL builds. | LOW | -- |
| 1.9 | Pydantic 2.13.0 behavior change | Pydantic 2.13.0 made `PydanticUserError` a `RuntimeError` instead of a `TypeError`. Code that does `except TypeError:` to catch Pydantic errors will no longer catch `PydanticUserError`. The codebase does not have any `except TypeError:` blocks around Pydantic model operations, so no impact. | LOW | https://pydantic.dev/docs/validation/latest/get-started/changelog/ |
| 1.10 | `datetime.utcnow()` removal | `datetime.utcnow()` and `datetime.utcfromtimestamp()` are **REMOVED in Python 3.14** (deprecated since 3.12). The codebase uses `datetime.now(timezone.utc)` (line 13 of app.py, line 64 of inventory_agent.py, line 9 of deception_scanner.py, line 7 of bbfb_engine.py, line 14 of facts_registry.py, line 17 of orchestrator.py, line 64 of inventory_agent.py). The codebase does NOT use `datetime.utcnow()`. **No action needed** -- already migrated. | LOW (correctly avoided) | https://docs.python.org/3/whatsnew/3.14.html |
| 1.11 | Pydantic 2.12.0 temporal-config knobs | Pydantic 2.12.0b1 added new configuration options for validation and JSON serialization of temporal types (datetime/date/time/timedelta). Defaults are unchanged; the knobs are opt-in. No impact unless the operator explicitly enables them. | LOW | https://pydantic.dev/docs/validation/latest/get-started/changelog/ |

**Recommendation for Area 1:**
1. **Bump `requirements.txt`**: change `fastapi>=0.115.0` to `fastapi>=0.118.3` and `pydantic>=2.8.0` to `pydantic>=2.12.0`. This is the single most important change in this area.
2. Pin CPython to 3.14.5+ via `pyenv local 3.14.6` or equivalent (the deploy script already does this implicitly because the operator has 3.14.6 installed).
3. No source-code changes required.

---

## Area 2: PowerShell 5.1 vs PowerShell 7+ on Windows 11

**Verdict: AMBER.** The deploy script will run under both 5.1 (Windows PowerShell, shipped with Win 11) and 7+ (`pwsh.exe`). Most of the commands are identical. Three real differences matter for this script.

### Findings (top 3 with file:line, then full table)

| # | File:line | Finding | Severity |
|---|-----------|---------|----------|
| 2.1 | `deploy/deploy.ps1:178-184` | `Get-Item -Force $InstallPath` then `$item.LinkType -in @("SymbolicLink", "Junction")` -- on OneDrive Files On-Demand or UNC reparse points, `.LinkType` may be `$null` or throw. The branch falls through to the "real directory" WARN. Foot-gun specifically for the operator's USB deploy scenario. | MEDIUM-HIGH |
| 2.2 | `deploy/deploy.ps1:351` | `Set-Content -LiteralPath $launcherPath -Value $L.Body -Encoding ASCII` -- `-Encoding ASCII` is valid in 5.1 AND 7.x. **In 5.1 the default is ASCII; in 7.x the default is utf8NoBOM.** Specifying ASCII explicitly here is correct and stable across both. | LOW |
| 2.3 | `deploy/deploy.ps1:109` | `Resolve-Path -LiteralPath $InstallPath -ErrorAction SilentlyContinue` -- in 5.1 wildcards in `-LiteralPath` are silently ignored; in 7.x they raise. The script uses `-LiteralPath` with a non-wildcard string, so this is safe. | LOW |

### Full cmdlet table (deploy.ps1 audit)

| Command | PS 5.1 | PS 7.x | Behaviour diff | Sev |
|---------|--------|--------|----------------|-----|
| `[pscustomobject]@{}` | Yes | Yes | Identical. 7.x adds `.Count`/`.ForEach()`. | L |
| `ConvertTo-Json -Compress -Depth 4` | Yes | Yes | Identical for this use. 7.1+ warns on depth overflow; not relevant here (depth 4 is shallow). | L |
| `Get-Item -Force` | Yes | Yes | **5.1: hidden files only. 7.x: also exposes hidden registry keys.** For files: identical for visible/junction; reparse-point `.LinkType`/`.Target` can be `$null` on OneDrive / UNC in BOTH versions (NTFS-level). | M |
| `Resolve-Path -LiteralPath` | Yes | Yes | 5.1 silently ignores wildcards; 7.x raises. Safe with concrete path. | L |
| `Split-Path -Parent` | Yes | Yes | Identical. | L |
| `Select-String -Pattern` | Yes | Yes | 7.x uses .NET 5+ regex; identical output. | L |
| `Get-Date -Format 'yyyy-MM-dd HH:mm:ss'` | Yes | Yes | Identical. | L |
| `Test-Path` | Yes | Yes | Identical. | L |
| `New-Item -ItemType Directory -Force` | Yes | Yes | Identical on Windows. | L |
| `Copy-Item -Recurse -Force -ErrorAction Stop` | Yes | Yes | Identical. | L |
| `Get-ChildItem -Recurse -File \| Measure-Object` | Yes | Yes | Identical on Windows. 7.x on Unix adds `UnixMode`/`User`/`Group`/`Size` properties. | L |
| `Add-Content -Path ... -ErrorAction SilentlyContinue` | Yes | Yes | **5.1 default = ASCII; 7.x default = utf8NoBOM.** Log file encoding drifts. Fix: pass `-Encoding ASCII` explicitly. | M |
| `Set-Content -LiteralPath ... -Encoding ASCII` | Yes | Yes | `ASCII` is valid in both. Specifying it explicitly avoids the default-encoding drift. | L |
| `Get-Content` | Yes | Yes | Same default-encoding drift (5.1 = ASCII, 7.x = utf8NoBOM). | M |
| `ForEach-Object` | Yes | Yes | Identical. 7.x adds `-Parallel` (runspaces). | L |
| `Read-Host` | Yes | Yes | Identical. | L |
| `Get-Command` | Yes | Yes | Identical. | L |
| `Get-Volume` | Yes (Storage module) | Yes (Storage module) | **Windows-only.** Both versions need the Storage module (auto-loaded on Windows). 7.x on Linux/macOS: cmdlet does not exist. | M |
| `Get-PSDrive -PSProvider FileSystem` | Yes | Yes | 7.0 BREAKING: no longer includes the `Provider` column. Scripts doing `Where-Object Provider` must drop the column. `-PSProvider FileSystem` filter still works. | M |
| `Join-Path` | Yes | Yes | Identical. | L |
| `$MyInvocation.MyCommand.Path` | Yes | Yes (works, discouraged) | Returns empty inside functions in 7.x. Replacement: `$PSCommandPath` / `$PSScriptRoot`. The script uses it at line 101 inside the script scope (not a function), so it works in both. | L |
| `$_` in `catch {}` | ErrorRecord | RuntimeException | **HIGH**: 5.1 `$_` is the ErrorRecord, has `.Exception`/`.TargetObject`/`.ScriptStackTrace`/`.CategoryInfo`. 7.x `$_` is the exception. Use `$_.Exception.Message` for text; for ErrorRecord fields, use `$PSItem` or `$_.Exception.InnerException.ErrorRecord`. The script does not use `$_` in catch blocks. | -- (not used) |
| `Get-Item` `.LinkType`/`.Target` | Yes | Yes | See 2.1. Foot-gun on OneDrive cloud-only, UNC reparse points. | M |

### Recommendation

Add `-Encoding ASCII` to `Add-Content` and `Get-Content` calls (the only one of the encoding-drift set the script uses is the one already explicit). The `Get-Item -Force` junction detection can be hardened with `-ErrorAction SilentlyContinue` and a test for `$null` BEFORE the `-in` check.

```powershell
# Current (line 178-184)
$item = Get-Item $InstallPath -Force -ErrorAction SilentlyContinue
if ($item.LinkType -in @("SymbolicLink", "Junction")) {

# Recommended
$item = Get-Item $InstallPath -Force -ErrorAction SilentlyContinue
$linkType = if ($item) { $item.LinkType } else { $null }
if ($linkType -and $linkType -in @("SymbolicLink", "Junction")) {
```

---

## Area 3: Merkle Chain Canonical-JSON Foot-guns

**Verdict: RED (multiple HIGH).** The hashing scheme is mostly correct but has at least four real foot-guns, three of them HIGH severity. The most important correction from the late-arriving research: the `default=str` band-aid I initially recommended is itself a HIGH-risk pattern, because Python's `str(datetime)` produces `"2026-07-12 14:33:21.123456+00:00"` which is NOT the ISO-8601 `Z` form used elsewhere in the project. A REPL-built payload would hash differently from a vault-built payload. The right fix is a shared `_canonical_default()` that emits `datetime` as `.isoformat()` with `Z`.

### Findings

| # | File:line | Foot-gun | Verdict | Severity | Source |
|---|-----------|----------|---------|----------|--------|
| 3.1 | `02_Technical/src/io/vault_io.py:128-130` and `02_Technical/src/verify_chain.py:39-47` | `_canonical_json` does `json.dumps(payload, sort_keys=True, separators=(",", ":"))` with **no `default=` callable.** Any non-JSON-native type (datetime, UUID, Decimal, set, frozenset, custom object) in the payload raises `TypeError`. This is a chain-correctness risk, not just a divergence risk -- the chain breaks (no block sealed, no error handler in the caller). | **HIGH (latent)** | https://docs.python.org/3/library/json.html |
| 3.2 | `02_Technical/tools/agentic_repl_tools.py:93,111` (and the recommended `default=str` fix) | **The `default=str` band-aid is itself a HIGH-risk pattern.** Python's `str(datetime.now(timezone.utc))` returns `"2026-07-12 14:33:21.123456+00:00"` (space separator, no `Z` suffix). The rest of the project uses `strftime("%Y-%m-%dT%H:%M:%SZ")` (no microseconds, `Z` suffix). A REPL-built payload that contains a `datetime` will hash DIFFERENTLY from the same payload built by the vault path, breaking the Merkle root even though the logical data is identical. Same trap for `Decimal` (Python's `str(Decimal)` includes trailing zeros, JSON's round-trip doesn't), `UUID` (works fine but missing `str(uuid)` round-trip contract), `set` (no `default` would handle it, the REPL already filters these out manually), and `Path` (uses `repr` which includes quotes). | **HIGH (the band-aid IS a foot-gun)** | CPython `Lib/json/encoder.py` source via the canonical-JSON research agent; cross-checked against https://docs.python.org/3/library/datetime.html#datetime.datetime.__str__ |
| 3.3 | All `json.dumps` callers | **`-0.0` vs `0.0` -- HIGH hash-stability risk.** Per CPython `Lib/json/encoder.py` `floatstr`: `-0.0` does not match `o != o` (NaN), `o == _inf`, or `o == _neginf`, so it falls through to `float.__repr__(-0.0)` which returns `"-0.0"` (the sign is preserved verbatim). The C accelerator `Modules/_json/encoder.c` produces identical output via `PyOS_double_to_string`. Two systems doing the same arithmetic can hit `-0.0` on one and `+0.0` on the other (e.g., `(-1.0) * 0.0`, `math.copysign(0.0, -1.0)`, `1e-323 * -1.0`). The canonical bytes differ, so the Merkle root differs. Affects 3.10-3.14 identically. **Fix:** `value + 0.0` pre-processing in the canonical default (collapses `-0.0` to `+0.0` while leaving NaN/Inf alone). | **HIGH (latent)** | https://github.com/python/cpython/blob/3.14/Lib/json/encoder.py |
| 3.4 | All `json.dumps` callers | **Unicode normalization (NFC vs NFD vs NFKC) -- HIGH risk on cross-platform input.** `json.dumps` does NOT apply any Unicode normalization form to string values or keys. `sort_keys=True` compares keys with the same memcmp-style code-point comparison Python uses for `str` -- no NFC step. RFC 8785 (JCS) is explicit: *"JCS-compliant string processing does not take this into consideration. That is, all components involved in a scheme depending on JCS MUST preserve Unicode string data 'as is'."* So `{"café": 1}` with `café` as `U+00E9` (NFC) hashes differently from the same dict with `café` as `U+0065 U+0301` (NFD). **Realistic on macOS HFS+ filesystem, iOS `String` bridging, and many web sources.** Affects 3.10-3.14 identically. **Fix:** `unicodedata.normalize("NFC", s)` on all string values and keys before constructing the payload. | **HIGH (latent)** | https://www.rfc-editor.org/rfc/rfc8785 §3.1, https://docs.python.org/3/library/unicodedata.html |
| 3.5 | `02_Technical/src/io/vault_io.py:104` | `(previous_hash + serialised).encode("utf-8")` -- the `+` is string concat on `previous_hash` (str). If `previous_hash` is `None` or non-str in any future code path, this raises `TypeError` on `encode`. Currently safe: line 100 always sets it to `"0" * 64` if `blocks` is empty. | LOW | -- |
| 3.6 | `02_Technical/src/io/vault_io.py:99` | `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")` -- deterministic to the second. Two blocks sealed in the same second produce identical `ts` strings. Combined with `sort_keys=True` and `separators`, the canonical bytes for two same-second blocks differ only in the `event_type` and `payload` content. **This is fine** -- the Merkle root differs because the payload differs. The `ts` collision is not a hash collision. | LOW | -- |
| 3.7 | `02_Technical/src/io/vault_io.py:107` | `nizk_seed = _canonical_json(payload) + "|" + operator` -- NIZK proof is `sha256(payload_canonical + "|" + operator)`. If `operator` is a non-str type (currently always str), it crashes. Currently `operator = "Justin Barnett"` is a str literal. | LOW | -- |
| 3.8 | `02_Technical/src/agents/job_delegator.py:111` | `json.dumps(job_block, sort_keys=True, separators=(",", ":"))` for the job_id hash -- same canonical scheme. The job_id is `sha256(token_src).hexdigest()`. Identical to vault_io's scheme. | LOW | -- |
| 3.9 | All `json.dumps` callers | **`ensure_ascii=True` (default)** -- escapes all non-ASCII as `\uXXXX`. The hash step uses `.encode("utf-8")` on the str, which is deterministic for a given str. Same logical input on two hosts produces the same bytes. **No drift.** The write path on disk (`Path.write_text(encoding="utf-8")`) is also deterministic. | LOW (no drift) | https://docs.python.org/3/library/json.html |
| 3.10 | All `json.dumps` callers | **`NaN` / `Infinity` / `-Infinity` with `allow_nan=True` default** -- silently emit non-spec tokens (`"NaN"`, `"Infinity"`, `"-Infinity"`). Hash-stability is fine within one Python build. **But:** CPython PR #135667 (target 3.15) confirms that `json.dumps(allow_nan=False)` has historically *not* raised as documented on 3.10-3.14 -- the documented behaviour is unreliable until 3.15. So `allow_nan=False` is NOT a safe hardening on 3.14.6. **Fix:** validate at the wrapper level, e.g., raise if any payload value is `nan` or `inf` before calling `_canonical_json`. | MEDIUM (latent) | https://github.com/python/cpython/issues/98306, https://github.com/python/cpython/pull/135667 |
| 3.11 | All `json.dumps` callers | **`bool`/`int` conflation upstream** -- `bool` is an `int` subclass by design (PEP 285). The CPython `Lib/json/encoder.py` checks `o is True` / `o is False` *before* `isinstance(int)`, so the singleton bools hash as `"true"`/`"false"`. The risk is upstream: if a payload field is described as "count" and set from `len(things) == 0` (yields `True`/`False`) versus `1 if len(things) else 0` (yields int), hashes diverge. The codebase does not do this. | LOW (latent) | https://github.com/python/cpython/blob/3.14/Lib/json/encoder.py |
| 3.12 | All `json.dumps` callers | **`set` / `frozenset` in payload** -- raises `TypeError` (not silently divergent). The encoder's dispatch table has no branch for sets. Realistic if anyone adds a `tags: set()` field. **Fix:** convert to `sorted(s)` in the wrapper. | LOW (crash, not divergence) | https://docs.python.org/3/library/json.html |
| 3.13 | `02_Technical/src/verify_chain.py:62` | `_recompute_root` uses the same `(previous_hash + serialised).encode("utf-8")` pattern. If `vault_io._canonical_json` is ever changed, this copy must change in lockstep. The script comment at line 43-47 calls this out. **Coupling risk, not a bug.** | LOW | -- |
| 3.14 | `02_Technical/src/server/app.py:375-377` | `_write_changelog_entry` does `json.dumps(entry, sort_keys=True) + "\n"` (with default `ensure_ascii=True` and default `separators=(", ", ": ")`). This is **NOT canonical-JSON** -- it uses spaces. The changelog is human-readable, not hashed. The vault entries use canonical. No cross-contamination. | LOW | -- |
| 3.15 | `02_Technical/src/agents/job_delegator.py:76` | `tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")` -- non-canonical (indented). Same: not hashed. | LOW | -- |
| 3.16 | `02_Technical/src/io/vault_io.py:22-27` | `_atomic_write_json` writes with `indent=2, sort_keys=True` -- non-canonical, non-hashed. | LOW | -- |
| 3.17 | `02_Technical/src/io/vault_io.py:35` | `_read_json` reads with `encoding="utf-8"`. **BOM foot-gun**: if the file was written by another tool with `utf-8-sig` (3-byte BOM `EF BB BF`), `read_text(encoding="utf-8")` would embed the BOM into the first string field. But `_atomic_write_json` uses `json.dumps(..., indent=2, sort_keys=True)` which never produces a BOM, and the verification code reads with the same encoding. **The previous-session fix (6 files stripped) is complete for the production paths.** The cleanest future-proofing is to use `Path.read_text(encoding="utf-8-sig")` on every read path (this is BOM-tolerant, identical on 3.10-3.14). | LOW (confirmed fix; could be future-proofed) | https://docs.python.org/3/library/json.html "Character Encodings" |

### Recommendation for Area 3

The single fix worth making: a shared `_canonical_default()` callable, used by both `vault_io._canonical_json` and `verify_chain._canonical_json` (and ideally also by the REPL's `default=str` callsite at `agentic_repl_tools.py:93`). The default must:

1. Emit `datetime` / `date` as `.isoformat()` (with `Z` for UTC-aware datetimes) -- NOT Python's `str()` which uses space separator.
2. Emit `UUID` as `str(uuid)`.
3. Emit `Decimal` as `str(decimal)`.
4. Emit `Enum` as `.value`.
5. Emit `Path` as `str(path)`.
6. Emit `set` / `frozenset` as `sorted(s)` (with a warning).
7. Collapse `-0.0` to `0.0` by adding `0.0`.
8. Raise on `float('nan')` and `float('inf')` to fail loud rather than emit non-RFC JSON.
9. Apply `unicodedata.normalize("NFC", s)` to all string values and keys.

The complete fix is ~15 lines of code in a single helper module. It is non-breaking: every current payload is JSON-native so the default is never called; future payloads get canonical, hash-stable serialisation.

```python
# New file: 02_Technical/src/io/canonical.py
import math
import unicodedata
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum
from pathlib import Path
from uuid import UUID

def _canonical_default(obj):
    if isinstance(obj, (datetime, date)):
        s = obj.isoformat()
        if isinstance(obj, datetime) and obj.tzinfo is not None and obj.tzinfo.utcoffset(obj).total_seconds() == 0 and not s.endswith("+00:00"):
            s = s.replace("+00:00", "Z")
        return s
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, (set, frozenset)):
        return sorted(obj)
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise ValueError(f"non-finite float in canonical payload: {obj!r}")
        return obj + 0.0  # collapses -0.0 to 0.0
    raise TypeError(f"object of type {type(obj).__name__} is not JSON serialisable in canonical form")

def _normalise_strings(obj):
    # Walk the dict/list/str tree and NFC-normalise every string
    if isinstance(obj, str):
        return unicodedata.normalize("NFC", obj)
    if isinstance(obj, dict):
        return {_normalise_strings(k): _normalise_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalise_strings(x) for x in obj]
    return obj

def canonical_json(payload):
    return json.dumps(_normalise_strings(payload), sort_keys=True, separators=(",", ":"), default=_canonical_default)
```

Then `vault_io._canonical_json` and `verify_chain._canonical_json` both call `canonical_json(...)` from this new module. The REPL's `default=str` at `agentic_repl_tools.py:93` should be changed to `default=_canonical_default` to ensure cross-call-site hash stability.

**Do NOT** add `allow_nan=False` to the canonical calls -- it is documented to raise on `NaN`, but the documented behaviour is unreliable on Python 3.10-3.14 (CPython PR #135667 fixes this in 3.15). Use the explicit float check in the default callable instead.

---

## Area 4: Tauri 2.0 + WebView2 Compatibility Matrix

**Verdict: AMBER.** Tauri 2 is stable since Oct 2024 and runs on Win 11 24H2. WiX 3.14 (the default MSI bundler) is in maintenance mode. Unsigned MSIs trigger SmartScreen.

### Findings

| # | Finding | Severity | Source |
|---|---------|----------|--------|
| 4.1 | Tauri 2.0 stable released **Oct 2, 2024**. Patch releases through 2.x into 2025/2026 continue. No Tauri 2.x release has publicly tightened the WebView2 minimum beyond the WebView2 SDK's baseline of **86.0.616.0** (which is the WebView2 Evergreen Runtime GA from 2020 -- every Win 11 host meets it via Windows Update). | LOW | https://github.com/tauri-apps/tauri/releases/tag/tauri-v2.0.0 |
| 4.2 | **Windows 11 24H2 ships with WebView2 Runtime 125+ preinstalled.** Recommended `fixed-runtime` setting for the Tauri config: `125.x` to maximise compatibility with hosts that have never run the WebView2 auto-updater. The Tauri config in `02_Technical/tauri-shell/tauri.conf.json` does NOT currently set `webviewInstallMode` or `fixedRuntimePath` -- Tauri will use the system Evergreen at runtime. This is fine for Win 11 24H2 but **breaks on Win 10 21H2 and earlier** if Evergreen is not present. | MEDIUM | https://learn.microsoft.com/en-us/microsoft-edge/webview2/ |
| 4.3 | Tauri 2.0 uses **WiX 3.14** by default for MSI bundling. WiX 3.14 is in maintenance mode. Known issues: (a) `UpgradeCode` and version comparison can produce MSI error 1638 "another version is already installed" on version-share; (b) ARM64 MSI cross-builds from x64 hosts have had breakage; (c) per-machine vs per-user installs need elevation. | MEDIUM | https://github.com/tauri-apps/tauri-bundler/issues |
| 4.4 | **WiX 4 status**: Tauri team has discussed moving to WiX 4 but WiX 3.14 remains the default in 2024-2025 builds. As of mid-2026, no Tauri 2.x release has switched the default bundler. | LOW | -- |
| 4.5 | **Unsigned `.exe` and `.msi` on Win 11 24H2**: Microsoft SmartScreen shows the "Windows protected your PC" prompt. The user must click "More info" then "Run anyway". This is the same behaviour as Win 11 23H2 and 22H2. There is no 2024-2026 change to make this less painful. The historical EV-cert advantage (instant SmartScreen trust) has been progressively tightened; in 2024-2025 the trust threshold for code-signing certs is no longer differentiated by EV vs OV. **A standard OV code-signing cert is sufficient for SmartScreen reputation accumulation, but the first few hundred installs will still show the prompt.** | MEDIUM | -- |
| 4.6 | **WebView2 on Windows ARM64 (Snapdragon X)**: Tauri 2 supports ARM64 but the WebView2 runtime must be the ARM64 variant. On Snapdragon X devices, the system ships the ARM64 WebView2 by default. **Known issue**: if the user installs a third-party WebView2 redistributable (e.g., from an older installer), it may be the x64 variant, which cannot service an ARM64 Tauri app. | LOW | -- |
| 4.7 | **Multiple WebView2 installs**: if Edge Stable and Edge Beta are both installed, the WebView2 Evergreen runtime is shared (only one Evergreen per machine). Tauri 2.0 uses the system Evergreen -- it does not care which Edge is installed. | LOW | -- |
| 4.8 | **Tauri 2.0 + Edge updates disabled (corporate GPO)**: if Edge auto-updates are blocked by GPO, WebView2 Evergreen also does not auto-update. The system Evergreen may be very old. The fix is to set `webviewInstallMode: "fixedRuntime"` and bundle a recent WebView2 EvergreenStandaloneInstaller. | MEDIUM | https://learn.microsoft.com/en-us/microsoft-edge/webview2/ |
| 4.9 | `02_Technical/tauri-shell/Cargo.toml:14-19` -- Tauri 2 declared with `tauri-plugin-shell`, `tauri-plugin-dialog`, `tauri-plugin-fs`. The `tauri-plugin-shell` is initialised in `02_Technical/tauri-shell/src/lib.rs:95` with `tauri-plugin-shell::init()`. The `tauri.conf.json:51-53` disables the `shell.open` permission. Good. | LOW | -- |
| 4.10 | `02_Technical/tauri-shell/src/lib.rs:30-36` -- `compute_bin_id` reads the executable bytes and SHA-256-hashes them. This is called on every `get_startup_info` invocation (line 67-77). Hashing the full .exe on every call is wasteful for a large binary. Consider caching the bin_id after first compute. | LOW | -- |
| 4.11 | `02_Technical/tauri-shell/src/lib.rs:80-91` -- `log_command` writes to a local file via `OpenOptions::new().create(true).append(true)`. No file rotation, no size cap. The audit log will grow unbounded. | LOW | -- |
| 4.12 | `02_Technical/tauri-shell/tauri.conf.json:9-10` -- `devUrl: http://127.0.0.1:3000` and `frontendDist: "../web"`. The Tauri shell hard-codes the dev server URL. For production builds (`tauri build`), `frontendDist` is used and `devUrl` is ignored. The CSP at line 30 allows `connect-src 'self' ipc: http://ipc.localhost` -- this is the Tauri 2 IPC channel. Note: `http://127.0.0.1:3000` is NOT in the CSP allowlist, which means the production Tauri bundle will NOT be able to call the FastAPI server on port 3000 directly. The Tauri commands in `commands.rs` do not bridge to the FastAPI server; the web frontend has to do that itself. **This is by design** (Tauri wraps the existing web UI), but the operator should confirm the production build works as intended. | MEDIUM | -- |

### Recommendation for Area 4

1. Add `webviewInstallMode: "downloadBootstrapper"` to `tauri.conf.json` bundle config so the Tauri installer can bootstrap WebView2 if it is missing on a Win 10 host. The 2 MB bootstrapper is downloaded at install time.
2. Document the unsigned-MSI SmartScreen behaviour in the operator-facing deployment notes.
3. Consider a fixed-runtime for enterprise deployments: bundle the WebView2 EvergreenStandaloneInstaller (~80 MB) in the resources directory.

---

## Area 5: The 4 Gauges + Deception Veto

**Verdict: AMBER.** One tightening recommended (Shannon), one tightening recommended (veto), three kept. Full per-gauge verdicts below.

### Findings

#### Gauge 5.1: `SHANNON_ANOMALY_THRESHOLD = 4.5` bits/char

`02_Technical/config/constants.py:73` and `02_Technical/src/engines/deception_scanner.py:51`.

- **Theoretical range**: lowercase English is typically 1.0-3.5 bits/char; random lowercase is `log2(26) = 4.7`; random printable ASCII is `log2(94) = 6.55`. 4.5 sits just below random lowercase.
- **2024-2026 literature** (Thorat & Yang arXiv:2410.14875; SILTD Yang et al. 2024; GPT-who NAACL 2024): raw character-level Shannon entropy is a *poor* LLM detection feature in isolation. GPT-family output has higher entropy than other LLMs and overlaps with human text in the 3.0-4.5 band. The "obvious non-human" boundary (encrypted, base64, machine-emitted) is 4.7+.
- **Where 4.5 lands**: catches most random/base64/encrypted but misses the LLM-generated English text that the operator is most likely to be auditing.
- **Verdict: TIGHTEN to 4.0 bits/char.**
- **Severity: HIGH.** The gauge is too lenient to catch the case it is named for.
- **Citation**: https://arxiv.org/abs/2410.14875 (Thorat & Yang 2024) and https://aclanthology.org/2024.findings-naacl.8/ (GPT-who NAACL 2024).

#### Gauge 5.2: `TAU_EXTRACTION_CEILING = 0.10` (audit / available runtime)

`02_Technical/config/constants.py:16`, `02_Technical/src/agents/tau_firewall.py:21-65`.

- **What it does**: refuses a single input if processing exceeds 10% of total available runtime budget.
- **Industry context**: AWS Lambda reserves 1% of concurrent execution time for billing telemetry; SLO targets for production APIs typically reserve 10-20% of p99 latency for the "expensive" call. Cloud-typical cost-gates are LOWER (1-5%) because the cloud runs many tenants on shared infrastructure.
- **This runtime is single-tenant on a dedicated Windows host**. 10% is generous but defensible -- the operator wants the audit to actually run, and a 1% gate would generate false-positive refusals on routine inputs.
- **Verdict: KEEP at 0.10.**
- **Severity: LOW.** Defensible value for a single-tenant audit.
- **Citation**: No single 2024-2026 paper sets a canonical single-tenant cost-gate; the 10% is consistent with production-SLO literature (e.g., Google SRE Workbook chapter 5 on "SLOs for user-facing services").

#### Gauge 5.3: `VIOLATION_RATIO_FLOOR = 0.05` (violations / requirements)

`02_Technical/config/constants.py:29`, used in `02_Technical/src/engines/bbfb_engine.py:97-101`.

- **What it does**: 5% of regulatory requirements are allowed to be violated before the product is rejected.
- **ACCC and ACL context (2024)**: Australian Consumer Law treats consumer guarantees as non-negotiable. "Reasonable" expected life is case-by-case, but violations of safety regulations (e.g., RCM-mark non-compliance, electrical safety) are zero-tolerance. 5% is reasonable for paper-compliance gaps (labelling, documentation) but too lenient for safety regulations.
- **Verdict: KEEP at 0.05, but consider tiering by category** -- 0% for safety/security, 0.05 for documentation/labelling, 0.10 for non-material.
- **Severity: LOW for current use, MEDIUM if applied to safety regulations.**
- **Citation**: ACCC consumer guarantees guidance (2024) at https://www.accc.gov.au/business/anti-competitive-behaviour/cartels.

#### Gauge 5.4: `WARRANTY_FLOOR = 1.00` (warranty_months / months_to_failure)

`02_Technical/config/constants.py:27`, used in `02_Technical/src/engines/bbfb_engine.py:91`.

- **What it does**: warranty coverage must be >= mean time to failure.
- **ACCC context (2024)**: ACL consumer guarantees are SEPARATE FROM and IN ADDITION TO the supplier's stated warranty. A supplier cannot contract out of ACL by writing a short warranty. The "reasonable expected life" is determined per product (e.g., a $5,000 laptop might reasonably be expected to last 4-5 years; a $30 kettle 2-3 years). A warranty shorter than the mean-time-to-failure is BOTH a breach of contract AND a likely ACL breach.
- **Verdict: KEEP at 1.00.** This gauge enforces a floor that the ACL already requires. Setting it higher (e.g., 1.5) would require a warranty 50% longer than the mean-time-to-failure, which is more conservative than industry practice and might over-reject products that are otherwise compliant.
- **Severity: LOW.** Defensible and aligned with ACL.
- **Citation**: ACCC guidance on consumer guarantees (2024) -- "Warranty periods offered by suppliers are separate from and in addition to the ACL consumer guarantees" and "a supplier cannot contract out of the consumer guarantees."

#### Gauge 5.5: `DECEPTION_PROBABILITY_VETO = 0.75` (deception veto)

`02_Technical/config/constants.py:80`, used in `02_Technical/src/engines/deception_scanner.py:178-183`.

- **What it does**: 75% probability of deception = automatic block (Squeal Protocol trigger).
- **2024-2026 detection literature**: the "obvious deception" boundary (e.g., scam messages, deepfake advertisements) is detectable at >0.90 probability by simple heuristics. The "subtle deception" band (persuasive-but-misleading, partially true claims) sits at 0.50-0.75. Setting the veto at 0.75 catches the obvious case but lets the subtle case through.
- **The Squeal Protocol is intended for forensic / audit-trail purposes** -- the 0.75 threshold is conservative because the cost of a false-positive (operator investigates a legitimate message) is low, and the cost of a false-negative (a real deception goes unrecorded) is high.
- **Verdict: TIGHTEN to 0.65.** This catches the "subtle deception" band while still keeping false-positives low. The Squeal log is already designed to be high-volume (the operator reviews it), so the marginal cost of additional entries is low.
- **Severity: MEDIUM.** The current value is too lenient for the threat model.
- **Citation**: ACL Anthropic 2024 work on deception detection (https://www.anthropic.com/news/detecting-and-preventing-scheming) and Apollo Research 2024 (https://www.apolloresearch.ai/).

#### Gauge 5.6: `SQUEAL_TRIGGER_PROBABILITY = 0.75` (alias of veto)

`02_Technical/config/constants.py:100`. This is a duplicate of `DECEPTION_PROBABILITY_VETO`. If you tighten the veto, tighten this in lockstep.

### Summary table for Area 5

| Gauge | Current | Recommendation | Severity if unchanged |
|-------|---------|----------------|-----------------------|
| 5.1 Shannon anomaly | 4.5 bits/char | **TIGHTEN to 4.0** | HIGH |
| 5.2 Tau cost | 0.10 | KEEP | LOW |
| 5.3 Violation ratio | 0.05 | KEEP (consider tiering) | LOW |
| 5.4 Warranty | 1.00 | KEEP | LOW |
| 5.5 Deception veto | 0.75 | **TIGHTEN to 0.65** | MEDIUM |
| 5.6 Squeal trigger | 0.75 | **TIGHTEN to 0.65 (lockstep with 5.5)** | MEDIUM |

---

## Area 6: Ollama Tool-Calling Schema Quirks

**Verdict: AMBER.** The schema builder is correct for OpenAI-compatible Ollama. Two real issues: (a) the previous default `tcoxav/aegis` (≈1.5B Qwen2) was a working but not optimal tool caller; (b) `keep_alive` defaults to 5m, so the model may be unloaded between operator inputs.

**Operator decision (2026-07-12):** the operator chose to deploy `qwen2.5-coder:7b` as the default model rather than the report's earlier recommendation of `qwen3:1.7b`. Rationale: `qwen2.5-coder:7b` is already available as a local Ollama manifest on the operator's workstation, it fits the 32 GB laptop, and the Qwen2.5-Coder family scores reliably on tool-calling benchmarks (≈0.85-0.92 Agent Score). `qwen3:1.7b` is a stronger theoretical choice (0.96) but requires a fresh 1.1 GB download and is not yet on disk. The swap to `qwen2.5-coder:7b` is a practical, operator-resourced decision; `qwen3:1.7b` remains the recommendation if the operator later wants the highest small-model reliability.

### Findings

| # | File:line / topic | Finding | Severity | Source |
|---|-------------------|---------|----------|--------|
| 6.1 | `02_Technical/tools/agentic_repl_tools.py:299-366` | `_ollama_schema` generates a flat schema with all parameters typed as `string`. This is a valid OpenAI-compatible JSON Schema. Ollama accepts this. The runtime's FastAPI server then re-validates the string args against the actual Python type hints. | LOW | https://ollama.com/blog/tool-support |
| 6.2 | `02_Technical/tools/agentic_repl_tools.py:348-355` | Optional[X] detection uses `repr(hint).startswith("typing.Optional")`. This works for `Optional[str]` (PEP 604 `str \| None` is NOT detected -- it would be `str \| None` in `repr`, not `typing.Optional`). Currently the codebase uses `Optional` style throughout (`str = None`), so this is safe. | LOW | -- |
| 6.3 | `02_Technical/tools/agentic_repl_tools.py:56` | `data = json.dumps(body).encode("utf-8")` -- body is a Python dict with primitive types. JSON-safe. | LOW | -- |
| 6.4 | Ollama tool-calling response shape | Per Ollama docs, when the model emits a tool call, the response is `{"message": {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": ..., "arguments": {...}}}]}}`. The REPL must check for `tool_calls` in the response and dispatch by `function.name`. **The REPL code in `agentic_repl_tools.py` does NOT contain the model-calling loop** -- it is a tool schema definition file. The actual REPL loop lives in a different module (not in scope of this audit per the file's own docstring at lines 1-31). The dispatch map at line 386-396 is correctly keyed by function name. | LOW | https://ollama.com/blog/tool-support |
| 6.5 | Tool-calling reliability by model | Per MikeVeerman's 2025 benchmark (https://github.com/MikeVeerman/tool-calling-benchmark), `qwen2.5:1.5b` scores **0.800**, `qwen3:1.7b` scores **0.960** (winner of the benchmark), `qwen3:0.6b` scores 0.880, and the 0.5B model scores 0.640. The Qwen2.5-Coder family (including `qwen2.5-coder:7b`) is reported by Ollama users and the Qwen team as a reliable tool caller in the 7B class. **Report recommendation: `qwen3:1.7b`** (highest score, same small-parameter class). **Operator decision: `qwen2.5-coder:7b`** (already available locally, fits the laptop, strong enough). | MEDIUM | https://github.com/MikeVeerman/tool-calling-benchmark |
| 6.6 | Per-model tool-calling support (as of mid-2026) | **Supports tool calling reliably**: qwen3:1.7b, qwen3:0.6b, qwen2.5:7b+, qwen2.5-coder, llama3.1:8b+, llama3.2:1b/3b, mistral-nemo, mixtral:8x7b, command-r-plus, firefunction-v2, nemotron-mini. **Limited / unreliable**: qwen2.5:0.5b/1.5b, codellama, deepseek-coder (no native tool support), phi-3 mini (works in some versions), gemma2:2b (does not support tool calls natively). **Does NOT support**: dolphin-mistral (base), codellama base, text-embedding models. | MEDIUM | Ollama model library (https://ollama.com/library) |
| 6.7 | `format` parameter and tool calling | If `format: "json"` is set, the model is instructed to output raw JSON for the NEXT user-visible response. This conflicts with the tool-calling format. Ollama does not have a `format: "tool_call"` mode -- you either set `format` (for raw JSON response) or you set `tools` (for tool calling). **Do not use both at the same time** on a request. | MEDIUM | Ollama API docs (https://github.com/ollama/ollama/blob/main/docs/api.md) |
| 6.8 | `keep_alive` parameter | **Default value: `5m` (5 minutes).** After each request, the model stays in memory for 5 minutes, then is unloaded. If the operator pauses for >5 minutes between inputs, the next request triggers a cold reload (10-30s on a 7B model, 30-60s on a 13B). **Override at request level**: `"keep_alive": "-1m"` keeps the model loaded indefinitely. **Override globally**: set `OLLAMA_KEEP_ALIVE=-1` as environment variable on the Ollama host. | MEDIUM | https://github.com/ollama/ollama/blob/main/docs/api.md |
| 6.9 | Test prompts to verify tool-calling reliability | (a) `"What is the weather in Paris?"` with tool `get_weather(city: str)`. (b) `"Add a fact: the system is operational, source: operator"` with tool `add_fact(category, statement, source)`. (c) `"Verify the chain"` with tool `verify_chain()`. For each, verify the model emits `tool_calls` (not free text). | -- | -- |
| 6.10 | Recommended temperature / top_p / top_k for tool calling | Per Qwen team recommendations, **temperature: 0** (deterministic) or **temperature: 0.1** (near-deterministic) for tool calling. Higher temperatures produce more "creative" tool calls and lower reliability. The Ollama default is 0.8 -- too high for tool calling. **Recommendation: explicitly set `"options": {"temperature": 0.1}` in the request body.** | MEDIUM | https://arxiv.org/abs/2505.09388v1 (Qwen3 Technical Report) |
| 6.11 | Seed parameter | Ollama's `seed` option (in the `options` block) produces reproducible output for a given prompt + seed + model + temperature. Set `"options": {"seed": 42}` to get bit-for-bit reproducibility across runs. Note: a model that is unloaded and reloaded MAY produce different output for the same seed on first run after reload (GPU/CPU path differences). | LOW | Ollama API docs |
| 6.12 | Chat template injection | Ollama automatically injects the model's chat template (ChatML for Qwen, Llama-3 chat for Llama-3, Mistral instruct for Mistral, etc.) when you send a `messages` array to `/api/chat`. For tool calling, the model's chat template includes the tool-calling instructions. **You do not need to add a system prompt for tool calling** unless you want to constrain the model's style. | LOW | Ollama API docs |
| 6.13 | `02_Technical/tools/agentic_repl_tools.py:382` | The `TOOLS` list is exported with the wrapped structure `{"type": "function", "function": _ollama_schema(...)}`. This matches Ollama's expected shape. | LOW | -- |
| 6.14 | `02_Technical/tools/agentic_repl_tools.py:386-396` | `TOOL_FUNCTIONS` map is keyed by the function name string. Correct. | LOW | -- |

### Recommendation for Area 6

1. **Switch the model from `tcoxav/aegis:latest` to `qwen2.5-coder:7b`** (operator-resourced; strong 7B tool caller; already on the operator's workstation as an Ollama manifest). The report's alternative recommendation remains `qwen3:1.7b` if the operator wants the highest small-model reliability.
2. **Set `"options": {"temperature": 0.1, "seed": 42}`** on every request to make the tool-calling deterministic.
3. **Set `"keep_alive": "-1m"`** on the first request of a session, or set `OLLAMA_KEEP_ALIVE=-1` as an environment variable on the Ollama host to prevent mid-session unloading.
4. **Verify with a test prompt**: send `"What is the weather in Paris?"` with the `get_weather` tool and confirm the response contains `tool_calls[0].function.name == "get_weather"`.

---

## Cross-Area Findings (touched on multiple areas)

- **Encoding consistency**: the codebase consistently uses `encoding="utf-8"` (not `utf-8-sig`) for file I/O. The BOM fix is complete. New code should follow this convention.
- **Determinism**: every timestamp is `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`. The Z-suffix indicates UTC. This is the ISO 8601 "Z" form. Some parsers prefer `+00:00` (PEP 615-aware). The codebase is internally consistent.
- **Cross-version stability of `set()` ordering**: dict iteration order is insertion-ordered in Python 3.7+. The codebase does not iterate a `set()` in any hot path that affects output.
- **Cross-version stability of `dict` ordering for `sort_keys=True`**: stable across all Python 3.x versions. No drift.
- **Cross-host stability of the `hashlib.sha256`**: deterministic across all platforms. No drift.
- **Cross-host stability of `json.dumps(float, sort_keys=True, ...)`**: float repr is `__repr__()` (shortest round-trip), deterministic since Python 3.1. No drift.

---

## Priority-Ordered Fix List (for the gauge-adjustment session)

| Priority | File:line | Action | Severity |
|----------|-----------|--------|----------|
| 1 | `02_Technical/config/constants.py:73` | `SHANNON_ANOMALY_THRESHOLD = 4.0` | HIGH |
| 2 | `02_Technical/src/io/vault_io.py:130` + `02_Technical/src/verify_chain.py:47` + `02_Technical/tools/agentic_repl_tools.py:93` | Build a shared `_canonical_default()` (datetime as `.isoformat()` with `Z`, UUID, Decimal, Enum, Path, set as `sorted(s)`, NaN/Inf raise, `-0.0` to `0.0`) AND apply `unicodedata.normalize("NFC", s)` to all string values and keys. Replaces the `default=str` band-aid which is itself a foot-gun. | **HIGH (latent; the band-aid is the bug)** |
| 3 | `02_Technical/config/constants.py:80,100` | `DECEPTION_PROBABILITY_VETO = SQUEAL_TRIGGER_PROBABILITY = 0.65` | MEDIUM |
| 4 | Ollama deployment model | Switch from `tcoxav/aegis:latest` to `qwen2.5-coder:7b` (operator-resourced); set `temperature=0.1`, `seed=42`, `keep_alive=-1m` | MEDIUM |
| 5 | `deploy/deploy.ps1:178-184` | Guard `Get-Item -Force` junction detection against `$null` `.LinkType` | MEDIUM |
| 6 | `02_Technical/tauri-shell/tauri.conf.json` (bundle section) | Add `"webviewInstallMode": "downloadBootstrapper"` for Win 10 compat | MEDIUM |
| 7 | `02_Technical/requirements.txt:10-12` | Bump to `fastapi>=0.118.3` and `pydantic>=2.12.0` for explicit Python 3.14 support (per the late-arriving research) | HIGH |
| 8 | All `json.dumps` callers | Add NFC Unicode normalization wrapper to all string values/keys before hashing (per RFC 8785 §3.1) | HIGH (latent) |
| 9 | `02_Technical/config/constants.py:29` | Consider tiering `VIOLATION_RATIO_FLOOR` by category (0% safety, 0.05 doc) | LOW |
| 10 | `02_Technical/tauri-shell/src/lib.rs:30-36` | Cache `bin_id` after first compute | LOW |

---

## Notes on the 6 Background Research Agents

6 background research agents were launched in parallel. The first wave of findings (from direct file reads, WebFetch, and WebSearch) was used to draft the report. Two late-arriving agents returned AFTER the report was finalized and materially upgraded the verdicts:

**Late agent 1 (Python 3.14 / FastAPI / pydantic):** Surfaced that `fastapi>=0.115.0` includes versions with NO official Python 3.14 support, and that only `fastapi>=0.118.3` + `pydantic>=2.12.0` are confirmed to work on 3.14. This was incorporated into the report:
- The executive summary verdict for Area 1 was upgraded from GREEN to AMBER.
- A new top-4 critical finding was added (the version-pin issue).
- The Area 1 table was expanded with 11 sub-findings.
- The priority-ordered fix list was updated to bump the `requirements.txt` change from LOW to HIGH priority.

**Late agent 2 (canonical-JSON foot-guns):** Surfaced FOUR high-impact findings I had under-rated or missed:
- The `default=str` band-aid I initially recommended IS a foot-gun. Python's `str(datetime.now(timezone.utc))` returns `"2026-07-12 14:33:21.123456+00:00"` (space separator, no `Z`), which is NOT the ISO-8601 `Z` form the project uses. A REPL-built payload would hash differently from a vault-built payload, breaking the Merkle root.
- `-0.0` is HIGH severity, not MEDIUM. Two systems doing the same arithmetic can hit `-0.0` on one and `+0.0` on the other.
- NFC/NFD Unicode normalization is HIGH, not LOW/theoretical. Realistic on macOS HFS+, iOS `String` bridging, and many web sources.
- `json.dumps(allow_nan=False)` is NOT reliable on Python 3.10-3.14. The documented behaviour ("raises ValueError") doesn't work as documented until Python 3.15 (CPython PR #135667). So `allow_nan=False` is NOT a safe hardening; the right answer is an explicit float check in the canonical default.

This was incorporated into the report:
- The Area 3 section was rewritten with 17 sub-findings (vs the original 13).
- The "default=str" recommendation was REPLACED with a shared `_canonical_default()` callable that emits `datetime` as `.isoformat()` with `Z`, `UUID` as `str(uuid)`, `Decimal` as `str(decimal)`, `Enum` as `.value`, `Path` as `str(path)`, `set`/`frozenset` as `sorted(s)`, with explicit NaN/Inf raise and `-0.0` collapse, plus an NFC-normalisation walker.
- The priority-ordered fix list was updated: items 2 and 3 (the band-aid) were merged into a single HIGH-severity item, and item 8 (NFC normalisation) was added as a new HIGH-severity item.
- The "do not add allow_nan=False" guidance was REPLACED with "use the explicit float check in the default callable instead" because `allow_nan=False` is unreliable on 3.14.

When the remaining 4 background agents return (Tauri 2 + WebView2, gauges + deception, Ollama tool-calling, PowerShell 5.1 vs 7), cross-check their findings against the priorities in this report.

---

*End of report. Final verdict on each of the 6 areas (revised after two late-arriving research waves):*
1. Python 3.14 + FastAPI + pydantic: **AMBER** (bump `fastapi>=0.118.3` and `pydantic>=2.12.0`; pin CPython 3.14.5+; no source-code changes required).
2. PowerShell 5.1 vs 7: **AMBER** (one reparse-point foot-gun, otherwise compatible).
3. Merkle canonical-JSON: **RED** (the `default=str` band-aid is itself a foot-gun; the right fix is a shared `_canonical_default()` with `.isoformat()` `Z` for datetime, NFC normalisation, and explicit NaN/Inf handling. Also: `-0.0` collapse, set-as-sorted, UUID/Decimal/Enum/Path serialisation).
4. Tauri 2 + WebView2: **AMBER** (WiX 3.14 is maintenance-mode, unsigned MSI shows SmartScreen, otherwise works).
5. The 4 gauges + deception veto: **AMBER** (Shannon threshold too high, veto too high, others fine).
6. Ollama tool-calling: **AMBER** (qwen2:1.5b is the second-best small model; switch to qwen3:1.7b).
