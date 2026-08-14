from __future__ import annotations

from typing import Any

from .errors import ToolNotFoundError


class ToolRegistry:
    """Stores and retrieves tool definitions."""

    def __init__(self):
        self._tools: dict[str, Any] = {}

    def register(self, tool: Any) -> None:
        name = getattr(tool, "name", None)
        if not name:
            raise ValueError("Tool must have a name.")
        if self.has(name):
            raise ValueError(f"Tool '{name}' is already registered.")
        self._tools[name] = tool

    def unregister(self, tool_name: str) -> None:
        if not self.has(tool_name):
            raise ToolNotFoundError(f"Tool '{tool_name}' is not registered.")
        del self._tools[tool_name]

    def get(self, tool_name: str) -> Any:
        tool = self._tools.get(tool_name)
        if tool is None:
            raise ToolNotFoundError(f"Tool '{tool_name}' is not registered.")
        return tool

    def has(self, tool_name: str) -> bool:
        return tool_name in self._tools

    def list_tools(self) -> list[Any]:
        return list(self._tools.values())

    def get_available_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema.to_dict() if hasattr(tool.input_schema, "to_dict") else tool.input_schema,
            }
            for tool in self._tools.values()
        ]
