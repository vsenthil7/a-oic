from typing import Dict, Any
from a_oic.policy.decision import PolicyResult


class AIPlanRejected(Exception):
    """Raised when AI output violates schema or policy."""
    pass


class AIAdapter:
    """
    Boundary adapter for AI systems (e.g., watsonx Granite).
    AI has no authority here — only structured suggestion.
    """

    def generate_plan(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns a raw AI plan suggestion.
        Must be validated by schema before use.
        """
        raise NotImplementedError("AI adapter not implemented yet")


def validate_ai_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder for JSON schema validation.
    Will be wired to ai_plan.schema.json.
    """
    if not isinstance(plan, dict):
        raise AIPlanRejected("AI plan must be an object")

    if "actions" not in plan:
        raise AIPlanRejected("AI plan missing actions")

    return plan
