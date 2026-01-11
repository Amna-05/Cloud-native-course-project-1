"""Test FastAPI endpoints."""
import pytest

def test_health_check(client):
    """Test GET /health"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# ==================== CREATE ====================
def test_create_task(client, sample_task):
    """Test POST /tasks/"""
    response = client.post("/tasks/", json=sample_task)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_task["title"]
    assert data["description"] == sample_task["description"]
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_task_missing_title(client):
    """Test POST /tasks/ with missing title"""
    response = client.post("/tasks/", json={"description": "No title"})
    assert response.status_code == 422  # Validation error

def test_create_task_empty_title(client):
    """Test POST /tasks/ with empty title"""
    response = client.post("/tasks/", json={"title": "", "description": "Empty"})
    assert response.status_code == 422

# ==================== READ (LIST) ====================
def test_list_tasks_empty(client):
    """Test GET /tasks/ with no tasks"""
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []

def test_list_tasks(client, sample_task, sample_task_completed):
    """Test GET /tasks/ with multiple tasks"""
    # Create tasks
    client.post("/tasks/", json=sample_task)
    client.post("/tasks/", json=sample_task_completed)

    # List all
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_list_tasks_with_skip_limit(client, sample_task):
    """Test GET /tasks/ with pagination"""
    # Create 5 tasks
    for i in range(5):
        client.post("/tasks/", json={
            "title": f"Task {i}",
            "description": f"Task {i} description",
            "completed": False
        })

    # Get first 2
    response = client.get("/tasks/?skip=0&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Get next 2
    response = client.get("/tasks/?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_list_tasks_filter_completed(client):
    """Test GET /tasks/ with completed filter"""
    # Create tasks
    client.post("/tasks/", json={"title": "Pending", "completed": False})
    client.post("/tasks/", json={"title": "Done", "completed": True})

    # Filter completed
    response = client.get("/tasks/?completed=true")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["completed"] is True

    # Filter pending
    response = client.get("/tasks/?completed=false")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["completed"] is False

# ==================== READ (SINGLE) ====================
def test_get_task(client, sample_task):
    """Test GET /tasks/{id}"""
    # Create task
    create_response = client.post("/tasks/", json=sample_task)
    task_id = create_response.json()["id"]

    # Get it
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == sample_task["title"]

def test_get_task_not_found(client):
    """Test GET /tasks/{id} with invalid ID"""
    response = client.get("/tasks/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

# ==================== UPDATE ====================
def test_update_task(client, sample_task):
    """Test PUT /tasks/{id}"""
    # Create task
    create_response = client.post("/tasks/", json=sample_task)
    task_id = create_response.json()["id"]

    # Update it
    update_data = {
        "title": "Updated Title",
        "description": "Updated description",
        "completed": True
    }
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"
    assert data["completed"] is True

def test_update_task_partial(client, sample_task):
    """Test PUT /tasks/{id} with partial update"""
    # Create task
    create_response = client.post("/tasks/", json=sample_task)
    task_id = create_response.json()["id"]

    # Partial update (only title)
    response = client.put(f"/tasks/{task_id}", json={"title": "New Title"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == sample_task["description"]

def test_update_task_not_found(client):
    """Test PUT /tasks/{id} with invalid ID"""
    response = client.put("/tasks/99999", json={"title": "Updated"})
    assert response.status_code == 404

# ==================== DELETE ====================
def test_delete_task(client, sample_task):
    """Test DELETE /tasks/{id}"""
    # Create task
    create_response = client.post("/tasks/", json=sample_task)
    task_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404

def test_delete_task_not_found(client):
    """Test DELETE /tasks/{id} with invalid ID"""
    response = client.delete("/tasks/99999")
    assert response.status_code == 404

# ==================== INTEGRATION ====================
def test_full_crud_workflow(client):
    """Test complete CRUD workflow"""
    # CREATE
    create_data = {"title": "New Task", "description": "Initial", "completed": False}
    create_response = client.post("/tasks/", json=create_data)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # READ
    read_response = client.get(f"/tasks/{task_id}")
    assert read_response.status_code == 200
    assert read_response.json()["title"] == "New Task"

    # UPDATE
    update_response = client.put(f"/tasks/{task_id}", json={"completed": True})
    assert update_response.status_code == 200
    assert update_response.json()["completed"] is True

    # DELETE
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204

    # VERIFY DELETE
    final_response = client.get(f"/tasks/{task_id}")
    assert final_response.status_code == 404
