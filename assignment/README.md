# Task Management API

A complete FastAPI CRUD application with SQLModel database and pytest test suite.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Create database and run server
python -m uvicorn task_api.main:app --reload --port 8000

# Visit Swagger UI
open http://localhost:8000/docs
```

## Project Structure

```
assignment/
├── task_api/                    # FastAPI application
│   ├── __init__.py
│   ├── main.py                  # FastAPI app + 5 CRUD endpoints
│   ├── models.py                # SQLModel schemas (Task)
│   └── database.py              # SQLite setup
│
├── tests/                       # Pytest test suite
│   ├── __init__.py
│   ├── conftest.py              # Fixtures (session, client, sample data)
│   └── test_routes.py           # 15+ endpoint tests
│
├── .claude/skills/              # 5 Agent Skills
│   ├── writing-linkedin-posts/
│   ├── writing-upwork-proposals/
│   ├── building-fastapi-apis/
│   ├── designing-with-sqlmodel/
│   └── testing-with-pytest/
│
├── requirements.txt             # Dependencies
├── pytest.ini                   # Pytest configuration
└── README.md                    # This file
```

## API Endpoints

### Health Check
- `GET /health` → Returns API status

### Tasks CRUD

| Method | Endpoint | Action |
|--------|----------|--------|
| POST | `/tasks/` | Create task |
| GET | `/tasks/` | List all tasks (with pagination & filtering) |
| GET | `/tasks/{id}` | Get single task |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |

## Database Schema

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str  # Required, indexed
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime  # Auto-set to now
    updated_at: datetime  # Auto-set to now
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_routes.py::test_create_task -v

# With coverage
pytest --cov=task_api tests/

# Watch mode (requires pytest-watch)
ptw tests/
```

## Test Coverage

- ✓ 15+ endpoint tests covering all CRUD operations
- ✓ Error handling (404, 422, etc.)
- ✓ Pagination & filtering
- ✓ Full CRUD workflow integration test

## Skills Included

### Non-Technical
1. **writing-linkedin-posts** - Craft TOFU/MOFU/BOFU posts
2. **writing-upwork-proposals** - Win freelance jobs

### Technical
3. **building-fastapi-apis** - FastAPI patterns & best practices
4. **designing-with-sqlmodel** - Database schema design
5. **testing-with-pytest** - TDD & pytest patterns

Each skill includes:
- SKILL.md with complete instructions
- references/ with deep-dive patterns
- scripts/verify.py for validation

## Next Steps

1. **Run the API**:
   ```bash
   python -m uvicorn task_api.main:app --reload
   ```

2. **Test in Swagger UI**:
   - Visit http://localhost:8000/docs
   - Try creating, reading, updating, deleting tasks

3. **Run Test Suite**:
   ```bash
   pytest tests/ -v
   ```

4. **Record Demo Video** (60-90 seconds):
   - Show API Swagger UI
   - Create a task
   - List tasks
   - Update a task
   - Delete a task
   - Show test results

## Technologies

- **Framework**: FastAPI
- **Database**: SQLModel + SQLite
- **Testing**: pytest
- **Validation**: Pydantic

## Environment Variables

```env
# Optional - defaults to SQLite
DATABASE_URL=sqlite:///tasks.db
```

## Troubleshooting

**ModuleNotFoundError**: Make sure you've installed dependencies:
```bash
pip install -r requirements.txt
```

**Database locked**: Delete `tasks.db` and restart:
```bash
rm tasks.db
python -m uvicorn task_api.main:app --reload
```

---

**Created**: 2026-01-11
**Status**: Complete ✓
**Demo Ready**: Yes ✓
