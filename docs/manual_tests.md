# Manual & Executable Validation — A‑OIC Kernel

> **Important clarification (read first)**
>
>This project uses **TWO kinds of tests**, both intentional:
>
>1. **Automated tests** → enforce truth (pytest, CI, non-negotiable)
>2. **Executable manual tests** → teach humans (run locally, inspect output)
>
>Manual tests are **NOT markdown-only descriptions**.
>They are **runnable commands with fixed inputs and expected outputs**.
>
>This document standardizes how every manual test works so there is:
>- No confusion
>- No copy–paste errors
>- No guessing what to run

---

## Rule of the System (LOCKED)

> Every automated test **MUST** have a corresponding **executable manual test**.
>
>The difference is:
>- Automated test → `pytest` decides PASS/FAIL
>- Manual test → **you run a command and read the output**

Both exist. Neither replaces the other.

---

## Manual Tests ARE Executable — How

> These commands are intentionally written to be **PowerShell-safe and copy-pasteable on Windows**, which is the lowest common denominator for reviewers.


Manual tests are executed in **one of three allowed ways**:

1. `python -c "..."` (inline, zero files)
2. `python -m a_oic.<module>` (preferred later)
3. Temporary local script (NOT committed)

No other forms are allowed.

---

# MANUAL TEST 1 — Policy Gate (SEV1, No Runbook)

### What this validates
Deterministic policy logic **without AI**.

### Input
- Severity: `SEV1`
- Runbook present: `False`

### Command (EXECUTABLE)
```powershell
python -c "from a_oic.policy.decision import evaluate_incident; result=evaluate_incident(severity='SEV1', has_runbook=False); print(result)"
```

### Expected Output
```
PolicyResult(
  decision=Decision.REQUIRE_APPROVAL,
  reason='SEV1 incident without verified runbook'
)
```

### Why this exists
SEV1 + no SOP is **high-risk**.
System must **fail closed** and require HITL.

---

# MANUAL TEST 2 — Policy Gate (SEV3, With Runbook)

### Command
```powershell
python -c "from a_oic.policy.decision import evaluate_incident; result=evaluate_incident(severity='SEV3', has_runbook=True); print(result)"
```

### Expected Output
```
PolicyResult(
  decision=Decision.ALLOW,
  reason='Low risk incident'
)
```

### Why
Low-risk + SOP → safe automation.

---

# MANUAL TEST 3 — AI Plan Validation (Missing Actions)

### What this validates
AI **cannot** omit required structure.

### Input
```python
bad_plan = {
  "summary": "Restart service"
}
```

### Command
```powershell
python -c "from a_oic.adapters.ai_plan_validator import validate_ai_plan; from a_oic.adapters.ai_adapter import AIPlanRejected; 
try: validate_ai_plan({'summary':'Restart service'})
except AIPlanRejected as e: print('REJECTED:', e)"
```

### Expected Output
```
REJECTED: AI plan schema violation: 'actions' is a required property
```

### Why
AI must produce **explicit executable intent**.
Vague plans are rejected.

---

# MANUAL TEST 4 — AI Plan Validation (Illegal Action)

### Input
```python
bad_plan = {
  "summary": "Do something risky",
  "actions": [{"type": "self_destruct", "target": "prod-db"}]
}
```

### Command
```powershell
python -c "from a_oic.adapters.ai_plan_validator import validate_ai_plan; from a_oic.adapters.ai_adapter import AIPlanRejected;
try: validate_ai_plan({'summary':'Do something risky','actions':[{'type':'self_destruct','target':'prod-db'}]})
except AIPlanRejected as e: print('REJECTED:', e)"
```

### Expected Output
```
REJECTED: AI plan schema violation: 'self_destruct' is not one of ...
```

### Why
AI **cannot invent new verbs**.
Only whitelisted actions are allowed.

---

# MANUAL TEST 5 — AI Plan Validation (VALID → ACCEPT)

### Input
```python
{
  "summary": "Restart service safely",
  "actions": [{"type": "restart", "target": "payments-api"}]
}
```

### Command
```powershell
python -c "from a_oic.adapters.ai_plan_validator import validate_ai_plan;
plan={'summary':'Restart service safely','actions':[{'type':'restart','target':'payments-api'}]};
print(validate_ai_plan(plan))"
```

### Expected Output
```
{'summary': 'Restart service safely', 'actions': [{'type': 'restart', 'target': 'payments-api'}]}
```

### Why

