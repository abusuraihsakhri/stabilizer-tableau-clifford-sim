"""
FastAPI REST API Server for Stabilizer Tableau Clifford Sim.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import Field
from stabilizer_tableau.tableau import simulate_circuit
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Stabilizer Tableau Clifford Sim API",
    description="Clifford circuit simulation and legacy audit endpoint",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


class CircuitRequest(BaseModel):
    qubits: int = Field(ge=1, le=64)
    circuit: str = Field(max_length=200_000)
    seed: int = Field(default=0, ge=-(2**31), le=2**32 - 1)


@app.post("/api/simulate")
def api_simulate(req: CircuitRequest):
    try:
        return simulate_circuit(req.qubits, req.circuit, req.seed)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "stabilizer-tableau-clifford-sim", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


# Register the workbench after the REST routes, preserving their priority.
app.mount("/", StaticFiles(directory=str(Path(__file__).resolve().parent.parent / "stabilizer_tableau" / "web"), html=True), name="workbench")
