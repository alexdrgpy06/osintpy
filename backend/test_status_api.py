from fastapi.testclient import TestClient
from main import app, task_manager

client = TestClient(app)

def test_status_api():
    # Create a mock task
    target_data = {"alias": "testuser"}
    task_id = task_manager.create_task(target_data)

    # Call the API
    response = client.get(f"/api/search/status/{task_id}")

    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["pending", "running", "completed"]
    assert "id" in data
    assert data["id"] == task_id

def test_status_api_not_found():
    response = client.get("/api/search/status/nonexistent_task_id")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Task not found"
