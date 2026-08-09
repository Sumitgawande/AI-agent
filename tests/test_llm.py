import os
import sys
from pathlib import Path


def test_provider_switching(monkeypatch):
    # ensure package imports work in tests
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    # default local
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    import app.llm.factory as fct

    p = fct.get_llm_provider()
    assert p.generate("hi").content.startswith("[local]")

    # openai (simulated)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    p = fct.get_llm_provider()
    assert "OpenAI" in p.generate("test").content or "OpenAI" in p.generate("test").content

    # anthropic (simulated)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    p = fct.get_llm_provider()
    assert "Anthropic" in p.generate("test").content or "Anthropic" in p.generate("test").content
