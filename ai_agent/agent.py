from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

from .tools import Tool, build_default_tools

load_dotenv()


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

        if not user_input.strip():
            return "Please provide a task."

        if self.provider == "local" or not os.getenv("OPENAI_API_KEY"):
            return self._run_local(user_input)

        return self._run_remote(user_input)

    def _run_local(self, user_input: str) -> str:
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
        return (
            f"Remote model path is not implemented yet. "
            f"Using provider={self.provider} model={self.model_name}."
        )

    def _find_tool(self, name: str) -> Tool:
        for tool in self.tools:
            if tool.name == name:
                return tool
        raise ValueError(f"Tool {name} not found")


def create_agent() -> Agent:
    return Agent()
