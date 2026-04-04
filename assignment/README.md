# Task Management API

A production-grade FastAPI CRUD application with a fully automated CI/CD pipeline — linting, type-checking, testing, Docker build, ECR push, and ECS Fargate deployment on every push to `main`.

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Project Structure](#project-structure)
3. [Local Development](#local-development)
4. [Running Tests](#running-tests)
5. [Docker](#docker)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [AWS Infrastructure](#aws-infrastructure)
8. [GitHub Configuration](#github-configuration)
9. [Database](#database)

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI 0.104 |
| ORM / Validation | SQLModel 0.0.14 (SQLAlchemy 2.x + Pydantic 2.x) |
| Database (dev/test) | SQLite in-memory |
| Database (production) | Supabase (PostgreSQL) |
| Linting | Ruff 0.4.4 |
| Type checking | mypy 1.8 |
| Testing | pytest 7.4 + httpx + pytest-cov |
| Container | Docker (python:3.12-slim) |
| CI/CD | GitHub Actions |
| Registry | AWS ECR |
| Runtime | AWS ECS Fargate |

---

## Project Structure

```
.github/workflows/ci.yml   ← full CI/CD pipeline definition
assignment/
├── task_api/
│   ├── main.py            ← FastAPI app, 6 CRUD endpoints
│   ├── models.py          ← SQLModel schemas (Task, TaskCreate, TaskUpdate, TaskRead)
│   └── database.py        ← engine factory, Supabase URL normalisation, get_session
├── tests/
│   ├── conftest.py        ← function-scoped fixtures (engine, session, client)
│   ├── test_models.py     ← unit tests: validators, field constraints, defaults
│   └── test_routes.py     ← integration tests: full HTTP → DB → response
├── dockerfile
├── mypy.ini
├── pytest.ini
└── requirements.txt
```

---

## Local Development

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run dev server (SQLite by default)
uvicorn task_api.main:app --reload --port 8000
```

API is available at `http://localhost:8000`
Swagger UI at `http://localhost:8000/docs`

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/tasks/` | Create task |
| GET | `/tasks/` | List tasks (pagination + filter by completed) |
| GET | `/tasks/{id}` | Get single task |
| PUT | `/tasks/{id}` | Update task (partial updates supported) |
| DELETE | `/tasks/{id}` | Delete task |

---

## Running Tests

```bash
# All tests with coverage report
pytest tests/ -v --cov=task_api --cov-report=term-missing

# Single test
pytest tests/test_routes.py::test_create_task_returns_201 -v

# Coverage threshold (CI enforces ≥ 80%)
pytest tests/ --cov=task_api --cov-fail-under=80
```

Tests use a fresh in-memory SQLite database per test — no external services needed. Coverage is currently **95%** across 51 tests.

---

## Docker

```bash
# Build
docker build -f dockerfile -t task-api .

# Run locally with SQLite
docker run -p 8000:8000 task-api

# Run with Supabase (production database)
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  task-api

# Verify
curl http://localhost:8000/health
```

---

## CI/CD Pipeline

The pipeline is defined in `.github/workflows/ci.yml` and runs automatically on every push.

```
push / PR to main or dev
  ├── Lint (ruff)        ─┐
  ├── Type check (mypy)  ─┼── run in parallel
  └── Test (pytest)      ─┘
            │
            │ all three pass + push to main only
            ▼
     Build Docker image → push to ECR (:sha + :latest)
            │
            ▼
     Render new ECS task definition with updated image
            │
            ▼
     Deploy to ECS Fargate → wait for service stability
```

- PRs only run lint + type-check + test — no deploy
- CD only triggers on direct push to `main`
- If any CI job fails, the build and deploy are blocked
- ECS performs a rolling deploy — new task starts before old one stops (zero downtime)

---

## AWS Infrastructure

All infrastructure was created via AWS CLI. Below is what exists and how to recreate it from scratch.

### Prerequisites

- AWS CLI installed and configured
- Docker installed
- An IAM user with programmatic access for deployments (see [GitHub Configuration](#github-configuration))

### Architecture

```
GitHub Actions
  → ECR (image registry)
       → ECS Fargate (container runtime)
            → Supabase (PostgreSQL database)
```

### Step-by-step Setup

#### 1. ECR — Create the image repository

```bash
aws ecr create-repository \
  --repository-name task-api \
  --image-tag-mutability MUTABLE \
  --image-scanning-configuration scanOnPush=true \
  --region $AWS_REGION
```

#### 2. IAM — ECS Task Execution Role

ECS needs this role to pull images from ECR and write logs to CloudWatch.

```bash
# Create role
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ecs-tasks.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach AWS managed policy
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

> **Gotcha:** If the role exists but tasks fail with `ECS was unable to assume the role`, the trust relationship is wrong. Fix it:
> ```bash
> aws iam update-assume-role-policy \
>   --role-name ecsTaskExecutionRole \
>   --policy-document '{
>     "Version": "2012-10-17",
>     "Statement": [{
>       "Effect": "Allow",
>       "Principal": {"Service": "ecs-tasks.amazonaws.com"},
>       "Action": "sts:AssumeRole"
>     }]
>   }'
> ```

#### 3. ECS — Create the cluster

```bash
aws ecs create-cluster \
  --cluster-name task-api-cluster \
  --capacity-providers FARGATE \
  --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 \
  --region $AWS_REGION
```

#### 4. CloudWatch — Create log group

Must exist before ECS starts the task.

```bash
aws logs create-log-group \
  --log-group-name /ecs/task-api \
  --region $AWS_REGION
```

#### 5. ECS — Register task definition

Replace `YOUR_ACCOUNT_ID`, `YOUR_REGION`, and `YOUR_SUPABASE_URL`:

```bash
aws ecs register-task-definition \
  --family task-api-task \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 256 \
  --memory 512 \
  --execution-role-arn arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskExecutionRole \
  --container-definitions "[
    {
      \"name\": \"task-api\",
      \"image\": \"YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/task-api:latest\",
      \"portMappings\": [{\"containerPort\": 8000, \"protocol\": \"tcp\"}],
      \"environment\": [{
        \"name\": \"DATABASE_URL\",
        \"value\": \"YOUR_SUPABASE_URL\"
      }],
      \"logConfiguration\": {
        \"logDriver\": \"awslogs\",
        \"options\": {
          \"awslogs-group\": \"/ecs/task-api\",
          \"awslogs-region\": \"YOUR_REGION\",
          \"awslogs-stream-prefix\": \"ecs\"
        }
      }
    }
  ]" \
  --region $AWS_REGION
```

> **Supabase URL:** Use the session pooler connection string (port 5432), not the transaction pooler (port 6543). Transaction mode conflicts with SQLAlchemy's prepared statement cache.

#### 6. EC2 — Create security group

```bash
VPC_ID=$(aws ec2 describe-vpcs \
  --filters "Name=is-default,Values=true" \
  --query 'Vpcs[0].VpcId' --output text \
  --region $AWS_REGION)

SG_ID=$(aws ec2 create-security-group \
  --group-name task-api-sg \
  --description "Allow inbound port 8000" \
  --vpc-id $VPC_ID \
  --query 'GroupId' --output text \
  --region $AWS_REGION)

aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp --port 8000 --cidr 0.0.0.0/0 \
  --region $AWS_REGION
```

#### 7. ECS — Create the service

```bash
SUBNET_IDS=$(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=$VPC_ID" "Name=default-for-az,Values=true" \
  --query 'Subnets[*].SubnetId' --output text \
  --region $AWS_REGION | tr '\t' ',')

aws ecs create-service \
  --cluster task-api-cluster \
  --service-name task-api-service \
  --task-definition task-api-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[${SUBNET_IDS}],
    securityGroups=[${SG_ID}],
    assignPublicIp=ENABLED
  }" \
  --region $AWS_REGION
```

### First deploy — push image manually before pipeline runs

ECS cannot start if ECR has no image. Push one manually before the first pipeline run:

```bash
ECR_REGISTRY="YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com"

aws ecr get-login-password --region $AWS_REGION \
  | docker login --username AWS --password-stdin $ECR_REGISTRY

docker build -f dockerfile -t task-api .
docker tag task-api:latest $ECR_REGISTRY/task-api:latest
docker push $ECR_REGISTRY/task-api:latest
```

### Verify the deployment

```bash
# Get public IP of the running task
TASK_ARN=$(aws ecs list-tasks \
  --cluster task-api-cluster \
  --query 'taskArns[0]' --output text \
  --region $AWS_REGION)

ENI_ID=$(aws ecs describe-tasks \
  --cluster task-api-cluster --tasks $TASK_ARN \
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
  --output text --region $AWS_REGION)

PUBLIC_IP=$(aws ec2 describe-network-interfaces \
  --network-interface-ids $ENI_ID \
  --query 'NetworkInterfaces[0].Association.PublicIp' \
  --output text --region $AWS_REGION)

curl http://$PUBLIC_IP:8000/health
```

### View logs

```bash
# List log streams
aws logs describe-log-streams \
  --log-group-name /ecs/task-api \
  --region $AWS_REGION \
  --query 'logStreams[*].logStreamName'

# Read a stream
aws logs get-log-events \
  --log-group-name /ecs/task-api \
  --log-stream-name "ecs/task-api/TASK_ID" \
  --region $AWS_REGION \
  --query 'events[*].message'
```

Or in the console: **CloudWatch → Log groups → /ecs/task-api**

---

## GitHub Configuration

### IAM user for GitHub Actions

Create a dedicated IAM user (`github-actions-deployer`) with programmatic access only — no console access. Attach a custom policy with least-privilege permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage",
        "ecr:BatchGetImage"
      ],
      "Resource": "arn:aws:ecr:REGION:ACCOUNT_ID:repository/task-api"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:DescribeTaskDefinition",
        "ecs:DescribeServices",
        "ecs:RegisterTaskDefinition",
        "ecs:UpdateService"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole"
    }
  ]
}
```

### Secrets (Settings → Secrets and variables → Actions → Secrets)

| Name | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | github-actions-deployer access key ID |
| `AWS_SECRET_ACCESS_KEY` | github-actions-deployer secret access key |

### Variables (same page → Variables tab)

| Name | Value |
|---|---|
| `AWS_REGION` | your AWS region |
| `ECR_REPOSITORY` | `task-api` |
| `ECS_CLUSTER` | `task-api-cluster` |
| `ECS_SERVICE` | `task-api-service` |
| `ECS_TASK_DEFINITION` | `task-api-task` |
| `CONTAINER_NAME` | `task-api` |

> `DATABASE_URL` is set inside the ECS task definition — GitHub Actions never handles it.

---

## Database

### Development / Testing
SQLite is used automatically with no configuration. The `tasks.db` file is git-ignored.

### Production (Supabase)
Set the `DATABASE_URL` environment variable in the ECS task definition:

```
postgresql://USER:PASSWORD@HOST:5432/DATABASE
```

The app handles:
- `postgres://` → `postgresql://` URL normalisation (SQLAlchemy 2.x requirement)
- `pool_pre_ping=True` to recover from idle connection drops (Supabase closes idle connections after ~5 minutes)
