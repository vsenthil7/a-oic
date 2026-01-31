import pytest

from a_oic.adapters.ai_plan_validator import validate_ai_plan
from a_oic.adapters.ai_adapter import AIPlanRejected


def test_ai_plan_missing_actions_is_rejected():
    bad_plan = {
        "summary": "Restart service"
        # missing actions
    }

    with pytest.raises(AIPlanRejected):
        validate_ai_plan(bad_plan)


def test_ai_plan_invalid_action_type_is_rejected():
    bad_plan = {
        "summary": "Do something risky",
        "actions": [
            {"type": "self_destruct", "target": "prod-db"}
        ]
    }

    with pytest.raises(AIPlanRejected):
        validate_ai_plan(bad_plan)
