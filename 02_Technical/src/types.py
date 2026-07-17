"""
Order Get It Right - Type Definitions

Every public type is a Pydantic BaseModel.  This gives the runtime a single
canonical schema, automatic JSON serialisation, and stable API contracts."""
from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TabId(str, Enum):
    dashboard = "dashboard"
    bbfb = "bbfb"
    deception = "deception"
    facts = "facts"
    protocol = "protocol"
    discovery = "discovery"
    evaluation = "evaluation"
    batch = "batch"


class DeceptionPattern(BaseModel):
    id: str
    name: str
    category: str
    description: str
    indicators: List[str]
    severity: str
    threshold: float


class DeceptionMatch(BaseModel):
    patternId: str
    patternName: str
    confidence: float
    matchedIndicators: List[str]
    severity: str


class EntropyAnalysis(BaseModel):
    shannonEntropy: float
    normalizedEntropy: float
    characterDistribution: Dict[str, int]
    anomalyFlag: bool
    lowEntropyFlag: bool


class DeceptionReport(BaseModel):
    inputText: str
    entropy: EntropyAnalysis
    detectedPatterns: List[DeceptionMatch]
    deceptionProbability: float
    structuralDeceptionFlag: bool
    forensicReasoning: List[str]
    timestamp: str


class LAWGateInput(BaseModel):
    metric: str
    value: float
    threshold: float


class LAWGateResult(LAWGateInput):
    passed: bool


class GRACERiskResult(BaseModel):
    rawPenalty: float
    normalizedPenalty: float
    riskLevel: str


class FRUITResult(BaseModel):
    compositeValueScore: float
    weightedScores: List[Dict[str, Any]]
    compliant: bool
    threshold: float


class BBFBResult(BaseModel):
    inputEvidence: List[Dict[str, Any]]
    law: List[LAWGateResult]
    grace: GRACERiskResult
    fruit: FRUITResult
    overallCompliant: bool
    timestamp: str


class RealOptionsValuation(BaseModel):
    """The Real-Options Lattice output.

    F7 (2026-07-18): the ``framing`` field is mandatory and non-empty.
    Every consumer of this model MUST surface the framing string so a
    third-party reader (operator, auditor, s.177 affidavit recipient)
    cannot mistake the optionality index for a business valuation.
    The default factory loads ``LATTICE_FRAMING`` from
    ``config/constants.py`` so a refactor that drops the explicit
    ``framing=...`` kwarg still surfaces the disclaimer.
    """
    stage1Value: float
    stage2Value: float
    totalValue: float
    threshold: float
    decision: str
    adjustedVolatilityStage1: float
    adjustedVolatilityStage2: float
    learningDelta: float
    timestamp: str
    framing: str = "deception-adjusted optionality index (not a business valuation)"


class Fact(BaseModel):
    id: int
    category: str
    statement: str
    source: str
    verified: bool
    createdAt: str
    updatedAt: str


class FactCreate(BaseModel):
    category: str
    statement: str
    source: str


class ProductEvidence(BaseModel):
    productName: str = "Unknown Product"
    pricePaid: float = 0.0
    priceAdvertised: float = 0.0
    specClaimed: float = 0.0
    specClaimedUnit: str = ""
    specMeasured: float = 0.0
    warrantyMonths: float = 0.0
    monthsToFailure: float = 0.0
    knownIssues: float = 0.0
    totalFeaturesOrParts: float = 0.0
    regulatoryRequirements: float = 0.0
    violationsFound: float = 0.0
    notes: str = ""


class CalculateRequest(BaseModel):
    evidence: ProductEvidence


class AnalyzeRequest(BaseModel):
    text: str
    prioritizedPatterns: Optional[List[str]] = None
    context: Optional[str] = None


class ACLDemandRequest(BaseModel):
    invoice_spec: str
    hardware_id: str
    text: str
    consumer_name: str = "[Consumer Name]"
    supplier_name: str = "[Supplier Name]"
    evidence: Optional[ProductEvidence] = None


class PipelineRequest(BaseModel):
    inbox: str
    outbox: str
    formats: str = "md,pdf,docx"


class PipelineResultModel(BaseModel):
    input: str
    status: str
    outputs: List[str]
    error: Optional[str] = None
    deceptionProbability: float = 0.0
    bbfbCompliant: Optional[bool] = None
    aclGenerated: bool = False


class EvaluationCase(BaseModel):
    id: str
    label: str
    input: str
    expectedDeceptive: bool
    expectedMinPatterns: int = 0
    expectedMinDeceptionProbability: Optional[float] = None
    expectedMaxDeceptionProbability: Optional[float] = None
    tags: List[str] = Field(default_factory=list)


class EvaluationCaseResult(BaseModel):
    caseId: str
    label: str
    passed: bool
    deceptionProbability: float
    patternCount: int
    expectedDeceptive: bool
    predictedDeceptive: bool
    falsePositive: bool
    falseNegative: bool
    tags: List[str] = Field(default_factory=list)


class EvaluationMetrics(BaseModel):
    totalCases: int
    passed: int
    failed: int
    accuracy: float
    truePositives: int
    trueNegatives: int
    falsePositives: int
    falseNegatives: int
    precision: float
    recall: float
    f1Score: float


class EvaluationRunResult(BaseModel):
    runId: str
    suiteName: str
    metrics: EvaluationMetrics
    cases: List[EvaluationCaseResult]
    timestamp: str


class SystemStatus(BaseModel):
    status: str
    project: str
    version: str
    operator: str
    jurisdiction: str
    ontologyVersion: str
    constantsChecksum: str
    timestamp: str