import pytest
from a_oic.adapters.ai_plan_validator import validate_ai_plan
from a_oic.adapters.ai_adapter import AIPlanRejected


def test_missing_schema_version_rejected():
    with pytest.raises(AIPlanRejected):
        validate_ai_plan({
            "summary": "Restart service safely to recover production availability",
            "actions": [{"type": "restart", "target": "api"}]
        })


def test_unknown_schema_version_rejected():
    with pytest.raises(AIPlanRejected):
        validate_ai_plan({
            "schema_version": "2.0",
            "summary": "Restart service safely to recover production availability",
            "actions": [{"type": "restart", "target": "api"}]
        })


def test_supported_schema_version_accepted():
    plan = validate_ai_plan({
        "schema_version": "1.0",
        "summary": "Restart service safely to recover production availability",
        "actions": [{"type": "restart", "target": "api"}]
    })
    assert plan["schema_version"] == "1.0"
