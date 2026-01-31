from a_oic.policy.decision import evaluate_incident, Decision


def test_sev1_without_runbook_requires_approval():
    result = evaluate_incident("SEV1", has_runbook=False)
    assert result.decision == Decision.REQUIRE_APPROVAL


def test_sev3_is_allowed():
    result = evaluate_incident("SEV3", has_runbook=True)
    assert result.decision == Decision.ALLOW