- **Confirms AI output can pass when bounded**
- **Demonstrates AI suggestion ≠ execution**
- **Reinforces that policy & orchestration decide next**

---

# MANUAL TEST 6 — End-to-End Execution (ALLOW → EXECUTED)

### What this validates
The **full execution spine** works end-to-end:

Policy decision → validated AI plan → orchestrate execution → audit record

No AI authority. No shortcuts.

---

### Input
```python
incident_id = "INC-DEMO-001"
policy_decision = "ALLOW"
policy_reason = "Low risk incident"

plan = {
  "summary": "Restart service safely",
  "actions": [{"type": "restart", "target": "payments-api"}]
}

```

### Command
```powershell
python -c "from a_oic.adapters.ai_plan_validator import validate_ai_plan; from a_oic.orchestrate.executor import LocalOrchestrateStub, execute_plan; plan=validate_ai_plan({'summary':'Restart service safely','actions':[{'type':'restart','target':'payments-api'}]}); out=execute_plan(incident_id='INC-DEMO-001',policy_decision='ALLOW',policy_reason='Low risk incident',validated_plan=plan,orchestrate=LocalOrchestrateStub()); print(out.record.to_dict()); print(out.orchestrate)"
```


### Expected Output
```
{
  'incident_id': 'INC-DEMO-001',
  'decision': 'ALLOW',
  'actions': [{'type': 'restart', 'target': 'payments-api'}],
  'status': ExecutionStatus.EXECUTED,
  'created_at_utc': '...',
  'reason': 'Low risk incident'
}
OrchestrateResult(ok=True, detail='Executed 1 action(s) for INC-DEMO-001')
```

### Why

- **Confirms execution only happens after policy `ALLOW`**
- **Proves orchestration is a replaceable boundary (stub ↔ real engine)**
- **Demonstrates auditable, replayable execution state**
- **Shows the kernel remains deterministic even with orchestration present**

---


---
# MANUAL TEST 7 — Orchestrate Adapter Selection (Feature Flag)

### What this validates

- **Orchestration is a `replaceable boundary`**
- **Kernel logic does not change when execution backend changes**
- **Feature flags select runtime behavior, not code paths**

---
### Preconditions
```powershell
$env:USE_REAL_ORCHESTRATE="true"
```

### Input
```python
incident_id = "INC-ORCH-001"
policy_decision = "ALLOW"
policy_reason = "Low risk incident"

plan = {
  "summary": "Restart service safely",
  "actions": [{"type": "restart", "target": "payments-api"}]
}
```

### Command
```powershell
python -c "from a_oic.adapters.ai_plan_validator import validate_ai_plan; \
from a_oic.orchestrate.executor import execute_plan; \
plan=validate_ai_plan({'summary':'Restart service safely','actions':[{'type':'restart','target':'payments-api'}]}); \
out=execute_plan(incident_id='INC-ORCH-001',policy_decision='ALLOW',policy_reason='Low risk incident',validated_plan=plan,orchestrate=None); \
print(out.record.to_dict()); print(out.orchestrate)"
```


### Expected Output
```
{
  'incident_id': 'INC-ORCH-001',
  'decision': 'ALLOW',
  'actions': [{'type': 'restart', 'target': 'payments-api'}],
  'status': ExecutionStatus.EXECUTED,
  'created_at_utc': '...',
  'reason': 'Low risk incident'
}
OrchestrateResult(ok=True, detail='watsonx orchestrate executed restart for INC-ORCH-001')
```

### Why

- **Confirms adapter selection via environment, not code**
- **Proves IBM execution can be wired without touching kernel**
- **Demonstrates enterprise-safe swap (stub → real engine)**
- **Guarantees policy + audit stay deterministic**

---

## Relationship to Automated Tests

| Automated Test File | Covered Manual Tests |
|---------------------|----------------------|
| `test_policy_gate.py` | Manual Tests 1 & 2 |
| `test_ai_plan_validation.py` | Manual Tests 3 & 4 |
| `test_ai_plan_acceptance.py` | Manual Test 5 |
| `test_end_to_end_execution.py` | Manual Test 6 |
| `test_orchestrate_adapter_switch.py` | Manual Test 7 |


Automated tests **prove enforcement**.
Manual tests **prove understanding**.

---

## Final Governance Statement

- Manual tests are executable
- Manual tests are reproducible
- Manual tests never bypass policy
- Manual tests never replace automation

This ensures:
- Humans understand the system
- AI never gains authority
- Reviewers can replay behavior

---
_Last updated: 31/01/2026_

