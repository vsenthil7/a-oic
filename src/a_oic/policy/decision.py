from enum import Enum
from dataclasses import dataclass


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


@dataclass(frozen=True)
class PolicyResult:
    decision: Decision
    reason: str


def evaluate_incident(severity: str, has_runbook: bool) -> PolicyResult:
    """
    Deterministic policy gate.
    AI output is NOT trusted here.
    """

    if severity == "SEV1" and not has_runbook:
        return PolicyResult(
            decision=Decision.REQUIRE_APPROVAL,
            reason="SEV1 incident without verified runbook"
        )

    if severity in {"SEV1", "SEV2"}:
        return PolicyResult(
            decision=Decision.REQUIRE_APPROVAL,
            reason="High severity incident"
        )

    return PolicyResult(
        decision=Decision.ALLOW,
        reason="Low risk incident"
    )
