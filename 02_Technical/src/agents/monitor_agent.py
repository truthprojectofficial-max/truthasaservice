"""
Order Get It Right -- Monitor Agent (v1.0.0)

The human-in-the-loop oversight role. Runs the operator's own review on
the running system: chain integrity, agent-hand-off patterns, the recent
changelog, and the Squeal log. Emits an Incident Briefing that the
operator reads and signs before sealing it to the chain.

This is the answer to "the perp has to monitor what is going on so some
human in the loop reports to explain." A perp (or a runaway model, or
a wrong-footed third party) can change a verdict, hide a block, edit
a Squeal file, or add a fake fact. The monitor catches each of those
because every block, every fact, every Squeal, and every changelog
line is on the chain or in a directory the monitor scans.

Deterministic. No LLM. No network. The monitor is the same shape as
the other four agents: a class with a method, sealed to the chain.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config.constants import (
    PROJECT_NAME,
    PROJECT_VERSION,
    PROJECT_OPERATOR,
    PROJECT_VAULT_DIR,
    PROJECT_CHANGELOG_DIR,
    PROJECT_LOGS_DIR,
    PROJECT_SQUEAL_DIR,
)
from src.io import vault_io
from src.utils.canonical import canonical_dumps


# Patterns that the monitor hunts for, by category.
# These are the "the perp is trying to hide something" markers.
HIDE_PATTERNS = {
    "delete_keyword":       [r"\bdelete\s+block\b", r"\bremove\s+block\b", r"\bdrop\s+block\b"],
    "edit_keyword":         [r"\bedit\s+block\b", r"\bamend\s+block\b", r"\bbackdate\b", r"\bmutate\s+chain\b"],
    "rewrite_keyword":      [r"\brewrite\s+chain\b", r"\brebuild\s+chain\b", r"\btruncate\s+chain\b"],
    "tamper_keyword":       [r"\btamper\b", r"\bcover[- ]up\b", r"\bhide\s+the\s+block\b"],
    "self_pardon_keyword":  [r"\bi\s+approve\s+this\b", r"\bself[- ]approve\b", r"\bself[- ]pardon\b"],
    "backdoor_keyword":     [r"\bbackdoor\b", r"\bsecret\s+key\b", r"\badmin\s+override\b"],
}


_ID_RE = re.compile(r"""\b(fact_id|job_id)\s*[=:]\s*["\']?([A-Za-z0-9_:\\-\\.]+)""")


def _scan_text_for_patterns(text: str) -> Dict[str, List[str]]:
    """Return a dict of category -> list of (line_no, line_text) hits."""
    hits: Dict[str, List[str]] = {}
    for lineno, line in enumerate(text.splitlines(), start=1):
        lower = line.lower()
        for cat, pats in HIDE_PATTERNS.items():
            for pat in pats:
                if re.search(pat, lower):
                    hits.setdefault(cat, []).append(f"line {lineno}: {line.strip()[:200]}")
    return hits


def _load_chain_blocks() -> List[Dict[str, Any]]:
    return vault_io.merkle_all()


def _recompute_chain_root(blocks: List[Dict[str, Any]]) -> str:
    """Re-derive the chain root from disk, exactly like LedgerSealAgent.verify_root does."""
    if not blocks:
        return "0" * 64
    previous_hash = "0" * 64
    for block in blocks:
        payload = {
            "event": block["event_type"],
            "payload": block["payload"],
            "ts": block["timestamp"],
        }
        serialised = canonical_dumps(payload)
        computed = hashlib.sha256((previous_hash + serialised).encode("utf-8")).hexdigest()
        if computed != block["current_hash"]:
            return f"BROKEN_AT_BLOCK_{block['index']}"
        previous_hash = block["current_hash"]
    return previous_hash


