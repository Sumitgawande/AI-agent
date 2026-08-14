from __future__ import annotations


class ToolError(Exception):
    """Base error for all tool framework failures."""

    code = "TOOL_ERROR"

    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message, **({"details": self.details} if self.details else {})}


class ToolNotFoundError(ToolError):
    code = "TOOL_NOT_FOUND"


class ToolValidationError(ToolError):
    code = "TOOL_VALIDATION_ERROR"


class ToolExecutionError(ToolError):
    code = "TOOL_EXECUTION_ERROR"


class ToolTimeoutError(ToolError):
    code = "TOOL_TIMEOUT"


class ToolAuthorizationError(ToolError):
    code = "TOOL_AUTHORIZATION_ERROR"


class ToolRetryExhaustedError(ToolError):
    code = "TOOL_RETRY_EXHAUSTED"
