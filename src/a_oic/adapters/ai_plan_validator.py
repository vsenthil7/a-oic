import json
from pathlib import Path
from jsonschema import Draft202012Validator

from a_oic.adapters.ai_adapter import AIPlanRejected
from a_oic.contracts.registry import is_supported

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

    # ---- VERSION GATE (AUTHORITATIVE) ----
    version = plan.get("schema_version")
    if not version:
        raise AIPlanRejected("Missing schema_version in AI plan")

    if not is_supported(version):
        raise AIPlanRejected(f"Unsupported AI plan schema_version: {version}")

    # ---- SCHEMA VALIDATION ----
    schema = load_ai_plan_schema()
    validator = Draft202012Validator(schema)

    errors = sorted(validator.iter_errors(plan), key=lambda e: e.path)
    if errors:
        messages = "; ".join(error.message for error in errors)
        raise AIPlanRejected(f"AI plan schema violation: {messages}")

    return plan
