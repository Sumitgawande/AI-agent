import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app.tools.errors import ToolExecutionError, ToolNotFoundError, ToolValidationError
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry
from app.tools.schema import ToolArgumentSchema, create_schema_from_type
from app.tools.tools import CalculatorTool, EchoTool, Tool


class AddTool(Tool):
    name = "add"
    description = "Add two integers"
    input_schema = ToolArgumentSchema(
        parameters={
            "a": {"type": "integer", "required": True},
            "b": {"type": "integer", "required": True},
        }
    )

    async def execute(self, **kwargs):
        return kwargs["a"] + kwargs["b"]


def test_tool_definition_smoke():
    tool = Tool(name="echo", description="echo message", input_schema=ToolArgumentSchema(parameters={"message": {"type": "string", "required": True}}))
    assert tool.name == "echo"
    assert tool.description == "echo message"
    assert tool.input_schema is not None


def test_registry_register_and_lookup():
    registry = ToolRegistry()
    tool = EchoTool()
    registry.register(tool)

    assert registry.has("echo") is True
    assert registry.get("echo").name == "echo"
    assert len(registry.list_tools()) == 1

    with pytest.raises(ValueError):
        registry.register(EchoTool())

    with pytest.raises(ToolNotFoundError):
        registry.get("missing")


def test_tool_schema_validation():
    schema = ToolArgumentSchema(
        parameters={
            "message": {"type": "string", "required": True},
            "count": {"type": "integer", "required": False, "default": 1},
        }
    )

    valid = schema.validate({"message": "hello", "count": 2})
    assert valid["message"] == "hello"
    assert valid["count"] == 2

    with pytest.raises(ToolValidationError):
        schema.validate({})

    with pytest.raises(ToolValidationError):
        schema.validate({"message": 123})

    with pytest.raises(ToolValidationError):
        schema.validate({"message": "hello", "extra": True})


def test_tool_executor_success_and_validation_error():
    registry = ToolRegistry()
    registry.register(EchoTool())
    executor = ToolExecutor(registry)

    result = executor.execute("echo", {"message": "hello"})
    assert result.success is True
    assert result.output == "hello"

    with pytest.raises(ToolValidationError):
        executor.execute("echo", {})


def test_tool_executor_async_and_timeout():
    registry = ToolRegistry()
    registry.register(AddTool())
    executor = ToolExecutor(registry)

    result = asyncio.run(executor.execute_async("add", {"a": 2, "b": 3}))
    assert result.success is True
    assert result.output == 5

    async def delayed_tool(**kwargs):
        await asyncio.sleep(0.2)
        return "done"

    tool = Tool(name="slow", description="slow tool", input_schema=ToolArgumentSchema(parameters={}), executor=delayed_tool)
    registry.register(tool)
    result = asyncio.run(executor.execute_async("slow", {}, timeout_seconds=0.05))
    assert result.success is False
    assert result.error["code"] == "TOOL_TIMEOUT"


def test_tool_executor_retry_and_exhaustion():
    registry = ToolRegistry()

    attempts = {"count": 0}

    class FlakyTool(Tool):
        name = "flaky"
        description = "Flaky tool"
        input_schema = ToolArgumentSchema(parameters={})

        async def execute(self, **kwargs):
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise RuntimeError("transient")
            return "ok"

    registry.register(FlakyTool())
    executor = ToolExecutor(registry, retry_policy={"max_retries": 3, "retryable_errors": {"RuntimeError"}})

    result = asyncio.run(executor.execute_async("flaky", {}))
    assert result.success is True
    assert result.output == "ok"
    assert attempts["count"] == 3


def test_calculator_and_echo_sample_tools():
    calc = CalculatorTool()
    echo = EchoTool()

    assert calc.execute(expression="2 + 2") == 4
    assert echo.execute(message="hi") == "hi"


def test_schema_factory_supports_python_types():
    schema = create_schema_from_type({"expression": str, "count": int})
    validated = schema.validate({"expression": "1+1", "count": 2})
    assert validated["expression"] == "1+1"
    assert validated["count"] == 2

    with pytest.raises(ToolValidationError):
        schema.validate({"expression": "x", "count": "bad"})
