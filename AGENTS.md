# AGENTS.md: SchemaEvolutionTracker Operational Protocol

## 1. Project Overview & Core Mission
**SchemaEvolutionTracker** is a high-performance, immutable audit-log system for relational database schema migrations. The mission is to provide a deterministic, version-controlled history of schema state transitions, ensuring zero-drift between application models and database DDL.

**Core Mission:** Maintain a strictly typed, append-only ledger of schema evolution events, enabling automated rollbacks and cross-environment schema synchronization.

---

## 2. Local PowerShell Commands
All automation must be executed via the project root. Agents must verify environment readiness before task execution.

*   **Setup:** `./scripts/init.ps1` (Installs venv, syncs dependencies via `uv`, configures pre-commit hooks).
*   **Test:** `pytest tests/ --cov=src --cov-report=term-missing` (Must maintain >95% coverage).
*   **Run:** `python -m src.main --config ./config/prod.yaml`
*   **Lint:** `ruff check . && mypy src/ --strict` (Zero-warning policy).
*   **Clean:** `Remove-Item -Recurse -Force .venv, .pytest_cache, .mypy_cache, dist`

---

## 3. Engineering Invariants
Failure to adhere to these invariants results in immediate task rejection.

*   **Zero-Placeholder Mandate:** Never commit `TODO`, `FIXME`, or `[Insert Logic Here]` blocks. If a module is incomplete, it must be stubbed with `raise NotImplementedError("Detailed rationale required")`.
*   **Typing Strictness:** Every function, method, and class attribute must be annotated. Use `from typing import Any, Dict, List, Optional, Union, Callable`. No `Any` usage allowed in production logic; use `TypeVar` or `Protocol` for generics.
*   **Line Endings:** Enforce `LF` (Line Feed) globally. Git configuration must be set to `core.autocrlf input`.
*   **Modularity:** Circular imports are strictly forbidden. Use dependency injection for all database adapters and external service clients.
*   **Immutability:** Prefer `dataclasses` with `frozen=True` for all schema state representations.

---

## 4. Self-Healing & Error Recovery Protocol
When an agent encounters a traceback or runtime failure, it must follow this recursive diagnostic loop:

1.  **Traceback Isolation:** Capture the full stack trace. Identify the entry point of the failure.
2.  **State Inspection:** Log the state of the `SchemaRegistry` and the current `MigrationNode` at the time of failure.
3.  **Hypothesis Generation:** Propose a fix based on the `ARCHITECTURE.md` design patterns.
4.  **Local Reproduction:** Create a minimal unit test in `tests/repro_issue_XXX.py` that triggers the exception.
5.  **Verification:** The fix is only valid if `pytest` passes the new reproduction test AND all existing regression tests.
6.  **Cleanup:** Delete the reproduction test file before submitting the PR.

---

## 5. Definition of Done (DoD) Quality Gate
A task is only "Done" when the following criteria are met:

*   **Static Analysis:** `mypy --strict` returns 0 errors. `ruff` reports 0 violations.
*   **Test Coverage:** No decrease in total project coverage. New features must include unit tests covering edge cases (null inputs, database connection timeouts, malformed schema definitions).
*   **Documentation:** All public-facing functions/classes have Google-style docstrings.
*   **Performance:** Execution time for schema validation must remain under 50ms for a 100-node evolution graph.
*   **Atomic Commits:** Each commit represents a single logical change. No "fixup" commits in the final history.
*   **Schema Integrity:** The `MigrationNode` hash verification passes for all existing nodes in the ledger.