import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import FastAPI

# The profile router is actually not included in main.py, so we should test it in isolation
from routes.profile import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_resolve_identity():
    # Write a test to test the /api/profile/resolve endpoint
    # The endpoint calls IdentityResolver.merge_profiles(gov_data, osint_data)

    gov_data = [
        {"identity": {"full_name": "JOHN DOE", "ci": "1234567"}}
    ]
    osint_data = [
        {"digital_footprint": [{"platform": "GitHub", "url": "https://github.com/johndoe"}]}
    ]

    with patch('routes.profile.IdentityResolver.merge_profiles') as mock_merge:
        mock_merge.return_value = {
            "identity": {"full_name": "JOHN DOE", "ci": "1234567"},
            "digital_footprint": [{"platform": "GitHub", "url": "https://github.com/johndoe"}],
            "risk_score": 10
        }

        response = client.post(
            "/api/profile/resolve",
            json={
                "gov_data": gov_data,
                "osint_data": osint_data
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["identity"]["full_name"] == "JOHN DOE"
        assert data["digital_footprint"][0]["platform"] == "GitHub"
        assert data["risk_score"] == 10

        mock_merge.assert_called_once_with(gov_data, osint_data)
