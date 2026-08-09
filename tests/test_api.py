from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_chat():
    payload = {"message": "Hello there", "session_id": "s1"}
    r = client.post("/api/v1/chat", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert data.get("session_id") == "s1"


def test_agent_run():
    payload = {"input": "Calculate 1 + 2"}
    r = client.post("/api/v1/agents/default/run", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "output" in data


def test_agent_run_bad_request():
    r = client.post("/api/v1/agents/default/run", json={})
    assert r.status_code == 400 or r.status_code == 422
