from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health_endpoint_returns_success() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_login_and_dashboard() -> None:
    token_response = client.post("/auth/token", json={"username": "admin", "password": "admin"})
    assert token_response.status_code == 200

    token = token_response.json()["access_token"]
    auth_header = {"Authorization": " ".join(("Bearer", token))}
    response = client.get("/dashboard/summary", headers=auth_header)
    assert response.status_code == 200
    assert "finance" in response.json()
