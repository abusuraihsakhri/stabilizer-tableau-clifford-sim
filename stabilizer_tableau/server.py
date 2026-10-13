"""
FastAPI REST API Server for Aaronson-Gottesman Stabilizer Tableau Fast Clifford Simulator.
"""
from typing import Dict, Any
from .models import FrontierPayload
from .agents import StabilizerCoordinator
from .tableau import simulate_circuit

coordinator = StabilizerCoordinator()


def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel, Field
        from fastapi import HTTPException
        from fastapi.staticfiles import StaticFiles
        from pathlib import Path

        app = FastAPI(
            title="Aaronson-Gottesman Stabilizer Tableau Fast Clifford Simulator",
            description="Simulates Clifford circuits using binary symplectic stabilizer tableau representations.",
            version="2.0.0-FRONTIER",
        )

        class TaskRequest(BaseModel):
            task_id: str = "TASK-2026-001"
            target_identifier: str = "TARGET-BIO-KEY"
            primary_metric: float = 28.5
            secondary_metric: float = 14.2
            status_descriptor: str = "DISCORDANT_ANOMALY"
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = {}

        class ChatRequest(BaseModel):
            query: str

        class CircuitRequest(BaseModel):
            qubits: int = Field(ge=1, le=64)
            circuit: str = Field(max_length=200_000)
            seed: int = Field(default=0, ge=-(2**31), le=2**32 - 1)

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "stabilizer-tableau-clifford-sim", "domain": "Quantum Computing", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit")
        def api_audit(req: TaskRequest):
            payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
            )
            return coordinator.process(payload)

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        @app.post("/api/simulate")
        def api_simulate(req: CircuitRequest):
            try:
                return simulate_circuit(req.qubits, req.circuit, req.seed)
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc

        app.mount("/", StaticFiles(directory=str(Path(__file__).resolve().parent / "web"), html=True), name="workbench")
        return app
    except ImportError:
        return None
