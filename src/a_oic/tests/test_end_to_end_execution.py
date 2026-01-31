from a_oic.adapters.ai_plan_validator import validate_ai_plan
from a_oic.orchestrate.executor import LocalOrchestrateStub, execute_plan


def test_end_to_end_sev3_allow_executes_restart():
    # Given: policy says ALLOW (we already tested policy module separately)
    incident_id = "INC-EXEC-001"
    policy_decision = "ALLOW"
    policy_reason = "Low risk incident"

    # And: AI output is bounded and validated
    plan = validate_ai_plan(
        {
            "schema_version": "1.0",
            "summary": "Restart service safely to recover production availability",
            "actions": [{"type": "restart", "target": "payments-api"}],
        }
    )

    # When: we execute through orchestrate boundary
    outcome = execute_plan(
        incident_id=incident_id,
        policy_decision=policy_decision,
        policy_reason=policy_reason,
        validated_plan=plan,
        orchestrate=LocalOrchestrateStub(),
    )

    # Then: record is EXECUTED and orchestrate returns ok
    assert outcome.record.incident_id == incident_id
    assert outcome.record.status.value == "EXECUTED"
    assert outcome.orchestrate is not None
    assert outcome.orchestrate.ok is True
