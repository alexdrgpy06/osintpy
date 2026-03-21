from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import pytest
from main import app

client = TestClient(app)

@patch("main.SystemValidator.get_full_health", new_callable=AsyncMock)
@patch("main.task_manager.run_engine", new_callable=AsyncMock)
def test_search_endpoint(mock_run_engine, mock_get_full_health):
    mock_get_full_health.return_value = {"status": "ok"}

    payload = {
        "ci_ruc": "123456",
        "nombre": "Test User",
        "alias": "testuser",
        "email": "test@example.com",
        "telefono": "0981123456",
        "notas_adicionales": "Testing"
    }

    # We use TestClient from Starlette, which works sync
    response = client.post("/api/search", json=payload)

    assert response.status_code == 200
    assert "task_id" in response.json()
    task_id = response.json()["task_id"]
    assert isinstance(task_id, str)

    # Check that mocks were called
    mock_get_full_health.assert_called_once()
    # Mock for run_engine is an AsyncMock, so it is added to background tasks
    # We can assert that the background task was added by calling background_tasks.add_task
    # But for a basic API unit test, verifying the task_id is returned successfully is sufficient

def test_search_endpoint_missing_body():
    response = client.post("/api/search")
    assert response.status_code == 422 # Unprocessable Entity
