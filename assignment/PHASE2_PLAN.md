# Phase 2: Technical Foundation & API Implementation
**Deadline: 30 Minutes | Status: Planning**

---

## Executive Summary

Complete **Task Management API** with 3 technical skills + 1 working FastAPI application with full CRUD, SQLModel database, and pytest tests.

### Deliverables Checklist
- [ ] 3 Technical Skills (building-fastapi-apis, designing-with-sqlmodel, testing-with-pytest)
- [ ] Task Management API (working and tested)
- [ ] Project structure (all files ready to run)
- [ ] Demo video script (ready to record)

---

## Part 1: Technical Skills (3 Skills) - 8 Minutes

### Skill 1: **building-fastapi-apis**
**Trigger**: "Build FastAPI endpoints", "Create REST API"
**Value**: FastAPI best practices, error handling, validation, middleware

**Files to Create**:
- `assignment/.claude/skills/building-fastapi-apis/SKILL.md`
- `assignment/.claude/skills/building-fastapi-apis/scripts/verify.py`

**Content includes**:
- App structure (main.py, routes/, models/)
- Request/response validation
- Error handling patterns
- CORS, middleware setup
- Verification checks SKILL.md syntax + example endpoint structure

---

### Skill 2: **designing-with-sqlmodel**
**Trigger**: "Design database schema", "Create SQLModel"
**Value**: SQLModel patterns, relationship design, migrations, type safety

**Files to Create**:
- `assignment/.claude/skills/designing-with-sqlmodel/SKILL.md`
- `assignment/.claude/skills/designing-with-sqlmodel/scripts/verify.py`

**Content includes**:
- SQLModel models (declarative, type-safe)
- Relationships (one-to-many, many-to-many)
- Validation rules
- Database initialization
- Verification checks model structure + imports

---

### Skill 3: **testing-with-pytest**
**Trigger**: "Write pytest tests", "Test TDD approach"
**Value**: pytest fixtures, test organization, mocking, coverage

**Files to Create**:
- `assignment/.claude/skills/testing-with-pytest/SKILL.md`
- `assignment/.claude/skills/testing-with-pytest/scripts/verify.py`

**Content includes**:
- Pytest setup (conftest.py, fixtures)
- Test structure (arrange-act-assert)
- Mocking database calls
- Testing FastAPI endpoints
- Verification checks test discovery + syntax

---

## Part 2: Task Management API Project - 20 Minutes

### Project Structure
```
assignment/
├── .claude/
│   └── skills/              ← 5 total skills (2 existing + 3 new)
├── task_api/
│   ├── __init__.py
│   ├── main.py              ← FastAPI app
│   ├── models.py            ← SQLModel schemas
│   ├── database.py          ← SQLite setup
│   ├── routes/
│   │   └── tasks.py         ← CRUD endpoints
│   └── dependencies.py      ← Session dependency
├── tests/
│   ├── conftest.py          ← pytest fixtures
│   ├── test_models.py       ← Model tests
│   └── test_routes.py       ← Endpoint tests
├── requirements.txt         ← Dependencies
├── pytest.ini               ← Pytest config
└── README.md                ← Instructions
```

### API Endpoints (4 CRUD)

| Method | Endpoint | Action |
|--------|----------|--------|
| POST | `/tasks/` | Create task |
| GET | `/tasks/` | List all tasks |
| GET | `/tasks/{id}` | Get single task |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |

### Database Schema: Task

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Part 3: TDD Test Suite - 5 Minutes

### Test Files to Create

**tests/conftest.py** (Fixtures)
- Database session
- Test client
- Sample task data

**tests/test_models.py** (Model Tests)
- Task creation
- Field validation
- Default values

**tests/test_routes.py** (Endpoint Tests)
- POST /tasks/ → creates task
- GET /tasks/ → lists tasks
- GET /tasks/{id} → gets single task
- PUT /tasks/{id} → updates task
- DELETE /tasks/{id} → deletes task

---

## Time Breakdown (30 Minutes Total)

| Phase | Minutes | Tasks |
|-------|---------|-------|
| Skills Creation | 8 | Create 3 technical skills + verify |
| Project Setup | 5 | Create directory structure + requirements.txt |
| Database Models | 3 | SQLModel schemas + database.py |
| CRUD Endpoints | 6 | main.py + routes/tasks.py |
| Pytest Tests | 5 | conftest.py + test files |
| Final Verification | 3 | Run tests + verify API works |

---

## Files to Generate

### Core API Files
- [ ] `assignment/task_api/__init__.py`
- [ ] `assignment/task_api/main.py` (FastAPI app)
- [ ] `assignment/task_api/models.py` (SQLModel)
- [ ] `assignment/task_api/database.py` (SQLite + engine)
- [ ] `assignment/task_api/dependencies.py` (Session)
- [ ] `assignment/task_api/routes/tasks.py` (CRUD)
- [ ] `assignment/task_api/routes/__init__.py`

### Test Files
- [ ] `assignment/tests/__init__.py`
- [ ] `assignment/tests/conftest.py` (Fixtures)
- [ ] `assignment/tests/test_models.py`
- [ ] `assignment/tests/test_routes.py`

### Config & Dependencies
- [ ] `assignment/requirements.txt`
- [ ] `assignment/pytest.ini`
- [ ] `assignment/.gitignore`

### Skills
- [ ] `assignment/.claude/skills/building-fastapi-apis/SKILL.md`
- [ ] `assignment/.claude/skills/building-fastapi-apis/scripts/verify.py`
- [ ] `assignment/.claude/skills/designing-with-sqlmodel/SKILL.md`
- [ ] `assignment/.claude/skills/designing-with-sqlmodel/scripts/verify.py`
- [ ] `assignment/.claude/skills/testing-with-pytest/SKILL.md`
- [ ] `assignment/.claude/skills/testing-with-pytest/scripts/verify.py`

---

## Verification Checklist

After creation:
1. ✓ All 5 skills pass validation
2. ✓ `pip install -r requirements.txt` works
3. ✓ `pytest tests/ -v` shows 5+ passing tests
4. ✓ `python -m task_api.main` runs without errors
5. ✓ Can curl: `POST /tasks/`, `GET /tasks/`, `GET /tasks/{id}`, `PUT /tasks/{id}`, `DELETE /tasks/{id}`

---

## Next Steps (After This Plan Approved)

1. Create 3 technical skills immediately (parallel with API setup)
2. Build API project structure
3. Write database models
4. Build CRUD endpoints
5. Write pytest tests
6. Run final verification
7. Prepare for demo video

---

**Approval Needed**: Do you approve this plan? Any changes needed before we proceed?
