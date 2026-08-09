from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

from ..core.logging import get_logger
from ..tools.tools import Tool, build_default_tools

logger = get_logger(__name__)


@dataclass
class AgentMessage:
    role: str
    content: str


@dataclass
class Agent:
    name: str = "AI-Agent"
    tools: List[Tool] = field(default_factory=build_default_tools)
    memory: List[AgentMessage] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.provider = os.getenv("MODEL_PROVIDER", "local")
        self.model_name = os.getenv("MODEL_NAME", "fallback")

    def add_message(self, role: str, content: str) -> None:
        self.memory.append(AgentMessage(role=role, content=content))

    def run(self, user_input: str) -> str:
        self.add_message("user", user_input)
        logger.info(
            "run_request",
            extra={
                "provider": self.provider,
                "model_name": self.model_name,
                "user_input": user_input,
            },
        )

        if not user_input.strip():
            return "Please provide a task."

        # Business logic (local execution) only — provider routing
        # is handled by the application/service layer so this class
        # remains provider-agnostic.
        return self._run_local(user_input)

    def _run_local(self, user_input: str) -> str:
        logger.info("local_execution", extra={"user_input": user_input})
        lower = user_input.lower()

        if "time" in lower:
            tool = self._find_tool("get_current_time")
            return tool.func(user_input)

        if "calculate" in lower or any(ch in lower for ch in "+-/*0123456789"):
            tool = self._find_tool("calculator")
            return tool.func(user_input)

        if any(term in lower for term in ["python", "ai", "agent"]):
            tool = self._find_tool("knowledge_lookup")
            return tool.func(user_input)

        if len(user_input.split()) > 8:
            tool = self._find_tool("summarize_text")
            return tool.func(user_input)

        return (
            "I can help you with time, calculations, general knowledge, or text summarization. "
            "Try asking me something concrete."
        )

    def _run_remote(self, user_input: str) -> str:
        logger.info(
            "remote_execution",
            extra={"provider": self.provider, "model_name": self.model_name},
        )
        return (
            f"Remote model path is not implemented yet. "
            f"Using provider={self.provider} model={self.model_name}."
        )

    def _find_tool(self, name: str) -> Tool:
        logger.debug("find_tool", extra={"tool": name})
        for tool in self.tools:
            if tool.name == name:
                return tool
        raise ValueError(f"Tool {name} not found")


def create_agent() -> Agent:
    logger.info("create_agent", extra={"agent_name": "AI-Agent"})
    return Agent()
