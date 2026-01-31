from a_oic.policy.decision import evaluate_incident, PolicyResult
from typing import Dict


def evaluate_incident_payload(
    incident: Dict,
    has_runbook: bool
) -> PolicyResult:
    """
    Core kernel entrypoint.
    - Assumes schema validation already passed
    - No AI involved
    - Deterministic and testable
    """

    severity = incident["severity"]

    return evaluate_incident(
        severity=severity,
        has_runbook=has_runbook
    )
