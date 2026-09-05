"""
Automated Pytest Test Suite for Stabilizer Tableau Clifford Sim.
Domain: Quantum Computing / Stabilizer Circuit Simulation
Reference: Aaronson-Gottesman Clifford Algorithm
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, AuditTrail, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_audit_trail_integrity_verification():
    """Test that audit trail detects tampering and verifies HMAC signatures."""
    trail = AuditTrail(secret_key="test-key-for-integrity-verification")

    # Log some entries
    trail.log("test-actor", "tier-1", "TEST_EVENT", {"data": "value1"})
    trail.log("test-actor", "tier-1", "TEST_EVENT", {"data": "value2"})
    trail.log("test-actor", "tier-1", "TEST_EVENT", {"data": "value3"})

    # Verify integrity of untampered trail
    assert trail.verify_integrity() is True

    # Tamper with an entry
    trail.logs[1]["payload_hash"] = "tampered_hash"

    # Integrity check should fail
    assert trail.verify_integrity() is False


def test_audit_trail_secure_key_generation():
    """Test that AuditTrail generates a secure random key when none is provided."""
    trail1 = AuditTrail()
    trail2 = AuditTrail()

    # Both should have different auto-generated keys
    assert trail1.secret_key != trail2.secret_key

    # Key should be non-empty bytes
    assert len(trail1.secret_key) > 0
    assert isinstance(trail1.secret_key, bytes)


def test_phi_guard_redaction():
    """Test that PHI guard properly redacts sensitive information."""
    text_with_phi = "Patient John Doe MRN-12345678 phone 555-123-4567"
    redacted = PHIGuard.redact_phi(text_with_phi)
    assert "John Doe" not in redacted
    assert "MRN-12345678" not in redacted
    assert "555-123-4567" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted
