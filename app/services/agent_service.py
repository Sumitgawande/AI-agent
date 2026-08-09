from __future__ import annotations

from typing import Optional

from ..agents.agent import create_agent


class AgentService:
    def __init__(self) -> None:
        # for now a single shared agent instance; later can be per-agent-id
        self._agent = create_agent()

    def run(self, input_text: str, session_id: Optional[str] = None) -> str:
        # This method isolates agent execution from HTTP layer
        return self._agent.run(input_text)


_agent_service = AgentService()


def get_agent_service() -> AgentService:
    return _agent_service
