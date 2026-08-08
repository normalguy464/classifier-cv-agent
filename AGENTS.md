# AI Classifier Agent Repository Guide

## Purpose and Scope

This repository initially implements the Classifier Agent for an AI-assisted Vietnamese recruitment system. The architecture must preserve stable boundaries so Parser, Communication, and Scheduler agents can be added later without rewriting the Classifier Agent.

The Classifier Agent accepts versioned structured inputs, evaluates candidate-job fit through hybrid L1-L2-L3 scoring, returns a versioned structured result, and supports a human review decision. It must not parse source CV files, send email, or call calendar services.

This file is the repository-wide instruction source for contributors and coding agents. More specific nested `AGENTS.md` files may add constraints for a subtree, but they must not weaken the rules in this file.

## Current Delivery Boundary

The internship release includes:

- Versioned CV, job, rubric, configuration, evidence, and classification contracts.
- L1 deterministic rule scoring.
- L2 section-level semantic matching.
- L3 evidence-grounded LLM scoring with structured output validation.
- Score aggregation, confidence handling, quality gates, and `Needs Review` routing.
- Human approval and override with an audit record.
- Baselines, ablation experiments, metrics, stability checks, and error analysis.
- A FastAPI backend and a minimal Next.js demonstration interface.

The internship release excludes:

- PDF, DOCX, and OCR extraction.
- Email generation and delivery.
- Booking and calendar integration.
- Production-scale distributed task processing.
- Automated final hiring decisions.

## Technology Stack

### Backend and AI

- Python 3.12.
- `uv` for Python dependency and environment management.
- FastAPI for HTTP APIs.
- Pydantic v2 for input, output, configuration, and provider contracts.
- LangGraph for stateful classifier workflow orchestration.
- SQLAlchemy 2 and Alembic for persistence and migrations.
- PostgreSQL with pgvector as the system of record and vector store.
- Sentence Transformers behind an embedding adapter.
- An LLM provider abstraction with structured output validation.
- scikit-learn, pandas, NumPy, and plotting libraries for evaluation.

### Frontend

- A supported Node.js LTS release recorded in `.nvmrc` when the frontend is scaffolded.
- `pnpm` with a committed lockfile.
- Next.js App Router.
- TypeScript in strict mode.
- Tailwind CSS.

### Quality and Testing

- Ruff for Python linting and format verification.
- Pyright for Python static type checking.
- pytest and pytest-asyncio for Python tests.
- ESLint for TypeScript linting.
- Vitest and Testing Library for frontend unit and component tests.
- Playwright for browser-level end-to-end tests.

Exact dependency versions must be committed in lockfiles. Do not upgrade a major dependency or regenerate a lockfile unless the task explicitly requires it.

## Target Repository Structure

The repository should converge on this structure as implementation proceeds:

The canonical Classifier Agent package path is `backend/app/agents/classifier/`.

