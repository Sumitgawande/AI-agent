from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Callable, List

from .errors import ToolExecutionError, ToolValidationError
from .schema import ToolArgumentSchema


class Tool:
    name: str = ""
    description: str = ""
    input_schema: ToolArgumentSchema = ToolArgumentSchema()
    timeout_seconds: float = 30.0

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        input_schema: ToolArgumentSchema | None = None,
        executor: Callable[..., Any] | None = None,
        timeout_seconds: float | None = None,
        func: Callable[..., Any] | None = None,
    ) -> None:
        self.name = name or getattr(self, "name", "")
        self.description = description or getattr(self, "description", "")
        self.input_schema = input_schema or getattr(self, "input_schema", ToolArgumentSchema())
        self.executor = executor or getattr(self, "executor", None)
        self.timeout_seconds = timeout_seconds if timeout_seconds is not None else getattr(self, "timeout_seconds", 30.0)
        self.func = func or self.executor or getattr(self, "execute", None)

        if not self.name:
            raise ValueError("Tool name is required.")
        if not self.description:
            raise ValueError("Tool description is required.")
        if self.input_schema is None:
            self.input_schema = ToolArgumentSchema()
        if self.func is None and not hasattr(self, "execute"):
            raise TypeError("Tool must define an execute method or provide an executor callable.")

    async def execute_async(self, **kwargs: Any) -> Any:
        if self.executor is not None:
            result = self.executor(**kwargs)
            if hasattr(result, "__await__"):
                return await result
            return result

        execute_method = getattr(self, "execute", None)
        if execute_method is None:
            raise ToolExecutionError("Tool does not define an execute method.")

        result = execute_method(**kwargs)
        if hasattr(result, "__await__"):
            return await result
        return result

    def execute(self, **kwargs: Any) -> Any:
        raise NotImplementedError("Tool subclasses must implement execute().")


class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluate a simple arithmetic expression"
    input_schema = ToolArgumentSchema(parameters={"expression": {"type": "string", "required": True}})
    timeout_seconds = 10.0

    def execute(self, expression: str) -> float | int:
        expr = expression.strip()
        if expr.lower().startswith("calculate"):
            expr = expr[len("calculate") :].strip()
        expr = expr.replace("^", "**")
        expr = "".join(ch for ch in expr if ch.isdigit() or ch in "+-*/(). ,")
        if not expr:
            raise ToolValidationError("No valid calculation expression found.")
        return eval(expr, {"__builtins__": {}}, {"math": math})


class EchoTool(Tool):
    name = "echo"
    description = "Return the same message passed as input"
    input_schema = ToolArgumentSchema(parameters={"message": {"type": "string", "required": True}})
    timeout_seconds = 5.0

    def execute(self, message: str) -> str:
        return message


def get_current_time(_arg: str) -> str:
    return f"The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."


def calculator(arg: str) -> str:
    try:
        expr = arg.strip()
        if expr.lower().startswith("calculate"):
            expr = expr[len("calculate") :].strip()
        expr = expr.replace("^", "**")
        expr = "".join(ch for ch in expr if ch.isdigit() or ch in "+-*/(). ,")
        if not expr:
            return "Calculation failed: no expression found"
        result = eval(expr, {"__builtins__": {}}, {"math": math})
        return f"Result: {result}"
    except Exception as exc:
        return f"Calculation failed: {exc}"


def knowledge_lookup(arg: str) -> str:
    knowledge = {
        "python": "Python is a high-level, interpreted programming language used for automation, web apps, data science, and AI.",
        "ai": "AI is the field of building systems that can perceive, reason, and act intelligently.",
        "agent": "An agent is a system that can interpret tasks, use tools, and produce useful outputs with minimal human intervention.",
    }
    needle = arg.lower().strip()
    if needle in knowledge:
        return knowledge[needle]
    return "I can answer general questions about Python, AI, and agents."


def summarize_text(arg: str) -> str:
    sentences = [s.strip() for s in arg.split(".") if s.strip()]
    if not sentences:
        return "No text to summarize."
    summary = " ".join(sentences[:2])
    return f"Summary: {summary}"


def build_default_tools() -> List[Tool]:
    return [
        Tool(
            name="get_current_time",
            description="Return the current date and time",
            input_schema=ToolArgumentSchema(parameters={"arg": {"type": "string", "required": False, "default": ""}}),
            executor=get_current_time,
        ),
        Tool(
            name="calculator",
            description="Evaluate a simple arithmetic expression",
            input_schema=ToolArgumentSchema(parameters={"arg": {"type": "string", "required": True}}),
            executor=calculator,
        ),
        Tool(
            name="knowledge_lookup",
            description="Answer general questions about Python, AI, and agents",
            input_schema=ToolArgumentSchema(parameters={"arg": {"type": "string", "required": True}}),
            executor=knowledge_lookup,
        ),
        Tool(
            name="summarize_text",
            description="Create a short summary from a block of text",
            input_schema=ToolArgumentSchema(parameters={"arg": {"type": "string", "required": True}}),
            executor=summarize_text,
        ),
    ]
