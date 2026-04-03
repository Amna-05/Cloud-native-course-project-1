# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What this project is

A **Task Management REST API** used as the vehicle for a fully automated CI/CD pipeline. Every push to `main` lints, type-checks, tests, builds a Docker image, pushes to AWS ECR, and deploys to AWS ECS Fargate — automatically.

---

## Tech stack

| Layer | Technology |
|---|---|
| API framework | FastAPI 0.104 |
| ORM / validation | SQLModel 0.0.14 (SQLAlchemy 2.x + Pydantic 2.x) |
| DB — dev/test | SQLite in-memory |
| DB — production | Supabase (PostgreSQL, session pooler port 5432) |
| Linting | Ruff 0.4.4 |
| Type checking | mypy 1.8 |
| Testing | pytest 7.4 + httpx + pytest-cov |
| Container | Docker (python:3.12-slim) |
| CI/CD | GitHub Actions |
| Registry | AWS ECR (`task-api` repo, region `ap-south-1`) |
| Runtime | AWS ECS Fargate (`task-api-cluster` / `task-api-service`) |

---

## Repository layout

```
.github/workflows/ci.yml     ← full CI/CD pipeline
assignment/                  ← all application code
├── task_api/
│   ├── main.py              ← FastAPI app, lifespan, 6 routes
│   ├── models.py            ← SQLModel schemas: Task, TaskCreate, TaskUpdate, TaskRead
│   └── database.py          ← engine factory, URL normalisation, get_session
├── tests/
│   ├── conftest.py          ← function-scoped engine/session/client fixtures
│   ├── test_models.py       ← unit tests: validators, defaults, field constraints
│   └── test_routes.py       ← integration tests: HTTP → DB → response
├── dockerfile
├── mypy.ini
├── requirements.txt
└── pytest.ini
```

All commands are run from **`assignment/`**.

---

## Commands

```bash
source venv/bin/activate          # local only

# dev server
python -m uvicorn task_api.main:app --reload --port 8000

# lint + type-check
ruff check .
mypy task_api/

# tests with coverage
pytest tests/ -v --cov=task_api --cov-report=term-missing

# single test
pytest tests/test_routes.py::test_create_task_returns_201 -v

# build image locally
docker build -f dockerfile -t task-api .

# run container locally against Supabase
docker run -p 8000:8000 -e DATABASE_URL=postgresql://... task-api
```

---

## Architecture decisions worth knowing

**SQLModel schema split.** `Task` (table=True) is the DB model. `TaskCreate`, `TaskUpdate`, `TaskRead` are API schemas inheriting `TaskBase` — validators (title strip, whitespace rejection) are defined once and apply everywhere.

**Test isolation: function-scoped in-memory SQLite.** Every test gets a fresh `create_engine("sqlite:///:memory:")` with `StaticPool`. `get_session` is overridden via dependency injection. No rollback tricks, no external services — CI-safe.

**Supabase URL normalisation.** Supabase gives `postgres://` URLs; SQLAlchemy 2.x requires `postgresql://`. `database.py` rewrites this at startup. `pool_pre_ping=True` handles stale connections (Supabase drops idle after ~5 min).

**Use session pooler (port 5432), not transaction pooler (port 6543).** pgbouncer transaction mode conflicts with SQLAlchemy's prepared statement cache.

---

## CI/CD pipeline (`.github/workflows/ci.yml`)

```
push/PR to main or dev
  ├── lint (ruff)       ─┐
  ├── type-check (mypy) ─┼── parallel
  └── test (pytest)     ─┘
            │ all pass + push to main only
            ▼
      build & push image to ECR  (:sha + :latest)
            ▼
      deploy to ECS Fargate
      (download task-def → render new image → update service → wait for stability)
```

PRs only run lint + type-check + test. Build and deploy run on `main` push only.

---

## AWS infrastructure

| Resource | Name |
|---|---|
| Region | configured in GitHub variable `AWS_REGION` |
| ECR repository | configured in GitHub variable `ECR_REPOSITORY` |
| ECS cluster | configured in GitHub variable `ECS_CLUSTER` |
| ECS service | configured in GitHub variable `ECS_SERVICE` |
| Task definition | configured in GitHub variable `ECS_TASK_DEFINITION` |
| Container name | configured in GitHub variable `CONTAINER_NAME` |
| Task execution role | `ecsTaskExecutionRole` |
| Security group | `task-api-sg` (inbound TCP 8000 open) |
| CloudWatch log group | `/ecs/task-api` |

**First deploy gotcha:** ECS will fail to start tasks if ECR has no image yet. Push the image manually before the pipeline runs for the first time:
```bash
aws ecr get-login-password --region $AWS_REGION \
  | docker login --username AWS --password-stdin \
    $ECR_REGISTRY
docker build -f dockerfile -t task-api .
docker tag task-api:latest $ECR_REGISTRY/task-api:latest
docker push $ECR_REGISTRY/task-api:latest
```
(`ECR_REGISTRY` = `<account-id>.dkr.ecr.<region>.amazonaws.com` — get it from the ECR console.)

---

## GitHub Actions secrets & variables

**Secrets** (Settings → Secrets and variables → Actions → Secrets):

| Name | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | github-actions-deployer IAM access key |
| `AWS_SECRET_ACCESS_KEY` | github-actions-deployer IAM secret key |

**Variables** (same page → Variables tab):

| Name | Value |
|---|---|
| `AWS_REGION` | `ap-south-1` |
| `ECR_REPOSITORY` | `task-api` |
| `ECS_CLUSTER` | `task-api-cluster` |
| `ECS_SERVICE` | `task-api-service` |
| `ECS_TASK_DEFINITION` | `task-api-task` |
| `CONTAINER_NAME` | `task-api` |

`DATABASE_URL` is set inside the ECS task definition as a container environment variable — GitHub Actions never touches it.

---

## Coverage baseline

**95%** across 51 tests. Intentionally uncovered: PostgreSQL engine branch in `database.py` (production-only) and `if __name__ == "__main__"` guard. Minimum to maintain: **≥ 80%**.
