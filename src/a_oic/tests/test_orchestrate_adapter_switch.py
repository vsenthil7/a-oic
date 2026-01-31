import os
from a_oic.orchestrate.executor import execute_plan
from a_oic.adapters.ai_plan_validator import validate_ai_plan

def test_real_orchestrate_path_selected(monkeypatch):
    monkeypatch.setenv("USE_REAL_ORCHESTRATE", "true")

    plan = validate_ai_plan({
        "summary": "Restart service safely",
        "actions": [{"type": "restart", "target": "payments-api"}]
    })

    outcome = execute_plan(
        incident_id="INC-ORCH-001",
        policy_decision="ALLOW",
        policy_reason="Low risk",
        validated_plan=plan,
        orchestrate=None
    )

    assert outcome.orchestrate.detail.startswith("watsonx orchestrate executed")