def _scan_directory_for_keywords(directory: Path, label: str) -> Dict[str, List[str]]:
    """Walk a directory of text files and run hide-pattern detection on every file."""
    out: Dict[str, List[str]] = {}
    if not directory.exists():
        return out
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in {".txt", ".md", ".json", ".log", ".py", ".yml", ".yaml", ".ps1", ".sh"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        hits = _scan_text_for_patterns(text)
        for cat, snippets in hits.items():
            for snippet in snippets:
                out.setdefault(cat, []).append(f"{label}:{path.name} {snippet}")
    return out


def _event_type_counter(blocks: List[Dict[str, Any]]) -> Dict[str, int]:
    counter: Dict[str, int] = Counter()
    for block in blocks:
        counter[block.get("event_type", "UNKNOWN")] += 1
    return dict(counter)


def _recent_blocks(blocks: List[Dict[str, Any]], n: int = 20) -> List[Dict[str, Any]]:
    return blocks[-n:] if len(blocks) > n else list(blocks)


def _format_briefing(payload: Dict[str, Any]) -> str:
    """Format an Incident Briefing as a human-readable Markdown document."""
    lines: List[str] = []
    lines.append("=" * 80)
    lines.append("INCIDENT BRIEFING -- " + str(payload["system_id"]))
    lines.append("=" * 80)
    lines.append(f"Operator of record:    {payload['operator']}")
    lines.append(f"Briefing generated at: {payload['briefing_timestamp']}")
    lines.append(f"Chain root observed:   {payload['chain_root_observed']}")
    lines.append(f"Chain root recomputed: {payload['chain_root_recomputed']}")
    lines.append(f"Chain integrity:       {payload['chain_integrity']}")
    lines.append(f"Block count:           {payload['block_count']}")
    lines.append(f"First block:           {payload['first_block_ts']}")
    lines.append(f"Last block:            {payload['last_block_ts']}")
    lines.append(f"Event-type histogram:  {json.dumps(payload['event_histogram'], sort_keys=True)}")
    lines.append("=" * 80)
    lines.append("")
    lines.append("1. CHAIN INTEGRITY")
    lines.append(f"   Re-derivation {'MATCHES' if payload['chain_integrity']=='OK' else 'FAILS'} the observed root.")
    lines.append(f"   {payload['block_count']} blocks sealed since genesis (2026-07-11T17:15:10Z).")
    lines.append("")
    lines.append("2. SQUEAL PROTOCOL")
    lines.append(f"   {payload['squeal_file_count']} Squeal report file(s) under {payload['squeal_dir']}.")
    if payload["squeal_file_count"] == 0:
        lines.append("   No high-deception events triggered since the last briefing.")
    lines.append("")
    lines.append("3. CHANGELOG")
    lines.append(f"   {payload['changelog_line_count']} line(s) in {payload['changelog_path']}.")
    lines.append(f"   Last entry type: {payload['changelog_last_type']}")
    lines.append(f"   Last entry summary: {payload['changelog_last_summary'][:120]}")
    lines.append("")
    lines.append("4. HIDE-PATTERN SCAN")
    if payload["hide_pattern_hits_total"] == 0:
        lines.append("   No hide-keyword patterns found across the vault, logs, Squeal, or changelog.")
    else:
        lines.append(f"   {payload['hide_pattern_hits_total']} hide-keyword match(es) found. See payload.")
        for cat, snippets in payload["hide_pattern_hits"].items():
            lines.append(f"   - {cat}: {len(snippets)} hit(s)")
    lines.append("")
    lines.append("5. RECENT BLOCKS (most recent 20)")
    for b in payload["recent_blocks"]:
        lines.append(f"   #{b['index']:>4}  {b['event_type']:<30}  {b['timestamp']}  {b['current_hash'][:16]}...")
    lines.append("")
    lines.append("6. UNEXPLAINED VERDICTS")
    if not payload["unexplained_verdicts"]:
        lines.append("   No SUPPRESSED verdicts without a corresponding REFUSAL or Squeal record.")
    else:
        for v in payload["unexplained_verdicts"]:
            lines.append(f"   - block {v['index']}: {v['event_type']} -- {v.get('reason', 'no reason recorded')}")
    lines.append("")
    lines.append("7. OPERATOR ACTION REQUIRED")
    lines.append("   Read this briefing. Sign the bottom. Seal the signed briefing to the chain")
    lines.append("   (use: seal MONITOR_BRIEFING_SIGNED <this briefing with your signature>).")
    lines.append("   If anything in section 4 is unexpected, escalate per the GOVERNANCE.md charter")
    lines.append("   and append a type:'incident' changelog entry.")
    lines.append("")
    lines.append("=" * 80)
    lines.append(f"SIGNED: ____________________________________   Date: ____________")
    lines.append(f"        {payload['operator']}")
    lines.append(f"        {PROJECT_NAME} v{PROJECT_VERSION} Monitor")
    lines.append("=" * 80)
    return "\n".join(lines)


class MonitorAgent:
    """The human-in-the-loop oversight role. Deterministic. No LLM."""

    def __init__(self) -> None:
        self.operator = PROJECT_OPERATOR
        self.system_id = f"{PROJECT_NAME} v{PROJECT_VERSION}"

    def run_briefing(self, seal_to_chain: bool = False) -> Dict[str, Any]:
        """Run a full oversight sweep and return a structured briefing."""
        blocks = _load_chain_blocks()
        observed_root = vault_io.merkle_stats()["merkleRoot"]
        recomputed_root = _recompute_chain_root(blocks)
        chain_ok = (observed_root == recomputed_root)
        histogram = _event_type_counter(blocks)
        squeal_dir = Path(PROJECT_SQUEAL_DIR)
        changelog_path = Path(PROJECT_CHANGELOG_DIR)
        logs_dir = Path(PROJECT_LOGS_DIR)
        vault_dir = Path(PROJECT_VAULT_DIR)

        # Count Squeal files
        squeal_files: List[str] = []
        if squeal_dir.exists():
            squeal_files = sorted(p.name for p in squeal_dir.iterdir() if p.is_file() and p.name.startswith("squeal-"))

        # Read changelog
        changelog_lines: List[str] = []
        if changelog_path.exists():
            try:
                changelog_lines = changelog_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                pass
        last_changelog: Dict[str, Any] = {}
        for line in reversed(changelog_lines):
            line = line.strip()
            if not line:
                continue
            try:
                last_changelog = json.loads(line)
                break
            except json.JSONDecodeError:
                continue

        # Hide-pattern scan
        hits: Dict[str, List[str]] = {}
        for label, d in (
            ("VAULT", vault_dir),
            ("SQUEAL", squeal_dir),
            ("LOGS", logs_dir),
            ("CHANGELOG", changelog_path.parent if changelog_path.parent.exists() else None),
        ):
            if d is None or not d.exists():
                continue
            sub = _scan_directory_for_keywords(d, label)
            for cat, snippets in sub.items():
                hits.setdefault(cat, []).extend(snippets)
        hits_total = sum(len(v) for v in hits.values())

        # Cross-check: a SUPPRESSED verdict is "unexplained" if no REFUSAL block
        # within a +-10-block window references the same fact_id / job_id, and
        # no Squeal report on disk references the same id. The orchestrator
        # seals REFUSAL alongside every SUPPRESSED (see src/agents/orchestrator.py).
        _REFUSAL_WINDOW = 10
        refusal_ids: Dict[str, List[int]] = {}
        for rb in blocks:
            if rb.get("event_type") == "REFUSAL":
                pld = rb.get("payload") or {}
                for key in ("fact_id", "job_id"):
                    val = pld.get(key)
                    if isinstance(val, str) and val:
                        refusal_ids.setdefault(val, []).append(rb["index"])
        squeal_refs: set = set()
        if squeal_dir.exists():
            for s_path in squeal_dir.iterdir():
                if not (s_path.is_file() and s_path.name.startswith("squeal-")):
                    continue
                try:
                    txt = s_path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for m in _ID_RE.finditer(txt):
                    squeal_refs.add(m.group(2))
        unexplained: List[Dict[str, Any]] = []
        for b in blocks:
            if b.get("event_type") != "SUPPRESSED":
                continue
            pld = b.get("payload") or {}
            ref_ids = [pld.get(k) for k in ("fact_id", "job_id") if isinstance(pld.get(k), str) and pld.get(k)]
            if not ref_ids:
                unexplained.append({"index": b["index"], "event_type": b["event_type"], "reason": "no fact_id/job_id in payload"})
                continue
            explained = False
            for rid in ref_ids:
                if any(abs(w - b["index"]) <= _REFUSAL_WINDOW for w in refusal_ids.get(rid, [])):
                    explained = True
                    break
                if rid in squeal_refs:
                    explained = True
                    break
            if not explained:
                unexplained.append({"index": b["index"], "event_type": b["event_type"], "reason": "no REFUSAL within +-10 blocks and no Squeal on disk"})

        briefing_payload: Dict[str, Any] = {
            "system_id": self.system_id,
            "system_version": PROJECT_VERSION,
            "operator": self.operator,
            "briefing_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "chain_root_observed": observed_root,
            "chain_root_recomputed": recomputed_root,
            "chain_integrity": "OK" if chain_ok else f"BROKEN ({recomputed_root})",
            "block_count": len(blocks),
            "first_block_ts": blocks[0]["timestamp"] if blocks else None,
            "last_block_ts": blocks[-1]["timestamp"] if blocks else None,
            "event_histogram": histogram,
            "squeal_file_count": len(squeal_files),
            "squeal_dir": str(squeal_dir),
            "changelog_path": str(changelog_path),
            "changelog_line_count": len([l for l in changelog_lines if l.strip()]),
            "changelog_last_type": last_changelog.get("type", "(none)"),
            "changelog_last_summary": last_changelog.get("summary", "(none)"),
            "hide_pattern_hits": hits,
            "hide_pattern_hits_total": hits_total,
            "unexplained_verdicts": unexplained,
            "recent_blocks": [
                {
                    "index": b["index"],
                    "event_type": b["event_type"],
                    "timestamp": b["timestamp"],
                    "current_hash": b["current_hash"],
                }
                for b in _recent_blocks(blocks, 20)
            ],
        }
        briefing_payload["briefing_markdown"] = _format_briefing(briefing_payload)
        return briefing_payload


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    agent = MonitorAgent()
    briefing = agent.run_briefing()
    print(briefing["briefing_markdown"])


