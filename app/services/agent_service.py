from __future__ import annotations

import os
from typing import Optional

from ..agents.agent import create_agent
from ..llm.factory import get_llm_provider


class AgentService:
    def __init__(self) -> None:
        # shared agent instance
        self._agent = create_agent()
        # lazily created provider; respects LLM_PROVIDER env var
        self._llm_provider = None

    def _get_provider(self):
        if self._llm_provider is None:
            provider_name = os.getenv("LLM_PROVIDER", None)
            self._llm_provider = get_llm_provider(provider_name)
        return self._llm_provider

    def run(self, input_text: str, session_id: Optional[str] = None) -> str:
        # if agent configured as 'local', run local logic
        if getattr(self._agent, "provider", "local") == "local":
            return self._agent.run(input_text)

        # otherwise delegate to configured LLM provider
        provider = self._get_provider()
        resp = provider.generate(input_text)
        return resp.content


_agent_service = AgentService()


def get_agent_service() -> AgentService:
    return _agent_service
