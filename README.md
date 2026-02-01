# A-OIC — Autonomous Operations Incident Controller (Kernel)

## What this repository is

A-OIC is an enterprise-grade incident control kernel that proves one core idea:

AI can assist operations without ever becoming the authority.

This repository contains the deterministic core, contracts, policy gates, and
executable validation needed to safely integrate AI into production operations.

---

## What this repo IS

- A production-ready kernel for incident decision control
- Deterministic, testable, fail-closed
- Contract-first AI governance
- Designed to plug into IBM watsonx.ai, watsonx Orchestrate, and watsonx.data
- Fully validated with automated tests and executable manual tests

## What this repo is NOT

- A UI
- A notebook demo
- A system where AI decides or executes
- A vendor-locked runtime (adapters are swappable)

---

## Core principle

Authority is layered, not delegated.

Layer breakdown:
- Contracts: define what AI may say
- Policy gate: decide ALLOW / DENY / REQUIRE_APPROVAL
- AI reasoning: propose plans only (bounded)
- Execution: deterministic, non-AI
- Audit: record everything

AI may propose, but never decide or execute.

---

## Repository structure (current)

src/a_oic/
- adapters/        AI and validation boundaries
- contracts/       JSON schemas and version registry
- policy/          Deterministic policy gate
- orchestrate/     Execution boundary (stub and IBM adapter)
- state/           Execution records (audit-ready)
- tests/           Automated enforcement tests

docs/
- manual_tests.md  Executable, human-readable tests

---

## How to understand the system

### Automated tests (enforcement)

Run:
pytest -q

Expected output:
.......... [100%]

This is intentional:
- Pytest output is minimal by design
- These tests enforce invariants
- They are not meant to explain behavior

Automated tests answer:
Did the system violate a rule?

---

### Manual tests (human understanding)

Read and execute:
docs/manual_tests.md

Manual tests:
- Are copy-paste runnable
- Show inputs and expected outputs
- Demonstrate why behavior exists
- Prove determinism, not just correctness

Manual tests answer:
What actually happens, and why?

---

## What is validated

- Policy decisions (SEV1, SEV3)
- AI output schema validation
- Contract versioning and fail-closed behavior
- Execution gating
- Adapter swapping
- End-to-end execution flow

---

## IBM tool alignment

This kernel is IBM-tool-ready by design.

Intended runtime wiring:
- watsonx.ai: reasoning model (Granite)
- watsonx Orchestrate: execution and HITL
- watsonx.data: audit, replay, postmortem

In this repo:
- IBM tools are abstracted behind adapters
- Kernel logic remains portable and testable
- Runtime wiring happens outside the core

This is enterprise-correct, not a shortcut.

---

## Status

- All automated tests passing
- Manual tests validated
- Kernel complete
- Ready for IBM runtime wiring after hackathon

---

Last updated: 01/02/2026
