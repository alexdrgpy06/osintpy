import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
import sys
import unittest.mock as mock

# monitor_target doesn't exist in services.task_manager yet, so it MUST be mocked before importing routes.tracking
sys.modules['services.task_manager'] = mock.MagicMock()

from routes.tracking import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_add_to_watchlist_success():
    # Reset mock to ensure clean state
    sys.modules['services.task_manager'].monitor_target.delay.reset_mock()
    response = client.post(
        "/api/tracking/add",
        json={"target_id": "123", "query": "test query", "query_type": "email", "frequency_hours": 24}
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "tracking_active",
        "target_id": "123",
        "note": "Background tasks may be restricted without Redis"
    }
    sys.modules['services.task_manager'].monitor_target.delay.assert_called_once_with("123", "test query", "email")

def test_add_to_watchlist_celery_exception():
    sys.modules['services.task_manager'].monitor_target.delay.reset_mock()
    sys.modules['services.task_manager'].monitor_target.delay.side_effect = Exception("Celery not running")
    response = client.post(
        "/api/tracking/add",
        json={"target_id": "123", "query": "test query", "query_type": "email", "frequency_hours": 24}
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "tracking_active",
        "target_id": "123",
        "note": "Background tasks may be restricted without Redis"
    }
    sys.modules['services.task_manager'].monitor_target.delay.assert_called_once_with("123", "test query", "email")
