import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from routes.profile import router

app = FastAPI()
app.include_router(router)

# Set raise_server_exceptions=False so the client returns a 500 response instead of throwing
client = TestClient(app, raise_server_exceptions=False)

def test_get_profile():
    response = client.get("/api/profile/123")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "123"
    assert "full_name" in data
    assert data["status"] == "Active"

def test_summarize_profile_success():
    with patch('routes.profile.ai_processor.summarize_person', new_callable=AsyncMock) as mock_summarize:
        mock_summarize.return_value = "This is a comprehensive summary."

        response = client.post("/api/profile/123/summarize", json={"some_key": "some_value"})

        assert response.status_code == 200
        assert response.json() == {"summary": "This is a comprehensive summary."}
        mock_summarize.assert_called_once_with("123", {"some_key": "some_value"})

def test_summarize_profile_internal_error():
    with patch('routes.profile.ai_processor.summarize_person', new_callable=AsyncMock) as mock_summarize:
        mock_summarize.side_effect = Exception("Internal processing error")

        # TestClient should now return a 500
        response = client.post("/api/profile/456/summarize", json={"data": "test"})
        assert response.status_code == 500

def test_resolve_identity():
    with patch('routes.profile.IdentityResolver.merge_profiles') as mock_merge:
        mock_merge.return_value = {"status": "resolved"}

        response = client.post(
            "/api/profile/resolve",
            json={
                "gov_data": [{"source": "gov"}],
                "osint_data": [{"source": "osint"}]
            }
        )

        assert response.status_code == 200
        assert response.json() == {"status": "resolved"}
        mock_merge.assert_called_once_with([{"source": "gov"}], [{"source": "osint"}])
