from __future__ import annotations

import os
from typing import Any

from ..interface import LLMProvider, LLMResponse


class AnthropicProvider:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("LLM_MODEL", "claude-simulated")

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        # Simulated Anthropics response; real implementations would call SDK/API.
        api_key = os.getenv("ANTHROPIC_API_KEY")
        content = (
            f"[Anthropic simulated:{self.model}] Response to: {prompt}"
            if api_key
            else f"[Anthropic stub:{self.model}] No API key configured; echo: {prompt}"
        )
        return LLMResponse(content=content, model=self.model, usage={}, finish_reason="stop", metadata={})


def get_provider(**kwargs: Any) -> LLMProvider:
    return AnthropicProvider(**kwargs)
