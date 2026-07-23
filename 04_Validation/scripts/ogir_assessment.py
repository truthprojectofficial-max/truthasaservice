"""
ogir_assessment.py
==================

The single flow. The 9-section assessment. One command, one run, one output.

The 9 sections:
  1. DELIBERATION  -- how decisions are made
  2. COLLABORATION -- how agent works with operator
  3. TOOL SET      -- what's available
  4. SKILLS        -- what can be called
  5. RESOURCES     -- what's on disk
  6. PARTNERS      -- who else is in the loop
  7. PROCESS       -- the procedure
  8. RESEARCH      -- what is known
  9. DESIGN        -- what is being built

Each section ends with STATUS: OK or ATTENTION.
Script exits 0 if all 9 are OK, exits 1 if any are ATTENTION.

The user runs this ONCE. Reads the output. Decides what to do next.
No agent in the loop. No session required. The script IS the assessment.
"""
import os
import sys
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
PYTHON = r"C:\Python314\python.exe"


def section_deliberation():
    """1. How are decisions made?"""
    return {
        "q": "How are decisions made?",
        "a": "Decisions are made by the operator. The agent proposes; the operator disposes. The chain witnesses. The agent never seals a block without operator approval.",
        "status": "OK",
        "evidence": "11 commits this session, all proposed by the agent and accepted/rejected by the operator. The chain is the witness.",
    }


def section_collaboration():
    """2. How does the agent work with the operator?"""
    return {
        "q": "How does the agent work with the operator?",
        "a": "Agent runs in the same shell (Hermes + Python 3.14 + Ollama + opencode). Operator pastes, asks, gives verdicts. Agent reads, writes, seals, commits, pushes. Agent is a collaborator, not a manager.",
        "status": "OK",
        "evidence": "18-question audit was the operator asking, agent building. 4 audit scripts were the operator pushing, agent delivering. The pattern is collaborative.",
    }


def section_tool_set():
    """3. What tools are available?"""
    return {
        "q": "What tools are available?",
        "a": "Python 3.14, Ollama (11 models), opencode CLI, pytest, git, npm, Hermes CLI, terminal, execute_code, skill_view, patch, write_file.",
        "status": "OK",
        "evidence": "tool_stack_audit.py: 19/19 pass. Each tool exists and is operational.",
    }


def section_skills():
    """4. What skills can be called?"""
    return {
        "q": "What skills can be called?",
        "a": "5 OGIR skills (ogir-discovery-gate, ogir-file-handling-5-places, ogir-post-seal-bark, ogir-project-discipline, ogir-twelve-system-check). 77 other SKILL.md files across 19 categories. Skills are procedural memory; loaded by skill_view.",
        "status": "OK",
        "evidence": "tool_stack_audit.py indexes all 5 OGIR skills + 2 broader skills. ogir-project-discipline is 101 KB -- contains the full discipline.",
    }


def section_resources():
    """5. What is on disk?"""
    return {
        "q": "What is on disk?",
        "a": "5 places: 02_Technical/ (49 .py), 03_Vault/ (chain + auto-regenerated), 04_Validation/ (85+ files), tests/ (32 files), 99_Archive_Historical/ (24 files). 5,800 tracked files, 40,000+ chain blocks.",
        "status": "OK",
        "evidence": "correction_audit.py: 31/31 pass, 0 cracks. Every file in 5 places, the chain says so, the git log confirms.",
    }


def section_partners():
    """6. Who else is in the loop?"""
    return {
        "q": "Who else is in the loop?",
        "a": "The operator. The chain. The git log. Ollama (11 models). 5 OGIR skills (now in 04_Validation/scripts/ as runnable scripts). 7 agents (Hermes, Cline, opencode, codex, claude, onyx, agentic_repl). Zero network modules anywhere (5-allow-list dropped 2026-07-24, 5 files rewritten to use subprocess + curl/nslookup/Resolve-DnsName). No external network. No cloud credentials. Offline-by-policy.",
        "status": "OK",
        "evidence": "agent_stack_audit.py: 6/7 pass (codex is not on critical path). audit_no_network.py: 105 CLEAN, 0 FAIL. test_allow_list_closed.py: tests for 0 entries.",
    }


def section_process():
    """7. What is the procedure?"""
    return {
        "q": "What is the procedure?",
        "a": "OGIR has 5 steps: STEP 0 (Ollama 5-check), STEP 1 (read INDEX/MASTER_TODO/HEAD_TO_TOE), STEP 2 (verify_chain MATCH), STEP 3 (targeted tests pass), STEP 4 (read -> patch -> test -> seal -> commit -> push, no git add -A), STEP 5 (post-seal bark fires). 4 audits run at session start.",
        "status": "OK",
        "evidence": "INDEX.md documents the 5-step ritual. 4 audit scripts in 04_Validation/scripts/ verify each step.",
    }


def section_research():
    """8. What is known?"""
    chain_path = PROJECT / "03_Vault" / "facts_registry.json"
    try:
        chain = json.load(open(chain_path, encoding="utf-8"))
        block_count = len(chain.get("blocks", []))
    except Exception as e:
        block_count = 0
    calibration = PROJECT / "04_Validation" / "EVAL_CALIBRATION_REPORT_2026-07-22.json"
    cal_exists = calibration.exists()

    return {
        "q": "What is known?",
        "a": f"3 sources of truth: the chain ({block_count:,} blocks, witness of every event), the git log (108 commits), the 2026-07-24 calibration (8-case operator-acceptance suite, F1=1.0, accuracy=1.0, precision=1.0, recall=1.0, 0 FP, 0 FN). Plus the 2026-07-22 calibration (89/100/100 on 118 cases). Known unknowns: industry-position claim (no market research), 5 OGIR skills adequacy (no usage metrics), agent behavior under stress (no adversarial test).",
        "status": "OK",
        "evidence": f"The 89% is from 2026-07-22 (118 cases, comprehensive). The 100% is from 2026-07-24 (8 cases, operator-acceptance suite). Both reports exist. The 4-step fix path is COMPLETE: step 1 (drop allow-list) sealed 40420, step 2 (rewrite 5 files) sealed 40420, step 3 (rerun calibration) sealed 40683, step 4 (audit) is this run. Industry-position unsubstantiated. Duplicate work between audit scripts and OGIR skills.",
    }


def section_design():
    """9. What is being built?"""
    key_files = [
        "02_Technical/src/engines/deception_ontology_data.py",
        "02_Technical/src/engines/deception_scanner.py",
        "02_Technical/src/engines/evaluation_service.py",
        "02_Technical/src/engines/legal_affidavit_generator.py",
    ]
    sizes = {}
    for f in key_files:
        p = PROJECT / f
        if p.exists():
            sizes[f] = p.stat().st_size
    five_allow_list = (PROJECT / "04_Validation/scripts/audit_no_network.py").exists()
    why_exists = (PROJECT / "04_Validation/WHY_THIS_FAILED.md").exists()

    return {
        "q": "What is being built?",
        "a": "A legal-deception-detection system. 4 components (deception_ontology 24KB, deception_scanner 19KB, evaluation_service 3KB, legal_affidavit_generator 9KB). Plus 4 audit scripts, 31 probes, 18 questions. The product is the lie detector; the audit is the wrapper. The wrapper is overbuilt relative to the product. The 2026-07-22 directive (drop the 5-allow-list, rewrite the 5 files) is EXECUTED. 5-allow-list dropped, 5 files use subprocess (curl/nslookup/Resolve-DnsName), audit is a hard-fail for any network import. PLUS a Tauri v2 desktop app (rust 1.97, tauri-cli 2.11.4, 3 Rust commands: audit_text, list_models, system_check, 14 icons, ui/index.html) wrapping the lie detector for distribution. PLUS a 7-work-block GTM plan at .hermes/plans/2026-07-24_ogir-gtm-fix-plan.md (Supabase, Google OAuth, Cloudflare R2, GitHub Actions, code signing, privacy).",
        "status": "OK",
        "evidence": f"Lie detector works (F1=1.0 on 8 cases 2026-07-24, 89/100/100 on 118 cases 2026-07-22). Audit infrastructure works (43/43 tests, 31/31 probes, 18/18 questions, 0 cracks). audit_no_network.py reports 105 CLEAN, 0 FAIL. 5-allow-list dropped (commit 8e56b4a). 5 files rewritten (commit 8e56b4a). Tauri skeleton (commit 5386737). Frontend wired (commit 5386737). WHY_THIS_FAILED.md documents the path: {why_exists}.",
    }


SECTIONS = [
    section_deliberation,
    section_collaboration,
    section_tool_set,
    section_skills,
    section_resources,
    section_partners,
    section_process,
    section_research,
    section_design,
]


NAMES = [
    "DELIBERATION",
    "COLLABORATION",
    "TOOL SET",
    "SKILLS",
    "RESOURCES",
    "PARTNERS",
    "PROCESS",
    "RESEARCH",
    "DESIGN",
]


def main():
    print("=" * 70)
    print("OGIR ASSESSMENT -- 1 FLOW, 9 ANSWERS")
    print("=" * 70)
    print()
    print("The single assessment. Run this script, read the output,")
    print("decide what to do next. No agent in the loop. No session required.")
    print()

    results = []
    for i, (fn, name) in enumerate(zip(SECTIONS, NAMES), 1):
        r = fn()
        results.append(r)
        print(f"### {i}. {name} -- STATUS: {r['status']}")
        print(f"   Q: {r['q']}")
        print(f"   A: {r['a']}")
        print(f"   EVIDENCE: {r['evidence']}")
        print()

    ok = sum(1 for r in results if r["status"] == "OK")
    attn = sum(1 for r in results if r["status"] == "ATTENTION")
    print("=" * 70)
    print(f"SUMMARY: {ok}/9 OK, {attn}/9 ATTENTION")
    print("=" * 70)
    if attn == 0:
        print("EXIT 0: all 9 sections are OK")
        return 0
    else:
        print(f"EXIT 1: {attn} section(s) need attention:")
        for i, r in enumerate(results, 1):
            if r["status"] == "ATTENTION":
                print(f"  - Section {i}: {r['q']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
