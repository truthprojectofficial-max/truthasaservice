"""
Order Get It Right - FastAPI Server

Provides the full HTTP API used by the web UI.  Every endpoint is
backed by a deterministic Python function.  No cloud AI is invoked
in the request path.
"""
import json
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
import os
from typing import Optional

from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.server.tracing import TracingMiddleware
from src.server.session_tracker import SessionTrackerMiddleware
from src.engines.deception_scanner import audit_text
from src.engines.bbfb_engine import calculate_bbfb
from src.engines.acl_demand_generator import generate_acl_demand
from src.engines.evaluation_service import run_evaluation_suite
from src.engines.evaluation_cases import DEFAULT_EVALUATION_CASES
from src.engines import facts_registry
from src.engines.squeal_protocol import list_squeal_reports
from src.engines.legal_affidavit_generator import LegalAffidavitGenerator
from src.io.pipeline import (
    process_directory,
    clear_eject,
    request_eject,
)
from src.io.extractors import is_supported_input
from src.utils.canonical import canonical_dumps
from src.types import (
    AnalyzeRequest,
    CalculateRequest,
    Fact,
    FactCreate,
    ProductEvidence,
    ACLDemandRequest,
    PipelineResultModel,
    SystemStatus,
)
from config.constants import (
    PROJECT_CHANGELOG_DIR,
    PROJECT_NAME,
    PROJECT_VERSION,
    PROJECT_OPERATOR,
    PROJECT_JURISDICTION,
    DECEPTION_ONTOLOGY_VERSION,
)

DATA_DIR = Path(__file__).parent.parent / "data"
# STATIC_DIR must be parent.parent.parent (three levels up from app.py):
# app.py -> server/ -> src/ -> 02_Technical/  -> /web
# parent.parent lands on 02_Technical/src/web/ which does not exist
# (the real web folder is 02_Technical/web/). This bug silently broke
# browser-mode UI serving -- the / endpoint fell through to the JSON
# fallback and /static was never mounted. Fixed in
# UI_OPERATOR_FACING_REDESIGN_2026_07_17 with a regression test in
# tests/test_static_dir.py.
STATIC_DIR = Path(__file__).parent.parent.parent / "web"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BATCH_JOBS: dict = {}


def _parse_formats(formats: Optional[str]) -> list:
    if not formats:
        return [".md", ".pdf", ".docx"]
    out = []
    for p in formats.split(","):
        p = p.strip().lower()
        if not p.startswith("."):
            p = "." + p
        out.append(p)
    return out or [".md", ".pdf", ".docx"]