```text
Classifier_agent_code/
|-- AGENTS.md
|-- progress.md
|-- README.md
|-- .gitignore
|-- .env.example
|-- .nvmrc
|-- pyproject.toml
|-- uv.lock
|-- pnpm-lock.yaml
|-- docker-compose.yml
|-- configs/
|   |-- models.yaml
|   |-- scoring.yaml
|   `-- rubrics/
|-- data/
|   |-- samples/
|   |   |-- cvs/
|   |   `-- jobs/
|   |-- annotations/
|   |-- to_review/
|   |-- reviewed/
|   |-- frozen_test/
|   `-- README.md
|-- backend/
|   |-- __init__.py
|   |-- alembic.ini
|   |-- migrations/
|   `-- app/
|       |-- __init__.py
|       |-- main.py
|       |-- core/
|       |-- contracts/
|       |-- domain/
|       |-- agents/
|       |   `-- classifier/
|       |       |-- state.py
|       |       |-- graph.py
|       |       |-- routing.py
|       |       |-- nodes/
|       |       |-- scoring/
|       |       `-- prompts/
|       |-- workflows/
|       |   `-- recruitment/
|       |-- application/
|       |-- infrastructure/
|       `-- api/
|-- frontend/
|   |-- package.json
|   `-- src/
|       |-- app/
|       |-- components/
|       |-- hooks/
|       `-- lib/
|-- evaluation/
|   |-- baselines/
|   |-- experiments/
|   |-- metrics/
|   `-- reports/
|-- tests/
|   |-- unit/
|   |-- contract/
|   |-- integration/
|   |-- e2e/
|   `-- fixtures/
|-- scripts/
`-- docs/
```

Do not create empty placeholder modules or directories unless the active task needs them.

## Collaboration Workflow

Implementation follows eight stages with explicit handoff gates. Keep `progress.md` at the repository root current after every meaningful work session, user review, or gate transition. Do not advance a stage until its gate is satisfied.

### Stage 1: Requirements and Rubric

- The coding agent proposes job profiles, hard and preferred requirements, criteria, initial weights, and initial thresholds.
- The user reviews the business meaning and confirms the final rubric.
- Deliverables are versioned job profiles, rubric files, and scoring configuration.
- Gate 1 is complete when the user explicitly approves the rubric and requirements.

### Stage 2: Data Contracts

- The coding agent defines and validates `CVProfile`, `JobProfile`, `ScoringRubric`, `ClassificationConfig`, `Evidence`, and `ClassificationResult`.
- The user reviews representative examples for readability and missing fields.
- Gate 2 is complete when schema version 1 is approved and frozen for pilot work.

### Stage 3: Pilot Dataset

- The coding agent creates ten diverse synthetic CV profiles, annotation guidance, and an annotation tool or editable artifact.
- The user confirms labels, criterion scores, short rationales, and ambiguous cases.
- Gate 3 is complete when the pilot labels are reviewed and the rubric works without unresolved structural ambiguity.

### Stage 4: Parallel Core Development and Dataset Review

- The coding agent implements contracts, L1, baselines, L2, L3, aggregation, quality gates, workflow orchestration, tests, and the initial CLI or API.
- The user reviews and labels the remaining synthetic or approved anonymized dataset using the frozen rubric.
- Gate 4 is complete when the classifier core passes its checks and the reviewed dataset is ready for controlled evaluation.

### Stage 5: Classifier Review

- The coding agent runs the classifier, produces score breakdowns, disagreements, error cases, and `Needs Review` cases.
- The user inspects representative errors and uncertain cases to distinguish model errors, label errors, and rubric ambiguity.
- Gate 5 is complete when core behavior and corrected labels are confirmed.

### Stage 6: Validation Tuning and Configuration Freeze

- The coding agent evaluates candidate weights, thresholds, prompts, and models on validation data only.
- The user reviews the tradeoffs and approves the final configuration.
- Gate 6 is complete when rubric, weights, thresholds, prompts, embedding model, LLM model, and configuration versions are frozen.

### Stage 7: Frozen Test Evaluation

- The coding agent runs baselines, ablations, final metrics, stability checks, performance checks, and error analysis on frozen test data.
- The user validates the conclusions and selects representative examples for the report and defense.
- Gate 7 is complete when results are frozen and no further tuning is performed against test outcomes.

### Stage 8: Demonstration and Defense Preparation

- The coding agent completes the API, minimal dashboard, deterministic demo data, technical documentation, demo script, and defense rehearsal material.
- The user runs the demonstration, studies the implementation, verifies the report, and practices explaining decisions and limitations.
- Gate 8 is complete when the acceptance gate passes and the user can independently demonstrate and defend the system.

### Progress Tracking Rules

- `progress.md` is the single source of truth for the current stage, current gate, completed work, pending user actions, pending coding-agent actions, decisions, blockers, and next step.
- Update `progress.md` at the end of every meaningful session and before handing work to the other party.
- Record decisions with a date and enough context to avoid reopening settled choices without new evidence.
- Never record secrets, credentials, private CV content, or unnecessary personal data in `progress.md`.
- Keep `AGENTS.md` stable as the process definition. Store changing execution state only in `progress.md`.

### Artifact Explanation and Handoff

- Before creating a non-trivial file or group of files, explain the intended purpose, scope, and expected user-facing effect in a concise progress update.
- After creating a file, explain it to the user individually in the handoff: its path, purpose, whether it is source code, configuration, test, data, or documentation, its main inputs or consumers, and any user decision it requires.
- Explain changed files when their externally visible role changes or when the user asks for an explanation.
- Do not describe a file as implemented, validated, or production-ready beyond what was actually verified.

### Glossary Maintenance

- Treat `docs/thuat_ngu.md` as a cumulative reference for the user and update it during every stage when new English, technical, workflow, scoring, data, or evaluation terms are introduced.
- Add each new term with its original wording, a preferred Vietnamese explanation, its project-specific meaning, and the stage that introduced it when useful.
- Keeping the glossary current does not require translating source code, contract fields, commands, product names, or every English phrase in project documentation.
- Before a stage handoff, check that the terms the user must understand to review that stage are present in the glossary.

## Architecture Rules

### Contracts

- All agent boundaries use Pydantic models with an explicit `schema_version`.
- The primary classifier input consists of `CVProfile`, `JobProfile`, `ScoringRubric`, and `ClassificationConfig`.
- The primary classifier output is `ClassificationResult`.
- Downstream automation may consume only an HR-approved `ApprovedDecision`, never an unreviewed model prediction.
- Contracts must distinguish missing information from evidence that a requirement is not satisfied.
- Public contract changes require migration notes and contract tests.

### Classifier Boundaries

- The Classifier Agent must not read PDF, DOCX, image, or OCR input directly.
- The Classifier Agent must not send email, create booking links, or call calendar APIs.
- The Classifier Agent must not make an irreversible hiring decision.
- The Classifier Agent must not depend on frontend types.
- The Classifier Agent must not expose provider-specific response objects outside infrastructure adapters.
- Parser output must conform to `CVProfile`; the Classifier must not import Parser implementation code.
- Future Communication and Scheduler agents must consume approved contracts through the top-level recruitment workflow.

### Workflow and Scoring

- LangGraph nodes coordinate state transitions and delegate calculations to scoring services.
- Scoring modules must remain independent from LangGraph, FastAPI, database sessions, and provider clients.
- L1 is deterministic rule scoring against explicit rubric requirements.
- L2 performs section-level semantic matching and records the embedding model version.
- L3 uses evidence-grounded LLM reasoning and validates all output against a Pydantic schema.
- Aggregation weights, thresholds, prompt versions, model versions, and rubric versions must be supplied through configuration.
- Missing critical evidence, invalid provider output, large scoring disagreement, or boundary scores must route to `Needs Review` according to versioned policy.
- Persist workflow status and results through repository interfaces, not directly from pure scoring functions.

### Dependency Direction

- Domain and contract modules must not import FastAPI, SQLAlchemy, LangGraph, or concrete provider SDKs.
- Application use cases may depend on domain types and abstract ports.
- Infrastructure modules implement database, embedding, and LLM ports.
- API routes call application use cases and contain no scoring logic.
- Frontend code consumes API contracts and contains no backend scoring logic.

## Coding Conventions

### Comments and Docstrings

- Do not add inline comments or block comments in source code, tests, scripts, or configuration files.
- Do not leave commented-out code.
- Short docstrings are allowed only for public APIs, public contracts, and important abstractions.
- A docstring must describe the contract, invariant, or externally visible behavior. It must not restate the implementation.
- Express implementation intent through names, types, small functions, validated contracts, and tests.

### Icons and Decorative Symbols

- Do not add emoji, decorative Unicode symbols, icon libraries, icon components, or icon assets anywhere in backend or frontend code.
- Do not use icons in buttons, status indicators, navigation, alerts, empty states, charts, generated text, test fixtures, or documentation examples embedded in source files.
- Use concise text labels for every user interface action and status.

### Python

- Add type annotations to all function parameters, return values, class attributes, and public variables.
- Use absolute imports.
- Prefer immutable domain values and pure functions for calculations.
- Keep functions focused and names explicit.
- Use Pydantic models at external and agent boundaries.
- Use dependency injection for repositories, embedding adapters, LLM adapters, clocks, and identifiers.
- Raise typed application or domain exceptions and translate them at the API boundary.
- Do not use bare `except` clauses.
- Do not use mutable default arguments.
- Keep asynchronous code for I/O boundaries. Do not make CPU-only scoring asynchronous without a measured reason.

### TypeScript

- Enable strict TypeScript checking.
- Do not use `any`; use `unknown` and validate external data.
- Keep API access in the frontend library layer.
- Keep business scoring logic out of React components.
- Use accessible text labels and semantic HTML.
- Use Server Components by default and Client Components only when interaction requires them.

### Configuration and Secrets

- Do not hard-code secrets, credentials, provider model identifiers, thresholds, scoring weights, prompts, rate limits, or service URLs.
- Load runtime settings through typed configuration and environment variables.
- Commit `.env.example` with placeholder names only.
- Never commit `.env`, credentials, tokens, private keys, real CVs, or provider responses containing personal data.
- Prompts, rubrics, model selections, weights, and thresholds must be versioned and traceable in every classification run.

## Data and Evaluation Policy

- Use synthetic, consented, or irreversibly anonymized CV data only.
- Keep protected attributes such as age, gender, ethnicity, religion, marital status, disability, and hometown out of scoring inputs.
- If protected attributes are retained for approved audit work, store them separately with restricted access and never expose them to L1, L2, or L3 scoring.
- Human reviewers must confirm ground-truth labels. Model-generated labels alone are not valid ground truth.
- Record label rationale, rubric version, reviewer identity or pseudonymous identifier, and review status.
- Freeze test data before final tuning. Never choose prompts, models, weights, rules, or thresholds after viewing test outcomes.
- Use validation data for tuning and frozen test data only for final reporting.
- Report baseline and ablation results alongside the proposed hybrid method.
- Do not state expected performance as an achieved result.
- Preserve failed cases for reproducible error analysis without retaining unnecessary personal data.

## Target Commands

These commands are the target repository contract. They become mandatory when the referenced manifests and directories are scaffolded.

### Environment and Services

```powershell
uv sync --all-groups
pnpm --dir frontend install --frozen-lockfile
docker compose up -d postgres
docker compose down
```

### Database

```powershell
uv run alembic -c backend/alembic.ini upgrade head
uv run alembic -c backend/alembic.ini check
```

### Development

```powershell
uv run uvicorn backend.app.main:app --reload
pnpm --dir frontend dev
```

### Backend Quality

```powershell
uv run ruff check backend evaluation scripts tests
uv run ruff format --check backend evaluation scripts tests
uv run pyright backend evaluation scripts
uv run pytest -q
uv run pytest -q tests/unit
uv run pytest -q tests/contract
uv run pytest -q tests/integration
```

### Frontend Quality

```powershell
pnpm --dir frontend lint
pnpm --dir frontend test --run
pnpm --dir frontend build
pnpm --dir frontend test:e2e
```

### Evaluation

```powershell
uv run python -m evaluation.experiments.run_baselines
uv run python -m evaluation.experiments.run_ablation
uv run python -m evaluation.experiments.run_stability
uv run python -m evaluation.experiments.run_performance
```

Do not invent replacement commands when a declared command fails. Inspect the relevant manifest and correct either the implementation or this instruction file as part of the same authorized task.

## Testing Requirements

- Every code change must add or update automated tests in the same change. Cover normal behavior, invalid input, boundary values, and expected failure or fallback behavior relevant to the change.
- Tests for scoring, aggregation, metrics, and configuration validation must assert score bounds, weight totals, threshold boundaries, anomalous values, and version or cross-reference consistency where applicable.
- Run the relevant automated tests after each implementation change and report the exact command, result, and any test that could not run. Do not mark a code change complete when its required tests fail.
- For configuration, data, or documentation-only changes made before the project test stack is scaffolded, run the strongest available static validation and explicitly report any unavailable parser, linter, or test dependency.
- Every scoring rule requires unit tests for satisfied, unsatisfied, missing, malformed, and boundary inputs.
- Aggregation requires tests for weight validation, score bounds, threshold boundaries, and fallback behavior.
- Routing requires tests for completed, `Needs Review`, provider failure, invalid structured output, and human override paths.
- Embedding and LLM adapters require contract tests using deterministic fakes or recorded sanitized fixtures.
- API integration tests must cover validation, authorization, persistence, error mapping, and version fields.
- Database tests must cover migrations, repository behavior, and pgvector dimension compatibility.
- Frontend tests must cover score breakdown, evidence display, review actions, loading, empty, and error states using text-only controls.
- End-to-end tests must cover classify, inspect evidence, approve, override, and retrieve audit history.
- Evaluation code must have deterministic tests for metrics, data splits, baseline execution, and leakage prevention.

## Acceptance Gate

Before declaring a change complete:

1. Run the relevant backend and frontend lint, format-check, type-check, test, and build commands.
2. Run migration checks when persistence changes.
3. Run contract tests when schemas, prompts, models, or provider adapters change.
4. Confirm no secret, PII, real CV, protected scoring attribute, comment, emoji, icon dependency, icon component, or icon asset was added.
5. Confirm all public contract and configuration versions are recorded where required.
6. Confirm new behavior has tests and failure paths are explicit.
7. Update architecture, data contract, scoring, evaluation, or demo documentation when externally visible behavior changes.
8. Report the commands executed, their results, and any check that could not be run.

Do not claim completion while a required check is failing. Do not silently weaken tests, quality rules, data safeguards, or human review requirements to make a check pass.
