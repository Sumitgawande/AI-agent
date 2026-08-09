from __future__ import annotations

import os
from typing import Any

from .interface import LLMProvider


def get_llm_provider(name: str | None = None, **kwargs: Any) -> LLMProvider:
    """Return a concrete LLM provider by name.

    Uses `LLM_PROVIDER` environment variable when `name` is not provided.
    Supported: `openai`, `anthropic`, `local` (no-op).
    """
    provider_name = (name or os.getenv("LLM_PROVIDER", "local")).lower()

    if provider_name == "openai":
        from .providers.openai_provider import get_provider

        return get_provider(**kwargs)

    if provider_name == "anthropic":
        from .providers.anthropic_provider import get_provider

        return get_provider(**kwargs)

    # default: local stub provider that echoes
    class LocalProvider:
        def generate(self, prompt: str, **k: Any):
            return __import__("app.llm.interface", fromlist=["*"]).LLMResponse(
                content=f"[local] {prompt}", model=None, usage={}, finish_reason="stop", metadata={}
            )

    return LocalProvider()
