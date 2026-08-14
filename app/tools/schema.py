from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import BaseModel, ValidationError, create_model

from .errors import ToolValidationError


class ToolArgumentSchema:
    """Provider-neutral tool input schema.

    Provides a lightweight structure for describing tool parameters and validating
    incoming payloads before execution.
    """

    def __init__(self, parameters: dict[str, Any] | None = None):
        self.parameters = parameters or {}

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(self.parameters)

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        if payload is None:
            payload = {}

        if not isinstance(payload, dict):
            raise ToolValidationError("Tool arguments must be a JSON object.")

        errors: list[str] = []
        result: dict[str, Any] = {}

        for name, definition in self.parameters.items():
            required = bool(definition.get("required", False))
            default = definition.get("default")
            expected_type = definition.get("type")
            allowed_values = definition.get("enum")

            if name not in payload:
                if required:
                    errors.append(f"Missing required argument: {name}")
                elif default is not None:
                    result[name] = default
                continue

            value = payload[name]
            if expected_type is not None:
                if expected_type == "string":
                    if not isinstance(value, str):
                        errors.append(f"Argument '{name}' must be a string.")
                elif expected_type == "integer":
                    if not isinstance(value, int) or isinstance(value, bool):
                        errors.append(f"Argument '{name}' must be an integer.")
                elif expected_type == "number":
                    if not isinstance(value, (int, float)) or isinstance(value, bool):
                        errors.append(f"Argument '{name}' must be a number.")
                elif expected_type == "boolean":
                    if not isinstance(value, bool):
                        errors.append(f"Argument '{name}' must be a boolean.")
                elif expected_type == "object":
                    if not isinstance(value, dict):
                        errors.append(f"Argument '{name}' must be an object.")
                elif expected_type == "array":
                    if not isinstance(value, list):
                        errors.append(f"Argument '{name}' must be a list.")

            if allowed_values is not None and value not in allowed_values:
                errors.append(f"Argument '{name}' must be one of: {allowed_values}")

            result[name] = value

        unexpected = set(payload.keys()) - set(self.parameters.keys())
        for name in sorted(unexpected):
            errors.append(f"Unexpected argument: {name}")

        if errors:
            raise ToolValidationError("Tool argument validation failed.", details={"errors": errors})

        return result

    @property
    def json_schema(self) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        required: list[str] = []

        for name, definition in self.parameters.items():
            if definition.get("required", False):
                required.append(name)
            properties[name] = {
                "type": definition.get("type", "string"),
                "description": definition.get("description", ""),
            }
            if definition.get("enum"):
                properties[name]["enum"] = definition.get("enum")

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }


def create_schema_from_type(field_types: dict[str, type | Any]) -> ToolArgumentSchema:
    parameters: dict[str, dict[str, Any]] = {}
    for name, value_type in field_types.items():
        if value_type is str:
            parameters[name] = {"type": "string", "required": True}
        elif value_type is int:
            parameters[name] = {"type": "integer", "required": True}
        elif value_type is float:
            parameters[name] = {"type": "number", "required": True}
        elif value_type is bool:
            parameters[name] = {"type": "boolean", "required": True}
        elif value_type is dict:
            parameters[name] = {"type": "object", "required": True}
        elif value_type is list:
            parameters[name] = {"type": "array", "required": True}
        else:
            parameters[name] = {"type": "string", "required": True}
    return ToolArgumentSchema(parameters=parameters)
