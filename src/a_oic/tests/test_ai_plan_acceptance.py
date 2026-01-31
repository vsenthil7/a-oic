from a_oic.adapters.ai_plan_validator import validate_ai_plan


def test_valid_ai_plan_is_accepted():
    valid_plan = {
        "summary": "Restart service safely",
        "actions": [
            {"type": "restart", "target": "payments-api"}
        ],
    }

    result = validate_ai_plan(valid_plan)

    assert result == valid_plan
