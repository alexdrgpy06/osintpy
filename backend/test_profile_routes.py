from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch
from routes.profile import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

@patch("routes.profile.IdentityResolver.merge_profiles")
def test_resolve_identity_success(mock_merge_profiles):
    # Setup mock return value
    mock_merge_profiles.return_value = {
        "identity": {"full_name": "Test User", "ci": "1234567"},
        "risk_score": 50,
        "summary": "Mock summary"
    }

    # Request payload
    gov_data = [{"source": "TSJE", "ci": "1234567"}]
    osint_data = [{"source": "Facebook", "url": "https://fb.com/test"}]

    # Send request
    # Note: query parameters or body parameters?
    # According to FastAPI:
    # async def resolve_identity(gov_data: List[dict], osint_data: List[dict])
    # By default, since they are complex types (List[dict]), FastAPI expects them in the JSON body.
    # However, having two body parameters without a single Pydantic model can be tricky in FastAPI unless they are explicitly defined using Body().
    # Let's see how FastAPI expects it: as JSON like {"gov_data": [...], "osint_data": [...]}
    response = client.post(
        "/api/profile/resolve",
        json={"gov_data": gov_data, "osint_data": osint_data}
    )

    # Assertions
    assert response.status_code == 200
    assert response.json() == {
        "identity": {"full_name": "Test User", "ci": "1234567"},
        "risk_score": 50,
        "summary": "Mock summary"
    }

    # Ensure mock was called with correct arguments
    mock_merge_profiles.assert_called_once_with(gov_data, osint_data)

def test_resolve_identity_validation_error():
    # Sending invalid payload (e.g. dict instead of lists)
    response = client.post(
        "/api/profile/resolve",
        json={"gov_data": {"not": "a list"}, "osint_data": [{"valid": "list"}]}
    )

    assert response.status_code == 422 # Unprocessable Entity
