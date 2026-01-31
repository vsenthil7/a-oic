import json
from jsonschema import Draft202012Validator, ValidationError
from pathlib import Path

from a_oic.adapters.ai_adapter import AIPlanRejected


_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "contracts"
    / "ai_plan.schema.json"
)


def load_ai_plan_schema() -> dict:
    with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_ai_plan(plan: dict) -> dict:
    """
    Enforces strict AI output validation.
    Any deviation is rejected before policy or execution.
    """
    schema = load_ai_plan_schema()
    validator = Draft202012Validator(schema)

    errors = sorted(validator.iter_errors(plan), key=lambda e: e.path)
    if errors:
        messages = "; ".join(error.message for error in errors)
        raise AIPlanRejected(f"AI plan schema violation: {messages}")

    return plan
