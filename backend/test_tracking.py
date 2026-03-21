import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import sys
import os

# Ensure backend dir is in path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Mock monitor_target to avoid ImportError during test collection
import services.task_manager

class MockMonitorTarget:
    def delay(self, *args, **kwargs):
        pass

# Add the mock directly to the module before importing the router
setattr(services.task_manager, 'monitor_target', MockMonitorTarget())

from routes.tracking import router

# Create a minimal FastAPI app for testing
app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_get_watchlist():
    response = client.get("/api/tracking/list")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    # Verify the structure of the mock data
    assert "id" in data[0]
    assert "name" in data[0]
    assert "last_check" in data[0]
    assert "alerts" in data[0]

    assert data[0]["id"] == "1"
    assert data[0]["name"] == "SANTIAGO BALBUENA"

    assert data[1]["id"] == "2"
    assert data[1]["name"] == "OBJETIVO DELTA"
