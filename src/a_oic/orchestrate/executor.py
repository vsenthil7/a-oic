from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from a_oic.state.execution_record import ExecutionRecord, ExecutionStatus, now_utc_iso
from a_oic.orchestrate.watsonx_adapter import WatsonxOrchestrateAdapter


def _select_orchestrate(orchestrate):
    """
    Selects orchestrate adapter.
    Priority:
    1. Explicitly passed orchestrate
    2. Feature-flagged real watsonx adapter
    3. Local stub (default)
    """
    if orchestrate is not None:
        return orchestrate

    if os.getenv("USE_REAL_ORCHESTRATE") == "true":
        return WatsonxOrchestrateAdapter(client=None)  # real client injected later

    return LocalOrchestrateStub()


@dataclass(frozen=True)
class OrchestrateResult:
    ok: bool
    detail: str


class OrchestrateClient(Protocol):
    """
    Boundary only. Today: local stub.
    Tomorrow: IBM watsonx Orchestrate.
    """
    def execute_actions(self, incident_id: str, actions: List[Dict[str, Any]]) -> OrchestrateResult:
        ...


class LocalOrchestrateStub:
    """
    Deterministic stub for now.
    Produces auditable output with zero external dependency.
    """
    def execute_actions(self, incident_id: str, actions: List[Dict[str, Any]]) -> OrchestrateResult:
        allowed = {"scale", "rollback", "restart", "verify"}
        for a in actions:
            if a.get("type") not in allowed:
                return OrchestrateResult(ok=False, detail=f"Rejected unknown action type: {a.get('type')}")
        return OrchestrateResult(ok=True, detail=f"Executed {len(actions)} action(s) for {incident_id}")


@dataclass(frozen=True)
class ExecutionOutcome:
    record: ExecutionRecord
    orchestrate: Optional[OrchestrateResult] = None


def execute_plan(
    *,
    incident_id: str,
    policy_decision: str,
    policy_reason: str,
    validated_plan: Dict[str, Any],
    orchestrate: Optional[OrchestrateClient],
) -> ExecutionOutcome:
    """
    Execution spine:
    - AI plan must already be schema-validated (bounded)
    - Policy decision is authoritative
    - Orchestration boundary executes only when allowed
    """

    orchestrate = _select_orchestrate(orchestrate)

    actions: List[Dict[str, Any]] = list(validated_plan.get("actions", []))

    # Fail-closed: if decision isn't ALLOW, do not execute
    if policy_decision != "ALLOW":
        status = (
            ExecutionStatus.REQUIRE_APPROVAL
            if policy_decision == "REQUIRE_APPROVAL"
            else ExecutionStatus.BLOCKED
        )
        rec = ExecutionRecord(
            incident_id=incident_id,
            decision=policy_decision,
            actions=actions,
            status=status,
            created_at_utc=now_utc_iso(),
            reason=policy_reason,
        )
        return ExecutionOutcome(record=rec, orchestrate=None)

    # Allowed path
    rec_pending = ExecutionRecord(
        incident_id=incident_id,
        decision=policy_decision,
        actions=actions,
        status=ExecutionStatus.PENDING,
        created_at_utc=now_utc_iso(),
        reason=policy_reason,
    )

    result = orchestrate.execute_actions(incident_id, actions)

    final_status = ExecutionStatus.EXECUTED if result.ok else ExecutionStatus.FAILED
    rec_final = ExecutionRecord(
        incident_id=incident_id,
        decision=policy_decision,
        actions=actions,
        status=final_status,
        created_at_utc=rec_pending.created_at_utc,
        reason=policy_reason if result.ok else result.detail,
    )

    return ExecutionOutcome(record=rec_final, orchestrate=result)
