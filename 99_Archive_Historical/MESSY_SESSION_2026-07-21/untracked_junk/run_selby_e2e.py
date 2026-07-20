"""
End-to-end real-case driver: Barnett v Selby Acoustics (SELBY-001).

Runs the real intake through every gate of the deterministic engine
and the legal generators, and seals the verdict to the Merkle chain.

This is a real-evidence validation run, not a unit test.
"""
import json
import os
os.environ.setdefault("PYTHONHASHSEED", "0")

from datetime import datetime, timezone

from src.types import ProductEvidence
from src.engines.deception_scanner import audit_text
from src.engines.bbfb_engine import calculate_bbfb, spec_value_curve
from src.engines.real_options_lattice import (
    hardened_compound_binomial_gate,
    derive_lattice_inputs_from_evidence,
)
from src.engines.acl_demand_generator import generate_acl_demand
from src.engines.legal_affidavit_generator import LegalAffidavitGenerator
from src.engines import facts_registry
from src.io import vault_io
from config.constants import (
    PROJECT_VAULT_DIR,
    SPEC_VALUE_VETO_FLOOR,
    GRACE_CRITICAL_THRESHOLD,
    CVS_THRESHOLD,
    DECEPTION_PROBABILITY_VETO,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTAKE = os.path.join(ROOT, "data", "inbox", "SELBY_001_major_failure_intake.txt")
LEDGER = os.path.join(PROJECT_VAULT_DIR, "facts_registry.json")
HR = "=" * 78


def banner(title):
    print("\n" + HR)
    print(title)
    print(HR)


banner("0. REAL INTAKE -- Barnett v Selby Acoustics (SELBY-001)")
text = open(INTAKE, "r", encoding="utf-8").read()
print(f"Source file : {INTAKE}")
print(f"Length      : {len(text)} chars")
print(f"First line  : {text.splitlines()[0]}")

banner("1. DECEPTION GATE -- 54-pattern ontology v3.10 + Shannon entropy")
deception = audit_text(text)
print(f"Shannon entropy          : {deception.entropy.shannonEntropy:.4f} bits/char")
print(f"Normalised entropy        : {deception.entropy.normalizedEntropy:.4f}")
print(f"Anomaly flag (>4.5)       : {deception.entropy.anomalyFlag}")
print(f"Low-entropy flag (<2.5)   : {deception.entropy.lowEntropyFlag}")
print(f"Deception probability     : {deception.deceptionProbability * 100:.1f}%")
print(f"Structural deception flag : {deception.structuralDeceptionFlag}")
print(f"Patterns matched          : {len(deception.detectedPatterns)}")
for m in deception.detectedPatterns:
    print(f"  - {m.patternId} {m.patternName} | sev={m.severity} conf={m.confidence*100:.1f}% "
          f"| hits={m.matchedIndicators}")
print(f"Veto threshold            : {DECEPTION_PROBABILITY_VETO*100:.0f}% "
      f"-> {'VETOED' if deception.deceptionProbability >= DECEPTION_PROBABILITY_VETO else 'below veto'}")
if deception.forensicReasoning:
    print("Forensic reasoning:")
    for r in deception.forensicReasoning[:6]:
        print(f"  - {r}")
banner("2. PRODUCT EVIDENCE -- mapped from SELBY-001 intake [PERFORMANCE METRICS]")
evidence = ProductEvidence(
    productName="Audio Pro C10 MkII W (Gen 3) -- supplied Gen 2 (Addon)",
    pricePaid=625.0,
    priceAdvertised=625.0,
    specClaimed=15.0,
    specClaimedUnit="dB",
    specMeasured=0.0,
    warrantyMonths=24,
    monthsToFailure=4,
    knownIssues=4,
    totalFeaturesOrParts=8,
    regulatoryRequirements=1,
    violationsFound=1,
    notes="Selby supplied 2021 Gen 2 (Addon) hardware invoiced as 2025 Gen 3 (W).",
)
print(f"pricePaid/Advertised   : {evidence.pricePaid} / {evidence.priceAdvertised}  -> ratio {evidence.pricePaid/evidence.priceAdvertised:.4f}")
print(f"specMeasured/Claimed   : {evidence.specMeasured} / {evidence.specClaimed} {evidence.specClaimedUnit}  -> ratio {evidence.specMeasured/evidence.specClaimed:.4f}")
print(f"spec_value_curve(ratio): {spec_value_curve(evidence.specMeasured/evidence.specClaimed):.4f}  (veto floor {SPEC_VALUE_VETO_FLOOR})")
print(f"warranty/failure       : {evidence.warrantyMonths} / {evidence.monthsToFailure}  -> ratio {evidence.warrantyMonths/evidence.monthsToFailure:.4f}")
print(f"knownIssues/total      : {evidence.knownIssues} / {evidence.totalFeaturesOrParts}  -> ratio {evidence.knownIssues/evidence.totalFeaturesOrParts:.4f}")
print(f"violations/regulatory  : {evidence.violationsFound} / {evidence.regulatoryRequirements}  -> ratio {evidence.violationsFound/evidence.regulatoryRequirements:.4f}")

banner("3. BBFB GATE -- LAW (multiplicative veto) + GRACE (quadratic) + FRUIT (weighted)")
bbfb = calculate_bbfb(evidence)
print("LAW gate (any single failure forces the whole product to 0):")
print(f"  {'metric':<22} {'value':>8} {'threshold':>10} {'passed':>8}")
law_pass = True
for g in bbfb.law:
    print(f"  {g.metric:<22} {g.value:>8.4f} {g.threshold:>10.4f} {'YES' if g.passed else '**NO**':>8}")
    law_pass = law_pass and g.passed
print(f"  LAW overall            : {1 if law_pass else 0}  ({'PASS' if law_pass else '**VETOED**'})")
print()
print(f"GRACE quadratic penalty:")
print(f"  raw penalty            : {bbfb.grace.rawPenalty:.4f}")
print(f"  normalised penalty     : {bbfb.grace.normalizedPenalty:.4f}  (CRITICAL threshold {GRACE_CRITICAL_THRESHOLD})")
print(f"  risk level             : {bbfb.grace.riskLevel}")
print()
print(f"FRUIT weighted composite:")
for w in bbfb.fruit.weightedScores:
    print(f"  {w['name']:<14} weighted = {w['weighted']:.6f}")
print(f"  composite value score  : {bbfb.fruit.compositeValueScore:.6f}  (CVS threshold {CVS_THRESHOLD})")
print(f"  overall compliant      : {bbfb.overallCompliant}")
verdict_comp = "COMPLIANT" if bbfb.overallCompliant else "**NON-COMPLIANT -- economic harm substantiated**"
print(f"BBFB verdict: {verdict_comp}")

banner("4. OPTIONALITY LATTICE -- evidence-driven Cox-Ross-Rubinstein (NOT a valuation)")
derived = derive_lattice_inputs_from_evidence(evidence)
print(f"Derived inputs from evidence:")
print(f"  S0  (capital at stake)   : {derived['s0']:.4f}  (= pricePaid)")
print(f"  K1  (stage-1 strike)     : {derived['k1']:.4f}  (= pricePaid * 0.85)")
print(f"  K2  (stage-2 strike)     : {derived['k2']:.4f}  (= pricePaid * 0.5)")
print(f"  sigma1 (spec gap)        : {derived['sigma1']:.4f}  (= 0.3 * (1 + specGap))")
print(f"  sigma2 (compliance gap)  : {derived['sigma2']:.4f}  (= 0.2 * (1 + complianceGap))")
print()
lattice = hardened_compound_binomial_gate(
    deception_score=deception.deceptionProbability,
    entropy=deception.entropy.shannonEntropy,
    evidence=evidence,
)
print(f"Stage-1 value            : {lattice.stage1Value:.4f}")
print(f"Stage-2 value            : {lattice.stage2Value:.4f}")
print(f"Total optionality index  : {lattice.totalValue:.4f}")
print(f"Threshold (85% of K1+K2) : {lattice.threshold:.4f}")
print(f"Decision                 : {lattice.decision}")
print(f"Adjusted vol stage 1     : {lattice.adjustedVolatilityStage1:.4f}")
print(f"Adjusted vol stage 2     : {lattice.adjustedVolatilityStage2:.4f}")
print()
print(f"FRAMING (mandatory): {lattice.framing}")

banner("5. DECISION GATE -- GO / DEFER / TEST FIRST / REJECT")
if not law_pass or bbfb.grace.riskLevel == "CRITICAL" or not bbfb.overallCompliant:
    final_action = "REJECT"
    reason = "Economic harm substantiated; Major Failure under ACL s 260"
elif lattice.decision != "GO":
    final_action = "DEFER"
    reason = f"Lattice decision = {lattice.decision}"
else:
    final_action = "GO"
    reason = "Within limits -- proceed"
print(f"finalAction : {final_action}")
print(f"reason      : {reason}")

banner("6. LEGAL OUTPUT #1 -- ACL Section 56 demand letter (Markdown)")
bbfb_dict = json.loads(bbfb.model_dump_json())
demand = generate_acl_demand(
    invoice_spec="Audio Pro C10 MKII Wireless Multiroom Speaker White (C10 MKII-WH)",
    hardware_id="Audio Pro C10 MkII Gen 2 (Addon) -- 2021 legacy hardware",
    deception_report=deception,
    consumer_name="Justin Barnett",
    supplier_name="Selby Acoustics (Centennial Marketing Pty Ltd)",
    bbfb_score=bbfb_dict,
)
demand_path = os.path.join(ROOT, "04_Validation", "reports", "SELBY_001_acl_s56_demand.md")
os.makedirs(os.path.dirname(demand_path), exist_ok=True)
with open(demand_path, "w", encoding="utf-8") as f:
    f.write(demand)
print(f"Demand letter written: {demand_path}")
print(f"Length: {len(demand)} chars")
print("--- first 35 lines ---")
for line in demand.splitlines()[:35]:
    print(line)

banner("7. LEGAL OUTPUT #2 -- Evidence Act s.177 / s.79 affidavit (from Merkle ledger)")
affidavit_gen = LegalAffidavitGenerator(LEDGER)
affidavit = affidavit_gen.compile_full_affidavit()
affidavit_path = os.path.join(ROOT, "04_Validation", "reports", "SELBY_001_s177_affidavit.txt")
with open(affidavit_path, "w", encoding="utf-8") as f:
    f.write(affidavit)
print(f"Affidavit written: {affidavit_path}")
print(f"Length: {len(affidavit)} chars  ({affidavit.count(chr(10))} lines)")
print("--- header ---")
print("\n".join(affidavit.splitlines()[:14]))

banner("8. TRUTH LEDGER -- seal the SELBY-001 verdict to the Merkle chain")
before = vault_io.read_facts_registry()
before_root = before.get("merkle_root", "n/a") if isinstance(before, dict) else "n/a"
before_blocks = len(before.get("blocks", [])) if isinstance(before, dict) else 0
print(f"Chain before seal: {before_blocks} blocks, root {str(before_root)[:16]}...")
seal_block = vault_io.append_block("AUDIT_CYCLE_COMPLETE", {
    "case": "SELBY-001",
    "parties": "Barnett v Selby Acoustics (Centennial Marketing Pty Ltd)",
    "finalAction": final_action,
    "reason": reason,
    "deceptionProbability": round(deception.deceptionProbability, 4),
    "bbfbOverallCompliant": bbfb.overallCompliant,
    "bbfbCVS": bbfb.fruit.compositeValueScore,
    "latticeDecision": lattice.decision,
    "latticeTotalValue": round(lattice.totalValue, 4),
    "demandLetter": os.path.basename(demand_path),
    "affidavit": os.path.basename(affidavit_path),
    "operator": "OGIR-OPERATOR",
})
after = vault_io.read_facts_registry()
after_root = after.get("merkle_root", "n/a") if isinstance(after, dict) else "n/a"
after_blocks = len(after.get("blocks", [])) if isinstance(after, dict) else 0
print(f"Sealed block index : {seal_block['index']}")
print(f"Sealed block hash   : {seal_block['current_hash']}")
print(f"Chain after seal    : {after_blocks} blocks, root {str(after_root)[:16]}...")
print(f"Chain grew by       : {after_blocks - before_blocks} block(s)")

banner("8b. CASE-SPECIFIC AFFIDAVIT -- focused exhibit (full trail kept, payload elided for non-case blocks)")
case_aff = affidavit_gen.compile_case_affidavit("SELBY-001", include_spine=True)
case_aff_path = os.path.join(ROOT, "04_Validation", "reports", "SELBY_001_s177_case_affidavit.txt")
with open(case_aff_path, "w", encoding="utf-8") as f:
    f.write(case_aff)
case_lines = case_aff.count("\n")
spine_lines = sum(1 for ln in case_aff.splitlines() if ln.startswith("[SPINE]"))
print(f"Case affidavit written: {case_aff_path}")
print(f"Length            : {len(case_aff)} chars  ({case_lines} lines)")
print(f"Spine entries     : {spine_lines}  (non-case blocks kept as compact trail)")
print(f"Full-archive size : {len(affidavit)} chars  -> case exhibit is "
      f"{len(affidavit) / max(len(case_aff), 1):.1f}x smaller")
print("--- header (case exhibit) ---")
print("\n".join(case_aff.splitlines()[:18]))

banner("9. END-TO-END VERDICT SUMMARY -- SELBY-001 (Barnett v Selby Acoustics)")
print(f"Deception probability : {deception.deceptionProbability * 100:.1f}%  "
      f"({'VETOED' if deception.deceptionProbability >= DECEPTION_PROBABILITY_VETO else 'below veto'})")
print(f"BBFB LAW              : {'PASS' if law_pass else '**VETOED**'}")
print(f"BBFB GRACE risk       : {bbfb.grace.riskLevel}  (penalty {bbfb.grace.normalizedPenalty:.4f})")
print(f"BBFB CVS              : {bbfb.fruit.compositeValueScore:.6f}  "
      f"({'compliant' if bbfb.overallCompliant else 'NON-COMPLIANT'})")
print(f"Lattice decision      : {lattice.decision}  (index {lattice.totalValue:.4f} vs {lattice.threshold:.4f})")
print(f"FINAL ACTION          : {final_action} -- {reason}")
print(f"Demand letter         : {os.path.basename(demand_path)}")
print(f"Affidavit             : {os.path.basename(affidavit_path)}")
print(f"Case affidavit        : {os.path.basename(case_aff_path)}  "
      f"({len(case_aff)} chars, focused exhibit)")
print(f"Chain seal            : block {seal_block['index']} hash {seal_block['current_hash'][:16]}...")
print()
print("Cited ACL: s.18 (misleading conduct), s.56 (goods by description), "
      "s.259(3) (major failure remedy), s.260 (major failure).")
print("Evidence Act 1995 (Cth): s.177 (expert opinion), s.79 (Makita v Sprowles [2001] NSWCA 305).")
print(HR)
