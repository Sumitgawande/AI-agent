import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app


def _make_failing_provider():
    class P:
        def generate(self, prompt: str, **kwargs):
            raise RuntimeError("provider failure")

    return P()


def test_chat_provider_failure(monkeypatch):
    # Patch the factory used by AgentService to return a failing provider
    import app.services.agent_service as svc

    monkeypatch.setattr(svc, "get_llm_provider", lambda name=None: _make_failing_provider())
    # ensure the service uses remote provider path instead of local agent logic
    svc._agent_service._agent.provider = "openai"

    client = TestClient(app)
    r = client.post("/api/v1/chat", json={"message": "Hello", "session_id": "s1"})
    assert r.status_code == 500
    # API raises an HTTPException with detail "AGENT_EXECUTION_FAILED"
    assert r.json().get("detail") == "AGENT_EXECUTION_FAILED"


def test_agent_run_provider_failure(monkeypatch):
    import app.services.agent_service as svc

    monkeypatch.setattr(svc, "get_llm_provider", lambda name=None: _make_failing_provider())
    svc._agent_service._agent.provider = "openai"

    client = TestClient(app)
    r = client.post("/api/v1/agents/default/run", json={"input": "Do something"})
    assert r.status_code == 500
    assert r.json().get("detail") == "AGENT_EXECUTION_FAILED"
