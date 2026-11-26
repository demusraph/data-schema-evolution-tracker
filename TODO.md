# TODO.md: SchemaEvolutionTracker Roadmap

## Phase 1: Architecture Scaffolding & Foundation
- [ ] Initialize repository structure with `src/`, `tests/`, `docs/`, and `scripts/`.
- [ ] Configure `pyproject.toml` with Poetry/Rye, enforcing Python 3.11+ and strict `mypy` settings.
- [ ] Implement base abstract classes for `SchemaAdapter` (SQLAlchemy, Django, Raw SQL).
- [ ] Define core Pydantic models for `SchemaSnapshot`, `EvolutionDelta`, and `MigrationPlan`.
- [ ] Setup CI/CD pipeline (GitHub Actions) for linting (Ruff), type checking (Mypy), and security scanning (Bandit).
- [ ] Establish logging infrastructure using `structlog` for structured observability.

**DoD:** Repository passes all linting/type-check gates; base interfaces defined with 100% type coverage.

## Phase 2: Core Domain Logic & Engine Implementation
- [ ] Develop the `SnapshotEngine` to capture current database state into serialized JSON/YAML.
- [ ] Implement the `DiffEngine` to compute structural differences between two `SchemaSnapshot` objects.
- [ ] Create the `EvolutionPlanner` to generate idempotent migration scripts based on detected deltas.
- [ ] Implement the `VersionRegistry` to track historical schema states in a dedicated metadata table.
- [ ] Build the `ConflictResolver` to handle non-additive changes (e.g., column drops, type changes) with user-defined strategies.

**DoD:** Engine successfully detects schema drift and generates valid SQL for additive changes; 80%+ unit test coverage.

## Phase 3: Automated Stress Testing & Verification (DoD Gates)
- [ ] Develop `TestContainer` factory using `testcontainers-python` to spin up ephemeral Postgres/MySQL/SQLite instances.
- [ ] Create a suite of "destructive" tests (e.g., renaming tables, changing constraints, circular dependencies).
- [ ] Implement property-based testing using `Hypothesis` to generate edge-case schema mutations.
- [ ] Establish performance benchmarks for large-scale schema snapshots (>10k tables).
- [ ] Define "DoD Gates":
    - [ ] Zero regression on existing schema migration logic.
    - [ ] 100% pass rate on integration tests across all supported DB backends.
    - [ ] No critical/high vulnerabilities detected by `safety` or `snyk`.

**DoD:** All stress tests pass; benchmarks documented; CI/CD gate enforced for 90% branch coverage.

## Phase 4: Packaging, Documentation & README
- [ ] Author `ARCHITECTURE.md` detailing the internal dependency graph and state machine logic.
- [ ] Generate API documentation using `mkdocs-material` and `mkdocstrings`.
- [ ] Create a `CONTRIBUTING.md` guide for local development and PR submission standards.
- [ ] Finalize `README.md` with "Quick Start" code snippets and architectural diagrams.
- [ ] Configure `pyproject.toml` for PyPI distribution (metadata, classifiers, entry points).

**DoD:** Documentation is auto-generated and hosted; README contains functional "Hello World" example.

## Phase 5: Release & Production Readiness
- [ ] Implement semantic versioning (SemVer) automation via `python-semantic-release`.
- [ ] Create a `CHANGELOG.md` template and automated generation script.
- [ ] Perform security audit of the `EvolutionPlanner` to prevent SQL injection in generated scripts.
- [ ] Publish initial release candidate (RC) to TestPyPI.
- [ ] Finalize production release to PyPI and tag repository.

**DoD:** Successful deployment to PyPI; verified installation via `pip install schema-evolution-tracker`; stable release tag created.