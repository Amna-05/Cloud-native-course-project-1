"""Integration tests for Task API endpoints.

Each test uses the `client` fixture from conftest.py, which provides a
TestClient backed by a fresh in-memory SQLite database. Every test is
fully independent — no shared state.
"""


# ==================== HEALTH ====================


def test_health_check_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_response_body(client):
    data = client.get("/health").json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


# ==================== CREATE ====================


def test_create_task_returns_201(client):
    response = client.post("/tasks/", json={"title": "Buy groceries"})
    assert response.status_code == 201


def test_create_task_response_contains_expected_fields(client):
    response = client.post("/tasks/", json={"title": "Test", "description": "Desc"})
    data = response.json()
    assert data["title"] == "Test"
    assert data["description"] == "Desc"
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks/", json={"description": "No title here"})
    assert response.status_code == 422


def test_create_task_empty_title_returns_422(client):
    response = client.post("/tasks/", json={"title": ""})
    assert response.status_code == 422


def test_create_task_whitespace_title_returns_422(client):
    response = client.post("/tasks/", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_title_is_stripped(client):
    response = client.post("/tasks/", json={"title": "  Buy milk  "})
    assert response.json()["title"] == "Buy milk"


def test_create_task_completed_defaults_to_false(client):
    response = client.post("/tasks/", json={"title": "Task"})
    assert response.json()["completed"] is False


def test_create_task_can_be_created_as_completed(client):
    response = client.post("/tasks/", json={"title": "Done task", "completed": True})
    assert response.json()["completed"] is True


# ==================== LIST ====================


def test_list_tasks_empty_db_returns_empty_list(client):
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_returns_all_created_tasks(client):
    client.post("/tasks/", json={"title": "Task A"})
    client.post("/tasks/", json={"title": "Task B"})
    response = client.get("/tasks/")
    assert len(response.json()) == 2


def test_list_tasks_pagination_limit(client):
    for i in range(5):
        client.post("/tasks/", json={"title": f"Task {i}"})
    response = client.get("/tasks/?skip=0&limit=3")
    assert len(response.json()) == 3


def test_list_tasks_pagination_skip(client):
    for i in range(5):
        client.post("/tasks/", json={"title": f"Task {i}"})
    response = client.get("/tasks/?skip=4&limit=10")
    assert len(response.json()) == 1


def test_list_tasks_skip_beyond_total_returns_empty(client):
    client.post("/tasks/", json={"title": "Only task"})
    response = client.get("/tasks/?skip=100&limit=10")
    assert response.json() == []


def test_list_tasks_filter_completed_true(client):
    client.post("/tasks/", json={"title": "Pending", "completed": False})
    client.post("/tasks/", json={"title": "Done", "completed": True})
    tasks = client.get("/tasks/?completed=true").json()
    assert len(tasks) == 1
    assert tasks[0]["completed"] is True


def test_list_tasks_filter_completed_false(client):
    client.post("/tasks/", json={"title": "Pending", "completed": False})
    client.post("/tasks/", json={"title": "Done", "completed": True})
    tasks = client.get("/tasks/?completed=false").json()
    assert len(tasks) == 1
    assert tasks[0]["completed"] is False


def test_list_tasks_no_filter_returns_all(client):
    client.post("/tasks/", json={"title": "Pending", "completed": False})
    client.post("/tasks/", json={"title": "Done", "completed": True})
    assert len(client.get("/tasks/").json()) == 2


# ==================== GET SINGLE ====================


def test_get_task_returns_correct_task(client):
    task_id = client.post("/tasks/", json={"title": "Find me"}).json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "Find me"


def test_get_task_not_found_returns_404(client):
    response = client.get("/tasks/99999")
    assert response.status_code == 404


def test_get_task_not_found_detail_message(client):
    response = client.get("/tasks/99999")
    assert "not found" in response.json()["detail"].lower()


# ==================== UPDATE ====================


def test_update_task_returns_200(client):
    task_id = client.post("/tasks/", json={"title": "Old"}).json()["id"]
    response = client.put(f"/tasks/{task_id}", json={"title": "New"})
    assert response.status_code == 200


def test_update_task_full_update(client):
    task_id = client.post("/tasks/", json={"title": "Old", "description": "Old desc"}).json()["id"]
    response = client.put(f"/tasks/{task_id}", json={
        "title": "New", "description": "New desc", "completed": True
    })
    data = response.json()
    assert data["title"] == "New"
    assert data["description"] == "New desc"
    assert data["completed"] is True


def test_update_task_partial_preserves_other_fields(client):
    task_id = client.post("/tasks/", json={
        "title": "Original", "description": "Keep me", "completed": False
    }).json()["id"]
    response = client.put(f"/tasks/{task_id}", json={"title": "Changed"})
    data = response.json()
    assert data["title"] == "Changed"
    assert data["description"] == "Keep me"
    assert data["completed"] is False


def test_update_task_completed_only(client):
    task_id = client.post("/tasks/", json={"title": "Task"}).json()["id"]
    response = client.put(f"/tasks/{task_id}", json={"completed": True})
    assert response.json()["completed"] is True


def test_update_task_not_found_returns_404(client):
    response = client.put("/tasks/99999", json={"title": "X"})
    assert response.status_code == 404


# ==================== DELETE ====================


def test_delete_task_returns_204(client):
    task_id = client.post("/tasks/", json={"title": "Delete me"}).json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204


def test_delete_task_removes_task_from_db(client):
    task_id = client.post("/tasks/", json={"title": "Gone soon"}).json()["id"]
    client.delete(f"/tasks/{task_id}")
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_delete_task_not_found_returns_404(client):
    response = client.delete("/tasks/99999")
    assert response.status_code == 404


def test_delete_does_not_affect_other_tasks(client):
    id_a = client.post("/tasks/", json={"title": "Task A"}).json()["id"]
    id_b = client.post("/tasks/", json={"title": "Task B"}).json()["id"]
    client.delete(f"/tasks/{id_a}")
    assert client.get(f"/tasks/{id_b}").status_code == 200


# ==================== INTEGRATION WORKFLOW ====================


def test_full_crud_workflow(client):
    """End-to-end: create → read → update → delete → confirm gone."""
    # Create
    task_id = client.post("/tasks/", json={
        "title": "Workflow task", "description": "E2E test", "completed": False
    }).json()["id"]

    # Read
    assert client.get(f"/tasks/{task_id}").json()["title"] == "Workflow task"

    # Update
    assert client.put(f"/tasks/{task_id}", json={"completed": True}).json()["completed"] is True

    # List — should appear
    tasks = client.get("/tasks/").json()
    assert any(t["id"] == task_id for t in tasks)

    # Delete
    assert client.delete(f"/tasks/{task_id}").status_code == 204

    # Confirm gone
    assert client.get(f"/tasks/{task_id}").status_code == 404
