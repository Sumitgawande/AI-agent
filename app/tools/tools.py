from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List


@dataclass
class Tool:
    name: str
    description: str
    func: Callable[[str], str]


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
            func=get_current_time,
        ),
        Tool(
            name="calculator",
            description="Evaluate a simple arithmetic expression",
            func=calculator,
        ),
        Tool(
            name="knowledge_lookup",
            description="Answer general questions about Python, AI, and agents",
            func=knowledge_lookup,
        ),
        Tool(
            name="summarize_text",
            description="Create a short summary from a block of text",
            func=summarize_text,
        ),
    ]
