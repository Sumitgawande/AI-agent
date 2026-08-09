from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol


@dataclass
class LLMResponse:
    content: str
    model: str | None = None
    usage: Dict[str, Any] | None = None
    finish_reason: str | None = None
    metadata: Dict[str, Any] | None = None


class LLMProvider(Protocol):
    """Lightweight provider interface tailored to this codebase.

    The implementation intentionally keeps a synchronous `generate` method
    to match the current synchronous agent flow; providers may perform
    async I/O internally if needed and expose a sync wrapper.
    """

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        ...