def _constants_checksum() -> str:
    import hashlib
    constants_text = open(Path(__file__).parent.parent.parent / "config" / "constants.py", "rb").read()
    return hashlib.sha256(constants_text).hexdigest()[:16]


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Modern FastAPI lifespan handler. Replaces @app.on_event("startup").

    The startup branch runs once when the app boots under uvicorn.
    The shutdown branch seals a SHUTDOWN block to the Merkle chain
    so a clean server stop is itself an auditable event. The facts
    registry is in-memory and intentionally not persisted across
    processes; every write is sealed to the Merkle chain by
    vault_io.append_block as the write happens. The shutdown seal
    records the STOP event for the same reason a STARTUP seed is
    idempotent on an empty registry: it is a deterministic witness
    that a process boundary was crossed.

    CONCURRENCY ASSUMPTION (F16, 2026-07-18):
    Single uvicorn worker is assumed. `vault_io.append_block` is a
    read-modify-write of `facts_registry.json` with no process-wide
    lock. Under uvicorn with a single worker (the default), this is
    fine: a single process holds the file open for the lifetime of
    the audit. Under `uvicorn --workers N` with N > 1, two workers
    could each read the same state, append their own block, and the
    later writer would clobber the earlier one. The Merkle chain
    would still verify (each block's current_hash is self-consistent)
    but the chain would be missing blocks. Multi-worker support
    would require a process-wide lock (e.g. `fcntl.flock`,
    `msvcrt.locking`, or a Redis SETNX), which is not in scope for
    this air-gap single-tenant build. Do NOT run with `--workers N`
    where N > 1 without first adding a lock around
    `vault_io.append_block`. See DEPLOYMENT.md section "Concurrency"
    for the deployment-side reminder.

    TestClient DOES fire lifespan correctly (unlike the deprecated
    on_event hook), so the lazy _ensure_seeded() guard in /api/facts
    is now redundant -- it is kept as a belt-and-suspenders safety
    net for any other test harness that might import the app
    object without going through the lifespan path. See OPEN_ITEMS A1.
    """
    _ensure_seeded()
    yield
    # shutdown: seal the STOP event. A single Orchestrator instance is
    # constructed and torn down; the orchestrator's shutdown() appends
    # a SHUTDOWN block to the Merkle chain on disk. This used to be
    # dead code (the lifespan was a no-op) which meant a clean
    # uvicorn stop left the chain without a final SHUTDOWN block.
    from src.agents.orchestrator import Orchestrator
    Orchestrator().shutdown()


app = FastAPI(title=PROJECT_NAME, version=PROJECT_VERSION, lifespan=_lifespan)
app.add_middleware(TracingMiddleware)
app.add_middleware(SessionTrackerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health")
def health() -> dict:
    return {
        "status": "operational",
        "project": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "operator": PROJECT_OPERATOR,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/status", response_model=SystemStatus)
def system_status() -> SystemStatus:
    return SystemStatus(
        status="operational",
        project=PROJECT_NAME,
        version=PROJECT_VERSION,
        operator=PROJECT_OPERATOR,
        jurisdiction=PROJECT_JURISDICTION,
        ontologyVersion=DECEPTION_ONTOLOGY_VERSION,
        constantsChecksum=_constants_checksum(),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest) -> dict:
    report = audit_text(req.text, context=req.context, prioritized_patterns=req.prioritizedPatterns)
    return report.model_dump()


@app.post("/api/calculate")
def calculate(req: CalculateRequest) -> dict:
    return calculate_bbfb(req.evidence).model_dump()


@app.post("/api/acl-demand")
def acl_demand(req: ACLDemandRequest) -> dict:
    report = audit_text(req.text)
    bbfb_dict = None
    if req.evidence is not None:
        bbfb_dict = calculate_bbfb(req.evidence).model_dump()
    demand = generate_acl_demand(
        req.invoice_spec,
        req.hardware_id,
        report,
        req.consumer_name,
        req.supplier_name,
        bbfb_dict,
    )
    return {"demand": demand}


@app.get("/api/facts")
def list_facts(category: Optional[str] = None, verified: Optional[bool] = None) -> dict:
    _ensure_seeded()
    return {
        "facts": [f for f in facts_registry.list_facts(category, verified)]
    }


@app.post("/api/facts")
def create_fact(fact: FactCreate) -> dict:
    # Seed the in-memory registry on the first POST. The lifespan
    # handler in modern FastAPI fires on uvicorn boot, but under
    # TestClient the lifespan does not fire before the first request,
    # so the first operator POST in a fresh process would otherwise
    # land in a registry that has none of the three grounding facts.
    # _seed_facts_once() is guarded by `if list_facts(): return`, so
    # this is safe -- it never wipes operator-added facts. This
    # closes the remaining half of OPEN_ITEMS A3.
    _ensure_seeded()
    # Uses FactCreate (not the full Fact model) so the client only
    # has to send the three fields the server does not assign:
    # category, statement, source. id / verified / createdAt /
    # updatedAt are assigned by the registry.
    created = facts_registry.add_fact(fact.category, fact.statement, fact.source)
    return created


@app.get("/api/eval/run")
def run_eval() -> dict:
    result = run_evaluation_suite(DEFAULT_EVALUATION_CASES, suite_name="default")
    return result.model_dump()


@app.get("/api/ledger")
def ledger() -> dict:
    return {"stats": facts_registry.get_stats(), "blocks": facts_registry.ledger_blocks()}


@app.get("/api/verify-chain")
def verify_chain_endpoint() -> dict:
    """Re-derive the Merkle root from on-disk blocks and compare.

    This is the HTTP surface for the standalone `python -m src.verify_chain`
    CLI subcommand. It returns the verification result without
    side-effects: nothing is sealed, no log is written, the chain is
    not touched. A third party can call this endpoint to confirm the
    chain is intact without holding the project folder.
    """
    from src.verify_chain import verify
    return verify()


@app.get("/api/squeal")
def squeal_list() -> dict:
    return {"reports": list_squeal_reports()}


@app.post("/api/affidavit")
def generate_affidavit() -> dict:
    from src.config import VAULT_DIR
    generator = LegalAffidavitGenerator(ledger_path=str(VAULT_DIR / "facts_registry.json"))
    output_path = generator.save_to_vault()
    return {"affidavit": generator.compile_full_affidavit(), "path": output_path}


@app.get("/api/affidavit/preview")
def preview_affidavit() -> dict:
    """Compile the affidavit markdown and return it without writing to disk.

    Companion to POST /api/affidavit. The POST endpoint both compiles
    the affidavit AND writes the result to the vault's archive
    directory as a permanent transcript. The preview endpoint compiles
    the same markdown but returns it in the response body without
    touching the disk. Use this when an operator wants to inspect the
    document before committing to the archive -- the chain is unchanged
    either way (the archive file is outside the Merkle chain), but a
    preview is cheaper and avoids leaving a draft on disk.
    """
    from src.config import VAULT_DIR
    generator = LegalAffidavitGenerator(ledger_path=str(VAULT_DIR / "facts_registry.json"))
    return {
        "affidavit": generator.compile_full_affidavit(),
        "preview": True,
        "wroteToDisk": False,
    }


@app.post("/api/batch/eject")
def batch_eject() -> dict:
    request_eject()
    return {"ejected": True, "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/batch/process")
def batch_process(
    inbox: str = Form(...),
    outbox: str = Form(...),
    formats: Optional[str] = Form("md,pdf,docx"),
) -> dict:
    job_id = str(uuid.uuid4())[:8]
    inbox_path = Path(inbox).resolve()
    outbox_path = Path(outbox).resolve()
    clear_eject()
    results = process_directory(inbox_path, outbox_path, _parse_formats(formats))
    files = []
    for r in results:
        for op in r.output_paths:
            files.append({"filename": op.name, "path": str(op)})
    BATCH_JOBS[job_id] = {
        "id": job_id,
        "inbox": str(inbox_path),
        "outbox": str(outbox_path),
        "files": files,
        "summary": {
            "success": sum(1 for r in results if r.status == "success"),
            "errors": sum(1 for r in results if r.status == "error"),
            "warnings": sum(1 for r in results if r.status == "warning"),
            "ejected": sum(1 for r in results if r.status == "ejected"),
        },
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    return BATCH_JOBS[job_id]


@app.post("/api/batch/upload")
def batch_upload(
    files: list[UploadFile] = File(...),
    formats: Optional[str] = Form("md,pdf,docx"),
) -> dict:
    job_id = str(uuid.uuid4())[:8]
    work_dir = Path(tempfile.mkdtemp(prefix=f"ogir_batch_{job_id}_"))
    inbox_path = work_dir / "inbox"
    outbox_path = work_dir / "outbox"
    inbox_path.mkdir(parents=True, exist_ok=True)
    outbox_path.mkdir(parents=True, exist_ok=True)

    saved = []
    for upload in files:
        if not upload.filename:
            continue
        dest = inbox_path / Path(upload.filename).name
        try:
            content = upload.file.read()
            dest.write_bytes(content)
            saved.append(str(dest))
        finally:
            upload.file.close()

    if not saved:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail="No files uploaded.")

    clear_eject()
    results = process_directory(inbox_path, outbox_path, _parse_formats(formats))
    output_files = []
    for r in results:
        for op in r.output_paths:
            output_files.append({"filename": op.name, "path": str(op)})
    BATCH_JOBS[job_id] = {
        "id": job_id,
        "workDir": str(work_dir),
        "files": output_files,
        "summary": {
            "success": sum(1 for r in results if r.status == "success"),
            "errors": sum(1 for r in results if r.status == "error"),
            "warnings": sum(1 for r in results if r.status == "warning"),
        },
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    return BATCH_JOBS[job_id]


@app.get("/api/batch/job/{job_id}")
def batch_job(job_id: str) -> dict:
    job = BATCH_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/batch/download/{job_id}/{filename}")
def batch_download(job_id: str, filename: str):
    job = BATCH_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    safe_name = Path(filename).name
    file_entry = next((f for f in job.get("files", []) if f["filename"] == safe_name), None)
    if not file_entry:
        raise HTTPException(status_code=404, detail="File not found in job")
    filepath = Path(file_entry["path"])
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File missing on disk")
    return FileResponse(filepath, filename=safe_name)


@app.get("/")
def root():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"status": f"{PROJECT_NAME} v{PROJECT_VERSION}", "docs": "/docs"}



# ---------------------------------------------------------------------------
# Changelog & Incident Audit
#
# Every time something fails or changes, the operator appends a record
# here.  This is the human-facing counterpart to the Merkle truth ledger.
# The Merkle ledger proves "what the engine decided"; the changelog
# records "what the operator noticed".  Both are required.
#
# File format: JSONL (one JSON object per line, UTF-8, sort_keys=True,
# append-only).  Schema: {binId, details, summary, timestamp, type}.
# ---------------------------------------------------------------------------
_CHANGELOG_PATH = Path(os.environ.get("OGIR_CHANGELOG", PROJECT_CHANGELOG_DIR))


def _read_changelog() -> list:
    if not _CHANGELOG_PATH.exists():
        return []
    entries = []
    with _CHANGELOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _write_changelog_entry(entry: dict) -> dict:
    with _CHANGELOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


class ChangelogRequest(BaseModel):
    type: str
    summary: str
    details: str = ""
    binId: str = "browser"


@app.get("/api/changelog")
def changelog_list() -> dict:
    return {"entries": _read_changelog()}


@app.post("/api/changelog")
def changelog_add(req: ChangelogRequest) -> dict:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": req.type,
        "summary": req.summary,
        "details": req.details,
        "binId": req.binId,
    }
    # Gate test-suite synthetic writes so the live human-facing
    # changelog stays clean. The pytest suite identifies itself with
    # binId="test-runner"; we redirect those entries to a temp file
    # unless the env var OGIR_TEST_WRITE_CHANGELOG=1 is set (operator
    # opt-in). This closes the "changelog pollution" finding (F5 in
    # OGIR_ASSESSMENT_2026-07-18.md) without removing the wiring test.
    is_test_write = (
        req.binId == "test-runner"
        and os.environ.get("OGIR_TEST_WRITE_CHANGELOG", "") != "1"
    )
    if is_test_write:
        import tempfile as _tempfile
        with _tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        ) as _tmp:
            _tmp.write(json.dumps(entry, sort_keys=True) + "\n")
            tmp_path = _tmp.name
        return {"status": "redirected_to_temp", "path": tmp_path, **entry}
    _write_changelog_entry(entry)
    return entry


# ---------------------------------------------------------------------------
# MCP Server: Handshake of Delegation
#
# Endpoints:
#   GET  /api/mcp/jobs                  -- list all jobs
#   GET  /api/mcp/jobs/pending?agent=  -- list pending jobs for an agent
#   POST /api/mcp/jobs                  -- create a new job token
#   POST /api/mcp/jobs/{id}/claim       -- mark a job IN_PROGRESS
#   POST /api/mcp/jobs/{id}/close       -- close a job COMPLETED/FAILED/REFUSED
#   GET  /api/mcp/tau                   -- Tau firewall stats
#   GET  /api/mcp/stats                 -- full delegator stats
# ---------------------------------------------------------------------------
from src.agents.job_delegator import AgentJobDelegator, SPATIAL_MAP
from src.agents.tau_firewall import StructuralRefusal

_MCP_DELEGATOR: AgentJobDelegator = None


def _get_delegator() -> AgentJobDelegator:
    global _MCP_DELEGATOR
    if _MCP_DELEGATOR is None:
        from src.agents.tau_firewall import TauFirewall
        _MCP_DELEGATOR = AgentJobDelegator(tau=TauFirewall())
    return _MCP_DELEGATOR


class JobCreateRequest(BaseModel):
    assigner: str
    target_agent: str
    task_urn: str
    data: Optional[dict] = None


class JobCloseRequest(BaseModel):
    result_hash: str
    status: str = "COMPLETED"


@app.get("/api/mcp/jobs")
def mcp_list_jobs() -> dict:
    return {"jobs": _get_delegator().list_all_jobs()}


@app.get("/api/mcp/jobs/pending")
def mcp_list_pending(agent: str) -> dict:
    return {"agent": agent, "jobs": _get_delegator().list_pending_jobs(agent)}


@app.post("/api/mcp/jobs")
def mcp_create_job(req: JobCreateRequest):
    try:
        job_id = _get_delegator().create_job_token(
            assigner=req.assigner,
            target_agent=req.target_agent,
            task_urn=req.task_urn,
            data=req.data,
        )
        return {"jobId": job_id}
    except StructuralRefusal as e:
        return JSONResponse(status_code=423, content={"error": "TAU_CEILING_EXCEEDED", "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/mcp/jobs/{job_id}/claim")
def mcp_claim_job(job_id: str):
    try:
        return _get_delegator().claim_job(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Job not found")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.post("/api/mcp/jobs/{job_id}/close")
def mcp_close_job(job_id: str, req: JobCloseRequest):
    try:
        return _get_delegator().close_job(job_id, req.result_hash, status=req.status)
    except KeyError:
        raise HTTPException(status_code=404, detail="Job not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/mcp/tau")
def mcp_tau_stats() -> dict:
    return _get_delegator().tau.stats()


@app.get("/api/mcp/stats")
def mcp_stats() -> dict:
    return _get_delegator().stats()


@app.get("/api/ontology")
def ontology_list() -> dict:
    from src.engines.deception_ontology_data import DECEPTION_ONTOLOGY
    return {
        "version": DECEPTION_ONTOLOGY_VERSION,
        "count": len(DECEPTION_ONTOLOGY),
        "patterns": [p.model_dump() for p in DECEPTION_ONTOLOGY],
    }


@app.post("/api/parse/evidence")
def parse_evidence(req: dict) -> dict:
    from src.io.evidence_parser import extract_product_evidence
    text = req.get("text", "")
    parsed = extract_product_evidence(text)
    if parsed is None:
        return {"parsed": None, "reason": "no product-like evidence found"}
    return {
        "parsed": {
            "product_name": parsed.product_name,
            "price_paid": parsed.price_paid,
            "price_advertised": parsed.price_advertised,
            "spec_claimed": parsed.spec_claimed,
            "spec_claimed_unit": parsed.spec_claimed_unit,
            "spec_measured": parsed.spec_measured,
            "warranty_months": parsed.warranty_months,
            "months_to_failure": parsed.months_to_failure,
            "known_issues": parsed.known_issues,
            "total_features_or_parts": parsed.total_features_or_parts,
            "regulatory_requirements": parsed.regulatory_requirements,
            "violations_found": parsed.violations_found,
            "confidence": parsed.confidence,
            "raw_hits": parsed.raw_hits,
        }
    }


class CanonicalDumpRequest(BaseModel):
    payload: dict


@app.post("/api/canonical/dump")
def canonical_dump(req: CanonicalDumpRequest) -> dict:
    """Return the canonical-JSON serialisation of the supplied payload.

    This is the HTTP surface for ``src.utils.canonical.canonical_dumps``.
    It lets tests and third-party clients verify that the runtime will
    produce a byte-identical serialisation without importing the utility.
    NaN / Inf and unknown types are rejected with a 400 so the caller
    knows the payload is not canonicalisable.
    """
    try:
        return {"canonical": canonical_dumps(req.payload)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "CANONICAL_VALUE_ERROR", "message": str(e)})
    except TypeError as e:
        raise HTTPException(status_code=400, detail={"error": "CANONICAL_TYPE_ERROR", "message": str(e)})


class OrchestratorRequest(BaseModel):
    category: str
    statement: str
    product_evidence: Optional[dict] = None


@app.post("/api/orchestrator/process")
def orchestrator_process(req: OrchestratorRequest):
    from src.agents.orchestrator import Orchestrator
    from src.types import ProductEvidence
    core = Orchestrator()
    evidence = None
    if req.product_evidence is not None:
        evidence = ProductEvidence(**req.product_evidence)
    result = core.process_input(
        category=req.category,
        statement=req.statement,
        product_evidence=evidence,
    )
    return result

def _seed_facts_once() -> None:
    """Seed the in-memory facts registry with the three grounding facts.

    Safe across restarts: only resets and re-seeds if the registry is
    currently empty. This preserves operator-added facts between
    server boots while still guaranteeing that a fresh process always
    starts with the three grounding facts present. The orchestrator
    no longer re-seeds on every request (see orchestrator.py). The
    app startup handler calls this for uvicorn-mode boots; /api/facts
    calls _ensure_seeded() as belt-and-suspenders for TestClient.
    """
    if facts_registry.list_facts():
        return
    facts_registry.reset_registry()
    facts_registry.add_fact(
        "Governance",
        f"{PROJECT_NAME} enforces the four-gate audit model (Deception / BBFB / Valuation / Decision).",
        "system",
    )
    facts_registry.add_fact(
        "Forensic",
        f"All deception detections use the deterministic {DECEPTION_ONTOLOGY_VERSION} ontology.",
        "system",
    )
    facts_registry.add_fact(
        "Technical",
        "BBFB engine uses LAW / GRACE / FRUIT decomposition with quadratic penalty and weighted FRUIT score.",
        "system",
    )


_SEEDED: bool = False


def _ensure_seeded() -> None:
    """Module-level idempotency guard. The seed runs at most once per process."""
    global _SEEDED
    if _SEEDED:
        return
    _SEEDED = True
    _seed_facts_once()