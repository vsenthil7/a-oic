# Manual Test Scenarios — A-OIC Kernel

> **Purpose**
>
> This document preserves **human-understanding test scenarios** for the A‑OIC kernel.
> These are **not executable tests**. Authoritative behavior is enforced via automated tests under `src/a_oic/tests/`.
>
> Manual scenarios exist to:
> - Build intuition
> - Explain behavior to reviewers/judges
> - Support demos and walkthroughs

---

## Scope

These scenarios validate **deterministic policy behavior** implemented in:

- `a_oic.policy.decision.evaluate_incident`
- `a_oic.core.evaluator.evaluate_incident_payload`

No AI, orchestration, or external systems are involved at this stage.

---

## Scenario 1 — SEV1 Incident without Runbook

### Input
- `severity`: `SEV1`
- `has_runbook`: `false`

### Expected Decision
- **Decision**: `REQUIRE_APPROVAL`
- **Reason**: `SEV1 incident without verified runbook`

### Rationale
A SEV1 incident represents a critical production impact.
Without a verified runbook (SOP), autonomous action is unsafe.

The system must:
- Fail closed
- Escalate to Human‑in‑the‑Loop (HITL)

This enforces operational governance and auditability.

---

## Scenario 2 — SEV3 Incident with Runbook

### Input
- `severity`: `SEV3`
- `has_runbook`: `true`

### Expected Decision
- **Decision**: `ALLOW`
- **Reason**: `Low risk incident`

### Rationale
A SEV3 incident is low‑to‑moderate impact.
With a verified runbook present, the risk is controlled.

The system may:
- Proceed with automated execution
- Skip human approval

This supports fast recovery while preserving safety.

---

## Relationship to Automated Tests

Each manual scenario corresponds to automated tests such as:

- `test_sev1_without_runbook_requires_approval`
- `test_sev3_is_allowed`

Automated tests are the **source of truth**.
Manual scenarios provide **explanatory context**, not enforcement.

---

## Governance Note

- No executable scripts are stored in this folder
- No alternative execution paths are introduced
- All supported behavior flows through the kernel

This maintains a **single authoritative decision path**:

```
Schema → Policy → (AI later) → Orchestrate
```

---

_Last updated: 31/01/2026_

