from __future__ import annotations

import os
from typing import Any

from ..interface import LLMProvider, LLMResponse


class OpenAIProvider:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("LLM_MODEL", "gpt-4-simulated")

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        # Minimal, pluggable implementation: try to use OPENAI_API_KEY if present
        # Real implementation would call openai SDK; here we keep a safe simulation.
        api_key = os.getenv("OPENAI_API_KEY")
        content = (
            f"[OpenAI simulated:{self.model}] Response to: {prompt}"
            if api_key
            else f"[OpenAI stub:{self.model}] No API key configured; echo: {prompt}"
        )
        return LLMResponse(content=content, model=self.model, usage={}, finish_reason="stop", metadata={})


def get_provider(**kwargs: Any) -> LLMProvider:
    return OpenAIProvider(**kwargs)
