from __future__ import annotations

import asyncio
import inspect
import time
from dataclasses import dataclass, field
from typing import Any

from .errors import (
    ToolExecutionError,
    ToolNotFoundError,
    ToolRetryExhaustedError,
    ToolTimeoutError,
    ToolValidationError,
)
from .registry import ToolRegistry


@dataclass
class ToolResult:
    success: bool
    output: Any = None
    error: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0


class ToolExecutor:
    def __init__(self, registry: ToolRegistry, retry_policy: dict[str, Any] | None = None):
        self.registry = registry
        self.retry_policy = retry_policy or {"max_retries": 0, "retryable_errors": {"RuntimeError", "TimeoutError"}}

    def execute(self, tool_name: str, arguments: dict[str, Any], timeout_seconds: float | None = None) -> ToolResult:
        result = asyncio.run(self.execute_async(tool_name, arguments, timeout_seconds=timeout_seconds))
        if not result.success:
            code = (result.error or {}).get("code")
            if code == "TOOL_VALIDATION_ERROR":
                raise ToolValidationError((result.error or {}).get("message", "Tool validation failed."), details=(result.error or {}).get("details"))
            if code == "TOOL_NOT_FOUND":
                raise ToolNotFoundError((result.error or {}).get("message", "Tool not found."))
            if code == "TOOL_TIMEOUT":
                raise ToolTimeoutError((result.error or {}).get("message", "Tool execution timed out."))
            raise ToolExecutionError((result.error or {}).get("message", "Tool execution failed."), details=(result.error or {}).get("details"))
        return result

    async def execute_async(self, tool_name: str, arguments: dict[str, Any], timeout_seconds: float | None = None) -> ToolResult:
        start = time.perf_counter()
        try:
            tool = self.registry.get(tool_name)
        except ToolNotFoundError as exc:
            return ToolResult(
                success=False,
                error={"code": exc.code, "message": exc.message},
                metadata={"tool_name": tool_name},
                execution_time=time.perf_counter() - start,
            )

        if timeout_seconds is None:
            timeout_seconds = getattr(tool, "timeout_seconds", 30)

        try:
            validated = tool.input_schema.validate(arguments)
        except ToolValidationError as exc:
            return ToolResult(
                success=False,
                error={"code": exc.code, "message": exc.message, "details": exc.details},
                metadata={"tool_name": tool_name},
                execution_time=time.perf_counter() - start,
            )

        attempts = 0
        while True:
            try:
                result = await self._run_tool_with_timeout(tool, validated, timeout_seconds)
                return ToolResult(
                    success=True,
                    output=result,
                    metadata={"tool_name": tool_name, "attempts": attempts + 1},
                    execution_time=time.perf_counter() - start,
                )
            except ToolTimeoutError as exc:
                if attempts >= self.retry_policy.get("max_retries", 0):
                    return ToolResult(
                        success=False,
                        error={"code": exc.code, "message": exc.message},
                        metadata={"tool_name": tool_name, "attempts": attempts + 1},
                        execution_time=time.perf_counter() - start,
                    )
                attempts += 1
                continue
            except ToolExecutionError as exc:
                if self._is_retryable(exc):
                    if attempts >= self.retry_policy.get("max_retries", 0):
                        return ToolResult(
                            success=False,
                            error={"code": ToolRetryExhaustedError.code, "message": "Tool retry limit exhausted."},
                            metadata={"tool_name": tool_name, "attempts": attempts + 1},
                            execution_time=time.perf_counter() - start,
                        )
                    attempts += 1
                    continue
                return ToolResult(
                    success=False,
                    error={"code": exc.code, "message": exc.message, "details": exc.details},
                    metadata={"tool_name": tool_name, "attempts": attempts + 1},
                    execution_time=time.perf_counter() - start,
                )
            except Exception as exc:
                wrapped = ToolExecutionError("Tool execution failed.", details={"error": str(exc)})
                if self._is_retryable(exc):
                    if attempts >= self.retry_policy.get("max_retries", 0):
                        return ToolResult(
                            success=False,
                            error={"code": ToolRetryExhaustedError.code, "message": "Tool retry limit exhausted."},
                            metadata={"tool_name": tool_name, "attempts": attempts + 1},
                            execution_time=time.perf_counter() - start,
                        )
                    attempts += 1
                    continue
                return ToolResult(
                    success=False,
                    error={"code": wrapped.code, "message": wrapped.message, "details": wrapped.details},
                    metadata={"tool_name": tool_name, "attempts": attempts + 1},
                    execution_time=time.perf_counter() - start,
                )

    async def _run_tool_with_timeout(self, tool: Any, validated_arguments: dict[str, Any], timeout_seconds: float) -> Any:
        try:
            return await asyncio.wait_for(self._invoke_tool(tool, validated_arguments), timeout=timeout_seconds)
        except asyncio.TimeoutError as exc:
            raise ToolTimeoutError("Tool execution timed out.") from exc

    async def _invoke_tool(self, tool: Any, validated_arguments: dict[str, Any]) -> Any:
        if getattr(tool, "executor", None) is not None:
            result = tool.executor(**validated_arguments)
            if inspect.isawaitable(result):
                return await result
            return result

        executor = getattr(tool, "execute", None)
        if executor is None:
            raise ToolExecutionError("Tool does not define an execute method.")

        result = executor(**validated_arguments)
        if inspect.isawaitable(result):
            return await result
        return result

    def _is_retryable(self, exc: Exception) -> bool:
        retryable = self.retry_policy.get("retryable_errors", set())
        for retryable_error in retryable:
            if isinstance(exc, type(retryable_error)) or exc.__class__.__name__ == str(retryable_error):
                return True
        return False
